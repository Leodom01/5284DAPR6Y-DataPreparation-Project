# Dataset agnostic quality assessment framework
The goal of this framework is to assess and validate the quality of datasets used in ML pipelines. This tool is designed to be compatible with any dataset that includes column names, requiring no specific background or domain knowledge.

Our tool depends heavily on the following components:
* Semantic error detection via embeddings
* Syntactic error detection via LLMs and RegEx validation 
* Improved TFX Schema Inference

## Requirements

- Python 3.10 or higher
- api_key for chatgpt 3.5 or locally ran Llama2 or Mixtral 
# Usage
```pip install -r requirements.txt```


