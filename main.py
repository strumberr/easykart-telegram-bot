from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import os
import requests
from datetime import datetime
import random
from dotenv import load_dotenv


load_dotenv()

kart_access_token = "54jkwilsnowmnnsmkso"


apis = {
    "kids": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=242396&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=1000&accessToken={kart_access_token}",
    "normal": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=242392&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=1000&accessToken={kart_access_token}",
    "adults": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=5000&accessToken={kart_access_token}"
}


async def start(update: Update, context):
    user_name = update.message.from_user.username

    commands = [
        "<b>/userstats</b> - Get user stats",
        "<b>/help</b> - Get help"
    ]

    await update.message.reply_text(f"Hello, {user_name}! Here are the available commands:\n\n" + "\n".join(commands), parse_mode="HTML")


async def handle_text(update: Update, context):
    # reply with the same message
    await update.message.reply_text(update.message.text)


def userStatInfo(user_name, category):
    
    api = apis[category]
    
    response = requests.get(api)
    data = response.json()

    total_records = len(data["records"])

    searched_user_cleaned = user_name.replace(" ", "")
    print(f"searched_user_cleaned: {searched_user_cleaned}")

    first_place = data["records"][0]["score"]

    for i in data["records"]:
        current_user = str(i['participant'].replace(" ", ""))
        # print(f"current_user: {current_user}")
        if current_user == searched_user_cleaned:

            date = i['date']
            formatted_date = date.split("T")[0]
            date_object = datetime.strptime(formatted_date, '%Y-%m-%d')
            day_of_week = date_object.strftime('%A')

            player_top_percentage = (i['position'] / total_records) * 100

            percentage_to_beat_first = abs(
                ((float(first_place) - float(i['score'])) / float(first_place)) * 100)

            seconds_to_beat_first = float(first_place) - float(i['score'])

            label = ""
            if player_top_percentage >= 80:
                label = "Newbie"
            elif player_top_percentage >= 60:
                label = "Beginner"
            elif player_top_percentage >= 40:
                label = "Amateur"
            elif player_top_percentage >= 20:
                label = "Pro"
            elif player_top_percentage >= 10:
                label = "Epic"
            elif player_top_percentage >= 1:
                label = "Legendary"
            else:
                label = "Track Owner"

            message1 = (
                f"<b>🏎️ Participant:</b> {i['participant']}\n"
                f"<b>🚀 Fastest Lap:</b> <i>{i['score']} seconds</i>\n"
                f"<b>📅 Date:</b> {formatted_date} ({day_of_week})\n"
                f"<b>🏆 Position:</b> {i['position']} out of {total_records}\n"
                f"<b>📊 Top Percentile:</b> <i>Top {player_top_percentage:.2f}%</i> of all racers\n"
                f"<b>⏱️ Gap to Lead:</b> <i>{abs(seconds_to_beat_first):.3f} seconds</i> faster needed ({percentage_to_beat_first:.2f}%)"
                f"\n<b>Performance Label:</b> <i>{label}</i> 🏅"
                "\n\n<b>Let's aim even higher next time!</b> 🎉"
            )

            message2 = (
                f"<b>🏎️ Racer:</b> {i['participant']}\n"
                f"<b>🚀 Lap Time:</b> <i>{i['score']} seconds</i>\n"
                f"<b>📅 Race Date:</b> {formatted_date} ({day_of_week})\n"
                f"<b>🏆 Final Position:</b> {i['position']} out of {total_records}\n"
                f"<b>📊 Performance:</b> <i>Top {player_top_percentage:.2f}%</i> among all participants\n"
                f"<b>⏱️ Gap to Leader:</b> <i>{abs(seconds_to_beat_first):.3f} seconds</i> faster needed ({percentage_to_beat_first:.2f}%)"
                f"\n<b>Performance Label:</b> <i>{label}</i> 🏅"
                "\n\n<b>Strive for excellence in the next race!</b> 🏁"
            )

            message3 = (
                f"<b>🏎️ Driver:</b> {i['participant']}\n"
                f"<b>🚀 Best Lap:</b> <i>{i['score']} seconds</i>\n"
                f"<b>📅 Event Date:</b> {formatted_date} ({day_of_week})\n"
                f"<b>🏆 Final Placement:</b> {i['position']} out of {total_records}\n"
                f"<b>📊 Performance Rank:</b> <i>Top {player_top_percentage:.2f}%</i> overall\n"
                f"<b>⏱️ Difference to Lead:</b> <i>{abs(seconds_to_beat_first):.3f} seconds</i> faster required ({percentage_to_beat_first:.2f}%)"
                f"\n<b>Performance Label:</b> <i>{label}</i> 🏅"
                "\n\n<b>Keep pushing boundaries for greater achievements!</b> 🏅"
            )

            message_options = [message1, message2, message3]
            random_message = random.choice(message_options)

            return True, random_message
    else:
        return False, "User not found in the records"



async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # return a list of commands in beautiful html format
    commands = [
        "<b>Commands:</b>",
        "",
        "<b>/userstats</b> - Get user stats",
        "<b>/help</b> - Get help"
    ]

    await update.message.reply_text("\n".join(commands), parse_mode="HTML")




async def userstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    list_of_cities = ["Kids", "Normal", "Adults"]
    button_list = []
    for each in list_of_cities:
        button_list.append(InlineKeyboardButton(each, callback_data=each))
    

    reply_markup = InlineKeyboardMarkup(await build_menu(button_list, n_cols=len(list_of_cities)))

    

    if update.message:
        if 'category' in context.user_data:
            del context.user_data['category']
        else:
            await update.message.reply_text('Please select a category to view detailed GoKart driver stats: 📊', reply_markup=reply_markup)
    
    elif update.callback_query:
        button_pressed = update.callback_query.data
        context.user_data['category'] = button_pressed  # Store the selected category in user_data

        await update.callback_query.answer()
        await update.callback_query.message.reply_text(f"Please provide the driver's username for the {button_pressed} category:")
    
    else:
        pass



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
        user_info = userStatInfo(username, category.lower())
        await message.edit_text(user_info[1], parse_mode="HTML")
        
        # Clear the user_data category to reset the state
        del context.user_data['category']
    else:
        await update.message.reply_text("For a list of commands, type /help. 🏎️📊")




def main():
    bot_token = os.getenv('BOT_TOKEN')
    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler(command='start', callback=start))
    # app.add_handler(CommandHandler(command='userstats', callback=userStats))

    # add the buttons
    app.add_handler(CommandHandler('userstats', userstats))
    
    # Handler for non-command text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_response))
    app.add_handler(CallbackQueryHandler(userstats))
    


    app.add_handler(CommandHandler(command='help', callback=help))

    app.run_polling()


if __name__ == '__main__':
    main()
