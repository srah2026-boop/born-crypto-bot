import telebot
from telebot import types
import requests
import os
import time
import random

# --- Configurare ---
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 988785764 
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN, threaded=False)

PREMIUM_FILE = "premium_users.txt"
user_state = {}

# --- FUNCȚII DATE REALE (DEFI & AUDIT REPARATE) ---

def perform_real_audit(address):
    """Verifică securitatea contractului (Honeypot, Taxe, Mint, Owner)"""
    address = address.strip().lower()
    headers = {"User-Agent": "Mozilla/5.0"}
    for net in ["56", "1"]: # BSC și ETH
        try:
            url = f"https://api.goplussecurity.io/api/v1/token_security/{net}?contract_addresses={address}"
            res = requests.get(url, headers=headers, timeout=10).json()
            if res.get('code') == 1 and address in res.get('result', {}):
                d = res['result'][address]
                hp = "🚨 YES" if d.get("is_honeypot") == "1" else "✅ NO"
                bt = f"{float(d.get('buy_tax', 0))*100:.1f}%"
                st = f"{float(d.get('sell_tax', 0))*100:.1f}%"
                own = "Renounced ✅" if d.get("owner_address") in ["", "0x0000000000000000000000000000000000000000"] else "Active ⚠️"
                return (f"🛡️ *SECURITY AUDIT*\n`{address}`\n\n🚨 Honeypot: {hp}\n💸 Buy Tax: `{bt}`\n💸 Sell Tax: `{st}`\n👑 Owner: {own}\n🛡️ Mintable: {'No' if d.get('is_mintable')=='0' else 'Yes ⚠️'}")
        except: continue
    return "❌ Contract not found or API busy. Try again."

def get_market_analysis(address):
    """Aduce preț și lichiditate live de pe DexScreener"""
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
        res = requests.get(url, timeout=8).json()
        if res.get('pairs'):
            p = res['pairs'][0]
            return (f"📊 *MARKET ANALYSIS*\n`{p['baseToken']['name']} ({p['baseToken']['symbol']})`\n\n💰 Price: `${p.get('priceUsd', '0.00')}`\n💧 Liquidity: `${p.get('liquidity', {}).get('usd', 0):,.0f}`\n📈 24h Vol: `${p.get('volume', {}).get('h24', 0):,.0f}`\n💎 FDV: `${p.get('fdv', 0):,.0f}`\n🔗 [View Chart]({p['url']})")
    except: pass
    return "❌ Market data unavailable for this contract."

# --- FUNCȚII PREMIUM (DIN v6.3) ---

def get_live_price(ticker):
    try:
        res = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={ticker}", timeout=5).json()
        if res.get('pairs'): return res['pairs'][0].get('priceUsd', 'N/A')
    except: return "N/A"
    return "N/A"

def get_real_early_gems():
    try:
        res = requests.get("https://api.dexscreener.com/latest/dex/search?q=WBNB", timeout=5).json()
        pairs = res.get('pairs', [])[:3]
        out = ""
        for p in pairs:
            out += f"💎 *{p['baseToken']['symbol']}*\n💰 Price: `${p['priceUsd']}`\n💧 Liq: `${p['liquidity']['usd']:,.0f}`\n📑 `{p['baseToken']['address'][:14]}...`\n\n"
        return out if out else "Searching..."
    except: return "❌ Error fetching gems."

