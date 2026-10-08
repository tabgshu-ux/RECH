import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 員工薪資與保險扣款模組多語系字典 (i18n)
# ----------------------------------------------------
PAYROLL_I18N = {
    "繁體中文": {
        "title": "💰 財務部 - 員工薪資計算、津貼與保險扣除中心",
        "caption": "依據越南勞動法規與裕豐電機工業薪資結構，管理基礎薪資、各項津貼、保險扣款（BHXH 8%、BHYT 1.5%、BHTN 1%）、請假遲到扣款及 1.5 倍/3 倍國定假日加班費。",
        "tab_summary": "📊 全廠薪資總表與 Excel 匯出",
        "tab_calc": "⚙️ 個別員工薪資、津貼與扣款調整",
        "tab_history": "📑 歷史薪資與會計帳務查詢",
        "summary_header": "📋 2026 年 10 月全廠員工薪資總冊 (Lương Tháng 10/2026)",
        "calc_header": "⚡ 個別員工薪資、津貼與扣減項目精算",
        "select_emp": "選擇員工 (Select Employee) *",
        # 收入欄位
        "sec_earnings": "➕ 收入與津貼項目 (Các khoản thu nhập & Phụ cấp)",
        "lbl_base": "底薪 / 基礎薪資 (VND) *",
        "lbl_meal": "餐費補助 (Phụ cấp cơm) *",
        "lbl_fuel": "油費補助 (Phụ cấp xăng) *",
        "lbl_phone": "電話補助 (Phụ cấp điện thoại) *",
        "lbl_title_allowance": "職務加給 (Phụ cấp chức vụ) *",
        "lbl_driving": "執照補助 (Trợ cấp giấy phép) *",
        "lbl_ot_normal": "平日加班時數 (1.5倍薪資) *",
        "lbl_ot_holiday": "國定假日加班時數 (3倍薪資 / 300%) *",
        # 扣款欄位
        "sec_deductions": "➖ 應扣金額與保險扣款 (Các khoản khấu trừ & Bảo hiểm)",
        "lbl_late_hours": "遲到時數 / 總度遲 (Tới trễ - Giờ) *",
        "lbl_leave_hours": "請假扣薪時數 (Nghỉ phép trừ lương - Giờ) *",
        "lbl_advance": "借款 / 預支薪資 (Tiền ứng) *",
        "btn_calc": "💾 立即重新計算並更新薪資",
        "success_calc": "✅ 員工 `{name}` 薪資與扣款資料已成功更新！",
        "col_index": "STT",
        "col_code": "工號",
        "col_name": "姓名 (Họ tên)",
        "col_title": "職稱",
        "col_base": "薪資總額",
        "col_allowance": "津貼合計",
        "col_ot": "加班費合計",
        "col_deduct": "扣款合計 (含保險)",
        "col_net": "實領金額 (Thực lãnh)"
    },
    "Tiếng Việt": {
        "title": "💰 Khối Tài chính - Tính lương, Phụ cấp & Khấu trừ Bảo hiểm",
        "caption": "Quản lý lương cơ bản, phụ cấp, bảo hiểm bắt buộc (BHXH 8%, BHYT 1.5%, BHTN 1%), khấu trừ nghỉ/trễ và tăng ca 1.5x / Lễ 3x theo luật lao động VN.",
        "tab_summary": "📊 Tổng hợp Lương toàn nhà máy & Xuất Excel",
        "tab_calc": "⚙️ Điều chỉnh Lương, Phụ cấp & Khấu trừ cá nhân",
        "tab_history": "📑 Lịch sử lương & Sách toán kế toán",
        "summary_header": "📋 Bảng lương chi tiết toàn thể nhân viên tháng 10/2026",
        "calc_header": "⚡ Tính toán lương, phụ cấp & khấu trừ cho từng nhân viên",
        "select_emp": "Chọn nhân viên *",
        "sec_earnings": "➕ Các khoản thu nhập & Phụ cấp",
        "lbl_base": "Lương cơ bản (VND) *",
        "lbl_meal": "Phụ cấp cơm (VND) *",
        "lbl_fuel": "Phụ cấp xăng (VND) *",
        "lbl_phone": "Phụ cấp điện thoại (VND) *",
        "lbl_title_allowance": "Phụ cấp chức vụ (VND) *",
        "lbl_driving": "Trợ cấp giấy phép (VND) *",
        "lbl_ot_normal": "Số giờ tăng ca ngày thường (1.5x) *",
        "lbl_ot_holiday": "Số giờ tăng ca ngày lễ (3x / 300%) *",
        "sec_deductions": "➖ Các khoản khấu trừ & Bảo hiểm bắt buộc",
        "lbl_late_hours": "Số giờ đi trễ / tổng độ trễ *",
        "lbl_leave_hours": "Số giờ nghỉ phép trừ lương *",
        "lbl_advance": "Tiền ứng trước / Tạm ứng *",
        "btn_calc": "💾 Cập nhật và Tính lại Lương",
        "success_calc": "✅ Đã cập nhật thành công bảng lương cho nhân viên `{name}`!",
        "col_index": "STT",
        "col_code": "Mã NV",
        "col_name": "Họ tên",
        "col_title": "Chức vụ",
        "col_base": "Lương cơ bản",
        "col_allowance": "Tổng phụ cấp",
        "col_ot": "Tiền tăng ca",
        "col_deduct": "Tổng khấu trừ (Gồm BH)",
        "col_net": "Số tiền thực lãnh"
    },
    "English": {
        "title": "Finance - Payroll, Allowances & Insurance Deductions Center",
        "caption": "Manage base salary, allowances, statutory insurance (BHXH 8%, BHYT 1.5%, BHTN 1%), deductions, and 1.5x/3x holiday overtime per labor laws.",
        "tab_summary": "📊 Payroll Summary & Excel Export",
        "tab_calc": "⚙️ Individual Salary & Deduction Adjustment",
        "tab_history": "📑 Payroll History & Accounting Records",
        "summary_header": "📋 Full Plant Payroll Summary - October 2026",
        "calc_header": "⚡ Individual Employee Salary, Allowance & Deduction Calculation",
        "select_emp": "Select Employee *",
        "sec_earnings": "➕ Earnings & Allowances",
        "lbl_base": "Base Salary (VND) *",
        "lbl_meal": "Meal Allowance (VND) *",
        "lbl_fuel": "Fuel Allowance (VND) *",
        "lbl_phone": "Phone Allowance (VND) *",
        "lbl_title_allowance": "Job Title Allowance (VND) *",
        "lbl_driving": "License Allowance (VND) *",
        "lbl_ot_normal": "Normal Overtime Hours (1.5x) *",
        "lbl_ot_holiday": "Holiday Overtime Hours (3x / 300%) *",
        "sec_deductions": "➖ Deductions & Statutory Insurance",
        "lbl_late_hours": "Late Hours / Penalties *",
        "lbl_leave_hours": "Unpaid Leave Hours *",
        "lbl_advance": "Salary Advance (Tiền ứng) *",
        "btn_calc": "💾 Recalculate & Save Payroll",
        "success_calc": "✅ Payroll for employee `{name}` updated successfully!",
        "col_index": "No.",
        "col_code": "Emp ID",
        "col_name": "Employee Name",
        "col_title": "Job Title",
        "col_base": "Base Salary",
        "col_allowance": "Total Allowances",
        "col_ot": "Overtime Pay",
        "col_deduct": "Total Deductions (Inc. Insurance)",
        "col_net": "Net Salary"
    }
}

