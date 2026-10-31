import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def render_employee_list(engine=None, lang="繁體中文"):
    st.markdown("### 📑 現職員工總名冊與證件預警")
    if engine:
        try:
            df = pd.read_sql("SELECT emp_code, emp_name, department, position, staff_type, attendance_mode, base_salary, visa_expire FROM public.employee_profiles WHERE status = '在職';", con=engine)
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
                            conn.execute(text("UPDATE public.employee_profiles SET status = '離職' WHERE emp_code = :no;"), {"no": target_emp_no})
                        st.success(f"✅ 員工 `{selected_to_terminate}` 已成功辦理離職！")
                        st.rerun()
            else:
                st.info("目前尚無在職員工紀錄。請先至薪資模組批次匯入 Excel，系統將自動同步建立名冊！")
        except Exception:
            st.info("目前尚無在職員工紀錄。")
    else:
        st.info("資料庫引擎未連線。")
