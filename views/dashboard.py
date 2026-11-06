# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：水電工程實務型導覽頁 (左側部門 + 右側待辦簽核區與二級功能)
# ==========================================

import streamlit as st

def render_dashboard(db_conn):
    # 1. 讀取一級部門與二級功能
    modules = db_conn.query("SELECT * FROM sys_modules WHERE is_active = TRUE ORDER BY sort_order;")
    features = db_conn.query("SELECT * FROM sys_features WHERE is_active = TRUE ORDER BY sort_order;")
    
    if not modules:
        st.info("目前系統尚未設定任何部門模組。")
        return

    # -------------------------------------------------------------------------
    # 2. 左側側邊欄：一級部門切換
    # -------------------------------------------------------------------------
    st.sidebar.markdown("### 🏢 部門選單")
    
    if 'selected_module_id' not in st.session_state or not st.session_state['selected_module_id']:
        st.session_state['selected_module_id'] = modules[0]['id']

    for mod in modules:
        # 當前選中的部門按鈕高亮
        is_selected = (st.session_state['selected_module_id'] == mod['id'])
        btn_type = "primary" if is_selected else "secondary"
        
        if st.sidebar.button(
            f"{mod['name_zh']} ({mod['name_vi']})", 
            key=f"sidebar_mod_{mod['id']}", 
            type=btn_type, 
            use_container_width=True
        ):
            st.session_state['selected_module_id'] = mod['id']
            st.rerun()

    # -------------------------------------------------------------------------
    # 3. 右側主畫面：當前部門的簽核中心與功能區塊
    # -------------------------------------------------------------------------
    current_mod = next((m for m in modules if m['id'] == st.session_state['selected_module_id']), modules[0])
    
    st.title(f"📌 {current_mod['name_zh']} 工作台")
    st.caption(f"Bảng làm việc: {current_mod['name_vi']}")
    st.divider()

    # -------------------------------------------------------------------------
    # 區塊 A：簽核與待辦中心 (讓主管/內勤開啟頁面就能快速處理)
    # -------------------------------------------------------------------------
    st.markdown("### ⚡ 待辦與簽核中心 (Trung tâm phê duyệt)")
    col_todo1, col_todo2, col_todo3 = st.columns(3)
    
    with col_todo1:
        with st.container(border=True):
            st.metric(label="待審核單據 / Chờ phê duyệt", value="3 件", delta="需緊急處理", delta_color="inverse")
            if st.button("前往簽核 📋", key="btn_quick_approval", use_container_width=True):
                st.toast("跳轉至簽核中心...")

    with col_todo2:
        with st.container(border=True):
            st.metric(label="外勤/現場打卡異常 / Chấm công bất thường", value="1 件", delta="-2 人未打卡")
            if st.button("查看考勤 ⏰", key="btn_quick_attendance", use_container_width=True):
                st.toast("跳轉至考勤異常核對...")

    with col_todo3:
        with st.container(border=True):
            st.metric(label="本月工程/採購進度 / Tiến độ công trình", value="85%", delta="正常進行")
            if st.button("查看報表 📊", key="btn_quick_report", use_container_width=True):
                st.toast("跳轉至報表...")

    st.divider()

    # -------------------------------------------------------------------------
    # 區塊 B：該部門二級功能按鈕區
    # -------------------------------------------------------------------------
    st.markdown("### 🛠️ 部門核心功能 (Chức năng chính)")
    
    current_features = [f for f in features if f['module_id'] == current_mod['id']]
    
    if not current_features:
        st.warning("此部門目前尚未配置功能項目。")
        return

    # 採用緊湊型網格，避免畫面太空
    col_count = 3
    for i in range(0, len(current_features), col_count):
        cols = st.columns(col_count)
        for j in range(col_count):
            if i + j < len(current_features):
                feat = current_features[i + j]
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"#### {feat['name_zh']}")
                        st.caption(feat['name_vi'])
                        st.write("") # 留空微調 spacing
                        
                        if st.button(
                            f"開啟 {feat['name_zh']} ➡️", 
                            key=f"card_btn_{feat['id']}", 
                            use_container_width=True, 
                            type="primary"
                        ):
                            st.session_state['active_feature_id'] = feat['id']
                            st.session_state['current_view'] = 'dynamic_feature'
                            st.rerun()
