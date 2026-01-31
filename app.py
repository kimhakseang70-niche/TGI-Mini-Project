import re
import pandas as pd
import streamlit as st
from db import init_db, insert, fetch_latest

st.set_page_config(page_title="Niche Shop", page_icon="🛍️", layout="centered")

# -----------------------------
# Init Neon DB
# -----------------------------
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(
    page_title="Niche Shop",
    page_icon="🛍️",
    layout="wide"   # 👈 FULL SCREEN
)

# st.title("🛒 Order anything")
# st.caption("Submit the form. Data is saved to Postgres and shown below.")

# with st.form("submission_form", clear_on_submit=True):
#     customer_name = st.text_input("👤 Customer Name")
#     email = st.text_input("📧 Email")
#     product_name = st.text_input("🎫 Product / Event Name")
#     quantity = st.number_input("🔢 Quantity", min_value=1, step=1)
#     note = st.text_area("📝 Optional Note")
#     submitted = st.form_submit_button("Save to Database")

left_col, right_col = st.columns([1, 2.5], gap="large")


# =============================
# RIGHT SIDE — Order Form
# =============================
with left_col:
    st.title("🛒 Order anything")
    st.caption("Submit the form. Data is saved to Postgres.")

    with st.form("submission_form", clear_on_submit=True):
        customer_name = st.text_input("👤 Customer Name")
        email = st.text_input("📧 Email")
        product_name = st.text_input("🎫 Product / Event Name")
        quantity = st.number_input("🔢 Quantity", min_value=1, step=1)
        note = st.text_area("📝 Optional Note")
        submitted = st.form_submit_button("Save to Database")


# =============================
# LEFT SIDE — Data Preview
# =============================
with right_col:
    st.title("📊 Order Entry Form")
    st.caption("Latest submissions (newest first)")

    message_box = st.empty()
    
    try:
        rows = fetch_latest(50)
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No records yet.")
    except Exception as e:
        st.error("Could not fetch rows from the database.")
        st.code(str(e))

# -----------------------------
# Validation helpers
# -----------------------------
def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def clean_text(text: str) -> str:
    return text.strip()

# -----------------------------
# Validation logic (VERY IMPORTANT)
# -----------------------------
if submitted:
    errors = []

    customer_name = clean_text(customer_name).title()
    email = clean_text(email).lower()
    product_name = clean_text(product_name).title()
    note = clean_text(note)

    if not customer_name:
        st.error("Customer name cannot be empty")

    if not is_valid_email(email):
        st.error("Email is not valid")

    if not product_name:
        st.error("Product name cannot be empty")

    if quantity <= 0:
        st.error("Quantity must be greater than 0")

    if errors:
        for err in errors:
            st.error(err)
    else:
        insert(customer_name, email, product_name, quantity, note)
        st.success("✅ Order saved successfully!")
st.divider()

# st.divider()
# st.subheader("📄 Latest Submissions")

# -----------------------------
# Data Preview (Quality Check)
# -----------------------------
# st.title("📊 Order Entry Form")
# try:
#     rows = fetch_latest(50)
#     if rows:
#         df = pd.DataFrame(rows)
#         st.dataframe(df, use_container_width=True)
#     else:
#         st.info("No records yet. Submit the form above.")
# except Exception as e:
#     st.error("Could not fetch rows from the database.")
#     st.code(str(e))

