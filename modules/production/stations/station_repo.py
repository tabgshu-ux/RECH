# ==========================================
# 檔案路徑：modules/production/stations/station_repo.py
# 職責：生產部鈑金、塗裝、電配三站共用資料層（接收設計圖與生產料件、回報進度）
# ==========================================

from datetime import datetime
import pandas as pd
from sqlalchemy import text


def ensure_station_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS prod_station_workorders (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        wo_no VARCHAR(64) UNIQUE NOT NULL,
                        project_id VARCHAR(80),
                        drawing_no VARCHAR(100) NOT NULL,
                        drawing_rev VARCHAR(24) DEFAULT 'Rev.A',
                        item_name VARCHAR(200) NOT NULL,
                        spec_summary VARCHAR(255),
                        required_qty INT DEFAULT 1,
                        completed_qty INT DEFAULT 0,
                        station_code VARCHAR(32) NOT NULL,
                        station_status VARCHAR(32) DEFAULT 'WAITING_START',
                        ecn_alert VARCHAR(200),
                        updated_by VARCHAR(100),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def load_station_orders(engine, tenant_id: str, station_code: str) -> pd.DataFrame:
    """讀取指定工站（SHEET_METAL / PAINTING / PANEL_WIRING）的設計圖與生產料件清單"""
    station_labels = {
        "SHEET_METAL": ("WO-SM-2611-01", "DWG-PNL-400A-01", "Rev.B", "400A 主配電盤櫃體／門板／隔板", "SPCC 2.0mm 冷軋鋼板折彎焊接", 6, 2, "IN_PROGRESS", "ECN-02：門鎖位置下移 20mm"),
        "PAINTING": ("WO-PT-2611-01", "DWG-PNL-400A-02", "Rev.B", "400A 配電盤櫃體與門板烤漆", "RAL 7032 粉體烤漆 80μm", 6, 0, "WAITING_START", None),
        "PANEL_WIRING": ("WO-PW-2611-01", "DWG-PNL-400A-03", "Rev.A", "400A 主配電盤一次／二次配線組裝", "銅排 40x5mm + 1.5mm² 控制線", 4, 1, "IN_PROGRESS", None),
    }
    fb = station_labels.get(station_code, ("WO-001", "DWG-001", "Rev.A", "標準料件", "依設計圖", 1, 0, "WAITING_START", None))
    fallback = [
        {
            "wo_no": fb[0],
            "project_id": "PRJ-2026-01",
            "drawing_no": fb[1],
            "drawing_rev": fb[2],
            "item_name": fb[3],
            "spec_summary": fb[4],
            "required_qty": fb[5],
            "completed_qty": fb[6],
            "station_status": fb[7],
            "ecn_alert": fb[8] or "-",
            "updated_by": "設計部下發",
        }
    ]
    if not engine:
        return pd.DataFrame(fallback)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT wo_no, COALESCE(project_id, '-') AS project_id,
                           drawing_no, COALESCE(drawing_rev, 'Rev.A') AS drawing_rev,
                           item_name, COALESCE(spec_summary, '-') AS spec_summary,
                           COALESCE(required_qty, 1) AS required_qty,
                           COALESCE(completed_qty, 0) AS completed_qty,
                           COALESCE(station_status, 'WAITING_START') AS station_status,
                           COALESCE(ecn_alert, '-') AS ecn_alert,
                           COALESCE(updated_by, '-') AS updated_by
                    FROM prod_station_workorders
                    WHERE tenant_id = :tid AND station_code = :scode
                    ORDER BY id DESC
                """),
                {"tid": tenant_id, "scode": station_code},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame(fallback)
    except Exception:
        return pd.DataFrame(fallback)


def dispatch_from_design(engine, tenant_id: str, project_id: str | None, drawing_no: str, drawing_rev: str, item_name: str, spec_summary: str, required_qty: int, station_code: str, ecn_alert: str | None, user_name: str, now_vn: datetime) -> str:
    """接收設計圖並建立指定生產工站（鈑金／塗裝／電配）料件生產單"""
    prefix = {"SHEET_METAL": "SM", "PAINTING": "PT", "PANEL_WIRING": "PW"}.get(station_code, "WO")
    wo_no = f"WO-{prefix}-{now_vn.strftime('%Y%m%d-%H%M%S')}"
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO prod_station_workorders (
                    tenant_id, wo_no, project_id, drawing_no, drawing_rev,
                    item_name, spec_summary, required_qty, completed_qty,
                    station_code, station_status, ecn_alert, updated_by, updated_at
                )
                VALUES (
                    :tid, :wono, :pid, :dno, :drev,
                    :iname, :spec, :rqty, 0,
                    :scode, 'WAITING_START', :ecn, :uby, :uat
                )
            """),
            {
                "tid": tenant_id, "wono": wo_no, "pid": project_id,
                "dno": drawing_no, "drev": drawing_rev, "iname": item_name,
                "spec": spec_summary, "rqty": required_qty, "scode": station_code,
                "ecn": ecn_alert, "uby": user_name, "uat": now_vn,
            },
        )
    return wo_no


def update_station_progress(engine, tenant_id: str, wo_no: str, completed_qty: int, station_status: str, user_name: str, now_vn: datetime):
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE prod_station_workorders
                SET completed_qty = :cqty,
                    station_status = :st,
                    updated_by = :uby,
                    updated_at = :uat
                WHERE tenant_id = :tid AND wo_no = :wono
            """),
            {"cqty": completed_qty, "st": station_status, "uby": user_name, "uat": now_vn, "tid": tenant_id, "wono": wo_no},
        )
