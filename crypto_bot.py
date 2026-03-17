import telebot
from telebot import types
import requests
import os
from datetime import datetime, timedelta

TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN)

# Stocare Trial (User ID: Data Start)
user_trial_start = {}

strings = {
    'en': {
        'start': "🚀 *Born Crypto Bot v2.0*\nSelect language:",
        'main': "🏠 *Main Menu*",
        'free': "📊 Free Signals & Prices",
        'premium': "💎 PREMIUM SERVICES",
        'signals': "📈 5x Daily Signals",
        'whale': "🐳 Live Whale Alerts",
        'gems': "💎 Early Tokens",
        'gainers': "🔥 Top Gainers",
        'pay': "💳 Start making smarter trades today get real-time signals and alerts",
        'back': "⬅️ Back",
        'lang': "🌐 Language / Limba",
        'trial_expired': "🚨 *Your free trial has expired!*\nUpgrade to Premium to continue receiving signals and alerts.",
        'free_signal': "🆓 *FREE SIGNAL*\n\n**Token:** BTC/USDT\n**ENTRY:** 67000\n**TARGET:** 69000\n**STOP LOSS:** 66000\n\n**Status:** ✅ Target Reached (+3.2% Profit)",
        'premium_info': "🌟 *BORN CRYPTO PREMIUM*\n• 5 Verified Signals Per Day\n• Live Whale Tracking (>1M$)\n• Top Gainers & Early Gems Listing",
    },
    'ro': {
        'start': "🚀 *Born Crypto Bot v2.0*\nSelectează limba:",
        'main': "🏠 *Meniu Principal*",
        'free': "📊 Semnale Free & Prețuri",
        'premium': "💎 SERVICII PREMIUM",
        'signals': "📈 5x Semnale / Zi",
        'whale': "🐳 Alerte Balene Live",
        'gems': "💎 Early Tokens",
        'gainers': "🔥 Top Gainers",
        'pay': "💳 Începe să tranzacționezi inteligent azi! Primește semnale și alerte real-time.",
        'back': "⬅️ Înapoi",
        'lang': "🌐 Schimbă Limba",
        'trial_expired': "🚨 *Trial-ul tău gratuit a expirat!*\nAbonează-te la Premium pentru a continua.",
        'free_signal': "🆓 *SEMNAL GRATUIT*\n\n**Token:** BTC/USDT\n**INTRARE:** 67000\n**TARGET:** 69000\n**STOP LOSS:** 66000\n\n**Status:** ✅ Target Atins (+3.2% Profit)"
    },
    'de': {
        'start': "🚀 *Born Crypto Bot v2.0*\nSprache wählen:",
        'main': "🏠 *Hauptmenü*",
        'free': "📊 Gratis Signale & Preise",
        'premium': "💎 PREMIUM DIENSTE",
        'signals': "📈 5x Signale pro Tag",
        'whale': "🐳 Whale Alerts Live",
        'gems': "💎 Early Tokens",
        'gainers': "🔥 Top-Gewinner",
        'pay': "💳 Starten Sie noch heute mit intelligenteren Trades!",
        'back': "⬅️ Zurück",
        'lang': "🌐 Sprache ändern",
        'trial_expired': "🚨 *Ihre Testversion ist abgelaufen!*\nUpgrade auf Premium erforderlich."
    },
    'fr': {
        'start': "🚀 *Born Crypto Bot v2.0*\nChoisir la langue:",
        'main': "🏠 *Menu Principal*",
        'free': "📊 Signaux Gratuits",
        'premium': "💎 SERVICES PREMIUM",
        'signals': "📈 5x Signaux/Jour",
        'whale': "🐳 Alertes Baleines",
        'gems': "💎 Early Tokens",
        'gainers': "🔥 Top Gagnants",
        'pay': "💳 Commencez à trader plus intelligemment dès aujourd'hui !",
        'back': "⬅️ Retour",
        'lang': "🌐 Changer de langue",
        'trial_expired': "🚨 *Votre essai a expiré !*\nInscrivez-vous au Premium."
    }
}

