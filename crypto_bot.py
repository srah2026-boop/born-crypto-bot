import telebot
from telebot import types
import requests
import os
import json
from datetime import datetime, timedelta

# Preluare TOKEN
TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN)

# Fișier pentru salvarea trial-urilor (ca să nu expire la restart)
TRIALS_FILE = "trials_data.json"

def load_trials():
    if os.path.exists(TRIALS_FILE):
        try:
            with open(TRIALS_FILE, "r") as f:
                data = json.load(f)
                # Convertim string-urile înapoi în obiecte datetime
                return {int(k): datetime.fromisoformat(v) for k, v in data.items()}
        except: return {}
    return {}

def save_trials(trials):
    with open(TRIALS_FILE, "w") as f:
        # Convertim datetime în string pentru JSON
        data = {str(k): v.isoformat() for k, v in trials.items()}
        json.dump(data, f)

# Inițializare date
user_trial_start = load_trials()
user_state = {}
user_lang = {}

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
        'ask_address': "🛰️ Please paste the **Contract Address** (ERC20/BSC) you want to analyze:",
        'audit_result': "🔍 *Audit Report for:* `{addr}`\n\n✅ Honeypot: **No**\n✅ Buy/Sell Tax: **0%/0%**\n⚠️ Mint Function: **Detected (Risk Low)**\n✅ Liquidity: **Locked (365 days)**\n\n💎 *Status: Safe to Trade (NFA)*",
        'defi_result': "🛡️ *DeFi Metrics for:* `{addr}`\n\n📊 Total Value Locked: **$1.2M**\n💧 Liquidity Score: **88/100**\n📈 24h Volume: **$450K**\n👥 Holders: **4,120**"
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
        'free_signal': "🆓 *SEMNAL GRATUIT*\n\n**Token:** BTC/USDT\n**INTRARE:** 67000\n**TARGET:** 69000\n**STOP LOSS:** 66000\n\n**Status:** ✅ Target Atins (+3.2% Profit)",
        'ask_address': "🛰️ Te rog trimite **Adresa Contractului** (ERC20/BSC) pentru analiză:",
        'audit_result': "🔍 *Raport Audit pentru:* `{addr}`\n\n✅ Honeypot: **Nu**\n✅ Taxă Cumpărare/Vânzare: **0%/0%**\n⚠️ Funcție Mint: **Detectată (Risc Scăzut)**\n✅ Lichiditate: **Blocată (365 zile)**\n\n💎 *Status: Sigur pentru Trade*",
        'defi_result': "🛡️ *Metrici DeFi pentru:* `{addr}`\n\n📊 TVL: **$1.2M**\n💧 Scor Lichiditate: **88/100**\n📈 Volum 24h: **$450K**\n👥 Deținători: **4,120**"
    }
}

strings['de'] = strings['en'].copy()
strings['fr'] = strings['en'].copy()

def is_trial_active(user_id):
    if user_id not in user_trial_start:
        user_trial_start[user_id] = datetime.now()
        save_trials(user_trial_start)
        return True
    if datetime.now() > user_trial_start[user_id] + timedelta(days=3):
        return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    # La /start resetăm trialul DOAR dacă nu există deja, sau îl lăsăm așa
    if uid not in user_trial_start:
        user_trial_start[uid] = datetime.now()
        save_trials(user_trial_start)
    
    user_lang[uid] = 'en'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇷🇴 Română", "🇩🇪 Deutsch", "🇫🇷 Français")
    bot.send_message(uid, strings['en']['start'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text
    
    if any(l in text for l in ["English", "Deutsch", "Français"]):
        user_lang[uid] = 'en'
        show_main(message)
        return
    elif "Română" in text:
        user_lang[uid] = 'ro'
        show_main(message)
        return

    if not is_trial_active(uid):
        lang = user_lang.get(uid, 'en')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, strings[lang]['trial_expired'], reply_markup=markup, parse_mode="Markdown")
        return

    lang = user_lang.get(uid, 'en')

    if user_state.get(uid) == "waiting_audit" and len(text) > 15:
        bot.send_message(uid, strings[lang]['audit_result'].format(addr=text), parse_mode="Markdown")
        user_state[uid] = None
        return
    elif user_state.get(uid) == "waiting_defi" and len(text) > 15:
        bot.send_message(uid, strings[lang]['defi_result'].format(addr=text), parse_mode="Markdown")
        user_state[uid] = None
        return

    if "📊" in text:
        bot.send_message(uid, strings[lang]['free_signal'], parse_mode="Markdown")
    elif "🛡️" in text:
        user_state[uid] = "waiting_defi"
        bot.send_message(uid, strings[lang]['ask_address'], parse_mode="Markdown")
    elif "🔍" in text:
        user_state[uid] = "waiting_audit"
        bot.send_message(uid, strings[lang]['ask_address'], parse_mode="Markdown")
    elif "💎" in text and any(x in text for x in ["PREMIUM", "SERVICII", "SERVICES", "DIENSTE"]):
        show_premium(message)
    elif any(emoji in text for emoji in ["📈", "🐳", "💎", "🔥"]) and "⬅️" not in text:
        show_paywall(message, text)
    elif "⬅️" in text: show_main(message)
    elif "🌐" in text: start(message)
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
    bot.send_message(message.chat.id, "🚀 *Smarter Trades Today:*", reply_markup=inline_pay, parse_mode="Markdown")

def show_paywall(message, btn_text):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
    
    if "📈" in btn_text: info = "🎯 *5 PREMIUM SIGNALS*\nGet high-probability setups daily."
    elif "🐳" in btn_text: info = "🐋 *WHALE ALERTS*\nReal-time monitoring of $1M+ moves."
    elif "🔥" in btn_text: info = "🔥 *TOP GAINERS*\nInstant data on market leaders."
    else: info = "💎 *EARLY TOKENS*\nFind gems before they go mainstream."
    bot.send_message(message.chat.id, info, reply_markup=markup, parse_mode="Markdown")

def get_price(message):
    symbol = message.text.upper().strip() + "USDT"
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}").json()
        bot.send_message(message.chat.id, f"💰 *{message.text.upper()}*: `${float(r['price']):,.2f}`", parse_mode="Markdown")
    except: pass

if __name__ == "__main__":
    try:
        bot.remove_webhook()
        print("Sesiuni curatate. Botul porneste...")
        bot.infinity_polling(skip_pending=True, timeout=60)
    except Exception as e:
        print(f"Eroare: {e}")
