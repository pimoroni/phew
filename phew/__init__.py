__version__ = "0.0.2"

# highly recommended to set a lowish garbage collection threshold
# to minimise memory fragmentation as we sometimes want to
# allocate relatively large blocks of ram.
import gc, os, machine
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

wlan = None

# helper method to quickly get connected to wifi
def connect_to_wifi(ssid, password, timeout_seconds=30):
  global wlan
  import network, time

  disable_wifi()

  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)    
  wlan.connect(ssid, password)

  start = time.ticks_ms()
  while not wlan.isconnected() and (time.ticks_ms() - start) < (timeout_seconds * 1000):
    time.sleep(0.25)

  if wlan.status() != 3:
    return None

  return wlan.ifconfig()[0]

# helper method to put the pico into access point mode
def access_point(ssid, password = None):
  global wlan
  import network

  disable_wifi()

  # start up network in access point mode  
  wlan = network.WLAN(network.AP_IF)
  wlan.config(essid=ssid)
  if password:
    wlan.config(password=password)
  else:    
    wlan.config(security=0) # disable password
  wlan.active(True)

  return wlan

def disable_wifi():
  global wlan
  if wlan:
    wlan.disconnect()
    wlan.active(False)
    wlan = None