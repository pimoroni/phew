__version__ = "0.0.2"

# highly recommended to set a lowish garbage collection threshold
# to minimise memory fragmentation as we sometimes want to
# allocate relatively large blocks of ram.
import gc, os
gc.threshold(50000)

# phew! the Pico (or Python) HTTP Endpoint Wrangler
from . import logging

# determine if remotely mounted or not, changes some behaviours like
# logging truncation
remote_mount = False
try:
  os.statvfs(".") # causes exception if remotely mounted (mpremote/pyboard.py)
except:
  logging.debug("> detected remotely mounted filesystem")
  remote_mount = True

# helper method to quickly get connected to wifi
def connect_to_wifi(ssid, password, timeout_seconds=30):
  import network, time

  rp2.country("GB")
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect(ssid, password)

  start = time.ticks_ms()
  while (time.ticks_ms() - start) < (timeout_seconds * 1000):
    if wlan.status() < 0 or wlan.status() >= 3:
      break
    time.sleep(0.1)

  if wlan.status() != 3:
    return None

  return wlan.ifconfig()[0]

# helper method to put the pico into access point mode
def access_point(ssid, password = None):
  import rp2, network

  # start up network in access point mode
  rp2.country("GB")
  ap = network.WLAN(network.AP_IF)
  if ap.isconnected():
    ap.disconnect()
  ap.active(False)

  ap.config(essid=ssid)
  if password:
    ap.config(password=password)
  else:    
    ap.config(security=0) # disable password
  ap.active(True)

  return ap
