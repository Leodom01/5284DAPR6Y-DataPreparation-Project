import tensorflow_data_validation as tfdv
import tensorflow as tf

# Path to the data directory
DATA_DIR = './datasets/salaries/ds_salaries.csv'

# Path to the label column
LABEL_COLUMN = 'company_size'

stats = tfdv.generate_statistics_from_csv(DATA_DIR)

tfdv.visualize_statistics(stats)
