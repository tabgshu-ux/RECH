from datetime import datetime, time
import streamlit as st
from modules.approval.workflow_repo import create_leave_request


def render(engine, tenant_id: str, user_name: str, user_role: str, project_id: str | None, now_vn: datetime):
    st.markdown("#### 📝 1. 員工請假申請")
    st.info("提交請假單後自動送交部門主管簽核，核准後同步計入人事考勤與薪資結算。")
    with st.form("wf_form_leave"):
        leave_type = st.selectbox("假別*", ["特休 / 年假 (Phép năm)", "病假 (Nghỉ ốm)", "事假 (Nghỉ việc riêng)", "公假 / 補休 (Nghỉ bù)"])
        c1, c2 = st.columns(2)
        with c1:
            s_date = st.date_input("開始日期", value=now_vn.date())
            s_time = st.time_input("開始時間", value=time(8, 0), step=1800)
        with c2:
            e_date = st.date_input("結束日期", value=now_vn.date())
            e_time = st.time_input("結束時間", value=time(17, 0), step=1800)
        leave_hours = st.number_input("請假總時數（小時）", min_value=1.0, max_value=240.0, value=8.0, step=1.0)
        reason = st.text_area("請假事由與代理人說明*", placeholder="請輸入請假事由與職務代理人...")
        if st.form_submit_button("📨 送出請假申請單", type="primary", use_container_width=True):
            start_dt, end_dt = datetime.combine(s_date, s_time), datetime.combine(e_date, e_time)
            if end_dt <= start_dt:
                st.warning("⚠️ 結束時間必須晚於開始時間。")
            elif not reason.strip():
                st.warning("⚠️ 請填寫請假事由。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                try:
                    lno = create_leave_request(engine, tenant_id, user_name, user_role, project_id, leave_type, start_dt, end_dt, float(leave_hours), reason.strip(), now_vn)
                    st.success(f"✅ 已提交請假單 `{lno}`，送交部門主管審核。")
                except Exception as e:
                    st.error(f"❌ 送出請假單失敗：{e}")
