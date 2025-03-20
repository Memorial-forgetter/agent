import random
import threading

import openai
import os

openai.api_base = "https://api.siliconflow.cn/v1"
class Keypool():
    def __init__(self):
        self.api_keys = [
            '',
        ]
        self.counter = 0
        self.lock = threading.Lock()

    def getkey(self):
        self.lock.acquire()
        key_ret = self.api_keys[self.counter]
        self.counter = (self.counter + 1) % len(self.api_keys)
        self.lock.release()
        return key_ret


class ChatGPT:
    def __init__(self, model="Pro/deepseek-ai/DeepSeek-R1", key="", conversation_list=[],keypool = None):
        self.model = model
        self.conversation_list = conversation_list
        self.lock = threading.Lock()
        # openai.api_key = ""
        self.client = openai.OpenAI(
            base_url="https://api.siliconflow.cn/v1",
            # defaults to os.environ.get("OPENAI_API_KEY")
            api_key="sk-rdffprsjjtdjnfhivtftvpiobqdrahnxgmmnwhrjxxrpxfcj",
        )

    def call(self, prompt,model = "Pro/deepseek-ai/DeepSeek-R1"):
        answer = None
        self.conversation_list.append(
            {"role": "system", "content": "You are a helpful instruction-following assistant."})
        self.conversation_list.append({"role": "user", "content": prompt})
        try:
            answer = ""

            response = self.client.chat.completions.create(model=model, messages=self.conversation_list, temperature=0.5)
            answer = response.choices[0].message.content.strip()
            self.conversation_list = []
            print("Answer:", answer)
        except Exception as e:
            print("Call Openai API Error:", e)
            raise e
        return answer

gpt = ChatGPT()
# gpt.call("What is the capital of the United States?")