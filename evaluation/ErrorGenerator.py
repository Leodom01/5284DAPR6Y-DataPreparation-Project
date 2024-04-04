# We want to generate errors which should be
# Set to nulla value
# If numberic set to 0 or to 99999999
# If text set to                     or xxxxxxxxxxxxxx
# if text remove some letters here and there
# If numberic set to the negative version of the value
# If categorical column then add typo in the category name
# If categorical add a random new value in one entry only

import pandas as pd
import random as rnd
import numpy as np
from dateutil.parser import parse


class ErrorGenerator:
    # Probabilities of a given error to occur
    NA_PROB = 0.2
    STRING_PROB = 0.2
    NUMBER_PROB = 0.2
    DATE_PROB = 0.2
    DATETIME_PROB = 0.2
    TIME_PROB = 0.2
    URL_PROB = 0.2
    BOOL_PROB = 0.2
    EMAIL_PROB = 0.2
    JSON_PROB = 0.2
    NETWORK_PROB = 0.2
    XML_PROB = 0.2

    # Setup report structure to return
    report = dict()
    report["na"] = list()
    report["string_char"] = list()
    report["num_placeholder"] = list()
    report["num_outlier"] = list()
    report["num_signswap"] = list()
    report["date"] = list()
    report["datetime"] = list()
    report["time"] = list()
    report["url"] = list()
    report["bool"] = list()
    report["email"] = list()
    report["json"] = list()
    report["network"] = list()
    report["email"] = list()
    report["xml"] = list()

    # Set some values to na
    def set_na(self, column):
        idxs = rnd.sample(list(range(len(column))), int(len(column) * self.NA_PROB))
        column[idxs] = None
        self.report["na"].extend(idxs)

    # Generate a random (positive or negative) bitflip in a char in a random position of random values
    def break_string(self, column):
        idxs = rnd.sample(list(range(len(column))), int(len(column) * self.STRING_PROB))
        for idx in idxs:
            if column[idx] is None:
                continue
            char_idx = np.random.randint(len(column[idx]) - 1)
            self.report["string_char"].append(char_idx)
            if np.random.random < 0.5:
                new_char = chr(ord(column[idx][char_idx]) + 1)
            else:
                new_char = chr(ord(column[idx][char_idx]) - 1)
            column[idx][char_idx] = new_char

    def break_number(self, column):
        PLACEHOLDER_PROB = 0.3
        OUTLIER_PROB = 0.3
        SIGN_CHANGE_PROB = 0.2

        idxs = rnd.sample(list(range(len(column))), int(len(column) * self.NUMBER_PROB))
        random = np.random.random()
        if random < PLACEHOLDER_PROB:
            pick = "placeholder"
        elif random < PLACEHOLDER_PROB + OUTLIER_PROB:
            pick = "outlier"
        else:
            pick = "sign"

        match pick:
            case "placeholder":
                if np.random.random() < 0.5:
                    column[idxs] = 0
                else:
                    column[idxs] = 999999
                self.report["num_placeholder"].extend(idxs)
            case "outlier":
                mean = np.mean(column)
                std = np.std(column)
                for idx in idxs:
                    if column[idx] is None:
                        continue
                    new_val = mean + np.random.choice([-1, 1]) * np.random.uniform(5, 7) * std
                    column[idx] = new_val
                    self.report["num_outlier"].append(idx)
            case "sign":
                column[idxs] = column[idxs] * (-1)
                self.report["num_signswap"].extend(idxs)

    def break_date(self, column):
        idxs = rnd.sample(list(range(len(column))), int(len(column) * self.DATE_PROB))
        for idx in idxs:
            if column[idx] is None:
                continue
            date = parse(column[idx])
            column[idx] = str(date.day + 30) + "/" + str(date.month) + "-" + str(date.year)
            self.report["date"].append(idx)

    def break_datetime(self, column):
        idxs = rnd.sample(list(range(len(column))), int(len(column) * self.DATETIME_PROB))
        for idx in idxs:
            if column[idx] is None:
                continue
            datetime = parse(column[idx])
            column[idx] = (
                        str(datetime.hour) + ":" + str(datetime.minute + 60) + "/" + str(datetime.second) + ":" + str(
                    datetime.microsecond) + " " + str(datetime.day + 30) + "/" + str(datetime.month) + "/" + str(
                    datetime.year))
            self.report["datetime"].append(idx)

    def break_time(self, column):
        idxs = rnd.sample(list(range(len(column))), int(len(column) * self.TIME_PROB))
        for idx in idxs:
            if column[idx] is None:
                continue
            time = parse(column[idx])
            column[idx] = str(time.hour + 24) + ":" + str(time.minute) + "-" + str(time.second) + "/" + str(
                time.microsecond)
            self.report["time"].append(idx)

    def break_url(self, column):
        idxs = rnd.sample(list(range(len(column))), int(len(column) * self.URL_PROB))
        column[idxs] = column[idxs].apply(lambda val: val.split("://")[-1] if val is not None else val)
        self.report["url"].extend(idxs)

    def break_bool(self, column):
        idxs = rnd.sample(list(range(len(column))), int(len(column) * self.BOOL_PROB))
        for idx in idxs:
            if column[idx] is None:
                continue
            self.report["bool"].append(idx)
            bool_val = bool(column[idx])
            if np.random.random() < 0.5:
                # Text version
                column[idx] = "true" if bool_val else "false"
            else:
                # Numeric value
                column[idx] = 1 if bool_val else 0

    def break_email(self, column):
        idxs = rnd.sample(list(range(len(column))), int(len(column) * self.EMAIL_PROB))
        column[idxs] = column[idxs].apply(lambda val: val.replace("@", "AT") if val is not None else val)
        self.report["email"].extend(idxs)

    def break_json(self, column):
        idxs = rnd.sample(list(range(len(column))), int(len(column) * self.JSON_PROB))
        column[idxs] = column[idxs].apply(lambda row: row[:1] + "{{breaking: it}" + row[1:] if row is not None else row)
        self.report["json"].extend(idxs)

    def break_network(self, column):
        idxs = rnd.sample(list(range(len(column))), int(len(column) * self.NETWORK_PROB))
        for idx in idxs:
            if column[idx] is None:
                continue
            self.report["network"].append(idx)
            if np.random.random() < 0.5:
                # Change one value to more than 255
                column[idx] = "300." + ".".join(column[idx].split(".")[1:])
            else:
                # Add one more value
                column[idx] = str(column[idx]) + ".128"

    def break_xml(self, column):
        idxs = rnd.sample(list(range(len(column))), int(len(column) * self.XML_PROB))
        column[idxs] = "</>" + column[idxs]
        self.report["xml"].extend(idxs)

    def generate_errors(self,
                        dataset_path="df_test.csv",
                        dataset_columns=["number", "date", "datetime", "time", "url", "bool", "email", "net_address",
                                         "xml"]):

        df = pd.read_csv(dataset_path)

        # print("Columns in the dataset:")
        # print(df.columns)

        for idx, column in enumerate(df.columns):
            self.set_na(df[column])
            # print("Set NA to: " + column)
            match dataset_columns[idx]:
                case "number":
                    self.break_number(df[column])
                case "date":
                    self.break_date(df[column])
                case "datetime":
                    self.break_datetime(df[column])
                case "time":
                    self.break_time(df[column])
                case "url":
                    self.break_url(df[column])
                case "bool":
                    self.break_bool(df[column])
                case "email":
                    self.break_email(df[column])
                case "json":
                    self.break_json(df[column])
                case "net_address":
                    self.break_network(df[column])
                case "xml":
                    self.break_xml(df[column])

        return df, self.report

if __name__ == "__main__":
    errorGen = ErrorGenerator()
    df, report = errorGen.generate_errors()
    print(df)
    print(report)