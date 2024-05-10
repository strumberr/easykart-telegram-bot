from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from random import shuffle

from GoKart_Quiz_Questions import quiz_questions

TOKEN = "7182734140:AAH5cVKOP_zGNm8VXH3V77m9WT-0WLk8lwY"
active_quizzes = {}

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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    greeting = "Hello, I am quiz bot for go-karts, do the quiz to become better in real life! for stating the quiz, use command: /quiz"
    await update.message.reply_text(greeting)

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

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("quiz", start_quiz))
    app.add_handler(CallbackQueryHandler(handle_query, pattern="^quiz[3|5|10]$"))
    app.add_handler(CallbackQueryHandler(handle_option_click, pattern="^answer_"))
    app.run_polling()

if __name__ == "__main__":
    main()
