import streamlit as st

MANAGEMENT_DASHBOARD_I18N = {
    "繁體中文": {
        "title": "👔 管理部綜合導航中心",
        "caption": "管理公司人事行政、總務後勤與財務會計等核心作業。請點擊下方卡片快速進入對應管理專區。",
        "card_hr_title": "👤 人事行政區",
        "card_hr_desc": "掌握員工名冊、出勤、薪資與保險。",
        "card_hr_items": "- 📋 員工基本檔案\n- ⏱️ 員工打卡紀錄\n- 💳 員工薪資與保險\n- 🔑 密碼變更設定",
        "btn_hr": "🚀 進入人事行政中心",
        
        "card_ga_title": "📦 總務後勤區",
        "card_ga_desc": "廠區車輛、門禁安防、固定資產與食宿。",
        "card_ga_items": "- 🚗 車輛進出口與門禁\n- 🔧 車輛維修紀錄\n- 🏢 固定資產管理\n- 🍲 宿舍與伙食管理\n- 🌿 廠區設施維護",
        "btn_ga": "🚀 進入總務後勤中心",
        
        "card_fin_title": "💰 財務會計區",
        "card_fin_desc": "採購應付、應收帳款與越南稅務合規。",
        "card_fin_items": "- 🛒 採購與應付帳款 (AP)\n- 📊 應收帳款管理 (AR)\n- 📑 越南稅務與報表\n- 🧾 電子發票管理",
        "btn_fin": "🚀 進入財務會計中心",
        
        "btn_back": "⬅️ 返回總覽卡片",
        "select_item": "選擇作業項目",
        
        "hr_sub": "👥 人事行政作業專區",
        "hr_options": ["員工基本檔案", "員工打卡紀錄", "員工薪資與保險", "密碼修改"],
        
        "ga_sub": "📦 總務後勤作業專區",
        "ga_options": ["車輛進出口與門禁", "車輛維修紀錄", "固定資產管理", "宿舍與伙食管理", "廠區設施維護"],
        
        "fin_sub": "💰 財務會計作業專區",
        "fin_options": ["採購與應付帳款", "應收帳款管理", "越南稅務報表", "電子發票管理"]
    },
    "Tiếng Việt": {
        "title": "👔 Trung tâm Điều hành Quản lý Tổng hợp",
        "caption": "Quản lý nhân sự, hậu cần chung và kế toán tài chính. Nhấp vào các thẻ bên dưới để truy cập nhanh các khu vực quản lý.",
        "card_hr_title": "👤 Khu vực Nhân sự & Hành chính",
        "card_hr_desc": "Quản lý hồ sơ nhân viên, chấm công, lương và bảo hiểm.",
        "card_hr_items": "- 📋 Hồ sơ nhân viên cơ bản\n- ⏱️ Lịch sử chấm công\n- 💳 Lương & Bảo hiểm\n- 🔑 Thay đổi mật khẩu",
        "btn_hr": "🚀 Vào Trung tâm Nhân sự",
        
        "card_ga_title": "📦 Khu vực Hậu cần & Tổng vụ",
        "card_ga_desc": "Phương tiện nhà máy, an ninh cổng, tài sản cố định và ký túc xá.",
        "card_ga_items": "- 🚗 Kiểm soát cổng xe ra vào\n- 🔧 Lịch sử bảo trì xe\n- 🏢 Quản lý tài sản cố định\n- 🍲 Ký túc xá & Suất ăn\n- 🌿 Bảo trì cơ sở hạ tầng",
        "btn_ga": "🚀 Vào Trung tâm Hậu cần",
        
        "card_fin_title": "💰 Khu vực Kế toán & Tài chính",
        "card_fin_desc": "Mua sắm phải trả, khoản phải thu và tuân thủ thuế Việt Nam.",
        "card_fin_items": "- 🛒 Mua sắm & Phải trả (AP)\n- 📊 Khoản phải thu (AR)\n- 📑 Báo cáo thuế Việt Nam\n- 🧾 Hóa đơn điện tử",
        "btn_fin": "🚀 Vào Trung tâm Tài chính",
        
        "btn_back": "⬅️ Quay lại Tổng quan",
        "select_item": "Chọn mục thao tác",
        
        "hr_sub": "👥 Khu vực Nghiệp vụ Nhân sự",
        "hr_options": ["Hồ sơ nhân viên", "Chấm công", "Lương & Bảo hiểm", "Đổi mật khẩu"],
        
        "ga_sub": "📦 Khu vực Nghiệp vụ Hậu cần",
        "ga_options": ["Kiểm soát cổng xe", "Bảo trì xe", "Tài sản cố định", "Ký túc xá & Suất ăn", "Bảo trì cơ sở"],
        
        "fin_sub": "💰 Khu vực Kế toán & Tài chính",
        "fin_options": ["Mua sắm & Phải trả", "Khoản phải thu", "Báo cáo thuế", "Hóa đơn điện tử"]
    },
    "English": {
        "title": "👔 Management Department Dashboard",
        "caption": "Manage HR, general affairs, and finance operations. Click cards below to access modules.",
        "card_hr_title": "👤 HR & Administration",
        "card_hr_desc": "Manage employee registry, attendance, payroll & insurance.",
        "card_hr_items": "- 📋 Employee Profiles\n- ⏱️ Attendance Records\n- 💳 Payroll & Insurance\n- 🔑 Password Settings",
        "btn_hr": "🚀 Enter HR Center",
        
        "card_ga_title": "📦 General Affairs & Logistics",
        "card_ga_desc": "Factory vehicles, gate security, fixed assets & catering.",
        "card_ga_items": "- 🚗 Vehicle Gate & Access\n- 🔧 Vehicle Maintenance\n- 🏢 Fixed Assets\n- 🍲 Dormitory & Catering\n- 🌿 Facility Maintenance",
        "btn_ga": "🚀 Enter GA Center",
        
        "card_fin_title": "Finance & Accounting",
        "card_fin_desc": "Procurement AP, AR, and Vietnamese tax compliance.",
        "card_fin_items": "- 🛒 Procurement & AP\n- 📊 Accounts Receivable (AR)\n- 📑 VN Tax Reports\n- 🧾 E-Invoice Management",
        "btn_fin": "🚀 Enter Finance Center",
        
        "btn_back": "⬅️ Back to Dashboard",
        "select_item": "Select Task",
        
        "hr_sub": "👥 HR Operations",
        "hr_options": ["Employee Profiles", "Attendance", "Payroll & Insurance", "Password Settings"],
        
        "ga_sub": "📦 General Affairs Operations",
        "ga_options": ["Vehicle Gate", "Vehicle Maintenance", "Fixed Assets", "Dorm & Catering", "Facility Maintenance"],
        
        "fin_sub": "💰 Finance Operations",
        "fin_options": ["Procurement & AP", "Accounts Receivable", "Tax Reports", "E-Invoices"]
    }
}

