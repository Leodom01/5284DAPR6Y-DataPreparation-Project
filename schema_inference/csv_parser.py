import csv

from pb_parser import Schema


def validate_csv_against_schema(schema: Schema, csv_file_path: str, ignored_domains=None):
    # First, create a mapping from feature names to Feature objects and domains
    schema_dict = {
        feature.name: {
            'feature': feature,
            'domain': None,
            'required': True if feature.presence.min_fraction else False
        } for feature in schema.features}

    for domain in schema.domains:
        if domain.name in schema_dict:
            schema_dict[domain.name]['domain'] = domain.values

    # Open the CSV file and parse it
    faulty_rows = []
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)

        # Validate headers
        if set(headers) != set(schema_dict.keys()):
            raise ValueError("CSV headers don't match the schema feature names.")

        # Create a mapping of header to index for efficient lookup
        header_to_index = {header: index for index, header in enumerate(headers)}

        count = 0
        # Validate rows
        for row_index, row in enumerate(reader, start=1):  # Start from 1 to account for header
            is_faulty_row = False


            for feature_name, feature_info in schema_dict.items():
                feature_index = header_to_index[feature_name]
                value = row[feature_index]

                if value == '' and feature_info['required']:
                    faulty_rows.append(row_index - 1)
                    is_faulty_row = True
                    break  # No need to check further if row is already faulty

                # Validate type
                try:
                    if feature_info['feature'].type == 2:  # INT
                        int(value)
                    elif feature_info['feature'].type == 3:  # FLOAT
                        float(value)
                except ValueError:
                    faulty_rows.append(row_index - 1)
                    is_faulty_row = True
                    break  # No need to check further if row is already faulty

                #Validate domain
                if not ignored_domains or feature_name in ignored_domains:
                    continue

                if feature_info['domain'] is not None and value not in feature_info['domain']:
                    faulty_rows.append(row_index - 1)
                    is_faulty_row = True
                    break  # No need to check further if row is already faulty

            if not is_faulty_row and len(row) != len(headers):
                # If the row does not have the same number of elements as the header, mark it as faulty
                faulty_rows.append(row_index - 1)

    return faulty_rows


def count_csv_lines_and_column_names(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Read the header line
        line_count = sum(1 for row in reader)  # Count the remaining lines
    return line_count, headers