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
        "base_salary": "基本底薪 (Lương cơ bản)",
        "meal_allowance": "餐費補助 (Phụ cấp cơm)",
        "fuel_allowance": "油費補助 (Phụ cấp xăng)",
        "phone_allowance": "電話補助 (Phụ cấp điện thoại)",
        "position_allowance": "職務加給 (Tiền chức vụ)",
        "license_allowance": "執照/牌照加給 (Phụ cấp giấy phép)",
        "tips": "小費 / 獎金 (Tiền tips)",
        "loan_deduction": "本月借款預支 (Tiền ứng)",
        "print_btn": "列印正式薪資單",
        "approve_btn": "確認核准並拋轉會計傳票",
        "export_excel_btn": "下載標準薪資總表 (Excel)",
    },
    "Tiếng Việt": {
        "title": "💰 Bộ phận Tài chính - Trung tâm Tính lương & Khấu trừ Bảo hiểm",
        "caption": "Quản lý lương, bảo hiểm xã hội, tăng ca, lương lễ 300% và khấu trừ chấm công.",
        "tab_list": "📊 Bảng lương toàn nhà máy & Xuất Excel",
        "tab_calc": "🧮 Tính lương & Tăng ca từng nhân viên",
        "tab_attendance": "📱 Tổng kết chấm công & Tăng ca",
        "tab_history": "📜 Lịch sử bảng lương & Kế toán",
        "select_month": "Chọn tháng quyết toán lương",
        "base_salary": "Lương cơ bản",
        "meal_allowance": "Phụ cấp tiền cơm",
        "fuel_allowance": "Phụ cấp tiền xăng",
        "phone_allowance": "Phụ cấp điện thoại",
        "position_allowance": "Tiền chức vụ",
        "license_allowance": "Phụ cấp giấy phép",
        "tips": "Tiền tips / Thưởng",
        "loan_deduction": "Tiền ứng / Tạm ứng",
        "print_btn": "In phiếu lương chính thức",
        "approve_btn": "Xác nhận duyệt & Ghi sổ kế toán",
        "export_excel_btn": "Tải xuống bảng lương chuẩn (Excel)",
    },
    "English": {
        "title": "💰 Finance Dept - Employee Payroll & Insurance Calculation Center",
        "caption": "Plant-wide payroll management, statutory insurance, overtime, and holiday pay calculation.",
        "tab_list": "📊 Plant-wide Payroll Summary & Excel Export",
        "tab_calc": "🧮 Individual Payroll & Overtime Calculator",
        "tab_attendance": "📱 Attendance & Overtime Summary",
        "tab_history": "📜 Payroll History & Accounting",
        "select_month": "Select Payroll Settlement Month",
        "base_salary": "Base Salary",
        "meal_allowance": "Meal Allowance",
        "fuel_allowance": "Fuel Allowance",
        "phone_allowance": "Phone Allowance",
        "position_allowance": "Position Allowance",
        "license_allowance": "License Allowance",
        "tips": "Tips / Bonus",
        "loan_deduction": "Advance / Loan Deduction",
        "print_btn": "Print Official Payslip",
        "approve_btn": "Approve & Post to Accounting",
        "export_excel_btn": "Download Standard Payroll Summary (Excel)",
    }
}

