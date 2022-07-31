# paws: pico's agile web server
from . import logging

# helper method to quickly get connected to wifi
def connect_to_wifi(ssid, password, timeout_seconds=30):
  import network, time

  logging.debug("> connecting to wifi network:", ssid)

  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect(ssid, password)

  start = time.ticks_ms()
  while (time.ticks_ms() - start) < (timeout_seconds * 1000):
    if wlan.status() < 0 or wlan.status() >= 3:
      break
    time.sleep(0.1)

  if wlan.status() != 3:
    logging.debug("  - failed to connect")
    return None

  logging.debug("  - ip address: ", wlan.ifconfig()[0])

  return wlan.ifconfig()[0]
