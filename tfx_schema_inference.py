import pandas as pd
import tensorflow_data_validation as tfdv


def schema_inference(data: pd.DataFrame):
    # Infer the schema
    stats = tfdv.generate_statistics_from_dataframe(data)
    # stats = tfdv.generate_statistics_from_csv(path)
    tfdv.visualize_statistics(stats)
    # print(stats)
    schema = tfdv.infer_schema(stats)
    return schema


# Example usage
if __name__ == '__main__':
    path = 'datasets/carprices/car_prices.csv'
    #path = 'datasets/salaries/ds_salaries.csv'
    data = pd.read_csv(path)
    schema = schema_inference(data)
    # print(schema)
    # tfdv.display_schema(schema=schema)
