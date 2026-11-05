"""
UZEX Spot Data Ingestion and Database Builder
Transforms 500,000 spot trade records and dimension tables into an indexed,
high-performance SQLite database with Full-Text Search (FTS5).
"""

import os
import sys
import csv
import glob
import time
import sqlite3
from datetime import datetime

DB_PATH = "uzex_data.db"

def clean_num(val):
    if not val or val == "" or val is None:
        return 0.0
    s = str(val).replace(" ", "").replace("\xa0", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0

def clean_int(val):
    if not val or val == "" or val is None:
        return 0
    s = str(val).replace(" ", "").replace("\xa0", "").strip()
    try:
        return int(float(s))
    except ValueError:
        return 0

def parse_date_iso(date_str):
    if not date_str or not isinstance(date_str, str):
        return None, None, None
    parts = date_str.strip().split(".")
    if len(parts) == 3:
        try:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            return f"{year:04d}-{month:02d}-{day:02d}", year, month
        except ValueError:
            return None, None, None
    return None, None, None

def build_database():
    start_time = time.time()
    print("=" * 60)
    print("Starting UZEX SQLite Database Build...")
    print("=" * 60)

    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"Removed existing {DB_PATH}")
        except Exception as e:
            print(f"Warning: could not remove {DB_PATH}: {e}")

    conn = sqlite3.connect(DB_PATH)
    conn.create_function("py_lower", 1, lambda s: s.lower() if s is not None else "")
    cur = conn.cursor()

    # Enable WAL mode and synchronous=NORMAL for fastest bulk inserts and read performance
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")
    cur.execute("PRAGMA cache_size = -64000;") # 64MB cache
    cur.execute("PRAGMA temp_store = MEMORY;")

    # 1. USD Rates Table
    print("\n[1/5] Importing USD Rates...")
    cur.execute("""
    CREATE TABLE usd_rates (
        rate_date TEXT PRIMARY KEY,
        rate_date_iso TEXT,
        rate REAL
    );
    """)
    usd_map = {}
    with open("usd_rates.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows_to_insert = []
        for r in reader:
            if not r or len(r) < 2:
                continue
            d_str = r[0].strip()
            rate = clean_num(r[1])
            iso_d, _, _ = parse_date_iso(d_str)
            usd_map[d_str] = rate
            rows_to_insert.append((d_str, iso_d, rate))
        cur.executemany("INSERT INTO usd_rates VALUES (?, ?, ?)", rows_to_insert)
    print(f"Loaded {len(rows_to_insert)} USD daily exchange rates.")

    # 2. Participants Table
    print("\n[2/5] Importing Market Participants (14,392 companies)...")
    cur.execute("""
    CREATE TABLE participants (
        inn TEXT PRIMARY KEY,
        name TEXT,
        region TEXT,
        activity TEXT,
        role TEXT,
        vat_payer TEXT
    );
    """)
    with open("participants.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows_to_insert = []
        for r in reader:
            if not r or len(r) < 6:
                continue
            rows_to_insert.append((
                str(r[0]).strip(), # INN
                r[1].strip(),      # Name
                r[2].strip(),      # Region
                r[3].strip(),      # Activity
                r[4].strip(),      # Role
                r[5].strip(),      # VAT Payer
            ))
        cur.executemany("INSERT INTO participants VALUES (?, ?, ?, ?, ?, ?)", rows_to_insert)
    print(f"Loaded {len(rows_to_insert)} participants.")

    # 3. Brokers Table
    print("\n[3/5] Importing Brokers (120 firms)...")
    cur.execute("""
    CREATE TABLE brokers (
        broker_code TEXT PRIMARY KEY,
        name TEXT,
        inn TEXT,
        region TEXT
    );
    """)
    with open("brokers.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows_to_insert = []
        for r in reader:
            if not r or len(r) < 4:
                continue
            rows_to_insert.append((
                r[0].strip(),
                r[1].strip(),
                str(r[2]).strip(),
                r[3].strip()
            ))
        cur.executemany("INSERT INTO brokers VALUES (?, ?, ?, ?)", rows_to_insert)
    print(f"Loaded {len(rows_to_insert)} brokers.")

    # 4. Contracts Table
    print("\n[4/5] Importing Contracts (6,616 contracts)...")
    cur.execute("""
    CREATE TABLE contracts (
        contract_number INTEGER PRIMARY KEY,
        product_name TEXT,
        brand TEXT,
        size TEXT,
        grade TEXT,
        type TEXT,
        class_item TEXT,
        tnved_code TEXT,
        group_name TEXT,
        category TEXT,
        industry TEXT,
        unit TEXT,
        lot REAL,
        currency TEXT,
        base_price REAL,
        deposit_percent TEXT,
        delivery_basis TEXT,
        region TEXT,
        warehouse_address TEXT,
        auction_type TEXT,
        contract_type TEXT,
        contract_form TEXT,
        payment_term_days INTEGER,
        delivery_term_days INTEGER,
        packaging TEXT,
        seller_inn TEXT,
        reg_date TEXT,
        valid_till TEXT
    );
    """)
    contract_currency_map = {}
    with open("contracts.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows_to_insert = []
        for r in reader:
            if not r or len(r) < 28:
                continue
            c_num = clean_int(r[0])
            c_curr = r[13].strip()
            contract_currency_map[c_num] = c_curr
            rows_to_insert.append((
                c_num,
                r[1].strip(),
                r[2].strip(),
                r[3].strip(),
                r[4].strip(),
                r[5].strip(),
                r[6].strip(),
                r[7].strip(),
                r[8].strip(),
                r[9].strip(),
                r[10].strip(),
                r[11].strip(),
                clean_num(r[12]),
                c_curr,
                clean_num(r[14]),
                r[15].strip(),
                r[16].strip(),
                r[17].strip(),
                r[18].strip(),
                r[19].strip(),
                r[20].strip(),
                r[21].strip(),
                clean_int(r[22]),
                clean_int(r[23]),
                r[24].strip(),
                str(r[25]).strip(),
                r[26].strip(),
                r[27].strip()
            ))
        cur.executemany("""
        INSERT INTO contracts VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """, rows_to_insert)
    print(f"Loaded {len(rows_to_insert)} contracts.")

    # 5. Deals Tables (500,000 deals)
    print("\n[5/5] Importing 500,000 Deals (2022-2026)...")
    cur.execute("""
    CREATE TABLE deals (
        deal_number INTEGER PRIMARY KEY,
        deal_date TEXT,
        deal_date_iso TEXT,
        deal_year INTEGER,
        deal_month INTEGER,
        deal_time TEXT,
        auction_type TEXT,
        quantity REAL,
        amount REAL,
        amount_uzs REAL,
        start_price REAL,
        unit_price REAL,
        contract_number INTEGER,
        product_name TEXT,
        lot REAL,
        unit TEXT,
        region TEXT,
        contract_type TEXT,
        contract_form TEXT,
        deal_state TEXT,
        seller_inn TEXT,
        buyer_inn TEXT,
        seller_broker TEXT,
        buyer_broker TEXT,
        payment_date TEXT,
        delivery_date TEXT,
        delivered_qty REAL
    );
    """)

    deal_files = sorted(glob.glob("deals_*.csv"))
    total_deals = 0

    for df_path in deal_files:
        t0 = time.time()
        file_rows = []
        with open(df_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            for r in reader:
                if not r or len(r) < 22:
                    continue
                d_num = clean_int(r[0])
                d_date = r[1].strip()
                iso_d, d_year, d_month = parse_date_iso(d_date)
                qty = clean_num(r[4])
                amt = clean_num(r[5])
                st_price = clean_num(r[6])
                c_num = clean_int(r[7])
                p_name = r[8].strip()
                lot = clean_num(r[9])
                unit = r[10].strip()
                region = r[11].strip()
                c_type = r[12].strip()
                c_form = r[13].strip()
                d_state = r[14].strip()
                s_inn = str(r[15]).strip()
                b_inn = str(r[16]).strip()
                s_broker = r[17].strip()
                b_broker = r[18].strip()
                pay_date = r[19].strip()
                deliv_date = r[20].strip()
                deliv_qty = clean_num(r[21])

                # Calculate unit price and amount in UZS
                total_units = qty * lot
                unit_price = (amt / total_units) if total_units > 0 else 0.0

                curr = contract_currency_map.get(c_num, "Узбекский сум")
                if curr == "Доллар США" or c_type == "Экспортный":
                    usd_rate = usd_map.get(d_date, 12500.0)
                    amt_uzs = amt * usd_rate
                else:
                    amt_uzs = amt

                file_rows.append((
                    d_num, d_date, iso_d, d_year, d_month, r[2].strip(),
                    r[3].strip(), qty, amt, amt_uzs, st_price, unit_price,
                    c_num, p_name, lot, unit, region, c_type, c_form,
                    d_state, s_inn, b_inn, s_broker, b_broker,
                    pay_date, deliv_date, deliv_qty
                ))

        cur.executemany("""
        INSERT INTO deals VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """, file_rows)
        conn.commit()
        total_deals += len(file_rows)
        print(f"  Processed {df_path}: {len(file_rows):,} rows ({time.time() - t0:.2f}s)")

    print(f"\nTotal deals inserted: {total_deals:,}")

    # 6. Building High-Performance Indexes
    print("\nCreating B-Tree Indexes for Sub-Millisecond Queries...")
    idx_start = time.time()
    indexes = [
        "CREATE INDEX idx_deals_contract_num ON deals(contract_number);",
        "CREATE INDEX idx_deals_date_iso ON deals(deal_date_iso);",
        "CREATE INDEX idx_deals_year_month ON deals(deal_year, deal_month);",
        "CREATE INDEX idx_deals_seller_inn ON deals(seller_inn);",
        "CREATE INDEX idx_deals_buyer_inn ON deals(buyer_inn);",
        "CREATE INDEX idx_deals_seller_broker ON deals(seller_broker);",
        "CREATE INDEX idx_deals_buyer_broker ON deals(buyer_broker);",
        "CREATE INDEX idx_deals_state ON deals(deal_state);",
        "CREATE INDEX idx_deals_region ON deals(region);",
        "CREATE INDEX idx_deals_prod_name ON deals(product_name);",
        "CREATE INDEX idx_deals_prod_num ON deals(product_name, deal_number DESC);",
        "CREATE INDEX idx_deals_amount_desc ON deals(amount DESC);",
        "CREATE INDEX idx_contracts_seller_inn ON contracts(seller_inn);",
        "CREATE INDEX idx_contracts_category ON contracts(category);",
        "CREATE INDEX idx_contracts_industry ON contracts(industry);",
        "CREATE INDEX idx_participants_name ON participants(name);",
        "CREATE INDEX idx_participants_region ON participants(region);",
        "CREATE INDEX idx_brokers_inn ON brokers(inn);"
    ]
    for sql in indexes:
        cur.execute(sql)
    conn.commit()
    print(f"Indexes created in {time.time() - idx_start:.2f}s")

    # 7. Building Summary Tables for Sub-Millisecond Analytics
    print("\nBuilding Pre-Aggregated Summary Tables for Instant Analytics...")
    sum_start = time.time()
    cur.execute("""
    CREATE TABLE product_summary AS
    SELECT 
        product_name,
        py_lower(product_name) as product_name_lower,
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
    cur.execute("CREATE INDEX idx_prod_sum_lower ON product_summary(product_name_lower);")
    cur.execute("CREATE INDEX idx_prod_sum_year ON product_summary(deal_year);")

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

    cur.execute("""
    CREATE TABLE top_buyers_summary AS
    SELECT 
        d.deal_year,
        d.buyer_inn,
        COALESCE(p.name, 'Noma''lum') as company_name,
        COALESCE(p.region, d.region) as region,
        COUNT(*) as deals_count,
        SUM(d.amount_uzs) as total_uzs
    FROM deals d
    LEFT JOIN participants p ON p.inn = d.buyer_inn
    GROUP BY d.deal_year, d.buyer_inn;
    """)
    cur.execute("CREATE INDEX idx_top_buyers_yr_vol ON top_buyers_summary(deal_year, total_uzs DESC);")

    cur.execute("""
    CREATE TABLE regional_summary AS
    SELECT 
        region,
        deal_year,
        COUNT(*) as deals_count,
        SUM(amount_uzs) as total_uzs,
        COUNT(DISTINCT seller_inn) as sellers_count,
        COUNT(DISTINCT buyer_inn) as buyers_count
    FROM deals
    GROUP BY region, deal_year;
    """)
    cur.execute("CREATE INDEX idx_reg_sum_reg ON regional_summary(region);")

    cur.execute("""
    CREATE TABLE all_time_top_buyers AS
    SELECT 
        buyer_inn,
        company_name,
        region,
        SUM(deals_count) as deals_count,
        SUM(total_uzs) as total_uzs
    FROM top_buyers_summary
    GROUP BY buyer_inn
    ORDER BY total_uzs DESC
    LIMIT 100;
    """)

    cur.execute("""
    CREATE TABLE all_time_top_sellers AS
    SELECT 
        seller_inn,
        company_name,
        region,
        SUM(deals_count) as deals_count,
        SUM(total_uzs) as total_uzs
    FROM top_sellers_summary
    GROUP BY seller_inn
    ORDER BY total_uzs DESC
    LIMIT 100;
    """)

    # Fast Product Top Sellers
    cur.execute("""
    CREATE TABLE product_top_sellers AS
    SELECT 
        d.product_name,
        py_lower(d.product_name) as product_name_lower,
        d.seller_inn,
        p.name as seller_name,
        p.region as seller_region,
        COUNT(*) as deals_count,
        SUM(d.amount) as total_uzs,
        SUM(d.quantity * d.lot) as total_volume,
        d.unit
    FROM deals d
    LEFT JOIN participants p ON d.seller_inn = p.inn
    GROUP BY d.product_name, d.seller_inn;
    """)
    cur.execute("CREATE INDEX idx_pts_prod ON product_top_sellers(product_name);")
    cur.execute("CREATE INDEX idx_pts_lower ON product_top_sellers(product_name_lower);")
    cur.execute("CREATE INDEX idx_pts_total ON product_top_sellers(total_uzs DESC);")

    # Fast Product Top Buyers
    cur.execute("""
    CREATE TABLE product_top_buyers AS
    SELECT 
        d.product_name,
        py_lower(d.product_name) as product_name_lower,
        d.buyer_inn,
        p.name as buyer_name,
        p.region as buyer_region,
        COUNT(*) as deals_count,
        SUM(d.amount) as total_uzs,
        SUM(d.quantity * d.lot) as total_volume,
        d.unit
    FROM deals d
    LEFT JOIN participants p ON d.buyer_inn = p.inn
    GROUP BY d.product_name, d.buyer_inn;
    """)
    cur.execute("CREATE INDEX idx_ptb_prod ON product_top_buyers(product_name);")
    cur.execute("CREATE INDEX idx_ptb_lower ON product_top_buyers(product_name_lower);")
    cur.execute("CREATE INDEX idx_ptb_total ON product_top_buyers(total_uzs DESC);")

    # Fast Top Brokers
    cur.execute("""
    CREATE TABLE top_brokers_summary AS
    SELECT 
        b.broker_code,
        b.name,
        b.inn,
        b.region,
        (
            SELECT COUNT(*) FROM deals WHERE seller_broker = b.broker_code OR buyer_broker = b.broker_code
        ) as deals_count,
        (
            SELECT COALESCE(SUM(amount_uzs), 0) FROM deals WHERE seller_broker = b.broker_code OR buyer_broker = b.broker_code
        ) as total_volume_uzs
    FROM brokers b
    ORDER BY total_volume_uzs DESC;
    """)
    cur.execute("CREATE INDEX idx_tbs_code ON top_brokers_summary(broker_code);")

    conn.commit()
    print(f"Summary tables created in {time.time() - sum_start:.2f}s")

    # 7. Building Full-Text Search (FTS5) Tables
    print("\nCreating Full-Text Search (FTS5) Virtual Tables...")
    fts_start = time.time()
    cur.execute("""
    CREATE VIRTUAL TABLE fts_products USING fts5(
        contract_number UNINDEXED,
        product_name,
        category,
        group_name,
        tokenize='unicode61'
    );
    """)
    cur.execute("""
    INSERT INTO fts_products(contract_number, product_name, category, group_name)
    SELECT contract_number, product_name, category, group_name FROM contracts;
    """)

    cur.execute("""
    CREATE VIRTUAL TABLE fts_participants USING fts5(
        inn UNINDEXED,
        name,
        region,
        activity,
        tokenize='unicode61'
    );
    """)
    cur.execute("""
    INSERT INTO fts_participants(inn, name, region, activity)
    SELECT inn, name, region, activity FROM participants;
    """)
    conn.commit()
    print(f"FTS5 virtual tables populated in {time.time() - fts_start:.2f}s")

    # Verification counts
    cur.execute("SELECT COUNT(*) FROM deals;")
    d_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM contracts;")
    c_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM participants;")
    p_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM brokers;")
    b_count = cur.fetchone()[0]

    conn.close()

    total_time = time.time() - start_time
    db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print("\n" + "=" * 60)
    print("DATABASE BUILD COMPLETED SUCCESSFULLY!")
    print(f"Deals:        {d_count:,}")
    print(f"Contracts:    {c_count:,}")
    print(f"Participants: {p_count:,}")
    print(f"Brokers:      {b_count:,}")
    print(f"DB Size:      {db_size_mb:.2f} MB")
    print(f"Elapsed Time: {total_time:.2f} seconds")
    print("=" * 60)

if __name__ == "__main__":
    build_database()
