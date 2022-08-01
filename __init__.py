# phew! the Pico (or Python) HTTP Endpoint Wrangler
from .phew import server, logging, dns, connect_to_wifi

from .phew.server import redirect, serve_file
from .phew.template import render_template
