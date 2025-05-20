from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import ccxt
import pandas as pd
import numpy as np

# your bot token, don't leak it bro
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# hookin' up to binance API
exchange = ccxt.binance({
    'rateLimit': 1200,
    'options': {'adjustForTimeDifference': True},
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
})

# just keepin' track of user langs
user_language = {}

# grab crypto chart data real quick
def get_crypto_data(symbol, timeframe='1h', limit=50):
    data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

# basic price check + trend vibes
def analyze_market(symbol, timeframe):
    df = get_crypto_data(symbol, timeframe)
    df['ma_short'] = df['close'].rolling(window=5).mean()  # short MA, fast moves
    df['ma_long'] = df['close'].rolling(window=20).mean()  # long MA, slow but steady
    
    if df['ma_short'].iloc[-1] > df['ma_long'].iloc[-1]:
        trend = "💹 Long (Market Up)"
    else:
        trend = "📉 Short (Market Down)"
    
    buy_price = df['low'].min()  # lookin’ for the bottom
    sell_price = df['high'].max()  # takin' profits at the top
    current_price = df['close'].iloc[-1]  # what's the price rn
    
    return trend, buy_price, sell_price, current_price

# let user pick their lingo
async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data='id')],
        [InlineKeyboardButton("🇬🇧 English", callback_data='en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please select your preferred language:\nSilakan pilih bahasa yang Anda inginkan:",
        reply_markup=reply_markup
    )

# save the user's language pick
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_language[query.from_user.id] = query.data
    
    if query.data == 'id':
        message = "✅ Bahasa telah diubah ke Bahasa Indonesia!"
    else:
        message = "✅ Language has been set to English!"
    
    await query.edit_message_text(text=message)

# when someone types /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_language.get(update.message.from_user.id, 'en')
    if lang == 'id':
        message = "🚀 Selamat datang di Bot Prediksi Crypto! 🚀\n\nKetik /help untuk melihat fitur bot ini. Yuk, gas trading crypto! 💰"
    else:
        message = "🚀 welcome to the crypto prediction bot! 🚀\n\nhit /help to see what this bot can do. let’s get that crypto bread! 💰"
    await update.message.reply_text(message)

# showin' what this bot is about
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_language.get(update.message.from_user.id, 'en')
    if lang == 'id':
        message = "ℹ️ Info Bot ℹ️\n\nBot ini ngebantu lo buat prediksi pasar crypto biar makin cuan! 💸\n Fitur utama: rekomendasi LONG/SHORT, harga beli/jual, dan analisis simpel.\n\n Bikin pakai: Magic Programming! 🔮"
    else:
        message = "ℹ️ bot info ℹ️\n\nthis bot helps ya figure out market vibes so u can get that sweet crypto gainz 💸\n main tools: long/short calls, buy/sell zones, and a quick analysis.\n\n powered by code wizardry 🔮"
    await update.message.reply_text(message)

# helpin' users not get lost
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_language.get(update.message.from_user.id, 'en')
    if lang == 'id':
        message = "🛠️ Bantuan 🛠️\n\nBerikut ini perintah yang bisa Anda gunakan:\n👉 /start - Buka pesan selamat datang\n👉 /info - Info tentang bot ini\n👉 /language - Untuk mengubah bahasa(Tersedia 2 Bahasa: ID & ENG)\n👉 /crypto [SYMBOL] [TIMEFRAME] - Prediksi crypto (contoh: /crypto BTC/USDT 1h)"
    else:
        message = "🛠️ help menu 🛠️\n\nuse these commands like a boss:\n👉 /start - welcome stuff\n👉 /info - what this bot does\n👉 /language - switch up your lingo\n👉 /crypto [SYMBOL] [TIMEFRAME] - check crypto (ex: /crypto BTC/USDT 1h)"
    await update.message.reply_text(message)

# main command for predictions
async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0].upper()  # like BTC/USDT
        timeframe = context.args[1] if len(context.args) > 1 else '1h'  # defaultin' to 1h
        trend, buy_price, sell_price, current_price = analyze_market(symbol, timeframe)
        
        lang = user_language.get(update.message.from_user.id, 'en')
        if lang == 'id':
            response = (
                f"📊 Prediksi Crypto 📊\n\n"
                f"💡 Crypto: {symbol}\n"
                f"⏱️ Timeframe: {timeframe}\n"
                f"📈 Rekomendasi: {trend}\n"
                f"📍 Harga Saat Ini: {current_price:.12f}\n"
                f"🛒 Harga Beli: {buy_price:.12f}\n"
                f"💰 Harga Jual: {sell_price:.12f}\n\n"
                f"🔥 Semoga cuan, Sobat Crypto! 🔥"
            )
        else:
            response = (
                f"📊 crypto breakdown 📊\n\n"
                f"💡 coin: {symbol}\n"
                f"⏱️ timeframe: {timeframe}\n"
                f"📈 move: {trend}\n"
                f"📍 current: {current_price:.12f}\n"
                f"🛒 buy zone: {buy_price:.12f}\n"
                f"💰 sell zone: {sell_price:.12f}\n\n"
                f"🔥 hope u print mad gains 🔥"
            )
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"❌ uh oh, something went wrong: {str(e)}")

# where the bot starts doing its thing
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("language", language))
    application.add_handler(CallbackQueryHandler(set_language))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("crypto", crypto))
    
    application.run_polling()

if __name__ == "__main__":
    main()
