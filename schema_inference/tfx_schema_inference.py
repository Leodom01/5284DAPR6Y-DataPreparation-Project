import random
from collections import Counter

import pandas as pd
import tensorflow_data_validation as tfdv
from tensorflow_metadata.proto.v0 import schema_pb2

from schema_inference.helper import schema_pb2obj, Schema


class SchemaInference:
    BATCH_SIZE = 100

    def __init__(self, path):
        self.data = pd.read_csv(path)
        self.batch_indices_list = []
        self.feature_count = {column: Counter() for column in self.data.columns}
        self.domain_count = {column: Counter() for column in self.data.columns}
        self.aggregated_schema = None
        self.anomalies = []

    def _count_relevant_data(self, schema: Schema):
        for feature in schema.features:
            name = feature.name

            if name in self.data.columns:
                self.feature_count[name][feature.type] += 1
                self.feature_count[name]['presence_min_fraction'] += 1 if feature.presence.min_fraction else 0
                self.feature_count[name]['presence_min_count'] += 1 if feature.presence.min_count > 0 else 0

        for domain in schema.domains:
            self.domain_count[domain.name][frozenset(domain.values)] += 1

    def _partition_data(self, seed=42):
        random.seed(seed)

        indices = list(self.data.index)
        random.shuffle(indices)
        self.batch_indices_list = []

        while indices:
            if len(indices) >= self.BATCH_SIZE:
                subset = indices[:self.BATCH_SIZE]
                self.batch_indices_list.append(subset)
                indices = indices[self.BATCH_SIZE:]
            else:
                self.batch_indices_list.append(indices)
                indices = []

    def _infer_schemas_from_batches(self):
        # Infer the schema
        for batch_indices in self.batch_indices_list:
            batch = self.data.iloc[batch_indices]
            stats = tfdv.generate_statistics_from_dataframe(batch)
            schema_pb = tfdv.infer_schema(stats)
            schema = schema_pb2obj(schema_pb)
            self._count_relevant_data(schema)

    def _aggregate_schemas(self):
        ...

    def infer_schema(self) -> schema_pb2.Schema:
        self._partition_data()
        self._infer_schemas_from_batches()
        self._aggregate_schemas()
        return self.aggregated_schema

    def detect_anomalies(self):
        ...

        # return


# Example usage
if __name__ == '__main__':
    # Load data
    # path = '../datasets/carprices/car_prices.csv'
    data_path = '../datasets/salaries/ds_salaries.csv'

    schema_inferer = SchemaInference(data_path)
    schema_inferer._partition_data(seed=42)
    aggregated_schema = schema_inferer.infer_schema()
    # print(aggregated_schema)
    # print(schema_pb2obj(aggregated_schema))
    # tfdv.display_schema(schema=aggregated_schema)
