"""
Bilingual Response Formatter (Uzbek & Russian)
Formats structured exchange data into Telegram HTML messages with clear layouts.
"""

from typing import Dict, Any, List, Optional
from config import (
    DEAL_STATE_TRANSLATIONS,
    AUCTION_TYPE_TRANSLATIONS,
    CONTRACT_TYPE_TRANSLATIONS,
    CONTRACT_FORM_TRANSLATIONS
)
from engine.database import format_number

def format_deal(d: Dict[str, Any], lang: str = "uz") -> str:
    """Formats full deal details."""
    is_uz = (lang == "uz")
    deal_num = d["deal_number"]
    curr = d.get("contract_currency", "Узбекский сум")
    curr_label = "so'm" if is_uz and curr == "Узбекский сум" else ("сум" if curr == "Узбекский сум" else "$ (USD)")

    state_raw = d.get("deal_state", "")
    state_trans = DEAL_STATE_TRANSLATIONS.get(state_raw, {}).get(lang, state_raw)

    auc_raw = d.get("auction_type", "")
    auc_trans = AUCTION_TYPE_TRANSLATIONS.get(auc_raw, {}).get(lang, auc_raw)

    c_type_raw = d.get("contract_type", "")
    c_type_trans = CONTRACT_TYPE_TRANSLATIONS.get(c_type_raw, {}).get(lang, c_type_raw)

    c_form_raw = d.get("contract_form", "")
    c_form_trans = CONTRACT_FORM_TRANSLATIONS.get(c_form_raw, {}).get(lang, c_form_raw)

    tot_units = d["quantity"] * d["lot"]

    if is_uz:
        lines = [
            f"📋 <b>BIRJA BITIMI № {deal_num}</b>",
            f"━━━━━━━━━━━━━━━━━━",
            f"📅 <b>Sana va vaqt:</b> {d['deal_date']} | {d['deal_time']}",
            f"🟢 <b>Holati:</b> {state_trans}",
            f"📦 <b>Tovar:</b> {d['product_name']}",
            f"📊 <b>Hajmi:</b> {format_number(d['quantity'], 0)} lot × {format_number(d['lot'])} = <b>{format_number(tot_units)} {d['unit']}</b>",
            f"💰 <b>Bitim summasi:</b> <b>{format_number(d['amount'])} {curr_label}</b>",
        ]
        if d.get("amount_uzs") and curr != "Узбекский сум":
            lines.append(f"💵 <b>So'mdagi ekvivalenti:</b> {format_number(d['amount_uzs'])} so'm")

        lines.extend([
            f"🏷 <b>Birlik narxi:</b> {format_number(d['unit_price'])} {curr_label} / {d['unit']}",
            f"🏁 <b>Boshlang'ich narx:</b> {format_number(d['start_price'])} {curr_label}",
            f"📑 <b>Shartnoma:</b> № {d['contract_number']} ({c_type_trans}, {c_form_trans})",
            f"⚖️ <b>Savdo turi:</b> {auc_trans}",
            f"📍 <b>Ombor hududi:</b> {d['region']}",
            "",
            "🏢 <b>Tomonlar:</b>",
            f"• <b>Sotuvchi:</b> {d.get('seller_name', 'Noma''lum')} (STIR: <code>{d['seller_inn']}</code>)",
            f"  <i>Broker:</i> {d.get('seller_broker_name', d['seller_broker'])} (<code>{d['seller_broker']}</code>)",
            f"• <b>Xaridor:</b> {d.get('buyer_name', 'Noma''lum')} (STIR: <code>{d['buyer_inn']}</code>)",
            f"  <i>Broker:</i> {d.get('buyer_broker_name', d['buyer_broker'])} (<code>{d['buyer_broker']}</code>)",
        ])

        if d.get("payment_date") or d.get("delivery_date"):
            lines.append("")
            lines.append("🚚 <b>Ijro tafsilotlari:</b>")
            if d.get("payment_date"):
                lines.append(f"• To'langan sana: {d['payment_date']}")
            if d.get("delivery_date"):
                lines.append(f"• Yetkazilgan sana: {d['delivery_date']}")
            if d.get("delivered_qty"):
                lines.append(f"• Yetkazilgan miqdor: {format_number(d['delivered_qty'])} lot")

        return "\n".join(lines)
    else:
        lines = [
            f"📋 <b>БИРЖЕВАЯ СДЕЛКА № {deal_num}</b>",
            f"━━━━━━━━━━━━━━━━━━",
            f"📅 <b>Дата и время:</b> {d['deal_date']} | {d['deal_time']}",
            f"🟢 <b>Статус:</b> {state_trans}",
            f"📦 <b>Товар:</b> {d['product_name']}",
            f"📊 <b>Объём:</b> {format_number(d['quantity'], 0)} лотов × {format_number(d['lot'])} = <b>{format_number(tot_units)} {d['unit']}</b>",
            f"💰 <b>Сумма сделки:</b> <b>{format_number(d['amount'])} {curr_label}</b>",
        ]
        if d.get("amount_uzs") and curr != "Узбекский сум":
            lines.append(f"💵 <b>В сумах:</b> {format_number(d['amount_uzs'])} сум")

        lines.extend([
            f"🏷 <b>Цена за единицу:</b> {format_number(d['unit_price'])} {curr_label} / {d['unit']}",
            f"🏁 <b>Стартовая цена:</b> {format_number(d['start_price'])} {curr_label}",
            f"📑 <b>Контракт:</b> № {d['contract_number']} ({c_type_trans}, {c_form_trans})",
            f"⚖️ <b>Тип торгов:</b> {auc_trans}",
            f"📍 <b>Регион склада:</b> {d['region']}",
            "",
            "🏢 <b>Участники:</b>",
            f"• <b>Продавец:</b> {d.get('seller_name', 'Не указано')} (ИНН: <code>{d['seller_inn']}</code>)",
            f"  <i>Брокер:</i> {d.get('seller_broker_name', d['seller_broker'])} (<code>{d['seller_broker']}</code>)",
            f"• <b>Покупатель:</b> {d.get('buyer_name', 'Не указано')} (ИНН: <code>{d['buyer_inn']}</code>)",
            f"  <i>Брокер:</i> {d.get('buyer_broker_name', d['buyer_broker'])} (<code>{d['buyer_broker']}</code>)",
        ])

        if d.get("payment_date") or d.get("delivery_date"):
            lines.append("")
            lines.append("🚚 <b>Исполнение сделки:</b>")
            if d.get("payment_date"):
                lines.append(f"• Дата оплаты: {d['payment_date']}")
            if d.get("delivery_date"):
                lines.append(f"• Дата поставки: {d['delivery_date']}")
            if d.get("delivered_qty"):
                lines.append(f"• Фактически поставлено: {format_number(d['delivered_qty'])} лотов")

        return "\n".join(lines)

