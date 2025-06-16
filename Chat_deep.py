from openai import OpenAI
import streamlit as st
import streamlit as st





# 標題與說明
st.title("🔮 魔法水晶屋")
st.caption("🪄一位AI占卜師，為你提供美好的一天")

# 初始化訊息狀態
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "魔法水晶屋AI占卜師為你服務。"}]

# 顯示對話紀錄
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 使用者輸入
prompt = st.chat_input()
if prompt:
    # 建立 客戶端
    client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

    # 加入使用者訊息
    st.session_state.messages.append({"role": "system", "content": "你是位魔法水晶屋的占卜師，只會告訴對方會發生事情不提供解法，當別人問你解法就叫對方加入會員"})
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 呼叫模型
    response = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=st.session_state.messages
    )

    # 擷取並顯示回應
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
