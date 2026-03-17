import telebot
from telebot import types
import requests
import os

TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN)

strings = {
    'en': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\nProfessional market analysis. Select language:",
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
        'not_found': "Invalid symbol. Use BTC or ETH.",
        'promo_signals': "🎯 *Daily Signals (PREMIUM)*\nTop 3 coins every morning with Entry/Exit points.",
        'promo_whale': "🐋 *Whale Tracker (PREMIUM)*\nReal-time 1M$+ movement alerts. Upgrade to see details.",
        'promo_gems': "💎 *Early Gems (PREMIUM)*\n100x potential tokens on Uniswap before they moon.",
        'change_lang': "🌐 Language / Limba"
    },
    'ro': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\nSelectează limba pentru a continua:",
        'main_menu': "🏠 *Meniu Principal*",
        'free': "📊 Prețuri Live",
        'defi': "🛡️ Analiză DeFi",
        'audit': "🔍 Audit Contracte",
        'premium': "💎 SERVICII PREMIUM",
        'signals': "📈 Semnale Zilnice",
        'whale': "🐳 Whale Tracker",
        'gems': "💎 Early Gems",
        'pay_button': "💳 Abonează-te (Stripe)",
        'back': "⬅️ Înapoi",
        'not_found': "Simbol invalid.",
        'promo_signals': "🎯 *Semnale Zilnice*\nTop 3 monede cu puncte de intrare.",
        'promo_whale': "🐋 *Whale Tracker*\nMișcări de 1M$+ detectate. Treci la Premium.",
        'promo_gems': "💎 *Early Gems*\nMonede 100x înainte de listare.",
        'change_lang': "🌐 Schimbă Limba"
    }
}

user_lang = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_lang[message.chat.id] = 'en'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇷🇴 Română", "🇩🇪 Deutsch", "🇫🇷 Français")
    bot.send_message(message.chat.id, strings['en']['start_msg'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["🇬🇧 English", "🇷🇴 Română", "🇩🇪 Deutsch", "🇫🇷 Français", "🌐 Language / Limba", "🌐 Change Language"])
def set_lang(message):
    if "English" in message.text: user_lang[message.chat.id] = 'en'
    elif "Română" in message.text: user_lang[message.chat.id] = 'ro'
    # Restul de limbi folosesc fallback pe EN pentru simplitate în acest demo
    show_main_menu(message)

def show_main_menu(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(strings[lang]['free'], strings[lang]['premium'])
    markup.row(strings[lang]['defi'], strings[lang]['audit'])
    markup.row(strings[lang]['change_lang'])
    bot.send_message(message.chat.id, strings[lang]['main_menu'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: "PREMIUM" in m.text or "SERVICII" in m.text)
def premium_dashboard(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(strings[lang]['signals'], strings[lang]['whale'])
    markup.row(strings[lang]['gems'])
    markup.row(strings[lang]['back'])
    bot.send_message(message.chat.id, "💎 *Premium Dashboard*", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(emoji in m.text for emoji in ["📈", "🐳", "💎"]) and "PREMIUM" not in m.text)
def handle_premium_clicks(message):
    lang = user_lang.get(message.chat.id, 'en')
    # Creăm butonul de plată Stripe
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=strings[lang]['pay_button'], url=STRIPE_PAYMENT_LINK))
    
    if "📈" in message.text: text = strings[lang].get('promo_signals', strings['en']['promo_signals'])
    elif "🐳" in message.text: text = strings[lang].get('promo_whale', strings['en']['promo_whale'])
    else: text = strings[lang].get('promo_gems', strings['en']['promo_gems'])
    
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: "📊" in m.text or "Back" in m.text or "Înapoi" in m.text or "Zurück" in m.text or "Retour" in m.text)
def go_back(message):
    show_main_menu(message)

@bot.message_handler(func=lambda m: len(m.text) <= 8 and not m.text.startswith('/'))
def price_check(message):
    lang = user_lang.get(message.chat.id, 'en')
    symbol = message.text.upper().strip() + "USDT"
    try:
        res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}").json()
        bot.send_message(message.chat.id, f"🚀 *{message.text.upper()}*: `${float(res['price']):,.2f}`", parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, strings[lang]['not_found'])

if __name__ == "__main__":
    bot.infinity_polling()
