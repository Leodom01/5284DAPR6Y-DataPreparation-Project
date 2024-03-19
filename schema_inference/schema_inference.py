import random
from collections import Counter

import pandas as pd
import tensorflow_data_validation as tfdv
from tensorflow_metadata.proto.v0 import schema_pb2

from pb_parser import schema_pb2obj, Schema
from schema_rules import aggregate, aggregate_presence_min_count, aggregate_presence_min_fraction

BATCH_SIZE = 5
AGGREGATION_THRESHOLD = 0.9


class SchemaInference:
    def __init__(self, path):
        self.data = pd.read_csv(path)
        self.batch_indices_list = []
        self.feature_type_count = {column: Counter() for column in self.data.columns}
        self.feature_presence_count = {column: Counter() for column in self.data.columns}
        self.domain_count = {column: Counter() for column in self.data.columns}
        self.aggregated_schema = schema_pb2.Schema()
        self.anomalies = []

    def _count_relevant_data(self, schema: Schema):
        for feature in schema.features:
            name = feature.name

            if name in self.data.columns:
                self.feature_type_count[name][feature.type] += 1
                self.feature_presence_count[name]['min_fraction'] += 1 if feature.presence.min_fraction else 0
                self.feature_presence_count[name]['min_count'] += 1 if feature.presence.min_count > 0 else 0

        for domain in schema.domains:
            self.domain_count[domain.name][frozenset(domain.values)] += 1

    def _partition_data(self, seed=42):
        random.seed(seed)

        indices = list(self.data.index)
        random.shuffle(indices)
        #self.batch_indices_list = [[i for i in range(0,10)], [i for i in range(10, 20)]]

        while indices:
            if len(indices) >= BATCH_SIZE:
                subset = indices[:BATCH_SIZE]
                self.batch_indices_list.append(subset)
                indices = indices[BATCH_SIZE:]
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
        features = []
        domains= []

        min_size = int(len(self.batch_indices_list) * AGGREGATION_THRESHOLD) + 1

        for column in self.data.columns:
            features.append(
                schema_pb2.Feature(
                    name=column,
                    type=aggregate(
                        'type',
                        self.feature_type_count[column],
                        min_size
                    ),
                    presence=schema_pb2.FeaturePresence(
                        min_fraction=aggregate_presence_min_fraction(
                            self.feature_presence_count[column]['min_fraction'],
                            min_size
                        ),
                        min_count=aggregate_presence_min_count(
                            self.feature_presence_count[column]['min_count'],
                            min_size
                        )
                    )
                )
            )

            domains.append(
                schema_pb2.StringDomain(
                    name=column,
                    value=aggregate(
                        'domain',
                        self.domain_count[column],
                        min_size
                    )
                )
            )

        self.aggregated_schema.feature.extend(features)
        self.aggregated_schema.string_domain.extend(domains)

    def infer_schema(self) -> schema_pb2.Schema:
        self._partition_data()
        self._infer_schemas_from_batches()
        self._aggregate_schemas()
        return self.aggregated_schema

    def detect_anomalies(self, path: str):
        stats = tfdv.generate_statistics_from_csv(path)
        self.anomalies = tfdv.validate_statistics(stats, schema=self.aggregated_schema)
        print(self.anomalies)


# Example usage
if __name__ == '__main__':
    # Load data
    # path = '../datasets/carprices/car_prices.csv'
    #data_path = '../datasets/salaries/ds_salaries.csv'
    data_path= '../datasets/test.csv'
    # for chunk in pd.read_csv(data_path, chunksize=10):
    #     # Process each batch (chunk) of data
    #     print(chunk)
    #     stats = tfdv.generate_statistics_from_dataframe(chunk)
    #     schema = tfdv.infer_schema(stats)
    #     print(schema)

    schema_inferer = SchemaInference(data_path)
    aggregated_schema = schema_inferer.infer_schema()
    schema_inferer.detect_anomalies(data_path)
    # print(aggregated_schema)
    # print(schema_pb2obj(aggregated_schema))
    # tfdv.display_schema(schema=aggregated_schema)
