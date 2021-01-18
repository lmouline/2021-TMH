import unittest
from unittest.mock import patch
import pv_simulator.out
from os import path, remove


class TestLoggerOutPut(unittest.TestCase):
    @patch('pv_simulator.out.info')
    def test(self, mocked):
        msg = "Random message"
        pv_simulator.out.LoggerOutput().out(msg)
        mocked.assert_called_with(msg)


class TestCSVFile(unittest.TestCase):
    YEAR = 1900
    MONTH = 1
    DAY = 31

    @patch('pv_simulator.out.datetime')
    def test_new_file(self, mocked_date):
        mocked_date.today().year = self.YEAR
        mocked_date.today().month = self.MONTH
        mocked_date.today().day = self.DAY

        file_name = f"test-{self.YEAR}-{self.MONTH}-{self.DAY}.csv"

        self.assertFalse(path.exists(file_name))

        with pv_simulator.out.CSVFileOutput("test"):
            pass

        self.assertTrue(path.exists(file_name))

        with open(file_name, "r") as file:
            lines = file.readlines()
            self.assertEqual(1, len(lines))
            self.assertEqual("value1,value2", lines[0].strip())

        remove(file_name)

    @patch('pv_simulator.out.datetime')
    def test_changing_day(self, mocked_date):
        mocked_date.today().year = self.YEAR
        mocked_date.today().month = self.MONTH
        mocked_date.today().day = self.DAY + 1

        with pv_simulator.out.CSVFileOutput("test") as file:
            file.out(pv_simulator.out.OutMsg(value1="Line 1", value2=1))
            file.out(pv_simulator.out.OutMsg(value1="Line 2", value2=2))

            mocked_date.today().day = self.DAY + 2

            file.out(pv_simulator.out.OutMsg(value1="Line 3", value2=3))

        file1 = f"test-{self.YEAR}-{self.MONTH}-{self.DAY + 1}.csv"
        file2 = f"test-{self.YEAR}-{self.MONTH}-{self.DAY + 2}.csv"

        self.assertTrue(path.exists(file1))
        self.assertTrue(path.exists(file2))

        with open(file1, "r") as file:
            lines = file.readlines()
            self.assertEqual(3, len(lines))
            self.assertEqual("value1,value2", lines[0].strip())
            self.assertEqual("Line 1,1", lines[1].strip())
            self.assertEqual("Line 2,2", lines[2].strip())

        with open(file2, "r") as file:
            lines = file.readlines()
            self.assertEqual(2, len(lines))
            self.assertEqual("value1,value2", lines[0].strip())
            self.assertEqual("Line 3,3", lines[1].strip())

        remove(file1)
        remove(file2)

    @patch('pv_simulator.out.datetime')
    def test_with_existing_file(self, mocked_date):
        mocked_date.today().year = self.YEAR
        mocked_date.today().month = self.MONTH
        mocked_date.today().day = self.DAY + 3

        file_name = f"test-{self.YEAR}-{self.MONTH}-{self.DAY + 3}.csv"

        with open(file_name, 'w') as file:
            file.writelines("A line\n")

        with pv_simulator.out.CSVFileOutput("test") as file:
            file.out(pv_simulator.out.OutMsg(value1="Line 1", value2=1))

        with open(file_name, "r") as file:
            lines = file.readlines()
            self.assertEqual(2, len(lines))
            self.assertEqual("A line", lines[0].strip())
            self.assertEqual("Line 1,1", lines[1].strip())

        remove(file_name)
