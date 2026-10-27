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

UI_STRINGS = {
    "繁體中文": {
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ 裕豐電機工業系統登入",
        "username": "帳號 (工號)",
        "password": "密碼",
        "login_btn": "🔑 登入系統",
        "logout_btn": "🚪 登出系統",
        "lang_selector": "🌐 選擇系統語系 / Select Language",
        "parent_header": "請選擇一級部門 / Chọn phòng ban :",
        "sub_header": "選擇子部門與功能 / Chọn chức năng :",
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
# 🚀 3. 已登入側邊欄與動態功能選單
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

# 從動態樹狀結構取得部門與子功能
dept_module_tree = get_department_module_tree()
department_names = list(dept_module_tree.keys())

# 權限過濾：非 admin 隱藏資訊管理部 (IT)
available_dept_names = []
for d_name in department_names:
    if current_role_clean != "admin" and "資訊管理部" in d_name:
        continue
    if current_role_clean == "security" and "管理部" not in d_name:
        continue
    available_dept_names.append(d_name)

if not available_dept_names:
    available_dept_names = department_names

if current_role_clean == "security":
    selected_dept_label = next((d for d in available_dept_names if "管理部" in d), available_dept_names[0])
    st.sidebar.markdown(f"**{ui_t['parent_header']}**")
    st.sidebar.markdown(f"👔 {selected_dept_label}")
    sub_features = ["🚗 廠區車輛進出口門禁與派車審核"]
    selected_feat_label = sub_features[0]
else:
    if st.session_state.selected_dept_index >= len(available_dept_names):
        st.session_state.selected_dept_index = 0

    selected_dept_label = st.sidebar.radio(
        ui_t["parent_header"],
        available_dept_names,
        index=st.session_state.selected_dept_index,
        key="dept_radio_idx"
    )
    
    selected_dept_index = available_dept_names.index(selected_dept_label)
    if selected_dept_index != st.session_state.selected_dept_index:
        st.session_state.selected_dept_index = selected_dept_index
        st.session_state.selected_feat_index = 0
        st.rerun()

    sub_features = dept_module_tree.get(selected_dept_label, [])
    if not sub_features:
        sub_features = ["(此部門尚無功能模組)"]

    if st.session_state.selected_feat_index >= len(sub_features):
        st.session_state.selected_feat_index = 0

    st.sidebar.caption(f"**{selected_dept_label.split('(')[0].strip()}**")
    
    selected_feat_label = st.sidebar.radio(
        ui_t["sub_header"],
        sub_features,
        index=st.session_state.selected_feat_index,
        key="feat_radio_idx"
    )
    
    selected_feat_index = sub_features.index(selected_feat_label)
    if selected_feat_index != st.session_state.selected_feat_index:
        st.session_state.selected_feat_index = selected_feat_index
        st.rerun()

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
# 🔀 智慧關鍵字動態安全路由分流（完整對應所有子功能名稱）
# ----------------------------------------------------
feat_str = str(selected_feat_label)

if "公告" in feat_str or "佈告欄" in feat_str:
    load_module_safely("modules.company_announcements", "render_company_announcements_page", engine=engine, lang=curr_lang)

elif "原料價格" in feat_str or "Gemini" in feat_str:
    load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route="commodities_fx", lang=curr_lang)

elif "財務類" in feat_str or "AR/AP & P&L" in feat_str:
    load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route="financials_pl", lang=curr_lang)

elif "工程專案進度" in feat_str or "異常監控" in feat_str:
    load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route="project_progress_exec", lang=curr_lang)

elif "請假" in feat_str or "電子簽核" in feat_str:
    load_module_safely("modules.approval_workflow", "render_approval_center", lang=curr_lang)

elif "宿舍" in feat_str or "伙食" in feat_str:
    load_module_safely("modules.dorm_catering", "render_dorm_catering_module", engine=engine, lang=curr_lang)

elif "工程主管戰情室" in feat_str or "工程專案報價" in feat_str:
    load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang)

elif "工程" in feat_str or "施工日報表" in feat_str or "配電盤電氣" in feat_str or "BOM" in feat_str or "FAT/SAT" in feat_str:
    load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang)

