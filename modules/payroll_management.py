import datetime
import pandas as pd
from sqlalchemy import text
import streamlit as st

# ----------------------------------------------------
# 🌐 薪資與保險模組多語系字典 (i18n)
# ----------------------------------------------------
PAYROLL_I18N = {
    "繁體中文": {
        "title": "💰 財務部 - 員工薪資與保險扣款試算中心",
        "caption": "提供各廠區員工底薪、津貼、保險、借款扣款明細與薪資單列印",
        "tab_calc": "🧮 員工薪資單與保險試算",
        "tab_attendance": "📱 出勤與考勤記錄同步",
        "tab_history": "📜 歷史發薪紀錄與清冊",
        "section_title": "📋 員工本月薪資結構、保險、借款扣款與實發淨額明細",
        "select_month": "選擇薪資結算月份",
        "info_calc": "💡 系統會根據員工所屬廠區自動計算當地法定保險與幣別。",
        "base_salary": "基本底薪 (Base Salary)",
        "allowance": "職務與專業津貼",
        "full_attendance": "全勤獎金 / 加班津貼",
        "leave_deduction": "請假/缺勤扣款金額",
        "loan_deduction": "本月借款/預支扣款",
        "other_allowance": "其他加項/補發金額",
        "print_btn": "🖨️ 列印/匯出薪資單",
        "approve_btn": "💾 確認核准並入帳",
        "att_title": "📱 出勤與考勤時數總結",
        "att_caption": "提供請假與全勤獎金發放依據。",
        "hist_title": "📜 歷史發薪紀錄與清冊",
        "hist_caption": "供財務與會計部查閱各月份薪資發放總表。",
    },
    "Tiếng Việt": {
        "title": "💰 Bộ phận Tài chính - Trung tâm Tính lương & Khấu trừ Bảo hiểm",
        "caption": "Cung cấp chi tiết lương cơ bản, phụ cấp, bảo hiểm, khấu trừ khoản vay và in phiếu lương",
        "tab_calc": "🧮 Tính lương & Bảo hiểm nhân viên",
        "tab_attendance": "📱 Đồng bộ chấm công & Chuyên cần",
        "tab_history": "📜 Lịch sử bảng lương & Danh sách",
        "section_title": "📋 Cơ cấu lương tháng, bảo hiểm, khấu trừ và thực nhận chi tiết",
        "select_month": "Chọn tháng quyết toán lương",
        "info_calc": "💡 Hệ thống tự động tính toán bảo hiểm và tiền tệ theo nhà máy của nhân viên.",
        "base_salary": "Lương cơ bản (Base Salary)",
        "allowance": "Phụ cấp chức vụ & chuyên môn",
        "full_attendance": "Thưởng chuyên cần / Làm thêm giờ",
        "leave_deduction": "Khấu trừ nghỉ phép / vắng mặt",
        "loan_deduction": "Khấu trừ tạm ứng / khoản vay",
        "other_allowance": "Các khoản cộng / bù khác",
        "print_btn": "🖨️ In / Xuất phiếu lương",
        "approve_btn": "💾 Xác nhận duyệt & Ghi sổ",
        "att_title": "📱 Tổng kết giờ làm việc & Chấm công",
        "att_caption": "Cung cấp cơ sở cho việc tính thưởng chuyên cần và nghỉ phép.",
        "hist_title": "📜 Lịch sử chi trả lương & Danh sách",
        "hist_caption": "Dành cho bộ phận tài chính và kế toán tra cứu tổng hợp.",
    },
    "English": {
        "title": "💰 Finance Dept - Employee Payroll & Insurance Calculation Center",
        "caption": "Provides basic salary, allowances, insurance, loan deductions, and payslip printing",
        "tab_calc": "🧮 Payroll & Insurance Calculator",
        "tab_attendance": "📱 Attendance & Time Tracking Sync",
        "tab_history": "📜 Payroll History & Records",
        "section_title": "📋 Monthly Salary Structure, Insurance, Deductions & Net Payable",
        "select_month": "Select Payroll Settlement Month",
        "info_calc": "💡 The system automatically calculates local statutory insurance and currency based on the employee's plant site.",
        "base_salary": "Base Salary",
        "allowance": "Position & Professional Allowance",
        "full_attendance": "Full Attendance / Overtime Bonus",
        "leave_deduction": "Leave / Absence Deduction",
        "loan_deduction": "Monthly Loan / Advance Deduction",
        "other_allowance": "Other Additions / Retroactive Pay",
        "print_btn": "🖨️ Print / Export Payslip",
        "approve_btn": "💾 Approve & Post Entry",
        "att_title": "📱 Attendance & Working Hours Summary",
        "att_caption": "Provides the basis for leave and full-attendance bonuses.",
        "hist_title": "📜 Historical Payroll Records & Registry",
        "hist_caption": "For finance and accounting departments to review monthly payroll tables.",
    }
}

