import telebot
from telebot import types
import requests
import os
import time

# --- CONFIGURARE ---
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)
user_state = {}

def get_audit_data(address):
    address = address.strip().lower()
    
    # 1. INCERCAM DEXSCREENER (Pentru Pret si verificari de baza)
    # DexScreener este mult mai permisiv cu serverele cloud
    price = "N/A"
    liquidity = "N/A"
    try:
        dex_url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
        dex_res = requests.get(dex_url, timeout=10).json()
        if dex_res.get('pairs'):
            pair = dex_res['pairs'][0]
            price = f"${pair.get('priceUsd', '0.00')}"
            liquidity = f"${pair.get('liquidity', {}).get('usd', 0):,.0f}"
    except: pass

    # 2. INCERCAM GOPLUS (Pentru Securitate)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0",
        "Accept": "application/json"
    }
    
    security = None
    for net_id in ["56", "1"]:
        try:
            url = f"https://api.goplussecurity.io/api/v1/token_security/{net_id}?contract_addresses={address}"
            res = requests.get(url, headers=headers, timeout=10).json()
            if res.get('code') == 1 and res.get('result') and address in res['result']:
                data = res['result'][address]
                security = {
                    "hp": "DA 🚨" if str(data.get("is_honeypot")) == "1" else "NU ✅",
                    "bt": f"{float(data.get('buy_tax', 0))*100:.1f}%",
                    "st": f"{float(data.get('sell_tax', 0))*100:.1f}%",
                    "lp": "DA ✅" if str(data.get("lp_locked")) == "1" else "NU ⚠️",
                    "ow": "Renounced ✅" if data.get("owner_address") == "0x0000000000000000000000000000000000000000" else "Active ⚠️"
                }
                break
        except: continue

    # 3. CONSTRUIRE RASPUNS
    if security:
        return (f"🛡️ *RAPORT COMPLET*\n\n"
                f"💰 Pret: `{price}`\n"
                f"💧 Lichiditate: `{liquidity}`\n"
                f"🚨 Honeypot: {security['hp']}\n"
                f"💸 Taxe: {security['bt']} / {security['st']}\n"
                f"🔒 LP Locked: {security['lp']}\n"
                f"👑 Owner: {security['ow']}")
    elif price != "N/A":
        return (f"📊 *DATE PIATA (Securitate Indisponibila)*\n\n"
                f"💰 Pret: `{price}`\n"
                f"💧 Lichiditate: `{liquidity}`\n\n"
                f"⚠️ _Nota: API-ul de securitate este momentan ocupat, dar tokenul exista in piata._")
    
    return None

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text

    if "🛡️" in text or "🔍" in text:
        user_state[uid] = "waiting"
        bot.send_message(uid, "🛰️ Trimite adresa (BSC/ETH):")
        return

    if user_state.get(uid) == "waiting" and text.startswith("0x"):
        bot.send_message(uid, "⌛ Scanăm...")
        report = get_audit_data(text)
        if report:
            bot.send_message(uid, report, parse_mode="Markdown")
        else:
            bot.send_message(uid, "❌ Contractul nu a putut fi gasit pe nicio retea.")
        user_state[uid] = None

if __name__ == "__main__":
    bot.polling(none_stop=True)
