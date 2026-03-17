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
user_state = {} 
user_lang = {}

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

# --- FUNCTIE PRET TOKEN (DexScreener) ---
def get_token_price(address):
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
        res = requests.get(url, timeout=5).json()
        if res.get('pairs'):
            # Luam prima pereche care are pretul in USD
            for pair in res['pairs']:
                if 'priceUsd' in pair:
                    return f"${pair['priceUsd']}"
    except: pass
    return "N/A"

# --- FUNCTIE ANALIZA SECURITATE (GoPlus) ---
def get_security_data(address):
    address = address.strip().lower()
    # Incercam pe BSC (56) si ETH (1)
    for net_id in ["56", "1"]:
        try:
            url = f"https://api.goplussecurity.io/api/v1/token_security/{net_id}?contract_addresses={address}"
            response = requests.get(url, timeout=10)
            res_data = response.json()
            
            if res_data.get('code') == 1 and address in res_data.get('result', {}):
                data = res_data['result'][address]
                price = get_token_price(address)
                return {
                    "price": price,
                    "hp": "DA 🚨" if data.get("is_honeypot") == "1" else "NU ✅",
                    "bt": f"{float(data.get('buy_tax', 0))*100:.1f}%",
                    "st": f"{float(data.get('sell_tax', 0))*100:.1f}%",
                    "lp": "DA ✅" if data.get("lp_locked") == "1" or data.get("lp_hold_confirm") == "1" else "NU ⚠️",
                    "ow": "Renounced ✅" if data.get("owner_address") in ["0x0000000000000000000000000000000000000000", ""] or not data.get("owner_address") else "Active ⚠️"
                }
        except Exception as e:
            print(f"Error checking net {net_id}: {e}")
            continue
    return None

# --- MARKETING FOLLOW-UP ---
def send_marketing_followup(chat_id, lang):
    time.sleep(120)
    text = {
        'en': "🚀 Want better crypto signals?\n\n*Upgrade to Premium:*\n✅ Real-time alerts\n✅ Whale tracking\n✅ Early gems\n\n💰 Only 10€/month",
        'ro': "🚀 Vrei semnale crypto mai bune?\n\n*Treci la Premium:*\n✅ Alerte în timp real\n✅ Urmărire Balene\n✅ Early gems\n\n💰 Doar 10€/lună"
    }
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="💎 Upgrade Now", url=STRIPE_PAYMENT_LINK))
    try:
        bot.send_message(chat_id, text.get(lang, 'en'), reply_markup=markup, parse_mode="Markdown")
    except: pass

# --- TOP SIGNALS (Binance) ---
def get_top_signals():
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    results = []
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        prices = requests.get(url, timeout=5).json()
        price_dict = {item['symbol']: float(item['price']) for item in prices if item['symbol'] in symbols}
        for sym in symbols:
            if sym in price_dict:
                p = price_dict[sym]
                results.append(f"🔸 **{sym.replace('USDT', '')}**\nEntry: `{p:.2f}`\nTarget: `{p * 1.025:.2f}`\n")
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
    bot.send_message(uid, "🚀 *Born Crypto Bot v2.0*", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text
    lang = user_lang.get(uid, 'en')

    if "English" in text: user_lang[uid] = 'en'; show_main(message); return
    if "Română" in text: user_lang[uid] = 'ro'; show_main(message); return

    # --- LOGICA AUDIT ---
    if user_state.get(uid) == "waiting_addr":
        if text.startswith("0x"):
            bot.send_message(uid, "⌛ " + ("Analyzing..." if lang == 'en' else "Analizăm..."))
            data = get_security_data(text)
            if data:
                res = (f"🔍 *Audit:* `{text[:10]}...`\n"
                       f"💰 *Price:* `{data['price']}`\n\n"
                       f"Honeypot: {data['hp']}\n"
                       f"Taxe: {data['bt']}/{data['st']}\n"
                       f"LP: {data['lp']}\n"
                       f"Owner: {data['ow']}")
                bot.send_message(uid, res, parse_mode="Markdown")
            else:
                bot.send_message(uid, "❌ Contract not found on ETH/BSC. Make sure the address is correct.")
        user_state[uid] = None
        return

    # --- MENIU ---
    if "📊" in text:
        signals = get_top_signals()
        bot.send_message(uid, "🆓 *TOP SIGNALS*\n\n" + signals, parse_mode="Markdown")
        threading.Thread(target=send_marketing_followup, args=(uid, lang)).start()
    
    elif "🛡️" in text or "🔍" in text:
        user_state[uid] = "waiting_addr"
        bot.send_message(uid, "🛰️ " + ("Paste address (ETH/BSC):" if lang == 'en' else "Trimite adresa contractului (ETH/BSC):"))
    
    elif "💎" in text: show_premium(message)
    elif "⬅️" in text: show_main(message)
    elif "🌐" in text: start(message)

def show_main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Free Signals", "💎 PREMIUM")
    markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
    markup.row("🌐 Language")
    bot.send_message(message.chat.id, "🏠 *Main Menu*", reply_markup=markup, parse_mode="Markdown")

def show_premium(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📈 5x Signals", "🐳 Whale Alerts")
    markup.row("💎 Early Gems", "🔥 Gainers")
    markup.row("⬅️ Back")
    bot.send_message(message.chat.id, "💎 *PREMIUM*", reply_markup=markup, parse_mode="Markdown")

if __name__ == "__main__":
    try: bot.remove_webhook()
    except: pass
    bot.polling(none_stop=True)
