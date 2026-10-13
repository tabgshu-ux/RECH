import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🇻🇳 越南法規標準金額格式化 (千位數用 '.'，例如: 13.507.200)
# ----------------------------------------------------
def parse_vn_num(val_str):
    """將包含 '.' 或 ',' 的字串轉回純數字 float"""
    if isinstance(val_str, (int, float)):
        return float(val_str)
    if not val_str:
        return 0.0
    # 移除所有點號與逗號空格
    cleaned = str(val_str).replace(".", "").replace(",", "").replace("VND", "").strip()
    try:
        return float(cleaned)
    except Exception:
        return 0.0

def fmt_vn_num(val):
    """格式化為越南法規金額數字 (例如: 13.507.200)"""
    try:
        v = float(val)
        return f"{v:,.0f}".replace(",", ".")
    except Exception:
        return "0"

def fmt_vn_curr(val):
    """格式化為越南法規金額 (例如: 13.507.200 VND)"""
    return fmt_vn_num(val) + " VND"

# ----------------------------------------------------
# 🌐 員工薪資與保險扣除管理多語系字典 (i18n)
# ----------------------------------------------------
PAYROLL_I18N = {
    "繁體中文": {
        "title": "💰 管理部 - 員工薪資計算與電子薪資單中心",
        "caption": "符合越南勞動法與 2026/09 最新薪資結構：支援 6 大津貼、4 階梯加班費、全勤獎金條件試算、社保/醫保/失業保扣繳與電子薪資單 (金額採 '.' 千位分隔)。",
        "tab_calc": "🧮 月度薪資試算與結算",
        "tab_slip": "📄 個人電子薪資單 (Phiếu lương)",
        "tab_history": "📊 歷史薪資清冊與發放紀錄",
        "lbl_month": "計薪月份 (YYYY-MM)",
        "lbl_emp_code": "員工工號 / 人事編號",
        "lbl_emp_name": "員工姓名",
        "lbl_dept": "所屬部門",
        "lbl_factory": "工作廠區",
        "lbl_base_salary": "約定底薪 Lương cb (VND)",
        "lbl_standard_hours": "標準上班時數 (預設 208 小時)",
        "lbl_actual_hours": "實際上班時數 (小時)",
        "lbl_allowance_pos": "職務津貼 Phụ cấp chức vụ (VND)",
        "lbl_allowance_eval": "評核獎金 Tiền thưởng đánh giá (VND)",
        "lbl_allowance_gas": "出差油費 Phụ Cấp Xăng (VND)",
        "lbl_allowance_women": "女性津貼 Phụ cấp phụ nữ (VND)",
        "lbl_allowance_spec": "專業獎金 Tiền thưởng chuyên môn (VND)",
        "lbl_meal_fee": "伙食費 Tiền cơm (VND)",
        "lbl_network_fee": "電話/網路費補貼 PC đt/mạng (VND)",
        "lbl_prod_bonus": "績效獎金 Thưởng năng suất (VND)",
        "lbl_ot15": "加班 1.5 倍時數 (小時)",
        "lbl_ot195": "加班 1.95 倍時數 (小時)",
        "lbl_ot20": "加班 2.0 倍時數 (小時)",
        "lbl_ot30": "加班 3.0 倍時數 (小時)",
        "lbl_advance": "本月預支金額 Tạm ứng (VND)",
        "lbl_other_deduct": "其他扣款 Khoản trừ (VND)",
        "btn_calc_and_save": "💾 計算並寫入 Supabase 薪資資料庫",
        "msg_success": "✅ 薪資清冊計算完畢並已成功寫入資料庫！",
        "lbl_net_pay": "💵 本月應發實領金額 (Thực lãnh)",
        "header_summary": "📋 歷史月度薪資與保險扣除統計表"
    },
    "Tiếng Việt": {
        "title": "💰 Phòng Quản lý - Tính Luơng & Phiếu Lương Điện Tử",
        "caption": "Tuân thủ Luật Lao động VN & Bảng lương 09/2026: Phụ cấp, Tăng ca 4 hệ số, Chuyên cần, BHXH/BHYT/BHTN và Phiếu lương cá nhân.",
        "tab_calc": "🧮 Tính lương & Tăng ca",
        "tab_slip": "📄 Phiếu Lương Cá Nhân",
        "tab_history": "📊 Lịch sử bảng lương & Báo cáo",
        "lbl_month": "Tháng tính lương (YYYY-MM)",
        "lbl_emp_code": "Mã nhân viên (MNS)",
        "lbl_emp_name": "Tên nhân viên",
        "lbl_dept": "Phòng ban",
        "lbl_factory": "Nhà máy",
        "lbl_base_salary": "Lương cơ bản (VND)",
        "lbl_standard_hours": "Số giờ LV chuẩn (208 giờ)",
        "lbl_actual_hours": "Số giờ thực làm (Giờ)",
        "lbl_allowance_pos": "Phụ cấp chức vụ (VND)",
        "lbl_allowance_eval": "Tiền thưởng đánh giá (VND)",
        "lbl_allowance_gas": "Phụ cấp xăng (VND)",
        "lbl_allowance_women": "Phụ cấp phụ nữ (VND)",
        "lbl_allowance_spec": "Tiền thưởng chuyên môn (VND)",
        "lbl_meal_fee": "Tiền cơm (VND)",
        "lbl_network_fee": "Phụ cấp điện thoại/mạng (VND)",
        "lbl_prod_bonus": "Thưởng năng suất (VND)",
        "lbl_ot15": "Số giờ tăng ca 1.5",
        "lbl_ot195": "Số giờ tăng ca 1.95",
        "lbl_ot20": "Số giờ tăng ca 2.0",
        "lbl_ot30": "Số giờ tăng ca 3.0",
        "lbl_advance": "Số tiền tạm ứng (VND)",
        "lbl_other_deduct": "Khoản trừ khác (VND)",
        "btn_calc_and_save": "💾 Tính & Lưu Bảng Lương vào Cơ Sở Dữ Liệu",
        "msg_success": "✅ Đã tính lương và lưu bảng lương thành công!",
        "lbl_net_pay": "💵 Lương thực lãnh (Thực lãnh)",
        "header_summary": "📋 Lịch sử Bảng lương & Bảo hiểm tháng"
    },
    "English": {
        "title": "💰 GA & HR - Payroll & Digital Payslip Management",
        "caption": "Vietnamese Labor Law Compliant (09/2026 Structure): Allowances, 4 OT rates, Attendance Bonus logic, Insurance and Digital Payslip.",
        "tab_calc": "🧮 Payroll & Overtime Calculation",
        "tab_slip": "📄 Individual Digital Payslip",
        "tab_history": "📊 Historical Payroll Records",
        "lbl_month": "Payroll Month (YYYY-MM)",
        "lbl_emp_code": "Employee Code",
        "lbl_emp_name": "Employee Name",
        "lbl_dept": "Department",
        "lbl_factory": "Work Plant",
        "lbl_base_salary": "Base Salary (VND)",
        "lbl_standard_hours": "Standard Work Hours (208h)",
        "lbl_actual_hours": "Actual Work Hours",
        "lbl_allowance_pos": "Position Allowance (VND)",
        "lbl_allowance_eval": "Evaluation Bonus (VND)",
        "lbl_allowance_gas": "Gasoline Allowance (VND)",
        "lbl_allowance_women": "Women Allowance (VND)",
        "lbl_allowance_spec": "Specialty Bonus (VND)",
        "lbl_meal_fee": "Meal Allowance (VND)",
        "lbl_network_fee": "Phone/Internet Subsidy (VND)",
        "lbl_prod_bonus": "Productivity Bonus (VND)",
        "lbl_ot15": "OT 1.5x Hours",
        "lbl_ot195": "OT 1.95x Hours",
        "lbl_ot20": "OT 2.0x Hours",
        "lbl_ot30": "OT 3.0x Hours",
        "lbl_advance": "Salary Advance (VND)",
        "lbl_other_deduct": "Other Deductions (VND)",
        "btn_calc_and_save": "💾 Calculate & Save to Database",
        "msg_success": "✅ Payroll calculation saved to database successfully!",
        "lbl_net_pay": "💵 Net Pay (Thực lãnh)",
        "header_summary": "📋 Monthly Payroll & Insurance Summary"
    }
}