def format_contract(c: Dict[str, Any], lang: str = "uz") -> str:
    """Formats contract details."""
    is_uz = (lang == "uz")
    c_num = c["contract_number"]
    curr = c.get("currency", "Узбекский сум")
    stats = c.get("stats", {})

    if is_uz:
        lines = [
            f"📑 <b>SHARTNOMA KARTASI № {c_num}</b>",
            f"━━━━━━━━━━━━━━━━━━",
            f"📦 <b>Mahsulot:</b> {c['product_name']}",
            f"🏷 <b>Kategoriya:</b> {c.get('category', '-')} ({c.get('group_name', '-')})",
            f"🏢 <b>Soha:</b> {c.get('industry', '-')}",
            f"🔢 <b>TN VED kodi:</b> <code>{c.get('tnved_code', '-')}</code>",
            "",
            f"💰 <b>Bazaviy narx:</b> {format_number(c['base_price'])} {curr}",
            f"📏 <b>Lot hajmi:</b> {format_number(c['lot'])} {c['unit']}",
            f"🔒 <b>Garov summasi:</b> {c.get('deposit_percent', '-')}",
            f"🚚 <b>Yetkazish sharti (Incoterms):</b> {c.get('delivery_basis', '-')}",
            f"📦 <b>Qadoqlanishi:</b> {c.get('packaging', '-')}",
            "",
            f"📍 <b>Ombor:</b> {c.get('warehouse_address', c.get('region', '-'))}",
            f"⏱ <b>To'lov muddati:</b> {c.get('payment_term_days', '-')} kun",
            f"⏱ <b>Yetkazish muddati:</b> {c.get('delivery_term_days', '-')} kun",
            f"📅 <b>Amal qilish davri:</b> {c.get('reg_date', '-')} dan {c.get('valid_till', '-')} gacha",
            "",
            f"🏢 <b>Sotuvchi kompaniya:</b>",
            f"{c.get('seller_name', 'Noma''lum')} (STIR: <code>{c.get('seller_inn', '-')}</code>)",
            f"Hudud: {c.get('seller_region', '-')}, Faoliyat: {c.get('seller_activity', '-')}",
        ]
        if stats and stats.get("deals_count", 0) > 0:
            lines.append("")
            lines.append(f"📊 <b>Ushbu shartnoma bo'yicha bitimlar:</b>")
            lines.append(f"• Tuzilgan bitimlar soni: <b>{stats['deals_count']} ta</b>")
            lines.append(f"• Jami savdo hajmi: {format_number(stats['total_volume_traded'])} {c['unit']}")
            lines.append(f"• Umumiy aylanma: {format_number(stats['total_amount_uzs'])} so'm")
            lines.append(f"• Oxirgi bitim sanasi: {stats['last_deal_date']}")

        return "\n".join(lines)
    else:
        lines = [
            f"📑 <b>КАРТОЧКА КОНТРАКТА № {c_num}</b>",
            f"━━━━━━━━━━━━━━━━━━",
            f"📦 <b>Продукт:</b> {c['product_name']}",
            f"🏷 <b>Категория:</b> {c.get('category', '-')} ({c.get('group_name', '-')})",
            f"🏢 <b>Отрасль:</b> {c.get('industry', '-')}",
            f"🔢 <b>Код ТН ВЭД:</b> <code>{c.get('tnved_code', '-')}</code>",
            "",
            f"💰 <b>Базисная цена:</b> {format_number(c['base_price'])} {curr}",
            f"📏 <b>Размер лота:</b> {format_number(c['lot'])} {c['unit']}",
            f"🔒 <b>Сумма залога:</b> {c.get('deposit_percent', '-')}",
            f"🚚 <b>Базис поставки:</b> {c.get('delivery_basis', '-')}",
            f"📦 <b>Упаковка:</b> {c.get('packaging', '-')}",
            "",
            f"📍 <b>Склад:</b> {c.get('warehouse_address', c.get('region', '-'))}",
            f"⏱ <b>Срок оплаты:</b> {c.get('payment_term_days', '-')} дней",
            f"⏱ <b>Срок поставки:</b> {c.get('delivery_term_days', '-')} дней",
            f"📅 <b>Срок действия:</b> с {c.get('reg_date', '-')} по {c.get('valid_till', '-')}",
            "",
            f"🏢 <b>Продавец:</b>",
            f"{c.get('seller_name', 'Не указано')} (ИНН: <code>{c.get('seller_inn', '-')}</code>)",
            f"Регион: {c.get('seller_region', '-')}, Вид деятельности: {c.get('seller_activity', '-')}",
        ]
        if stats and stats.get("deals_count", 0) > 0:
            lines.append("")
            lines.append(f"📊 <b>Сделки по контракту:</b>")
            lines.append(f"• Количество сделок: <b>{stats['deals_count']}</b>")
            lines.append(f"• Всего реализовано: {format_number(stats['total_volume_traded'])} {c['unit']}")
            lines.append(f"• Общая сумма: {format_number(stats['total_amount_uzs'])} сум")
            lines.append(f"• Дата последней сделки: {stats['last_deal_date']}")

        return "\n".join(lines)