elif "外勤出勤" in feat_str or "工地人數" in feat_str or "現場外勤打卡" in feat_str:
    load_module_safely("modules.field_attendance", "render_field_attendance_page", engine=engine, lang=curr_lang, view_mode="management" if "統計" in feat_str else "field_worker")

elif "採購與應付帳款" in feat_str or "AP" in feat_str:
    load_module_safely("modules.procurement_ap", "render_procurement_ap_page", engine=engine, lang=curr_lang)

elif "應收帳款" in feat_str or "對帳" in feat_str:
    load_module_safely("modules.sales_order_ar", "render_sales_order_ar_page", engine=engine, lang=curr_lang)

elif "越南稅務" in feat_str or "Thông tư 200" in feat_str:
    load_module_safely("modules.financial_tax_reports", "render_financial_tax_reports_page", engine=engine, lang=curr_lang)

elif "固定資產" in feat_str or "設備管理" in feat_str:
    load_module_safely("modules.asset_management", "render_asset_management_page", engine=engine, lang=curr_lang)

elif "薪資" in feat_str or "保險扣除" in feat_str:
    load_module_safely("modules.payroll_management", "render_payroll_management_page", engine=engine, lang=curr_lang)

elif "電子發票" in feat_str or "XML" in feat_str:
    load_module_safely("modules.invoice_management", "render_invoice_management_page", engine=engine, lang=curr_lang)

elif "打卡" in feat_str or "出勤紀錄" in feat_str:
    load_module_safely("modules.internal_attendance", "render_internal_attendance_page", engine=engine, lang=curr_lang)

elif "廠區" in feat_str or "工作廠區" in feat_str:
    load_module_safely("modules.factory_management", "render_factory_management_page", engine=engine, lang=curr_lang)

elif "員工" in feat_str or "人事" in feat_str:
    load_module_safely("modules.employee_management", "render_employee_management", engine=engine, t=ui_t, lang=curr_lang)

elif "車輛進出口門禁" in feat_str or "派車審核" in feat_str:
    load_module_safely("modules.vehicle_gate_log", "render_vehicle_gate_log_page", engine=engine, lang=curr_lang)

elif "車輛維修" in feat_str or "保養紀錄" in feat_str:
    load_module_safely("modules.vehicle_maintenance", "render_vehicle_maintenance_page", engine=engine, lang=curr_lang)

elif "倉庫" in feat_str or "倉儲" in feat_str:
    load_module_safely("modules.warehouse_management", "render_warehouse_management", engine=engine, t=ui_t, lang=curr_lang)

elif "板金" in feat_str:
    load_module_safely("modules.sheet_metal", "render_sheet_metal_module", engine=engine, t=ui_t, lang=curr_lang)

elif "塗料" in feat_str or "烤漆" in feat_str:
    load_module_safely("modules.painting", "render_painting_module", engine=engine, t=ui_t, lang=curr_lang)

elif "配盤" in feat_str or "組裝" in feat_str:
    load_module_safely("modules.assembly", "render_assembly_module", engine=engine, t=ui_t, lang=curr_lang)

elif "系統角色權限" in feat_str or "模組開關" in feat_str:
    if current_role_clean == "admin":
        load_module_safely("modules.user_management", "render_user_management_page", engine=engine, lang=curr_lang)
    else:
        st.error("⚠️ 權限不足：資訊管理部僅限系統管理員 (admin) 登入存取。")

feat_str = str(selected_feat_label)

elif "API" in feat_str:
    if current_role_clean == "admin":
        load_module_safely("modules.system_licensing", "render_licensing_control_page", engine=engine, lang=curr_lang)
    else:
        st.error("⚠️ 權限不足：僅限系統管理員 (admin) 存取。")

else:
    # 預設萬用回退：若自訂了新部門或新功能，預設嘗試載入對應名稱的模組或顯示友善提示
    st.markdown(f"### 📍 目前選定功能：{selected_feat_label}")
    st.info("💡 此功能模組正在載入中，或您可以前往【資訊管理部 > 系統角色權限與模組開關設定】進行進一步配置。")
