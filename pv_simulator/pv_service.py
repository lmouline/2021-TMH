import json
import math
import time

from math import cos
import random

from pv_simulator.broker import Consumer
from pv_simulator.out import Output, OutMsg

_NOISE = 0.01
_MAX_POWER_KW = 4

_SUN_RISE_H = 8
_SUN_SET_H = 20

_SHIFT_BASE = 10_000
_SHIFT_NOISE_MIN = -0.05
_SHIFT_NOISE_MAX = 0.02
_SHIFT_NOISE_DIFF = _SHIFT_NOISE_MAX - _SHIFT_NOISE_MIN


def _noise() -> float:
    return (random.random() * 2 * _NOISE) - _NOISE


def _shift_noise() -> float:
    return _SHIFT_BASE + random.random() * _SHIFT_NOISE_DIFF - math.fabs(_SHIFT_NOISE_MIN)


def _rand_power(time_s: int, factor: float, shift_noise: float) -> float:
    _, _, _, hour, *_ = time.localtime(time_s)

    if _SUN_RISE_H > hour > _SUN_SET_H:
        return 0

    return factor * cos(time_s / 15_000 - shift_noise) + _noise()


class PVService:
    def __init__(self, meter_id: str, consumer: Consumer, *outputs: Output):
        self._factor = random.random() * _MAX_POWER_KW
        self._shift_noise = _shift_noise()
        self.consumer = consumer

        def callback(ch, method, properties, body):
            message = json.loads(body)

            pv_power_value = self.read_power(message["time_s"])

            sum_power_w = pv_power_value * 1_000 + message["value"]

            for output in outputs:
                output.out(OutMsg(time_s=message["time_s"], meter_power_value_w=message["value"],
                                  pv_power_value_kw=pv_power_value, sum_meter_pv_w=sum_power_w))

        self.consumer.bind_messages(meter_id, callback)

    def __del__(self):
        self.consumer.stop_consuming()

    def read_power(self, time_s) -> float:
        return _rand_power(time_s, self._factor, self._shift_noise)

