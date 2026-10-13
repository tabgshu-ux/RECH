import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🇻🇳 越南法規標準金額格式化 (千位數用 '.'，例如: 13.507.200)
# ----------------------------------------------------
def parse_vn_num(val_str):
    """將包含 '.' 或 ',' 或 NaN 的字串轉回純數字 float"""
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
# 🌐 多語系字典 (i18n)
# ----------------------------------------------------
PAYROLL_I18N = {
    "繁體中文": {
        "title": "💰 管理部 - 員工薪資計算與電子薪資單中心",
        "caption": "符合越南勞動法：支援批次匯入 Excel、6 大津貼、4 階梯加班費、社保/醫保扣繳與 1:1 電子薪資單。",
        "tab_calc": "🧮 單筆薪資核算",
        "tab_import": "📤 批次匯入 Excel (建立人事與9月薪資)",
        "tab_slip": "📄 個人電子薪資單 (Phiếu lương)",
        "tab_history": "📊 歷史薪資清冊與發放紀錄",
        "lbl_month": "計薪月份 (YYYY-MM)",
        "lbl_emp_code": "員工工號 / 人事編號",
        "lbl_emp_name": "員工姓名",
        "lbl_dept": "所屬部門 / 職務",
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
    }
}

def calculate_attendance_bonus(actual_hours):
    if actual_hours >= 207:
        return 400000.0
    elif 204 <= actual_hours <= 206.5:
        return 200000.0
    return 0.0

