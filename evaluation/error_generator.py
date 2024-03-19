# We want to generate errors which should be
# Set to nulla value
# If numberic set to 0 or to 99999999
# If text set to                     or xxxxxxxxxxxxxx
# if text remove some letters here and there
# If numberic set to the negative version of the value
# If categorical column then add typo in the category name
# If categorical add a random new value in one entry only

import pandas as pd
from random import random
import numpy as np
from dateutil.parser import *

NA_PROB = 0.01
STRING_PROB = 0.01
NUMBER_PROB = 0.01
DATE_PROB = 0.01
DATETIME_PROB = 0.01
TIME_PROB = 0.01
URL_PROB = 0.01
BOOL_PROB = 0.01
EMAIL_PROB = 0.01
JSON_PROB = 0.01
NETWORK_PROB = 0.01
XML_PROB = 0.01


# Set some values to na
def set_na(column):
    idxs = np.random.randint(len(column), size=int(len(column) * NA_PROB))
    column[idxs] = None


# Generate a random (positive or negative) bitflip in a char in a random position of random values
def break_string(column):
    idxs = np.random.randint(len(column), size=int(len(column) * STRING_PROB))
    for idx in idxs:
        char_idx = np.random.randint(len(column[idx]) - 1)
        if np.random.random < 0.5:
            new_char = chr(ord(column[idx][char_idx]) + 1)
        else:
            new_char = chr(ord(column[idx][char_idx]) - 1)
        column[idx][char_idx] = new_char


def break_number(column):
    PLACEHOLDER_PROB = 0.3
    OUTLIER_PROB = 0.3
    SIGN_CHANGE_PROB = 0.2

    idxs = np.random.randint(len(column), size=int(len(column) * NUMBER_PROB))
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
        case "outlier":
            mean = np.mean(column)
            std = np.std(column)
            for idx in idxs:
                new_val = mean + np.random.choice([-1, 1]) * np.random.uniform(5, 7) * std
                column[idx] = new_val
        case "sign":
            column[idxs] = column[idxs] * (-1)


def break_date(column):
    idxs = np.random.randint(len(column), size=int(len(column) * DATE_PROB))
    for idx in idxs:
        date = parse(column[idx])
        column[idx] = str(date.day + 30) + "/" + str(date.month) + "-" + str(date.year)


def break_datetime(column):
    idxs = np.random.randint(len(column), size=int(len(column) * DATETIME_PROB))
    for idx in idxs:
        datetime = parse(column[idx])
        column[idx] = (str(datetime.hour) + ":" + str(datetime.minute + 60) + "/" + str(datetime.second) + ":" + str(
            datetime.microsecond) + str(datetime.day + 30) + "/" + str(datetime.month) + "-" + str(datetime.year))


def break_time(column):
    idxs = np.random.randint(len(column), size=int(len(column) * TIME_PROB))
    for idx in idxs:
        time = parse(column[idx])
        column[idx] = str(time.hour+24)+":"+str(time.minute)+"-"+str(time.second)+"/"+str(time.microsecond)

def break_url(column):
    idxs = np.random.randint(len(column), size=int(len(column) * URL_PROB))
    column[idxs] = column[idxs].apply(lambda val: val.split("://")[-1])

def break_bool(column):
    idxs = np.random.randint(len(column), size=int(len(column) * BOOL_PROB))
    for idx in idxs:
        bool_val = bool(column[idx])
        if np.random.random() < 0.5:
            # Text version
            column[idx] = "true" if bool_val else "false"
        else:
            # Numeric value
            column[idx] = 1 if bool_val else 0
def break_email(column):
    idxs = np.random.randint(len(column), size=int(len(column) * EMAIL_PROB))
    column[idxs] = column[idxs].apply(lambda val: val.replace("@", "AT"))


def break_json(column):
    idxs = np.random.randint(len(column), size=int(len(column) * JSON_PROB))


def break_network(column):
    idxs = np.random.randint(len(column), size=int(len(column) * NETWORK_PROB))


def break_xml(column):
    idxs = np.random.randint(len(column), size=int(len(column) * XML_PROB))


def main():
    dataset_path = "df_test.csv"
    dataset_columns = ["ID", "number", "date", "datetime", "time", "url", "bool", "email", "json", "net_address", "xml"]

    df = pd.read_csv(dataset_path, index_col=False)

    print("Columns in the dataset:")
    print(df.columns)

    for idx, column in enumerate(df.columns):
        set_na(df[column])
        match dataset_columns[idx]:
            case "number":
                break_number(df[column])
            case "date":
                break_date(df[column])
            case "datetime":
                break_datetime(df[column])
            case "time":
                break_time(df[column])
            case "url":
                break_url(df[column])
            case "bool":
                break_bool(df[column])
            case "email":
                break_email(df[column])
            case "json":
                break_json(df[column])
            case "net_address":
                break_network(df[column])
            case "xml":
                break_xml(df[column])

    print("Final DataFrame:")
    print(df)


if __name__ == "__main__":
    main()
