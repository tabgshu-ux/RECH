# ==========================================
# 檔案路徑：modules/common/l1_dept_overviews.py
# 職責：各 L1 部門首頁總覽面板（工程部：工地數/施工人數/款項進度；生產部：各組進度與數量；其他 L1 部門共用總覽）
# ==========================================

import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _query_first_valid(engine, queries: list[tuple[str, dict]]) -> list[dict]:
    if not engine:
        return []
    for sql, params in queries:
        try:
            with engine.connect() as conn:
                rows = conn.execute(text(sql), params).fetchall()
                if rows:
                    return [r._asdict() for r in rows]
        except Exception:
            continue
    return []


def _load_engineering_overview_data(engine, tenant_id: str) -> dict:
    fallback_projects = [
        {
            "project_id": "PRJ-2026-01",
            "quote_id": "QT-2026-008",
            "project_name": "西寧廠二期配電盤擴建工程",
            "workers": 34,
            "progress_pct": 85,
            "billed_pct": 80,
            "status": "🟢 施工順暢",
        },
        {
            "project_id": "PRJ-2026-02",
            "quote_id": "QT-2026-011",
            "project_name": "平陽工業區廠房機電統包",
            "workers": 28,
            "progress_pct": 62,
            "billed_pct": 50,
            "status": "🟡 需留意工期",
        },
        {
            "project_id": "PRJ-2026-03",
            "quote_id": "QT-2026-015",
            "project_name": "隆安省光電園區變壓器安裝",
            "workers": 24,
            "progress_pct": 40,
            "billed_pct": 30,
            "status": "🟢 正常",
        },
    ]

    db_rows = _query_first_valid(
        engine,
        [
            (
                """
                SELECT project_id, quote_id, project_name,
                       COALESCE(worker_count, 0) AS workers,
                       COALESCE(progress_pct, 0) AS progress_pct,
                       COALESCE(billed_pct, 0) AS billed_pct,
                       COALESCE(status_label, '🟢 正常') AS status
                FROM eng_projects
                WHERE tenant_id = :tid
                ORDER BY id DESC
                LIMIT 20
                """,
                {"tid": tenant_id},
            ),
            (
                """
                SELECT project_code AS project_id, quote_id, project_name,
                       COALESCE(workers_count, 0) AS workers,
                       COALESCE(progress_rate, 0) AS progress_pct,
                       COALESCE(billing_rate, 0) AS billed_pct,
                       COALESCE(status, '🟢 正常') AS status
                FROM engineering_projects
                LIMIT 20
                """,
                {},
            ),
        ],
    )

    projects = db_rows if db_rows else fallback_projects
    active_sites = len(projects)
    total_workers = sum(int(float(p.get("workers") or 0)) for p in projects)
    avg_progress = (
        sum(float(p.get("progress_pct") or 0) for p in projects) / active_sites
        if active_sites > 0
        else 0.0
    )
    avg_billed = (
        sum(float(p.get("billed_pct") or 0) for p in projects) / active_sites
        if active_sites > 0
        else 0.0
    )

    return {
        "active_sites": active_sites,
        "total_workers": total_workers,
        "avg_progress": round(avg_progress, 1),
        "avg_billed": round(avg_billed, 1),
        "projects": projects,
    }


