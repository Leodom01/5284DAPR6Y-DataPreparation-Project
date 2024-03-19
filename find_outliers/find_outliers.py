import pandas as pd
import numpy as np
from sklearn.cluster import OPTICS
import spacy



model = spacy.load("en_core_web_sm")



# ------------------------------------------------------------------------------------
def get_categories(df, threshold = 0.1):
    
    candidates = df.select_dtypes(include=["object", "category"]).columns.tolist()

    for candid in candidates:
        if df[candid].nunique() / df[candid].shape[0] < threshold:
            cat_cols.append(candid)

    return cat_cols
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------

def embed_categorical_column(df, column_name):
    
    unique_values = df[column_name].dropna().unique()

    embeddings = []
    reverse_mapping = {}
    
    for value in unique_values:
        embedding = model(str(value)).vector
        embeddings.append(embedding)
        reverse_mapping[tuple(embedding)] = str(value)
    
    embeddings_array = np.array(embeddings)

    result = {
        'embeddings': embeddings_array,
        'reverse_mapping': reverse_mapping
    }
    
    return result
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
def identify_noise_vectors_and_values(df, column_name):
    embedding_result = embed_categorical_column(df, column_name)
    embeddings = embedding_result['embeddings']
    reverse_mapping = embedding_result['reverse_mapping']
    
    optics = OPTICS(min_samples=3, xi=.07, min_cluster_size=.05)
    optics.fit(embeddings)
    
    noise_flags = optics.labels_ == -1
    
    noise_values = []
    
    for i, is_noise in enumerate(noise_flags):
        if is_noise:
            embedding_tuple = tuple(embeddings[i])
            if embedding_tuple in reverse_mapping:
                noise_values.append(reverse_mapping[embedding_tuple])
    
    print("Original values of noise vectors:", noise_values)
