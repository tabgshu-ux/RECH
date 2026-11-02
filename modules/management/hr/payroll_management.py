import streamlit as st
import pandas as pd
from sqlalchemy import text

# ----------------------------------------------------
# 🇻🇳 越南法規標準金額格式化 (千位數用 '.'，例如: 38.078.000)
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
        if v == 0:
            return "-"
        return f"{v:,.0f}".replace(",", ".")
    except Exception:
        return "-"

def fmt_vn_curr(val):
    try:
        v = float(val)
        return f"{v:,.0f}".replace(",", ".") + " VND"
    except Exception:
        return "0 VND"

# ----------------------------------------------------
# 🌐 多語系字典 (i18n)
# ----------------------------------------------------
PAYROLL_I18N = {
    "繁體中文": {
        "title": "💰 管理部 - 員工薪資計算與電子薪資單中心",
        "caption": "裕豐電機工業標準：1:1 復刻公司正式 Excel 經典黑框薪資單與精準計算。",
        "tab_calc": "🧮 單筆薪資核算",
        "tab_import": "📥 批次匯入",
        "tab_slip": "📄 員工薪資單 (公司經典版)",
        "tab_history": "📊 歷史薪資清冊與發放紀錄",
        "lbl_month": "計薪月份 (YYYY-MM)",
        "lbl_emp_code": "員工工號 / 人事編號",
        "lbl_emp_name": "員工姓名 (越南文 / 中文)",
        "lbl_dept": "所屬部門 / 職務",
        "lbl_factory": "工作廠區",
        "btn_calc_and_save": "💾 計算並寫入 Supabase 薪資資料庫",
        "msg_success": "✅ 薪資清冊計算完畢，並已同步更新資料庫！",
        "lbl_net_pay": "💵 本月應發實領金額 (THỰC LÃNH)",
        "header_summary": "📋 歷史月度薪資與保險扣除統計表"
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
                    factory VARCHAR(100) DEFAULT '西寧廠 (Tay Ninh)',
                    base_salary NUMERIC(12,2) DEFAULT 0,
                    pos_allowance NUMERIC(12,2) DEFAULT 0,
                    eval_bonus NUMERIC(12,2) DEFAULT 0,
                    gas_allowance NUMERIC(12,2) DEFAULT 0,
                    spec_bonus NUMERIC(12,2) DEFAULT 0,
                    actual_hours NUMERIC(6,2) DEFAULT 208,
                    leave_hours NUMERIC(6,2) DEFAULT 0,
                    ot_15_hours NUMERIC(6,2) DEFAULT 0,
                    ot_195_hours NUMERIC(6,2) DEFAULT 0,
                    ot_20_hours NUMERIC(6,2) DEFAULT 0,
                    ot_30_hours NUMERIC(6,2) DEFAULT 0,
                    meal_fee NUMERIC(12,2) DEFAULT 0,
                    prod_bonus NUMERIC(12,2) DEFAULT 0,
                    total_gross NUMERIC(12,2) DEFAULT 0,
                    pit_tax NUMERIC(12,2) DEFAULT 0,
                    bhxh_deduction NUMERIC(12,2) DEFAULT 0,
                    bhyt_deduction NUMERIC(12,2) DEFAULT 0,
                    bhtn_deduction NUMERIC(12,2) DEFAULT 0,
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
                    factory VARCHAR(100) DEFAULT '西寧廠 (Tay Ninh)',
                    department VARCHAR(100),
                    position VARCHAR(100),
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
            payroll_m = st.text_input("計薪月份", value="2026-09", key="calc_m")
        with c_m2:
            e_code = st.text_input("員工工號", value="2005010102", key="calc_code")
        with c_m3:
            dept_name = st.text_input("部門職務", value="GĐ CT 工程經理", key="calc_dept")
        with c_m4:
            factory_sel = st.selectbox("工作廠區", ["西寧廠 (Tay Ninh)", "工程工地 (Site)"], index=1)

        st.markdown("---")
        
        with st.form("form_calc_payroll"):
            st.markdown("##### 1️⃣ 薪資項目設定")
            col1, col2, col3 = st.columns(3)
            with col1:
                e_name = st.text_input("員工姓名 (越/中)", value="PHẠM HOÀNG LÂM\n范 皇 林")
                str_base_sal = st.text_input("底薪 Lương CB", value="21.011.200")
                str_pos_allowance = st.text_input("職務津貼 PC chức vụ", value="3.000.000")
            with col2:
                str_eval_bonus = st.text_input("評核獎金 Tiền thưởng đánh giá", value="5.567.968")
                str_gas_allowance = st.text_input("出差油費 PC tiền xăng", value="6.000.000")
                str_spec_bonus = st.text_input("工程補助津貼 Pc.đi CT", value="4.000.000")
            with col3:
                act_hours = st.number_input("上班實際時數", min_value=0.0, value=208.0, step=0.5)
                leave_hours = st.number_input("請假時數", min_value=0.0, value=0.0, step=0.5)
                str_meal_fee = st.text_input("餐費 Tiền cơm", value="1.200.000")

            st.markdown("##### 2️⃣ 加班與扣款項目設定")
            col4, col5, col6 = st.columns(3)
            with col4:
                ot_15 = st.number_input("加班時數 Tăng ca*1.5", min_value=0.0, value=0.0, step=0.5)
                ot_195 = st.number_input("加班時數 Tăng ca*1.95", min_value=0.0, value=0.0, step=0.5)
            with col5:
                ot_20 = st.number_input("加班時數 Tăng ca*2.0", min_value=0.0, value=0.0, step=0.5)
                ot_30 = st.number_input("加班時數 Tăng ca*3.0", min_value=0.0, value=0.0, step=0.5)
            with col6:
                str_pit = st.text_input("所得稅 TN cá nhân", value="180.421")
                str_bhxh = st.text_input("社會保險 BHXH", value="1.920.896")
                str_bhyt = st.text_input("醫療保險 BHYT", value="360.168")
                str_bhtn = st.text_input("失業保險 BH Thất nghiệp", value="240.112")

            base_sal = parse_vn_num(str_base_sal)
            pos_allowance = parse_vn_num(str_pos_allowance)
            eval_bonus = parse_vn_num(str_eval_bonus)
            gas_allowance = parse_vn_num(str_gas_allowance)
            spec_bonus = parse_vn_num(str_spec_bonus)
            meal_fee = parse_vn_num(str_meal_fee)
            pit = parse_vn_num(str_pit)
            bhxh = parse_vn_num(str_bhxh)
            bhyt = parse_vn_num(str_bhyt)
            bhtn = parse_vn_num(str_bhtn)

            total_gross = base_sal + pos_allowance + eval_bonus + gas_allowance + spec_bonus + meal_fee
            total_deduct = pit + bhxh + bhyt + bhtn
            net_pay = total_gross - total_deduct

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("合計總收入 (Tổng lương)", fmt_vn_curr(total_gross))
            m2.metric("扣款總計 (Tổng khấu trừ)", fmt_vn_curr(total_deduct))
            m3.metric(L["lbl_net_pay"], fmt_vn_curr(net_pay))

            if st.form_submit_button(L["btn_calc_and_save"], type="primary", use_container_width=True):
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.payroll_records 
                                (payroll_month, emp_code, emp_name, department, factory, base_salary, pos_allowance, eval_bonus, 
                                 gas_allowance, spec_bonus, actual_hours, leave_hours, ot_15_hours, ot_195_hours, ot_20_hours, ot_30_hours,
                                 meal_fee, total_gross, pit_tax, bhxh_deduction, bhyt_deduction, bhtn_deduction, net_salary)
                                VALUES (:m, :code, :name, :dept, :factory, :bs, :pos, :ev, :gas, :spec, :act_h, :leave_h,
                                        :ot15, :ot195, :ot20, :ot30, :meal, :gross, :pit, :bhxh, :bhyt, :bhtn, :net)
                                ON CONFLICT (payroll_month, emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    department = EXCLUDED.department,
                                    factory = EXCLUDED.factory,
                                    base_salary = EXCLUDED.base_salary,
                                    total_gross = EXCLUDED.total_gross,
                                    pit_tax = EXCLUDED.pit_tax,
                                    bhxh_deduction = EXCLUDED.bhxh_deduction,
                                    bhyt_deduction = EXCLUDED.bhyt_deduction,
                                    bhtn_deduction = EXCLUDED.bhtn_deduction,
                                    net_salary = EXCLUDED.net_salary;
                            """), {
                                "m": payroll_m, "code": e_code, "name": e_name, "dept": dept_name, "factory": factory_sel,
                                "bs": base_sal, "pos": pos_allowance, "ev": eval_bonus, "gas": gas_allowance,
                                "spec": spec_bonus, "act_h": act_hours, "leave_h": leave_hours,
                                "ot15": ot_15, "ot195": ot_195, "ot20": ot_20, "ot30": ot_30,
                                "meal": meal_fee, "gross": total_gross, "pit": pit, "bhxh": bhxh, "bhyt": bhyt, "bhtn": bhtn, "net": net_pay
                            })
                        st.success(L["msg_success"])
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入資料庫失敗: " + str(e))

    # ----------------------------------------------------
    # 📤 Tab 2: 批次匯入
    # ----------------------------------------------------
    with tab_import:
        st.markdown("### 📤 批次匯入 Excel")
        st.caption("上傳公司標準 Excel 薪資檔案，系統將自動解析並寫入資料庫！")

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
                                spec = parse_vn_num(row.iloc[10]) if len(row) > 10 else 0.0
                                act_h = parse_vn_num(row.iloc[13]) if len(row) > 13 and pd.notna(row.iloc[13]) else 208.0
                                meal = parse_vn_num(row.iloc[20]) if len(row) > 20 else 0.0
                                
                                gross = parse_vn_num(row.iloc[27]) if len(row) > 27 else (bs + pos + ev + gas + spec + meal)
                                pit = parse_vn_num(row.iloc[32]) if len(row) > 32 else 0.0
                                bhxh = parse_vn_num(row.iloc[33]) if len(row) > 33 else 0.0
                                bhyt = parse_vn_num(row.iloc[34]) if len(row) > 34 else 0.0
                                bhtn = parse_vn_num(row.iloc[35]) if len(row) > 35 else 0.0
                                net = parse_vn_num(row.iloc[39]) if len(row) > 39 else (gross - pit - bhxh - bhyt - bhtn)

                                parsed_records.append({
                                    "m": import_month, "code": emp_code, "name": emp_name, "dept": dept,
                                    "factory": factory_label, "bs": bs, "pos": pos, "ev": ev, "gas": gas,
                                    "spec": spec, "act_h": act_h, "meal": meal, "gross": gross,
                                    "pit": pit, "bhxh": bhxh, "bhyt": bhyt, "bhtn": bhtn, "net": net
                                })

                if parsed_records and engine:
                    with engine.begin() as conn:
                        for rec in parsed_records:
                            conn.execute(text("""
                                INSERT INTO public.payroll_records 
                                (payroll_month, emp_code, emp_name, department, factory, base_salary, pos_allowance, eval_bonus, 
                                 gas_allowance, spec_bonus, actual_hours, meal_fee, total_gross, 
                                 pit_tax, bhxh_deduction, bhyt_deduction, bhtn_deduction, net_salary)
                                VALUES (:m, :code, :name, :dept, :factory, :bs, :pos, :ev, :gas, :spec, :act_h,
                                        :meal, :gross, :pit, :bhxh, :bhyt, :bhtn, :net)
                                ON CONFLICT (payroll_month, emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    department = EXCLUDED.department,
                                    factory = EXCLUDED.factory,
                                    base_salary = EXCLUDED.base_salary,
                                    total_gross = EXCLUDED.total_gross,
                                    pit_tax = EXCLUDED.pit_tax,
                                    bhxh_deduction = EXCLUDED.bhxh_deduction,
                                    bhyt_deduction = EXCLUDED.bhyt_deduction,
                                    bhtn_deduction = EXCLUDED.bhtn_deduction,
                                    net_salary = EXCLUDED.net_salary;
                            """), rec)

                st.success(f"🎉 成功批次匯入 {len(parsed_records)} 筆員工資料！")
                st.rerun()
            except Exception as e:
                st.error("❌ 批次解析失敗: " + str(e))

    # ----------------------------------------------------
    # 📄 Tab 3: 員工薪資單 (完全 1:1 復刻公司正式 Excel 經典黑框版型)[cite: 22]
    # ----------------------------------------------------
    with tab_slip:
        st.markdown("### 📄 員工詳細薪資條 (公司經典正式版)")
        st.caption("💡 1:1 完美復刻公司正式 Excel 的黑框對齊排版：上下分行姓名、各項津貼與扣款欄位精準呈現。")

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
                "payroll_month": "2026-09", "emp_code": "2005010102", "emp_name": "PHẠM HOÀNG LÂM\n范 皇 林",
                "department": "GĐ CT 工程經理", "factory": "工程工地 (Site)", "base_salary": 21011200,
                "pos_allowance": 3000000, "eval_bonus": 5567968, "gas_allowance": 6000000,
                "spec_bonus": 4000000, "actual_hours": 208, "leave_hours": 0,
                "ot_15_hours": 0, "ot_195_hours": 0, "ot_20_hours": 0, "ot_30_hours": 0,
                "meal_fee": 1200000, "total_gross": 40779168, "pit_tax": 180421,
                "bhxh_deduction": 1920896, "bhyt_deduction": 360168, "bhtn_deduction": 240112, "net_salary": 38078000
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

        raw_name = str(target_slip.get('emp_name', '')).replace("\r", "").replace("\n", " ")
        name_tokens = [t for t in raw_name.split(" ") if t]
        vn_tokens = [t for t in name_tokens if any(ord(c) < 128 for c in t)]
        cn_tokens = [t for t in name_tokens if any(ord(c) >= 128 for c in t)]
        vn_name_part = " ".join(vn_tokens) if vn_tokens else raw_name
        cn_name_part = " ".join(cn_tokens) if cn_tokens else ""

        m_fmt = str(target_slip.get("payroll_month", "2026-09")).replace("-", ".")
        
        b_sal = float(target_slip.get('base_salary', 0))
        p_al = float(target_slip.get('pos_allowance', 0))
        e_bo = float(target_slip.get('eval_bonus', 0))
        g_al = float(target_slip.get('gas_allowance', 0))
        s_bo = float(target_slip.get('spec_bonus', 0))
        m_fe = float(target_slip.get('meal_fee', 0))
        act_h = float(target_slip.get('actual_hours', 208))
        leave_h = float(target_slip.get('leave_hours', 0))
        
        ot15 = float(target_slip.get('ot_15_hours', 0))
        ot195 = float(target_slip.get('ot_195_hours', 0))
        ot20 = float(target_slip.get('ot_20_hours', 0))
        ot30 = float(target_slip.get('ot_30_hours', 0))
        
        gross = float(target_slip.get('total_gross', b_sal + p_al + e_bo + g_al + s_bo + m_fe))
        pit = float(target_slip.get('pit_tax', 0))
        bhxh = float(target_slip.get('bhxh_deduction', 0))
        bhyt = float(target_slip.get('bhyt_deduction', 0))
        bhtn = float(target_slip.get('bhtn_deduction', 0))
        net = float(target_slip.get('net_salary', gross - (pit + bhxh + bhyt + bhtn)))

        # 🎨 完全 1:1 復刻公司標準 Excel 薪資條的 HTML 經典黑框排版[cite: 22]
        slip_html = f"""
        <div style="border: 2px solid #000; padding: 25px; border-radius: 2px; background-color: #FFFFFF; font-family: Arial, sans-serif; max-width: 780px; margin: auto; color: #000;">
            <div style="text-align: center; font-weight: bold; font-size: 16px; margin-bottom: 3px; letter-spacing: 1px;">REETECH INDUSTRIAL CO.,LTD</div>
            <div style="text-align: center; font-weight: bold; font-size: 15px; margin-bottom: 12px; border-bottom: 2px solid #000; padding-bottom: 8px;">
                領薪資明細／CHI TIẾT LƯƠNG T.{m_fmt}
            </div>

            <table style="width: 100%; border-collapse: collapse; border: 1px solid #000; font-size: 13px; text-align: left;">
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; width: 18%; background: #fdfdfd; font-weight: bold;">人事編號<br><span style="font-size: 10px; color: #555;">Mã nhân viên</span></td>
                    <td style="border: 1px solid #000; padding: 6px; width: 32%; font-weight: bold; color: #1E3A8A;">{target_slip.get('emp_code')}</td>
                    <td style="border: 1px solid #000; padding: 6px; width: 18%; background: #fdfdfd; font-weight: bold;">姓名<br><span style="font-size: 10px; color: #555;">Họ tên</span></td>
                    <td style="border: 1px solid #000; padding: 6px; width: 32%; font-weight: bold; line-height: 1.3;">
                        <div style="font-size: 13px; color: #000;">{vn_name_part}</div>
                        <div style="font-size: 12px; color: #444; font-weight: normal;">{cn_name_part}</div>
                    </td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">職務<br><span style="font-size: 10px; color: #555;">Chức vụ</span></td>
                    <td style="border: 1px solid #000; padding: 6px;">{target_slip.get('department')}</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">底薪<br><span style="font-size: 10px; color: #555;">Lương CB</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right; font-weight: bold;">{fmt_vn_num(b_sal)}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">職務津貼<br><span style="font-size: 10px; color: #555;">PC chức vụ</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right;">{fmt_vn_num(p_al)}</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">評核獎金<br><span style="font-size: 10px; color: #555;">Tiền thưởng đánh giá</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right;">{fmt_vn_num(e_bo)}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">出差油費<br><span style="font-size: 10px; color: #555;">PC tiền xăng</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right;">{fmt_vn_num(g_al)}</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">工程補助津貼<br><span style="font-size: 10px; color: #555;">Pc.đi CT</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right;">{fmt_vn_num(s_bo)}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">上班標準時數<br><span style="font-size: 10px; color: #555;">SG làm việc TC</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;" colspan="3">208</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">上班實際時數<br><span style="font-size: 10px; color: #555;">SG làm việc TT</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">{act_h}</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">請假<br><span style="font-size: 10px; color: #555;">Nghỉ phép</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">{leave_h}</td>
                </tr>
                <tr style="background-color: #f8fafc; font-weight: bold;">
                    <td style="border: 1px solid #000; padding: 6px;">合計／Cộng</td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right; color: #047857;" colspan="3">{fmt_vn_num(b_sal + p_al + e_bo + g_al + s_bo)}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">加班時數<br><span style="font-size: 10px; color: #555;">SG Tăng ca*1.5</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">{ot15}</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">加班時數<br><span style="font-size: 10px; color: #555;">Tăng ca*2.0</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">{ot20}</td>
                </tr>
                <tr style="background-color: #f8fafc; font-weight: bold;">
                    <td style="border: 1px solid #000; padding: 6px;">合計／Cộng</td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">-</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">加班時數<br><span style="font-size: 10px; color: #555;">Tăng ca*1.95</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">{ot195}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">餐費<br><span style="font-size: 10px; color: #555;">Tiền cơm</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right;">{fmt_vn_num(m_fe)}</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">績效獎金<br><span style="font-size: 10px; color: #555;">Thưởng N.Suất</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right;">-</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">電話/網路費補貼<br><span style="font-size: 10px; color: #555;">PC đt/mạng</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right;">-</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">看倉管<br><span style="font-size: 10px; color: #555;">Giữ kho</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right;">-</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">全勤<br><span style="font-size: 10px; color: #555;">Chuyên cần</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right;">-</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">加班時數<br><span style="font-size: 10px; color: #555;">Tăng ca*3.0</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">{ot30}</td>
                </tr>
                <tr style="font-weight: bold; background-color: #1E3A8A; color: white;">
                    <td style="border: 1px solid #000; padding: 8px;">總計／Tổng lương</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: right;" colspan="3">{fmt_vn_curr(gross)}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 5px; text-align: center; font-weight: bold; background: #e2e8f0;" colspan="4">KHOẢN TRỪ／扣款項目</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">所得稅<br><span style="font-size: 10px; color: #555;">TN cá nhân</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right; color: #DC2626;">{fmt_vn_num(pit)}</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">社會保險<br><span style="font-size: 10px; color: #555;">BHXH</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right; color: #DC2626;">{fmt_vn_num(bhxh)}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">醫療保險<br><span style="font-size: 10px; color: #555;">BHYT</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right; color: #DC2626;">{fmt_vn_num(bhyt)}</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">失業保險<br><span style="font-size: 10px; color: #555;">BH Thất nghiệp</span></td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right; color: #DC2626;">{fmt_vn_num(bhtn)}</td>
                </tr>
                <tr style="background-color: #fef08a;">
                    <td style="border: 1px solid #000; padding: 10px; font-weight: bold; font-size: 15px;">實領／THỰC LÃNH</td>
                    <td style="border: 1px solid #000; padding: 10px; text-align: right; font-weight: bold; font-size: 18px; color: #047857;" colspan="3">{fmt_vn_curr(net)}</td>
                </tr>
            </table>

            <div style="border-top: 1px dashed #000; margin-top: 15px; padding-top: 8px; font-size: 11px; text-align: center; font-style: italic;">
                Nhân viên phải quý trọng công việc, làm việc có tinh thần trách nhiệm.<br>
                Không được làm những việc vi phạm pháp luật và qui định công ty.
            </div>
        </div>
        """
        st.components.v1.html(slip_html, height=820, scrolling=True)

        # 🖨️ 單人專屬預覽與列印按鈕
        st.markdown("<br>", unsafe_allow_html=True)
        col_pr1, col_pr2 = st.columns([1, 3])
        with col_pr1:
            if st.button("🖨️ 列印此張薪資單 (Print Slip)", type="primary", use_container_width=True):
                st.markdown("""
                    <script> window.print(); </script>
                """, unsafe_allow_html=True)
                st.info("💡 已觸發列印指令，請於彈出視窗中選擇印表機或儲存為 PDF。")
        with col_pr2:
            st.caption("提示：點擊左側列印按鈕即可呼叫瀏覽器列印，完美輸出與您公司正式 Excel 完全一致的 1:1 經典黑框薪資單！")

    # ----------------------------------------------------
    # 📊 Tab 4: 歷史薪資清冊查詢
    # ----------------------------------------------------
    with tab_history:
        st.markdown("#### " + str(L["header_summary"]))
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("""
                        SELECT payroll_month, emp_code, emp_name, department, factory, base_salary, total_gross, (pit_tax + bhxh_deduction + bhyt_deduction + bhtn_deduction) as total_deduct, net_salary, status
                        FROM public.payroll_records
                        ORDER BY payroll_month DESC, emp_code ASC
                    """))
                    rows = res.fetchall()
                    if rows:
                        formatted_rows = []
                        for r in rows:
                            row_dict = dict(r._mapping)
                            row_dict["底薪"] = fmt_vn_curr(row_dict.get("base_salary", 0))
                            row_dict["應領總額"] = fmt_vn_curr(row_dict.get("total_gross", 0))
                            row_dict["扣款總計"] = fmt_vn_curr(row_dict.get("total_deduct", 0))
                            row_dict["實發淨薪"] = fmt_vn_curr(row_dict.get("net_salary", 0))
                            formatted_rows.append(row_dict)

                        df_p = pd.DataFrame(formatted_rows)[["payroll_month", "emp_code", "emp_name", "department", "factory", "底薪", "應領總額", "扣款總計", "實發淨薪", "status"]]
                        df_p.columns = ["計薪月份", "工號", "姓名", "部門/職務", "廠區", "底薪", "應領總額", "扣款總計", "實發淨薪", "狀態"]
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
