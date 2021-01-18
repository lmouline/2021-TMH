""" A module that is responsible of 'output' service

Author: Ludovic Mouline
"""
from __future__ import annotations

from logging import info
from datetime import datetime
import csv
from os import path
from typing import TypedDict


class OutMsg(TypedDict):
    value1: str
    value2: int


class Output:
    """Informal interface for the output mechanism."""

    def out(self, msg) -> None:
        """Process the given message"""
        pass


class LoggerOutput(Output):
    """This output logs the message as it in the console."""

    def out(self, msg) -> None:
        info(msg)


class CSVFileOutput(Output):
    """This implementation saves the message into a CSV file.

    One CSV file is created for each day. The messages are then appended to the file.
    This approach keeps the file of the current day open for the full day. This is to prevent opening and closing
    too often.

    Warning: this method does not lock the file. Therefore, it can be modified or (worst) deleted by an external
    process.

    Warning 1: This method is supposed to be used on globally distributed system. The definition of the day is the
    "local current day".

    This class should be use with the 'with' statement as following:

    '''
    with CSVFileOutput("test2") as out:
    '''

    """
    FILE_NAME_SEP = '-'
    FILE_EXT = '.csv'

    def __init__(self, base_file_name: str):
        self.base_file_name = base_file_name
        self.current_file = None
        self.writer = None
        self.today_file_name = None

    def __today_file_name(self) -> str:
        """
        Return the formatted file name that is:
        <BASE_FILE_NAME>_YYYY_M_D
        :return: the formatted file name for the current day
        """
        today = datetime.today()
        return self.base_file_name + self.FILE_NAME_SEP + str(today.year) + self.FILE_NAME_SEP + str(
            today.month) \
               + self.FILE_NAME_SEP + str(today.day) + self.FILE_EXT

    def __open(self, today_file_name: str = None) -> None:
        """
        Function that opens for writing the given file, and closes the current file if any

        :param today_file_name: name of the file to open
        """
        if today_file_name is None:
            self.today_file_name = self.__today_file_name()

        file_exist = path.isfile(self.today_file_name)

        self.current_file = open(self.today_file_name, 'a', newline='')
        self.writer = csv.DictWriter(self.current_file, fieldnames=OutMsg.__annotations__.keys())

        if not file_exist:
            self.writer.writeheader()

    def __close(self) -> None:
        """
        Close the current file
        """
        if self.current_file is not None:
            self.current_file.close()

    def __enter__(self) -> CSVFileOutput:
        """
        Open the file for the current day
        """
        self.__open()
        return self

    def __exit__(self, *args):
        """Close the current file"""
        self.__close()

    def out(self, msg: OutMsg) -> None:
        """
        Append the message content to the current CSV file.
        If the day has changed since the previous call, the function closes the current file and creates a new one.

        :param msg: information to add in the CSV file
        """
        today = datetime.today()

        file_name = self.base_file_name + self.FILE_NAME_SEP + str(today.year) + self.FILE_NAME_SEP + str(today.month) \
                    + self.FILE_NAME_SEP + str(today.day) + self.FILE_EXT

        if file_name != self.today_file_name:
            # Day has changed from the previous call
            self.__close()
            self.__open(file_name)

        self.writer.writerow(msg)


if __name__ == '__main__':
    with CSVFileOutput("test2") as out:
        for i in range(1, 10):
            out.out(OutMsg(value1="Youpi", value2=i))

