"""
Database Optimization & Summary Tables for Sub-10ms Queries
Pre-computes product summaries, yearly statistics, and optimal indexes.
"""

import sqlite3
import time

def optimize():
    t0 = time.time()
    conn = sqlite3.connect("uzex_data.db")
    cur = conn.cursor()

    print("Building pre-aggregated summary tables...")

    # 1. Product Summary Table
    cur.execute("DROP TABLE IF EXISTS product_summary;")
    cur.execute("""
    CREATE TABLE product_summary AS
    SELECT 
        product_name,
        deal_year,
        unit,
        COUNT(*) as deals_count,
        MIN(unit_price) as min_price,
        MAX(unit_price) as max_price,
        AVG(unit_price) as avg_price,
        SUM(quantity * lot) as total_volume,
        SUM(amount_uzs) as total_amount_uzs
    FROM deals
    WHERE unit_price > 0
    GROUP BY product_name, deal_year, unit;
    """)
    cur.execute("CREATE INDEX idx_prod_sum_name ON product_summary(product_name);")
    cur.execute("CREATE INDEX idx_prod_sum_year ON product_summary(deal_year);")

    # 2. Market Yearly Overview Table
    cur.execute("DROP TABLE IF EXISTS market_yearly_summary;")
    cur.execute("""
    CREATE TABLE market_yearly_summary AS
    SELECT 
        deal_year,
        COUNT(*) as total_deals,
        SUM(amount_uzs) as total_uzs,
        COUNT(DISTINCT seller_inn) as active_sellers,
        COUNT(DISTINCT buyer_inn) as active_buyers,
        COUNT(DISTINCT contract_number) as active_contracts,
        SUM(CASE WHEN deal_state = 'Исполнен' THEN 1 ELSE 0 END) as executed_deals,
        SUM(CASE WHEN deal_state LIKE 'Аннулирован%' THEN 1 ELSE 0 END) as cancelled_deals,
        SUM(CASE WHEN contract_type = 'Экспортный' THEN 1 ELSE 0 END) as export_deals,
        SUM(CASE WHEN contract_type = 'Экспортный' THEN amount ELSE 0 END) as export_amount_usd
    FROM deals
    GROUP BY deal_year;
    """)

    # 3. Top Sellers Summary Table
    cur.execute("DROP TABLE IF EXISTS top_sellers_summary;")
    cur.execute("""
    CREATE TABLE top_sellers_summary AS
    SELECT 
        d.deal_year,
        d.seller_inn,
        COALESCE(p.name, 'Noma''lum') as company_name,
        COALESCE(p.region, d.region) as region,
        COUNT(*) as deals_count,
        SUM(d.amount_uzs) as total_uzs
    FROM deals d
    LEFT JOIN participants p ON p.inn = d.seller_inn
    GROUP BY d.deal_year, d.seller_inn;
    """)
    cur.execute("CREATE INDEX idx_top_sellers_yr_vol ON top_sellers_summary(deal_year, total_uzs DESC);")

    # 4. Top Products Summary Table
    cur.execute("DROP TABLE IF EXISTS top_products_summary;")
    cur.execute("""
    CREATE TABLE top_products_summary AS
    SELECT 
        deal_year,
        product_name,
        unit,
        COUNT(*) as deals_count,
        SUM(quantity * lot) as total_volume,
        SUM(amount_uzs) as total_uzs
    FROM deals
    GROUP BY deal_year, product_name;
    """)
    cur.execute("CREATE INDEX idx_top_prods_yr_cnt ON top_products_summary(deal_year, deals_count DESC);")

    # 5. Composite index for latest deal lookup by product
    cur.execute("CREATE INDEX IF NOT EXISTS idx_deals_prod_num ON deals(product_name, deal_number DESC);")

    conn.commit()
    conn.close()
    print(f"Summary tables and indexes created in {time.time() - t0:.2f}s")

if __name__ == "__main__":
    optimize()
