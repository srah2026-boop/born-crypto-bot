import telebot
from telebot import types
import requests
import os

TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN)

# Dicționar cu Engleza ca primă limbă (Default)
strings = {
    'en': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\n\nYour professional assistant for the crypto market. Select your language to continue:",
        'main_menu': "🏠 *Main Menu*\nChoose a service:",
        'free': "📊 Live Prices",
        'defi': "🛡️ DeFi Analysis",
        'audit': "🔍 Contract Audit",
        'premium': "💎 PREMIUM SERVICES",
        'signals': "📈 Daily Signals",
        'whale': "🐳 Whale Tracker",
        'gems': "💎 Early Gems",
        'pay_button': "💳 Subscribe Now (Stripe)",
        'back': "⬅️ Back",
        'not_found': "Invalid symbol. Please use BTC, ETH, etc.",
        'promo_signals': "🎯 *Daily Signals (PREMIUM)*\nGet the Top 3 coins to watch every morning with precise Entry & Exit points. Don't miss the next pump!",
        'promo_whale': "🐋 *Whale Tracker (PREMIUM)*\nWe detected big movements (1M$+). To see the destination wallet and exchange alerts, upgrade now.",
        'promo_gems': "💎 *Early Gems (PREMIUM)*\nFind 100x potential tokens on Uniswap before they hit major exchanges. Be early!",
        'change_lang': "🌐 Change Language"
    },
    'ro': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\nSelectează limba pentru a continua:",
        'main_menu': "🏠 *Meniu Principal*\nAlege un serviciu:",
        'free': "📊 Prețuri Live",
        'defi': "🛡️ Analiză DeFi",
        'audit': "🔍 Audit Contracte",
        'premium': "💎 SERVICII PREMIUM",
        'signals': "📈 Semnale Zilnice",
        'whale': "🐳 Whale Tracker",
        'gems': "💎 Early Gems",
        'pay_button': "💳 Abonează-te acum (Stripe)",
        'back': "⬅️ Înapoi",
        'not_found': "Simbol invalid.",
        'promo_signals': "🎯 *Semnale Zilnice (PREMIUM)*\nPrimești Top 3 monede de urmărit în fiecare dimineață.",
        'promo_whale': "🐋 *Whale Tracker (PREMIUM)*\nAm detectat mișcări mari (1M$+). Treci la Premium pentru detalii.",
        'promo_gems': "💎 *Early Gems (PREMIUM)*\nGăsește monede cu potențial de 100x pe Uniswap.",
        'change_lang': "🌐 Schimbă Limba"
    },
    'de': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\nWählen Sie eine Sprache:",
        'main_menu': "🏠 *Hauptmenü*",
        'free': "📊 Live-Preise",
        'premium': "💎 PREMIUM-DIENSTE",
        'signals': "📈 Tägliche Signale",
        'whale': "🐳 Whale Tracker",
        'gems': "💎 Early Gems",
        'pay_button': "💳 Jetzt abonnieren",
        'change_lang': "🌐 Sprache ändern",
        'back': "⬅️ Zurück"
    },
    'fr': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\nChoisissez votre langue:",
        'main_menu': "🏠 *Menu Principal*",
        'free': "📊 Prix en Direct",
        'premium': "💎 SERVICES PREMIUM",
        'signals': "📈 Signaux Quotidiens",
        'whale': "🐳 Whale Tracker",
        'gems': "💎 Early Gems",
        'pay_button': "💳 S'abonner",
        'change_lang': "🌐 Changer de langue",
        'back': "⬅️ Retour"
    }
}

# Default language setting
user_lang = {}

@bot.message_handler(commands=['start'])
def start(message):
    # Resetăm pe Engleză la start
    user_lang[message.chat.id] = 'en'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇩🇪 Deutsch", "🇷🇴 Română", "🇫🇷 Français")
    bot.send_message(message.chat.id, strings['en']['start_msg'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["🇬🇧 English", "🇩🇪 Deutsch", "🇷🇴 Română", "🇫🇷 Français", "🌐 Change Language", "🌐 Schimbă Limba", "🌐 Sprache ändern", "🌐 Changer de langue"])
def set_lang(message):
    if "English" in message.text: user_lang[message.chat.id] = 'en'
    elif "Deutsch" in message.text: user_lang[message.chat.id] = 'de'
    elif "Română" in message.text: user_lang[message.chat.id] = 'ro'
    elif "Français" in message.text: user_lang[message.chat.id] = 'fr'
    show_main_menu(message)

def show_main_menu(message):
    lang = user_lang.get(message.chat.id, 'en') # Fallback pe EN
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(strings[lang]['free'], strings[lang]['premium'])
    markup.add(strings[lang]['defi'], strings[lang]['audit'])
    markup.add(strings[lang]['change_lang'])
    bot.send_message(message.chat.id, strings[lang]['main_menu'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(x in m.text for x in ["PREMIUM", "SERVICES", "SERVICII", "DIENSTE"]))
def premium_menu(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(strings[lang]['signals'], strings[lang]['whale'])
    markup.add(strings[lang]['gems'], strings[lang]['back'])
    bot.send_message(message.chat.id, "💎 *Premium Dashboard*", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(emoji in m.text for emoji in ["📈", "🐳", "💎"]) and "PREMIUM" not in m.text)
def paywall(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=strings[lang]['pay_button'], url=STRIPE_PAYMENT_LINK))
    
    # Logică Paywall - Mesaje de convingere
    if "📈" in message.text: text = strings[lang].get('promo_signals', strings['en']['promo_signals'])
    elif "🐳" in message.text: text = strings[lang].get('promo_whale', strings['en']['promo_whale'])
    else: text = strings[lang].get('promo_gems', strings['en']['promo_gems'])
    
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: "📊" in m.text or "⬅️" in m.text)
def back_home(message):
    show_main_menu(message)

@bot.message_handler(func=lambda m: len(m.text) <= 8 and not m.text.startswith('/'))
def prices(message):
    lang = user_lang.get(message.chat.id, 'en')
    symbol = message.text.upper().strip() + "USDT"
    try:
        res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}").json()
        bot.send_message(message.chat.id, f"🚀 *{message.text.upper()}*: `${float(res['price']):,.2f}`", parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, strings[lang]['not_found'])

if __name__ == "__main__":
    bot.infinity_polling()
