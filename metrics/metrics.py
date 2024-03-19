from __future__ import annotations

import math

import numpy as np
import pandas as pd

TEXTUAL_TYPE_THRESHOLD = 0.01


def metric_name(column: str, metric: str) -> str:
    return column + "_" + metric


def calculate_index_of_peculiarity(trigram_counts) -> float:
    xy_count = trigram_counts.get('xy', 0)
    yz_count = trigram_counts.get('yz', 0)
    xyz_count = trigram_counts.get('xyz', 1)  # Add smoothing to handle zero counts

    index = 0.5 * (math.log(xy_count) + math.log(yz_count)) - math.log(xyz_count)
    return index


def calculate_column_peculiarity(column: pd.Series, size: int) -> list[float] | None:
    # Detect if column is textual
    if not column.dtype in ["object"]:
        return None

    # Calculate the ratio of distinct values
    distinct_ratio = len(column.unique()) / size
    if distinct_ratio >= TEXTUAL_TYPE_THRESHOLD:
        return None

    # join all the values in the column
    sentence = " ".join(column)
    trigrams = [sentence[i:i + 3] for i in range(len(sentence) - 2)]
    trigram_counts = {trigram: sentence.count(trigram) for trigram in trigrams}
    indices = [calculate_index_of_peculiarity(trigram_counts) for trigram in trigrams]
    peculiarity_score: float = math.sqrt(sum(index ** 2 for index in indices) / len(trigrams))
    return peculiarity_score


def calculate_metrics(dataset: pd.DataFrame) -> pd.DataFrame:
    metrics: pd.DataFrame = pd.DataFrame(columns=["metric_name", "value"])
    metric_names: list = []
    values: list = []

    # size of the dataset
    size = len(dataset)
    metric_names.append("size")
    values.append(size)

    # statistics for numeric data types
    stats: pd.DataFrame = dataset.describe(include="all")
    for column in dataset.columns:
        for index, row in stats.iterrows():
            if index == "count":
                metric_names.append(metric_name(column, "completeness"))
                values.append(row[column] / size)
            if index in ["unique"]:
                metric_names.append(metric_name(column, "distinct_ratio"))
                values.append(row[column] / size)
            if index in ["freq"]:
                metric_names.append(metric_name(column, "top_ratio"))
                values.append(row[column] / size)
            else:
                metric_names.append(metric_name(column, str(index)))
                values.append(row[column])

        peculiarity_score: float | None = calculate_column_peculiarity(dataset[column], size)
        if peculiarity_score is not None:
            metric_names.append(metric_name(dataset[column], "peculiarity"))
            values.append(peculiarity_score)

    # TODO: include more complex metrics, e.g. distribution of values, feature_correlation, data_drift

    metrics["metric_name"] = metric_names
    metrics["value"] = values
    sorted_metrics = metrics.sort_values(by="metric_name")

    return sorted_metrics



# Example usage
if __name__ == '__main__':
    path = '../datasets/carprices/car_prices.csv'
    data = pd.read_csv(path)
    data_metrics = calculate_metrics(data)
    print(data_metrics)
