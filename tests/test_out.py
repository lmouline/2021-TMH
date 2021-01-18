import unittest
from unittest.mock import patch
import pv_simulator.out


class TestClass(unittest.TestCase):
    @patch('pv_simulator.out.info')
    def test(self, mocked):
        pv_simulator.out.LoggerOutput().out("Take this!")
        mocked.assert_called_once()
