import json
import pandas as pd
from openai import OpenAI
from collections import Counter
import requests
from tqdm import tqdm

OLLAMA_URL = "http://localhost:11434/api/generate"


class LLM:
    def __init__(self, api_key: str) -> None:
        self.client = OpenAI(api_key=api_key)

    def explore_data_types(self, data: pd.DataFrame, sample_size: int = 15, batch_size: int = 3, model_name: str = "chatgpt") -> dict[str, str]:
        result = dict()
        column_names: list[str] = data.columns

        for column_name in tqdm(column_names):
            result_list = []
            for _ in tqdm(range(batch_size)):
                random_values = data[column_name].sample(n=sample_size)
                if model_name == "chatgpt":
                    tmp_result = self.chatgpt(column_name, random_values)
                elif model_name == "mixtral":
                    tmp_result = self.ollama(column_name, random_values, "dolphin-mixtral:8x7b")
                else:
                    tmp_result = self.ollama(column_name, random_values, "llama2:70b")
                result_list.append(tmp_result)
            counter = Counter(result_list)
            result[column_name] = counter.most_common(1)[0][0]

        return result
        
    def chatgpt(self, column_name: str, values: list[str]) -> str:
        values = [str(i) for i in values]
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
                {"role": "user", "content": f"column name: {column_name}, values: {', '.join(values)}"}
            ],
            response_format={"type": "json_object"}
        )

        result_json = json.loads(completion.choices[0].message.content)

        return result_json["type"]

    def ollama(self, column_name: str, values: list[str], model_name: str = "dolphin-mixtral:8x7b") -> str:
        values = [str(i) for i in values]
        prompt = ("In the following prompts I will give you a column name and some values."
            " Tell me whether the type is either DATE, TIME, DATETIME, URL, EMAIL, INT, FLOAT, JSON, BOOLEAN,"
            " NETWROK ADDDRESSES, XML, CATEGORY or TEXT. Only decide for a data type if most samples fit."
            " I will provide you with sample values from this column. Only give me the answer in one word format "
            "for example 'DATE' (required) \n"
            "------\n"
            f"column name: {column_name}, values: {', '.join(values)}"
            )
        
        data = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        response_json = requests.post(OLLAMA_URL, json=data).json()        
        return response_json["response"].strip()


if __name__ == "__main__":
    llm = LLM(api_key="")
    data = pd.read_csv("datasets/carprices/car_prices.csv", sep=",")

    print("[+] The result of ChatGPT 3.5")
    print(llm.explore_data_types(data=data, model_name="chatgpt"))
    print("[+] The result of llama2:70b")
    print(llm.explore_data_types(data=data, model_name="llama2"))
    print("[+] The result of dolphin-mixtral:8x7b")
    print(llm.explore_data_types(data=data, model_name="mixtral"))   

