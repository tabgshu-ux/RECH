# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：純企業組織路由分發器（零冗餘、零額外標題，直接載入各部門模組）
# ==========================================

import streamlit as st
import importlib

def render_dashboard(db_engine):
    current_lang = st.session_state.get('current_lang', '繁體中文')

    # 1. 初始化全公司一級部門清單
    departments = [
        {"id": "ceo", "name_zh": "總經理室", "name_vi": "Văn phòng Tổng Giám đốc", "level": "L1", "icon": "👑"},
        {"id": "eng", "name_zh": "工程部", "name_vi": "Phòng Kỹ thuật", "level": "L1", "icon": "🛠️"},
        {"id": "mgmt", "name_zh": "管理部", "name_vi": "Phòng Hành chính Quản trị", "level": "L1", "icon": "🏢"},
        {"id": "prod", "name_zh": "生產部", "name_vi": "Phòng Sản xuất", "level": "L1", "icon": "🏭"},
        {"id": "warehouse", "name_zh": "倉庫管理", "name_vi": "Quản lý kho", "level": "L1", "icon": "📦"},
        {"id": "approval", "name_zh": "簽核中心", "name_vi": "Trung tâm phê duyệt", "level": "L1", "icon": "✍️"},
    ]

    if 'selected_dept_id' not in st.session_state:
        st.session_state['selected_dept_id'] = 'mgmt'

    current_dept_id = st.session_state['selected_dept_id']
    current_target = next((d for d in departments if d['id'] == current_dept_id), departments[2])

    # 2. 側邊欄：動態組織樹狀導覽
    st.sidebar.markdown("### 🏢 企業組織樹狀導覽")
    st.sidebar.markdown("---")

    for dept in departments:
        is_selected = (dept['id'] == current_dept_id)
        btn_type = "primary" if is_selected else "secondary"
        btn_label = f"{dept['icon']} {dept['name_zh']} ({dept['name_vi']})"
        
        if st.sidebar.button(btn_label, key=f"btn_dept_{dept['id']}", use_container_width=True, type=btn_type):
            st.session_state['selected_dept_id'] = dept['id']
            st.session_state['active_feature_id'] = None
            st.session_state.pop('active_sub_module', None)
            st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("⚙️ 系統設定 (Cấu hình hệ thống)", use_container_width=True):
        st.session_state['current_view'] = 'dynamic_feature'
        st.session_state['active_feature_id'] = 'feat_it_menu'
        st.rerun()

    # =========================================================================
    # 3. 路由分發核心：完全不印多餘大標題，直接把畫面交給對應的模組檔案！
    # =========================================================================
    
    # -------------------------------------------------------------------------
    # 3.1 管理部 (Management Department)
    # -------------------------------------------------------------------------
    if current_target['id'] == 'mgmt':
        active_feat = st.session_state.get('active_feature_id')

        if active_feat == 'feat_hr':
            if st.button("⬅️ 返回管理部總覽", key="back_to_mgmt"):
                st.session_state['active_feature_id'] = None
                st.rerun()

            if 'mgmt_hr_sub' not in st.session_state:
                st.session_state['mgmt_hr_sub'] = 'employee'

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("📁 員工管理", use_container_width=True, type="primary" if st.session_state['mgmt_hr_sub'] == 'employee' else "secondary"):
                    st.session_state['mgmt_hr_sub'] = 'employee'
                    st.rerun()
            with col2:
                if st.button("⏱️ 考勤管理", use_container_width=True, type="primary" if st.session_state['mgmt_hr_sub'] == 'attendance' else "secondary"):
                    st.session_state['mgmt_hr_sub'] = 'mgmt_att'
                    st.rerun()
            with col3:
                if st.button("💰 薪資管理", use_container_width=True, type="primary" if st.session_state['mgmt_hr_sub'] == 'payroll' else "secondary"):
                    st.session_state['mgmt_hr_sub'] = 'payroll'
                    st.rerun()
            with col4:
                if st.button("⚙️ 人事設定", use_container_width=True, type="primary" if st.session_state['mgmt_hr_sub'] == 'settings' else "secondary"):
                    st.session_state['mgmt_hr_sub'] = 'settings'
                    st.rerun()

            st.markdown("---")
            hr_sub = st.session_state['mgmt_hr_sub']
            if hr_sub == 'employee':
                try:
                    from modules.management.hr.employee import employee_profile
                    employee_profile.render(db_engine, lang=current_lang)
                except Exception as e:
                    st.error(f"載入員工模組失敗: {e}")
            else:
                st.info(f"📌 [人事子模組: {hr_sub}] 建置中...")

        else:
            try:
                from modules.management.supervisor_dashboard import render as render_supervisor
                render_supervisor(db_engine, lang=current_lang)
            except Exception as e:
                st.warning(f"戰情資料載入提示: {e}")
            st.markdown("---")

            cols = st.columns(3)
            l2_sections = [
                {"id": "feat_hr", "name": "📂 人事 / 行政", "desc": "越籍員工、外派幹部、合約、考勤與薪資保險。"},
                {"id": "feat_ga", "name": "📂 總務 / 採購", "desc": "廠區採購、供應商主檔、宿舍與車輛維修管理。"},
                {"id": "feat_fi", "name": "📂 財務 / 會計", "desc": "應收帳款 (AR) 與越南稅務標準財報 (Thông tư 200)。"},
            ]
            for idx, sec in enumerate(l2_sections):
                with cols[idx]:
                    with st.container(border=True):
                        st.markdown(f"#### {sec['name']}")
                        st.caption(sec['desc'])
                        if st.button("進入該部門專區 ➡️", key=f"btn_sec_{sec['id']}", use_container_width=True, type="primary"):
                            st.session_state['active_feature_id'] = sec['id']
                            st.rerun()

    # -------------------------------------------------------------------------
    # 3.2 總經理室 (CEO Office) -> 直接呼叫獨立模組，不佔任何額外空白
    # -------------------------------------------------------------------------
    elif current_target['id'] == 'ceo':
        try:
            from modules.executive import executive_dashboard
            if hasattr(executive_dashboard, "render"):
                executive_dashboard.render(db_engine, lang=current_lang)
            elif hasattr(executive_dashboard, "show"):
                executive_dashboard.show(engine=db_engine, lang=current_lang)
            else:
                st.info("👑 [總經理室] 決策戰情室載入中...")
        except Exception as e:
            st.error(f"⚠️ 載入總經理室模組發生異常: {str(e)}")

    # -------------------------------------------------------------------------
    # 3.3 其他部門預留路由
    # -------------------------------------------------------------------------
    elif current_target['id'] == 'eng':
        st.info("🛠️ [工程部] 模組載入中...")
    elif current_target['id'] == 'prod':
        st.info("🏭 [生產部] 模組載入中...")
    elif current_target['id'] == 'warehouse':
        st.info("📦 [倉庫管理] 模組載入中...")
    elif current_target['id'] == 'approval':
        st.info("✍️ [簽核中心] 模組載入中...")
    else:
        st.warning("💡 模組路由掛載中...")
