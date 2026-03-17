import telebot
from telebot import types
import requests
import os

TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN)

# Dicționar complet cu TOATE funcțiile (EN, RO, DE, FR)
strings = {
    'en': {
        'start': "🚀 *Born Crypto Bot v2.0*\nProfessional crypto assistant. Select language:",
        'main': "🏠 *Main Menu*",
        'free': "📊 Live Prices",
        'defi': "🛡️ DeFi Analysis",
        'audit': "🔍 Contract Audit",
        'premium': "💎 PREMIUM SERVICES",
        'signals': "📈 Daily Signals",
        'whale': "🐳 Whale Tracker",
        'gems': "💎 Early Gems",
        'pay': "💳 Subscribe Now (Stripe)",
        'back': "⬅️ Back",
        'lang': "🌐 Language / Limba",
        'defi_info': "🛡️ *DeFi Analysis*\nChecking liquidity pools, TVL, and slippage on DEXs.",
        'audit_info': "🔍 *Contract Audit*\nScanning for honeypots, mint functions, and liquidity locks.",
        'promo_sig': "🎯 *Daily Signals (PREMIUM)*\nGet Top 3 coins every morning with Entry/Exit points.",
        'promo_wha': "🐋 *Whale Tracker (PREMIUM)*\nReal-time 1M$+ alerts. Upgrade to see details.",
        'promo_gem': "💎 *Early Gems (PREMIUM)*\n100x potential tokens on Uniswap before they moon."
    },
    'ro': {
        'start': "🚀 *Born Crypto Bot v2.0*\nAsistent profesional. Selectează limba:",
        'main': "🏠 *Meniu Principal*",
        'free': "📊 Prețuri Live",
        'defi': "🛡️ Analiză DeFi",
        'audit': "🔍 Audit Contracte",
        'premium': "💎 SERVICII PREMIUM",
        'signals': "📈 Semnale Zilnice",
        'whale': "🐳 Whale Tracker",
        'gems': "💎 Early Gems",
        'pay': "💳 Abonează-te (Stripe)",
        'back': "⬅️ Înapoi",
        'lang': "🌐 Schimbă Limba",
        'defi_info': "🛡️ *Analiză DeFi*\nVerificare lichiditate și TVL pe Uniswap/Pancake.",
        'audit_info': "🔍 *Audit Contract*\nScanare pentru honeypot și funcții de mint periculoase.",
        'promo_sig': "🎯 *Semnale Zilnice (PREMIUM)*\nTop 3 monede cu puncte de intrare/ieșire.",
        'promo_wha': "🐋 *Whale Tracker (PREMIUM)*\nMișcări de 1M$+ detectate. Treci la Premium.",
        'promo_gem': "💎 *Early Gems (PREMIUM)*\nMonede 100x înainte de listare."
    }
}

user_lang = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_lang[message.chat.id] = 'en' # Start default în Engleză
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇷🇴 Română", "🇩🇪 Deutsch", "🇫🇷 Français")
    bot.send_message(message.chat.id, strings['en']['start'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["🇬🇧 English", "🇷🇴 Română", "🇩🇪 Deutsch", "🇫🇷 Français", "🌐 Language / Limba", "🌐 Schimbă Limba"])
def set_lang(message):
    if "Română" in message.text: user_lang[message.chat.id] = 'ro'
    else: user_lang[message.chat.id] = 'en'
    show_main_menu(message)

def show_main_menu(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Rândul 1: Prețuri și Premium
    markup.row(strings[lang]['free'], strings[lang]['premium'])
    # Rândul 2: DeFi și Audit
    markup.row(strings[lang]['defi'], strings[lang]['audit'])
    # Rândul 3: Limba
    markup.row(strings[lang]['lang'])
    bot.send_message(message.chat.id, strings[lang]['main'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: "PREMIUM" in m.text or "SERVICII" in m.text)
def premium_menu(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(strings[lang]['signals'], strings[lang]['whale'])
    markup.row(strings[lang]['gems'], strings[lang]['back'])
    bot.send_message(message.chat.id, "💎 *Premium Services*", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: "🛡️" in m.text or "Analiză DeFi" in m.text or "DeFi Analysis" in m.text)
def defi_func(message):
    lang = user_lang.get(message.chat.id, 'en')
    bot.send_message(message.chat.id, strings[lang]['defi_info'], parse_mode="Markdown")

@bot.message_handler(func=lambda m: "🔍" in m.text or "Audit" in m.text)
def audit_func(message):
    lang = user_lang.get(message.chat.id, 'en')
    bot.send_message(message.chat.id, strings[lang]['audit_info'], parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(emoji in m.text for emoji in ["📈", "🐳", "💎"]) and "PREMIUM" not in m.text)
def paywall(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
    
    if "📈" in message.text: text = strings[lang]['promo_sig']
    elif "🐳" in message.text: text = strings[lang]['promo_wha']
    else: text = strings[lang]['promo_gem']
    
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: "📊" in m.text or "Back" in m.text or "Înapoi" in m.text)
def back_home(message):
    show_main_menu(message)

@bot.message_handler(func=lambda m: len(m.text) <= 8 and not m.text.startswith('/'))
def get_price(message):
    lang = user_lang.get(message.chat.id, 'en')
    symbol = message.text.upper().strip() + "USDT"
    try:
        res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}").json()
        price = f"{float(res['price']):,.2f}"
        bot.send_message(message.chat.id, f"🚀 *{message.text.upper()}*: `${price}`", parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "❌ Coin not found.")

if __name__ == "__main__":
    bot.infinity_polling()
