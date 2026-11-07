# ==========================================
# 檔案路徑：app.py
# 職責：系統主入口，統一管理初始化、Session State、導覽列與動態模組分發路由
# ==========================================

import streamlit as st
import pandas as pd
import importlib
import os
from sqlalchemy import text, create_engine
from modules.it_system.admin_settings import render_admin_settings
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

@st.cache_resource
def get_db_engine():
    db_url = os.environ.get("SUPABASE_DB_URL") or st.secrets.get("SUPABASE_DB_URL", "")
    if db_url:
        clean_url = db_url.strip()
        if "pooler.supabase.com" in clean_url and "?" not in clean_url:
            clean_url += "?sslmode=require"
        try:
            return create_engine(clean_url, pool_pre_ping=True, connect_args={"prepare_threshold": None})
        except Exception:
            return None
    return None

db_engine = get_db_engine()

if not st.session_state['logged_in']:
    render_login_page(db_engine)
    st.stop()

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

current_lang = st.session_state.get('current_lang', 'zh')

if st.session_state['current_view'] == 'dashboard':
    render_dashboard(db_engine)
elif st.session_state['current_view'] == 'dynamic_feature':
    active_feat_id = str(st.session_state.get('active_feature_id', ''))
    
    # 🌟 IT 系統設定
    if active_feat_id == 'feat_it_menu':
        render_admin_settings(db_engine, lang=current_lang)
        
    # 🌟 管理部主管戰情室
    elif active_feat_id == 'feat_mgmt_supervisor':
        try:
            from modules.management.supervisor_dashboard import render
            render(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入管理部主管戰情室發生錯誤: {e}")
            
    # 🌟 智慧判斷：獨立導向員工檔案、考勤、薪資頁面（完美避開 __init__.py 攔截）
    elif '員工' in active_feat_id or '履約' in active_feat_id or active_feat_id == 'feat_hr':
        try:
            from modules.management.hr.employee import employee_profile
            if hasattr(employee_profile, "render_hr_profile_page"):
                employee_profile.render_hr_profile_page(engine=db_engine, lang=current_lang)
            elif hasattr(employee_profile, "render"):
                employee_profile.render(db_engine=db_engine, lang=current_lang)
            else:
                st.error("找不到 employee_profile 的渲染入口函式。")
        except Exception as e:
            st.error(f"載入員工檔案管理模組發生錯誤: {e}")

    elif '考勤' in active_feat_id or '打卡' in active_feat_id:
        try:
            from modules.management.hr.attendance import attendance_punch
            if hasattr(attendance_punch, "render"):
                attendance_punch.render(db_engine=db_engine, lang=current_lang)
            elif hasattr(attendance_punch, "main"):
                attendance_punch.main(db_engine=db_engine, lang=current_lang)
            else:
                st.info("⏱️ 考勤打卡模組已載入。")
        except Exception as e:
            st.error(f"載入考勤打卡模組發生錯誤: {e}")

    elif '薪資' in active_feat_id or '保險' in active_feat_id or 'BHXH' in active_feat_id:
        try:
            from modules.management.hr import payroll_management
            if hasattr(payroll_management, "render"):
                payroll_management.render(db_engine=db_engine, lang=current_lang)
            elif hasattr(payroll_management, "render_payroll_management"):
                payroll_management.render_payroll_management(db_engine=db_engine, lang=current_lang)
            else:
                st.info("💰 薪資計算與保險模組已載入。")
        except Exception as e:
            st.error(f"載入薪資保險模組發生錯誤: {e}")

    # 🌟 其他部門模組路由
    elif active_feat_id == 'feat_ga':
        try:
            from modules.procurement_ap import render_procurement_ap_page
            render_procurement_ap_page(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入總務採購模組發生錯誤: {e}")
    elif active_feat_id == 'feat_fi':
        try:
            from modules.financial_tax_reports import render_financial_tax_reports_page
            render_financial_tax_reports_page(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入財務會計模組發生錯誤: {e}")
    elif active_feat_id == 'feat_site_log':
        try:
            from modules.engineering_management import render_engineering_management_page
            render_engineering_management_page(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入工程管理模組發生錯誤: {e}")
    elif active_feat_id == 'feat_panel_build':
        try:
            from modules.assembly import render_assembly_module
            render_assembly_module(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入生產組裝模組發生錯誤: {e}")
    elif active_feat_id == 'feat_material':
        try:
            from modules.warehouse_management import render_warehouse_management
            render_warehouse_management(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入倉庫管理模組發生錯誤: {e}")
    elif active_feat_id == 'feat_my_approvals':
        try:
            from modules.approval_workflow import render_approval_center
            render_approval_center(lang=current_lang)
        except Exception as e:
            st.error(f"載入簽核中心發生錯誤: {e}")
    else:
        st.info(f"💡 功能代碼 [{active_feat_id}] 正在建置中，您可以透過上方按鈕返回部門選單。")
