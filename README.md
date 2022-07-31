# PICOHTTP

A small webserver and templating library specifically designed for MicroPython on the RP2040.

```python
import random
from picohttp import server, template

@server.route("/random", methods=["GET"])
def random_number(request):
  return str(random.random())

@server.route("/greet/<name>", methods=["GET"])
def greet(request, name):
  return "Hello" + name

@server.route("/are/you/a/teapot", methods=["GET"])
def im_a_teapot(request):
  return "Yes", 418

@server.catchall()
def catchall(request):
  return "Not found", 404

server.run()
```
