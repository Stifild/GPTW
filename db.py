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
            f"genre TEXT, "
            f"main_charecter TEXT, "
            f"setting TEXT, "
            f"messages TEXT, "
            f"is_blocked INTEGER, "
            f"library TEXT);"
        )
        logging.info(f"Таблица {DB_TABLE_USERS_NAME} создана")


    def add_user(self, user_id: int):
        try:
            self.executer(
                f"INSERT INTO {DB_TABLE_USERS_NAME} "
                f"(user_id, sessions, is_blocked) "
                f"VALUES (?, 0, 0);", (user_id,)
            )
            logging.info(f"Добавлен пользователь {user_id}")
        except Exception as e:
            logging.error(f"Возникла ошибка при добавлении пользователя {user_id}: {e}")


    def check_user(self, user_id: int) -> bool:
        try:
            result = self.executer(f"SELECT user_id FROM {DB_TABLE_USERS_NAME} WHERE user_id=?", (user_id,))
            return bool(result)
        except Exception as e:
            logging.error(f"Возникла ошибка при проверке пользователя {user_id}: {e}")
        


    def update_value(self, user_id: int, column: str, value):
        try:
            self.executer(f"UPDATE {DB_TABLE_USERS_NAME} SET {column}=? WHERE user_id=?", (value, user_id))
            logging.info(f"Обновлено значение {column} для пользователя {user_id}")
        except Exception as e:
            logging.error(f"Возникла ошибка при обновлении значения {column} для пользователя {user_id}: {e}")


    def get_user_data(self, user_id: int):
        try:
            result = self.executer(f"SELECT * FROM {DB_TABLE_USERS_NAME} WHERE user_id=?", (user_id,))
            presult = {
                "sessions": result[0][2],
                "tokens": result[0][3],
                "genry": result[0][4],
                "main_charecter": result[0][5],
                "setting": result[0][6],
                "messages": result[0][7],
                "is_blocked": result[0][8],
                "library": result[0][9]
            }
            return presult
        except Exception as e:
            logging.error(f"Возникла ошибка при получении данных пользователя {user_id}: {e}")
    
    def get_all_users(self) -> list[tuple[int, int, int, int, str, str, str]]:
        try:
            result = self.executer(f"SELECT * FROM {DB_TABLE_USERS_NAME}")
            return result
        except Exception as e:
            logging.error(f"Возникла ошибка при получении данных всех пользователей: {e}")

    def delete_user(self, user_id: int):
        try:
            self.executer(f"DELETE FROM {DB_TABLE_USERS_NAME} WHERE user_id=?", (user_id,))
            logging.warning(f"Удален пользователь {user_id}")
        except Exception as e:
            logging.error(f"Возникла ошибка при удалении пользователя {user_id}: {e}")