def get_payroll_lang_dict(lang_param):
    lang = lang_param or st.session_state.get("lang", "繁體中文")
    return PAYROLL_I18N.get(lang, PAYROLL_I18N["繁體中文"])

# ----------------------------------------------------
# 🌐 各國強制社會保險與所得稅扣款比率字典
# ----------------------------------------------------
INSURANCE_RATES = {
    "🇻🇳 越南廠 (Tay Ninh / Binh Duong)": {
        "bhxh_social": 0.08,     # 社保 8%
        "bhyt_health": 0.015,    # 醫保 1.5%
        "bhtn_unemploy": 0.01,   # 失業險 1%
        "currency": "VND",
        "rate_label": "越南法定社保/醫保/失業險 (個人負擔 10.5%)"
    },
    "🇻🇳 越南海防廠 (Hai Phong Plant)": {
        "bhxh_social": 0.08,
        "bhyt_health": 0.015,
        "bhtn_unemploy": 0.01,
        "currency": "VND",
        "rate_label": "越南法定社保/醫保/失業險 (個人負擔 10.5%)"
    },
    "🇹🇼 台灣總部 (Taiwan HQ)": {
        "labor_ins": 0.023,      # 勞保約 2.3%
        "health_ins": 0.0517,    # 健保約 5.17% (自付額)
        "currency": "TWD",
        "rate_label": "台灣勞健保自付額 (勞保+健保級距)"
    },
    "🇨🇳 中國廠區 (Dongguan Plant)": {
        "pension": 0.08,         # 養老 8%
        "medical": 0.02,         # 醫療 2%
        "housing_fund": 0.07,    # 住房公積金 7%
        "currency": "CNY",
        "rate_label": "中國五險一金個人提撥"
    }
}


