# example script to show how uri routing and parameters work
#
# create a file called secrets.py alongside this one and add the
# following two lines to it:
#
#	WIFI_SSID = "<ssid>"
#	WIFI_PASSWORD = "<password>"
#
# with your wifi details instead of <ssid> and <password>.

import binascii
import ssl
from phew import server, connect_to_wifi
from phew.template import render_template

import secrets

connect_to_wifi(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)

phew_app = server.Phew()

@phew_app.route("/login", methods=["GET", "POST"])
def login(request):
  if request.method == "GET":
      return render_template("login.html", error="")

  if request.method == "POST":
      username = request.form["username"]
      password = request.form["password"]
      # TODO: username and password handling
      if username == "admin" and password == "admin":
          session = phew_app.create_session()
          return server.Response("OK", status=302,
                              headers={"Content-Type": "text/html",
                                       "Set-Cookie": f"sessionid={session.session_id}; Max-Age={session.max_age}; Secure; HttpOnly",
                                       "Location": "/"})

  return render_template("login.html", error="Login failure")

@phew_app.route("/logout", methods=["GET"])
def logout(request):
    if phew_app.active_session(request):
        phew_app.remove_session(request)
        return server.Response(render_template("logout.html"), status=200,
                               headers={"Content-Type": "text/html",
                                        "Set-Cookie": f"sessionid=deleted; expires=Thu, 01 Jan 1970 00:00:00 GMT"})
    else:
        return render_template("logout.html")

# basic response with status code and content type
@phew_app.route("/", methods=["GET"])
@phew_app.login_required()
def index(request):
    return render_template("index.html", text="Hello World")

# login catchall handler.  Redirect to /login
@phew_app.login_catchall()
def redirect_to_login(request):
    return server.redirect("/login", status=302)


# basic response with status code and content type
@phew_app.route("/basic", methods=["GET"])
@phew_app.login_required()
def basic(request):
  return render_template("index.html", text="Gosh, a request")

# basic response with status code and content type
@phew_app.route("/status-code", methods=["GET"])
@phew_app.login_required()
def status_code(request):
  return render_template("index.html", text="Here, have a status code 200")

# url parameter and template render
@phew_app.route("/hello/<name>", methods=["GET"])
@phew_app.login_required()
def hello(request, name):
  return render_template("index.html", text=name)


# query string example
@phew_app.route("/random", methods=["GET"])
@phew_app.login_required()
def random_number(request):
  import random
  min = int(request.query.get("min", 0))
  max = int(request.query.get("max", 100))
  return render_template("index.html", text=str(random.randint(min, max)))

@phew_app.route("/favicon.ico", methods=["GET"])
def status_code(request):
  return server.serve_file("/developer_board.svg")


# catchall example
@phew_app.catchall()
@phew_app.login_required()
def catchall(request):
  return render_template("404.html", text=f"{request.path} not found")


# set up TLS
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain("cert.der", "key.der")

# start the webserver
phew_app.run(host='0.0.0.0', port=443, ssl=ctx)
