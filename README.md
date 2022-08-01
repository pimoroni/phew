# **phew!** the Pico (or Python) HTTP Endpoint Wrangler

> :warning: **Heads up! This is a very new project and should be considered, at best,
alpha stage.**

A small webserver and templating library specifically designed for MicroPython
on the Pico W. It aims to provide a complete toolkit for easily creating high
quality web based interfaces for your projects.

**phew!** is ideal for creating web based provisioning interfaces for connected projects
using the [Raspberry Pi Pico W](https://shop.pimoroni.com/products/raspberry-pi-pico-w).

- [What **phew!** does](#what-phew-does)
- [Basic example](#basic-example)
- [Function reference](#function-reference)
  - [server module](#server_module)
    - [add_route](#add_route)
    - [set_catchall](#set_catchall)
    - [run](#run)
  - [Types](#types)
    - [Request type](#request)
    - [Response type](#response)
      - [Shorthand](#shorthand)
  - [Templates](#templates)
    - [render_template](#render_template)
    - [Template expressions](#template-expressions)
      - [Variables](#variables)
      - [Conditional display](#conditional-display)
      - [Includes](#includes)
  - [dns module](#dns_module)
    - [run_catchall](#run_catchall)

## What **phew!** does:

- a basic web server
- optimised for speed (at `import` and during execution)
- minimal use of memory
- parameterised routing rules `/greet/<name>`
- templating engine that allows inline python expressions `{{name.lower()}}`
- `GET`, `POST` request methods
- query string decoding and parsing
- catchall handler for unrouted requests
- `multipart/form-data`, `x-www-form-urlencoded`, and JSON `POST` bodies
- string, byte, or generator based responses
- `connect_to_wifi` convenience method

Where possible **phew!** tries to minimise the amount of code and setup that you,
the developer, has to do in favour of picking sane defaults and hiding away bits
of minutiae that rarely needs to be tweaked.

## Basic example

An example web server that returns a random number between 1 and 100 (or optionally
the range specified by the callee) when requested:

```python
from phew import server, connect_to_wifi

connect_to_wifi("<ssid>", "<password>")

@server.route("/random", methods=["GET"])
def random_number(request):
  import random
  min = int(request.query.get("min", 0))
  max = int(request.query.get("max", 100))
  return str(random.randint(min, max))

@server.catchall()
def catchall(request):
  return "Not found", 404

server.run()
```

**phew** is designed specifically with performance and minimal resource use in mind.
Generally this means it will prioritise doing as little work as possible including 
assuming the correctness of incoming requests.

---

## Function reference
  
### server module

The `server` module provides all functionality for running a web server with 
route handlers.

#### add_route

```python
server.add_route(path, handler, methods=["GET"])
```

Adds a new route into the routing table. When an incoming request is received the server checks each route to find the most specific one that matches the request based on the path and method. If a route is found then the `handler` function is called with a `request` parameter
that contains details about the request.

```python
def my_handler(request):
  return "I got it!", 200

server.add_route("/testpath", my_handler, methods=["GET"])
```

Or, alternatively, using a decorator:

```python
@server.route("/testpath", methods=["GET"])
def my_handler(request):
  return "I got it!", 200
```

#### set_catchall

```python
server.set_catchall(handler)
```

Provide a catchall method for requests that didn't match a route.

```python
def my_catchall(request):
  return "No matching route", 404

server.set_catchall(my_catchall)
```

Or, alternatively, using a decorator:

```python
@server.set_catchall()
def my_catchall(request):
  return "No matching route", 404
```

#### run

```python
server.run(host="0.0.0.0", port=80)
```

Starts up the web server and begins handling incoming requests. 

```python
server.run()
```

### Types 

#### Request

The `Request` object contains all of the information that was parsed out of the
incoming request including form data, query string parameters, HTTP method, path,
and more.

Handler functions provided to `add_route` and `set_catchall` will recieve a 
`Request` object as their first parameter.

|member|example|type|description|
|---|---|---|---|
|protocol|`"HTTP/1.1"`|string|protocol version|
|method|`"GET"` or `"POST"`|string|HTTP method used for this request|
|uri|`"/path/to/page?parameter=foo"`|string|full URI of the request|
|path|`"/path/to/page"`|string|just the path part of the URI|
|query_string|`"parameter=foo"`|string|just the query string part of the URI|
|form|`{"foo": "bar", "name": "geoff"}`|dict|`POST` body parsed as `multipart/form-data`|
|data|`[{"name": "jenny"}, {"name": "geoff"}]`|any|`POST` body parsed as JSON|
|query|`{"parameter": "foo"}`|dict|result of parsing the query string|

At the time your route handler is being called the request has been fully parsed and you can access any properties that are relevant to the request (e.g. the `form` dictionary for a `multipart/form-data` request) any irrelevant properties will be set to `None`.

```python
@server.add_route("/login", ["POST"])
def login_form(request):
  username = request.form.get("username", None)
  password = request.form.get("password", None)

  # check the user credentials with your own code
  # for example: 
  # 
  # logged_in = authenticate_user(username, password)

  if not logged_in:
    return "Username or password not recognised", 401

  return "Logged in!", 200
```

#### Response

The `Response` object encapsulates all of the attributes of your programs response
to an incoming request. This include the status code of the result (e.g. 200 OK!)
, the data to return, and any associated headers.

Handler functions can create and return a `Response` object explicitly or use a couple
of shorthand forms to avoid writing the boilerplate needed.

|member|example|type|description|
|---|---|---|---|
|status|`200`|int|HTTP status code|
|headers|`{"Content-Type": "text/html"}`|dict|dictionary of headers to return|
|body|`"this is the response body"`|string or generator|the content to be returned|

```python
@server.add_route("/greeting/<name>", ["GET"])
def user_details(request):
  return Response(f"Hello, {name}", status=200, {"Content-Type": "text/html"})
```

##### Shorthand

As shorthand instead of returning a `Response` object the handle may also return a `tuple` with between
one and three values:

- body - either a string or generator method
- status code - defaults to `200` if not provided
- headers - defaults to `{"Content-Type": "text/html"}` if not provided

For example:

```python
@server.add_route("/greeting/<name>", ["GET"])
def user_details(request, name):
  return f"Hello, {name}", 200
```

### Templates

A web server isn't much use without something to serve. While it's straightforward 
to serve the contents of a file or some generated JSON things get more complicated
when we want to present a dynamically generated web page to the user.

**phew!** provides a templating engine which allows you to write normal HTML with 
fragments of Python code embedded to output variable values, parse input, or dynamically
load assets.

#### render_template

```python
render_template(template, param1="foo", param2="bar", ...):
```

The `render_template` method takes a path to a template file on the filesystem and 
a list of named paramaters which will be passed into the template when parsing.

The method is a generator which yields the parsing result in chunks, minimising the
amount of memory used to hold the results as they can be streamed directly out rather
than having to build the entire result as a string first.

Generally you will call `render_template` to create the body of a `Response` in one
of your handler methods.

#### Template expressions

Templates are not much use if you can't inject dynamic data into them. With **phew!**
you can embed Python expressions with `{{<expression here>}}` which will be evaluated 
during parsing.

##### Variables

In the simplest form you can embed a simple value by just enclosing it in double curly braces. 
It's also possible to perform more complicated transformations using any built in Python method.

```html
  <div id="name">{{name}}</div>

  <div id="name">{{name.upper()}}</div>
  
  <div id="name">{{"/".join(name.split(" "))}}</div>
```

##### Conditional display

If you want to show a value only if some other condition is met then you can use the
(slightly clunky) Python tenary operator.

```html
<div>
  You won
  {{"1st" if prize == 1 else ""}}
  {{"2nd" if prize == 2 else ""}}
  {{"3rd" if prize == 3 else ""}}
  prize!
</div>
```

or

```html
<div>
  You won
  {{["1st", "2nd", "3rd"][prize]}}
  prize!
</div>
```

While a bit unweildy this methods works. An alternative would be to select the appropriate
value in your handler and simply pass it into the template as a parameter however that
would mean having some of your copy embedded into your Python code rather than all of it
in one place in the template file.

##### Includes

You can include another template by calling `render_template()` again within your outer template.

`include.html`
```html
Hello there {{name}}!
```

`main.html`
```html
<!DOCTYPE html>
<body>
  {{render_template("include.html", name=name)}}
</body>
```

:warning: Note: you need to explicitly pass through template parameters into the included template - they are not available by default.

### dns module

To make implementing device provisioning interfaces (via captive portal) simple **phew!** provides a catchall DNS server.

If you put the Pico W into access point mode and then run the catchall DNS server it will route all DNS requests back to the local device so that they can be handled.

#### run_catchall

```python
dns.run_catchall(ip_address)
```

Pass in the IP address of your device once in access point mode.