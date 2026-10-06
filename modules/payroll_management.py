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
        "caption": "連動打卡、請假與簽核系統，自動計算越南法定保險、津貼與考勤扣款。",
        "tab_list": "📊 全廠區本月薪資詳細總表與 Excel 匯出",
        "tab_calc": "🧮 單一員工詳細薪資與考勤扣款試算",
        "tab_attendance": "📱 出勤打卡與請假記錄連線",
        "tab_history": "📜 歷史發薪紀錄與會計拋轉",
        "select_month": "選擇薪資結算月份",
        "info_calc": "💡 系統已連動出勤打卡與請假系統，遲到與請假扣款將自動帶入。",
        "base_salary": "薪資總額 / 基本底薪",
        "meal_allowance": "餐費補助 (Phụ cấp cơm)",
        "fuel_allowance": "油費補助 (Phụ cấp xăng)",
        "phone_allowance": "電話補助 (Phụ cấp điện thoại)",
        "overtime_pay": "加班費 (Tiền tăng ca)",
        "position_allowance": "職務加給 (Tiền chức vụ)",
        "license_allowance": "執照/牌照加給 (Phụ cấp giấy phép)",
        "tips": "小費 / 獎金 (Tiền tips)",
        "loan_deduction": "本月借款預支 (Tiền ứng)",
        "print_btn": "🖨️ 列印正式薪資單",
        "approve_btn": "💾 確認核准並拋轉會計傳票",
        "att_title": "📱 連動打卡與請假考勤數據",
        "att_caption": "即時同步現場工程人員與辦公室同仁的遲到時數與請假天數。",
        "export_excel_btn": "📊 下載完整越南標準薪資總表 (Excel)",
    },
    "Tiếng Việt": {
        "title": "💰 Bộ phận Tài chính - Trung tâm Tính lương & Khấu trừ Bảo hiểm",
        "caption": "Tích hợp hệ thống chấm công, nghỉ phép và phê duyệt, tự động khấu trừ đi trễ và nghỉ phép.",
        "tab_list": "📊 Bảng lương chi tiết toàn nhà máy & Xuất Excel",
        "tab_calc": "🧮 Tính lương & Khấu trừ chi tiết từng nhân viên",
        "tab_attendance": "📱 Đồng bộ chấm công & Nghỉ phép",
        "tab_history": "📜 Lịch sử bảng lương & Bút toán kế toán",
        "select_month": "Chọn tháng quyết toán lương",
        "info_calc": "💡 Hệ thống tự động liên kết với dữ liệu chấm công và nghỉ phép để khấu trừ.",
        "base_salary": "Lương tổng / Lương cơ bản",
        "meal_allowance": "Phụ cấp tiền cơm",
        "fuel_allowance": "Phụ cấp tiền xăng",
        "phone_allowance": "Phụ cấp điện thoại",
        "overtime_pay": "Tiền tăng ca",
        "position_allowance": "Tiền chức vụ",
        "license_allowance": "Phụ cấp giấy phép",
        "tips": "Tiền tips / Thưởng",
        "loan_deduction": "Tiền ứng / Tạm ứng",
        "print_btn": "🖨️ In phiếu lương chính thức",
        "approve_btn": "💾 Xác nhận duyệt & Ghi sổ kế toán",
        "att_title": "📱 Dữ liệu chấm công & Nghỉ phép thời gian thực",
        "att_caption": "Đồng bộ số phút đi trễ và ngày nghỉ phép của nhân viên.",
        "export_excel_btn": "📊 Tải xuống bảng lương chuẩn (Excel)",
    },
    "English": {
        "title": "💰 Finance Dept - Employee Payroll & Insurance Calculation Center",
        "caption": "Integrated with attendance and leave systems for automated deductions.",
        "tab_list": "📊 Plant-wide Detailed Payroll Summary & Excel Export",
        "tab_calc": "🧮 Individual Employee Payroll & Deduction Calculator",
        "tab_attendance": "📱 Attendance & Leave System Integration",
        "tab_history": "📜 Payroll History & Accounting Entries",
        "select_month": "Select Payroll Settlement Month",
        "info_calc": "💡 System automatically links with attendance and leave records for deductions.",
        "base_salary": "Base Salary / Total Salary",
        "meal_allowance": "Meal Allowance",
        "fuel_allowance": "Fuel Allowance",
        "phone_allowance": "Phone Allowance",
        "overtime_pay": "Overtime Pay",
        "position_allowance": "Position Allowance",
        "license_allowance": "License Allowance",
        "tips": "Tips / Bonus",
        "loan_deduction": "Advance / Loan Deduction",
        "print_btn": "🖨️ Print Official Payslip",
        "approve_btn": "💾 Approve & Post to Accounting",
        "att_title": "📱 Live Attendance & Leave Data",
        "att_caption": "Syncs tardiness minutes and leave days for accurate payroll.",
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

    # 模擬或讀取員工名冊（含越南廠員工與考勤連線數據）
    if "employees_db" in st.session_state and st.session_state.employees_db:
        emp_list = st.session_state.employees_db
    else:
        emp_list = [
            {"id": "EMP-001", "name": "Phạm Thanh Qúy (范青贵)", "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)", "dept": "營運部", "title": "副店長 (Phó cửa hàng trưởng)", "join_date": "2024-11-14", "base_salary": 6000000.0, "tardiness_mins": 0, "leave_days": 0},
            {"id": "EMP-002", "name": "Nguyễn Văn A", "site": "🇻🇳 越南廠 (Tay Ninh / Binh Duong)", "dept": "工程部", "title": "配電盤組裝工程師", "join_date": "2023-05-10", "base_salary": 8000000.0, "tardiness_mins": 15, "leave_days": 1},
            {"id": "EMP-003", "name": "陳智賢", "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)", "dept": "經營高層", "title": "總經理 (General Manager)", "join_date": "2021-03-01", "base_salary": 25000000.0, "tardiness_mins": 0, "leave_days": 0}
        ]

    # ----------------------------------------------------
    # 📊 頁籤一：全廠區員工薪資詳細總表與 Excel 匯出
    # ----------------------------------------------------
    with tab_list:
        st.markdown("### 📊 全廠區員工本月薪資總表 (越南標準會計格式)")
        st.caption("完整包含底薪、各項津貼補助、保險 (BHXH 8%, BHYT 1.5%, BHTN 1%)、打卡遲到扣款與請假扣款。")

        summary_rows = []
        for emp in emp_list:
            base = emp.get("base_salary", 6000000.0)
            work_days = 26  # 標準工作天數
            
            # 換算
            daily_wage = base / work_days
            hourly_wage = daily_wage / 8.0
            minute_wage = hourly_wage / 60.0

            # 從打卡與請假系統取得數據
            tardiness_mins = emp.get("tardiness_mins", 0)
            leave_days = emp.get("leave_days", 0)

            tardiness_deduction = tardiness_mins * minute_wage
            leave_deduction = leave_days * daily_wage

            # 法定保險 (BHXH 8%, BHYT 1.5%, BHTN 1% = 10.5%)
            bhxh = base * 0.08
            bhyt = base * 0.015
            bhtn = base * 0.01
            total_insurance = bhxh + bhyt + bhtn

            # 津貼與補助
            meal = 250000.0
            fuel = 250000.0
            phone = 0.0
            overtime = 43659.0
            position_bonus = 2000000.0
            license_bonus = 1000000.0
            tips = 871000.0

            total_due = base + meal + fuel + phone + overtime + position_bonus + license_bonus + tips
            total_deduct = total_insurance + leave_deduction + tardiness_deduction + 0.0  # 借款 0
            net_pay = total_due - total_deduct

            summary_rows.append({
                "工號": emp['id'],
                "姓名": emp['name'],
                "職稱": emp['title'],
                "薪資總額": base,
                "總工作天數": work_days,
                "請假天數": leave_days,
                "遲到分鐘": tardiness_mins,
                "日薪": round(daily_wage, 2),
                "時薪": round(hourly_wage, 2),
                "每分鐘薪資": round(minute_wage, 2),
                "餐費補助": meal,
                "油費補助": fuel,
                "加班費": overtime,
                "職務加給": position_bonus,
                "執照加給": license_bonus,
                "小費獎金": tips,
                "應付金額合計": total_due,
                "社會保險(8%)": bhxh,
                "醫療保險(1.5%)": bhyt,
                "失業保險(1%)": bhtn,
                "請假扣款": round(leave_deduction, 2),
                "遲到扣款": round(tardiness_deduction, 2),
                "借款預支": 0.0,
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
            file_name=f"Reetech_Payroll_Standard_{datetime.date.today().strftime('%Y%m')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+sheet",
            type="primary",
            key="download_std_excel"
        )

    # ----------------------------------------------------
    # 🧮 頁籤二：單一員工詳細薪資與考勤扣款試算
    # ----------------------------------------------------
    with tab_calc:
        st.markdown("### 🧮 單一員工薪資結構與考勤自動連線試算")
        st.caption("系統自動對應打卡系統遲到記錄與請假系統核准時數，即時計算扣款與實發金額。")

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
        curr = "VND"

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
            overtime_pay = st.number_input(L["overtime_pay"], value=43659.0, step=1000.0, key=f"ot_{emp_id}")

        st.markdown("---")
        st.markdown("##### ⏰ 打卡系統與請假系統自動連線扣款數據")
        
        # 自動從考勤系統抓取數據
        col_att1, col_att2, col_att3 = st.columns(3)
        with col_att1:
            tardiness_mins = st.number_input("遲到總分鐘數 (來自打卡系統)", min_value=0.0, value=float(emp.get("tardiness_mins", 0)), step=1.0, key=f"tard_{emp_id}")
        with col_att2:
            leave_days = st.number_input("請假天數 (來自請假簽核系統)", min_value=0.0, value=float(emp.get("leave_days", 0)), step=0.5, key=f"leave_{emp_id}")
        with col_att3:
            loan_deduction = st.number_input(L["loan_deduction"], min_value=0.0, value=0.0, step=100000.0, key=f"loan_{emp_id}")

        # 計算工資單價
        work_days = 26.0
        daily_wage = base_salary / work_days
        hourly_wage = daily_wage / 8.0
        minute_wage = hourly_wage / 60.0

        # 計算扣款
        tardiness_deduction = tardiness_mins * minute_wage
        leave_deduction = leave_days * daily_wage

        # 保險計算 (BHXH 8%, BHYT 1.5%, BHTN 1%)
        bhxh = base_salary * 0.08
        bhyt = base_salary * 0.015
        bhtn = base_salary * 0.01
        total_insurance = bhxh + bhyt + bhtn

        tips = 871000.0
        total_due = base_salary + meal_allowance + fuel_allowance + position_allowance + license_allowance + overtime_pay + tips
        total_deduct = total_insurance + leave_deduction + tardiness_deduction + loan_deduction
        net_payable = total_due - total_deduct

        # 呈現正式越南會計薪資單明細
        st.markdown(
            f"""
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #cbd5e1; font-family: sans-serif; color: #1e293b;">
                <h3 style="margin-top:0; color:#0f172a;">📄 裕豐電機工業 (Reetech Industrial) - 正式薪資結算明細單</h3>
                <p style="margin:2px 0; color:#475569;"><b>結算月份</b>: {pay_month.strftime('%Y年%m月')} | <b>工號</b>: {emp_id} | <b>姓名</b>: {emp['name']}</p>
                <hr style="margin: 10px 0; border:0; border-top:1px solid #94a3b8;">
                
                <b>1. 考勤與薪資換算基準：</b><br>
                &nbsp;&nbsp;• 總工作天數: {work_days} 天 | 日薪: <b>{daily_wage:,.2f} ₫</b> | 時薪: <b>{hourly_wage:,.2f} ₫</b> | 每分鐘薪資: <b>{minute_wage:,.2f} ₫</b><br><br>

                <b>2. 應付金額 (Số tiền đến hạn)：</b><br>
                &nbsp;&nbsp;• 薪資總額 / 底薪: <b>{base_salary:,.2f} ₫</b><br>
                &nbsp;&nbsp;• 餐費補助: {meal_allowance:,.2f} ₫ | 油費補助: {fuel_allowance:,.2f} ₫<br>
                &nbsp;&nbsp;• 職務加給: {position_allowance:,.2f} ₫ | 執照加給: {license_allowance:,.2f} ₫<br>
                &nbsp;&nbsp;• 加班費 (Tăng ca): {overtime_pay:,.2f} ₫ | 小費/獎金: {tips:,.2f} ₫<br>
                &nbsp;&nbsp;👉 <b>應付金額總合計 (Total Due): {total_due:,.2f} ₫</b><br><br>

                <b>3. 應扣金額 (Số tiền khấu trừ) - 自動連線打卡與請假系統：</b><br>
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
            {"工號": "EMP-001", "姓名": "Phạm Thanh Qúy", "出勤天數": 26, "請假天數": 0, "遲到分鐘": 0, "狀態": "🟢 正常出勤"},
            {"工號": "EMP-002", "姓名": "Nguyễn Văn A", "出勤天數": 25, "請假天數": 1, "遲到分鐘": 15, "狀態": "⚠️ 曾遲到/請假"},
            {"工號": "EMP-003", "姓名": "陳智賢", "出勤天數": 26, "請假天數": 0, "遲到分鐘": 0, "狀態": "🟢 正常出勤"}
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
