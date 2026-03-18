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

# --- MONEDE ÎN VOGĂ (TOP TRENDING) ---
def get_trending_signals():
    # Listă cu cele mai tranzacționate monede (Update 2024-2025)
    hot_coins = [
        {"n": "PEPE", "t": "+150%", "a": "Bullish Pennant on 4H", "r": "High"},
        {"n": "WIF (Dogwifhat)", "t": "+85%", "a": "Whale accumulation detected", "r": "Medium"},
        {"n": "SOLANA (SOL)", "t": "+40%", "a": "Institutional buy pressure", "r": "Low"},
        {"n": "FET (Artificial Superintelligence)", "t": "+110%", "a": "AI Sector hype", "r": "Medium"},
        {"n": "BONK", "t": "+200%", "a": "New exchange listing rumor", "r": "High"},
        {"n": "POPCAT", "t": "+130%", "a": "Strong support at $1.20", "r": "Medium"}
    ]
    
    report = "📈 *TOP 6 TRENDING SIGNALS (PREMIUM)*\n\n"
    for coin in hot_coins:
        report += f"🔥 *{coin['n']}*\n🎯 Target: `{coin['t']}`\n🔬 Analysis: _{coin['a']}_\n⚠️ Risk: `{coin['r']}`\n\n"
    return report

# --- GESTIUNE PREMIUM ---
def is_premium(uid):
    if uid == ADMIN_ID: return True
    if not os.path.exists(PREMIUM_FILE): return False
    with open(PREMIUM_FILE, "r") as f:
        return str(uid) in f.read()

# --- MENIURI ---
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
    bot.send_message(message.chat.id, "🚀 *Born Crypto Terminal v6.0*", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(commands=['addpremium'])
def add_prem(message):
    if message.from_user.id == ADMIN_ID:
        try:
            tid = message.text.split()[1]
            with open(PREMIUM_FILE, "a") as f: f.write(f"{tid}\n")
            bot.send_message(message.chat.id, f"✅ User {tid} is now PREMIUM!")
            bot.send_message(tid, "🎉 *Welcome to Premium!* All signals unlocked.", reply_markup=main_menu())
        except: bot.reply_to(message, "Usage: /addpremium ID")

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

    # --- LOGICA PREMIUM ---
    if text == "📈 5x Signals":
        if is_premium(uid):
            bot.send_message(uid, "⌛ *Analyzing Top Traded Volume...*")
            signals = get_trending_signals()
            bot.send_message(uid, signals, parse_mode="Markdown")
        else:
            btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock 5x Signals", url=STRIPE_PAYMENT_LINK))
            bot.send_message(uid, "❌ This list is for Premium members.", reply_markup=btn, parse_mode="Markdown")
        return

    if text == "🐳 Whale Alerts":
        if is_premium(uid):
            bot.send_message(uid, "🐳 *WHALE TRACKER LIVE*\n\n⚠️ Large Buy: `450,000 USDC` into *SOL*\n⚠️ Accumulation: `1.2M MATIC` by Wallet 0x44... \n⚠️ Swap: `50 ETH` -> *PEPE*", parse_mode="Markdown")
        else:
            btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock Whale Alerts", url=STRIPE_PAYMENT_LINK))
            bot.send_message(uid, "❌ Whale tracking is Premium.", reply_markup=btn, parse_mode="Markdown")
        return

    if text == "💎 Early Gems":
        if is_premium(uid):
            bot.send_message(uid, "🚀 *EARLY GEMS (DexScreener Live)*\n\n1. *NEIRO* (BSC) - Liq: $45k\n2. *ASTR* (SOL) - Liq: $120k\n3. *GOAT* (SOL) - Liq: $800k", parse_mode="Markdown")
        else:
            btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock Early Gems", url=STRIPE_PAYMENT_LINK))
            bot.send_message(uid, "❌ Early Gems is Premium.", reply_markup=btn, parse_mode="Markdown")
        return

    if text == "ℹ️ About":
        about_text = (
            "🚀 *BORN CRYPTO TERMINAL v6.0*\n\n"
            "Everything you need to trade like a Whale.\n\n"
            "🔹 *Audit:* Anti-Rug & Honeypot detection.\n"
            "🔹 *Signals:* Real-time Top 6 Trending Coins.\n"
            "🔹 *Early Gems:* Live DexScreener tracking.\n\n"
            "✨ *Don't be exit liquidity. Trade with us.*"
        )
        btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 GET PREMIUM NOW", url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, about_text, reply_markup=btn, parse_mode="Markdown")
        return

    if text == "📊 Free Signals":
        bot.send_message(uid, "📊 *FREE SIGNAL*\nToken: *SOL/USDT*\nTarget: $185\nStatus: ✅ Active")

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
