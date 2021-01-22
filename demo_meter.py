import logging
import os
import sys
import time
import argparse
from pv_simulator.broker import Broker, Producer
from pv_simulator.meter import MeterFactory, Meter

logging.getLogger().setLevel(logging.INFO)

arg_parser = argparse.ArgumentParser(description="Demonstration code for the meter service. "
                                                 "Please make sure to have a running RabbitMQ instance.")
arg_parser.add_argument("-conf", "--configuration-file", type=str, help=f"path of the broker configuration file. "
                                                                        f"Default: {Broker.DEFAULT_CFG_FILE_NAME}")
arg_parser.add_argument("-nb", "--nb-meter", type=int, help="number of meters that should be created. Default: 1")
options = arg_parser.parse_args()

nb_meter = options.nb_meter if options.nb_meter is not None and options.nb_meter > 0 else 1
conf_file = options.configuration_file if options.configuration_file is not None else Broker.DEFAULT_CFG_FILE_NAME

broker = Producer(conf_file)

meters: [Meter] = []
ids: [str] = []
for i in range(nb_meter):
    m = MeterFactory.instance().new_meter(broker)
    meters.append(m)
    ids.append(m.meter_id)

logging.info(f"Meter created: {ids}")

try:
    while True:
        for m in meters:
            m.send_consumption()
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Demo stopped by the user. Channels will be destroyed.")
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
