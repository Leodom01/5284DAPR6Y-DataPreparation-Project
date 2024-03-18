import json

from openai import OpenAI


class LLM:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def chatgpt(self, column_name: str, values: list[str]) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "In the following prompts I will give you a column name and some values."
                                              " Tell me whether the type is either DATE, TIME, DATETIME, URL, EMAIL, "
                                              "(INT, FLOAT), JSON, BOOLEAN, NETWROK ADDDRESSES or XML. "
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


if __name__ == "__main__":
    llm = LLM(api_key="")
    column_type = llm.chatgpt(
        column_name="time",
        values=["2024-03-03 08:30:00", "2024-03-03 12:45:00", "luke.hall@example.com", "2024-03-03 15:20:00",
                "2024-03-04 09:00:00"]
    )
    print(column_type)

    column_type = llm.chatgpt(
        column_name="time",
        values=["emma.martin@example.com", "luke.hall@example.com", "chloe.davis@example.com",
                "ethan.jackson@example.com",
                "2024-03-03 08:30:00",
                "ava.robinson@example.com",
                ]
    )
    print(column_type)

    column_type = llm.chatgpt(
        column_name="time",
        values=["https://www.example.com/page?category=electronics&product=laptop",
                "https://www.example.com/blog/article?id=123&category=technology",
                "https://www.example.com/shop/product?product_id=456&color=blue",
                "https://www.example.com/page?category=clothing&gender=male&size=XL",
                "https://www.example.com/blog/post?id=789&tag=tips&source=twitter",
                "2024-03-03 08:30:00",
                "ava.robinson@example.com",
                ]
    )
    print(column_type)
