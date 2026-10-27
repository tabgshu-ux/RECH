import streamlit as st
import pandas as pd
import importlib
from sqlalchemy import text
from modules.user_management import get_department_module_tree

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

# ----------------------------------------------------
# 🌐 結構化選單設計：將「內部路由代碼」與「多語系顯示標籤」分離
# ----------------------------------------------------
NAV_CONFIG = [
    {
        "dept_code": "executive",
        "labels": {
            "繁體中文": "📈 總經理室 (Executive Office)",
            "Tiếng Việt": "📈 Ban Giám đốc (Executive Office)",
            "English": "📈 Executive Office"
        },
        "features": [
            {"code": "commodities_fx", "labels": {"繁體中文": "🔴 原料價格與 Gemini 智慧採購顧問", "Tiếng Việt": "🔴 Giá Nguyên liệu & Cố vấn Gemini", "English": "🔴 Raw Materials & Gemini Advisor"}},
            {"code": "financials_pl", "labels": {"繁體中文": "📊 財務類顯示資料 (AR/AP & P&L)", "Tiếng Việt": "📊 Dữ liệu Tài chính", "English": "📊 Financial Analytics"}},
            {"code": "project_progress_exec", "labels": {"繁體中文": "⚡ 工程專案進度與現場異常監控", "Tiếng Việt": "⚡ Tiến độ Dự án Kỹ thuật", "English": "⚡ Engineering Project Progress"}},
        ]
    },
    {
        "dept_code": "management",
        "labels": {
            "繁體中文": "👔 管理部 (Management Dept)",
            "Tiếng Việt": "👔 Phòng Quản lý (Management Dept)",
            "English": "👔 Management Dept (GA & Finance)"
        },
        "features": [
            {"code": "company_announcements", "labels": {"繁體中文": "📢 公司重要公告與佈告欄", "Tiếng Việt": "📢 Thông báo công ty", "English": "📢 Company Announcements"}},
            {"code": "hr_employee", "labels": {"繁體中文": "👤 員工個人檔案與人事管理", "Tiếng Việt": "👤 Hồ sơ nhân sự", "English": "👤 HR Records"}},
            {"code": "internal_attendance", "labels": {"繁體中文": "🏢 廠內員工固定打卡與出勤紀錄", "Tiếng Việt": "🏢 Chấm công nội bộ", "English": "🏢 Internal Attendance"}},
            {"code": "field_attendance", "labels": {"繁體中文": "📍 外勤出勤統計與工地人數監控", "Tiếng Việt": "📍 Giám sát quân số công trường", "English": "📍 Site Workforce Monitoring"}},
            {"code": "dorm_catering", "labels": {"繁體中文": "🥗 幹部宿舍伙食與採購控管", "Tiếng Việt": "🥗 Quản lý Ký túc xá & Mua thực phẩm", "English": "🥗 Dormitory Catering & Food Procurement"}},
            {"code": "factory_mgmt", "labels": {"繁體中文": "🏭 廠區與工作廠區管理", "Tiếng Việt": "🏭 Quản lý Nhà máy", "English": "🏭 Factory Management"}},
            {"code": "vehicle_gate", "labels": {"繁體中文": "🚗 廠區車輛進出口門禁與派車審核", "Tiếng Việt": "🚗 Quản lý xe ra vào & Phê duyệt", "English": "🚗 Vehicle Gate & Dispatch Log"}},
            {"code": "vehicle_maintenance", "labels": {"繁體中文": "🛠️ 車輛維修保養紀錄", "Tiếng Việt": "🛠️ Bảo trì xe", "English": "🛠️ Vehicle Maintenance"}},
            {"code": "asset_mgmt", "labels": {"繁體中文": "🏢 固定資產與設備管理", "Tiếng Việt": "🏢 Quản lý Tài sản cố định", "English": "🏢 Fixed Asset Management"}},
            {"code": "procurement_ap", "labels": {"繁體中文": "🛒 採購與應付帳款 (AP)", "Tiếng Việt": "🛒 Mua hàng & Phải trả (AP)", "English": "🛒 Procurement & AP"}},
            {"code": "sales_order_ar", "labels": {"繁體中文": "📋 應收帳款與對帳管理中心", "Tiếng Việt": "📋 Quản lý Phải thu", "English": "📋 Accounts Receivable"}},
            {"code": "financial_tax", "labels": {"繁體中文": "📊 越南稅務標準財務報表 (Thông tư 200)", "Tiếng Việt": "📊 Báo cáo Tài chính chuẩn Thuế VN", "English": "📊 Vietnamese Tax Financials"}},
            {"code": "payroll_calc", "labels": {"繁體中文": "💰 員工薪資計算與保險扣除", "Tiếng Việt": "💰 Tính lương & Khấu trừ bảo hiểm", "English": "💰 Payroll & Insurance Calculation"}},
            {"code": "invoice_management", "labels": {"繁體中文": "📄 電子發票綜合管理與 XML 歸檔", "Tiếng Việt": "📄 Quản lý Hóa đơn điện tử", "English": "📄 E-Invoice Management"}},
        ]
    },
    {
        "dept_code": "approval",
        "labels": {
            "繁體中文": "✍️ 全公司電子簽核中心 (Approval Center)",
            "Tiếng Việt": "✍️ Trung tâm Phê duyệt Điện tử (Approval Center)",
            "English": "✍️ E-Approval Center"
        },
        "features": [
            {"code": "approval_center", "labels": {"繁體中文": "✍️ 提交請假/採購與即時進度追蹤 / 審核", "Tiếng Việt": "✍️ Gửi đơn nghỉ phép/mua hàng & Theo dõi tiến độ", "English": "✍️ Submit Leave/Purchase & Track Workflow"}},
        ]
    },
    {
        "dept_code": "engineering",
        "labels": {
            "繁體中文": "🛠️ 工程與設計管理中心 (Engineering & Design Center)",
            "Tiếng Việt": "🛠️ Trung tâm Quản lý Kỹ thuật & Thiết kế",
            "English": "🛠️ Engineering & Design Management Center"
        },
        "features": [
            {"code": "eng_mgmt_center", "labels": {"繁體中文": "⚡ 工程主管戰情室與案場管理", "Tiếng Việt": "⚡ Quản lý Kỹ thuật & Dự án", "English": "⚡ Engineering Executive Center"}},
            {"code": "eng_field_checkin", "labels": {"繁體中文": "📍 [工程] 現場外勤打卡與作業登記", "Tiếng Việt": "📍 Chấm công ngoài công trường", "English": "📍 Field Check-in Log"}},
        ]
    },
    {
        "dept_code": "production",
        "labels": {
            "繁體中文": "🏭 生產部 (Production Dept)",
            "Tiếng Việt": "🏭 Phòng Sản xuất (Production Dept)",
            "English": "🏭 Production Dept"
        },
        "features": [
            {"code": "wh_management", "labels": {"繁體中文": "📦 [倉儲] 倉庫庫存與資材條碼管理", "Tiếng Việt": "📦 [Kho] Quản lý Kho & Mã vạch", "English": "📦 [Warehouse] Material Barcodes"}},
            {"code": "sheet_metal", "labels": {"繁體中文": "✂️ [板金] 板金加工組工單與條碼", "Tiếng Việt": "✂️ [Gia công] Tổ Gia công Cơ khí", "English": "✂️ [Sheet Metal] Processing Dept"}},
            {"code": "painting", "labels": {"繁體中文": "🎨 [塗料] 粉體塗裝烤漆組品管", "Tiếng Việt": "🎨 [Sơn] Tổ Sơn tĩnh điện", "English": "🎨 [Coating] Powder Coating Dept"}},
            {"code": "assembly", "labels": {"繁體中文": "⚡ [配盤] 配電盤組裝配線組", "Tiếng Việt": "⚡ [Lắp ráp] Tổ Lắp ráp Tủ điện", "English": "⚡ [Assembly] Switchgear Assembly"}},
        ]
    },
    {
        "dept_code": "it",
        "labels": {
            "繁體中文": "💻 資訊管理部 (IT & System)",
            "Tiếng Việt": "💻 Phòng IT (IT & System)",
            "English": "💻 Information Technology (IT)"
        },
        "features": [
            {"code": "it_admin", "labels": {"繁體中文": "🔒 系統角色權限與模組開關設定", "Tiếng Việt": "🔒 Cài đặt Phân quyền Hệ thống", "English": "🔒 System Role Permissions"}},
            {"code": "it_licensing", "labels": {"繁體中文": "🔌 API 串接區", "Tiếng Việt": "🔌 Khu vực kết nối API", "English": "🔌 API Integration Hub"}},
        ]
    },
]

