"""This module is responsible of the PV service.

It consumes a meter value, read its own power value, add the two and wrote to an output (see out module).

Author: Ludovic Mouline
"""
import json
from time import localtime
from math import cos, fabs
from random import random

import pv_simulator.broker
from pv_simulator.out import Output, OutMsg

# Below constants are used to mock a PV power value
# The value should not exceed the _MAX_POWER_KW, and we assume that it's value is always equals to 0 between _SUN_RISE_H
# and _SUN_SET_H.
# For the day, to reproduce a belly-curve, we used the cosine function with shifting parameters.
# These parameters have been experimentally defined to represent values strictly superior to 0.
# Noise parameters are here to avoid a "perfect" curve.
#
# The idea was not to represent a realistic function but something that can get closed to that.
# One may try to reproduce this with other functions (sine, gaussian distribution, gamma distribution, ...).
_MAX_POWER_KW = 4

_POWER_NOISE = 0.01

_SUN_RISE_H = 8
_SUN_SET_H = 20

# WARNING: changing one of the below values may result in negative power consumption
_PERIOD_FACTOR_SHIFT = 1 / 15_000
_SHIFT_BASE = 10_000
_SHIFT_NOISE_MIN = -0.05
_SHIFT_NOISE_MAX = 0.02
_SHIFT_NOISE_DIFF = _SHIFT_NOISE_MAX - _SHIFT_NOISE_MIN


def _power_noise() -> float:
    """Returns the noise to add to the power value. The noise is a float between
    [-_POWER_NOISE, _POWER_NOISE]"""
    return (random() * 2 * _POWER_NOISE) - _POWER_NOISE


def _shift_noise() -> float:
    """Returns a noise to add to the cosine shift performed."""
    return _SHIFT_BASE + random() * _SHIFT_NOISE_DIFF - fabs(_SHIFT_NOISE_MIN)


def _rand_power(time_s: int, factor: float, shift_noise: float) -> float:
    """Mock the PV power reader by generating a values with the following constraints:
         - 0 if the current time is less than _SUN_RISE_H or greater than _SUN_SET_H
         - value of the cos(x), where x is the time of the day, we performed shifting operation and modification
         of the period to have only one "positive bell" (values >= 0) between _SUN_RISE_H and _SUN_SET_H
    """
    _, _, _, hour, *_ = localtime(time_s)

    if hour < _SUN_RISE_H or hour >= _SUN_SET_H:
        return 0

    return factor * cos(time_s * _PERIOD_FACTOR_SHIFT - shift_noise) + _power_noise()


class PVService:
    """Class to encapsulate the behaviour of a PV service"""

    def __init__(self, meter_id: str, consumer: pv_simulator.broker.Consumer, *outputs: Output):
        factor = random() * _MAX_POWER_KW
        shift_noise = _shift_noise()
        self.consumer = consumer

        def callback(ch, method, properties, body):
            message = json.loads(body)  # Message is json string build from the meter.MeterValMsg typed dictionary

            pv_power_value = _rand_power(message["time_s"], factor, shift_noise)
            sum_power_w = pv_power_value * 1_000 + message["value"]

            for output in outputs:
                output.out(OutMsg(meter_id=meter_id, time_s=message["time_s"], meter_power_value_w=message["value"],
                                  pv_power_value_kw=pv_power_value, sum_meter_pv_w=sum_power_w))

        self.consumer.bind_messages(meter_id, callback)

    def __del__(self):
        self.consumer.stop_consuming()
