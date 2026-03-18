import telebot
from telebot import types
import requests
import os
import time
import threading

# --- Configurare ---
TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN, threaded=False)

user_state = {}

# --- FUNCTIE MARKETING (Mesaj automat dupa 2 minute) ---
def send_marketing_followup(chat_id):
    time.sleep(120) 
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="💎 UPGRADE TO PREMIUM", url=STRIPE_PAYMENT_LINK))
    try:
        bot.send_message(chat_id, "🚀 *Don't trade alone!*\nJoin our Premium members to get 10x Gems and real-time Whale Alerts.", reply_markup=markup, parse_mode="Markdown")
    except: pass

# --- MOTOR SCANARE ---
def get_security_data(address):
    address = address.strip().lower()
    headers = {"User-Agent": "Mozilla/5.0"}
    report = {"price": "N/A", "liq": "N/A", "hp": "N/A", "tax": "N/A", "ow": "N/A"}
    try:
        res = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}", timeout=8).json()
        if res.get('pairs'):
            p = res['pairs'][0]
            report["price"] = f"${p.get('priceUsd', '0.00')}"
            report["liq"] = f"${p.get('liquidity', {}).get('usd', 0):,.0f}"
    except: pass
    for net_id in ["56", "1"]:
        try:
            url = f"https://api.goplussecurity.io/api/v1/token_security/{net_id}?contract_addresses={address}"
            g_res = requests.get(url, headers=headers, timeout=10).json()
            if g_res.get('code') == 1 and address in g_res.get('result', {}):
                data = g_res['result'][address]
                report["hp"] = "NO ✅" if str(data.get("is_honeypot")) == "0" else "YES 🚨"
                report["tax"] = f"{float(data.get('buy_tax', 0))*100:.1f}% / {float(data.get('sell_tax', 0))*100:.1f}%"
                report["ow"] = "Renounced ✅" if data.get("owner_address") in ["0x0000000000000000000000000000000000000000", ""] else "Active ⚠️"
                break
        except: continue
    return report

# --- BUTOANELE DIN DREAPTA/STANGA (INLINE AUDIT) ---
def get_inline_audit_buttons(address):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_chart = types.InlineKeyboardButton("📊 Chart", url=f"https://dexscreener.com/search?q={address}")
    btn_buy = types.InlineKeyboardButton("🛒 Buy Token", url=f"https://pancakeswap.finance/swap?outputCurrency={address}")
    btn_alert = types.InlineKeyboardButton("🔔 Set Price Alert", callback_data="lock_premium")
    btn_add = types.InlineKeyboardButton("➕ Add to Portfolio", callback_data="lock_premium")
    btn_ultra = types.InlineKeyboardButton("✨ Show Ultra Benefits", callback_data="ultra_info")
    markup.add(btn_chart, btn_buy, btn_alert, btn_add)
    markup.row(btn_ultra)
    return markup

# --- MENIURI ---
def show_main(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Free Signals", "💎 PREMIUM")
    markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
    markup.row("🌐 Language", "ℹ️ About")
    bot.send_message(chat_id, "🏠 *Born Crypto Terminal Online*", reply_markup=markup, parse_mode="Markdown")

# --- HANDLERS CALLBACK (BUTOANE INLINE) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "lock_premium":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock Premium", url=STRIPE_PAYMENT_LINK))
        bot.send_message(call.message.chat.id, "⚠️ *Premium Feature*\nLive monitoring and portfolio tracking are only available for Premium members.", reply_markup=markup, parse_mode="Markdown")
    
    elif call.data == "ultra_info":
        ultra_text = (
            "✨ *ULTRA PREMIUM BENEFITS*\n\n"
            "🚀 *Instant Alerts:* Zero delay on market moves.\n"
            "🐳 *Whale Tracker:* Watch the big wallets in real-time.\n"
            "💎 *Early Access:* Sniper-level info on new launches.\n"
            "🛡️ *Auto-Audit:* Automatic safety check for every token you track."
        )
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("💎 GET ULTRA NOW", url=STRIPE_PAYMENT_LINK))
        bot.send_message(call.message.chat.id, ultra_text, reply_markup=markup, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

# --- HANDLERS MESAJE ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇷🇴 Română")
    bot.send_message(message.chat.id, "🚀 *Born Crypto Bot v4.5*", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text
    
    if text in ["🇬🇧 English", "🇷🇴 Română"]: show_main(uid); return

    if user_state.get(uid) == "waiting":
        if text.startswith("0x") and len(text) > 30:
            bot.send_message(uid, "⌛ *Scanning...*", parse_mode="Markdown")
            data = get_security_data(text)
            report = (f"🛡️ *SECURITY REPORT*\n`{text}`\n\n💰 Price: `{data['price']}`\n💧 Liq: `{data['liq']}`\n"
                      f"🚨 Honeypot: {data['hp']}\n💸 Tax: {data['tax']}\n👑 Owner: {data['ow']}")
            bot.send_message(uid, report, reply_markup=get_inline_audit_buttons(text), parse_mode="Markdown")
        user_state[uid] = None; return

    if "🛡️" in text or "🔍" in text:
        user_state[uid] = "waiting"
        bot.send_message(uid, "🛰️ *Paste Contract Address:*", parse_mode="Markdown")
    
    elif "📊" in text:
        bot.send_message(uid, "📊 *FREE SIGNAL*\nToken: BTC/USDT\nENTRY: 67200\nSTATUS: ✅ Active", parse_mode="Markdown")
        threading.Thread(target=send_marketing_followup, args=(uid,)).start()

    elif "💎 PREMIUM" in text:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📈 5x Signals", "🐳 Whale Alerts")
        markup.row("💎 Early Gems", "⬅️ Back")
        bot.send_message(uid, "💎 *PREMIUM TERMINAL*", reply_markup=markup, parse_mode="Markdown")

    elif "ℹ️ About" in text:
        about_text = (
            "🚀 *BORN CRYPTO TERMINAL v4.5*\n\n"
            "Your all-in-one DeFi powerhouse for smart trading. Stop guessing, start using professional data!\n\n"
            "🔥 *BOT FUNCTIONS:*\n"
            "🔹 *Contract Audit:* Scan for Honeypots, Rug-pulls, and High Taxes.\n"
            "🔹 *DeFi Analysis:* Real-time price and liquidity tracking.\n"
            "🔹 *Free Signals:* High-accuracy daily market setups.\n\n"
            "💎 *WHY UPGRADE TO PREMIUM?*\n"
            "The market moves fast. Premium members get the unfair advantage:\n"
            "✅ *Early Gems:* Be the first to buy new tokens before they trend.\n"
            "✅ *Whale Alerts:* Track institutional money movements live.\n"
            "✅ *5x-10x Signals:* Access our private, high-conviction alerts.\n\n"
            "✨ *Don't be the exit liquidity. Trade like a pro!*"
        )
        btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 UNLOCK PREMIUM", url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, about_text, reply_markup=btn, parse_mode="Markdown")

    elif text in ["📈 5x Signals", "🐳 Whale Alerts", "💎 Early Gems"]:
        btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔓 Unlock Now", url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, f"❌ *{text}* is Premium only.", reply_markup=btn, parse_mode="Markdown")

    elif "⬅️" in text or "Back" in text: show_main(uid)
    elif "🌐" in text: start(message)

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
