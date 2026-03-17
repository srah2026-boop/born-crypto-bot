import telebot
from telebot import types
import requests
import os

# Configurare Date
TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN)

# Dicționar Master (Engleza e Baza)
strings = {
    'en': {
        'start': "🚀 *Born Crypto Bot v2.0*\nYour professional trading suite. Select language:",
        'main': "🏠 *Main Menu*",
        'free': "📊 Live Prices (Binance)",
        'defi': "🛡️ DeFi Analysis",
        'audit': "🔍 Contract Audit",
        'premium': "💎 PREMIUM SERVICES",
        'signals': "📈 Daily Signals",
        'whale': "🐳 Whale Tracker",
        'gems': "💎 Early Gems",
        'pay': "💳 Subscribe Now (Stripe)",
        'back': "⬅️ Back",
        'lang': "🌐 Language / Limba",
        'price_info': "Enter a coin symbol (e.g., BTC, ETH, SOL) to get the live Binance price:",
        'defi_info': "🛡️ *DeFi Analysis Tool*\nReal-time monitoring of DEX liquidity pools and TVL. Upgrade to Premium for deep-scan alerts.",
        'audit_info': "🔍 *Smart Contract Audit*\nScanning for Honeypots and Mint functions. Paste a contract address to start (Premium only).",
        'promo_sig': "🎯 *Daily Signals*\nGet the Top 3 high-probability trades every morning with TP/SL.",
        'promo_wha': "🐋 *Whale Tracker*\nTrack $1M+ movements between wallets and exchanges in real-time.",
        'promo_gem': "💎 *Early Gems*\nDiscover micro-cap tokens with 100x potential before they hit CEXs."
    },
    'ro': {
        'start': "🚀 *Born Crypto Bot v2.0*\nAsistentul tău profesional. Selectează limba:",
        'main': "🏠 *Meniu Principal*",
        'free': "📊 Prețuri Live (Binance)",
        'defi': "🛡️ Analiză DeFi",
        'audit': "🔍 Audit Contracte",
        'premium': "💎 SERVICII PREMIUM",
        'signals': "📈 Semnale Zilnice",
        'whale': "🐳 Whale Tracker",
        'gems': "💎 Early Gems",
        'pay': "💳 Abonează-te (Stripe)",
        'back': "⬅️ Înapoi",
        'lang': "🌐 Schimbă Limba",
        'price_info': "Introdu simbolul monedei (ex: BTC, ETH) pentru prețul Binance live:",
        'defi_info': "🛡️ *Analiză DeFi*\nMonitorizare bazine lichiditate și TVL. Treci la Premium pentru alerte avansate.",
        'audit_info': "🔍 *Audit Contract*\nScanare Honeypot și funcții Mint. Introdu adresa contractului (Doar Premium).",
        'promo_sig': "🎯 *Semnale Zilnice*\nTop 3 tranzacții cu probabilitate mare în fiecare dimineață.",
        'promo_wha': "🐋 *Whale Tracker*\nUrmărește mișcările de 1M$+ între portofele și burse.",
        'promo_gem': "💎 *Early Gems*\nDescoperă proiecte noi cu potențial de 100x pe DEX-uri."
    }
}

user_lang = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_lang[message.chat.id] = 'en' # Start obligatoriu în Engleză
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
        bot.send_message(message.chat.id, strings[lang]['price_info'])
    elif "🛡️" in text:
        bot.send_message(message.chat.id, strings[lang]['defi_info'], parse_mode="Markdown")
    elif "🔍" in text:
        bot.send_message(message.chat.id, strings[lang]['audit_info'], parse_mode="Markdown")
    elif "💎 PREMIUM" in text or "💎 SERVICII" in text:
        show_premium(message)

    # Logica Premium (Paywall)
    elif any(emoji in text for emoji in ["📈", "🐳", "💎"]) and "PREMIUM" not in text and "SERVICII" not in text:
        show_paywall(message, text)

    # Înapoi
    elif "⬅️" in text:
        show_main(message)

    # Prețuri Live Binance
    elif len(text) <= 8 and not text.startswith('/'):
        symbol = text.upper().strip() + "USDT"
        try:
            r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}").json()
            price = f"{float(r['price']):,.2f}"
            bot.send_message(message.chat.id, f"🚀 *{text.upper()}* Live: `${price}`\n_Source: Binance_", parse_mode="Markdown")
        except:
            pass 

def show_main(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(strings[lang]['free'], strings[lang]['premium'])
    markup.row(strings[lang]['defi'], strings[lang]['audit'])
    markup.row(strings[lang]['lang'])
    bot.send_message(message.chat.id, strings[lang]['main'], reply_markup=markup, parse_mode="Markdown")

def show_premium(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(strings[lang]['signals'], strings[lang]['whale'])
    markup.row(strings[lang]['gems'], strings[lang]['back'])
    bot.send_message(message.chat.id, "💎 *Premium Control Panel*", reply_markup=markup, parse_mode="Markdown")

def show_paywall(message, btn_text):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
    
    if "📈" in btn_text: promo = strings[lang]['promo_sig']
    elif "🐳" in btn_text: promo = strings[lang]['promo_wha']
    else: promo = strings[lang]['promo_gem']
    
    bot.send_message(message.chat.id, promo, reply_markup=markup, parse_mode="Markdown")

if __name__ == "__main__":
    bot.infinity_polling()
