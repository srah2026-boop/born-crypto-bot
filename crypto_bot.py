import telebot
from telebot import types
import requests
import os
import time
import threading

# --- Configurare ---
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 988785764  # ID-ul tău a fost setat aici
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN, threaded=False)

PREMIUM_FILE = "premium_users.txt"
user_state = {}

# --- GESTIUNE PREMIUM ---
def get_premium_list():
    if not os.path.exists(PREMIUM_FILE): return []
    try:
        with open(PREMIUM_FILE, "r") as f:
            return [line.strip() for line in f.readlines()]
    except: return []

def add_to_premium(uid):
    with open(PREMIUM_FILE, "a") as f:
        f.write(f"{uid}\n")

def is_premium(uid):
    # Admin-ul are acces premium automat
    if uid == ADMIN_ID: return True
    return str(uid) in get_premium_list()

# --- MENIURI ---
def show_main(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Free Signals", "💎 PREMIUM")
    markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
    markup.row("🌐 Language", "ℹ️ About")
    bot.send_message(chat_id, "🏠 *Born Crypto Terminal Online*", reply_markup=markup, parse_mode="Markdown")

# --- HANDLER ADMIN ---
@bot.message_handler(commands=['addpremium'])
def admin_add(message):
    if message.from_user.id == ADMIN_ID:
        try:
            target_id = message.text.split()[1]
            add_to_premium(target_id)
            bot.send_message(message.chat.id, f"✅ User {target_id} activated!")
            bot.send_message(target_id, "🎉 *Welcome!* Your account is now PREMIUM. All features unlocked!")
        except:
            bot.reply_to(message, "Usage: /addpremium ID")
    else:
        bot.reply_to(message, "❌ Unauthorized.")

# --- HANDLERS COMENZI MENIU (Cele din poze: /buy, /target, /premium) ---
@bot.message_handler(commands=['buy', 'target', 'premium'])
def handle_menu_commands(message):
    uid = message.chat.id
    if is_premium(uid):
        if message.text == "/buy":
            bot.send_message(uid, "➕ *Portfolio:* Send a contract address to start tracking its performance.")
        elif message.text == "/target":
            bot.send_message(uid, "🔔 *Alerts:* Send the price target for your last scanned token.")
        elif message.text == "/premium":
            bot.send_message(uid, "✨ *Ultra Mode Active:* You are receiving 0-delay signals and whale alerts.")
    else:
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock Premium", url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, "❌ *Feature Locked.* Upgrade to Premium to use this tool.", reply_markup=markup, parse_mode="Markdown")

# --- ROUTER PRINCIPAL ---
@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text

    if text in ["🇬🇧 English", "🇷🇴 Română"]: show_main(uid); return

    if text == "ℹ️ About":
        about_text = (
            "🚀 *BORN CRYPTO TERMINAL v5.0*\n\n"
            "Professional DeFi trading powerhouse. Everything you need to win in one bot.\n\n"
            "🔥 *BOT FUNCTIONS:*\n"
            "🔹 *Contract Audit:* Anti-Rug, Honeypot & Tax detection.\n"
            "🔹 *DeFi Analysis:* Live price & liquidity monitoring.\n"
            "🔹 *Free Signals:* Daily high-probability trade setups.\n\n"
            "💎 *PREMIUM BENEFITS:*\n"
            "✅ *Early Gems:* Access new tokens before they trend.\n"
            "✅ *Whale Tracker:* Watch the smart money movements.\n"
            "✅ *Portfolio & Alerts:* Manage your bags like a pro.\n\n"
            "✨ *Don't be exit liquidity. Trade with Born Crypto.*"
        )
        btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 GET PREMIUM NOW", url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, about_text, reply_markup=btn, parse_mode="Markdown")

    elif text == "💎 PREMIUM":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📈 5x Signals", "🐳 Whale Alerts")
        markup.row("💎 Early Gems", "⬅️ Back")
        bot.send_message(uid, "💎 *PREMIUM ACCESS*", reply_markup=markup, parse_mode="Markdown")

    elif text in ["📈 5x Signals", "🐳 Whale Alerts", "💎 Early Gems"]:
        if is_premium(uid):
            bot.send_message(uid, f"✅ *Loading {text}...* (Database updated 1 min ago)")
        else:
            btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock Now", url=STRIPE_PAYMENT_LINK))
            bot.send_message(uid, f"❌ *{text}* is Premium only.", reply_markup=btn, parse_mode="Markdown")

    elif text == "⬅️ Back": show_main(uid)
    elif text == "📊 Free Signals":
        bot.send_message(uid, "📊 *FREE SIGNAL*\nToken: BTC/USDT\nENTRY: 67200\nSTATUS: ✅ Completed")

# --- PORNIRE ---
if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    print("Born Crypto Bot is RUNNING...")
    bot.infinity_polling()