def format_participant(p: Dict[str, Any], lang: str = "uz") -> str:
    """Formats market participant company profile."""
    is_uz = (lang == "uz")
    inn = p["inn"]

    if is_uz:
        lines = [
            f"🏢 <b>KOMPANIYA PROFILI: {p['name']}</b>",
            f"━━━━━━━━━━━━━━━━━━",
            f"🆔 <b>STIR (INN):</b> <code>{inn}</code>",
            f"📍 <b>Hudud:</b> {p['region']}",
            f"💼 <b>Faoliyat turi:</b> {p['activity']}",
            f"🏷 <b>Asosiy rol:</b> {p['role']}",
            f"🧾 <b>QQS to'lovchisi:</b> {p['vat_payer']}",
            "",
            f"📊 <b>Savdo ko'rsatkichlari (2022-2026):</b>",
            f"• <b>Sotuvchi sifatida:</b> {p['seller_deals_count']} ta bitim | {format_number(p['seller_total_uzs'])} so'm",
            f"• <b>Xaridor sifatida:</b> {p['buyer_deals_count']} ta bitim | {format_number(p['buyer_total_uzs'])} so'm",
            f"• <b>Umumiy aylanma:</b> {format_number(p['seller_total_uzs'] + p['buyer_total_uzs'])} so'm",
        ]
        recent = p.get("recent_deals", [])
        if recent:
            lines.append("")
            lines.append("🕒 <b>Oxirgi bitimlari:</b>")
            for r in recent:
                lines.append(f"• №{r['deal_number']} ({r['deal_date']}) - {r['product_name'][:30]}... ({format_number(r['amount'])} so'm)")

        return "\n".join(lines)
    else:
        lines = [
            f"🏢 <b>ПРОФИЛЬ УЧАСТНИКА: {p['name']}</b>",
            f"━━━━━━━━━━━━━━━━━━",
            f"🆔 <b>ИНН:</b> <code>{inn}</code>",
            f"📍 <b>Регион:</b> {p['region']}",
            f"💼 <b>Вид деятельности:</b> {p['activity']}",
            f"🏷 <b>Роль:</b> {p['role']}",
            f"🧾 <b>Плательщик НДС:</b> {p['vat_payer']}",
            "",
            f"📊 <b>Торговая активность (2022-2026 гг.):</b>",
            f"• <b>Как продавец:</b> {p['seller_deals_count']} сделок | {format_number(p['seller_total_uzs'])} сум",
            f"• <b>Как покупатель:</b> {p['buyer_deals_count']} сделок | {format_number(p['buyer_total_uzs'])} сум",
            f"• <b>Совокупный оборот:</b> {format_number(p['seller_total_uzs'] + p['buyer_total_uzs'])} сум",
        ]
        recent = p.get("recent_deals", [])
        if recent:
            lines.append("")
            lines.append("🕒 <b>Последние сделки:</b>")
            for r in recent:
                lines.append(f"• №{r['deal_number']} ({r['deal_date']}) - {r['product_name'][:30]}... ({format_number(r['amount'])} сум)")

        return "\n".join(lines)

def format_broker(b: Dict[str, Any], lang: str = "uz") -> str:
    """Formats broker firm profile."""
    is_uz = (lang == "uz")
    code = b["broker_code"]

    if is_uz:
        return (
            f"🏛 <b>BROKERLIK IDORASI: {b['name']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🏷 <b>Broker kodi:</b> <code>{code}</code>\n"
            f"🆔 <b>STIR:</b> <code>{b.get('inn', '—')}</code>\n"
            f"📍 <b>Hudud:</b> {b['region']}\n\n"
            f"📊 <b>Birja faoliyati:</b>\n"
            f"• Vositachilik qilgan bitimlari: <b>{format_number(b['total_mediated_deals'], 0)} ta</b>\n"
            f"• Bitimlar umumiy hajmi: <b>{format_number(b['total_volume_uzs'])} so'm</b>"
        )
    else:
        return (
            f"🏛 <b>БРОКЕРСКАЯ КОНТОРА: {b['name']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🏷 <b>Код брокера:</b> <code>{code}</code>\n"
            f"🆔 <b>ИНН:</b> <code>{b.get('inn', '—')}</code>\n"
            f"📍 <b>Регион:</b> {b['region']}\n\n"
            f"📊 <b>Торговые показатели:</b>\n"
            f"• Всего оформлено сделок: <b>{format_number(b['total_mediated_deals'], 0)}</b>\n"
            f"• Совокупный оборот: <b>{format_number(b['total_volume_uzs'])} сум</b>"
        )

