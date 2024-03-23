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
    bot.send_message(user_id, "Привет! Я бот-помощник. Для начала выбери предмет.", reply_markup=io.create_reply_markup(["Выбрать предмет"]))
    logging.info(f"Пользователь {user_id} начал работу")
    bot.register_next_step_handler(message, choose_subject)

def filter_choose_subject(message):
    return message.text.lower() in ["выбрать предмет", "другой предмет"]

@bot.message_handler(func=filter_choose_subject)
def choose_subject(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Выбери предмет из списка:", reply_markup=io.create_reply_markup(["Математика", "Физика", "Химия", "Информатика"]))
    bot.register_next_step_handler(message, select_subject)

def select_subject(message):
    user_id = message.from_user.id
    subject = message.text
    if subject.lower() in ["математика", "физика", "химия", "информатика"]:
        subject = subject.lower()
        io.update_value(user_id, "subject", subject)
        bot.send_message(user_id, "Теперь выбери уровень сложности обьяснения:", reply_markup=io.create_reply_markup(["Легкий", "Средний", "Сложный"]))
        bot.register_next_step_handler(message, select_level)
    else:
        bot.send_message(user_id, "Пожалуйста, выбери предмет из списка.", reply_markup=io.create_reply_markup(["Математика", "Физика", "Химия", "Информатика"]))
        bot.register_next_step_handler(message, select_subject)

def filter_choose_level(message):
    return message.text.lower() in ["изменить уровень сложности"]

@bot.message_handler(func=filter_choose_level)
def choose_level(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Выбери уровень сложности обьяснения:", reply_markup=io.create_reply_markup(["Легкий", "Средний", "Сложный"]))
    bot.register_next_step_handler(message, select_level)

def select_level(message):
    user_id = message.from_user.id
    level = message.text
    if level.lower() in ["легкий", "средний", "сложный"]:
        level = level.lower()
        io.update_value(user_id, "level", level)
        messages = json.dumps([{"role": "system", "content": io.get_system_content(io.get_user_data(user_id)["subject"], io.get_user_data(user_id)["level"])}], ensure_ascii=False)
        io.update_value(user_id, "messages", messages)
        bot.send_message(user_id, "Отлично! Теперь ты можешь задать свой вопрос.", reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, ask_question)
    else:
        bot.send_message(user_id, "Пожалуйста, выбери уровень сложности из списка.", reply_markup=io.create_reply_markup(["Легкий", "Средний", "Сложный"]))
        bot.register_next_step_handler(message, select_level)

def filter_solve_question(message):
    return message.text.lower() in ["задать другой вопрос"]

@bot.message_handler(func=filter_solve_question)
def solve_question(message):
    user_id = message.from_user.id
    messages = json.dumps([{"role": "system", "content": io.get_system_content(io.get_user_data(user_id)["subject"], io.get_user_data(user_id)["level"])}], ensure_ascii=False)
    io.update_value(user_id, "messages", messages)
    bot.send_message(user_id, "Теперь ты можешь задать свой вопрос.", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, ask_question)

def filter_continue_explanation(message):
    return message.text.lower() in ["продолжить обьяснение"]

@bot.message_handler(func=filter_continue_explanation)
def continue_explanation(message):
    user_id = message.from_user.id
    bot.send_chat_action(user_id, "typing")
    answer = io.ask_gpt(user_id)
    bot.send_message(user_id, answer, reply_markup=io.create_reply_markup(["Изменить уровень сложности", "Другой предмет", "Продолжить обьяснение", "Задать другой вопрос"]))

def ask_question(message):
    user_id = message.from_user.id
    task = message.text
    bot.send_chat_action(user_id, "typing")
    answer = io.ask_gpt(user_id, task)
    bot.send_message(user_id, answer, reply_markup=io.create_reply_markup(["Изменить уровень сложности", "Другой предмет", "Продолжить обьяснение", "Задать другой вопрос"]))

@bot.message_handler(commands=["logs"])
def send_logs(message):
    user_id = message.from_user.id
    if io.is_admin(user_id):
        with open(LOGS_PATH, "r") as file:
            bot.send_document(user_id, file)

bot.infinity_polling()
    