# ==========================================
# 檔案路徑：app.py
# 職責：對齊裕豐 7 大一級部門標準順序與全域路由（對接卡片式儀表板）
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
if 'current_lang' not in st.session_state:
    st.session_state['current_lang'] = 'zh'

# 100% 嚴格對齊你指定的一級部門與排序 (Metadata)
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
                
                # 系統設定
                {"id": "feat_it_menu", "module_id": "sys_config", "name_zh": "選單動態配置", "name_vi": "Cấu hình menu", "sort_order": 1, "is_active": True},
            ]
        elif "sys_sub_tabs" in sql:
            return [
                {"id": "tab_emp_data", "feature_id": "feat_hr", "name_zh": "員工資料管理", "name_vi": "Quản lý nhân sự", "sort_order": 1, "is_active": True},
                {"id": "tab_card_rec", "feature_id": "feat_hr", "name_zh": "員工打卡紀錄", "name_vi": "Ghi nhận chấm công", "sort_order": 2, "is_active": True},
                {"id": "tab_contract", "feature_id": "feat_hr", "name_zh": "員工合約管理", "name_vi": "Quản lý hợp đồng", "sort_order": 3, "is_active": True},
                {"id": "tab_salary", "feature_id": "feat_hr", "name_zh": "員工薪資與保險", "name_vi": "Lương & Bảo hiểm", "sort_order": 4, "is_active": True},
                {"id": "tab_leave_rec", "feature_id": "feat_hr", "name_zh": "員工請假紀錄", "name_vi": "Ghi nhận nghỉ phép", "sort_order": 5, "is_active": True},
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
