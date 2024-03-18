import pandas as pd
from datetime import datetime
import re


def is_binary(file):
    """
    Check if a file is binary by reading the first few bytes and checking for NULL bytes.
    """
    CHUNK_SIZE = 1024
    for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
        if b"\x00" in chunk:  # Check for NULL bytes
            file.seek(0)
            return True
    file.seek(0)
    return False


def get_sample(column, percent_to_check=0.1, min_samples=3):
    
    """
    Extracts a representative sample from a specified column of a DataFrame.
    
    Args:
        column (pandas.Series): The column from which to extract the sample.
        percent_to_check (float, optional): The percentage of the DataFrame size to consider
            when determining the sample size. Defaults to 0.1 (10%).
        min_samples (int, optional): The minimum number of samples to include in the sample,
            even if it exceeds the calculated percentage. Defaults to 3.

    Returns:
        pandas.Series: A sample of the specified column.
    """

    df_size = len(column)
    
    # Calculate the minimum number of samples based on the DataFrame size
    min_samples_required = max(min_samples, int(df_size * percent_to_check))  # At least % or min_samples, whichever is greater
    
    # If there are not enough records in the DataFrame set min to df_size
    if df_size < min_samples_required:
        min_samples_required = df_size
    
    sample = column.sample(n=min_samples_required)
    return sample


def has_any_utc_datetime(column, percent_to_check=0.1):
    """
    Checks if any value in a DataFrame column can be parsed as a UTC datetime,
    including those with 'Z' and common timezone offset patterns (e.g., '+05:30', '-08:00').

    Samples a proportion of the data and iteratively attempts conversion
    for efficiency using get_sample method

    Args:
        column (pandas.Series): The DataFrame column to evaluate.
        percent_to_check (float, optional): Proportion of data to sample (0 to 1). Defaults to 0.1. There is still check to get minimum ammount of samples required.

    Returns:
        bool: True if at least one value can be parsed as a UTC datetime, False otherwise.
    """
    
    sample = get_sample(column, percent_to_check)

    # Prioritize efficient 'Z' format check
    # certain that the column is of object type and it's text
    #if pd.api.types.is_string_dtype(sample):   
    if any(value.endswith('Z') for value in sample):
        return True  # Early return for 'Z' format

    # Check other UTC timezone offset patterns and attempt conversion
    for value in sample:
        # Match potential UTC format using regular expression
        if re.match(r"(Z|\+\d{2}:\d{2}|-\d{2}:\d{2})$", value):
            try:
                pd.to_datetime(value, utc=True)
                return True  # Early return on successful conversion
            except (ValueError, TypeError):
                pass  # Conversion failed (might not be valid UTC)

    return False  # No valid UTC datetime conversions found

import pandas as pd

def has_any_unix_timestamp(column, percent_to_check=0.1):
    """
    Checks if any value in a DataFrame column can be converted to a valid Unix timestamp (integer).

    Samples a proportion of the data and iteratively attempts conversion
    for efficiency using get_sample method

    Args:
        column (pandas.Series): The DataFrame column to evaluate.
        percent_to_check (float, optional): Proportion of data to sample (0 to 1). Defaults to 0.1. There is still check to get minimum ammount of samples required.

    Returns:
        bool: True if at least one value can be parsed as a valid Unix timestamp, False otherwise.
    """

    sample = get_sample(column, percent_to_check)

    # Check if any value can be converted to integer (potential Unix timestamp)
    try:
        # Attempt conversion with error handling
        converted_values = pd.to_numeric(sample, errors='coerce')
        return converted_values.notna().any()  # Check for successful conversions
    except pd.api.types.errors.DtypeConversionError:
        # Potential type mismatch, return False
        return False
    

    return False  # No valid integer conversions found


def infer_datetime_format(column, percent_to_check = 0.1):
    """
    Attempts to infer the datetime format of a column in a DataFrame.

    This function checks a sample of the data (default 10%) to determine if all values can be converted
    to datetime objects using a consistent format.

    Args:
        column (pandas dataframe): The column containing data to be checked.
        percent_to_check (float, optional): The proportion of the data to sample (0 to 1). Defaults to 0.1.

    Returns:
        str or None: The discovered format string if all data is consistent,
                       'mixed' if different formats are found,
                       None if no format is discovered (likely non-datetime data).
    """

    common_format = None

    # Iterate over the random values specified by rec_num of the column
    for value in get_sample(column, percent_to_check=percent_to_check):
        try:
            # Try to parse the value as a datetime object with various formats
            parsed_value = None

            # add more formats
            for format_str in ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%Y/%d/%m"]:
                try:
                    parsed_value = datetime.strptime(value, format_str)
                    break  # Exit loop if successfully parsed with a format
                except ValueError:
                    pass  # Continue to next format if parsing fails

            # If parsing fails for all formats, skip this value
            if parsed_value is None:
                continue

            # If this is the first parsed value, set the common format
            if common_format is None:
                common_format = format_str
            # If the format of this value is different from common_format, return 'mixed'
            elif common_format != format_str:
                return "mixed"
        except TypeError:
            # Skip if value is NaN
            continue

    # returns format if values have the same format and format will be None if no value were converted or format found
    return common_format
