import streamlit as st
import json
from sqlalchemy import text

def init_settings_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            # 建立動態欄位設定表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.erp_dynamic_fields (
                    id SERIAL PRIMARY KEY,
                    category VARCHAR(50) NOT NULL,
                    field_key VARCHAR(100) UNIQUE NOT NULL,
                    field_name_zh VARCHAR(150) NOT NULL,
                    field_name_vn VARCHAR(150),
                    default_amount NUMERIC(12,2) DEFAULT 0,
                    sort_order INT DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # 自動相容舊資料庫，若缺少 default_amount 欄位則自動補上
            try:
                conn.execute(text("ALTER TABLE public.erp_dynamic_fields ADD COLUMN IF NOT EXISTS default_amount NUMERIC(12,2) DEFAULT 0;"))
            except Exception:
                pass

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.payroll_settings (
                    id SERIAL PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    description TEXT,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # 初始化預設保險參數
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

            # 初始化預設項目
            f_count = conn.execute(text("SELECT COUNT(*) FROM public.erp_dynamic_fields")).scalar()
            if f_count == 0:
                default_fields = [
                    ('income', 'pos_allowance', '職務津貼', 'PC chức vụ', 3000000, 1),
                    ('income', 'eval_bonus', '評核獎金', 'Tiền thưởng đánh giá', 5567968, 2),
                    ('income', 'gas_allowance', '出差油費', 'PC tiền xăng', 6000000, 3),
                    ('income', 'spec_bonus', '工程補助', 'Pc.đi CT', 4000000, 4),
                    ('income', 'meal_fee', '餐費', 'Tiền cơm', 1200000, 5),
                    ('income', 'prod_bonus', '績效獎金', 'Thưởng N.Suất', 0, 6),
                    ('income', 'network_fee', '電話/網路補貼', 'PC đt/mạng', 0, 7),
                    ('income', 'warehouse_fee', '看倉管', 'Giữ kho', 0, 8),
                    ('income', 'attendance_bonus', '全勤', 'Chuyên cần', 0, 9),
                    ('deduct', 'pit_tax', '所得稅', 'TN cá nhân', 0, 1),
                    ('deduct', 'advance_pay', '本月預支', 'Tạm ứng', 0, 2),
                    ('deduct', 'other_deduct', '其他扣款', 'Khoản trừ khác', 0, 3)
                ]
                for cat, f_key, f_zh, f_vn, amt, order in default_fields:
                    conn.execute(text("""
                        INSERT INTO public.erp_dynamic_fields (category, field_key, field_name_zh, field_name_vn, default_amount, sort_order)
                        VALUES (:cat, :key, :zh, :vn, :amt, :order) ON CONFLICT (field_key) DO NOTHING;
                    """), {"cat": cat, "key": f_key, "zh": f_zh, "vn": f_vn, "amt": amt, "order": order})
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
    st.markdown("### 🎛️ 勞健保與薪資項目參數設定 (ERP Control Panel)")
    st.caption("直接在下方區塊設定費率與各項薪資津貼，系統自動對應，完全不需手動輸入程式碼代號。")

    init_settings_db(engine)

    bhxh_r = float(get_payroll_setting(engine, "bhxh_rate", "8.0"))
    bhyt_r = float(get_payroll_setting(engine, "bhyt_rate", "1.5"))
    bhtn_r = float(get_payroll_setting(engine, "bhtn_rate", "1.0"))

    # 1. 保險參數設定區塊
    st.markdown("---")
    st.markdown("#### 🛡️ 勞健保與法定費率參數設定")
    with st.form("form_erp_params"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_bhxh = st.number_input("社會保險費率 BHXH (%)", min_value=0.0, max_value=100.0, value=bhxh_r, step=0.1)
        with col2:
            new_bhyt = st.number_input("醫療保險費率 BHYT (%)", min_value=0.0, max_value=100.0, value=bhyt_r, step=0.1)
        with col3:
            new_bhtn = st.number_input("失業保險費率 BHTN (%)", min_value=0.0, max_value=100.0, value=bhtn_r, step=0.1)

        if st.form_submit_button("💾 儲存保險費率參數", type="primary", use_container_width=True):
            if engine:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhxh_rate'"), {"v": str(new_bhxh)})
                        conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhyt_rate'"), {"v": str(new_bhyt)})
                        conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhtn_rate'"), {"v": str(new_bhtn)})
                    st.success("✅ 保險參數儲存成功！")
                    st.rerun()
                except Exception as e:
                    st.error("❌ 儲存失敗: " + str(e))

    # 2. 薪資項目新增區塊
    st.markdown("---")
    st.markdown("#### 📑 薪資項目自由增修與預設金額設定")
    st.caption("只要輸入中文與越文名稱，系統自動幫您建立欄位！")

    with st.form("form_quick_add_field"):
        c_a, c_b, c_c, c_d = st.columns(4)
        with c_a:
            q_cat = st.selectbox("項目類別", ["應領項目 (Income)", "應扣項目 (Deduct)"])
        with c_b:
            q_zh = st.text_input("中文名稱", placeholder="例如：夜班津貼")
        with c_c:
            q_vn = st.text_input("越文名稱", placeholder="PC ca đêm")
        with c_d:
            q_amt = st.number_input("預設金額 (VND)", min_value=0.0, value=0.0, step=100000.0)

        if st.form_submit_button("➕ 新增薪資項目到系統", type="primary", use_container_width=True):
            if q_zh:
                cat_val = "income" if "應領" in q_cat else "deduct"
                import time
                auto_key = f"custom_field_{int(time.time())}"
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.erp_dynamic_fields (category, field_key, field_name_zh, field_name_vn, default_amount, sort_order)
                                VALUES (:cat, :key, :zh, :vn, :amt, 99)
                            """), {"cat": cat_val, "key": auto_key, "zh": q_zh, "vn": q_vn, "amt": q_amt})
                        st.success(f"✅ 成功新增項目：{q_zh}！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 新增失敗: " + str(e))
            else:
                st.warning("⚠️ 請至少輸入中文名稱。")

    # 3. 現有項目清單管理
    st.markdown("---")
    st.markdown("#### 📋 目前啟用的薪資項目清單")
    fields = get_dynamic_fields(engine)
    if fields:
        for f in fields:
            col_x1, col_x2, col_x3, col_x4 = st.columns([3, 3, 2, 1])
            col_x1.text(f"[{'應領' if f['category']=='income' else '應扣'}] {f['field_name_zh']}")
            col_x2.text(f"越文: {f['field_name_vn']}")
            col_x3.text(f"預設: {float(f.get('default_amount', 0)):,.0f} VND")
            if col_x4.button("🗑️ 刪除", key=f"del_item_{f['id']}"):
                if engine:
                    with engine.begin() as conn:
                        conn.execute(text("DELETE FROM public.erp_dynamic_fields WHERE id = :id"), {"id": f['id']})
                    st.success(f"已刪除 {f['field_name_zh']}")
                    st.rerun()
