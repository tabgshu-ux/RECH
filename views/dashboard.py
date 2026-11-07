# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：左側僅保留 L1 大部門；點擊主畫面下方的 L2 二級部門卡片時，直接切換顯示該二級部門之掛載模組與儀表板
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_dashboard(db_engine=None):
    st.title("🏭 裕豐電機工業 SaaS ERP - 企業導覽選單")
    st.caption("左側選單維持 L1 一級大部門導覽；點擊下方二級部門卡片可直接進入該課室之專屬功能介面。")
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

    if not departments:
        departments = [
            {"id": "gm", "name_zh": "總經理室", "name_vi": "Văn phòng Tổng Giám đốc", "level": "L1", "parent": "None"},
            {"id": "mgmt", "name_zh": "管理部", "name_vi": "Bộ phận Quản lý", "level": "L1", "parent": "None"},
            {"id": "eng", "name_zh": "工程部", "name_vi": "Bộ phận Công trình", "level": "L1", "parent": "None"},
            {"id": "prod", "name_zh": "生產部", "name_vi": "Bộ phận Sản xuất", "level": "L1", "parent": "None"},
        ]

    # 2. 側邊欄導覽：嚴格只顯示 L1 一級大部門
    st.sidebar.markdown("### 🏢 企業組織樹狀導覽")
    
    current_selected_id = st.session_state.get('selected_module_id', None)
    l1_depts = [d for d in departments if d["level"] == "L1" or d["parent"] == "None" or not d["parent"]]
    
    l1_ids = [d['id'] for d in l1_depts]
    if current_selected_id not in l1_ids and l1_depts:
        current_selected_id = l1_depts[0]['id']
        st.session_state['selected_module_id'] = current_selected_id

    for l1 in l1_depts:
        is_current = (l1['id'] == current_selected_id)
        if st.sidebar.button(f"📂 {l1['name_zh']} ({l1['name_vi']})", use_container_width=True, key=f"sb_l1_{l1['id']}", type="primary" if is_current else "secondary"):
            st.session_state['selected_module_id'] = l1['id']
            st.session_state.pop('selected_sub_dept_id', None) # 切換 L1 時清除二級部門焦點
            st.session_state['current_view'] = 'dashboard'
            st.rerun()

    st.sidebar.divider()
    
    if st.sidebar.button("⚙️ 系統設定 (Cấu hình hệ thống)", use_container_width=True, key="sb_sys_config_fixed"):
        st.session_state['current_view'] = 'dynamic_feature'
        st.session_state['active_feature_id'] = 'feat_it_menu'
        st.rerun()

    # 3. 判斷當前要顯示的是 L1 大部門 還是 被點擊進入的 L2 二級部門
    active_sub_id = st.session_state.get('selected_sub_dept_id', None)
    
    if active_sub_id:
        current_target = next((d for d in departments if d['id'] == active_sub_id), None)
    else:
        current_target = next((d for d in l1_depts if d['id'] == current_selected_id), l1_depts[0] if l1_depts else None)

    if current_target:
        # 如果目前在檢視二級部門，提供返回按鈕
        if active_sub_id:
            if st.button("⬅️ 返回上一層大部門", type="secondary"):
                st.session_state.pop('selected_sub_dept_id', None)
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

        st.subheader(f"📂 {current_target['name_zh']} - 功能儀表板")
        st.caption(f"部門代碼: {current_target['id']} | 層級: {current_target['level']} | 越文名稱: {current_target['name_vi']}")
        st.markdown("<br>", unsafe_allow_html=True)

        # 若是管理部 L1，顯示戰情指標
        if ("管理部" in current_target['name_zh'] or current_target['id'] == 'mgmt') and not active_sub_id:
            st.markdown("### 📊 管理部主管即時統合戰情指標")
            st.caption("以下為管理部各課室本月即時統合數據，供主管第一時間掌握全盤動態：")
            try:
                from modules.management.supervisor_dashboard import render as render_supervisor
                render_supervisor(db_engine, lang=st.session_state.get('current_lang', 'zh'))
            except Exception as e:
                st.warning(f"戰情資料載入提示: {e}")
            st.markdown("---")
            st.subheader("⚙️ 隸屬二級部門與業務模組")

        # 4. 若當前是 L1 大部門，主畫面下方展現下屬二級部門卡片
        if not active_sub_id:
            sub_departments = [d for d in departments if d["parent"] == current_target['id']]
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
                            if st.button(f"進入 {sub['name_zh']} ➡️", key=f"btn_sub_dept_{sub['id']}", use_container_width=True, type="primary"):
                                st.session_state['selected_sub_dept_id'] = sub['id']
                                st.rerun()
                st.markdown("---")

        # 5. 從資料庫動態讀取當前部門（L1 或 L2）實際掛載的模組清單
        assigned_modules = []
        if db_engine is not None:
            try:
                with db_engine.connect() as conn:
                    df_mods = pd.read_sql(
                        text("SELECT module_name FROM sys_department_modules WHERE dept_code = :code"), 
                        con=conn, 
                        params={"code": current_target['id']}
                    )
                    if not df_mods.empty:
                        assigned_modules = df_mods["module_name"].tolist()
            except Exception:
                pass

        if not assigned_modules:
            st.info(f"💡 此部門 [{current_target['name_zh']}] 目前尚未掛載任何業務模組。您可以前往「系統設定」中自由勾選掛載！")
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
                        if st.button("進入功能 ➡️", key=f"btn_mod_{current_target['id']}_{idx}", use_container_width=True, type="primary"):
                            st.session_state['current_view'] = 'dynamic_feature'
                            st.session_state['active_feature_id'] = feat_id
                            st.rerun()
