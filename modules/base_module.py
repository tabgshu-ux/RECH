# ==========================================
# 檔案路徑：modules/base_module.py
# 職責：內頁 Tab 動態分發器 (負責畫出小功能 Tab 頁籤)
# ==========================================

import streamlit as st

def render_dynamic_module(feature_id, db_conn):
    # 1. 撈取目前點擊的功能大項資訊
    all_features = db_conn.query("SELECT * FROM sys_features WHERE is_active = TRUE;")
    current_feat = next((f for f in all_features if f['id'] == feature_id), None)
    
    if not current_feat:
        st.error("找不到該功能大項的配置資訊！")
        return

    st.header(f"📋 {current_feat['name_zh']}")
    st.caption(f"Trang: {current_feat['name_vi']}")
    
    # 2. 撈取該功能大項底下的三級子 Tab 分頁
    sub_tabs = db_conn.query(f"SELECT * FROM sys_sub_tabs WHERE feature_id = '{feature_id}' ORDER BY sort_order;")
    
    if not sub_tabs:
        st.warning("此功能大項尚未設定細項 Tab 頁籤。請聯絡管理者至系統設定新增。")
        return

    # 3. 建立 Streamlit 頁籤
    tab_titles = [f"{t['name_zh']} ({t['name_vi']})" for t in sub_tabs]
    tabs = st.tabs(tab_titles)
    
    # 4. 渲染各 Tab 內容 (未來可以在此處引入真正的子業務檔案)
    for idx, tab_info in enumerate(sub_tabs):
        with tabs[idx]:
            st.write(f"### 內容區域：{tab_info['name_zh']}")
            st.info(f"此處執行 `{tab_info['id']}` 的具體表單與資料庫讀寫操作。")
