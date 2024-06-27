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

from phew import logging

def copy(s, t):
    try:
        if os.stat(t)[0] & 0x4000:  # is directory
            t = t.rstrip("/") + "/" + s
    except OSError:
        pass
    with open(s, "rb") as s:
        with open(t, "wb") as t:
            while True:
                l = s.read(512)
                if not l: break
                t.write(l)

class TestUtils(unittest.TestCase):

    def test_truncate_after_last_newline(self):
        size = 10
        copy("tests/testlog_1.txt", "tests/templogfile.txt")
        start_size = os.stat("tests/templogfile.txt").st_size
        logging.truncate("tests/templogfile.txt", target_size=size)
        with open("tests/templogfile.txt", "r") as l:
            self.assertEqual("", l.read(4))
        truncated_size = os.stat("tests/templogfile.txt").st_size
        self.assertEqual(0, truncated_size)


    def test_truncate_between_first_and_last_newlines(self):
        size = 4000
        copy("tests/testlog_1.txt", "tests/templogfile.txt")
        start_size = os.stat("tests/templogfile.txt").st_size
        logging.truncate("tests/templogfile.txt", target_size=size)
        with open("tests/templogfile.txt", "r") as l:
            self.assertEqual("2021", l.read(4))
        truncated_size = os.stat("tests/templogfile.txt").st_size
        self.assertEqual(size, truncated_size + 32)

    def test_truncate_before_first_newline(self):
        size = 8615
        copy("tests/testlog_1.txt", "tests/templogfile.txt")
        start_size = os.stat("tests/templogfile.txt").st_size
        logging.truncate("tests/templogfile.txt", target_size=size)
        with open("tests/templogfile.txt", "r") as l:
            self.assertEqual("2021", l.read(4))
        truncated_size = os.stat("tests/templogfile.txt").st_size
        self.assertEqual(size, truncated_size + 59)

    def test_truncate_on_newline(self):

            copy("tests/testlog_1.txt", "tests/templogfile.txt")
            start_size = os.stat("tests/templogfile.txt").st_size
            size = start_size - 64
            logging.truncate("tests/templogfile.txt", target_size=size)
            with open("tests/templogfile.txt", "r") as l:
                self.assertEqual("2021-01-01 00:02:21", l.read(19))
            truncated_size = os.stat("tests/templogfile.txt").st_size
            self.assertEqual(size, truncated_size, msg=f"Truncate first {size}")

    def test_truncate_after_end_of_file(self):
        size = 10000
        copy("tests/testlog_1.txt", "tests/templogfile.txt")
        start_size = os.stat("tests/templogfile.txt").st_size
        logging.truncate("tests/templogfile.txt", target_size=size)
        with open("tests/templogfile.txt", "r") as l:
            self.assertEqual("2021", l.read(4))
        truncated_size = os.stat("tests/templogfile.txt").st_size
        self.assertEqual(start_size, truncated_size)

    def test_truncate_to_zero(self):

        copy("tests/testlog_1.txt", "tests/templogfile.txt")
        logging.truncate("tests/templogfile.txt", target_size=0)
        with open("tests/templogfile.txt", "r") as l:
            self.assertEqual("", l.read(4))
        truncated_size = os.stat("tests/templogfile.txt").st_size
        self.assertEqual(0, truncated_size)


    def test_truncate_after_last_newline_no_newline_at_eof(self):
        size = 10
        copy("tests/testlog_no_newline_at_eof.txt", "tests/templogfile.txt")
        start_size = os.stat("tests/templogfile.txt").st_size
        logging.truncate("tests/templogfile.txt", target_size=size)
        with open("tests/templogfile.txt", "r") as l:
            self.assertEqual("", l.read(4))
        truncated_size = os.stat("tests/templogfile.txt").st_size
        self.assertEqual(0, truncated_size)


    def test_truncate_to_zero_no_newline_at_eof(self):

        copy("tests/testlog_no_newline_at_eof.txt", "tests/templogfile.txt")
        logging.truncate("tests/templogfile.txt", target_size=0)
        with open("tests/templogfile.txt", "r") as l:
            self.assertEqual("", l.read(4))
        truncated_size = os.stat("tests/templogfile.txt").st_size
        self.assertEqual(0, truncated_size)


    def tearDown(self):
        os.remove("tests/templogfile.txt")

if __name__ == '__main__':
    unittest.main()