def _load_production_overview_data(engine, tenant_id: str) -> dict:
    fallback_lines = [
        {
            "line_code": "L2_SHEET",
            "sub_dept": "板金組",
            "po_id": "PO-2026-101",
            "plan_qty": 120,
            "done_qty": 102,
            "progress_pct": 85.0,
            "status": "🟢 正常",
        },
        {
            "line_code": "L2_PAINT",
            "sub_dept": "塗裝組",
            "po_id": "PO-2026-102",
            "plan_qty": 120,
            "done_qty": 84,
            "progress_pct": 70.0,
            "status": "🟢 正常",
        },
        {
            "line_code": "L2_PANEL",
            "sub_dept": "配盤組",
            "po_id": "PO-2026-103",
            "plan_qty": 85,
            "done_qty": 51,
            "progress_pct": 60.0,
            "status": "🟡 趕工中",
        },
        {
            "line_code": "L2_WH",
            "sub_dept": "倉庫管理",
            "po_id": "PR-2026-205",
            "plan_qty": 325,
            "done_qty": 276,
            "progress_pct": 84.9,
            "status": "🟢 料帳同步",
        },
    ]

    db_rows = _query_first_valid(
        engine,
        [
            (
                """
                SELECT line_code, sub_dept_name AS sub_dept, po_id,
                       COALESCE(plan_qty, 0) AS plan_qty,
                       COALESCE(done_qty, 0) AS done_qty,
                       COALESCE(progress_pct, 0) AS progress_pct,
                       COALESCE(status_label, '🟢 正常') AS status
                FROM prod_line_progress
                WHERE tenant_id = :tid
                ORDER BY id ASC
                LIMIT 20
                """,
                {"tid": tenant_id},
            ),
            (
                """
                SELECT work_center AS line_code, section_name AS sub_dept, order_no AS po_id,
                       COALESCE(target_qty, 0) AS plan_qty,
                       COALESCE(completed_qty, 0) AS done_qty,
                       COALESCE(completion_rate, 0) AS progress_pct,
                       COALESCE(status, '🟢 正常') AS status
                FROM production_progress
                LIMIT 20
                """,
                {},
            ),
        ],
    )

    lines = db_rows if db_rows else fallback_lines
    total_plan = sum(float(x.get("plan_qty") or 0) for x in lines)
    total_done = sum(float(x.get("done_qty") or 0) for x in lines)
    overall_pct = round((total_done / total_plan * 100), 1) if total_plan > 0 else 0.0

    return {
        "line_count": len(lines),
        "total_plan": total_plan,
        "total_done": total_done,
        "overall_pct": overall_pct,
        "lines": lines,
    }


