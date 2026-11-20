# ==========================================
# 檔案路徑：modules/security/gate_repo.py
# 職責：廠區保全共用資料存取（車輛與攜帶物品查驗、人員進出、訪客登記、郵件包裹）
# ==========================================

from datetime import datetime
import pandas as pd
from sqlalchemy import text


def ensure_security_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS sec_vehicle_gate_logs (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        dispatch_no VARCHAR(64),
                        project_id VARCHAR(80),
                        vehicle_plate VARCHAR(120) NOT NULL,
                        driver_or_user VARCHAR(120),
                        direction VARCHAR(24) NOT NULL,
                        mileage_km VARCHAR(64),
                        carried_items TEXT,
                        cargo_check_status VARCHAR(32) DEFAULT 'VERIFIED_OK',
                        guard_name VARCHAR(120),
                        passed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS sec_personnel_gate_logs (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        project_id VARCHAR(80),
                        person_type VARCHAR(32) NOT NULL,
                        person_name VARCHAR(120) NOT NULL,
                        company_or_dept VARCHAR(160),
                        direction VARCHAR(24) NOT NULL,
                        note TEXT,
                        guard_name VARCHAR(120),
                        passed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS sec_visitor_logs (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        visitor_id VARCHAR(64),
                        visitor_name VARCHAR(120) NOT NULL,
                        company_name VARCHAR(160),
                        host_contact VARCHAR(120),
                        visit_purpose VARCHAR(200),
                        badge_no VARCHAR(40),
                        status VARCHAR(24) DEFAULT 'IN_SITE',
                        guard_name VARCHAR(120),
                        check_in_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        check_out_at TIMESTAMP WITH TIME ZONE
                    );
                """)
            )
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS sec_mail_package_logs (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        package_id VARCHAR(64),
                        carrier_or_sender VARCHAR(160),
                        recipient_name VARCHAR(120) NOT NULL,
                        recipient_dept VARCHAR(100),
                        item_summary VARCHAR(200) NOT NULL,
                        status VARCHAR(24) DEFAULT 'RECEIVED',
                        picked_by VARCHAR(120),
                        guard_name VARCHAR(120),
                        received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        picked_at TIMESTAMP WITH TIME ZONE
                    );
                """)
            )
    except Exception:
        pass


def fetch_approved_dispatches(engine, tenant_id: str) -> list[dict]:
    if not engine:
        return []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT dispatch_no, applicant_name, vehicle_plate, driver_name, destination, reason_detail
                    FROM approval_vehicle_dispatches
                    WHERE tenant_id = :tid AND status = 'APPROVED_FOR_GATE'
                    ORDER BY id DESC LIMIT 20
                """),
                {"tid": tenant_id},
            ).fetchall()
            return [r._asdict() for r in rows]
    except Exception:
        return []


def log_vehicle_gate(engine, tenant_id: str, dispatch_no: str | None, project_id: str | None, vehicle_plate: str, driver_or_user: str, direction: str, mileage_km: str, carried_items: str, cargo_check_status: str, guard_name: str, now_vn: datetime):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO sec_vehicle_gate_logs (
                    tenant_id, dispatch_no, project_id, vehicle_plate,
                    driver_or_user, direction, mileage_km, carried_items,
                    cargo_check_status, guard_name, passed_at
                )
                VALUES (
                    :tid, :dno, :pid, :vplate,
                    :duser, :dir, :km, :items,
                    :cstatus, :gname, :pat
                )
            """),
            {
                "tid": tenant_id, "dno": dispatch_no, "pid": project_id,
                "vplate": vehicle_plate, "duser": driver_or_user, "dir": direction,
                "km": mileage_km, "items": carried_items, "cstatus": cargo_check_status,
                "gname": guard_name, "pat": now_vn,
            },
        )
        if dispatch_no and direction == "OUT":
            conn.execute(
                text("UPDATE approval_vehicle_dispatches SET gate_status = 'DEPARTED' WHERE tenant_id = :tid AND dispatch_no = :dno"),
                {"tid": tenant_id, "dno": dispatch_no},
            )
            conn.execute(
                text("UPDATE approval_requests SET gate_status = 'DEPARTED', gate_mileage = :km WHERE tenant_id = :tid AND req_no = :dno"),
                {"km": mileage_km, "tid": tenant_id, "dno": dispatch_no},
            )


