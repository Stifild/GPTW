import telebot, logging, iop, json
from config import LOGS_PATH

io = iop.IOP()

logging.basicConfig(filename=LOGS_PATH, level=logging.INFO, format='%(asctime)s - %(message)s', filemode="w")

bot = telebot.TeleBot(io.bot_token)

@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.from_user.id
    if not io.check_user(user_id):
        io.add_user(user_id)
    bot.send_message(user_id, "Привет! Я бот-сценарист. Для начала выбери жанр нашей истории.", reply_markup=io.create_reply_markup(["Выбрать жанр"]))
    logging.info(f"Пользователь {user_id} начал работу")
    bot.register_next_step_handler(message, )

def filter_choose_genre(message):
    return message.text.lower() in ["выбрать жанр", "другой жанр"]

@bot.message_handler(func=filter_choose_genre)
def choose_genre(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Выбери жанр из списка или напиши свой.", reply_markup=io.create_reply_markup(io.get_genres()))
    bot.register_next_step_handler(message, select_genre)

def select_genre(message):
    user_id = message.from_user.id
    genre = message.text
    io.update_value(user_id, "genre", genre)
    bot.send_message(user_id, "Отлично! Теперь выбери Главного героя или напиши своего.", reply_markup=io.create_reply_markup(io.get_characters()))
    bot.register_next_step_handler(message, select_main_character)

def filter_choose_main_character(message):
    return message.text.lower() in ["изменить главного героя"]

@bot.message_handler(func=filter_choose_main_character)
def choose_main_character(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Выбери Главного героя из списка или напиши своего.", reply_markup=io.create_reply_markup(io.get_characters()))
    bot.register_next_step_handler(message, select_main_character)

def select_main_character(message):
    user_id = message.from_user.id
    character = message.text
    io.update_value(user_id, "main_character", character)
    bot.send_message(user_id, "Отлично! Теперь выбери сеттинг или напиши свой.", reply_markup=io.create_reply_markup(io.get_settings()))
    bot.register_next_step_handler(message, select_setting)

def filter_choose_setting(message):
    return message.text.lower() in ["изменить сеттинг"]

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
    
    bot.register_next_step_handler(message, write_story)
    