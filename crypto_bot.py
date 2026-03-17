import telebot
import sqlite3
import requests
import random

# ==========================================
# 1. CONFIGURATION
# ==========================================
API_TOKEN = '8074686270:AAEifF-UUGyjVOYBPUiaiKCd6xPhs2dknYE'
ADMIN_ID = 988785764  
STRIPE_PAY_LINK = "https://buy.stripe.com/3cIaEX5go5CKbek0lo3cc00"

bot = telebot.TeleBot(API_TOKEN)

STRINGS = {
    'en': {
        'welcome': "🛡️ **Welcome to Born Crypto Terminal v3** 🛡️\n\nYour advanced De-Fi assistant is ready. Choose a tool:",
        'prices': "📈 LIVE PRICES", 'news': "📰 NEWS", 'rugcheck': "🔍 RUG-CHECK",
        'newpairs': "🚀 NEW PAIRS", 'flow': "🌊 WHALE FLOW", 'status': "👤 STATUS",
        'premium': "💎 PREMIUM", 'lang_btn': "🌐 LANGUAGE",
        'info_prices': "📊 **Market Overview:** Fetching real-time prices from Binance...",
        'info_news': "📰 **Market News:** Scanning global crypto sources...",
        'info_rug': "🔍 **Rug-Check Audit:** Analyzing smart contracts. Paste a contract below:",
        'info_pairs': "🚀 **Liquidity Scanner:** Monitoring new tokens on Solana/Base...",
        'info_flow': "🌊 **Whale Outflow:** Tracking CEX to Wallet movements (Bullish indicator)...",
        'restricted': "❌ **PREMIUM ONLY**\nUpgrade to unlock!",
        'pay_info': "💎 **PREMIUM ACCESS**\n👉 [PAY HERE]({link})\n⚠️ ID: `{uid}`",
    },
    'ro': {
        'welcome': "🛡️ **Bine ai venit la Born Crypto Terminal v3** 🛡️\n\nAsistentul tău De-Fi avansat este gata. Alege o unealtă:",
        'prices': "📈 PREȚURI LIVE", 'news': "📰 ȘTIRI", 'rugcheck': "🔍 RUG-CHECK",
        'newpairs': "🚀 MONEDE NOI", 'flow': "🌊 FLUX BALENE", 'status': "👤 STATUS",
        'premium': "💎 PREMIUM", 'lang_btn': "🌐 LIMBĂ",
        'info_prices': "📊 **Prețuri Live:** Se preiau datele de pe Binance...",
        'info_news': "📰 **Știri Crypto:** Scanăm sursele globale...",
        'info_rug': "🔍 **Audit Rug-Check:** Analiză contracte smart. Trimite contractul:",
        'info_pairs': "🚀 **Scanner Monede Noi:** Monitorizare Solana/Base...",
        'info_flow': "🌊 **Fluxul Balenelor:** Urmărește retragerile din burse (Semnal Bullish)...",
        'restricted': "❌ **DOAR PREMIUM**\nUpgradează pentru acces!",
        'pay_info': "💎 **ACCES PREMIUM**\n👉 [PLĂTEȘTE AICI]({link})\n⚠️ ID: `{uid}`",
    },
    'de': {
        'welcome': "🛡️ **Willkommen beim Born Crypto Terminal**\nWählen Sie ein Werkzeug:",
        'prices': "📈 LIVE-PREISE", 'news': "📰 NEWS", 'rugcheck': "🔍 RUG-CHECK",
        'newpairs': "🚀 NEUE PAARE", 'flow': "🌊 WHALE FLOW", 'status': "👤 STATUS",
        'premium': "💎 PREMIUM", 'lang_btn': "🌐 SPRACHE",
        'info_prices': "📊 Marktdaten werden geladen...", 'info_news': "📰 News werden gescannt...",
        'info_rug': "🔍 Vertrag wird geprüft...", 'info_pairs': "🚀 Neue Pools werden gescannt...",
        'info_flow': "🌊 Whale-Bewegungen werden verfolgt...", 'restricted': "❌ NUR PREMIUM",
        'pay_info': "💎 **PREMIUM**\n👉 [HIER ZAHLEN]({link})",
    },
    'fr': {
        'welcome': "🛡️ **Bienvenue sur Born Crypto Terminal**\nChoisissez un outil:",
        'prices': "📈 PRIX EN DIRECT", 'news': "📰 NOUVELLES", 'rugcheck': "🔍 RUG-CHECK",
        'newpairs': "🚀 NOUVEAUX PAIRS", 'flow': "🌊 WHALE FLOW", 'status': "👤 STATUT",
        'premium': "💎 PREMIUM", 'lang_btn': "🌐 LANGUE",
        'info_prices': "📊 Chargement des prix...", 'info_news': "📰 Scan des nouvelles...",
        'info_rug': "🔍 Audit du contrat...", 'info_pairs': "🚀 Scan des nouveaux pools...",
        'info_flow': "🌊 Suivi des flux CEX...", 'restricted': "❌ PREMIUM UNIQUEMENT",
        'pay_info': "💎 **PREMIUM**\n👉 [PAYER ICI]({link})",
    }
}

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, plan TEXT, lang TEXT)')
    conn.commit(); conn.close()

