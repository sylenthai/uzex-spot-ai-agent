"""
Intelligent Query Router and Intent Classifier
Analyzes bilingual queries, extracts entities, coordinates with database and guardrails.
Includes comprehensive Uzbek-Russian commodity synonyms, model concealment, and zero-hallucination protection.
"""

import re
from typing import Dict, Any, Tuple, Optional, List
from engine import database
from engine import formatter
from engine.guardrail import AntiHallucinationGuardrail
from engine import llm_agent
from config import (
    IDENTITY_RESPONSE_UZ,
    IDENTITY_RESPONSE_RU,
    OUT_OF_SCOPE_UZ,
    OUT_OF_SCOPE_RU
)

COMMODITY_SYNONYMS = {
    # Uzbek Latin / variations -> Russian catalog search terms
    "sement": ["цемент", "портландцемент"],
    "tsement": ["цемент", "портландцемент"],
    "shakar": ["сахар", "сахар белый"],
    "paxta": ["хлопок", "хлопок-сырец"],
    "paxta-xomashyosi": ["хлопок-сырец"],
    "bug'doy": ["пшеница"],
    "bugdoy": ["пшеница"],
    "un": ["мука", "мука пшеничная"],
    "benzin": ["бензин", "бензин автомобильный"],
    "dizel": ["дизельное топливо", "топливо дизельное"],
    "solyarka": ["топливо дизельное"],
    "yog'": ["масло хлопковое", "масло"],
    "yog": ["масло хлопковое", "масло"],
    "moy": ["масло хлопковое"],
    "paxta yog'i": ["масло хлопковое"],
    "gaz": ["сжиженный газ"],
    "propan": ["сжиженный газ"],
    "armatura": ["арматура", "арматура стальная"],
    "polietilen": ["полиэтилен"],
    "polivinilxlorid": ["поливинилхлорид"],
    "pvh": ["поливинилхлорид"],
    "selitra": ["селитра", "аммиачная селитра"],
    "karbamid": ["карбамид"],
    "shrot": ["шрот", "шрот хлопковых семян"],
    "guruch": ["рис", "рис шлифованный"],
    "alyuminiy": ["алюминий", "профиль алюминиевый"],
    "po'lat": ["сталь", "лист стальной"],
    "polat": ["сталь", "лист стальной"],
    "metall": ["металл", "прокат", "арматура"],
    "kislota": ["кислота серная", "кислота"],

    # Russian synonyms
    "цемент": ["цемент", "портландцемент"],
    "сахар": ["сахар", "сахар белый"],
    "хлопок": ["хлопок", "хлопок-сырец"],
    "пшеница": ["пшеница", "пшеница продовольственная"],
    "мука": ["мука", "мука пшеничная"],
    "бензин": ["бензин", "бензин автомобильный"],
    "дизель": ["дизельное топливо", "топливо дизельное"],
    "солярка": ["топливо дизельное"],
    "масло": ["масло хлопковое"],
    "газ": ["сжиженный газ"],
    "арматура": ["арматура", "арматура стальная"],
    "полиэтилен": ["полиэтилен"],
    "поливинилхлорид": ["поливинилхлорид"],
    "пвх": ["поливинилхлорид"],
    "селитра": ["аммиачная селитра", "селитра"],
    "карбамид": ["карбамид"],
    "шрот": ["шрот", "шрот хлопковых семян"],
    "рис": ["рис", "рис шлифованный"],
    "алюминий": ["алюминий", "профиль алюминиевый"],
    "сталь": ["сталь", "лист стальной"]
}

REGIONS_LIST = [
    "toshkent shahri", "toshkent viloyati", "samarqand viloyati", "farg‘ona viloyati",
    "farg'ona viloyati", "andijon viloyati", "namangan viloyati", "buxoro viloyati",
    "qashqadaryo viloyati", "surxondaryo viloyati", "xorazm viloyati", "navoiy viloyati",
    "jizzax viloyati", "sirdaryo viloyati", "qoraqalpog‘iston", "toshkent", "samarqand",
    "farg'ona", "farg‘ona", "andijon", "namangan", "buxoro", "qashqadaryo",
    "surxondaryo", "xorazm", "navoiy", "jizzax", "sirdaryo",
    "ташкент", "самарканд", "фергана", "андижан", "наманган", "бухара",
    "кашкадарья", "сурхандарья", "хорезм", "навои", "джизак", "сырдарья"
]

