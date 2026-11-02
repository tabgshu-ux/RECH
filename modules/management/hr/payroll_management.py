import streamlit as st
import pandas as pd
from sqlalchemy import text

# ----------------------------------------------------
# 🇻🇳 越南法規標準金額格式化
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
# 🌐 資料庫初始化與動態設定表
# ----------------------------------------------------
def init_payroll_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            # 1. 薪資動態設定表 (儲存欄位名稱與保險費率)
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.payroll_settings (
                    id SERIAL PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    description TEXT,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            ;"""))

            # 初始化預設設定（若尚無設定）
            res = conn.execute(text("SELECT COUNT(*) FROM public.payroll_settings")).scalar()
            if res == 0:
                default_settings = [
                    ("bhxh_rate", "8.0", "社會保險百分比 (%)"),
                    ("bhyt_rate", "1.5", "醫療保險百分比 (%)"),
                    ("bhtn_rate", "1.0", "失業保險百分比 (%)"),
                    ("custom_income_fields", "職務津貼 (PC chức vụ),評核獎金 (Tiền thưởng đánh giá),出差油費 (PC tiền xăng),工程補助 (Pc.đi CT),績效獎金 (Thưởng N.Suất),電話/網路補貼 (PC đt/mạng),看倉管 (Giữ kho),全勤 (Chuyên cần)", "自訂應領項目欄位"),
                    ("custom_deduct_fields", "所得稅 (TN cá nhân),本月預支 (Tạm ứng),其他扣款 (Khoản trừ khác)", "自訂應扣項目欄位")
                ]
                for k, v, d in default_settings:
                    conn.execute(text("""
                        INSERT INTO public.payroll_settings (setting_key, setting_value, description)
                        VALUES (:k, :v, :d) ON CONFLICT (setting_key) DO NOTHING;
                    """), {"k": k, "v": v, "d": d})

            # 2. 薪資主檔紀錄表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.payroll_records (
                    id SERIAL PRIMARY KEY,
                    payroll_month VARCHAR(7) NOT NULL,
                    emp_code VARCHAR(50) NOT NULL,
                    emp_name VARCHAR(100) NOT NULL,
                    department VARCHAR(100),
                    factory VARCHAR(100) DEFAULT '西寧廠 (Tay Ninh)',
                    base_salary NUMERIC(12,2) DEFAULT 0,
                    allowances_json TEXT, -- 儲存動態應領項目與金額 JSON
                    ot_pay NUMERIC(12,2) DEFAULT 0,
                    meal_fee NUMERIC(12,2) DEFAULT 0,
                    deductions_json TEXT, -- 儲存動態應扣項目與金額 JSON
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
        print("DB Init Error:", e)

def get_setting(engine, key, default_val):
    if not engine:
        return default_val
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT setting_value FROM public.payroll_settings WHERE setting_key = :k"), {"k": key}).scalar()
            return res if res is not None else default_val
    except Exception:
        return default_val

# ----------------------------------------------------
# 頁面主體渲染
# ----------------------------------------------------
def render_payroll_management_page(engine=None, lang="繁體中文", **kwargs):
    st.title("💰 管理部 - 薪資計算與動態欄位設定中心")
    st.caption("支援人事自主設定應領/應扣欄位名稱、動態保險費率百分比調整與公司經典黑框 1:1 電子薪資條。")

    init_payroll_db(engine)

    # 分頁導覽：新增「⚙️ 薪資欄位與費率設定」
    tab_calc, tab_config, tab_slip, tab_history = st.tabs([
        "🧮 單筆薪資核算", 
        "⚙️ 薪資欄位與費率設定 (Settings)", 
        "📄 員工薪資單 (經典版)", 
        "📊 歷史薪資清冊"
    ])

    # ----------------------------------------------------
    # ⚙️ Tab 2: 薪資欄位與費率設定頁面 (人事自主設定)
    # ----------------------------------------------------
    with tab_config:
        st.markdown("### ⚙️ 企業薪資動態設定與費率控制台")
        st.caption("您可以在此隨時調整保險扣除百分比，以及新增或修改應領/應扣項目的欄位名稱！")

        # 讀取現有設定
        bhxh_r = float(get_setting(engine, "bhxh_rate", "8.0"))
        bhyt_r = float(get_setting(engine, "bhyt_rate", "1.5"))
        bhtn_r = float(get_setting(engine, "bhtn_rate", "1.0"))
        income_fields_str = get_setting(engine, "custom_income_fields", "")
        deduct_fields_str = get_setting(engine, "custom_deduct_fields", "")

        with st.form("form_payroll_settings"):
            st.markdown("##### 1️⃣ 國家法定/公司保險費率設定 (%)")
            c_f1, c_f2, c_f3 = st.columns(3)
            with c_f1:
                new_bhxh = st.number_input("社會保險費率 BHXH (%)", min_value=0.0, max_value=100.0, value=bhxh_r, step=0.1)
            with c_f2:
                new_bhyt = st.number_input("醫療保險費率 BHYT (%)", min_value=0.0, max_value=100.0, value=bhyt_r, step=0.1)
            with c_f3:
                new_bhtn = st.number_input("失業保險費率 BHTN (%)", min_value=0.0, max_value=100.0, value=bhtn_r, step=0.1)

            st.markdown("##### 2️⃣ 動態應領項目欄位名稱 (以逗號分隔)")
            new_income_fields = st.text_area("自訂應領津貼/獎金項目", value=income_fields_str, help="例如：職務津貼, 評核獎金, 出差油費, 工程補助, 績效獎金, 全勤獎金")

            st.markdown("##### 3️⃣ 動態應扣項目欄位名稱 (以逗號分隔)")
            new_deduct_fields = st.text_area("自訂應扣款項項目", value=deduct_fields_str, help="例如：所得稅, 本月預支, 其他扣款")

            if st.form_submit_button("💾 儲存並更新全系統薪資配置", type="primary", use_container_width=True):
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhxh_rate'"), {"v": str(new_bhxh)})
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhyt_rate'"), {"v": str(new_bhyt)})
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhtn_rate'"), {"v": str(new_bhtn)})
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'custom_income_fields'"), {"v": new_income_fields})
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'custom_deduct_fields'"), {"v": new_deduct_fields})
                        st.success("✅ 薪資設定更新成功！所有計算與薪資單將立即套用最新欄位與費率。")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 儲存設定失敗: " + str(e))
                else:
                    st.success("✅ [展示模式] 設定已暫存！")

    # ----------------------------------------------------
    # 🧮 Tab 1: 單筆薪資核算 (動態產生欄位輸入框)
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
        
        # 取得當前設定的動態項目
        curr_income_list = [x.strip() for x in get_setting(engine, "custom_income_fields", "").split(",") if x.strip()]
        curr_deduct_list = [x.strip() for x in get_setting(engine, "custom_deduct_fields", "").split(",") if x.strip()]
        
        curr_bhxh_pct = float(get_setting(engine, "bhxh_rate", "8.0"))
        curr_bhyt_pct = float(get_setting(engine, "bhyt_rate", "1.5"))
        curr_bhtn_pct = float(get_setting(engine, "bhtn_rate", "1.0"))

        with st.form("form_calc_payroll_dynamic"):
            st.markdown("##### 1️⃣ 基本薪資與動態應領項目")
            col1, col2 = st.columns(2)
            with col1:
                e_name = st.text_input("員工姓名 (越/中)", value="PHẠM HOÀNG LÂM\n范 皇 林")
                str_base_sal = st.text_input("約定底薪 Lương CB (保險計算基礎)", value="21.011.200")
                str_meal_fee = st.text_input("餐費 Tiền cơm", value="1.200.000")
            with col2:
                ot_pay = st.number_input("加班費總額 Tăng ca", min_value=0.0, value=0.0, step=1000.0)

            # 動態產生應領項目輸入框
            st.markdown("##### 2️⃣ 自訂應領項目數值設定 (動態載入)")
            income_inputs = {}
            inc_cols = st.columns(3)
            default_vals = {
                "職務津貼": 3000000, "評核獎金": 5567968, "出差油費": 6000000, 
                "工程補助": 4000000, "績效獎金": 0, "全勤": 0
            }
            for idx, field_name in enumerate(curr_income_list):
                col_target = inc_cols[idx % 3]
                def_v = default_vals.get(field_name.split("(")[0].strip(), 0)
                with col_target:
                    income_inputs[field_name] = st.text_input(f"➕ {field_name}", value=str(def_v))

            # 動態產生應扣項目輸入框
            st.markdown(f"##### 3️⃣ 自訂應扣項目與動態保險計算 (依底薪 × {curr_bhxh_pct}% 等)")
            deduct_inputs = {}
            ded_cols = st.columns(3)
            ded_defaults = {"所得稅": 180421, "本月預支": 0, "其他扣款": 0}
            for idx, field_name in enumerate(curr_deduct_list):
                col_target = ded_cols[idx % 3]
                def_v = ded_defaults.get(field_name.split("(")[0].strip(), 0)
                with col_target:
                    deduct_inputs[field_name] = st.text_input(f"➖ {field_name}", value=str(def_v))

            # 進行總金額計算
            base_sal = parse_vn_num(str_base_sal)
            meal_fee = parse_vn_num(str_meal_fee)
            
            total_allowances = sum([parse_vn_num(val) for val in income_inputs.values()])
            total_gross = base_sal + total_allowances + ot_pay + meal_fee

            # 動態百分比計算保險
            bhxh_val = base_sal * (curr_bhxh_pct / 100.0)
            bhyt_val = base_sal * (curr_bhyt_pct / 100.0)
            bhtn_val = base_sal * (curr_bhtn_pct / 100.0)
            insurance_total = bhxh_val + bhyt_val + bhtn_val

            other_deductions_total = sum([parse_vn_num(val) for val in deduct_inputs.values()])
            total_deduct = insurance_total + other_deductions_total
            net_pay = total_gross - total_deduct

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("合計總收入 (Tổng lương)", fmt_vn_curr(total_gross))
            m2.metric(f"保險及扣款總計 ({curr_bhxh_pct}%社保等)", fmt_vn_curr(total_deduct))
            m3.metric("本月實領金額 (THỰC LÃNH)", fmt_vn_curr(net_pay))

            import json
            if st.form_submit_button("💾 計算並寫入 Supabase 資料庫", type="primary", use_container_width=True):
                if engine:
                    try:
                        import json
                        allowances_json = json.dumps({k: parse_vn_num(v) for k, v in income_inputs.items()}, ensure_ascii=False)
                        deductions_json = json.dumps({k: parse_vn_num(v) for k, v in deduct_inputs.items()}, ensure_ascii=False)

                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.payroll_records 
                                (payroll_month, emp_code, emp_name, department, factory, base_salary, allowances_json, 
                                 ot_pay, meal_fee, deductions_json, total_gross, bhxh_deduction, bhyt_deduction, bhtn_deduction, net_salary)
                                VALUES (:m, :code, :name, :dept, :factory, :bs, :allow, :ot, :meal, :ded, :gross, :bhxh, :bhyt, :bhtn, :net)
                                ON CONFLICT (payroll_month, emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    department = EXCLUDED.department,
                                    factory = EXCLUDED.factory,
                                    base_salary = EXCLUDED.base_salary,
                                    allowances_json = EXCLUDED.allowances_json,
                                    ot_pay = EXCLUDED.ot_pay,
                                    meal_fee = EXCLUDED.meal_fee,
                                    deductions_json = EXCLUDED.deductions_json,
                                    total_gross = EXCLUDED.total_gross,
                                    bhxh_deduction = EXCLUDED.bhxh_deduction,
                                    bhyt_deduction = EXCLUDED.bhyt_deduction,
                                    bhtn_deduction = EXCLUDED.bhtn_deduction,
                                    net_salary = EXCLUDED.net_salary;
                            """), {
                                "m": payroll_m, "code": e_code, "name": e_name, "dept": dept_name, "factory": factory_sel,
                                "bs": base_sal, "allow": allowances_json, "ot": ot_pay, "meal": meal_fee, "ded": deductions_json,
                                "gross": total_gross, "bhxh": bhxh_val, "bhyt": bhyt_val, "bhtn": bhtn_val, "net": net_pay
                            })
                        st.success("✅ 薪資計算完畢並已動態寫入資料庫！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入資料庫失敗: " + str(e))

    # ----------------------------------------------------
    # 📄 Tab 3: 員工薪資單 (動態渲染欄位與經典黑框)
    # ----------------------------------------------------
    with tab_slip:
        st.markdown("### 📄 員工詳細薪資條 (動態欄位經典版)")
        st.caption("自動依據人事設定的動態項目與動態保險費率渲染 1:1 官方薪資條。")

        slip_records = []
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT * FROM public.payroll_records ORDER BY emp_code ASC"))
                    slip_records = [dict(r._mapping) for r in res.fetchall()]
            except Exception:
                pass

        if not slip_records:
            import json
            slip_records = [{
                "payroll_month": "2026-09", "emp_code": "2005010102", "emp_name": "PHẠM HOÀNG LÂM\n范 皇 林",
                "department": "GĐ CT 工程經理", "factory": "工程工地 (Site)", "base_salary": 21011200,
                "allowances_json": json.dumps({"職務津貼": 3000000, "評核獎金": 5567968, "出差油費": 6000000, "工程補助": 4000000}),
                "ot_pay": 0, "meal_fee": 1200000,
                "deductions_json": json.dumps({"所得稅": 180421}),
                "total_gross": 40779168, "bhxh_deduction": 1920896, "bhyt_deduction": 360168, "bhtn_deduction": 240112, "net_salary": 38078000
            }]

        col_op1, col_op2 = st.columns([2, 2])
        with col_op1:
            if st.button("🖨️ 一鍵批次列印全公司薪資條", type="primary", use_container_width=True):
                st.success(f"✅ 已成功產生共 {len(slip_records)} 張薪資條批次列印檔！")
        with col_op2:
            def get_display_name(raw):
                s = str(raw).replace("\r", "").replace("\n", " ")
                parts = [p for p in s.split(" ") if p]
                vn_parts = [p for p in parts if any(ord(c) < 128 for c in p)]
                cn_parts = [p for p in parts if any(ord(c) >= 128 for c in p)]
                return f"{' '.join(vn_parts)} - {' '.join(cn_parts)}"

            emp_options = {f"{r['emp_code']} - {get_display_name(r['emp_name'])}": r for r in slip_records}
            selected_emp_key = st.selectbox("🎯 選擇要檢視薪資條的員工", list(emp_options.keys()))
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
        meal_fe = float(target_slip.get('meal_fee', 0))
        ot_p = float(target_slip.get('ot_pay', 0))

        import json
        try:
            allowances_dict = json.loads(target_slip.get('allowances_json', '{}'))
        except Exception:
            allowances_dict = {}

        try:
            deductions_dict = json.loads(target_slip.get('deductions_json', '{}'))
        except Exception:
            deductions_dict = {}

        bhxh = float(target_slip.get('bhxh_deduction', 0))
        bhyt = float(target_slip.get('bhyt_deduction', 0))
        bhtn = float(target_slip.get('bhtn_deduction', 0))

        # 計算總收入 = 底薪 + 各動態津貼 + 加班 + 餐費
        allowance_sum = sum(float(v) for v in allowances_dict.values())
        gross = b_sal + allowance_sum + ot_p + meal_fe

        # 計算總扣款 = 保險 + 各動態扣款
        other_ded_sum = sum(float(v) for v in deductions_dict.values())
        total_deduct = bhxh + bhyt + bhtn + other_ded_sum
        net = gross - total_deduct

        # 动态產生 HTML 表格列
        allowance_rows_html = ""
        allow_items = list(allowances_dict.items())
        for i in range(0, len(allow_items), 2):
            k1, v1 = allow_items[i]
            k2, v2 = allow_items[i+1] if i+1 < len(allow_items) else ("", None)
            
            col2_html = f'<td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">{k2}</td><td style="border: 1px solid #000; padding: 6px; text-align: right;">{fmt_vn_num(v2)}</td>' if k2 else '<td style="border: 1px solid #000; padding: 6px; background: #fdfdfd;"></td><td style="border: 1px solid #000; padding: 6px;"></td>'
            allowance_rows_html += f"""
            <tr>
                <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">{k1}</td>
                <td style="border: 1px solid #000; padding: 6px; text-align: right;">{fmt_vn_num(v1)}</td>
                {col2_html}
            </tr>
            """

        slip_html = f"""
        <div style="border: 2px solid #000; padding: 25px; background-color: #FFFFFF; font-family: Arial, sans-serif; max-width: 780px; margin: auto; color: #000;">
            <div style="text-align: center; font-weight: bold; font-size: 16px; margin-bottom: 3px;">REETECH INDUSTRIAL CO.,LTD</div>
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
                {allowance_rows_html}
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">餐費 (Tiền cơm)</td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right;">{fmt_vn_num(meal_fe)}</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #fdfdfd; font-weight: bold;">加班費 (Tăng ca)</td>
                    <td style="border: 1px solid #000; padding: 6px; text-align: right;">{fmt_vn_num(ot_p)}</td>
                </tr>
                <tr style="font-weight: bold; background-color: #1E3A8A; color: white;">
                    <td style="border: 1px solid #000; padding: 8px;">總計／Tổng lương</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: right;" colspan="3">{fmt_vn_curr(gross)}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 5px; text-align: center; font-weight: bold; background: #e2e8f0;" colspan="4">KHOẢN TRỪ／動態扣款與保險項目</td>
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

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🖨️ 列印此張薪資單", type="primary", use_container_width=True):
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
            st.info("💡 已觸發瀏覽器列印。")

    # ----------------------------------------------------
    # 📊 Tab 4: 歷史薪資清冊查詢
    # ----------------------------------------------------
    with tab_history:
        st.markdown("#### 📋 歷史月度薪資與保險扣除統計表")
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
