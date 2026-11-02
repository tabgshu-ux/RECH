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

def render_payroll_settings_tab(engine=None):
    st.markdown("### ⚙️ 高級 ERP 人事與薪資欄位動態設定中心")
    st.caption("完全透過網頁端自主設定：自由增減應領/應扣欄位名稱、調整保險扣除百分比（%）及員工資料表欄位。")

    init_settings_db(engine)

    # 內部再分子 Tab 讓畫面乾淨、高級
    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        "📑 薪資單欄位與項目設定", 
        "🛡️ 保險費率動態設定 (%)", 
        "📋 員工資料表欄位設定"
    ])

    bhxh_r = float(get_payroll_setting(engine, "bhxh_rate", "8.0"))
    bhyt_r = float(get_payroll_setting(engine, "bhyt_rate", "1.5"))
    bhtn_r = float(get_payroll_setting(engine, "bhtn_rate", "1.0"))
    income_str = get_payroll_setting(engine, "income_fields", "")
    deduct_str = get_payroll_setting(engine, "deduct_fields", "")
    profile_str = get_payroll_setting(engine, "profile_fields", "")

    with sub_tab1:
        st.markdown("#### 📑 薪資單應領與應扣項目動態維護")
        st.caption("在此新增、刪除或修改薪資單上的各項津貼、獎金與扣款欄位名稱（以逗號分隔）。")
        with st.form("form_fields_setting"):
            new_income = st.text_area("➕ 應領項目欄位設定 (Income Fields)", value=income_str, help="例如：職務津貼, 評核獎金, 出差油費...")
            new_deduct = st.text_area("➖ 應扣項目欄位設定 (Deduction Fields)", value=deduct_str, help="例如：所得稅, 本月預支, 其他扣款...")
            
            if st.form_submit_button("💾 儲存欄位設定", type="primary", use_container_width=True):
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'income_fields'"), {"v": new_income})
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'deduct_fields'"), {"v": new_deduct})
                        st.success("✅ 薪資單欄位設定已成功更新！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 儲存失敗: " + str(e))
                else:
                    st.success("✅ [展示模式] 欄位設定已暫存！")

    with sub_tab2:
        st.markdown("#### 🛡️ 國家法定保險動態百分比 (%)")
        st.caption("當越南社會保險、醫療保險或失業保險費率調整時，可直接在此修改，系統計算與薪資單將自動套用。")
        with st.form("form_insurance_setting"):
            c1, c2, c3 = st.columns(3)
            with c1:
                new_bhxh = st.number_input("社會保險 BHXH (%)", min_value=0.0, max_value=100.0, value=bhxh_r, step=0.1)
            with c2:
                new_bhyt = st.number_input("醫療保險 BHYT (%)", min_value=0.0, max_value=100.0, value=bhyt_r, step=0.1)
            with c3:
                new_bhtn = st.number_input("失業保險 BHTN (%)", min_value=0.0, max_value=100.0, value=bhtn_r, step=0.1)

            if st.form_submit_button("💾 儲存保險費率", type="primary", use_container_width=True):
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhxh_rate'"), {"v": str(new_bhxh)})
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhyt_rate'"), {"v": str(new_bhyt)})
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'bhtn_rate'"), {"v": str(new_bhtn)})
                        st.success("✅ 保險費率百分比已成功更新！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 儲存失敗: " + str(e))
                else:
                    st.success("✅ [展示模式] 保險費率已暫存！")

    with sub_tab3:
        st.markdown("#### 📋 員工基本資料表欄位自訂")
        st.caption("自訂員工檔案需要收集與顯示的欄位結構。")
        with st.form("form_profile_setting"):
            new_profile = st.text_input("員工資料欄位 (以逗號分隔)", value=profile_str)
            if st.form_submit_button("💾 儲存員工資料表設定", type="primary", use_container_width=True):
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE public.payroll_settings SET setting_value = :v WHERE setting_key = 'profile_fields'"), {"v": new_profile})
                        st.success("✅ 員工資料表欄位設定已更新！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 儲存失敗: " + str(e))
                else:
                    st.success("✅ [展示模式] 已暫存！")
