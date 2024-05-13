from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import os
import requests
from datetime import datetime
import random

def compareDriversStats(user1, user2, category, apis):
    api = apis[category]
    
    response = requests.get(api)
    data = response.json()

    total_records = len(data["records"])

    user1_cleaned = user1.replace(" ", "").lower()
    user2_cleaned = user2.replace(" ", "").lower()

    user1_stats = None
    user2_stats = None

    for record in data["records"]:
        current_user = record['participant'].replace(" ", "").lower()
        if current_user == user1_cleaned:
            user1_stats = extractUserStats(record, total_records)
        elif current_user == user2_cleaned:
            user2_stats = extractUserStats(record, total_records)

        if user1_stats and user2_stats:
            break

    if not user1_stats:
        return False, f"User {user1} not found in the records"
    if not user2_stats:
        return False, f"User {user2} not found in the records"

    comparison_message = createComparisonMessage(user1, user2, user1_stats, user2_stats)
    return True, comparison_message

def extractUserStats(record, total_records):
    score = float(record['score'])
    position = record['position']
    percentile = (position / total_records) * 100
    return {
        "score": score,
        "position": position,
        "percentile": percentile
    }

def createComparisonMessage(user1, user2, stats1, stats2):

    winner = user1 if stats1["score"] < stats2["score"] else user2
    loser = user2 if stats1["score"] < stats2["score"] else user1
    winning_stats = stats1 if stats1["score"] < stats2["score"] else stats2
    losing_stats = stats2 if stats1["score"] < stats2["score"] else stats1

    time_difference = abs(winning_stats['score'] - losing_stats['score'])
    
    percentage_difference = (time_difference / losing_stats['score']) * 100

    return (
        f"<b>🏎️ Driver Comparison:</b>\n\n"
        f"<b>{user1}</b>:\n"
        f"  🚀 <b>Lap Time:</b> <i>{stats1['score']} seconds</i>\n"
        f"  🏁 <b>Position:</b> {stats1['position']} (Top {stats1['percentile']:.2f}%)\n\n"
        f"<b>{user2}</b>:\n"
        f"  🚀 <b>Lap Time:</b> <i>{stats2['score']} seconds</i>\n"
        f"  🏁 <b>Position:</b> {stats2['position']} (Top {stats2['percentile']:.2f}%)\n\n"
        f"<b>🏆 Winner:</b> {winner} with <i>{winning_stats['score']} seconds</i>.\n"
        f"🥈 {loser} is <i>{time_difference:.3f} seconds</i> behind ({percentage_difference:.2f}% slower).\n"
        f"<i>Fastest lap time achieved!</i>"
    )
