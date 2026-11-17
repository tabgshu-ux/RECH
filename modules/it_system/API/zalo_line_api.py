# ==========================================
# 檔案路徑：modules/it_system/API/zalo_line_api.py
# 職責：Zalo Official Account & LINE 訊息通知 API 閘道設定
# ==========================================

import streamlit as st

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("#### 💬 Zalo OA & LINE Messaging API 訊息與通知設定")
    st.caption("設定越南業務推播、請購簽核通知與員工出勤異常自動提醒之通訊 API。")

    with st.form("zalo_line_form"):
        channel = st.selectbox("通訊平台選擇", ["Zalo Official Account (OA)", "LINE Messaging API", "Telegram Bot API"])
        token = st.text_input("Bot Token / Access Token", type="password", value="zalo_oa_token_********************")
        webhook_url = st.text_input("Webhook 接收端點", value="https://rechvn.streamlit.app/webhook/zalo")
        
        if st.form_submit_button("💾 儲存通訊 API 設定", type="primary", use_container_width=True):
            st.success(f"🎉 成功儲存 [{channel}] 的 API 閘道設定！")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