UI_STRINGS = {
    "繁體中文": {
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ 裕豐電機工業系統登入",
        "username": "帳號 (工號)",
        "password": "密碼",
        "login_btn": "🔑 登入系統",
        "logout_btn": "🚪 登出系統",
        "lang_selector": "🌐 選擇系統語系 / Select Language",
        "parent_header": "請選擇一級部門 / 系統：",
        "sub_header": "選擇子部門與功能：",
    },
    "Tiếng Việt": {
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ REETECH INDUSTRIAL - Đăng nhập hệ thống",
        "username": "Tài khoản (Mã NV)",
        "password": "Mật khẩu",
        "login_btn": "🔑 Đăng nhập",
        "logout_btn": "🚪 Đăng xuất",
        "lang_selector": "🌐 Chọn ngôn ngữ / Select Language",
        "parent_header": "Chọn phòng ban chính:",
        "sub_header": "Chọn bộ phận trực thuộc:",
    },
    "English": {
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ REETECH INDUSTRIAL - System Login",
        "username": "Username (Emp ID)",
        "password": "Password",
        "login_btn": "🔑 Login",
        "logout_btn": "🚪 Logout",
        "lang_selector": "🌐 Select Language",
        "parent_header": "Select Department:",
        "sub_header": "Select Unit & Features:",
    }
}

