# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：左側一級部門選單連動 + 右側二級功能卡片陣列
# ==========================================

import streamlit as st

def render_dashboard(db_conn):
    # 1. 從資料庫讀取所有啟用的「一級部門」與「二級功能」
    modules = db_conn.query("SELECT * FROM sys_modules WHERE is_active = TRUE ORDER BY sort_order;")
    features = db_conn.query("SELECT * FROM sys_features WHERE is_active = TRUE ORDER BY sort_order;")
    
    if not modules:
        st.info("目前系統尚未設定任何部門模組。")
        return

    # 2. 左側側邊欄：顯示 1 級部門列表
    st.sidebar.markdown("### 🏢 企業部門選單")
    
    # 預設選擇第一個部門
    if 'selected_module_id' not in st.session_state or not st.session_state['selected_module_id']:
        st.session_state['selected_module_id'] = modules[0]['id']

    # 繪製側邊欄部門按鈕
    for mod in modules:
        btn_type = "primary" if st.session_state['selected_module_id'] == mod['id'] else "secondary"
        if st.sidebar.button(f"{mod['name_zh']} ({mod['name_vi']})", key=f"sidebar_mod_{mod['id']}", type=btn_type, use_container_width=True):
            st.session_state['selected_module_id'] = mod['id']
            st.rerun()

    # 3. 右側主畫面：取得當前選定的部門資訊
    current_mod = next((m for m in modules if m['id'] == st.session_state['selected_module_id']), modules[0])
    
    st.title(f"📂 {current_mod['name_zh']} - 功能儀表板")
    st.caption(f"Trang chủ: {current_mod['name_vi']}")
    st.divider()

    # 篩選屬於該部門的二級功能
    current_features = [f for f in features if f['module_id'] == current_mod['id']]
    
    if not current_features:
        st.warning("此部門目前尚未配置任何二級功能項目。")
        return

    # 4. 右側卡片式佈局：3欄式自動延伸拉長
    col_count = 3
    for i in range(0, len(current_features), col_count):
        cols = st.columns(col_count)
        for j in range(col_count):
            if i + j < len(current_features):
                feat = current_features[i + j]
                with cols[j]:
                    with st.container(border=True):
                        st.subheader(feat['name_zh'])
                        st.caption(feat['name_vi'])
                        st.divider()
                        
                        if st.button("進入功能 ➡️", key=f"card_btn_{feat['id']}", use_container_width=True, type="primary"):
                            st.session_state['active_feature_id'] = feat['id']
                            st.session_state['current_view'] = 'dynamic_feature'
                            st.rerun()
