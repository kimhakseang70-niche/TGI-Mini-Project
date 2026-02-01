import streamlit as st
import time

# ✅ MUST BE FIRST STREAMLIT CALL
st.set_page_config(
    page_title="Niche Shop",
    page_icon="🛍️",
    layout="wide"
)

import re
import pandas as pd
from db import init_db, insert, fetch_latest

# -----------------------------
# Init Neon DB (SAFE)
# -----------------------------
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# -----------------------------
# Validation helpers
# -----------------------------
def is_valid_email(email: str) -> bool:
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

def clean_text(text: str) -> str:
    return text.strip()

# -----------------------------
# UI
# -----------------------------
st.markdown(
    """
    <style>
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.55);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .loading-box {
        background: white;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    </style>
    """,
    unsafe_allow_html=True
)

left_col, right_col = st.columns([1, 2.5], gap="large")

# =============================
# LEFT — Order Form
# =============================
with left_col:
    st.title("🛒 Shopping")
    st.caption("Order anything, get nothing 😄")

    error_box = st.empty()   # 👈 placeholder (prevents jump)
    success_box = st.empty()
    popup = st.empty()

    with st.form("submission_form", clear_on_submit=True):
        customer_name = st.text_input("👤 Customer Name")
        email = st.text_input("📧 Email")
        product_name = st.text_input("🎫 Product Name")
        quantity = st.number_input("🔢 Quantity", min_value=1, step=1)
        note = st.text_area("📝 Optional Note")
        submitted = st.form_submit_button("Save to Database")

# =============================
# RIGHT — Data Preview
# =============================
# TODO add new row without request
with right_col:
    st.title("📊 Order List")
    st.caption("Newest first")

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
# Form submission logic
# -----------------------------
if submitted:
    error_box.empty()
    success_box.empty()
    popup.empty()

    customer_name = clean_text(customer_name).title()
    email = clean_text(email).lower()
    product_name = clean_text(product_name).title()
    note = clean_text(note)

    errors = []

    if not customer_name:
        errors.append("❌ Customer name cannot be empty")

    if not is_valid_email(email):
        errors.append("❌ Email is not valid")

    if not product_name:
        errors.append("❌ Product name cannot be empty")

    if quantity <= 0:
        errors.append("❌ Quantity must be greater than 0")

    if errors:
        error_box.error("\n".join(errors))
    else:
        insert(customer_name, email, product_name, quantity, note)
        # 🔥 ANIME LOADING
        # 🔥 SHOW POPUP LOADING
        popup.markdown(
            """
            <div class="loading-overlay">
                <div class="loading-box">
                    <img src="https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif" width="180">
                    <p>Saving your order… </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        time.sleep(1.5)  # anime delay 😄
        popup.empty()

        st.session_state["just_saved"] = True
        st.rerun()   # 👈 FORCE REFRESH
