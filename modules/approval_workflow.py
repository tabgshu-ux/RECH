# ==========================================
# 檔案路徑：modules/approval_workflow.py
# 職責：全公司電子簽核中心（保留請假/採購/倉庫/外出/派車/主管審查/進度追蹤/保全放行全分頁）
# ==========================================

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_all_approval_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS approval_requests (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        req_no VARCHAR(64) UNIQUE NOT NULL,
                        req_type VARCHAR(48) NOT NULL,
                        project_id VARCHAR(80),
                        ref_doc_id VARCHAR(80),
                        applicant_name VARCHAR(120) NOT NULL,
                        dept_or_role VARCHAR(120),
                        title_or_item VARCHAR(200) NOT NULL,
                        amount_vnd NUMERIC(18, 2) DEFAULT 0,
                        detail_text TEXT,
                        start_at TIMESTAMP WITHOUT TIME ZONE,
                        end_at TIMESTAMP WITHOUT TIME ZONE,
                        status VARCHAR(32) DEFAULT 'PENDING_SUPERVISOR',
                        approver_name VARCHAR(120),
                        gate_status VARCHAR(32) DEFAULT 'PENDING_GATE',
                        gate_mileage VARCHAR(64),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
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
                        gate_status VARCHAR(32) DEFAULT 'PENDING_GATE',
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


def _tab_leave_request(engine, tenant_id: str, user_name: str, user_role: str, now_vn: datetime):
    st.markdown("#### 📝 1. 員工請假申請")
    st.info("提交請假單後自動送交部門主管簽核，核准後同步計入人事考勤與薪資結算。")
    with st.form("wf_form_leave"):
        leave_type = st.selectbox(
            "假別*",
            ["特休 / 年假 (Phép năm)", "病假 (Nghỉ ốm)", "事假 (Nghỉ việc riêng)", "公假 / 補休 (Nghỉ bù)"],
        )
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
            start_dt = datetime.combine(s_date, s_time)
            end_dt = datetime.combine(e_date, e_time)
            if end_dt <= start_dt:
                st.warning("⚠️ 結束時間必須晚於開始時間。")
            elif not reason.strip():
                st.warning("⚠️ 請填寫請假事由。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                lno = f"LV-{now_vn.strftime('%Y%m%d-%H%M%S')}"
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
                                "lno": lno,
                                "ename": user_name,
                                "drole": user_role,
                                "ltype": leave_type,
                                "sat": start_dt,
                                "eat": end_dt,
                                "hrs": float(leave_hours),
                                "rsn": reason.strip(),
                            },
                        )
                        conn.execute(
                            text("""
                                INSERT INTO approval_requests (
                                    tenant_id, req_no, req_type, project_id, ref_doc_id,
                                    applicant_name, dept_or_role, title_or_item,
                                    amount_vnd, detail_text, start_at, end_at, status
                                )
                                VALUES (
                                    :tid, :rno, 'LEAVE', :pid, :lno,
                                    :aname, :drole, :title,
                                    0, :detail, :sat, :eat, 'PENDING_SUPERVISOR'
                                )
                            """),
                            {
                                "tid": tenant_id,
                                "rno": lno,
                                "pid": st.session_state.get("active_project_id"),
                                "lno": lno,
                                "aname": user_name,
                                "drole": user_role,
                                "title": f"{leave_type}（{leave_hours} 小時）",
                                "detail": reason.strip(),
                                "sat": start_dt,
                                "eat": end_dt,
                            },
                        )
                    st.success(f"✅ 已提交請假單 `{lno}`，送交部門主管審核。")
                except Exception as e:
                    st.error(f"❌ 送出請假單失敗：{e}")


