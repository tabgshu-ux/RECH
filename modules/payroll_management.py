import datetime
import io
import pandas as pd
from sqlalchemy import text
import streamlit as st

# ----------------------------------------------------
# 🌐 薪資與保險模組多語系字典 (i18n)
# ----------------------------------------------------
PAYROLL_I18N = {
    "繁體中文": {
        "title": "💰 財務部 - 員工薪資與保險扣款試算中心",
        "caption": "提供各廠區員工薪資結構、越南法定保險、加班費、假日 3 倍薪與考勤扣款結算。",
        "tab_list": "📊 全廠區本月薪資總表與 Excel 匯出",
        "tab_calc": "🧮 單一員工薪資與加班試算",
        "tab_attendance": "📱 出勤打卡與加班記錄總結",
        "tab_history": "📜 歷史發薪紀錄與傳票拋轉",
        "select_month": "選擇薪資結算月份",
        "select_emp": "請選擇欲試算的員工：",
        "base_salary": "基本底薪 (Lương cơ bản)",
        "meal_allowance": "餐費補助 (Phụ cấp cơm)",
        "fuel_allowance": "油費補助 (Phụ cấp xăng)",
        "phone_allowance": "電話補助 (Phụ cấp điện thoại)",
        "position_allowance": "職務加給 (Tiền chức vụ)",
        "license_allowance": "執照/牌照加給 (Phụ cấp giấy phép)",
        "tips": "小費 / 獎金 (Tiền tips)",
        "loan_deduction": "本月借款預支 (Tiền ứng)",
        "tardiness_mins": "遲到分鐘數",
        "leave_days": "請假天數",
        "ot_normal_hours": "平日加班時數 (1.5x)",
        "holiday_work_days": "國定假日出勤天數 (3x)",
        "print_btn": "列印正式薪資單",
        "approve_btn": "確認核准並拋轉會計傳票",
        "export_excel_btn": "下載標準薪資總表 (Excel)",
        "payslip_title": "裕豐電機工業 (Reetech Industrial) - 正式薪資結算明細單",
        "base_standard": "1. 薪資換算基準",
        "work_days_label": "標準工作天數",
        "daily_wage": "日薪",
        "hourly_wage": "時薪",
        "minute_wage": "每分鐘薪資",
        "due_title": "2. 應付金額 (Số tiền đến hạn)",
        "ded_title": "3. 應扣金額 (Số tiền khấu trừ)",
        "total_due": "應付金額總合計 (Total Due)",
        "social_ins": "社會保險 (BHXH 8%)",
        "health_ins": "醫療保險 (BHYT 1.5%)",
        "unemploy_ins": "失業險 (BHTN 1%)",
        "leave_ded": "請假扣款",
        "tard_ded": "遲到扣款",
        "total_deduct": "應扣金額合計 (Total Deduct)",
        "net_pay": "本月實領金額 (Số tiền thực lãnh)"
    },
    "Tiếng Việt": {
        "title": "💰 Bộ phận Tài chính - Trung tâm Tính lương & Khấu trừ Bảo hiểm",
        "caption": "Quản lý lương, bảo hiểm xã hội, tăng ca, lương lễ 300% và khấu trừ chấm công.",
        "tab_list": "📊 Bảng lương toàn nhà máy & Xuất Excel",
        "tab_calc": "🧮 Tính lương & Tăng ca từng nhân viên",
        "tab_attendance": "📱 Tổng kết chấm công & Tăng ca",
        "tab_history": "📜 Lịch sử bảng lương & Kế toán",
        "select_month": "Chọn tháng quyết toán lương",
        "select_emp": "Chọn nhân viên tính lương:",
        "base_salary": "Lương cơ bản",
        "meal_allowance": "Phụ cấp tiền cơm",
        "fuel_allowance": "Phụ cấp tiền xăng",
        "phone_allowance": "Phụ cấp điện thoại",
        "position_allowance": "Tiền chức vụ",
        "license_allowance": "Phụ cấp giấy phép",
        "tips": "Tiền tips / Thưởng",
        "loan_deduction": "Tiền ứng / Tạm ứng",
        "tardiness_mins": "Số phút đi trễ",
        "leave_days": "Số ngày nghỉ phép",
        "ot_normal_hours": "Giờ tăng ca ngày thường (1.5x)",
        "holiday_work_days": "Ngày làm việc lễ tết (3x)",
        "print_btn": "In phiếu lương chính thức",
        "approve_btn": "Xác nhận duyệt & Ghi sổ kế toán",
        "export_excel_btn": "Tải xuống bảng lương chuẩn (Excel)",
        "payslip_title": "Công ty TNHH Cơ điện Reetech - Phiếu lương chính thức",
        "base_standard": "1. Đơn giá lương quy đổi",
        "work_days_label": "Ngày làm việc chuẩn",
        "daily_wage": "Lương ngày",
        "hourly_wage": "Lương giờ",
        "minute_wage": "Lương phút",
        "due_title": "2. Các khoản thu nhập (Số tiền đến hạn)",
        "ded_title": "3. Các khoản khấu trừ (Số tiền khấu trừ)",
        "total_due": "Tổng thu nhập (Total Due)",
        "social_ins": "Bảo hiểm xã hội (BHXH 8%)",
        "health_ins": "Bảo hiểm y tế (BHYT 1.5%)",
        "unemploy_ins": "Bảo hiểm thất nghiệp (BHTN 1%)",
        "leave_ded": "Khấu trừ nghỉ phép",
        "tard_ded": "Khấu trừ đi trễ",
        "total_deduct": "Tổng khấu trừ (Total Deduct)",
        "net_pay": "Số tiền thực lãnh (Số tiền thực lãnh)"
    },
    "English": {
        "title": "💰 Finance Dept - Employee Payroll & Insurance Calculation Center",
        "caption": "Plant-wide payroll management, statutory insurance, overtime, and holiday pay calculation.",
        "tab_list": "📊 Plant-wide Payroll Summary & Excel Export",
        "tab_calc": "🧮 Individual Payroll & Overtime Calculator",
        "tab_attendance": "📱 Attendance & Overtime Summary",
        "tab_history": "📜 Payroll History & Accounting",
        "select_month": "Select Payroll Settlement Month",
        "select_emp": "Select Employee:",
        "base_salary": "Base Salary",
        "meal_allowance": "Meal Allowance",
        "fuel_allowance": "Fuel Allowance",
        "phone_allowance": "Phone Allowance",
        "position_allowance": "Position Allowance",
        "license_allowance": "License Allowance",
        "tips": "Tips / Bonus",
        "loan_deduction": "Advance / Loan Deduction",
        "tardiness_mins": "Tardiness Minutes",
        "leave_days": "Leave Days",
        "ot_normal_hours": "Overtime Hours (1.5x)",
        "holiday_work_days": "Holiday Work Days (3x)",
        "print_btn": "Print Official Payslip",
        "approve_btn": "Approve & Post to Accounting",
        "export_excel_btn": "Download Standard Payroll Summary (Excel)",
        "payslip_title": "Reetech Industrial - Official Payslip",
        "base_standard": "1. Wage Conversion Base",
        "work_days_label": "Standard Work Days",
        "daily_wage": "Daily Wage",
        "hourly_wage": "Hourly Wage",
        "minute_wage": "Minute Wage",
        "due_title": "2. Earnings (Số tiền đến hạn)",
        "ded_title": "3. Deductions (Số tiền khấu trừ)",
        "total_due": "Total Earnings (Total Due)",
        "social_ins": "Social Insurance (BHXH 8%)",
        "health_ins": "Health Insurance (BHYT 1.5%)",
        "unemploy_ins": "Unemployment Ins (BHTN 1%)",
        "leave_ded": "Leave Deduction",
        "tard_ded": "Tardiness Deduction",
        "total_deduct": "Total Deductions (Total Deduct)",
        "net_pay": "Net Payable (Số tiền thực lãnh)"
    }
}