def fetch_vehicle_gate_df(engine, tenant_id: str) -> pd.DataFrame:
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT TO_CHAR(passed_at AT TIME ZONE 'Asia/Ho_Chi_Minh', 'MM-DD HH24:MI') AS t_str,
                           direction, vehicle_plate, driver_or_user, mileage_km,
                           carried_items, cargo_check_status, COALESCE(dispatch_no, '-') AS dispatch_no
                    FROM sec_vehicle_gate_logs
                    WHERE tenant_id = :tid
                    ORDER BY id DESC LIMIT 30
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def log_personnel_gate(engine, tenant_id: str, project_id: str | None, person_type: str, person_name: str, company_or_dept: str, direction: str, note: str, guard_name: str, now_vn: datetime):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO sec_personnel_gate_logs (
                    tenant_id, project_id, person_type, person_name,
                    company_or_dept, direction, note, guard_name, passed_at
                )
                VALUES (
                    :tid, :pid, :ptype, :pname,
                    :cdept, :dir, :note, :gname, :pat
                )
            """),
            {
                "tid": tenant_id, "pid": project_id, "ptype": person_type,
                "pname": person_name, "cdept": company_or_dept, "dir": direction,
                "note": note, "gname": guard_name, "pat": now_vn,
            },
        )


def fetch_personnel_gate_df(engine, tenant_id: str) -> pd.DataFrame:
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT TO_CHAR(passed_at AT TIME ZONE 'Asia/Ho_Chi_Minh', 'MM-DD HH24:MI') AS t_str,
                           direction, person_type, person_name, company_or_dept, COALESCE(note, '-') AS note
                    FROM sec_personnel_gate_logs
                    WHERE tenant_id = :tid
                    ORDER BY id DESC LIMIT 30
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def create_visitor_log(engine, tenant_id: str, visitor_name: str, company_name: str, host_contact: str, visit_purpose: str, badge_no: str, guard_name: str, now_vn: datetime) -> str:
    vid = f"VIS-{now_vn.strftime('%Y%m%d-%H%M%S')}"
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO sec_visitor_logs (
                    tenant_id, visitor_id, visitor_name, company_name,
                    host_contact, visit_purpose, badge_no, status, guard_name, check_in_at
                )
                VALUES (
                    :tid, :vid, :vname, :cname,
                    :hcont, :vpur, :bno, 'IN_SITE', :gname, :cin
                )
            """),
            {
                "tid": tenant_id, "vid": vid, "vname": visitor_name, "cname": company_name,
                "hcont": host_contact, "vpur": visit_purpose, "bno": badge_no,
                "gname": guard_name, "cin": now_vn,
            },
        )
    return vid


def checkout_visitor_log(engine, tenant_id: str, visitor_id: str, now_vn: datetime):
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE sec_visitor_logs
                SET status = 'LEFT_SITE', check_out_at = :cout
                WHERE tenant_id = :tid AND visitor_id = :vid
            """),
            {"cout": now_vn, "tid": tenant_id, "vid": visitor_id},
        )


def fetch_visitor_df(engine, tenant_id: str) -> pd.DataFrame:
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT visitor_id, visitor_name, company_name, host_contact,
                           visit_purpose, badge_no, status,
                           TO_CHAR(check_in_at AT TIME ZONE 'Asia/Ho_Chi_Minh', 'MM-DD HH24:MI') AS cin_str
                    FROM sec_visitor_logs
                    WHERE tenant_id = :tid
                    ORDER BY id DESC LIMIT 30
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def create_mail_package_log(engine, tenant_id: str, carrier_or_sender: str, recipient_name: str, recipient_dept: str, item_summary: str, guard_name: str, now_vn: datetime) -> str:
    pid = f"PKG-{now_vn.strftime('%Y%m%d-%H%M%S')}"
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO sec_mail_package_logs (
                    tenant_id, package_id, carrier_or_sender, recipient_name,
                    recipient_dept, item_summary, status, guard_name, received_at
                )
                VALUES (
                    :tid, :pid, :sender, :rname,
                    :rdept, :isum, 'RECEIVED', :gname, :rat
                )
            """),
            {
                "tid": tenant_id, "pid": pid, "sender": carrier_or_sender,
                "rname": recipient_name, "rdept": recipient_dept, "isum": item_summary,
                "gname": guard_name, "rat": now_vn,
            },
        )
    return pid


def mark_package_picked(engine, tenant_id: str, package_id: str, picked_by: str, now_vn: datetime):
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE sec_mail_package_logs
                SET status = 'PICKED_UP', picked_by = :pby, picked_at = :pat
                WHERE tenant_id = :tid AND package_id = :pid
            """),
            {"pby": picked_by, "pat": now_vn, "tid": tenant_id, "pid": package_id},
        )


def fetch_mail_package_df(engine, tenant_id: str) -> pd.DataFrame:
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT package_id, carrier_or_sender, recipient_name, recipient_dept,
                           item_summary, status, COALESCE(picked_by, '-') AS picked_by,
                           TO_CHAR(received_at AT TIME ZONE 'Asia/Ho_Chi_Minh', 'MM-DD HH24:MI') AS r_str
                    FROM sec_mail_package_logs
                    WHERE tenant_id = :tid
                    ORDER BY id DESC LIMIT 30
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()
