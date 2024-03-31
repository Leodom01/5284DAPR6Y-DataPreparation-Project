import time

import pandas as pd
import tensorflow_data_validation as tfdv

from pb_parser import Domain, schema_pb2obj
from schema_inference import SchemaInference


def domain_difference(domains1: list[Domain], domains2: list[Domain]) -> pd.DataFrame:
    domains1 = sorted(domains1, key=lambda x: x.name)
    domains2 = sorted(domains2, key= lambda x: x.name)

    if [d.name for d in domains1] != [d.name for d in domains2]:
        raise ValueError()

    df = pd.DataFrame(columns=[d.name for d in domains1])

    for domain1, domain2 in zip(domains1, domains2):
        df[domain1.name] = len(domain1.values) - len(domain2.values)

    return df


def check_performance(path):

    aggr_start = time.time()

    schema_inferer = SchemaInference(path)
    aggregated_schema = schema_inferer.infer_schema()
    aggr_end = time.time()#
    aggr_time = aggr_end - aggr_start

    og_start = time.time()
    og_stats = tfdv.generate_statistics_from_csv(path)
    og_schema_pb = tfdv.infer_schema(og_stats)
    og_end = time.time()
    og_time = og_end - og_start

    end = time.time()
    # print(DeepDiff(schema_pb2obj(aggregated_schema).domains, schema_pb2obj(og_schema_pb).domains, ignore_order=True))
    print(domain_difference(schema_pb2obj(aggregated_schema).domains, schema_pb2obj(aggregated_schema).domains))
    print((aggr_time - og_time) / og_time)

if __name__ == '__main__':
    data_path_1 = '../datasets/carprices/car_prices.csv'
    data_path_2 = '../datasets/kickstarter/ks-projects-201801.csv'

    check_performance(data_path_1)
    print("")
    check_performance(data_path_2)

