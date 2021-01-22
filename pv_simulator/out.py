""" A module that is responsible for outputting the result of the simulator in a file, the console,
or any other resource.

Author: Ludovic Mouline
"""
from __future__ import annotations
from logging import info
from datetime import datetime
import csv
from os import path
from typing import TypedDict


class OutMsg(TypedDict):
    meter_id: str
    time_s: int
    meter_power_value_w: float
    pv_power_value_kw: float
    sum_meter_pv_w: float


class Output:
    """Informal interface for the output mechanism."""

    def out(self, msg: OutMsg) -> None:
        """Process the given message"""
        pass


class LoggerOutput(Output):
    """This output logs the message like it in the console."""

    def out(self, msg: OutMsg) -> None:
        info(msg)


class CSVFileOutput(Output):
    """This implementation saves the message into a CSV file.

    One CSV file is created for each day. The messages are then appended to the file.
    This approach keeps the file of the current day open for the full day. This is to prevent opening and closing
    too often.

    Warning 1: this method does not lock the file. Therefore, it can be modified or (worst) deleted by an external
    process. It may result in unexpected behaviour.

    Warning 2: This method is not supposed to be used in a globally distributed system. The definition of the day is the
    "current local day".
    """
    _FILE_NAME_SEP = '-'
    _FILE_EXT = '.csv'

    def __init__(self, base_file_name: str):
        self.base_file_name = base_file_name
        self.current_file = None
        self.writer = None
        self.today_file_name = None

        self._open()

    def _csv_file_name(self, date) -> str:
        return self.base_file_name + self._FILE_NAME_SEP + str(date.year) + self._FILE_NAME_SEP + str(date.month) \
               + self._FILE_NAME_SEP + str(date.day) + self._FILE_EXT

    def _today_file_name(self) -> str:
        """
        Returns the formatted file name that is:
        <BASE_FILE_NAME>_YYYY_M_D
        :return: the formatted file name for the current day
        """
        return self._csv_file_name(datetime.today())

    def _open(self, today_file_name: str = None) -> None:
        """
        Opens for writing the given file and closes the current file if any

        :param today_file_name: name of the file to open
        """
        if today_file_name is None:
            self.today_file_name = self._today_file_name()
        else:
            self.today_file_name = today_file_name

        file_exist = path.isfile(self.today_file_name)

        self.current_file = open(self.today_file_name, 'a', newline='')
        self.writer = csv.DictWriter(self.current_file, fieldnames=OutMsg.__annotations__.keys())

        if not file_exist:
            self.writer.writeheader()

        self.current_file.flush()

    def _close(self) -> None:
        """
        Closes the current file
        """
        if self.current_file is not None:
            self.current_file.flush()
            self.current_file.close()

    def __del__(self):
        """Closes the current file"""
        self._close()

    def out(self, msg: OutMsg) -> None:
        """
        Appends the message content to the current CSV file.
        If the day has changed since the previous call, the function closes the current file and creates a new one.

        :param msg: information to add in the CSV file
        """

        file_name = self._today_file_name()

        if file_name != self.today_file_name:
            # Day has changed from the previous call
            self._close()
            self._open(file_name)

        self.writer.writerow(msg)
        self.current_file.flush()
