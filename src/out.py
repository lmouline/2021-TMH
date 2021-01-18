from logging import info, error
from datetime import datetime
import csv
from os import path
from typing import Iterable

from typing import TypedDict


class OutMsg(TypedDict):
    pass


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
    """
    FILE_NAME_SEP = '-'
    FILE_EXT = '.csv'

    def __init__(self, base_file_name: str):
        self.base_file_name = base_file_name
        self.current_file = None
        self.writer = None
        self.today_file_name = None

    def __open(self, today_file_name: str, csv_header: Iterable[str]) -> None:
        self.today_file_name = today_file_name

        file_exist = path.isfile(self.today_file_name)

        try:
            self.current_file = open(self.today_file_name, 'a', newline='')
            self.writer = csv.DictWriter(self.current_file, fieldnames=csv_header)

            if not file_exist:
                self.writer.writeheader()
        except Exception as e:
            error(f"Error while opening the file{e}")

    def out(self, msg: OutMsg):
        today = datetime.today()

        file_name = self.base_file_name + self.FILE_NAME_SEP + str(today.year) + self.FILE_NAME_SEP + str(today.month) \
                    + self.FILE_NAME_SEP + str(today.day) + self.FILE_EXT

        if self.current_file is None:
            # File has not been open yet (1st call)
            self.__open(file_name, msg.keys())
        elif file_name != self.today_file_name:
            # Day has changed from the previous call
            if self.current_file is not None:
                # Safety check, should always be True
                self.current_file.close()

            self.__open(file_name, msg.keys())

        try:
            self.writer.writerow(msg)
        except Exception as e:
            error(f"Error occurs while writing to a file: {e}")


if __name__ == '__main__':
    LoggerOutput().out("Test message")

    CSVFileOutput("Test").out({'meter_value': 10, 'pv_value': 2, 'sum': 2.01})
