import json
import unittest
from unittest.mock import Mock, patch

from pv_simulator.meter import Meter, MeterFactory, MeterValMsg


class MeterTest(unittest.TestCase):
    def tearDown(self) -> None:
        MeterFactory._MeterFactory__instance = None

    def test_creation(self):
        mock_broker = Mock()

        meter_factory = MeterFactory.instance()

        self.assertEqual("Meter 0", meter_factory.new_meter(mock_broker).meter_id)
        self.assertEqual("Meter 1", meter_factory.new_meter(mock_broker).meter_id)
        self.assertEqual("Meter 2", meter_factory.new_meter(mock_broker).meter_id)

    @patch("pv_simulator.meter.Meter.read_consumption")
    @patch("pv_simulator.meter.logging")
    @patch("pv_simulator.meter.time")
    def test_msg_formatting(self, mock_time, mock_logging, mocked_read_cons):
        v = 854.32
        time = 19354789

        mocked_read_cons.return_value = v
        mock_time.time.return_value = time
        mock_broker = Mock()

        expected_msg = MeterValMsg(meter_id="Meter 0", value=v, time_s=time)
        expected_to_send = json.dumps(expected_msg)

        MeterFactory.__instance = None
        meter_factory = MeterFactory.instance()
        meter = meter_factory.new_meter(mock_broker)

        meter.send_consumption()
        mocked_read_cons.allow_called_once()
        mock_broker.send_msg.assert_called_once_with(meter, expected_to_send)
        mock_logging.info.assert_called_once()

    def test_deletion(self):
        mock_broker = Mock()
        meter_id = "Meter ID"
        meter = Meter(meter_id, mock_broker)
        del meter
        mock_broker.del_channel.assert_called_once_with(meter_id)