def render_payroll_management_page(engine=None, lang="繁體中文"):
    L = get_payroll_lang_dict(lang)
    
    st.title(L["title"])
    st.caption(L["caption"])

    tab_calc, tab_attendance, tab_history = st.tabs([
        L["tab_calc"],
        L["tab_attendance"],
        L["tab_history"]
    ])

    # 讀取動態 HR 人員名冊
    if "employees_db" in st.session_state and st.session_state.employees_db:
        emp_list = st.session_state.employees_db
    else:
        emp_list = [
            {"id": "EMP-001", "name": "張董事長", "site": "🇹🇼 台灣總部 (Taiwan HQ)", "dept": "經營高層", "title": "董事長"},
            {"id": "EMP-002", "name": "Nguyễn Văn A", "site": "🇻🇳 越南廠 (Tay Ninh / Binh Duong)", "dept": "工程部", "title": "配電盤組裝工程師"}
        ]

    # ----------------------------------------------------
    # 🧮 頁籤一：詳細薪資單與保險試算
    # ----------------------------------------------------
    with tab_calc:
        st.markdown(f"### {L['section_title']}")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            pay_month = st.date_input(L["select_month"], value=datetime.date.today(), key="payroll_month")
        with col_m2:
            st.info(L["info_calc"])

        st.divider()

        for emp in emp_list:
            emp_site = emp.get("site", "🇻🇳 越南廠 (Tay Ninh / Binh Duong)")
            ins_info = INSURANCE_RATES.get(emp_site, INSURANCE_RATES["🇻🇳 越南廠 (Tay Ninh / Binh Duong)"])
            curr = ins_info["currency"]

            with st.container():
                st.markdown(f"#### 👤 員工姓名: **{emp['name']}** (`{emp['id']}`) | 部門: {emp['dept']} | 職位: {emp['title']}")
                st.caption(f"📍 所屬工作廠區: **{emp_site}** | 計價幣別: **{curr}**")

                # 薪資結構細項設定
                c1, c2, c3 = st.columns(3)
                with c1:
                    default_base = 25000000.0 if curr == "VND" else (80000.0 if curr == "TWD" else 8000.0)
                    base_salary = st.number_input(L["base_salary"], value=default_base, step=1000.0, key=f"base_{emp['id']}")
                with c2:
                    allowance = st.number_input(L["allowance"], value=2000000.0 if curr == "VND" else 5000.0, step=500.0, key=f"allow_{emp['id']}")
                with c3:
                    full_attendance_bonus = st.number_input(L["full_attendance"], value=1000000.0 if curr == "VND" else 2000.0, step=500.0, key=f"bonus_{emp['id']}")

                # 扣款與借款調整欄位
                c4, c5, c6 = st.columns(3)
                with c4:
                    leave_deduction = st.number_input(L["leave_deduction"], value=0.0, step=100.0, key=f"leave_{emp['id']}")
                with c5:
                    loan_deduction = st.number_input(L["loan_deduction"], value=0.0, step=500.0, key=f"loan_{emp['id']}")
                with c6:
                    other_allowance = st.number_input(L["other_allowance"], value=0.0, step=100.0, key=f"other_{emp['id']}")

                # 自動計算保險扣款
                if "越南" in emp_site:
                    social_ins = base_salary * ins_info["bhxh_social"]
                    health_ins = base_salary * ins_info["bhyt_health"]
                    unemploy_ins = base_salary * ins_info["bhtn_unemploy"]
                    total_ins = social_ins + health_ins + unemploy_ins
                elif "台灣" in emp_site:
                    social_ins = base_salary * ins_info["labor_ins"]
                    health_ins = base_salary * ins_info["health_ins"]
                    unemploy_ins = 0.0
                    total_ins = social_ins + health_ins
                else:
                    social_ins = base_salary * ins_info["pension"]
                    health_ins = base_salary * ins_info["medical"]
                    unemploy_ins = base_salary * ins_info["housing_fund"]
                    total_ins = social_ins + health_ins + unemploy_ins

                # 總應發與實發計算（加入借款扣款）
                gross_salary = base_salary + allowance + full_attendance_bonus + other_allowance
                total_deduction = total_ins + leave_deduction + loan_deduction
                net_payable = gross_salary - total_deduction

                # 📊 薪資單明細呈現
                st.markdown(
                    f"""
                    <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; font-family: sans-serif; color: #1e293b;">
                        <h4 style="margin-top:0; color:#0f172a;">📄 裕豐電機工業 - 薪資結算明細單 ({pay_month.strftime('%Y年%m月')})</h4>
                        <hr style="margin: 5px 0 10px 0; border:0; border-top:1px solid #cbd5e1;">
                        <b>1. 應發項目 (Earnings)：</b><br>
                        &nbsp;&nbsp;• 基本底薪: <b>{base_salary:,.2f} {curr}</b><br>
                        &nbsp;&nbsp;• 職務/專業津貼: <b>{allowance:,.2f} {curr}</b><br>
                        &nbsp;&nbsp;• 全勤獎金/加班費: <b>{full_attendance_bonus:,.2f} {curr}</b><br>
                        &nbsp;&nbsp;• 其他補發項目: <b>{other_allowance:,.2f} {curr}</b><br>
                        &nbsp;&nbsp;👉 <b>總應發金額 (Gross): {gross_salary:,.2f} {curr}</b><br><br>
                        <b>2. 扣款項目 (Deductions)：</b><br>
                        &nbsp;&nbsp;• 🛡️ 當地法定保險 ({ins_info['rate_label']}): <b>- {total_ins:,.2f} {curr}</b><br>
                        &nbsp;&nbsp;• ⏰ 請假/缺勤扣款: <b>- {leave_deduction:,.2f} {curr}</b><br>
                        &nbsp;&nbsp;• 💳 員工借款/預支扣款: <b>- {loan_deduction:,.2f} {curr}</b><br>
                        &nbsp;&nbsp;👉 <b>總扣款金額: {total_deduction:,.2f} {curr}</b><br>
                        <hr style="margin: 10px 0; border:0; border-top:1px solid #cbd5e1;">
                        <h3 style="color: #047857; margin:0;">💰 本月實發淨額 (Net Payable): {net_payable:,.2f} {curr}</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(f"{L['print_btn']} [{emp['name']}]", key=f"print_{emp['id']}"):
                        st.success(f"✅ 已成功產生 {emp['name']} 的薪資單，可連接印表機列印。")
                with col_btn2:
                    if st.button(f"{L['approve_btn']} [{emp['name']}]", type="primary", key=f"approve_{emp['id']}"):
                        st.success(f"🎉 已成功核准 {emp['name']} 本月薪資 ({net_payable:,.2f} {curr})！")

                st.divider()

    # ----------------------------------------------------
    # 📱 頁籤二：出勤記錄
    # ----------------------------------------------------
    with tab_attendance:
        st.markdown(f"### {L['att_title']}")
        st.info(L["att_caption"])
        
        mock_att = [
            {"員工編號": "EMP-001", "姓名": "張董事長", "應出勤天數": 22, "實際出勤": 22, "請假時數": 0, "全勤狀態": "🌟 全勤"},
            {"員工編號": "EMP-002", "姓名": "Nguyễn Văn A", "應出勤天數": 22, "實際出勤": 21, "請假時數": 8, "全勤狀態": "📝 請假 1 天"}
        ]
        st.dataframe(pd.DataFrame(mock_att), use_container_width=True)

    # ----------------------------------------------------
    # 📜 頁籤三：歷史發薪紀錄
    # ----------------------------------------------------
    with tab_history:
        st.markdown(f"### {L['hist_title']}")
        st.caption(L["hist_caption"])


def show(engine=None, lang="繁體中文"):
    render_payroll_management_page(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_payroll_management_page(engine, lang)
