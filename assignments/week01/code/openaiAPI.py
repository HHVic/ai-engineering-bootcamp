import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
base_url = os.getenv('OPENAI_API_BASE')
model = os.getenv('OPENAI_MODEL')

print(f"-- debug -- openai api key is {base_url}")
print(f"-- debug -- openai api key is {api_key[0:10]}******")

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)


response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": "你是什么模型？能做什么？"}
    ]
)

print(response.choices[0].message.content)


# 正常会输出结果：Hello! It's great to see you. How can I assist you today?