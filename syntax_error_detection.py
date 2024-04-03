import re

import llm as llm
from regex_patterns import regex_repository


"""
The goal of this module is to combine the result of semantic type detection acquired by the llm with specific rules in
the form of regex patterns. We use the llm to find which particular type does the column belong to. Then, by using our
regex pattern repository, we check for syntactic errors in the column. 
"""

class Syntax_error_detection:
    def __init__(self, api_key: ""):
        self.llm_handler = llm.LLM(api_key=api_key)
        self.regex_patterns = regex_repository()

    def _find_compatible_regex(self, dataset, column, regex_list):
        """
        Validates each column entry according to a list of regex patterns.
        Returns the regex pattern with the highest fraction of compliant rows and indices of rows that do not comply.
        """
        highest_fraction = 0
        best_regex = None
        non_compliant_indices = []

        for regex in regex_list:
            fraction_compliant, non_compliant = self._apply_regex(dataset, column, regex)
            if fraction_compliant > highest_fraction:
                highest_fraction = fraction_compliant
                best_regex = regex
                non_compliant_indices = non_compliant

        return best_regex, non_compliant_indices

    def _apply_regex(self, dataset, column, regex):
        """
        Validates each column entry according to the regex pattern. It returns the fraction of rows that comply with the
        pattern, indices of rows that do not comply.
        """
        total_entries = len(dataset)
        compliant_entries = 0
        non_compliant_indices = []

        # Iterate through the column
        for index, entry in enumerate(dataset[column]):
            # Check if entry complies with the regex pattern
            if re.match(regex, str(entry)):
                compliant_entries += 1
            else:
                non_compliant_indices.append(index)

        # Calculate the fraction of compliant entries
        fraction_compliant = compliant_entries / total_entries

        return fraction_compliant, non_compliant_indices

    def find_syntax_errors(self, dataset, llm):
        """
        Uses the llm module to query for semantic type detection for each column in the dataset. Furthermore, if
        available, it combines the llm provided regex with the regex repository. Afterward, it applies each of regex
        patterns (regex repository + llm provided regex) to the column entries and chooses the one that matches most of
        the entries. The rows that are not matched with the most compatible regex pattern are considered syntactically
        wrong.
        """
        syntactic_errors = {}
        llm_result = self.llm_handler.explore_data_types(dataset, model_name=llm)
        print(llm_result)
        for column in dataset.columns:
            semantic_type = llm_result[column]['type']
            final_patterns = None
            if semantic_type.lower() in self.regex_patterns.get_categories():
                final_patterns = self.regex_patterns.get_category_regex(semantic_type.lower())
                if llm_result[column]['regex'] is not None:
                    final_patterns = final_patterns + llm_result[column]['regex']

            if final_patterns is None:
                syntactic_errors[column] = {'regex_pattern': None, 'errors': None}
            else:
                most_compatible_regex, errors = self._find_compatible_regex(dataset, column, final_patterns)
                syntactic_errors[column] = {'regex_pattern': most_compatible_regex, 'errors': errors, 'type': semantic_type}

        return syntactic_errors

if __name__ == "__main__":
    import pandas as pd
    sed = Syntax_error_detection(api_key='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')
    dataset = pd.read_csv("datasets/carprices/car_prices.csv", sep=",")
    error_detected = sed.find_syntax_errors(dataset, "chatgpt")







