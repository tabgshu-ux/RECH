import datetime
import pandas as pd
import streamlit as st
from sqlalchemy import text


def init_hr_leave_db(engine):
    """初始化請假紀錄資料表（含租戶欄位）"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS hr_leaves (
                    leave_id VARCHAR(50) PRIMARY KEY,
                    tenant_id VARCHAR(64) DEFAULT 'REETECH_VN',
                    emp_id VARCHAR(50),
                    emp_name VARCHAR(100),
                    leave_type VARCHAR(50),
                    start_date VARCHAR(50),
                    end_date VARCHAR(50),
                    reason TEXT,
                    status VARCHAR(50) DEFAULT '待審核'
                );
            """))
            conn.execute(text("ALTER TABLE hr_leaves ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(64) DEFAULT 'REETECH_VN';"))
    except Exception as e:
        st.error(f"初始化請假資料表失敗: {e}")


def get_approved_leave_days_by_employee(engine, tenant_id: str = "REETECH_VN", pay_month: str | None = None) -> dict[str, float]:
    """供薪資模組呼叫：彙整每位員工請假天數 {emp_name: total_days}"""
    result: dict[str, float] = {}
    if not engine:
        return result
    try:
        with engine.connect() as conn:
            sql = """
                SELECT emp_name, start_date, end_date, COALESCE(status, '') AS status
                FROM hr_leaves
                WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
            """
            rows = conn.execute(text(sql), {"tid": tenant_id}).fetchall()
            for r in rows:
                ename = str(r[1] if False else (r[1] or "")).strip()
                if not ename:
                    continue
                try:
                    d1 = datetime.date.fromisoformat(str(r[2])[:10])
                    d2 = datetime.date.fromisoformat(str(r[3])[:10])
                    if pay_month and not (str(r[2]).startswith(pay_month) or str(r[3]).startswith(pay_month)):
                        continue
                    days = max(1, (d2 - d1).days + 1)
                    result[ename] = result.get(ename, 0.0) + float(days)
                except Exception:
                    continue
    except Exception:
        pass
    return result


def render_leave_records(engine, lang="繁體中文", **kwargs):
    init_hr_leave_db(engine)
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    st.markdown("##### 📝 請假申請與審核紀錄 (Leave Application)")
    st.info("💡 說明：同仁請假申請與歷史審核紀錄。（註：正式請假單路由可連動【電子簽核中心】統一審核）")

    leaves = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(
                    text("""
                        SELECT leave_id, emp_id, emp_name, leave_type, start_date, end_date, reason, status
                        FROM hr_leaves
                        WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                        ORDER BY leave_id DESC
                    """),
                    {"tid": tenant_id},
                ).fetchall()
                for r in res:
                    leaves.append({
                        "leave_id": r[0], "emp_id": r[1], "emp_name": r[2],
                        "leave_type": r[3], "start_date": r[4], "end_date": r[5],
                        "reason": r[6], "status": r[7],
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
                            conn.execute(
                                text("""
                                    INSERT INTO hr_leaves (leave_id, tenant_id, emp_id, emp_name, leave_type, start_date, end_date, reason, status)
                                    VALUES (:lid, :tid, :eid, :ename, :ltype, :sdt, :edt, :rsn, :st)
                                """),
                                {
                                    "lid": leave_id, "tid": tenant_id, "eid": l_emp_id.strip(),
                                    "ename": l_name.strip(), "ltype": l_type, "sdt": str(l_start),
                                    "edt": str(l_end), "rsn": l_reason.strip(), "st": "待審核 (Pending)",
                                },
                            )
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


def render(engine=None, lang="繁體中文", **kwargs):
    return render_leave_records(engine=engine, lang=lang, **kwargs)


def show(engine=None, lang="繁體中文", **kwargs):
    return render_leave_records(engine=engine, lang=lang, **kwargs)