def get_payroll_lang_dict(lang_param):
    # 💡 自動優先採用傳入的語系參數，若無則抓取 session_state
    current_lang = lang_param or st.session_state.get("lang", "繁體中文")
    return PAYROLL_I18N.get(current_lang, PAYROLL_I18N["繁體中文"])

# ----------------------------------------------------
# 📊 匯出完整 Excel 輔助函式
# ----------------------------------------------------
def convert_payroll_to_excel(summary_data):
    output = io.BytesIO()
    df_export = pd.DataFrame(summary_data)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Reetech_Payroll_2026', index=False)
    return output.getvalue()


def render_payroll_management_page(engine=None, lang="繁體中文"):
    # 💡 強制綁定全域語系
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = get_payroll_lang_dict(active_lang)

    st.title(L["title"])
    st.caption(L["caption"])

    tab_list, tab_calc, tab_attendance, tab_history = st.tabs([
        L["tab_list"],
        L["tab_calc"],
        L["tab_attendance"],
        L["tab_history"]
    ])

    if "employees_db" in st.session_state and st.session_state.employees_db:
        emp_list = st.session_state.employees_db
    else:
        emp_list = [
            {
                "id": "EMP-001", "name": "張董事長", "site": "🇹🇼 台灣總部 (Taiwan HQ)", 
                "dept": "管理部", "title": "董事長 (Chairman)", "join_date": "2020-01-15", "base_salary": 80000.0, 
                "tardiness_mins": 0, "leave_days": 0, "ot_normal_hours": 0, "holiday_work_days": 0
            },
            {
                "id": "EMP-002", "name": "Nguyễn Văn A", "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)", 
                "dept": "工程部", "title": "高級機電工程師 (Senior M&E Engineer)", "join_date": "2023-05-10", "base_salary": 15000000.0, 
                "tardiness_mins": 10, "leave_days": 0, "ot_normal_hours": 15, "holiday_work_days": 1
            },
            {
                "id": "EMP-003", "name": "陳智賢", "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)", 
                "dept": "工程部", "title": "配電盤組裝技師 (Panel Assembly Technician)", "join_date": "2022-03-01", "base_salary": 9000000.0, 
                "tardiness_mins": 0, "leave_days": 1, "ot_normal_hours": 22, "holiday_work_days": 2
            }
        ]

    # ----------------------------------------------------
    # 📊 頁籤一：全廠區員工薪資總表與 Excel 匯出
    # ----------------------------------------------------
    with tab_list:
        st.markdown(f"### {L['tab_list']}")

        summary_rows = []
        for emp in emp_list:
            base = emp.get("base_salary", 9000000.0)
            work_days = 26.0
            
            daily_wage = base / work_days
            hourly_wage = daily_wage / 8.0
            minute_wage = hourly_wage / 60.0

            tardiness_mins = emp.get("tardiness_mins", 0)
            leave_days = emp.get("leave_days", 0)
            ot_normal_hours = emp.get("ot_normal_hours", 10.0)
            holiday_work_days = emp.get("holiday_work_days", 1.0)

            tardiness_deduction = tardiness_mins * minute_wage
            leave_deduction = leave_days * daily_wage
            overtime_pay = ot_normal_hours * hourly_wage * 1.5
            holiday_pay = holiday_work_days * daily_wage * 3.0

            bhxh = base * 0.08
            bhyt = base * 0.015
            bhtn = base * 0.01

            meal = 250000.0
            fuel = 250000.0
            phone = 200000.0
            position_bonus = 1000000.0
            license_bonus = 1000000.0
            tips = 0.0

            total_due = base + meal + fuel + phone + overtime_pay + holiday_pay + position_bonus + license_bonus + tips
            total_deduct = (bhxh + bhyt + bhtn) + leave_deduction + tardiness_deduction
            net_pay = total_due - total_deduct

            summary_rows.append({
                "工號": emp['id'],
                "姓名": emp['name'],
                "部門": emp['dept'],
                "職稱": emp['title'],
                "廠區": emp['site'],
                "薪資總額(底薪)": base,
                "請假天數": leave_days,
                "遲到分鐘": tardiness_mins,
                "平日加班(1.5x)": ot_normal_hours,
                "國定假日(3x)": holiday_work_days,
                "應付金額合計": round(total_due, 2),
                "應扣金額合計": round(total_deduct, 2),
                "本月實發淨額": round(net_pay, 2)
            })

        df_summary = pd.DataFrame(summary_rows)
        st.dataframe(df_summary, use_container_width=True)

        st.markdown("---")
        excel_data = convert_payroll_to_excel(summary_rows)
        st.download_button(
            label=L["export_excel_btn"],
            data=excel_data,
            file_name=f"Reetech_Payroll_Standard_{datetime.date.today().strftime('%Y%m')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+sheet",
            type="primary",
            key="download_std_excel"
        )

    # ----------------------------------------------------
    # 🧮 頁籤二：單一員工詳細薪資與加班、假日 3 倍薪試算
    # ----------------------------------------------------
    with tab_calc:
        st.markdown(f"### {L['tab_calc']}")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            pay_month = st.date_input(L["select_month"], value=datetime.date.today(), key="payroll_month_std")
        with col_m2:
            emp_opts = {f"{emp['id']} - {emp['name']} ({emp['dept']})": emp for emp in emp_list}
            selected_emp_label = st.selectbox(L["select_emp"], list(emp_opts.keys()), key="sel_emp_std")
            selected_emp = emp_opts[selected_emp_label]

        st.divider()

        emp = selected_emp
        emp_id = emp['id']
        emp_site = emp.get("site", "🇻🇳 越南西寧廠")

        st.markdown(f"#### 員工姓名: **{emp['name']}** (`{emp_id}`) | 部門: {emp['dept']} | 職稱: {emp['title']}")
        st.caption(f"工作廠區: {emp_site} | 到職日: {emp.get('join_date', '2024-01-01')}")

        c1, c2, c3 = st.columns(3)
        with c1:
            default_base = float(emp.get("base_salary", 9000000.0))
            base_salary = st.number_input(L["base_salary"], value=default_base, step=100000.0, key=f"base_{emp_id}")
        with c2:
            meal_allowance = st.number_input(L["meal_allowance"], value=250000.0, step=50000.0, key=f"meal_{emp_id}")
        with c3:
            fuel_allowance = st.number_input(L["fuel_allowance"], value=250000.0, step=50000.0, key=f"fuel_{emp_id}")

        c4, c5, c6 = st.columns(3)
        with c4:
            position_allowance = st.number_input(L["position_allowance"], value=1000000.0, step=100000.0, key=f"pos_{emp_id}")
        with c5:
            license_allowance = st.number_input(L["license_allowance"], value=1000000.0, step=100000.0, key=f"lic_{emp_id}")
        with c6:
            tips = st.number_input(L["tips"], value=0.0, step=50000.0, key=f"tips_{emp_id}")

        st.markdown("---")
        
        col_att1, col_att2, col_att3, col_att4 = st.columns(4)
        with col_att1:
            tardiness_mins = st.number_input(L["tardiness_mins"], min_value=0.0, value=float(emp.get("tardiness_mins", 0)), step=1.0, key=f"tard_{emp_id}")
        with col_att2:
            leave_days = st.number_input(L["leave_days"], min_value=0.0, value=float(emp.get("leave_days", 0)), step=0.5, key=f"leave_{emp_id}")
        with col_att3:
            ot_normal_hours = st.number_input(L["ot_normal_hours"], min_value=0.0, value=float(emp.get("ot_normal_hours", 10.0)), step=1.0, key=f"ot_{emp_id}")
        with col_att4:
            holiday_work_days = st.number_input(L["holiday_work_days"], min_value=0.0, value=float(emp.get("holiday_work_days", 1.0)), step=0.5, key=f"hol_{emp_id}")

        loan_deduction = st.number_input(L["loan_deduction"], min_value=0.0, value=0.0, step=100000.0, key=f"loan_{emp_id}")

        work_days = 26.0
        daily_wage = base_salary / work_days
        hourly_wage = daily_wage / 8.0
        minute_wage = hourly_wage / 60.0

        overtime_pay = ot_normal_hours * hourly_wage * 1.5
        holiday_pay = holiday_work_days * daily_wage * 3.0

        tardiness_deduction = tardiness_mins * minute_wage
        leave_deduction = leave_days * daily_wage

        bhxh = base_salary * 0.08
        bhyt = base_salary * 0.015
        bhtn = base_salary * 0.01

        total_due = base_salary + meal_allowance + fuel_allowance + position_allowance + license_allowance + overtime_pay + holiday_pay + tips
        total_deduct = bhxh + bhyt + bhtn + leave_deduction + tardiness_deduction + loan_deduction
        net_payable = total_due - total_deduct

        st.markdown("---")
        st.markdown(f"### {L['payslip_title']}")
        st.markdown(f"**結算月份 / Tháng**: {pay_month.strftime('%Y年%m月')} | **工號 / Mã NV**: {emp_id} | **姓名 / Họ tên**: {emp['name']} | **部門 / Bộ phận**: {emp['dept']}")

        st.markdown(f"#### {L['base_standard']}")
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        with col_b1: st.markdown(f"{L['work_days_label']}: `{work_days}`")
        with col_b2: st.markdown(f"{L['daily_wage']}: `{daily_wage:,.2f} ₫`")
        with col_b3: st.markdown(f"{L['hourly_wage']}: `{hourly_wage:,.2f} ₫`")
        with col_b4: st.markdown(f"{L['minute_wage']}: `{minute_wage:,.2f} ₫`")

        st.markdown("---")
        # 左右雙欄並排對照
        col_due, col_ded = st.columns(2)

        with col_due:
            st.markdown(f"#### {L['due_title']}")
            st.markdown(f"- {L['base_salary']}: `{base_salary:,.2f} ₫`")
            st.markdown(f"- {L['meal_allowance']}: `{meal_allowance:,.2f} ₫`")
            st.markdown(f"- {L['fuel_allowance']}: `{fuel_allowance:,.2f} ₫`")
            st.markdown(f"- {L['position_allowance']}: `{position_allowance:,.2f} ₫`")
            st.markdown(f"- {L['license_allowance']}: `{license_allowance:,.2f} ₫`")
            st.markdown(f"- {L['ot_normal_hours']} (`{ot_normal_hours}`h): `{overtime_pay:,.2f} ₫`")
            st.markdown(f"- {L['holiday_work_days']} (`{holiday_work_days}`d @ 300%): `{holiday_pay:,.2f} ₫`")
            st.markdown(f"- {L['tips']}: `{tips:,.2f} ₫`")
            st.markdown(f"**{L['total_due']}: `{total_due:,.2f} ₫`**")

        with col_ded:
            st.markdown(f"#### {L['ded_title']}")
            st.markdown(f"- {L['social_ins']}: `- {bhxh:,.2f} ₫`")
            st.markdown(f"- {L['health_ins']}: `- {bhyt:,.2f} ₫`")
            st.markdown(f"- {L['unemploy_ins']}: `- {bhtn:,.2f} ₫`")
            st.markdown(f"- {L['leave_ded']} (`{leave_days}`d): `- {leave_deduction:,.2f} ₫`")
            st.markdown(f"- {L['tard_ded']} (`{tardiness_mins}`m): `- {tardiness_deduction:,.2f} ₫`")
            st.markdown(f"- {L['loan_deduction']}: `- {loan_deduction:,.2f} ₫`")
            st.markdown("")
            st.markdown("")
            st.markdown(f"**{L['total_deduct']}: `{total_deduct:,.2f} ₫`**")

        st.markdown("---")
        st.markdown(f"### 💰 {L['net_pay']}: `{net_payable:,.2f} VND`")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(L["print_btn"], key=f"print_std_{emp_id}"):
                st.success("✅")
        with col_btn2:
            if st.button(L["approve_btn"], type="primary", key=f"approve_std_{emp_id}"):
                st.success("✅")

    # ----------------------------------------------------
    # 📱 頁籤三：出勤打卡與請假記錄
    # ----------------------------------------------------
    with tab_attendance:
        st.markdown(f"### {L['tab_attendance']}")
        
        att_data = [
            {"工號": "EMP-001", "姓名": "張董事長", "部門": "管理部", "出勤天數": 26, "請假天數": 0, "遲到分鐘": 0, "平日加班(時)": 0, "國定假日出勤(天)": 0},
            {"工號": "EMP-002", "姓名": "Nguyễn Văn A", "部門": "工程部", "出勤天數": 26, "請假天數": 0, "遲到分鐘": 10, "平日加班(時)": 15, "國定假日出勤(天)": 1},
            {"工號": "EMP-003", "姓名": "陳智賢", "部門": "工程部", "出勤天數": 25, "請假天數": 1, "遲到分鐘": 0, "平日加班(時)": 22, "國定假日出勤(天)": 2}
        ]
        st.dataframe(pd.DataFrame(att_data), use_container_width=True)

    # ----------------------------------------------------
    # 📜 頁籤四：歷史發薪紀錄
    # ----------------------------------------------------
    with tab_history:
        st.markdown(f"### {L['tab_history']}")
        st.info("OK")


def show(engine=None, lang="繁體中文"):
    render_payroll_management_page(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_payroll_management_page(engine, lang)
