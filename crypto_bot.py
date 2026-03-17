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
        # Verificam pe BSC (56) si Ethereum (1)
        url = f"https://api.goplussecurity.io/api/v1/token_security/1?contract_addresses={address}"
        res = requests.get(url).json()
        if res['code'] != 1: # Daca nu e pe ETH, incercam pe BSC
            url = f"https://api.goplussecurity.io/api/v1/token_security/56?contract_addresses={address}"
            res = requests.get(url).json()
        
        data = res['result'][address.lower()]
        audit = {
            "honeypot": "DA 🚨" if data.get("is_honeypot") == "1" else "NU ✅",
            "buy_tax": f"{float(data.get('buy_tax', 0))*100:.1f}%",
            "sell_tax": f"{float(data.get('sell_tax', 0))*100:.1f}%",
            "lp_locked": "DA ✅" if data.get("lp_locked") == "1" else "NU ⚠️",
            "owner": "Renounced ✅" if data.get("owner_address") == "0x0000000000000000000000000000000000000000" else "Active ⚠️"
        }
        return audit
    except:
        return None

strings = {
    'en': {
        'start': "🚀 *Born Crypto Bot v2.0*\nSelect language:",
        'main': "🏠 *Main Menu*",
        'free': "📊 Free Signals",
        'premium': "💎 PREMIUM",
        'pay': "💳 Upgrade Now",
        'lang': "🌐 Language / Limba",
        'trial_expired': "🚨 *Trial expired!*\nUpgrade to Premium.",
        'ask_address': "🛰️ Paste Contract Address:",
        'audit_res': "🔍 *Audit:* `{addr}`\n\nHoneypot: {hp}\nBuy Tax: {bt}\nSell Tax: {st}\nLP Locked: {lp}\nOwner: {ow}"
    },
    'ro': {
        'start': "🚀 *Born Crypto Bot v2.0*\nSelectează limba:",
        'main': "🏠 *Meniu Principal*",
        'free': "📊 Semnale Free",
        'premium': "💎 SERVICII PREMIUM",
        'pay': "💳 Cumpără Acum",
        'lang': "🌐 Schimbă Limba",
        'trial_expired': "🚨 *Trial expirat!*\nAbonează-te.",
        'ask_address': "🛰️ Trimite adresa contractului:",
        'audit_res': "🔍 *Audit:* `{addr}`\n\nHoneypot: {hp}\nTaxa Cumparare: {bt}\nTaxa Vanzare: {st}\nLP Blocat: {lp}\nOwner: {ow}"
    },
    'de': {
        'start': "🚀 *Born Crypto Bot v2.0*\nSprache wählen:",
        'main': "🏠 *Hauptmenü*",
        'free': "📊 Kostenlose Signale",
        'premium': "💎 PREMIUM DIENSTE",
        'pay': "💳 Jetzt upgraden",
        'lang': "🌐 Sprache ändern",
        'trial_expired': "🚨 *Testversion abgelaufen!*",
        'ask_address': "🛰️ Vertragsadresse einfügen:",
        'audit_res': "🔍 *Audit:* `{addr}`\nHoneypot: {hp}\nSteuer: {bt}/{st}"
    },
    'fr': {
        'start': "🚀 *Born Crypto Bot v2.0*\nChoisir la langue:",
        'main': "🏠 *Menu Principal*",
        'free': "📊 Signaux Gratuits",
        'premium': "💎 SERVICES PREMIUM",
        'pay': "💳 Acheter maintenant",
        'lang': "🌐 Changer de langue",
        'trial_expired': "🚨 *Essai expiré!*",
        'ask_address': "🛰️ Coller l'adresse du contrat:",
        'audit_res': "🔍 *Audit:* `{addr}`\nHoneypot: {hp}\nTaxe: {bt}/{st}"
    }
}

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

    # REPARARE LIMBI
    if "English" in text: user_lang[uid] = 'en'; show_main(message); return
    if "Română" in text: user_lang[uid] = 'ro'; show_main(message); return
    if "Deutsch" in text: user_lang[uid] = 'de'; show_main(message); return
    if "Français" in text: user_lang[uid] = 'fr'; show_main(message); return

    lang = user_lang.get(uid, 'en')

    if not is_trial_active(uid):
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, strings[lang]['trial_expired'], reply_markup=markup, parse_mode="Markdown")
        return

    # LOGICA AUDIT REALA
    if user_state.get(uid) == "waiting_addr":
        bot.send_message(uid, "⌛ Analizăm contractul...")
        data = get_security_data(text)
        if data:
            res = strings[lang]['audit_res'].format(addr=text[:10]+"...", hp=data['honeypot'], bt=data['buy_tax'], st=data['sell_tax'], lp=data['lp_locked'], ow=data['owner'])
            bot.send_message(uid, res, parse_mode="Markdown")
        else:
            bot.send_message(uid, "❌ Adresă invalidă sau rețea nesuportată (Folosiți ETH/BSC).")
        user_state[uid] = None
        return

    if "📊" in text: bot.send_message(uid, strings[lang]['free'], parse_mode="Markdown")
    elif "🛡️" in text or "🔍" in text:
        user_state[uid] = "waiting_addr"
        bot.send_message(uid, strings[lang]['ask_address'])
    elif "💎" in text: show_premium(message)
    elif "🌐" in text: start(message)

def show_main(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(strings[lang]['free'], strings[lang]['premium'])
    markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
    markup.row(strings[lang]['lang'])
    bot.send_message(message.chat.id, strings[lang]['main'], reply_markup=markup, parse_mode="Markdown")

def show_premium(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text=strings[lang]['pay'], url=STRIPE_PAYMENT_LINK))
    bot.send_message(message.chat.id, "🌟 PREMIUM: Signals, Whale Alerts & More", reply_markup=markup)

if __name__ == "__main__":
    try:
        bot.remove_webhook()
        time.sleep(1)
    except: pass
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            time.sleep(5)
