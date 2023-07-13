
import openai

class OpenaiManager:
    def __init__(self, api_key):
        openai.api_key = api_key

    def sendMessage(self, massage):
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
                                                  messages=[{"role": "user",
                                                             "content": massage}])
        return completion["choices"][0]["message"]["content"]
