# **phew!** the Pico (or Python) HTTP Endpoint Wrangler

A small webserver and templating library specifically designed for MicroPython
on the Pico W. It aims to provide a complete toolkit for easily creating high
quality web based interfaces for your projects.

**phew!** is ideal for creating web based provisioning interfaces for connected projects
using the [Raspberry Pi Pico W](https://shop.pimoroni.com/products/raspberry-pi-pico-w).

- [**phew!** the Pico (or Python) HTTP Endpoint Wrangler](#phew-the-pico-or-python-http-endpoint-wrangler)
  - [What **phew!** does:](#what-phew-does)
  - [How to use](#how-to-use)
  - [Basic example](#basic-example)
  - [Running multiple web applications](#running-multiple-web-applications)
  - [Transport Layer Security (TLS)](#transport-layer-security-tls)
    - [Generating a Key and Certificate](#generating-a-key-and-cert)
  - [Sessions](#sessions)
    - [Session Authentication](#session-authentication)
  - [Function reference](#function-reference)
    - [server module](#server-module)
      - [add\_route](#add_route)
      - [set\_catchall](#set_catchall)
      - [run](#run)
    - [Session interface](#session-interface)
      - [create_session](#create_session)
      - [remove_session](#remove_session)
      - [login_required](#login_required)
      - [login_catchall](#login_catchall)
    - [Types](#types)
      - [Request](#request)
      - [Response](#response)
        - [Shorthand](#shorthand)
      - [Session](#session)
    - [Templates](#templates)
      - [render\_template](#render_template)
      - [Template expressions](#template-expressions)
        - [Variables](#variables)
        - [Conditional display](#conditional-display)
        - [Includes](#includes)
    - [logging module](#logging-module)
      - [log(level, text)](#loglevel-text)
      - [debug(\*items)](#debugitems)
      - [info(\*items)](#infoitems)
      - [warn(\*items)](#warnitems)
      - [error(\*items)](#erroritems)
      - [set\_truncate\_thresholds(truncate\_at, truncate\_to)](#set_truncate_thresholdstruncate_at-truncate_to)
    - [dns module](#dns-module)
      - [run\_catchall](#run_catchall)
    - [Helper functions](#helper-functions)
      - [connect\_to\_wifi](#connect_to_wifi)
      - [access\_point](#access_point)
      - [is\_connected\_to\_wifi](#is_connected_to_wifi)
      - [get\_ip\_address](#get_ip_address)
  - [Other Resources](#other-resources)

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
- `connect_to_wifi` and `access_point` convenience methods

Where possible **phew!** tries to minimise the amount of code and setup that you,
the developer, has to do in favour of picking sane defaults and hiding away bits
of minutiae that rarely needs to be tweaked.

## How to use

**phew!** can be installed using [pip](https://pypi.org/project/micropython-phew/) from the command line or from your favourite IDE. In Thonny this can be achieved by clicking `Tools` -> `Manage packages` and searching for `micropython-phew`.

## Basic example

An example web server that returns a random number between 1 and 100 (or optionally
the range specified by the callee) when requested:

```python
from phew import server, connect_to_wifi

connect_to_wifi("<ssid>", "<password>")

phew_app = server.Phew()

@phew_app.route("/random", methods=["GET"])
def random_number(request):
  import random
  min = int(request.query.get("min", 0))
  max = int(request.query.get("max", 100))
  return str(random.randint(min, max))

@phew_app.catchall()
def catchall(request):
  return "Not found", 404

phew_app.run()
```

**phew** is designed specifically with performance and minimal resource use in mind.
Generally this means it will prioritise doing as little work as possible including
assuming the correctness of incoming requests.

---

## Running multiple web applications

A device may require multiple web apps.  For instance, a setup web app for the access point
and a configuration web app for normal operation.  Phew supports the creation of many apps
with registration of routes per app. To create a new app, just create another ```server.Phew```
instance.

For concurrent execute of apps, each must be configured to connect to a different port and be
run in the same uasyncio loop as tasks.

```python
import uasyncio
from phew import server

phew_app1 = server.Phew()
phew_app2 = server.Phew()

# route methods declared here for both apps

loop = uasyncio.get_event_loop()
phew_app1.run_as_task(loop, host="0.0.0.0", port=80)
phew_app2.run_as_task(loop, host="0.0.0.0", port=8080)
loop.run_forever()
```

## Transport Layer Security (TLS)

Phew supports Transport Layer Security (TLS) by exposing the capabilities of
asynicio.

TLS is enabled by providing an ```ssl.SSLContext``` to either ```Phew.run```
or ```Phew.run_as_task```.

TLS setup introduces about a 5 second delay on a request.  This time depends on
the key algorithm used.

```python
import ssl

# set up TLS
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain("cert.der", "key.der")

# start the webserver
phew_app.run(host='0.0.0.0', port=443, ssl=ctx)
```

See [auth example app](https://github.com/ccrighton/phew/tree/main/examples/auth)
for a working implementation.

Configuration options for the ```ssl.SSLContext``` are documented at [Micropython SSL/TLS module](https://docs.micropython.org/en/latest/library/ssl.html).

### Generating a key and cert

Generate the key.
```commandline
openssl ecparam -name prime256v1 -genkey -noout -out key.der -outform DER
```

Generate the self-signed certificate.
```commandline
openssl req -new -x509 -key key.der -out cert.der -outform DER -days 365 -node
```

List the certificate details:
```commandline
openssl x509 -in cert.der  -text
```

Copy the key and cert files to the device.
```commandline
mpremote cp cert.der key.der :
```

## Sessions

Phew provides a simple session api to support authenticated session establishment. ```Phew.create_session()``` is
called to set up a new session.  The session returned contains the session id and max age values to be used in the
cookie exchange.

The following code creates the response to set the session cookie.  This needs to be run only if the client has provided
valid credentials.  For instance the client may do a POST request of a username and password as form data.

```python
session = phew_app.create_session()
return server.Response("OK", status=302,
                    headers={"Content-Type": "text/html",
                             "Set-Cookie": f"sessionid={session.session_id}; Max-Age={session.max_age}; Secure; HttpOnly",
                             "Location": "/"})
```

To ensure that the session id is sent only on TLS sessions, please ensure that the ```Secure``` parameter is set in the
```Set-Cookie``` header.

Once the session is established, all route handlers that have the ```login_required()``` annotation will check that
the request contains a cookie with the valid session id set.

```python
@phew_app.route("/", methods=["GET"])
@phew_app.login_required()
def index(request):
    return render_template("index.html", text="Hello World")
```

Add the ```login_required()``` annotation to all route handlers that need authentication.  However, do not add it to
the login route handler as this will prevent the establishment of a session.

```Phew.remove_session(request)``` is called to end the session.  For example, a logout route handler will call it to
log the session out.

```python
@phew_app.route("/logout", methods=["GET"])
def logout(request):
    phew_app.remove_session(request)
    return render_template("logout.html")
```

### Session Authentication

The method used for session authentication is within the control of the application using the Phew library.

In the example provided a login form is used that provides username and password in form data.


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

phew_app.add_route("/testpath", my_handler, methods=["GET"])
```

Or, alternatively, using a decorator:

```python
@phew_app.route("/testpath", methods=["GET"])
def my_handler(request):
  return "I got it!", 200
```

#### set_catchall

```python
phew_app.set_catchall(handler)
```

Provide a catchall method for requests that didn't match a route.

```python
def my_catchall(request):
  return "No matching route", 404

phew_app.set_catchall(my_catchall)
```

Or, alternatively, using a decorator:

```python
@phew_app.catchall()
def my_catchall(request):
  return "No matching route", 404
```

#### run

```python
phew_app.run(host="0.0.0.0", port=80)
```

Starts up the web server and begins handling incoming requests.

```python
phew_app.run()
```

### Session interface

#### create_session

Create a new session that provides the parameters needed for cookie based session establishment.
```python
session = phew_app.create_session()
```

#### remove_session

Remove an existing session, resulting in that session no longer being active so the user is logged out.
```python
phew_app.remove_session(request)
```

#### login_required

A decorator for a route handler that redirects and requests to decorated routes to the login handler.

```python
@phew_app.route("/hello", methods=["GET"])
@phew_app.login_required()
def hello(request, name):
  return render_template("index.html")
```

#### login_catchall

Decorator that sets the handler for the login page.  DO NOT decorate with ```login_required```.

```python
@phew_app.login_catchall()
def redirect_to_login(request):
    return server.redirect("/login", status=302)
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
@phew_app.route("/login", ["POST"])
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
@phew_app.route("/greeting/<name>", ["GET"])
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
@phew_app.route("/greeting/<name>", ["GET"])
def user_details(request, name):
  return f"Hello, {name}", 200
```

#### Session

The `Session` object contains the attributes of a session.  It is returned by the `create_session` function.

| member     | example                            | type | description                             |
|------------|------------------------------------|------|-----------------------------------------|
| session_id | `5146c4a8b8a3c83e54b5c06ce009988c` | str  | 128 bit hex encoded session identifier  |
| max_age    | `86400`                            | int  | seconds from session creation to expiry |
| expires    | `1609563847`                       | int  | seconds from epoch to session expiry    |

The `Session` object provides a convenience function for checking expiry:

```python
Session.expired()
```
Return boolean.

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

##### Lists

It is possible to perform operations on lists using str.join and list comprehension as in the following table example.

```html
<table>
{{"".join([f"<tr><td>item</td></tr>\r\n" for item in mylist])}}
</table>
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

While a bit unwieldy this methods works. An alternative would be to select the appropriate
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

### logging module

#### log(level, text)

Add a new entry into the log file.

```python
log("info", "> i'd like to take a minute, just sit right there")
log("error", "> the license plate said 'Fresh' and it had dice in the mirror")
```

The entry will automatically have the current date and time, the `level` value, and the amount of free memory in kB prepended:

```
2022-09-04 15:29:20 [debug    / 110kB] > performing startup
2022-09-04 15:30:42 [info     / 113kB]   - wake reason: rtc_alarm
2022-09-04 15:30:42 [debug    / 112kB]   - turn on activity led
2022-09-04 15:30:43 [info     / 102kB] > running pump 1 for 0.4 second
2022-09-04 15:30:46 [info     / 110kB] > 5 cache files need uploading
2022-09-04 15:30:46 [info     / 107kB] > connecting to wifi network 'yourssid'
2022-09-04 15:30:48 [debug    / 100kB]   - connecting
2022-09-04 15:30:51 [info     /  87kB]   - ip address:  192.168.x.x
2022-09-04 15:30:57 [info     /  79kB]   - uploaded 2022-09-04T15:19:03Z.json 2022-09-04 15:31:01 [info     /  82kB]   - uploaded 2022-09-04T15:28:17Z.json 2022-09-04 15:31:06 [info     /  88kB]   - uploaded 2022-09-04T15:30:43Z.json 2022-09-04 15:31:11 [info     /  95kB]   - uploaded 2022-09-04T15:29:00Z.json 2022-09-04 15:31:16 [info     / 100kB]   - uploaded 2022-09-04T15:29:21Z.json 2022-09-04 15:31:16 [info     /  98kB] > going to sleep
```

#### debug(*items)

Shorthand method for writing debug messages to the log.

```python
warn("> this is a story")
```

#### info(*items)

Shorthand method for writing information to the log.

```python
num = 123
info("> all about how", num, time.time())
```

#### warn(*items)

Shorthand method for writing warnings to the log.

```python
warn("> my life got flipped")
```

#### error(*items)

Shorthand method for writing errors to the log.

```python
warn("> turned upside down")
```

#### set_truncate_thresholds(truncate_at, truncate_to)

Will automatically truncate the log file to `truncate_to` bytes long when it reaches `truncate_at` bytes in length.

```python
# automatically truncate when we're closed to the
# filesystem block size to keep to a single block
set_truncate_thresholds(3.5 * 1024, 2 * 1.024)
```

Truncation always happens on the nearest line ending boundary so the truncated file may not exactly match the size specified.

### dns module

To make implementing device provisioning interfaces (via captive portal) simple **phew!** provides a catchall DNS server.

If you put the Pico W into access point mode and then run the catchall DNS server it will route all DNS requests back to the local device so that they can be handled.

#### run_catchall

```python
dns.run_catchall(ip_address)
```

Pass in the IP address of your device once in access point mode.

### Helper functions

#### connect_to_wifi

```python
connect_to_wifi(ssid, password, timeout=30)
```

Connects to the network specified by `ssid` with the provided password.

Returns the device IP address on success or `None` on failure.

#### access_point

```python
access_point(ssid, password=None)
```

Create an access point with the specified SSID. Optionally password protected if provided.

#### is_connected_to_wifi

```python
result = is_connected_to_wifi()
```

Returns `True` if there is an active WiFi connection.

#### get_ip_address

```python
get_ip_address()
```

Returns the current IP address if connected to a network or acting as an access point or `None` otherwise.

## Other Resources

Here are some Phew! community projects and guides that you might find useful. Note that code at the links below has not been tested by us and we're not able to offer support with it.

- :link: [Hacking Big Mouth Billy Bass](https://www.youtube.com/watch?v=dOEjfBplueM)
- :link: [How to set up a Phew! Access Point](https://www.kevsrobots.com/blog/phew-access-point.html)
- :link: [Wireless Networking Setup Example for Raspberry Pi Pico W](https://github.com/simonprickett/phewap)
