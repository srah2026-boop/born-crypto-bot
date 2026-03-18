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

# --- FUNCTII DATE REALE (DeFi & Audit) ---

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
                hp = "🚨 DA" if data.get("is_honeypot") == "1" else "✅ NU"
                buy_tax = f"{float(data.get('buy_tax', 0))*100:.1f}%"
                sell_tax = f"{float(data.get('sell_tax', 0))*100:.1f}%"
                owner = "Renounced ✅" if data.get("owner_address") in ["", "0x0000000000000000000000000000000000000000"] else "Active ⚠️"
                return (f"🛡️ *AUDIT REPORT*\n`{address}`\n\n🚨 Honeypot: {hp}\n💸 Buy Tax: `{buy_tax}`\n💸 Sell Tax: `{sell_tax}`\n👑 Owner: {owner}\n✅ Mint: {'No 🛡️' if data.get('is_mintable') == '0' else 'Yes 🚨'}")
        except: continue
    return "❌ Contract not found or network not supported."

def get_market_analysis(address):
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
        res = requests.get(url, timeout=8).json()
        if res.get('pairs'):
            p = res['pairs'][0]
            return (f"📊 *DEFI ANALYSIS*\n`{p['baseToken']['name']} ({p['baseToken']['symbol']})`\n\n💰 Price: `${p.get('priceUsd', '0.00')}`\n💧 Liquidity: `${p.get('liquidity', {}).get('usd', 0):,.0f}`\n📈 24h Vol: `${p.get('volume', {}).get('h24', 0):,.0f}`\n💎 FDV: `${p.get('fdv', 0):,.0f}`\n🔗 [View Chart]({p['url']})")
    except: pass
    return "❌ Market data not available for this contract."

# --- LOGICA GESTIUNE ---

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
    bot.send_message(message.chat.id, "🚀 *Born Crypto Terminal v6.2 Online*", reply_markup=main_menu(), parse_mode="Markdown")

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

    # --- REPARARE DEFI & AUDIT ---
    if text == "🛡️ DeFi Analysis":
        user_state[uid] = "waiting_defi"
        bot.send_message(uid, "🛰️ *Send contract address for Market Analysis:*", parse_mode="Markdown")
        return

    if text == "🔍 Contract Audit":
        user_state[uid] = "waiting_audit"
        bot.send_message(uid, "🔍 *Send contract address for Security Audit:*", parse_mode="Markdown")
        return

    if user_state.get(uid) == "waiting_defi" and text.startswith("0x"):
        bot.send_message(uid, "⌛ *Fetching Market Data...*")
        bot.send_message(uid, get_market_analysis(text), parse_mode="Markdown", disable_web_page_preview=True)
        user_state[uid] = None
        return

    if user_state.get(uid) == "waiting_audit" and text.startswith("0x"):
        bot.send_message(uid, "⌛ *Scanning Contract Security...*")
        bot.send_message(uid, perform_real_audit(text), parse_mode="Markdown")
        user_state[uid] = None
        return

    # --- TEXTUL ABOUT SOLID ȘI ATRACTIV ---
    if text == "ℹ️ About":
        about_text = (
            "🚀 *WELCOME TO BORN CRYPTO TERMINAL v6.2*\n"
            "The most advanced DeFi tool for smart traders. Stop being exit liquidity!\n\n"
            "🔥 *OUR MAIN FUNCTIONS:*\n\n"
            "📊 *Free Signals:* Daily market setups for major coins (BTC/ETH). High accuracy, zero cost.\n\n"
            "🛡️ *DeFi Analysis:* Send any contract address and receive instant data: Live Price, Liquidity, and Volume. Essential for tracking your bags.\n\n"
            "🔍 *Contract Audit:* Our security engine scans for Honeypots, Hidden Taxes, and Owner privileges. Stay safe from Rug-pulls!\n\n"
            "💎 *PREMIUM FEATURES (VIP):*\n"
            "📈 *5x Signals:* Exclusive access to the 'Top 6 Trending Coins' (PEPE, SOL, WIF, etc.) with entry points and 5x-10x potential.\n"
            "🐳 *Whale Alerts:* Real-time tracking of institutional wallets. Buy when the whales buy!\n"
            "💎 *Early Gems:* Sniper access to new tokens on DexScreener before they trend globally.\n\n"
            "✨ *Ready to trade like a Professional?*\n"
            "Don't wait for the pump—be there before it happens. Join our VIP community now!"
        )
        btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 UPGRADE TO PREMIUM", url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, about_text, reply_markup=btn, parse_mode="Markdown")
        return

    if text == "📈 5x Signals":
        if is_premium(uid):
            bot.send_message(uid, "📈 *TOP 6 TRENDING SIGNALS (PREMIUM)*\n1. PEPE\n2. WIF\n3. SOL\n4. FET\n5. BONK\n6. POPCAT", parse_mode="Markdown")
        else:
            bot.send_message(uid, "❌ This list is for Premium members.", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock Now", url=STRIPE_PAYMENT_LINK)))
        return

    if text == "📊 Free Signals":
        bot.send_message(uid, "📊 *FREE SIGNAL*\nToken: *SOL/USDT*\nTarget: $185\nStatus: ✅ Active")

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
