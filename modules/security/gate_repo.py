def fetch_security_summary_for_ga(engine, tenant_id: str) -> dict:
    """供總務／採購後勤資料中心讀取保全統計（車輛查驗、人員進出、訪客、郵件包裹）"""
    ensure_security_tables(engine)
    summary = {
        "vehicle_logs_count": 0,
        "cargo_abnormal_count": 0,
        "personnel_logs_count": 0,
        "visitors_in_site": 0,
        "packages_unpicked": 0,
    }
    if not engine:
        return summary
    try:
        with engine.connect() as conn:
            summary["vehicle_logs_count"] = int(
                conn.execute(
                    text("SELECT COUNT(*) FROM sec_vehicle_gate_logs WHERE tenant_id = :tid"),
                    {"tid": tenant_id},
                ).scalar()
                or 0
            )
            summary["cargo_abnormal_count"] = int(
                conn.execute(
                    text("SELECT COUNT(*) FROM sec_vehicle_gate_logs WHERE tenant_id = :tid AND cargo_check_status = 'ABNORMAL_HOLD'"),
                    {"tid": tenant_id},
                ).scalar()
                or 0
            )
            summary["personnel_logs_count"] = int(
                conn.execute(
                    text("SELECT COUNT(*) FROM sec_personnel_gate_logs WHERE tenant_id = :tid"),
                    {"tid": tenant_id},
                ).scalar()
                or 0
            )
            summary["visitors_in_site"] = int(
                conn.execute(
                    text("SELECT COUNT(*) FROM sec_visitor_logs WHERE tenant_id = :tid AND status = 'IN_SITE'"),
                    {"tid": tenant_id},
                ).scalar()
                or 0
            )
            summary["packages_unpicked"] = int(
                conn.execute(
                    text("SELECT COUNT(*) FROM sec_mail_package_logs WHERE tenant_id = :tid AND status = 'RECEIVED'"),
                    {"tid": tenant_id},
                ).scalar()
                or 0
            )
    except Exception:
        pass
    return summary
