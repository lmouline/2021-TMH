import logging
import os
import sys
import time

from pv_simulator.broker import Producer
from pv_simulator.meter import MeterFactory

logging.getLogger().setLevel(logging.INFO)

broker = Producer("broker-cfg.ini")
meter = MeterFactory.instance().new_meter(broker)

try:
    while True:
        meter.send_consumption()
        time.sleep(1)
except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
