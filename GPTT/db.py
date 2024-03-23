import sqlite3, logging
from config import LOGS_PATH, DB_NAME, DB_TABLE_USERS_NAME

logging.basicConfig(filename=LOGS_PATH, level=logging.INFO, format='%(asctime)s - %(message)s', filemode="w")

class Database:
    def __init__(self):
        self.create_table()
    
    def executer(self, command: str, data: tuple = None):
        try:
            self.connection = sqlite3.connect(DB_NAME)
            self.cursor = self.connection.cursor()

            if data:
                self.cursor.execute(command, data)
                self.connection.commit()

            else:
                self.cursor.execute(command)

        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса: ", e)

        else:
            result = self.cursor.fetchall()
            self.connection.close()
            return result
    
    def create_table(self):
        self.executer(f"CREATE TABLE IF NOT EXISTS {DB_TABLE_USERS_NAME} (id INTEGER PRIMARY KEY, user_id INTEGER, level TEXT, subject TEXT, messages TEXT)")
        logging.info(f"Таблица {DB_TABLE_USERS_NAME} создана")
    
    def add_user(self, user_id: int):
        self.executer(f"INSERT INTO {DB_TABLE_USERS_NAME} (user_id) VALUES (?)", (user_id,))
        logging.info(f"Добавлен пользователь {user_id}")
    
    def check_user(self, user_id: int) -> bool:
        result = self.executer(f"SELECT * FROM {DB_TABLE_USERS_NAME} WHERE user_id=?", (user_id,))
        return bool(result)
    
    def update_value(self, user_id: int, column: str, value):
        self.executer(f"UPDATE {DB_TABLE_USERS_NAME} SET {column}=? WHERE user_id=?", (value, user_id))
        logging.info(f"Обновлено значение {column} для пользователя {user_id}")
    
    def get_user_data(self, user_id: int):
        result = self.executer(f"SELECT * FROM {DB_TABLE_USERS_NAME} WHERE user_id=?", (user_id,))
        presult = {
            "id": result[0][0],
            "user_id": result[0][1],
            "level": result[0][2],
            "subject": result[0][3],
            "messages": result[0][4]
        }
        return presult
    
    def delete_user(self, user_id: int):
        self.executer(f"DELETE FROM {DB_TABLE_USERS_NAME} WHERE user_id=?", (user_id,))
        logging.info(f"Удален пользователь {user_id}")
    