def format_product_stats(s: Dict[str, Any], lang: str = "uz") -> str:
    """Formats commodity pricing and trend dynamics."""
    is_uz = (lang == "uz")
    unit = s.get("unit", "birlik")

    if is_uz:
        lines = [
            f"📊 <b>TOVAR NARXLARI TAHLILI</b>",
            f"📦 <b>Tovar:</b> {s['product_name']}",
            f"━━━━━━━━━━━━━━━━━━",
            f"🏷 <b>O'rtacha narx:</b> <b>{format_number(s['avg_price'])} so'm / {unit}</b>",
            f"📉 <b>Eng past narx:</b> {format_number(s['min_price'])} so'm",
            f"📈 <b>Eng yuqori narx:</b> {format_number(s['max_price'])} so'm",
            f"🔢 <b>Jami bitimlar soni:</b> {format_number(s['count'], 0)} ta",
            f"⚖️ <b>Jami sotilgan hajm:</b> {format_number(s['total_volume'])} {unit}",
            f"💰 <b>Umumiy aylanma:</b> {format_number(s['total_amount_uzs'])} so'm",
        ]
        trend = s.get("yearly_trend", [])
        if trend:
            lines.append("")
            lines.append("📅 <b>Yillar bo'yicha narx dinamikasi:</b>")
            for t in trend:
                lines.append(f"• <b>{t['deal_year']}-yil:</b> {format_number(t['avg_price'])} so'm | {format_number(t['deals_count'], 0)} bitim")

        latest = s.get("latest_deal")
        if latest:
            lines.append("")
            lines.append(f"🕒 <b>Oxirgi bitim (№{latest['deal_number']}, {latest['deal_date']}):</b>")
            lines.append(f"Narxi: <b>{format_number(latest['unit_price'])} so'm/{unit}</b> ({latest['region']})")

        return "\n".join(lines)
    else:
        lines = [
            f"📊 <b>АНАЛИЗ ЦЕН НА ТОВАР</b>",
            f"📦 <b>Товар:</b> {s['product_name']}",
            f"━━━━━━━━━━━━━━━━━━",
            f"🏷 <b>Средневзвешенная цена:</b> <b>{format_number(s['avg_price'])} сум / {unit}</b>",
            f"📉 <b>Минимальная цена:</b> {format_number(s['min_price'])} сум",
            f"📈 <b>Максимальная цена:</b> {format_number(s['max_price'])} сум",
            f"🔢 <b>Всего заключено сделок:</b> {format_number(s['count'], 0)}",
            f"⚖️ <b>Совокупный объём:</b> {format_number(s['total_volume'])} {unit}",
            f"💰 <b>Общий оборот:</b> {format_number(s['total_amount_uzs'])} сум",
        ]
        trend = s.get("yearly_trend", [])
        if trend:
            lines.append("")
            lines.append("📅 <b>Динамика средних цен по годам:</b>")
            for t in trend:
                lines.append(f"• <b>{t['deal_year']} год:</b> {format_number(t['avg_price'])} сум | {format_number(t['deals_count'], 0)} сделок")

        latest = s.get("latest_deal")
        if latest:
            lines.append("")
            lines.append(f"🕒 <b>Последняя сделка (№{latest['deal_number']}, {latest['deal_date']}):</b>")
            lines.append(f"Цена: <b>{format_number(latest['unit_price'])} сум/{unit}</b> ({latest['region']})")

        return "\n".join(lines)

def format_top_sellers(sellers: List[Dict[str, Any]], lang: str = "uz", year: Optional[int] = None) -> str:
    """Formats Top Sellers leaderboard."""
    is_uz = (lang == "uz")
    title_period = f"{year}-yil" if is_uz and year else (f"{year} год" if year else ("2022-2026 yillar" if is_uz else "2022-2026 гг."))

    if is_uz:
        lines = [
            f"🏆 <b>ENG YIRIK SOTUVCHI KOMPANIYALAR ({title_period})</b>",
            f"━━━━━━━━━━━━━━━━━━",
        ]
        for idx, s in enumerate(sellers, 1):
            lines.append(
                f"<b>{idx}. {s['company_name']}</b>\n"
                f"   STIR: <code>{s['seller_inn']}</code> | {s['region']}\n"
                f"   Bitimlar: {format_number(s['deals_count'], 0)} ta | Hajm: <b>{format_number(s['total_uzs'])} so'm</b>\n"
            )
        return "\n".join(lines)
    else:
        lines = [
            f"🏆 <b>ТОП ПРОДАВЦОВ ПО ОБЪЁМУ ТОРГОВ ({title_period})</b>",
            f"━━━━━━━━━━━━━━━━━━",
        ]
        for idx, s in enumerate(sellers, 1):
            lines.append(
                f"<b>{idx}. {s['company_name']}</b>\n"
                f"   ИНН: <code>{s['seller_inn']}</code> | {s['region']}\n"
                f"   Сделок: {format_number(s['deals_count'], 0)} | Оборот: <b>{format_number(s['total_uzs'])} сум</b>\n"
            )
        return "\n".join(lines)

