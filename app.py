# ==========================================
# 檔案路徑：app.py
# 職責：系統主入口、登入控管與左側/頂部導覽切換
# ==========================================

import streamlit as st
from views.login import render_login_page
from views.dashboard import render_dashboard
from modules.it_system.admin_settings import render_admin_settings
from modules.base_module import render_dynamic_module

st.set_page_config(
    page_title="裕豐電機工業 SaaS ERP",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# 資料庫模擬/引擎介面
class DatabaseEngine:
    def query(self, sql, params=None):
        if "sys_modules" in sql:
            return [
                {"id": "hr", "name_zh": "人事/行政", "name_vi": "Nhân sự / Hành chính", "sort_order": 1, "is_active": True},
                {"id": "ga", "name_zh": "總務/採購", "name_vi": "Tổng vụ / Mua hàng", "sort_order": 2, "is_active": True},
                {"id": "fi", "name_zh": "財務/會計", "name_vi": "Tài chính / Kế toán", "sort_order": 3, "is_active": True},
                {"id": "it_system", "name_zh": "IT 系統管理", "name_vi": "Quản trị hệ thống IT", "sort_order": 4, "is_active": True},
            ]
        elif "sys_features" in sql:
            return [
                {"id": "feat_leave", "module_id": "hr", "name_zh": "員工請假紀錄", "name_vi": "Ghi nhận nghỉ phép", "sort_order": 1, "is_active": True},
                {"id": "feat_card", "module_id": "hr", "name_zh": "員工打卡紀錄", "name_vi": "Ghi nhận chấm công", "sort_order": 2, "is_active": True},
                {"id": "feat_po", "module_id": "ga", "name_zh": "採購申請", "name_vi": "Yêu cầu mua hàng", "sort_order": 1, "is_active": True},
                {"id": "feat_it_menu", "module_id": "it_system", "name_zh": "選單動態配置", "name_vi": "Cấu hình menu", "sort_order": 1, "is_active": True},
            ]
        elif "sys_sub_tabs" in sql:
            return [
                {"id": "tab_vn", "feature_id": "feat_leave", "name_zh": "越南員工請假紀錄", "name_vi": "Nghỉ phép nhân viên VN", "sort_order": 1, "is_active": True},
                {"id": "tab_expat", "feature_id": "feat_leave", "name_zh": "外籍幹部請假紀錄", "name_vi": "Nghỉ phép cán bộ nước ngoài", "sort_order": 2, "is_active": True},
            ]
        return []

    def execute(self, sql, params=None):
        pass

db_conn = DatabaseEngine()

# 未登入攔截
if not st.session_state['logged_in']:
    render_login_page(db_conn)
    st.stop()

# 頂部列
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

# 全域動態路由
if st.session_state['current_view'] == 'dashboard':
    render_dashboard(db_conn)
elif st.session_state['current_view'] == 'dynamic_feature':
    active_feat_id = st.session_state.get('active_feature_id')
    if active_feat_id == 'feat_it_menu':
        render_admin_settings(db_conn)
    else:
        render_dynamic_module(active_feat_id, db_conn)
