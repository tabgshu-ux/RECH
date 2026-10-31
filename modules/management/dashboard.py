import streamlit as st

def render_management_dashboard(engine=None, lang="繁體中文", **kwargs):
    st.title("👔 管理部綜合導航中心")
    st.caption("管理公司人事行政、總務後勤與財務會計等核心作業。請點擊下方卡片快速進入對應管理專區。")
    st.markdown("---")

    # 初始化管理部內部導航狀態
    if "mgmt_active_tab" not in st.session_state:
        st.session_state.mgmt_active_tab = "總覽"

    # 若目前在總覽頁，顯示三大精美卡片
    if st.session_state.mgmt_active_tab == "總覽":
        col_hr, col_ga, col_fin = st.columns(3)

        # 1. 人事行政區
        with col_hr:
            st.markdown("### 👤 人事行政區")
            st.markdown("掌握員工名冊、出勤、薪資與保險。")
            st.markdown("- 📋 員工基本檔案\n- ⏱️ 員工打卡紀錄\n- 💳 員工薪資與保險\n- 🔑 密碼變更設定")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 進入人事行政中心", use_container_width=True, key="btn_hr"):
                st.session_state.mgmt_active_tab = "人事行政"
                st.rerun()

        # 2. 總務後勤區
        with col_ga:
            st.markdown("### 📦 總務後勤區")
            st.markdown("廠區車輛、門禁安防、固定資產與食宿。")
            st.markdown("- 🚗 車輛進出口與門禁\n- 🔧 車輛維修紀錄\n- 🏢 固定資產管理\n- 🍲 宿舍與伙食管理\n- 🌿 廠區設施維護")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 進入總務後勤中心", use_container_width=True, key="btn_ga"):
                st.session_state.mgmt_active_tab = "總務後勤"
                st.rerun()

        # 3. 財務會計區
        with col_fin:
            st.markdown("### 💰 財務會計區")
            st.markdown("採購應付、應收帳款與越南稅務合規。")
            st.markdown("- 🛒 採購與應付帳款 (AP)\n- 📊 應收帳款管理 (AR)\n- 📑 越南稅務與報表\n- 🧾 電子發票管理")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 進入財務會計中心", use_container_width=True, key="btn_fin"):
                st.session_state.mgmt_active_tab = "財務會計"
                st.rerun()

    else:
        # 進入子專區後，上方提供漂亮的返回總覽按鈕與分頁切換
        col_back, col_tabs = [st.col(1), st.col(4)] if hasattr(st, "col") else st.columns([1, 4])
        with col_back:
            if st.button("⬅️ 返回總覽卡片", type="secondary"):
                st.session_state.mgmt_active_tab = "總覽"
                st.rerun()

        st.markdown("---")

        # 根據不同的子專區渲染對應的功能
        active_tab = st.session_state.mgmt_active_tab
        
        if active_tab == "人事行政":
            st.subheader("👥 人事行政作業專區")
            sub_choice = st.radio("選擇作業項目", ["員工基本檔案", "員工打卡紀錄", "員工薪資與保險", "密碼修改"], horizontal=True)
            st.markdown("---")
            if "員工基本檔案" in sub_choice:
                from modules.employee_management import render_employee_management
                render_employee_management(engine=engine, lang=lang)
            elif "員工打卡紀錄" in sub_choice:
                from modules.management.hr.internal_attendance import render_internal_attendance_page
                render_internal_attendance_page(engine=engine, lang=lang)
            elif "員工薪資與保險" in sub_choice:
                from modules.payroll_management import render_payroll_management_page
                render_payroll_management_page(engine=engine, lang=lang)
            elif "密碼修改" in sub_choice:
                from modules.management.hr.change_password import render_change_password_page
                render_change_password_page(engine=engine, lang=lang)

        elif active_tab == "總務後勤":
            st.subheader("📦 總務後勤作業專區")
            sub_choice = st.radio("選擇作業項目", ["車輛進出口與門禁", "車輛維修紀錄", "固定資產管理", "宿舍與伙食管理", "廠區設施維護"], horizontal=True)
            st.markdown("---")
            if "車輛進出口" in sub_choice:
                from modules.management.general_affairs.vehicle_gate_log import render_vehicle_gate_log_page
                render_vehicle_gate_log_page(engine=engine, lang=lang)
            elif "車輛維修紀錄" in sub_choice:
                from modules.management.general_affairs.vehicle_maintenance import show
                show(engine=engine, lang=lang)
            elif "固定資產管理" in sub_choice:
                from modules.management.general_affairs.asset_management import render_asset_management_page
                render_asset_management_page(engine=engine, lang=lang)
            elif "宿舍與伙食" in sub_choice:
                from modules.management.dorm_catering import render_dorm_catering_module
                render_dorm_catering_module(engine=engine, lang=lang)
            elif "廠區設施" in sub_choice:
                from modules.management.plant_management import render_plant_management_page
                render_plant_management_page(engine=engine, lang=lang)

        elif active_tab == "財務會計":
            st.subheader("💰 財務會計作業專區")
            sub_choice = st.radio("選擇作業項目", ["採購與應付帳款", "應收帳款管理", "越南稅務報表", "電子發票管理"], horizontal=True)
            st.markdown("---")
            if "採購與應付帳款" in sub_choice:
                from modules.procurement_ap import render_procurement_ap_page
                render_procurement_ap_page(engine=engine, lang=lang)
            elif "應收帳款管理" in sub_choice:
                from modules.sales_order_ar import render_sales_order_ar_page
                render_sales_order_ar_page(engine=engine, lang=lang)
            elif "越南稅務報表" in sub_choice:
                from modules.financial_tax_reports import render_financial_tax_reports_page
                render_financial_tax_reports_page(engine=engine, lang=lang)
            elif "電子發票管理" in sub_choice:
                from modules.invoice_management import render_invoice_management_page
                render_invoice_management_page(engine=engine, lang=lang)
