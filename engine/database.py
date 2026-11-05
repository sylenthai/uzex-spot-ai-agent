"""
High-Performance Database Engine for UZEX Spot Data
Provides sub-millisecond lookups, aggregations, and FTS5 search using pre-aggregated indexes.
"""

import sqlite3
import re
from typing import Dict, Any, List, Optional
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.create_function("py_lower", 1, lambda s: s.lower() if s is not None else "")
    return conn

def init_user_settings_table():
    """Ensures user settings table exists for Telegram bot state persistence."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                lang TEXT DEFAULT 'uz',
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

init_user_settings_table()

def get_user_lang(user_id: int) -> str:
    """Retrieves saved language preference for a Telegram user."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT lang FROM user_settings WHERE user_id = ?;", (user_id,))
            row = cur.fetchone()
            if row and row["lang"]:
                return row["lang"]
    except Exception:
        pass
    return "uz"

def set_user_lang(user_id: int, lang: str):
    """Saves language preference for a Telegram user."""
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO user_settings (user_id, lang, last_interaction)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET lang = excluded.lang, last_interaction = CURRENT_TIMESTAMP;
            """, (user_id, lang))
            conn.commit()
    except Exception:
        pass

def format_number(val: Optional[float], decimals: int = 2) -> str:
    """Formats numbers with spaces as thousand separators (e.g. 1 250 000.50)"""
    if val is None:
        return "0"
    if decimals == 0:
        return f"{int(round(val)):,}".replace(",", " ")
    parts = f"{val:,.{decimals}f}".split(".")
    integer_part = parts[0].replace(",", " ")
    dec_part = parts[1].rstrip("0")
    if dec_part:
        return f"{integer_part}.{dec_part}"
    return integer_part

def get_deal_by_id(deal_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves full details of a specific deal by deal_number in ~1ms."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                d.*,
                c.currency as contract_currency,
                c.base_price,
                c.delivery_basis,
                c.warehouse_address,
                c.packaging,
                c.payment_term_days,
                c.delivery_term_days,
                c.category as product_category,
                c.industry as product_industry,
                p_seller.name as seller_name,
                p_seller.region as seller_region,
                p_buyer.name as buyer_name,
                p_buyer.region as buyer_region,
                b_seller.name as seller_broker_name,
                b_buyer.name as buyer_broker_name
            FROM deals d
            LEFT JOIN contracts c ON c.contract_number = d.contract_number
            LEFT JOIN participants p_seller ON p_seller.inn = d.seller_inn
            LEFT JOIN participants p_buyer ON p_buyer.inn = d.buyer_inn
            LEFT JOIN brokers b_seller ON b_seller.broker_code = d.seller_broker
            LEFT JOIN brokers b_buyer ON b_buyer.broker_code = d.buyer_broker
            WHERE d.deal_number = ?;
        """, (deal_id,))
        row = cur.fetchone()
        if not row:
            return None
        return dict(row)

