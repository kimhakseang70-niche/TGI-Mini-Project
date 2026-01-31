import os
import psycopg2
import psycopg2.extras

DB_URL = os.environ.get("NEON_DATABASE_URL")

CREATE_TABLE_SQL = """
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_SQL = """
INSERT INTO orders (customer_name, email, product_name, quantity, note)
       VALUES (%s, %s, %s, %s, %s)
"""

SELECT_LATEST_SQL = """
SELECT order_id, customer_name, email, product_name, quantity, note, created_at
  FROM orders
 ORDER BY created_at DESC
 LIMIT 20
 ORDER BY id DESC
 LIMIT %s
"""

def get_conn():
    import os
    import streamlit as st
    import psycopg2

    db_url = os.getenv("NEON_DATABASE_URL") or st.secrets.get("NEON_DATABASE_URL")

    if not db_url:
        raise ValueError("NEON_DATABASE_URL is not set in Streamlit Secrets")

    return psycopg2.connect(db_url)



def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)

def insert(customer_name: str, email: str, product_name: str, quantity:int, note: str) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(INSERT_SQL, (customer_name, email, product_name, quantity, note))
            new_id = cur.fetchone()[0]
            return int(new_id)

def fetch_latest(limit: int = 50):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(SELECT_LATEST_SQL, (limit,))
            return cur.fetchall()