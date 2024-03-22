import requests, logging
from transformers import AutoTokenizer
from config import GPT_URL, MODEL_NAME, MAX_ONTASK_TOKENS, LOGS_PATH, TEMPERATURE

logging.basicConfig(filename=LOGS_PATH, level=logging.INFO, format='%(asctime)s - %(message)s', filemode="w")

class GPT:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.url = GPT_URL
        self.max_tokens = MAX_ONTASK_TOKENS
        self.temperature = TEMPERATURE

    def ask_gpt(self, messages: list) -> str:
        response = requests.post(
            GPT_URL,
            headers={"Content-Type": "application/json"},
            json={
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
        )

        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"]
            logging.info(f"Отправлено: task\nПолучен результат: result")
            return result
        else:
            logging.error(f"Отправлено: task\nПолучена ошибка: {response.json()}")
            return "Ошибка"
    
    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))