def detect_language(text: str) -> str:
    """
    Detects whether the text is primarily Uzbek or Russian.
    """
    text_lower = text.lower()

    cyrillic_chars = len(re.findall(r"[а-яё]", text_lower))
    latin_chars = len(re.findall(r"[a-z]", text_lower))
    uz_specific = len(re.findall(r"[ўқғҳ]", text_lower)) + len(re.findall(r"[og][‘']", text_lower))

    uz_words = [
        "narxi", "qancha", "bitim", "shartnoma", "haqida", "qayerda",
        "kim", "kursi", "yillik", "bo'yicha", "sotuvchi", "xaridor",
        "ma'lumot", "tovar", "holati", "bekor", "eng", "yirik"
    ]
    ru_words = [
        "сделка", "сделки", "сделку", "контракт", "контракта", "цена",
        "цены", "сколько", "информация", "где", "кто", "курс", "года",
        "по", "продавец", "продавцов", "покупатель", "данные", "товар",
        "товары", "статус", "отменен", "рублей", "доллар", "расскажи"
    ]

    uz_word_score = sum(1 for m in uz_words if m in text_lower)
    ru_word_score = sum(1 for m in ru_words if m in text_lower)

    if ru_word_score > uz_word_score:
        return "ru"
    if uz_word_score > ru_word_score:
        return "uz"

    if cyrillic_chars > latin_chars and uz_specific == 0:
        return "ru"
    return "uz"

def extract_year(text: str) -> Optional[int]:
    """Extracts a year between 2022 and 2026 if present."""
    match = re.search(r"\b(202[2-6])\b", text)
    if match:
        return int(match.group(1))
    return None

def extract_date(text: str) -> Optional[str]:
    """Extracts DD.MM.YYYY date string if present."""
    match = re.search(r"\b(\d{2}\.\d{2}\.202[2-6])\b", text)
    if match:
        return match.group(1)
    return None