def format_top_buyers(buyers: List[Dict[str, Any]], lang: str = "uz", year: Optional[int] = None) -> str:
    """Formats Top Buyers leaderboard."""
    is_uz = (lang == "uz")
    title_period = f"{year}-yil" if is_uz and year else (f"{year} год" if year else ("2022-2026 yillar" if is_uz else "2022-2026 гг."))

    if is_uz:
        lines = [
            f"🛒 <b>ENG YIRIK XARIDOR KOMPANIYALAR ({title_period})</b>",
            f"━━━━━━━━━━━━━━━━━━",
        ]
        for idx, b in enumerate(buyers, 1):
            lines.append(
                f"<b>{idx}. {b['company_name']}</b>\n"
                f"   STIR: <code>{b['buyer_inn']}</code> | {b['region']}\n"
                f"   Xaridlar: {format_number(b['deals_count'], 0)} ta | Summa: <b>{format_number(b['total_uzs'])} so'm</b>\n"
            )
        return "\n".join(lines)
    else:
        lines = [
            f"🛒 <b>ТОП ПОКУПАТЕЛЕЙ ПО ОБЪЁМУ ТОРГОВ ({title_period})</b>",
            f"━━━━━━━━━━━━━━━━━━",
        ]
        for idx, b in enumerate(buyers, 1):
            lines.append(
                f"<b>{idx}. {b['company_name']}</b>\n"
                f"   ИНН: <code>{b['buyer_inn']}</code> | {b['region']}\n"
                f"   Покупок: {format_number(b['deals_count'], 0)} | Сумма: <b>{format_number(b['total_uzs'])} сум</b>\n"
            )
        return "\n".join(lines)

def format_region_stats(r: Dict[str, Any], lang: str = "uz") -> str:
    """Formats regional exchange statistics."""
    is_uz = (lang == "uz")
    if is_uz:
        return (
            f"📍 <b>HUDUDIY BIRJA KO'RSATKICHLARI: {r['region']}</b>\n"
            f"Davr: <b>{r['year']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔢 <b>Jami bitimlar soni:</b> {format_number(r['deals_count'], 0)} ta\n"
            f"💰 <b>Umumiy aylanma:</b> <b>{format_number(r['total_uzs'])} so'm</b>\n"
            f"🏢 <b>Faol sotuvchilar:</b> {format_number(r['sellers_count'], 0)} ta\n"
            f"🛒 <b>Faol xaridorlar:</b> {format_number(r['buyers_count'], 0)} ta"
        )
    else:
        return (
            f"📍 <b>РЕГИОНАЛЬНЫЕ ПОКАЗАТЕЛИ: {r['region']}</b>\n"
            f"Период: <b>{r['year']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔢 <b>Количество сделок:</b> {format_number(r['deals_count'], 0)}\n"
            f"💰 <b>Совокупный объём:</b> <b>{format_number(r['total_uzs'])} сум</b>\n"
            f"🏢 <b>Активных продавцов:</b> {format_number(r['sellers_count'], 0)}\n"
            f"🛒 <b>Активных покупателей:</b> {format_number(r['buyers_count'], 0)}"
        )

def format_top_products(products: List[Dict[str, Any]], lang: str = "uz", year: Optional[int] = None) -> str:
    """Formats Top Traded Commodities."""
    is_uz = (lang == "uz")
    title_period = f"{year}-yil" if is_uz and year else (f"{year} год" if year else ("2022-2026 yillar" if is_uz else "2022-2026 гг."))

    if is_uz:
        lines = [
            f"🔥 <b>ENG KO'P SOTILGAN TOVARLAR ({title_period})</b>",
            f"━━━━━━━━━━━━━━━━━━",
        ]
        for idx, p in enumerate(products, 1):
            lines.append(
                f"<b>{idx}. {p['product_name']}</b>\n"
                f"   Bitimlar soni: <b>{format_number(p['deals_count'], 0)} ta</b>\n"
                f"   Jami hajm: {format_number(p['total_volume'])} {p['unit']} | Aylanma: {format_number(p['total_uzs'])} so'm\n"
            )
        return "\n".join(lines)
    else:
        lines = [
            f"🔥 <b>ТОП САМЫХ ВОСТРЕБОВАННЫХ ТОВАРОВ ({title_period})</b>",
            f"━━━━━━━━━━━━━━━━━━",
        ]
        for idx, p in enumerate(products, 1):
            lines.append(
                f"<b>{idx}. {p['product_name']}</b>\n"
                f"   Количество сделок: <b>{format_number(p['deals_count'], 0)}</b>\n"
                f"   Объём: {format_number(p['total_volume'])} {p['unit']} | Оборот: {format_number(p['total_uzs'])} сум\n"
            )
        return "\n".join(lines)

