# paws - Pico Agile Web Server

A small webserver and templating library specifically designed for MicroPython
on the Pico W. It aims to provide a complete toolkit for easily creating high
quality web based interfaces for your projects.

Things **paws** provides:

- a basic web server
- parameterised routing rules `/greet/<name>`
- templating engine that allows inline python expressions `{{name.lower()}}`
- `GET`, `POST` request methods
- `multipart/form-data`, `x-www-form-urlencoded`, and JSON `POST` bodies
- query string decoding
- catchall handler for any request that doesn't match a route
- string, byte, or generator based responses
- convenience function for setting up wifi connections

Where possible **paws** tries to minimise the amount of code and setup that you,
the developer, has to do in favour of picking sane defaults and hiding away bits
of minutiae that rarely needs to be tweaked.

## Basic example

An example web server that returns a random number between 1 and 100 (or optionally
the range specified by the callee) when requested:

```python
from paws import server, connect_to_wifi

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

**paws** is designed specifically with performance and minimal resource use in mind.
Generally this means it will prioritise doing as little work as possible including 
assuming the correctness of incoming requests.

# API

- [server](#server)
  - [server.add_route](#serveradd_route)
  - [server.set_catchall](#serverset_catchall)
  - [server.run](#serverrun)
  
## `server`

The `server` module provides all functionality for running a web server with 
route handlers.

### server.add_route

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

### server.set_catchall

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

### server.run

```python
server.run(host="0.0.0.0", port=80)
```

Starts up the web server and begins handling incoming requests. 

```python
server.run()
```