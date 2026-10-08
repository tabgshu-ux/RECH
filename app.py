import streamlit as st
import pandas as pd
import importlib
from sqlalchemy import text

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
        "username": "帳號 (工號)",
        "password": "密碼",
        "login_btn": "🔑 登入系統",
        "logout_btn": "🚪 登出系統",
        "lang_selector": "🌐 語言設定 / Language",
        "parent_header": "請選擇一級部門 / 系統：",
        "sub_header": "選擇子部門與功能：",
        "departments": {
            "📈 總經理室 (Executive Office)": {
                "features": {
                    "🔴 原料價格與 Gemini 智慧採購顧問": "commodities_fx",
                    "📊 財務類顯示資料 (AR/AP & P&L)": "financials_pl",
                    "⚡ 工程專案進度與現場異常監控": "project_progress_exec",
                }
            },
            "👔 管理部 (Management Dept)": {
                "features": {
                    "👤 員工個人檔案與人事管理": "hr_employee",
                    "🏢 廠內員工固定打卡與出勤紀錄": "internal_attendance",
                    "📍 外勤 GPS 打卡與工地即時人數": "field_attendance",
                    "🏭 廠區與工作廠區管理": "factory_mgmt",
                    "🚗 廠區車輛進出口門禁與派車審核": "vehicle_gate",
                    "🛠️ 車輛維修保養紀錄": "vehicle_maintenance",
                    "🏢 固定資產與設備管理": "asset_mgmt",
                    "🛒 採購與應付帳款 (AP)": "procurement_ap",
                    "📋 應收帳款": "sales_order_ar",
                    "📊 越南稅務標準財務報表 (Thông tư 200)": "financial_tax",
                    "💰 員工薪資計算與保險扣除": "payroll_calc",
                    "📄 電子發票綜合管理": "invoice_management",
                }
            },
            "✍️ 全公司電子簽核中心 (Approval Center)": {
                "features": {
                    "✍️ 提交請假/採購與即時進度追蹤 / 審核": "approval_center",
                }
            },
            "🛠️ 工程與設計管理中心 (Engineering & Design Center)": {
                "features": {
                    "⚡ [工程] 配電盤與工程專案報價": "eng_quote",
                    "📊 [工程] 工程驗收與進度追蹤": "eng_progress",
                    "📋 [工程] 現場工程日報表與出工統計": "field_daily_report",
                    "🎨 [設計] 配電盤電氣與機構設計圖庫 Storage": "eng_design",
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
        "username": "Tài khoản (Mã NV)",
        "password": "Mật khẩu",
        "login_btn": "🔑 Đăng nhập",
        "logout_btn": "🚪 Đăng xuất",
        "lang_selector": "🌐 Chọn ngôn ngữ",
        "parent_header": "Chọn phòng ban chính:",
        "sub_header": "Chọn bộ phận trực thuộc:",
        "departments": {
            "📈 Ban Giám đốc (Executive Office)": {
                "features": {
                    "🔴 Giá Nguyên liệu & Cố vấn Gemini": "commodities_fx",
                    "📊 Dữ liệu Tài chính": "financials_pl",
                    "⚡ Tiến độ Dự án Kỹ thuật": "project_progress_exec",
                }
            },
            "👔 Phòng Quản lý (Management Dept)": {
                "features": {
                    "👤 Hồ sơ nhân sự": "hr_employee",
                    "🏢 Chấm công nội bộ": "internal_attendance",
                    "📍 Chấm công GPS công trường": "field_attendance",
                    "🏭 Quản lý Nhà máy": "factory_mgmt",
                    "🚗 Quản lý xe ra vào & Phê duyệt": "vehicle_gate",
                    "🛠️ Bảo trì xe": "vehicle_maintenance",
                    "🏢 Quản lý Tài sản cố định": "asset_mgmt",
                    "🛒 Mua hàng & Phải trả (AP)": "procurement_ap",
                    "📋 Phải thu": "sales_order_ar",
                    "📊 Báo cáo Tài chính chuẩn Thuế VN": "financial_tax",
                    "💰 Tính lương & Khấu trừ bảo hiểm": "payroll_calc",
                    "📄 Quản lý Hóa đơn điện tử": "invoice_management",
                }
            },
            "✍️ Trung tâm Phê duyệt Điện tử (Approval Center)": {
                "features": {
                    "✍️ Gửi đơn nghỉ phép/mua hàng & Theo dõi tiến độ": "approval_center",
                }
            },
            "🛠️ Trung tâm Quản lý Kỹ thuật & Thiết kế": {
                "features": {
                    "⚡ [Kỹ thuật] Báo giá Dự án & Truyền AR": "eng_quote",
                    "📊 [Kỹ thuật] Tiến độ nghiệm thu dự án cơ điện": "eng_progress",
                    "📋 [Kỹ thuật] Nhật ký Thi công Công trình": "field_daily_report",
                    "🎨 [Thiết kế] Kho Storage Bản vẽ": "eng_design",
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
        "username": "Username (Emp ID)",
        "password": "Password",
        "login_btn": "🔑 Login",
        "logout_btn": "🚪 Logout",
        "lang_selector": "🌐 Select Language",
        "parent_header": "Select Department:",
        "sub_header": "Select Unit & Features:",
        "departments": {
            "📈 Executive Office": {
                "features": {
                    "🔴 Raw Materials & Gemini Advisor": "commodities_fx",
                    "📊 Financial Analytics": "financials_pl",
                    "⚡ Engineering Project Progress": "project_progress_exec",
                }
            },
            "👔 Management Dept (GA & Finance)": {
                "features": {
                    "👤 HR Records": "hr_employee",
                    "🏢 Internal Attendance": "internal_attendance",
                    "📍 Field GPS Attendance": "field_attendance",
                    "🏭 Factory Management": "factory_mgmt",
                    "🚗 Vehicle Gate & Dispatch Log": "vehicle_gate",
                    "🛠️ Vehicle Maintenance": "vehicle_maintenance",
                    "🏢 Fixed Asset Management": "asset_mgmt",
                    "🛒 Procurement & AP": "procurement_ap",
                    "📋 Accounts Receivable": "sales_order_ar",
                    "📊 Vietnamese Tax Financials": "financial_tax",
                    "💰 Payroll & Insurance Calculation": "payroll_calc",
                    "📄 E-Invoice Management": "invoice_management",
                }
            },
            "✍️ E-Approval Center": {
                "features": {
                    "✍️ Submit Leave/Purchase & Track Workflow": "approval_center",
                }
            },
            "🛠️ Engineering & Design Management Center": {
                "features": {
                    "⚡ [Engineering] Quotation & AR Transfer": "eng_quote",
                    "📊 [Engineering] M&E Acceptance & Progress": "eng_progress",
                    "📋 [Engineering] Daily Construction Report": "field_daily_report",
                    "🎨 [Design] Drawing Storage Center": "eng_design",
                }
            },
            "🏭 Production Dept": {
                "features": {
                    "📦
