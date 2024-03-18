# from django.test import TestCase
from unittest import TestCase

from .infer_data_types import *
from .misc import *

import pandas as pd
import numpy as np
import random
import csv
from faker import Faker

import glob
import io
import os

import memory_profiler
import gc


# Sample CSV string
csv_string = """
Time,Name,Birthdate,Score,Grade,Sum
  01:30:00,Alice,1/01/1990,1709991489000,A,1+2j
  00:15:42,Bob,2023-09-15 12:30:45-05:00,75,B,2+3j
  02:00:00,Charlie,3/03/1992,85,A,3+2
  102:30:50,David,4/04/1993,70,B,7j
  01:30:00,P0DT1H30M,Not Available,Not Available,A,8
  nan,2+3j,2023-09-15 12:30:45+00:00,1500,B,abc
"""


class LargeFilesTesting(TestCase):

    def large_sample_data_create(self):
        """
        WARNING: TAKES a while
        """

        # Generate random data
        fake = Faker()

        # set number of records here
        rec_num = 1000

        # create random data to load into dataFrame
        data = []
        for _ in range(rec_num):
            name = fake.first_name()
            birthdate = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime(
                "%m/%d/%Y"
            )
            score = random.randint(50, 100)
            grade = random.choice(["A", "B", "C"])
            data.append([name, birthdate, score, grade])

        # Add 'Not Available' randomly
        for _ in range(rec_num):
            index = random.randint(0, rec_num / 100)
            data[index][2] = "NA"

        # create data frame
        df = pd.DataFrame(data, columns=["Name", "Birthdate", "Score", "Grade"])
        return df

    def large_size_file_create(self):
        # 1000000 and 52 == roughly 1GB (WARNING TAKES a while, 30s+)
        # 250 000 and 52 == 250 MB
        rows = 500000
        columns = 52

        with open("backend/apiapp/TestsData/large_sample.csv", "w") as f:
            w = csv.writer(f, lineterminator="\n")
            for i in range(rows):
                a = []
                l = [i]
                for j in range(columns):
                    l.append(random.random())
                a.append(l)
                w.writerows(a)

    def test_df_all_converted(self):
        df = self.large_sample_data_create()

        # assert all object
        for col in df.columns:
            self.assertEqual(df[col].dtype, "object")

        # assert all columns have one of specified types
        infer_and_convert_data_types(df)
        for col in df.columns:
            self.assertTrue(
                df[col].dtype
                in [
                    pd.DatetimeTZDtype,
                    "datetime64[ns]",
                    np.float64,
                    "timedelta64[ns]",
                    "category",
                ]
            )

    @memory_profiler.profile
    def test_large_csv_file_to_df_all_converted(self):

        # set size inside method
        # self.large_size_file_create()

        with open("backend/apiapp/TestsData/sample_data.csv", "rb") as file:
            df = pd.read_csv(
                file, dtype="object"
            )  # columns type might be identified, for testing purpose make them all 'object'

        # assert all object
        for col in df.columns:
            self.assertEqual(df[col].dtype, "object")

        # Measure memory before conversion
        gc.collect()
        # Display memory usage of each column
        print(df.memory_usage(deep=True))
        before_mem = memory_profiler.memory_usage()[0]

        infer_and_convert_data_types(df)

        # Display memory usage of each column
        print(df.memory_usage(deep=True))
        # Measure memory after conversion
        after_mem = memory_profiler.memory_usage()[0]
        print(
            f"before: {before_mem  / 1024 / 1024} mb after: {after_mem / 1024 / 1024} mb"
        )

        # assert all columns have one of specified types
        for col in df.columns:
            self.assertTrue(
                df[col].dtype
                in [
                    pd.DatetimeTZDtype,
                    "datetime64[ns]",
                    np.int64,
                    np.float64,
                    "timedelta64[ns]",
                    "category",
                ]
            )


class CsvFilesTesting(TestCase):

    # load all .csv files into self.data_frames
    def setUp(self):
        """Loads the file data for each test."""

        # print(f"cwd: {os.getcwd()}")

        fileNames = glob.glob("backend/apiapp/TestsData/*.csv")
        self.data_frames = {}

        for file_name in fileNames:
            name = os.path.splitext(os.path.basename(file_name))[0]
            with open(file_name, "rb") as file:
                self.data_frames[name] = pd.read_csv(file)

    def test_pd_converts_to_datetime_ns(self):
        df = self.data_frames["datetime"]
        result, df["date"] = try_convert_to_datetime(df["date"], errors_rate=0.2)
        self.assertTrue(result)
        self.assertTrue(df["date"].dtypes == "datetime64[ns]")

    def test_pd_converts_to_datetime_ns_utc(self):
        df = self.data_frames["datetime_utc"]
        result, df["date"] = try_convert_to_datetime(df["date"], errors_rate=0.2)
        self.assertTrue(result)
        self.assertTrue(df["date"].dtypes == "datetime64[ns, UTC-05:00]")

    def test_pd_converts_mixed_to_datetime_ns_utc(self):
        df = self.data_frames["datetime_mixed"]
        result, df["date"] = try_convert_to_datetime(df["date"], errors_rate=0.2)
        self.assertTrue(result)
        self.assertTrue(df["date"].dtypes == "datetime64[ns, UTC]")


