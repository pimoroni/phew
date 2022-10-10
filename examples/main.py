# example script to show how uri routing and parameters work
#
# create a file called secrets.py alongside this one and add the
# following two lines to it:
#
#	WIFI_SSID = "<ssid>"
#	WIFI_PASSWORD = "<password>"
#
# with your wifi details instead of <ssid> and <password>.

from phew import server, connect_to_wifi
from phew.template import render_template

import secrets

connect_to_wifi(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)

# basic response with status code and content type
@server.route("/basic", methods=["GET", "POST"])
def basic(request):
  return "Gosh, a request", 200, "text/html"

# basic response with status code and content type
@server.route("/status-code", methods=["GET", "POST"])
def status_code(request):
  return "Here, have a status code", 200, "text/html"

# url parameter and template render
@server.route("/hello/<name>", methods=["GET"])
def hello(request, name):
  return await render_template("example.html", name=name)

# response with custom status code
@server.route("/are/you/a/teapot", methods=["GET"])
def teapot(request):
  return "Yes", 418

# custom response object
@server.route("/response", methods=["GET"])
def response_object(request):
  return server.Response("test body", status=302, content_type="text/html", headers={"Cache-Control": "max-age=3600"})

# query string example
@server.route("/random", methods=["GET"])
def random_number(request):
  import random
  min = int(request.query.get("min", 0))
  max = int(request.query.get("max", 100))
  return str(random.randint(min, max))

# catchall example
@server.catchall()
def catchall(request):
  return "Not found", 404

# start the webserver
server.run()
