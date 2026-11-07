import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def init_hr_attendance_db(engine):
    """初始化出勤打卡資料表"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS hr_attendance (
                    punch_id VARCHAR(50) PRIMARY KEY,
                    emp_id VARCHAR(50),
                    emp_name VARCHAR(100),
                    date VARCHAR(50),
                    check_in VARCHAR(50),
                    check_out VARCHAR(50),
                    status VARCHAR(50)
                );
            """))
    except Exception as e:
        st.error(f"初始化出勤資料表失敗: {e}")

def render_attendance_punch(engine, lang="繁體中文"):
    init_hr_attendance_db(engine)
    st.markdown("##### ⏰ 廠內固定考勤打卡與異常追蹤 (Attendance & Punch)")
    st.info("💡 說明：記錄同仁每日上下班打卡時間，系統自動比對出勤狀態（正常、遲到、早退、曠職）。")

    punch_records = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT * FROM hr_attendance ORDER BY date DESC, punch_id DESC")).fetchall()
                for r in res:
                    punch_records.append({
                        "punch_id": r[0], "emp_id": r[1], "emp_name": r[2],
                        "date": r[3], "check_in": r[4], "check_out": r[5], "status": r[6]
                    })
        except Exception as e:
            st.warning(f"讀取打卡紀錄失敗: {e}")

    with st.form("punch_form"):
        st.markdown("##### ⏱️ 模擬手動/門禁打卡登錄")
        c1, c2, c3 = st.columns(3)
        with c1:
            p_emp_id = st.text_input("工號", value="EMP-001")
            p_name = st.text_input("姓名", value="Nguyễn Văn A")
        with c2:
            p_date = st.date_input("打卡日期", value=datetime.date.today())
            p_status = st.selectbox("出勤狀態", ["🟢 正常 (Normal)", "🟡 遲到 (Late)", "🔴 曠職 (Absent)", "🔵 請假 (Leave)"])
        with c3:
            p_in = st.text_input("上班時間 (HH:MM)", value="08:00")
            p_out = st.text_input("下班時間 (HH:MM)", value="17:00")

        if st.form_submit_button("🚀 登錄打卡紀錄至資料庫", type="primary", use_container_width=True):
            if p_emp_id and p_name:
                today_str = str(p_date)
                punch_id = f"PUNCH-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO hr_attendance (punch_id, emp_id, emp_name, date, check_in, check_out, status)
                                VALUES (:pid, :eid, :ename, :dt, :cin, :cout, :st)
                            """), {
                                "pid": punch_id, "eid": p_emp_id.strip(), "ename": p_name.strip(),
                                "dt": today_str, "cin": p_in.strip(), "cout": p_out.strip(), "st": p_status
                            })
                        st.success("✅ 打卡紀錄已成功寫入資料庫！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"寫入失敗: {e}")
            else:
                st.warning("請填寫完整資訊！")

    st.markdown("---")
    st.markdown("##### 📋 近期出勤打卡日誌與異常追蹤")
    if punch_records:
        st.dataframe(pd.DataFrame(punch_records), use_container_width=True, hide_index=True)
    else:
        st.info("目前尚無出勤打卡紀錄。")
