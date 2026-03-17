import telebot
from telebot import types
import requests
import os
import json
import time
import threading
from datetime import datetime, timedelta

# --- CONFIGURARE ---
TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN, threaded=False)

user_state = {}
user_lang = {}

# --- MOTORUL DE ANALIZĂ (ULTRA-STABIL) ---
def get_security_data(address):
    address = address.strip().lower()
    # Header-e de browser real (Chrome pe Windows)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://goplussecurity.io",
        "Referer": "https://goplussecurity.io/"
    }

    # Verificăm ambele rețele (BSC - 56, ETH - 1)
    for net_id in ["56", "1"]:
        try:
            url = f"https://api.goplussecurity.io/api/v1/token_security/{net_id}?contract_addresses={address}"
            # Încercăm de 2 ori dacă prima dată eșuează
            for attempt in range(2):
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    res_json = response.json()
                    if res_json.get('code') == 1 and res_json.get('result'):
                        # Căutăm adresa indiferent de litere mari/mici
                        result_data = None
                        for key in res_json['result']:
                            if key.lower() == address:
                                result_data = res_json['result'][key]
                                break
                        
                        if result_data:
                            # Calculăm prețul via DexScreener
                            price = "N/A"
                            try:
                                p_req = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}", timeout=5).json()
                                if p_req.get('pairs'):
                                    price = f"${p_req['pairs'][0].get('priceUsd', '0.00')}"
                            except: pass

                            return {
                                "price": price,
                                "hp": "DA 🚨" if str(result_data.get("is_honeypot")) == "1" else "NU ✅",
                                "bt": f"{float(result_data.get('buy_tax', 0))*100:.1f}%",
                                "st": f"{float(result_data.get('sell_tax', 0))*100:.1f}%",
                                "lp": "DA ✅" if str(result_data.get("lp_locked")) == "1" or str(result_data.get("lp_hold_confirm")) == "1" else "NU ⚠️",
                                "ow": "Renounced ✅" if result_data.get("owner_address") in ["0x0000000000000000000000000000000000000000", ""] or not result_data.get("owner_address") else "Active ⚠️"
                            }
                time.sleep(1) # Mică pauză între reîncercări
        except Exception as e:
            print(f"Network error on net {net_id}: {e}")
            continue
    return None

# --- HANDLERS ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇷🇴 Română")
    bot.send_message(message.chat.id, "🚀 *Born Crypto Bot v2.0*", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text
    lang = user_lang.get(uid, 'ro')

    if "English" in text: user_lang[uid] = 'en'; show_main(message); return
    if "Română" in text: user_lang[uid] = 'ro'; show_main(message); return

    # --- LOGICA PROCESARE ADRESĂ ---
    if user_state.get(uid) == "waiting_addr":
        if text.startswith("0x") and len(text) > 30:
            bot.send_message(uid, "⌛ " + ("Analyzing security..." if lang == 'en' else "Analizăm securitatea..."))
            data = get_security_data(text)
            if data:
                res = (f"🛡️ *RAPORT COMPLET*\n`{text[:14]}...`\n\n"
                       f"💰 Pret: `{data['price']}`\n"
                       f"🚨 Honeypot: {data['hp']}\n"
                       f"💸 Taxe: {data['bt']} / {data['st']}\n"
                       f"🔒 LP Locked: {data['lp']}\n"
                       f"👑 Owner: {data['ow']}")
                bot.send_message(uid, res, parse_mode="Markdown")
            else:
                bot.send_message(uid, "❌ Not Found. Asigură-te că e ETH sau BSC.")
        user_state[uid] = None
        return

    # --- MENIU ---
    if "🛡️" in text or "🔍" in text:
        user_state[uid] = "waiting_addr"
        bot.send_message(uid, "🛰️ " + ("Paste address:" if lang == 'en' else "Trimite adresa:"))
    
    elif "📊" in text:
        bot.send_message(uid, "📈 *Generăm semnale...*") # Pune aici logica de Binance

def show_main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Semnale Free", "💎 PREMIUM")
    markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
    bot.send_message(message.chat.id, "🏠 *Meniu*", reply_markup=markup, parse_mode="Markdown")

if __name__ == "__main__":
    bot.polling(none_stop=True)
