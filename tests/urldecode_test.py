import os
import unittest
from unittest import mock
from unittest.mock import patch

spi_mock = mock.Mock()
machine_mock = mock.MagicMock()
machine_mock.Pin = mock.MagicMock()
machine_mock.SPI = mock.MagicMock(return_value=spi_mock)
gc_mock = mock.MagicMock()
patch.dict("sys.modules", machine=machine_mock).start()
patch.dict("sys.modules", gc=gc_mock).start()
patch.dict("sys.modules", uasyncio=mock.MagicMock()).start()

from phew import server

class TestUrlDecode(unittest.TestCase):

    encoding = {" ": "%20",
                "!": "%21",
                "#": "%23",
                "$": "%24",
                "%": "%25",
                "A": "%41",
                "0": "%30",
                "€": "%E2%82%AC"}

    def test_url_unencoded(self):
            url = "http://www.google.com"
            self.assertEqual(url, server.urldecode(url))

    def test_urldecode_multiple_sequential_unicode(self):
            url = "%20%20%E2%82%AC%20%20"
            self.assertEqual("  €  ", server.urldecode(url))

    def test_urldecode(self):
        for k,v in self.encoding.items():
            self.assertEqual(k, server.urldecode(v))

    def test_urldecode_invalid(self):
        self.assertEqual("%XX ", server.urldecode("%XX%20"))

    def test_urldecode_invalid(self):

        replacement = chr(int("0xFFFD", 16))
        self.assertEqual("ABCD " + replacement + " ABCD", server.urldecode("ABCD %8d%ef%65%20 ABCD"))

    def test_urldecode_invalid_code_after_valid(self):

        replacement = chr(int("0xFFFD", 16))
        self.assertEqual("___A%XX___", server.urldecode("___%41%XX___"))

    def test_urldecode_invalid_unicode_before_invalid_code(self):

        replacement = chr(int("0xFFFD", 16))
        self.assertEqual("___" + replacement + "%XX___", server.urldecode("___%8d%ef%XX___"))


if __name__ == '__main__':
    unittest.main()
