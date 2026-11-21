# ==========================================
# 檔案路徑：modules/management/hr/payroll/field_payroll_calc.py
# 職責：L2 行政／人事 - 人事薪資計算（臨時工/點工逐人結算 + 週日設備保養核准加班費彙整）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _fmt_vnd(val: float | int) -> str:
    return f"{round(float(val or 0)):,}".replace(",", ".") + " ₫"


def _load_worker_logs_df(engine, tenant_id: str) -> pd.DataFrame:
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT id,
                           COALESCE(work_date::text, '') AS work_date,
                           COALESCE(project_id, '-') AS project_id,
                           COALESCE(worker_name, '-') AS worker_name,
                           COALESCE(role_or_dept, '點工') AS role_or_dept,
                           COALESCE(work_days, 0) AS work_days,
                           COALESCE(daily_rate_vnd, 0) AS daily_rate_vnd,
                           COALESCE(adjustment_vnd, 0) AS adjustment_vnd,
                           COALESCE(total_amount_vnd, 0) AS total_amount_vnd,
                           COALESCE(status, '待結算') AS status
                    FROM public.hr_daily_worker_logs
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                    ORDER BY id DESC LIMIT 200
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def _load_approved_sunday_ot_df(engine, tenant_id: str) -> pd.DataFrame:
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT id,
                           COALESCE(maint_date::text, '') AS maint_date,
                           COALESCE(dept_name, '-') AS dept_name,
                           COALESCE(staff_name, '-') AS staff_name,
                           COALESCE(equipment_name, '-') AS equipment_name,
                           COALESCE(hours_worked, 0) AS hours_worked,
                           COALESCE(ot_pay_vnd, 0) AS ot_pay_vnd,
                           COALESCE(approved_by, '-') AS approved_by
                    FROM public.hr_sunday_maint_overtime
                    WHERE tenant_id = :tid
                      AND approval_status = '已核准'
                    ORDER BY maint_date DESC, id DESC
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    _ = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()

    st.markdown("### 💵 人事薪資計算 — 逐人薪資結算與週日保養加班費")
    st.caption("彙整逐人點工／臨時工結算明細，並自動帶入已簽名核准的「週日設備保養加班費」（設計／生產部／倉庫）。")

    df_worker = _load_worker_logs_df(engine, tenant_id)
    df_sunday = _load_approved_sunday_ot_df(engine, tenant_id)

    worker_sum = float(df_worker["total_amount_vnd"].sum()) if not df_worker.empty and "total_amount_vnd" in df_worker.columns else 0.0
    sunday_sum = float(df_sunday["ot_pay_vnd"].sum()) if not df_sunday.empty and "ot_pay_vnd" in df_sunday.columns else 0.0

    m1, m2, m3 = st.columns(3)
    m1.metric("點工／臨時工結算合計", _fmt_vnd(worker_sum))
    m2.metric("已核准週日保養加班費", _fmt_vnd(sunday_sum))
    m3.metric("本次彙總應發金額", _fmt_vnd(worker_sum + sunday_sum))

    st.divider()
    st.markdown("#### 👷 臨時工／點工逐人薪資結算")
    if df_worker.empty:
        st.info("目前尚無臨時工／點工出勤紀錄，可由工程部「外包估驗與臨時工／點工出工登記」逐人填寫。")
    else:
        disp_w = df_worker.copy()
        disp_w["日薪"] = disp_w["daily_rate_vnd"].apply(_fmt_vnd)
        disp_w["調薪／加減"] = disp_w["adjustment_vnd"].apply(_fmt_vnd)
        disp_w["結算金額"] = disp_w["total_amount_vnd"].apply(_fmt_vnd)
        st.dataframe(
            disp_w.rename(columns={
                "work_date": "日期",
                "project_id": "專案",
                "worker_name": "人員姓名",
                "role_or_dept": "組別／職務",
                "work_days": "工天",
                "status": "狀態",
            })[["日期", "專案", "組別／職務", "人員姓名", "工天", "日薪", "調薪／加減", "結算金額", "狀態"]],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.markdown("#### 🔧 已核准之週日設備保養加班費（回流薪資計算）")
    if df_sunday.empty:
        st.info("目前尚無「已核准」的週日設備保養加班費；如有週日保養紀錄，請於下方或「週日設備保養簽核與加班費結算」簽名核准。")
    else:
        grp = (
            df_sunday.groupby(["staff_name", "dept_name"], as_index=False)
            .agg(total_hours=("hours_worked", "sum"), total_ot=("ot_pay_vnd", "sum"), times=("id", "count"))
        )
        grp["保養次數"] = grp["times"].astype(str) + " 次"
        grp["核准加班費"] = grp["total_ot"].apply(_fmt_vnd)
        st.dataframe(
            grp.rename(columns={"staff_name": "員工姓名", "dept_name": "部門", "total_hours": "總時數"})[
                ["部門", "員工姓名", "保養次數", "總時數", "核准加班費"]
            ],
            use_container_width=True,
            hide_index=True,
        )

    # 嵌入週日設備保養簽核與登記區塊（不另開新檔，共用 hr_sunday_maint_overtime 資料表）
    try:
        from modules.management.hr.sunday_maintenance_ot import render_sunday_maintenance_overtime_section

        render_sunday_maintenance_overtime_section(engine=engine, tenant_id=tenant_id, show_header=True)
    except Exception:
        pass


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
