import os

import pandas as pd

from dotenv import load_dotenv
from evaluation.ErrorGenerator import ErrorGenerator
from find_outliers.find_outliers import outliers as find_semantic_outliers
from llm.syntax_error_detection import Syntax_error_detection
from metrics.metrics import DataProfiler
from schema_inference.helper import shuffle_csv_rows
from schema_inference.schema_inference import infer_schema_and_detect_anomalies

from pipeline import run_pipeline

load_dotenv()

# Path to the data directory
DATA_DIRS = {
    # 'kickstarter': {
    #     'path': './datasets/kickstarter/ks-projects-201801.csv',
    #     'column_types': ['_', '_', '_', '_', 'number', 'date',
    #    '_', 'datetime', '_', '_', '_', '_',
    #    'number', 'number', 'number'],
    # }
    'test':{
        'path': './datasets/test.csv',
        'column_types': ['_', 'number', '_']
    }

    # 'car_prices': './datasets/carprices/car_prices.csv'
}


def get_rows_from_anomalies(anomalies):
    rows = []
    for _, d in anomalies.items():
        for _, l in d.items():
            if isinstance(l, list):
                rows.extend(l)

    return rows


def detected_errors_by_type(error_rows, anomalies):
    # merge all
    ...


def compute_metrics(data_df):
    dp = DataProfiler()
    values, metrics = dp.compute_for(data_df, return_labels=True)
    return metrics, values


if __name__ == '__main__':
    for k, dataset in DATA_DIRS.items():
        # Optional: shuffle the data
        # Shuffle params
        # seed = 42
        # shuffled_data_path = '../datasets/shuffled/car_prices.csv'
        #shuffle_csv_rows(data_path, shuffled_data_path, seed=seed)

        metrics_dict = {}

        # Original data
        data_df = pd.read_csv(dataset['path'])
        metrics, original_values = compute_metrics(data_df)
        metrics_dict['original'] = original_values

        # Error data
        error_df, error_rows = ErrorGenerator().generate_errors(
            dataset_path=dataset['path'], dataset_columns=dataset['column_types']
        )
        _, error_values = compute_metrics(error_df)
        metrics_dict['error_data'] = error_values

        anomalies, schema = run_pipeline(data_df, dataset['path'])
        anomaly_rows = get_rows_from_anomalies(anomalies)
        _, without_anomaly_values = compute_metrics(data_df[~data_df.index.isin(anomaly_rows)])
        metrics_dict['without_anomalies'] = without_anomaly_values

        # 1. how many errors detected from error gen?
        # TODO: return % by type of error
        #  % of detected anomalies
        # print('Detected rows:', len(detected_rows)/len/(error_rows))


        # Metri
        metrics_df = pd.DataFrame.from_dict(metrics_dict, orient='index', columns=metrics)
        metrics_df.to_csv(k + '_evaluation_error_generation.csv')
        # csv for % detected row by error type and int total
        # csv for % detected rpws by feature



