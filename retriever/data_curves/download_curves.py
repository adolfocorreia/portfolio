#!/usr/bin/env python3

import argparse
import os
import sys
from datetime import date, timedelta

import pandas as pd
from bizdays import Calendar
from pyettj import NoDataError, PyETTJError, ettj

CAL = Calendar.load("PMC/BMF")


def parse_year() -> int:
    parser = argparse.ArgumentParser(description="Download B3 curves")
    parser.add_argument(
        "year",
        nargs="?",
        type=int,
        default=date.today().year,
        help="Year to download (default: current year)",
    )
    args = parser.parse_args()
    return args.year


def update_curve_data(year: int, file_name: str, curve_name: str) -> None:
    error = None

    # Compute missing dates in the CSV file
    if os.path.exists(file_name):
        previous_df = pd.read_csv(file_name, parse_dates=["refdate"])
        first_date = previous_df["refdate"].max().date() + timedelta(days=1)
    else:
        previous_df = None
        first_date = date(year, 1, 1)
    last_date = min(date(year, 12, 31), date.today() - timedelta(days=1))

    # No need to update file if:
    # - next date to fetch (first_date) is newer than last needed date
    # - there are no business days in the interval
    date_list = CAL.seq(first_date, last_date)
    if (first_date > last_date) or (len(date_list) < 1):
        os.utime(file_name, None)  # Touch file
        return

    # Fetch new data from B3
    print(f"Getting curves from {first_date} to {last_date}...")
    new_df = None
    for day in date_list:
        try:
            day_df = ettj.get_ettj(
                day.strftime("%Y-%m-%d"), curva=curve_name, cache=False, retry=5
            )
            new_df = pd.concat([new_df, day_df], ignore_index=False)
        except NoDataError:
            # Warn about missing day and continue fetching curves
            print(f"No curve data for day {day}")
        except PyETTJError as e:
            # Warn about error, abort loop but persist previously fetched curves
            print(f"Error when getting curve {curve_name} for {day}: {e}")
            error = "Error fetching curves"
            if new_df is None:
                sys.exit(error)
                return
            else:
                break

    assert new_df is not None

    # Adjust curve dataframe
    new_df.rename(
        columns={
            "curva": "curve",
            "dias_corridos": "cur_days",
            "dias_uteis": "biz_days",
            "taxa": "rate",
        },
        inplace=True,
    )
    new_df["forward_date"] = (
        new_df["refdate"] + pd.to_timedelta(new_df["cur_days"], unit="d")
    ).dt.date
    new_df = new_df[
        ["refdate", "curve", "cur_days", "biz_days", "forward_date", "rate"]
    ]

    for col in new_df.columns:
        assert len(new_df[col].apply(type).unique()) == 1

    # Append fetched curves to the existing dataframe
    if previous_df is not None:
        df = pd.concat([previous_df, new_df], ignore_index=True)
    else:
        df = new_df
    df = df.drop_duplicates()

    # Persist curves
    df.to_csv(file_name, index=False)

    if error is not None:
        sys.exit(error)


def main():
    year = parse_year()

    # Download DI x Pre curves
    print("Downloading DI x Pre curves...")
    pre_file_name = os.path.join(os.getcwd(), f"yc_di_pre_{year}.csv")
    update_curve_data(year, pre_file_name, "PRE")

    # Download DI x IPCA curves
    print("Downloading DI x IPCA curves...")
    ipca_file_name = os.path.join(os.getcwd(), f"yc_di_ipca_{year}.csv")
    update_curve_data(year, ipca_file_name, "DIC")


if __name__ == "__main__":
    main()
