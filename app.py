import streamlit as st
import importlib

# 頁面基本設定
st.set_page_config(
    page_title="REETECH Vietnam SaaS ERP",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 🔐 登入驗證模組 (Login Authentication)
# ----------------------------------------------------
def render_login_page():
    st.markdown("<h2 style='text-align: center;'>🏭 REETECH Vietnam SaaS ERP</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>西寧廠企業資源規劃系統 - 請先登入帳號</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username_input = st.text_input("👤 帳號 / Username", placeholder="請輸入帳號 (例如: admin)")
            password_input = st.text_input("🔑 密碼 / Password", type="password", placeholder="請輸入密碼")
            lang_choice = st.selectbox("🌐 語言 / Language", ["繁體中文", "Tiếng Việt", "English"])
            
            submit_login = st.form_submit_button("🚀 登入系統 / Login", type="primary", use_container_width=True)
            
            if submit_login:
                # 簡單驗證（實務上可串接資料庫 users 表格進行雜湊驗證）
                if username_input.strip() == "admin" and password_input == "admin123":
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = "admin"
                    st.session_state["user_role"] = "系統管理員"
                    st.session_state["lang"] = lang_choice
                    st.success("🎉 登入成功！正在進入系統...")
                    st.rerun()
                elif username_input.strip() != "" and password_input.strip() != "":
                    # 一般廠區同仁或主管帳號
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = username_input.strip()
                    st.session_state["user_role"] = "一般使用者 / 員工"
                    st.session_state["lang"] = lang_choice
                    st.success(f"🎉 歡迎 [{username_input}] 登入 REETECH ERP！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請輸入正確的帳號與密碼！")

        st.info("💡 預設測試帳號：\n- 系統管理員: `admin` / `admin123` (可見 IT 資訊管理)\n- 一般同仁: 自行輸入姓名登入")

# ----------------------------------------------------
# 🏭 主系統介面 (Main App)
# ----------------------------------------------------
def main():
    # 檢查是否已登入
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        render_login_page()
        return

    # 已登入後的側邊欄選單
    current_user = st.session_state.get("current_user", "Guest")
    user_role = st.session_state.get("user_role", "員工")
    is_admin = (current_user.lower() == "admin")
    current_lang = st.session_state.get("lang", "繁體中文")

    st.sidebar.title("🏭 REETECH ERP 中樞")
    st.sidebar.markdown(f"👤 **使用者**: {current_user} (`{user_role}`)")
    
    if st.sidebar.button("🚪 登出系統 / Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
        st.rerun()

    st.sidebar.markdown("---")

    # 依造您的要求排序的部門與核心功能選單
    departments_dict = {
        "繁體中文": [
            "📈 總經理室 (Executive Office)",
            "🛠️ 工程與設計管理中心 (Engineering & Design)",
            "👔 管理部 (Management Dept)",
            "🏭 生產部 (Production Dept)",
            "📦 倉庫管理 (Warehouse Management)",
            "📍 外勤工程打卡與即時人數 (Field Attendance)",
            "✍️ 全公司電子簽核中心 (Approval Center)"
        ],
        "Tiếng Việt": [
            "📈 Văn phòng Giám đốc (Executive Office)",
            "🛠️ Trung tâm Kỹ thuật & Thiết kế (Engineering)",
            "👔 Phòng Quản lý (Management Dept)",
            "📦 Quản lý Kho (Warehouse)",
            "📍 Chấm công & Vị trí hiện trường (Field Attendance)",
            "✍️ Trung tâm Phê duyệt điện tử (Approval Center)"
        ],
        "English": [
            "📈 Executive Office",
            "🛠️ Engineering & Design Center",
            "Management Dept",
            "Production Dept",
            "Warehouse Management",
            "Field Attendance & Headcount",
            "Electronic Approval Center"
        ]
    }

    it_menu_label = {
        "繁體中文": "💻 資訊管理部 (IT System - Admin Only)",
        "Tiếng Việt": "💻 Quản lý CNTT (IT System - Admin Only)",
        "English": "💻 IT System (Admin Only)"
    }

    menu_list = list(departments_dict.get(current_lang, departments_dict["繁體中文"]))
    
    # 只有 Admin 才能看到資訊管理部
    if is_admin:
        menu_list.append(it_menu_label.get(current_lang, it_menu_label["繁體中文"]))

    selected_dept = st.sidebar.radio("📌 選擇部門與功能 / Select Module", menu_list)
    st.sidebar.markdown("---")
    
    engine = st.session_state.get("db_engine", None)

    # ----------------------------------------------------
# 🔀 裕豐電機專屬：全部門與細緻子功能智慧安全路由分流
# ----------------------------------------------------
feat_str = str(selected_feat_label)
dept_str = str(selected_dept_label)

# 1. 資訊管理部 (僅限 admin)
if "資訊管理部" in dept_str or "IT System" in dept_str or "Quản lý CNTT" in dept_str:
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

# 2. 總經理室 (Executive Office)
elif "總經理室" in dept_str or "Executive Office" in dept_str or "Văn phòng Giám đốc" in dept_str:
    if "原料價格" in feat_str or "Gemini" in feat_str:
        load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route="commodities_fx", lang=curr_lang)
    elif "財務類" in feat_str or "AR/AP & P&L" in feat_str:
        load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route="financials_pl", lang=curr_lang)
    elif "專案進度" in feat_str or "異常監控" in feat_str:
        load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route="project_progress_exec", lang=curr_lang)
    elif "政策" in feat_str or "法規" in feat_str:
        load_module_safely("modules.vietnam_policy_news", "render_vietnam_policy_news_page", engine=engine, lang=curr_lang)
    else:
        load_module_safely("modules.executive_dashboard", "render_executive_dashboard_page", sub_route="commodities_fx", lang=curr_lang)