def init_payroll_db(engine):
    """資料庫初始化與自動拓建遺漏欄位"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            # 1. 建立基本資料表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.payroll_records (
                    id SERIAL PRIMARY KEY,
                    payroll_month VARCHAR(7) NOT NULL,
                    emp_code VARCHAR(50) NOT NULL,
                    emp_name VARCHAR(100) NOT NULL,
                    department VARCHAR(100),
                    factory VARCHAR(100) DEFAULT '文房 (VP)',
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

            # 2. 自動補齊所有潛在缺少欄位 (包含 updated_at, created_at, total_gross 等)
            alter_cols = [
                ("factory", "VARCHAR(100) DEFAULT '文房 (VP)'"),
                ("base_salary", "NUMERIC(12,2) DEFAULT 0"),
                ("pos_allowance", "NUMERIC(12,2) DEFAULT 0"),
                ("eval_bonus", "NUMERIC(12,2) DEFAULT 0"),
                ("gas_allowance", "NUMERIC(12,2) DEFAULT 0"),
                ("women_allowance", "NUMERIC(12,2) DEFAULT 0"),
                ("spec_bonus", "NUMERIC(12,2) DEFAULT 0"),
                ("actual_hours", "NUMERIC(6,2) DEFAULT 208"),
                ("work_salary", "NUMERIC(12,2) DEFAULT 0"),
                ("overtime_pay", "NUMERIC(12,2) DEFAULT 0"),
                ("meal_fee", "NUMERIC(12,2) DEFAULT 0"),
                ("prod_bonus", "NUMERIC(12,2) DEFAULT 0"),
                ("network_fee", "NUMERIC(12,2) DEFAULT 0"),
                ("attendance_bonus", "NUMERIC(12,2) DEFAULT 0"),
                ("other_deduct", "NUMERIC(12,2) DEFAULT 0"),
                ("total_gross", "NUMERIC(12,2) DEFAULT 0"),
                ("bhxh_deduction", "NUMERIC(12,2) DEFAULT 0"),
                ("bhyt_deduction", "NUMERIC(12,2) DEFAULT 0"),
                ("bhtn_deduction", "NUMERIC(12,2) DEFAULT 0"),
                ("pit_tax", "NUMERIC(12,2) DEFAULT 0"),
                ("advance_pay", "NUMERIC(12,2) DEFAULT 0"),
                ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
                ("updated_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")
            ]
            for col_name, col_type in alter_cols:
                try:
                    conn.execute(text(f"ALTER TABLE public.payroll_records ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                except Exception:
                    pass
    except Exception as e:
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
            e_code = st.text_input(L["lbl_emp_code"], value="2007031201", key="calc_code")
        with c_m3:
            dept_name = st.text_input(L["lbl_dept"], value="PGĐ BP Tài vụ (財務部 副理)", key="calc_dept")
        with c_m4:
            st.text_input(L["lbl_factory"], value="文房 (VP)", disabled=True)

        st.markdown("---")
        
        with st.form("form_calc_payroll"):
            st.markdown("##### 1️⃣ 基本薪資與 6 大津貼項目 (Lương & Phụ cấp)")
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
                                VALUES (:m, :code, :name, :dept, '文房 (VP)', :bs, :pos, :ev, :gas, :wom, :spec, :act_h,
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
                                    net_salary = EXCLUDED.net_salary;
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

    # ----------------------------------------------------
    # 📤 Tab 2: 批次匯入 Excel 薪資表與建立人事資料
    # ----------------------------------------------------
    with tab_import:
        st.markdown("### 📤 批次匯入 Excel 薪資表 (自動建立人事與歷史薪資)")
        st.caption("只需上傳公司 Excel 檔案 (例如 `Lương 09.2026.xls`)，系統會自動拆解文房、廠房與工程清冊，並寫入資料庫！")

        uploaded_file = st.file_uploader("請選擇要匯入的 Excel 薪資檔案 (.xls / .xlsx)", type=["xls", "xlsx"])
        import_month = st.text_input("匯入薪資月份 (YYYY-MM)", value="2026-09")

        if uploaded_file and st.button("🚀 開始自動解析並匯入資料庫", type="primary"):
            try:
                xls = pd.ExcelFile(uploaded_file)
                parsed_records = []

                sheet_mapping = {
                    "VAN PHONG": "文房 (VP)",
                    "NHA XUONG": "廠房 (NX)",
                    "CONG TRINH": "工程 (CT)"
                }

                for sheet_name, factory_label in sheet_mapping.items():
                    if sheet_name in xls.sheet_names:
                        df_s = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                        for idx in range(6, len(df_s)):
                            row = df_s.iloc[idx]
                            emp_code = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
                            emp_name = str(row.iloc[3]).replace("\n", " ").strip() if pd.notna(row.iloc[3]) else ""
                            
                            if emp_code and emp_code.isdigit() and len(emp_code) >= 6:
                                dept = str(row.iloc[4]).replace("\n", " ").strip() if pd.notna(row.iloc[4]) else ""
                                bs = parse_vn_num(row.iloc[5])
                                pos = parse_vn_num(row.iloc[6])
                                ev = parse_vn_num(row.iloc[7])
                                gas = parse_vn_num(row.iloc[8])
                                wom = parse_vn_num(row.iloc[9])
                                spec = parse_vn_num(row.iloc[10])
                                act_h = parse_vn_num(row.iloc[13]) if pd.notna(row.iloc[13]) else 208.0
                                ws = parse_vn_num(row.iloc[14])
                                ot_pay = parse_vn_num(row.iloc[19])
                                meal = parse_vn_num(row.iloc[20])
                                prod = parse_vn_num(row.iloc[21])
                                net_f = parse_vn_num(row.iloc[22])
                                att = parse_vn_num(row.iloc[23])
                                od = parse_vn_num(row.iloc[24])
                                gross = parse_vn_num(row.iloc[25])
                                bhxh = parse_vn_num(row.iloc[30])
                                bhyt = parse_vn_num(row.iloc[31])
                                bhtn = parse_vn_num(row.iloc[32])
                                net = parse_vn_num(row.iloc[36])

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
                    st.success(f"🎉 成功批次匯入 {len(parsed_records)} 筆員工 2026/09 薪資與人事資料至 Supabase 資料庫！")
                    st.rerun()
                elif not engine:
                    st.info(f"解析成功！共讀取到 {len(parsed_records)} 筆員工資料 (展示模式)。")
            except Exception as e:
                st.error("❌ 批次解析失敗: " + str(e))

    # ----------------------------------------------------
    # 📄 Tab 3: 1:1 電子薪資單
    # ----------------------------------------------------
    with tab_slip:
        m_formatted = payroll_m.replace("-", ".") if "-" in payroll_m else payroll_m
        slip_html = f"""
        <div style="border: 2px solid #1E3A8A; padding: 20px; border-radius: 8px; background-color: #FFFFFF; font-family: sans-serif; max-width: 850px; margin: auto; color: #111;">
            <div style="text-align: center; border-bottom: 2px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 15px;">
                <h2 style="margin: 0; color: #1E3A8A; font-weight: bold;">REETECH INDUSTRIAL CO., LTD</h2>
                <h3 style="margin: 5px 0 0 0; color: #333;">領薪資明細／CHI TIẾT LƯƠNG T.{m_formatted}</h3>
            </div>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 12px; font-size: 14px;">
                <tr style="background-color: #F3F4F6;">
                    <td style="padding: 6px; border: 1px solid #CBD5E1; font-weight: bold; width: 20%;">人事編號<br><span style="font-size: 12px; color: #555;">Mã nhân viên</span></td>
                    <td style="padding: 6px; border: 1px solid #CBD5E1; width: 30%; color: #1E3A8A; font-weight: bold;">{e_code}</td>
                    <td style="padding: 6px; border: 1px solid #CBD5E1; font-weight: bold; width: 20%;">姓名<br><span style="font-size: 12px; color: #555;">Họ tên</span></td>
                    <td style="padding: 6px; border: 1px solid #CBD5E1; width: 30%; font-weight: bold;">{e_name}</td>
                </tr>
                <tr>
                    <td style="padding: 6px; border: 1px solid #CBD5E1; font-weight: bold;">職務<br><span style="font-size: 12px; color: #555;">Chức vụ</span></td>
                    <td style="padding: 6px; border: 1px solid #CBD5E1;">{dept_name}</td>
                    <td style="padding: 6px; border: 1px solid #CBD5E1; font-weight: bold;">底薪<br><span style="font-size: 12px; color: #555;">Lương CB</span></td>
                    <td style="padding: 6px; border: 1px solid #CBD5E1; font-weight: bold;">{fmt_vn_num(base_sal)}</td>
                </tr>
            </table>
            <div style="background-color: #10B981; color: white; padding: 12px; border-radius: 6px; text-align: center; margin-bottom: 15px;">
                <span style="font-size: 16px; font-weight: bold; display: block;">實領／THỰC LÃNH</span>
                <span style="font-size: 26px; font-weight: bold; font-family: monospace;">{fmt_vn_curr(net_pay)}</span>
            </div>
            <div style="border-top: 1px dashed #94A3B8; padding-top: 10px; font-size: 12px; color: #475569; text-align: center; font-style: italic;">
                Nhân viên phải quý trọng công việc, làm việc có tinh thần trách nhiệm.<br>
                Không được làm những việc vi phạm pháp luật và qui định công ty.
            </div>
        </div>
        """
        st.components.v1.html(slip_html, height=450, scrolling=True)

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
                        st.dataframe(df_p, use_container_width=True)
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
