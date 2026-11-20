# ==========================================
# 檔案路徑：modules/management/hr/payroll/field_payroll_calc.py
# 職責：管理部人事 - 臨時工／點工逐人薪資彙算與發薪批次結算
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _fmt_vnd(val: float | int) -> str:
    return f"{round(float(val or 0)):,}".replace(",", ".")


def _ensure_payroll_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS hr_daily_worker_logs (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        log_no VARCHAR(64) UNIQUE NOT NULL,
                        project_id VARCHAR(80),
                        site_name VARCHAR(160) NOT NULL,
                        worker_name VARCHAR(120) NOT NULL,
                        worker_role VARCHAR(80) DEFAULT '點工／臨時工',
                        work_date DATE NOT NULL,
                        work_days NUMERIC(8, 2) NOT NULL,
                        base_daily_rate_vnd NUMERIC(18, 2) NOT NULL,
                        rate_adj_vnd NUMERIC(18, 2) DEFAULT 0,
                        effective_rate_vnd NUMERIC(18, 2) NOT NULL,
                        total_amount_vnd NUMERIC(18, 2) NOT NULL,
                        performance_rating VARCHAR(32) DEFAULT 'NORMAL',
                        performance_note TEXT,
                        payroll_status VARCHAR(32) DEFAULT 'PENDING_PAYROLL',
                        payroll_batch_id VARCHAR(64),
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def _load_worker_logs(engine, tenant_id: str) -> pd.DataFrame:
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT log_no, COALESCE(project_id, '-') AS project_id, site_name,
                           worker_name, COALESCE(worker_role, '點工') AS worker_role,
                           TO_CHAR(work_date, 'YYYY-MM-DD') AS work_date,
                           COALESCE(work_days, 0) AS work_days,
                           COALESCE(base_daily_rate_vnd, 0) AS base_daily_rate_vnd,
                           COALESCE(rate_adj_vnd, 0) AS rate_adj_vnd,
                           COALESCE(effective_rate_vnd, 0) AS effective_rate_vnd,
                           COALESCE(total_amount_vnd, 0) AS total_amount_vnd,
                           COALESCE(performance_rating, 'NORMAL') AS performance_rating,
                           COALESCE(performance_note, '-') AS performance_note,
                           COALESCE(payroll_status, 'PENDING_PAYROLL') AS payroll_status,
                           COALESCE(payroll_batch_id, '-') AS payroll_batch_id
                    FROM hr_daily_worker_logs
                    WHERE tenant_id = :tid
                    ORDER BY id DESC LIMIT 100
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    hr_user = st.session_state.get("user_name") or "HR_Payroll"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 💵 人事薪資計算 — 臨時工／點工逐人薪資結算")
    st.caption("依工程部回傳的「逐人點工出工與表現調薪／調降」明細，自動按人名彙整發薪金額並產生發薪批次。")
    _ensure_payroll_tables(engine)

    df = _load_worker_logs(engine, tenant_id)
    if df.empty:
        st.info("目前尚無臨時工／點工出工紀錄，可由工程部「外包估驗與臨時工／點工出工登記」逐人填寫。")
        return

    pending_df = df[df["payroll_status"] == "PENDING_PAYROLL"]
    st.markdown("#### 👥 依點工姓名彙整（待發放／歷史明細）")
    by_person = (
        df.groupby(["worker_name", "worker_role", "payroll_status"], as_index=False)
        .agg(
            出工天數=("work_days", "sum"),
            平均核定日薪=("effective_rate_vnd", "mean"),
            累計日薪調整=("rate_adj_vnd", "sum"),
            應付總額=("total_amount_vnd", "sum"),
        )
    )
    by_person["平均核定日薪(₫)"] = by_person["平均核定日薪"].apply(_fmt_vnd)
    by_person["累計日薪調整(₫)"] = by_person["累計日薪調整"].apply(_fmt_vnd)
    by_person["應付總額(₫)"] = by_person["應付總額"].apply(_fmt_vnd)
    st.dataframe(
        by_person.rename(columns={"worker_name": "點工姓名", "worker_role": "工種", "payroll_status": "薪資狀態"})[
            ["點工姓名", "工種", "薪資狀態", "出工天數", "平均核定日薪(₫)", "累計日薪調整(₫)", "應付總額(₫)"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.markdown("#### 📋 逐筆點工出工與表現調薪明細")
    disp = df.copy()
    for col in ["base_daily_rate_vnd", "rate_adj_vnd", "effective_rate_vnd", "total_amount_vnd"]:
        disp[col] = disp[col].apply(_fmt_vnd)
    disp = disp.rename(columns={
        "log_no": "出工單號", "project_id": "專案", "site_name": "案場",
        "worker_name": "點工姓名", "worker_role": "工種", "work_date": "日期",
        "work_days": "工天", "base_daily_rate_vnd": "基準日薪(₫)",
        "rate_adj_vnd": "調升/調降(₫)", "effective_rate_vnd": "核定日薪(₫)",
        "total_amount_vnd": "應付金額(₫)", "performance_rating": "表現",
        "performance_note": "評語/調薪原因", "payroll_status": "發薪狀態",
        "payroll_batch_id": "發薪批次",
    })
    st.dataframe(disp, use_container_width=True, hide_index=True)

    if not pending_df.empty and engine:
        st.divider()
        st.markdown("#### 🧾 產生點工發薪批次")
        batch_no = f"PAYBATCH-{now_vn.strftime('%Y%m%d-%H%M')}"
        pending_sum = float(pending_df["total_amount_vnd"].sum())
        st.info(f"目前共有 **{len(pending_df)}** 筆待結算點工紀錄，合計應發 **{_fmt_vnd(pending_sum)} ₫**（經辦：{hr_user}）。")
        if st.button(f"✅ 確認結算並產生發薪批次 `{batch_no}`", type="primary", use_container_width=True):
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            UPDATE hr_daily_worker_logs
                            SET payroll_status = 'PAID_BATCHED', payroll_batch_id = :bno
                            WHERE tenant_id = :tid AND payroll_status = 'PENDING_PAYROLL'
                        """),
                        {"bno": batch_no, "tid": tenant_id},
                    )
                st.success(f"✅ 已完成結算，發薪批次編號：`{batch_no}`（合計 {_fmt_vnd(pending_sum)} ₫）。")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 批次結算失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
