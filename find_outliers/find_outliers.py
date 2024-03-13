import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from collections import defaultdict
from sklearn.decomposition import PCA
import time


model = SentenceTransformer("all-MiniLM-L6-v2")


def find_cat_columns(df, threshold=0.1):

    cat_cols = []

    candidates = df.select_dtypes(include=["object", "category"]).columns.tolist()

    for candid in candidates:
        if df[candid].nunique() / df[candid].shape[0] < threshold:
            cat_cols.append(candid)

    return cat_cols


def embed_column(df, column_name, dim=5):
    pca = PCA(n_components=dim)

    unique_values = pd.unique(df[column_name])

    embeddings = [model.encode(value, convert_to_numpy=True) for value in unique_values]

    reduced_embeddings = pca.fit_transform(embeddings)

    embedding_to_value = {
        tuple(embedding): value
        for value, embedding in zip(unique_values, reduced_embeddings)
    }

    column_embeddings = np.array(
        [
            reduced_embeddings[unique_values.tolist().index(value)]
            for value in df[column_name]
        ]
    )

    result = {"embeddings": column_embeddings, "value_map": embedding_to_value}

    return result


import numpy as np


def detect_outliers(embeddings, value_map, std_dev_threshold=3):
    mean_embedding = np.mean(embeddings, axis=0)

    distances = np.linalg.norm(embeddings - mean_embedding, axis=1)

    mean_distance = np.mean(distances)
    std_distance = np.std(distances)

    outliers_mask = distances > (mean_distance + std_dev_threshold * std_distance)

    outlier_embeddings = embeddings[outliers_mask]

    outlier_values_set = {
        value_map[tuple(embedding)] for embedding in outlier_embeddings
    }

    outlier_values_list = list(outlier_values_set)

    return outlier_values_list


def report_outliers(df, embeddings_dim=None, std_dev_threshold=3, cat_threshold=0.1):

    categorical_columns = find_cat_columns(df, cat_threshold)

    n_samples, n_features = df.shape
    if not embeddings_dim:
        embeddings_dim = min(n_samples, n_features)

    for column_name in categorical_columns:
        print(f"Processing column: {column_name}")
        result = embed_column(df, column_name, dim=embeddings_dim)
        embeddings = result["embeddings"]
        value_map = result["value_map"]

        outlier_values = detect_outliers(
            embeddings, value_map, std_dev_threshold=std_dev_threshold
        )

        if outlier_values:
            print(f"Potential errors detected in column '{column_name}':")
            for outlier_value in outlier_values:
                outlier_rows = df.index[df[column_name] == outlier_value].tolist()
                for row in outlier_rows:
                    print(f"  Row {row}: {outlier_value}")
            print("\n")
        else:
            print(f"No potential errors detected in column '{column_name}'.\n")
