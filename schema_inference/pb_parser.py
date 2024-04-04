from __future__ import annotations

from dataclasses import dataclass

import tensorflow_data_validation as tfdv
import numpy as np
import pandas as pd


TYPE_MAPPING = {
    0: 'TYPE_UNKNOWN',
    1: 'BYTES',
    2: 'INT',
    3: 'FLOAT',
    4: 'STRUCT',
}


def proto2dict(proto, fields):
    proto_dict = dict(proto.ListFields())
    return dict((k, proto_dict.get(hsh)) for k, hsh in proto.DESCRIPTOR.fields_by_name.items() if k in fields)

def schema_pb2obj(proto):
    schema_fields = ['feature', 'string_domain']
    feature_fields = ['name', 'type', 'presence']
    presence_fields = ['min_fraction', 'min_count']
    domain_fields = ['name', 'value']

    features: list[Feature] = []
    domains: list[Domain] = []

    schema_dict = proto2dict(proto, schema_fields)

    for feature in schema_dict['feature']:
        feature_dict = proto2dict(feature, feature_fields)
        presence_dict = proto2dict(feature_dict['presence'], presence_fields)
        features.append(
            Feature(
                name=feature_dict['name'],
                type=feature_dict['type'],
                presence=Presence(
                    min_fraction=presence_dict['min_fraction'] if 'min_fraction' in presence_dict else None,
                    min_count=presence_dict['min_count'] if 'min_count' in presence_dict else 0
                )
            )
        )

    if schema_dict['string_domain']:
        for domain in schema_dict['string_domain']:
            domain_dict = proto2dict(domain, domain_fields)
            domains.append(
                Domain(
                    name=domain_dict['name'],
                    values=set(domain_dict['value'])
                )
            )

    return Schema(features=features, domains=domains)


@dataclass
class Presence:
    min_fraction: float | None
    min_count: int


@dataclass
class Feature:
    name: str
    type: int
    presence: Presence


@dataclass
class Domain:
    name: str
    values: set[str]


@dataclass
class Schema:
    features: list[Feature]
    domains: list[Domain]


# Example usage
if __name__ == '__main__':
    columns = ['int_categorical', 'int_continuous', 'float_categorical', 'float_continuous', 'string_domain1',
               'string_domain2']

    # Dataframe 1
    data1 = {
        'int_categorical': np.random.randint(0, 3, size=10),  # Random integer categorical values (0, 1, 2)
        'int_continuous': np.random.randint(1, 100, size=10),  # Random integer continuous values
        'float_categorical': np.random.rand(10),  # Random float categorical values
        'float_continuous': np.random.rand(10),  # Random float continuous values
        'string_domain1': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],  # String domain values
        'string_domain2': ['apple', 'banana', 'cherry', 'date', 'elderberry', 'fig', 'grape', 'honeydew', 'kiwi',
                           'lemon']  # String domain values
    }
    df1 = pd.DataFrame(data1, columns=columns)

    # Dataframe 2 (with differences and missing values)
    data2 = {
        'int_categorical': np.random.randint(0, 3, size=10),  # Random integer categorical values (0, 1, 2)
        'int_continuous': np.random.randint(1, 100, size=10),  # Random integer continuous values
        'float_categorical': np.random.rand(10),  # Random float categorical values
        'float_continuous': np.random.rand(10),  # Random float continuous values
        # 'string_domain1': ['A', 'B', 'C', np.nan, 'E', 'F', 'G', 'H', 'I', 'K'],  # String domain values with a missing value and a difference
        'string_domain1': [np.nan for _ in range(10)],
        'string_domain2': ['apple', 'banana', 'cherry', 'date', 'elderberry', 'fig', 'grape', 'honeydew', 'kiwi',
                           'lime']  # String domain values with a difference
    }
    df2 = pd.DataFrame(data2, columns=columns)

    stats1 = tfdv.generate_statistics_from_dataframe(df1)
    schema1 = tfdv.infer_schema(stats1)

    stats2 = tfdv.generate_statistics_from_dataframe(df2)
    schema2 = tfdv.infer_schema(stats2)

    schema1_dict = proto2dict(schema1)
    schema2_dict = schema_pb2obj(schema2)

    print(schema1_dict)
    print(schema2_dict)
