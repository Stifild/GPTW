import json, requests, logging, time

from config import MAX_ONTASK_TOKENS, FOLDER_ID, GPT_MODEL, TEMPERATURE, TOKENS_DATA_PATH, LOGS_PATH, IAM_TOKEN_ENDPOINT, IAM_TOKEN_PATH

logging.basicConfig(filename=LOGS_PATH, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode="w")

class GPT:
    def __init__(self):
        self.max_tokens = MAX_ONTASK_TOKENS
        self.temperature = TEMPERATURE
        self.folder_id = FOLDER_ID
        self.gpt_model = GPT_MODEL
        self.tokens_data_path = TOKENS_DATA_PATH

    def count_tokens_in_dialogue(self, messages: list) -> int:
        iam_token = self.get_iam_token()

        headers = {
            'Authorization': f'Bearer {iam_token}',
            'Content-Type': 'application/json'
        }
        data = {
            "modelUri": f"gpt://{self.folder_id}/{self.gpt_model}/latest",
            "maxTokens": self.max_tokens,
            "messages": []
        }

        for row in messages:
            data["messages"].append(
                {
                    "role": row["role"],
                    "text": row["content"]
                }
            )

        return len(
            requests.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion",
                json=data,
                headers=headers
            ).json()["tokens"]
        )


    def increment_tokens_by_request(self, messages: list[dict]):
        try:
            with open(self.tokens_data_path, "r") as token_file:
                tokens_count = json.load(token_file)["tokens_count"]

        except FileNotFoundError:
            tokens_count = 0

        current_tokens_used = self.count_tokens_in_dialogue(messages)
        tokens_count += current_tokens_used

        with open(self.tokens_data_path, "w") as token_file:
            json.dump({"tokens_count": tokens_count}, token_file)


    def ask_gpt(self, messages):
        iam_token = self.get_iam_token()

        url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            'Authorization': f'Bearer {iam_token}',
            'Content-Type': 'application/json'
        }

        data = {
            "modelUri": f"gpt://{self.folder_id}/{self.gpt_model}/latest",
            "completionOptions": {
                "stream": False,
                "temperature": self.temperature,
                "maxTokens": self.max_tokens
            },
            "messages": []
        }

        for row in messages:
            data["messages"].append(
                {
                    "role": row["role"],
                    "text": row["content"]
                }
            )

        try:
            response = requests.post(url, headers=headers, json=data)

        except Exception as e:
            logging.ERROR("Произошла непредвиденная ошибка.", e)

        else:
            if response.status_code != 200:
                logging.ERROR("Ошибка при получении ответа:", response.status_code)
            else:
                result = response.json()['result']['alternatives'][0]['message']['text']
                messages.append({"role": "assistant", "content": result})
                self.increment_tokens_by_request(messages)
                return result

    with open(TOKENS_DATA_PATH, "r") as f:
        logging.INFO("За всё время израсходовано:", json.load(f)["tokens_count"], "токенов")
    
    def create_new_iam_token():
        headers = {"Metadata-Flavor": "Google"}

        try:
            response = requests.get(IAM_TOKEN_ENDPOINT, headers=headers)

        except Exception as e:
            print("Не удалось выполнить запрос:", e)
            print("Токен не получен")

        else:
            if response.status_code == 200:
                token_data = {
                    "access_token": response.json().get("access_token"),
                    "expires_at": response.json().get("expires_in") + time.time()
                }

                with open(IAM_TOKEN_PATH, "w") as token_file:
                    json.dump(token_data, token_file)

            else:
                print("Ошибка при получении ответа:", response.status_code)
                print("Токен не получен")

    def get_iam_token(self) -> str:
        try:
            with open(IAM_TOKEN_PATH, "r") as token_file:
                token_data = json.load(token_file)

            expires_at = token_data.get("expires_at")

            if expires_at <= time.time():
                self.create_new_iam_token()

        except FileNotFoundError:
            self.create_new_iam_token()

        with open(IAM_TOKEN_PATH, "r") as token_file:
            token_data = json.load(token_file)

        return token_data.get("access_token")