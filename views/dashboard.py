# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：100% 資料庫動態驅動的企業導覽與部門功能儀表板（左側選單完全對應資料庫，絕不寫死）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_dashboard(db_engine=None):
    st.title("🏭 裕豐電機工業 SaaS ERP - 企業導覽選單")
    st.caption("系統已實現 100% 網頁配置化架構：左側部門選單與各部門掛載模組完全由資料庫動態驅動。")
    st.markdown("---")

    # 1. 從資料庫動態讀取所有啟用的部門（1~4級樹狀結構）
    dynamic_departments = []
    if db_engine is not None:
        try:
            with db_engine.connect() as conn:
                df_depts = pd.read_sql(
                    text("SELECT dept_code, dept_name_zh, dept_name_vi, level_depth, parent_code FROM sys_departments WHERE is_active = TRUE ORDER BY id ASC"), 
                    con=conn
                )
                if not df_depts.empty:
                    for _, row in df_depts.iterrows():
                        dynamic_departments.append({
                            "id": row["dept_code"],
                            "name_zh": row["dept_name_zh"],
                            "name_vi": row["dept_name_vi"] or "",
                            "level": row["level_depth"] or "L1",
                            "parent": row["parent_code"]
                        })
        except Exception:
            pass

    # 若資料庫無資料時的緊急安全預設值
    if not dynamic_departments:
        dynamic_departments = [
            {"id": "gm", "name_zh": "總經理室", "name_vi": "Văn phòng Tổng Giám đốc", "level": "L1", "parent": None},
            {"id": "mgmt", "name_zh": "管理部", "name_vi": "Bộ phận Quản lý", "level": "L1", "parent": None},
        ]

    # 2. 側邊欄動態選單渲染（完全對應資料庫資料）
    st.sidebar.markdown("### 🏢 企業動態導覽選單")
    
    # 取得目前 session 中記錄的選中部門 ID，若無則預設為資料庫中的第一筆部門
    current_selected_id = st.session_state.get('selected_module_id', None)
    valid_ids = [d['id'] for d in dynamic_departments]
    
    if current_selected_id not in valid_ids:
        current_selected_id = dynamic_departments[0]['id']
        st.session_state['selected_module_id'] = current_selected_id

    # 渲染資料庫中的所有動態部門按鈕
    for dept in dynamic_departments:
        indent = ""
        if dept["level"] == "L2": indent = "    └ 📁 "
        elif dept["level"] == "L3": indent = "        └ 📁 "
        elif dept["level"] == "L4": indent = "            └ 📁 "
        else: indent = "📂 "

        btn_label = f"{indent}{dept['name_zh']} ({dept['name_vi']})"
        
        # 標註當前選中狀態
        is_current = (dept['id'] == current_selected_id)
        
        if st.sidebar.button(btn_label, use_container_width=True, key=f"sb_dept_{dept['id']}", type="primary" if is_current else "secondary"):
            st.session_state['selected_module_id'] = dept['id']
            st.session_state['current_view'] = 'dashboard'
            st.rerun()

    st.sidebar.divider()
    
    # 唯一固定常駐的系統設定入口
    if st.sidebar.button("⚙️ 系統設定 (Cấu hình hệ thống)", use_container_width=True, key="sb_sys_config_fixed"):
        st.session_state['current_view'] = 'dynamic_feature'
        st.session_state['active_feature_id'] = 'feat_it_menu'
        st.rerun()

    # 3. 取得當前選中的部門詳細資料
    current_dept = next((d for d in dynamic_departments if d['id'] == current_selected_id), dynamic_departments[0])
    
    if current_dept:
        st.subheader(f"📂 {current_dept['name_zh']} - 功能儀表板")
        st.caption(f"部門代碼: {current_dept['id']} | 層級: {current_dept['level']} | 越文名稱: {current_dept['name_vi']}")
        st.markdown("<br>", unsafe_allow_html=True)

        # 🌟 如果是「管理部」，上方直接嵌入主管戰情儀表板統合資料
        if current_dept['id'] == 'mgmt':
            st.markdown("### 📊 管理部主管即時統合戰情指標")
            st.caption("以下為管理部各課室本月即時統合數據，供主管第一時間掌握全盤動態：")
            try:
                from modules.management.supervisor_dashboard import render as render_supervisor
                render_supervisor(db_engine, lang=st.session_state.get('current_lang', 'zh'))
            except Exception as e:
                st.warning(f"戰情資料載入提示: {e}")
            st.markdown("---")
            st.subheader("⚙️ 管理部子功能操作選單")

        # 4. 從資料庫動態讀取該部門實際掛載的模組清單
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
            st.info(f"💡 此部門 [{current_dept['name_zh']}] 目前尚未掛載任何業務模組。您可以前往「系統設定 ➡️ 公司部門及功能設定」中勾選並掛載對應的模組！")
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
