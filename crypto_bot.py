import telebot
from telebot import types
import requests
import os
import time

# --- Configurare ---
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=False) # threaded=False e mai stabil pe servere mici

user_state = {}

def get_combined_data(address):
    address = address.strip().lower()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Datele pe care vrem sa le extragem
    report = {
        "price": "N/A",
        "liq": "N/A",
        "hp": "N/A",
        "tax": "N/A",
        "ow": "N/A"
    }

    # 1. INCERCAM DEXSCREENER (Pret si Lichiditate)
    try:
        d_res = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}", timeout=8).json()
        if d_res.get('pairs'):
            p = d_res['pairs'][0]
            report["price"] = f"${p.get('priceUsd', '0.00')}"
            report["liq"] = f"${p.get('liquidity', {}).get('usd', 0):,.0f}"
    except: pass

    # 2. INCERCAM GOPLUS (Securitate)
    for net_id in ["56", "1"]:
        try:
            url = f"https://api.goplussecurity.io/api/v1/token_security/{net_id}?contract_addresses={address}"
            g_res = requests.get(url, headers=headers, timeout=10).json()
            if g_res.get('code') == 1 and address in g_res.get('result', {}):
                data = g_res['result'][address]
                report["hp"] = "DA 🚨" if str(data.get("is_honeypot")) == "1" else "NU ✅"
                report["tax"] = f"{float(data.get('buy_tax', 0))*100:.1f}% / {float(data.get('sell_tax', 0))*100:.1f}%"
                report["ow"] = "Renounced ✅" if data.get("owner_address") == "0x0000000000000000000000000000000000000000" else "Active ⚠️"
                break
        except: continue
    
    return report

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
    bot.send_message(message.chat.id, "🚀 *Born Crypto Bot Online*\n\nAlege o opțiune:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    uid = message.chat.id
    text = message.text

    if "🛡️" in text or "🔍" in text:
        user_state[uid] = "waiting"
        bot.send_message(uid, "🛰️ Trimite adresa contractului (BSC/ETH):")
        return

    if user_state.get(uid) == "waiting":
        if text.startswith("0x") and len(text) > 30:
            bot.send_message(uid, "⌛ Scanăm piața și contractul...")
            data = get_combined_data(text)
            
            final_msg = (f"📊 *RAPORT TOKEN*\n`{text[:12]}...`\n\n"
                         f"💰 Pret: `{data['price']}`\n"
                         f"💧 Lichiditate: `{data['liq']}`\n"
                         f"🚨 Honeypot: {data['hp']}\n"
                         f"💸 Taxe: {data['tax']}\n"
                         f"👑 Owner: {data['ow']}")
            bot.send_message(uid, final_msg, parse_mode="Markdown")
        else:
            bot.send_message(uid, "❌ Adresă invalidă.")
        user_state[uid] = None

# Pornire cu Error Handling
if __name__ == "__main__":
    print("Botul porneste...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Eroare: {e}")
            time.sleep(5)
