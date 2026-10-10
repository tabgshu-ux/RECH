import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 裕豐電機工業 AI ERP 系統 - 主程式進入點
# ----------------------------------------------------
st.set_page_config(
    page_title="裕豐電機工業 AI ERP 系統",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 導入各個模組
try:
    from modules import (
        employee_management,
        factory_management,
        warehouse_management,
        sales_quotation,
        sales_order_ar,
        procurement_ap,
        invoice_management,
        financial_tax_reports,
        payroll_management,
        internal_attendance,
        subcontractor_labor,
        erp_dashboard,
        executive_dashboard,
        engineering_department,
        engineering_pipeline,
        fat_sat_testing,
        field_attendance,
        field_daily_report,
        general_affairs,
        vehicle_maintenance,
        vehicle_gate_log,
        user_management,
        system_licensing,
        vietnam_tax_invoice,
        finance_tax
    )
except ImportError:
    import employee_management
    import factory_management
    import warehouse_management
    import sales_quotation
    import sales_order_ar
    import procurement_ap
    import invoice_management
    import financial_tax_reports
    import payroll_management
    import internal_attendance
    import subcontractor_labor
    import erp_dashboard
    import executive_dashboard
    import engineering_department
    import engineering_pipeline
    import fat_sat_testing
    import field_attendance
    import field_daily_report
    import general_affairs
    import vehicle_maintenance
    import vehicle_gate_log
    import user_management
    import system_licensing
    import vietnam_tax_invoice
    import finance_tax

# ----------------------------------------------------
# 🔐 登入狀態與工作階段初始化
# ----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user_info" not in st.session_state:
    st.session_state["user_info"] = {
        "name": "張董事長",
        "role": "admin",
        "dept": "總經理室",
        "factory": "西寧廠 (Tay Ninh)"
    }

if "current_lang" not in st.session_state:
    st.session_state["current_lang"] = "繁體中文"

# ----------------------------------------------------
# 🎨 自訂 CSS：登入畫面置中優化
# ----------------------------------------------------
st.markdown("""
    <style>
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 🔐 登入畫面（置中對齊優化）
# ----------------------------------------------------
def render_login_screen():
    # 運用三欄式版面 [1, 1.5, 1]，將中間欄位作為置中登入區塊
    _, col_center, _ = st.columns([1, 1.6, 1])

    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>⚡ 裕豐電機工業 AI ERP 系統</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>請輸入帳號密碼與選擇語系以登入系統</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("使用者帳號 (Username)", placeholder="請輸入帳號...")
            password = st.text_input("密碼 (Password)", type="password", placeholder="請輸入密碼...")
            
            selected_lang = st.selectbox(
                "選擇介面語系 (Select Language)",
                ["繁體中文", "Tiếng Việt", "English"]
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_login = st.form_submit_button("🚀 登入系統 (Login)", use_container_width=True)

            if submit_login:
                st.session_state["current_lang"] = selected_lang
                if len(username.strip()) > 0:
                    st.session_state["logged_in"] = True
                    st.session_state["user_info"] = {
                        "name": username,
                        "role": "admin" if username == "admin" else "manager",
                        "dept": "總經理室"
                    }
                    st.success("🎉 登入成功！")
                    st.rerun()
                else:
                    st.error("❌ 請輸入有效的使用者帳號！")

# ----------------------------------------------------
# 🚀 主系統架構與功能選單導航
# ----------------------------------------------------
def main():
    if not st.session_state.get("logged_in", False):
        render_login_screen()
        return

    user_info = st.session_state.get("user_info", {"name": "張董事長", "role": "admin", "dept": "總經理室"})
    current_lang = st.session_state.get("current_lang", "繁體中文")

    # ----------------------------------------------------
    # 📌 側邊欄導航 (Sidebar Navigation & Multi-Language)
    # ----------------------------------------------------
    with st.sidebar:
        st.markdown(f"### 👤 目前登入：`{user_info['name']}`")
        st.caption(f"角色: `{user_info['role']}` | 部門: `{user_info['dept']}`")
        
        st.markdown("---")
        
        # 語系切換器
        selected_lang = st.selectbox(
            "🌐 選擇系統語系 (Language)",
            ["繁體中文", "Tiếng Việt", "English"],
            index=["繁體中文", "Tiếng Việt", "English"].index(current_lang) if current_lang in ["繁體中文", "Tiếng Việt", "English"] else 0
        )
        if selected_lang != current_lang:
            st.session_state["current_lang"] = selected_lang
            st.rerun()

        st.markdown("---")
        st.markdown("### 🗂️ 裕豐 AI ERP 模組選單")

        # 依語系定義模組選單名稱
        if selected_lang == "Tiếng Việt":
            nav_options = [
                "📊 Tổng quan Quản lý (Executive Dashboard)",
                "🏢 Quản lý Nhân sự & Hồ sơ",
                "🏗️ Quản lý Nhà máy & Phân xưởng",
                "📦 Quản lý Kho & Vật tư",
                "💼 Kinh doanh & Báo giá AI (CAD/3D)",
                "📋 Phải thu Dự án (AR)",
                "🛒 Mua hàng & Phải trả (AP)",
                "🧾 Quản lý Hóa đơn Điện tử",
                "📊 Báo cáo Tài chính Thuế TT200",
                "💰 Quản lý Lương & Bảo hiểm",
                "🏢 Chấm công & Luật Lao động VN",
                "👷 Nhân công Thầu phụ & Chấm công",
                "⚡ Thiết kế Kỹ thuật & BOM",
                "📐 Chuỗi Kỹ thuật & Đường ống",
                "🧪 Kiểm tra FAT/SAT & Chất lượng",
                "📱 Báo cáo Hiện trường & Điểm danh",
                "🏢 Quản lý Tổng hành & Mua sắm",
                "🛠️ Bảo trì Xe & Nhập Excel",
                "🚗 Quản lý Xe ra vào Cổng",
                "🔒 Quản trị IT & Nhật ký Kiểm toán",
                "🔑 Bản quyền Thương mại & Storage",
                "📊 Hóa đơn điện tử & Tuân thủ thuế"
            ]
        elif selected_lang == "English":
            nav_options = [
                "📊 Executive Dashboard",
                "🏢 HR & Employee Management",
                "🏗️ Factory & Plant Management",
                "📦 Warehouse & Inventory",
                "💼 Sales & AI Quotation (CAD/3D)",
                "📋 Project Accounts Receivable (AR)",
                "🛒 Purchasing & Accounts Payable (AP)",
                "🧾 E-Invoice Management",
                "📊 Financial & Tax Reports (Circular 200)",
                "💰 Employee Payroll & Insurance",
                "🏢 Internal Attendance & VN Labor Law",
                "👷 Subcontractor Daily Labor & Payroll",
                "⚡ Engineering Dept & BOM",
                "📐 Engineering Pipeline & Drawings",
                "🧪 FAT/SAT Testing & Quality",
                "📱 Field Attendance & Daily Reports",
                "🏢 General Affairs & Procurement",
                "🛠️ Vehicle Maintenance & Excel Import",
                "🚗 Vehicle Gate Access & Dispatch",
                "🔒 IT Admin & Audit Logs",
                "🔑 Commercial Licensing & Storage",
                "📊 Vietnam E-Invoice & Tax Compliance"
            ]
        else:
            nav_options = [
                "📊 總經理室營運戰情室 (Executive Dashboard)",
                "🏢 管理部 - 員工個人檔案與人事管理",
                "🏗️ 廠務管理與產線動態 (Factory Management)",
                "📦 生產部/倉儲 - 倉庫庫存與資材管理",
                "💼 業務/行銷 - 報價與 CAD/3D Pipeline",
                "📋 財務部 - 工程專案應收帳款 (AR)",
                "🛒 財務部 - 採購與應付帳款 (AP)",
                "🧾 財務部 - 越南電子發票綜合管理",
                "📊 財務部 - 越文會計傳票與 Thông tư 200 報表",
                "💰 財務部 - 員工薪資與保險扣除中心",
                "🏢 管理部 - 廠內智慧考勤與越南勞動法",
                "👷 外包商點工計價與越南勞動法計薪",
                "⚡ 工程部 - 統包工程專案與 BOM 展開",
                "📐 工程部 - 管道工項與設計圖紙管線",
                "🧪 品保部 - FAT/SAT 測試驗收與缺失改善",
                "📱 工地現場 - 外勤打卡、點工與施工日報",
                "🏢 總務管理系統 - 固定資產與多幣別請款",
                "🛠️ 管理部 - 車輛維修保養與 Excel 批次匯入",
                "🚗 警衛室 - 廠區車輛進出與派車審核放行",
                "🔒 IT 管理中心 - 帳號權限與系統稽核軌跡",
                "🔑 IT 商業授權與 Storage 系統管理",
                "📊 越南營建電子發票與稅務合規管家"
            ]

        selected_module = st.selectbox("📌 選擇執行模組 (Select Module)", nav_options)

        st.markdown("---")
        if st.button("🚪 登出系統 (Logout)", use_container_width=True):
            st.session_state["logged_in"] = False
            st.rerun()

    # ----------------------------------------------------
    # 🔀 模組路由分流與安全呼叫
    # ----------------------------------------------------
    try:
        if any(k in selected_module for k in ["戰情室", "Executive Dashboard"]):
            executive_dashboard.show(lang=selected_lang)
        elif any(k in selected_module for k in ["人事管理", "HR & Employee", "員工個人檔案"]):
            employee_management.show(lang=selected_lang)
        elif any(k in selected_module for k in ["廠務管理", "Factory"]):
            factory_management.show(lang=selected_lang)
        elif any(k in selected_module for k in ["倉庫庫存", "Warehouse"]):
            warehouse_management.show(lang=selected_lang)
        elif any(k in selected_module for k in ["報價", "Sales", "CAD/3D"]):
            sales_quotation.show(lang=selected_lang)
        elif any(k in selected_module for k in ["應收帳款", "Receivable", "AR"]):
            sales_order_ar.show(lang=selected_lang)
        elif any(k in selected_module for k in ["應付帳款", "Purchasing", "AP"]):
            procurement_ap.show(lang=selected_lang)
        elif any(k in selected_module for k in ["電子發票綜合管理", "E-Invoice Management"]):
            invoice_management.show(lang=selected_lang)
        elif any(k in selected_module for k in ["Thông tư 200", "會計傳票", "Financial & Tax Reports"]):
            financial_tax_reports.show(lang=selected_lang)
        elif any(k in selected_module for k in ["員工薪資", "Payroll"]):
            payroll_management.show(lang=selected_lang)
        elif any(k in selected_module for k in ["考勤", "Attendance", "勞動法"]):
            internal_attendance.show(lang=selected_lang)
        elif any(k in selected_module for k in ["外包商", "Subcontractor"]):
            subcontractor_labor.show(lang=selected_lang)
        elif any(k in selected_module for k in ["工程部", "Engineering Dept"]):
            engineering_department.show(lang=selected_lang)
        elif any(k in selected_module for k in ["管道工項", "Pipeline"]):
            engineering_pipeline.show(lang=selected_lang)
        elif any(k in selected_module for k in ["FAT", "SAT", "測試驗收"]):
            fat_sat_testing.show(lang=selected_lang)
        elif any(k in selected_module for k in ["工地現場", "Field Attendance", "施工日報"]):
            field_daily_report.show(lang=selected_lang)
        elif any(k in selected_module for k in ["總務管理", "General Affairs"]):
            general_affairs.show(lang=selected_lang)
        elif any(k in selected_module for k in ["車輛維修", "Vehicle Maintenance"]):
            vehicle_maintenance.show(lang=selected_lang)
        elif any(k in selected_module for k in ["車輛進出", "Gate Access"]):
            vehicle_gate_log.show(lang=selected_lang)
        elif any(k in selected_module for k in ["帳號權限", "User Permissions", "IT 管理中心"]):
            user_management.show(lang=selected_lang)
        elif any(k in selected_module for k in ["商業授權", "Licensing"]):
            system_licensing.show(lang=selected_lang)
        elif any(k in selected_module for k in ["越南營建電子發票", "Vietnam E-Invoice & Tax"]):
            vietnam_tax_invoice.show(lang=selected_lang)
        else:
            executive_dashboard.show(lang=selected_lang)
    except Exception as e:
        st.error(f"❌ 模組載入發生錯誤: {e}")
        st.info("💡 請確認所有模組檔案皆已完整放置於專案目錄中。")

if __name__ == "__main__":
    main()
