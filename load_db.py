"""Midstone 2: load the Kaveri Exports CSVs and answer ten business questions.

Run from the folder containing this file:
    python load_db.py

Optional environment variables:
    DATABASE_URL  Database URL (default: sqlite:///kaveri.db)
    RAW_DIR       CSV folder (default: data/raw)
    REGISTER      Your Intelli register number
"""
import json
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///kaveri.db")
RAW_DIR = os.getenv("RAW_DIR", "data/raw")
REGISTER = os.getenv("REGISTER", "YOUR-REGISTER")
TABLES = ["regions", "customers", "products", "orders", "order_items"]


def clean(name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Apply the three cleaning rules from business_brief.md."""
    # Rule 2: trim spaces around every text value.
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].str.strip()

    # Rule 3: normalize both supported date formats to YYYY-MM-DD.
    if name == "orders":
        iso = pd.to_datetime(df["order_date"], format="%Y-%m-%d", errors="coerce")
        dmy = pd.to_datetime(df["order_date"], format="%d/%m/%Y", errors="coerce")
        parsed = iso.fillna(dmy)
        df["order_date"] = parsed.dt.strftime("%Y-%m-%d")

    # Rule 1: drop exact duplicate rows.
    return df.drop_duplicates().reset_index(drop=True)


def load(engine) -> dict:
    counts = {}
    for name in TABLES:
        path = os.path.join(RAW_DIR, f"{name}.csv")
        df = clean(name, pd.read_csv(path, dtype={"order_date": str}))
        df.to_sql(name, con=engine, if_exists="replace", index=False)
        counts[name] = len(df)
        print(f"{name:12} {len(df):6} rows")
    return counts


# Each query returns one value. substr() works with the ISO date strings
# produced above and is supported by both SQLite and PostgreSQL.
QUESTIONS = {
    "q1": "SELECT COUNT(*) FROM customers",
    "q2": """
        SELECT ROUND(COALESCE(SUM(total_amount), 0), 2)
        FROM orders
        WHERE substr(order_date, 1, 4) = '2024'
    """,
    "q3": """
        SELECT c.country
        FROM orders o
        JOIN customers c ON c.customer_id = o.customer_id
        GROUP BY c.country
        ORDER BY COUNT(*) DESC, c.country ASC
        LIMIT 1
    """,
    "q4": """
        SELECT ROUND(COALESCE(SUM(total_amount), 0), 2)
        FROM orders
        WHERE substr(order_date, 1, 4) = '2023'
    """,
    "q5": """
        SELECT COUNT(*)
        FROM orders
        WHERE LOWER(TRIM(status)) = 'cancelled'
    """,
    "q6": """
        SELECT p.product_name
        FROM order_items oi
        JOIN orders o ON o.order_id = oi.order_id
        JOIN products p ON p.product_id = oi.product_id
        WHERE substr(o.order_date, 1, 4) = '2024'
          AND LOWER(TRIM(o.status)) <> 'cancelled'
        GROUP BY p.product_id, p.product_name
        ORDER BY SUM(oi.line_total) DESC, p.product_name ASC
        LIMIT 1
    """,
    "q7": """
        SELECT ROUND(AVG(total_amount), 2)
        FROM orders
        WHERE substr(order_date, 1, 4) = '2024'
          AND LOWER(TRIM(status)) <> 'cancelled'
    """,
    "q8": """
        SELECT r.region_name
        FROM orders o
        JOIN customers c ON c.customer_id = o.customer_id
        JOIN regions r ON r.region_id = c.region_id
        WHERE substr(o.order_date, 1, 4) = '2024'
        GROUP BY r.region_id, r.region_name
        ORDER BY SUM(o.total_amount) DESC, r.region_name ASC
        LIMIT 1
    """,
    "q9": """
        SELECT substr(order_date, 1, 7) AS revenue_month
        FROM orders
        WHERE substr(order_date, 1, 4) = '2024'
        GROUP BY substr(order_date, 1, 7)
        ORDER BY SUM(total_amount) DESC, revenue_month ASC
        LIMIT 1
    """,
    "q10": """
        SELECT COUNT(*)
        FROM customers c
        WHERE NOT EXISTS (
            SELECT 1
            FROM orders o
            WHERE o.customer_id = c.customer_id
              AND substr(o.order_date, 1, 4) = '2025'
        )
    """,
}


def answer(engine) -> dict:
    out = {}
    with engine.connect() as con:
        for qid, sql in QUESTIONS.items():
            out[qid] = con.execute(text(sql)).scalar()
            print(f"{qid:4} {out[qid]}")
    return out


if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    counts = load(engine)
    answers = answer(engine)
    with open("answers.json", "w", encoding="utf-8") as f:
        json.dump(
            {"register": REGISTER, "row_counts": counts, "answers": answers},
            f,
            indent=2,
        )
    print("wrote answers.json")
