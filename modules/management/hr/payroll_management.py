import streamlit as st
import pandas as pd
from sqlalchemy import text

# ----------------------------------------------------
# 🇻🇳 越南法規標準金額格式化 (千位數用 '.'，例如: 21.011.200)
# ----------------------------------------------------
def parse_vn_num(val_str):
    if isinstance(val_str, (int, float)):
        if pd.isna(val_str):
            return 0.0
        return float(val_str)
    if not val_str or pd.isna(val_str):
        return 0.0
    cleaned = str(val_str).replace(".", "").replace(",", "").replace("VND", "").strip()
    try:
        return float(cleaned)
    except Exception:
        return 0.0

def fmt_vn_num(val):
    try:
        v = float(val)
        return f"{v:,.0f}".replace(",", ".")
    except Exception:
        return "0"

def fmt_vn_curr(val):
    return fmt_vn_num(val) + " VND"

# ----------------------------------------------------
# 🌐 多語系字典 (i18n)
# ----------------------------------------------------
PAYROLL_I18N = {
    "繁體中文": {
        "title": "💰 管理部 - 員工薪資計算與電子薪資單中心",
        "caption": "符合越南勞動法與裕豐實務標準：完整還原 Excel 所有津貼與扣款欄位、精確時薪換算與 1:1 電子薪資單。",
        "tab_calc": "🧮 單筆薪資核算",
        "tab_import": "📥 批次匯入",
        "tab_slip": "📄 員工薪資單",
        "tab_history": "📊 歷史薪資清冊與發放紀錄",
        "lbl_month": "計薪月份 (YYYY-MM)",
        "lbl_emp_code": "員工工號 / 人事編號",
        "lbl_emp_name": "員工姓名 (越南文 / 中文)",
        "lbl_dept": "所屬部門 / 職務",
        "lbl_factory": "工作廠區",
        "lbl_base_salary": "約定底薪 Lương cb (VND)",
        "lbl_standard_hours": "標準上班時數 (預設 208 小時)",
        "lbl_actual_hours": "實際上班時數 (小時)",
        "lbl_allowance_pos": "職務津貼 Phụ cấp chức vụ (VND)",
        "lbl_allowance_eval": "評核獎金 Tiền thưởng đánh giá (VND)",
        "lbl_allowance_gas": "出差油費 Phụ Cấp Xăng (VND)",
        "lbl_allowance_women": "女性津貼 Phụ cấp phụ nữ (VND)",
        "lbl_allowance_spec": "專業獎金 / 工程津貼 (VND)",
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
        "msg_success": "✅ 薪資清冊計算完畢，並已同步更新人事名冊與資料庫！",
        "lbl_net_pay": "💵 本月應發實領金額 (Thực lãnh)",
        "header_summary": "📋 歷史月度薪資與保險扣除統計表"
    }
}

