# ==========================================
# 檔案路徑：views/login.py
# 職責：系統登入驗證頁面 (帳密驗證、語系選擇、Session 寫入)
# ==========================================

import streamlit as st

def render_login_page(db_conn):
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h2 style='text-align: center;'>🏭 裕豐電機工業 SaaS ERP</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>請輸入您的企業帳號與密碼進行登入</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            username = st.text_input("帳號 (Username / Mã số)", placeholder="請輸入帳號")
            password = st.text_input("密碼 (Password / Mật khẩu)", type="password", placeholder="請輸入密碼")
            
            lang = st.selectbox("系統語系 (Language)", ["繁體中文", "Tiếng Việt"])
            
            if st.button("🔐 登入系統 (Login)", type="primary", use_container_width=True):
                if username and password:
                    # 未來接真實資料庫語句驗證：SELECT * FROM sys_users WHERE username = %s AND password_hash = %s
                    # 此處寫入驗證成功狀態
                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = username
                    st.session_state['current_lang'] = 'zh' if lang == "繁體中文" else 'vi'
                    st.session_state['current_view'] = 'dashboard'
                    st.success("登入成功！正在載入主頁...")
                    st.rerun()
                else:
                    st.error("請完整輸入帳號與密碼！")
