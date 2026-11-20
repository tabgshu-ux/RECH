# ==========================================
# 檔案路徑：modules/common/attendance_payroll_bridge.py
# 職責：串接工程部外勤打卡/點工紀錄 -> 管理部(人事)考勤核准 -> 薪資與專案人工成本結算
# ==========================================

from datetime import date
import pandas as pd
from sqlalchemy import text


def ensure_hr_payroll_bridge_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS eng_field_clockins (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        employee_id VARCHAR(64),
                        employee_name VARCHAR(120) NOT NULL,
                        project_id VARCHAR(80),
                        clock_type VARCHAR(24) DEFAULT 'CLOCK_IN',
                        clock_time TIMESTAMP WITH TIME ZONE NOT NULL,
                        gps_lat NUMERIC(10, 6),
                        gps_lng NUMERIC(10, 6),
                        gps_address VARCHAR(255),
                        photo_base64 TEXT,
                        hr_sync_status VARCHAR(32) DEFAULT 'PENDING_HR',
                        payroll_batch_id VARCHAR(64),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS eng_daily_labor_headcount (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        work_date DATE NOT NULL,
                        project_id VARCHAR(80),
                        site_name VARCHAR(160) NOT NULL,
                        subcon_id VARCHAR(80),
                        subcon_workers INT DEFAULT 0,
                        daily_wage_workers INT DEFAULT 0,
                        daily_wage_rate NUMERIC(14, 2) DEFAULT 450000,
                        gps_location VARCHAR(255),
                        hr_sync_status VARCHAR(32) DEFAULT 'PENDING_HR',
                        payroll_batch_id VARCHAR(64),
                        recorded_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS hr_payroll_settlements (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        payroll_batch_id VARCHAR(64) UNIQUE NOT NULL,
                        period_ym VARCHAR(16) NOT NULL,
                        employee_id VARCHAR(64),
                        employee_name VARCHAR(120) NOT NULL,
                        worker_category VARCHAR(32) DEFAULT 'FULL_TIME',
                        project_id VARCHAR(80),
                        work_days NUMERIC(6, 2) DEFAULT 0,
                        overtime_hours NUMERIC(6, 2) DEFAULT 0,
                        base_or_daily_pay NUMERIC(16, 2) DEFAULT 0,
                        site_allowance NUMERIC(16, 2) DEFAULT 0,
                        ot_pay NUMERIC(16, 2) DEFAULT 0,
                        social_ins_deduct NUMERIC(16, 2) DEFAULT 0,
                        net_pay NUMERIC(16, 2) DEFAULT 0,
                        status VARCHAR(32) DEFAULT 'CALCULATED',
                        settled_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
            # 相容舊表補齊關聯欄位（Hooks & Foreign Keys）
            for alter_sql in [
                "ALTER TABLE eng_field_clockins ADD COLUMN IF NOT EXISTS employee_id VARCHAR(64);",
                "ALTER TABLE eng_field_clockins ADD COLUMN IF NOT EXISTS hr_sync_status VARCHAR(32) DEFAULT 'PENDING_HR';",
                "ALTER TABLE eng_field_clockins ADD COLUMN IF NOT EXISTS payroll_batch_id VARCHAR(64);",
                "ALTER TABLE eng_daily_labor_headcount ADD COLUMN IF NOT EXISTS daily_wage_rate NUMERIC(14, 2) DEFAULT 450000;",
                "ALTER TABLE eng_daily_labor_headcount ADD COLUMN IF NOT EXISTS hr_sync_status VARCHAR(32) DEFAULT 'PENDING_HR';",
                "ALTER TABLE eng_daily_labor_headcount ADD COLUMN IF NOT EXISTS payroll_batch_id VARCHAR(64);",
            ]:
                conn.execute(text(alter_sql))
    except Exception:
        pass


def fetch_hr_field_clockins(engine, tenant_id: str, start_date: date, end_date: date) -> pd.DataFrame:
    """管理部（人事）讀取外勤工程人員打卡紀錄（含專案歸屬與人事核准狀態）"""
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT id,
                           COALESCE(employee_id, '-') AS employee_id,
                           employee_name,
                           COALESCE(project_id, '未指定專案') AS project_id,
                           DATE(clock_time AT TIME ZONE 'Asia/Ho_Chi_Minh') AS work_date,
                           TO_CHAR(clock_time AT TIME ZONE 'Asia/Ho_Chi_Minh', 'HH24:MI:SS') AS clock_hm,
                           COALESCE(gps_address, '-') AS gps_address,
                           COALESCE(hr_sync_status, 'PENDING_HR') AS hr_sync_status,
                           COALESCE(payroll_batch_id, '-') AS payroll_batch_id
                    FROM eng_field_clockins
                    WHERE tenant_id = :tid
                      AND DATE(clock_time AT TIME ZONE 'Asia/Ho_Chi_Minh') BETWEEN :sdate AND :edate
                    ORDER BY clock_time DESC
                """),
                {"tid": tenant_id, "sdate": start_date, "edate": end_date},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def fetch_hr_daily_labor(engine, tenant_id: str, start_date: date, end_date: date) -> pd.DataFrame:
    """管理部（人事）讀取點工與外包出勤統計（供點工計薪與專案人工成本分攤）"""
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT id,
                           work_date,
                           COALESCE(project_id, '未指定專案') AS project_id,
                           site_name,
                           COALESCE(subcon_id, '-') AS subcon_id,
                           COALESCE(subcon_workers, 0) AS subcon_workers,
                           COALESCE(daily_wage_workers, 0) AS daily_wage_workers,
                           COALESCE(daily_wage_rate, 450000) AS daily_wage_rate,
                           COALESCE(hr_sync_status, 'PENDING_HR') AS hr_sync_status,
                           COALESCE(payroll_batch_id, '-') AS payroll_batch_id
                    FROM eng_daily_labor_headcount
                    WHERE tenant_id = :tid
                      AND work_date BETWEEN :sdate AND :edate
                    ORDER BY work_date DESC, id DESC
                """),
                {"tid": tenant_id, "sdate": start_date, "edate": end_date},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def approve_records_for_hr(engine, tenant_id: str, start_date: date, end_date: date) -> tuple[int, int]:
    """管理部（人事）批次核准外勤打卡與點工紀錄，鎖定進入薪資結算池"""
    if not engine:
        return 0, 0
    c_updated = 0
    l_updated = 0
    try:
        with engine.begin() as conn:
            res1 = conn.execute(
                text("""
                    UPDATE eng_field_clockins
                    SET hr_sync_status = 'HR_APPROVED'
                    WHERE tenant_id = :tid
                      AND DATE(clock_time AT TIME ZONE 'Asia/Ho_Chi_Minh') BETWEEN :sdate AND :edate
                      AND COALESCE(hr_sync_status, 'PENDING_HR') = 'PENDING_HR'
                """),
                {"tid": tenant_id, "sdate": start_date, "edate": end_date},
            )
            c_updated = res1.rowcount or 0

            res2 = conn.execute(
                text("""
                    UPDATE eng_daily_labor_headcount
                    SET hr_sync_status = 'HR_APPROVED'
                    WHERE tenant_id = :tid
                      AND work_date BETWEEN :sdate AND :edate
                      AND COALESCE(hr_sync_status, 'PENDING_HR') = 'PENDING_HR'
                """),
                {"tid": tenant_id, "sdate": start_date, "edate": end_date},
            )
            l_updated = res2.rowcount or 0
    except Exception:
        pass
    return c_updated, l_updated