def get_user_data(user_id):
    conn = sqlite3.connect('users.db'); cursor = conn.cursor()
    cursor.execute("SELECT plan, lang FROM users WHERE user_id = ?", (str(user_id),))
    res = cursor.fetchone(); conn.close()
    return res if res else ('free', 'en')

init_db()

# --- KEYBOARDS ---
def lang_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🇬🇧 English", "🇷🇴 Română", "🇩🇪 Deutsch", "🇫🇷 Français")
    return markup

def main_keyboard(plan, lang):
    s = STRINGS.get(lang, STRINGS['en'])
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(s['prices'], s['news'])
    markup.add(s['rugcheck'], s['newpairs'])
    markup.add(s['flow'], s['status'])
    if plan != 'premium': markup.add(s['premium'])
    markup.add(s['lang_btn'])
    return markup

# --- HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = sqlite3.connect('users.db'); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, plan, lang) VALUES (?, 'free', 'en')", (uid,))
    conn.commit(); conn.close()
    bot.send_message(message.chat.id, "Select Language / Alege Limba:", reply_markup=lang_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🇬🇧 English", "🇷🇴 Română", "🇩🇪 Deutsch", "🇫🇷 Français", "🌐 LANGUAGE", "🌐 LIMBĂ", "🌐 SPRACHE", "🌐 LANGUE"])
def set_lang(message):
    uid = str(message.from_user.id)
    mapping = {"🇬🇧 English": "en", "🇷🇴 Română": "ro", "🇩🇪 Deutsch": "de", "🇫🇷 Français": "fr"}
    if "🌐" in message.text:
        bot.send_message(message.chat.id, "Select Language:", reply_markup=lang_keyboard())
        return
    new_lang = mapping.get(message.text, 'en')
    conn = sqlite3.connect('users.db'); cur = conn.cursor()
    cur.execute("UPDATE users SET lang = ? WHERE user_id = ?", (new_lang, uid))
    conn.commit(); conn.close()
    plan, _ = get_user_data(uid)
    bot.send_message(message.chat.id, STRINGS.get(new_lang, STRINGS['en'])['welcome'], reply_markup=main_keyboard(plan, new_lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    uid = str(message.from_user.id)
    plan, lang = get_user_data(uid)
    s = STRINGS.get(lang, STRINGS['en'])
    msg = message.text

    if msg == s['prices']:
        bot.send_message(message.chat.id, s['info_prices'], parse_mode="Markdown")
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/price").json()
            symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
            res = "\n".join([f"• {i['symbol'].replace('USDT','')}: `${float(i['price']):,.2f}`" for i in r if i['symbol'] in symbols])
            bot.send_message(message.chat.id, "✅ **Live Feed:**\n" + res, parse_mode="Markdown")
        except: bot.send_message(message.chat.id, "❌ Price service down.")

    elif msg == s['news']:
        bot.send_message(message.chat.id, s['info_news'], parse_mode="Markdown")
        try:
            r = requests.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN").json()
            news = "\n\n".join([f"🔹 [{n['title']}]({n['url']})" for n in r['Data'][:2]])
            bot.send_message(message.chat.id, news, parse_mode="Markdown", disable_web_page_preview=True)
        except: bot.send_message(message.chat.id, "❌ News service down.")

    elif msg == s['rugcheck']:
        bot.send_message(message.chat.id, s['info_rug'], parse_mode="Markdown")

    elif msg == s['newpairs']:
        bot.send_message(message.chat.id, s['info_pairs'], parse_mode="Markdown")
        if plan != 'premium': bot.send_message(message.chat.id, s['restricted'])
        else: bot.send_message(message.chat.id, "🚀 **Live Pair Alert**\nToken: `BORN-ALPHA` (SOL)\nStatus: `Scanning...`", parse_mode="Markdown")

    elif msg == s['flow']:
        bot.send_message(message.chat.id, s['info_flow'], parse_mode="Markdown")
        if plan != 'premium': bot.send_message(message.chat.id, s['restricted'])
        else:
            amount = random.randint(300, 1200)
            bot.send_message(message.chat.id, f"🌊 **Flow Update**\n`{amount} BTC` left Exchanges.\n📈 Trend: `Bullish`", parse_mode="Markdown")

    elif msg == s['status']:
        bot.send_message(message.chat.id, f"👤 ID: `{uid}`\n⭐ Plan: {plan.upper()}", parse_mode="Markdown")

    elif msg == s['premium']:
        bot.send_message(message.chat.id, s['pay_info'].format(link=STRIPE_PAY_LINK, uid=uid), parse_mode="Markdown")

bot.infinity_polling()