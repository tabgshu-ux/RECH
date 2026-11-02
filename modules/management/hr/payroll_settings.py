import streamlit as st
from sqlalchemy import text

def init_settings_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.payroll_settings (
                    id SERIAL PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    description TEXT,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            res = conn.execute(text("SELECT COUNT(*) FROM public.payroll_settings")).scalar()
            if res == 0:
                defaults = [
                    ("bhxh_rate", "8.0", "社會保險 %"),
                    ("bhyt_rate", "1.5", "醫療保險 %"),
                    ("bhtn_rate", "1.0", "失業保險 %"),
                    ("income_fields", "職務津貼 (PC chức vụ),評核獎金 (Tiền thưởng đánh giá),出差油費 (PC tiền xăng),工程補助 (Pc.đi CT),餐費 (Tiền cơm),績效獎金 (Thưởng N.Suất),電話/網路補貼 (PC đt/mạng),看倉管 (Giữ kho),全勤 (Chuyên cần)", "應領項目"),
                    ("deduct_fields", "所得稅 (TN cá nhân),本月預支 (Tạm ứng),其他扣款 (Khoản trừ khác)", "應扣項目"),
                    ("profile_fields", "工號,姓名(越/中),部門,職務,廠區,底薪,電話,入職日期", "員工資料表自訂欄位")
                ]
                for k, v, d in defaults:
                    conn.execute(text("""
                        INSERT INTO public.payroll_settings (setting_key, setting_value, description)
                        VALUES (:k, :v, :d) ON CONFLICT (setting_key) DO NOTHING;
                    """), {"k": k, "v": v, "d": d})
    except Exception as e:
        print("Settings DB Init Error:", e)

def get_payroll_setting(engine, key, default_val):
    if not engine:
        return default_val
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT setting_value FROM public.payroll_settings WHERE setting_key = :k"), {"k": key}).scalar()
            return res if res is not None else default_val
    except Exception:
        return default_val

def render_payroll_settings_page(engine=None, **kwargs):
    st.markdown("### ⚙️ 人事設定與欄位管理控制台")
    st.caption("在此獨立設定薪資單的「應領項目」、「應扣項目」、員工資料欄位與動態保險費率百分比（%）。")

    init_settings_db(engine)

    bhxh_r = float(get_payroll_setting(engine, "bhxh_rate", "8.0"))
    bhyt_r = float(get_payroll_setting(engine, "bhyt_rate", "1.5"))
    bhtn_r = float(get_payroll_setting(engine, "bhtn_rate", "1.0"))
    income_str = get_payroll_setting(engine, "income_fields", "")
    deduct_str = get_payroll_setting(engine, "deduct_fields", "")
    profile_str = get_payroll_setting(engine, "profile_fields", "")

    with st.form("form_standalone_hr_settings"):
        st.markdown("##### 1️⃣ 國家法定/公司保險動態百分比 (%)")
        c1, c2, c3 = st.columns(3)
        with c1:
            new_bhxh = st.number_input("社會保險 BHXH (%)", min_value=0.0, max_value=100.0, value=bhxh_r, step=0.1)
        with c2:
            new_bhyt = st.number_input("醫療保險 BHYT (%)", min_value=0.0, max_value=100.0, value=bhyt_r, step=0.1)
        with c3:
            new_bhtn = st.number_input("失業保險 BHTN (%)", min_value=0.0, max_value=100.0, value=bhtn_r, step=0.1)

        st.markdown("##### 2️⃣ 薪資單應領項目欄位名稱 (以逗號分隔)")
        new_income = st.text_area("設定應領津貼/獎金項目", value=income_str)

        st.markdown("##### 3️⃣ 薪資單應扣項目欄位名稱 (以逗號分隔)")
        new_deduct = st.text_area("設定應扣款項項目", value=deduct_str)

        st.markdown("##### 4️⃣ 員工基本資料表欄位自訂")
        new_profile = st.text_input("設定員工檔案資料欄位", value=profile_str)

        if st.form_submit_button("💾 儲存人事設定", type="primary", use_container_width=True):
            if engine:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhxh_rate'"), {"v": str(new_bhxh)})
                        conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhyt_rate'"), {"v": str(new_bhyt)})
                        conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhtn_rate'"), {"v": str(new_bhtn)})
                        conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'income_fields'"), {"v": new_income})
                        conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'deduct_fields'"), {"v": new_deduct})
                        conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'profile_fields'"), {"v": new_profile})
                    st.success("✅ 人事設定已成功儲存並生效！")
                    st.rerun()
                except Exception as e:
                    st.error("❌ 儲存失敗: " + str(e))
            else:
                st.success("✅ [展示模式] 設定已暫存！")