def format_market_overview(m: Dict[str, Any], lang: str = "uz") -> str:
    """Formats general market overview."""
    is_uz = (lang == "uz")
    raw_year = str(m.get('year', ''))
    if is_uz:
        period_text = raw_year if raw_year else "Barcha yillar (2022–2026)"
        return (
            f"📈 <b>UZEX BIRJA UMUMIY KO'RSATKICHLARI</b>\n"
            f"Davr: <b>{period_text}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔢 <b>Jami bitimlar soni:</b> <b>{format_number(m['total_deals'], 0)} ta</b>\n"
            f"💰 <b>Umumiy aylanma:</b> <b>{format_number(m['total_uzs'])} so'm</b>\n"
            f"🏢 <b>Faol sotuvchilar:</b> {format_number(m['active_sellers'], 0)} ta kompaniya\n"
            f"🛒 <b>Faol xaridorlar:</b> {format_number(m['active_buyers'], 0)} ta kompaniya\n"
            f"📑 <b>Savdodagi shartnomalar:</b> {format_number(m['active_contracts'], 0)} ta\n\n"
            f"✅ <b>To'liq ijro etilgan:</b> {format_number(m['executed_deals'], 0)} ta bitim\n"
            f"❌ <b>Bekor qilingan (to'lanmagan):</b> {format_number(m['cancelled_deals'], 0)} ta bitim\n"
            f"🚢 <b>Eksport bitimlari:</b> {format_number(m['export_deals'], 0)} ta (${format_number(m['export_amount_usd'])} USD)"
        )
    else:
        period_text = "Все годы (2022–2026 гг.)" if "barcha" in raw_year.lower() or not raw_year else f"{raw_year} год"
        return (
            f"📈 <b>ОБЩИЕ ПОКАЗАТЕЛИ БИРЖИ UZEX</b>\n"
            f"Период: <b>{period_text}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔢 <b>Всего заключено сделок:</b> <b>{format_number(m['total_deals'], 0)}</b>\n"
            f"💰 <b>Совокупный объём торгов:</b> <b>{format_number(m['total_uzs'])} сум</b>\n"
            f"🏢 <b>Активных продавцов:</b> {format_number(m['active_sellers'], 0)} компаний\n"
            f"🛒 <b>Активных покупателей:</b> {format_number(m['active_buyers'], 0)} компаний\n"
            f"📑 <b>Контрактов в обращении:</b> {format_number(m['active_contracts'], 0)}\n\n"
            f"✅ <b>Исполнено полностью:</b> {format_number(m['executed_deals'], 0)} сделок\n"
            f"❌ <b>Аннулировано (не оплачено):</b> {format_number(m['cancelled_deals'], 0)} сделок\n"
            f"🚢 <b>Экспортных сделок:</b> {format_number(m['export_deals'], 0)} (${format_number(m['export_amount_usd'])} USD)"
        )

def format_usd_rate(r: Dict[str, Any], lang: str = "uz") -> str:
    """Formats USD rate information."""
    is_uz = (lang == "uz")
    if is_uz:
        return (
            f"💵 <b>AQSH DOLLARI KURSI</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 <b>Sana:</b> {r['rate_date']}\n"
            f"🏷 <b>Kurs:</b> <b>1 USD = {format_number(r['rate'])} so'm</b>\n\n"
            f"ℹ️ <i>Eksport shartnomalari bo'yicha hisob-kitoblar ushbu rasmiy kurs asosida amalga oshiriladi.</i>"
        )
    else:
        return (
            f"💵 <b>КУРС ДОЛЛАРА США</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 <b>Дата:</b> {r['rate_date']}\n"
            f"🏷 <b>Курс:</b> <b>1 USD = {format_number(r['rate'])} сум</b>\n\n"
            f"ℹ️ <i>Данный курс используется для пересчета экспортных сделок в национальной валюте.</i>"
        )

def format_usd_rate_yearly(stats: Dict[str, Any], lang: str = "uz") -> str:
    """Formats annual USD exchange rate statistics."""
    is_uz = (lang == "uz")
    year = stats.get("year", 2022)
    min_r = format_number(stats.get("min_rate", 0))
    max_r = format_number(stats.get("max_rate", 0))
    avg_r = format_number(stats.get("avg_rate", 0))
    start_r = format_number(stats.get("start_rate", 0))
    start_d = stats.get("start_date", f"01.01.{year}")
    end_r = format_number(stats.get("end_rate", 0))
    end_d = stats.get("end_date", f"31.12.{year}")
    cnt = stats.get("count", 365)

    if is_uz:
        return (
            f"💵 <b>{year}-YILDAGI AQSH DOLLARI KURSI</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 <b>O'rtacha kurs:</b> <b>1 USD = {avg_r} so'm</b>\n"
            f"📈 <b>Maksimal kurs:</b> {max_r} so'm\n"
            f"📉 <b>Minimal kurs:</b> {min_r} so'm\n"
            f"🗓 <b>Yil boshida ({start_d}):</b> {start_r} so'm\n"
            f"🗓 <b>Yil yakunida ({end_d}):</b> {end_r} so'm\n"
            f"📅 <b>Hisoblangan kunlar:</b> {cnt} kun\n\n"
            f"ℹ️ <i>Ma'lumotlar Markaziy bankning birja hisob-kitoblarida qo'llanilgan rasmiy kurslar reyestridan olindi.</i>"
        )
    else:
        return (
            f"💵 <b>КУРС ДОЛЛАРА США ЗА {year} ГОД</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 <b>Средний курс:</b> <b>1 USD = {avg_r} сум</b>\n"
            f"📈 <b>Максимальный курс:</b> {max_r} сум\n"
            f"📉 <b>Минимальный курс:</b> {min_r} сум\n"
            f"🗓 <b>На начало года ({start_d}):</b> {start_r} сум\n"
            f"🗓 <b>На конец года ({end_d}):</b> {end_r} сум\n"
            f"📅 <b>Количество дней:</b> {cnt} дней\n\n"
            f"ℹ️ <i>Данные получены из официального реестра курсов ЦБ, применяемых в биржевых расчетах.</i>"
        )

