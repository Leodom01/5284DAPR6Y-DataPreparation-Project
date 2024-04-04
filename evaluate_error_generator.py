import os

import pandas as pd

from dotenv import load_dotenv
from evaluation.ErrorGenerator import ErrorGenerator
from find_outliers.find_outliers import outliers as find_semantic_outliers
from llm.syntax_error_detection import Syntax_error_detection
from schema_inference.helper import shuffle_csv_rows
from schema_inference.schema_inference import infer_schema_and_detect_anomalies

from pipeline import run_pipeline

load_dotenv()

# Path to the data directory
DATA_DIRS = {
    'kickstarter': {
        'path': './datasets/kickstarter/ks-projects-201801.csv',
        'column_types': ['_', '_', '_', '_', 'number', 'date',
       '_', 'datetime', '_', '_', '_', '_',
       'number', 'number', 'number'],
    }
    # 'car_prices': './datasets/carprices/car_prices.csv'
}


if __name__ == '__main__':
    for k, dataset in DATA_DIRS.items():
        # Optional: shuffle the data
        # Shuffle params
        # seed = 42
        # shuffled_data_path = '../datasets/shuffled/car_prices.csv'
        #shuffle_csv_rows(data_path, shuffled_data_path, seed=seed)

        data_df = pd.read_csv(dataset['path'])
        # metrics

        error_data, error_rows = ErrorGenerator().generate_errors(
            dataset_path=dataset['path'], dataset_columns=dataset['column_types']
        )
        # metrics

        anomalies = run_pipeline(data_df, dataset['path'])
        # metrics

        # 1. how many errors detected from error gen?
        # TODO: return % by type of error
        #  % of detected anomalies
        # print('Detected rows:', len(detected_rows)/len/(error_rows))

        # metrics after removing detected rows

        # save csv for metrics (3 rows)
        # csv for % detected row by error type and int total
        # csv for % detected rpws by feature



