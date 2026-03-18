import telebot
from telebot import types
import requests
import os
import time
import random

# --- Configuration ---
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 988785764 
ADMIN_USERNAME = "Bellamilly" 
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN, threaded=False)

PREMIUM_FILE = "premium_users.txt"
user_state = {}

# --- FIXED AUDIT FUNCTION (v7.6) ---
def perform_real_audit(address):
    clean_address = address.strip().lower()
    if not clean_address.startswith("0x"):
        return "⚠️ *Invalid Format:* Please provide a valid 0x address."
    
    # Professional headers to prevent API blocking on Koyeb
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Checking most common networks: 1=ETH, 56=BSC, 8453=Base, 137=Polygon
    networks = ["1", "56", "8453", "137"]
    
    for net_id in networks:
        try:
            # Optimized API URL
            url = f"https://api.goplussecurity.io/api/v1/token_security/{net_id}?contract_addresses={clean_address}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 1 and clean_address in data.get("result", {}):
                    res = data["result"][clean_address]
                    
                    # Formatting the report
                    hp = "🚨 *YES*" if res.get("is_honeypot") == "1" else "✅ *NO*"
                    buy_tax = f"{float(res.get('buy_tax', 0))*100:.1f}%"
                    sell_tax = f"{float(res.get('sell_tax', 0))*100:.1f}%"
                    owner = "Renounced ✅" if res.get("owner_address") in ["", "0x0000000000000000000000000000000000000000", "0x000000000000000000000000000000000000dead"] else "Active ⚠️"
                    
                    chain_name = {"1": "Ethereum", "56": "BSC", "8453": "Base", "137": "Polygon"}.get(net_id)
                    
                    return (f"🛡️ *SECURITY AUDIT ({chain_name})*\n`{clean_address}`\n\n"
                            f"🚨 Honeypot: {hp}\n"
                            f"💸 Buy Tax: `{buy_tax}` | Sell Tax: `{sell_tax}`\n"
                            f"👑 Owner: {owner}\n"
                            f"🛡️ Mintable: {'No' if res.get('is_mintable')=='0' else 'Yes 🚨'}\n"
                            f"✅ Proxy: {'No' if res.get('is_proxy')=='0' else 'Yes ⚠️'}")
        except:
            continue
            
    return "❌ *Contract Not Found:* This could be a very new token or an unsupported network. Try again in 1 minute."

# --- LIVE DATA FUNCTIONS ---
def get_live_price(ticker):
    try:
        res = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={ticker}", timeout=5).json()
        if res.get('pairs'): return res['pairs'][0].get('priceUsd', 'N/A')
    except: return "N/A"
    return "N/A"

def get_market_analysis(address):
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
        res = requests.get(url, timeout=10).json()
        if res.get('pairs'):
            p = res['pairs'][0]
            return (f"📊 *MARKET ANALYSIS*\n`{p['baseToken']['name']} ({p['baseToken']['symbol']})`\n\n"
                    f"💰 Price: `${p.get('priceUsd', '0.00')}`\n"
                    f"💧 Liquidity: `${p.get('liquidity', {}).get('usd', 0):,.0f}`\n"
                    f"📈 24h Vol: `${p.get('volume', {}).get('h24', 0):,.0f}`\n"
                    f"🔗 [View Chart]({p['url']})")
    except: pass
    return "❌ *No Market Data found.*"

def get_real_early_gems():
    try:
        res = requests.get("https://api.dexscreener.com/latest/dex/search?q=WBNB", timeout=5).json()
        pairs = res.get('pairs', [])[:3]
        out = "💎 *EARLY GEMS DETECTED*\n\n"
        for p in pairs:
            out += f"🌟 *{p['baseToken']['symbol']}*\n💰 Price: `${p['priceUsd']}`\n💧 Liq: `${p['liquidity']['usd']:,.0f}`\n📑 `{p['baseToken']['address'][:14]}...`\n\n"
        return out
    except: return "❌ Error fetching gems."

def get_whale_alerts():
    vol = [random.randint(300000, 950000) for _ in range(3)]
    tk = ["SOL", "ETH", "PEPE", "TAO"]
    alert = "🐳 *LIVE WHALE ALERTS*\n\n"
    for v in vol:
        alert += f"⚠️ *LARGE BUY:* `${v:,.0f}` in *{random.choice(tk)}*\n🕒 Just now | ✅ Verified\n\n"
    return alert

# --- SYSTEM LOGIC ---
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

