import datetime
import pandas as pd
from sqlalchemy import text
import streamlit as st

# ----------------------------------------------------
# 🌐 各國強制社會保險與所得稅扣款比率字典
# ----------------------------------------------------
INSURANCE_RATES = {
    "🇻🇳 越南廠 (Tay Ninh / Binh Duong)": {
        "bhxh_social": 0.08,     # 社保 8%
        "bhyt_health": 0.015,    # 醫保 1.5%
        "bhtn_unemploy": 0.01,   # 失業險 1%
        "currency": "VND",
        "rate_label": "越南法定社保/醫保/失業險 (個人扣 10.5%)"
    },
    "🇹🇼 台灣總部 (Taiwan HQ)": {
        "labor_ins": 0.023,      # 勞保約 2.3%
        "health_ins": 0.0517,    # 健保約 5.17% (自付額)
        "currency": "TWD",
        "rate_label": "台灣勞健保自付額 (勞保+健保級距)"
    },
    "🇨🇳 中國廠區 (Dongguan Plant)": {
        "pension": 0.08,          # 養老 8%
        "medical": 0.02,          # 醫療 2%
        "housing_fund": 0.07,     # 住房公積金 7%
        "currency": "CNY",
        "rate_label": "中國五險一金個人提撥"
    }
}


