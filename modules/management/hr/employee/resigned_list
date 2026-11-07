import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_resigned_list(engine=None, lang="繁體中文"):
    st.markdown("### 📁 離職名冊管理")
    if engine:
        try:
            df_resigned = pd.read_sql("SELECT emp_code, emp_name, department, position, staff_type FROM public.employee_profiles WHERE status = '離職';", con=engine)
            if not df_resigned.empty:
                st.dataframe(df_resigned, use_container_width=True, hide_index=True)
            else:
                st.info("目前無離職人員紀錄。")
        except Exception:
            st.info("目前無離職人員紀錄。")
    else:
        st.info("資料庫引擎未連線。")
