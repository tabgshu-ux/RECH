# ==========================================
# 檔案路徑：modules/approval/workflow_repo.py
# 職責：電子簽核共用資料存取與狀態流轉（確保主單、請假、派車與門禁狀態一致）
# ==========================================

from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import text


def ensure_tables(engine):
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


def create_leave_request(engine, tenant_id: str, user_name: str, user_role: str, project_id: str | None, leave_type: str, start_dt: datetime, end_dt: datetime, leave_hours: float, reason: str, now_vn: datetime) -> str:
    lno = f"LV-{now_vn.strftime('%Y%m%d-%H%M%S')}"
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
                "tid": tenant_id, "lno": lno, "ename": user_name, "drole": user_role,
                "ltype": leave_type, "sat": start_dt, "eat": end_dt, "hrs": leave_hours, "rsn": reason,
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
                "tid": tenant_id, "rno": lno, "pid": project_id, "lno": lno,
                "aname": user_name, "drole": user_role,
                "title": f"{leave_type}（{leave_hours} 小時）", "detail": reason,
                "sat": start_dt, "eat": end_dt,
            },
        )
    return lno


def create_ops_request(engine, tenant_id: str, user_name: str, user_role: str, project_id: str | None, rcode: str, rlabel: str, title_item: str, amount_vnd: float, exec_dt: datetime, detail_text: str, now_vn: datetime) -> str:
    prefix = {"PROCUREMENT": "PR", "WAREHOUSE": "WH", "OUTING": "OUT"}.get(rcode, "REQ")
    req_no = f"{prefix}-{now_vn.strftime('%Y%m%d-%H%M%S')}"
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
                "tid": tenant_id, "rno": req_no, "rtype": rcode, "pid": project_id, "refid": req_no,
                "aname": user_name, "drole": user_role, "title": f"[{rlabel}] {title_item}",
                "amt": amount_vnd, "detail": detail_text,
                "sat": exec_dt, "eat": exec_dt + timedelta(hours=9),
            },
        )
    return req_no


def create_vehicle_dispatch(engine, tenant_id: str, user_name: str, user_role: str, project_id: str | None, vehicle_plate: str, driver_name: str | None, purpose_type: str, destination: str, reason_detail: str, depart_dt: datetime, return_dt: datetime, now_vn: datetime) -> str:
    dno = f"CAR-{now_vn.strftime('%Y%m%d-%H%M%S')}"
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
                "tid": tenant_id, "dno": dno, "pid": project_id, "aname": user_name,
                "drole": user_role, "vplate": vehicle_plate, "dname": driver_name,
                "ptype": purpose_type, "dest": destination, "rsn": reason_detail,
                "dep_at": depart_dt, "ret_at": return_dt,
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
                "tid": tenant_id, "dno": dno, "pid": project_id, "aname": user_name,
                "drole": user_role, "title": f"公務派車 {vehicle_plate} ➔ {destination}",
                "detail": reason_detail, "dep_at": depart_dt, "ret_at": return_dt,
            },
        )
    return dno


def decide_request(engine, tenant_id: str, req_no: str, approve: bool, approver_name: str):
    main_st = "APPROVED" if approve else "REJECTED"
    car_st = "APPROVED_FOR_GATE" if approve else "REJECTED"
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE approval_requests SET status = :st, approver_name = :appr WHERE tenant_id = :tid AND req_no = :rno"),
            {"st": main_st, "appr": approver_name, "tid": tenant_id, "rno": req_no},
        )
        conn.execute(
            text("UPDATE approval_vehicle_dispatches SET status = :st WHERE tenant_id = :tid AND dispatch_no = :rno"),
            {"st": car_st, "tid": tenant_id, "rno": req_no},
        )
        conn.execute(
            text("UPDATE hr_leave_requests SET status = :st WHERE tenant_id = :tid AND leave_no = :rno"),
            {"st": main_st, "tid": tenant_id, "rno": req_no},
        )


def release_vehicle_gate(engine, tenant_id: str, dispatch_no: str, mileage: str | None):
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE approval_vehicle_dispatches SET gate_status = 'DEPARTED' WHERE tenant_id = :tid AND dispatch_no = :dno"),
            {"tid": tenant_id, "dno": dispatch_no},
        )
        conn.execute(
            text("UPDATE approval_requests SET gate_status = 'DEPARTED', gate_mileage = :km WHERE tenant_id = :tid AND req_no = :dno"),
            {"km": mileage, "tid": tenant_id, "dno": dispatch_no},
        )


def list_requests_df(engine, tenant_id: str, req_type: str = "ALL", limit: int = 40) -> pd.DataFrame:
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            sql = """
                SELECT req_no, req_type, applicant_name, title_or_item, amount_vnd,
                       TO_CHAR(start_at, 'YYYY-MM-DD HH24:MI') AS s_str,
                       TO_CHAR(end_at, 'YYYY-MM-DD HH24:MI') AS e_str,
                       status, COALESCE(approver_name, '-') AS approver_name, gate_status
                FROM approval_requests
                WHERE tenant_id = :tid
            """
            params = {"tid": tenant_id, "lim": limit}
            if req_type != "ALL":
                sql += " AND req_type = :rtype"
                params["rtype"] = req_type
            sql += " ORDER BY id DESC LIMIT :lim"
            rows = conn.execute(text(sql), params).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def list_vehicles_df(engine, tenant_id: str, limit: int = 30) -> pd.DataFrame:
    if not engine:
        return pd.DataFrame()
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
                    ORDER BY id DESC LIMIT :lim
                """),
                {"tid": tenant_id, "lim": limit},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()
