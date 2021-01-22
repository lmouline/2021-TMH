import argparse
import logging
import os
import sys

import pv_simulator.pv_service as pv_service
from pv_simulator.broker import Consumer, Broker
import pv_simulator.out as out

logging.getLogger().setLevel(logging.INFO)

arg_parser = argparse.ArgumentParser(description="Demonstration code for the PV service. "
                                                 "Please make sure to have a running RabbitMQ instance.")
arg_parser.add_argument("-conf", "--configuration-file", type=str, help=f"path of the broker configuration file. "
                                                                        f"Default: {Broker._DEFAULT_CFG_FILE_NAME}")
arg_parser.add_argument("-ids", "--meter-ids", nargs="+", help="IDs of the meter (separated by a space).",
                        required=True)
options = arg_parser.parse_args()

conf_file = options.configuration_file if options.configuration_file is not None else Broker._DEFAULT_CFG_FILE_NAME

consumer = Consumer(conf_file)
pvs: [pv_service.PVService] = []

for meter_id in options.meter_ids:
    pvs.append(pv_service.PVService(meter_id, consumer, out.LoggerOutput(), out.CSVFileOutput(meter_id)))

try:
    consumer.start_consuming()
except KeyboardInterrupt:
    logging.info("Demo stopped by the user.")
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
