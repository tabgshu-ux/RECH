# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：依照指定 7 大部門順序渲染側邊欄與右側卡片（依系統語系純淨顯示）
# ==========================================

import streamlit as st

def render_dashboard(db_conn):
    lang = st.session_state.get('current_lang', 'zh')
    
    # 按照 sort_order 嚴格排序讀取
    modules = db_conn.query("SELECT * FROM sys_modules WHERE is_active = TRUE ORDER BY sort_order ASC;")
    features = db_conn.query("SELECT * FROM sys_features WHERE is_active = TRUE ORDER BY sort_order ASC;")
    
    if not modules:
        msg = "目前系統尚未設定任何部門模組。" if lang == 'zh' else "Hệ thống chưa được cấu hình bộ phận."
        st.info(msg)
        return

    is_admin = (st.session_state.get('user_name') == 'admin')

    # -------------------------------------------------------------------------
    # 1. 左側側邊欄：一級部門導覽
    # -------------------------------------------------------------------------
    sidebar_title = "🏢 企業導覽選單" if lang == 'zh' else "🏢 Danh mục bộ phận"
    st.sidebar.markdown(f"### {sidebar_title}")
    
    if 'selected_module_id' not in st.session_state or not st.session_state['selected_module_id']:
        st.session_state['selected_module_id'] = 'all' if is_admin else modules[0]['id']

    # Admin 全局控制台按鈕
    if is_admin:
        is_all_selected = (st.session_state['selected_module_id'] == 'all')
        btn_type_all = "primary" if is_all_selected else "secondary"
        admin_btn_label = "🌐 全公司總覽 (CEO / Admin)" if lang == 'zh' else "🌐 Tổng quan công ty (CEO / Admin)"
        
        if st.sidebar.button(admin_btn_label, key="sidebar_mod_all", type=btn_type_all, use_container_width=True):
            st.session_state['selected_module_id'] = 'all'
            st.rerun()
        st.sidebar.divider()

    # 依序渲染一級部門按鈕（純淨語系顯示，自動過濾不必要的雙語括號）
    for mod in modules:
        is_selected = (st.session_state['selected_module_id'] == mod['id'])
        btn_type = "primary" if is_selected else "secondary"
        
        raw_name = mod['name_zh'] if lang == 'zh' else mod['name_vi']
        mod_display_name = raw_name.split('(')[0].strip() if lang == 'zh' else raw_name
        
        if st.sidebar.button(
            mod_display_name, 
            key=f"sidebar_mod_{mod['id']}", 
            type=btn_type, 
            use_container_width=True
        ):
            st.session_state['selected_module_id'] = mod['id']
            st.rerun()

    # -------------------------------------------------------------------------
    # 2. 右側主畫面渲染
    # -------------------------------------------------------------------------
    
    # 【模式 A：Admin 全局控制台】
    if st.session_state['selected_module_id'] == 'all':
        title = "👑 全公司管理控制台 (Admin Dashboard)" if lang == 'zh' else "👑 Bảng điều khiển quản lý"
        subtitle = "裕豐電機工業 - 全局營運與各部門業務一覽" if lang == 'zh' else "Reetech Industrial - Tổng quan vận hành"
        
        st.title(title)
        st.caption(subtitle)
        st.divider()

        # 全局 KPI 指標
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        with col_kpi1:
            with st.container(border=True):
                st.metric(label="全公司待審單據", value="7 件", delta="待辦事項", delta_color="inverse")
        with col_kpi2:
            with st.container(border=True):
                st.metric(label="外勤/工地打卡率", value="92%", delta="3 人未打卡")
        with col_kpi3:
            with st.container(border=True):
                st.metric(label="本月工程估驗款", value="185,000 USD", delta="+8%")
        with col_kpi4:
            with st.container(border=True):
                st.metric(label="配電盤組裝進度", value="94%", delta="2 套待出貨")

        st.divider()

        # 跨部門業務一覽與快捷跳轉
        sec_title = "📊 跨部門業務一覽與快捷跳轉" if lang == 'zh' else "📊 Danh mục chức năng các bộ phận"
        st.markdown(f"### {sec_title}")
        
        col_count = 3
        for i in range(0, len(modules), col_count):
            cols = st.columns(col_count)
            for j in range(col_count):
                if i + j < len(modules):
                    mod = modules[i + j]
                    raw_mod_name = mod['name_zh'] if lang == 'zh' else mod['name_vi']
                    mod_name = raw_mod_name.split('(')[0].strip() if lang == 'zh' else raw_mod_name
                    
                    with cols[j]:
                        with st.container(border=True):
                            st.subheader(f"📂 {mod_name}")
                            st.divider()
                            
                            sub_feats = [f for f in features if f['module_id'] == mod['id']]
                            if sub_feats:
                                for feat in sub_feats:
                                    raw_feat_name = feat['name_zh'] if lang == 'zh' else feat['name_vi']
                                    feat_name = raw_feat_name.split('(')[0].strip() if lang == 'zh' else raw_feat_name
                                    if st.button(
                                        f"👉 {feat_name}", 
                                        key=f"admin_wall_btn_{mod['id']}_{feat['id']}", 
                                        use_container_width=True
                                    ):
                                        st.session_state['active_feature_id'] = feat['id']
                                        st.session_state['current_view'] = 'dynamic_feature'
                                        st.rerun()
                            else:
                                no_feat_msg = "尚未配置功能項目" if lang == 'zh' else "Chưa có chức năng"
                                st.caption(no_feat_msg)

    # 【模式 B：單部門工作台】
    else:
        current_mod = next((m for m in modules if m['id'] == st.session_state['selected_module_id']), modules[0])
        raw_mod_name = current_mod['name_zh'] if lang == 'zh' else current_mod['name_vi']
        mod_name = raw_mod_name.split('(')[0].strip() if lang == 'zh' else raw_mod_name
        
        page_title = f"📂 {mod_name} - 功能儀表板" if lang == 'zh' else f"📂 {mod_name} - Bảng điều khiển"
        st.title(page_title)
        st.divider()

        current_features = [f for f in features if f['module_id'] == current_mod['id']]
        
        if not current_features:
            msg = "此部門目前尚未配置功能項目。" if lang == 'zh' else "Bộ phận này chưa được cấu hình."
            st.warning(msg)
            return

        col_count = 3
        for i in range(0, len(current_features), col_count):
            cols = st.columns(col_count)
            for j in range(col_count):
                if i + j < len(current_features):
                    feat = current_features[i + j]
                    raw_feat_name = feat['name_zh'] if lang == 'zh' else feat['name_vi']
                    feat_name = raw_feat_name.split('(')[0].strip() if lang == 'zh' else raw_feat_name
                    btn_label = "進入功能 ➡️" if lang == 'zh' else "Vào chức năng ➡️"
                    
                    with cols[j]:
                        with st.container(border=True):
                            st.subheader(feat_name)
                            st.divider()
                            
                            if st.button(btn_label, key=f"card_btn_{feat['id']}", use_container_width=True, type="primary"):
                                st.session_state['active_feature_id'] = feat['id']
                                st.session_state['current_view'] = 'dynamic_feature'
                                st.rerun()
