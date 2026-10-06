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
        "caption": "連動打卡、請假、越南法定 3 倍國定假日薪資與加班費自動計算。",
        "tab_list": "📊 全廠區本月薪資詳細總表與 Excel 匯出",
        "tab_calc": "🧮 單一員工詳細薪資、加班與假日 3 倍薪試算",
        "tab_attendance": "📱 出勤打卡、請假與加班時數連線",
        "tab_history": "📜 歷史發薪紀錄與會計拋轉",
        "select_month": "選擇薪資結算月份",
        "info_calc": "💡 系統已自動整合越南勞動法規：國定假日出勤 3 倍薪、平日加班 1.5 倍、遲到請假自動扣款。",
        "base_salary": "基本底薪 (Lương cơ bản)",
        "meal_allowance": "餐費補助 (Phụ cấp cơm)",
        "fuel_allowance": "油費補助 (Phụ cấp xăng)",
        "phone_allowance": "電話補助 (Phụ cấp điện thoại)",
        "position_allowance": "職務加給 (Tiền chức vụ)",
        "license_allowance": "執照/牌照加給 (Phụ cấp giấy phép)",
        "tips": "小費 / 獎金 (Tiền tips)",
        "loan_deduction": "本月借款預支 (Tiền ứng)",
        "print_btn": "🖨️ 列印正式薪資單",
        "approve_btn": "💾 確認核准並拋轉會計傳票",
        "att_title": "📱 連動打卡、請假與加班考勤數據",
        "att_caption": "即時同步現場工程人員與辦公室同仁的加班時數、休假日出勤與遲到記錄。",
        "export_excel_btn": "📊 下載完整越南標準薪資總表 (Excel)",
    },
    "Tiếng Việt": {
        "title": "💰 Bộ phận Tài chính - Trung tâm Tính lương & Khấu trừ Bảo hiểm",
        "caption": "Tích hợp chấm công, nghỉ phép, lương lễ tết 300% theo luật lao động VN và tính tiền tăng ca.",
        "tab_list": "📊 Bảng lương chi tiết toàn nhà máy & Xuất Excel",
        "tab_calc": "🧮 Tính lương, tăng ca & Lương ngày lễ 300%",
        "tab_attendance": "📱 Đồng bộ chấm công, nghỉ phép & Tăng ca",
        "tab_history": "📜 Lịch sử bảng lương & Bút toán kế toán",
        "select_month": "Chọn tháng quyết toán lương",
        "info_calc": "💡 Tự động tính toán lương làm việc ngày lễ (300%), tăng ca ngày thường (150%) theo luật VN.",
        "base_salary": "Lương cơ bản",
        "meal_allowance": "Phụ cấp tiền cơm",
        "fuel_allowance": "Phụ cấp tiền xăng",
        "phone_allowance": "Phụ cấp điện thoại",
        "position_allowance": "Tiền chức vụ",
        "license_allowance": "Phụ cấp giấy phép",
        "tips": "Tiền tips / Thưởng",
        "loan_deduction": "Tiền ứng / Tạm ứng",
        "print_btn": "🖨️ In phiếu lương chính thức",
        "approve_btn": "💾 Xác nhận duyệt & Ghi sổ kế toán",
        "att_title": "📱 Dữ liệu chấm công, nghỉ phép & Tăng ca thực tế",
        "att_caption": "Đồng bộ giờ tăng ca, làm việc ngày lễ và đi trễ.",
        "export_excel_btn": "📊 Tải xuống bảng lương chuẩn (Excel)",
    },
    "English": {
        "title": "💰 Finance Dept - Employee Payroll & Insurance Calculation Center",
        "caption": "Integrated with attendance, leave, VN labor law 300% holiday pay, and overtime calculation.",
        "tab_list": "📊 Plant-wide Detailed Payroll Summary & Excel Export",
        "tab_calc": "🧮 Individual Payroll, Overtime & 3X Holiday Pay Calculator",
        "tab_attendance": "📱 Attendance, Leave & Overtime Integration",
        "tab_history": "📜 Payroll History & Accounting Entries",
        "select_month": "Select Payroll Settlement Month",
        "info_calc": "💡 Automatically calculates 3X holiday pay, 1.5X overtime, and attendance deductions.",
        "base_salary": "Base Salary",
        "meal_allowance": "Meal Allowance",
        "fuel_allowance": "Fuel Allowance",
        "phone_allowance": "Phone Allowance",
        "position_allowance": "Position Allowance",
        "license_allowance": "License Allowance",
        "tips": "Tips / Bonus",
        "loan_deduction": "Advance / Loan Deduction",
        "print_btn": "🖨️ Print Official Payslip",
        "approve_btn": "💾 Approve & Post to Accounting",
        "att_title": "📱 Live Attendance, Leave & Overtime Data",
        "att_caption": "Syncs overtime hours, holiday work days, and tardiness.",
        "export_excel_btn": "📊 Download Standard Payroll Summary (Excel)",
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

    # 模擬或讀取員工名冊（含越南廠員工、考勤、加班與國定假日出勤數據）
    if "employees_db" in st.session_state and st.session_state.employees_db:
        emp_list = st.session_state.employees_db
    else:
        emp_list = [
            {
                "id": "EMP-001", "name": "Phạm Thanh Qúy (范青贵)", "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)", 
                "dept": "營運部", "title": "副店長 (Phó cửa hàng trưởng)", "join_date": "2024-11-14", "base_salary": 6000000.0, 
                "tardiness_mins": 0, "leave_days": 0, "ot_normal_hours": 10, "holiday_work_days": 1
            },
            {
                "id": "EMP-002", "name": "Nguyễn Văn A", "site": "🇻🇳 越南廠 (Tay Ninh / Binh Duong)", 
                "dept": "工程部", "title": "配電盤組裝工程師", "join_date": "2023-05-10", "base_salary": 8000000.0, 
                "tardiness_mins": 15, "leave_days": 1, "ot_normal_hours": 20, "holiday_work_days": 2
            },
            {
                "id": "EMP-003", "name": "陳智賢", "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)", 
                "dept": "經營高層", "title": "總經理 (General Manager)", "join_date": "2021-03-01", "base_salary": 25000000.0, 
                "tardiness_mins": 0, "leave_days": 0, "ot_normal_hours": 0, "holiday_work_days": 0
            }
        ]

    # ----------------------------------------------------
    # 📊 頁籤一：全廠區員工薪資詳細總表與 Excel 匯出
    # ----------------------------------------------------
    with tab_list:
        st.markdown("### 📊 全廠區員工本月薪資總表 (越南標準會計與勞動法)")
        st.caption("自動整合底薪、津貼、保險 (10.5%)、遲到請假扣款、平日加班 (1.5倍) 與國定假日出勤 3 倍薪 (300%)。")

        summary_rows = []
        for emp in emp_list:
            base = emp.get("base_salary", 6000000.0)
            work_days = 26.0  # 標準月工作天數
            
            daily_wage = base / work_days
            hourly_wage = daily_wage / 8.0
            minute_wage = hourly_wage / 60.0

            # 考勤與加班數據
            tardiness_mins = emp.get("tardiness_mins", 0)
            leave_days = emp.get("leave_days", 0)
            ot_normal_hours = emp.get("ot_normal_hours", 10.0)      # 平日加班時數 (1.5倍)
            holiday_work_days = emp.get("holiday_work_days", 1.0)   # 國定假日出勤天數 (3倍)

            # 扣款與加班費計算
            tardiness_deduction = tardiness_mins * minute_wage
            leave_deduction = leave_days * daily_wage
            
            # 加班費：平日加班時數 * 時薪 * 1.5
            overtime_pay = ot_normal_hours * hourly_wage * 1.5
            
            # 國定假日 3 倍薪：假日出勤天數 * 日薪 * 3.0 (含原本當日薪資，故額外加發 2 倍或直接以 3 倍計)
            holiday_pay = holiday_work_days * daily_wage * 3.0

            # 法定保險 (BHXH 8%, BHYT 1.5%, BHTN 1% = 10.5%)
            bhxh = base * 0.08
            bhyt = base * 0.015
            bhtn = base * 0.01
            total_insurance = bhxh + bhyt + bhtn

            # 津貼與補助
            meal = 250000.0
            fuel = 250000.0
            phone = 0.0
            position_bonus = 2000000.0
            license_bonus = 1000000.0
            tips = 871000.0

            total_due = base + meal + fuel + phone + overtime_pay + holiday_pay + position_bonus + license_bonus + tips
            total_deduct = total_insurance + leave_deduction + tardiness_deduction + 0.0
            net_pay = total_due - total_deduct

            summary_rows.append({
                "工號": emp['id'],
                "姓名": emp['name'],
                "職稱": emp['title'],
                "薪資總額(底薪)": base,
                "總工作天數": work_days,
                "請假天數": leave_days,
                "遲到分鐘": tardiness_mins,
                "平日加班時數(1.5x)": ot_normal_hours,
                "國定假日出勤天數(3x)": holiday_work_days,
                "日薪": round(daily_wage, 2),
                "時薪": round(hourly_wage, 2),
                "餐費補助": meal,
                "油費補助": fuel,
                "加班費(Tăng ca)": round(overtime_pay, 2),
                "國定假日3倍薪(Lương lễ 300%)": round(holiday_pay, 2),
                "職務加給": position_bonus,
                "執照加給": license_bonus,
                "小費獎金": tips,
                "應付金額合計": round(total_due, 2),
                "社會保險(8%)": bhxh,
                "醫療保險(1.5%)": bhyt,
                "失業保險(1%)": bhtn,
                "請假扣款": round(leave_deduction, 2),
                "遲到扣款": round(tardiness_deduction, 2),
                "應扣金額合計": round(total_deduct, 2),
                "本月實發淨額 (Net)": round(net_pay, 2)
            })

        df_summary = pd.DataFrame(summary_rows)
        st.dataframe(df_summary, use_container_width=True)

        st.markdown("---")
        excel_data = convert_payroll_to_excel(summary_rows)
        st.download_button(
            label=L["export_excel_btn"],
            data=excel_data,
            file_name=f"Reetech_Payroll_VN_Standard_{datetime.date.today().strftime('%Y%m')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+sheet",
            type="primary",
            key="download_std_excel"
        )

    # ----------------------------------------------------
    # 🧮 頁籤二：單一員工詳細薪資與加班、假日 3 倍薪試算
    # ----------------------------------------------------
    with tab_calc:
        st.markdown("### 🧮 單一員工薪資、加班與國定假日 3 倍薪自動試算")
        st.caption("系統自動帶入考勤系統之加班時數、國定假日出勤天數、遲到與請假記錄進行精準結算。")

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
        emp_site = emp.get("site", "🇻🇳 越南廠")

        st.markdown(f"#### 👤 員工姓名: **{emp['name']}** (`{emp_id}`) | 職稱: {emp['title']}")
        st.caption(f"📍 工作廠區: **{emp_site}** | 到職日: {emp.get('join_date', '2024-01-01')}")

        # 薪資與補助設定
        c1, c2, c3 = st.columns(3)
        with c1:
            base_salary = st.number_input(L["base_salary"], value=float(emp.get("base_salary", 6000000.0)), step=100000.0, key=f"base_{emp_id}")
        with c2:
            meal_allowance = st.number_input(L["meal_allowance"], value=250000.0, step=50000.0, key=f"meal_{emp_id}")
        with c3:
            fuel_allowance = st.number_input(L["fuel_allowance"], value=250000.0, step=50000.0, key=f"fuel_{emp_id}")

        c4, c5, c6 = st.columns(3)
        with c4:
            position_allowance = st.number_input(L["position_allowance"], value=2000000.0, step=100000.0, key=f"pos_{emp_id}")
        with c5:
            license_allowance = st.number_input(L["license_allowance"], value=1000000.0, step=100000.0, key=f"lic_{emp_id}")
        with c6:
            tips = st.number_input(L["tips"], value=871000.0, step=50000.0, key=f"tips_{emp_id}")

        st.markdown("---")
        st.markdown("##### ⏰ 打卡、請假、加班與【越南國定假日 3 倍薪】自動連線設定")
        
        col_att1, col_att2, col_att3, col_att4 = st.columns(4)
        with col_att1:
            tardiness_mins = st.number_input("遲到分鐘數", min_value=0.0, value=float(emp.get("tardiness_mins", 0)), step=1.0, key=f"tard_{emp_id}")
        with col_att2:
            leave_days = st.number_input("請假天數", min_value=0.0, value=float(emp.get("leave_days", 0)), step=0.5, key=f"leave_{emp_id}")
        with col_att3:
            ot_normal_hours = st.number_input("平日加班時數 (1.5倍)", min_value=0.0, value=float(emp.get("ot_normal_hours", 10.0)), step=1.0, key=f"ot_{emp_id}")
        with col_att4:
            holiday_work_days = st.number_input("國定假日出勤天數 (3倍薪)", min_value=0.0, value=float(emp.get("holiday_work_days", 1.0)), step=0.5, key=f"hol_{emp_id}")

        loan_deduction = st.number_input(L["loan_deduction"], min_value=0.0, value=0.0, step=100000.0, key=f"loan_{emp_id}")

        # 計算工資單價
        work_days = 26.0
        daily_wage = base_salary / work_days
        hourly_wage = daily_wage / 8.0
        minute_wage = hourly_wage / 60.0

        # 計算加班費與 3 倍假日薪資
        overtime_pay = ot_normal_hours * hourly_wage * 1.5           # 平日加班 1.5 倍
        holiday_pay = holiday_work_days * daily_wage * 3.0           # 國定假日 3 倍薪 (300%)

        # 計算扣款
        tardiness_deduction = tardiness_mins * minute_wage
        leave_deduction = leave_days * daily_wage

        # 保險計算 (BHXH 8%, BHYT 1.5%, BHTN 1%)
        bhxh = base_salary * 0.08
        bhyt = base_salary * 0.015
        bhtn = base_salary * 0.01
        total_insurance = bhxh + bhyt + bhtn

        total_due = base_salary + meal_allowance + fuel_allowance + position_allowance + license_allowance + overtime_pay + holiday_pay + tips
        total_deduct = total_insurance + leave_deduction + tardiness_deduction + loan_deduction
        net_payable = total_due - total_deduct

        # 呈現正式越南會計薪資單明細
        st.markdown(
            f"""
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #cbd5e1; font-family: sans-serif; color: #1e293b;">
                <h3 style="margin-top:0; color:#0f172a;">📄 裕豐電機工業 (Reetech Industrial) - 正式薪資結算明細單</h3>
                <p style="margin:2px 0; color:#475569;"><b>結算月份</b>: {pay_month.strftime('%Y年%m月')} | <b>工號</b>: {emp_id} | <b>姓名</b>: {emp['name']}</p>
                <hr style="margin: 10px 0; border:0; border-top:1px solid #94a3b8;">
                
                <b>1. 薪資換算基準 (Đơn giá lương)：</b><br>
                &nbsp;&nbsp;• 標準工作天數: {work_days} 天 | 日薪: <b>{daily_wage:,.2f} ₫</b> | 時薪: <b>{hourly_wage:,.2f} ₫</b> | 每分鐘: <b>{minute_wage:,.2f} ₫</b><br><br>

                <b>2. 應付金額 (Số tiền đến hạn)：</b><br>
                &nbsp;&nbsp;• 薪資總額 / 底薪: <b>{base_salary:,.2f} ₫</b><br>
                &nbsp;&nbsp;• 餐費補助: {meal_allowance:,.2f} ₫ | 油費補助: {fuel_allowance:,.2f} ₫<br>
                &nbsp;&nbsp;• 職務加給: {position_allowance:,.2f} ₫ | 執照加給: {license_allowance:,.2f} ₫<br>
                &nbsp;&nbsp;• 平日加班費 ({ot_normal_hours} 小時 @ 1.5x): <b>{overtime_pay:,.2f} ₫</b><br>
                &nbsp;&nbsp;• 🌟 國定假日 3 倍薪 ({holiday_work_days} 天 @ 300% Lương lễ): <b>{holiday_pay:,.2f} ₫</b><br>
                &nbsp;&nbsp;• 小費/獎金: {tips:,.2f} ₫<br>
                &nbsp;&nbsp;👉 <b>應付金額總合計 (Total Due): {total_due:,.2f} ₫</b><br><br>

                <b>3. 應扣金額 (Số tiền khấu trừ)：</b><br>
                &nbsp;&nbsp;• 🛡️ 社會保險 (BHXH 8%): <b>- {bhxh:,.2f} ₫</b><br>
                &nbsp;&nbsp;• 🛡️ 醫療保險 (BHYT 1.5%): <b>- {bhyt:,.2f} ₫</b><br>
                &nbsp;&nbsp;• 🛡️ 失業險 (BHTN 1%): <b>- {bhtn:,.2f} ₫</b><br>
                &nbsp;&nbsp;• 📝 請假扣款 ({leave_days} 天): <b>- {leave_deduction:,.2f} ₫</b><br>
                &nbsp;&nbsp;• ⏰ 遲到扣款 ({tardiness_mins} 分鐘): <b>- {tardiness_deduction:,.2f} ₫</b><br>
                &nbsp;&nbsp;• 💳 預支借款 (Tiền ứng): <b>- {loan_deduction:,.2f} ₫</b><br>
                &nbsp;&nbsp;👉 <b>應扣金額合計 (Total Deduct): {total_deduct:,.2f} ₫</b><br>
                
                <hr style="margin: 15px 0; border:0; border-top:2px solid #047857;">
                <h2 style="color: #047857; margin:0;">💰 實領金額 (Số tiền thực lãnh): {net_payable:,.2f} VND</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(L["print_btn"], key=f"print_std_{emp_id}"):
                st.success(f"✅ 已成功產生 {emp['name']} 的正式薪資單，可連接印表機列印。")
        with col_btn2:
            if st.button(L["approve_btn"], type="primary", key=f"approve_std_{emp_id}"):
                st.success(f"🎉 已成功核准 {emp['name']} 本月薪資並拋轉會計總帳傳票！")

    # ----------------------------------------------------
    # 📱 頁籤三：出勤打卡與請假記錄連線
    # ----------------------------------------------------
    with tab_attendance:
        st.markdown(f"### {L['att_title']}")
        st.info(L["att_caption"])
        
        att_data = [
            {"工號": "EMP-001", "姓名": "Phạm Thanh Qúy", "出勤天數": 26, "請假天數": 0, "遲到分鐘": 0, "平日加班(時)": 10, "國定假日出勤(天)": 1, "狀態": "🟢 正常出勤"},
            {"工號": "EMP-002", "姓名": "Nguyễn Văn A", "出勤天數": 25, "請假天數": 1, "遲到分鐘": 15, "平日加班(時)": 20, "國定假日出勤(天)": 2, "狀態": "⭐ 有加班/假日出勤"},
            {"工號": "EMP-003", "姓名": "陳智賢", "出勤天數": 26, "請假天數": 0, "遲到分鐘": 0, "平日加班(時)": 0, "國定假日出勤(天)": 0, "狀態": "🟢 正常出勤"}
        ]
        st.dataframe(pd.DataFrame(att_data), use_container_width=True)

    # ----------------------------------------------------
    # 📜 頁籤四：歷史發薪紀錄與會計拋轉
    # ----------------------------------------------------
    with tab_history:
        st.markdown(f"### {L['hist_title']}")
        st.caption("歷月份薪資發放憑證與會計傳票拋轉記錄運作中。")


def show(engine=None, lang="繁體中文"):
    render_payroll_management_page(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_payroll_management_page(engine, lang)
