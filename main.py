from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import os
import requests
from datetime import datetime
import random
from dotenv import load_dotenv
from components.userStats.userInfo import userStatInfo

from components.authentication.authenticate import get_auth_bearer, get_access_token
from components.userStats.top10 import top10Drivers

from components.quiz.quizQuestions import quiz_questions
from components.userStats.compareDrivers import compareDriversStats

load_dotenv()

public_authorization_bearer = get_auth_bearer()
kart_access_token = get_access_token(public_authorization_bearer)

# kart_access_token = "30npomaynanpnoioomm"

apis = {
    "kids": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=242396&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=1000&accessToken={kart_access_token}",
    "normal": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=242392&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=1000&accessToken={kart_access_token}",
    "adults": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=5000&accessToken={kart_access_token}"
}


async def start(update: Update, context):
    user_name = update.message.from_user.username

    commands = [
        "<b>Commands:</b>",
        "",
        "<b>/userstats</b> - Get user stats",
        "<b>/compare</b> - Compare two drivers",
        "<b>/help</b> - Get help",
        "<b>/top10</b> - Get top 10 drivers",
        "<b>/quiz</b> - Do a quiz",
        
    ]

    await update.message.reply_text(f"Hello, {user_name}! Here are the available commands:\n\n" + "\n".join(commands), parse_mode="HTML")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = [
        "<b>Commands:</b>",
        "",
        "<b>/userstats</b> - Get user stats",
        "<b>/compare</b> - Compare two drivers",
        "<b>/help</b> - Get help",
        "<b>/top10</b> - Get top 10 drivers",
        "<b>/quiz</b> - Do a quiz",
        
    ]

    await update.message.reply_text("\n".join(commands), parse_mode="HTML")



async def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu






async def handle_text_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'action' in context.user_data:
        if context.user_data['action'] == 'userstats':
            category = context.user_data['category']
            username = update.message.text
            message = await update.message.reply_text(f"Retrieving stats for {username} in category {category}...")
            user_info = userStatInfo(username, category.lower(), apis)
            await message.edit_text(user_info[1], parse_mode="HTML")
            del context.user_data['action'], context.user_data['category']
        elif context.user_data['action'] == 'compare':
            if 'first_username' not in context.user_data:
                context.user_data['first_username'] = update.message.text
                await update.message.reply_text("Enter the second driver's username for comparison:")
            else:
                first_username = context.user_data['first_username']
                second_username = update.message.text
                category = context.user_data['category']
                
                message = await update.message.reply_text(f"Comparing {first_username} and {second_username}...")
                result, comparison_message = compareDriversStats(first_username, second_username, category.lower(), apis)
                if result:
                    await message.edit_text(comparison_message, parse_mode="HTML")
                else:
                    await message.edit_text(comparison_message)
                
                # Clear context data after comparison
                del context.user_data['action'], context.user_data['category'], context.user_data['first_username']
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
    query_data = update.callback_query.data
    action, category = query_data.split('_')
    
    if action in ['top10', 'userstats', 'compare']:
        await update.callback_query.answer()
        context.user_data['action'] = action
        context.user_data['category'] = category
        
        if action == 'top10':
            await update.callback_query.message.reply_text(f"Retrieving top 10 drivers for the {category} category...")
            top_10_drivers = top10Drivers(category.lower(), apis)
            await update.callback_query.message.reply_text(top_10_drivers, parse_mode="HTML")
        elif action == 'userstats':
            await update.callback_query.message.reply_text(f"Please provide the driver's username for the {category} category:")
        elif action == 'compare':
            await update.callback_query.message.reply_text("Enter the first driver's username for comparison:")


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
        
    await update.message.reply_text("If you want to do a quiz about gokarts, go to this bot: https://t.me/quizller_kart_bot 🏎️📝")



async def compare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    list_of_categories = ["Kids", "Normal", "Adults"]
    
    button_list = [InlineKeyboardButton(each, callback_data='compare_' + each) for each in list_of_categories]
    reply_markup = InlineKeyboardMarkup(await build_menu(button_list, n_cols=len(list_of_categories)))
    
    await update.message.reply_text('Please select a category to compare GoKart drivers: 📊', reply_markup=reply_markup)





def main():
    bot_token = os.getenv('BOT_TOKEN')
    app = Application.builder().token(bot_token).build()

    # Command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('userstats', userstats))
    app.add_handler(CommandHandler('top10', top10))

    # Callback queries handler
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    # Handler for non-command text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_response))
    
    # Quiz handler
    app.add_handler(CommandHandler('quiz', quiz))
    
    # Compare handler
    app.add_handler(CommandHandler('compare', compare))

    app.run_polling()


if __name__ == '__main__':
    main()
