import telebot
from telebot import types
import requests
import os

# Configurare Token din Koyeb
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# Dicționar extins pentru 4 limbi
strings = {
    'en': {
        'welcome': "Welcome! This is your Crypto Bot. Select language:",
        'main_menu': "Main Menu:",
        'free': "📊 Free Version (Live Prices)",
        'premium': "💎 Premium (Signals & Alerts)",
        'select_coin': "Enter coin symbol (e.g. BTC, ETH, SOL):",
        'price_msg': "🚀 *{0}* Live Price: `${1}`\nSource: Binance Live",
        'not_found': "Invalid symbol. Please use symbols like BTC or ETH.",
        'change_lang': "🌐 Change Language",
        'back': "⬅️ Back"
    },
    'de': {
        'welcome': "Willkommen! Wählen Sie Ihre Sprache:",
        'main_menu': "Hauptmenü:",
        'free': "📊 Free Version (Live-Preise)",
        'premium': "💎 Premium (Signale)",
        'select_coin': "Geben Sie das Symbol ein (z. B. BTC):",
        'price_msg': "🚀 *{0}* Live-Preis: `${1}`\nQuelle: Binance Live",
        'not_found': "Ungültiges Symbol. Bitte verwenden Sie BTC oder ETH.",
        'change_lang': "🌐 Sprache ändern",
        'back': "⬅️ Zurück"
    },
    'ro': {
        'welcome': "Bine ai venit! Selectează limba:",
        'main_menu': "Meniu Principal:",
        'free': "📊 Versiune Free (Prețuri Live)",
        'premium': "💎 Premium (Semnale)",
        'select_coin': "Introdu simbolul monedei (ex: BTC, ETH):",
        'price_msg': "🚀 Preț Live *{0}*: `${1}`\nSursă: Binance Live",
        'not_found': "Simbol invalid. Folosește BTC sau ETH.",
        'change_lang': "🌐 Schimbă Limba",
        'back': "⬅️ Înapoi"
    },
    'fr': {
        'welcome': "Bienvenue! Sélectionnez votre langue:",
        'main_menu': "Menu Principal:",
        'free': "📊 Version Free (Prix en Direct)",
        'premium': "💎 Premium (Signaux)",
        'select_coin': "Entrez le symbole (ex: BTC):",
        'price_msg': "🚀 Prix en direct *{0}*: `${1}`\nSource: Binance",
        'not_found': "Symbole invalide. Utilisez BTC sau ETH.",
        'change_lang': "🌐 Changer de langue",
        'back': "⬅️ Retour"
    }
}

user_lang = {}

# Funcție Live Binance
def get_binance_price(symbol):
    symbol = symbol.upper() + "USDT"
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        response = requests.get(url).json()
        price = float(response['price'])
        return f"{price:,.2f}" if price > 1 else f"{price:,.6f}"
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    # Setăm limba default pe Engleză la prima pornire
    user_lang[message.chat.id] = 'en'
    show_language_menu(message)

def show_language_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇩🇪 Deutsch", "🇷🇴 Română", "🇫🇷 Français")
    bot.send_message(message.chat.id, "Select Language / Sprache wählen / Selectează limba:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["🇬🇧 English", "🇩🇪 Deutsch", "🇷🇴 Română", "🇫🇷 Français", "🌐 Change Language", "🌐 Sprache ändern", "🌐 Schimbă Limba", "🌐 Changer de langue"])
def set_language(message):
    if "English" in message.text: user_lang[message.chat.id] = 'en'
    elif "Deutsch" in message.text: user_lang[message.chat.id] = 'de'
    elif "Română" in message.text: user_lang[message.chat.id] = 'ro'
    elif "Français" in message.text: user_lang[message.chat.id] = 'fr'
    
    if "Change" in message.text or "Language" in message.text or "Sprache" in message.text or "Limba" in message.text:
        show_language_menu(message)
    else:
        show_main_menu(message)

def show_main_menu(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(strings[lang]['free'], strings[lang]['premium'])
    markup.add(strings[lang]['change_lang'])
    bot.send_message(message.chat.id, strings[lang]['main_menu'], reply_markup=markup)

@bot.message_handler(func=lambda m: any(x in m.text for x in ["Free", "Versiune", "Version"]))
def free_mode(message):
    lang = user_lang.get(message.chat.id, 'en')
    bot.send_message(message.chat.id, strings[lang]['select_coin'])

@bot.message_handler(func=lambda m: any(x in m.text for x in ["Premium", "💎"]))
def premium_mode(message):
    lang = user_lang.get(message.chat.id, 'en')
    msg = "💎 Premium is currently invitation only." if lang == 'en' else "💎 Versiunea Premium este doar pe bază de invitație."
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: len(m.text) <= 10)
def handle_crypto(message):
    lang = user_lang.get(message.chat.id, 'en')
    symbol = message.text.upper().strip()
    price = get_binance_price(symbol)
    
    if price:
        bot.send_message(message.chat.id, strings[lang]['price_msg'].format(symbol, price), parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, strings[lang]['not_found'])

if __name__ == "__main__":
    print("Botul Binance Live a pornit pe Koyeb...")
    bot.infinity_polling()
