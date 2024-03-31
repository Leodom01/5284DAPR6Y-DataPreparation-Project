# Improved TFX Schema Inference
Example usage found in schema_inference.py

### Set parameters
- BATCH_SIZE(0.05)
- AGGREGATION_THRESHOLD(0.9)
- DISTINCT_THRESHOLD(0.8)

### Infer schema and detect anomalies
```python
schema, anomalies = infer_schema_and_detect_anomalies(data_path, BATCH_SIZE, AGGREGATION_THRESHOLD, DISTINCT_THRESHOLD)
```

### Optional:
Shuffle data before
```python
    shuffle_csv_rows(data_path, new_data_path, seed=42)
```