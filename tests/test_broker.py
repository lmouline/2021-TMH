import logging
import unittest
from unittest.mock import patch, Mock

from pv_simulator.broker import Producer, Consumer


class NoLoggerTest(unittest.TestCase):
    def setUp(self) -> None:
        logging.getLogger().disabled = True

    def tearDown(self) -> None:
        logging.getLogger().disabled = False


class TestBroker(NoLoggerTest):
    @patch('pv_simulator.broker.pika')
    @patch('pv_simulator.broker.logging')
    def test_no_correct_file(self, logging_mock, pika_mock):
        Producer()
        pika_mock.ConnectionParameters.assert_called_once_with(host="localhost", port=5672)
        pika_mock.BlockingConnection.assert_called_once()
        logging_mock.warning.assert_called_once()
        logging_mock.info.assert_called()

    @patch('pv_simulator.broker.pika')
    @patch('pv_simulator.broker.logging')
    def test_file_wo_correct_section(self, logging_mock, pika_mock):
        Producer("tests/wrong-broker.ini")
        pika_mock.ConnectionParameters.assert_called_once_with(host="localhost", port=5672)
        pika_mock.BlockingConnection.assert_called_once()
        logging_mock.warning.assert_called_once()
        logging_mock.info.assert_called()

    @patch('pv_simulator.broker.pika')
    @patch('pv_simulator.broker.logging')
    def test_file_correct(self, logging_mock, pika_mock):
        Producer("tests/broker-test.ini")
        pika_mock.ConnectionParameters.assert_called_once_with(host="192.168.74.98", port=123456)
        pika_mock.BlockingConnection.assert_called_once()
        logging_mock.info.assert_called()

    @patch('pv_simulator.broker.pika')
    def test_comm_close_after_del(self, pika_mock):
        broker = Producer()
        del broker
        pika_mock.BlockingConnection().close.assert_called_once()

    @patch('pv_simulator.broker.pika')
    def test_del_channel(self, pika_mock):
        broker = Producer()

        meter_id = "Meter <ID>"
        broker.del_channel(meter_id)
        pika_mock.BlockingConnection().channel().queue_delete.assert_called_once_with(queue=meter_id)


class TestProducer(NoLoggerTest):

    @patch('pv_simulator.broker.pika')
    def test_send_msg(self, pika_mock):
        broker = Producer()
        mock_meter = Mock()
        mock_meter.meter_id = "Meter <ID>"

        msg = "False msg"

        broker.send_msg(mock_meter, msg)
        pika_mock.BlockingConnection().channel().queue_declare.assert_called_once_with(queue=mock_meter.meter_id)
        pika_mock.BlockingConnection().channel().basic_publish.assert_called_once_with(exchange='',
                                                                                       routing_key=mock_meter.meter_id,
                                                                                       body=msg)


class TestConsumer(NoLoggerTest):
    @patch('pv_simulator.broker.pika')
    def test_bind_messages(self, pika_mock):
        consumer = Consumer()

        meter_id = "Meter <ID>"

        def callback(): pass

        consumer.bind_messages(meter_id, callback)
        pika_mock.BlockingConnection().channel().queue_declare.assert_called_once_with(queue=meter_id)
        pika_mock.BlockingConnection().channel().basic_consume.assert_called_once_with(queue=meter_id,
                                                                                       auto_ack=True,
                                                                                       on_message_callback=callback)
        pika_mock.BlockingConnection().channel().start_consuming.assert_not_called()

    @patch('pv_simulator.broker.pika')
    def test_start_consuming(self, pika_mock):
        consumer = Consumer()

        consumer.start_consuming()
        pika_mock.BlockingConnection().channel().start_consuming.assert_called_once()
