"""
Configuration, Constants and Bilingual Dictionaries for UZEX AI Agent
Supports Uzbek (Latn) and Russian with professional exchange terminology.
Strict Zero-Hallucination and Model Secrecy guarantees.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Official Bot Identity
BOT_NAME_UZ = "UZEX Spot Savdolari AI Agenti"
BOT_NAME_RU = "AI-Агент Биржевых Торгов UZEX"
BOT_USERNAME = "@uzex_spot_ai_bot"

# Telegram Bot Token (from env or fallback)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# DeepSeek LLM API Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

# SQLite Database Path
DB_PATH = os.getenv("DB_PATH", "uzex_data.db")

# Strict Anti-Hallucination Refusal Message (NO DIGITS, NO COMPANY NAMES, NO COMMODITIES!)
NO_DATA_FOUND_UZ = (
    "❌ <b>Ma'lumot topilmadi</b>\n\n"
    "Birja ma'lumotlari reyestrida ushbu so'rov bo'yicha ma'lumot mavjud emas.\n\n"
    "⚠️ <i>Qat'iy qoida: Agent faqat tasdiqlangan reyestr yozuvlariga tayanadi va "
    "ma'lumot yo'q joyda raqam, kompaniya yoki tovarlarni keltirmaydi hamda o'ylab topmaydi.</i>"
)

NO_DATA_FOUND_RU = (
    "❌ <b>Данные не найдены</b>\n\n"
    "В реестре биржевых сделок информация по указанному запросу отсутствует.\n\n"
    "⚠️ <i>Строгое правило: Агент опирается исключительно на официальный реестр и "
    "категорически не указывает и не выдумывает цифры, компании или товары при отсутствии данных.</i>"
)

# Identity Response (STRICTLY NO MENTION OF DEEPSEEK, OPENAI, OR ANY LLM MODEL!)
IDENTITY_RESPONSE_UZ = (
    f"🏛 <b>Men — {BOT_NAME_UZ}man.</b>\n\n"
    "Mening vazifam — tovar-xomashyo birjasining rasmiy reyestr ma'lumotlari "
    "(bitimlar, shartnomalar, narxlar, ishtirokchilar va brokerlar) bo'yicha aniq faktik ma'lumotlar taqdim etish.\n\n"
    "🔒 <b>Xavfsizlik kafolati:</b> Men faqat tasdiqlangan birja bazasi bilan ishlayman va "
    "ma'lumot yo'q joyda hech qachon son yoki nomlarni o'ylab topmayman."
)

IDENTITY_RESPONSE_RU = (
    f"🏛 <b>Я — {BOT_NAME_RU}.</b>\n\n"
    "Моя задача — предоставлять достоверную аналитическую и справочную информацию "
    "по официальному реестру товарно-сырьевой биржи (сделки, контракты, цены, участники и брокеры).\n\n"
    "🔒 <b>Гарантия надежности:</b> Я опираюсь исключительно на верифицированную базу данных и "
    "строго не выдумываю цифры или наименования при их отсутствии."
)

# Out of scope Response
OUT_OF_SCOPE_UZ = (
    "ℹ️ <b>Mavzudan tashqari so'rov</b>\n\n"
    "Men faqat UZEX birja savdolari, shartnomalari, tovar narxlari va ishtirokchilari "
    "bo'yicha rasmiy ma'lumot beruvchi ixtisoslashgan agentman.\n"
    "Birjaga oid bo'lmagan umumiy mavzularda ma'lumot taqdim eta olmayman."
)

OUT_OF_SCOPE_RU = (
    "ℹ️ <b>Запрос вне биржевой тематики</b>\n\n"
    "Я являюсь специализированным агентом исключительно по биржевым торгам UZEX.\n"
    "По темам, не относящимся к биржевой деятельности, информация не предоставляется."
)

# Status Translations
DEAL_STATE_TRANSLATIONS = {
    "Новый": {
        "uz": "Yangi (oxirgi kun holatida)",
        "ru": "Новый (на конец выгрузки)"
    },
    "Не подписан": {
        "uz": "Imzolanmagan (kutish holatida)",
        "ru": "Не подписан сторонами"
    },
    "Заключен": {
        "uz": "Tuzilgan (to'lov muddati o'tmagan)",
        "ru": "Заключен (срок оплаты не истек)"
    },
    "Ждёт оплату": {
        "uz": "To'lov kutilmoqda (spot imzolangan)",
        "ru": "Ждёт оплату (спот подписан)"
    },
    "Оплачен": {
        "uz": "To'langan (yetkazib berish kutilmoqda)",
        "ru": "Оплачен (товар готовится к поставке)"
    },
    "Исполнен": {
        "uz": "To'liq bajarilgan (to'langan va yetkazilgan)",
        "ru": "Исполнен полностью"
    },
    "Исполнен(Частично)": {
        "uz": "Qisman bajarilgan",
        "ru": "Исполнен частично"
    },
    "Аннулирован(Не оплачен)": {
        "uz": "Bekor qilingan (muddatida to'lanmagan)",
        "ru": "Аннулирован (не оплачен в срок)"
    }
}

AUCTION_TYPE_TRANSLATIONS = {
    "Английский аукцион": {
        "uz": "Ingliz auksioni (narx ko'tarilishi)",
        "ru": "Английский аукцион (на повышение)"
    },
    "Обратный аукцион": {
        "uz": "Teskari auksion (narx pasayishi)",
        "ru": "Обратный аукцион (на понижение)"
    },
    "Двусторонний аукцион": {
        "uz": "Ikki tomonlama auksion",
        "ru": "Двусторонний аукцион"
    }
}

CONTRACT_TYPE_TRANSLATIONS = {
    "Внутренний": {"uz": "Ichki bozor", "ru": "Внутренний рынок"},
    "Экспортный": {"uz": "Eksport", "ru": "Экспортный"}
}

CONTRACT_FORM_TRANSLATIONS = {
    "Спот": {"uz": "Spot (darhol yetkazish)", "ru": "Спот"},
    "Форвард": {"uz": "Forvard", "ru": "Форвард"},
    "Фьючерс": {"uz": "Fyuchers", "ru": "Фьючерс"}
}

# UI Labels & Messages
MESSAGES = {
    "uz": {
        "welcome": (
            f"👋 <b>Assalomu alaykum!</b>\n\n"
            f"Men <b>{BOT_NAME_UZ}</b>man.\n"
            f"Mening bazamda 2022–2026 yillardagi <b>500 000 ta birja bitimi</b>, "
            f"6 616 ta shartnoma, 14 392 ta kompaniya va brokerlik idoralari mavjud.\n\n"
            f"📌 <b>Asosiy qoidam:</b> Men faqat aniq faktlarga tayanaman. Bazada yo'q ma'lumotni hech qachon o'ylab topmayman!\n\n"
            f"Savolingizni erkin matn ko'rinishida yuborishingiz yoki quyidagi menyudan foydalanishingiz mumkin:"
        ),
        "help": (
            f"📖 <b>{BOT_NAME_UZ} Yo'riqnomasi:</b>\n\n"
            f"Quyidagi shakllarda so'rov yuborishingiz mumkin:\n"
            f"• <b>Bitim raqami:</b> <code>504707</code> yoki <code>bitim 100001</code>\n"
            f"• <b>Shartnoma raqami:</b> <code>shartnoma 100034</code>\n"
            f"• <b>Kompaniya STIR:</b> <code>915688255</code> yoki kompaniya nomi\n"
            f"• <b>Broker kodi:</b> <code>BK001</code> yoki <code>BK060</code>\n"
            f"• <b>Tovar narxi:</b> <i>sement narxi</i>, <i>paxta o'rtacha narxi</i>\n"
            f"• <b>Reytinglar:</b> <i>top sotuvchilar</i>, <i>eng yirik xaridorlar</i>\n"
            f"• <b>Dollar kursi:</b> <i>dollar kursi 15.05.2024</i>"
        ),
        "btn_deal": "🔍 Bitim tekshirish",
        "btn_contract": "📄 Shartnoma",
        "btn_company": "🏢 Kompaniya / STIR",
        "btn_product": "📊 Tovar narxlari",
        "btn_stats": "📈 Birja statistikasi",
        "btn_usd": "💵 Dollar kursi",
        "btn_lang": "🌐 Tilni o'zgartirish",
        "ask_deal_id": "Iltimos, bitim raqamini kiriting (masalan: <code>504707</code>):",
        "ask_contract_id": "Iltimos, shartnoma raqamini kiriting (masalan: <code>100034</code>):",
        "ask_stir": "Kompaniyaning 9 xonali STIR raqamini yoki nomini kiriting:",
        "ask_product": "Tovar nomini kiriting (masalan: <i>sement</i>, <i>shakar</i>, <i>paxta</i>, <i>un</i>):",
        "ask_date": "Sanani KK.OO.YYYY formatida kiriting (masalan: <code>15.05.2024</code>):"
    },
    "ru": {
        "welcome": (
            f"👋 <b>Здравствуйте!</b>\n\n"
            f"Я <b>{BOT_NAME_RU}</b>.\n"
            f"В моей базе содержится <b>500 000 сделок</b> с 2022 по 2026 год, "
            f"6 616 контрактов, 14 392 компании и 120 брокерских контор.\n\n"
            f"📌 <b>Главное правило:</b> Я строго опираюсь только на факты реестра. "
            f"Если данных нет в базе, я никогда ничего не придумываю!\n\n"
            f"Вы можете задать вопрос в свободной форме или воспользоваться меню ниже:"
        ),
        "help": (
            f"📖 <b>Справка по {BOT_NAME_RU}:</b>\n\n"
            f"Вы можете отправить:\n"
            f"• <b>Номер сделки:</b> <code>504707</code> или <code>сделка 100001</code>\n"
            f"• <b>Номер контракта:</b> <code>контракт 100034</code>\n"
            f"• <b>ИНН компании:</b> <code>915688255</code> или название фирмы\n"
            f"• <b>Код брокера:</b> <code>BK001</code> или <code>BK060</code>\n"
            f"• <b>Цены на товары:</b> <i>цена на цемент</i>, <i>хлопок средняя цена</i>\n"
            f"• <b>Рейтинги:</b> <i>топ продавцов</i>, <i>топ покупателей</i>\n"
            f"• <b>Курс доллара:</b> <i>курс доллара 15.05.2024</i>"
        ),
        "btn_deal": "🔍 Поиск сделки",
        "btn_contract": "📄 Контракт",
        "btn_company": "🏢 Компания / ИНН",
        "btn_product": "📊 Цены на товары",
        "btn_stats": "📈 Статистика биржи",
        "btn_usd": "💵 Курс доллара",
        "btn_lang": "🌐 Сменить язык",
        "ask_deal_id": "Пожалуйста, введите номер сделки (например: <code>504707</code>):",
        "ask_contract_id": "Пожалуйста, введите номер контракта (например: <code>100034</code>):",
        "ask_stir": "Введите 9-значный ИНН компании или её название:",
        "ask_product": "Введите наименование товара (например: <i>цемент</i>, <i>сахар</i>, <i>хлопок</i>, <i>мука</i>):",
        "ask_date": "Введите дату в формате ДД.ММ.ГГГГ (например: <code>15.05.2024</code>):"
    }
}