def _tab_ops_requests(engine, tenant_id: str, user_name: str, user_role: str, now_vn: datetime):
    st.markdown("#### 📦 2. 採購請款／倉庫領調／外出簽核申請")
    st.info("涵蓋採購請款（PR/PO）、倉庫領料／調撥簽核與人員外出簽核，統一送交權責主管審查。")
    with st.form("wf_form_ops_req"):
        c1, c2 = st.columns(2)
        with c1:
            req_cat = st.selectbox(
                "簽核類別*",
                [
                    ("PROCUREMENT", "🛒 採購與請款申請單 (PR/PO)"),
                    ("WAREHOUSE", "🏭 倉庫領料／跨庫調撥簽核"),
                    ("OUTING", "🚶 人員外出／差旅簽核"),
                ],
                format_func=lambda x: x[1],
            )
            title_item = st.text_input("申請主旨／品項名稱*", placeholder="例：西寧廠區主配電盤銅排採購 / 領料")
        with c2:
            amount_vnd = st.number_input("涉及金額 (VND，外出／領料可填 0)", min_value=0, value=0, step=100000)
            out_date = st.date_input("預計執行／外出日期", value=now_vn.date())

        detail_text = st.text_area("詳細說明／專案關聯*", placeholder="請填寫規格、數量、倉庫／案場或外出地點與事由...")

        if st.form_submit_button("📨 提交簽核申請", type="primary", use_container_width=True):
            rcode, rlabel = req_cat
            if not title_item.strip() or not detail_text.strip():
                st.warning("⚠️ 請填寫申請主旨與詳細說明。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                prefix = {"PROCUREMENT": "PR", "WAREHOUSE": "WH", "OUTING": "OUT"}.get(rcode, "REQ")
                req_no = f"{prefix}-{now_vn.strftime('%Y%m%d-%H%M%S')}"
                exec_dt = datetime.combine(out_date, time(8, 0))
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO approval_requests (
                                    tenant_id, req_no, req_type, project_id, ref_doc_id,
                                    applicant_name, dept_or_role, title_or_item,
                                    amount_vnd, detail_text, start_at, end_at, status
                                )
                                VALUES (
                                    :tid, :rno, :rtype, :pid, :refid,
                                    :aname, :drole, :title,
                                    :amt, :detail, :sat, :eat, 'PENDING_SUPERVISOR'
                                )
                            """),
                            {
                                "tid": tenant_id,
                                "rno": req_no,
                                "rtype": rcode,
                                "pid": st.session_state.get("active_project_id"),
                                "refid": req_no,
                                "aname": user_name,
                                "drole": user_role,
                                "title": f"[{rlabel}] {title_item.strip()}",
                                "amt": float(amount_vnd),
                                "detail": detail_text.strip(),
                                "sat": exec_dt,
                                "eat": exec_dt + timedelta(hours=9),
                            },
                        )
                    st.success(f"✅ 已提交【{rlabel}】單號 `{req_no}`，送交主管審核。")
                except Exception as e:
                    st.error(f"❌ 提交簽核單失敗：{e}")


def _tab_vehicle_dispatch(engine, tenant_id: str, user_name: str, user_role: str, now_vn: datetime, code: str):
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
                                destination, reason_detail, depart_at, return_at, status, gate_status
                            )
                            VALUES (
                                :tid, :dno, :pid, :aname,
                                :drole, :vplate, :dname, :ptype,
                                :dest, :rsn, :dep_at, :ret_at, 'PENDING_SUPERVISOR', 'PENDING_GATE'
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
                    conn.execute(
                        text("""
                            INSERT INTO approval_requests (
                                tenant_id, req_no, req_type, project_id, ref_doc_id,
                                applicant_name, dept_or_role, title_or_item,
                                amount_vnd, detail_text, start_at, end_at, status, gate_status
                            )
                            VALUES (
                                :tid, :dno, 'VEHICLE', :pid, :dno,
                                :aname, :drole, :title,
                                0, :detail, :dep_at, :ret_at, 'PENDING_SUPERVISOR', 'PENDING_GATE'
                            )
                        """),
                        {
                            "tid": tenant_id,
                            "dno": dispatch_no,
                            "pid": st.session_state.get("active_project_id"),
                            "aname": user_name,
                            "drole": user_role,
                            "title": f"公務派車 {vehicle_plate} ➔ {destination.strip()}",
                            "detail": reason_detail.strip(),
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


def _tab_supervisor_review(engine, tenant_id: str, approver_name: str):
    st.markdown("#### 📋 4. 待簽核案件審查（主管專區）")
    if not engine:
        st.info("尚未連線資料庫。")
        return

    filter_type = st.selectbox(
        "篩選簽核類別",
        ["ALL", "LEAVE", "PROCUREMENT", "WAREHOUSE", "OUTING", "VEHICLE"],
        format_func=lambda x: {
            "ALL": "全部類別（請假／採購／倉庫／外出／派車）",
            "LEAVE": "📝 請假簽核",
            "PROCUREMENT": "🛒 採購請款簽核",
            "WAREHOUSE": "🏭 倉庫簽核",
            "OUTING": "🚶 外出簽核",
            "VEHICLE": "🚗 公務派車簽核",
        }[x],
    )

    try:
        with engine.connect() as conn:
            sql = """
                SELECT req_no, req_type, applicant_name, title_or_item, amount_vnd,
                       TO_CHAR(start_at, 'YYYY-MM-DD HH24:MI') AS s_str,
                       TO_CHAR(end_at, 'YYYY-MM-DD HH24:MI') AS e_str,
                       status
                FROM approval_requests
                WHERE tenant_id = :tid
            """
            params = {"tid": tenant_id}
            if filter_type != "ALL":
                sql += " AND req_type = :rtype"
                params["rtype"] = filter_type
            sql += " ORDER BY id DESC LIMIT 40"
            rows = conn.execute(text(sql), params).fetchall()
    except Exception:
        st.info("尚無簽核紀錄。")
        return

    if not rows:
        st.info("目前無符合條件的簽核單據。")
        return

    st.dataframe(
        pd.DataFrame([
            {
                "單號": r.req_no,
                "類別": r.req_type,
                "申請人": r.applicant_name,
                "主旨／項目": r.title_or_item,
                "金額(₫)": f"{round(float(r.amount_vnd or 0)):,}".replace(",", "."),
                "開始時間": r.s_str or "-",
                "結束時間": r.e_str or "-",
                "簽核狀態": r.status,
            }
            for r in rows
        ]),
        use_container_width=True,
        hide_index=True,
    )

    pending_nos = [r.req_no for r in rows if r.status == "PENDING_SUPERVISOR"]
    if pending_nos:
        sel_no = st.selectbox("選擇待審核單號", pending_nos, key="wf_sel_pending_no")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("✅ 核准放行", key="wf_btn_approve", type="primary", use_container_width=True):
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            UPDATE approval_requests
                            SET status = 'APPROVED', approver_name = :appr
                            WHERE tenant_id = :tid AND req_no = :rno
                        """),
                        {"appr": approver_name, "tid": tenant_id, "rno": sel_no},
                    )
                    conn.execute(
                        text("UPDATE approval_vehicle_dispatches SET status = 'APPROVED_FOR_GATE' WHERE tenant_id = :tid AND dispatch_no = :rno"),
                        {"tid": tenant_id, "rno": sel_no},
                    )
                    conn.execute(
                        text("UPDATE hr_leave_requests SET status = 'APPROVED' WHERE tenant_id = :tid AND leave_no = :rno"),
                        {"tid": tenant_id, "rno": sel_no},
                    )
                st.success(f"✅ 已核准單號 `{sel_no}`。")
                st.rerun()
        with b2:
            if st.button("❌ 駁回退件", key="wf_btn_reject", use_container_width=True):
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            UPDATE approval_requests
                            SET status = 'REJECTED', approver_name = :appr
                            WHERE tenant_id = :tid AND req_no = :rno
                        """),
                        {"appr": approver_name, "tid": tenant_id, "rno": sel_no},
                    )
                    conn.execute(
                        text("UPDATE approval_vehicle_dispatches SET status = 'REJECTED' WHERE tenant_id = :tid AND dispatch_no = :rno"),
                        {"tid": tenant_id, "rno": sel_no},
                    )
                    conn.execute(
                        text("UPDATE hr_leave_requests SET status = 'REJECTED' WHERE tenant_id = :tid AND leave_no = :rno"),
                        {"tid": tenant_id, "rno": sel_no},
                    )
                st.warning(f"已駁回單號 `{sel_no}`。")
                st.rerun()


def _tab_progress_tracker(engine, tenant_id: str):
    st.markdown("#### 📊 5. 簽核進度即時追蹤")
    if not engine:
        st.info("尚未連線資料庫。")
        return
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT req_no AS "單號", req_type AS "類別", applicant_name AS "申請人",
                           title_or_item AS "申請內容", status AS "簽核狀態",
                           COALESCE(approver_name, '-') AS "簽核主管",
                           gate_status AS "門禁狀態"
                    FROM approval_requests
                    WHERE tenant_id = :tid
                    ORDER BY id DESC
                    LIMIT 50
                """),
                {"tid": tenant_id},
            ).fetchall()
            if not rows:
                st.info("目前尚無簽核追蹤紀錄。")
            else:
                st.dataframe(pd.DataFrame([r._asdict() for r in rows]), use_container_width=True, hide_index=True)
    except Exception:
        st.info("目前尚無簽核追蹤紀錄。")


