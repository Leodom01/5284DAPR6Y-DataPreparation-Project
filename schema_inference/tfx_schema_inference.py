import random

import pandas as pd
import tensorflow_data_validation as tfdv


class SchemaInference:
    BATCH_SIZE = 5000

    def __init__(self, path):
        self.data = pd.read_csv(path)
        self.batch_indices_list = []
        self.schemas = []
        self.aggregated_schema = None
        self.anomalies = []

    def partition_data(self, seed=None):
        if seed is not None:
            random.seed(seed)

        indices = list(self.data.index)
        random.shuffle(indices)  # Shuffle the indices randomly
        self.batch_indices_list = []

        while indices:
            if len(indices) >= self.BATCH_SIZE:
                subset = indices[:self.BATCH_SIZE]
                self.batch_indices_list.append(subset)
                indices = indices[self.BATCH_SIZE:]
            else:
                self.batch_indices_list.append(indices)
                indices = []

        return

    def infer_schema(self):
        # Infer the schema
        for batch_indices in self.batch_indices_list:
            batch = self.data.iloc[batch_indices]
            stats = tfdv.generate_statistics_from_dataframe(batch)
        # stats = tfdv.generate_statistics_from_csv(path)
            tfdv.visualize_statistics(stats)
        # print(stats)
            schema = tfdv.infer_schema(stats)
            return schema

        #return


# Example usage
if __name__ == '__main__':
    # Load data
    # path = '../datasets/carprices/car_prices.csv'
    data_path = '../datasets/salaries/ds_salaries.csv'

    schema_inferer = SchemaInference(data_path)
    schema_inferer.partition_data(seed=42)
    schema = schema_inferer.infer_schema()
    # print(schema)
    # tfdv.display_schema(schema=schema)