class CsvStringTesting(TestCase):

    def test_explicit_column_def_converts(self):
        # print("Pandas version:", pd.__version__)
        csv_file = io.StringIO(csv_string)
        df = pd.read_csv(csv_file)

        # convert with infer logic
        df = infer_and_convert_data_types(df)

        self.assertTrue(df["Birthdate"].dtypes == "datetime64[ns, UTC]")
        self.assertTrue(df["Score"].dtypes == "float64")
        self.assertTrue(df["Grade"].dtypes == "category")
        self.assertTrue(df["Time"].dtypes == "timedelta64[ns]")
        self.assertTrue(df["Sum"].dtypes == "complex128")

        self.assertTrue(df["Name"].dtypes == "object")

        # convert explicitly usign col_def
        col_def = [
            {"field": "Time", "type": "complex"},
            {"field": "Score", "type": "string"},
            {"field": "Name", "type": "number"},
        ]

        df = infer_and_convert_data_types(df, col_def)

        self.assertTrue(df["Time"].dtypes == "complex128")
        self.assertTrue(df["Name"].dtypes == "float64")
        self.assertTrue(df["Score"].dtypes == "object")

    def test_pd_converts(self):
        # print("Pandas version:", pd.__version__)
        csv_file = io.StringIO(csv_string)
        df = pd.read_csv(csv_file, parse_dates=True)

        infer_and_convert_data_types(df)

        self.assertTrue(df["Birthdate"].dtypes == "datetime64[ns, UTC]")
        self.assertTrue(df["Score"].dtypes == "float64")
        self.assertTrue(df["Grade"].dtypes == "category")
        self.assertTrue(df["Time"].dtypes == "timedelta64[ns]")
        self.assertTrue(df["Sum"].dtypes == "complex128")

    def test_pd_converts_to_numeric(self):
        csv_file = io.StringIO(csv_string)
        df = pd.read_csv(csv_file)
        result, df["Score"] = try_convert_to_numeric(df["Score"], errors_rate=0.2)
        self.assertTrue(result)
        self.assertTrue(df["Score"].dtypes == "float64")

    def test_pd_converts_to_datetime(self):
        csv_file = io.StringIO(csv_string)
        df = pd.read_csv(csv_file)
        result, df["Birthdate"] = try_convert_to_datetime(
            df["Birthdate"], errors_rate=0.2
        )
        self.assertTrue(result)
        self.assertTrue(df["Birthdate"].dtypes == "datetime64[ns, UTC]")

    def test_pd_converts_to_timedelta(self):
        csv_file = io.StringIO(csv_string)
        df = pd.read_csv(csv_file)
        result, df["Time"] = try_convert_to_timedelta(df["Time"], errors_rate=0.2)
        self.assertTrue(result)
        self.assertTrue(df["Time"].dtypes == "timedelta64[ns]")

    def test_pd_converts_to_complex(self):
        csv_file = io.StringIO(csv_string)
        df = pd.read_csv(csv_file)
        result, df["Sum"] = try_convert_to_complex(df["Sum"], errors_rate=0.2)
        self.assertTrue(result)
        self.assertTrue(df["Sum"].dtypes == "complex128")


class BulkTesting(TestCase):

    def setUp(self):
        """Loads the file data for each test."""
        self.files = glob.glob("backend/apiapp/TestsData/*.*")

    def test_data_no_exception(self):
        """Test case to handle each file. in TestsData folder"""
        try:
            for file_name in self.files:
                _, ext = os.path.splitext(file_name)
                with open(file_name, "rb") as file:
                    if ext.lower().startswith(".xl"):
                        df = pd.read_excel(file)
                    else:
                        df = pd.read_csv(file)

                self.assertFalse(df.empty, f"{file_name} df is empty !")
                infer_and_convert_data_types(df)
        except Exception as e:
            self.fail(f"file {str(file_name)} exception: {e}")
