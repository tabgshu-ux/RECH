import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_management_payroll_audit(engine, lang="繁體中文"):
    st.markdown("### 💰 管理部專用：出勤時間、加班時數與薪資結算稽核")
    st.info("💡 說明：管理部可在此檢視所有工人的上下班打卡時間、現場照片與系統自動計算的加班時數，作為月底核發薪資與加班費的唯一依據。")

    logs = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT * FROM field_punch_logs ORDER BY punch_time DESC")).fetchall()
                for r in res:
                    logs.append({
                        "emp_id": r[1], "emp_name": r[2], "site_name": r[3],
                        "type": r[4], "photo": r[8], "time": r[9], "status": r[10], "note": r[11]
                    })
        except Exception:
            pass

    if logs:
        df = pd.DataFrame(logs)
        st.markdown("##### 📋 員工出勤與加班明細總覽")
        st.dataframe(df[["time", "emp_id", "emp_name", "site_name", "type", "note"]], use_container_width=True, hide_index=True)
    else:
        st.info("目前尚無出勤與打卡紀錄。")