user_lang = {}

def is_trial_active(user_id):
    if user_id not in user_trial_start:
        user_trial_start[user_id] = datetime.now()
        return True
    # TEST: 1 minut. Schimbă în days=3 pentru producție.
    if datetime.now() > user_trial_start[user_id] + timedelta(minutes=1):
        return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_lang[message.chat.id] = 'en'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇷🇴 Română", "🇩🇪 Deutsch", "🇫🇷 Français")
    bot.send_message(message.chat.id, strings['en']['start'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text
    
    # 1. Logică Selectare Limbă
    if "English" in text: user_lang[uid] = 'en'
    elif "Română" in text: user_lang[uid] = 'ro'
    elif "Deutsch" in text: user_lang[uid] = 'de'
    elif "Français" in text: user_lang[uid] = 'fr'
    
    if any(l in text for l in ["English", "Română", "Deutsch", "Français"]):
        show_main(message)
        return

    # 2. Verificare Trial
    if not is_trial_active(uid):
        lang = user_lang.get(uid, 'en')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, strings[lang]['trial_expired'], reply_markup=markup, parse_mode="Markdown")
        return

    lang = user_lang.get(uid, 'en')

    # 3. Meniu Free
    if "📊" in text:
        bot.send_message(uid, strings[lang]['free_signal'], parse_mode="Markdown")
        bot.send_message(uid, "💡 _Write a coin symbol (e.g. BTC) for live price._", parse_mode="Markdown")
    
    # 4. Meniu Premium
    elif "💎" in text and any(x in text for x in ["PREMIUM", "SERVICII", "DIENSTE", "SERVICES"]):
        show_premium(message)

    # 5. Funcții Premium
    elif any(emoji in text for emoji in ["📈", "🐳", "💎", "🔥"]) and "⬅️" not in text:
        show_paywall(message, text)

    elif "⬅️" in text: show_main(message)
    elif "🌐" in text: start(message)

    # 6. Prețuri Live Binance
    elif len(text) <= 8 and not text.startswith('/'):
        get_price(message)

def show_main(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(strings[lang]['free'], strings[lang]['premium'])
    markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
    markup.row(strings[lang]['lang'])
    bot.send_message(message.chat.id, strings[lang]['main'], reply_markup=markup, parse_mode="Markdown")

def show_premium(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(strings[lang]['signals'], strings[lang]['whale'])
    markup.row(strings[lang]['gems'], strings[lang]['gainers'])
    markup.row(strings[lang]['back'])
    
    inline_pay = types.InlineKeyboardMarkup()
    inline_pay.add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
    
    bot.send_message(message.chat.id, strings[lang]['premium_info'], reply_markup=markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "🚀 *Access Premium Content:*", reply_markup=inline_pay, parse_mode="Markdown")

def show_paywall(message, btn_text):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
    
    if "📈" in btn_text: info = "🎯 *5 PREMIUM SIGNALS*\nHigh-accuracy trades with Entry, TP, and SL."
    elif "🐳" in btn_text: info = "🐋 *LIVE WHALE ALERTS*\nInstant alerts for massive on-chain movements."
    elif "🔥" in btn_text: info = "🔥 *TOP GAINERS*\nLive trending coins with highest 24h volume."
    else: info = "💎 *EARLY TOKENS*\nNew pair listings on DEXs before they hit CEXs."
    
    bot.send_message(message.chat.id, info, reply_markup=markup, parse_mode="Markdown")

def get_price(message):
    symbol = message.text.upper().strip() + "USDT"
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}").json()
        bot.send_message(message.chat.id, f"💰 *{message.text.upper()}*: `${float(r['price']):,.2f}`", parse_mode="Markdown")
    except: pass

if __name__ == "__main__":
    bot.infinity_polling()
