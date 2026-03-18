import telebot
from telebot import types
import requests
import os
import time
import random

# --- Configurare ---
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 988785764 
ADMIN_USERNAME = "Bellamilly" 
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN, threaded=False)

PREMIUM_FILE = "premium_users.txt"
user_state = {}

# --- REPARARE FINALĂ AUDIT ---

def perform_real_audit(address):
    address = address.strip().lower()
    if not address.startswith("0x"):
        return "⚠️ *Format Invalid:* Momentan suportăm doar rețelele 0x (ETH, BSC, BASE, POLYGON)."
    
    headers = {"User-Agent": "Mozilla/5.0"}
    # Listă extinsă de rețele: 1 (ETH), 56 (BSC), 137 (Polygon), 8453 (Base), 42161 (Arbitrum)
    networks = ["1", "56", "8453", "137", "42161"]
    
    for net in networks:
        try:
            url = f"https://api.goplussecurity.io/api/v1/token_security/{net}?contract_addresses={address}"
            response = requests.get(url, headers=headers, timeout=5)
            res = response.json()
            
            # Verificăm dacă GoPlus a găsit contractul pe această rețea
            if res.get('code') == 1 and address in res.get('result', {}):
                d = res['result'][address]
                
                # Traducem datele în format vizual atractiv
                hp = "🚨 *DA*" if d.get("is_honeypot") == "1" else "✅ *NU*"
                bt = f"{float(d.get('buy_tax', 0))*100:.1f}%"
                st = f"{float(d.get('sell_tax', 0))*100:.1f}%"
                own = "Renounced ✅" if d.get("owner_address") in ["", "0x0000000000000000000000000000000000000000"] else "Active ⚠️"
                
                net_name = {"1": "Ethereum", "56": "BSC", "8453": "Base", "137": "Polygon", "42161": "Arbitrum"}.get(net)
                
                return (f"🛡️ *SECURITY AUDIT ({net_name})*\n`{address}`\n\n"
                        f"🚨 Honeypot: {hp}\n"
                        f"💸 Buy Tax: `{bt}` | Sell Tax: `{st}`\n"
                        f"👑 Owner: {own}\n"
                        f"🛡️ Mintable: {'No' if d.get('is_mintable')=='0' else 'Yes 🚨'}\n"
                        f"✅ Proxy: {'No' if d.get('is_proxy')=='0' else 'Yes ⚠️'}")
        except Exception:
            continue # Dacă nu găsește pe o rețea, trece la următoarea
            
    return "❌ *Contract Not Found:* Asigură-te că adresa este corectă și moneda este listată pe un DEX."

# --- FUNCȚIE DEFI (Care funcționează deja) ---

def get_market_analysis(address):
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
        res = requests.get(url, timeout=8).json()
        if res.get('pairs'):
            p = res['pairs'][0]
            return (f"📊 *MARKET ANALYSIS*\n`{p['baseToken']['name']} ({p['baseToken']['symbol']})`\n\n"
                    f"💰 Price: `${p.get('priceUsd', '0.00')}`\n"
                    f"💧 Liquidity: `${p.get('liquidity', {}).get('usd', 0):,.0f}`\n"
                    f"📈 24h Vol: `${p.get('volume', {}).get('h24', 0):,.0f}`\n"
                    f"🔗 [View Chart]({p['url']})")
    except: pass
    return "❌ *No Market Data available.*"

# --- LOGICA SISTEM ---

def is_premium(uid):
    if uid == ADMIN_ID: return True
    if not os.path.exists(PREMIUM_FILE): return False
    with open(PREMIUM_FILE, "r") as f: return str(uid) in f.read()

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Free Signals", "💎 PREMIUM")
    markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
    markup.row("🌐 Language", "ℹ️ About")
    return markup

def premium_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📈 5x Signals", "🐳 Whale Alerts")
    markup.row("💎 Early Gems", "⬅️ Back")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"🚀 *Born Crypto Terminal v7.1*\n🆔 *ID:* `{message.chat.id}`", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(commands=['addpremium'])
def add_prem(message):
    if message.from_user.id == ADMIN_ID:
        try:
            tid = message.text.split()[1]
            with open(PREMIUM_FILE, "a") as f: f.write(f"{tid}\n")
            bot.send_message(message.chat.id, f"✅ User {tid} activated!")
        except: pass

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text

    if text == "💎 PREMIUM":
        bot.send_message(uid, "💎 *Premium Access*", reply_markup=premium_menu(), parse_mode="Markdown")
        return
    if text == "⬅️ Back":
        bot.send_message(uid, "🏠 *Main Menu*", reply_markup=main_menu(), parse_mode="Markdown")
        return

    # --- INPUT ADRESE ---
    if text == "🛡️ DeFi Analysis":
        user_state[uid] = "waiting_defi"
        bot.send_message(uid, "🛰️ *Trimite adresa contractului:*", parse_mode="Markdown")
        return
    if text == "🔍 Contract Audit":
        user_state[uid] = "waiting_audit"
        bot.send_message(uid, "🔍 *Trimite adresa pentru scanare:*", parse_mode="Markdown")
        return

    if user_state.get(uid) == "waiting_defi" and text.startswith("0x"):
        bot.send_message(uid, get_market_analysis(text), parse_mode="Markdown", disable_web_page_preview=True)
        user_state[uid] = None
        return
    if user_state.get(uid) == "waiting_audit" and text.startswith("0x"):
        bot.send_message(uid, perform_real_audit(text), parse_mode="Markdown")
        user_state[uid] = None
        return

    if text == "ℹ️ About":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔓 GET PREMIUM NOW", url=STRIPE_PAYMENT_LINK))
        markup.add(types.InlineKeyboardButton("👨‍💻 CONTACT @Bellamilly", url=f"https://t.me/{ADMIN_USERNAME}"))
        bot.send_message(uid, "🚀 *BORN CRYPTO TERMINAL*\nProfessional DeFi suite.", reply_markup=markup, parse_mode="Markdown")

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