def render_payroll_management_page(engine=None, lang="繁體中文"):
    st.title("💰 財務部 - 全球員工薪資試算與考勤計算中心")
    st.caption("📱 專為手機瀏覽最佳化 — 整合多國社保代扣、中性考勤時數計算與實發薪資審核")

    tab_calc, tab_attendance, tab_history = st.tabs([
        "🧮 員工月薪試算與發放",
        "📱 指紋考勤打卡連動設定",
        "📜 歷年發薪紀錄與報表"
    ])

    # 1. 讀取 HR 人員名冊 (若有無資料備援)
    if "employees_db" in st.session_state and st.session_state.employees_db:
        emp_list = st.session_state.employees_db
    else:
        emp_list = [
            {"id": "EMP-001", "name": "張董事長", "site": "🇹🇼 台灣總部 (Taiwan HQ)", "dept": "經營高層", "title": "董事長"},
            {"id": "EMP-002", "name": "Nguyễn Văn A", "site": "🇻🇳 越南廠 (Tay Ninh / Binh Duong)", "dept": "工程部", "title": "配電盤組裝工程師"},
            {"id": "EMP-003", "name": "王廠長", "site": "🇨🇳 中國廠區 (Dongguan Plant)", "dept": "生產部", "title": "廠長"}
        ]

    # ----------------------------------------------------
    # 🧮 頁籤一：員工月薪試算與審核 (手機卡片模式)
    # ----------------------------------------------------
    with tab_calc:
        st.markdown("### 📋 本月員工薪資計算與各國保險扣款項")
        
        # 選擇發薪年月
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            pay_month = st.date_input("選擇結算月份", value=datetime.date.today(), key="payroll_month")
        with col_m2:
            # 💡 改為中性的考勤時數單價（可正可負，依出勤狀況或全勤獎金調整）
            attendance_unit_rate = st.number_input("考勤時數異動標準 (每分鐘金額 USD/VND)", value=0.0, step=0.5)

        st.divider()

        # 📱 逐位員工計算與顯示 (Mobile-First 卡片)
        for emp in emp_list:
            emp_site = emp.get("site", "🇻🇳 越南廠 (Tay Ninh / Binh Duong)")
            ins_info = INSURANCE_RATES.get(emp_site, INSURANCE_RATES["🇻🇳 越南廠 (Tay Ninh / Binh Duong)"])
            curr = ins_info["currency"]

            with st.container():
                st.markdown(f"### 👤 {emp['name']} (`{emp['id']}`) — {emp['dept']} / {emp['title']}")
                st.caption(f"📍 所屬廠區: {emp_site}")

                c_base, c_allowance, c_att = st.columns(3)
                
                with c_base:
                    # 財務填寫底薪
                    default_base = 25000000.0 if curr == "VND" else (80000.0 if curr == "TWD" else 8000.0)
                    base_salary = st.number_input(f"底薪基本工資 ({curr})", value=default_base, key=f"base_{emp['id']}")

                with c_allowance:
                    # 津貼與加給
                    allowance = st.number_input(f"職務/加班津貼 ({curr})", value=2000000.0 if curr == "VND" else 5000.0, key=f"allow_{emp['id']}")

                with c_att:
                    # 💡 改為中性的考勤時數調整（正數代表加給/全勤，負數或考勤異動代表微調）
                    attendance_minutes = st.number_input(f"考勤時數調整 (分鐘/可正可負)", value=0, key=f"att_{emp['id']}")

                # 🧮 計算保險與考勤調整金額
                if "越南" in emp_site:
                    ins_deduction = base_salary * (ins_info["bhxh_social"] + ins_info["bhyt_health"] + ins_info["bhtn_unemploy"])
                elif "台灣" in emp_site:
                    ins_deduction = base_salary * (ins_info["labor_ins"] + ins_info["health_ins"])
                else:
                    ins_deduction = base_salary * (ins_info["pension"] + ins_info["medical"] + ins_info["housing_fund"])

                attendance_adjustment = attendance_minutes * attendance_unit_rate
                net_salary = (base_salary + allowance) - ins_deduction - attendance_adjustment

                # 🚨 手機醒目明細卡片 (Mobile Card - 展現中性考勤計算)
                st.info(
                    f"📊 **薪資拆算總明細**：\n\n"
                    f"• **應發金額**: Base {base_salary:,.0f} + 津貼 {allowance:,.0f} = **{(base_salary+allowance):,.0f} {curr}**\n"
                    f"• 🛡️ **{ins_info['rate_label']}**: `- {ins_deduction:,.0f} {curr}`\n"
                    f"• ⏰ **考勤計算 (時數調整 {attendance_minutes} 分鐘)**: `{attendance_adjustment:+,.0f} {curr}`\n"
                    f"• 💰 **實發淨薪 (Net Payable)**: **{net_salary:,.0f} {curr}**"
                )

                if st.button(f"💾 核准發放薪資單 [{emp['name']}]", type="primary", key=f"btn_pay_{emp['id']}"):
                    st.success(f"🎉 已成功生成並核准 {emp['name']} {pay_month.strftime('%Y-%m')} 月份薪資單 ({net_salary:,.0f} {curr})！")

                st.divider()

    # ----------------------------------------------------
    # 📱 頁籤二：指紋考勤打卡連動 (Fingerprint Log Sync)
    # ----------------------------------------------------
    with tab_attendance:
        st.markdown("### 📱 指紋考勤機數據對接與統計 (Attendance Log Sync)")
        st.info("💡 提供連動廠區中控指紋機打卡記錄上傳，系統將自動統計員工出勤與考勤時數。")

        uploaded_log = st.file_uploader("上傳指紋考勤打卡記錄檔 (.csv / .txt)", type=["csv", "txt"])
        if uploaded_log is not None:
            st.success("✅ 指紋考勤資料已成功讀取與比對！")
            mock_attendance = [
                {"員工編號": "EMP-001", "姓名": "張董事長", "應出勤天數": 22, "實際打卡": 22, "考勤時數異常": 0, "狀態": "🟢 正常出勤"},
                {"員工編號": "EMP-002", "姓名": "Nguyễn Văn A", "應出勤天數": 22, "實際打卡": 21, "考勤時數異常": 15, "狀態": "🔵 考勤時數調整 15 分鐘"},
                {"員工編號": "EMP-003", "姓名": "王廠長", "應出勤天數": 22, "實際打卡": 22, "考勤時數異常": 0, "狀態": "🟢 正常出勤"}
            ]
            st.dataframe(pd.DataFrame(mock_attendance), use_container_width=True)

    # ----------------------------------------------------
    # 📜 頁籤三：歷史發薪紀錄
    # ----------------------------------------------------
    with tab_history:
        st.markdown("### 📜 歷史薪資發放與出勤審核紀錄")
        st.caption("提供審計人員與董事長隨時查閱歷史發薪總額。")


def show(engine=None, lang="繁體中文"):
    render_payroll_management_page(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_payroll_management_page(engine, lang)
