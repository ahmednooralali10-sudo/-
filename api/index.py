import os
import aiohttp
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ⚠️ استبدل النص بين التنصيص بتوكن البوت الخاص بك من BotFather
TELEGRAM_BOT_TOKEN = "8698478340:AAFuFvx1weGntmz_1RlHYYhsy5NMfSFxkME"
VERCEL_API_URL = "https://apikey-py-xore.vercel.app/key/links"

app = Flask(__name__)

# إعداد تطبيق التليجرام
bot_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

async def bypass_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ يرجى كتابة الرابط بعد الأمر.\nمثال:\n`/pypas https://auth.platorelay.com/...`", 
            parse_mode="Markdown"
        )
        return

    target_url = context.args[0]
    await update.message.reply_text("⏳ جاري معالجة الرابط واستخراج المفتاح...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(VERCEL_API_URL, json={"url": target_url}, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    key = data.get("key") or data.get("raw_html") or "لم يتم العثور على مفتاح"
                    await update.message.reply_text(
                        f"✅ **تم استخراج المفتاح بنجاح:**\n\n`{key}`", 
                        parse_mode="Markdown"
                    )
                else:
                    await update.message.reply_text(f"❌ حدث خطأ في السيرفر: {response.status}")

    except Exception as e:
        await update.message.reply_text(
            f"❌ حدث خطأ أثناء الاتصال بالـ API:\n`{str(e)}`", 
            parse_mode="Markdown"
        )

# إضافة الأمر للبوت
bot_app.add_handler(CommandHandler("pypas", bypass_command))

@app.route("/", methods=["GET"])
def home():
    return "Bot is running on Vercel!"

@app.route("/webhook", methods=["POST"])
async def webhook():
    """استقبال تحديثات تليجرام عبر Webhook"""
    if request.method == "POST":
        async with bot_app:
            update = Update.de_json(request.get_json(force=True), bot_app.bot)
            await bot_app.process_update(update)
        return "ok", 200
    return "bad request", 400
