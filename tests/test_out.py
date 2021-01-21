import os
import shutil
import unittest
from unittest.mock import patch
import pv_simulator.out
from os import path, remove


class TestLoggerOutPut(unittest.TestCase):
    @patch('pv_simulator.out.info')
    def test(self, mocked):
        msg = pv_simulator.out.OutMsg(time_s=1547, pv_power_value_kw=2.5,
                                      meter_power_value_w=8745.65, sum_meter_pv_w=11245.65)
        pv_simulator.out.LoggerOutput().out(msg)
        mocked.assert_called_with(msg)


class TestCSVFile(unittest.TestCase):
    YEAR = 1900
    MONTH = 1
    DAY = 31

    TEST_FILE_FOLDER = "tmp-test"

    def setUp(self) -> None:
        os.mkdir(self.TEST_FILE_FOLDER)

    def tearDown(self) -> None:
        shutil.rmtree(self.TEST_FILE_FOLDER)

    @patch('pv_simulator.out.datetime')
    def test_new_file(self, mocked_date):
        mocked_date.today().year = self.YEAR
        mocked_date.today().month = self.MONTH
        mocked_date.today().day = self.DAY

        file_name = f"{self.TEST_FILE_FOLDER}{os.sep}test-{self.YEAR}-{self.MONTH}-{self.DAY}.csv"

        self.assertFalse(path.exists(file_name))

        file = pv_simulator.out.CSVFileOutput(f"{self.TEST_FILE_FOLDER}{os.sep}test")
        del file

        self.assertTrue(path.exists(file_name))

        with open(file_name, "r") as file:
            lines = file.readlines()
            self.assertEqual(1, len(lines))
            self.assertEqual("time_s,meter_power_value_w,pv_power_value_kw,sum_meter_pv_w", lines[0].strip())

    @patch('pv_simulator.out.datetime')
    def test_changing_day(self, mocked_date):
        mocked_date.today().year = self.YEAR
        mocked_date.today().month = self.MONTH
        mocked_date.today().day = self.DAY + 1

        file = pv_simulator.out.CSVFileOutput(f"{self.TEST_FILE_FOLDER}{os.sep}test")
        file.out(pv_simulator.out.OutMsg(time_s=1547, pv_power_value_kw=2.5,
                                         meter_power_value_w=8745.65, sum_meter_pv_w=11245.65))
        file.out(pv_simulator.out.OutMsg(time_s=1548, pv_power_value_kw=2.4,
                                         meter_power_value_w=8600.54, sum_meter_pv_w=11000.54))

        mocked_date.today().day = self.DAY + 2

        file.out(pv_simulator.out.OutMsg(time_s=1549, pv_power_value_kw=0.2,
                                         meter_power_value_w=500.35, sum_meter_pv_w=700.35))
        del file

        file1 = f"{self.TEST_FILE_FOLDER}{os.sep}test-{self.YEAR}-{self.MONTH}-{self.DAY + 1}.csv"
        file2 = f"{self.TEST_FILE_FOLDER}{os.sep}test-{self.YEAR}-{self.MONTH}-{self.DAY + 2}.csv"

        self.assertTrue(path.exists(file1))
        self.assertTrue(path.exists(file2))

        with open(file1, "r") as file:
            lines = file.readlines()
            self.assertEqual(3, len(lines))
            self.assertEqual("time_s,meter_power_value_w,pv_power_value_kw,sum_meter_pv_w", lines[0].strip())
            self.assertEqual("1547,8745.65,2.5,11245.65", lines[1].strip())
            self.assertEqual("1548,8600.54,2.4,11000.54", lines[2].strip())

        with open(file2, "r") as file:
            lines = file.readlines()
            self.assertEqual(2, len(lines))
            self.assertEqual("time_s,meter_power_value_w,pv_power_value_kw,sum_meter_pv_w", lines[0].strip())
            self.assertEqual("1549,500.35,0.2,700.35", lines[1].strip())

    @patch('pv_simulator.out.datetime')
    def test_with_existing_file(self, mocked_date):
        mocked_date.today().year = self.YEAR
        mocked_date.today().month = self.MONTH
        mocked_date.today().day = self.DAY + 3

        file_name = f"{self.TEST_FILE_FOLDER}{os.sep}test-{self.YEAR}-{self.MONTH}-{self.DAY + 3}.csv"

        with open(file_name, 'w') as file:
            file.writelines("A line\n")

        file = pv_simulator.out.CSVFileOutput(f"{self.TEST_FILE_FOLDER}{os.sep}test")
        file.out(pv_simulator.out.OutMsg(time_s=1549, pv_power_value_kw=0.2,
                                         meter_power_value_w=500.35, sum_meter_pv_w=700.35))
        del file

        with open(file_name, "r") as file:
            lines = file.readlines()
            self.assertEqual(2, len(lines))
            self.assertEqual("A line", lines[0].strip())
            self.assertEqual("1549,500.35,0.2,700.35", lines[1].strip())

        remove(file_name)
