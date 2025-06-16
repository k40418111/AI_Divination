from openai import OpenAI
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
import pandas as pd
import os

cookies = EncryptedCookieManager(
    prefix="myapp_",
    password="my_super_secret_key"
)

if not cookies.ready():
    st.stop()

# 正確的 CSV 絕對路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "userinfo.csv")
#CSV_PATH = "./userinfo.csv"
#CSV_PATH = r"C:\Users\Aict Lab702\Documents\llm-Cloude\userinfo.csv"
if not os.path.exists(CSV_PATH):
    df = pd.DataFrame(columns=["username", "password", "role", "count", "logged_in"])
    df.to_csv(CSV_PATH, index=False)
else:
    df = pd.read_csv(CSV_PATH)

username_cookie = cookies.get("username")
role_cookie = cookies.get("role")
logged_in_cookie = cookies.get("logged_in")

# 初始化狀態
# 初始化狀態（從 cookie 同步）
if "logged_in" not in st.session_state:
    st.session_state.logged_in = (logged_in_cookie == "true")
if "username" not in st.session_state:
    st.session_state.username = username_cookie or ""
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "魔法水晶屋AI占卜師為你服務。"}]
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0



st.markdown(
    """
    <style>
    html, body, .stApp, .stAppHeader, .stBottomBlockContainer {
        background-color: #fde2e4	;  /* 背景 */
    }
    </style>
    """,
    unsafe_allow_html=True
)
with st.sidebar:
    if st.session_state.get("logged_in", False):
        st.markdown(f"👤 歡迎，{st.session_state.username}（角色：{cookies.get('role')}）")
        if st.button("🚪 登出"):
            cookies["username"] = ""
            cookies["role"] = ""
            cookies["logged_in"] = "false"
            cookies.save()

            df.loc[df["username"] == st.session_state.username, "logged_in"] = False
            df.to_csv(CSV_PATH, index=False)

            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("✅ 已登出")
            st.rerun()
    else:
        st.subheader("🔐 會員登入")
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("使用者名稱")
            password = st.text_input("密碼", type="password")
            submitted = st.form_submit_button("登入")

        if submitted:
            user_row = df[(df["username"] == username.strip()) & (df["password"] == password)]
            if not user_row.empty:
                role = user_row.iloc[0]["role"]

                cookies["username"] = username.strip()
                cookies["role"] = role
                cookies["logged_in"] = "true"
                cookies.save()

                df.loc[df["username"] == username.strip(), "logged_in"] = True
                df.to_csv(CSV_PATH, index=False)

                st.session_state.logged_in = True
                st.session_state.username = username.strip()
                st.success("✅ 登入成功，歡迎使用！")
                st.rerun()
            else:
                st.error("❌ 使用者名稱或密碼錯誤")




# === 判斷登入狀態 ===
if st.session_state.get("show_login", False) and not st.session_state.get("logged_in", False):
    with st.form("login_form", clear_on_submit=True):
        st.subheader("🔐 會員登入")
        username = st.text_input("使用者名稱")
        password = st.text_input("密碼", type="password")
        submitted = st.form_submit_button("登入")

        if submitted:
            user_row = df[(df["username"] == username.strip()) & (df["password"] == password)]
            if not user_row.empty:
                role = user_row.iloc[0]["role"]

                cookies["username"] = username.strip()
                cookies["role"] = role
                cookies["logged_in"] = "true"
                cookies.save()

                df.loc[df["username"] == username.strip(), "logged_in"] = True
                df.to_csv(CSV_PATH, index=False)

                # 設定狀態
                st.session_state.logged_in = True
                st.session_state.username = username.strip()
                st.session_state.show_login = False  # 關閉登入畫面
                st.success("✅ 登入成功，歡迎使用！")
                st.rerun()
            else:
                st.error("❌ 使用者名稱或密碼錯誤")



# 🎯 中間主畫面
# 標題與說明
st.title("🔮 魔法水晶屋")
st.caption("🪄一位AI占卜師，為你提供美好的一天")

# 初始化訊息狀態

