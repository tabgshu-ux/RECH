# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：支援 admin 最高管理者全局視角與各部門切換的工作台
# ==========================================

import streamlit as st

def render_dashboard(db_conn):
    # 1. 讀取一級部門與二級功能 (Metadata)
    modules = db_conn.query("SELECT * FROM sys_modules WHERE is_active = TRUE ORDER BY sort_order;")
    features = db_conn.query("SELECT * FROM sys_features WHERE is_active = TRUE ORDER BY sort_order;")
    
    if not modules:
        st.info("目前系統尚未設定任何部門模組。")
        return

    is_admin = (st.session_state.get('user_name') == 'admin')

    # -------------------------------------------------------------------------
    # 2. 左側側邊欄：一級部門切換 (admin 額外提供「全公司總覽」)
    # -------------------------------------------------------------------------
    st.sidebar.markdown("### 🏢 企業導覽選單")
    
    # 初始化選擇狀態：admin 預設進入全公司總覽 'all'，一般使用者預設進入第一個部門
    if 'selected_module_id' not in st.session_state or not st.session_state['selected_module_id']:
        st.session_state['selected_module_id'] = 'all' if is_admin else modules[0]['id']

    # admin 專用「全公司總覽」按鈕
    if is_admin:
        is_all_selected = (st.session_state['selected_module_id'] == 'all')
        btn_type_all = "primary" if is_all_selected else "secondary"
        if st.sidebar.button("🌐 全公司總覽 (CEO / Admin)", key="sidebar_mod_all", type=btn_type_all, use_container_width=True):
            st.session_state['selected_module_id'] = 'all'
            st.rerun()
        st.sidebar.divider()

    # 一般部門按鈕清單
    for mod in modules:
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
    # 3. 右側主畫面分流：【全公司總覽 (Admin)】 vs 【單一部門工作台】
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # 模式 A：Admin 最高管理者全局視角 (selected_module_id == 'all')
    # -------------------------------------------------------------------------
    if st.session_state['selected_module_id'] == 'all':
        st.title("👑 全公司管理控制台 (Admin Dashboard)")
        st.caption("裕豐電機工業 - 全局營運與跨部門簽核監控")
        st.divider()

        # 頂部全局 KPI
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        with col_kpi1:
            with st.container(border=True):
                st.metric(label="全公司待審單據", value="7 件", delta="高優先級 2 件", delta_color="inverse")
        with col_kpi2:
            with st.container(border=True):
                st.metric(label="工地/外勤打卡率", value="92%", delta="3 人未打卡")
        with col_kpi3:
            with st.container(border=True):
                st.metric(label="本月採購/報銷總額", value="125,000 USD", delta="+5% vs 上月")
        with col_kpi4:
            with st.container(border=True):
                st.metric(label="系統運作狀態", value="正常 (Normal)", delta="Supabase DB 綠燈")

        st.divider()

        # 全局快捷營運模組九宮格 (按部門彙整呈現)
        st.markdown("### 📊 跨部門業務一覽與快捷跳轉")
        col_count = 2
        for i in range(0, len(modules), col_count):
            cols = st.columns(col_count)
            for j in range(col_count):
                if i + j < len(modules):
                    mod = modules[i + j]
                    with cols[j]:
                        with st.container(border=True):
                            st.subheader(f"📂 {mod['name_zh']} ({mod['name_vi']})")
                            sub_feats = [f for f in features if f['module_id'] == mod['id']]
                            if sub_feats:
                                for feat in sub_feats:
                                    if st.button(f"👉 {feat['name_zh']}", key=f"admin_btn_{mod['id']}_{feat['id']}", use_container_width=True):
                                        st.session_state['active_feature_id'] = feat['id']
                                        st.session_state['current_view'] = 'dynamic_feature'
                                        st.rerun()
                            else:
                                st.caption("目前無設定功能")

    # -------------------------------------------------------------------------
    # 模式 B：單一部門工作台 (selected_module_id != 'all')
    # -------------------------------------------------------------------------
    else:
        current_mod = next((m for m in modules if m['id'] == st.session_state['selected_module_id']), modules[0])
        
        st.title(f"📂 {current_mod['name_zh']} - 功能儀表板")
        st.caption(f"Trang chủ: {current_mod['name_vi']}")
        st.divider()

        current_features = [f for f in features if f['module_id'] == current_mod['id']]
        
        if not current_features:
            st.warning("此部門目前尚未配置功能項目。")
            return

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
