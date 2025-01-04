import glob
import inspect
import os
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime as dt
from pathlib import Path

import pandas as pd


def is_file_up_to_date(file_name, base_year=None):
    # Check if file exists
    if not os.path.isfile(file_name):
        return False

    # Check if file is not empty
    if os.stat(file_name).st_size == 0:
        return False

    current_year = time.localtime()[0]

    if base_year is None or base_year == current_year:
        newer_than_1day = time.time() - os.path.getmtime(file_name) < 24 * 60 * 60
        return newer_than_1day
    else:
        first_day_of_base_year = time.mktime((base_year, 1, 1, 0, 0, 0, -1, -1, -1))
        newer_than_base_year = os.path.getmtime(file_name) > first_day_of_base_year
        return newer_than_base_year


class DataRetriever(ABC):
    _initial_year = 2014
    _date_regex = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def __init__(self, asset_type):
        self.asset_type = asset_type.lower()

        module_file = inspect.getfile(inspect.currentframe())
        module_dir = os.path.dirname(os.path.abspath(module_file))
        self.data_directory = module_dir + "/data_" + asset_type.lower()

        self.codes = sorted(
            line.strip() for line in open(self.data_directory + "/codes.txt")
        )

        self._data = None

        self._needs_to_be_loaded = True
        self.check_and_update_data()

    def check_and_update_data(self):
        self._check_and_download_data_files()
        self._check_and_load_data_files()

    def _check_and_download_data_files(self):
        years = range(DataRetriever._initial_year, time.localtime()[0] + 1)
        patterns = self._get_data_file_patterns()
        tuples = [(p % y, y) for p in patterns for y in years]

        for file_name, year in tuples:
            if is_file_up_to_date(file_name, year):
                continue

            self._download_data_files(year)
            # Check again to see if file was successfully updated
            assert is_file_up_to_date(file_name, year), (
                "File %s was not updated!" % file_name
            )
            self._needs_to_be_loaded = True

    def _download_data_files(self, year):
        print("Downloading %s data files..." % self.asset_type)
        old_path = Path.cwd()
        os.chdir(self.data_directory)
        wait_status = os.system("./download_%s_files.sh %s" % (self.asset_type, year))
        exit_code = os.waitstatus_to_exitcode(wait_status)
        assert exit_code == 0
        os.chdir(old_path)
        time.sleep(5)

    def _check_and_load_data_files(self):
        if not self._needs_to_be_loaded:
            return

        if self._check_cache_files():
            print("Loading %s from cache files..." % self.asset_type)
            self._load_data_from_cache()
        else:
            print("Loading %s data files..." % self.asset_type)
            self._load_data_files()
            self._write_data_to_cache()
            assert self._check_cache_files(), "Cache files not updated!"

        print("Done loading %s..." % self.asset_type)
        self._needs_to_be_loaded = False

    def _check_cache_files(self):
        # Check if cache files exist
        cache_files = sorted(glob.glob(self.data_directory + "/*.cache"))
        if not cache_files:
            return False

        # Get oldest cache file timestamp
        cache_ts = min(map(os.path.getmtime, cache_files))

        # Ignore cache if it is older than 6 hours
        if time.time() - cache_ts > 6 * 60 * 60:
            return False

        # Get newest data file timestamp
        years = range(DataRetriever._initial_year, time.localtime()[0] + 1)
        patterns = self._get_data_file_patterns()
        file_list = [p % y for p in patterns for y in years]
        data_ts = max(map(os.path.getmtime, file_list))

        return data_ts < cache_ts

    def _load_data_from_cache(self):
        self._data = {}
        cache_files = sorted(glob.glob(self.data_directory + "/*.cache"))
        for cache_file in cache_files:
            name = Path(cache_file).stem
            self._data[name] = pd.read_feather(cache_file)

    def _write_data_to_cache(self):
        assert isinstance(self._data, dict)
        for key, df in self._data.items():
            assert isinstance(df, pd.DataFrame)
            file_name = os.path.join(self.data_directory, key + ".cache")
            df.to_feather(file_name)

    @abstractmethod
    def _get_data_file_patterns(self):
        pass

    @abstractmethod
    def _available_codes(self):
        pass

    @abstractmethod
    def _load_data_files(self):
        pass


class ValueRetriever(DataRetriever, ABC):
    def get_today_value(self, code):
        return self.get_value(code, dt.strftime(dt.today(), "%Y-%m-%d"))

    @abstractmethod
    def get_value(self, code, date) -> float:
        assert code in self._available_codes()
        assert DataRetriever._date_regex.match(date)


class VariationRetriever(DataRetriever, ABC):
    @abstractmethod
    def get_variation(self, code:str, begin_date:str, end_date:str, percentage:float=1.0) -> float:
        assert code is not None
        assert code in self._available_codes()
        assert DataRetriever._date_regex.match(begin_date)
        assert DataRetriever._date_regex.match(end_date)


class CurveRetriever(DataRetriever, ABC):
    @abstractmethod
    def get_curve_vertices(self, code, base_date):
        assert code in self._available_codes()
        assert DataRetriever._date_regex.match(base_date)
