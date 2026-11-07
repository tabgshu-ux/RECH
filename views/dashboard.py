# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：卡片式部門與功能選單儀表板（支援管理部上方直接顯示統合戰情數據）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_dashboard(db_engine=None):
    st.title("🏭 裕豐電機工業 SaaS ERP - 企業導覽選單")
    st.caption("請點擊下方一級部門，或從左側選單進入對應功能儀表板。")
    st.markdown("---")

    modules = [
        {"id": "gm", "name_zh": "總經理室", "name_vi": "Văn phòng Tổng Giám đốc", "sort_order": 1},
        {"id": "mgmt", "name_zh": "管理部", "name_vi": "Bộ phận Quản lý", "sort_order": 2},
        {"id": "eng", "name_zh": "工程部", "name_vi": "Bộ phận Công trình", "sort_order": 3},
        {"id": "prod", "name_zh": "生產部", "name_vi": "Bộ phận Sản xuất", "sort_order": 4},
        {"id": "wh", "name_zh": "倉庫管理", "name_vi": "Quản lý kho", "sort_order": 5},
        {"id": "approval", "name_zh": "簽核中心", "name_vi": "Trung tâm phê duyệt", "sort_order": 6},
        {"id": "sys_config", "name_zh": "系統設定", "name_vi": "Cấu hình hệ thống", "sort_order": 7},
    ]

    # 側邊欄導覽
    st.sidebar.markdown("### 🏢 企業導覽選單")
    selected_mod_id = st.session_state.get('selected_module_id', modules[1]['id'])

    for mod in modules:
        btn_label = f"{mod['name_zh']} ({mod.get('name_vi', '')})"
        if st.sidebar.button(btn_label, use_container_width=True, key=f"sb_mod_{mod['id']}"):
            st.session_state['selected_module_id'] = mod['id']
            st.session_state['current_view'] = 'dashboard'
            st.rerun()

    current_mod = next((m for m in modules if m['id'] == selected_mod_id), modules[1])
    
    if current_mod:
        st.subheader(f"📂 {current_mod['name_zh']} - 功能儀表板")
        st.caption(current_mod.get('name_vi', ''))
        st.markdown("<br>", unsafe_allow_html=True)

        # 🌟 如果是「管理部」，在功能選單上方直接嵌入主管戰情儀表板統合資料
        if current_mod['id'] == 'mgmt':
            st.markdown("### 📊 管理部主管即時統合戰情指標")
            st.caption("以下為管理部各課室本月即時統合數據，供主管第一時間掌握全盤動態：")
            
            try:
                from modules.management.supervisor_dashboard import render as render_supervisor
                render_supervisor(db_engine, lang=st.session_state.get('current_lang', 'zh'))
            except Exception as e:
                st.warning(f"戰情資料載入提示: {e}")

            st.markdown("---")
            st.subheader("⚙️ 管理部子功能操作選單")

        # 定義該部門底下的子功能卡片
        features = []
        if current_mod['id'] == 'mgmt':
            features = [
                {"id": "feat_mgmt_supervisor", "name_zh": "管理部主管綜合戰情室", "name_vi": "Báo cáo tổng hợp quản lý"},
                {"id": "feat_hr", "name_zh": "人事/行政管理", "name_vi": "Nhân sự / Hành chính"},
                {"id": "feat_ga", "name_zh": "總務/採購管理", "name_vi": "Tổng vụ / Mua hàng"},
                {"id": "feat_fi", "name_zh": "財務/會計管理", "name_vi": "Tài chính / Kế toán"}
            ]
        elif current_mod['id'] == 'gm':
            features = [{"id": "feat_gm_rpt", "name_zh": "經營營運報表", "name_vi": "Báo cáo vận hành"}]
        elif current_mod['id'] == 'eng':
            features = [
                {"id": "feat_site_log", "name_zh": "工地日報與巡檢", "name_vi": "Nhật ký công trình"},
                {"id": "feat_dispatch", "name_zh": "工務派工與調度", "name_vi": "Điều động công trình"}
            ]
        elif current_mod['id'] == 'prod':
            features = [{"id": "feat_panel_build", "name_zh": "配電盤組裝進度", "name_vi": "Tiến độ lắp ráp tủ điện"}]
        elif current_mod['id'] == 'wh':
            features = [{"id": "feat_material", "name_zh": "工程領料與工具借還", "name_vi": "Xuất vật tư & Dụng cụ"}]
        elif current_mod['id'] == 'approval':
            features = [{"id": "feat_my_approvals", "name_zh": "待簽核單據彙整", "name_vi": "Danh sách cần duyệt"}]
        elif current_mod['id'] == 'sys_config':
            features = [{"id": "feat_it_menu", "name_zh": "選單與動態架構配置", "name_vi": "Cấu hình menu"}]

        # 以卡片網格渲染功能
        cols = st.columns(3)
        for idx, feat in enumerate(features):
            col = cols[idx % 3]
            with col:
                with st.container(border=True):
                    st.markdown(f"#### {feat['name_zh']}")
                    st.caption(feat.get('name_vi', ''))
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("進入功能 ➡️", key=f"btn_feat_{feat['id']}", use_container_width=True, type="primary"):
                        st.session_state['current_view'] = 'dynamic_feature'
                        st.session_state['active_feature_id'] = feat['id']
                        st.rerun()
