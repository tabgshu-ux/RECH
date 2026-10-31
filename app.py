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

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("❓ 忘記密碼 / Quên mật khẩu / Forgot Password?"):
            st.info("💡 若您不慎遺失密碼，請聯繫**管理部人事**進行身分核對與密碼重設。")

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

dept_module_tree = get_department_module_tree()
department_names = list(dept_module_tree.keys())

available_dept_names = []
for d_name in department_names:
    if current_role_clean != "admin" and "資訊管理部" in d_name:
        continue
    if current_role_clean == "security" and "管理部" not in d_name:
        continue
    available_dept_names.append(d_name)

if not available_dept_names:
    available_dept_names = department_names

if current_role_clean in ["fieldworker", "外勤人員", "worker", "外勤技師"]:
    selected_dept_label = "📍 外勤工程打卡與工作回報 (Field Attendance)"
    selected_feat_label = "📍 現場外勤打卡與工作回報"
    st.sidebar.markdown("**📌 外勤專用直達模式**")
elif current_role_clean == "security":
    selected_dept_label = next((d for d in available_dept_names if "管理部" in d), available_dept_names[0])
    st.sidebar.markdown(f"**{ui_t['parent_header']}**")
    st.sidebar.markdown(f"👔 {selected_dept_label}")
    selected_feat_label = "🚗 廠區車輛進出口門禁與派車審核"
else:
    st.sidebar.markdown(f"**{ui_t['parent_header']}**")
    
    selected_dept_label = st.sidebar.radio(
        ui_t["parent_header"],
        available_dept_names,
        index=st.session_state.get("selected_dept_index", 0),
        key="dept_radio_idx",
        label_visibility="collapsed"
    )
    
    selected_dept_index = available_dept_names.index(selected_dept_label)
    if selected_dept_index != st.session_state.get("selected_dept_index", 0):
        st.session_state.selected_dept_index = selected_dept_index
        st.session_state.selected_feat_index = 0
        st.session_state.mgmt_active_tab = "總覽"
        st.rerun()

    selected_feat_label = selected_dept_label

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
# 🔀 精準路由分發 
# ----------------------------------------------------
try:
    feat_str = str(selected_feat_label)
    dept_str = str(selected_dept_label)

    if "外勤工程打卡" in dept_str or "Field Attendance" in dept_str:
        load_module_safely("modules.field_gps_attendance", "render_field_gps_attendance", engine=engine, lang=curr_lang)

    elif "資訊管理部" in dept_str:
        if current_role_clean == "admin":
            sub_mod_choice = st.selectbox("📌 選擇 IT 管理子模組", ["🏢 1. 獨立企業部門與模組拼圖", "⚙️ 2. 組織角色與權限指派 (RBAC)", "🔌 3. 資料庫與 API 閘道器", "📊 4. 系統稽核日誌與追蹤"])
            if "獨立企業部門" in sub_mod_choice:
                load_module_safely("modules.it_system.department_config", "render", engine=engine, lang=curr_lang)
            elif "組織角色" in sub_mod_choice:
                load_module_safely("modules.it_system.role_rbac", "render", engine=engine, lang=curr_lang)
            elif "資料庫" in sub_mod_choice:
                load_module_safely("modules.it_system.db_bridge", "render", engine=engine, lang=curr_lang)
            elif "系統稽核" in sub_mod_choice:
                load_module_safely("modules.it_system.audit_logs", "render", engine=engine, lang=curr_lang)
        else:
            st.error("🚫 權限不足：資訊管理部僅限系統管理員 (admin) 存取與設定！")

    elif "總經理室" in dept_str:
        sub_exec_choice = st.selectbox("📌 選擇總經理室子功能", ["📊 原料價格與匯率戰情室", "💰 財務與損益類", "📈 專案進度與異常監控", "🇻🇳 越南政策與法規"])
        if "原料價格" in sub_exec_choice:
            load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route="commodities_fx", lang=curr_lang)
        elif "財務" in sub_exec_choice:
            load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route="financials_pl", lang=curr_lang)
        elif "專案進度" in sub_exec_choice:
            load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route="project_progress_exec", lang=curr_lang)
        elif "政策" in sub_exec_choice:
            load_module_safely("modules.vietnam_policy_news", "render_vietnam_policy_news_page", engine=engine, lang=curr_lang)
        else:
            load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route="commodities_fx", lang=curr_lang)

    elif "管理部" in dept_str:
        load_module_safely("modules.management.dashboard", "render_management_dashboard", engine=engine, lang=curr_lang)

    elif "工程與設計管理中心" in dept_str:
        eng_sub_choice = st.selectbox("📌 選擇工程中心子模組", [
            "1. 工程主管戰情室", "2. 工程專案報價系統", "3. 施工日報表 (點工點料)", 
            "4. AI 施工照片辨識", "5. 工程證照預警", "6. 配電盤電氣與機構設計圖庫", 
            "7. 配電盤 BOM 零件與採購連動", "8. 外包商計價", "9. FAT/SAT 現場驗收"
        ])
        if "1. 工程主管戰情室" in eng_sub_choice:
            load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang, sub_tab="dashboard")
        elif "2. 工程專案報價系統" in eng_sub_choice:
            load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang, sub_tab="quotation")
        elif "3. 施工日報表" in eng_sub_choice:
            load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang, sub_tab="daily_report")
        elif "4. AI 施工照片辨識" in eng_sub_choice:
            load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang, sub_tab="ai_audit")
        elif "5. 工程證照預警" in eng_sub_choice:
            load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang, sub_tab="license_alert")
        elif "6. 配電盤電氣與機構設計圖庫" in eng_sub_choice:
            load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang, sub_tab="drawing_gallery")
        elif "7. 配電盤 BOM 零件" in eng_sub_choice:
            load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang, sub_tab="bom_procurement")
        elif "8. 外包商計價" in eng_sub_choice:
            load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang, sub_tab="subcontractor")
        elif "9. FAT/SAT" in eng_sub_choice:
            load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang, sub_tab="fatsat")

    elif "生產部" in dept_str:
        prod_sub_choice = st.selectbox("📌 選擇生產部子模組", ["板金加工模組", "塗料產線模組", "配盤組裝模組"])
        if "板金" in prod_sub_choice:
            load_module_safely("modules.sheet_metal", "render_sheet_metal_module", engine=engine, t=ui_t, lang=curr_lang)
        elif "塗料" in prod_sub_choice:
            load_module_safely("modules.painting", "render_painting_module", engine=engine, t=ui_t, lang=curr_lang)
        elif "配盤" in prod_sub_choice:
            load_module_safely("modules.assembly", "render_assembly_module", engine=engine, t=ui_t, lang=curr_lang)

    elif "倉庫管理" in dept_str:
        load_module_safely("modules.warehouse_management", "render_warehouse_management", engine=engine, t=ui_t, lang=curr_lang)

    elif "電子簽核中心" in dept_str:
        load_module_safely("modules.approval_workflow", "render_approval_center", lang=curr_lang)

    else:
        st.markdown(f"### 📍 目前選定部門：{dept_str}")
        st.info("💡 此部門模組正在運行中。")

except Exception as e:
    st.error(f"⚠️ 路由分發發生異常: {str(e)}")
