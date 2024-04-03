import json
import time

import pandas as pd
from openai import OpenAI
from collections import Counter
import requests
import re
# from data import correct_data

OLLAMA_URL = "http://localhost:11434/api/generate"


class LLM:
    def __init__(self, api_key: str) -> None:
        self.client = OpenAI(api_key=api_key)

    def explore_data_types(self, data: pd.DataFrame, sample_size: int = 5, batch_size: int = 5,
                           model_name: str = "chatgpt") -> dict[str, str]:
        result = dict()
        column_names: list[str] = data.columns
        regex_time_list = []
        type_time_list = []

        for column_name in (column_names):
            result_list = []
            type_result_list = []
            re_result_list = []

            random_values = None
            for _ in (range(batch_size)):
                random_values = data[column_name].sample(n=sample_size)
                if model_name == "chatgpt":
                    tmp_result = self.chatgpt(column_name, random_values)
                elif model_name == "mixtral":
                    tmp_result = self.ollama(column_name, random_values, "dolphin-mixtral:8x7b")
                else:
                    tmp_result = self.ollama(column_name, random_values, "llama2:70b")
                type_result_list.append(tmp_result["type"])
                re_result_list.append(tmp_result["regex"])
                type_time_list.append(tmp_result["regex_time"])
                if tmp_result["regex"] is not None:
                    regex_time_list.append(tmp_result["regex_time"])
            counter = Counter(type_result_list)
            column_type = counter.most_common(1)[0][0]
            column_regex = None
            if column_type in ['DATE', 'DATETIME', 'TIME']:
                for pattern in re_result_list:
                    if pattern is not None and pattern != "UNKNOWN" and self._check_re(random_values, pattern):
                        column_regex = pattern
                        break

            result[column_name] = {"type": column_type, "regex": column_regex}

        if len(regex_time_list) != 0:
            average_regex_time = sum(regex_time_list) / len(regex_time_list)
        else:
            average_regex_time = 0

        result["regex_time"] = average_regex_time
        result["type_time"] = sum(type_time_list) / len(type_time_list)
        return result

    # def get_correct_number(self, result, data_name: str):
    #     correct_re = 0
    #     all_re = 0
    #     correct_type = 0
    #     all_col = 0
    #
    #     for k, v in result.items():
    #
    #         if k not in correct_data[data_name]:
    #             continue
    #         all_col += 1
    #         if correct_data[data_name][k]["type"] == v["type"]:
    #             correct_type += 1
    #         if correct_data[data_name][k]["regex"]:
    #             all_re += 1
    #             if v["regex"] is not None and v["regex"] != "UNKNOWN":
    #                 correct_re += 1
    #     return (all_col, correct_type), (all_re, correct_re)

    def _check_re(self, values: list[str], regex_str: str) -> bool:
        try:
            pattern = re.compile(regex_str)
            matches = []
            for value in values:
                if pattern.search(value):
                    matches.append(value)

            if len(matches) >= len(values) / 2:
                return True
            else:
                return False
        except:
            return False

    def chatgpt(self, column_name: str, values: list[str]) -> dict[str, str]:
        values = [str(i) for i in values]
        type_time = 0
        regex_time = 0
        start_time = time.time()
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "In the following prompts I will give you a column name and some values."
                                              " Tell me whether the type is either DATE, TIME, DATETIME, URL, EMAIL, "
                                              "INT, FLOAT, JSON, BOOLEAN, NETWROK ADDDRESSES, XML, CATEGORY or TEXT. "
                                              "Only decide for a data type if most samples fit. "
                                              "I will provide you with sample values from this column."
                                              " Give me the answer in JSON format with the"
                                              " fields type (required)"},
                {"role": "user", "content": f"column name: {column_name}, values: {', '.join(values)}"[:16000]}
            ],
            response_format={"type": "json_object"}
        )
        try:
            result_json = json.loads(completion.choices[0].message.content)
            column_type = result_json["type"]
        except:
            column_type = "UNKNOWN"
        type_time = time.time() - start_time

        column_regex = None
        if result_json["type"] in ["DATE", "DATETIME", "TIME"]:
            start_time = time.time()
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "I will give you some date, datetime or time type "
                                                  "values(',' is separator), and you will give me one regex "
                                                  "for single value(ignore other types)."
                                                  " The output should be in JSON format."
                     },
                    {"role": "user", "content": f"values: {', '.join(values)}"}
                ],
                response_format={"type": "json_object"}
            )
            try:
                result_json = json.loads(completion.choices[0].message.content)

                column_regex = result_json["regex"]
            except:
                column_regex = "UNKNOWN"
            regex_time = time.time() - start_time
        return {"type": column_type, "regex": column_regex, "type_time": type_time, "regex_time": regex_time}

    def ollama(self, column_name: str, values: list[str], model_name: str = "dolphin-mixtral:8x7b") -> str:
        values = [str(i) for i in values]
        type_time = 0
        regex_time = 0
        start_time = time.time()
        prompt = ("In the following prompts I will give you a column name and some values."
                  " Tell me whether the type is either DATE, TIME, DATETIME, URL, EMAIL, INT, FLOAT, JSON, BOOLEAN,"
                  " NETWROK ADDDRESSES, XML, CATEGORY or TEXT. Only decide for a data type if most samples fit."
                  " I will provide you with sample values from this column. Only give me one word answer(required)"
#"for example 'DATE' \n"
                  "------\n"
                  f"column name: {column_name}, values: {', '.join(values)}"
                  )

        data = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        try:
            response_json = requests.post(OLLAMA_URL, json=data).json()
            column_type = response_json["response"].strip()
        except:
            column_type = "UNKNOWN"

        type_time = time.time() - start_time
        column_regex = None
        if column_type in ["DATE", "DATETIME", "TIME"]:
            start_time = time.time()
            prompt = ("I will give you some date, datetime or time type "
                      "values(',' is separator), and you will give me one regex "
                      "for single value(ignore other types)."
                      " Only give me a regex as an answer(required)"
                      "for example '\\d{2}-\\d{2}-\\d{2}'"
                      "------\n"
                      f"values: {', '.join(values)}"
                      "------\n"
                      "Answer in the most concise way, only one regex"
                      )

            data = {
                "model": model_name,
                "prompt": prompt,
                "stream": False
            }

            try:
                response_json = requests.post(OLLAMA_URL, json=data).json()
                column_regex = response_json["response"].strip()
            except:
                column_regex = "UNKNOWN"
            regex_time = time.time() - start_time

        return {"type": column_type, "regex": column_regex, "type_time": type_time, "regex_time": regex_time}
        # values = [str(i) for i in values]
        # prompt = ("In the following prompts I will give you a column name and some values."
        #     " Tell me whether the type is either DATE, TIME, DATETIME, URL, EMAIL, INT, FLOAT, JSON, BOOLEAN,"
        #     " NETWROK ADDDRESSES, XML, CATEGORY or TEXT. Only decide for a data type if most samples fit."
        #     " I will provide you with sample values from this column. Only give me one word answer"
        #     "for example 'DATE' \n"
        #     "------\n"
        #     f"column name: {column_name}, values: {', '.join(values)}"
        #     )

        # data = {
        #     "model": model_name,
        #     "prompt": prompt,
        #     "stream": False
        # }
        # response_json = requests.post(OLLAMA_URL, json=data).json()
        # return response_json["response"].strip()


