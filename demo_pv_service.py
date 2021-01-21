import logging
import os
import sys

import pv_simulator.pv_service as pv_service
from pv_simulator.broker import Consumer
import pv_simulator.out as out

logging.getLogger().setLevel(logging.INFO)

consumer = Consumer("broker-cfg.ini")
service = pv_service.PVService("Meter 0", consumer, out.LoggerOutput(), out.CSVFileOutput("Meter-0"))

try:
    consumer.start_consuming()
except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

