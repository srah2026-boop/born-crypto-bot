import telebot
import requests
from flask import Flask
from threading import Thread
import os

# 1. PARTEA PENTRU RENDER (Mini-server pentru stabilitate)
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

# 2. CONFIGURARE BOT TELEGRAM (TOKEN-UL TAU)
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
    
    welcome_text = (
        "⚡ **BORN CRYPTO TERMINAL v3**\n\n"
        "Statut: ✅ Real-Time Active\n"
        "Alege o functie din meniul de mai jos:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    if message.text == "📈 LIVE PRICES":
        try:
            # Preluare pret real Bitcoin de pe Binance
            res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
            pret_btc = float(res.json()['price'])
            
            # Preluare pret real Ethereum de pe Binance
            res_eth = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT")
            pret_eth = float(res_eth.json()['price'])
            
            raspuns = (
                "📊 **DATE PIATA LIVE**\n\n"
                f"• **Bitcoin (BTC):** `${pret_btc:,.2f}`\n"
                f"• **Ethereum (ETH):** `${pret_eth:,.2f}`\n\n"
                "✅ Date actualizate prin Binance API"
            )
            bot.reply_to(message, raspuns, parse_mode="Markdown")
        except:
            bot.reply_to(message, "⚠️ Serviciul de preturi este momentan ocupat.")

    elif message.text == "🔍 RUG-CHECK":
        bot.reply_to(message, "🛡️ **Rug-Check Audit:** Introdu adresa contractului (CA) pentru scanare.")

    elif message.text == "🌊 WHALE FLOW":
        bot.reply_to(message, "🐋 **Whale Tracker:** Activitate detectata pe rutele CEX -> Cold Wallet.")

    elif message.text == "💎 PREMIUM":
        bot.reply_to(message, "🌟 **Acces Premium:** Contacteaza @Admin pentru VIP.")

# 3. PORNIRE CORECTA (REPARAT)
if __name__ == "__main__":
    keep_alive()
    print("Botul a fost lansat cu succes!")
    bot.polling(none_stop=True)
