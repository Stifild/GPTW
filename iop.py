# Welcome to the IOP (Input/Output Processer) module.

import json, dotenv, os, telebot, random, requests, time

os.mkdir("data") if not os.path.exists("data") else None

from config import ADMIN_LIST, IAM_TOKEN_ENDPOINT, IAM_TOKEN_PATH
from db import Database
from gpt import GPT

db = Database()
gpt = GPT()

dotenv.load_dotenv()

class IOP:
    def __init__(self):
        self.bot_token = os.getenv("TOKEN")
        self.admin_list = ADMIN_LIST
        self.genres = ["Фантастика", "Детектив", "Фэнтези", "Приключения", "Романтика", "Ужасы", "Драма", "Комедия", "Триллер", "Боевик", "Исторический", "Мистика", "Психология", "Философия", "Научно-популярный", "Публицистика"]
    
    def get_user_data(self, user_id: int) -> dict:
        return db.get_user_data(user_id)
    
    def get_all_users(self) -> list[tuple]:
        return db.get_all_users()
    
    def add_user(self, user_id: int):
        db.add_user(user_id)
    
    def check_user(self, user_id: int) -> bool:
        return db.check_user(user_id)
    
    def update_value(self, user_id: int, column: str, value):
        db.update_value(user_id, column, value)
    
    def delete_user(self, user_id: int):
        db.delete_user(user_id)

    def get_system_content(self, task: str, user_id: int) -> str:
        user_data = self.get_user_data(user_id)
        genre = user_data['genre']
        main_character = user_data["main_chareckter"]
        setting = user_data["setting"]
        task_message = f"и эта история должна учитывать это: {task}" if task.lower() != "продолжить без замечаний" else ""
        return f"Сделай историю с жанром {genre}, главным героем {main_character}, сетингом {setting} {task_message}."

    def ask_gpt(self, user_id: int, task: str | None = None) -> str:
        message = json.loads(db.get_user_data(user_id)["messages"])
        if task:
            message.append({"role": "user", "content": task})
        answer = gpt.ask_gpt(message)
        message.append({"role": "assistant", "content": answer})
        self.update_value(user_id, "messages", json.dumps(message, ensure_ascii=False))
        return answer
    
    def count_tokens(self, text: str) -> int:
        return gpt.count_tokens(text)
    
    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_list
    
    def create_reply_markup(self, buttons: list[str]) -> telebot.types.ReplyKeyboardMarkup:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for button in buttons:
            markup.add(button)
        return markup
    
    def get_genres(self) -> list[str]:
        return random.sample(self.genres, 4)
    