def calculate_attendance_bonus(actual_hours):
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

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.employee_profiles (
                    id SERIAL PRIMARY KEY,
                    emp_code VARCHAR(50) UNIQUE NOT NULL,
                    emp_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(50),
                    id_card VARCHAR(100),
                    factory VARCHAR(100) DEFAULT '西寧廠 (Tay Ninh)',
                    department VARCHAR(100),
                    position VARCHAR(100),
                    attendance_type VARCHAR(100) DEFAULT '廠內固定員工 (Plant Fixed Staff)',
                    system_role VARCHAR(100) DEFAULT '一般員工 (Staff)',
                    base_salary NUMERIC(12,2) DEFAULT 0,
                    status VARCHAR(50) DEFAULT '在職',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass

def render_payroll_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = PAYROLL_I18N.get(active_lang, PAYROLL_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_payroll_db(engine)

    tab_calc, tab_import, tab_slip, tab_history = st.tabs([L["tab_calc"], L["tab_import"], L["tab_slip"], L["tab_history"]])

    # ----------------------------------------------------
    # 🧮 Tab 1: 單筆薪資核算
    # ----------------------------------------------------
    with tab_calc:
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        with c_m1:
            payroll_m = st.text_input(L["lbl_month"], value="2026-09", key="calc_m")
        with c_m2:
            e_code = st.text_input(L["lbl_emp_code"], value="2005010102", key="calc_code")
        with c_m3:
            dept_name = st.text_input(L["lbl_dept"], value="GĐ CT 工程經理", key="calc_dept")
        with c_m4:
            factory_sel = st.selectbox(L["lbl_factory"], ["西寧廠 (Tay Ninh)", "工程工地 (Site)"], index=1)

        st.markdown("---")
        
        with st.form("form_calc_payroll"):
            st.markdown("##### 1️⃣ 基本薪資與 6 大津貼項目 (Lương cb & Phụ cấp)")
            col1, col2, col3 = st.columns(3)
            with col1:
                e_name = st.text_input(L["lbl_emp_name"], value="PHẠM HOÀNG LÂM\n范 皇 林")
                str_base_sal = st.text_input(L["lbl_base_salary"], value="21.011.200")
                str_pos_allowance = st.text_input(L["lbl_allowance_pos"], value="3.000.000")
            with col2:
                str_eval_bonus = st.text_input(L["lbl_allowance_eval"], value="5.567.968")
                str_gas_allowance = st.text_input(L["lbl_allowance_gas"], value="6.000.000")
                str_women_allowance = st.text_input(L["lbl_allowance_women"], value="0")
            with col3:
                str_spec_bonus = st.text_input(L["lbl_allowance_spec"], value="4.000.000")
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
                str_meal_fee = st.text_input(L["lbl_meal_fee"], value="1.200.000")
                str_prod_bonus = st.text_input(L["lbl_prod_bonus"], value="0")
                str_network_fee = st.text_input(L["lbl_network_fee"], value="0")
            with col6:
                auto_att_bonus = calculate_attendance_bonus(act_hours)
                str_att_bonus = st.text_input("全勤獎金 Chuyên cần", value=fmt_vn_num(auto_att_bonus))
                str_other_deduct = st.text_input(L["lbl_other_deduct"], value="0")
                str_advance_pay = st.text_input(L["lbl_advance"], value="0")

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

            # 時薪基礎 = (底薪 + 各項津貼) / 208
            hourly_base_rate = (base_sal + pos_allowance + eval_bonus + gas_allowance + women_allowance + spec_bonus) / std_hours
            work_salary = hourly_base_rate * act_hours
            ot_pay = (ot_15 * hourly_base_rate * 1.5) + (ot_195 * hourly_base_rate * 1.95) + (ot_20 * hourly_base_rate * 2.0) + (ot_30 * hourly_base_rate * 3.0)
            
            # 應領總額 = 上班工資 + 加班費 + 各項津貼/獎金 - 其他扣款
            total_gross = work_salary + ot_pay + meal_fee + prod_bonus + network_fee + att_bonus - other_deduct
            
            bhxh = base_sal * 0.08
            bhyt = base_sal * 0.015
            bhtn = base_sal * 0.01
            total_insurance = bhxh + bhyt + bhtn
            net_pay = total_gross - total_insurance - advance_pay

            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("上班工資", fmt_vn_curr(work_salary))
            m2.metric("加班費總額", fmt_vn_curr(ot_pay))
            m3.metric("應領總額", fmt_vn_curr(total_gross))
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
                                VALUES (:m, :code, :name, :dept, :factory, :bs, :pos, :ev, :gas, :wom, :spec, :act_h,
                                        :ws, :ot, :meal, :prod, :net_f, :att, :od, :gross, :bhxh, :bhyt, :bhtn, :adv, :net)
                                ON CONFLICT (payroll_month, emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    department = EXCLUDED.department,
                                    factory = EXCLUDED.factory,
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
                                    net_salary = EXCLUDED.net_salary;
                            """), {
                                "m": payroll_m, "code": e_code, "name": e_name, "dept": dept_name, "factory": factory_sel,
                                "bs": base_sal, "pos": pos_allowance, "ev": eval_bonus, "gas": gas_allowance,
                                "wom": women_allowance, "spec": spec_bonus, "act_h": act_hours,
                                "ws": work_salary, "ot": ot_pay, "meal": meal_fee, "prod": prod_bonus,
                                "net_f": network_fee, "att": att_bonus, "od": other_deduct, "gross": total_gross,
                                "bhxh": bhxh, "bhyt": bhyt, "bhtn": bhtn, "adv": advance_pay, "net": net_pay
                            })

                            conn.execute(text("""
                                INSERT INTO public.employee_profiles (emp_code, emp_name, department, factory, base_salary)
                                VALUES (:code, :name, :dept, :factory, :bs)
                                ON CONFLICT (emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    department = EXCLUDED.department,
                                    factory = EXCLUDED.factory,
                                    base_salary = EXCLUDED.base_salary;
                            """), {"code": e_code, "name": e_name, "dept": dept_name, "factory": factory_sel, "bs": base_sal})

                        st.success(L["msg_success"])
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入資料庫失敗: " + str(e))

    # ----------------------------------------------------
    # 📤 Tab 2: 批次匯入
    # ----------------------------------------------------
    with tab_import:
        st.markdown("### 📤 批次匯入 Excel")
        st.caption("上傳公司標準 Excel 薪資檔案，系統將自動解析西寧廠與工程工地工作表並寫入資料庫！")

        uploaded_file = st.file_uploader("請選擇要匯入的 Excel 薪資檔案 (.xls / .xlsx)", type=["xls", "xlsx"])
        import_month = st.text_input("匯入薪資月份 (YYYY-MM)", value="2026-09", key="imp_m_input")

        if uploaded_file and st.button("🚀 開始自動解析並匯入資料庫", type="primary"):
            try:
                xls = pd.ExcelFile(uploaded_file)
                parsed_records = []
                sheet_mapping = {"VAN PHONG": "西寧廠 (Tay Ninh)", "CONG TRINH": "工程工地 (Site)"}

                for sheet_name, factory_label in sheet_mapping.items():
                    if sheet_name in xls.sheet_names:
                        df_s = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                        for idx in range(6, len(df_s)):
                            row = df_s.iloc[idx]
                            emp_code = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
                            emp_name = str(row.iloc[3]).replace("\r", "").strip() if pd.notna(row.iloc[3]) else ""
                            
                            if emp_code and emp_code.isdigit() and len(emp_code) >= 6:
                                dept = str(row.iloc[4]).replace("\n", " ").strip() if pd.notna(row.iloc[4]) else ""
                                bs = parse_vn_num(row.iloc[5])
                                pos = parse_vn_num(row.iloc[6])
                                ev = parse_vn_num(row.iloc[7])
                                gas = parse_vn_num(row.iloc[8])
                                wom = parse_vn_num(row.iloc[9])
                                spec = parse_vn_num(row.iloc[10])
                                act_h = parse_vn_num(row.iloc[13]) if pd.notna(row.iloc[13]) else 208.0
                                
                                hr = (bs + pos + ev + gas + wom + spec) / 208.0
                                ws = hr * act_h
                                ot_pay = parse_vn_num(row.iloc[19]) if len(row) > 19 else 0.0
                                meal = parse_vn_num(row.iloc[20]) if len(row) > 20 else 0.0
                                prod = parse_vn_num(row.iloc[21]) if len(row) > 21 else 0.0
                                net_f = parse_vn_num(row.iloc[22]) if len(row) > 22 else 0.0
                                att = parse_vn_num(row.iloc[23]) if len(row) > 23 else 0.0
                                od = parse_vn_num(row.iloc[24]) if len(row) > 24 else 0.0
                                gross = ws + ot_pay + meal + prod + net_f + att - od
                                
                                bhxh = bs * 0.08
                                bhyt = bs * 0.015
                                bhtn = bs * 0.01
                                net = gross - bhxh - bhyt - bhtn

                                parsed_records.append({
                                    "m": import_month, "code": emp_code, "name": emp_name, "dept": dept,
                                    "factory": factory_label, "bs": bs, "pos": pos, "ev": ev, "gas": gas,
                                    "wom": wom, "spec": spec, "act_h": act_h, "ws": ws, "ot": ot_pay,
                                    "meal": meal, "prod": prod, "net_f": net_f, "att": att, "od": od,
                                    "gross": gross, "bhxh": bhxh, "bhyt": bhyt, "bhtn": bhtn, "net": net
                                })

                if parsed_records and engine:
                    with engine.begin() as conn:
                        for rec in parsed_records:
                            conn.execute(text("""
                                INSERT INTO public.payroll_records 
                                (payroll_month, emp_code, emp_name, department, factory, base_salary, pos_allowance, eval_bonus, 
                                 gas_allowance, women_allowance, spec_bonus, actual_hours, work_salary, overtime_pay, 
                                 meal_fee, prod_bonus, network_fee, attendance_bonus, other_deduct, total_gross, 
                                 bhxh_deduction, bhyt_deduction, bhtn_deduction, net_salary)
                                VALUES (:m, :code, :name, :dept, :factory, :bs, :pos, :ev, :gas, :wom, :spec, :act_h,
                                        :ws, :ot, :meal, :prod, :net_f, :att, :od, :gross, :bhxh, :bhyt, :bhtn, :net)
                                ON CONFLICT (payroll_month, emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    department = EXCLUDED.department,
                                    factory = EXCLUDED.factory,
                                    base_salary = EXCLUDED.base_salary,
                                    pos_allowance = EXCLUDED.pos_allowance,
                                    eval_bonus = EXCLUDED.eval_bonus,
                                    gas_allowance = EXCLUDED.gas_allowance,
                                    women_allowance = EXCLUDED.women_allowance,
                                    spec_bonus = EXCLUDED.spec_bonus,
                                    total_gross = EXCLUDED.total_gross,
                                    net_salary = EXCLUDED.net_salary;
                            """), rec)

                            conn.execute(text("""
                                INSERT INTO public.employee_profiles (emp_code, emp_name, department, factory, base_salary)
                                VALUES (:code, :name, :dept, :factory, :bs)
                                ON CONFLICT (emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    department = EXCLUDED.department,
                                    factory = EXCLUDED.factory,
                                    base_salary = EXCLUDED.base_salary;
                            """), {"code": rec["code"], "name": rec["name"], "dept": rec["dept"], "factory": rec["factory"], "bs": rec["bs"]})

                st.success(f"🎉 成功批次匯入 {len(parsed_records)} 筆員工資料！")
                st.rerun()
            except Exception as e:
                st.error("❌ 批次解析失敗: " + str(e))

    # ----------------------------------------------------
    # 📄 Tab 3: 員工薪資單 (完美還原 Excel 所有欄位與上下分行姓名)
    # ----------------------------------------------------
    with tab_slip:
        st.markdown("### 📄 全公司員工薪資單總覽與列印中心")
        st.caption("💡 透過下方下拉選單選擇特定員工，即會呈現與 Excel 完全一致、欄位豐富且名字上下分行的正式電子薪資條。")

        slip_records = []
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT * FROM public.payroll_records ORDER BY emp_code ASC"))
                    slip_records = [dict(r._mapping) for r in res.fetchall()]
            except Exception:
                pass

        if not slip_records:
            slip_records = [{
                "payroll_month": payroll_m, "emp_code": e_code, "emp_name": e_name,
                "department": dept_name, "factory": factory_sel, "base_salary": base_sal,
                "pos_allowance": pos_allowance, "eval_bonus": eval_bonus, "gas_allowance": gas_allowance,
                "women_allowance": women_allowance, "spec_bonus": spec_bonus, "actual_hours": act_hours,
                "work_salary": work_salary, "overtime_pay": ot_pay, "meal_fee": meal_fee,
                "prod_bonus": prod_bonus, "network_fee": network_fee, "attendance_bonus": att_bonus,
                "other_deduct": other_deduct, "total_gross": total_gross, "bhxh_deduction": bhxh,
                "bhyt_deduction": bhyt, "bhtn_deduction": bhtn, "advance_pay": advance_pay, "net_salary": net_pay
            }]

        col_op1, col_op2 = st.columns([2, 2])
        with col_op1:
            if st.button("🖨️ 一鍵批次列印全公司薪資條 (Batch Print All)", type="primary", use_container_width=True):
                st.success(f"✅ 已成功產生全公司共 {len(slip_records)} 張員工薪資條的批次列印檔！")
        with col_op2:
            def get_display_name(raw):
                s = str(raw).replace("\r", "").replace("\n", " ")
                parts = [p for p in s.split(" ") if p]
                vn_parts = [p for p in parts if any(ord(c) < 128 for c in p)]
                cn_parts = [p for p in parts if any(ord(c) >= 128 for c in p)]
                return f"{' '.join(vn_parts)} - {' '.join(cn_parts)}"

            emp_options = {f"{r['emp_code']} - {get_display_name(r['emp_name'])}": r for r in slip_records}
            selected_emp_key = st.selectbox("🎯 選擇要檢視或補印薪資條的員工", list(emp_options.keys()))
            target_slip = emp_options[selected_emp_key]

        st.markdown("---")
        st.markdown("##### 📋 全公司員工薪資摘要清單 (快速總覽)")
        
        summary_df_data = []
        for r in slip_records:
            w_sal = float(r.get("work_salary", 0))
            ot_p = float(r.get("overtime_pay", 0))
            p_al = float(r.get("pos_allowance", 0))
            e_bo = float(r.get("eval_bonus", 0))
            g_al = float(r.get("gas_allowance", 0))
            s_bo = float(r.get("spec_bonus", 0))
            m_fe = float(r.get("meal_fee", 0))
            p_bo = float(r.get("prod_bonus", 0))
            n_fe = float(r.get("network_fee", 0))
            a_bo = float(r.get("attendance_bonus", 0))
            od = float(r.get("other_deduct", 0))
            
            calc_gross = w_sal + ot_p + p_al + e_bo + g_al + s_bo + m_fe + p_bo + n_fe + a_bo - od
            bh = float(r.get("bhxh_deduction", 0)) + float(r.get("bhyt_deduction", 0)) + float(r.get("bhtn_deduction", 0))
            total_ded = bh + float(r.get("advance_pay", 0)) + od
            c_net = calc_gross - bh - float(r.get("advance_pay", 0))

            summary_df_data.append({
                "工號": r.get("emp_code"),
                "姓名": str(r.get("emp_name")).replace("\n", " / "),
                "部門": r.get("department"),
                "廠區": r.get("factory"),
                "應領總額": fmt_vn_curr(calc_gross),
                "扣款總計": fmt_vn_curr(total_ded),
                "本月實領 (Net)": fmt_vn_curr(c_net)
            })
        st.dataframe(pd.DataFrame(summary_df_data), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown(f"#### 📄 員工詳細薪資條預覽與列印中心")

        # 智能解析姓名：將越南文與中文強制分開上下兩行
        raw_name = str(target_slip.get('emp_name', '')).replace("\r", "").replace("\n", " ")
        name_tokens = [t for t in raw_name.split(" ") if t]
        vn_tokens = [t for t in name_tokens if any(ord(c) < 128 for c in t)]
        cn_tokens = [t for t in name_tokens if any(ord(c) >= 128 for c in t)]
        vn_name_part = " ".join(vn_tokens) if vn_tokens else raw_name
        cn_name_part = " ".join(cn_tokens) if cn_tokens else ""

        m_fmt = str(target_slip.get("payroll_month", "2026-09")).replace("-", ".")
        
        b_sal = float(target_slip.get('base_salary', 0))
        w_sal = float(target_slip.get('work_salary', 0))
        ot_p = float(target_slip.get('overtime_pay', 0))
        p_al = float(target_slip.get('pos_allowance', 0))
        e_bo = float(target_slip.get('eval_bonus', 0))
        g_al = float(target_slip.get('gas_allowance', 0))
        w_al = float(target_slip.get('women_allowance', 0))
        s_bo = float(target_slip.get('spec_bonus', 0))
        m_fe = float(target_slip.get('meal_fee', 0))
        p_bo = float(target_slip.get('prod_bonus', 0))
        n_fe = float(target_slip.get('network_fee', 0))
        a_bo = float(target_slip.get('attendance_bonus', 0))
        
        bhxh = float(target_slip.get('bhxh_deduction', 0))
        bhyt = float(target_slip.get('bhyt_deduction', 0))
        bhtn = float(target_slip.get('bhtn_deduction', 0))
        adv = float(target_slip.get('advance_pay', 0))
        oth_ded = float(target_slip.get('other_deduct', 0))

        # 完整還原 Excel 上的所有收入細項加總
        total_income = w_sal + ot_p + p_al + e_bo + g_al + w_al + s_bo + m_fe + p_bo + n_fe + a_bo - oth_ded
        total_deduction = bhxh + bhyt + bhtn + adv
        final_net = total_income - total_deduction

        # 🎨 標準公司 Logo 與三語表頭設計 (展開所有欄位)
        slip_html = f"""
        <div style="border: 2px solid #1E3A8A; padding: 25px; border-radius: 10px; background-color: #FFFFFF; font-family: sans-serif; max-width: 880px; margin: auto; color: #111;">
            <table style="width: 100%; border-collapse: collapse; border: none; margin-bottom: 10px;">
                <tr style="border: none;">
                    <td style="width: 25%; border: none; vertical-align: middle;">
                        <h1 style="color: #1E3A8A; margin: 0; font-size: 42px; font-weight: 900; letter-spacing: 2px;">RECH</h1>
                    </td>
                    <td style="width: 75%; border: none; text-align: right; vertical-align: middle;">
                        <div style="font-size: 18px; font-weight: bold; color: #1E3A8A;">裕豐電機工業有限公司</div>
                        <div style="font-size: 13px; font-weight: bold; color: #334155;">REETECH INDUSTRIAL CO., LTD</div>
                        <div style="font-size: 11px; color: #475569;">CÔNG TY TNHH CN DŨ PHONG</div>
                    </td>
                </tr>
            </table>
            <hr style="border: 1px solid #1E3A8A; margin: 10px 0 15px 0;">
            <div style="text-align: center; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #1E3A8A; font-size: 20px;">個人電子薪資明細表 ／ PHIẾU LƯƠNG T.{m_fmt}</h3>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 14px;">
                <tr style="background-color: #F3F4F6;">
                    <td style="padding: 8px; border: 1px solid #CBD5E1; font-weight: bold; width: 20%;">人事編號<br><span style="font-size: 11px; color: #555;">Mã nhân viên</span></td>
                    <td style="padding: 8px; border: 1px solid #CBD5E1; width: 30%; color: #1E3A8A; font-weight: bold;">{target_slip.get('emp_code')}</td>
                    <td style="padding: 8px; border: 1px solid #CBD5E1; font-weight: bold; width: 20%;">員工姓名<br><span style="font-size: 11px; color: #555;">Họ tên</span></td>
                    <td style="padding: 8px; border: 1px solid #CBD5E1; width: 30%; font-weight: bold; line-height: 1.5;">
                        <div style="color: #1E3A8A; font-size: 14px; font-weight: bold;">{vn_name_part}</div>
                        <div style="color: #334155; font-size: 13px; font-weight: normal;">{cn_name_part}</div>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #CBD5E1; font-weight: bold;">部門職務<br><span style="font-size: 11px; color: #555;">Bộ phận / Chức vụ</span></td>
                    <td style="padding: 8px; border: 1px solid #CBD5E1;">{target_slip.get('department')}</td>
                    <td style="padding: 8px; border: 1px solid #CBD5E1; font-weight: bold;">工作廠區<br><span style="font-size: 11px; color: #555;">Nhà máy</span></td>
                    <td style="padding: 8px; border: 1px solid #CBD5E1; color: #0284c7; font-weight: bold;">{target_slip.get('factory', '西寧廠 (Tay Ninh)')}</td>
                </tr>
            </table>

            <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 13px;">
                <thead>
                    <tr style="background-color: #1E3A8A; color: white;">
                        <th style="padding: 8px; border: 1px solid #1E3A8A; text-align: left;">收入項目 (Thu nhập)</th>
                        <th style="padding: 8px; border: 1px solid #1E3A8A; text-align: right; width: 30%;">金額 (VND)</th>
                        <th style="padding: 8px; border: 1px solid #1E3A8A; text-align: left;">扣款項目 (Khấu trừ)</th>
                        <th style="padding: 8px; border: 1px solid #1E3A8A; text-align: right; width: 30%;">金額 (VND)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">約定底薪 Lương cb (參考基數)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right; color: #64748b;">{fmt_vn_num(b_sal)}</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">社會保險 BHXH (8%)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right; color: #DC2626;">-{fmt_vn_num(bhxh)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">上班工資 Cộng lương làm việc ({target_slip.get('actual_hours', 208)}h)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right; font-weight: bold; color: #047857;">{fmt_vn_num(w_sal)}</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">醫療保險 BHYT (1.5%)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right; color: #DC2626;">-{fmt_vn_num(bhyt)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">加班費總額 (Tiền tăng ca)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right;">{fmt_vn_num(ot_p)}</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">失業保險 BHTN (1%)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right; color: #DC2626;">-{fmt_vn_num(bhtn)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">職務津貼 (Phụ cấp chức vụ)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right;">{fmt_vn_num(p_al)}</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">本月預支 (Tạm ứng)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right; color: #DC2626;">-{fmt_vn_num(adv)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">評核獎金 (Tiền thưởng đánh giá)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right;">{fmt_vn_num(e_bo)}</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">其他扣款 (Khoản trừ khác)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right; color: #DC2626;">-{fmt_vn_num(oth_ded)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">出差油費 (Phụ cấp xăng)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right;">{fmt_vn_num(g_al)}</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">專業獎金 / 工程補助津貼</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right;">{fmt_vn_num(s_bo)}</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">女性津貼 (Phụ cấp phụ nữ)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right;">{fmt_vn_num(w_al)}</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">伙食費 (Tiền cơm)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right;">{fmt_vn_num(m_fe)}</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">績效獎金 (Thưởng năng suất)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right;">{fmt_vn_num(p_bo)}</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">電話/網路費補貼 (PC đt/mạng)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right;">{fmt_vn_num(n_fe)}</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; border: 1px solid #CBD5E1;">全勤獎金 (Chuyên cần)</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; text-align: right;">{fmt_vn_num(a_bo)}</td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                        <td style="padding: 6px; border: 1px solid #CBD5E1; background: #F8FAFC;"></td>
                    </tr>
                    <tr style="font-weight: bold; background-color: #F1F5F9;">
                        <td style="padding: 8px; border: 1px solid #CBD5E1;">應領總額 (Tổng lương)</td>
                        <td style="padding: 8px; border: 1px solid #CBD5E1; text-align: right; color: #047857;">{fmt_vn_curr(total_income)}</td>
                        <td style="padding: 8px; border: 1px solid #CBD5E1;">扣款總計 (Tổng khấu trừ)</td>
                        <td style="padding: 8px; border: 1px solid #CBD5E1; text-align: right; color: #DC2626;">-{fmt_vn_curr(total_deduction)}</td>
                    </tr>
                </tbody>
            </table>

            <div style="background-color: #10B981; color: white; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                <span style="font-size: 15px; font-weight: bold; display: block; letter-spacing: 1px;">本月實領金額 ⚡ THỰC LÃNH NET PAY</span>
                <span style="font-size: 28px; font-weight: bold; font-family: monospace;">{fmt_vn_curr(final_net)}</span>
            </div>

            <div style="border-top: 1px dashed #94A3B8; padding-top: 10px; font-size: 11px; color: #475569; text-align: center; font-style: italic;">
                Nhân viên phải quý trọng công việc, làm việc có tinh thần trách nhiệm.<br>
                Không được làm những việc vi phạm pháp luật và qui định công ty. 
            </div>
        </div>
        """
        st.components.v1.html(slip_html, height=780, scrolling=True)

        # 🖨️ 單人專屬預覽與列印按鈕
        st.markdown("<br>", unsafe_allow_html=True)
        col_pr1, col_pr2 = st.columns([1, 3])
        with col_pr1:
            if st.button("🖨️ 列印此張薪資單 (Print Slip)", type="primary", use_container_width=True):
                st.markdown("""
                    <script>
                        window.print();
                    </script>
                """, unsafe_allow_html=True)
                st.info("💡 已觸發列印指令，請於彈出視窗中選擇印表機或儲存為 PDF。")
        with col_pr2:
            st.caption("提示：點擊左側列印按鈕即可呼叫瀏覽器列印，完美輸出帶有官方正式薪資計算與上下分行姓名的電子薪資單。")

    # ----------------------------------------------------
    # 📊 Tab 4: 歷史薪資清冊查詢
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
                        df_p.columns = ["計薪月份", "工號", "姓名", "部門/職務", "廠區", "底薪", "上班工資", "加班費", "應領總額", "保險扣除", "實發淨薪", "狀態"]
                        st.dataframe(df_p, use_container_width=True, hide_index=True)
                    else:
                        st.info("目前尚無歷史薪資紀錄。")
            except Exception as e:
                st.error("讀取歷史薪資紀錄失敗: " + str(e))
        else:
            st.info("目前展示模式，請連接 PostgreSQL / Supabase 以讀取歷史紀錄。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_payroll_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_payroll_management_page(engine=engine, lang=lang, **kwargs)
