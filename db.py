import sqlite3, logging

from config import DB_NAME, DB_TABLE_USERS_NAME, LOGS_PATH

logging.basicConfig(filename=LOGS_PATH, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filemode="w")

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
            logging.error("Ошибка при выполнении запроса: ", e)

        else:
            result = self.cursor.fetchall()
            self.connection.close()
            return result


    def create_table(self):
        self.executer(
            f"CREATE TABLE IF NOT EXISTS {DB_TABLE_USERS_NAME} "
            f"(id INTEGER PRIMARY KEY, "
            f"user_id INTEGER, "
            f"sessions INTEGER, "
            f"tokens INTEGER, "
            f"subject TEXT, "
            f"level TEXT, "
            f"messages TEXT"
            f"is_blocked INTEGER);"
        )
        logging.info(f"Таблица {DB_TABLE_USERS_NAME} создана")


    def add_user(self, user_id: int):
        self.executer(
            f"INSERT INTO {DB_TABLE_USERS_NAME} "
            f"(user_id, sessions, is_blocked) "
            f"VALUES (?, 0, 0);"
        )
        logging.info(f"Добавлен пользователь {user_id}")


    def check_user(self, user_id: int) -> bool:
        result = self.executer(f"SELECT user_id FROM {DB_TABLE_USERS_NAME} WHERE user_id=?", (user_id,))
        return bool(result)


    def update_value(self, user_id: int, column: str, value):
        self.executer(f"UPDATE {DB_TABLE_USERS_NAME} SET {column}=? WHERE user_id=?", (value, user_id))
        logging.info(f"Обновлено значение {column} для пользователя {user_id}")


    def get_user_data(self, user_id: int):
        result = self.executer(f"SELECT * FROM {DB_TABLE_USERS_NAME} WHERE user_id=?", (user_id,))
        presult = {
            "sessions": result[2],
            "tokens": result[3],
            "subject": result[4],
            "level": result[5],
            "messages": result[6],
            "is_blocked": result[7]
        }
        return presult
    
    def get_all_users(self) -> list[tuple[int, int, int, int, str, str, str]]:
        sql_query = (
            f"SELECT * "
            f"FROM {DB_TABLE_USERS_NAME};"
        )

        result = self.executer(sql_query)
        return result

    def delete_user(self, user_id: int):
        self.executer(f"DELETE FROM {DB_TABLE_USERS_NAME} WHERE user_id=?", (user_id,))
        logging.warning(f"Удален пользователь {user_id}")