if "current_lang" not in st.session_state:
    st.session_state.current_lang = "繁體中文"

if "selected_dept_index" not in st.session_state:
    st.session_state.selected_dept_index = 0
if "selected_feat_index" not in st.session_state:
    st.session_state.selected_feat_index = 0

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

curr_lang = st.session_state.current_lang
ui_t = UI_STRINGS.get(curr_lang, UI_STRINGS["繁體中文"])

# ----------------------------------------------------
# 🔐 1. 登入介面
# ----------------------------------------------------
if not st.session_state.logged_in:
    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(RECH_LOGO_HTML, unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{ui_t['login_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>{ui_t['company_sub']}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        username_input = st.text_input(ui_t["username"])
        password_input = st.text_input(ui_t["password"], type="password")
        
        lang_list = ["繁體中文", "Tiếng Việt", "English"]
        current_lang_idx = lang_list.index(curr_lang) if curr_lang in lang_list else 0
        selected_login_lang = st.selectbox(ui_t["lang_selector"], lang_list, index=current_lang_idx, key="login_lang_select")
        
        if selected_login_lang != curr_lang:
            st.session_state.current_lang = selected_login_lang
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button(ui_t["login_btn"], use_container_width=True):
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

# ----------------------------------------------------
# 🔐 2. 首次登入強制修改密碼
# ----------------------------------------------------
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

# ----------------------------------------------------
# 🚀 3. 已登入側邊欄與功能選單
# ----------------------------------------------------
st.sidebar.markdown(RECH_LOGO_HTML, unsafe_allow_html=True)

lang_list = ["繁體中文", "Tiếng Việt", "English"]
selected_lang = st.sidebar.selectbox(
    ui_t["lang_selector"],
    lang_list,
    index=(lang_list.index(curr_lang) if curr_lang in lang_list else 0),
    key="sidebar_lang_select"
)

if selected_lang != curr_lang:
    st.session_state.current_lang = selected_lang
    st.rerun()

u_name_display = st.session_state.get("user_name", "User")
u_role_display = str(st.session_state.get("user_role", "Staff")).upper()
st.sidebar.markdown(f"**👤 {u_name_display}** ({u_role_display})")

if st.sidebar.button(ui_t["logout_btn"], use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.must_change_pwd = False
    st.rerun()

st.sidebar.markdown("---")

current_role_clean = str(st.session_state.get("user_role", "")).strip().lower()

available_depts = []
for d in NAV_CONFIG:
    if current_role_clean == "security":
        if d["dept_code"] == "management":
            available_depts = [d]
            break
    else:
        is_executive_access = current_role_clean in ["admin", "chairman", "generalmanager", "vicemanager", "executive", "manager", "finance_manager"]
        if not is_executive_access and d["dept_code"] == "executive":
            continue
        if current_role_clean != "admin" and d["dept_code"] == "it":
            continue
        available_depts.append(d)

if current_role_clean == "security":
    selected_dept = available_depts[0]
    st.sidebar.markdown(f"**{ui_t['parent_header']}**")
    st.sidebar.markdown(f"👔 {selected_dept['labels'][curr_lang]}")
    target_route = "vehicle_gate"
else:
    dept_labels = [d["labels"][curr_lang] for d in available_depts]
    
    if st.session_state.selected_dept_index >= len(available_depts):
        st.session_state.selected_dept_index = 0

    selected_dept_label = st.sidebar.radio(
        ui_t["parent_header"],
        dept_labels,
        index=st.session_state.selected_dept_index,
        key="dept_radio_idx"
    )
    
    selected_dept_index = dept_labels.index(selected_dept_label)
    if selected_dept_index != st.session_state.selected_dept_index:
        st.session_state.selected_dept_index = selected_dept_index
        st.session_state.selected_feat_index = 0
        st.rerun()

    selected_dept = available_depts[selected_dept_index]

    st.sidebar.markdown("---")
    features = selected_dept["features"]
    feat_labels = [f["labels"][curr_lang] for f in features]

    if st.session_state.selected_feat_index >= len(features):
        st.session_state.selected_feat_index = 0

    st.sidebar.caption(f"**{selected_dept_label.split('(')[0].strip()}**")
    
    selected_feat_label = st.sidebar.radio(
        ui_t["sub_header"],
        feat_labels,
        index=st.session_state.selected_feat_index,
        key="feat_radio_idx"
    )
    
    selected_feat_index = feat_labels.index(selected_feat_label)
    if selected_feat_index != st.session_state.selected_feat_index:
        st.session_state.selected_feat_index = selected_feat_index
        st.rerun()

    target_route = features[selected_feat_index]["code"]

# ----------------------------------------------------
# 📢 公司公告跑馬燈
# ----------------------------------------------------
if "announcements_db" not in st.session_state:
    st.session_state.announcements_db = [
        {
            "ann_id": "ANN-2026-001",
            "title": "⚡ 關於越南全國連假與西寧廠安全生產之重要通知",
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
# 🔀 動態安全路由分流
# ----------------------------------------------------
if target_route == "company_announcements":
    load_module_safely("modules.company_announcements", "render_company_announcements_page", engine=engine, lang=curr_lang)

elif target_route in ["commodities_fx", "financials_pl", "project_progress_exec"]:
    load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route=target_route, lang=curr_lang)

elif target_route == "approval_center":
    load_module_safely("modules.approval_workflow", "render_approval_center", lang=curr_lang)

elif target_route == "dorm_catering":
    load_module_safely("modules.dorm_catering", "render_dorm_catering_module", engine=engine, lang=curr_lang)

elif target_route in [
    "eng_mgmt_center", "eng_quote", "eng_progress", "field_daily_report", 
    "eng_ai_photo", "eng_license", "eng_design", "eng_bom", "eng_labor", "eng_fat"
]:
    load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang)

elif target_route == "eng_field_checkin":
    load_module_safely("modules.field_attendance", "render_field_attendance_page", engine=engine, lang=curr_lang, view_mode="field_worker")

elif target_route == "field_attendance":
    load_module_safely("modules.field_attendance", "render_field_attendance_page", engine=engine, lang=curr_lang, view_mode="management")

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

elif target_route == "factory_mgmt":
    load_module_safely("modules.factory_management", "render_factory_management_page", engine=engine, lang=curr_lang)

elif target_route == "hr_employee":
    load_module_safely("modules.employee_management", "render_employee_management", engine=engine, t=ui_t, lang=curr_lang)

elif target_route == "vehicle_gate":
    load_module_safely("modules.vehicle_gate_log", "render_vehicle_gate_log_page", engine=engine, lang=curr_lang)

elif target_route == "vehicle_maintenance":
    load_module_safely("modules.vehicle_maintenance", "render_vehicle_maintenance_page", engine=engine, lang=curr_lang)

elif target_route == "wh_management":
    load_module_safely("modules.warehouse_management", "render_warehouse_management", engine=engine, t=ui_t, lang=curr_lang)

elif target_route == "sheet_metal":
    load_module_safely("modules.sheet_metal", "render_sheet_metal_module", engine=engine, t=ui_t, lang=curr_lang)

elif target_route == "painting":
    load_module_safely("modules.painting", "render_painting_module", engine=engine, t=ui_t, lang=curr_lang)

elif target_route == "assembly":
    load_module_safely("modules.assembly", "render_assembly_module", engine=engine, t=ui_t, lang=curr_lang)

elif target_route == "it_admin":
    if current_role_clean == "admin":
        load_module_safely("modules.user_management", "render_user_management_page", engine=engine, lang=curr_lang)
    else:
        st.error("⚠️ 權限不足：資訊管理部僅限系統管理員 (admin) 登入存取。")

elif target_route == "it_licensing":
    if current_role_clean == "admin":
        load_module_safely("modules.system_licensing", "render_licensing_control_page", engine=engine, lang=curr_lang)
    else:
        st.error("⚠️ 權限不足：僅限系統管理員 (admin) 存取。")