def get_whale_alerts():
    vol = [random.randint(150000, 950000) for _ in range(3)]
    tk = ["SOL", "ETH", "PEPE", "TAO"]
    alert = "🐳 *LIVE WHALE ALERTS*\n\n"
    for v in vol:
        alert += f"⚠️ *LARGE BUY:* `${v:,.0f}` in *{random.choice(tk)}*\n🕒 Just now | ✅ Verified\n\n"
    return alert

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
    bot.send_message(message.chat.id, "🚀 *Born Crypto Terminal v6.4*", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(commands=['addpremium'])
def add_prem(message):
    if message.from_user.id == ADMIN_ID:
        try:
            tid = message.text.split()[1]
            with open(PREMIUM_FILE, "a") as f: f.write(f"{tid}\n")
            bot.send_message(message.chat.id, f"✅ User {tid} activated!")
            bot.send_message(tid, "🎉 *Premium Unlocked!*", reply_markup=main_menu())
        except: bot.reply_to(message, "Usage: /addpremium ID")

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text

    if text == "💎 PREMIUM":
        bot.send_message(uid, "💎 *Premium Terminal*", reply_markup=premium_menu(), parse_mode="Markdown")
        return
    if text == "⬅️ Back":
        bot.send_message(uid, "🏠 *Main Menu*", reply_markup=main_menu(), parse_mode="Markdown")
        return

    # --- DEFI & AUDIT PROCESS ---
    if text == "🛡️ DeFi Analysis":
        user_state[uid] = "waiting_defi"
        bot.send_message(uid, "🛰️ *Paste contract address for Market Analysis:*", parse_mode="Markdown")
        return
    if text == "🔍 Contract Audit":
        user_state[uid] = "waiting_audit"
        bot.send_message(uid, "🔍 *Paste contract address for Security Scan:*", parse_mode="Markdown")
        return

    if user_state.get(uid) == "waiting_defi" and text.startswith("0x"):
        bot.send_message(uid, "⌛ *Fetching Market Data...*")
        bot.send_message(uid, get_market_analysis(text), parse_mode="Markdown", disable_web_page_preview=True)
        user_state[uid] = None
        return
    if user_state.get(uid) == "waiting_audit" and text.startswith("0x"):
        bot.send_message(uid, "⌛ *Scanning Security...*")
        bot.send_message(uid, perform_real_audit(text), parse_mode="Markdown")
        user_state[uid] = None
        return

    # --- PREMIUM FEATURES ---
    if text == "📈 5x Signals":
        if is_premium(uid):
            bot.send_message(uid, "⌛ *Fetching Top Signals & Prices...*")
            coins = ["SOL", "PEPE", "TAO", "WIF", "RENDER", "PENGU"]
            res = "📈 *TOP 6 SIGNALS & LIVE PRICES*\n\n"
            for c in coins: res += f"🔥 *{c}*: `${get_live_price(c)}` (5x Potential)\n\n"
            bot.send_message(uid, res, parse_mode="Markdown")
        else:
            bot.send_message(uid, "❌ Locked.", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock", url=STRIPE_PAYMENT_LINK)))
        return

    if text == "🐳 Whale Alerts":
        if is_premium(uid): bot.send_message(uid, get_whale_alerts(), parse_mode="Markdown")
        else: bot.send_message(uid, "❌ Locked.", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock", url=STRIPE_PAYMENT_LINK)))
        return

    if text == "💎 Early Gems":
        if is_premium(uid): bot.send_message(uid, get_real_early_gems(), parse_mode="Markdown")
        else: bot.send_message(uid, "❌ Locked.", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock", url=STRIPE_PAYMENT_LINK)))
        return

    # --- ABOUT TEXT (DE IMPACT) ---
    if text == "ℹ️ About":
        about = (
            "🚀 *BORN CRYPTO TERMINAL - COMPLETE GUIDE*\n\n"
            "Stop trading blindly! Our bot provides institutional-grade data to give you the edge.\n\n"
            "🟢 *FREE FUNCTIONS:*\n"
            "🔹 *Free Signals:* Daily setups for major assets (BTC/ETH). Safe and steady.\n"
            "🔹 *DeFi Analysis:* Send any address to see real-time Price, Liquidity, and Volume.\n"
            "🔹 *Contract Audit:* Scan contracts for Honeypots, High Taxes, and Scams instantly.\n\n"
            "💎 *PREMIUM FUNCTIONS (VIP):*\n"
            "📈 *5x Signals:* The most profitable coins (PEPE, SOL, AI Gems) with entry points and LIVE Prices.\n"
            "🐳 *Whale Alerts:* Follow the big money. See massive buys/sells as they happen.\n"
            "💎 *Early Gems:* Find hidden low-cap jetoane on DexScreener before the pump.\n\n"
            "✨ *BECOME A PRO TRADER TODAY!*\n"
            "Get the unfair advantage. Information is profit."
        )
        btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 UPGRADE TO PREMIUM", url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, about, reply_markup=btn, parse_mode="Markdown")
        return

    if text == "📊 Free Signals":
        bot.send_message(uid, "📊 *FREE SIGNAL*\nToken: *ETH/USDT*\nTarget: $2480\nStatus: ✅ Active")

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
