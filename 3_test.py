import streamlit as st
import pandas as pd
import os
from streamlit_cookies_manager import EncryptedCookieManager

cookies = EncryptedCookieManager(
    prefix="myapp_",
    password="my_super_secret_key"
)

if not cookies.ready():
    st.stop()

CSV_PATH = "./userinfo.csv"
if not os.path.exists(CSV_PATH):
    df = pd.DataFrame(columns=["username", "password", "role", "count", "logged_in"])
    df.to_csv(CSV_PATH, index=False)
else:
    df = pd.read_csv(CSV_PATH)

username_cookie = cookies.get("username")
role_cookie = cookies.get("role")
logged_in_cookie = cookies.get("logged_in")

# ✅ 改成這樣判斷登入
if logged_in_cookie != "true" or username_cookie == "":
    st.title("🔐 使用 Cookie 驗證登入")

    username = st.text_input("使用者名稱")
    password = st.text_input("密碼", type="password")

    if st.button("登入"):
        user_row = df[(df["username"] == username.strip()) & (df["password"] == password)]

        if not user_row.empty:
            role = user_row.iloc[0]["role"]

            cookies["username"] = username.strip()
            cookies["role"] = role
            cookies["logged_in"] = "true"
            cookies.save()

            df.loc[df["username"] == username.strip(), "logged_in"] = True
            df.to_csv(CSV_PATH, index=False)

            st.success("✅ 登入成功，請重新整理或切換頁面")
            st.rerun()
        else:
            st.error("❌ 使用者名稱或密碼錯誤")

else:
    st.success(f"👤 已登入為：{username_cookie}（角色：{role_cookie}）")

    if st.button("登出"):
        cookies["username"] = ""
        cookies["role"] = ""
        cookies["logged_in"] = "false"
        cookies.save()

        df.loc[df["username"] == username_cookie, "logged_in"] = False
        df.to_csv(CSV_PATH, index=False)

        st.success("✅ 已登出")
        st.rerun()