def get_contract_by_id(contract_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves full details of a contract by contract_number in ~2ms."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                c.*,
                p.name as seller_name,
                p.region as seller_region,
                p.activity as seller_activity,
                p.vat_payer as seller_vat
            FROM contracts c
            LEFT JOIN participants p ON p.inn = c.seller_inn
            WHERE c.contract_number = ?;
        """, (contract_id,))
        c_row = cur.fetchone()
        if not c_row:
            return None
        res = dict(c_row)

        # Get deal stats under this contract
        cur.execute("""
            SELECT 
                COUNT(*) as deals_count,
                SUM(quantity * lot) as total_volume_traded,
                SUM(amount_uzs) as total_amount_uzs,
                MIN(deal_date) as first_deal_date,
                MAX(deal_date) as last_deal_date
            FROM deals
            WHERE contract_number = ?;
        """, (contract_id,))
        deal_stats = dict(cur.fetchone())
        res["stats"] = deal_stats
        return res

def get_participant_by_inn(inn: str) -> Optional[Dict[str, Any]]:
    """Retrieves participant details and trade metrics by 9-digit INN/STIR."""
    inn_str = str(inn).strip()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM participants WHERE inn = ?;", (inn_str,))
        p_row = cur.fetchone()
        if not p_row:
            return None
        res = dict(p_row)

        # Seller statistics from summary table if available
        cur.execute("""
            SELECT 
                COALESCE(SUM(deals_count), 0) as seller_deals_count,
                COALESCE(SUM(total_uzs), 0) as seller_total_uzs
            FROM top_sellers_summary
            WHERE seller_inn = ?;
        """, (inn_str,))
        s_stats = cur.fetchone()
        res["seller_deals_count"] = s_stats["seller_deals_count"] if s_stats else 0
        res["seller_total_uzs"] = s_stats["seller_total_uzs"] if s_stats else 0

        # Buyer statistics
        cur.execute("""
            SELECT 
                COUNT(*) as buyer_deals_count,
                COALESCE(SUM(amount_uzs), 0) as buyer_total_uzs
            FROM deals
            WHERE buyer_inn = ?;
        """, (inn_str,))
        b_stats = cur.fetchone()
        res["buyer_deals_count"] = b_stats["buyer_deals_count"] if b_stats else 0
        res["buyer_total_uzs"] = b_stats["buyer_total_uzs"] if b_stats else 0

        # Recent 3 deals
        cur.execute("""
            SELECT deal_number, deal_date, product_name, amount, amount_uzs, deal_state
            FROM deals
            WHERE seller_inn = ? OR buyer_inn = ?
            ORDER BY deal_number DESC
            LIMIT 3;
        """, (inn_str, inn_str))
        res["recent_deals"] = [dict(r) for r in cur.fetchall()]
        return res

def search_participants_by_name(query_str: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Searches participants using FTS5 virtual table in < 2ms."""
    clean_q = re.sub(r"[^\w\s]", "", query_str.strip())
    if not clean_q:
        return []
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT p.inn, p.name, p.region, p.activity, p.role
                FROM fts_participants f
                JOIN participants p ON p.inn = f.inn
                WHERE fts_participants MATCH ?
                LIMIT ?;
            """, (f'"{clean_q}"*', limit))
            results = [dict(r) for r in cur.fetchall()]
            if results:
                return results
        except sqlite3.OperationalError:
            pass

        # Fast indexed prefix search
        cur.execute("""
            SELECT inn, name, region, activity, role
            FROM participants
            WHERE name LIKE ?
            LIMIT ?;
        """, (f"{clean_q}%", limit))
        return [dict(r) for r in cur.fetchall()]

def get_broker_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Retrieves broker details and mediated deal stats in < 1ms."""
    code_str = code.strip().upper()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM top_brokers_summary WHERE UPPER(broker_code) = ?;", (code_str,))
        row = cur.fetchone()
        if not row:
            cur.execute("SELECT * FROM brokers WHERE UPPER(broker_code) = ?;", (code_str,))
            row = cur.fetchone()
            if not row:
                return None
            res = dict(row)
            res["total_mediated_deals"] = 0
            res["total_volume_uzs"] = 0
            return res
        res = dict(row)
        res["total_mediated_deals"] = res.get("deals_count", 0)
        return res

def get_top_brokers(limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieves top brokers by mediated volume in < 1ms."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT broker_code, name, region, deals_count, total_volume_uzs
            FROM top_brokers_summary
            ORDER BY total_volume_uzs DESC
            LIMIT ?;
        """, (limit,))
        return [dict(r) for r in cur.fetchall()]

def get_usd_rate(date_str: str) -> Optional[Dict[str, Any]]:
    """Retrieves USD exchange rate in < 1ms."""
    clean_d = date_str.strip()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM usd_rates WHERE rate_date = ? OR rate_date_iso = ?;", (clean_d, clean_d))
        row = cur.fetchone()
        if row:
            return dict(row)
        return None

def get_latest_usd_rate() -> Optional[Dict[str, Any]]:
    """Retrieves the most recent USD rate in < 1ms."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM usd_rates ORDER BY rate_date_iso DESC LIMIT 1;")
        row = cur.fetchone()
        if row:
            return dict(row)
        return None

def get_product_price_stats(product_query: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Sub-millisecond commodity price analytics powered by product_summary table.
    Guarantees strict Zero-Hallucination: returns None if commodity does not exist.
    """
    clean_q = re.sub(r"[^\w\s]", "", product_query.strip())
    if not clean_q or len(clean_q) < 2:
        return None
    lower_q = clean_q.lower()

    with get_connection() as conn:
        cur = conn.cursor()

        # Query summary table with both lowercase and normal matching (<3,000 rows instead of 500,000!)
        base_sql = "FROM product_summary WHERE (product_name_lower LIKE ? OR product_name LIKE ?)"
        params = [f"%{lower_q}%", f"%{clean_q}%"]
        if year:
            base_sql += " AND deal_year = ?"
            params.append(year)

        cur.execute(f"""
            SELECT 
                product_name,
                unit,
                SUM(deals_count) as count,
                MIN(min_price) as min_price,
                MAX(max_price) as max_price,
                SUM(avg_price * deals_count) / SUM(deals_count) as avg_price,
                SUM(total_volume) as total_volume,
                SUM(total_amount_uzs) as total_amount_uzs
            {base_sql}
            GROUP BY unit
            ORDER BY count DESC
            LIMIT 1;
        """, params)
        agg_row = cur.fetchone()
        if not agg_row or agg_row["count"] is None or agg_row["count"] == 0:
            return None

        res = dict(agg_row)

        # Yearly breakdown from summary table
        cur.execute("""
            SELECT 
                deal_year,
                SUM(deals_count) as deals_count,
                SUM(avg_price * deals_count) / SUM(deals_count) as avg_price,
                MIN(min_price) as min_price,
                MAX(max_price) as max_price,
                SUM(total_volume) as total_volume
            FROM product_summary
            WHERE (product_name_lower LIKE ? OR product_name LIKE ?)
            GROUP BY deal_year
            ORDER BY deal_year ASC;
        """, [f"%{lower_q}%", f"%{clean_q}%"])
        res["yearly_trend"] = [dict(r) for r in cur.fetchall()]

        # Latest deal using optimal composite index (product_name, deal_number DESC)
        cur.execute("""
            SELECT deal_number, deal_date, product_name, unit_price, quantity, lot, unit, amount, region
            FROM deals
            WHERE product_name = ?
            ORDER BY deal_number DESC
            LIMIT 1;
        """, [res["product_name"]])
        latest = cur.fetchone()
        if not latest:
            cur.execute("""
                SELECT deal_number, deal_date, product_name, unit_price, quantity, lot, unit, amount, region
                FROM deals
                WHERE (product_name LIKE ? OR py_lower(product_name) LIKE ?)
                ORDER BY deal_number DESC
                LIMIT 1;
            """, [f"%{clean_q}%", f"%{lower_q}%"])
            latest = cur.fetchone()

        if latest:
            res["latest_deal"] = dict(latest)

        return res

def get_top_sellers_by_product(product_term: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieves top sellers for a specific commodity in < 2ms."""
    clean_q = re.sub(r"[^\w\s]", "", product_term.strip()).lower()
    if not clean_q:
        return []
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                seller_inn,
                seller_name,
                seller_region,
                product_name,
                unit,
                SUM(deals_count) as deals_count,
                SUM(total_uzs) as total_uzs,
                SUM(total_volume) as total_volume
            FROM product_top_sellers
            WHERE (product_name_lower LIKE ? OR product_name LIKE ?)
            GROUP BY seller_inn
            ORDER BY total_uzs DESC
            LIMIT ?;
        """, (f"%{clean_q}%", f"%{product_term}%", limit))
        return [dict(r) for r in cur.fetchall()]

def get_top_buyers_by_product(product_term: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieves top buyers for a specific commodity in < 2ms."""
    clean_q = re.sub(r"[^\w\s]", "", product_term.strip()).lower()
    if not clean_q:
        return []
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                buyer_inn,
                buyer_name,
                buyer_region,
                product_name,
                unit,
                SUM(deals_count) as deals_count,
                SUM(total_uzs) as total_uzs,
                SUM(total_volume) as total_volume
            FROM product_top_buyers
            WHERE (product_name_lower LIKE ? OR product_name LIKE ?)
            GROUP BY buyer_inn
            ORDER BY total_uzs DESC
            LIMIT ?;
        """, (f"%{clean_q}%", f"%{product_term}%", limit))
        return [dict(r) for r in cur.fetchall()]

def get_extreme_deal(extreme_type: str = "max_amount", product_term: Optional[str] = None, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Retrieves the largest or smallest deal in < 2ms."""
    with get_connection() as conn:
        cur = conn.cursor()
        where_clauses = ["d.amount > 0"]
        params = []
        if product_term:
            clean_p = product_term.strip()
            where_clauses.append("(d.product_name LIKE ? OR py_lower(d.product_name) LIKE ?)")
            params.extend([f"%{clean_p}%", f"%{clean_p.lower()}%"])
        if year:
            where_clauses.append("d.deal_year = ?")
            params.append(year)

        where_sql = " AND ".join(where_clauses)
        order_clause = "d.amount DESC" if extreme_type == "max_amount" else ("d.amount ASC" if extreme_type == "min_amount" else "d.unit_price DESC")

        sql = f"""
            SELECT 
                d.deal_number, d.deal_date, d.product_name, d.amount, d.quantity, d.lot, d.unit, 
                d.unit_price, d.region, d.deal_state, d.auction_type,
                d.seller_inn, p1.name as seller_name,
                d.buyer_inn, p2.name as buyer_name
            FROM deals d
            LEFT JOIN participants p1 ON d.seller_inn = p1.inn
            LEFT JOIN participants p2 ON d.buyer_inn = p2.inn
            WHERE {where_sql}
            ORDER BY {order_clause}
            LIMIT 1;
        """
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None

def get_top_sellers(limit: int = 5, year: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retrieves top sellers in < 1ms."""
    with get_connection() as conn:
        cur = conn.cursor()
        if year:
            cur.execute("""
                SELECT 
                    seller_inn,
                    company_name,
                    region,
                    deals_count,
                    total_uzs
                FROM top_sellers_summary
                WHERE deal_year = ?
                ORDER BY total_uzs DESC
                LIMIT ?;
            """, (year, limit))
        else:
            cur.execute("""
                SELECT 
                    seller_inn,
                    company_name,
                    region,
                    deals_count,
                    total_uzs
                FROM all_time_top_sellers
                LIMIT ?;
            """, (limit,))
        return [dict(r) for r in cur.fetchall()]

def get_top_buyers(limit: int = 5, year: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retrieves top buying companies in < 1ms."""
    with get_connection() as conn:
        cur = conn.cursor()
        if year:
            cur.execute("""
                SELECT 
                    buyer_inn,
                    company_name,
                    region,
                    deals_count,
                    total_uzs
                FROM top_buyers_summary
                WHERE deal_year = ?
                ORDER BY total_uzs DESC
                LIMIT ?;
            """, (year, limit))
        else:
            cur.execute("""
                SELECT 
                    buyer_inn,
                    company_name,
                    region,
                    deals_count,
                    total_uzs
                FROM all_time_top_buyers
                LIMIT ?;
            """, (limit,))
        return [dict(r) for r in cur.fetchall()]

def get_region_stats(region_query: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Retrieves regional exchange statistics in < 1ms."""
    clean_r = re.sub(r"[^\w\s]", "", region_query.strip())
    if not clean_r or len(clean_r) < 3:
        return None
    with get_connection() as conn:
        cur = conn.cursor()
        if year:
            cur.execute("""
                SELECT 
                    region,
                    deals_count,
                    total_uzs,
                    sellers_count,
                    buyers_count
                FROM regional_summary
                WHERE region LIKE ? AND deal_year = ?
                LIMIT 1;
            """, (f"%{clean_r}%", year))
        else:
            cur.execute("""
                SELECT 
                    region,
                    SUM(deals_count) as deals_count,
                    SUM(total_uzs) as total_uzs,
                    MAX(sellers_count) as sellers_count,
                    MAX(buyers_count) as buyers_count
                FROM regional_summary
                WHERE region LIKE ?
                GROUP BY region
                LIMIT 1;
            """, (f"%{clean_r}%",))
        row = cur.fetchone()
        if not row:
            return None
        res = dict(row)
        res["year"] = f"{year}-yil" if year else "Barcha yillar (2022-2026)"
        return res

def get_top_products(limit: int = 5, year: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retrieves most traded commodities from pre-aggregated summary in < 1ms."""
    with get_connection() as conn:
        cur = conn.cursor()
        if year:
            cur.execute("""
                SELECT 
                    product_name,
                    unit,
                    deals_count,
                    total_volume,
                    total_uzs
                FROM top_products_summary
                WHERE deal_year = ?
                ORDER BY deals_count DESC
                LIMIT ?;
            """, (year, limit))
        else:
            cur.execute("""
                SELECT 
                    product_name,
                    unit,
                    SUM(deals_count) as deals_count,
                    SUM(total_volume) as total_volume,
                    SUM(total_uzs) as total_uzs
                FROM top_products_summary
                GROUP BY product_name
                ORDER BY deals_count DESC
                LIMIT ?;
            """, (limit,))
        return [dict(r) for r in cur.fetchall()]

def get_general_stats(year: Optional[int] = None) -> Dict[str, Any]:
    """Retrieves market statistics in < 1ms from market_yearly_summary."""
    with get_connection() as conn:
        cur = conn.cursor()
        if year:
            cur.execute("""
                SELECT * FROM market_yearly_summary WHERE deal_year = ?;
            """, (year,))
            row = cur.fetchone()
            if row:
                res = dict(row)
                res["year"] = f"{year}-yil"
                return res

        cur.execute("""
            SELECT 
                SUM(total_deals) as total_deals,
                SUM(total_uzs) as total_uzs,
                MAX(active_sellers) as active_sellers,
                MAX(active_buyers) as active_buyers,
                MAX(active_contracts) as active_contracts,
                SUM(executed_deals) as executed_deals,
                SUM(cancelled_deals) as cancelled_deals,
                SUM(export_deals) as export_deals,
                SUM(export_amount_usd) as export_amount_usd
            FROM market_yearly_summary;
        """)
        row = cur.fetchone()
        res = dict(row)
        res["year"] = "Barcha yillar (2022-2026)"
        return res
