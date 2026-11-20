# ==========================================
# 檔案路徑：modules/approval_workflow.py
# 職責：全公司電子簽核中心（派車申請含時分、請假審核、簽核進度與門禁放行）
# ==========================================

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_approval_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS approval_vehicle_dispatches (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        dispatch_no VARCHAR(64) UNIQUE NOT NULL,
                        project_id VARCHAR(80),
                        applicant_name VARCHAR(120) NOT NULL,
                        dept_or_role VARCHAR(120),
                        vehicle_plate VARCHAR(120) NOT NULL,
                        driver_name VARCHAR(120),
                        purpose_type VARCHAR(100),
                        destination VARCHAR(200) NOT NULL,
                        reason_detail TEXT,
                        depart_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                        return_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                        status VARCHAR(32) DEFAULT 'PENDING_SUPERVISOR',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
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


def _render_vehicle_dispatch_tab(engine, tenant_id: str, user_name: str, user_role: str, now_vn: datetime, code: str):
    txt = {
        "zh": {
            "hdr": "🚗 3. 廠區公務派車申請單",
            "flow": "派車申請流程：員工填單 ➔ 部門主管簽核 ➔ 門禁保全確認出廠放行與里程登記。",
            "app_name": "申請人姓名（系統綁定）*",
            "dept_role": "所屬部門（系統綁定）",
            "veh": "選擇公務車輛／車號*",
            "drv": "駕駛員／司機姓名",
            "ptype": "派車用途類別*",
            "dest": "前往目的地／案場名稱*",
            "reason": "派車公務事由與詳細說明*",
            "dep_date": "預計出廠日期",
            "dep_time": "預計出廠時間（時:分）",
            "ret_date": "預計返回日期",
            "ret_time": "預計返回時間（時:分）",
            "submit": "📨 提交派車申請單送部門主管審核",
            "time_err": "⚠️ 預計返回時間必須晚於預計出廠時間，請重新確認。",
            "req_err": "⚠️ 請填寫前往目的地與派車事由。",
            "ok": "✅ 已提交派車單 `{}`（出車：{} ➔ 返回：{}），送交部門主管審核。",
        },
        "vi": {
            "hdr": "🚗 3. Phiếu Đăng Ký Xe Công Vụ Nhà Máy",
            "flow": "Quy trình: Nhân viên gửi phiếu ➔ Trưởng bộ phận duyệt ➔ Bảo vệ xác nhận xuất xe & số km.",
            "app_name": "Người Đề Nghị (Hệ thống)*",
            "dept_role": "Bộ Phận / Chức Vụ",
            "veh": "Chọn Xe Công Vụ / Biển Số*",
            "drv": "Tài Xế / Người Lái",
            "ptype": "Loại Mục Đích Đi Xe*",
            "dest": "Điểm Đến / Tên Công Trường*",
            "reason": "Lý Do & Chi Tiết Công Tác*",
            "dep_date": "Ngày Dự Kiến Xuất Xe",
            "dep_time": "Giờ Dự Kiến Xuất Xe",
            "ret_date": "Ngày Dự Kiến Về",
            "ret_time": "Giờ Dự Kiến Về",
            "submit": "📨 Gửi Phiếu Xin Xe Trình Duyệt",
            "time_err": "⚠️ Thời gian dự kiến về phải sau thời gian dự kiến xuất xe.",
            "req_err": "⚠️ Vui lòng nhập điểm đến và lý do đi xe.",
            "ok": "✅ Đã gửi phiếu `{}` (Xuất: {} ➔ Về: {}).",
        },
        "en": {
            "hdr": "🚗 3. Factory Vehicle Dispatch Request",
            "flow": "Workflow: Employee submits ➔ Department manager approves ➔ Security gate logs departure & mileage.",
            "app_name": "Applicant (System)*",
            "dept_role": "Department / Role",
            "veh": "Select Vehicle / Plate*",
            "drv": "Driver Name",
            "ptype": "Dispatch Purpose Type*",
            "dest": "Destination / Site Name*",
            "reason": "Purpose & Detailed Notes*",
            "dep_date": "Est. Departure Date",
            "dep_time": "Est. Departure Time",
            "ret_date": "Est. Return Date",
            "ret_time": "Est. Return Time",
            "submit": "📨 Submit Dispatch Request for Approval",
            "time_err": "⚠️ Return time must be later than departure time.",
            "req_err": "⚠️ Please enter destination and dispatch purpose.",
            "ok": "✅ Submitted dispatch `{}` (Depart: {} ➔ Return: {}).",
        },
    }[code]

    st.markdown(f"#### {txt['hdr']}")
    st.info(txt["flow"])

    default_dep_dt = (now_vn + timedelta(minutes=15)).replace(second=0, microsecond=0)
    default_ret_dt = (default_dep_dt + timedelta(hours=3)).replace(second=0, microsecond=0)

    c_left, c_mid, c_right = st.columns([3.5, 3.5, 3.0])

    with c_left:
        st.text_input(txt["app_name"], value=user_name, disabled=True, key="v_app_name")
        st.text_input(txt["dept_role"], value=user_role, disabled=True, key="v_dept_role")
        purpose_type = st.selectbox(
            txt["ptype"],
            ["商務／工程公務外出", "工地巡檢與會勘", "物料／設備運送", "客戶驗收與拜訪"],
            key="v_purpose_type",
        )

    with c_mid:
        vehicle_plate = st.selectbox(
            txt["veh"],
            [
                "60A-888.99 (Toyota Fortuner 7座)",
                "61C-452.18 (Mitsubishi Triton 皮卡)",
                "70A-129.66 (Toyota Innova 公務車)",
            ],
            key="v_vehicle_plate",
        )
        driver_name = st.text_input(txt["drv"], value="Nguyễn Văn Tài (專職司機)", key="v_driver_name")
        destination = st.text_input(
            txt["dest"],
            placeholder="例：西寧省安平工業區客場",
            key="v_destination",
        )

    with c_right:
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            dep_date = st.date_input(txt["dep_date"], value=default_dep_dt.date(), key="v_dep_date")
        with d_col2:
            dep_time = st.time_input(
                txt["dep_time"],
                value=time(default_dep_dt.hour, default_dep_dt.minute),
                step=900,
                key="v_dep_time",
            )

        r_col1, r_col2 = st.columns(2)
        with r_col1:
            ret_date = st.date_input(txt["ret_date"], value=default_ret_dt.date(), key="v_ret_date")
        with r_col2:
            ret_time = st.time_input(
                txt["ret_time"],
                value=time(default_ret_dt.hour, default_ret_dt.minute),
                step=900,
                key="v_ret_time",
            )

    reason_detail = st.text_area(
        txt["reason"],
        placeholder="例：前往西寧廠區載運 400A 配電盤，並陪同客戶驗收。",
        key="v_reason_detail",
    )

    depart_dt = datetime.combine(dep_date, dep_time)
    return_dt = datetime.combine(ret_date, ret_time)

    if st.button(txt["submit"], type="primary", use_container_width=True, key="v_submit_btn"):
        if not destination.strip() or not reason_detail.strip():
            st.warning(txt["req_err"])
        elif return_dt <= depart_dt:
            st.warning(txt["time_err"])
        elif not engine:
            st.error("❌ 尚未連線資料庫。")
        else:
            dispatch_no = f"CAR-{now_vn.strftime('%Y%m%d-%H%M%S')}"
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO approval_vehicle_dispatches (
                                tenant_id, dispatch_no, project_id, applicant_name,
                                dept_or_role, vehicle_plate, driver_name, purpose_type,
                                destination, reason_detail, depart_at, return_at, status
                            )
                            VALUES (
                                :tid, :dno, :pid, :aname,
                                :drole, :vplate, :dname, :ptype,
                                :dest, :rsn, :dep_at, :ret_at, 'PENDING_SUPERVISOR'
                            )
                        """),
                        {
                            "tid": tenant_id,
                            "dno": dispatch_no,
                            "pid": st.session_state.get("active_project_id"),
                            "aname": user_name,
                            "drole": user_role,
                            "vplate": vehicle_plate,
                            "dname": driver_name.strip() or None,
                            "ptype": purpose_type,
                            "dest": destination.strip(),
                            "rsn": reason_detail.strip(),
                            "dep_at": depart_dt,
                            "ret_at": return_dt,
                        },
                    )
                st.success(
                    txt["ok"].format(
                        dispatch_no,
                        depart_dt.strftime("%Y/%m/%d %H:%M"),
                        return_dt.strftime("%Y/%m/%d %H:%M"),
                    )
                )
            except Exception as e:
                st.error(f"❌ 提交派車申請單失敗：{e}")


def _render_supervisor_queue(engine, tenant_id: str):
    st.markdown("#### 📋 4. 待簽核案件審查（主管專區）")
    if not engine:
        st.info("尚未連線資料庫。")
        return

    try:
        with engine.connect() as conn:
            car_rows = conn.execute(
                text("""
                    SELECT dispatch_no, applicant_name, vehicle_plate, destination,
                           TO_CHAR(depart_at, 'YYYY-MM-DD HH24:MI') AS dep_str,
                           TO_CHAR(return_at, 'YYYY-MM-DD HH24:MI') AS ret_str,
                           status
                    FROM approval_vehicle_dispatches
                    WHERE tenant_id = :tid
                    ORDER BY id DESC
                    LIMIT 20
                """),
                {"tid": tenant_id},
            ).fetchall()

            lv_rows = conn.execute(
                text("""
                    SELECT leave_no, employee_name, leave_type,
                           TO_CHAR(start_at, 'YYYY-MM-DD HH24:MI') AS s_str,
                           TO_CHAR(end_at, 'YYYY-MM-DD HH24:MI') AS e_str,
                           leave_hours, status
                    FROM hr_leave_requests
                    WHERE tenant_id = :tid
                    ORDER BY id DESC
                    LIMIT 20
                """),
                {"tid": tenant_id},
            ).fetchall()
    except Exception:
        st.info("尚無待簽核單據。")
        return

    st.markdown("**🚗 派車單列表**")
    if car_rows:
        st.dataframe(
            pd.DataFrame([
                {
                    "派車單號": r.dispatch_no,
                    "申請人": r.applicant_name,
                    "車輛": r.vehicle_plate,
                    "目的地": r.destination,
                    "預計出廠": r.dep_str,
                    "預計返回": r.ret_str,
                    "狀態": r.status,
                }
                for r in car_rows
            ]),
            use_container_width=True,
            hide_index=True,
        )
        pending_cars = [r.dispatch_no for r in car_rows if r.status == "PENDING_SUPERVISOR"]
        if pending_cars:
            sel_car = st.selectbox("選擇待審核派車單", pending_cars, key="sel_pending_car")
            b1, b2 = st.columns(2)
            with b1:
                if st.button("✅ 主管核准派車", key="btn_app_car", type="primary", use_container_width=True):
                    with engine.begin() as conn:
                        conn.execute(
                            text("UPDATE approval_vehicle_dispatches SET status = 'APPROVED_FOR_GATE' WHERE tenant_id = :tid AND dispatch_no = :dno"),
                            {"tid": tenant_id, "dno": sel_car},
                        )
                    st.success(f"已核准派車單 {sel_car}，可交由門禁保全放行。")
                    st.rerun()
            with b2:
                if st.button("❌ 駁回派車單", key="btn_rej_car", use_container_width=True):
                    with engine.begin() as conn:
                        conn.execute(
                            text("UPDATE approval_vehicle_dispatches SET status = 'REJECTED' WHERE tenant_id = :tid AND dispatch_no = :dno"),
                            {"tid": tenant_id, "dno": sel_car},
                        )
                    st.warning(f"已駁回派車單 {sel_car}。")
                    st.rerun()
    else:
        st.info("目前尚無派車申請紀錄。")

    st.divider()
    st.markdown("**📝 員工請假單列表**")
    if lv_rows:
        st.dataframe(
            pd.DataFrame([
                {
                    "請假單號": r.leave_no,
                    "員工": r.employee_name,
                    "假別": r.leave_type,
                    "開始時間": r.s_str,
                    "結束時間": r.e_str,
                    "時數": float(r.leave_hours or 0),
                    "狀態": r.status,
                }
                for r in lv_rows
            ]),
            use_container_width=True,
            hide_index=True,
        )
        pending_lvs = [r.leave_no for r in lv_rows if r.status == "PENDING_SUPERVISOR"]
        if pending_lvs:
            sel_lv = st.selectbox("選擇待審核請假單", pending_lvs, key="sel_pending_lv")
            l1, l2 = st.columns(2)
            with l1:
                if st.button("✅ 核准請假單", key="btn_app_lv", type="primary", use_container_width=True):
                    with engine.begin() as conn:
                        conn.execute(
                            text("UPDATE hr_leave_requests SET status = 'APPROVED' WHERE tenant_id = :tid AND leave_no = :lno"),
                            {"tid": tenant_id, "lno": sel_lv},
                        )
                    st.success(f"已核准請假單 {sel_lv}。")
                    st.rerun()
            with l2:
                if st.button("❌ 駁回請假單", key="btn_rej_lv", use_container_width=True):
                    with engine.begin() as conn:
                        conn.execute(
                            text("UPDATE hr_leave_requests SET status = 'REJECTED' WHERE tenant_id = :tid AND leave_no = :lno"),
                            {"tid": tenant_id, "lno": sel_lv},
                        )
                    st.warning(f"已駁回請假單 {sel_lv}。")
                    st.rerun()
    else:
        st.info("目前尚無請假申請紀錄。")


def render_approval_center(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "admin"
    user_role = st.session_state.get("user_role") or "角色"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### ✍️ 全公司電子簽核中心 (Approval Center)")
    st.caption("提交請假、採購請款、公務派車或專案簽呈；系統自動依權限進行多級電子簽核。")
    _ensure_approval_tables(engine)

    tab_car, tab_queue = st.tabs([
        "🚗 3. 廠區公務派車申請單",
        "📋 4. 待簽核案件審查（主管專區）",
    ])

    with tab_car:
        _render_vehicle_dispatch_tab(engine, tenant_id, user_name, user_role, now_vn, code)

    with tab_queue:
        _render_supervisor_queue(engine, tenant_id)


def render(engine=None, lang="zh", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)


def show(engine=None, lang="zh", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)
