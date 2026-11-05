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

COMMODITY_PATTERNS = [
    # (regex pattern, Russian db search terms, canonical name)
    (r"(?:sement|tsement|цемент|портландцемент)", ["портландцемент", "цемент"], "Портландцемент"),
    (r"(?:paxta|хлопок|хлопк)", ["хлопок", "хлопок-сырец"], "Хлопок"),
    (r"(?:benzin|аи-?80|аи-?92|бензин)", ["бензин"], "Бензин автомобильный"),
    (r"(?:bug\'?doy|bugdoy|пшениц)", ["пшеница"], "Пшеница"),
    (r"(?:un|мука|мук)", ["мука"], "Мука пшеничная"),
    (r"(?:shakar|сахар)", ["сахар"], "Сахар"),
    (r"(?:dizel|дизел|solyark|солярк)", ["топливо дизельное", "дизельное топливо"], "Топливо дизельное"),
    (r"(?:propan|пропан|suyuqlantirilgan gaz|сжиженный газ|gaz|газ)", ["сжиженный газ"], "Сжиженный газ"),
    (r"(?:armatur|арматур)", ["арматура"], "Арматура стальная"),
    (r"(?:paxta yog\'?i|yog\'?|moy|масло хлопков|масло)", ["масло хлопковое", "масло"], "Масло хлопковое"),
    (r"(?:polietilen|полиэтилен)", ["полиэтилен"], "Полиэтилен"),
    (r"(?:karbamid|карбамид|mochevina|мочевина)", ["карбамид"], "Карбамид"),
    (r"(?:selitr|селитр)", ["селитра", "аммиачная селитра"], "Аммиачная селитра"),
    (r"(?:shrot|шрот)", ["шрот"], "Шрот хлопковых семян"),
    (r"(?:polivinilxlorid|поливинилхлорид|pvh|пвх)", ["поливинилхлорид"], "Поливинилхлорид"),
    (r"(?:alyuminiy|алюмин)", ["алюмин"], "Алюминиевый профиль"),
    (r"(?:mis|katod|медн|медь)", ["катод медный", "медь"], "Катод медный"),
    (r"(?:bitum|битум)", ["битум"], "Битум нефтяной"),
    (r"(?:shisha|oyna|стекл)", ["стекло"], "Стекло листовое"),
    (r"(?:g\'?isht|gisht|кирпич)", ["кирпич"], "Кирпич керамический"),
    (r"(?:kislota|кислот)", ["кислота серная"], "Серная кислота"),
]

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
    """Detects whether the text is primarily Uzbek or Russian."""
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

