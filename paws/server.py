import uasyncio
from paws import logging

_routes = []
catchall_handler = None

def urldecode(text):
  text.replace("+", " ")
  result = ""
  token_caret = 0

  # decode any % encoded characters
  while True:
    start = text.find("%", token_caret)

    if start == -1:
      result += text[token_caret:]
      break

    result += text[token_caret:start]
    code = (int(text[start + 1]) * 16) + int(text[start + 2])
    result += chr(code)
    token_caret = start + 3

  return result


class Request:
  def __init__(self, method, uri, protocol):
    self.method = method
    self.uri = uri
    self.protocol = protocol
    self.form = {}
    self.data = {}
    self.query = {}
    query_string_start = uri.find("?") if uri.find("?") != -1 else len(uri)
    self.path = uri[:query_string_start]
    self.query_string = uri[query_string_start + 1:]
    if self.query_string:
      for parameter in self.query_string.split("&"):
        key, value = parameter.split("=")
        key = urldecode(key)
        value = urldecode(value)
        self.query[key] = value


  def __str__(self):
    return f"""request: {self.method} {self.path} {self.protocol}
headers: {str(self.headers)}
form: {str(self.form)}
data: {str(self.data)}"""


class Response:
  def __init__(self, body, status=200, content_type="text/html", headers={}):
    self.status = status
    self.content_type = content_type
    self.headers = headers
    self.body = body

  def add_header(self, name, value):
    self.headers[name] = value


class Route:
  def __init__(self, path, handler, methods=["GET"]):
    self.path = path
    self.methods = methods
    self.handler = handler
    self.path_parts = path.split("/")

  # returns True if the supplied request matches this route
  def matches(self, request):
    if request.method not in self.methods:
      return False
    compare_parts = request.path.split("/")
    if len(compare_parts) != len(self.path_parts):
      return False
    for i, compare in enumerate(compare_parts):
      part = self.path_parts[i]
      is_parameter = len(part) > 0 and part[0] == "<"
      if not is_parameter and part != compare:
        return False
    return True

  # call the route handler passing any named parameters in the path
  def call_handler(self, request):
    parameters = {}
    compare_parts = request.path.split("/")
    for i, compare in enumerate(compare_parts):
      part = self.path_parts[i]
      is_parameter = len(part) > 0 and part[0] == "<"
      if is_parameter:
        name = part[1:-1]
        parameters[name] = compare

    return self.handler(request, **parameters)
        
  def __str__(self):
    return f"""path: {self.path}
methods: {str(self.methods)}
"""

  def __repr__(self):
    return f"<Route object {self.path} ({", ".join(self.methods)})>"


# parses the headers for a http request (or the headers attached to
# each field in a multipart/form-data)
async def _parse_headers(reader):
  headers = {}
  while True:
    header_line = yield from reader.readline()
    if header_line == b"\r\n": # crlf denotes body start
      break
    name, value = header_line.decode().strip().split(": ", 1)
    headers[name.lower()] = value
  return headers


# returns the route matching the supplied path or None
def match_route(request):
  for route in _routes:
    if route.matches(request):
      return route
  return None


# adds a new route to the routing table
def add_route(path, handler, methods=["GET"]):
  global _routes
  _routes.append(Route(path, handler, methods))
  # descending complexity order so most complex routes matched first
  _routes = sorted(_routes, key=lambda route: len(route.path_parts), reverse=True)


# decorator shorthand for adding a route
def route(path, methods=["GET"]):
  def _route(f):
    add_route(path, f, methods=methods)
    return f
  return _route


# decorator for adding catchall route
def catchall():
  def _catchall(f):
    global catchall_handler
    catchall_handler = f
    return f
  return _catchall
  

# if the content type is multipart/form-data then parse the fields
async def _parse_form_data(reader, headers):
  boundary = headers["content-type"].split("boundary=")[1]
  # discard first boundary line
  dummy = yield from reader.readline()

  form = {}
  while True:
    # get the field name
    field_headers = await _parse_headers(reader)
    if len(field_headers) == 0:
      break
    name = field_headers["content-disposition"].split("name=\"")[1][:-1]
    # get the field value
    value = ""
    while True:
      line = yield from reader.readline()
      line = line.decode().strip()
      # if we hit a boundary then save the value and move to next field
      if line == "--" + boundary:
        form[name] = value
        break
      # if we hit end of form data boundary then save value and return
      if line == "--" + boundary + "--":
        form[name] = value
        return form
      value += line
  return None


# if the content type is application/json then parse the body
async def _parse_json_body(reader, headers):
  import json
  content_length_bytes = int(headers["content-length"])
  body = yield from reader.readexactly(content_length_bytes)
  return json.loads(body.decode())


status_message_map = {
  200: "OK", 201: "Created", 202: "Accepted", 
  203: "Non-Authoritative Information", 204: "No Content",
  205: "Reset Content", 206: "Partial Content", 300: "Multiple Choices",
  301: "Moved Permanently", 302: "Found", 303: "See Other",
  304: "Not Modified", 305: "Use Proxy", 306: "Switch Proxy",
  307: "Temporary Redirect", 308: "Permanent Redirect",
  400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
  404: "Not Found", 405: "Method Not Allowed", 406: "Not Acceptable",
  408: "Request Timeout", 409: "Conflict", 410: "Gone",
  414: "URI Too Long", 415: "Unsupported Media Type", 
  416: "Range Not Satisfiable", 418: "I'm a teapot",
  500: "Internal Server Error", 501: "Not Implemented"
}


# handle an incoming request to the web server
async def _handle_request(reader, writer):
  request_line = yield from reader.readline()
  method, uri, protocol = request_line.decode().split()
  request = Request(method, uri, protocol)
  logging.info(">", request.method, request.path)
  request.headers = await _parse_headers(reader)
  if "content-length" in request.headers and "content-type" in request.headers:
    if request.headers["content-type"].startswith("multipart/form-data"):
      request.form = await _parse_form_data(reader, request.headers)
    if request.headers["content-type"].startswith("application/json"):
      request.data = await _parse_json_body(reader, request.headers)

  response = None

  route = match_route(request)
  if route:
    response = route.call_handler(request)
  elif catchall_handler:
    response = catchall_handler(request)
  
  # if shorthand body generator only notation used then convert to tuple
  if type(response).__name__ == "generator":
    response = (response,)

  # if shorthand body text only notation used then convert to tuple
  if isinstance(response, str):
    response = (response,)

  # if shorthand tuple notation used then build full response object
  if isinstance(response, tuple):
    body = response[0]
    status = response[1] if len(response) >= 2 else 200
    content_type = response[2] if len(response) >= 3 else "text/html"
    response = Response(body, status=status)
    response.add_header("Content-Type", content_type)
    if hasattr(body, '__len__'):
      response.add_header("Content-Length", len(body))

  # write status line
  status_message = status_message_map.get(response.status, "Unknown")
  writer.write(f"HTTP/1.1 {status} {status_message}\r\n".encode("ascii"))

  # write headers
  for key, value in response.headers.items():
    writer.write(f"{key}: {value}\r\n".encode("ascii"))

  # blank line to denote end of headers
  writer.write("\r\n".encode("ascii"))

  if type(body).__name__ == "generator":
    for chunk in body:
      writer.write(chunk)
  else:
    writer.write(body)

  writer.close()
  await writer.wait_closed()


def run(host = "0.0.0.0", port = 80):
  logging.info("> starting webserver on port {}".format(port))

  loop = uasyncio.get_event_loop()
  loop.create_task(uasyncio.start_server(_handle_request, host, port))
  loop.run_forever()