# ==========================================
# 檔案路徑：app.py
# 職責：裕豐 SaaS ERP 統一入口、動態租戶識別、卡片式儀表板路由與 7 大系統設定中心分流
# ==========================================

import streamlit as st
import pandas as pd
import importlib
from sqlalchemy import text
from modules.it_system.admin_settings import get_department_module_tree, render_admin_settings
from views.login import render_login_page
from views.dashboard import render_dashboard

st.set_page_config(
    page_title="裕豐電機工業 SaaS ERP",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

MOBILE_CSS_AND_JS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.35rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.15rem !important; }
    h3, .stSubheader { font-size: 1.05rem !important; }
    p, div, span, label { font-size: 0.9rem !important; }
    .block-container { padding: 1rem 0.5rem !important; }
}
</style>
"""
st.markdown(MOBILE_CSS_AND_JS, unsafe_allow_html=True)

# 狀態初始化
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'dashboard'
if 'active_feature_id' not in st.session_state:
    st.session_state['active_feature_id'] = None
if 'selected_module_id' not in st.session_state:
    st.session_state['selected_module_id'] = None
if 'current_lang' not in st.session_state:
    st.session_state['current_lang'] = 'zh'

# 100% 嚴格對齊 7 大一級部門與功能 Metadata
class DatabaseEngine:
    def query(self, sql, params=None):
        if "sys_modules" in sql:
            return [
                {"id": "gm", "name_zh": "總經理室", "name_vi": "Văn phòng Tổng Giám đốc", "sort_order": 1, "is_active": True},
                {"id": "mgmt", "name_zh": "管理部", "name_vi": "Bộ phận Quản lý", "sort_order": 2, "is_active": True},
                {"id": "eng", "name_zh": "工程部", "name_vi": "Bộ phận Công trình", "sort_order": 3, "is_active": True},
                {"id": "prod", "name_zh": "生產部", "name_vi": "Bộ phận Sản xuất", "sort_order": 4, "is_active": True},
                {"id": "wh", "name_zh": "倉庫管理", "name_vi": "Quản lý kho", "sort_order": 5, "is_active": True},
                {"id": "approval", "name_zh": "簽核中心", "name_vi": "Trung tâm phê duyệt", "sort_order": 6, "is_active": True},
                {"id": "sys_config", "name_zh": "系統設定", "name_vi": "Cấu hình hệ thống", "sort_order": 7, "is_active": True},
            ]
        elif "sys_features" in sql:
            return [
                # 總經理室
                {"id": "feat_gm_rpt", "module_id": "gm", "name_zh": "經營營運報表", "name_vi": "Báo cáo vận hành", "sort_order": 1, "is_active": True},
                {"id": "feat_gm_ai", "module_id": "gm", "name_zh": "原料價格與 Gemini 智慧採購顧問", "name_vi": "Tư vấn AI mua hàng", "sort_order": 2, "is_active": True},
                {"id": "feat_gm_fi", "module_id": "gm", "name_zh": "財務類與 AR/AP & P&L 戰情儀表板", "name_vi": "Bảng điều khiển tài chính", "sort_order": 3, "is_active": True},
                {"id": "feat_gm_eng", "module_id": "gm", "name_zh": "工程專案進度與現場異常即時監控", "name_vi": "Giám sát tiến độ công trình", "sort_order": 4, "is_active": True},
                {"id": "feat_gm_pol", "module_id": "gm", "name_zh": "越南經營政策與法規每日動態", "name_vi": "Chính sách pháp luật VN", "sort_order": 5, "is_active": True},

                # 管理部
                {"id": "feat_hr", "module_id": "mgmt", "name_zh": "人事/行政", "name_vi": "Nhân sự / Hành chính", "sort_order": 1, "is_active": True},
                {"id": "feat_ga", "module_id": "mgmt", "name_zh": "總務/採購", "name_vi": "Tổng vụ / Mua hàng", "sort_order": 2, "is_active": True},
                {"id": "feat_fi", "module_id": "mgmt", "name_zh": "財務/會計", "name_vi": "Tài chính / Kế toán", "sort_order": 3, "is_active": True},
                
                # 工程部
                {"id": "feat_site_log", "module_id": "eng", "name_zh": "工地日報與巡檢", "name_vi": "Nhật ký công trình", "sort_order": 1, "is_active": True},
                {"id": "feat_dispatch", "module_id": "eng", "name_zh": "工務派工與調度", "name_vi": "Điều động công trình", "sort_order": 2, "is_active": True},
                
                # 生產部
                {"id": "feat_panel_build", "module_id": "prod", "name_zh": "配電盤組裝進度", "name_vi": "Tiến độ lắp ráp tủ điện", "sort_order": 1, "is_active": True},
                
                # 倉庫管理
                {"id": "feat_material", "module_id": "wh", "name_zh": "工程領料與工具借還", "name_vi": "Xuất vật tư & Dụng cụ", "sort_order": 1, "is_active": True},
                {"id": "feat_invcheck", "module_id": "wh", "name_zh": "倉儲盤點", "name_vi": "Kiểm kê kho", "sort_order": 2, "is_active": True},
                
                # 簽核中心
                {"id": "feat_my_approvals", "module_id": "approval", "name_zh": "待簽核單據彙整", "name_vi": "Danh sách cần duyệt", "sort_order": 1, "is_active": True},
                
                # 系統設定 (對應 7 大動態配置中心)
                {"id": "feat_it_menu", "module_id": "sys_config", "name_zh": "選單與動態架構配置", "name_vi": "Cấu hình menu", "sort_order": 1, "is_active": True},
            ]
        return []

    def execute(self, sql, params=None):
        pass

db_conn = DatabaseEngine()

# 未登入攔截
if not st.session_state['logged_in']:
    render_login_page(db_conn)
    st.stop()

# 頂部導覽列
col_logo, col_user, col_nav, col_logout = st.columns([5, 2, 2, 1])
with col_logo:
    st.subheader("🏭 裕豐電機工業 SaaS ERP")
with col_user:
    st.caption(f"👤 {st.session_state['user_name']}")
with col_nav:
    if st.session_state['current_view'] != 'dashboard':
        if st.button("🏠 回部門選單", use_container_width=True):
            st.session_state['current_view'] = 'dashboard'
            st.session_state['active_feature_id'] = None
            st.rerun()
with col_logout:
    if st.button("🚪 登出", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['current_view'] = 'dashboard'
        st.rerun()

st.divider()

# 全域動態路由分流
if st.session_state['current_view'] == 'dashboard':
    render_dashboard(db_conn)
elif st.session_state['current_view'] == 'dynamic_feature':
    active_feat_id = st.session_state.get('active_feature_id')
    
    if active_feat_id == 'feat_it_menu':
        render_admin_settings(db_conn, lang=st.session_state.get('current_lang', 'zh'))
    elif active_feat_id == 'feat_gm_rpt':
        try:
            from modules.executive_dashboard import render_executive_dashboard_page
            render_executive_dashboard_page(lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.error(f"載入總經理室報表發生錯誤: {e}")
    elif active_feat_id == 'feat_gm_ai':
        try:
            from modules.executive_dashboard import render_executive_dashboard_page
            render_executive_dashboard_page(sub_route="commodities_fx", lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.error(f"載入原料價格與 Gemini 顧問發生錯誤: {e}")
    elif active_feat_id == 'feat_gm_fi':
        try:
            from modules.executive_dashboard import render_executive_dashboard_page
            render_executive_dashboard_page(sub_route="financials_pl", lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.error(f"載入財務戰情儀表板發生錯誤: {e}")
    elif active_feat_id == 'feat_gm_eng':
        try:
            from modules.executive_dashboard import render_executive_dashboard_page
            render_executive_dashboard_page(sub_route="project_progress_exec", lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.error(f"載入工程進度監控發生錯誤: {e}")
    elif active_feat_id == 'feat_gm_pol':
        try:
            from modules.vietnam_policy_news import render_vietnam_policy_news_page
            render_vietnam_policy_news_page(engine=None, lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.error(f"載入越南法規動態發生錯誤: {e}")
    elif active_feat_id == 'feat_hr':
        try:
            from modules.employee_management import render_employee_management
            render_employee_management(db_conn, lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.error(f"載入人事管理模組發生錯誤: {e}")
    elif active_feat_id == 'feat_ga':
        try:
            from modules.procurement_ap import render_procurement_ap_page
            render_procurement_ap_page(db_conn, lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.error(f"載入總務採購模組發生錯誤: {e}")
    elif active_feat_id == 'feat_fi':
        try:
            from modules.financial_tax_reports import render_financial_tax_reports_page
            render_financial_tax_reports_page(db_conn, lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.error(f"載入財務會計模組發生錯誤: {e}")
    elif active_feat_id == 'feat_site_log':
        try:
            from modules.engineering_management import render_engineering_management_page
            render_engineering_management_page(db_conn, lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.error(f"載入工程管理模組發生錯誤: {e}")
    elif active_feat_id == 'feat_panel_build':
        try:
            from modules.assembly import render_assembly_module
            render_assembly_module(db_conn, lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.error(f"載入生產組裝模組發生錯誤: {e}")
    elif active_feat_id == 'feat_material':
        try:
            from modules.warehouse_management import render_warehouse_management
            render_warehouse_management(db_conn, lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.error(f"載入倉庫管理模組發生錯誤: {e}")
    elif active_feat_id == 'feat_my_approvals':
        try:
            from modules.approval_workflow import render_approval_center
            render_approval_center(lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.error(f"載入簽核中心發生錯誤: {e}")
    else:
        st.info(f"💡 功能代碼 [{active_feat_id}] 正在建置中，您可以透過上方按鈕返回部門選單。")
