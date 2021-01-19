"""This module implements the producer connection to a RabbitMQ broker.

The configuration should be defined in a <FILE_NAME>.ini file. It should contains a section called "broker", with at
most two values: host (string) and a port number (int). One, or all, can be omitted. In such a case,
default values will be used: 'localhost' for the host and 5672 for the port.

A warning message is printed if the "broker" section or the file is omitted.

Example:
    [broker]
    host = localhost
    port = 5672

This module do not support more complex configuration (SSL, virtual host, login/password).

Author: Ludovic Mouline
"""
from __future__ import annotations
import configparser
import pika
import logging
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pv_simulator.meter


class Broker:
    """Class that handles the connection to the broker."""

    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 5672
    DEFAULT_CFG_FILE_NAME = "broker.ini"

    SECTION_NAME = "broker"
    CFG_HOST = "host"
    CFG_PORT = "port"

    connection: pika.BlockingConnection
    channel: pika.adapters.blocking_connection.BlockingChannel

    def __init__(self, config_file: str = DEFAULT_CFG_FILE_NAME):
        self.__init_broker(config_file)

    def __init_broker(self, config_file: str) -> None:
        """Initialise the producer connection following the given configuration file. If no file is given or not well
        written, the default values are used. A warning message is printed if the "broker" section or the file
        is omitted.

        :param str config_file: path of the configuration file
        """
        config = configparser.ConfigParser()
        success_files = config.read(config_file)

        if len(success_files) == 0:
            logging.warning(
                f"None of the configuration files has been successfully read. The default configuration settings "
                f"have been used.")
            host = self.DEFAULT_HOST
            port = self.DEFAULT_PORT
        elif not config.has_section(self.SECTION_NAME):
            logging.warning(
                f"No configuration file has a \"{self.SECTION_NAME}\" section. The default configuration settings "
                f"have been used.")
            host = self.DEFAULT_HOST
            port = self.DEFAULT_PORT
        else:
            host = self.DEFAULT_HOST if config[self.SECTION_NAME][self.CFG_HOST] is None \
                else config[self.SECTION_NAME][self.CFG_HOST]
            port = self.DEFAULT_PORT if config[self.SECTION_NAME][self.CFG_PORT] is None \
                else config[self.SECTION_NAME][self.CFG_PORT]

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
        self.channel = self.connection.channel()

    def __del__(self):
        """Closes the connection when the broker instance is deleted."""
        if self.connection is not None:
            self.connection.close()

    def open_channel(self, meter: pv_simulator.meter.Meter):
        self.channel.queue_declare(queue=meter.id)

    def del_channel(self, meter: pv_simulator.meter.Meter):
        self.channel.queue_delete(queue=meter.id)

    def send_msg(self, meter: pv_simulator.meter.Meter, msg: str):
        self.open_channel(meter)
        self.channel.basic_publish(exchange='', routing_key=meter.id, body=msg)