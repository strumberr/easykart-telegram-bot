from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import os
import requests
from datetime import datetime
import random


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

async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    new_file = await update.message.effective_attachment[-1].get_file()
    file = await new_file.download_to_drive()
    
    return file

async def userStats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api = "https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=&startDate=2020-5-1+06%3A00%3A00&endDate=&maxResult=5000&accessToken=87sjcwkcjbcxbboxxob"
    
    response = requests.get(api)
    data = response.json()

    total_records = len(data["records"])
    
    # get all text after the command
    command_parts = update.message.text.split(" ")
    if len(command_parts) > 1:
        searched_user = " ".join(command_parts[1:])
    else:
        await update.message.reply_text("Please specify the user name.")
        return

    searched_user_cleaned = searched_user.replace(" ", "")
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
            
            percentage_to_beat_first = abs(((float(first_place) - float(i['score'])) / float(first_place)) * 100)
            
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
            
            await update.message.reply_text(random_message, parse_mode="HTML")

            break
    else:
        await update.message.reply_text("We could not find that user!")
        
        


# def userButtons(update: Update, context: CallbackContext):
#     keyboard = [
#         [InlineKeyboardButton("Adult", callback_data='adult'),
#          InlineKeyboardButton("Normal", callback_data='normal'),
#          InlineKeyboardButton("Kids", callback_data='kids')]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     update.message.reply_text('Please choose a category:', reply_markup=reply_markup)


# def button(update: Update, context: CallbackContext):
#     query = update.callback_query
#     query.answer()
    
#     # Define different URLs for each category
#     urls = {
#         'adult': "https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=5000&accessToken=87sjcwkcjbcxbboxxob",
#         'normal': "https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=242392&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=1000&accessToken=13inbopbnjkolkoomlp",
#         'kids': "https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=242396&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=1000&accessToken=13inbopbnjkolkoomlp"
#     }
    
#     # Fetch data based on the selected category
#     api_url = urls[query.data]
#     response = requests.get(api_url)
#     data = response.json()

#     update.message.reply_text(f"Stats for in category {query.data}")

        
        
# async def compareTwoDrivers(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     api = "https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=&startDate=2020-5-1+06%3A00%3A00&endDate=&maxResult=5000&accessToken=87sjcwkcjbcxbboxxob"
    
#     response = requests.get(api)
#     data = response.json()



async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # return a list of commands in beautiful html format
    commands = [
        "<b>Commands:</b>",
        "",
        "<b>/userstats</b> - Get user stats",
        "<b>/help</b> - Get help"
    ]
    
    await update.message.reply_text("\n".join(commands), parse_mode="HTML")





# async def image_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
#     file = await downloader(update, context)
    
#     await update.message.reply_text("testing")
    

def main():
    bot_token = os.getenv('BOT_TOKEN')
    app = Application.builder().token(bot_token).build()
    
    app.add_handler(CommandHandler(command='start', callback=start))
    # app.add_handler(MessageHandler(filters.TEXT, callback=handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, downloader))    
    app.add_handler(CommandHandler(command='userstats', callback=userStats))
    
    app.add_handler(CommandHandler(command='help', callback=help))

    # app.add_handler(CommandHandler(command='buttons', callback=userButtons))

  
  
  
    app.run_polling()
    
if __name__ == '__main__':
    main()
