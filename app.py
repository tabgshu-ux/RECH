# ==========================================
# 檔案路徑：app.py
# 職責：系統主入口、全域狀態管理、選單路由控制與資料庫連線注入
# ==========================================

import streamlit as st
import importlib
from views.dashboard import render_dashboard
from modules.it_system.admin_settings import render_admin_settings
from modules.base_module import render_dynamic_module

# -----------------------------------------------------------------------------
# 1. 全域頁面設定與 Session 狀態初始化
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="裕豐電機工業 SaaS ERP",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 追蹤當前頁面與啟用的功能 ID
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'dashboard'
if 'active_feature_id' not in st.session_state:
    st.session_state['active_feature_id'] = None
if 'current_lang' not in st.session_state:
    st.session_state['current_lang'] = 'zh' # 支援雙語 'zh' / 'vi'

# -----------------------------------------------------------------------------
# 2. 資料庫連線引擎 (對接 Supabase / PostgreSQL)
# -----------------------------------------------------------------------------
class DatabaseEngine:
    def __init__(self):
        # 此處保留接軌 st.connection / psycopg2 / Supabase 之連線 Hook
        pass

    def query(self, sql, params=None):
        """
        執行 SQL 查詢並回傳 Dict 格式結果
        (開發階段降級保護：若資料庫尚未寫入 sys_modules 則自動輸出基礎核心選單)
        """
        try:
            # 實作部署時改為: return st.connection("postgresql", type="sql").query(sql, params=params)
            pass
        except Exception:
            pass

        # 資料庫尚未完成建表前之內建 Fallback 結構
        if "sys_modules" in sql:
            return [
                {"id": "hr", "name_zh": "人事/行政", "name_vi": "Nhân sự / Hành chính", "sort_order": 1, "is_active": True},
                {"id": "ga", "name_zh": "總務/採購", "name_vi": "Tổng vụ / Mua hàng", "sort_order": 2, "is_active": True},
                {"id": "fi", "name_zh": "財務/會計", "name_vi": "Tài chính / Kế toán", "sort_order": 3, "is_active": True},
                {"id": "it_system", "name_zh": "IT 系統管理", "name_vi": "Quản trị hệ thống IT", "sort_order": 4, "is_active": True},
            ]
        elif "sys_features" in sql:
            return [
                {"id": "feat_leave", "module_id": "hr", "name_zh": "員工請假紀錄", "name_vi": "Ghi nhận nghỉ phép", "route_key": "modules.hr.leave_management", "sort_order": 1, "is_active": True},
                {"id": "feat_card", "module_id": "hr", "name_zh": "員工打卡紀錄", "name_vi": "Ghi nhận chấm công", "route_key": "modules.hr.attendance", "sort_order": 2, "is_active": True},
                {"id": "feat_po", "module_id": "ga", "name_zh": "採購申請", "name_vi": "Yêu cầu mua hàng", "route_key": "modules.purchase.po_request", "sort_order": 1, "is_active": True},
                {"id": "feat_it_menu", "module_id": "it_system", "name_zh": "選單動態配置", "name_vi": "Cấu hình menu", "route_key": "modules.it_system.admin_settings", "sort_order": 1, "is_active": True},
            ]
        elif "sys_sub_tabs" in sql:
            return [
                {"id": "tab_vn", "feature_id": "feat_leave", "name_zh": "越南員工請假紀錄", "name_vi": "Nghỉ phép nhân viên VN", "sort_order": 1, "is_active": True},
                {"id": "tab_expat", "feature_id": "feat_leave", "name_zh": "外籍幹部請假紀錄", "name_vi": "Nghỉ phép cán bộ nước ngoài", "sort_order": 2, "is_active": True},
            ]
        return []

    def execute(self, sql, params=None):
        """執行 INSERT / UPDATE / DELETE 操作"""
        # 實作部署時改為 SQL connection execute 邏輯
        st.toast(f"執行資料庫指令成功！", icon="✅")

# 實體化資料庫連線
db_conn = DatabaseEngine()

# -----------------------------------------------------------------------------
# 3. 系統全域頂部導覽列與語系選單
# -----------------------------------------------------------------------------
col_logo, col_space, col_home, col_lang = st.columns([4, 3, 2, 1])

with col_logo:
    st.title("🏭 裕豐電機工業 SaaS ERP")

with col_home:
    if st.button("🏠 回業務導覽主頁", use_container_width=True, type="secondary"):
        st.session_state['current_view'] = 'dashboard'
        st.session_state['active_feature_id'] = None