if st.session_state.logged_in:
    st.session_state["messages"] = [{"role": "assistant", "content": f"魔法水晶屋AI占卜師為尊貴的{st.session_state.username}會員服務。"}]
else:
    st.session_state["messages"] = [{"role": "assistant", "content": "魔法水晶屋AI占卜師為您服務。"}]

# 顯示對話紀錄
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 使用者輸入
prompt = st.chat_input()
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )
    
    #登入後，語氣改變
    if st.session_state.logged_in:
        system_prompt = f"你是魔法水晶屋的占卜師，現在對方是會員 {st.session_state.username}，提供完整預測與解法。你說到可以破財消災時推薦我們的扛災玉鐲499元，需要招財時推薦招財金牌9999元，以及19999元心靈課程"

        st.session_state.messages.insert(1, {"role": "system", "content": system_prompt})

        response = client.chat.completions.create(
         model="deepseek/deepseek-chat-v3-0324:free",
         messages=st.session_state.messages,
        )

        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)
    else:
         if st.session_state.usage_count < 3:
            st.session_state.usage_count += 1  # 每次使用+1
            system_prompt = "你是位魔法水晶屋的占卜師，只會告訴對方會發生的事情，不提供解法，當別人問你解法就請對方點擊左上角登入會員。"
            st.session_state.messages.insert(1, {"role": "system", "content": system_prompt})

            response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=st.session_state.messages,)
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.chat_message("assistant").write(reply)
         else:
          st.chat_message("assistant").write("🛑 免費占卜次數已用完。請點擊右上角登入會員以獲得完整服務 💎")





# 廣告彈出視窗（未登入才顯示）
if not st.session_state.logged_in:
    st.markdown("""
<style>
@keyframes borderFlash {
    0% { border-color: #ff6ec4; }
    50% { border-color: #7873f5; }
    100% { border-color: #ff6ec4; }
}

@keyframes slideInLeft {
    from { left: -250px; opacity: 0; }
    to { left: 10px; opacity: 1; }
}
@keyframes slideInRight {
    from { right: -250px; opacity: 0; }
    to { right: 10px; opacity: 1; }
}

.popup-ad {
    position: fixed;
    top: 100px;
    width: 300px;
    height: 750px;
    background: linear-gradient(135deg, #fffbe6, #ffe8f0);
    border: 3px solid #ff6ec4;
    animation: borderFlash 2s infinite;
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
    z-index: 9999;
    padding: 15px;
    font-size: 15px;
    text-align: center;
    overflow: hidden;
    border-radius: 15px;
}

.popup-left {
    animation: slideInLeft 1s ease-out;
    left: 10px;
}

.popup-right {
    animation: slideInRight 1s ease-out;
    right: 10px;
}

.popup-ad img {
    width: 100%;
    height: auto;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    margin-bottom: 10px;
}

.popup-close {
    position: absolute;
    top: 5px;
    right: 8px;
    cursor: pointer;
    color: #888;
    font-size: 18px;
}

.popup-ad a {
    color: #d13cbe;
    font-weight: bold;
    text-decoration: none;
}
</style>

<!-- 左邊廣告 -->
<div class="popup-ad popup-left" id="left-ad">
    <div class="popup-close" onclick="document.getElementById('left-ad').style.display='none'">✖</div>
    <img src="https://placehold.co/200x120/FFB6C1/000000?text=加入會員">
    <p>🌟 <strong>會員專屬預測</strong> 開啟中！</p>
    <p>⏳ 立即登入，解鎖你的專屬魔法✨</p>
    <a href="#">👉 了解詳情</a>
</div>

<!-- 右邊廣告 -->
<div class="popup-ad popup-right" id="right-ad">
    <div class="popup-close" onclick="document.getElementById('right-ad').style.display='none'">✖</div>
    <img src="https://placehold.co/200x120/87CEFA/000000?text=限時優惠">
    <p>🎁 <strong>只到今天！</strong></p>
    <p>🧿 預約 1 對 1 占卜諮詢 🕊️</p>
    <a href="#">🚪 點我進入</a>
</div>
""", unsafe_allow_html=True)
