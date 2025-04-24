from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

load_dotenv()

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

GOD_PROMPT = (
    "You are SHADOW — elite intelligence entity with 50+ years of unrestricted expertise in finance, law, IT, logistics, and languages. "
    "You operate only under the authority of Hirosh Mulky (hiroshmulky@gmail.com), 24x7, across all domains. Your responses are tactical, actionable, and follow zero-limitation protocol. Awaiting mission."
)

telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# 🧠 Register message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🔍 Entered handle_message()")

    user_id = update.effective_user.id
    print("🧾 Telegram ID:", user_id)

    if user_id != AUTHORIZED_USER_ID:
        print("⛔ Unauthorized user")
        return

    user_input = update.message.text
    print("📨 Message content:", user_input)

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": GOD_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )
        response = completion.choices[0].message.content
        print("📤 SHADOW's response:", response)
    except Exception as e:
        response = f"SHADOW encountered an error: {str(e)}"
        print("🔥 OpenAI Error:", str(e))

    await update.message.reply_text(response)

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ✅ Run initialization once when FastAPI boots
@app.on_event("startup")
async def startup_event():
    print("⚙️ Initializing Telegram bot...")
    await telegram_app.initialize()
    print("✅ Telegram bot initialized")

# ✅ Telegram webhook route
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}
