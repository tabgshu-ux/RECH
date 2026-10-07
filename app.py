import inspect
import modules.approval_workflow as approval_workflow
import modules.asset_management as asset_management
import modules.contract_management as contract_management
import modules.db_connection as db_conn
import modules.employee_management as employee_management
import modules.engineering_department as engineering_department
import modules.executive_dashboard as executive_dashboard
import modules.factory_management as factory_management
import modules.field_attendance as field_attendance
import modules.invoice_management as invoice_management
import modules.payroll_management as payroll_management
import modules.procurement_ap as procurement_ap
import modules.sales_order_ar as sales_order_ar
import modules.system_licensing as system_licensing
import modules.user_management as user_management
import modules.vehicle_gate_log as vehicle_gate_log
import modules.vehicle_maintenance as vehicle_maintenance
import modules.warehouse_management as warehouse_management
import pandas as pd
from sqlalchemy import text
import streamlit as st

st.set_page_config(
    page_title="裕豐電機工業 REETECH INDUSTRIAL AI ERP",
    page_icon="⚡",
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

RECH_LOGO_HTML = """
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 15px; padding: 6px 8px; background: transparent; border-bottom: 2px solid rgba(15, 23, 42, 0.15);">
    <div style="font-size: 28px; font-weight: 900; color: #000055; letter-spacing: -1px; line-height: 1;">RECH</div>
    <div style="border-left: 2px solid #000055; padding-left: 8px; line-height: 1.15;">
        <div style="font-size: 13px; font-weight: 800; color: #000055;">裕豐電機工業有限公司</div>
        <div style="font-size: 8.5px; font-weight: 700; color: #1E293B;">REETECH INDUSTRIAL CO., LTD</div>
        <div style="font-size: 8px; font-weight: 700; color: #334155;">CÔNG TY TNHH CN DŨ PHONG</div>
    </div>
</div>
"""

NAV_STRUCTURE = {
    "繁體中文": {
        "company_name": "裕豐電機工業有限公司",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ 裕豐電機工業 REETECH INDUSTRIAL - 系統登入",
        "username": "帳號",
        "password": "密碼",
        "login_btn": "🔑 登入系統",
        "logout_btn": "🚪 登出系統",
        "lang_selector": "🌐 語言設定 / Language",
        "parent_header": "請選擇一級部門 / 系統：",
        "sub_header": "選擇子部門與功能：",
        "departments": {
            "📈 營運戰情室 (Executive)": {
                "features": {
                    "🔴 原料價格與隨時股市物價/匯率": "commodities_fx",
                    "📊 財務類顯示資料 (AR/AP & P&L)": "financials_pl",
                    "⚡ 工程專案進度與驗收資料": "project_progress_exec",
                }
            },
            "✍️ 全公司電子簽核中心 (Approval Center)": {
                "features": {
                    "✍️ 提交請假/採購與即時進度追蹤 / 審核": "approval_center",
                }
            },
            "👔 管理部 (Management Dept)": {
                "features": {
                    "👤 員工個人檔案與人事管理": "hr_employee",
                    "📍 外勤員工打卡資料與出勤統計計算": "field_attendance",
                    "🏭 廠區與工作廠區管理": "factory_mgmt",
                    "🚗 廠區車輛進出口門禁紀錄": "vehicle_gate",
                    "🛠️ 車輛維修保養紀錄": "vehicle_maintenance",
                    "🛒 採購與應付帳款 (AP)": "procurement_ap",
                    "📋 應收帳款": "sales_order_ar",
                    "💰 員工薪資管理": "payroll_calc",
                    "📄 電子發票綜合管理": "invoice_management",
                }
            },
            "🛠️ 工程與設計管理中心 (Engineering & Design Center)": {
                "features": {
                    "⚡ [工程] 配電盤與工程專案報價": "eng_quote",
                    "📊 [工程] 水電工程驗收與進度追蹤": "eng_progress",
                    "🎨 [設計] 配電盤電氣與機構設計圖庫上傳中心": "eng_design",
                }
            },
            "🏭 生產部 (Production Dept)": {
                "features": {
                    "📦 [倉儲] 倉庫庫存與資材條碼管理": "wh_management",
                    "✂️ [板金] 板金加工組工單與條碼": "sheet_metal",
                    "🎨 [塗料] 粉體塗裝烤漆組品管": "painting",
                    "⚡ [配盤] 配電盤組裝配線組": "assembly",
                }
            },
            "💻 資訊管理部 (IT & System)": {
                "features": {
                    "🔒 帳號權限與全系統稽核軌跡": "it_admin",
                    "🎛️ 客戶 ERP 模組授權與功能開關": "it_licensing",
                }
            },
        },
    },
    "Tiếng Việt": {
        "company_name": "CÔNG TY TNHH CN DŨ PHONG",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ REETECH INDUSTRIAL - Đăng nhập hệ thống",
        "username": "Tài khoản",
        "password": "Mật khẩu",
        "login_btn": "🔑 Đăng nhập",
        "logout_btn": "🚪 Đăng xuất",
        "lang_selector": "🌐 Chọn ngôn ngữ",
        "parent_header": "Chọn phòng ban chính:",
        "sub_header": "Chọn bộ phận trực thuộc:",
        "departments": {
            "📈 Ban Giám đốc (Executive)": {
                "features": {
                    "🔴 Giá Nguyên liệu & Tỷ giá": "commodities_fx",
                    "📊 Dữ liệu Tài chính": "financials_pl",
                    "⚡ Tiến độ Dự án Kỹ thuật": "project_progress_exec",
                }
            },
            "✍️ Trung tâm Phê duyệt Điện tử (Approval Center)": {
                "features": {
                    "✍️ Gửi đơn nghỉ phép/mua hàng & Theo dõi tiến độ": "approval_center",
                }
            },
            "👔 Phòng Quản lý (Management Dept)": {
                "features": {
                    "👤 Hồ sơ nhân sự": "hr_employee",
                    "📍 Chấm công GPS & Thống kê": "field_attendance",
                    "🏭 Quản lý Nhà máy": "factory_mgmt",
                    "🚗 Quản lý xe ra vào": "vehicle_gate",
                    "🛠️ Bảo trì xe": "vehicle_maintenance",
                    "🛒 Mua hàng & Phải trả (AP)": "procurement_ap",
                    "📋 Phải thu": "sales_order_ar",
                    "💰 Quản lý Lương": "payroll_calc",
                    "📄 Quản lý Hóa đơn điện tử": "invoice_management",
                }
            },
            "🛠️ Trung tâm Quản lý Kỹ thuật & Thiết kế": {
                "features": {
                    "⚡ [Kỹ thuật] Báo giá Dự án & Truyền AR": "eng_quote",
                    "📊 [Kỹ thuật] Tiến độ nghiệm thu dự án cơ điện": "eng_progress",
                    "🎨 [Thiết kế] Kho tải lên & Tải về Bản vẽ": "eng_design",
                }
            },
            "🏭 Phòng Sản xuất (Production Dept)": {
                "features": {
                    "📦 [Kho] Quản lý Kho & Mã vạch": "wh_management",
                    "✂️ [Gia công] Tổ Gia công Cơ khí": "sheet_metal",
                    "🎨 [Sơn] Tổ Sơn tĩnh điện": "painting",
                    "⚡ [Lắp ráp] Tổ Lắp ráp Tủ điện": "assembly",
                }
            },
            "💻 Phòng IT (IT & System)": {
                "features": {
                    "🔒 Quản lý Phân quyền": "it_admin",
                    "🎛️ Phân quyền Bản quyền ERP": "it_licensing",
                }
            },
        },
    },
    "English": {
        "company_name": "REETECH INDUSTRIAL CO., LTD",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ REETECH INDUSTRIAL - System Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "🔑 Login",
        "logout_btn": "🚪 Logout",
        "lang_selector": "🌐 Select Language",
        "parent_header": "Select Department:",
        "sub_header": "Select Unit & Features:",
        "departments": {
            "📈 Executive Management": {
                "features": {
                    "🔴 Raw Material Prices & FX": "commodities_fx",
                    "📊 Financial Analytics": "financials_pl",
                    "⚡ Engineering Project Progress": "project_progress_exec",
                }
            },
            "✍️ E-Approval Center": {
                "features": {
                    "✍️ Submit Leave/Purchase & Track Workflow": "approval_center",
                }
            },
            "👔 Management Dept (GA & Finance)": {
                "features": {
                    "👤 HR Records": "hr_employee",
                    "📍 GPS Attendance & Stats": "field_attendance",
                    "🏭 Factory Management": "factory_mgmt",
                    "🚗 Vehicle Gate Log": "vehicle_gate",
                    "🛠️ Vehicle Maintenance": "vehicle_maintenance",
                    "🛒 Procurement & AP": "procurement_ap",
                    "📋 Accounts Receivable": "sales_order_ar",
                    "💰 Payroll Management": "payroll_calc",
                    "📄 E-Invoice Management": "invoice_management",
                }
            },
            "🛠️ Engineering & Design Management Center": {
                "features": {
                    "⚡ [Engineering] Quotation & AR Transfer": "eng_quote",
                    "📊 [Engineering] M&E Acceptance & Progress": "eng_progress",
                    "🎨 [Design] Drawings Storage & Download": "eng_design",
                }
            },
            "🏭 Production Dept": {
                "features": {
                    "📦 [Warehouse] Material Barcodes": "wh_management",
                    "✂️ [Sheet Metal] Processing Dept": "sheet_metal",
                    "🎨 [Coating] Powder Coating Dept": "painting",
                    "⚡ [Assembly] Switchgear Assembly": "assembly",
                }
            },
            "💻 Information Technology (IT)": {
                "features": {
                    "🔒 User Permissions": "it_admin",
                    "🎛️ Client ERP Licensing": "it_licensing",
                }
            },
        },
    },
}

if "current_lang" not in st.session_state:
    st.session_state.current_lang = "繁體中文"

engine = db_conn.get_db_engine()

def safe_call_module(func, *args, **kwargs):
    if not callable(func):
        return
    try:
        sig = inspect.signature(func)
        valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        if "engine" in sig.parameters and "engine" not in valid_kwargs:
            valid_kwargs["engine"] = engine
        func(*args, **valid_kwargs)
    except Exception:
        try:
            func()
        except Exception as e:
            st.error(f"模組載入異常: {str(e)}")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_name = ""

lang_dict = NAV_STRUCTURE.get(
    st.session_state.current_lang, NAV_STRUCTURE["繁體中文"]
)

if not st.session_state.logged_in:
    st.markdown(RECH_LOGO_HTML, unsafe_allow_html=True)
    st.title(lang_dict["login_title"])
    st.caption(lang_dict["company_sub"])
    st.markdown("---")
    col1, _ = st.columns([1, 2])
    with col1:
        username = st.text_input(
            f"{lang_dict['username']} (admin / manager / security / staff)"
        )
        password = st.text_input(
            f"{lang_dict['password']} (123)", type="password"
        )
        if st.button(lang_dict["login_btn"], use_container_width=True):
            if password == "123":
                st.session_state.logged_in = True
                u_clean = username.strip().lower()
                if u_clean in ["admin", "executive", "boss"]:
                    st.session_state.user_role = "admin"
                elif u_clean in ["manager", "supervisor"]:
                    st.
