import math
from collections import Counter

import pandas as pd
import tensorflow_data_validation as tfdv
from tensorflow_metadata.proto.v0 import schema_pb2

from pb_parser import schema_pb2obj, Schema, TYPE_MAPPING
from csv_parser import validate_csv_against_schema, count_csv_lines_and_column_names
from helper import shuffle_csv_rows
from schema_rules import aggregate, aggregate_presence_min_count, aggregate_presence_min_fraction


class SchemaInference:
    def __init__(self, path, num_lines, column_names, batch_size, aggregation_threshold):
        self.path = path
        self.num_lines = num_lines
        self.columns = column_names
        self.batch_size = batch_size
        self.aggregation_threshold = aggregation_threshold
        self.feature_type_count = {column: Counter() for column in column_names}
        self.feature_presence_count = {column: Counter() for column in column_names}
        self.domain_count = {column: Counter() for column in column_names}
        self.aggregated_schema = None
        self.anomalies = []

    def _count_relevant_data(self, schema: Schema):
        for feature in schema.features:
            name = feature.name

            if name in self.columns:
                self.feature_type_count[name][feature.type] += 1
                self.feature_presence_count[name]['min_fraction'] += 1 if feature.presence.min_fraction else 0
                self.feature_presence_count[name]['min_count'] += 1 if feature.presence.min_count > 0 else 0

        for domain in schema.domains:
            self.domain_count[domain.name][frozenset(domain.values)] += 1

    def _infer_schema_from_csv(self):
        chunksize = math.floor(self.num_lines * self.batch_size)
        for batch in pd.read_csv(self.path, chunksize=chunksize):
            stats = tfdv.generate_statistics_from_dataframe(batch)
            schema_pb = tfdv.infer_schema(stats, max_string_domain_size=chunksize)
            schema = schema_pb2obj(schema_pb)
            self._count_relevant_data(schema)


    def _aggregate_schemas(self):
        features = []
        domains= []

        min_size = math.ceil(int(self.num_lines * self.batch_size * self.aggregation_threshold))

        for column in self.columns:
            features.append(
                schema_pb2.Feature(
                    name=column,
                    type=TYPE_MAPPING[aggregate(
                        'type',
                        self.feature_type_count[column],
                        min_size
                    )],
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

            if len(self.domain_count[column]) > 0:
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

        aggregated_schema_pb = schema_pb2.Schema()

        aggregated_schema_pb.feature.extend(features)
        aggregated_schema_pb.string_domain.extend(domains)

        self.aggregated_schema =schema_pb2obj(aggregated_schema_pb)

    def infer_schema(self) -> schema_pb2.Schema:
        self._infer_schema_from_csv()
        self._aggregate_schemas()
        return self.aggregated_schema

    def detect_anomalies(self, path: str, ignored_domains=None):
        self.anomalies = validate_csv_against_schema(self.aggregated_schema, path, ignored_domains=ignored_domains)


# Example usage
if __name__ == '__main__':
    og_data_path = '../datasets/carprices/car_prices.csv'
    # og_data_path = '../datasets/salaries/ds_salaries.csv'
    # og_data_path = '../datasets/test.csv'

    # PARAMS
    # Shuffle params
    shuffle = False
    seed = 42
    shuffled_data_path = '../datasets/shuffled/test.csv'
    data_path = shuffle_csv_rows(og_data_path, shuffled_data_path, seed=seed) if shuffle else og_data_path

    # Inference params
    num_lines, column_names = count_csv_lines_and_column_names(data_path)
    BATCH_SIZE = 0.2
    AGGREGATION_THRESHOLD = 0.9

    # Anomaly params
    ignored_domains = [
        #'year', 'make', 'model', 'trim', 'body',
        #'transmission',
        'vin',
        #'state',
        # 'condition',
        # 'odometer',
        # 'color',
        #'interior',
        'seller',
         # 'mmr',
        #'sellingprice',
        'saledate'
    ]

    #####

    # Initialize Schema Inferer
    schema_inferer = SchemaInference(data_path, num_lines, column_names, BATCH_SIZE, AGGREGATION_THRESHOLD)

    # Infer schema at schema_inferer.aggregated_schema
    schema_inferer.infer_schema()

    # Infer schema at schema_inferer.anomalies
    schema_inferer.detect_anomalies(data_path, ignored_domains=ignored_domains)

    # Print
    data = pd.read_csv(data_path)
    anomaly_indices = schema_inferer.anomalies
    print(data.shape)
    print("anomalies:", len(anomaly_indices))
    # print(data.iloc[anomaly_indices].head())


