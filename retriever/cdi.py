import pandas as pd
import datetime as dt
import glob

from retriever import DataRetriever


class CDIRetriever(DataRetriever):

    def __init__(self):
        DataRetriever.__init__(self, "cdi")

    def _get_data_file_patterns(self):
        return [self.data_directory + "/CDI_%s.csv"]

    def _available_codes(self):
        return ["CDI"]

    def _load_data_files(self):
        print "Loading CDI CSV files..."

        file_list = glob.glob(self.data_directory + "/CDI_*.csv")

        self._data = pd.DataFrame()

        for file_name in file_list:
            print "Loading file %s..." % file_name

            df = pd.read_csv(
                file_name,
                names=['date', 'annual'],
                header=0,
                parse_dates=['date'],
                index_col=['date']
            )

            self._data = self._data.append(df)

        self._data.annual /= 10000.0
        self._data['annual_plus_one'] = self._data.annual + 1.0

        # http://www.cetip.com.br/astec/di_documentos/metodologia2_i1.htm
        self._data['daily'] = (self._data.annual + 1.0)**(1.0 / 252.0) - 1.0
        self._data['daily_plus_one'] = self._data.daily + 1.0

    def get_value(self, code, date):
        raise Exception("Not implemented!")

    def get_variation(self, code, begin_date, end_date):
        DataRetriever.get_variation(self, code, begin_date, end_date)

        start = dt.datetime.strptime(begin_date, "%Y-%m-%d")
        end = dt.datetime.strptime(end_date, "%Y-%m-%d")

        # Last day is not considered
        end = end - dt.timedelta(days=1)

        interval_df = self._data.ix[start:end]
        return interval_df.daily_plus_one.prod() - 1.0
