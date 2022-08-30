import uasyncio, usocket
from . import logging

async def _handler(socket, ip_address):
  while True:
    try:
      yield uasyncio.core._io_queue.queue_read(socket)
      request, client = socket.recvfrom(256)
      response = request[:2] # request id
      response += b"\x81\x80" # response flags
      response += request[4:6] + request[4:6] # qd/an count
      response += b"\x00\x00\x00\x00" # ns/ar count
      response += request[12:] # origional request body
      response += b"\xC0\x0C" # pointer to domain name at byte 12
      response += b"\x00\x01\x00\x01" # type and class (A record / IN class)
      response += b"\x00\x00\x00\x3C" # time to live 60 seconds
      response += b"\x00\x04" # response length (4 bytes = 1 ipv4 address)
      response += bytes(map(int, ip_address.split("."))) # ip address parts
      socket.sendto(response, client)
    except Exception as e:
      logging.error(e)

def run_catchall(ip_address, port=53):
  logging.info("> starting catch all dns server on port {}".format(port))

  _socket = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
  _socket.setblocking(False)
  _socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
  _socket.bind(usocket.getaddrinfo(ip_address, port, 0, usocket.SOCK_DGRAM)[0][-1])

  loop = uasyncio.get_event_loop()
  loop.create_task(_handler(_socket, ip_address))