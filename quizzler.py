import telebot
from random import shuffle
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from GoKart_Quiz_Questions import quiz_questions

bot = telebot.TeleBot("7182734140:AAH5cVKOP_zGNm8VXH3V77m9WT-0WLk8lwY")

def generate_quiz(easy_count, medium_count, hard_count):
    quiz = []
    shuffle(quiz_questions["easy"])
    shuffle(quiz_questions["medium"])
    shuffle(quiz_questions["hard"])
    quiz.extend(quiz_questions["easy"][:easy_count])
    quiz.extend(quiz_questions["medium"][:medium_count])
    quiz.extend(quiz_questions["hard"][:hard_count])
    shuffle(quiz)
    return quiz

active_quizzes = {}

def start_quiz_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("3 Questions", callback_data="quiz3"))
    keyboard.add(InlineKeyboardButton("5 Questions", callback_data="quiz5"))
    keyboard.add(InlineKeyboardButton("10 Questions", callback_data="quiz10"))
    return keyboard

@bot.message_handler(commands=['quiz'])
def start_quiz(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Choose how many question quiz you want:", reply_markup=start_quiz_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("quiz"))
def handle_query(call):
    quiz_type = call.data
    if quiz_type == "quiz3":
        setup_quiz(call.message, 1, 1, 1)
    elif quiz_type == "quiz5":
        setup_quiz(call.message, 2, 2, 1)
    elif quiz_type == "quiz10":
        setup_quiz(call.message, 5, 3, 2)

def setup_quiz(message, easy, medium, hard):
    chat_id = message.chat.id
    quiz = generate_quiz(easy, medium, hard)
    active_quizzes[chat_id] = {"quiz": quiz, "index": 0, "score": 0}
    send_question(chat_id, quiz[0])

def send_question(chat_id, question):
    keyboard = InlineKeyboardMarkup()
    options = question['options']
    callback_data_prefix = f"{chat_id}_answer_"
    for index, option in enumerate(options, start=1):
        keyboard.add(InlineKeyboardButton(option, callback_data=f"{callback_data_prefix}{chr(64+index)}"))
    question_text = f"{question['question']}"
    bot.send_message(chat_id, question_text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.endswith(('A', 'B', 'C')))
def handle_option_click(call):
    handle_answer(call.message, call.data[-1])

@bot.message_handler(func=lambda message: message.chat.id in active_quizzes)
def handle_answer(message, text=None):
    chat_id = message.chat.id
    answer = (text or message.text).upper()
    quiz_data = active_quizzes[chat_id]
    current_question = quiz_data["quiz"][quiz_data["index"]]

    if answer not in ['A', 'B', 'C']:
        bot.send_message(chat_id, "Wrong input, please try again!")
        send_question(chat_id, current_question)
    else:
        if answer == current_question["answer"]:
            quiz_data["score"] += 1
        quiz_data["index"] += 1
        
        if quiz_data["index"] < len(quiz_data["quiz"]):
            send_question(chat_id, quiz_data["quiz"][quiz_data["index"]])
        else:
            bot.send_message(chat_id, f"Quiz finished! Your score: {quiz_data['score']}/{len(quiz_data['quiz'])}", reply_markup=start_quiz_keyboard())
            del active_quizzes[chat_id]

bot.polling()
