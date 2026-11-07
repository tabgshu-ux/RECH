# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：左側選單僅保留 L1 一級大部門，L2 二級部門則直接展現於主部門下方的儀表板卡片中
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_dashboard(db_engine=None):
    st.title("🏭 裕豐電機工業 SaaS ERP - 企業導覽選單")
    st.caption("左側選單維持 L1 一級大部門導覽；當點擊進入大部門時，所屬的二級部門與業務模組將直接展現於主畫面中。")
    st.markdown("---")

    # 1. 從資料庫動態讀取所有啟用的部門
    departments = []
    if db_engine is not None:
        try:
            with db_engine.connect() as conn:
                df_depts = pd.read_sql(
                    text("SELECT dept_code, dept_name_zh, dept_name_vi, level_depth, parent_code FROM sys_departments WHERE is_active = TRUE ORDER BY id ASC"), 
                    con=conn
                )
                if not df_depts.empty:
                    for _, row in df_depts.iterrows():
                        departments.append({
                            "id": row["dept_code"],
                            "name_zh": row["dept_name_zh"],
                            "name_vi": row["dept_name_vi"] or "",
                            "level": row["level_depth"] or "L1",
                            "parent": row["parent_code"] or "None"
                        })
        except Exception:
            pass

    # 若資料庫無資料時的緊急安全預設值
    if not departments:
        departments = [
            {"id": "gm", "name_zh": "總經理室", "name_vi": "Văn phòng Tổng Giám đốc", "level": "L1", "parent": "None"},
            {"id": "mgmt", "name_zh": "管理部", "name_vi": "Bộ phận Quản lý", "level": "L1", "parent": "None"},
            {"id": "eng", "name_zh": "工程部", "name_vi": "Bộ phận Công trình", "level": "L1", "parent": "None"},
            {"id": "prod", "name_zh": "生產部", "name_vi": "Bộ phận Sản xuất", "level": "L1", "parent": "None"},
        ]

    # 2. 🌟 左側導覽選單：嚴格只篩選並顯示 L1 一級大部門
    st.sidebar.markdown("### 🏢 企業組織樹狀導覽")
    
    current_selected_id = st.session_state.get('selected_module_id', None)
    l1_depts = [d for d in departments if d["level"] == "L1" or d["parent"] == "None" or not d["parent"]]
    
    l1_ids = [d['id'] for d in l1_depts]
    if current_selected_id not in l1_ids and l1_depts:
        current_selected_id = l1_depts[0]['id']
        st.session_state['selected_module_id'] = current_selected_id

    for l1 in l1_depts:
        is_current = (l1['id'] == current_selected_id)
        btn_label = f"📂 {l1['name_zh']} ({l1['name_vi']})"
        if st.sidebar.button(btn_label, use_container_width=True, key=f"sb_l1_{l1['id']}", type="primary" if is_current else "secondary"):
            st.session_state['selected_module_id'] = l1['id']
            st.session_state['current_view'] = 'dashboard'
            st.rerun()

    st.sidebar.divider()
    
    # 唯一固定常駐的系統設定入口
    if st.sidebar.button("⚙️ 系統設定 (Cấu hình hệ thống)", use_container_width=True, key="sb_sys_config_fixed"):
        st.session_state['current_view'] = 'dynamic_feature'
        st.session_state['active_feature_id'] = 'feat_it_menu'
        st.rerun()

    # 3. 取得當前選中的 L1 大部門詳細資料
    current_dept = next((d for d in l1_depts if d['id'] == current_selected_id), l1_depts[0] if l1_depts else None)
    
    if current_dept:
        st.subheader(f"📂 {current_dept['name_zh']} - 功能儀表板")
        st.caption(f"部門層級: {current_dept['level']} | 越文名稱: {current_dept['name_vi']}")
        st.markdown("<br>", unsafe_allow_html=True)

        # 🌟 如果是「管理部」，上方直接嵌入主管戰情儀表板統合資料
        if "管理部" in current_dept['name_zh'] or current_dept['id'] == 'mgmt':
            st.markdown("### 📊 管理部主管即時統合戰情指標")
            st.caption("以下為管理部各課室本月即時統合數據，供主管第一時間掌握全盤動態：")
            try:
                from modules.management.supervisor_dashboard import render as render_supervisor
                render_supervisor(db_engine, lang=st.session_state.get('current_lang', 'zh'))
            except Exception as e:
                st.warning(f"戰情資料載入提示: {e}")
            st.markdown("---")
            st.subheader("⚙️ 部門子功能與下屬二級部門操作選單")

        # 4. 🌟 展現下屬二級部門（L2/L3）於主畫面中
        sub_departments = [d for d in departments if d["parent"] == current_dept['id']]
        if sub_departments:
            st.markdown("##### 📁 隸屬此大部門之二級部門 / 課室：")
            sub_cols = st.columns(3)
            for idx, sub in enumerate(sub_departments):
                col = sub_cols[idx % 3]
                with col:
                    with st.container(border=True):
                        st.markdown(f"#### 📁 [{sub['level']}] {sub['name_zh']}")
                        st.caption(f"越文名稱: {sub['name_vi']}")
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"進入 {sub['name_zh']} ➡️", key=f"btn_sub_dept_{sub['id']}", use_container_width=True, type="secondary"):
                            st.session_state['selected_sub_dept_id'] = sub['id']
                            st.success(f"已選定二級部門: {sub['name_zh']}")
                            st.rerun()
            st.markdown("---")

        # 5. 從資料庫動態讀取該部門實際掛載的模組清單
        assigned_modules = []
        if db_engine is not None:
            try:
                with db_engine.connect() as conn:
                    df_mods = pd.read_sql(
                        text("SELECT module_name FROM sys_department_modules WHERE dept_code = :code"), 
                        con=conn, 
                        params={"code": current_dept['id']}
                    )
                    if not df_mods.empty:
                        assigned_modules = df_mods["module_name"].tolist()
            except Exception:
                pass

        if not assigned_modules:
            st.info(f"💡 此部門 [{current_dept['name_zh']}] 目前尚未掛載任何業務模組。您可以前往「系統設定」中自由勾選掛載！")
        else:
            st.markdown(f"##### 🧩 此部門當前掛載的業務模組（共 {len(assigned_modules)} 項）：")
            
            def get_feat_id_by_name(m_name):
                if "主管綜合戰情儀表板" in m_name: return "feat_mgmt_supervisor"
                if "人事" in m_name or "員工檔案" in m_name: return "feat_hr"
                if "採購" in m_name or "應付" in m_name or "總務" in m_name: return "feat_ga"
                if "財務" in m_name or "會計" in m_name or "200" in m_name: return "feat_fi"
                if "工程" in m_name or "日報" in m_name or "案場" in m_name: return "feat_site_log"
                if "設計" in m_name or "圖庫" in m_name or "配電盤" in m_name: return "feat_panel_build"
                if "組裝" in m_name or "配線" in m_name: return "feat_panel_build"
                if "倉庫" in m_name or "庫存" in m_name: return "feat_material"
                if "簽核" in m_name: return "feat_my_approvals"
                return "feat_general"

            cols = st.columns(3)
            for idx, mod_name in enumerate(assigned_modules):
                col = cols[idx % 3]
                feat_id = get_feat_id_by_name(mod_name)
                with col:
                    with st.container(border=True):
                        st.markdown(f"#### 📌 {mod_name}")
                        st.caption("已成功掛載至此部門，可直接點擊進入操作。")
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("進入功能 ➡️", key=f"btn_mod_{current_dept['id']}_{idx}", use_container_width=True, type="primary"):
                            st.session_state['current_view'] = 'dynamic_feature'
                            st.session_state['active_feature_id'] = feat_id
                            st.rerun()
