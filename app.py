import streamlit as st
import pandas as pd
import importlib
from modules import painting
from modules import sheet_metal
from modules import assembly
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
<div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 15px; padding: 6px 8px; background: transparent;">
    <div style="font-size: 32px; font-weight: 900; color: #000055; letter-spacing: -1px; line-height: 1;">RECH</div>
    <div style="border-left: 2px solid #000055; padding-left: 8px; line-height: 1.15; text-align: left;">
        <div style="font-size: 14px; font-weight: 800; color: #000055;">裕豐電機工業有限公司</div>
        <div style="font-size: 9px; font-weight: 700; color: #1E293B;">REETECH INDUSTRIAL CO., LTD</div>
        <div style="font-size: 8.5px; font-weight: 700; color: #334155;">CÔNG TY TNHH CN DŨ PHONG</div>
    </div>
</div>
"""

NAV_STRUCTURE = {
    "繁體中文": {
        "company_name": "裕豐電機工業有限公司",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ 裕豐電機工業系統登入",
        "username": "帳號 (工號)",
        "password": "密碼",
        "login_btn": "🔑 登入系統",
        "logout_btn": "🚪 登出系統",
        "lang_selector": "🌐 選擇系統語系 / Select Language",
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
                    "📢 公司重要公告與佈告欄": "company_announcements",
                    "👤 員工個人檔案與人事管理": "hr_employee",
                    "🏢 廠內員工固定打卡與出勤紀錄": "internal_attendance",
                    "📍 外勤位置驗證與工地即時人數": "field_attendance",
                    "🏭 廠區與工作廠區管理": "factory_mgmt",
                    "🚗 廠區車輛進出口門禁與派車審核": "vehicle_gate",
                    "🛠️ 車輛維修保養紀錄": "vehicle_maintenance",
                    "🏢 固定資產與設備管理": "asset_mgmt",
                    "🛒 採購與應付帳款 (AP)": "procurement_ap",
                    "📋 應收帳款與對帳管理中心": "sales_order_ar",
                    "📊 越南稅務標準財務報表 (Thông tư 200)": "financial_tax",
                    "💰 員工薪資計算與保險扣除": "payroll_calc",
                    "📄 電子發票綜合管理與 XML 歸檔": "invoice_management",
                    "📊 越南營建電子發票與稅務合規管家": "vn_tax_invoice",
                }
            },
            "✍️ 全公司電子簽核中心 (Approval Center)": {
                "features": {
                    "✍️ 提交請假/採購與即時進度追蹤 / 審核": "approval_center",
                }
            },
            "🛠️ 工程與設計管理中心 (Engineering & Design Center)": {
                "features": {
                    "⚡ [工程] 配電盤與工程專案雙層報價": "eng_quote",
                    "📊 [工程] 工程驗收與進度追蹤": "eng_progress",
                    "📋 [工程] 現場工程日報表與出工統計": "field_daily_report",
                    "🤖 [工程] AI 施工照片智慧辨識與歸檔": "eng_ai_photo",
                    "⚠️ [工程] 分包商與專業證照到期預警": "eng_license",
                    "🎨 [設計] 配電盤電氣與機構設計圖庫 Storage": "eng_design",
                    "🔌 [工程] 配電盤 BOM 零件自動展開與採購連動": "eng_bom",
                    "👷 [工程] 外包商點工計價與越南勞動法計薪": "eng_labor",
                    "🧪 [工程] FAT/SAT 試驗報告與 QR Code 驗收": "eng_fat",
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
        "lang_selector": "🌐 Chọn ngôn ngữ / Select Language",
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
                    "📢 Thông báo công ty": "company_announcements",
                    "👤 Hồ sơ nhân sự": "hr_employee",
                    "🏢 Chấm công nội bộ": "internal_attendance",
                    "📍 Chấm công vị trí công trường": "field_attendance",
                    "🏭 Quản lý Nhà máy": "factory_mgmt",
                    "🚗 Quản lý xe ra vào & Phê duyệt": "vehicle_gate",
                    "🛠️ Bảo trì xe": "vehicle_maintenance",
                    "🏢 Quản lý Tài sản cố định": "asset_mgmt",
                    "🛒 Mua hàng & Phải trả (AP)": "procurement_ap",
                    "📋 Quản lý Phải thu": "sales_order_ar",
                    "📊 Báo cáo Tài chính chuẩn Thuế VN": "financial_tax",
                    "💰 Tính lương & Khấu trừ bảo hiểm": "payroll_calc",
                    "📄 Quản lý Hóa đơn điện tử": "invoice_management",
                    "📊 Quản lý Hóa đơn điện tử & Tuân thủ Thuế": "vn_tax_invoice",
                }
            },
            "✍️ Trung tâm Phê duyệt Điện tử (Approval Center)": {
                "features": {
                    "✍️ Gửi đơn nghỉ phép/mua hàng & Theo dõi tiến độ": "approval_center",
                }
            },
            "🛠️ Trung tâm Quản lý Kỹ thuật & Thiết kế": {
                "features": {
                    "⚡ [Kỹ thuật] Báo giá Dự án": "eng_quote",
                    "📊 [Kỹ thuật] Tiến độ nghiệm thu": "eng_progress",
                    "📋 [Kỹ thuật] Nhật ký Thi công": "field_daily_report",
                    "🤖 [Kỹ thuật] AI Nhận diện ảnh": "eng_ai_photo",
                    "⚠️ [Kỹ thuật] Cảnh báo chứng chỉ": "eng_license",
                    "🎨 [Thiết kế] Kho Storage Bản vẽ": "eng_design",
                    "🔌 [Kỹ thuật] Bóc tách BOM & Mua hàng": "eng_bom",
                    "👷 [Kỹ thuật] Chấm công thầu phụ": "eng_labor",
                    "🧪 [Kỹ thuật] Thử nghiệm FAT/SAT": "eng_fat",
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
                    "📢 Company Announcements": "company_announcements",
                    "👤 HR Records": "hr_employee",
                    "🏢 Internal Attendance": "internal_attendance",
                    "📍 Field Attendance": "field_attendance",
                    "🏭 Factory Management": "factory_mgmt",
                    "🚗 Vehicle Gate & Dispatch Log": "vehicle_gate",
                    "🛠️ Vehicle Maintenance": "vehicle_maintenance",
                    "🏢 Fixed Asset Management": "asset_mgmt",
                    "🛒 Procurement & AP": "procurement_ap",
                    "📋 Accounts Receivable": "sales_order_ar",
                    "📊 Vietnamese Tax Financials": "financial_tax",
                    "💰 Payroll & Insurance Calculation": "payroll_calc",
                    "📄 E-Invoice Management": "invoice_management",
                    "📊 Vietnam E-Invoice & Tax Manager": "vn_tax_invoice",
                }
            },
            "✍️ E-Approval Center": {
                "features": {
                    "✍️ Submit Leave/Purchase & Track Workflow": "approval_center",
                }
            },
            "🛠️ Engineering & Design Management Center": {
                "features": {
                    "⚡ [Engineering] Quotation": "eng_quote",
                    "📊 [Engineering] M&E Acceptance": "eng_progress",
                    "📋 [Engineering] Daily Construction Report": "field_daily_report",
                    "🤖 [Engineering] AI Photo Recognition": "eng_ai_photo",
                    "⚠️ [Engineering] License Alerts": "eng_license",
                    "🎨 [Design] Drawing Storage Center": "eng_design",
                    "🔌 [Engineering] BOM & Procurement": "eng_bom",
                    "👷 [Engineering] Subcontractor Labor": "eng_labor",
                    "🧪 [Engineering] FAT/SAT Testing": "eng_fat",
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

try:
    db_conn = importlib.import_module("modules.db_connection")
    engine = db_conn.get_db_engine()
except Exception:
    engine = None

def load_module_safely(mod_name, func_name, *args, **kwargs):
    try:
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name, None)
        if callable(func):
            func(*args, **kwargs)
        else:
            st.error(f"模組 {mod_name} 中找不到方法 {func_name}")
    except Exception as e:
        st.error(f"載入模組 {mod_name} 發生異常: {str(e)}")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_name = ""
    st.session_state.must_change_pwd = False

lang_dict = NAV_STRUCTURE.get(
    st.session_state.current_lang, NAV_STRUCTURE["繁體中文"]
)

if not st.session_state.logged_in:
    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(RECH_LOGO_HTML, unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{lang_dict['login_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>{lang_dict['company_sub']}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        username_input = st.text_input(lang_dict["username"])
        password_input = st.text_input(lang_dict["password"], type="password")
        
        lang_list = ["繁體中文", "Tiếng Việt", "English"]
        current_lang_idx = lang_list.index(st.session_state.current_lang) if st.session_state.current_lang in lang_list else 0
        selected_login_lang = st.selectbox(lang_dict["lang_selector"], lang_list, index=current_lang_idx)
        
        if selected_login_lang != st.session_state.current_lang:
            st.session_state.current_lang = selected_login_lang
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button(lang_dict["login_btn"], use_container_width=True):
            u_clean = username_input.strip()
            
            if u_clean.lower() == "admin" and password_input == "123":
                st.session_state.logged_in = True
                st.session_state.user_role = "admin"
                st.session_state.user_name = "admin"
                st.session_state.must_change_pwd = False
                st.rerun()
            else:
                matched_emp = None
                if "employee_db" in st.session_state:
                    matched_emp = next((e for e in st.session_state.employee_db if e["工號"].lower() == u_clean.lower()), None)
                
                stored_pwd = matched_emp.get("密碼", "123456") if matched_emp else "123456"
                
                if matched_emp and password_input == stored_pwd:
                    st.session_state.logged_in = True
                    st.session_state.user_name = matched_emp["姓名"]
                    st.session_state.user_role = matched_emp.get("角色", "Staff")
                    st.session_state.must_change_pwd = matched_emp.get("must_change_password", False)
                    st.session_state.current_emp_code = matched_emp["工號"]
                    st.rerun()
                else:
                    st.error("⚠️ 帳號或初始密碼錯誤 / Incorrect username or password")
    st.stop()

if st.session_state.get("must_change_pwd", False):
    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(RECH_LOGO_HTML, unsafe_allow_html=True)
        st.warning("⚠️ **首次登入安全設定 / Lần đầu đăng nhập - Đổi mật khẩu**：為符合企業資安規範，請您立即變更由人事分派的初始密碼。")
        
        with st.form("force_change_pwd_form"):
            new_pwd = st.text_input("請輸入您的新密碼 (Mật khẩu mới) *", type="password")
            confirm_pwd = st.text_input("再次確認新密碼 (Nhập lại mật khẩu mới) *", type="password")
            
            if st.form_submit_button("💾 確認修改密碼並進入系統", type="primary", use_container_width=True):
                if new_pwd and new_pwd == confirm_pwd:
                    if "employee_db" in st.session_state:
                        for emp_item in st.session_state.employee_db:
                            if emp_item["工號"] == st.session_state.get("current_emp_code"):
                                emp_item["密碼"] = new_pwd
                                emp_item["must_change_password"] = False
                    st.session_state.must_change_pwd = False
                    st.success("🎉 密碼修改成功！正在進入系統...")
                    st.rerun()
                else:
                    st.error("⚠️ 兩次輸入的新密碼不相符或未填寫，請重新檢查！")
    st.stop()

st.sidebar.markdown(RECH_LOGO_HTML, unsafe_allow_html=True)

lang_list = ["繁體中文", "Tiếng Việt", "English"]
selected_lang = st.sidebar.selectbox(
    lang_dict["lang_selector"],
    lang_list,
    index=(lang_list.index(st.session_state.current_lang) if st.session_state.current_lang in lang_list else 0),
)

if selected_lang != st.session_state.current_lang:
    st.session_state.current_lang = selected_lang
    st.rerun()

u_name_display = st.session_state.get("user_name", "User")
u_role_display = str(st.session_state.get("user_role", "Staff")).upper()
st.sidebar.markdown(f"**👤 {u_name_display}** ({u_role_display})")

if st.sidebar.button(lang_dict["logout_btn"], use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.must_change_pwd = False
    st.rerun()

st.sidebar.markdown("---")

dept_options = list(lang_dict["departments"].keys())
current_role_clean = str(st.session_state.get("user_role", "")).strip().lower()

if current_role_clean == "security":
    dept_options = ["👔 管理部 (Management Dept)"]
    selected_parent_dept = dept_options[0]
    st.sidebar.markdown(f"**{lang_dict['parent_header']}**")
    feature_labels = ["🚗 廠區車輛進出口門禁與派車審核"] if st.session_state.current_lang == "繁體中文" else ["🚗 Quản lý xe ra vào & Phê duyệt"]
    selected_feature_label = feature_labels[0]
    target_route = "vehicle_gate"
else:
    is_executive_access = (
        current_role_clean in ["admin", "chairman", "generalmanager", "vicemanager", "executive", "manager", "finance_manager"]
    )

    if not is_executive_access:
        dept_options = [d for d in dept_options if "總經理室" not in d and "Executive" not in d and "Ban Giám đốc" not in d]

    if current_role_clean != "admin":
        dept_options = [d for d in dept_options if "資訊管理部" not in d and "IT" not in d and "Phòng IT" not in d]

    selected_parent_dept = st.sidebar.radio(lang_dict["parent_header"], dept_options, index=0)

    st.sidebar.markdown("---")
    features_dict = lang_dict["departments"][selected_parent_dept]["features"]
    feature_labels = list(features_dict.keys())

    st.sidebar.caption(f"**{selected_parent_dept.split('(')[0].strip()}**")
    selected_feature_label = st.sidebar.radio(lang_dict["sub_header"], feature_labels)
    target_route = features_dict[selected_feature_label]

curr_lang = st.session_state.current_lang

# ----------------------------------------------------
# 📢 登入即見：全公司重要公告彈窗提醒 (公告跑馬燈)
# ----------------------------------------------------
if "announcements_db" not in st.session_state:
    st.session_state.announcements_db = [
        {
            "ann_id": "ANN-2026-001",
            "title": "⚡ 關於越南全國連假與西寧/海防廠安全生產之重要通知",
            "category": "🔴 緊急公告 (Urgent)",
            "content": "請各部門主管務必於連假前落實廠區斷電巡檢、消防設備盤點，並確保留守人員通訊暢通。",
            "publisher": "總經理室 / 董事長辦公室",
            "date": "2026-10-09",
            "status": "🟢 發布中 (Active)"
        }
    ]

active_anns = [a for a in st.session_state.announcements_db if "發布中" in a["status"]]
if active_anns:
    latest_ann = active_anns[0]
    st.info(f"📢 **【公司佈告欄】{latest_ann['title']}**（發布單位：{latest_ann['publisher']} | 日期：{latest_ann['date']}）\n\n> {latest_ann['content']}")

# ----------------------------------------------------
# 動態安全路由分流
# ----------------------------------------------------
if target_route == "company_announcements":
    load_module_safely("modules.company_announcements", "render_company_announcements_page", engine=engine, lang=curr_lang)

elif target_route in ["commodities_fx", "financials_pl", "project_progress_exec"]:
    load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route=target_route, lang=curr_lang)

elif target_route == "approval_center":
    load_module_safely("modules.approval_workflow", "render_approval_center", lang=curr_lang)

elif target_route == "eng_quote":
    load_module_safely("modules.engineering_department", "render_engineering_department_page", engine=engine, lang=curr_lang, sub_action="1")

elif target_route == "eng_progress":
    load_module_safely("modules.engineering_department", "render_engineering_department_page", engine=engine, lang=curr_lang, sub_action="2")

elif target_route == "field_daily_report":
    load_module_safely("modules.engineering_department", "render_engineering_department_page", engine=engine, lang=curr_lang, sub_action="3")

elif target_route == "eng_ai_photo":
    load_module_safely("modules.engineering_department", "render_engineering_department_page", engine=engine, lang=curr_lang, sub_action="4")

elif target_route == "eng_license":
    load_module_safely("modules.engineering_department", "render_engineering_department_page", engine=engine, lang=curr_lang, sub_action="5")

elif target_route == "eng_design":
    load_module_safely("modules.engineering_department", "render_engineering_department_page", engine=engine, lang=curr_lang, sub_action="6")

elif target_route == "eng_bom":
    load_module_safely("modules.engineering_department", "render_engineering_department_page", engine=engine, lang=curr_lang, sub_action="7")

elif target_route == "eng_labor":
    load_module_safely("modules.engineering_department", "render_engineering_department_page", engine=engine, lang=curr_lang, sub_action="8")

elif target_route == "eng_fat":
    load_module_safely("modules.engineering_department", "render_engineering_department_page", engine=engine, lang=curr_lang, sub_action="9")

elif target_route == "vn_tax_invoice":
    load_module_safely("modules.vietnam_tax_api_config", "render_vn_tax_invoice_page", engine=engine, lang=curr_lang)

elif target_route == "procurement_ap":
    load_module_safely("modules.procurement_ap", "render_procurement_ap_page", engine=engine, lang=curr_lang)

elif target_route == "sales_order_ar":
    load_module_safely("modules.sales_order_ar", "render_sales_order_ar_page", engine=engine, lang=curr_lang)

elif target_route == "financial_tax":
    load_module_safely("modules.financial_tax_reports", "render_financial_tax_reports_page", engine=engine, lang=curr_lang)

elif target_route == "asset_mgmt":
    load_module_safely("modules.asset_management", "render_asset_management_page", engine=engine, lang=curr_lang)

elif target_route == "payroll_calc":
    load_module_safely("modules.payroll_management", "render_payroll_management_page", engine=engine, lang=curr_lang)

elif target_route == "invoice_management":
    load_module_safely("modules.invoice_management", "render_invoice_management_page", engine=engine, lang=curr_lang)

elif target_route == "internal_attendance":
    load_module_safely("modules.internal_attendance", "render_internal_attendance_page", engine=engine, lang=curr_lang)

elif target_route == "field_attendance":
    load_module_safely("modules.field_attendance", "render_field_attendance_page", engine=engine, lang=curr_lang)

elif target_route == "factory_mgmt":
    load_module_safely("modules.factory_management", "render_factory_management_page", engine=engine, lang=curr_lang)

elif target_route == "hr_employee":
    load_module_safely("modules.employee_management", "render_employee_management", engine=engine, t=lang_dict, lang=curr_lang)

elif target_route == "vehicle_gate":
    load_module_safely("modules.vehicle_gate_log", "render_vehicle_gate_log_page", engine=engine, lang=curr_lang)

elif target_route == "vehicle_maintenance":
    load_module_safely("modules.vehicle_maintenance", "render_vehicle_maintenance_page", engine=engine, lang=curr_lang)

elif target_route == "wh_management":
    load_module_safely("modules.warehouse_management", "render_warehouse_management", engine=engine, t=lang_dict, lang=curr_lang)

elif target_route == "sheet_metal":
    sheet_metal.render_sheet_metal_module(engine=engine, t=lang_dict, lang=curr_lang)

elif target_route == "painting":
    painting.render_painting_module(engine=engine, t=lang_dict, lang=curr_lang)

elif target_route == "assembly":
    assembly.render_assembly_module(engine=engine, t=lang_dict, lang=curr_lang)
    
elif target_route == "it_admin":
    if current_role_clean == "admin":
        load_module_safely("modules.user_management", "render_user_management_page", lang=curr_lang)
    else:
        st.error("⚠️ 權限不足：本系統無資訊管理部，僅限系統管理員 (admin) 登入檢視。")

elif target_route == "it_licensing":
    if current_role_clean == "admin":
        load_module_safely("modules.system_licensing", "render_licensing_control_page", lang=curr_lang)
    else:
        st.error("⚠️ 權限不足：僅限系統管理員 (admin) 存取。")