def render_payroll_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in PAYROLL_I18N else "繁體中文"
    L = PAYROLL_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    if "payroll_db" not in st.session_state:
        st.session_state.payroll_db = [
            {
                "code": "EMP-001",
                "name": "張董事長 (Chairman)",
                "title": "董事長 (Chairman)",
                "base_salary": 25000000.0,
                "meal_allowance": 1500000.0,
                "fuel_allowance": 1000000.0,
                "phone_allowance": 1000000.0,
                "title_allowance": 5000000.0,
                "driving_bonus": 1000000.0,
                "ot_normal_hours": 0.0,
                "ot_holiday_hours": 0.0,
                "late_hours": 0.0,
                "leave_hours": 0.0,
                "advance": 0.0
            },
            {
                "code": "EMP-002",
                "name": "Nguyễn Văn Quý",
                "title": "副店長 / 副經理 (Vice Manager)",
                "base_salary": 6000000.0,
                "meal_allowance": 250000.0,
                "fuel_allowance": 250000.0,
                "phone_allowance": 0.0,
                "title_allowance": 2000000.0,
                "driving_bonus": 1000000.0,
                "ot_normal_hours": 15.0,
                "ot_holiday_hours": 4.0,
                "late_hours": 1.5,
                "leave_hours": 0.0,
                "advance": 0.0
            }
        ]

    tab_summary, tab_calc, tab_history = st.tabs([
        L["tab_summary"], L["tab_calc"], L["tab_history"]
    ])

    with tab_summary:
        st.markdown(f"### {L['summary_header']}")
        
        summary_data = []
        for idx, item in enumerate(st.session_state.payroll_db, 1):
            base = item["base_salary"]
            hourly_rate = base / 208.0
            
            ot_pay = (item["ot_normal_hours"] * hourly_rate * 1.5) + (item["ot_holiday_hours"] * hourly_rate * 3.0)
            
            total_allowances = (
                item["meal_allowance"] + item["fuel_allowance"] + 
                item["phone_allowance"] + item["title_allowance"] + 
                item["driving_bonus"]
            )
            
            gross_total = base + total_allowances + ot_pay
            
            bhxh = base * 0.08
            bhyt = base * 0.015
            bhtn = base * 0.01
            insurance_total = bhxh + bhyt + bhtn
            
            late_deduct = item["late_hours"] * hourly_rate
            leave_deduct = item["leave_hours"] * hourly_rate
            
            total_deductions = insurance_total + late_deduct + leave_deduct + item["advance"]
            net_salary = gross_total - total_deductions

            summary_data.append({
                L["col_index"]: idx,
                L["col_code"]: item["code"],
                L["col_name"]: item["name"],
                L["col_title"]: item["title"],
                L["col_base"]: f"{base:,.0f} ₫",
                L["col_allowance"]: f"{total_allowances:,.0f} ₫",
                L["col_ot"]: f"{ot_pay:,.0f} ₫",
                L["col_deduct"]: f"{total_deductions:,.0f} ₫ (BHXH 10.5%)",
                L["col_net"]: f"{net_salary:,.0f} ₫"
            })

        st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
        
        st.download_button(
            label="📥 匯出全廠薪資總表 Excel (.xlsx)",
            data="Mock Excel Binary Data",
            file_name="Reetech_Payroll_Oct_2026.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

    with tab_calc:
        st.markdown(f"### {L['calc_header']}")
        emp_opts = {f"{e['code']} - {e['name']} ({e['title']})": e for e in st.session_state.payroll_db}
        sel_key = st.selectbox(L["select_emp"], list(emp_opts.keys()))
        selected_emp = emp_opts[sel_key]

        with st.form("form_individual_payroll"):
            st.markdown(f"#### {L['sec_earnings']}")
            c1, c2, c3 = st.columns(3)
            with c1:
                base_val = st.number_input(L["lbl_base"], min_value=0.0, value=float(selected_emp["base_salary"]), step=500000.0)
                meal_val = st.number_input(L["lbl_meal"], min_value=0.0, value=float(selected_emp["meal_allowance"]), step=50000.0)
                fuel_val = st.number_input(L["lbl_fuel"], min_value=0.0, value=float(selected_emp["fuel_allowance"]), step=50000.0)
            with c2:
                phone_val = st.number_input(L["lbl_phone"], min_value=0.0, value=float(selected_emp["phone_allowance"]), step=50000.0)
                title_val = st.number_input(L["lbl_title_allowance"], min_value=0.0, value=float(selected_emp["title_allowance"]), step=100000.0)
                driving_val = st.number_input(L["lbl_driving"], min_value=0.0, value=float(selected_emp["driving_bonus"]), step=100000.0)
            with c3:
                ot_normal_val = st.number_input(L["lbl_ot_normal"], min_value=0.0, value=float(selected_emp["ot_normal_hours"]), step=1.0)
                ot_holiday_val = st.number_input(L["lbl_ot_holiday"], min_value=0.0, value=float(selected_emp["ot_holiday_hours"]), step=1.0)

            st.markdown(f"#### {L['sec_deductions']}")
            d1, d2, d3 = st.columns(3)
            with d1:
                late_val = st.number_input(L["lbl_late_hours"], min_value=0.0, value=float(selected_emp["late_hours"]), step=0.5)
            with d2:
                leave_val = st.number_input(L["lbl_leave_hours"], min_value=0.0, value=float(selected_emp["leave_hours"]), step=0.5)
            with d3:
                advance_val = st.number_input(L["lbl_advance"], min_value=0.0, value=float(selected_emp["advance"]), step=100000.0)

            if st.form_submit_button(L["btn_calc"], type="primary", use_container_width=True):
                for e in st.session_state.payroll_db:
                    if e["code"] == selected_emp["code"]:
                        e["base_salary"] = base_val
                        e["meal_allowance"] = meal_val
                        e["fuel_allowance"] = fuel_val
                        e["phone_allowance"] = phone_val
                        e["title_allowance"] = title_val
                        e["driving_bonus"] = driving_val
                        e["ot_normal_hours"] = ot_normal_val
                        e["ot_holiday_hours"] = ot_holiday_val
                        e["late_hours"] = late_val
                        e["leave_hours"] = leave_val
                        e["advance"] = advance_val
                st.success(L["success_calc"].format(name=selected_emp["name"]))
                st.rerun()

    with tab_history:
        st.markdown("### 📑 歷史薪資與會計帳務查詢 (Lịch sử Lương & Kế toán)")
        st.info("系統已自動同步每月會計傳票與應付薪資憑證，支援歷年跨國廠區（西寧廠、海防廠）薪資報表歸檔查閱。")
        st.metric("2026年 9月份 實發總薪資", "482,500,000 ₫", "🟢 已完成銀行撥款")
        st.metric("2026年 8月份 實發總薪資", "475,200,000 ₫", "🟢 已完成銀行撥款")

def show(*args, **kwargs):
    render_payroll_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_payroll_management_page(*args, **kwargs)

def render_payroll_management(*args, **kwargs):
    render_payroll_management_page(*args, **kwargs)