def _tab_security_gate_check(engine, tenant_id: str, guard_name: str):
    st.markdown("#### 🛡️ 6. 保全門禁車輛放行查驗（保全專區）")
    st.info("查驗已核准之公務派車單，登記出廠／返回里程數並確認放行。")
    if not engine:
        st.info("尚未連線資料庫。")
        return
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT dispatch_no, applicant_name, vehicle_plate, driver_name, destination,
                           TO_CHAR(depart_at, 'YYYY-MM-DD HH24:MI') AS dep_str,
                           TO_CHAR(return_at, 'YYYY-MM-DD HH24:MI') AS ret_str,
                           status, gate_status
                    FROM approval_vehicle_dispatches
                    WHERE tenant_id = :tid
                    ORDER BY id DESC
                    LIMIT 30
                """),
                {"tid": tenant_id},
            ).fetchall()
    except Exception:
        st.info("目前尚無派車門禁紀錄。")
        return

    if not rows:
        st.info("目前尚無派車門禁紀錄。")
        return

    st.dataframe(
        pd.DataFrame([
            {
                "派車單號": r.dispatch_no,
                "申請人": r.applicant_name,
                "車輛": r.vehicle_plate,
                "司機": r.driver_name or "-",
                "目的地": r.destination,
                "預計出廠": r.dep_str,
                "預計返回": r.ret_str,
                "簽核狀態": r.status,
                "門禁放行": r.gate_status,
            }
            for r in rows
        ]),
        use_container_width=True,
        hide_index=True,
    )

    approved_cars = [r.dispatch_no for r in rows if r.status == "APPROVED_FOR_GATE" and r.gate_status != "DEPARTED"]
    if approved_cars:
        sel_dno = st.selectbox("選擇已核准派車單進行放行登記", approved_cars, key="wf_gate_car_sel")
        km_val = st.text_input("出廠里程數 (KM)", placeholder="例：45280 km", key="wf_gate_km")
        if st.button("🚦 確認出廠放行", type="primary", use_container_width=True, key="wf_gate_go"):
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE approval_vehicle_dispatches
                        SET gate_status = 'DEPARTED'
                        WHERE tenant_id = :tid AND dispatch_no = :dno
                    """),
                    {"tid": tenant_id, "dno": sel_dno},
                )
                conn.execute(
                    text("""
                        UPDATE approval_requests
                        SET gate_status = 'DEPARTED', gate_mileage = :km
                        WHERE tenant_id = :tid AND req_no = :dno
                    """),
                    {"km": km_val.strip() or None, "tid": tenant_id, "dno": sel_dno},
                )
            st.success(f"🚦 已登記派車單 `{sel_dno}` 出廠放行（經辦保全：{guard_name}）。")
            st.rerun()


