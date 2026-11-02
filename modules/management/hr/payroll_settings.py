import streamlit as st
import json
from sqlalchemy import text

def init_settings_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            # 建立動態設定與動態欄位定義表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.erp_dynamic_fields (
                    id SERIAL PRIMARY KEY,
                    category VARCHAR(50) NOT NULL, -- 'income' (應領) 或 'deduct' (應扣)
                    field_key VARCHAR(100) UNIQUE NOT NULL,
                    field_name_zh VARCHAR(150) NOT NULL,
                    field_name_vn VARCHAR(150),
                    sort_order INT DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.payroll_settings (
                    id SERIAL PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    description TEXT,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # 初始化預設保險費率
            res = conn.execute(text("SELECT COUNT(*) FROM public.payroll_settings")).scalar()
            if res == 0:
                defaults = [
                    ("bhxh_rate", "8.0", "社會保險 %"),
                    ("bhyt_rate", "1.5", "醫療保險 %"),
                    ("bhtn_rate", "1.0", "失業保險 %")
                ]
                for k, v, d in defaults:
                    conn.execute(text("""
                        INSERT INTO public.payroll_settings (setting_key, setting_value, description)
                        VALUES (:k, :v, :d) ON CONFLICT (setting_key) DO NOTHING;
                    """), {"k": k, "v": v, "d": d})

            # 初始化預設應領與應扣動態欄位
            f_count = conn.execute(text("SELECT COUNT(*) FROM public.erp_dynamic_fields")).scalar()
            if f_count == 0:
                default_fields = [
                    ('income', 'pos_allowance', '職務津貼', 'PC chức vụ', 1),
                    ('income', 'eval_bonus', '評核獎金', 'Tiền thưởng đánh giá', 2),
                    ('income', 'gas_allowance', '出差油費', 'PC tiền xăng', 3),
                    ('income', 'spec_bonus', '工程補助', 'Pc.đi CT', 4),
                    ('income', 'meal_fee', '餐費', 'Tiền cơm', 5),
                    ('income', 'prod_bonus', '績效獎金', 'Thưởng N.Suất', 6),
                    ('income', 'network_fee', '電話/網路補貼', 'PC đt/mạng', 7),
                    ('income', 'warehouse_fee', '看倉管', 'Giữ kho', 8),
                    ('income', 'attendance_bonus', '全勤', 'Chuyên cần', 9),
                    ('deduct', 'pit_tax', '所得稅', 'TN cá nhân', 1),
                    ('deduct', 'advance_pay', '本月預支', 'Tạm ứng', 2),
                    ('deduct', 'other_deduct', '其他扣款', 'Khoản trừ khác', 3)
                ]
                for cat, f_key, f_zh, f_vn, order in default_fields:
                    conn.execute(text("""
                        INSERT INTO public.erp_dynamic_fields (category, field_key, field_name_zh, field_name_vn, sort_order)
                        VALUES (:cat, :key, :zh, :vn, :order) ON CONFLICT (field_key) DO NOTHING;
                    """), {"cat": cat, "key": f_key, "zh": f_zh, "vn": f_vn, "order": order})
    except Exception as e:
        print("Settings DB Init Error:", e)

def get_dynamic_fields(engine, category=None):
    if not engine:
        return []
    try:
        with engine.connect() as conn:
            if category:
                res = conn.execute(text("SELECT * FROM public.erp_dynamic_fields WHERE category = :cat AND is_active = TRUE ORDER BY sort_order ASC"), {"cat": category})
            else:
                res = conn.execute(text("SELECT * FROM public.erp_dynamic_fields WHERE is_active = TRUE ORDER BY category, sort_order ASC"))
            return [dict(r._mapping) for r in res.fetchall()]
    except Exception:
        return []

def get_payroll_setting(engine, key, default_val):
    if not engine:
        return default_val
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT setting_value FROM public.payroll_settings WHERE setting_key = :k"), {"k": key}).scalar()
            return res if res is not None else default_val
    except Exception:
        return default_val

def render_payroll_settings_tab(engine=None):
    st.markdown("### ⚙️ 高級 ERP 人事設定與動態欄位控制中心")
    st.caption("直接在網頁端新增、刪除或修改薪資單的應領/應扣欄位與保險費率百分比，完全不用改程式碼！")

    init_settings_db(engine)

    sub_tab1, sub_tab2 = st.tabs(["📑 薪資單欄位動態增修 (Metadata)", "🛡️ 保險費率動態設定 (%)"])

    # 1. 欄位動態增修 Tab
    with sub_tab1:
        st.markdown("#### ➕ 新增或管理薪資項目欄位")
        
        # 新增欄位表單
        with st.form("form_add_dynamic_field"):
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                new_cat = st.selectbox("項目類別", ["income (應領項目)", "deduct (應扣項目)"])
            with col_b:
                new_zh = st.text_input("中文名稱", placeholder="例如：高溫津貼")
            with col_c:
                new_vn = st.text_input("越文/英文代號", placeholder="PC nhiệt độ")
            with col_d:
                new_key = st.text_input("系統欄位英文 Key", placeholder="temp_allowance")

            if st.form_submit_button("➕ 立即新增欄位到系統", type="primary", use_container_width=True):
                if new_zh and new_key:
                    cat_val = "income" if "income" in new_cat else "deduct"
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.erp_dynamic_fields (category, field_key, field_name_zh, field_name_vn, sort_order)
                                    VALUES (:cat, :key, :zh, :vn, 99)
                                    ON CONFLICT (field_key) DO UPDATE SET field_name_zh = EXCLUDED.field_name_zh, is_active = TRUE;
                                """), {"cat": cat_val, "key": new_key, "zh": new_zh, "vn": new_vn})
                            st.success(f"✅ 成功新增欄位：{new_zh} ({new_key})！")
                            st.rerun()
                        except Exception as e:
                            st.error("❌ 新增失敗: " + str(e))
                else:
                    st.warning("⚠️ 請填寫中文名稱與系統欄位 Key。")

        st.markdown("---")
        st.markdown("#### 📋 現有系統動態欄位清單 (可停用或刪除)")
        fields = get_dynamic_fields(engine)
        if fields:
            for f in fields:
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                c1.text(f"[{f['category'].upper()}] {f['field_name_zh']}")
                c2.text(f"越文: {f['field_name_vn']}")
                c3.text(f"Key: {f['field_key']}")
                if c4.button("🗑️ 刪除", key=f"del_{f['id']}"):
                    if engine:
                        with engine.begin() as conn:
                            conn.execute(text("DELETE FROM public.erp_dynamic_fields WHERE id = :id"), {"id": f['id']})
                        st.success(f"已刪除 {f['field_name_zh']}")
                        st.rerun()

    # 2. 保險費率設定 Tab
    with sub_tab2:
        bhxh_r = float(get_payroll_setting(engine, "bhxh_rate", "8.0"))
        bhyt_r = float(get_payroll_setting(engine, "bhyt_rate", "1.5"))
        bhtn_r = float(get_payroll_setting(engine, "bhtn_rate", "1.0"))

        with st.form("form_insurance_setting"):
            st.markdown("#### 🛡️ 國家法定保險動態百分比 (%)")
            c1, c2, c3 = st.columns(3)
            with c1:
                new_bhxh = st.number_input("社會保險 BHXH (%)", min_value=0.0, max_value=100.0, value=bhxh_r, step=0.1)
            with c2:
                new_bhyt = st.number_input("醫療保險 BHYT (%)", min_value=0.0, max_value=100.0, value=bhyt_r, step=0.1)
            with c3:
                new_bhtn = st.number_input("失業保險 BHTN (%)", min_value=0.0, max_value=100.0, value=bhtn_r, step=0.1)

            if st.form_submit_button("💾 儲存保險費率百分比", type="primary", use_container_width=True):
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhxh_rate'"), {"v": str(new_bhxh)})
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhyt_rate'"), {"v": str(new_bhyt)})
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhtn_rate'"), {"v": str(new_bhtn)})
                        st.success("✅ 保險費率已更新！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 儲存失敗: " + str(e))
