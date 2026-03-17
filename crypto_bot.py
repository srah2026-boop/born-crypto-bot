import telebot
import requests

# TOKEN-UL TAU
TOKEN = "7829595779:AAH7-vH_XjJmH9XG_mE_Z9_m_m_m_m" 
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = telebot.types.KeyboardButton("📈 LIVE PRICES")
    item2 = telebot.types.KeyboardButton("🔍 RUG-CHECK")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "🚀 BORN CRYPTO LIVE PE KOYEB!\n\nAlege o functie:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    if message.text == "📈 LIVE PRICES":
        try:
            res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
            pret = float(res.json()['price'])
            bot.reply_to(message, f"📊 Bitcoin (BTC): ${pret:,.2f}")
        except:
            bot.reply_to(message, "⚠️ Eroare API Binance.")

if __name__ == "__main__":
    print("Botul a pornit pe Koyeb...")
    bot.polling(none_stop=True)
