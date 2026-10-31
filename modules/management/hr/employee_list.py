import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def render_employee_list(engine=None, lang="繁體中文"):
    st.markdown("### 📑 現職員工總名冊與證件預警")
    if engine:
        try:
            with engine.begin() as conn:
                # 🛡️ 自動補全可能缺少的欄位，避免資料庫結構不一致報錯
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS staff_type VARCHAR(100) DEFAULT '越南籍員工';"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS attendance_mode VARCHAR(50) DEFAULT '需打卡';"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS visa_expire DATE DEFAULT '2027-12-31';"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT '在職';"))

            # 💡 安全且相容的查詢語法
            query = """
                SELECT DISTINCT 
                    COALESCE(e.emp_code, p.emp_code) as emp_code,
                    COALESCE(e.emp_name, p.emp_name) as emp_name,
                    COALESCE(e.department, p.department) as department,
                    COALESCE(e.position, '-') as position,
                    COALESCE(e.staff_type, '越南籍員工 (VN Local Staff)') as staff_type,
                    COALESCE(e.attendance_mode, '需打卡 (Required Punch)') as attendance_mode,
                    COALESCE(e.base_salary, p.base_salary, 0) as base_salary,
                    COALESCE(e.visa_expire, '2027-12-31') as visa_expire,
                    COALESCE(e.status, '在職') as status
                FROM public.payroll_records p
                FULL OUTER JOIN public.employee_profiles e ON p.emp_code = e.emp_code
                WHERE COALESCE(e.status, '在職', p.status) = '在職';
            """
            df = pd.read_sql(query, con=engine)
            
            if not df.empty:
                category_filter = st.radio("📂 選擇檢視群組", ["🇻🇳 越南籍員工名冊", "🌐 外派與外籍幹部名冊", "📋 全部員工總名冊"], horizontal=True)
                
                if "越南籍員工" in category_filter:
                    df_view = df[~df["staff_type"].str.contains("外派|外籍|Expat", na=False)]
                elif "外派與外籍幹部" in category_filter:
                    df_view = df[df["staff_type"].str.contains("外派|外籍|Expat", na=False)]
                else:
                    df_view = df

                today_date = datetime.date.today()
                expiring_soon = []
                for _, row in df.iterrows():
                    v_exp = row.get("visa_expire")
                    if v_exp and "外派" in str(row.get("staff_type", "")):
                        if isinstance(v_exp, str):
                            try:
                                v_exp = datetime.datetime.strptime(v_exp, "%Y-%m-%d").date()
                            except:
                                continue
                        days_left = (v_exp - today_date).days
                        if days_left <= 90:
                            expiring_soon.append((row["emp_code"], row["emp_name"], v_exp, days_left))

                if expiring_soon:
                    st.error("🚨 外派/外籍幹部證件（簽證/TRC/護照）90天前提前到期預警（越南辦事需時3個月）")
                    for eno, ename, edate, dleft in expiring_soon:
                        if dleft < 0:
                            st.markdown(f"🔴 **【已過期】** 幹部：`{eno} - {ename}` (證件到期日：`{edate}`，已逾期 `{abs(dleft)}` 天！)")
                        else:
                            st.markdown(f"⚠️ **【90天內到期提醒】** 幹部：`{eno} - {ename}` (證件到期日：`{edate}`，僅剩 `{dleft}` 天，請盡速送件)")
                    st.markdown("---")

                search_query = st.text_input("🔍 搜尋員工姓名、工號或部門篩選", placeholder="輸入工號、姓名或部門關鍵字...")
                if search_query:
                    mask = df_view.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
                    df_filtered = df_view[mask]
                else:
                    df_filtered = df_view

                st.dataframe(df_filtered, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.markdown("#### 🔄 員工離職狀態異動與結清處理")
                active_emp_list = [f"{r['emp_code']} - {r['emp_name']}" for _, r in df.iterrows()]
                selected_to_terminate = st.selectbox("選擇要辦理離職的員工 (工號 - 姓名)", active_emp_list)
                
                if st.button("🔴 辦理離職手續並移至離職名冊", type="secondary"):
                    if selected_to_terminate:
                        target_emp_no = selected_to_terminate.split(" - ")[0]
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.employee_profiles (emp_code, emp_name, status)
                                VALUES (:no, :name, '離職')
                                ON CONFLICT (emp_code) DO UPDATE SET status = '離職';
                            """), {"no": target_emp_no, "name": selected_to_terminate.split(" - ")[1]})
                        st.success(f"✅ 員工 `{selected_to_terminate}` 已成功辦理離職！")
                        st.rerun()
            else:
                st.info("目前尚無在職員工紀錄。請先至【員工薪資與保險】頁面建立薪資或匯入 Excel，名冊將會自動同步顯示！")
        except Exception as e:
            st.warning(f"⚠️ 讀取名冊發生異常：{str(e)}")
    else:
        st.info("資料庫引擎未連線。")
