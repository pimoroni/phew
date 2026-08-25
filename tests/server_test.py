import asyncio
import unittest
from unittest import mock
from unittest.mock import patch

machine_mock = mock.MagicMock()
machine_mock.Pin = mock.MagicMock()
gc_mock = mock.MagicMock()
patch.dict("sys.modules", machine=machine_mock).start()
patch.dict("sys.modules", gc=gc_mock).start()

# server.py grabs the event loop at import time, and calls time.ticks_ms()
patch("asyncio.get_event_loop", mock.MagicMock()).start()
patch("time.ticks_ms", mock.MagicMock(return_value=0), create=True).start()

from phew import server


class Reader:
  def __init__(self, request):
    self.lines = request.split(b"\r\n")

  async def readline(self):
    return (self.lines.pop(0) + b"\r\n") if self.lines else b"\r\n"

  async def read(self, count):
    return b""


class Writer:
  def __init__(self):
    self.written = b""
    self.closed = False

  def write(self, data):
    self.written += data if isinstance(data, bytes) else data.encode()

  async def drain(self):
    pass

  def close(self):
    self.closed = True

  async def wait_closed(self):
    pass


GET = b"GET /thing HTTP/1.1\r\nHost: pico.wireless\r\n\r\n"


class HandleRequestTest(unittest.TestCase):
  def setUp(self):
    server._routes = []
    server.catchall_handler = None
    # the real logging module wants a working machine.RTC and writes to log.txt
    logging_patch = patch.object(server, "logging")
    self.logging = logging_patch.start()
    self.addCleanup(logging_patch.stop)

  def handle(self, request=GET):
    writer = Writer()
    asyncio.run(server._handle_request(Reader(request), writer))
    status_line = writer.written.split(b"\r\n")[0].decode()
    return status_line, writer

  def test_no_route_and_no_catchall_is_404(self):
    status_line, writer = self.handle()
    self.assertEqual(status_line, "HTTP/1.1 404 Not Found")
    self.assertTrue(writer.closed)

  def test_handler_returning_nothing_is_500(self):
    server.add_route("/thing", lambda request: None)
    status_line, writer = self.handle()
    self.assertEqual(status_line, "HTTP/1.1 500 Internal Server Error")
    self.assertTrue(writer.closed)
    self.logging.error.assert_called_once()

  def test_catchall_returning_nothing_is_500(self):
    server.set_callback(lambda request: None)
    status_line, writer = self.handle()
    self.assertEqual(status_line, "HTTP/1.1 500 Internal Server Error")
    self.assertTrue(writer.closed)

  def test_handler_returning_a_string_is_200(self):
    server.add_route("/thing", lambda request: "hello")
    status_line, writer = self.handle()
    self.assertEqual(status_line, "HTTP/1.1 200 OK")
    self.assertIn(b"hello", writer.written)
    self.assertTrue(writer.closed)

  def test_handler_status_is_preserved(self):
    server.add_route("/thing", lambda request: ("nope", 404))
    status_line, _ = self.handle()
    self.assertEqual(status_line, "HTTP/1.1 404 Not Found")

  def test_malformed_request_line_closes_the_connection(self):
    _, writer = self.handle(b"\r\n")
    self.assertEqual(writer.written, b"")
    self.assertTrue(writer.closed)


class ResponseHeadersTest(unittest.TestCase):
  def test_responses_do_not_share_headers(self):
    first = server.Response("first")
    first.add_header("Content-Length", 5)
    self.assertEqual(server.Response("second").headers, {})

  def test_file_response_does_not_leak_headers(self):
    server.FileResponse("tests/server_test.py")
    self.assertEqual(server.Response("body").headers, {})

  def test_missing_file_is_404(self):
    self.assertEqual(server.FileResponse("no/such/file").status, 404)


if __name__ == "__main__":
  unittest.main()
