# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：支援 1~4 級樹狀階層的動態企業導覽選單（嚴格依循 Parent-Child 組織架構，L2 確實收納於 L1 底下）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_dashboard(db_engine=None):
    st.title("🏭 裕豐電機工業 SaaS ERP - 企業導覽選單")
    st.caption("系統已實現 100% 網頁配置化架構：左側部門選單嚴格依照 1~4 級組織樹狀結構（Parent-Child）動態呈現。")
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
                            "parent": row["parent_code"] or "無"
                        })
        except Exception:
            pass

    # 若資料庫無資料時的預設 Fallback
    if not departments:
        departments = [
            {"id": "gm", "name_zh": "總經理室", "name_vi": "Văn phòng Tổng Giám đốc", "level": "L1", "parent": "無"},
            {"id": "mgmt", "name_zh": "管理部", "name_vi": "Bộ phận Quản lý", "level": "L1", "parent": "無"},
        ]

    # 2. 側邊欄階層式樹狀導覽選單渲染
    st.sidebar.markdown("### 🏢 企業組織樹狀導覽")
    
    current_selected_id = st.session_state.get('selected_module_id', None)
    valid_ids = [d['id'] for d in departments]
    if current_selected_id not in valid_ids:
        current_selected_id = departments[0]['id']
        st.session_state['selected_module_id'] = current_selected_id

    # 篩選出 L1 根目錄部門與下層子部門
    l1_depts = [d for d in departments if d["level"] == "L1" or d["parent"] == "無" or not d["parent"]]
    
    for l1 in l1_depts:
        is_l1_current = (l1['id'] == current_selected_id)
        l1_label = f"📂 {l1['name_zh']} ({l1['name_vi']})"
        
        # 渲染 L1 大部門按鈕
        if st.sidebar.button(l1_label, use_container_width=True, key=f"sb_dept_l1_{l1['id']}", type="primary" if is_l1_current else "secondary"):
            st.session_state['selected_module_id'] = l1['id']
            st.session_state['current_view'] = 'dashboard'
            st.rerun()

        # 尋找並渲染屬於這個 L1 底下的 L2 / L3 / L4 子部門（例如管理部底下的「人事/行政」）
        sub_depts = [d for d in departments if d["parent"] == l1['id'] or (d["parent"] and l1['name_zh'] in d["parent"])]
        for sub in sub_depts:
            is_sub_current = (sub['id'] == current_selected_id)
            sub_label = f"    └ 📁 {sub['name_zh']} ({sub['name_vi']})"
            
            if st.sidebar.button(sub_label, use_container_width=True, key=f"sb_dept_sub_{sub['id']}", type="primary" if is_sub_current else "secondary"):
                st.session_state['selected_module_id'] = sub['id']
                st.session_state['current_view'] = 'dashboard'
                st.rerun()

    st.sidebar.divider()
    
    # 唯一固定常駐的系統設定入口
    if st.sidebar.button("⚙️ 系統設定 (Cấu hình hệ thống)", use_container_width=True, key="sb_sys_config_fixed"):
        st.session_state['current_view'] = 'dynamic_feature'
        st.session_state['active_feature_id'] = 'feat_it_menu'
        st.rerun()

    # 3. 取得當前選中的部門詳細資料
    current_dept = next((d for d in departments if d['id'] == current_selected_id), departments[0])
    
    if current_dept:
        st.subheader(f"📂 {current_dept['name_zh']} - 功能儀表板")
        st.caption(f"部門層級: {current_dept['level']} | 上層歸屬: {current_dept['parent']} | 越文名稱: {current_dept['name_vi']}")
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
            st.subheader("⚙️ 部門子功能操作選單")

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