# 3. 工程與設計管理中心 (Engineering & Design)
elif "工程" in dept_str or "Engineering" in dept_str or "Kỹ thuật" in dept_str:
    load_module_safely("modules.engineering_management", "render_engineering_management_page", engine=engine, lang=curr_lang)

# 4. 管理部 (Management Dept) - 包含公告、正式文件、人事、薪資、採購、資產、發票等
elif "管理部" in dept_str or "Management Dept" in dept_str or "Phòng Quản lý" in dept_str:
    if "公告" in feat_str or "佈告欄" in feat_str:
        load_module_safely("modules.company_announcements", "render_company_announcements_page", engine=engine, lang=curr_lang)
    elif "正式文件" in feat_str or "文件製作" in feat_str:
        load_module_safely("modules.management.document_generator", "render_document_generator_page", engine=engine, lang=curr_lang)
    elif "員工" in feat_str or "人事" in feat_str:
        load_module_safely("modules.employee_management", "render_employee_management", engine=engine, t=ui_t, lang=curr_lang)
    elif "打卡" in feat_str or "出勤" in feat_str:
        load_module_safely("modules.internal_attendance", "render_internal_attendance_page", engine=engine, lang=curr_lang)
    elif "宿舍" in feat_str or "伙食" in feat_str:
        load_module_safely("modules.dorm_catering", "render_dorm_catering_module", engine=engine, lang=curr_lang)
    elif "車輛進出口" in feat_str or "派車" in feat_str:
        load_module_safely("modules.vehicle_gate_log", "render_vehicle_gate_log_page", engine=engine, lang=curr_lang)
    elif "車輛維修" in feat_str or "保養" in feat_str:
        load_module_safely("modules.vehicle_maintenance", "render_vehicle_maintenance_page", engine=engine, lang=curr_lang)
    elif "固定資產" in feat_str or "設備" in feat_str:
        load_module_safely("modules.asset_management", "render_asset_management_page", engine=engine, lang=curr_lang)
    elif "採購" in feat_str or "應付帳款" in feat_str:
        load_module_safely("modules.procurement_ap", "render_procurement_ap_page", engine=engine, lang=curr_lang)
    elif "應收帳款" in feat_str or "對帳" in feat_str:
        load_module_safely("modules.sales_order_ar", "render_sales_order_ar_page", engine=engine, lang=curr_lang)
    elif "越南稅務" in feat_str or "Thông tư 200" in feat_str:
        load_module_safely("modules.financial_tax_reports", "render_financial_tax_reports_page", engine=engine, lang=curr_lang)
    elif "薪資" in feat_str or "保險" in feat_str:
        load_module_safely("modules.payroll_management", "render_payroll_management_page", engine=engine, lang=curr_lang)
    elif "電子發票" in feat_str or "XML" in feat_str:
        load_module_safely("modules.invoice_management", "render_invoice_management_page", engine=engine, lang=curr_lang)
    else:
        load_module_safely("modules.company_announcements", "render_company_announcements_page", engine=engine, lang=curr_lang)

# 5. 生產部 (Production Dept)
elif "生產部" in dept_str or "Production Dept" in dept_str or "Sản xuất" in dept_str:
    if "板金" in feat_str:
        load_module_safely("modules.sheet_metal", "render_sheet_metal_module", engine=engine, t=ui_t, lang=curr_lang)
    elif "塗料" in feat_str or "烤漆" in feat_str:
        load_module_safely("modules.painting", "render_painting_module", engine=engine, t=ui_t, lang=curr_lang)
    elif "配盤" in feat_str or "組裝" in feat_str:
        load_module_safely("modules.assembly", "render_assembly_module", engine=engine, t=ui_t, lang=curr_lang)
    elif "廠區" in feat_str:
        load_module_safely("modules.factory_management", "render_factory_management_page", engine=engine, lang=curr_lang)
    else:
        load_module_safely("modules.factory_management", "render_factory_management_page", engine=engine, lang=curr_lang)

# 6. 倉庫管理 (Warehouse Management)
elif "倉庫" in dept_str or "Warehouse" in dept_str or "Quản lý Kho" in dept_str:
    load_module_safely("modules.warehouse_management", "render_warehouse_management", engine=engine, t=ui_t, lang=curr_lang)

# 7. 外勤工程打卡與即時人數
elif "外勤" in dept_str or "Field Attendance" in dept_str or "Chấm công" in dept_str:
    load_module_safely("modules.management.hr.field_attendance", "render_field_attendance_page", engine=engine, lang=curr_lang, view_mode="management" if "統計" in feat_str else "field_worker")

# 8. 全公司電子簽核中心
elif "簽核" in dept_str or "Approval" in dept_str or "Phê duyệt" in dept_str:
    load_module_safely("modules.approval_workflow", "render_approval_center", lang=curr_lang)

else:
    st.markdown(f"### 📍 目前選定功能：{selected_feat_label}")
    st.info("💡 此模組正在運行中，或可至【資訊管理部】進行設定。")
   
except Exception as e:
        st.error(f"⚠️ 載入模組發生異常: {str(e)}")

if __name__ == "__main__":
    main()
