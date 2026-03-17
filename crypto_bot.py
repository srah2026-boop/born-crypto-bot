import telebot
from telebot import types
import requests
import os

# Configurare Token din Koyeb
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# Dicționar complet cu descrieri detaliate pentru meniu
strings = {
    'en': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\n\nYour professional assistant for the crypto market. I provide real-time data, audit tools, and DeFi analysis.\n\nSelect your language:",
        'main_menu': "🏠 *Main Menu*\nChoose a service from the buttons below:",
        'free': "📊 Live Prices",
        'defi': "🛡️ DeFi Analysis",
        'audit': "🔍 Contract Audit",
        'premium': "💎 Premium Signals",
        'defi_info': "🛡️ *DeFi Analysis*\nUsed to check liquidity pools, TVL, and slippage on DEXs (Uniswap/Pancake). Helps you understand if a pool is healthy.",
        'audit_info': "🔍 *Smart Contract Audit*\nScans for 'honeypots', 'mint' functions, and liquidity locks to prevent rugpulls and scams.",
        'select_coin': "Enter coin symbol (e.g. BTC, ETH, SOL):",
        'price_msg': "🚀 *{0}* Live Price: `${1}`\nSource: Binance Live",
        'not_found': "Invalid symbol. Please use BTC or ETH.",
        'change_lang': "🌐 Language / Limba",
        'back': "⬅️ Back"
    },
    'ro': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\n\nAsistentul tău profesional pentru piața crypto. Ofer date live, unelte de audit și analiză DeFi.\n\nSelectează limba:",
        'main_menu': "🏠 *Meniu Principal*\nAlege un serviciu din butoanele de mai jos:",
        'free': "📊 Prețuri Live",
        'defi': "🛡️ Analiză DeFi",
        'audit': "🔍 Audit Contracte",
        'premium': "💎 Semnale Premium",
        'defi_info': "🛡️ *Analiză DeFi*\nVerifică bazinele de lichiditate, TVL și slippage pe DEX-uri. Te ajută să vezi dacă un proiect are lichiditate reală.",
        'audit_info': "🔍 *Audit Smart Contract*\nScanează după 'honeypot', funcții de 'mint' sau blocarea lichidității pentru a evita scam-urile.",
        'select_coin': "Introdu simbolul (ex: BTC, ETH, SOL):",
        'price_msg': "🚀 Preț Live *{0}*: `${1}`\nSursă: Binance Live",
        'not_found': "Simbol invalid. Folosește BTC sau ETH.",
        'change_lang': "🌐 Language / Limba",
        'back': "⬅️ Înapoi"
    },
    'de': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\n\nIhr Krypto-Assistent. Live-Daten, Audit-Tools und DeFi-Analyse.\n\nWählen Sie eine Sprache:",
        'main_menu': "🏠 *Hauptmenü*\nWählen Sie einen Dienst:",
        'free': "📊 Live-Preise",
        'defi': "🛡️ DeFi-Analyse",
        'audit': "🔍 Kontrakt-Audit",
        'premium': "💎 Premium-Signale",
        'defi_info': "🛡️ *DeFi-Analyse*\nPrüft Liquiditätspools und TVL auf DEXs.",
        'audit_info': "🔍 *Smart Contract Audit*\nScannt nach 'Honeypots' und Liquiditätssperren.",
        'select_coin': "Symbol eingeben (z.B. BTC):",
        'price_msg': "🚀 *{0}* Live-Preis: `${1}`\nQuelle: Binance",
        'not_found': "Ungültiges Symbol.",
        'change_lang': "🌐 Language / Limba",
        'back': "⬅️ Zurück"
    },
    'fr': {
        'start_msg': "🚀 *Born Crypto Bot v2.0*\n\nVotre assistant crypto. Données en direct, audit et analyse DeFi.\n\nChoisissez votre langue:",
        'main_menu': "🏠 *Menu Principal*\nChoisissez un service:",
        'free': "📊 Prix en Direct",
        'defi': "🛡️ Analyse DeFi",
        'audit': "🔍 Audit de Contrat",
        'premium': "💎 Signaux Premium",
        'defi_info': "🛡️ *Outil DeFi*\nVérifie la liquidité et le TVL sur les DEX.",
        'audit_info': "🔍 *Audit de Contrat*\nDétecte les 'honeypots' et les arnaques.",
        'select_coin': "Entrez le symbole (ex: BTC):",
        'price_msg': "🚀 Prix *{0}*: `${1}`\nSource: Binance",
        'not_found': "Symbole invalide.",
        'change_lang': "🌐 Language / Limba",
        'back': "⬅️ Retour"
    }
}

user_lang = {}

def get_binance_price(symbol):
    symbol = symbol.upper() + "USDT"
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        response = requests.get(url).json()
        price = float(response['price'])
        return f"{price:,.2f}" if price > 1 else f"{price:,.6f}"
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 English", "🇩🇪 Deutsch", "🇷🇴 Română", "🇫🇷 Français")
    bot.send_message(message.chat.id, strings['en']['start_msg'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["🇬🇧 English", "🇩🇪 Deutsch", "🇷🇴 Română", "🇫🇷 Français", "🌐 Language / Limba"])
def set_lang(message):
    if "English" in message.text: user_lang[message.chat.id] = 'en'
    elif "Deutsch" in message.text: user_lang[message.chat.id] = 'de'
    elif "Română" in message.text: user_lang[message.chat.id] = 'ro'
    elif "Français" in message.text: user_lang[message.chat.id] = 'fr'
    show_main_menu(message)

def show_main_menu(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(strings[lang]['free'], strings[lang]['defi'])
    markup.add(strings[lang]['audit'], strings[lang]['premium'])
    markup.add(strings[lang]['change_lang'])
    bot.send_message(message.chat.id, strings[lang]['main_menu'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(x in m.text for x in ["📊"]))
def free_mode(message):
    lang = user_lang.get(message.chat.id, 'en')
    bot.send_message(message.chat.id, strings[lang]['select_coin'])

@bot.message_handler(func=lambda m: any(x in m.
