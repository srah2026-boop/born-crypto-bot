import telebot
from telebot import types
import requests
import os

TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN)

strings = {
    'en': {
        'start': "🚀 *Born Crypto Bot v2.0*\nSelect language:",
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
        'premium_intro': "🌟 *BORN CRYPTO PREMIUM*\n\nAccess our exclusive tools:\n• Professional Trading Signals\n• Real-time Whale Alerts\n• Early DEX Gems\n\n👇 *Click below to get instant access:*",
        'promo_sig': "🎯 *Premium Signals*\nTop 3 coins daily with Entry/Exit points.",
        'promo_wha': "🐋 *Whale Tracker*\nReal-time alerts for $1M+ moves.",
        'promo_gem': "💎 *Early Gems*\n100x potential tokens on Uniswap."
    },
    'ro': {
        'start': "🚀 *Born Crypto Bot v2.0*\nSelectează limba:",
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
        'premium_intro': "🌟 *BORN CRYPTO PREMIUM*\n\nAccesează uneltele noastre exclusive:\n• Semnale profesionale de trading\n• Alerte de balene în timp real\n• Gem-uri timpurii pe DEX-uri\n\n👇 *Apasă mai jos pentru acces instant:*",
        'promo_sig': "🎯 *Semnale PREMIUM*\nTop 3 monede cu puncte de intrare.",
        'promo_wha': "🐋 *Whale Tracker*\nMișcări de peste 1M$.",
        'promo_gem': "💎 *Early Gems*\nMonede cu potențial de 100x."
    }
}

user_lang = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_lang[message.chat.id] = 'en'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇷🇴 Română", "🇩🇪 Deutsch", "🇫🇷 Français")
    bot.send_message(message.chat.id, strings['en']['start'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(message):
    lang = user_lang.get(message.chat.id, 'en')
    text = message.text

    # Schimbare Limbă
    if any(l in text for l in ["English", "Deutsch", "Français"]):
        user_lang[message.chat.id] = 'en'
        show_main(message)
    elif "Română" in text:
        user_lang[message.chat.id] = 'ro'
        show_main(message)
    elif "🌐" in text:
        start(message)

    # Navigare Meniu Principal
    elif "📊" in text:
        bot.send_message(message.chat.id, "Enter coin symbol (BTC, ETH):")
    elif "🛡️" in text:
        bot.send_message(message.chat.id, strings[lang]['defi_info'] if 'defi_info' in strings[lang] else "DeFi Scan active.")
    elif "🔍" in text:
        bot.send_message(message.chat.id, strings[lang]['audit_info'] if 'audit_info' in strings[lang] else "Audit Scan active.")
    
    # CLICK PE PREMIUM (Acum trimite și link-ul de Stripe)
    elif "💎 PREMIUM" in text or "💎 SERVICII" in text:
        show_premium_and_pay(message)

    # Logica Sub-Meniu Premium (Paywall)
    elif any(emoji in text for emoji in ["📈", "🐳", "💎"]) and "PREMIUM" not in text and "SERVICII" not in text:
        show_paywall(message, text)

    elif "⬅️" in text:
        show_main(message)

    # Prețuri Binance
    elif len(text) <= 8 and not text.startswith('/'):
        get_price(message)

def show_main(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(strings[lang]['free'], strings[lang]['premium'])
    markup.row(strings[lang]['defi'], strings[lang]['audit'])
    markup.row(strings[lang]['lang'])
    bot.send_message(message.chat.id, strings[lang]['main'], reply_markup=markup, parse_mode="Markdown")

def show_premium_and_pay(message):
    lang = user_lang.get(message.chat.id, 'en')
    
    # 1. Schimbăm tastatura de jos
    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_reply.row(strings[lang]['signals'], strings[lang]['whale'])
    markup_reply.row(strings[lang]['gems'], strings[lang]['back'])
    
    # 2. Creăm butonul Inline de Stripe
    markup_inline = types.InlineKeyboardMarkup()
    markup_inline.add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
    
    # 3. Trimitem mesajul cu butonul de plată
    bot.send_message(message.chat.id, strings[lang]['premium_intro'], 
                     reply_markup=markup_reply, parse_mode="Markdown")
    bot.send_message(message.chat.id, "👇 *Secure Payment Link:*", 
                     reply_markup=markup_inline, parse_mode="Markdown")

def show_paywall(message, btn_text):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
    
    if "📈" in btn_text: promo = strings[lang]['promo_sig']
    elif "🐳" in btn_text: promo = strings[lang]['promo_wha']
    else: promo = strings[lang]['promo_gem']
    
    bot.send_message(message.chat.id, promo, reply_markup=markup, parse_mode="Markdown")

def get_price(message):
    symbol = message.text.upper().strip() + "USDT"
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}").json()
        price = f"{float(r['price']):,.2f}"
        bot.send_message(message.chat.id, f"🚀 *{message.text.upper()}*: `${price}`", parse_mode="Markdown")
    except:
        pass

if __name__ == "__main__":
    bot.infinity_polling()
