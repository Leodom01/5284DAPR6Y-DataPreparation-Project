import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")

def is_categorical(df, column_name, threshold = 0.1):

    if str(df[column_name].dtype) in {'object'}:
        nunique = df[column_name].nunique()
        if nunique/df[column_name].shape[0] <= threshold:
            return True
    return False


def is_numerical(df, column_name):
    return pd.api.types.is_numeric_dtype(df[column_name])
    

def embed_column(df, column_name):


    df[column_name] = df[column_name].apply(lambda x: x.lower() if isinstance(x, str) else x)

    value_counts = df[column_name].value_counts().to_dict()

    unique_values = list(value_counts.keys())
    value_to_embedding = {value: model.encode(value, convert_to_numpy=True) for value in unique_values}
    
    embeddings = np.array([value_to_embedding[value] for value in unique_values])
    embedding_counts = [value_counts[value] for value in unique_values]
    
    embedding_to_value = {tuple(embedding): value for value, embedding in value_to_embedding.items()}
    
    return {
        'embeddings': embeddings,
        'embedding_counts': embedding_counts,
        'embedding_to_value': embedding_to_value
    }


def euclidean_distance(X, Y):
    return np.sqrt(np.sum((X - Y) ** 2))


def identify_categorical_outliers(df, column_name, threshold = 1):
    
    result = embed_column(df, column_name)
    
    embeddings = result['embeddings']
    embedding_counts = np.array(result['embedding_counts'])
    embedding_to_value = result['embedding_to_value']
    
    total_weight = sum(embedding_counts)
    weighted_mean = np.sum(embeddings * embedding_counts[:, None], axis=0) / total_weight
    
    outliers = []
    
    for index, (embedding, count) in enumerate(zip(embeddings, embedding_counts)):

        other_weights = total_weight - count
        other_weighted_mean = (np.sum(embeddings * embedding_counts[:, None], axis=0) - embedding * count) / other_weights
        
        distance = euclidean_distance(other_weighted_mean, embedding)
                
        if distance > threshold: 
            outliers.append(embedding_to_value[tuple(embedding)])

    outlier_indices = df[df[column_name].isin(outliers)].index
    return outlier_indices


def identify_numerical_outliers(df, column_name, num_std = 3):

    mean = df[column_name].mean()
    std = df[column_name].std()

    outlier_indices = df[np.abs(df[column_name] - mean) > num_std * std].index
            
    return outlier_indices


def outliers_rate(df, column_name):

    nentries = df.shape[0]
    
    if is_categorical(df, column_name):
        return len(identify_categorical_outliers(df, column_name)) / nentries

    elif is_numerical(df, column_name):
        return len(identify_numerical_outliers(df, column_name)) / nentries
        
    return


def outliers(df, column_name):

    if is_categorical(df, column_name):
        return identify_categorical_outliers(df, column_name)

    elif is_numerical(df, column_name):
        return identify_numerical_outliers(df, column_name)

    return
