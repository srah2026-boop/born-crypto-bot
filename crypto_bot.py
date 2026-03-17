import telebot
from telebot import types
import requests
import os

# Configurare Token din Koyeb
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# Link-ul tău Stripe actualizat
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"

# Dicționar complet pentru toate funcțiile și limbile
strings = {
    'en': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\n\nYour professional assistant for the crypto market. I provide real-time data, audit tools, and DeFi analysis.\n\nSelect your language:",
        'main_menu': "🏠 *Main Menu*\nChoose a service:",
        'free': "📊 Live Prices",
        'defi': "🛡️ DeFi Analysis",
        'audit': "🔍 Contract Audit",
        'premium': "💎 Upgrade to Premium",
        'premium_info': "💎 *Premium Benefits:*\n• Daily Crypto Signals\n• Early Gem Alerts\n• 24/7 Whale Tracker\n\nClick below to subscribe via Stripe:",
        'pay_button': "💳 Pay with Stripe",
        'defi_info': "🛡️ *DeFi Analysis*\nCheck liquidity pools, TVL, and slippage on DEXs like Uniswap/Pancake.",
        'audit_info': "🔍 *Smart Contract Audit*\nScans for 'honeypots', 'mint' functions, and liquidity locks.",
        'select_coin': "Enter coin symbol (e.g. BTC, ETH):",
        'price_msg': "🚀 *{0}* Live Price: `${1}`",
        'change_lang': "🌐 Language / Limba",
        'not_found': "Invalid symbol. Try BTC."
    },
    'ro': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\n\nAsistentul tău profesional pentru piața crypto. Ofer date live, unelte de audit și analiză DeFi.\n\nSelectează limba:",
        'main_menu': "🏠 *Meniu Principal*\nAlege un serviciu:",
        'free': "📊 Prețuri Live",
        'defi': "🛡️ Analiză DeFi",
        'audit': "🔍 Audit Contracte",
        'premium': "💎 Treci la Premium",
        'premium_info': "💎 *Beneficii Premium:*\n• Semnale Crypto Zilnice\n• Alerte Gem-uri timpurii\n• Whale Tracker 24/7\n\nApasă mai jos pentru abonare via Stripe:",
        'pay_button': "💳 Plătește cu Stripe",
        'defi_info': "🛡️ *Analiză DeFi*\nVerifică bazinele de lichiditate și TVL pe DEX-uri.",
        'audit_info': "🔍 *Audit Smart Contract*\nScanează după 'honeypot' sau funcții de 'mint' periculoase.",
        'select_coin': "Introdu simbolul (ex: BTC, ETH):",
        'price_msg': "🚀 Preț Live *{0}*: `${1}`",
        'change_lang': "🌐 Language / Limba",
        'not_found': "Simbol invalid."
    },
    'de': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\nWählen Sie eine Sprache:",
        'main_menu': "🏠 *Hauptmenü*",
        'free': "📊 Live-Preise",
        'defi': "🛡️ DeFi-Analyse",
        'audit': "🔍 Kontrakt-Audit",
        'premium': "💎 Premium-Signale",
        'premium_info': "💎 *Premium-Vorteile:* Täglich Signale & Alarme.\nJetzt mit Stripe bezahlen:",
        'pay_button': "💳 Mit Stripe bezahlen",
        'select_coin': "Symbol eingeben (z.B. BTC):",
        'price_msg': "🚀 *{0}* Preis: `${1}`",
        'change_lang': "🌐 Sprache ändern",
        'not_found': "Ungültiges Symbol."
    },
    'fr': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\nChoisissez votre langue:",
        'main_menu': "🏠 *Menu Principal*",
        'free': "📊 Prix en Direct",
        'defi': "🛡️ Analyse DeFi",
        'audit': "🔍 Audit de Contrat",
        'premium': "💎 Signaux Premium",
        'premium_info': "💎 *Avantages Premium:* Signaux et alertes.\nPayez avec Stripe:",
        'pay_button': "💳 Payer avec Stripe",
        'select_coin': "Entrez le symbole (ex: BTC):",
        'price_msg': "🚀 Prix *{0}*: `${1}`",
        'change_lang': "🌐 Changer de langue",
        'not_found': "Symbole invalide."
    }
}

user_lang = {}

def get_binance_price(symbol):
    symbol = symbol.upper() + "USDT"
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        res = requests.get(url).json()
        price = float(res['price'])
        return f"{price:,.2f}" if price > 1 else f"{price:,.6f}"
    except: return None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇩🇪 Deutsch", "🇷🇴 Română", "🇫🇷 Français")
    bot.send_message(message.chat.id, strings['en']['start_msg'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["🇬🇧 English", "🇩🇪 Deutsch", "🇷🇴 Română", "🇫🇷 Français", "🌐 Language / Limba", "🌐 Sprache ändern", "🌐 Changer de langue"])
def set_lang(message):
    if "English" in message.text: user_lang[message.chat.id] = 'en'
    elif "Deutsch" in message.text: user_lang[message.chat.id] = 'de'
    elif "Română" in message.text: user_lang[message.chat.id] = 'ro'
    elif "Français" in message.text: user_lang[message.chat.id] = 'fr'
    show_main_menu(message)

def show_main_menu(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(strings[lang]['free'], strings[lang]['defi'])
    markup.add(strings[lang]['audit'], strings[lang]['premium'])
    markup.add(strings[lang]['change_lang'])
    bot.send_message(message.chat.id, strings[lang]['main_menu'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: "📊" in m.text)
def free_mode(message):
    lang = user_lang.get(message.chat.id, 'en')
    bot.send_message(message.chat.id, strings[lang]['select_coin'])

@bot.message_handler(func=lambda m: "🛡️" in m.text)
def defi_mode(message):
    lang = user_lang.get(message.chat.id, 'en')
    bot.send_message(message.chat.id, strings[lang]['defi_info'], parse_mode="Markdown")

@bot.message_handler(func=lambda m: "🔍" in m.text)
def audit_mode(message):
    lang = user_lang.get(message.chat.id, 'en')
    bot.send_message(message.chat.id, strings[lang]['audit_info'], parse_mode="Markdown")

@bot.message_handler(func=lambda m: "💎" in m.text)
def premium_section(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=strings[lang]['pay_button'], url=STRIPE_PAYMENT_LINK))
    bot.send_message(message.chat.id, strings[lang]['premium_info'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: len(m.text) <= 8 and not m.text.startswith('/'))
def price_handler(message):
    lang = user_lang.get(message.chat.id, 'en')
    price = get_binance_price(message.text)
    if price:
        bot.send_message(message.chat.id, strings[lang]['price_msg'].format(message.text.upper(), price), parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, strings[lang]['not_found'])

if __name__ == "__main__":
    bot.infinity_polling()
