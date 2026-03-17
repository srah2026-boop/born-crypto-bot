import telebot
from telebot import types
import requests
import os
import json
import time
import threading
from datetime import datetime, timedelta

# Configurare Initiala
TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN, threaded=False)

TRIALS_FILE = "trials_data.json"

def load_trials():
    if os.path.exists(TRIALS_FILE):
        try:
            with open(TRIALS_FILE, "r") as f:
                data = json.load(f)
                return {int(k): datetime.fromisoformat(v) for k, v in data.items()}
        except: return {}
    return {}

def save_trials(trials):
    try:
        with open(TRIALS_FILE, "w") as f:
            data = {str(k): v.isoformat() for k, v in trials.items()}
            json.dump(data, f)
    except: pass

user_trial_start = load_trials()
user_lang = {}

# --- FUNCTIE PENTRU MESAJE AUTOMATE (FOLLOW-UP) ---
def send_marketing_followup(chat_id, lang):
    time.sleep(120) # Asteapta 120 de secunde (2 minute)
    text = {
        'en': "🚀 Want better crypto signals?\n\n*Upgrade to Premium:*\n✅ Real-time alerts\n✅ Whale tracking\n✅ Early gems\n\n💰 Only 10€/month",
        'ro': "🚀 Vrei semnale crypto mai bune?\n\n*Treci la Premium:*\n✅ Alerte în timp real\n✅ Urmărire Balene\n✅ Early gems\n\n💰 Doar 10€/lună",
        'de': "🚀 Wollen Sie bessere Krypto-Signale?\n\n*Upgrade auf Premium:*",
        'fr': "🚀 Vous voulez de meilleurs signaux crypto?\n\n*Passer la Premium:*"
    }
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="💎 Upgrade Now", url=STRIPE_PAYMENT_LINK))
    try:
        bot.send_message(chat_id, text.get(lang, text['en']), reply_markup=markup, parse_mode="Markdown")
    except: pass

# --- FUNCTIE PENTRU TOP MONEDE (Binance Live) ---
def get_top_signals():
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    results = []
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        prices = requests.get(url, timeout=5).json()
        price_dict = {item['symbol']: float(item['price']) for item in prices if item['symbol'] in symbols}
        for sym in symbols:
            if sym in price_dict:
                price = price_dict[sym]; entry = price; target = price * 1.025
                results.append(f"🔸 **{sym.replace('USDT', '')}**\nEntry: `{entry:.2f}`\nTarget: `{target:.2f}`\n")
        return "\n".join(results)
    except: return "❌ Market data unavailable."

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    if uid not in user_trial_start:
        user_trial_start[uid] = datetime.now()
        save_trials(user_trial_start)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇷🇴 Română", "🇩🇪 Deutsch", "🇫🇷 Français")
    bot.send_message(uid, "🚀 *Born Crypto Bot v2.0*\nSelect language:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text

    if "English" in text: user_lang[uid] = 'en'; show_main(message); return
    if "Română" in text: user_lang[uid] = 'ro'; show_main(message); return
    if "Deutsch" in text: user_lang[uid] = 'de'; show_main(message); return
    if "Français" in text: user_lang[uid] = 'fr'; show_main(message); return

    lang = user_lang.get(uid, 'en')

    # Porneste thread-ul de follow-up (o singura data pe sesiune de interactiune)
    if text in ["📊 Semnale Free", "📊 Free Signals"]:
        threading.Thread(target=send_marketing_followup, args=(uid, lang)).start()

    # Logica de Trial & Navigare (Păstrată din versiunea anterioară)
    if "📊" in text: 
        bot.send_message(uid, "⌛ _Fetching market data..._", parse_mode="Markdown")
        signals = get_top_signals()
        header = "🆓 *LIVE TOP SIGNALS*\n\n" if lang == 'en' else "🆓 *SEMNALE LIVE TOP*\n\n"
        bot.send_message(uid, header + signals, parse_mode="Markdown")
    elif "🛡️" in text or "🔍" in text:
        bot.send_message(uid, "🛰️ " + ("Paste address:" if lang == 'en' else "Trimite adresa:"))
    elif "💎" in text: show_premium(message)
    elif "⬅️" in text: show_main(message)
    elif "🌐" in text: start(message)
    elif any(x in text for x in ["📈", "🐳", "🔥", "💎 Early"]):
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Pay", url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, "🔒 Premium feature!", reply_markup=markup)

def show_main(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Free Signals", "💎 PREMIUM")
    markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
    markup.row("🌐 Language")
    bot.send_message(message.chat.id, "🏠 *Main Menu*", reply_markup=markup, parse_mode="Markdown")

def show_premium(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📈 5x Signals", "🐳 Whale Alerts")
    markup.row("💎 Early Gems", "🔥 Gainers")
    markup.row("⬅️ Back")
    pay_btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="💳 Buy Now 10€", url=STRIPE_PAYMENT_LINK))
    bot.send_message(message.chat.id, "💎 *PREMIUM SERVICES*", reply_markup=markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "Get full access here:", reply_markup=pay_btn)

if __name__ == "__main__":
    try: bot.remove_webhook()
    except: pass
    while True:
        try: bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception: time.sleep(5)