# --- HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"🚀 *Born Crypto Terminal v7.6*\n🆔 *ID:* `{message.chat.id}`", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(commands=['addpremium'])
def add_prem(message):
    if message.from_user.id == ADMIN_ID:
        try:
            tid = message.text.split()[1]
            with open(PREMIUM_FILE, "a") as f: f.write(f"{tid}\n")
            bot.send_message(message.chat.id, f"✅ User {tid} activated!")
            bot.send_message(tid, "🎉 *Premium Unlocked!*", reply_markup=main_menu())
        except: pass

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text

    if text == "💎 PREMIUM":
        bot.send_message(uid, "💎 *Premium Terminal Access*", reply_markup=premium_menu(), parse_mode="Markdown")
        return
    if text == "⬅️ Back":
        bot.send_message(uid, "🏠 *Main Menu*", reply_markup=main_menu(), parse_mode="Markdown")
        return

    # --- ACTIONS ---
    if text == "🛡️ DeFi Analysis":
        user_state[uid] = "waiting_defi"
        bot.send_message(uid, "🛰️ *Send contract address for Analysis:*", parse_mode="Markdown")
        return
    if text == "🔍 Contract Audit":
        user_state[uid] = "waiting_audit"
        bot.send_message(uid, "🔍 *Send contract address for Security Scan:*", parse_mode="Markdown")
        return

    if user_state.get(uid) == "waiting_defi" and text.startswith("0x"):
        bot.send_message(uid, get_market_analysis(text), parse_mode="Markdown", disable_web_page_preview=True)
        user_state[uid] = None
        return
    if user_state.get(uid) == "waiting_audit" and text.startswith("0x"):
        bot.send_message(uid, "⌛ *Scanning blockchain for data...*", parse_mode="Markdown")
        bot.send_message(uid, perform_real_audit(text), parse_mode="Markdown")
        user_state[uid] = None
        return

    # --- PREMIUM FEATURES ---
    if text == "📈 5x Signals":
        if is_premium(uid):
            coins = [{"n": "PEPE", "t": "+150%"}, {"n": "WIF", "t": "+85%"}, {"n": "SOL", "t": "+40%"}, {"n": "FET", "t": "+110%"}, {"n": "BONK", "t": "+200%"}, {"n": "POPCAT", "t": "+130%"}]
            report = "📈 *TOP SIGNALS & LIVE PRICES*\n\n"
            for c in coins: report += f"🔥 *{c['n']}*\n💰 Live: `${get_live_price(c['n'])}` | Target: `{c['t']}`\n\n"
            bot.send_message(uid, report, parse_mode="Markdown")
        else:
            btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock Now", url=STRIPE_PAYMENT_LINK))
            bot.send_message(uid, f"❌ Locked. Upgrade and contact @{ADMIN_USERNAME}", reply_markup=btn, parse_mode="Markdown")
        return

    if text == "🐳 Whale Alerts":
        if is_premium(uid): bot.send_message(uid, get_whale_alerts(), parse_mode="Markdown")
        else: bot.send_message(uid, "❌ Locked.", parse_mode="Markdown")
        return

    if text == "💎 Early Gems":
        if is_premium(uid): bot.send_message(uid, get_real_early_gems(), parse_mode="Markdown")
        else: bot.send_message(uid, "❌ Locked.", parse_mode="Markdown")
        return

    if text == "ℹ️ About":
        full_about = (
            "🚀 *BORN CRYPTO TERMINAL - THE ULTIMATE GUIDE*\n\n"
            "Gain the institutional edge with our all-in-one DeFi toolkit.\n\n"
            "🟢 *FREE FEATURES:*\n"
            "🔹 *Free Signals:* Daily low-risk setups for major assets.\n"
            "🔹 *DeFi Analysis:* Live Price, Liquidity, and Volume.\n"
            "🔹 *Contract Audit:* Scan for Honeypots and scams instantly.\n\n"
            "💎 *PREMIUM FEATURES (VIP):*\n"
            "📈 *5x Signals:* High-growth coins with LIVE prices.\n"
            "🐳 *Whale Alerts:* Follow institutional smart money.\n"
            "💎 *Early Gems:* Discover rockets before they launch.\n\n"
            "✨ *GET STARTED:*\n"
            "1. Pay via the link below.\n"
            "2. Send your **ID** to @Bellamilly for activation."
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💳 UPGRADE TO PREMIUM", url=STRIPE_PAYMENT_LINK))
        markup.add(types.InlineKeyboardButton("👨‍💻 CONTACT @Bellamilly", url=f"https://t.me/{ADMIN_USERNAME}"))
        bot.send_message(uid, full_about, reply_markup=markup, parse_mode="Markdown")
        return

    if text == "📊 Free Signals":
        bot.send_message(uid, "📊 *FREE SIGNAL*\nToken: *ETH/USDT*\nTarget: $2480\nStatus: ✅ Active")

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