def _render_engineering_overview(engine, tenant_id: str, lang: str):
    code = ui_theme.norm_lang(lang)
    labels = {
        "zh": {
            "k1": "目前工地數量",
            "k2": "施工人數",
            "k3": "平均施工進度",
            "k4": "平均款項請款進度",
            "tbl": "📋 進行中工地施工與款項進度明細",
            "c_pid": "案場編號",
            "c_qid": "估價單號",
            "c_name": "工地／案場名稱",
            "c_wk": "施工人數",
            "c_prog": "施工進度 (%)",
            "c_bill": "款項進度 (%)",
            "c_st": "狀態",
        },
        "vi": {
            "k1": "Số Công Trường Đang Làm",
            "k2": "Nhân Công Thi Công",
            "k3": "Tiến Độ Thi Công TB",
            "k4": "Tiến Độ Thanh Toán TB",
            "tbl": "📋 Chi Tiết Tiến Độ Thi Công & Thanh Toán Công Trường",
            "c_pid": "Mã Dự Án",
            "c_qid": "Mã Báo Giá",
            "c_name": "Tên Công Trường",
            "c_wk": "Số Nhân Công",
            "c_prog": "Thi Công (%)",
            "c_bill": "Thanh Toán (%)",
            "c_st": "Trạng Thái",
        },
        "en": {
            "k1": "Active Work Sites",
            "k2": "Site Workers",
            "k3": "Avg. Build Progress",
            "k4": "Avg. Billing Progress",
            "tbl": "📋 Active Work Sites: Progress & Billing",
            "c_pid": "Project ID",
            "c_qid": "Quote ID",
            "c_name": "Site Name",
            "c_wk": "Workers",
            "c_prog": "Build (%)",
            "c_bill": "Billing (%)",
            "c_st": "Status",
        },
    }[code]

    data = _load_engineering_overview_data(engine, tenant_id)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(labels["k1"], f"{data['active_sites']} 處")
    c2.metric(labels["k2"], f"{data['total_workers']} 人")
    c3.metric(labels["k3"], f"{data['avg_progress']}%")
    c4.metric(labels["k4"], f"{data['avg_billed']}%")

    st.markdown(f"#### {labels['tbl']}")
    df = pd.DataFrame([
        {
            labels["c_pid"]: p.get("project_id") or "-",
            labels["c_qid"]: p.get("quote_id") or "-",
            labels["c_name"]: p.get("project_name") or "-",
            labels["c_wk"]: int(float(p.get("workers") or 0)),
            labels["c_prog"]: f"{float(p.get('progress_pct') or 0):.0f}%",
            labels["c_bill"]: f"{float(p.get('billed_pct') or 0):.0f}%",
            labels["c_st"]: p.get("status") or "-",
        }
        for p in data["projects"]
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_production_overview(engine, tenant_id: str, lang: str):
    code = ui_theme.norm_lang(lang)
    labels = {
        "zh": {
            "k1": "生產／倉儲組別數",
            "k2": "計畫總數量",
            "k3": "已完成／出入庫數量",
            "k4": "整體生產進度",
            "tbl": "📋 各部門／組別生產進度與數量一覽",
            "c_dept": "部門／組別",
            "c_po": "工單／採購單號",
            "c_plan": "計畫數量",
            "c_done": "完成數量",
            "c_pct": "進度 (%)",
            "c_st": "狀態",
        },
        "vi": {
            "k1": "Số Tổ Sản Xuất / Kho",
            "k2": "Tổng Số Lượng Kế Hoạch",
            "k3": "Số Lượng Đã Hoàn Thành",
            "k4": "Tiến Độ Sản Xuất Tổng",
            "tbl": "📋 Tiến Độ & Sản Lượng Theo Từng Tổ / Bộ Phận",
            "c_dept": "Tổ / Bộ Phận",
            "c_po": "Mã Lệnh / PO",
            "c_plan": "Kế Hoạch",
            "c_done": "Hoàn Thành",
            "c_pct": "Tiến Độ (%)",
            "c_st": "Trạng Thái",
        },
        "en": {
            "k1": "Production / WH Units",
            "k2": "Planned Quantity",
            "k3": "Completed Quantity",
            "k4": "Overall Progress",
            "tbl": "📋 Production Progress & Output by Unit",
            "c_dept": "Unit / Sub-Dept",
            "c_po": "Order / PO ID",
            "c_plan": "Planned",
            "c_done": "Completed",
            "c_pct": "Progress (%)",
            "c_st": "Status",
        },
    }[code]

    data = _load_production_overview_data(engine, tenant_id)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(labels["k1"], f"{data['line_count']} 組")
    c2.metric(labels["k2"], f"{data['total_plan']:,.0f}")
    c3.metric(labels["k3"], f"{data['total_done']:,.0f}")
    c4.metric(labels["k4"], f"{data['overall_pct']}%")

    st.markdown(f"#### {labels['tbl']}")
    df = pd.DataFrame([
        {
            labels["c_dept"]: x.get("sub_dept") or x.get("line_code") or "-",
            labels["c_po"]: x.get("po_id") or "-",
            labels["c_plan"]: f"{float(x.get('plan_qty') or 0):,.0f}",
            labels["c_done"]: f"{float(x.get('done_qty') or 0):,.0f}",
            labels["c_pct"]: f"{float(x.get('progress_pct') or 0):.1f}%",
            labels["c_st"]: x.get("status") or "-",
        }
        for x in data["lines"]
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_general_l1_overview(engine, tenant_id: str, node: dict, lang: str):
    code = ui_theme.norm_lang(lang)
    dept_name = node.get("node_name") or "L1 部門"
    titles = {
        "zh": ("📊 部門即時總覽", "待簽核單據", "進行中專案", "異常警示", "部門狀態"),
        "vi": ("📊 Tổng Quan Tức Thời Phòng Ban", "Chờ Phê Duyệt", "Dự Án Đang Chạy", "Cảnh Báo", "Trạng Thái"),
        "en": ("📊 Department Live Overview", "Pending Approvals", "Active Projects", "Alerts", "Status"),
    }[code]

    pending_cnt = 0
    if engine:
        try:
            with engine.connect() as conn:
                row = conn.execute(
                    text("SELECT COUNT(*) FROM sys_approval_requests WHERE status LIKE '%待%' OR status LIKE '%簽核%'")
                ).fetchone()
                if row:
                    pending_cnt = int(row[0] or 0)
        except Exception:
            pending_cnt = 0

    st.markdown(f"#### {titles[0]} — {dept_name}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(titles[1], f"{pending_cnt} 筆")
    c2.metric(titles[2], "3 案")
    c3.metric(titles[3], "0 筆")
    c4.metric(titles[4], "🟢 運作正常")


def render_l1_department_overview(engine, tenant_id: str, node: dict, lang: str = "zh") -> bool:
    """依 L1 實體部門渲染對應總覽；若為 L1 獨立功能入口則回傳 False 由上方直接開啟功能"""
    if str(node.get("level_tier") or "L1").upper() != "L1":
        return False
    if node.get("node_type") == "L1_FUNC":
        return False

    ncode = str(node.get("node_code") or "").upper()
    nname = str(node.get("node_name") or "")

    if ncode == "DEPT_ENG" or "工程" in nname:
        _render_engineering_overview(engine, tenant_id, lang)
        return True

    if ncode == "DEPT_PROD" or "生產" in nname:
        _render_production_overview(engine, tenant_id, lang)
        return True

    _render_general_l1_overview(engine, tenant_id, node, lang)
    return True
