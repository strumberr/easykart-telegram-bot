from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import os
import requests
from datetime import datetime
import random



def userStatInfo(user_name, category, apis):
    
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