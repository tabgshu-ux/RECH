# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：Admin 全局掌控全公司 7 大部門 + 單一部門切換
# ==========================================

import streamlit as st

def render_dashboard(db_conn):
    modules = db_conn.query("SELECT * FROM sys_modules WHERE is_active = TRUE ORDER BY sort_order;")
    features = db_conn.query("SELECT * FROM sys_features WHERE is_active = TRUE ORDER BY sort_order;")
    
    if not modules:
        st.info("目前系統尚未設定任何部門模組。")
        return

    is_admin = (st.session_state.get('user_name') == 'admin')

    # -------------------------------------------------------------------------
    # 1. 左側側邊欄：一級部門導覽
    # -------------------------------------------------------------------------
    st.sidebar.markdown("### 🏢 企業導覽選單")
    
    if 'selected_module_id' not in st.session_state or not st.session_state['selected_module_id']:
        st.session_state['selected_module_id'] = 'all' if is_admin else modules[0]['id']

    # Admin 專屬最高控制台按鈕
    if is_admin:
        is_all_selected = (st.session_state['selected_module_id'] == 'all')
        btn_type_all = "primary" if is_all_selected else "secondary"
        if st.sidebar.button("🌐 全公司總覽 (CEO / Admin)", key="sidebar_mod_all", type=btn_type_all, use_container_width=True):
            st.session_state['selected_module_id'] = 'all'
            st.rerun()
        st.sidebar.divider()

    # 各部門選項清單
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
    # 2. 右側主畫面：【Admin 全局總覽牆】 vs 【單一部門工作台】
    # -------------------------------------------------------------------------
    
    # 【模式 A：Admin 全局總覽牆】
    if st.session_state['selected_module_id'] == 'all':
        st.title("👑 全公司管理控制台 (Admin Dashboard)")
        st.caption("裕豐電機工業 - 全局營運、工地派工與跨部門簽核監控")
        st.divider()

        # 頂部全局營運指標
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        with col_kpi1:
            with st.container(border=True):
                st.metric(label="全公司待審單據", value="7 件", delta="工程/採購/請假", delta_color="inverse")
        with col_kpi2:
            with st.container(border=True):
                st.metric(label="工地/外勤打卡率", value="92%", delta="3 人未打卡 (乙級主管巡查中)")
        with col_kpi3:
            with st.container(border=True):
                st.metric(label="本月工程估驗款", value="185,000 USD", delta="+8% vs 上月")
        with col_kpi4:
            with st.container(border=True):
                st.metric(label="配電盤組裝進度", value="94%", delta="2 套待出貨")

        st.divider()

        # 核心：全公司所有部門的跨部門業務卡片牆 (3 欄自動延伸)
        st.markdown("### 📊 全公司各部門業務一覽 (CEO/Admin 直捷入口)")
        
        col_count = 3
        for i in range(0, len(modules), col_count):
            cols = st.columns(col_count)
            for j in range(col_count):
                if i + j < len(modules):
                    mod = modules[i + j]
                    with cols[j]:
                        with st.container(border=True):
                            st.subheader(f"📂 {mod['name_zh']}")
                            st.caption(mod['name_vi'])
                            st.divider()
                            
                            sub_feats = [f for f in features if f['module_id'] == mod['id']]
                            if sub_feats:
                                for feat in sub_feats:
                                    if st.button(
                                        f"👉 {feat['name_zh']}", 
                                        key=f"admin_wall_btn_{mod['id']}_{feat['id']}", 
                                        use_container_width=True
                                    ):
                                        st.session_state['active_feature_id'] = feat['id']
                                        st.session_state['current_view'] = 'dynamic_feature'
                                        st.rerun()
                            else:
                                st.caption("尚未配置功能項目")

    # 【模式 B：單一部門工作台】
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
