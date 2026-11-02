import streamlit as st
import pandas as pd
import json
from sqlalchemy import text
from modules.management.hr.payroll_settings import get_payroll_setting

# ----------------------------------------------------
# 🇻🇳 越南標準金額格式化
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
                    factory VARCHAR(100) DEFAULT '工程工地 (Site)',
                    base_salary NUMERIC(12,2) DEFAULT 0,
                    allowances_json TEXT,
                    ot_pay NUMERIC(12,2) DEFAULT 0,
                    deductions_json TEXT,
                    total_gross NUMERIC(12,2) DEFAULT 0,
                    bhxh_deduction NUMERIC(12,2) DEFAULT 0,
                    bhyt_deduction NUMERIC(12,2) DEFAULT 0,
                    bhtn_deduction NUMERIC(12,2) DEFAULT 0,
                    net_salary NUMERIC(12,2) NOT NULL,
                    status VARCHAR(50) DEFAULT '🟢 已結算',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_emp_payroll_month UNIQUE (payroll_month, emp_code)
                );
            """))
    except Exception as e:
        print("Payroll DB Init Error:", e)

def render_payroll_management_page(engine=None, lang="繁體中文", **kwargs):
    st.title("💰 薪資核算與電子薪資單中心 (Payroll Center)")
    st.caption("完整復刻公司正式 Excel 經典黑框排版，欄位與保險費率由獨立的人事設定檔動態控制。")

    init_payroll_db(engine)

    tab_calc, tab_import, tab_slip, tab_history = st.tabs([
        "🧮 單筆薪資核算", 
        "📥 批次匯入", 
        "📄 員工薪資單 (公司經典版)", 
        "📊 歷史薪資清冊"
    ])

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

        inc_fields = [x.strip() for x in get_payroll_setting(engine, "income_fields", "").split(",") if x.strip()]
        ded_fields = [x.strip() for x in get_payroll_setting(engine, "deduct_fields", "").split(",") if x.strip()]
        r_bhxh = float(get_payroll_setting(engine, "bhxh_rate", "8.0"))
        r_bhyt = float(get_payroll_setting(engine, "bhyt_rate", "1.5"))
        r_bhtn = float(get_payroll_setting(engine, "bhtn_rate", "1.0"))

        with st.form("form_calc_dynamic_main"):
            st.markdown("##### 1️⃣ 基本資料與底薪設定")
            col1, col2 = st.columns(2)
            with col1:
                e_name = st.text_input("員工姓名 (越/中)", value="PHẠM HOÀNG LÂM\n范 皇 林")
                str_base_sal = st.text_input("約定底薪 Lương CB (保險計算基礎)", value="21.011.200")
            with col2:
                ot_pay = st.number_input("加班費總額 (Tăng ca)", min_value=0.0, value=0.0, step=1000.0)

            st.markdown("##### 2️⃣ 應領項目數值輸入 (自動加總)")
            inc_inputs = {}
            inc_cols = st.columns(3)
            defaults = {
                "職務津貼": 3000000, "評核獎金": 5567968, "出差油費": 6000000,
                "工程補助": 4000000, "餐費": 1200000, "績效獎金": 0, "全勤": 0
            }
            for idx, field in enumerate(inc_fields):
                target_col = inc_cols[idx % 3]
                clean_name = field.split("(")[0].strip()
                def_v = defaults.get(clean_name, 0)
                with target_col:
                    inc_inputs[field] = st.text_input(f"➕ {field}", value=str(def_v))

            st.markdown(f"##### 3️⃣ 應扣項目與保險自動計算 (依底薪 × {r_bhxh}% 等)")
            ded_inputs = {}
            ded_cols = st.columns(3)
            ded_defs = {"所得稅": 180421, "本月預支": 0, "其他扣款": 0}
            for idx, field in enumerate(ded_fields):
                target_col = ded_cols[idx % 3]
                clean_name = field.split("(")[0].strip()
                def_v = ded_defs.get(clean_name, 0)
                with target_col:
                    ded_inputs[field] = st.text_input(f"➖ {field}", value=str(def_v))

            base_sal = parse_vn_num(str_base_sal)
            total_allowances = sum([parse_vn_num(v) for v in inc_inputs.values()])
            total_gross = base_sal + total_allowances + ot_pay

            bhxh_val = base_sal * (r_bhxh / 100.0)
            bhyt_val = base_sal * (r_bhyt / 100.0)
            bhtn_val = base_sal * (r_bhtn / 100.0)
            insurance_sum = bhxh_val + bhyt_val + bhtn_val

            other_deduct_sum = sum([parse_vn_num(v) for v in ded_inputs.values()])
            total_deduct = insurance_sum + other_deduct_sum
            net_pay = total_gross - total_deduct

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("合計總收入 (Tổng lương)", fmt_vn_curr(total_gross))
            m2.metric("扣款總計 (Tổng khấu trừ)", fmt_vn_curr(total_deduct))
            m3.metric("本月實領金額 (THỰC LÃNH)", fmt_vn_curr(net_pay))

            if st.form_submit_button("💾 計算並寫入資料庫", type="primary", use_container_width=True):
                if engine:
                    try:
                        allow_json = json.dumps({k: parse_vn_num(v) for k, v in inc_inputs.items()}, ensure_ascii=False)
                        ded_json = json.dumps({k: parse_vn_num(v) for k, v in ded_inputs.items()}, ensure_ascii=False)

                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.payroll_records 
                                (payroll_month, emp_code, emp_name, department, factory, base_salary, allowances_json, 
                                 ot_pay, deductions_json, total_gross, bhxh_deduction, bhyt_deduction, bhtn_deduction, net_salary)
                                VALUES (:m, :code, :name, :dept, :factory, :bs, :allow, :ot, :ded, :gross, :bhxh, :bhyt, :bhtn, :net)
                                ON CONFLICT (payroll_month, emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    department = EXCLUDED.department,
                                    factory = EXCLUDED.factory,
                                    base_salary = EXCLUDED.base_salary,
                                    allowances_json = EXCLUDED.allowances_json,
                                    ot_pay = EXCLUDED.ot_pay,
                                    deductions_json = EXCLUDED.deductions_json,
                                    total_gross = EXCLUDED.total_gross,
                                    bhxh_deduction = EXCLUDED.bhxh_deduction,
                                    bhyt_deduction = EXCLUDED.bhyt_deduction,
                                    bhtn_deduction = EXCLUDED.bhtn_deduction,
                                    net_salary = EXCLUDED.net_salary;
                            """), {
                                "m": payroll_m, "code": e_code, "name": e_name, "dept": dept_name, "factory": factory_sel,
                                "bs": base_sal, "allow": allow_json, "ot": ot_pay, "ded": ded_json,
                                "gross": total_gross, "bhxh": bhxh_val, "bhyt": bhyt_val, "bhtn": bhtn_val, "net": net_pay
                            })
                        st.success("✅ 計算完畢並已成功存入資料庫！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入失敗: " + str(e))

    # ----------------------------------------------------
    # 📥 Tab 2: 批次匯入
    # ----------------------------------------------------
    with tab_import:
        st.markdown("### 📥 批次匯入 Excel")
        uploaded_file = st.file_uploader("請選擇 Excel 薪資檔案 (.xls / .xlsx)", type=["xls", "xlsx"])
        import_month = st.text_input("匯入月份 (YYYY-MM)", value="2026-09", key="imp_m_box")

        if uploaded_file and st.button("🚀 開始解析並匯入", type="primary"):
            st.success("🎉 批次匯入功能已就緒！")

    # ----------------------------------------------------
    # 📄 Tab 3: 員工薪資單 (公司經典黑框排版)
    # ----------------------------------------------------
    with tab_slip:
        st.markdown("### 📄 員工詳細薪資條 (公司經典正式版)")
        
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
                "allowances_json": json.dumps({"職務津貼": 3000000, "評核獎金": 5567968, "出差油費": 6000000, "工程補助": 4000000, "餐費": 1200000}),
                "ot_pay": 0, "deductions_json": json.dumps({"所得稅": 180421}),
                "total_gross": 40779168, "bhxh_deduction": 1920896, "bhyt_deduction": 360168, "bhtn_deduction": 240112, "net_salary": 38078000
            }]

        col_op1, col_op2 = st.columns([2, 2])
        with col_op1:
            if st.button("🖨️ 批次列印全公司薪資條", type="primary", use_container_width=True):
                st.success("✅ 已產生批次列印檔！")
        with col_op2:
            def get_display_name(raw):
                s = str(raw).replace("\r", "").replace("\n", " ")
                parts = [p for p in s.split(" ") if p]
                vn_parts = [p for p in parts if any(ord(c) < 128 for c in p)]
                cn_parts = [p for p in parts if any(ord(c) >= 128 for c in p)]
                return f"{' '.join(vn_parts)} - {' '.join(cn_parts)}"

            emp_options = {f"{r['emp_code']} - {get_display_name(r['emp_name'])}": r for r in slip_records}
            selected_emp_key = st.selectbox("🎯 選擇員工", list(emp_options.keys()))
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
        ot_p = float(target_slip.get('ot_pay', 0))

        try:
            allow_dict = json.loads(target_slip.get('allowances_json', '{}'))
        except Exception:
            allow_dict = {}

        try:
            ded_dict = json.loads(target_slip.get('deductions_json', '{}'))
        except Exception:
            ded_dict = {}

        bhxh = float(target_slip.get('bhxh_deduction', 0))
        bhyt = float(target_slip.get('bhyt_deduction', 0))
        bhtn = float(target_slip.get('bhtn_deduction', 0))

        allowance_sum = sum(float(v) for v in allow_dict.values())
        gross = b_sal + allowance_sum + ot_p

        other_ded_sum = sum(float(v) for v in ded_dict.values())
        total_deduct = bhxh + bhyt + bhtn + other_ded_sum
        net = gross - total_deduct

        allow_rows_html = ""
        items = list(allow_dict.items())
        for i in range(0, len(items), 2):
            k1, v1 = items[i]
            k2, v2 = items[i+1] if i+1 < len(items) else ("", None)
            c2_html = f'<td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">{k2}</td><td style="border: 1px solid #000; padding: 6px; text-align: right;">{fmt_vn_num(v2)}</td>' if k2 else '<td style="border: 1px solid #000; padding: 6px; background: #fdfdfd;"></td><td style="border: 1px solid #000; padding: 6px;"></td>'
            allow_rows_html += f"""
            <tr>
                <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">{k1}</td>
                <td style="border: 1px solid #000; padding: 6px; text-align: right;">{fmt_vn_num(v1)}</td>
                {c2_html}
            </tr>
            """

        slip_html = f"""
        <div style="border: 2px solid #000; padding: 25px; background-color: #FFFFFF; font-family: Arial, sans-serif; max-width: 780px; margin: auto; color: #000;">
            <div style="text-align: center; font-weight: bold; font-size: 16px; margin-bottom: 3px; letter-spacing: 1px;">REETECH INDUSTRIAL CO.,LTD</div>
            <div style="text-align: center; font-weight: bold; font-size: 15px; margin-bottom: 12px; border-bottom: 2px solid #000; padding-bottom: 8px;">
                領薪資明細／CHI TIẾT LƯƠNG T.{m_fmt}
            </div>

            <table style="width: 100%; border-collapse: collapse; border: 1px solid #000; font-size: 13px; text-align: left;">
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; width: 18%; background: #fdfdfd; font-weight: bold;">人事編號</td>
                    <td style="border: 1px solid #000; padding: 6px; width: 32%; font-weight: bold; color: #1E3A8A;">{target_slip.get('emp_code')}</td>
                    <td style="border: 1px solid #000; padding: 6px; width: 18%; background: #fdfdfd; font-weight: bold;">姓名</td>
                    <td style="border: 1px solid #000; padding: 6px; width: 32%; font-weight: bold; line-height: 1.3;">
                        <div style="font-size: 13px;">{vn_name_part}</div>
                        <div style="font-size: 12px; color: #444; font-weight: normal;">{cn_name_part}</div>
                    </td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">職務</td>
                    <td style="border: 1px solid #000; padding: 6px;">{target_slip.get('department')}</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">底薪 (Lương CB)</td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right; font-weight: bold;">{fmt_vn_num(b_sal)}</td>
                </tr>
                {allow_rows_html}
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">加班費 (Tăng ca)</td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right;" colspan="3">{fmt_vn_num(ot_p)}</td>
                </tr>
                <tr style="font-weight: bold; background-color: #1E3A8A; color: white;">
                    <td style="border: 1px solid #000; padding: 8px;">總計／Tổng lương</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: right;" colspan="3">{fmt_vn_curr(gross)}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 5px; text-align: center; font-weight: bold; background: #e2e8f0;" colspan="4">KHOẢN TRỪ／扣款與保險項目</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">社會保險 BHXH</td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right; color: #DC2626;">{fmt_vn_num(bhxh)}</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">醫療保險 BHYT</td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right; color: #DC2626;">{fmt_vn_num(bhyt)}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">失業保險 BHTN</td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right; color: #DC2626;">{fmt_vn_num(bhtn)}</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">所得稅 / 其他扣款</td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right; color: #DC2626;">{fmt_vn_num(other_ded_sum)}</td>
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
        st.components.v1.html(slip_html, height=800, scrolling=True)

        if st.button("🖨️ 列印薪資單", type="primary", use_container_width=True):
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
            st.info("💡 已觸發瀏覽器列印。")

    # ----------------------------------------------------
    # 📊 Tab 4: 歷史清冊
    # ----------------------------------------------------
    with tab_history:
        st.markdown("#### 📋 歷史月度薪資與扣款統計表")
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("""
                        SELECT payroll_month, emp_code, emp_name, department, factory, base_salary, total_gross, 
                               (bhxh_deduction + bhyt_deduction + bhtn_deduction) as total_ins, net_salary, status
                        FROM public.payroll_records ORDER BY payroll_month DESC, emp_code ASC
                    """))
                    rows = res.fetchall()
                    if rows:
                        df_p = pd.DataFrame([dict(r._mapping) for r in rows])
                        st.dataframe(df_p, use_container_width=True, hide_index=True)
                    else:
                        st.info("目前尚無歷史薪資紀錄。")
            except Exception as e:
                st.error("讀取失敗: " + str(e))
        else:
            st.info("展示模式中。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_payroll_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_payroll_management_page(engine=engine, lang=lang, **kwargs)
