import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

cookies = EncryptedCookieManager(
    prefix="myapp_",
    password="my_super_secret_key"
)

if not cookies.ready():
    st.stop()
username_cookie = cookies.get("username")
role_cookie = cookies.get("role")
logged_in_cookie = cookies.get("logged_in")


st.write(username_cookie)
st.write(role_cookie)
st.write(logged_in_cookie)