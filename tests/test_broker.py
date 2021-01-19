import logging
import unittest
from unittest.mock import patch, Mock

from pv_simulator.broker import Broker


class TestBrokerConfig(unittest.TestCase):
    @patch('pv_simulator.broker.pika')
    @patch('pv_simulator.broker.logging')
    def test_no_correct_file(self, logging_mock, pika_mock):
        Broker()
        pika_mock.ConnectionParameters.assert_called_once_with(host="localhost", port=5672)
        pika_mock.BlockingConnection.assert_called_once()
        logging_mock.warning.assert_called_once()

    @patch('pv_simulator.broker.pika')
    @patch('pv_simulator.broker.logging')
    def test_file_wo_correct_section(self, logging_mock, pika_mock):
        Broker()
        pika_mock.ConnectionParameters.assert_called_once_with(host="localhost", port=5672)
        pika_mock.BlockingConnection.assert_called_once()
        logging_mock.warning.assert_called_once()

    @patch('pv_simulator.broker.pika')
    @patch('pv_simulator.broker.logging')
    def test_file_correct(self, logging_mock, pika_mock):
        Broker("broker-test.ini")
        pika_mock.ConnectionParameters.assert_called_once_with(host="192.168.74.98", port=123456)
        pika_mock.BlockingConnection.assert_called_once()
        logging_mock.info.assert_called_once()

    @patch('pv_simulator.broker.pika')
    @patch('pv_simulator.broker.logging')  # mock to avoid logging appears in the console during the tests
    def test_comm_close_after_del(self, logging_mock, pika_mock):
        broker = Broker()
        del broker
        pika_mock.BlockingConnection().close.assert_called_once()

    @patch('pv_simulator.broker.pika')
    @patch('pv_simulator.broker.logging')  # mock to avoid logging appears in the console during the tests
    def test_send_msg(self, logging_mock, pika_mock):
        broker = Broker()
        mock_meter = Mock()
        mock_meter.id = "Meter <ID>"

        msg = "False msg"

        broker.send_msg(mock_meter, msg)
        pika_mock.BlockingConnection().channel().queue_declare.assert_called_once_with(queue=mock_meter.id)
        pika_mock.BlockingConnection().channel().basic_publish.assert_called_once_with(exchange='',
                                                                                       routing_key=mock_meter.id,
                                                                                       body=msg)

    @patch('pv_simulator.broker.pika')
    @patch('pv_simulator.broker.logging')  # mock to avoid logging appears in the console during the tests
    def test_send_msg(self, logging_mock, pika_mock):
        broker = Broker()

        mock_meter = Mock()
        mock_meter.id = "Meter <ID>"
        broker.del_channel(mock_meter)
        pika_mock.BlockingConnection().channel().queue_delete.assert_called_once_with(queue=mock_meter.id)