def render_approval_center(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "admin"
    user_role = st.session_state.get("user_role") or "角色"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### ✍️ 全公司電子簽核中心 (Approval Center)")
    st.caption("提交請假、採購請款、倉庫領調、外出、公務派車或專案簽呈；系統自動依權限進行多級電子簽核。")
    _ensure_all_approval_tables(engine)

    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📝 1. 員工請假申請",
        "📦 2. 採購／倉庫／外出簽核",
        "🚗 3. 廠區公務派車申請單",
        "📋 4. 待簽核案件審查（主管專區）",
        "📊 5. 簽核進度即時追蹤",
        "🛡️ 6. 保全門禁車輛放行查驗",
    ])

    with t1:
        _tab_leave_request(engine, tenant_id, user_name, user_role, now_vn)
    with t2:
        _tab_ops_requests(engine, tenant_id, user_name, user_role, now_vn)
    with t3:
        _tab_vehicle_dispatch(engine, tenant_id, user_name, user_role, now_vn, code)
    with t4:
        _tab_supervisor_review(engine, tenant_id, user_name)
    with t5:
        _tab_progress_tracker(engine, tenant_id)
    with t6:
        _tab_security_gate_check(engine, tenant_id, user_name)


def render(engine=None, lang="zh", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)


def show(engine=None, lang="zh", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)
