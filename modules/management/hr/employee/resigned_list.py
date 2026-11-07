# ==========================================
# 檔案路徑：modules/management/hr/employee/resigned_list.py
# 職責：離職人員名冊與狀態管理
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_resigned_list(engine=None, lang="繁體中文", **kwargs):
    st.subheader("📁 離職人員名冊與狀態管理")
    st.caption("在此檢視已辦理離職手續之員工名單，並可進行狀態恢復或歸檔查閱。")
    st.markdown("---")

    if engine:
        try:
            with engine.begin() as conn:
                query = """
                    SELECT emp_code, emp_name, department, position, staff_type, status, updated_at
                    FROM public.employee_profiles
                    WHERE status = '離職';
                """
                df = pd.read_sql(query, con=engine)

            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("目前尚無離職人員紀錄。")
        except Exception as e:
            st.warning(f"⚠️ 讀取離職名冊發生異常：{str(e)}")
    else:
        st.info("資料庫引擎未連線。")

def render(engine=None, lang="繁體中文", **kwargs):
    render_resigned_list(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_resigned_list(engine=engine, lang=lang, **kwargs)