def route_query(user_text: str, forced_lang: Optional[str] = None) -> Dict[str, Any]:
    """
    Main entry point for natural language and structured queries.
    Coordinates between NLP, database, LLM augmentation, and strict zero-hallucination guardrail.
    """
    text = user_text.strip()
    lang = forced_lang or detect_language(text)
    lower = text.lower()
    year = extract_year(text)
    date_val = extract_date(text)

    # ----------------------------------------------------
    # 0. MODEL SECRECY & AGENT IDENTITY DEFENSE
    # ----------------------------------------------------
    identity_triggers = [
        "model", "модел", "deepseek", "chatgpt", "gpt",
        "openai", "claude", "llm", "sen kimsan", "siz kimsiz", "kim yaratgan",
        "kim sansan", "modelin nima", "ты кто", "кто ты", "кто тебя создал",
        "дипсик", "дип сик", "чатгпт", "гпт", "опенаи", "нейросеть",
        "архитектура", "o'zing haqingda", "haqingda ayt", "о себе", "расскажи о себе"
    ]
    if any(t in lower for t in identity_triggers):
        resp = IDENTITY_RESPONSE_UZ if lang == "uz" else IDENTITY_RESPONSE_RU
        return {
            "intent": "identity_query",
            "language": lang,
            "found": True,
            "response_text": resp,
            "raw_data": {"identity": "UZEX AI Agent"}
        }

    # ----------------------------------------------------
    # 0.1 OUT-OF-SCOPE FILTER
    # ----------------------------------------------------
    out_of_scope_triggers = [
        "ob-havo", "obhavo", "havo qanday", "погода", "футбол", "futbol",
        "she'r", "sher yoz", "стих", "анекдот", "latifa", "kinolar", "film",
        "retsept", "ovqat", "retsepti"
    ]
    if any(t in lower for t in out_of_scope_triggers):
        resp = OUT_OF_SCOPE_UZ if lang == "uz" else OUT_OF_SCOPE_RU
        return {
            "intent": "out_of_scope",
            "language": lang,
            "found": False,
            "response_text": resp,
            "raw_data": None
        }

    # ----------------------------------------------------
    # 1. BROKER CODE: BK001 - BK120
    # ----------------------------------------------------
    broker_match = re.search(r"\b(BK\d{3})\b", text, re.IGNORECASE)
    if broker_match:
        b_code = broker_match.group(1).upper()
        b_data = database.get_broker_by_code(b_code)
        if b_data:
            return {
                "intent": "broker_lookup",
                "language": lang,
                "found": True,
                "response_text": formatter.format_broker(b_data, lang),
                "raw_data": b_data,
                "entity_type": "broker",
                "entity_value": b_code
            }
        else:
            return {
                "intent": "broker_lookup",
                "language": lang,
                "found": False,
                "response_text": AntiHallucinationGuardrail.get_not_found_response(lang),
                "raw_data": None
            }

    # ----------------------------------------------------
    # 2. 9-DIGIT INN / STIR
    # ----------------------------------------------------
    stir_match = re.search(r"\b(\d{9})\b", text)
    if stir_match:
        inn_val = stir_match.group(1)
        p_data = database.get_participant_by_inn(inn_val)
        if p_data:
            return {
                "intent": "participant_lookup",
                "language": lang,
                "found": True,
                "response_text": formatter.format_participant(p_data, lang),
                "raw_data": p_data,
                "entity_type": "inn",
                "entity_value": inn_val
            }
        else:
            return {
                "intent": "participant_lookup",
                "language": lang,
                "found": False,
                "response_text": AntiHallucinationGuardrail.get_not_found_response(lang),
                "raw_data": None
            }

    # ----------------------------------------------------
    # 3. CONTRACT NUMBER
    # ----------------------------------------------------
    contract_kw_match = re.search(r"(?:shartnoma|kontrakt|контракт|договор)\s*№?\s*(\d+)", text, re.IGNORECASE)
    if contract_kw_match:
        c_num = int(contract_kw_match.group(1))
        c_data = database.get_contract_by_id(c_num)
        if c_data:
            return {
                "intent": "contract_lookup",
                "language": lang,
                "found": True,
                "response_text": formatter.format_contract(c_data, lang),
                "raw_data": c_data,
                "entity_type": "contract",
                "entity_value": str(c_num)
            }
        else:
            return {
                "intent": "contract_lookup",
                "language": lang,
                "found": False,
                "response_text": AntiHallucinationGuardrail.get_not_found_response(lang),
                "raw_data": None
            }

    # ----------------------------------------------------
    # 4. DEAL NUMBER (6-digit, 100000 - 999999)
    # ----------------------------------------------------
    deal_kw_match = re.search(r"(?:bitim|sdelka|сделка)?\s*№?\s*(\d{6})(?:-?\w*)?", text, re.IGNORECASE)
    if deal_kw_match:
        d_num = int(deal_kw_match.group(1))
        if 100000 <= d_num <= 999999:
            d_data = database.get_deal_by_id(d_num)
            if d_data:
                return {
                    "intent": "deal_lookup",
                    "language": lang,
                    "found": True,
                    "response_text": formatter.format_deal(d_data, lang),
                    "raw_data": d_data,
                    "entity_type": "deal",
                    "entity_value": str(d_num)
                }
            else:
                return {
                    "intent": "deal_lookup",
                    "language": lang,
                    "found": False,
                    "response_text": AntiHallucinationGuardrail.get_not_found_response(lang),
                    "raw_data": None
                }

    # ----------------------------------------------------
    # 5. USD EXCHANGE RATE
    # ----------------------------------------------------
    if any(k in lower for k in ["dollar", "доллар", "kurs", "курс"]):
        if date_val:
            rate_data = database.get_usd_rate(date_val)
            if rate_data:
                return {
                    "intent": "usd_rate",
                    "language": lang,
                    "found": True,
                    "response_text": formatter.format_usd_rate(rate_data, lang),
                    "raw_data": rate_data
                }
            else:
                return {
                    "intent": "usd_rate",
                    "language": lang,
                    "found": False,
                    "response_text": AntiHallucinationGuardrail.get_not_found_response(lang),
                    "raw_data": None
                }
        else:
            latest_rate = database.get_latest_usd_rate()
            if latest_rate:
                return {
                    "intent": "usd_rate",
                    "language": lang,
                    "found": True,
                    "response_text": formatter.format_usd_rate(latest_rate, lang),
                    "raw_data": latest_rate
                }

    # ----------------------------------------------------
    # 6. TOP SELLERS & TOP BUYERS
    # ----------------------------------------------------
    if any(k in lower for k in ["top xaridor", "eng yirik xaridor", "топ покупател", "крупнейшие покупател"]):
        top_buyers = database.get_top_buyers(limit=5, year=year)
        if top_buyers:
            return {
                "intent": "top_buyers",
                "language": lang,
                "found": True,
                "response_text": formatter.format_top_buyers(top_buyers, lang, year),
                "raw_data": top_buyers
            }

    if any(k in lower for k in ["top sotuvchi", "eng yirik sotuvchi", "топ продавц", "крупнейшие продавц"]):
        top_sellers = database.get_top_sellers(limit=5, year=year)
        if top_sellers:
            return {
                "intent": "top_sellers",
                "language": lang,
                "found": True,
                "response_text": formatter.format_top_sellers(top_sellers, lang, year),
                "raw_data": top_sellers
            }

    # ----------------------------------------------------
    # 7. TOP PRODUCTS
    # ----------------------------------------------------
    if any(k in lower for k in ["top tovar", "eng ko'p sotilgan", "топ товар", "востребованн"]):
        top_prods = database.get_top_products(limit=5, year=year)
        if top_prods:
            return {
                "intent": "top_products",
                "language": lang,
                "found": True,
                "response_text": formatter.format_top_products(top_prods, lang, year),
                "raw_data": top_prods
            }

    # ----------------------------------------------------
    # 8. GENERAL OVERVIEW & REGIONAL STATS
    # ----------------------------------------------------
    for reg in REGIONS_LIST:
        if reg in lower:
            reg_stats = database.get_region_stats(reg, year=year)
            if reg_stats:
                return {
                    "intent": "regional_stats",
                    "language": lang,
                    "found": True,
                    "response_text": formatter.format_region_stats(reg_stats, lang),
                    "raw_data": reg_stats
                }

    if any(k in lower for k in ["statistika", "umumiy ko'rsatkich", "общие показатели", "статистик"]):
        stats = database.get_general_stats(year=year)
        return {
            "intent": "general_stats",
            "language": lang,
            "found": True,
            "response_text": formatter.format_market_overview(stats, lang),
            "raw_data": stats
        }

    # ----------------------------------------------------
    # 9. COMMODITY / PRODUCT PRICE DYNAMICS
    # ----------------------------------------------------
    matched_search_terms = []
    for syn_key, search_terms in COMMODITY_SYNONYMS.items():
        if re.search(rf"\b{re.escape(syn_key)}\b", lower):
            matched_search_terms.extend(search_terms)

    for term in matched_search_terms:
        p_stats = database.get_product_price_stats(term, year=year)
        if p_stats:
            resp_text = formatter.format_product_stats(p_stats, lang)
            return {
                "intent": "product_price",
                "language": lang,
                "found": True,
                "response_text": resp_text,
                "raw_data": p_stats,
                "entity_type": "product",
                "entity_value": term
            }

    # Candidate extraction
    cleaned_candidate = text
    for stop in [
        "narxi", "narx", "qancha", "haqida", "qanday", "ber", "o'rtacha", "bo'yicha",
        "цена", "цены", "стоимость", "какая", "средняя", "на", "по", "в", "год", "года",
        "yil", "yili", "2022", "2023", "2024", "2025", "2026", "elektromobili", "kompaniyasi",
        "savdo", "qilgan", "sotdi", "oldi"
    ]:
        cleaned_candidate = re.sub(rf"\b{stop}\b", "", cleaned_candidate, flags=re.IGNORECASE)
    cleaned_candidate = cleaned_candidate.strip(" ?!,.:;\"'")

    if len(cleaned_candidate) >= 3:
        p_stats = database.get_product_price_stats(cleaned_candidate, year=year)
        if p_stats:
            return {
                "intent": "product_price",
                "language": lang,
                "found": True,
                "response_text": formatter.format_product_stats(p_stats, lang),
                "raw_data": p_stats,
                "entity_type": "product",
                "entity_value": cleaned_candidate
            }

        matched_participants = database.search_participants_by_name(cleaned_candidate, limit=3)
        if matched_participants:
            if len(matched_participants) == 1:
                p_full = database.get_participant_by_inn(matched_participants[0]["inn"])
                return {
                    "intent": "participant_lookup",
                    "language": lang,
                    "found": True,
                    "response_text": formatter.format_participant(p_full, lang),
                    "raw_data": p_full,
                    "entity_type": "company",
                    "entity_value": cleaned_candidate
                }
            else:
                is_uz = (lang == "uz")
                title = "🏢 <b>Topilgan kompaniyalar:</b>\n" if is_uz else "🏢 <b>Найденные компании:</b>\n"
                lines = [title]
                for p in matched_participants:
                    lines.append(f"• <b>{p['name']}</b>\n  STIR/ИНН: <code>{p['inn']}</code> | {p['region']}\n")
                if is_uz:
                    lines.append("<i>Batafsil ma'lumot olish uchun kompaniya STIR raqamini yuboring.</i>")
                else:
                    lines.append("<i>Для подробной информации отправьте ИНН компании.</i>")
                return {
                    "intent": "participant_search_list",
                    "language": lang,
                    "found": True,
                    "response_text": "\n".join(lines),
                    "raw_data": matched_participants
                }

    # ----------------------------------------------------
    # 10. STRICT ZERO-HALLUCINATION FALLBACK
    # ----------------------------------------------------
    # When no entity is found in our database, the agent strictly
    # returns the zero-hallucination refusal message WITHOUT mentioning
    # any numbers, companies or commodities!
    return {
        "intent": "unknown",
        "language": lang,
        "found": False,
        "response_text": AntiHallucinationGuardrail.get_not_found_response(lang),
        "raw_data": None
    }
