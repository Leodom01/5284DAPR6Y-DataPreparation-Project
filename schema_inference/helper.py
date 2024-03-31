import csv
import random


def shuffle_csv_rows(input_csv_path, output_csv_path, seed=42):
    with open(input_csv_path, 'r', newline='') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Read the header line
        data_rows = list(reader)  # Read the remaining data lines

    # Shuffle the data rows
    random.seed(seed)
    random.shuffle(data_rows)

    # Write the shuffled data to a new CSV file
    with open(output_csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write the header line
        writer.writerows(data_rows)  # Write the shuffled data rows

    return output_csv_path


def get_columns_above_threshold(dataframe, threshold):
    max_count = threshold * len(dataframe)
    columns = [col for col in dataframe.columns if dataframe[col].nunique() > max_count]
    return columns


