# ==========================================
# 檔案路徑：modules/engineering/site_ops/field_leave_request.py
# 職責：外勤工程人員手機請假申請（串接主管簽核、管理部人事考勤與薪資計算）
# ==========================================

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_leave_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS hr_leave_requests (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        leave_no VARCHAR(64) UNIQUE NOT NULL,
                        employee_name VARCHAR(120) NOT NULL,
                        dept_or_role VARCHAR(120),
                        leave_type VARCHAR(64) NOT NULL,
                        start_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                        end_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                        leave_hours NUMERIC(6, 2) DEFAULT 8,
                        reason TEXT,
                        status VARCHAR(32) DEFAULT 'PENDING_SUPERVISOR',
                        payroll_batch_id VARCHAR(64),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def render(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "外勤工程人員"
    user_role = st.session_state.get("user_role") or "FIELD_ENGINEER"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    txt = {
        "zh": {
            "title": "📝 外勤人員請假申請",
            "sub": "提交請假單後自動送交部門主管簽核，核准後同步計入人事考勤與薪資結算。",
            "t1": "1️⃣ 填寫請假申請",
            "t2": "2️⃣ 我的請假與簽核進度",
            "ltype": "假別",
            "s_date": "開始日期",
            "s_time": "開始時間",
            "e_date": "結束日期",
            "e_time": "結束時間",
            "hours": "請假總時數（小時）",
            "reason": "請假事由說明",
            "submit": "📨 送出請假申請",
            "ok": "✅ 已送出請假單 `{}`，等待主管簽核。",
            "empty": "目前尚無請假紀錄。",
        },
        "vi": {
            "title": "📝 Đơn Xin Nghỉ Phép Kỹ Sư Hiện Trường",
            "sub": "Gửi đơn xin nghỉ phép để trưởng bộ phận duyệt và tự động đồng bộ sang bảng công / tính lương.",
            "t1": "1️⃣ Tạo Đơn Xin Nghỉ",
            "t2": "2️⃣ Lịch Sử Nghỉ Phép Của Tôi",
            "ltype": "Loại Nghỉ Phép",
            "s_date": "Từ Ngày",
            "s_time": "Giờ Bắt Đầu",
            "e_date": "Đến Ngày",
            "e_time": "Giờ Kết Thúc",
            "hours": "Tổng Số Giờ Nghỉ",
            "reason": "Lý Do Xin Nghỉ",
            "submit": "📨 Gửi Đơn Xin Nghỉ Phép",
            "ok": "✅ Đã gửi đơn xin nghỉ `{}`, đang chờ duyệt.",
            "empty": "Chưa có dữ liệu nghỉ phép.",
        },
        "en": {
            "title": "📝 Field Engineer Leave Request",
            "sub": "Submit leave requests for manager approval and automatic sync to HR attendance and payroll.",
            "t1": "1️⃣ Submit Leave Request",
            "t2": "2️⃣ My Leave History",
            "ltype": "Leave Type",
            "s_date": "Start Date",
            "s_time": "Start Time",
            "e_date": "End Date",
            "e_time": "End Time",
            "hours": "Total Leave Hours",
            "reason": "Reason",
            "submit": "📨 Submit Leave Request",
            "ok": "✅ Submitted leave request `{}` for approval.",
            "empty": "No leave records yet.",
        },
    }[code]

    st.markdown(f"### {txt['title']}")
    st.caption(txt["sub"])
    _ensure_leave_table(engine)

    tab1, tab2 = st.tabs([txt["t1"], txt["t2"]])

    with tab1:
        with st.form("form_field_leave_req"):
            leave_type = st.selectbox(
                txt["ltype"],
                ["特休 / 年假 (Phép năm)", "病假 (Nghỉ ốm)", "事假 (Nghỉ việc riêng)", "公假 / 補休 (Nghỉ bù)"],
            )
            c1, c2 = st.columns(2)
            with c1:
                s_date = st.date_input(txt["s_date"], value=now_vn.date())
                s_time = st.time_input(txt["s_time"], value=time(8, 0), step=1800)
            with c2:
                e_date = st.date_input(txt["e_date"], value=now_vn.date())
                e_time = st.time_input(txt["e_time"], value=time(17, 0), step=1800)

            leave_hours = st.number_input(txt["hours"], min_value=1.0, max_value=240.0, value=8.0, step=1.0)
            reason = st.text_area(txt["reason"], placeholder="請簡述請假原因與職務代理人...")

            if st.form_submit_button(txt["submit"], type="primary", use_container_width=True):
                start_dt = datetime.combine(s_date, s_time)
                end_dt = datetime.combine(e_date, e_time)
                if end_dt <= start_dt:
                    st.warning("⚠️ 結束時間必須晚於開始時間。")
                elif not reason.strip():
                    st.warning("⚠️ 請填寫請假事由。")
                elif not engine:
                    st.error("❌ 尚未連線資料庫。")
                else:
                    leave_no = f"LV-{now_vn.strftime('%Y%m%d-%H%M%S')}"
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO hr_leave_requests (
                                        tenant_id, leave_no, employee_name, dept_or_role,
                                        leave_type, start_at, end_at, leave_hours, reason, status
                                    )
                                    VALUES (
                                        :tid, :lno, :ename, :drole,
                                        :ltype, :sat, :eat, :hrs, :rsn, 'PENDING_SUPERVISOR'
                                    )
                                """),
                                {
                                    "tid": tenant_id,
                                    "lno": leave_no,
                                    "ename": user_name,
                                    "drole": user_role,
                                    "ltype": leave_type,
                                    "sat": start_dt,
                                    "eat": end_dt,
                                    "hrs": float(leave_hours),
                                    "rsn": reason.strip(),
                                },
                            )
                        st.success(txt["ok"].format(leave_no))
                    except Exception as e:
                        st.error(f"❌ 送出請假單失敗：{e}")

    with tab2:
        if not engine:
            st.info(txt["empty"])
            return
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text("""
                        SELECT leave_no AS "請假單號", leave_type AS "假別",
                               TO_CHAR(start_at, 'YYYY-MM-DD HH24:MI') AS "開始時間",
                               TO_CHAR(end_at, 'YYYY-MM-DD HH24:MI') AS "結束時間",
                               leave_hours AS "時數", status AS "簽核狀態", reason AS "事由"
                        FROM hr_leave_requests
                        WHERE tenant_id = :tid AND employee_name = :ename
                        ORDER BY id DESC
                        LIMIT 20
                    """),
                    {"tid": tenant_id, "ename": user_name},
                ).fetchall()
                if not rows:
                    st.info(txt["empty"])
                else:
                    st.dataframe(pd.DataFrame([r._asdict() for r in rows]), use_container_width=True, hide_index=True)
        except Exception:
            st.info(txt["empty"])


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
