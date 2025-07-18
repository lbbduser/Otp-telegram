import os
from flask import Flask, request, jsonify
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
import threading

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME")
ADMIN_ID = os.environ.get("ADMIN_ID")  # your own Telegram user ID as string

bot = Bot(token=BOT_TOKEN)

numbers_file = "numbers.txt"

# Ensure the file exists
if not os.path.exists(numbers_file):
    with open(numbers_file, "w") as f:
        pass

def load_numbers():
    with open(numbers_file, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_number(number):
    numbers = load_numbers()
    if number not in numbers:
        with open(numbers_file, "a") as f:
            f.write(number + "\n")

def delete_number(number):
    numbers = load_numbers()
    numbers.discard(number)
    with open(numbers_file, "w") as f:
        for num in numbers:
            f.write(num + "\n")

def clear_numbers():
    open(numbers_file, "w").close()

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    number = data.get("number")
    service = data.get("service")
    code = data.get("code")
    full_sms = data.get("full_sms")
    now = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

    saved_numbers = load_numbers()
    if number not in saved_numbers:
        return {"status": "skipped (number not saved)"}

    message = f"""✨ New OTP Received ✨

📞 Number: {number}
🔧 Service: {service}
⏰ Time: {now}

🔑 OTP Code: {code}

📩 Full SMS: 
{full_sms}"""

    bot.send_message(chat_id=CHANNEL_USERNAME, text=message)
    return {"status": "sent"}

# Telegram Bot Handlers
def start(update, context):
    update.message.reply_text("👋 Welcome to OTP Bot")

def add(update, context):
    if str(update.effective_user.id) != ADMIN_ID:
        return
    if context.args:
        number = context.args[0]
        save_number(number)
        update.message.reply_text(f"✅ Number {number} added.")
    else:
        update.message.reply_text("⚠️ Usage: /add 8801xxxxxx")

def delete(update, context):
    if str(update.effective_user.id) != ADMIN_ID:
        return
    if context.args:
        number = context.args[0]
        delete_number(number)
        update.message.reply_text(f"🗑 Number {number} deleted.")
    else:
        update.message.reply_text("⚠️ Usage: /delete 8801xxxxxx")

def clear(update, context):
    if str(update.effective_user.id) != ADMIN_ID:
        return
    clear_numbers()
    update.message.reply_text("❌ All numbers deleted.")

def list_numbers(update, context):
    if str(update.effective_user.id) != ADMIN_ID:
        return
    nums = "\n".join(load_numbers())
    update.message.reply_text(f"📄 Saved Numbers:\n{nums}" if nums else "No numbers saved.")

def run_bot():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("delete", delete))
    dp.add_handler(CommandHandler("clear", clear))
    dp.add_handler(CommandHandler("list", list_numbers))

    updater.start_polling()
    updater.idle()

# Run bot in background
threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
