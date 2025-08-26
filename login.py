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
    if not os.path.exists(CREDENTIALS_FILE):
        return {}
    try:
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

# --------- Save Users to File ---------
def save_users(users):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# --------- Login / SignUp UI ---------
def login_page():
    st.title("🔐 Login ")

    #tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Reset Password"])
    tab1, = st.tabs(["Login"])

    # ---------- LOGIN ----------
    with tab1:
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

    # ---------- SIGN UP ----------
#    with tab2:
#       new_username = st.text_input("New Username", key="signup_username")
 #       new_password = st.text_input("New Password", type="password", key="signup_password")
  #      confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
#
 #       if st.button("Sign Up"):
  #          users = load_users()
   #         if new_username in users:
    #            st.error("❌ Username already exists")
     #          st.error("❌ Passwords do not match")
      #      else:
       #         users[new_username] = {"password": hash_password(new_password)}
        #        save_users(users)
         #       st.success("✅ Account created! You can now log in.")
#
    # ---------- RESET PASSWORD ----------
 #   with tab3:
  #      reset_username = st.text_input("Username", key="reset_username")
   #     reset_password1 = st.text_input("New Password", type="password", key="reset_password")
    #    reset_password2 = st.text_input("Confirm New Password", type="password", key="reset_confirm")
#
 #       if st.button("Reset Password"):
  #          users = load_users()
   #         if reset_username not in users:
    #            st.error("❌ Username does not exist")
     #       elif reset_password1 != reset_password2:
      #          st.error("❌ Passwords do not match")
       #     else:
        #        users[reset_username]["password"] = hash_password(reset_password1)
         #      st.success("✅ Password reset successfully")


# --------- Logout Function ---------
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()
