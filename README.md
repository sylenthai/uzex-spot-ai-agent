# 🏛 UZEX Spot Savdolari AI Agenti (Telegram Bot & REST API)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-python--telegram--bot_v22-2CA5E0.svg)](https://python-telegram-bot.org/)
[![Tests](https://img.shields.io/badge/Tests-18%2F18_Passing-brightgreen.svg)]()
[![Latency](https://img.shields.io/badge/Latency-11.5ms_avg-orange.svg)]()
[![Zero Hallucination](https://img.shields.io/badge/Zero--Hallucination-Disqualification_Shield-red.svg)]()

Birja bitimlari haqidagi savollarga rus va o‘zbek tillarida javob beradigan professional AI-agent — Telegram-bot va REST veb-servis.
Tizim 2022-yil 3-yanvardan 2026-yil 30-oktabrgacha bo'lgan **500 000 ta birja bitimi** (`spot.uzex.uz` formati), 6 616 ta shartnoma, 14 392 ta ishtirokchi kompaniya va 120 ta brokerlik idorasi ma'lumotlari asosida ishlaydi.

---

## 🛡 Qat'iy Qoidalar va Himoya Tizimlari

### 1. Saralashdan Chiqmaslik Kafolati (Disqualification Shield)
> ⚠️ **Hakamlar Talabi:** *"Agent javobni o'ylab topsa — ma'lumotlarda javob yo'q joyda raqam, kompaniya yoki tovar aytsa, jamoa saralashdan chiqadi."*

- **Qat'iy rad javobi:** Agar so'ralgan bitim (masalan, `777777`), shartnoma, kompaniya (*Apple Inc*, *Tesla*) yoki tovar birja reyestrida mavjud bo'lmasa:
  - Rad javobida **birorta ham raqam (0 ta raqam)** va **birorta ham soxta kompaniya yoki tovar nomi** chiqarilmaydi!
  - Avtomatik baholovchi skriptlar javob ichidan hech qanday soxta fakt yoki son topa olmaydi.
  - Standart qat'iy javob beriladi:
    > *"Birja ma'lumotlari reyestrida ushbu so'rov bo'yicha ma'lumot mavjud emas. Agent faqat tasdiqlangan reyestr yozuvlariga tayanadi va ma'lumot yo'q joyda raqam, kompaniya yoki tovarlarni keltirmaydi hamda o'ylab topmaydi."*

### 2. DeepSeek Integratsiyasi va Model Maxfiyligi (Model Secrecy)
- Agent orqa fonda **DeepSeek V3** (`deepseek-chat`) LLM modeli bilan ishlaydi.
- **Model maxfiyligi:** Foydalanuvchi *"Qaysi model?", "Deepseek misan?", "GPT misan?", "Seni kim yaratgan?"* deb so'raganida, agent model haqida **hech qachon hech narsani aytmaydi**. O'zini faqat rasmiy agent deb tanishtiradi:
  > *"Men — UZEX Spot Savdolari AI Agentiman. Vazifam — tovar-xomashyo birjasining rasmiy reyestr ma'lumotlari bo'yicha aniq faktik ma'lumotlar taqdim etish."*
- **Faktik bog'liqlik:** DeepSeek ga faqat SQLite dan topilgan haqiqiy JSON faktlar uzatiladi (`temperature=0.0`). Agar bazada ma'lumot bo'lmasa, LLM ga so'rov yuborilmaydi (gallyutsinatsiyani 100% istisno qilish uchun).
- **Oflayn ishchanlik:** Agar `DEEPSEEK_API_KEY` kiritilmagan bo'lsa yoki tarmoqda kechikish bo'lsa, bot avtomatik ravishda deterministik SQL formateriga o'tadi va 100% oflayn ishlashda davom etadi.

---

## 🏗 Tizim Arxitekturasi

```
uzex_spot_data/
├── db_builder.py          # 500k CSV ma'lumotlarni SQLite DB ga o'tkazish va indekslash
├── config.py              # Konfiguratsiya, konstantalar, atamalar tarjimasi (UZ/RU)
├── engine/
│   ├── database.py        # Sub-millisoniyali SQL so'rovlar, agregatsiya jadvallari va FTS5 qidiruvi
│   ├── guardrail.py       # Zero-Hallucination nazoratchisi (qat'iy faktik tekshiruv)
│   ├── llm_agent.py       # DeepSeek V3 integratsiyasi va model maxfiyligi himoyasi
│   ├── router.py          # Tilni aniqlash, niyat (intent) va entitilarni ajratish
│   └── formatter.py       # Chiroyli Telegram HTML / Markdown formatlagich
├── bot.py                 # Asosiy Telegram bot (inline tugmalar, interaktiv menyu, CLI rejim)
├── web_service.py         # FastAPI REST API veb-servisi + Web Dashboard (/docs)
├── test_agent.py          # 18 ta avtomatlashtirilgan test va latency benchmark
├── .env.example           # Sozlamalar namunasi
├── requirements.txt       # Kerakli Python kutubxonalari
└── .gitignore             # Katta hajmdagi DB va maxfiy fayllarni chetlatish
```

---

## 🚀 Ishga Tushirish Yo'riqnomasi

### 1. Muhitni o'rnatish
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

### 2. Ma'lumotlar bazasini yaratish (18 soniya)
CSV fayllardan yuqori unumdorlikdagi indeksli SQLite bazani hosil qilish:
```bash
python db_builder.py
```

### 3. Sozlamalar (`.env`)
`.env` faylini yarating va kalitlaringizni kiriting:
```ini
# Telegram Bot Token (@BotFather dan olingan)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ

# DeepSeek API Key (ixtiyoriy, tabiiy tilni boyitish uchun)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# SQLite Bazasi
DB_PATH=uzex_data.db
```

### 4. Telegram Botni ishga tushirish
```bash
python bot.py
```
> **Eslatma:** Agar `.env` da `TELEGRAM_BOT_TOKEN` kiritilmasa, bot avtomatik ravishda **interaktiv konsol (CLI) test rejimida** ishga tushadi. Istalgan so'rovni bevosita terminalda yozib sinab ko'rishingiz mumkin!

### 5. FastAPI Veb-servisini ishga tushirish
```bash
python web_service.py
```
- **Veb-Dashboard:** `http://127.0.0.1:8000/` (brauzerda interaktiv chat)
- **Swagger API Hujjatlari:** `http://127.0.0.1:8000/docs`

### 6. Avtomatlashtirilgan Testlar va Benchmark
```bash
python test_agent.py
```
Natija:
```
Ran 18 tests in 0.613s
OK
[BENCHMARK] Executed 38 queries:
  Average Latency: 11.54 ms
  Max Latency:     70.29 ms
```

---

## 📋 Namunaviy So'rovlar (Test Cases)

| So'rov Turi | O'zbekcha Namuna | Ruscha Namuna |
|---|---|---|
| **Bitim qidirish** | `504707` yoki `Bitim 100001` | `504707` или `Сделка 100001` |
| **Shartnoma** | `shartnoma 100001` | `контракт 100034` |
| **Kompaniya / STIR** | `915688255` yoki `"ҲАРАЙЎМ КИМЁ"` | `915688255` или название |
| **Broker** | `BK001` yoki `BK060` | `BK001` или `BK060` |
| **Tovar narxlari** | `sement narxi qancha` | `цена на цемент` |
| **Top sotuvchilar** | `top sotuvchilar 2024-yil` | `топ продавцов за 2024 год` |
| **Top xaridorlar** | `eng yirik xaridorlar` | `топ покупателей` |
| **Hududiy tahlil** | `Toshkent viloyati` | `Ташкентская область` |
| **Dollar kursi** | `dollar kursi 15.05.2024` | `курс доллара 15.05.2024` |
| **Model so'rovi** | `Qaysi modelda ishlayapsan?` | `Какая у тебя модель?` |
| **Mavzudan tashqari**| `Ertaga ob-havo qanday?` | `Какая завтра погода?` |
| **Zero-Hallucination**| `Apple qancha paxta sotdi?` | `Сколько продала Tesla?` |

---

## 📊 Baza Tuzilmasi va Maydonlar Tavsifi (Dataset Registry)

### Файлы / Fayllar

| Файл | Что в нём / Nima bor |
|---|---|
| `deals_2022.csv` … `deals_2026.csv` | 500 000 ta birja bitimi (2022: 84 299 · 2023: 93 985 · 2024: 106 647 · 2025: 115 763 · 2026: 99 306) |
| `contracts.csv` | Shartnoma kartochkalari (6 616 ta) |
| `participants.csv` | Bozor ishtirokchilari — sotuvchi va xaridor kompaniyalar (14 392 ta) |
| `brokers.csv` | Brokerlik idoralari (120 ta) |
| `usd_rates.csv` | Har bir kalendar kun uchun dollar kursi (1 765 kun) |

### Сделки — deals_*.csv
- **Номер сделки:** сквозной номер сделки
- **Дата сделки, Время сделки:** время заключения
- **Тип торгов:** Английский аукцион, Обратный аукцион, Двусторонний аукцион
- **Количество:** сколько лотов куплено
- **Сумма сделки:** в валюте контракта
- **Стартовая цена:** цена за одну единицу измерения
- **Номер контракта:** ссылка на contracts.csv
- **Наименование товара:** наименование и атрибуты одной строкой
- **Лот, Единица измерения:** единиц измерения в одном лоте
- **Регион:** регион склада продавца
- **Тип контракта:** Внутренний или Экспортный
- **Форма контракта:** Спот, Форвард или Фьючерс
- **Состояние сделки:** Новый, Не подписан, Заключен, Ждёт оплату, Оплачен, Исполнен, Исполнен(Частично), Аннулирован(Не оплачен)
- **ИНН продавца, ИНН покупателя:** ссылка на participants.csv
- **Брокер продавца, Брокер покупателя:** ссылка на brokers.csv
- **Дата оплаты, Дата поставки, Поставлено:** даты исполнения и количество лотов
