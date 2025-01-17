#!/usr/bin/env python

import inspect
import os
import re
import sys
import warnings
from datetime import date

import bizdays
import pandas as pd
from bcb import Expectativas, sgs
from dateutil import relativedelta as rd

assert len(sys.argv) == 2
YEAR = int(sys.argv[1])
assert re.match(r"^(19|20)[0-9]{2}$", str(YEAR))

DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
assert DIR is not None and DIR.strip() != ""

bizdays.set_option("mode", "pandas")


# API URL format:
# http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=csv&dataInicial=01/01/2024&dataFinal=31/12/2024

DAILY_SERIES = {
    "SELIC": 11,
    "CDI": 12,
}
MONTHLY_SERIES = {
    "IPCA": 433,
    "IGP-M": 189,
}


def get_expectation(period: date, index: str) -> float:
    ref_date = period.strftime("%m/%Y")
    ep = Expectativas().get_endpoint("ExpectativaMercadoMensais")
    df_exp = (
        ep.query()
        .filter(ep.Indicador == index)
        .filter(ep.DataReferencia == ref_date)
        .filter(ep.baseCalculo == 1)
        .orderby(ep.Data.desc())
        .limit(1)
        .collect()
    )
    return df_exp.iloc[0]["Mediana"]


def replace_na_with_expectation(df: pd.DataFrame, period: date) -> None:
    ts = pd.Timestamp(period).to_period("M")
    for index in MONTHLY_SERIES.keys():
        if df.isna().loc[ts, index]:
            print(f"Using market expectation for {index} ({period:%Y-%m})...")
            df.loc[ts, index] = get_expectation(period, index)


def try_sgs_get(series: dict[str, int], start: date, end: date) -> pd.DataFrame:
    for i in range(5):
        try:
            return sgs.get(series, start, end)
        except ValueError:
            print(f"sgs.get error ({i}/5)")
    return sgs.get(series, start, end)


def main():
    cal = bizdays.Calendar.load(name="ANBIMA")
    today = date.today()

    # First day of year being retrieved
    start = date(YEAR, 1, 1)
    # Last day of year being retrieved (or previous business day if considering current year)
    end = min(date(YEAR, 12, 31), cal.offset(today, -1).date())
    assert start < end

    # First day of current month
    current_month = today.replace(day=1)
    # First day of previous month
    previous_month = current_month - rd.relativedelta(months=1)
    assert current_month.day == previous_month.day == 1

    # Retrieve historical series
    print("Retrieving historical series data...")
    df_daily = try_sgs_get(DAILY_SERIES, start, end)

    # Monthly data may not be available for the current period, therefore we ensure the call includes past periods
    df_monthly = try_sgs_get(MONTHLY_SERIES, min(start, previous_month), end)
    df_monthly = df_monthly.reindex(pd.date_range(start, end, freq="MS"))
    df_monthly.index = df_monthly.index.to_period("M")

    # Replace NA values with market expectation
    for period in (previous_month, current_month):
        if start <= period <= end:
            replace_na_with_expectation(df_monthly, period)
    assert not df_monthly.isna().any(axis=None)

    # Convert rates from monthly to daily
    days = cal.seq(start, end)
    assert (days == df_daily.index).all()

    index = df_monthly.index
    days_per_month = pd.Series([cal.getbizdays(x.year, x.month) for x in index], index)
    df_conv = ((1 + df_monthly / 100).pow(1 / days_per_month, axis="index") - 1) * 100
    with warnings.catch_warnings():
        # Ignore PeriodIndex resampling deprecation
        warnings.simplefilter(action="ignore", category=FutureWarning)
        df_conv = df_conv.resample("1D").ffill()
    df_conv.index = df_conv.index.to_timestamp()
    assert set(days).issubset(set(df_conv.index))
    df_conv = df_conv.loc[days]

    # Join dataframes and save data to CSV files
    df_daily = pd.concat([df_daily, df_conv], axis="columns")
    df_daily.to_csv(os.path.join(DIR, f"sgs_daily_{YEAR}.csv"))
    df_monthly.to_csv(os.path.join(DIR, f"sgs_monthly_{YEAR}.csv"))


if __name__ == "__main__":
    main()
