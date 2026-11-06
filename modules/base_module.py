# ==========================================
# 檔案路徑：modules/base_module.py
# 職責：通用內頁 Tab 分發器 (負責載入二級大項下的子 Tab 頁籤)
# ==========================================

import streamlit as st

def render_dynamic_module(feature_id, db_conn):
    all_features = db_conn.query("SELECT * FROM sys_features WHERE is_active = TRUE;")
    current_feat = next((f for f in all_features if f['id'] == feature_id), None)
    
    if not current_feat:
        st.error("找不到該功能大項的配置資訊！")
        return

    st.header(f"📋 {current_feat['name_zh']}")
    st.caption(f"Trang: {current_feat['name_vi']}")
    
    sub_tabs = db_conn.query(f"SELECT * FROM sys_sub_tabs WHERE feature_id = '{feature_id}' ORDER BY sort_order;")
    
    if not sub_tabs:
        st.warning("此功能大項尚未設定細項 Tab 頁籤。請至 IT 系統管理的選單配置中新增。")
        return

    tab_titles = [f"{t['name_zh']} ({t['name_vi']})" for t in sub_tabs]
    tabs = st.tabs(tab_titles)
    
    for idx, tab_info in enumerate(sub_tabs):
        with tabs[idx]:
            st.write(f"### 內容區域：{tab_info['name_zh']}")
            st.info(f"此處執行 `{tab_info['id']}` 的具體表單與資料庫讀寫操作。")
