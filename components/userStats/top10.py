from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import os
import requests
from datetime import datetime
import random



def top10Drivers(category, apis):
    api = apis[category]
    response = requests.get(api)
    data = response.json()

    top_10_drivers = data["records"][:10]

    # Start building the HTML-formatted message
    message = "<b>🏁 Top 10 Fastest Drivers:</b>\n\n"
    for i, driver in enumerate(top_10_drivers, start=1):
        name = driver['participant']
        score = driver['score']
        # Using bold for names, normal text for scores, and ensuring proper alignment
        if i <= 3:
            message += f"<b>🏆 {i}. {name}</b>: {score} sec.\n"
        else:
            message += f"{i}. {name}: {score} sec.\n"

    return message
