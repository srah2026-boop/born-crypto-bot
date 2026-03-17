import telebot
import requests
from flask import Flask
from threading import Thread
import os

1. PARTEA PENTRU RENDER
app = Flask('')

@app.route('/')
def home():
return "Botul Born Crypto este online!"

def run():
port = int(os.environ.get("PORT", 8080))
app.run(host='0.0.0.0', port=port)

def keep_alive():
t = Thread(target=run)
t.start()

2. CONFIGURARE BOT TELEGRAM
TOKEN = "7829595779:AAH7-vH_XjJmH9XG_mE_Z9_m_m_m_m"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
item1 = telebot.types.KeyboardButton("📈 LIVE PRICES")
item2 = telebot.types.KeyboardButton("🔍 RUG-CHECK")
item3 = telebot.types.KeyboardButton("🌊 WHALE FLOW")
item4 = telebot.types.KeyboardButton("💎 PREMIUM")
markup.add(item1, item2, item3, item4)

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
if message.text == "📈 LIVE PRICES":
try:
res = requests.get("")
pret_btc = float(res.json()['price'])
bot.reply_to(message, f"📊 Bitcoin (BTC): ${pret_btc:,.2f}\n✅ Binance API")
except:
bot.reply_to(message, "⚠️ Serviciu ocupat.")
elif message.text == "🔍 RUG-CHECK":
bot.reply_to(message, "🛡️ Trimite adresa contractului.")
elif message.text == "🌊 WHALE FLOW":
bot.reply_to(message, "🐋 Activitate detectata pe Binance.")
elif message.text == "💎 PREMIUM":
bot.reply_to(message, "🌟 Contact @Admin pentru VIP.")

if name == "main":
keep_alive()
bot.polling(none_stop=True)
