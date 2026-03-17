import telebot
from telebot import types
import requests
import os
import json
import time
import threading
from datetime import datetime

# --- Configurare ---
TOKEN = os.environ.get("TOKEN")
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"
bot = telebot.TeleBot(TOKEN, threaded=False)

user_state = {}
user_lang = {}

# --- FUNCTIE MARKETING (TRIMITE MESAJ DUPA 2 MINUTE) ---
def send_marketing_followup(chat_id, lang):
    time.sleep(120)  # Așteaptă 2 minute
    if lang == 'ro':
        text = "🚀 *Vrei semnale crypto mai bune?*\n\nTreci la Premium pentru:\n✅ Alerte balene în timp real\n✅ Early Gems (proiecte noi)\n✅ Semnale 5x-10x"
        btn_text = "💎 Devino Premium"
    else:
        text = "🚀 *Want better crypto signals?*\n\nUpgrade to Premium for:\n✅ Real-time Whale Alerts\n✅ Early Gems\n✅ 5x-10x Signals"
        btn_text = "💎 Go Premium"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=btn_text, url=STRIPE_PAYMENT_LINK))
    try:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
    except:
        pass

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
                report["hp"] = "DA 🚨" if str(data.get("is_honeypot")) == "1" else "NU ✅"
                report["tax"] = f"{float(data.get('buy_tax', 0))*100:.1f}% / {float(data.get('sell_tax', 0))*100:.1f}%"
                report["ow"] = "Renounced ✅" if data.get("owner_address") in ["0x0000000000000000000000000000000000000000", ""] else "Active ⚠️"
                break
        except: continue
    return report

# --- MENIURI ---
def show_main(message):
    lang = user_lang.get(message.chat.id, 'ro')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == 'ro':
        markup.row("📊 Semnale Free", "💎 PREMIUM")
        markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
        markup.row("🌐 Limbă")
    else:
        markup.row("📊 Free Signals", "💎 PREMIUM")
        markup.row("🛡️ DeFi Analysis", "🔍 Contract Audit")
        markup.row("🌐 Language")
    bot.send_message(message.chat.id, "🏠 *Meniu*" if lang == 'ro' else "🏠 *Main Menu*", reply_markup=markup, parse_mode="Markdown")

# --- HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇷🇴 Română")
    bot.send_message(message.chat.id, "🚀 *Born Crypto Bot v3.0*", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(message):
    uid = message.chat.id
    text = message.text
    lang = user_lang.get(uid, 'ro')

    if text == "🇬🇧 English": user_lang[uid] = 'en'; show_main(message); return
    if text == "🇷🇴 Română": user_lang[uid] = 'ro'; show_main(message); return

    if user_state.get(uid) == "waiting":
        if text.startswith("0x") and len(text) > 30:
            bot.send_message(uid, "⌛ Scanăm...")
            data = get_security_data(text)
            res = (f"🛡️ *RAPORT:*\n`{text[:15]}...`\n\n💰 Preț: `{data['price']}`\n💧 Liquidity: `{data['liq']}`\n🚨 Honeypot: {data['hp']}\n💸 Taxe: {data['tax']}\n👑 Owner: {data['ow']}")
            bot.send_message(uid, res, parse_mode="Markdown")
        user_state[uid] = None
        return

    if "🛡️" in text or "🔍" in text:
        user_state[uid] = "waiting"
        bot.send_message(uid, "🛰️ Trimite adresa:")
    
    elif "📊" in text:
        bot.send_message(uid, "📈 *Semnale Gratuite:*\n\nBTC Entry: 64,500\nETH Entry: 3,450\n\n_Următorul semnal în 4 ore._")
        # Pornim cronometrul de 2 minute pentru marketing
        threading.Thread(target=send_marketing_followup, args=(uid, lang)).start()

    elif "💎 PREMIUM" in text:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📈 5x Signals", "🐳 Whale Alerts")
        markup.row("💎 Early Gems", "⬅️ Înapoi")
        bot.send_message(uid, "💎 *Meniu Premium*", reply_markup=markup, parse_mode="Markdown")

    elif text in ["📈 5x Signals", "🐳 Whale Alerts", "💎 Early Gems"]:
        btn_txt = "🔓 Deblochează" if lang == 'ro' else "🔓 Unlock"
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(btn_txt, url=STRIPE_PAYMENT_LINK))
        bot.send_message(uid, "❌ Funcție disponibilă doar în abonamentul Premium.", reply_markup=markup, parse_mode="Markdown")

    elif "⬅️" in text:
        show_main(message)
    elif "🌐" in text:
        start(message)

if __name__ == "__main__":
    bot.polling(none_stop=True)
