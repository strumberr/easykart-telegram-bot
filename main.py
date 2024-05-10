from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import os
import requests
from datetime import datetime
import random
from dotenv import load_dotenv
from components.userStats.userInfo import userStatInfo
from random import shuffle
#kuku

from components.authentication.authenticate import get_auth_bearer, get_access_token
from components.userStats.top10 import top10Drivers

from GoKart_Quiz_Questions import quiz_questions

load_dotenv()

public_authorization_bearer = get_auth_bearer()
kart_access_token = get_access_token(public_authorization_bearer)

# kart_access_token = "04jkwimlmnbninobkil"

apis = {
    "kids": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=242396&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=1000&accessToken={kart_access_token}",
    "normal": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=242392&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=1000&accessToken={kart_access_token}",
    "adults": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=5000&accessToken={kart_access_token}"
}


active_quizzes = {}

async def start(update: Update, context):
    user_name = update.message.from_user.username

    commands = [
        "<b>/userstats</b> - Get user stats",
        "<b>/help</b> - Get help"
    ]

    await update.message.reply_text(f"Hello, {user_name}! Here are the available commands:\n\n" + "\n".join(commands), parse_mode="HTML")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = [
        "<b>Commands:</b>",
        "",
        "<b>/userstats</b> - Get user stats",
        "<b>/help</b> - Get help"
    ]

    await update.message.reply_text("\n".join(commands), parse_mode="HTML")

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

def start_quiz_keyboard():
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("3 Questions", callback_data="quiz3")],
        [InlineKeyboardButton("5 Questions", callback_data="quiz5")],
        [InlineKeyboardButton("10 Questions", callback_data="quiz10")]
    ])
    return keyboard

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Choose how many questions you want for the quiz:", reply_markup=start_quiz_keyboard())

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    quiz_type = query.data
    if quiz_type == "quiz3":
        await setup_quiz(query.message, 1, 1, 1)
    elif quiz_type == "quiz5":
        await setup_quiz(query.message, 2, 2, 1)
    elif quiz_type == "quiz10":
        await setup_quiz(query.message, 5, 3, 2)
        
async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    quiz_type = query.data
    if quiz_type == "quiz3":
        await setup_quiz(query.message, 1, 1, 1)
    elif quiz_type == "quiz5":
        await setup_quiz(query.message, 2, 2, 1)
    elif quiz_type == "quiz10":
        await setup_quiz(query.message, 5, 3, 2)

async def setup_quiz(message, easy, medium, hard):
    chat_id = message.chat_id
    quiz = generate_quiz(easy, medium, hard)
    active_quizzes[chat_id] = {"quiz": quiz, "index": 0, "score": 0}
    await send_question(chat_id, quiz[0], message)

async def send_question(chat_id, question, message):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(option, callback_data=f"answer_{chat_id}_{chr(64 + index)}") for index, option in enumerate(question['options'], start=1)]])
    question_text = question['question']
    await message.reply_text(question_text, reply_markup=keyboard)

async def handle_option_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    _, chat_id, answer_letter = data.split('_')
    await handle_answer(query.message, answer_letter)

async def handle_answer(message, answer_letter):
    chat_id = message.chat_id
    quiz_data = active_quizzes[chat_id]
    current_question = quiz_data["quiz"][quiz_data["index"]]
    correct_answer = current_question["answer"]
    
    answer_index = ord(answer_letter) - 65  # Convert 'A', 'B', 'C' to 0, 1, 2
    is_correct = current_question['options'][answer_index] == correct_answer

    if is_correct:
        quiz_data["score"] += 1

    quiz_data["index"] += 1
    
    if quiz_data["index"] < len(quiz_data["quiz"]):
        await send_question(chat_id, quiz_data["quiz"][quiz_data["index"]], message)
    else:
        await message.reply_text(f"Quiz finished! Your score: {quiz_data['score']}/{len(quiz_data['quiz'])}", reply_markup=start_quiz_keyboard())
        del active_quizzes[chat_id]


async def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu




async def handle_text_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'category' in context.user_data:
        category = context.user_data['category']
        username = update.message.text
        
        message = await update.message.reply_text(f"Retrieving stats for {username} in category {category}...")
        user_info = userStatInfo(username, category.lower(), apis)
        await message.edit_text(user_info[1], parse_mode="HTML")
        
        del context.user_data['category']
    else:
        await update.message.reply_text("For a list of commands, type /help. 🏎️📊")


async def userstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    list_of_cities = ["Kids", "Normal", "Adults"]
    
    button_list = [InlineKeyboardButton(each, callback_data='userstats_' + each) for each in list_of_cities]
    reply_markup = InlineKeyboardMarkup(await build_menu(button_list, n_cols=len(list_of_cities)))
    
    await update.message.reply_text('Please select a category to view detailed GoKart driver stats: 📊', reply_markup=reply_markup)



async def top10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    list_of_cities = ["Kids", "Normal", "Adults"]
    
    button_list = [InlineKeyboardButton(each, callback_data='top10_' + each) for each in list_of_cities]
    reply_markup = InlineKeyboardMarkup(await build_menu(button_list, n_cols=len(list_of_cities)))
    
    await update.message.reply_text('Please select a group to view the top 10 GoKart drivers: 🏎️', reply_markup=reply_markup)

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split('_')
    if parts[0] == 'top10' or parts[0] == 'userstats':
        action, category = parts
        if action == 'top10':
            await query.message.reply_text(f"Retrieving top 10 drivers for the {category} category...")
            top_10_drivers = top10Drivers(category.lower(), apis)
            await query.message.reply_text(top_10_drivers, parse_mode="HTML")
        elif action == 'userstats':
            context.user_data['category'] = category
            await query.message.reply_text(f"Please provide the driver's username for the {category} category:")
    else:
        await handle_query(update, context)


def main():
    bot_token = os.getenv('BOT_TOKEN')
    app = Application.builder().token(bot_token).build()

    # Command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('userstats', userstats))
    app.add_handler(CommandHandler('top10', top10))
    app.add_handler(CommandHandler("quiz", start_quiz))

    # Handler for non-command text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_response))

    # Callback queries handler
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    app.run_polling()

if __name__ == '__main__':
    main()