def calculate_attendance_bonus(actual_hours):
    """Excel 公式全勤獎金算式: IF(H>=207, 400000, IF(204<=H<=206.5, 200000, 0))"""
    if actual_hours >= 207:
        return 400000.0
    elif 204 <= actual_hours <= 206.5:
        return 200000.0
    return 0.0

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
                    factory VARCHAR(100) DEFAULT '西寧廠 (Tay Ninh)',
                    base_salary NUMERIC(12,2) DEFAULT 0,
                    pos_allowance NUMERIC(12,2) DEFAULT 0,
                    eval_bonus NUMERIC(12,2) DEFAULT 0,
                    gas_allowance NUMERIC(12,2) DEFAULT 0,
                    women_allowance NUMERIC(12,2) DEFAULT 0,
                    spec_bonus NUMERIC(12,2) DEFAULT 0,
                    actual_hours NUMERIC(6,2) DEFAULT 208,
                    work_salary NUMERIC(12,2) DEFAULT 0,
                    overtime_pay NUMERIC(12,2) DEFAULT 0,
                    meal_fee NUMERIC(12,2) DEFAULT 0,
                    prod_bonus NUMERIC(12,2) DEFAULT 0,
                    network_fee NUMERIC(12,2) DEFAULT 0,
                    attendance_bonus NUMERIC(12,2) DEFAULT 0,
                    other_deduct NUMERIC(12,2) DEFAULT 0,
                    total_gross NUMERIC(12,2) DEFAULT 0,
                    bhxh_deduction NUMERIC(12,2) DEFAULT 0,
                    bhyt_deduction NUMERIC(12,2) DEFAULT 0,
                    bhtn_deduction NUMERIC(12,2) DEFAULT 0,
                    pit_tax NUMERIC(12,2) DEFAULT 0,
                    advance_pay NUMERIC(12,2) DEFAULT 0,
                    net_salary NUMERIC(12,2) NOT NULL,
                    status VARCHAR(50) DEFAULT '🟢 已結算 (Calculated)',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_emp_payroll_month UNIQUE (payroll_month, emp_code)
                );
            """))
    except Exception as e:
        st.warning("⚠️ 資料庫 Table 初始化提示: " + str(e))

def render_payroll_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = PAYROLL_I18N.get(active_lang, PAYROLL_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_payroll_db(engine)

    tab_calc, tab_slip, tab_history = st.tabs([L["tab_calc"], L["tab_slip"], L["tab_history"]])

    # ----------------------------------------------------
    # 🧮 Tab 1: 月度薪資與多階梯加班自動核算
    # ----------------------------------------------------
    with tab_calc:
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        with c_m1:
            payroll_m = st.text_input(L["lbl_month"], value=datetime.datetime.now().strftime("%Y-%m"))
        with c_m2:
            e_code = st.text_input(L["lbl_emp_code"], value="2007031201")
        with c_m3:
            dept_name = st.selectbox(L["lbl_dept"], ["👔 管理部", "🛠️ 工程部", "🏭 生產部", "📈 總經理室", "💻 資訊部"])
        with c_m4:
            st.text_input(L["lbl_factory"], value="西寧廠 (Tay Ninh)", disabled=True)

        st.markdown("---")
        
        with st.form("form_calc_payroll"):
            st.markdown("##### 1️⃣ 基本薪資與 6 大津貼項目 (Lương & Phụ cấp) - 採越南 '.' 千位分隔")
            col1, col2, col3 = st.columns(3)
            with col1:
                e_name = st.text_input(L["lbl_emp_name"], value="NGUYỄN THỊ TUYẾT NHUNG")
                str_base_sal = st.text_input(L["lbl_base_salary"], value="13.507.200")
                str_pos_allowance = st.text_input(L["lbl_allowance_pos"], value="3.000.000")
            with col2:
                str_eval_bonus = st.text_input(L["lbl_allowance_eval"], value="3.174.192")
                str_gas_allowance = st.text_input(L["lbl_allowance_gas"], value="144.000")
                str_women_allowance = st.text_input(L["lbl_allowance_women"], value="100.000")
            with col3:
                str_spec_bonus = st.text_input(L["lbl_allowance_spec"], value="500.000")
                std_hours = st.number_input(L["lbl_standard_hours"], min_value=1.0, value=208.0, step=1.0)
                act_hours = st.number_input(L["lbl_actual_hours"], min_value=0.0, value=208.0, step=0.5)

            st.markdown("##### 2️⃣ 四階梯加班費與補助項目 (Tăng ca & Subsidies)")
            col4, col5, col6 = st.columns(3)
            with col4:
                ot_15 = st.number_input(L["lbl_ot15"], min_value=0.0, value=0.0, step=0.5)
                ot_195 = st.number_input(L["lbl_ot195"], min_value=0.0, value=0.0, step=0.5)
                ot_20 = st.number_input(L["lbl_ot20"], min_value=0.0, value=0.0, step=0.5)
                ot_30 = st.number_input(L["lbl_ot30"], min_value=0.0, value=0.0, step=0.5)
            with col5:
                str_meal_fee = st.text_input(L["lbl_meal_fee"], value="648.000")
                str_prod_bonus = st.text_input(L["lbl_prod_bonus"], value="0")
                str_network_fee = st.text_input(L["lbl_network_fee"], value="300.000")
            with col6:
                auto_att_bonus = calculate_attendance_bonus(act_hours)
                str_att_bonus = st.text_input("全勤獎金 Chuyên cần (自動試算)", value=fmt_vn_num(auto_att_bonus))
                str_other_deduct = st.text_input(L["lbl_other_deduct"], value="0")
                str_advance_pay = st.text_input(L["lbl_advance"], value="0")

            # ----------------------------------------------------
            # 🧮 轉為數值計算
            # ----------------------------------------------------
            base_sal = parse_vn_num(str_base_sal)
            pos_allowance = parse_vn_num(str_pos_allowance)
            eval_bonus = parse_vn_num(str_eval_bonus)
            gas_allowance = parse_vn_num(str_gas_allowance)
            women_allowance = parse_vn_num(str_women_allowance)
            spec_bonus = parse_vn_num(str_spec_bonus)
            meal_fee = parse_vn_num(str_meal_fee)
            prod_bonus = parse_vn_num(str_prod_bonus)
            network_fee = parse_vn_num(str_network_fee)
            att_bonus = parse_vn_num(str_att_bonus)
            other_deduct = parse_vn_num(str_other_deduct)
            advance_pay = parse_vn_num(str_advance_pay)

            # Excel 精確算式核心邏輯
            hourly_base_rate = (base_sal + pos_allowance + eval_bonus + gas_allowance + women_allowance + spec_bonus) / std_hours
            work_salary = hourly_base_rate * act_hours

            ot_pay = (ot_15 * hourly_base_rate * 1.5) + (ot_195 * hourly_base_rate * 1.95) + (ot_20 * hourly_base_rate * 2.0) + (ot_30 * hourly_base_rate * 3.0)

            total_gross = work_salary + ot_pay + meal_fee + prod_bonus + network_fee + att_bonus - other_deduct

            bhxh = base_sal * 0.08
            bhyt = base_sal * 0.015
            bhtn = base_sal * 0.01
            total_insurance = bhxh + bhyt + bhtn

            net_pay = total_gross - total_insurance - advance_pay

            st.markdown("---")
            st.markdown("##### 📊 薪資試算精準結果：")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("上班工工資 (Cộng lương)", fmt_vn_curr(work_salary))
            m2.metric("加班費總額 (Tăng ca)", fmt_vn_curr(ot_pay))
            m3.metric("應領總額 (Tổng lương)", fmt_vn_curr(total_gross))
            m4.metric(L["lbl_net_pay"], fmt_vn_curr(net_pay))

            if st.form_submit_button(L["btn_calc_and_save"], type="primary", use_container_width=True):
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.payroll_records 
                                (payroll_month, emp_code, emp_name, department, factory, base_salary, pos_allowance, eval_bonus, 
                                 gas_allowance, women_allowance, spec_bonus, actual_hours, work_salary, overtime_pay, 
                                 meal_fee, prod_bonus, network_fee, attendance_bonus, other_deduct, total_gross, 
                                 bhxh_deduction, bhyt_deduction, bhtn_deduction, advance_pay, net_salary)
                                VALUES (:m, :code, :name, :dept, '西寧廠 (Tay Ninh)', :bs, :pos, :ev, :gas, :wom, :spec, :act_h,
                                        :ws, :ot, :meal, :prod, :net_f, :att, :od, :gross, :bhxh, :bhyt, :bhtn, :adv, :net)
                                ON CONFLICT (payroll_month, emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    department = EXCLUDED.department,
                                    base_salary = EXCLUDED.base_salary,
                                    pos_allowance = EXCLUDED.pos_allowance,
                                    eval_bonus = EXCLUDED.eval_bonus,
                                    gas_allowance = EXCLUDED.gas_allowance,
                                    women_allowance = EXCLUDED.women_allowance,
                                    spec_bonus = EXCLUDED.spec_bonus,
                                    actual_hours = EXCLUDED.actual_hours,
                                    work_salary = EXCLUDED.work_salary,
                                    overtime_pay = EXCLUDED.overtime_pay,
                                    meal_fee = EXCLUDED.meal_fee,
                                    prod_bonus = EXCLUDED.prod_bonus,
                                    network_fee = EXCLUDED.network_fee,
                                    attendance_bonus = EXCLUDED.attendance_bonus,
                                    other_deduct = EXCLUDED.other_deduct,
                                    total_gross = EXCLUDED.total_gross,
                                    bhxh_deduction = EXCLUDED.bhxh_deduction,
                                    bhyt_deduction = EXCLUDED.bhyt_deduction,
                                    bhtn_deduction = EXCLUDED.bhtn_deduction,
                                    advance_pay = EXCLUDED.advance_pay,
                                    net_salary = EXCLUDED.net_salary,
                                    updated_at = CURRENT_TIMESTAMP;
                            """), {
                                "m": payroll_m, "code": e_code, "name": e_name, "dept": dept_name,
                                "bs": base_sal, "pos": pos_allowance, "ev": eval_bonus, "gas": gas_allowance,
                                "wom": women_allowance, "spec": spec_bonus, "act_h": act_hours,
                                "ws": work_salary, "ot": ot_pay, "meal": meal_fee, "prod": prod_bonus,
                                "net_f": network_fee, "att": att_bonus, "od": other_deduct, "gross": total_gross,
                                "bhxh": bhxh, "bhyt": bhyt, "bhtn": bhtn, "adv": advance_pay, "net": net_pay
                            })
                        st.success(L["msg_success"])
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入資料庫失敗: " + str(e))
                else:
                    st.success("✅ 試算完成（展示模式）。")

    # ----------------------------------------------------
    # 📄 Tab 2: 個人電子薪資單 (Phiếu lương)
    # ----------------------------------------------------
    with tab_slip:
        st.markdown("### 📄 員工個人電子薪資單預覽 (Phiếu Lương Cá Nhân)")
        st.caption("適應手機端螢幕展示，符合越南財政部 (Thông tư 200) 格式規範。")

        total_allowance_sum = pos_allowance + eval_bonus + gas_allowance + women_allowance + spec_bonus

        with st.container(border=True):
            st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>CÔNG TY TNHH CN DŨ PHONG</h3>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center;'>PHIẾU LƯƠNG THÁNG " + str(payroll_m) + " (TÂY NINH)</h4>", unsafe_allow_html=True)
            st.markdown("---")

            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**MNS / 工號:** `" + str(e_code) + "`")
                st.write("**Họ tên / 姓名:** **" + str(e_name) + "**")
                st.write("**Bộ phận / 部門:** " + str(dept_name))
                st.write("**Số giờ thực làm / 實際時數:** " + str(act_hours) + " 小時")
            with col_b:
                st.write("**Lương cb / 底薪:** " + fmt_vn_curr(base_sal))
                st.write("**Tổng phụ cấp / 各項津貼:** " + fmt_vn_curr(total_allowance_sum))
                st.write("**Chuyên cần / 全勤獎金:** " + fmt_vn_curr(att_bonus))
                st.write("**Tiền cơm / 伙食費:** " + fmt_vn_curr(meal_fee))

            st.markdown("---")
            col_c, col_d, col_e = st.columns(3)
            col_c.metric("Tổng lương (應領總計)", fmt_vn_curr(total_gross))
            col_d.metric("BHXH/BHYT/BHTN (保險扣款)", fmt_vn_curr(total_insurance))
            col_e.metric("Thực lãnh (實領金額)", fmt_vn_curr(net_pay), delta="🟢 已核對無誤")

    # ----------------------------------------------------
    # 📊 Tab 3: 歷史薪資清冊查詢
    # ----------------------------------------------------
    with tab_history:
        st.markdown("#### " + str(L["header_summary"]))
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("""
                        SELECT payroll_month, emp_code, emp_name, department, factory, base_salary, work_salary, overtime_pay, total_gross, (bhxh_deduction + bhyt_deduction + bhtn_deduction) as total_insurance, net_salary, status
                        FROM public.payroll_records
                        ORDER BY payroll_month DESC, emp_code ASC
                    """))
                    rows = res.fetchall()
                    if rows:
                        formatted_rows = []
                        for r in rows:
                            row_dict = dict(r._mapping)
                            row_dict["底薪"] = fmt_vn_curr(row_dict.get("base_salary", 0))
                            row_dict["上班工資"] = fmt_vn_curr(row_dict.get("work_salary", 0))
                            row_dict["加班費"] = fmt_vn_curr(row_dict.get("overtime_pay", 0))
                            row_dict["應領總額"] = fmt_vn_curr(row_dict.get("total_gross", 0))
                            row_dict["保險扣除"] = fmt_vn_curr(row_dict.get("total_insurance", 0))
                            row_dict["實發淨薪"] = fmt_vn_curr(row_dict.get("net_salary", 0))
                            formatted_rows.append(row_dict)

                        df_p = pd.DataFrame(formatted_rows)[["payroll_month", "emp_code", "emp_name", "department", "factory", "底薪", "上班工資", "加班費", "應領總額", "保險扣除", "實發淨薪", "status"]]
                        df_p.columns = ["計薪月份", "工號", "姓名", "部門", "廠區", "底薪", "上班工資", "加班費", "應領總額", "保險扣除", "實發淨薪", "狀態"]
                        st.dataframe(df_p, use_container_width=True)
                    else:
                        st.info("目前尚無歷史薪資紀錄。")
            except Exception as e:
                st.info("尚未讀取到歷史薪資紀錄: " + str(e))
        else:
            st.info("目前展示模式，請連接 PostgreSQL / Supabase 以讀取歷史紀錄。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_payroll_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_payroll_management_page(engine=engine, lang=lang, **kwargs)
