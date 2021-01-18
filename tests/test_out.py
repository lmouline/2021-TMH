import unittest
from unittest.mock import patch
import out


class TestClass(unittest.TestCase):
    @patch('out.info')
    def test(self, mocked):
        out.LoggerOutput().out("Take this!")
        mocked.assert_called_once()
