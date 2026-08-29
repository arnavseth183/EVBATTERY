"""
Streamlit Login Interface with Secure Recovery
"""

import streamlit as st
from security.wallet_auth import WalletAuth

auth = WalletAuth()

st.title("AI Blockchain Trading Platform")

menu = ["Login", "Register", "Forgot Password"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------------------------------
# SESSION INIT
# ---------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------------------------------
# REGISTER
# ---------------------------------------
if choice == "Register":

    st.subheader("Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):

        wallet = auth.register_user(username, password)

        st.success("Account Created")

        st.write("Wallet Address:", wallet["address"])
        st.write("Private Key:", wallet["private_key"])
        st.warning("⚠️ Save private key safely! If lost, account cannot be recovered.")

        st.session_state.user = {
            "username": username,
            "wallet": wallet["address"],
            "balance": wallet.get("balance", 10000)
        }

        st.info("User session created. You can now trade.")

# ---------------------------------------
# LOGIN
# ---------------------------------------
elif choice == "Login":

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        user = auth.login(username, password)

        if user:

            st.success("Login Successful")

            st.session_state.user = {
                "username": username,
                "wallet": user["address"],
                "balance": user.get("balance", 10000)
            }

            st.write("Wallet Address:", user["address"])
            st.write("Balance: ₹", user["balance"])

            st.info("Session initialized for trading system")

        else:
            st.error("Invalid Credentials")

# ---------------------------------------
# FORGOT PASSWORD (NEW FEATURE)
# ---------------------------------------
elif choice == "Forgot Password":

    st.subheader("🔑 Recover Account")

    username = st.text_input("Enter Username")
    private_key = st.text_input("Enter Private Key", type="password")

    new_password = st.text_input("Enter New Password", type="password")

    if st.button("Reset Password"):

        if not username or not private_key or not new_password:
            st.error("All fields are required")
        else:
            try:
                # 🔥 Verify ownership using private key
                verified = auth.verify_private_key(username, private_key)

                if verified:
                    auth.update_password(username, new_password)

                    st.success("✅ Password Reset Successful")
                    st.info("You can now login with your new password")

                else:
                    st.error("❌ Invalid private key. Access denied.")

            except Exception as e:
                st.error(f"Recovery failed: {e}")

    st.warning("⚠️ If you lose your private key, your account cannot be recovered.")

# ---------------------------------------
# ACTIVE SESSION VIEW
# ---------------------------------------
if st.session_state.user:
    st.markdown("---")
    st.subheader("Active Session")
    st.json(st.session_state.user)