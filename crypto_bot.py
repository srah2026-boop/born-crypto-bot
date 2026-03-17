import telebot
from telebot import types
import requests
import os
import json
import time
from datetime import datetime, timedelta

# Configurare Initiala
TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN, threaded=False)

TRIALS_FILE = "trials_data.json"

def load_trials():
    if os.path.exists(TRIALS_FILE):
        try:
            with open(TRIALS_FILE, "r") as f:
                data = json.load(f)
                return {int(k): datetime.fromisoformat(v) for k, v in data.items()}
        except: return {}
    return {}

def save_trials(trials):
    try:
        with open(TRIALS_FILE, "w") as f:
            data = {str(k): v.isoformat() for k, v in trials.items()}
            json.dump(data, f)
    except: pass

user_trial_start = load_trials()
user_state = {}
user_lang = {}

# --- FUNCTIE ANALIZA REALA (GoPlus Security API) ---
def get_security_data(address):
    try:
        url = f"https://api.goplussecurity.io/api/v1/token_security/1?contract_addresses={address}"
        res = requests.get(url, timeout=10).json()
        if res.get('code') != 1:
            url = f"https://api.goplussecurity.io/api/v1/token_security/56?contract_addresses={address}"
            res = requests.get(url, timeout=10).json()
        
        data = res['result'][address.lower()]
        return {
            "honeypot": "DA 🚨" if data.get("is_honeypot") == "1" else "NU ✅",
            "buy_tax": f"{float(data.get('buy_tax', 0))*100:.1f}%",
            "sell_tax": f"{float(data.get('sell_tax', 0))*100:.1f}%",
            "lp_locked": "DA ✅" if data.get("lp_locked") == "1" else "NU ⚠️",
            "owner": "Renounced ✅" if data.get("owner_address") == "0x0000000000000000000000000000000000000000" else "Active ⚠️"
        }
    except: return None

strings = {
    'en': {
        'start': "🚀 *Born Crypto Bot v2.0*\nSelect language:",
        'main': "🏠 *Main Menu*",
        'free': "📊 Free Signals",
        'premium': "💎 PREMIUM",
        'signals': "📈 5x Signals", 'whale': "🐳 Whale Alerts", 'gems': "💎 Gems", 'gainers': "🔥 Gainers",
        'pay': "💳 Upgrade Now",
        'back': "⬅️ Back",
        'lang': "🌐 Language",
        'trial_expired': "🚨 *Trial expired!*",
        'ask_address': "🛰️ Paste Contract Address:",
        'free_msg': "🆓 *FREE SIGNAL*\n\n**Token:** BTC/USDT\n**ENTRY:** 67000\n**TARGET:** 69500\n**STATUS:** ✅ Completed",
        'audit_res': "🔍 *Audit:* `{addr}`\nHoneypot: {hp}\nTax: {bt}/{st}\nLP: {lp}\nOwner: {ow}"
    },
    'ro': {
        'start': "🚀 *Born Crypto Bot v2.0*\nSelectează limba:",
        'main': "🏠 *Meniu Principal*",
        'free': "📊 Semnale Free",
        'premium': "💎 SERVICII PREMIUM",
        'signals': "📈 5x Semnale", 'whale': "🐳 Alerte Balene", 'gems': "💎 Early Gems", 'gainers': "🔥 Top Gainers",
        'pay': "💳 Cumpără Acum",
        'back': "⬅️ Înapoi",
        'lang': "🌐 Schimbă Limba",
        'trial_expired': "🚨 *Trial expirat!*",
        'ask_address': "🛰️ Trimite adresa contractului:",
        'free_msg': "🆓 *SEMNAL GRATUIT*\n\n**Token:** BTC/USDT\n**INTRARE:** 67000\n**TARGET:** 69500\n**STATUS:** ✅ Finalizat",
        'audit_res': "🔍 *Audit:* `{addr}`\nHoneypot: {hp}\nTaxe: {bt}/{st}\nLP: {lp}\nOwner: {ow}"
    }
}
# Copiem ro/en pentru de/fr rapid
strings['de'] = strings['en'].copy(); strings['fr'] = strings['en'].copy()

def is_trial_active(user_id):
    if user_id not in user_trial_start:
        user_trial_start[user_id] = datetime.now()
        save_trials(user_trial_start)
        return True
    return datetime.now() <= user_trial_start[user_id] + timedelta(days=3)

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    if uid not in user_trial_start:
        user_trial_start[uid] = datetime.now()
        save_trials(user_trial_start)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇷🇴 Română", "🇩🇪 Deutsch", "🇫🇷 Français")
    bot.send_message(uid, strings['en']['start'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text

    if "English" in text: user_lang[uid] = 'en'; show_main(message); return
    if "Română" in text: user_lang[uid] = 'ro'; show_main(message); return
    if "Deutsch" in text: user_lang[uid] = 'de'; show_main(message); return
    if "Français" in text: user_lang[uid] = 'fr'; show_main(message); return

    lang = user_lang.get(uid, 'en')

    if not is_trial_active(uid):
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, strings[lang]['trial_expired'], reply_markup=markup, parse_mode="Markdown")
        return

    if user_state.get(uid) == "waiting_addr":
        bot.send_message(uid, "⌛ Analizăm...")
        data = get_security_data(text)
        if data:
            res = strings[lang]['audit_res'].format(addr=text[:10]+"...", hp=data['honeypot'], bt=data['buy_tax'], st=data['sell_tax'], lp=data['lp_locked'], ow=data['owner'])
            bot.send_message(uid, res, parse_mode="Markdown")
        else:
            bot.send_message(uid, "❌ Error. Use ETH/BSC addresses.")
        user_state[uid] = None
        return

    if "📊" in text: 
        bot.send_message(uid, strings[lang]['free_msg'], parse_mode="Markdown")
    elif "🛡️" in text or "🔍" in text:
        user_state[uid] = "waiting_addr"
        bot.send_message(uid, strings[lang]['ask_address'])
    elif "💎" in text: 
        show_premium(message)
    elif "⬅️" in text: 
        show_main(message)
    elif "🌐" in text: 
        start(message)

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
    
    pay_btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
    bot.send_message(message.chat.id, "💎 *PREMIUM MENU*", reply_markup=markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "Unlock all features here:", reply_markup=pay_btn)

if __name__ == "__main__":
    try: bot.remove_webhook()
    except: pass
    while True:
        try: bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception: time.sleep(5)
