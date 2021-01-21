import json
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock, MagicMock

import pv_simulator
from pv_simulator import pv_service
from pv_simulator.meter import MeterValMsg
from pv_simulator.out import OutMsg
from pv_simulator.pv_service import PVService


class TestModuleFunctions(unittest.TestCase):

    @parameterized.expand([[0], [1], [2], [3], [4], [5], [6], [7], [20], [21], [22], [23]])
    @patch("pv_simulator.pv_service.localtime")
    def test_rand_power_no_sun(self, current_hour, mock_local_time):
        mock_local_time.return_value = (0, 0, 0, current_hour, 0)
        self.assertEqual(0, pv_simulator.pv_service._rand_power(1, 1., 1.))

    @parameterized.expand([[8], [9], [10], [11], [12], [13], [14], [15], [16], [17], [18], [19]])
    @patch("pv_simulator.pv_service.localtime")
    def test_rand_power_sun(self, current_hour, mock_local_time):
        mock_local_time.return_value = (0, 0, 0, current_hour, 0)
        self.assertNotEqual(0, pv_simulator.pv_service._rand_power(1, 1., 1.))

    def test_deletion(self):
        mock_broker = Mock()
        meter_id = "Meter ID"
        pv_service = PVService(meter_id, mock_broker)
        del pv_service
        mock_broker.stop_consuming.assert_called_once()

    @patch("pv_simulator.pv_service._rand_power")
    def test_msg(self, mocked_rand_power: MagicMock):
        mock_out = Mock()
        mock_broker = Mock()

        mock_body = MeterValMsg(meter_id="Meter ID", time_s=124, value=84.35)
        mock_broker.bind_messages = lambda m_id, callback: callback(None, None, None, json.dumps(mock_body))

        mocked_rand_power.return_value = 2.5

        check = {'called': False}

        def out_out_mock(msg: dict):
            check['called'] = True
            self.assertEqual(124, msg['time_s'])
            self.assertEqual(84.35, msg['meter_power_value_w'])
            self.assertEqual(2.5, msg['pv_power_value_kw'])
            self.assertEqual(2584.35, msg['sum_meter_pv_w'])
            self.assertEqual(OutMsg.__annotations__.keys(), msg.keys())

        mock_out.out = out_out_mock

        PVService("Meter ID", mock_broker, mock_out)

        self.assertTrue(check['called'])