if __name__ == "__main__":
    llm = LLM(api_key="")
    type_col_num = 0
    correct_type_col_num = 0
    type_time = 0

    regex_col_num = 0
    correct_regex_col_num = 0
    regex_time = 0
    num_regex = 0
    dataset = {
        "audible": pd.read_csv("datasets/audible/audible_uncleaned.csv", sep=","),
        "car_price": pd.read_csv("datasets/carprices/car_prices.csv", sep=","),
        "glassdoor": pd.read_csv("datasets/glassdoor/Uncleaned_DS_jobs.csv", sep=","),
        "kickstarter": pd.read_csv("datasets/kickstarter/ks-projects-201612.csv", sep=",", encoding_errors="ignore"),
        "salaries": pd.read_csv("datasets/salaries/ds_salaries.csv", sep=","),
        "wearables": pd.read_csv("datasets/wearables/S001.csv", sep=","),
    }


    print("[+] The result of ChatGPT 3.5")
    for data_name, data in dataset.items():
        print(data_name)
        result = llm.explore_data_types(data=data, model_name="chatgpt", sample_size=35, batch_size=10)
        print(result)
        pred = llm.get_correct_number(result, data_name)
        type_col_num += pred[0][0]
        correct_type_col_num += pred[0][1]
        regex_col_num += pred[1][0]
        correct_regex_col_num += pred[1][1]
        if pred[1][0] != 0:
            num_regex += 1

        regex_time += result["regex_time"]
        type_time += result["type_time"]

    print(f"Type Acc: {1.0 * correct_type_col_num / type_col_num}")
    print(f"Type time: {1.0 * type_time / len(dataset)}")

    print(f"Regex Acc: {1.0 * correct_regex_col_num / regex_col_num}")
    print(f"Regax time: {1.0 * regex_time / num_regex}")



    # print("[+] The result of dolphin-mixtral:8x7b")
    # print(llm.explore_data_types(data=data, model_name="mixtral"))
    # print("[+] The result of llama2:70b")
    # print(llm.explore_data_types(data=data, model_name="llama2"))


