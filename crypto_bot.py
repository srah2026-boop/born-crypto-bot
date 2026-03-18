import telebot
from telebot import types
import requests
import os
import time
import random
import threading

# --- Configurare ---
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 988785764 
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN, threaded=False)

PREMIUM_FILE = "premium_users.txt"
user_state = {}

# --- FUNCTII DATE REALE ---

def perform_real_audit(address):
    address = address.strip().lower()
    headers = {"User-Agent": "Mozilla/5.0"}
    networks = ["56", "1"]
    for net in networks:
        try:
            url = f"https://api.goplussecurity.io/api/v1/token_security/{net}?contract_addresses={address}"
            res = requests.get(url, headers=headers, timeout=10).json()
            if res.get('code') == 1 and address in res.get('result', {}):
                data = res['result'][address]
                hp = "🚨 YES" if data.get("is_honeypot") == "1" else "✅ NO"
                buy_tax = f"{float(data.get('buy_tax', 0))*100:.1f}%"
                sell_tax = f"{float(data.get('sell_tax', 0))*100:.1f}%"
                owner = "Renounced ✅" if data.get("owner_address") in ["", "0x0000000000000000000000000000000000000000"] else "Active ⚠️"
                return (f"🛡️ *AUDIT REPORT*\n`{address}`\n\n🚨 Honeypot: {hp}\n💸 Buy Tax: `{buy_tax}`\n💸 Sell Tax: `{sell_tax}`\n👑 Owner: {owner}")
        except: continue
    return "❌ Contract not found."

def get_market_analysis(address):
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
        res = requests.get(url, timeout=8).json()
        if res.get('pairs'):
            p = res['pairs'][0]
            return (f"📊 *DEFI ANALYSIS*\n`{p['baseToken']['name']} ({p['baseToken']['symbol']})`\n\n💰 Price: `${p.get('priceUsd', '0')}`\n💧 Liquidity: `${p.get('liquidity', {}).get('usd', 0):,.0f}`\n📈 Volume: `${p.get('volume', {}).get('h24', 0):,.0f}`")
    except: pass
    return "❌ No data."

# --- PRO FUNCTIONS ---

def get_5x_signals_live():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/ethereum"
        res = requests.get(url, timeout=8).json()
        pairs = res.get("pairs", [])[:10]

        text = "📈 *5X SIGNALS ENGINE (PRO)*\n\n"

        for p in pairs:
            name = p['baseToken']['symbol']
            price = float(p.get("priceUsd", 0))
            liquidity = p.get("liquidity", {}).get("usd", 0)
            volume = p.get("volume", {}).get("h24", 0)
            fdv = p.get("fdv", 0)

            score = 0
            if volume > 500000: score += 2
            if liquidity > 200000: score += 2
            if fdv < 5000000: score += 2

            if score >= 5:
                status = "🔥 STRONG BUY"
            elif score >= 3:
                status = "⚡ MOMENTUM"
            else:
                status = "⚠️ RISKY"

            text += f"• {name}\n💰 ${price:.6f}\n📊 Score: {score}/6\n{status}\n\n"

        return text
    except:
        return "❌ Signals unavailable."

def get_whale_alerts():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/ethereum"
        res = requests.get(url, timeout=8).json()
        pairs = res.get("pairs", [])

        text = "🐳 *WHALE ALERTS PRO*\n\n"

        for p in pairs[:8]:
            vol = p.get("volume", {}).get("h24", 0)
            liquidity = p.get("liquidity", {}).get("usd", 0)
            name = p['baseToken']['symbol']

            if vol > 1000000 and liquidity > 300000:
                text += f"🚨 WHALE BUYING {name}\n💸 Volume: ${vol:,.0f}\n💧 Liquidity: ${liquidity:,.0f}\n\n"

        return text if text.strip() != "" else "No whale activity."
    except:
        return "❌ Whale data unavailable."

def get_early_gems():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/bsc"
        res = requests.get(url, timeout=8).json()
        pairs = res.get("pairs", [])

        text = "💎 *EARLY GEMS SCANNER (PRO)*\n\n"
        count = 0

        for p in pairs:
            liquidity = p.get("liquidity", {}).get("usd", 0)
            volume = p.get("volume", {}).get("h24", 0)
            fdv = p.get("fdv", 0)

            if liquidity < 150000 and volume > 50000 and fdv < 3000000:
                name = p['baseToken']['symbol']
                price = p.get("priceUsd", "0")
                text += f"💎 {name}\n💰 ${price}\n💧 ${liquidity:,.0f} | 📈 ${volume:,.0f}\n\n"
                count += 1
            if count >= 5:
                break

        return text if count > 0 else "No gems found."
    except:
        return "❌ Gems unavailable."

# --- PREMIUM USERS ---

def get_premium_users():
    if not os.path.exists(PREMIUM_FILE):
        return []
    with open(PREMIUM_FILE, "r") as f:
        return [int(x.strip()) for x in f.readlines() if x.strip().isdigit()]

last_sent = {"whales": set(), "gems": set(), "signals": set()}

def auto_alerts_loop():
    while True:
        try:
            users = get_premium_users()

            pairs = requests.get("https://api.dexscreener.com/latest/dex/pairs/ethereum", timeout=10).json().get("pairs", [])

            for p in pairs[:10]:
                name = p['baseToken']['symbol']
                vol = p.get("volume", {}).get("h24", 0)
                liquidity = p.get("liquidity", {}).get("usd", 0)
                fdv = p.get("fdv", 0)

                # Whale
                if vol > 1500000 and name not in last_sent["whales"]:
                    msg = f"🐳 *WHALE ALERT*\n\n{name}\nVolume: ${vol:,.0f}"
                    for u in users:
                        try: bot.send_message(u, msg, parse_mode="Markdown")
                        except: pass
                    last_sent["whales"].add(name)

                # Signal
                score = 0
                if vol > 500000: score += 2
                if liquidity > 200000: score += 2
                if fdv < 5000000: score += 2

                if score >= 5 and name not in last_sent["signals"]:
                    msg = f"📈 *5X SIGNAL*\n\n{name}\nScore: {score}/6"
                    for u in users:
                        try: bot.send_message(u, msg, parse_mode="Markdown")
                        except: pass
                    last_sent["signals"].add(name)

            time.sleep(60)

        except:
            time.sleep(60)

# --- LOGICA ---

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
    bot.send_message(message.chat.id, "🚀 *Born Crypto Terminal PRO Online*", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text

    if text == "💎 PREMIUM":
        bot.send_message(uid, "💎 Premium Access", reply_markup=premium_menu(), parse_mode="Markdown")
        return

    if text == "📈 5x Signals":
        if is_premium(uid):
            bot.send_message(uid, get_5x_signals_live(), parse_mode="Markdown")
        else:
            bot.send_message(uid, "🔒 Premium only.", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Upgrade", url=STRIPE_PAYMENT_LINK)))

    if text == "🐳 Whale Alerts":
        if is_premium(uid):
            bot.send_message(uid, get_whale_alerts(), parse_mode="Markdown")

    if text == "💎 Early Gems":
        if is_premium(uid):
            bot.send_message(uid, get_early_gems(), parse_mode="Markdown")

    if text == "📊 Free Signals":
        bot.send_message(uid, "📊 FREE SIGNAL\nSOL/USDT → Target $185")

# --- RUN ---

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)

    threading.Thread(target=auto_alerts_loop).start()

    bot.infinity_polling()
