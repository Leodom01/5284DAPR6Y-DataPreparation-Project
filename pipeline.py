import os

from dotenv import load_dotenv
from find_outliers.find_outliers import outliers as find_semantic_outliers
from llm.syntax_error_detection import Syntax_error_detection
from schema_inference.schema_inference import infer_schema_and_detect_anomalies

load_dotenv()


def run_pipeline(data_df, data_path):
    print(f'Run pipeline for {os.path.basename(data_path)}...')

    # PARAMS
    API_KEY= os.environ.get('API_KEY')
    BATCH_SIZE = 0.05
    AGGREGATION_THRESHOLD = 0.9
    DISTINCT_THRESHOLD = 0.8


    anomalies = {
        'semantic_outliers': [],
        'syntactic_outliers': None,
        'schema_anomalies': None
    }

    print('Find semantic outliers...')
    # semantic outliers
    for column in data_df.columns:
        anomalies['semantic_outliers'].append(find_semantic_outliers(data_df, column))

    # regex
    print('Find syntactic outliers')
    sed = Syntax_error_detection(api_key=API_KEY)
    syntax_errors = sed.find_syntax_errors(data_df, "chatgpt")
    anomalies['syntactic_outliers'] = syntax_errors

    # Schema anomalies
    print('Find anomalies using aggregated schema...')
    schema, schema_anomalies = infer_schema_and_detect_anomalies(data_path, BATCH_SIZE, AGGREGATION_THRESHOLD, DISTINCT_THRESHOLD)
    anomalies['schema_anomalies'] = schema_anomalies

    return anomalies, schema