def format_product_top_sellers(product_name: str, sellers: List[Dict[str, Any]], lang: str = "uz") -> str:
    """Formats top sellers for a specific commodity."""
    is_uz = (lang == "uz")
    if is_uz:
        lines = [
            f"🏆 <b>TOVAR BO'YICHA YIRIK SOTUVCHILAR: {product_name.upper()}</b>",
            f"━━━━━━━━━━━━━━━━━━",
        ]
        for idx, s in enumerate(sellers, 1):
            name = s.get("seller_name") or f"STIR {s.get('seller_inn')}"
            lines.append(
                f"<b>{idx}. {name}</b>\n"
                f"   STIR: <code>{s['seller_inn']}</code> | {s.get('seller_region', '')}\n"
                f"   Bitimlar: {format_number(s['deals_count'], 0)} ta | Aylanma: <b>{format_number(s['total_uzs'])} so'm</b>\n"
            )
        return "\n".join(lines)
    else:
        lines = [
            f"🏆 <b>КРУПНЕЙШИЕ ПРОДАВЦЫ ТОВАРА: {product_name.upper()}</b>",
            f"━━━━━━━━━━━━━━━━━━",
        ]
        for idx, s in enumerate(sellers, 1):
            name = s.get("seller_name") or f"ИНН {s.get('seller_inn')}"
            lines.append(
                f"<b>{idx}. {name}</b>\n"
                f"   ИНН: <code>{s['seller_inn']}</code> | {s.get('seller_region', '')}\n"
                f"   Сделок: {format_number(s['deals_count'], 0)} | Оборот: <b>{format_number(s['total_uzs'])} сум</b>\n"
            )
        return "\n".join(lines)

def format_product_top_buyers(product_name: str, buyers: List[Dict[str, Any]], lang: str = "uz") -> str:
    """Formats top buyers for a specific commodity."""
    is_uz = (lang == "uz")
    if is_uz:
        lines = [
            f"🛒 <b>TOVAR BO'YICHA YIRIK XARIDORLAR: {product_name.upper()}</b>",
            f"━━━━━━━━━━━━━━━━━━",
        ]
        for idx, b in enumerate(buyers, 1):
            name = b.get("buyer_name") or f"STIR {b.get('buyer_inn')}"
            lines.append(
                f"<b>{idx}. {name}</b>\n"
                f"   STIR: <code>{b['buyer_inn']}</code> | {b.get('buyer_region', '')}\n"
                f"   Bitimlar: {format_number(b['deals_count'], 0)} ta | Xarid: <b>{format_number(b['total_uzs'])} so'm</b>\n"
            )
        return "\n".join(lines)
    else:
        lines = [
            f"🛒 <b>КРУПНЕЙШИЕ ПОКУПАТЕЛИ ТОВАРА: {product_name.upper()}</b>",
            f"━━━━━━━━━━━━━━━━━━",
        ]
        for idx, b in enumerate(buyers, 1):
            name = b.get("buyer_name") or f"ИНН {b.get('buyer_inn')}"
            lines.append(
                f"<b>{idx}. {name}</b>\n"
                f"   ИНН: <code>{b['buyer_inn']}</code> | {b.get('buyer_region', '')}\n"
                f"   Сделок: {format_number(b['deals_count'], 0)} | Закупки: <b>{format_number(b['total_uzs'])} сум</b>\n"
            )
        return "\n".join(lines)