def extract_commodity(text: str) -> Optional[Tuple[str, List[str]]]:
    """Returns (canonical_name, [search_terms]) if a known commodity is found in text."""
    for pattern, search_terms, canonical_name in COMMODITY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return canonical_name, search_terms
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
    # 0.2 NON-EXCHANGE ENTITY & TRICK QUERY SHIELD
    # Catches foreign brands, cryptocurrencies, consumer electronics, precious metals
    # ----------------------------------------------------
    fake_asset_triggers = [
        "apple", "tesla", "google", "microsoft", "amazon", "meta", "samsung",
        "nvidia", "intel", "iphone", "айфон", "тесла", "биткоин", "bitcoin",
        "kripto", "крипто", "ethereum", "эфириум", "oltin", "золото", "kumush", "серебро"
    ]
    for fat in fake_asset_triggers:
        if re.search(rf"\b{re.escape(fat)}\b", lower):
            if not database.search_participants_by_name(fat, limit=1):
                return {
                    "intent": "unknown",
                    "language": lang,
                    "found": False,
                    "response_text": AntiHallucinationGuardrail.get_not_found_response(lang),
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
    # 6. COMMODITY-SPECIFIC QUERIES (Sellers, Buyers, Prices)
    # ----------------------------------------------------
    commodity_match = extract_commodity(text)
    if commodity_match:
        canonical_name, search_terms = commodity_match

        # 6.1 Top sellers of this specific commodity
        seller_signals = [
            "sotuvchi", "kim sotgan", "kim ko'p sotgan", "ko'p sotgan", "sotdi", "sotgan",
            "sotuvchilari", "продал", "продавец", "продавцы", "кто продает", "кто продал",
            "лидеры продаж", "поставщики", "kim sotadi"
        ]
        if any(s in lower for s in seller_signals):
            for t in search_terms:
                prod_sellers = database.get_top_sellers_by_product(t, limit=5)
                if prod_sellers:
                    resp_text = formatter.format_product_top_sellers(canonical_name, prod_sellers, lang)
                    llm_text = llm_agent.generate_llm_response(text, prod_sellers, lang=lang)
                    return {
                        "intent": "product_top_sellers",
                        "language": lang,
                        "found": True,
                        "response_text": llm_text or resp_text,
                        "raw_data": prod_sellers,
                        "entity_type": "product_sellers",
                        "entity_value": canonical_name
                    }

        # 6.2 Top buyers of this specific commodity
        buyer_signals = [
            "xaridor", "kim sotib olgan", "kim olgan", "sotib olgan", "oldi", "xaridorlari",
            "купил", "покупатель", "покупатели", "кто покупает", "кто купил", "закупки"
        ]
        if any(b in lower for b in buyer_signals):
            for t in search_terms:
                prod_buyers = database.get_top_buyers_by_product(t, limit=5)
                if prod_buyers:
                    resp_text = formatter.format_product_top_buyers(canonical_name, prod_buyers, lang)
                    llm_text = llm_agent.generate_llm_response(text, prod_buyers, lang=lang)
                    return {
                        "intent": "product_top_buyers",
                        "language": lang,
                        "found": True,
                        "response_text": llm_text or resp_text,
                        "raw_data": prod_buyers,
                        "entity_type": "product_buyers",
                        "entity_value": canonical_name
                    }

        # 6.3 Price statistics & dynamics of this commodity
        for term in search_terms:
            p_stats = database.get_product_price_stats(term, year=year)
            if p_stats:
                resp_text = formatter.format_product_stats(p_stats, lang)
                llm_text = llm_agent.generate_llm_response(text, p_stats, lang=lang)
                return {
                    "intent": "product_price",
                    "language": lang,
                    "found": True,
                    "response_text": llm_text or resp_text,
                    "raw_data": p_stats,
                    "entity_type": "product",
                    "entity_value": term
                }

    # ----------------------------------------------------
    # 7. EXTREME TRADES (Largest / Smallest Deal)
    # ----------------------------------------------------
    if any(k in lower for k in [
        "eng qimmat bitim", "eng yirik bitim", "eng katta bitim", "rekord bitim",
        "eng katta savdo", "самая крупная сделка", "самая дорогая сделка", "рекордная сделка"
    ]):
        ext_deal = database.get_extreme_deal("max_amount", year=year)
        if ext_deal:
            resp_text = formatter.format_extreme_deal(ext_deal, "max_amount", lang)
            llm_text = llm_agent.generate_llm_response(text, ext_deal, lang=lang)
            return {
                "intent": "extreme_deal",
                "language": lang,
                "found": True,
                "response_text": llm_text or resp_text,
                "raw_data": ext_deal
            }

    if any(k in lower for k in [
        "eng arzon bitim", "eng kichik bitim", "минимальная сделка", "самая дешевая сделка"
    ]):
        ext_deal = database.get_extreme_deal("min_amount", year=year)
        if ext_deal:
            resp_text = formatter.format_extreme_deal(ext_deal, "min_amount", lang)
            llm_text = llm_agent.generate_llm_response(text, ext_deal, lang=lang)
            return {
                "intent": "extreme_deal",
                "language": lang,
                "found": True,
                "response_text": llm_text or resp_text,
                "raw_data": ext_deal
            }

    # ----------------------------------------------------
    # 8. TOP BROKERS
    # ----------------------------------------------------
    if any(k in lower for k in ["top broker", "eng yirik broker", "faol broker", "brokerlar", "топ брокер", "крупнейшие брокер", "активные брокер"]):
        top_br = database.get_top_brokers(limit=5)
        if top_br:
            resp_text = formatter.format_top_brokers(top_br, lang)
            llm_text = llm_agent.generate_llm_response(text, top_br, lang=lang)
            return {
                "intent": "top_brokers",
                "language": lang,
                "found": True,
                "response_text": llm_text or resp_text,
                "raw_data": top_br
            }

    # ----------------------------------------------------
    # 9. GENERAL TOP BUYERS & SELLERS
    # ----------------------------------------------------
    if any(k in lower for k in [
        "top xaridor", "eng yirik xaridor", "eng faol xaridor", "faol xaridor",
        "kim ko'p sotib olgan", "xaridorlar reytingi", "yirik xaridorlar",
        "топ покупател", "крупнейшие покупател", "активные покупател", "кто больше купил", "лидеры покупок"
    ]):
        top_buyers = database.get_top_buyers(limit=5, year=year)
        if top_buyers:
            resp_text = formatter.format_top_buyers(top_buyers, lang, year)
            llm_text = llm_agent.generate_llm_response(text, top_buyers, lang=lang)
            return {
                "intent": "top_buyers",
                "language": lang,
                "found": True,
                "response_text": llm_text or resp_text,
                "raw_data": top_buyers
            }

    if any(k in lower for k in [
        "top sotuvchi", "eng yirik sotuvchi", "eng faol sotuvchi", "faol sotuvchi",
        "kim ko'p sotgan", "sotuvchilar reytingi", "yirik sotuvchilar",
        "топ продавц", "крупнейшие продавц", "активные продавц", "кто больше продал", "лидеры продаж"
    ]):
        top_sellers = database.get_top_sellers(limit=5, year=year)
        if top_sellers:
            resp_text = formatter.format_top_sellers(top_sellers, lang, year)
            llm_text = llm_agent.generate_llm_response(text, top_sellers, lang=lang)
            return {
                "intent": "top_sellers",
                "language": lang,
                "found": True,
                "response_text": llm_text or resp_text,
                "raw_data": top_sellers
            }

    # ----------------------------------------------------
    # 10. TOP PRODUCTS
    # ----------------------------------------------------
    if any(k in lower for k in ["top tovar", "eng ko'p sotilgan", "eng talabgir", "talab yuqori", "ommabop tovar", "топ товар", "востребованн", "самые продаваемые"]):
        top_prods = database.get_top_products(limit=5, year=year)
        if top_prods:
            resp_text = formatter.format_top_products(top_prods, lang, year)
            llm_text = llm_agent.generate_llm_response(text, top_prods, lang=lang)
            return {
                "intent": "top_products",
                "language": lang,
                "found": True,
                "response_text": llm_text or resp_text,
                "raw_data": top_prods
            }

    # ----------------------------------------------------
    # 11. GENERAL OVERVIEW & REGIONAL STATS
    # ----------------------------------------------------
    for reg in REGIONS_LIST:
        if reg in lower:
            reg_stats = database.get_region_stats(reg, year=year)
            if reg_stats:
                resp_text = formatter.format_region_stats(reg_stats, lang)
                llm_text = llm_agent.generate_llm_response(text, reg_stats, lang=lang)
                return {
                    "intent": "regional_stats",
                    "language": lang,
                    "found": True,
                    "response_text": llm_text or resp_text,
                    "raw_data": reg_stats
                }

    if any(k in lower for k in ["statistika", "umumiy ko'rsatkich", "общие показатели", "статистик"]):
        stats = database.get_general_stats(year=year)
        resp_text = formatter.format_market_overview(stats, lang)
        llm_text = llm_agent.generate_llm_response(text, stats, lang=lang)
        return {
            "intent": "general_stats",
            "language": lang,
            "found": True,
            "response_text": llm_text or resp_text,
            "raw_data": stats
        }

    # ----------------------------------------------------
    # 12. FALLBACK CANDIDATE EXTRACTION (Participant or Product)
    # ----------------------------------------------------
    cleaned_candidate = text
    for stop in [
        "narxi", "narx", "qancha", "haqida", "qanday", "ber", "o'rtacha", "bo'yicha",
        "цена", "цены", "стоимость", "какая", "средняя", "на", "по", "в", "год", "года",
        "yil", "yili", "2022", "2023", "2024", "2025", "2026", "elektromobili", "kompaniyasi",
        "savdo", "qilgan", "sotdi", "oldi", "nima", "qaysi", "kim", "qilingan"
    ]:
        cleaned_candidate = re.sub(rf"\b{stop}\b", "", cleaned_candidate, flags=re.IGNORECASE)
    cleaned_candidate = cleaned_candidate.strip(" ?!,.:;\"'")

    if len(cleaned_candidate) >= 3:
        p_stats = database.get_product_price_stats(cleaned_candidate, year=year)
        if p_stats:
            resp_text = formatter.format_product_stats(p_stats, lang)
            llm_text = llm_agent.generate_llm_response(text, p_stats, lang=lang)
            return {
                "intent": "product_price",
                "language": lang,
                "found": True,
                "response_text": llm_text or resp_text,
                "raw_data": p_stats,
                "entity_type": "product",
                "entity_value": cleaned_candidate
            }

        matched_participants = database.search_participants_by_name(cleaned_candidate, limit=3)
        if matched_participants:
            if len(matched_participants) == 1:
                p_full = database.get_participant_by_inn(matched_participants[0]["inn"])
                resp_text = formatter.format_participant(p_full, lang)
                llm_text = llm_agent.generate_llm_response(text, p_full, lang=lang)
                return {
                    "intent": "participant_lookup",
                    "language": lang,
                    "found": True,
                    "response_text": llm_text or resp_text,
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
    # 13. STRICT ZERO-HALLUCINATION FALLBACK
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
