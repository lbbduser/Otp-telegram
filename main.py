from flask import Flask, request, jsonify
import os, re, datetime, requests

app = Flask(__name__)

BOT_TOKEN = "7801552754:AAEsZECDJLu78eKTfT0X1XsS4BL85lfx9rE"
CHANNEL_ID = "@kofb11"

OTP_STORE = {}

def country_flag(number):
    if number.startswith("+880"): return "🇧🇩"
    if number.startswith("+225"): return "🇨🇮"
    if number.startswith("+91"): return "🇮🇳"
    if number.startswith("+84"): return "🇻🇳"
    return "🌍"

def mask_number(number):
    clean = number.replace("+", "")
    return f"{clean[:5]}*****{clean[-3:]}" if len(clean) > 8 else number

def extract_otp(text):
    match = re.search(r'\b\d{4,8}\b', text)
    return match.group(0) if match else None

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    return requests.post(url, data={"chat_id": CHANNEL_ID, "text": msg}).ok

@app.route("/push_otp")
def push_otp():
    number = request.args.get("number", "")
    service = request.args.get("service", "UNKNOWN").upper()
    sms = request.args.get("sms", "")
    otp = extract_otp(sms)
    time_str = datetime.datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

    OTP_STORE[number] = {"otp": otp, "sms": sms, "service": service, "time": time_str}

    msg = (
        "✨ New OTP Received ✨\n\n"
        f"📞 Number: {country_flag(number)} {mask_number(number)}\n"
        f"🔧 Service: {service}\n"
        f"⏰ Time: {time_str}\n\n"
        f"🔑 OTP Code: {otp}\n\n"
        f"📩 Full SMS: \n{sms}"
    )
    send_telegram(msg)
    return jsonify({"status": "sent", "otp": otp})

@app.route("/latest")
def latest():
    number = request.args.get("number", "")
    data = OTP_STORE.get(number)
    return jsonify({"found": bool(data), **data}) if data else jsonify({"found": False})

@app.route("/")
def home():
    return "OTP System Running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
