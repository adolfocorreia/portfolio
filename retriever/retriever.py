from abc import ABCMeta, abstractmethod
import os
import time
import re
import inspect
from datetime import datetime as dt


class DataRetriever(metaclass=ABCMeta):
    _initial_year = 2014
    _date_regex = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def __init__(self, asset_type):
        self.asset_type = asset_type.lower()

        module_file = inspect.getfile(inspect.currentframe())
        module_dir = os.path.dirname(os.path.abspath(module_file))
        self.data_directory = module_dir + "/data_" + asset_type.lower()

        self.codes = [line.strip() for line in open(self.data_directory + "/codes.txt")]

        self._needs_to_be_loaded = True
        self.check_and_update_data()

    def check_and_update_data(self):
        self._check_and_download_data_files()
        self._check_and_load_data_files()

    def _check_and_load_data_files(self):
        if self._needs_to_be_loaded:
            self._load_data_files()
            self._needs_to_be_loaded = False

    def _check_and_download_data_files(self):
        current_year = time.localtime()[0]
        for year in range(DataRetriever._initial_year, current_year + 1):
            for file_pattern in self._get_data_file_patterns():
                file_name = file_pattern % year
                if not self._is_file_up_to_date(file_name, year):
                    self._download_data_files(year)
                    self._needs_to_be_loaded = True
                    # Check again to see if file was downloaded
                    if not self._is_file_up_to_date(file_name, year):
                        raise Exception("File %s was not updated!" % file_name)

    def _download_data_files(self, year):
        print("Downloading %s data files..." % self.asset_type)
        old_path = os.getcwd()
        os.chdir(self.data_directory)
        os.system("./download_%s_files.sh %s" % (self.asset_type, year))
        os.chdir(old_path)
        time.sleep(5)

    @staticmethod
    def _is_file_up_to_date(file_name, base_year):
        # Check if file exists
        if not os.path.isfile(file_name):
            return False

        # Check if file is not empty
        if os.stat(file_name).st_size == 0:
            return False

        current_year = time.localtime()[0]

        if base_year == current_year:
            newer_than_1day = time.time() - os.path.getmtime(file_name) < 24 * 60 * 60
            return newer_than_1day
        else:
            first_day_of_base_year = time.mktime((base_year, 1, 1, 0, 0, 0, -1, -1, -1))
            newer_than_base_year = os.path.getmtime(file_name) > first_day_of_base_year
            return newer_than_base_year

    @abstractmethod
    def _get_data_file_patterns(self):
        pass

    @abstractmethod
    def _available_codes(self):
        pass

    @abstractmethod
    def _load_data_files(self):
        pass


class ValueRetriever(DataRetriever, metaclass=ABCMeta):
    def get_today_value(self, code):
        return self.get_value(code, dt.strftime(dt.today(), "%Y-%m-%d"))

    @abstractmethod
    def get_value(self, code, date):
        assert code in self._available_codes()
        assert DataRetriever._date_regex.match(date)


class VariationRetriever(DataRetriever, metaclass=ABCMeta):
    @abstractmethod
    def get_variation(self, code, begin_date, end_date):
        assert code in self._available_codes()
        assert DataRetriever._date_regex.match(begin_date)
        assert DataRetriever._date_regex.match(end_date)
