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
    meter_id: str
    value: float
    time_s: int


class Meter:
    __id_next = 0
    __BASE_ID = "Meter "

    def __init__(self, broker: pv_simulator.broker.Broker):
        self.id = self.__BASE_ID + str(self.__id_next)
        self.__id_next = self.__id_next + 1
        self.broker = broker

    def read_consumption(self) -> float:
        return uniform(MIN_CONS, MAX_CONS)

    def send_consumption(self) -> None:
        v = self.read_consumption()
        msg = MeterValMsg(meter_id=self.id, value=v, time_s=int(time.time()))
        to_send = json.dumps(msg)
        self.broker.send_msg(self, to_send)
        logging.info(f"Message sent: {to_send}")

