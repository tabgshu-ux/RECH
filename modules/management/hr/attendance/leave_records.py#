import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def init_hr_leave_db(engine):
    """初始化請假紀錄資料表"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS hr_leaves (
                    leave_id VARCHAR(50) PRIMARY KEY,
                    emp_id VARCHAR(50),
                    emp_name VARCHAR(100),
                    leave_type VARCHAR(50),
                    start_date VARCHAR(50),
                    end_date VARCHAR(50),
                    reason TEXT,
                    status VARCHAR(50) DEFAULT '待審核'
                );
            """))
    except Exception as e:
        st.error(f"初始化請假資料表失敗: {e}")

def render_leave_records(engine, lang="繁體中文"):
    init_hr_leave_db(engine)
    st.markdown("##### 📝 請假申請與審核紀錄 (Leave Application)")
    st.info("💡 說明：同仁請假申請與歷史審核紀錄。（註：正式請假單路由可連動【電子簽核中心】統一審核）")

    leaves = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT * FROM hr_leaves ORDER BY leave_id DESC")).fetchall()
                for r in res:
                    leaves.append({
                        "leave_id": r[0], "emp_id": r[1], "emp_name": r[2],
                        "leave_type": r[3], "start_date": r[4], "end_date": r[5],
                        "reason": r[6], "status": r[7]
                    })
        except Exception as e:
            st.warning(f"讀取請假紀錄失敗: {e}")

    with st.form("leave_form"):
        c1, c2 = st.columns(2)
        with c1:
            l_emp_id = st.text_input("工號", value="EMP-001")
            l_name = st.text_input("姓名", value="Nguyễn Văn A")
            l_type = st.selectbox("請假假別", ["事假 (Personal Leave)", "病假 (Sick Leave)", "特休假 (Annual Leave)", "婚喪假 (Special Leave)"])
        with c2:
            l_start = st.date_input("開始日期", value=datetime.date.today())
            l_end = st.date_input("結束日期", value=datetime.date.today())
            l_reason = st.text_input("請假事由", placeholder="請輸入請假原因...")

        if st.form_submit_button("🚀 提交請假申請", type="primary", use_container_width=True):
            if l_emp_id and l_name:
                leave_id = f"LEAVE-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO hr_leaves (leave_id, emp_id, emp_name, leave_type, start_date, end_date, reason, status)
                                VALUES (:lid, :eid, :ename, :ltype, :sdt, :edt, :rsn, :st)
                            """), {
                                "lid": leave_id, "eid": l_emp_id.strip(), "ename": l_name.strip(),
                                "ltype": l_type, "sdt": str(l_start), "edt": str(l_end),
                                "rsn": l_reason.strip(), "st": "待審核 (Pending)"
                            })
                        st.success("✅ 請假申請已成功送出並記錄至資料庫！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"寫入失敗: {e}")
            else:
                st.warning("請填寫必要欄位！")

    st.markdown("---")
    st.markdown("##### 📋 歷史請假紀錄總覽")
    if leaves:
        st.dataframe(pd.DataFrame(leaves), use_container_width=True, hide_index=True)
    else:
        st.info("目前無請假紀錄。")
