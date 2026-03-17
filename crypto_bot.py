import telebot
from telebot import types
import requests
import os
import json
import time
import threading
from datetime import datetime, timedelta

# --- Configurare Initiala ---
TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN, threaded=False)

TRIALS_FILE = "trials_data.json"
user_state = {} # Pentru a urmari daca asteptam o adresa de la user

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
user_lang = {}

# --- FUNCTIE ANALIZA SECURITATE (GoPlus API) ---
def get_security_data(address):
    address = address.strip().lower()
    # Incercam pe retelele principale (1 = ETH, 56 = BSC)
    for net_id in ["1", "56"]:
        try:
            url = f"https://api.goplussecurity.io/api/v1/token_security/{net_id}?contract_addresses={address}"
            res = requests.get(url, timeout=10).json()
            if res.get('code') == 1 and address in res.get('result', {}):
                data = res['result'][address]
                return {
                    "hp": "DA 🚨" if data.get("is_honeypot") == "1" else "NU ✅",
                    "bt": f"{float(data.get('buy_tax', 0))*100:.1f}%",
                    "st": f"{float(data.get('sell_tax', 0))*100:.1f}%",
                    "lp": "DA ✅" if data.get("lp_locked") == "1" else "NU ⚠️",
                    "ow": "Renounced ✅" if data.get("owner_address") in ["0x0000000000000000000000000000000000000000", ""] else "Active ⚠️"
                }
        except: continue
    return None

# --- FUNCTIE PENTRU MESAJE AUTOMATE (FOLLOW-UP) ---
def send_marketing_followup(chat_id, lang):
    time.sleep(120)
    text = {
        'en': "🚀 Want better crypto signals?\n\n*Upgrade to Premium:*\n✅ Real-time alerts\n✅ Whale tracking\n✅ Early gems\n\n💰 Only 10€/month",
        'ro': "🚀 Vrei semnale crypto mai bune?\n\n*Treci la Premium:*\n✅ Alerte în timp real\n✅ Urmărire Balene\n✅ Early gems\n\n💰 Doar 10€/lună"
    }
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="💎 Upgrade Now", url=STRIPE_PAYMENT_LINK))
    try:
        bot.send_message(chat_id, text.get(lang, text['en']), reply_markup=markup, parse_mode="Markdown")
    except: pass

# --- FUNCTIE PENTRU TOP MONEDE (Binance Live) ---
def get_top_signals():
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    results = []
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        prices = requests.get(url, timeout=5).json()
        price_dict = {item['symbol']: float(item['price']) for item in prices if item['symbol'] in symbols}
        for sym in symbols:
            if sym in price_dict:
                price = price_dict[sym]
                results.append(f"🔸 **{sym.replace('USDT', '')}**\nEntry: `{price:.2f}`\nTarget: `{price * 1.025:.2f}`\n")
        return "\n".join(results)
    except: return "❌ Market data unavailable."

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    if uid not in user_trial_start:
        user_trial_start[uid] = datetime.now()
        save_trials(user_trial_start)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇷🇴 Română", "🇩🇪 Deutsch", "🇫🇷 Français")
    bot.send_message(uid, "🚀 *Born Crypto Bot v2.0*\nSelect language:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text

    # Setare Limba
    if "English" in text: user_lang[uid] = 'en'; show_main(message); return
    if "Română" in text: user_lang[uid] = 'ro'; show_main(message); return
    
    lang = user_lang.get(uid, 'en')

    # --- LOGICA PROCESARE ADRESA (Audit/DeFi) ---
    if user_state.get(uid) == "waiting_addr":
        if text.startswith("0x") and len(text) > 30:
            bot.send_message(uid, "⌛ " + ("Analyzing security..." if lang == 'en' else "Analizăm securitatea..."))
            data = get_security_data(text)
            if data:
                res = f"🔍 *Audit:* `{text[:10]}...`\n\nHoneypot: {data['hp']}\nTaxe: {data['bt']}/{data['st']}\nLP: {data['lp']}\nOwner: {data['ow']}"
                bot.send_message(uid, res, parse_mode="Markdown")
            else:
                bot.send_message(uid, "❌ " + ("Contract not found on ETH/BSC." if lang == 'en' else "Contractul nu a fost găsit."))
        else:
            bot.send_message(uid, "❌ " + ("Invalid address." if lang == 'en' else "Adresă invalidă."))
        user_state[uid] = None # Resetam starea
        return

    # --- NAVIGARE MENIU ---
    if "📊" in text: 
        bot.send_message(uid, "⌛ _Fetching market data..._", parse_mode="Markdown")
        signals = get_top_signals()
        header = "🆓 *LIVE TOP SIGNALS*\n\n" if lang == 'en' else "🆓 *SEMNALE LIVE TOP*\n\n"
        bot.send_message(uid, header + signals, parse_mode="Markdown")
        threading.Thread(target=send_marketing_followup, args=(uid, lang)).start()

    elif "🛡️" in text or "🔍" in text:
        user_state[uid] = "waiting_addr"
        msg = "🛰️ Paste address (ETH/BSC):" if lang == 'en' else "🛰️ Trimite adresa contractului (ETH/BSC):"
        bot.send_message(uid, msg)

    elif "💎" in text: show_premium(message)
    elif "⬅️" in text: show_main(message)
    elif "🌐" in text: start(message)
    elif any(x in text for x in ["📈", "🐳", "🔥", "💎 Early"]):
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Upgrade", url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, "🔒 Premium feature!", reply_markup=markup)

def show_main(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Free Signals", "💎 PREMIUM")
    markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
    markup.row("🌐 Language")
    bot.send_message(message.chat.id, "🏠 *Main Menu*", reply_markup=markup, parse_mode="Markdown")

def show_premium(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📈 5x Signals", "🐳 Whale Alerts")
    markup.row("💎 Early Gems", "🔥 Gainers")
    markup.row("⬅️ Back")
    pay_btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="💳 Buy Now 10€", url=STRIPE_PAYMENT_LINK))
    bot.send_message(message.chat.id, "💎 *PREMIUM SERVICES*", reply_markup=markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "Get full access here:", reply_markup=pay_btn)

if __name__ == "__main__":
    try: bot.remove_webhook()
    except: pass
    bot.polling(none_stop=True)
