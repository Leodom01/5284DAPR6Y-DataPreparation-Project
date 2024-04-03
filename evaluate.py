import pandas as pd

from evaluation.ErrorGenerator import ErrorGenerator
from find_outliers.find_outliers import outliers as find_semantic_outliers
from llm.syntax_error_detection import Syntax_error_detection
from schema_inference.helper import shuffle_csv_rows
from schema_inference.schema_inference import infer_schema_and_detect_anomalies

# Path to the data directory
DATA_DIRS = {
    # 'salaries': {
    #     'path': './datasets/salaries/ds_salaries.csv',
    #     columns
    # }
    'car_prices': './datasets/carprices/car_prices.csv'
}



def run_pipeline(data_df, data_path):
    # PARAMS
    API_KEY= ''
    BATCH_SIZE = 0.05
    AGGREGATION_THRESHOLD = 0.9
    DISTINCT_THRESHOLD = 0.8


    anomalies = {
        'semantic_outliers': [],
        'syntactic_outliers': None,
        'schema_anomalies': None
    }

    # semantic outliers
    for column in data_df.columns:
        anomalies['semantic_outliers'].append(find_semantic_outliers(data_df, column))

    # regex
    sed = Syntax_error_detection(api_key=API_KEY)
    syntax_errors = sed.find_syntax_errors(data_df, "chatgpt")
    anomalies['syntactic_outliers'] = syntax_errors

    # Schema anomalies
    _, schema_anomalies = infer_schema_and_detect_anomalies(data_path, BATCH_SIZE, AGGREGATION_THRESHOLD, DISTINCT_THRESHOLD)
    anomalies['schema_anomalies'] = schema_anomalies

    return anomalies


if __name__ == '__main__':
    for k, data_path in DATA_DIRS.items():
        # Optional: shuffle the data
        # Shuffle params
        # seed = 42
        # shuffled_data_path = '../datasets/shuffled/car_prices.csv'
        #shuffle_csv_rows(data_path, shuffled_data_path, seed=seed)

        data_df = pd.read_csv(data_path)
        # metrics

        # TODO: Error generator
        error_data, error_rows = ErrorGenerator.generate_errors(data_path, dataset_columns=[])
        # metrics

        anomalies = run_pipeline(data_df, data_path)
        # metrics

        # 1. how many errors detected from error gen?
        # TODO: return % by type of error, and % of detected anomalies
        # print('Detected rows:', len(detected_rows)/len/(error_rows))


        # 2. auto ml model on whole dataset and data without detected rows
        # metrics

