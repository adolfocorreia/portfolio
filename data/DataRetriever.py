from abc import ABCMeta, abstractmethod
import os
import time
import re


class DataRetriever:
    __metaclass__ = ABCMeta

    _initial_year = 2014
    _date_regex = re.compile("^\d{4}-\d{2}-\d{2}$")

    def __init__(self, asset_name):
        self.asset_name = asset_name.lower()
        self.data_directory = "data_" + asset_name.lower()

        self._check_data_files()
        self._load_data_files()

    def _download_data_files(self, year):
        print "Downloading %s data files..." % self.asset_name
        old_path = os.getcwd()
        os.chdir(self.data_directory)
        os.system("./download_%s_files.sh %s" % (self.asset_name, year))
        os.chdir(old_path)
        time.sleep(1)

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
            newer_than_1day = (time.time() - os.path.getmtime(file_name)
                               < 24*60*60)
            return newer_than_1day
        else:
            first_day_of_base_year = time.mktime(
                (base_year, 1, 1, 0, 0, 0, -1, -1, -1)
            )
            newer_than_base_year = (os.path.getmtime(file_name)
                                    > first_day_of_base_year)
            return newer_than_base_year

    def _check_data_files(self):
        current_year = time.localtime()[0]
        for year in range(DataRetriever._initial_year, current_year+1):
            for file_pattern in self._get_data_file_patterns():
                file_name = file_pattern % year
                if not self._is_file_up_to_date(file_name, year):
                    self._download_data_files(year)
                    # Check again to see if file was downloaded
                    if not self._is_file_up_to_date(file_name, year):
                        raise Exception("File %s was not updated!" % file_name)

    @abstractmethod
    def _get_data_file_patterns(self):
        pass

    @abstractmethod
    def _available_codes(self):
        pass

    @abstractmethod
    def _load_data_files(self):
        pass

    @abstractmethod
    def get_value(self, code, date):
        assert code in self._available_codes()
        assert DataRetriever._date_regex.match(date)

    @abstractmethod
    def get_variation(self, code, begin_date, end_date):
        assert code in self._available_codes()
        assert DataRetriever._date_regex.match(begin_date)
        assert DataRetriever._date_regex.match(end_date)
