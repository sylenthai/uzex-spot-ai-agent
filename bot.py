"""
UZEX Spot Savdolari AI Agenti — Telegram Bot
Production-grade Telegram Bot built with python-telegram-bot (v22).
Features interactive state management, inline drill-down navigation,
strict zero-hallucination guardrail, and DeepSeek LLM integration with model secrecy.
"""

import os
import sys
import asyncio
import logging
from typing import Optional, Dict

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.constants import ParseMode, ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from config import (
    TELEGRAM_BOT_TOKEN,
    MESSAGES,
    BOT_NAME_UZ,
    BOT_NAME_RU,
    IDENTITY_RESPONSE_UZ,
    IDENTITY_RESPONSE_RU
)
from engine import database
from engine.router import route_query
from engine import llm_agent

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("uzex_bot")

# In-memory user state tracking (per user session)
USER_STATES: Dict[int, str] = {}

def get_main_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Returns the persistent main menu reply keyboard."""
    msg = MESSAGES.get(lang, MESSAGES["uz"])
    keyboard = [
        [KeyboardButton(msg["btn_deal"]), KeyboardButton(msg["btn_contract"])],
        [KeyboardButton(msg["btn_company"]), KeyboardButton(msg["btn_product"])],
        [KeyboardButton(msg["btn_stats"]), KeyboardButton(msg["btn_usd"])],
        [KeyboardButton(msg["btn_lang"])]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_lang_inline_keyboard() -> InlineKeyboardMarkup:
    """Returns inline buttons for language selection."""
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="set_lang:uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang:ru")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_deal_inline_keyboard(deal_data: dict, lang: str = "uz") -> Optional[InlineKeyboardMarkup]:
    """Generates drill-down inline buttons for a deal."""
    if not deal_data:
        return None
    buttons = []
    c_num = deal_data.get("contract_number")
    s_inn = deal_data.get("seller_inn")
    b_inn = deal_data.get("buyer_inn")

    row1 = []
    if c_num:
        c_label = f"📄 Shartnoma №{c_num}" if lang == "uz" else f"📄 Контракт №{c_num}"
        row1.append(InlineKeyboardButton(c_label, callback_data=f"show_contract:{c_num}"))
    if row1:
        buttons.append(row1)

    row2 = []
    if s_inn:
        s_label = f"🏢 Sotuvchi ({s_inn})" if lang == "uz" else f"🏢 Продавец ({s_inn})"
        row2.append(InlineKeyboardButton(s_label, callback_data=f"show_company:{s_inn}"))
    if b_inn:
        b_label = f"🏢 Xaridor ({b_inn})" if lang == "uz" else f"🏢 Покупатель ({b_inn})"
        row2.append(InlineKeyboardButton(b_label, callback_data=f"show_company:{b_inn}"))
    if row2:
        buttons.append(row2)

    return InlineKeyboardMarkup(buttons) if buttons else None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command."""
    user = update.effective_user
    user_id = user.id if user else 0
    current_lang = database.get_user_lang(user_id)
    USER_STATES[user_id] = "idle"

    msg = MESSAGES.get(current_lang, MESSAGES["uz"])
    await update.message.reply_html(
        msg["welcome"],
        reply_markup=get_main_keyboard(current_lang)
    )

    lang_prompt = "🌐 Tilni tanlang / Выберите язык:"
    await update.message.reply_text(
        lang_prompt,
        reply_markup=get_lang_inline_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /help command."""
    user_id = update.effective_user.id if update.effective_user else 0
    lang = database.get_user_lang(user_id)
    msg = MESSAGES.get(lang, MESSAGES["uz"])
    await update.message.reply_html(
        msg["help"],
        reply_markup=get_main_keyboard(lang)
    )

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /lang command."""
    await update.message.reply_text(
        "🌐 Tilni tanlang / Выберите язык:",
        reply_markup=get_lang_inline_keyboard()
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /stats command."""
    user_id = update.effective_user.id if update.effective_user else 0
    lang = database.get_user_lang(user_id)
    res = route_query("umumiy birja statistikasi", forced_lang=lang)
    await update.message.reply_html(
        res["response_text"],
        reply_markup=get_main_keyboard(lang)
    )

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles inline button clicks."""
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = update.effective_user.id if update.effective_user else 0
    current_lang = database.get_user_lang(user_id)

    if data.startswith("set_lang:"):
        new_lang = data.split(":")[1]
        database.set_user_lang(user_id, new_lang)
        ack_text = "✅ Til o'zbekchaga o'zgartirildi." if new_lang == "uz" else "✅ Язык переключен на русский."
        await query.edit_message_text(ack_text)
        msg = MESSAGES.get(new_lang, MESSAGES["uz"])
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg["welcome"],
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_keyboard(new_lang)
        )

    elif data.startswith("show_contract:"):
        c_num = data.split(":")[1]
        res = route_query(f"shartnoma {c_num}", forced_lang=current_lang)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=res["response_text"],
            parse_mode=ParseMode.HTML
        )

    elif data.startswith("show_company:"):
        inn = data.split(":")[1]
        res = route_query(inn, forced_lang=current_lang)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=res["response_text"],
            parse_mode=ParseMode.HTML
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles free text questions and menu button taps with state management."""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user_id = update.effective_user.id if update.effective_user else 0
    lang = database.get_user_lang(user_id)
    msg = MESSAGES.get(lang, MESSAGES["uz"])
    state = USER_STATES.get(user_id, "idle")

    # 1. State Machine Triggers for Main Menu Buttons
    if text in [MESSAGES["uz"]["btn_deal"], MESSAGES["ru"]["btn_deal"]]:
        USER_STATES[user_id] = "wait_deal"
        await update.message.reply_html(msg["ask_deal_id"])
        return
    elif text in [MESSAGES["uz"]["btn_contract"], MESSAGES["ru"]["btn_contract"]]:
        USER_STATES[user_id] = "wait_contract"
        await update.message.reply_html(msg["ask_contract_id"])
        return
    elif text in [MESSAGES["uz"]["btn_company"], MESSAGES["ru"]["btn_company"]]:
        USER_STATES[user_id] = "wait_company"
        await update.message.reply_html(msg["ask_stir"])
        return
    elif text in [MESSAGES["uz"]["btn_product"], MESSAGES["ru"]["btn_product"]]:
        USER_STATES[user_id] = "wait_product"
        await update.message.reply_html(msg["ask_product"])
        return
    elif text in [MESSAGES["uz"]["btn_usd"], MESSAGES["ru"]["btn_usd"]]:
        res = route_query("dollar kursi", forced_lang=lang)
        await update.message.reply_html(res["response_text"])
        return
    elif text in [MESSAGES["uz"]["btn_stats"], MESSAGES["ru"]["btn_stats"]]:
        res = route_query("umumiy statistika", forced_lang=lang)
        await update.message.reply_html(res["response_text"])
        return
    elif text in [MESSAGES["uz"]["btn_lang"], MESSAGES["ru"]["btn_lang"]]:
        await update.message.reply_text(
            "🌐 Tilni tanlang / Выберите язык:",
            reply_markup=get_lang_inline_keyboard()
        )
        return

    # 2. State-driven Query Enrichment
    enriched_query = text
    if state == "wait_deal":
        if text.isdigit() and len(text) == 6:
            enriched_query = f"bitim {text}"
    elif state == "wait_contract":
        if text.isdigit():
            enriched_query = f"shartnoma {text}"
    elif state == "wait_company":
        if text.isdigit() and len(text) == 9:
            enriched_query = text
    elif state == "wait_product":
        enriched_query = f"{text} narxi"

    # Reset state to idle after receiving input
    USER_STATES[user_id] = "idle"

    # 3. Processing Query
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    res = route_query(enriched_query, forced_lang=lang)

    # Attach drill-down buttons if deal
    inline_kb = None
    if res["intent"] == "deal_lookup" and res.get("raw_data"):
        inline_kb = get_deal_inline_keyboard(res["raw_data"], lang)

    await update.message.reply_html(
        res["response_text"],
        reply_markup=inline_kb
    )

def run_cli_interactive():
    """Interactive console simulation mode when running without a bot token."""
    print("=" * 65)
    print(f"🏛 {BOT_NAME_UZ.upper()} / {BOT_NAME_RU.upper()}")
    print("Production-Grade Spot Exchange AI Agent (RU + UZ)")
    print("Database: 500,000 deals, 6,616 contracts, 14,392 participants")
    print("Zero-Hallucination Disqualification Shield: ACTIVE")
    print("Type your query or 'exit' to quit. (Type 'uz' or 'ru' to switch lang)")
    print("=" * 65)

    cur_lang = "uz"
    while True:
        try:
            prompt = f"[{cur_lang.upper()}] Savol / Вопрос > "
            user_input = input(prompt).strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Chiqildi. / Выход.")
                break
            if user_input.lower() in ["uz", "o'zbek"]:
                cur_lang = "uz"
                print("Til o'zbekchaga o'zgartirildi.")
                continue
            if user_input.lower() in ["ru", "русский"]:
                cur_lang = "ru"
                print("Язык переключен на русский.")
                continue

            res = route_query(user_input, forced_lang=cur_lang)
            print("-" * 65)
            print(f"INTENT: {res['intent']} | FOUND: {res['found']} | LANG: {res['language']}")
            print("-" * 65)
            clean_text = (
                res["response_text"]
                .replace("<b>", "")
                .replace("</b>", "")
                .replace("<i>", "")
                .replace("</i>", "")
                .replace("<code>", "")
                .replace("</code>", "")
            )
            print(clean_text)
            print("=" * 65)
        except (KeyboardInterrupt, EOFError):
            print("\nChiqildi.")
            break

def main():
    """Starts the bot or runs in console test mode if no token."""
    token = TELEGRAM_BOT_TOKEN.strip()
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("\n" + "=" * 65)
        print("[INFO] TELEGRAM_BOT_TOKEN is not configured in .env.")
        print("[INFO] To connect a live Telegram bot, add your token to .env:")
        print("       TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ")
        print("[INFO] Starting interactive CLI test mode...")
        print("=" * 65 + "\n")
        run_cli_interactive()
        return

    print(f"Starting {BOT_NAME_UZ} with token: {token[:8]}...****")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"{BOT_NAME_UZ} is successfully running! Waiting for updates...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
