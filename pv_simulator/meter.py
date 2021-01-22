"""
This module implements a meter service.
A meter service reads a consumption value and sends it to a predefined broker.

The current implementation mocks the reading by generating a uniformly distributed value between 0 and 9000.

Author: Ludovic Mouline
"""
from __future__ import annotations
import logging
import time
import json
from random import uniform
from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    import pv_simulator.broker

MIN_CONS = 0
MAX_CONS = 9000
DELAY_MS = 1000


class MeterValMsg(TypedDict):
    """Type of the message sent through the broker."""
    meter_id: str
    value: float
    time_s: int


class MeterFactory:
    __instance = None

    def __init__(self):
        if MeterFactory.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            MeterFactory.__instance = self

        self.__BASE_ID = "Meter_"
        self.__id_next = 0

    @staticmethod
    def instance():
        if MeterFactory.__instance is None:
            MeterFactory()
        return MeterFactory.__instance

    def new_meter(self, broker: pv_simulator.broker.Producer) -> Meter:
        m_id = self.__BASE_ID + str(self.__id_next)
        self.__id_next = self.__id_next + 1
        return Meter(m_id, broker)


class Meter:
    """
    Representation of a meter where the id is: Meter <NB>, where NB is an integer that increases at each creation of
    a meter.

    WARNING: this approach cannot be used in a multi-threading application, or the meter id will not be unique.
    """

    def __init__(self, m_id: str, broker: pv_simulator.broker.Producer):
        """You should not directly call the constructor. We recommended using the factory."""
        self.meter_id = m_id
        self.broker = broker
        self.broker.open_channel(self.meter_id)

    def read_consumption(self) -> float:
        return uniform(MIN_CONS, MAX_CONS)

    def send_consumption(self) -> None:
        v = self.read_consumption()
        msg = MeterValMsg(meter_id=self.meter_id, value=v, time_s=int(time.time()))
        to_send = json.dumps(msg)
        self.broker.send_msg(self, to_send)
        logging.info(f"Message sent: {to_send}")

    def __del__(self):
        self.broker.del_channel(self.meter_id)