def render_management_dashboard(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in MANAGEMENT_DASHBOARD_I18N else "繁體中文"
    L = MANAGEMENT_DASHBOARD_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])
    st.markdown("---")

    if "mgmt_active_tab" not in st.session_state:
        st.session_state.mgmt_active_tab = "總覽"

    if st.session_state.mgmt_active_tab == "總覽":
        col_hr, col_ga, col_fin = st.columns(3)

        with col_hr:
            st.markdown(f"### {L['card_hr_title']}")
            st.markdown(L['card_hr_desc'])
            st.markdown(L['card_hr_items'])
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(L['btn_hr'], use_container_width=True, key="btn_hr"):
                st.session_state.mgmt_active_tab = "人事行政"
                st.rerun()

        with col_ga:
            st.markdown(f"### {L['card_ga_title']}")
            st.markdown(L['card_ga_desc'])
            st.markdown(L['card_ga_items'])
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(L['btn_ga'], use_container_width=True, key="btn_ga"):
                st.session_state.mgmt_active_tab = "總務後勤"
                st.rerun()

        with col_fin:
            st.markdown(f"### {L['card_fin_title']}")
            st.markdown(L['card_fin_desc'])
            st.markdown(L['card_fin_items'])
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(L['btn_fin'], use_container_width=True, key="btn_fin"):
                st.session_state.mgmt_active_tab = "財務會計"
                st.rerun()

    else:
        if st.button(L['btn_back'], type="secondary"):
            st.session_state.mgmt_active_tab = "總覽"
            st.rerun()

        st.markdown("---")

        active_tab = st.session_state.mgmt_active_tab
        
        if active_tab == "人事行政":
            st.subheader(L['hr_sub'])
            sub_choice = st.radio(L['select_item'], L['hr_options'], horizontal=True, label_visibility="collapsed")
            st.markdown("---")
            # 根據選擇項目對應載入模組 (支援多語系名稱判斷)
            if any(k in sub_choice for k in ["員工基本檔案", "Hồ sơ nhân viên", "Employee Profiles"]):
                from modules.employee_management import render_employee_management
                render_employee_management(engine=engine, lang=lang)
            elif any(k in sub_choice for k in ["員工打卡紀錄", "Chấm công", "Attendance"]):
                from modules.management.hr.internal_attendance import render_internal_attendance_page
                render_internal_attendance_page(engine=engine, lang=lang)
            elif any(k in sub_choice for k in ["員工薪資與保險", "Lương & Bảo hiểm", "Payroll"]):
                from modules.payroll_management import render_payroll_management_page
                render_payroll_management_page(engine=engine, lang=lang)
            elif any(k in sub_choice for k in ["密碼修改", "Đổi mật khẩu", "Password"]):
                from modules.management.hr.change_password import render_change_password_page
                render_change_password_page(engine=engine, lang=lang)

        elif active_tab == "總務後勤":
            st.subheader(L['ga_sub'])
            sub_choice = st.radio(L['select_item'], L['ga_options'], horizontal=True, label_visibility="collapsed")
            st.markdown("---")
            if any(k in sub_choice for k in ["車輛進出口", "Kiểm soát cổng xe", "Vehicle Gate"]):
                from modules.management.general_affairs.vehicle_gate_log import render_vehicle_gate_log_page
                render_vehicle_gate_log_page(engine=engine, lang=lang)
            elif any(k in sub_choice for k in ["車輛維修紀錄", "Bảo trì xe", "Maintenance"]):
                from modules.management.general_affairs.vehicle_maintenance import show
                show(engine=engine, lang=lang)
            elif any(k in sub_choice for k in ["固定資產管理", "Tài sản cố định", "Fixed Assets"]):
                from modules.management.general_affairs.asset_management import render_asset_management_page
                render_asset_management_page(engine=engine, lang=lang)
            elif any(k in sub_choice for k in ["宿舍與伙食", "Ký túc xá", "Dorm"]):
                from modules.management.dorm_catering import render_dorm_catering_module
                render_dorm_catering_module(engine=engine, lang=lang)
            elif any(k in sub_choice for k in ["廠區設施", "Bảo trì cơ sở", "Facility"]):
                from modules.management.plant_management import render_plant_management_page
                render_plant_management_page(engine=engine, lang=lang)

        elif active_tab == "財務會計":
            st.subheader(L['fin_sub'])
            sub_choice = st.radio(L['select_item'], L['fin_options'], horizontal=True, label_visibility="collapsed")
            st.markdown("---")
            if any(k in sub_choice for k in ["採購與應付帳款", "Mua sắm & Phải trả", "Procurement"]):
                from modules.procurement_ap import render_procurement_ap_page
                render_procurement_ap_page(engine=engine, lang=lang)
            elif any(k in sub_choice for k in ["應收帳款管理", "Khoản phải thu", "Accounts Receivable"]):
                from modules.sales_order_ar import render_sales_order_ar_page
                render_sales_order_ar_page(engine=engine, lang=lang)
            elif any(k in sub_choice for k in ["越南稅務報表", "Báo cáo thuế", "Tax Reports"]):
                from modules.financial_tax_reports import render_financial_tax_reports_page
                render_financial_tax_reports_page(engine=engine, lang=lang)
            elif any(k in sub_choice for k in ["電子發票管理", "Hóa đơn điện tử", "E-Invoices"]):
                from modules.invoice_management import render_invoice_management_page
                render_invoice_management_page(engine=engine, lang=lang)

def show(engine=None, lang="繁體中文", **kwargs):
    render_management_dashboard(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_management_dashboard(engine=engine, lang=lang, **kwargs)

def render_management_dashboard_module(*args, **kwargs):
    render_management_dashboard(*args, **kwargs)