def format_extreme_deal(d: Dict[str, Any], extreme_type: str = "max_amount", lang: str = "uz") -> str:
    """Formats the largest or most extreme trade."""
    is_uz = (lang == "uz")
    deal_num = d["deal_number"]
    contract_num = d.get("contract_number", "—")
    title_uz = "РЕКОРД БИТИМ: ЭНГ ЙИРИК БИРЖА БИТИМИ" if extreme_type == "max_amount" else "БИРЖА БИТИМИ"
    title_ru = "РЕКОРДНАЯ СДЕЛКА: КРУПНЕЙШАЯ НА БИРЖЕ" if extreme_type == "max_amount" else "БИРЖЕВАЯ СДЕЛКА"

    if is_uz:
        return (
            f"💎 <b>{title_uz} № {deal_num}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📄 <b>Shartnoma raqami:</b> № <code>{contract_num}</code>\n"
            f"📅 <b>Sana:</b> {d['deal_date']}\n"
            f"📦 <b>Mahsulot:</b> {d['product_name']}\n"
            f"💰 <b>Bitim summasi:</b> <b>{format_number(d['amount'])} so'm</b>\n"
            f"🏷 <b>Birlik narxi:</b> {format_number(d['unit_price'])} so'm/{d.get('unit', '')}\n"
            f"⚖️ <b>Hajmi:</b> {format_number(d['quantity'] * d.get('lot', 1))} {d.get('unit', '')}\n"
            f"📍 <b>Hudud:</b> {d['region']}\n\n"
            f"🏢 <b>Sotuvchi:</b> {d.get('seller_name') or d['seller_inn']} (STIR: <code>{d['seller_inn']}</code>)\n"
            f"🛒 <b>Xaridor:</b> {d.get('buyer_name') or d['buyer_inn']} (STIR: <code>{d['buyer_inn']}</code>)\n"
            f"📊 <b>Holati:</b> {d.get('deal_state', '')}"
        )
    else:
        return (
            f"💎 <b>{title_ru} № {deal_num}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📄 <b>Номер контракта:</b> № <code>{contract_num}</code>\n"
            f"📅 <b>Дата:</b> {d['deal_date']}\n"
            f"📦 <b>Товар:</b> {d['product_name']}\n"
            f"💰 <b>Сумма сделки:</b> <b>{format_number(d['amount'])} сум</b>\n"
            f"🏷 <b>Цена за единицу:</b> {format_number(d['unit_price'])} сум/{d.get('unit', '')}\n"
            f"⚖️ <b>Объем:</b> {format_number(d['quantity'] * d.get('lot', 1))} {d.get('unit', '')}\n"
            f"📍 <b>Регион:</b> {d['region']}\n\n"
            f"🏢 <b>Продавец:</b> {d.get('seller_name') or d['seller_inn']} (ИНН: <code>{d['seller_inn']}</code>)\n"
            f"🛒 <b>Покупатель:</b> {d.get('buyer_name') or d['buyer_inn']} (ИНН: <code>{d['buyer_inn']}</code>)\n"
            f"📊 <b>Статус:</b> {d.get('deal_state', '')}"
        )

def format_top_contracts(contracts: List[Dict[str, Any]], lang: str = "uz") -> str:
    """Formats top contracts leaderboard."""
    is_uz = (lang == "uz")
    if is_uz:
        lines = [
            "🏆 <b>ENG YIRIK BIRJA SHARTNOMALARI (TOP-5)</b>",
            "━━━━━━━━━━━━━━━━━━",
        ]
        for idx, c in enumerate(contracts, 1):
            s_name = f" | {c['seller_name']}" if c.get("seller_name") else ""
            lines.append(
                f"<b>{idx}. Shartnoma № {c['contract_number']}</b>\n"
                f"   📦 {c['product_name']}\n"
                f"   💰 Jami aylanma: <b>{format_number(c['total_uzs'])} so'm</b>\n"
                f"   📊 Bitimlar: {format_number(c['deals_count'], 0)} ta | Hajm: {format_number(c.get('total_volume', 0))} {c.get('unit', '')}{s_name}\n"
            )
        return "\n".join(lines)
    else:
        lines = [
            "🏆 <b>ТОП-5 КРУПНЕЙШИХ БИРЖЕВЫХ КОНТРАКТОВ</b>",
            "━━━━━━━━━━━━━━━━━━",
        ]
        for idx, c in enumerate(contracts, 1):
            s_name = f" | {c['seller_name']}" if c.get("seller_name") else ""
            lines.append(
                f"<b>{idx}. Контракт № {c['contract_number']}</b>\n"
                f"   📦 {c['product_name']}\n"
                f"   💰 Общий оборот: <b>{format_number(c['total_uzs'])} сум</b>\n"
                f"   📊 Сделок: {format_number(c['deals_count'], 0)} | Объем: {format_number(c.get('total_volume', 0))} {c.get('unit', '')}{s_name}\n"
            )
        return "\n".join(lines)

def format_top_brokers(brokers: List[Dict[str, Any]], lang: str = "uz") -> str:
    """Formats top brokers leaderboard."""
    is_uz = (lang == "uz")
    if is_uz:
        lines = [
            f"🏛 <b>ENG YIRIK BROKERLIK IDORALARI</b>",
            f"━━━━━━━━━━━━━━━━━━",
        ]
        for idx, b in enumerate(brokers, 1):
            lines.append(
                f"<b>{idx}. {b['name']}</b>\n"
                f"   Kodi: <code>{b['broker_code']}</code> | {b['region']}\n"
                f"   Bitimlar: {format_number(b['deals_count'], 0)} ta | Hajm: <b>{format_number(b['total_volume_uzs'])} so'm</b>\n"
            )
        return "\n".join(lines)
    else:
        lines = [
            f"🏛 <b>ТОП БРОКЕРСКИХ КОНТОР ПО ОБОРОТУ</b>",
            f"━━━━━━━━━━━━━━━━━━",
        ]
        for idx, b in enumerate(brokers, 1):
            lines.append(
                f"<b>{idx}. {b['name']}</b>\n"
                f"   Код: <code>{b['broker_code']}</code> | {b['region']}\n"
                f"   Сделок: {format_number(b['deals_count'], 0)} | Оборот: <b>{format_number(b['total_volume_uzs'])} сум</b>\n"
            )
        return "\n".join(lines)
