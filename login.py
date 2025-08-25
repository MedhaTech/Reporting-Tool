import streamlit as st
import json
import os
import hashlib

CREDENTIALS_FILE = "users.json"

# --------- Password Hashing ---------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --------- Load Users from File ---------
def load_users():
    # Default user
    default_users = {
        "reports@medhatech.in": {
            "password": hash_password("medhatech")
        }
    }
    if not os.path.exists(CREDENTIALS_FILE):
        save_users(default_users)
        return default_users
    try:
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default_users

# --------- Save Users to File ---------
def save_users(users):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# --------- Login UI ---------
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        users = load_users()
        hashed = hash_password(password)
        if username in users and users[username]["password"] == hashed:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Logged in successfully")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# --------- Logout Function ---------
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()
