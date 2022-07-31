# PICOHTTP

A small webserver and templating library specifically designed for MicroPython on the RP2040.

```python
import random
from paws import server, logging, connect_to_wifi

connect_to_wifi("<ssid>", "<password>")

@server.route("/random", methods=["GET"])
def random_number(request):
  return str(random.random())

@server.catchall()
def catchall(request):
  return "Not found", 404

server.run()
```
