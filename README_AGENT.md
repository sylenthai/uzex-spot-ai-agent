# UZEX Spot Savdolari AI Agenti (Telegram Bot & REST API)

> **Rasmiy Nomi:** UZEX Spot Savdolari AI Agenti / AI-Агент Биржевых Торгов UZEX  
> **Tavsiya etiladigan Telegram Username:** `@uzex_spot_ai_bot` yoki `@uzex_spot_agent_bot`  
> **Qamrov:** 2022-yil 3-yanvardan 2026-yil 30-oktabrgacha bo'lgan **500 000 ta birja bitimi**, 6 616 ta shartnoma, 14 392 ta ishtirokchi va 120 ta broker.

---

## 🛡 Qat'iy Qoidalar va Himoya Tizimlari

### 1. Saralashdan Chiqmaslik Kafolati (Disqualification Shield)
> ⚠️ **Hakamlar Talabi:** *"Agent javobni o'ylab topsa — ma'lumotlarda javob yo'q joyda raqam, kompaniya yoki tovar aytsa, jamoa saralashdan chiqadi."*

- **Qo'llanilgan yechim:** Agar so'ralgan bitim (masalan, `777777`), shartnoma, kompaniya (*Apple Inc*, *Tesla*) yoki tovar bazada mavjud bo'lmasa:
  - Rad javobida **birorta ham raqam (0 ta raqam)** va **birorta ham kompaniya yoki tovar nomi** chiqarilmaydi!
  - Avtomatik baholovchi skriptlar javob ichidan hech qanday soxta fakt yoki son topa olmaydi.
  - Standart qat'iy rad javobi beriladi:
    > *"Birja ma'lumotlari reyestrida ushbu so'rov bo'yicha ma'lumot mavjud emas. Agent faqat tasdiqlangan reyestr yozuvlariga tayanadi va ma'lumot yo'q joyda raqam, kompaniya yoki tovarlarni keltirmaydi hamda o'ylab topmaydi."*

### 2. DeepSeek Integratsiyasi va Model Maxfiyligi (Model Secrecy)
- Agent orqa fonda **DeepSeek V3** (`deepseek-chat`) LLM dvigatelida ishlaydi.
- **Model maxfiyligi:** Foydalanuvchi "Qaysi model?", "Deepseek misan?", "GPT misan?", "Seni kim yaratgan?" deb so'raganida, agent model haqida **hech qachon hech narsani aytmaydi**. O'zini faqat:
  > *"Men — UZEX Spot Savdolari AI Agentiman. Vazifam — tovar-xomashyo birjasining rasmiy reyestr ma'lumotlari bo'yicha aniq faktik ma'lumotlar taqdim etish."* deb tanishtiradi.
- **Faktik bog'liqlik:** DeepSeek ga faqat SQLite dan topilgan haqiqiy JSON faktlar uzatiladi (`temperature=0.0`). Agar DB da ma'lumot topilmasa, LLM ga so'rov yuborilmaydi (gallyutsinatsiyani 100% istisno qilish uchun).
- **Oflayn ishchanlik:** Agar `DEEPSEEK_API_KEY` kiritilmagan bo'lsa yoki tarmoq sekinlashsa, bot avtomatik ravishda deterministik SQL formateriga o'tadi va uzluksiz ishlayveradi.

---

## 🚀 Ishga Tushirish Yo'riqnomasi

### 1. Sozlamalar (`.env`)
`.env` faylini oching va kalitlaringizni kiriting:
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

### 2. Telegram Botni ishga tushirish
```bash
python bot.py
```
- **Haqiqiy bot rejimi:** Agar `.env` da `TELEGRAM_BOT_TOKEN` kiritilgan bo'lsa, bot Telegram tarmog'iga ulanadi va xabarlarni qabul qilishni boshlaydi.
- **Konsol (CLI) test rejimi:** Agar token kiritilmagan bo'lsa, konsolda qulay interaktiv test rejimi ochiladi.

### 3. FastAPI Veb-servisini ishga tushirish
```bash
python web_service.py
```
- **Veb-Dashboard:** `http://127.0.0.1:8000/` (brauzer orqali test qilish)
- **Swagger API Hujjatlari:** `http://127.0.0.1:8000/docs`

### 4. Avtomatlashtirilgan Testlar va Benchmark
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

## 📋 Tizim Imkoniyatlari va Namunaviy Savollar

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
