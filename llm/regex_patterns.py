import re


"""
A regex repository for common data formats. Currently supporting the following data types: 
DATE, TIME, DATETIME, URL, EMAIL, (INT, FLOAT), JSON, BOOLEAN, NETWORK IP ADDRESSES, XML
"""
class regex_repository:
    def __init__(self):

        self.date_patterns = [
            r'(0[1-9]|1[0-2])[/\-](0[1-9]|[12]\d|3[01])[/\-]\d{4}',  # MM/DD/YYYY or MM-DD-YYYY (with range checks)
            r'(January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec)\s(0[1-9]|[12]\d|3[01]),\s\d{4}',
            # Month Name DD, YYYY (with range checks)
            r'\d{4}[/\-](0[1-9]|1[0-2])[/\-](0[1-9]|[12]\d|3[01])',  # YYYY/MM/DD or YYYY-MM-DD (with range checks)
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',  # YYYY-MM-DDThh:mm:ssZ (ISO 8601 format)
            r'(0[1-9]|[12]\d|3[01])\s(0[1-9]|1[0-2])\s\d{4}'  # DD MM YYYY (with range checks)
        ]

        self.timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',  # YYYY-MM-DDTHH:MM:SSZ (ISO 8601 format)
            r'(0[1-9]|[12]\d|3[01])-(0[1-9]|1[0-2])-\d{4}\s([01]\d|2[0-3]):[0-5]\d:[0-5]\d',
            # DD-MM-YYYY HH:MM:SS (with range checks)
            r'(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}\s([01]\d|2[0-3]):[0-5]\d:[0-5]\d',
            # MM/DD/YYYY HH:MM:SS (with range checks)
            r'\d{4}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])\s([01]\d|2[0-3]):[0-5]\d:[0-5]\d',
            # YYYY/MM/DD HH:MM:SS (with range checks)
            r'\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\s([01]\d|2[0-3]):[0-5]\d:[0-5]\d',
            # YYYY-MM-DD HH:MM:SS (with range checks)
            r'(0[1-9]|[12]\d|3[01])-(0[1-9]|1[0-2])-\d{4}T([01]\d|2[0-3]):[0-5]\d:[0-5]\dZ',
            # DD-MM-YYYYTHH:MM:SSZ (with range checks)
            r'(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}T([01]\d|2[0-3]):[0-5]\d:[0-5]\dZ',
            # MM/DD/YYYYTHH:MM:SSZ (with range checks)
            r'\d{4}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])T([01]\d|2[0-3]):[0-5]\d:[0-5]\dZ',
            # YYYY/MM/DDTHH:MM:SSZ (with range checks)
            r'\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\s([01]\d|2[0-3]):[0-5]\d:[0-5]\d\.\d{3}',
            # YYYY-MM-DD HH:MM:SS.mmm (with range checks)
            r'\d{4}-\d{2}-\d{2}T([01]\d|2[0-3]):[0-5]\d:[0-5]\d\.\d{3}Z'  # YYYY-MM-DDTHH:MM:SS.mmmZ
        ]

        self.time_patterns = [
            r'([01]\d|2[0-3]):[0-5]\d:[0-5]\d',  # 24-hour time format (HH:MM:SS) (with range checks)
            r'([1-9]|1[0-2]):[0-5]\d:[0-5]\d\s(?:AM|PM)',
            # 12-hour time format with AM/PM (hh:mm:ss AM/PM) (with range checks)
            r'([01]\d|2[0-3]):[0-5]\d:[0-5]\d\.\d{3}',
            # 24-hour time format with milliseconds (HH:MM:SS.mmm) (with range checks)
            r'([1-9]|1[0-2]):[0-5]\d:[0-5]\d\.\d{3}\s(?:AM|PM)'
            # 12-hour time format with milliseconds and AM/PM (hh:mm:ss.mmm AM/PM) (with range checks)
        ]

        # Regex pattern for integer
        self.integer_pattern = [r'-?\d+']

        # Regex pattern for float
        self.float_pattern = [r'-?\d+\.\d+([eE]-?\d+)?']

        self.string_pattern = [r'.+']

        self.URL_pattern = [r'(https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z]{2,}(\.[a-zA-Z]{2,})'
                            r'(\.[a-zA-Z]{2,})?\/[a-zA-Z0-9]{2,}|((https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)'
                            r'?[a-zA-Z]{2,}(\.[a-zA-Z]{2,})(\.[a-zA-Z]{2,})?)|(https:\/\/www\.|http:\/\/www\.|https:\/\
                            /|http:\/\/)?[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}(\.[a-zA-Z0-9]{2,})?']

        self.email_pattern = [r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}']
        self.price_pattern = [r'[1-9]\d{0,7}(?:\.\d{1,4})?']
        self.boolean_pattern = [r'(True|False|T|F|true|false|t|f|1|0)']

        self.ip_pattern = [r'((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}',
                           r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b']

        self.data_categories = {'date': self.date_patterns, 'timestamp': self.timestamp_patterns,
                                'time': self.time_patterns, 'integer':self.integer_pattern, 'float': self.float_pattern,
                                'string': self.string_pattern, 'URL': self.URL_pattern, 'email': self.email_pattern, 'ip': self.ip_pattern}

    def get_categories(self):
        return self.data_categories.keys()

    def get_category_regex(self, type):
        return self.data_categories[type]

    def validat_column(self, dataset, column, regex):
        pattern = re.compile(regex, re.IGNORECASE)
        invalid_rows = []
        for i, entry in enumerate(dataset[column]):
            result = re.match(pattern, entry)
            if result is None:
                invalid_rows.append(i)
        return


def test_patterns(data_checker):
    test_data = {
        'date': ['01/01/2022', 'December 25, 2023', '2024-03-19', '2024-12-31', '31 03 2024'],
        'timestamp': ['2024-03-19T12:30:45Z', '31-03-2024 23:59:59', '03/31/2024 12:30:45', '2024/03/31 12:30:45', '2024-03-31T12:30:45Z'],
        'time': ['12:30:45', '11:59:59 AM', '23:59:59.123', '12:30:45.123 PM'],
        'integer': ['123', '-456', '7890', '0'],
        'float': ['123.456', '-789.012', '0.123', '456.789e-2'],
        'string': ['hello', 'world', '123', 'abc123'],
        'URL': ['https://www.example.com', 'http://example.com', 'www.example.com', 'example.com'],
        'email': ['test@example.com', 'user123@test.co.uk', 'test.user@example-domain.com'],
        'price': ['10.99', '100', '999.9999', '12345.678'],
        'ip': ['192.168.1.1', '255.255.255.0', '127.0.0.1', '0.0.0.0',
               '2001:0db8:85a3:0000:0000:8a2e:0370:7334', '2001:db8:0:1:1:1:1:1', '2001:db8::1:1:1:1', '::1']
    }

    for category, patterns in data_checker.get_dataformats().items():
        print(f"Testing patterns for category: {category}")
        for pattern in patterns:
            regex_pattern = re.compile(pattern)
            print(f"Pattern: {pattern}")
            for test_value in test_data[category]:
                match = regex_pattern.fullmatch(test_value)
                if match:
                    print(f"Matched: {test_value}")
                else:
                    print(f"Not Matched: {test_value}")
            print("\n============\n")

if __name__ == "__main__":
    tmp = regex_repository()
    test_patterns(tmp)
