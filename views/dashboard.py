# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：純企業組織路由分發器（已完全對接資料庫 sys_departments，實現左側選單與系統設定 100% 雙向即時聯動）
# ==========================================

import streamlit as st
import importlib
from sqlalchemy import text

def render_dashboard(db_engine):
    st.markdown("""
        <script>
            const body = window.parent.document.querySelector(".main");
            if (body) {
                body.scrollTop = 0;
            }
            window.scrollTo({top: 0, behavior: 'instant'});
        </script>
    """, unsafe_allow_html=True)

    current_lang = st.session_state.get('current_lang', '繁體中文')

    # 🌟 1. 從資料庫動態讀取所有啟用中 (is_active = TRUE) 的部門清單（實現真正的 No Hard-coding 與雙向聯動）
    departments = []
    default_depts = [
        {"id": "ceo", "name_zh": "總經理室總覽", "name_vi": "Văn phòng Tổng Giám đốc", "level": "L1", "icon": "👑", "code": "EXEC"},
        {"id": "eng", "name_zh": "工程部總覽", "name_vi": "Phòng Kỹ thuật", "level": "L1", "icon": "🛠️", "code": "ENG"},
        {"id": "mgmt", "name_zh": "管理部總覽", "name_vi": "Phòng Hành chính Quản trị", "level": "L1", "icon": "🏢", "code": "MGMT"},
        {"id": "prod", "name_zh": "生產部總覽", "name_vi": "Phòng Sản xuất", "level": "L1", "icon": "🏭", "code": "PROD"},
        {"id": "warehouse", "name_zh": "倉庫管理", "name_vi": "Quản lý kho", "level": "L1", "icon": "📦", "code": "WAREHOUSE"},
        {"id": "approval", "name_zh": "簽核中心", "name_vi": "Trung tâm phê duyệt", "level": "L1", "icon": "✍️", "code": "APPROVAL"},
    ]

    if db_engine is not None:
        try:
            with db_engine.connect() as conn:
                # 確保資料表存在並嘗試撈取
                db_rows = conn.execute(text("SELECT dept_code, dept_name, level_tier FROM sys_departments WHERE is_active = TRUE ORDER BY id")).fetchall()
                if db_rows:
                    for row in db_rows:
                        d_code, d_name, d_tier = row
                        # 對應圖示與內部 ID
                        icon = "🏢"
                        if "總經理" in d_name: icon = "👑"
                        elif "工程" in d_name: icon = "🛠️"
                        elif "管理" in d_name: icon = "🏢"
                        elif "生產" in d_name: icon = "🏭"
                        elif "倉庫" in d_name: icon = "📦"
                        elif "簽核" in d_name: icon = "✍️"
                        
                        departments.append({
                            "id": d_code.lower(),
                            "name_zh": d_name,
                            "name_vi": d_name,
                            "level": d_tier,
                            "icon": icon,
                            "code": d_code
                        })
        except Exception:
            pass

    # 若資料庫尚未初始化或無資料，則採用預設清單
    if not departments:
        departments = default_depts

    if 'selected_dept_id' not in st.session_state:
        st.session_state['selected_dept_id'] = departments[0]['id'] if departments else 'mgmt'

    current_dept_id = st.session_state['selected_dept_id']
    current_target = next((d for d in departments if d['id'] == current_dept_id), departments[0] if departments else None)

    # 🌟 2. 渲染左側動態組織樹導覽列
    st.sidebar.markdown("### 🏢 企業組織樹狀導覽")
    st.sidebar.markdown("---")

    for dept in departments:
        is_selected = (dept['id'] == current_dept_id)
        btn_type = "primary" if is_selected else "secondary"
        btn_label = f"{dept['icon']} {dept['name_zh']}"
        
        if st.sidebar.button(btn_label, key=f"btn_dept_{dept['id']}", use_container_width=True, type=btn_type):
            st.session_state['selected_dept_id'] = dept['id']
            st.session_state['active_feature_id'] = None
            st.session_state.pop('active_sub_module', None)
            st.session_state.pop('exec_active_sub', None)
            st.session_state.pop('mgmt_hr_sub', None)
            st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("⚙️ 系統設定 (Cấu hình hệ thống)", use_container_width=True):
        st.session_state['current_view'] = 'dynamic_feature'
        st.session_state['active_feature_id'] = 'feat_it_menu'
        st.rerun()

    if not current_target:
        st.warning("⚠️ 目前無可顯示的部門，請至系統設定中檢查部門啟用狀態。")
        return

    # 🌟 3. 各部門路由分發
    if current_target['code'] == 'MGMT' or current_target['id'] == 'mgmt':
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
                if st.button("⏱️ 考勤管理", use_container_width=True, type="primary" if st.session_state['mgmt_hr_sub'] == 'mgmt_att' else "secondary"):
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

    elif current_target['code'] == 'EXEC' or current_target['id'] == 'ceo':
        try:
            from modules.executive import executive_dashboard
            if hasattr(executive_dashboard, "render"):
                executive_dashboard.render(db_engine, lang=current_lang)
            elif hasattr(executive_dashboard, "show"):
                executive_dashboard.show(engine=db_engine, lang=current_lang)
            else:
                st.info("👑 [總經理室總覽] 載入中...")
        except Exception as e:
            st.error(f"⚠️ 載入總經理室模組發生異常: {str(e)}")

    elif current_target['code'] == 'ENG' or current_target['id'] == 'eng':
        try:
            from modules.engineering import engineering_department
            if hasattr(engineering_department, "show"):
                engineering_department.show(engine=db_engine, lang=current_lang)
            elif hasattr(engineering_department, "render"):
                engineering_department.render(db_engine, lang=current_lang)
            else:
                st.info("🛠️ [工程部總覽] 載入中...")
        except Exception as e:
            st.error(f"⚠️ 載入工程部模組發生異常: {str(e)}")

    elif current_target['code'] == 'PROD' or current_target['id'] == 'prod':
        try:
            from modules.production import production_overview
            if hasattr(production_overview, "show"):
                production_overview.show(engine=db_engine, lang=current_lang)
            elif hasattr(production_overview, "render"):
                production_overview.render(db_engine, lang=current_lang)
            else:
                st.info("🏭 [生產部總覽] 載入中...")
        except Exception as e:
            st.error(f"⚠️ 載入生產部總覽模組發生異常: {str(e)}")

    elif current_target['code'] == 'WAREHOUSE' or current_target['id'] == 'warehouse':
        st.info("📦 [倉庫管理總覽] 模組載入中...")
    elif current_target['code'] == 'APPROVAL' or current_target['id'] == 'approval':
        st.info("✍️ [簽核中心總覽] 模組載入中...")
    else:
        st.info(f"💡 [{current_target['name_zh']}] 專區模組建置中...")
