# %%

import pandas as pd
import numpy as np

from .misc import *

# import gc
# import memory_profiler


def infer_and_convert_data_types(df, column_def=[]):
    """
    Infers column types and performs conversions, allowing for explicit type definitions.

    Args:
        df (pd.DataFrame): DataFrame to process.
        column_def (Optional[List[Dict]]): List of dictionaries defining explicit column types.
            Example: [{'field': 'Score', 'type': 'numeric'}, ...]

    Returns:
        pd.DataFrame: DataFrame with inferred and converted data types.
    """

    errors_rate = 0.2  # Acceptable error rate for conversions, unless explicit.

    if column_def:
        # Apply explicit type conversions first, - will be converted no matter what , even with 100% error rate
        for col_def in column_def:
            field = col_def["field"]
            type = col_def["type"]
            if type == "string":
                df[field] = df[field].astype("object")
            if type == "number":
                _,df[field] = try_convert_to_numeric(df[field], errors_rate=1)
            if type == "complex":
                #_,df[field] = try_convert_to_complex(df[field], errors_rate=1)
                df[field] =  pd.to_numeric(df[field], errors='coerce').astype('complex128')
            if type == "date":
                _,df[field] = try_convert_to_datetime(df[field], errors_rate=1)
            if type == "duration":
                _,df[field] = try_convert_to_timedelta(df[field], errors_rate=1)
            if type == "category":
                _,df[field] = try_convert_to_category(df[field], unique_percent_max=100)

    # Infer and convert only object type columns. But check if they are not in explicitly defined list
    for col in df.select_dtypes(include=["object"]).columns:
        # Process only columns not explicitly defined in column_def
        if not any(d['field'] == col for d in column_def):
            for conversion_func in [
                try_convert_to_numeric,
                try_convert_to_complex,
                try_convert_to_datetime,
                try_convert_to_timedelta,
            ]:
                result, data = conversion_func(df[col], errors_rate)
                if result:
                    df[col] = data
                    break

            # category stands out with 50% of uniqness
            result, data = try_convert_to_category(
                df[col], unique_percent_max=50
            )  # 50% or less of unique -> treshold to categorize
            if result:
                df[col] = data
                continue

    return df


def try_convert_to_datetime(column, errors_rate):
    """
    Attempts to convert a pandas Series to datetime format, handling mixed formats and potential errors.

    Args:
        column (pd.Series): The pandas Series containing data to be converted.
        errors_rate (float): The maximum acceptable proportion of errors (NaN values) after conversion.

    Returns:
        tuple (bool, pd.Series or None):
            - True: Conversion successful and error rate within limits.
            - pd.Series: The converted datetime Series.
            - False: Conversion failed or error rate exceeded.
                   None: No datetime conversion possible.
    """

    df_size = len(column)  # Store DataFrame size for later calculations

    # Check for unique or mixed format in a sample of data for efficiency
    format = infer_datetime_format(column, percent_to_check=0.1)

    # Prioritize using inferred format for performance
    if format and format != "mixed":
        try:
            converted_column = pd.to_datetime(column, errors="coerce", format=format)
            # Check against error rate and return converted column if acceptable
            if converted_column.isna().sum() / df_size <= errors_rate:
                return True, converted_column
        except (ValueError, TypeError) as e:
            pass

    #check for potential Unix Epoch format         
    if  has_any_unix_timestamp(column, percent_to_check=0.1):        
        try:
            converted_column = pd.to_datetime(
                column, errors="coerce", unit='s'
            )
            if converted_column.isna().sum() / df_size <= errors_rate:
                return True, converted_column

        except (ValueError, TypeError) as e:
            pass


    # Fallback for mixed formats, unknown formats, or previous conversion failure
    # Note: parsing datetimes with mixed time zones will raise an error unless utc=True
    try:
        converted_column = pd.to_datetime(
            column, errors="coerce", format="mixed", utc=True
        )
        if converted_column.isna().sum() / df_size <= errors_rate:
            return True, converted_column

    except (ValueError, TypeError) as e:
        pass

    # Conversion failed
    return False, None


def try_convert_to_timedelta(column, errors_rate):
    try:
        converted_column = pd.to_timedelta(column, errors="coerce")

        if converted_column.isna().sum() / len(column) <= errors_rate:
            return True, converted_column
    except (ValueError, TypeError) as e:
        pass
    return False, None


def try_convert_to_numeric(column, errors_rate):
    try:
        converted_column = pd.to_numeric(column, errors="coerce")
        if converted_column.isna().sum() / len(column) <= errors_rate:
            return True, converted_column
    except ValueError:
        pass
    return False, None


def try_convert_to_category(column, unique_percent_max):
    """
    converts to categorical if percentage of unique entries is less or equal to given unique_percent param
    """
    try:
        # Conversion based on statistic about unique data
        # Percentage of unique values (n/a values are not included), meaning the lower the better
        # If unique close or 100% - there is no reason to categorize

        total_entries = len(column.dropna())
        percent_unique = (column.dropna().nunique() / total_entries) * 100

        # Check if the column should be categorical
        if percent_unique <= unique_percent_max:
            converted_column = column.astype("category")
            return True, converted_column
    except ValueError:
        pass
    return False, None


def try_convert_to_complex(column, errors_rate):
    try:
        converted_column = column.apply(parse_complex)
        if converted_column.isna().sum() / len(column) <= errors_rate:
            return True, converted_column
    except (ValueError, TypeError):
        pass
    return False, None


def parse_complex(s):
    """
    function to convert string to complex number
    """
    try:
        if "+" in s:
            real, imag = s.split("+")
            real = float(real)
            imag = float(imag[:-1]) if imag.endswith("j") else float(imag)
        elif "j" in s:
            real = 0  # np.nan
            imag = float(s[:-1])
        else:
            real = float(s) if s else np.nan
            imag = 0  # np.nan
        return complex(real, imag)
    except ValueError:
        return np.nan


# %%
