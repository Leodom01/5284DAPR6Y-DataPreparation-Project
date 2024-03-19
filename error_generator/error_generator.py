import random

import pandas as pd
import numpy as np


def introduce_missing_values(data: pd.DataFrame, column: str, missing_rate: float) -> pd.DataFrame:
    data.loc[data.sample(frac=missing_rate).index, column] = np.nan
    return data


def introduce_errors(data: pd.DataFrame, columns_rate: float = 0.3, error_rate: float = 0.1) -> pd.DataFrame:
    if len(data.columns) == 0:
        return data

    column_num = int(len(data.columns) * columns_rate)
    column_names = random.sample(tuple(data.columns), column_num)
    for column_name in column_names:
        if data[column_name].dtype in ['int64', 'float64']:
            data = introduce_outliers(data, column_name, error_rate / 3)
        else:
            data = introduce_typos(data, column_name, error_rate / 3)
            data = introduce_missing_values(data, column_name, error_rate / 3)
    return data


def introduce_typos(data: pd.DataFrame, column: str, typo_rate: float = 0.05) -> pd.DataFrame:
    indices = data.sample(frac=typo_rate).index
    for idx in indices:
        original_text = str(data.loc[idx, column])
        if len(original_text) > 1:  # Avoid modifying too short words
            typo_position = random.randint(0, len(original_text) - 2)
            # Simple typo: swap two consecutive characters
            typo_text = (original_text[:typo_position] + original_text[typo_position + 1] +
                         original_text[typo_position] + original_text[typo_position + 2:])
            data.loc[idx, column] = typo_text
    return data


def introduce_outliers(data, column, outlier_rate=0.01, factor=10) -> pd.DataFrame:
    indices = data.sample(frac=outlier_rate).index
    for idx in indices:
        if data[column].dtype in ['int64', 'float64']:
            data.loc[idx, column] *= factor
    return data


if __name__ == "__main__":
    data = pd.read_csv("../datasets/audible/audible_uncleaned.csv")
    data = introduce_errors(data, 0.4, 0.2)
    print(data)

