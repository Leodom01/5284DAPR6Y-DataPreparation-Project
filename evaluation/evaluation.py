import os
import pandas as pd
from metrics_v2 import DataProfiler

def load_dataset(folder_path):
    datasets = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.csv'):
            dataset = pd.read_csv(file_path)
            datasets.append(dataset)
    return pd.concat(datasets, ignore_index=True)


def remove_outliers(dataset):
    # Aynaz method
    pass


def remove_anomalies(dataset, schema):
    # Implement your anomaly detection logic here
    pass

def get_schema_wo_LLM(dataset):
    #Standard schema generation without LLM
    pass

def get_schema_w_LLM(dataset):
    #Improved schema generation with LLM
    pass

def main():

    dp =DataProfiler()

    datasets_folder = 'datasets'
    for folder_name in os.listdir(datasets_folder):
        folder_path = os.path.join(datasets_folder, folder_name)
        if os.path.isdir(folder_path):
            dataset = load_dataset(folder_path)

            # Starting quality
            starting_quality = dp.compute_for(batch=dataset)

            # Outlier remove quality
            dataset_o = remove_outliers(dataset)
            o_qty = dp.compute_for(dataset_o)

            # Get original dataset schema without LLM
            original_schema = get_schema_wo_LLM(dataset)

            # Schema detected anomalies
            a_wo_llm = remove_anomalies(dataset, original_schema)
            a_wo_llm_qty = dp.compute_for(a_wo_llm)

            # Get original dataset schema with LLM improvement
            improved_schema = get_schema_w_LLM(dataset)

            # Improved schema detected anomalies
            a_w_llm = remove_anomalies(dataset, improved_schema)
            a_w_llm_qty = dp.compute_for(a_w_llm)

            # End to end, outliers and anomalies improved
            schema = get_schema_w_LLM(dataset_o)
            pipeline_o_a = remove_anomalies(dataset_o, schema)
            pipeline_o_a_qty = dp.compute_for(pipeline_o_a)

            # End to end, anomalies improved and outliers
            schema = get_schema_w_LLM(dataset)
            anomalies_free = remove_anomalies(dataset, schema)
            pipeline_a_o = remove_outliers(anomalies_free)
            pipeline_a_o_qty = dp.compute_for(pipeline_a_o)

            # Print or log the results
            print(f"Dataset: {folder_name}")
            print(f"Starting quality: {starting_quality}")
            print(f"Outlier remove quality: {o_qty}")
            print(f"Default schema anomalies removed quality: {a_wo_llm_qty}")
            print(f"Improved schema anomalies removed quality: {a_w_llm_qty}")
            print(f"Full pipeline quality (outlier first): {pipeline_o_a_qty}")
            print(f"Full pipeline quality (anomalies first): {pipeline_a_o_qty}")
            print("=" * 50)


if __name__ == "__main__":
    main()
