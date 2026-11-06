# ==========================================
# 檔案路徑：app.py
# 職責：系統主入口、全域狀態管理與分流路由
# ==========================================

import streamlit as st
from views.dashboard import render_dashboard
from views.admin_settings import render_admin_settings
from modules.base_module import render_dynamic_module

# 模擬資料庫連線 (實作時替換為 Supabase/PostgreSQL 連線)
class DummyDB:
    def query(self, sql, params=None):
        # 這裡未來會接真實資料庫，先回傳範例結構測試
        if "sys_modules" in sql:
            return [
                {"id": "hr", "name_zh": "人事/行政", "name_vi": "Nhân sự / Hành chính", "sort_order": 1},
                {"id": "ga", "name_zh": "總務/採購", "name_vi": "Tổng vụ / Mua hàng", "sort_order": 2},
                {"id": "fi", "name_zh": "財務/會計", "name_vi": "Tài chính / Kế toán", "sort_order": 3},
            ]
        elif "sys_features" in sql:
            return [
                {"id": "feat_leave", "module_id": "hr", "name_zh": "員工請假紀錄", "name_vi": "Ghi nhận nghỉ phép", "route_key": "leave_mgmt", "sort_order": 1},
                {"id": "feat_card", "module_id": "hr", "name_zh": "員工打卡紀錄", "name_vi": "Ghi nhận chấm công", "route_key": "card_mgmt", "sort_order": 2},
                {"id": "feat_po", "module_id": "ga", "name_zh": "採購申請", "name_vi": "Yêu cầu mua hàng", "route_key": "po_mgmt", "sort_order": 1},
            ]
        elif "sys_sub_tabs" in sql:
            return [
                {"id": "tab_vn", "feature_id": "feat_leave", "name_zh": "越南員工請假紀錄", "name_vi": "Nghỉ phép nhân viên VN", "sort_order": 1},
                {"id": "tab_expat", "feature_id": "feat_leave", "name_zh": "外籍幹部請假紀錄", "name_vi": "Nghỉ phép cán bộ nước ngoài", "sort_order": 2},
            ]
        return []

    def execute(self, sql, params=None):
        pass

# 頁面寬度設定
st.set_page_config(page_title="裕豐 ERP 系統", layout="wide")

# 初始化全域 Session 狀態
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'dashboard'
if 'active_feature_id' not in st.session_state:
    st.session_state['active_feature_id'] = None

db_conn = DummyDB()

# 全域頂部導覽列
col_title, col_btn1, col_btn2 = st.columns([7, 2, 2])
with col_title:
    st.title("裕豐電機工業 SaaS ERP")
with col_btn1:
    if st.button("🏠 回業務主頁", use_container_width=True):
        st.session_state['current_view'] = 'dashboard'
        st.session_state['active_feature_id'] = None
        st.rerun()
with col_btn2:
    if st.button("⚙️ 系統選單配置", use_container_width=True):
        st.session_state['current_view'] = 'admin_settings'
        st.rerun()

st.divider()

# 動態分流路由
if st.session_state['current_view'] == 'dashboard':
    render_dashboard(db_conn)
elif st.session_state['current_view'] == 'admin_settings':
    render_admin_settings(db_conn)
elif st.session_state['current_view'] == 'dynamic_feature':
    render_dynamic_module(st.session_state['active_feature_id'], db_conn)
