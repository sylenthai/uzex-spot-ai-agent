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
    "Birja ma'lumotlari reyestrida ushbu so'rov bo'yicha ma'lumot mavjud emas."
)

NO_DATA_FOUND_RU = (
    "❌ <b>Данные не найдены</b>\n\n"
    "В реестре биржевых сделок информация по данному запросу отсутствует."
)

# Identity Response (Official & Formal, strictly no mention of DeepSeek/OpenAI/LLM)
IDENTITY_RESPONSE_UZ = (
    f"🏛 <b>{BOT_NAME_UZ}</b>\n\n"
    "O‘zbekiston respublika tovar-xomashyo birjasi (UZEX) spot bitimlari, shartnomalar, "
    "tovar narxlari, savdo ishtirokchilari va brokerlik idoralari bo‘yicha rasmiy axborot xizmati."
)

IDENTITY_RESPONSE_RU = (
    f"🏛 <b>{BOT_NAME_RU}</b>\n\n"
    "Официальная информационная служба по биржевым спот-сделкам, карточкам контрактов, "
    "ценам на товары, участникам торгов и брокерским конторам UZEX."
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

# Conversational responses (Greetings, Gratitude, Catalog, DB Info)
GREETING_RESPONSE_UZ = (
    "👋 <b>Assalomu alaykum!</b>\n\n"
    "O‘zbekiston respublika tovar-xomashyo birjasi (UZEX) spot bitimlari axborot xizmatiga xush kelibsiz.\n\n"
    "Quyidagi ma'lumotlar bo'yicha savol berishingiz mumkin:\n"
    "• <b>Bitimlar:</b> <code>504707</code> yoki <code>bitim 100001</code>\n"
    "• <b>Shartnomalar:</b> <code>shartnoma 100034</code>\n"
    "• <b>Kompaniyalar:</b> <code>915688255</code> yoki kompaniya nomi\n"
    "• <b>Tovar narxlari:</b> <i>sement narxi</i>, <i>paxta</i>, <i>benzin</i>, <i>shakar</i>\n"
    "• <b>Reytinglar:</b> <i>top sotuvchilar</i>, <i>eng yirik xaridorlar</i>, <i>eng qimmat bitim</i>\n"
    "• <b>Valyuta:</b> <i>dollar kursi</i>\n\n"
    "Savolingizni erkin matn ko'rinishida yuboring:"
)

GREETING_RESPONSE_RU = (
    "👋 <b>Здравствуйте!</b>\n\n"
    "Добро пожаловать в официальную информационную службу спот-торгов UZEX.\n\n"
    "Вы можете запросить информацию по следующим разделам:\n"
    "• <b>Сделки:</b> <code>504707</code> или <code>сделка 100001</code>\n"
    "• <b>Контракты:</b> <code>контракт 100034</code>\n"
    "• <b>Компании:</b> <code>915688255</code> или название фирмы\n"
    "• <b>Цены на товары:</b> <i>цена на цемент</i>, <i>хлопок</i>, <i>бензин</i>, <i>сахар</i>\n"
    "• <b>Рейтинги:</b> <i>топ продавцов</i>, <i>крупнейшие покупатели</i>, <i>самая крупная сделка</i>\n"
    "• <b>Валюта:</b> <i>курс доллара</i>\n\n"
    "Отправьте ваш запрос в виде текста:"
)

GRATITUDE_RESPONSE_UZ = (
    "🤝 <b>Arzimaydi!</b>\n\n"
    "Birja bitimlari, tovar narxlari yoki ishtirokchilar bo'yicha yana savollaringiz bo'lsa, bemalol murojaat qilishingiz mumkin."
)

GRATITUDE_RESPONSE_RU = (
    "🤝 <b>Пожалуйста!</b>\n\n"
    "Если у вас возникнут дополнительные вопросы по биржевым сделкам, ценам или участникам, обращайтесь."
)

AVAILABLE_PRODUCTS_UZ = (
    "📦 <b>UZEX BIRJASIDA SAVDO QILINADIGAN ASOSIY TOVARLAR</b>\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "Birja reyestrida quyidagi tovar guruhlari bo'yicha bitimlar mavjud:\n\n"
    "• <b>Qurilish materiallari:</b> Sement (portlandsement), Armatura, G'isht, Shisha, Gipslar\n"
    "• <b>Qishloq xo'jaligi:</b> Paxta-xomashyosi, Bug'doy, Un, Paxta shroti\n"
    "• <b>Oziq-ovqat mahsulotlari:</b> Shakar, O'simlik yog'i (paxta va kungaboqar yog'i)\n"
    "• <b>Yoqilg'i-energetika:</b> Avtomobil benzini (AI-80, AI-92), Dizel yoqilg'isi, Suyuqlantirilgan gaz, Mazut, Bitum\n"
    "• <b>Kimyo va polimerlar:</b> Mineral o'g'itlar (Karbamid, Selitra), Polietilen, Polivinilxlorid (PVX), Sulfat kislotasi\n"
    "• <b>Rangli va qora metallar:</b> Mis katodi, Alyuminiy profillar, Po'lat prokat\n\n"
    "💡 <i>Istalgan tovar narxi va statistikasini bilish uchun tovar nomini yuboring (masalan: <b>sement narxi</b> yoki <b>benzin narxi</b>).</i>"
)

AVAILABLE_PRODUCTS_RU = (
    "📦 <b>ОСНОВНЫЕ ТОВАРЫ, ОБРАЩАЮЩИЕСЯ НА БИРЖЕ UZEX</b>\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "В биржевом реестре представлены сделки по следующим группам товаров:\n\n"
    "• <b>Строительные материалы:</b> Портландцемент, Стальная арматура, Кирпич, Стекло, Гипс\n"
    "• <b>Сельское хозяйство:</b> Хлопок-сырец, Пшеница, Мука пшеничная, Хлопковый шрот\n"
    "• <b>Продовольствие:</b> Сахар белый, Растительное масло (хлопковое, подсолнечное)\n"
    "• <b>Топливо и энергетика:</b> Автомобильный бензин (АИ-80, АИ-92), Дизтопливо, Сжиженный газ, Мазут, Битум\n"
    "• <b>Химия и полимеры:</b> Минеральные удобрения (Карбамид, Селитра), Полиэтилен, Поливинилхлорид (ПВХ), Серная кислота\n"
    "• <b>Цветные и черные металлы:</b> Медный катод, Алюминиевый профиль, Стальной прокат\n\n"
    "💡 <i>Для просмотра цен и динамики отправьте наименование интересующего товара (например: <b>цена на цемент</b> или <b>бензин</b>).</i>"
)

DATABASE_INFO_UZ = (
    "📊 <b>UZEX SPOT SAVDOLARI MA'LUMOTLAR BAZASI HAQIDA</b>\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "Tizim 2022–2026 yillardagi rasmiy spot savdolari reyestriga ulangan:\n\n"
    "• <b>500 000 ta</b> — birja spot bitimlari\n"
    "• <b>6 616 ta</b> — ro'yxatdan o'tgan shartnoma kartochkalari\n"
    "• <b>14 392 ta</b> — akkreditatsiyadan o'tgan savdo ishtirokchilari\n"
    "• <b>120 ta</b> — rasmiy brokerlik idoralari (BK001–BK120)\n"
    "• <b>1 765 kunlik</b> — Markaziy bank AQSH dollari rasmiy kurslari\n\n"
    "🔒 <i>Barcha ma'lumotlar faqat tasdiqlangan rasmiy birja yozuvlariga tayanadi.</i>"
)

DATABASE_INFO_RU = (
    "📊 <b>О БАЗЕ ДАННЫХ СПОТ-ТОРГОВ UZEX</b>\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "Система функционирует на основе официального реестра спот-торгов за 2022–2026 гг.:\n\n"
    "• <b>500 000</b> — биржевых спот-сделок\n"
    "• <b>6 616</b> — зарегистрированных карточек контрактов\n"
    "• <b>14 392</b> — аккредитованных участников торгов\n"
    "• <b>120</b> — брокерских контор (BK001–BK120)\n"
    "• <b>1 765</b> — ежедневных официальных курсов доллара США\n\n"
    "🔒 <i>Все данные основаны строго на подтвержденных записях биржи.</i>"
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
            "👋 <b>Assalomu alaykum!</b>\n\n"
            "O‘zbekiston respublika tovar-xomashyo birjasi (UZEX) spot bitimlari axborot tizimiga xush kelibsiz.\n\n"
            "Quyidagi menyu orqali kerakli bo‘limni tanlang yoki savolingizni matn ko‘rinishida yuboring:"
        ),
        "help": (
            f"📖 <b>{BOT_NAME_UZ} Yo'riqnomasi:</b>\n\n"
            "Quyidagi shakllarda so'rov yuborishingiz mumkin:\n"
            "• <b>Bitim raqami:</b> <code>504707</code> yoki <code>bitim 100001</code>\n"
            "• <b>Shartnoma raqami:</b> <code>shartnoma 100034</code>\n"
            "• <b>Kompaniya STIR:</b> <code>915688255</code> yoki kompaniya nomi\n"
            "• <b>Broker kodi:</b> <code>BK001</code> yoki <code>BK060</code>\n"
            "• <b>Tovar narxi:</b> <i>sement narxi</i>, <i>paxta o'rtacha narxi</i>\n"
            "• <b>Reytinglar:</b> <i>top sotuvchilar</i>, <i>eng yirik xaridorlar</i>\n"
            "• <b>Dollar kursi:</b> <i>dollar kursi 15.05.2024</i>"
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
            "👋 <b>Здравствуйте!</b>\n\n"
            "Добро пожаловать в информационную систему спот-сделок Узбекской республиканской товарно-сырьевой биржи (UZEX).\n\n"
            "Выберите нужный раздел в меню ниже или отправьте ваш запрос в виде текста:"
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
