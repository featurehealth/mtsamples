import re
from collections import Counter
import pandas as pd

__all__ = ["specialty_to_df", "all_samples_to_df"]

def remove_trailing_non_alphanumeric(s):
    """
    Removes all non-alphanumeric characters from the end of a string.

    Parameters:
    - s (str): The input string.

    Returns:
    - str: The cleaned string with trailing non-alphanumeric characters removed.
    """
    return re.sub(r'[^a-zA-Z0-9]+$', '', s)

def clean_dictionary_keys(d):
    """
    Cleans the keys of a dictionary by removing trailing non-alphanumeric characters.

    Parameters:
    - d (dict): The input dictionary.

    Returns:
    - dict: The dictionary with cleaned keys.
    """
    return {remove_trailing_non_alphanumeric(key): value for key, value in d.items()}

def remove_url_key(d):
    """
    Removes the 'url' key from a dictionary if it exists.

    Parameters:
    - d (dict): The input dictionary.

    Returns:
    - dict: The dictionary with the 'url' key removed if it existed.
    """
    if isinstance(d, dict) and 'url' in d:
        del d['url']
    return d

def sort_columns_by_completeness(df):
    """
    Sort Pandas DataFrame columns by order of completeness (number of non-null values).

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: DataFrame with columns sorted by completeness.
    """
    completeness = df.notnull().sum()
    sorted_columns = completeness.sort_values(ascending=False).index
    df_sorted = df[sorted_columns]

    return df_sorted

def find_common_keys(dict_list, threshold_to_col=0.25):
    """
    Finds the most common keys across a list of dictionaries.

    Parameters:
    - dict_list (list): A list of dictionaries.
    - threshold_to_col (float): The threshold ratio of dictionaries a key must be in to be considered common.

    Returns:
    - list: A list of the most common keys.
    """
    key_counter = Counter()
    total_dicts = len(dict_list)
    for d in dict_list:
        key_counter.update(d.keys())
    min_count = threshold_to_col * total_dicts
    common_keys = [key for key, count in key_counter.items() if count >= min_count]
    return common_keys

def create_dataframe(dict_list, common_keys):
    """
    Creates a pandas DataFrame from a list of dictionaries, including only the most common keys.

    Parameters:
    - dict_list (list): A list of dictionaries.
    - common_keys (list): A list of the most common keys to include in the DataFrame.

    Returns:
    - pd.DataFrame: The resulting DataFrame with columns sorted by completeness.
    """
    rows = []
    for d in dict_list:
        row = {key: d.get(key, None) for key in common_keys}
        rows.append(row)
    df = pd.DataFrame(rows)
    return (sort_columns_by_completeness(df))

def specialty_to_df(input_list, threshold_to_col=0.25):
    """
    Converts a list of medical transcription samples for a specialty into a pandas DataFrame, including only the most common keys.

    Parameters:
    - input_list (list): A list of dictionaries for a specialty.
    - threshold_to_col (float): The threshold proportion of dictionaries a key must be in to be considered common.

    Returns:
    - pd.DataFrame: The resulting DataFrame with columns sorted by completeness.
    """
    cleaned_list = [clean_dictionary_keys(d) for d in all_samples["Surgery"]]
    common_keys = find_common_keys(cleaned_list, threshold_to_col=threshold_to_col)
    output_df = create_dataframe(cleaned_list, common_keys)
    output_df["sections"] = [remove_url_key(d) for d in cleaned_list]
    return (output_df)

def all_samples_to_df(input_dict, by_specialty=False, threshold_to_col=0.25):
    """
    Converts a dictionary of medical transcription samples grouped by their medical specialties into a single pandas DataFrame.

    Parameters:
    - input_dict (dict): A dictionary of medical transcription samples grouped by their medical specialties.
    - by_specialty (bool): If True, returns a dictionary of pandas DataFrames, one for each medical specialty. Default is False.
    - threshold_to_col (float): The threshold proportion of dictionaries a key must be in to be considered common.

    Returns:
    - dict or pd.DataFrame: If by_specialty is True, returns a dictionary of DataFrames for each medical specialty.
                            Otherwise, returns a single DataFrame containing all samples.
    """

    if by_specialty:
        all_samples_df = {}
        for key, value in input_dict.items():
            all_samples_df[key] = specialty_to_df(value, threshold_to_col=threshold_to_col)
    else:
        samples_list = []
        for key, value_list in input_dict.items():
            samples_list.extend(value_list)
        all_samples_df = specialty_to_df(samples_list, threshold_to_col=threshold_to_col)
    return (all_samples_df)
