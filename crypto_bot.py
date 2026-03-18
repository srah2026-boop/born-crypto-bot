import telebot
from telebot import types
import requests
import os
import time

# --- Configurare ---
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 988785764 
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
    if uid == ADMIN_ID: return True
    return str(uid) in get_premium_list()

# --- FUNCTIE MENIU PRINCIPAL (FORȚAT 2x3) ---
def show_main(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    # Rand 1
    markup.row("📊 Free Signals", "💎 PREMIUM")
    # Rand 2
    markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
    # Rand 3
    markup.row("🌐 Language", "ℹ️ About")
    
    bot.send_message(chat_id, "🏠 *Main Menu*", reply_markup=markup, parse_mode="Markdown")

# --- FUNCTIE MENIU PREMIUM ---
def show_premium_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row("📈 5x Signals", "🐳 Whale Alerts")
    markup.row("💎 Early Gems", "⬅️ Back")
    bot.send_message(chat_id, "💎 *Premium Terminal Access*", reply_markup=markup, parse_mode="Markdown")

# --- HANDLER ADMIN ---
@bot.message_handler(commands=['addpremium'])
def admin_add(message):
    if message.from_user.id == ADMIN_ID:
        try:
            target_id = message.text.split()[1]
            add_to_premium(target_id)
            bot.send_message(message.chat.id, f"✅ User {target_id} activated!")
            bot.send_message(target_id, "🎉 *Welcome!* Your account is now PREMIUM.", reply_markup=get_main_menu())
        except:
            bot.reply_to(message, "Usage: /addpremium ID")

# --- HANDLERS COMENZI / ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    show_main(message.chat.id)

@bot.message_handler(commands=['buy', 'target', 'premium'])
def handle_commands(message):
    uid = message.chat.id
    if is_premium(uid):
        bot.send_message(uid, f"✅ Feature {message.text} unlocked. Process starting...")
    else:
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock Premium", url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, "❌ Locked. Upgrade required.", reply_markup=markup)

# --- ROUTER TEXT ---
@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text

    # Navigare Meniu
    if text == "💎 PREMIUM":
        show_premium_menu(uid)
        return

    if text == "⬅️ Back":
        show_main(uid)
        return

    if text == "ℹ️ About":
        about_text = (
            "🚀 *BORN CRYPTO TERMINAL v5.0*\n\n"
            "Your professional DeFi suite. High-accuracy data and real-time alerts.\n\n"
            "🔥 *FUNCTIONS:*\n"
            "🔹 *Audit:* Anti-Rug & Honeypot detection.\n"
            "🔹 *Signals:* Daily high-probability trades.\n"
            "🔹 *Analysis:* Live price & liquidity monitoring.\n\n"
            "💎 *PREMIUM BENEFITS:*\n"
            "✅ *Early Gems:* Access new tokens first.\n"
            "✅ *Whale Tracker:* Watch the smart money.\n"
            "✅ *Portfolio & Alerts:* Manage your bags like a pro.\n\n"
            "✨ *Don't be exit liquidity. Trade with Born Crypto.*"
        )
        btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 GET PREMIUM NOW", url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, about_text, reply_markup=btn, parse_mode="Markdown")
        return

    # Logica pentru audit/defi
    if text in ["🛡️ DeFi Analysis", "🔍 Contract Audit"]:
        user_state[uid] = "waiting"
        bot.send_message(uid, "🛰️ *Paste Contract Address:*", parse_mode="Markdown")
        return

    # Afisare semnale
    if text == "📊 Free Signals":
        bot.send_message(uid, "📊 *FREE SIGNAL*\nToken: BTC/USDT\nENTRY: 67200\nSTATUS: ✅ Completed")
        return

    # Logica Premium (Gems, Whale, 5x)
    if text in ["📈 5x Signals", "🐳 Whale Alerts", "💎 Early Gems"]:
        if is_premium(uid):
            bot.send_message(uid, f"✅ *Loading {text}...* (Updates every 4 hours)")
        else:
            btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock Now", url=STRIPE_PAYMENT_LINK))
            bot.send_message(uid, f"❌ *{text}* is Premium only.", reply_markup=btn, parse_mode="Markdown")
        return

    # Daca userul a trimis o adresa pentru scanare
    if user_state.get(uid) == "waiting" and text.startswith("0x"):
        bot.send_message(uid, f"⌛ *Scanning {text[:10]}...*")
        # Aici poti pune codul de audit de dinainte
        user_state[uid] = None
        return

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
