import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 員工薪資與保險計算多語系字典 (i18n)
# ----------------------------------------------------
PAYROLL_I18N = {
    "繁體中文": {
        "title": "💰 管理部 - 員工薪資計算與保險扣除管理中心",
        "caption": "符合越南勞動法：自動跨表讀取現場外勤打卡天數！自動試算底薪、加班費、外勤津貼、社保 (BHXH 8%)、醫保 (BHYT 1.5%)、失業保 (BHTN 1%) 與實發淨薪。",
        "tab_calc": "🧮 月度薪資與外勤津貼自動核算",
        "tab_history": "📊 歷史薪資清冊與發放紀錄",
        "lbl_month": "計薪月份 (YYYY-MM)",
        "lbl_emp_code": "員工工號",
        "lbl_emp_name": "員工姓名",
        "lbl_dept": "所屬部門",
        "lbl_base_salary": "約定基本薪資 (VND)",
        "lbl_ot_hours": "本月加班時數 (小時)",
        "lbl_ot_rate": "加班費時薪倍率 (1.5倍/2.0倍)",
        "lbl_allowance": "職務與外勤津貼 (VND)",
        "lbl_daily_rate": "外勤每日津貼標準 (VND/天)",
        "btn_calc_and_save": "💾 計算並寫入 Supabase 薪資資料庫",
        "msg_success": "✅ 薪資清冊計算完畢並已成功寫入資料庫！",
        "lbl_net_pay": "💵 本月應發實付淨薪 (Net Salary)",
        "header_summary": "📋 歷史月度薪資與保險扣除統計表",
        "info_field_days": "📍 系統自動偵測：該員工 `{month}` 月在現場外勤打卡 **{days} 天**（自動試算外勤津貼 `{allowance:,.0f} VND`）。"
    },
    "Tiếng Việt": {
        "title": "💰 Phòng Quản lý - Tính Luơng & Khấu Trừ Bảo Hiểm",
        "caption": "Tuân thủ Luật Lao động VN: Tự động kết nối ngày chấm công công trường! Tính lương cơ bản, tăng ca, phụ cấp, BHXH (8%), BHYT (1.5%), BHTN (1%) và Lương thực nhận (Net).",
        "tab_calc": "🧮 Tính lương & Phụ cấp công tác",
        "tab_history": "📊 Lịch sử bảng lương & Báo cáo",
        "lbl_month": "Tháng tính lương (YYYY-MM)",
        "lbl_emp_code": "Mã nhân viên",
        "lbl_emp_name": "Tên nhân viên",
        "lbl_dept": "Phòng ban",
        "lbl_base_salary": "Lương cơ bản (VND)",
        "lbl_ot_hours": "Số giờ tăng ca (Giờ)",
        "lbl_ot_rate": "Hệ số tăng ca (1.5 / 2.0)",
        "lbl_allowance": "Phụ cấp công tác / Chức vụ (VND)",
        "lbl_daily_rate": "Đơn giá phụ cấp công tác (VND/Ngày)",
        "btn_calc_and_save": "💾 Tính & Lưu Bảng Lương vào Cơ Sở Dữ Liệu",
        "msg_success": "✅ Đã tính lương và lưu bảng lương thành công!",
        "lbl_net_pay": "💵 Lương thực nhận (Net Salary)",
        "header_summary": "📋 Lịch sử Bảng lương & Bảo hiểm tháng",
        "info_field_days": "📍 Hệ thống ghi nhận: Nhân viên chấm công công trường tháng `{month}` là **{days} ngày** (Phụ cấp tính tự động `{allowance:,.0f} VND`)."
    },
    "English": {
        "title": "💰 GA & HR - Payroll & Insurance Calculation Center",
        "caption": "Vietnamese Labor Law Compliant: Auto-fetches site check-in days! Calculates basic salary, OT, field allowances, BHXH (8%), BHYT (1.5%), BHTN (1%), and Net Pay.",
        "tab_calc": "🧮 Monthly Payroll & Allowance Calculation",
        "tab_history": "📊 Historical Payroll Records",
        "lbl_month": "Payroll Month (YYYY-MM)",
        "lbl_emp_code": "Employee Code",
        "lbl_emp_name": "Employee Name",
        "lbl_dept": "Department",
        "lbl_base_salary": "Base Salary (VND)",
        "lbl_ot_hours": "OT Hours",
        "lbl_ot_rate": "OT Multiplier (1.5x / 2.0x)",
        "lbl_allowance": "Field & Position Allowances (VND)",
        "lbl_daily_rate": "Daily Field Allowance Rate (VND/Day)",
        "btn_calc_and_save": "💾 Calculate & Save to Database",
        "msg_success": "✅ Payroll calculation saved to database successfully!",
        "lbl_net_pay": "💵 Net Salary Payable",
        "header_summary": "📋 Monthly Payroll & Insurance Summary",
        "info_field_days": "📍 System Auto-detect: Employee has **{days} site check-in days** in `{month}` (Calculated allowance `{allowance:,.0f} VND`)."
    }
}

