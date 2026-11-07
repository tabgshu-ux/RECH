# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：卡片式部門與功能選單儀表板（相容真實 SQLAlchemy Engine）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_dashboard(db_engine=None):
    st.title("🏭 裕豐電機工業 SaaS ERP - 企業導覽選單")
    st.caption("請點擊下方一級部門，或從左側選單進入對應功能儀表板。")
    st.markdown("---")

    # 讀取一級部門
    modules = []
    if db_engine is not None:
        try:
            query_str = "SELECT * FROM sys_modules WHERE is_active = TRUE ORDER BY sort_order ASC;"
            df_mods = pd.read_sql(query_str, con=db_engine)
            modules = df_mods.to_dict(orient="records")
        except Exception:
            pass

    # 若資料庫尚未初始化或無資料，提供預設標準 7 大部門
    if not modules:
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
    selected_mod_id = st.session_state.get('selected_module_id', modules[0]['id'] if modules else 'gm')

    for mod in modules:
        btn_label = f"{mod['name_zh']} ({mod.get('name_vi', '')})"
        if st.sidebar.button(btn_label, use_container_width=True, key=f"sb_mod_{mod['id']}"):
            st.session_state['selected_module_id'] = mod['id']
            st.session_state['current_view'] = 'dashboard'
            st.rerun()

    # 主畫面呈現選定部門的功能儀表板
    current_mod = next((m for m in modules if m['id'] == selected_mod_id), modules[0] if modules else None)
    
    if current_mod:
        st.subheader(f"📂 {current_mod['name_zh']} - 功能儀表板")
        st.caption(current_mod.get('name_vi', ''))
        st.markdown("<br>", unsafe_allow_html=True)

        # 讀取該部門底下的功能
        features = []
        if db_engine is not None:
            try:
                feat_query = "SELECT * FROM sys_features WHERE module_id = :mid AND is_active = TRUE ORDER BY sort_order ASC;"
                df_feats = pd.read_sql(text(feat_query), con=db_engine, params={"mid": current_mod['id']})
                features = df_feats.to_dict(orient="records")
            except Exception:
                pass

        # 若資料庫無對應功能，給予預設對應項目
        if not features:
            if current_mod['id'] == 'gm':
                features = [{"id": "feat_gm_rpt", "name_zh": "經營營運報表", "name_vi": "Báo cáo vận hành"}]
            elif current_mod['id'] == 'mgmt':
                features = [
                    {"id": "feat_hr", "name_zh": "人事/行政", "name_vi": "Nhân sự / Hành chính"},
                    {"id": "feat_ga", "name_zh": "總務/採購", "name_vi": "Tổng vụ / Mua hàng"},
                    {"id": "feat_fi", "name_zh": "財務/會計", "name_vi": "Tài chính / Kế toán"}
                ]
            elif current_mod['id'] == 'eng':
                features = [
                    {"id": "feat_site_log", "name_zh": "工地日報與巡檢", "name_vi": "Nhật ký công trình"},
                    {"id": "feat_dispatch", "name_zh": "工務派工與調度", "name_vi": "Điều động công trình"}
                ]
            elif current_mod['id'] == 'prod':
                features = [{"id": "feat_panel_build", "name_zh": "配電盤組裝進度", "name_vi": "Tiến độ lắp ráp tủ điện"}]
            elif current_mod['id'] == 'wh':
                features = [
                    {"id": "feat_material", "name_zh": "工程領料與工具借還", "name_vi": "Xuất vật tư & Dụng cụ"},
                    {"id": "feat_invcheck", "name_zh": "倉儲盤點", "name_vi": "Kiểm kê kho"}
                ]
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