def get_payroll_lang_dict(lang_param):
    lang = lang_param or st.session_state.get("lang", "繁體中文")
    return PAYROLL_I18N.get(lang, PAYROLL_I18N["繁體中文"])

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
    L = get_payroll_lang_dict(lang)

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
        st.markdown("### 全廠區員工本月薪資總表")

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
            total_insurance = bhxh + bhyt + bhtn

            meal = 250000.0
            fuel = 250000.0
            phone = 200000.0
            position_bonus = 1000000.0
            license_bonus = 1000000.0
            tips = 0.0

            total_due = base + meal + fuel + phone + overtime_pay + holiday_pay + position_bonus + license_bonus + tips
            total_deduct = total_insurance + leave_deduction + tardiness_deduction + 0.0
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
                "餐費補助": meal,
                "油費補助": fuel,
                "加班費": round(overtime_pay, 2),
                "國定假日3倍薪": round(holiday_pay, 2),
                "職務加給": position_bonus,
                "證照加給": license_bonus,
                "應付金額合計": round(total_due, 2),
                "社會保險(8%)": bhxh,
                "醫療保險(1.5%)": bhyt,
                "失業保險(1%)": bhtn,
                "請假扣款": round(leave_deduction, 2),
                "遲到扣款": round(tardiness_deduction, 2),
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
        st.markdown("### 單一員工薪資與加班試算")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            pay_month = st.date_input(L["select_month"], value=datetime.date.today(), key="payroll_month_std")
        with col_m2:
            emp_opts = {f"{emp['id']} - {emp['name']} ({emp['dept']})": emp for emp in emp_list}
            selected_emp_label = st.selectbox("請選擇欲試算的員工：", list(emp_opts.keys()), key="sel_emp_std")
            selected_emp = emp_opts[selected_emp_label]

        st.divider()

        emp = selected_emp
        emp_id = emp['id']
        emp_site = emp.get("site", "🇻🇳 越南西寧廠")

        st.markdown(f"#### 員工姓名: **{emp['name']}** (`{emp_id}`) | 部門: {emp['dept']} | 職稱: {emp['title']}")
        st.caption(f"工作廠區: {emp_site} | 到職日: {emp.get('join_date', '2024-01-01')}")

        c1, c2, c3 = st.columns(3)
        with c1:
            base_salary = st.number_input(L["base_salary"], value=float(emp.get("base_salary", 9000000.0)), step=100000.0, key=f"base_{emp_id}")
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
            tardiness_mins = st.number_input("遲到分鐘數", min_value=0.0, value=float(emp.get("tardiness_mins", 0)), step=1.0, key=f"tard_{emp_id}")
        with col_att2:
            leave_days = st.number_input("請假天數", min_value=0.0, value=float(emp.get("leave_days", 0)), step=0.5, key=f"leave_{emp_id}")
        with col_att3:
            ot_normal_hours = st.number_input("平日加班時數 (1.5x)", min_value=0.0, value=float(emp.get("ot_normal_hours", 10.0)), step=1.0, key=f"ot_{emp_id}")
        with col_att4:
            holiday_work_days = st.number_input("國定假日出勤天數 (3x)", min_value=0.0, value=float(emp.get("holiday_work_days", 1.0)), step=0.5, key=f"hol_{emp_id}")

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
        total_insurance = bhxh + bhyt + bhtn

        total_due = base_salary + meal_allowance + fuel_allowance + position_allowance + license_allowance + overtime_pay + holiday_pay + tips
        total_deduct = total_insurance + leave_deduction + tardiness_deduction + loan_deduction
        net_payable = total_due - total_deduct

        st.markdown("---")
        st.markdown(f"### 裕豐電機工業 (Reetech Industrial) - 正式薪資結算明細單")
        st.markdown(f"**結算月份**: {pay_month.strftime('%Y年%m月')} | **工號**: {emp_id} | **姓名**: {emp['name']} | **部門**: {emp['dept']}")

        st.markdown("#### 1. 薪資換算基準")
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        with col_b1: st.markdown(f"標準工作天數: `{work_days}` 天")
        with col_b2: st.markdown(f"日薪: `{daily_wage:,.2f} ₫`")
        with col_b3: st.markdown(f"時薪: `{hourly_wage:,.2f} ₫`")
        with col_b4: st.markdown(f"每分鐘薪資: `{minute_wage:,.2f} ₫`")

        st.markdown("---")
        # 💡 仿照圖片二：左右雙欄並排顯示「應付金額」與「應扣金額」
        col_due, col_ded = st.columns(2)

        with col_due:
            st.markdown("#### 2. 應付金額 (Số tiền đến hạn)")
            st.markdown(f"- 薪資總額 / 底薪: `{base_salary:,.2f} ₫`")
            st.markdown(f"- 餐費補助: `{meal_allowance:,.2f} ₫`")
            st.markdown(f"- 油費補助: `{fuel_allowance:,.2f} ₫`")
            st.markdown(f"- 職務加給: `{position_allowance:,.2f} ₫`")
            st.markdown(f"- 執照加給: `{license_allowance:,.2f} ₫`")
            st.markdown(f"- 平日加班費 (`{ot_normal_hours}` 小時 @ 1.5x): `{overtime_pay:,.2f} ₫`")
            st.markdown(f"- 國定假日 3 倍薪 (`{holiday_work_days}` 天 @ 300%): `{holiday_pay:,.2f} ₫`")
            st.markdown(f"- 小費/獎金: `{tips:,.2f} ₫`")
            st.markdown(f"**應付金額總合計 (Total Due): `{total_due:,.2f} ₫`**")

        with col_ded:
            st.markdown("#### 3. 應扣金額 (Số tiền khấu trừ)")
            st.markdown(f"- 社會保險 (BHXH 8%): `- {bhxh:,.2f} ₫`")
            st.markdown(f"- 醫療保險 (BHYT 1.5%): `- {bhyt:,.2f} ₫`")
            st.markdown(f"- 失業險 (BHTN 1%): `- {bhtn:,.2f} ₫`")
            st.markdown(f"- 請假扣款 (`{leave_days}` 天): `- {leave_deduction:,.2f} ₫`")
            st.markdown(f"- 遲到扣款 (`{tardiness_mins}` 分鐘): `- {tardiness_deduction:,.2f} ₫`")
            st.markdown(f"- 預支借款 (Tiền ứng): `- {loan_deduction:,.2f} ₫`")
            st.markdown("")
            st.markdown("")
            st.markdown(f"**應扣金額合計 (Total Deduct): `{total_deduct:,.2f} ₫`**")

        st.markdown("---")
        st.markdown(f"### 💰 本月實領金額 (Số tiền thực lãnh): `{net_payable:,.2f} VND`")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(L["print_btn"], key=f"print_std_{emp_id}"):
                st.success(f"已成功產生 {emp['name']} 的正式薪資單。")
        with col_btn2:
            if st.button(L["approve_btn"], type="primary", key=f"approve_std_{emp_id}"):
                st.success(f"已成功核准 {emp['name']} 本月薪資並拋轉會計總帳傳票！")

    # ----------------------------------------------------
    # 📱 頁籤三：出勤打卡與請假記錄
    # ----------------------------------------------------
    with tab_attendance:
        st.markdown("### 出勤打卡與加班記錄總結")
        
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
        st.markdown("### 歷史發薪紀錄與傳票拋轉")
        st.info("歷月份薪資發放憑證與會計傳票拋轉記錄運作中。")


def show(engine=None, lang="繁體中文"):
    render_payroll_management_page(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_payroll_management_page(engine, lang)