def init_payroll_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.payroll_records (
                    id SERIAL PRIMARY KEY,
                    payroll_month VARCHAR(7) NOT NULL,
                    emp_code VARCHAR(50) NOT NULL,
                    emp_name VARCHAR(100) NOT NULL,
                    department VARCHAR(100),
                    base_salary NUMERIC(12,2) DEFAULT 0,
                    overtime_pay NUMERIC(12,2) DEFAULT 0,
                    allowance NUMERIC(12,2) DEFAULT 0,
                    bhxh_deduction NUMERIC(12,2) DEFAULT 0,
                    bhyt_deduction NUMERIC(12,2) DEFAULT 0,
                    bhtn_deduction NUMERIC(12,2) DEFAULT 0,
                    net_salary NUMERIC(12,2) NOT NULL,
                    status VARCHAR(50) DEFAULT '🟡 待審核 (Pending)',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_emp_payroll_month UNIQUE (payroll_month, emp_code)
                );
            """))
    except Exception as e:
        st.warning(f"⚠️ 資料庫 Table 初始化提示: {str(e)}")

def render_payroll_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = PAYROLL_I18N.get(active_lang, PAYROLL_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_payroll_db(engine)

    tab_calc, tab_history = st.tabs([L["tab_calc"], L["tab_history"]])

    # ----------------------------------------------------
    # 🧮 Tab 1: 薪資與外勤津貼自動核算
    # ----------------------------------------------------
    with tab_calc:
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            payroll_m = st.text_input(L["lbl_month"], value=datetime.datetime.now().strftime("%Y-%m"))
        with c_m2:
            e_code = st.text_input(L["lbl_emp_code"], value="EMP-001")
        with c_m3:
            dept_name = st.selectbox(L["lbl_dept"], ["🛠️ 工程部", "👔 管理部", "🏭 生產部", "📈 總經理室"])

        # 📍 跨表查詢該員工當月外勤打卡天數
        field_days = 0
        if engine and e_code and payroll_m:
            try:
                with engine.connect() as conn:
                    # 依據工號與月份查詢上班打卡筆數
                    res = conn.execute(text("""
                        SELECT COUNT(DISTINCT DATE(check_time)) 
                        FROM public.field_attendance_logs 
                        WHERE (emp_code = :code OR emp_name = :code)
                          AND TO_CHAR(check_time, 'YYYY-MM') = :month
                          AND check_type LIKE '%上班%'
                    """), {"code": e_code, "month": payroll_m})
                    val = res.fetchone()[0]
                    if val:
                        field_days = int(val)
            except Exception:
                pass

        # 外勤每日津貼設定 (預設 200,000 VND/天)
        daily_allowance_rate = 200000.0
        auto_calculated_allowance = field_days * daily_allowance_rate

        if field_days > 0:
            st.info(L["info_field_days"].format(month=payroll_m, days=field_days, allowance=auto_calculated_allowance))
        else:
            st.caption("ℹ️ 當月尚無現場外勤打卡紀錄或該員工為廠內固定人員。")

        st.markdown("---")
        
        with st.form("form_calc_payroll"):
            col1, col2, col3 = st.columns(3)
            with col1:
                e_name = st.text_input(L["lbl_emp_name"], value="許福村")
                base_sal = st.number_input(L["lbl_base_salary"], min_value=0.0, value=15000000.0, step=500000.0)
            with col2:
                allowance = st.number_input(L["lbl_allowance"], min_value=0.0, value=float(auto_calculated_allowance), step=100000.0)
                ot_hrs = st.number_input(L["lbl_ot_hours"], min_value=0.0, value=10.0, step=1.0)
            with col3:
                ot_rate = st.selectbox(L["lbl_ot_rate"], [1.5, 2.0])

            # 越南法規保險扣除計算 (以底薪為基準)
            hourly_rate = (base_sal / 26.0) / 8.0
            ot_pay = ot_hrs * hourly_rate * ot_rate
            
            bhxh = base_sal * 0.08    # 社會保險 8%
            bhyt = base_sal * 0.015   # 醫療保險 1.5%
            bhtn = base_sal * 0.01    # 失業保險 1%
            total_deduction = bhxh + bhyt + bhtn
            
            net_pay = base_sal + ot_pay + allowance - total_deduction

            st.markdown("##### 📊 計算結果預覽：")
            m1, m2, m3 = st.columns(3)
            m1.metric("本月加班費", f"{ot_pay:,.0f} VND")
            m2.metric("保險扣除總額 (10.5%)", f"{total_deduction:,.0f} VND")
            m3.metric(L["lbl_net_pay"], f"{net_pay:,.0f} VND")

            if st.form_submit_button(L["btn_calc_and_save"], type="primary", use_container_width=True):
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.payroll_records 
                                (payroll_month, emp_code, emp_name, department, base_salary, overtime_pay, allowance, bhxh_deduction, bhyt_deduction, bhtn_deduction, net_salary)
                                VALUES (:m, :code, :name, :dept, :bs, :ot, :al, :bhxh, :bhyt, :bhtn, :net)
                                ON CONFLICT (payroll_month, emp_code) DO UPDATE
                                SET base_salary = EXCLUDED.base_salary,
                                    overtime_pay = EXCLUDED.overtime_pay,
                                    allowance = EXCLUDED.allowance,
                                    bhxh_deduction = EXCLUDED.bhxh_deduction,
                                    bhyt_deduction = EXCLUDED.bhyt_deduction,
                                    bhtn_deduction = EXCLUDED.bhtn_deduction,
                                    net_salary = EXCLUDED.net_salary,
                                    updated_at = CURRENT_TIMESTAMP;
                            """), {
                                "m": payroll_m, "code": e_code, "name": e_name, "dept": dept_name,
                                "bs": base_sal, "ot": ot_pay, "al": allowance,
                                "bhxh": bhxh, "bhyt": bhyt, "bhtn": bhtn, "net": net_pay
                            })
                        st.success(L["msg_success"])
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 寫入資料庫失敗: {str(e)}")

    # ----------------------------------------------------
    # 📊 Tab 2: 歷史薪資清冊查詢
    # ----------------------------------------------------
    with tab_history:
        st.markdown(f"#### {L['header_summary']}")
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("""
                        SELECT payroll_month, emp_code, emp_name, department, base_salary, overtime_pay, allowance, (bhxh_deduction + bhyt_deduction + bhtn_deduction) as total_insurance, net_salary, status
                        FROM public.payroll_records
                        ORDER BY payroll_month DESC, emp_code ASC
                    """))
                    rows = res.fetchall()
                    if rows:
                        df_p = pd.DataFrame(rows, columns=["計薪月份", "工號", "姓名", "部門", "底薪", "加班費", "津貼", "保險扣除", "實發淨薪", "狀態"])
                        st.dataframe(df_p, use_container_width=True)
                    else:
                        st.info("目前尚無歷史薪資紀錄。")
            except Exception:
                st.info("尚未讀取到歷史薪資紀錄。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_payroll_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_payroll_management_page(engine=engine, lang=lang, **kwargs)
