import telebot
import requests
import os

# Luăm token-ul direct din setările Koyeb (Environment Variables)
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

def get_crypto_price(coin):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    try:
        response = requests.get(url).json()
        if coin in response:
            return response[coin]['usd']
        return None
    except Exception as e:
        print(f"Eroare la API: {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salut! Sunt botul tău crypto. Trimite-mi numele unei monede (ex: bitcoin, ethereum) și îți zic prețul.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    coin = message.text.lower().strip()
    price = get_crypto_price(coin)
    if price:
        bot.reply_to(message, f"Prețul pentru {coin.capitalize()} este: ${price}")
    else:
        bot.reply_to(message, "Nu am găsit moneda asta. Încearcă 'bitcoin' sau 'ethereum'.")

if __name__ == "__main__":
    print("Botul a pornit...")
    bot.infinity_polling()
