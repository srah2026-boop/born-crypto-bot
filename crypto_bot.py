import telebot
import requests
import os

# Luăm token-ul din Environment Variables din Koyeb
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salut! Sunt botul tău crypto. Trimite-mi numele unei monede (ex: bitcoin) și îți zic prețul.")

@bot.message_handler(func=lambda message: True)
def get_price(message):
    coin = message.text.lower().strip()
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    try:
        response = requests.get(url).json()
        if coin in response:
            price = response[coin]['usd']
            bot.reply_to(message, f"Prețul pentru {coin.capitalize()} este: ${price}")
        else:
            bot.reply_to(message, "Nu am găsit moneda. Încearcă 'bitcoin'.")
    except:
        bot.reply_to(message, "Eroare la API. Revino mai târziu.")

if __name__ == "__main__":
    print("Botul a pornit...")
    bot.infinity_polling()
