import pandas as pd


def metric_name(column: str, metric: str) -> str:
    return column + "_" + metric


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
    for index, row in stats.iterrows():
        for column in dataset.columns:
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

    # TODO: include more complex metrics, e.g. distribution of values, feature_correlation, data_drift

    metrics["metric_name"] = metric_names
    metrics["value"] = values
    sorted_metrics = metrics.sort_values(by="metric_name")

    return sorted_metrics


# Example usage
if __name__ == '__main__':
    path = 'datasets/carprices/car_prices.csv'
    data = pd.read_csv(path)
    data_metrics = calculate_metrics(data)
    print(data_metrics)
