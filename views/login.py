# ==========================================
# 檔案路徑：views/login.py
# 職責：系統登入頁面（支援動態讀取多租戶 Logo 與公司名稱）
# ==========================================

import streamlit as st
import os
from sqlalchemy import text

def render_login_page(db_engine):
    # 嘗試從資料庫或 session_state 讀取最新企業識別
    company_name = st.session_state.get('tenant_company_name', "裕豐電機工業有限公司")
    logo_path = st.session_state.get('tenant_logo_url', "")

    # 置中排版與動態 Logo 渲染
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # 優先顯示動態上傳的 Logo，若無則顯示預設圖示
        if logo_path and os.path.exists(logo_path):
            st.image(logo_path, width=220)
            st.markdown(f"### **{company_name}**")
        else:
            st.markdown("### 🏭 裕豐電機工業 SaaS ERP")
            
        st.caption("請輸入您的企業帳號與密碼進行登入 (Đăng nhập hệ thống)")

        with st.form("login_form"):
            username = st.text_input("帳號 (Username / Mã số)")
            password = st.text_input("密碼 (Password / Mật khẩu)", type="password")
            lang_choice = st.selectbox("系統語系 (Language)", ["繁體中文", "Tiếng Việt"])
            
            submitted = st.form_submit_button("🔒 登入系統 (Login)", type="primary", use_container_width=True)
            
            if submitted:
                if username and password:
                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = username
                    st.session_state['current_lang'] = 'zh' if lang_choice == "繁體中文" else 'vi'
                    st.success("🎉 登入成功！正在進入系統...")
                    st.rerun()
                else:
                    st.warning("⚠️ 請輸入帳號與密碼。")
