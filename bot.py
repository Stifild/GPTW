import telebot, logging, json
from iop import IOP
from config import LOGS_PATH, MAX_USERS, MAX_COUNT_OF_SESSIONS

io = IOP()

logging.basicConfig(filename=LOGS_PATH, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode="w")

bot = telebot.TeleBot(io.bot_token)

@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.from_user.id
    if not io.check_user(user_id) or io.get_user_data(user_id)["is_blocked"]:
        if len(io.get_all_users()) < MAX_USERS:
            io.add_user(user_id)
        else:
            io.add_user(user_id)
            io.update_value(user_id, "is_blocked", True)
            bot.send_message(
                user_id,
                "К сожалению, лимит пользователей исчерпан. "
                "Вы не сможете воспользоваться ботом:("
            )
            return
    bot.send_message(user_id, "Привет! Я бот-сценарист. Для начала выбери жанр нашей истории.", reply_markup=io.create_reply_markup(["Выбрать жанр"]))
    logging.info(f"Пользователь {user_id} начал работу")
    bot.register_next_step_handler(message, choose_genre)

def filter_choose_genre(message):
    return message.text.lower() in ["выбрать жанр", "другой жанр", "начать новую историю"] if not io.get_user_data(message.from_user.id)["is_blocked"] else False

@bot.message_handler(func=filter_choose_genre)
def choose_genre(message):
    user_id = message.from_user.id
    io.update_value(user_id, "sessions", io.get_user_data(user_id)['sessions']+1)
    io.update_value(user_id, "tokens", MAX_COUNT_OF_SESSIONS)
    bot.send_message(user_id, "Начало новой истории!!! Выбери жанр из списка или напиши свой.", reply_markup=io.create_reply_markup(io.get_genres()))
    bot.register_next_step_handler(message, select_genre)

def select_genre(message):
    user_id = message.from_user.id
    genre = message.text
    io.update_value(user_id, "genre", genre)
    bot.send_message(user_id, "Отлично! Теперь выбери Главного героя или напиши своего.", reply_markup=io.create_reply_markup(io.get_characters()))
    bot.register_next_step_handler(message, select_main_character)

def filter_choose_main_character(message):
    return message.text.lower() in ["изменить главного героя"] if not io.get_user_data(message.from_user.id)["is_blocked"] else False

@bot.message_handler(func=filter_choose_main_character)
def choose_main_character(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Выбери Главного героя из списка или напиши своего.", reply_markup=io.create_reply_markup(io.get_characters()))
    bot.register_next_step_handler(message, select_main_character)

def select_main_character(message):
    user_id = message.from_user.id
    character = message.text
    io.update_value(user_id, "main_charecter", character)
    bot.send_message(user_id, "Отлично! Теперь выбери сеттинг или напиши свой.", reply_markup=io.create_reply_markup(io.get_settings()))
    bot.register_next_step_handler(message, select_setting)

def filter_choose_setting(message):
    return message.text.lower() in ["изменить сеттинг"] if not io.get_user_data(message.from_user.id)["is_blocked"] else False

@bot.message_handler(func=filter_choose_setting)
def choose_setting(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Выбери сеттинг из списка или напиши свой.", reply_markup=io.create_reply_markup(io.get_settings()))
    bot.register_next_step_handler(message, select_setting)

def select_setting(message):
    user_id = message.from_user.id
    setting = message.text
    io.update_value(user_id, "setting", setting)
    bot.send_message(user_id, "Отлично! Теперь если хочешь отправь какие-то свои замечания.", reply_markup=io.create_reply_markup(["Продолжить без замечаний"]))
    bot.register_next_step_handler(message, write_story)

def write_story(message):
    user_id = message.from_user.id
    task = message.text
    if task.lower() == "закончить":
        bot.send_message(user_id, "Возврашаюсь в меню.")
        io.update_value(user_id, "library", json.dumps([json.loads(io.get_user_data(user_id)["library"])].append(io.get_user_data(user_id)["messages"])))
        menu(message)
        return
    bot.send_chat_action(user_id, "typing")
    answer = io.ask_gpt(user_id, task)
    bot.send_message(user_id, answer+"\n\nПродолжи отрвок.", reply_markup=io.create_reply_markup(["Закончить"]))
    bot.register_next_step_handler(message, write_story)
    if io.get_user_data(user_id)["tokens"] == 0:
        io.update_value(user_id, "library", json.dumps([json.load(io.get_user_data(user_id)["library"])].append(io.get_user_data(user_id)["messages"])))
        bot.send_message(user_id, "Лимит истории исчерпан. Возвращаюсь в меню.")
        menu(message)
    
def filter_show_limits(message):
    return message.text.lower() in ["мои лимиты"] if not io.get_user_data(message.from_user.id)["is_blocked"] else False

@bot.message_handler(func=filter_show_limits)
def show_limits(message):
    user_id = message.from_user.id
    user_data = io.get_user_data(user_id)
    bot.send_message(user_id, f"Ты начал {user_data['sessions']} историй. У тебя осталось {MAX_COUNT_OF_SESSIONS - user_data['sessions']} историй.")
    menu(message)

def filter_show_about(message):
    return message.text.lower() in ["о боте"] if not io.get_user_data(message.from_user.id)["is_blocked"] else False

@bot.message_handler(func=filter_show_about)
def show_about(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Бот-сценарист создан для помощи в написании историй. Он использует нейросеть для генерации текста. Приятного использования!")
    menu(message)

def filter_show_library(message):
    return message.text.lower() in ["библиотека историй"] if not io.get_user_data(message.from_user.id)["is_blocked"] else False

@bot.message_handler(func=filter_show_library)
def show_library(message):
    user_id = message.from_user.id
    library = io.get_user_data(user_id)["library"]
    if library != "[]":
        bot.send_message(user_id, "Вот твои истории:")
        for story in json.loads(library):
            bot.send_message(user_id, story)
        menu(message)
    bot.send_message(user_id, "Библиотека историй пуста. Возвращаюсь в меню.")
    menu(message)

def menu(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Выбери действие:", reply_markup=io.create_reply_markup(["Начать новую историю", "Библиотека историй", "Мои лимиты", "О боте"]))

bot.infinity_polling(none_stop=True)
    