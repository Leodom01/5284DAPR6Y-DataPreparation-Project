import re
import llm as llm
from regex_patterns import regex_repository


class Syntax_error_detection:
    def __init__(self, api_key: ""):
        # Initialize Syntax_error_detection class with an API key for llm
        self.llm_handler = llm.LLM(api_key=api_key)
        # Load regex patterns repository
        self.regex_patterns = regex_repository()

    def _find_compatible_regex(self, dataset, column, regex_list):
        """
        Validates each column entry according to a list of regex patterns.
        Returns the regex pattern with the highest fraction of compliant rows and indices of rows that do not comply.
        """
        highest_fraction = 0
        best_regex = None
        non_compliant_indices = []

        # Iterate through each regex pattern in the list
        for regex in regex_list:
            # Apply the regex pattern to the dataset
            fraction_compliant, non_compliant = self._apply_regex(dataset, column, regex)
            # Update highest fraction and best regex if a better match is found
            if fraction_compliant > highest_fraction:
                highest_fraction = fraction_compliant
                best_regex = regex
                non_compliant_indices = non_compliant

        return best_regex, non_compliant_indices

    def _apply_regex(self, dataset, column, regex):
        """
        Validates each column entry according to the regex pattern.
        Returns the fraction of rows that comply with the pattern and indices of rows that do not comply.
        """
        total_entries = len(dataset)
        compliant_entries = 0
        non_compliant_indices = []

        # Iterate through each entry in the column
        for index, entry in enumerate(dataset[column]):
            # Check if the entry complies with the regex pattern
            if re.match(regex, str(entry)):
                compliant_entries += 1
            else:
                non_compliant_indices.append(index)

        # Calculate the fraction of compliant entries
        fraction_compliant = compliant_entries / total_entries

        return fraction_compliant, non_compliant_indices

    def find_syntax_errors(self, dataset, llm):
        """
        Uses the llm module to query for semantic type detection for each column in the dataset.
        Combines the llm provided regex with the regex repository, if available.
        Applies each regex pattern to the column entries and chooses the one that matches most of the entries.
        Rows that are not matched with the most compatible regex pattern are considered syntactically wrong.
        """
        syntactic_errors = {}
        # Use llm module to explore data types in the dataset
        llm_result = self.llm_handler.explore_data_types(dataset, model_name=llm)

        # Iterate through each column in the dataset
        for column in dataset.columns:
            # Get the semantic type detected by llm for the column
            semantic_type = llm_result[column]['type']
            final_patterns = None

            # Check if semantic type exists in regex patterns repository
            if semantic_type.lower() in self.regex_patterns.get_categories():
                final_patterns = self.regex_patterns.get_category_regex(semantic_type.lower())
                # If llm provided additional regex, append it to the patterns
                if llm_result[column]['regex'] is not None:
                    final_patterns = final_patterns + llm_result[column]['regex']

            if final_patterns is None:
                # If no compatible regex patterns found, mark column as having no regex pattern
                syntactic_errors[column] = {'regex_pattern': None, 'errors': None}
            else:
                # Find the most compatible regex pattern and detect errors
                most_compatible_regex, errors = self._find_compatible_regex(dataset, column, final_patterns)
                syntactic_errors[column] = {'regex_pattern': most_compatible_regex, 'errors': errors,
                                            'type': semantic_type}

        return syntactic_errors


if __name__ == "__main__":
    import pandas as pd

    sed = Syntax_error_detection(api_key='')
    # Load dataset
    dataset = pd.read_csv("datasets/carprices/car_prices.csv", sep=",")
    # Find syntax errors using the Syntax_error_detection class
    error_detected = sed.find_syntax_errors(dataset, "chatgpt")
