# ==========================================
# 檔案路徑：modules/management/hr/payroll/field_payroll_calc.py
# 職責：L2 行政／人事 - 全體員工薪資明細（細分津貼/獎金/社保）與週日保養加班分頁
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _fmt_vnd(val: float | int) -> str:
    try:
        return f"{round(float(val or 0)):,}".replace(",", ".") + " ₫"
    except Exception:
        return "0 ₫"


def _load_all_employees_df(engine, tenant_id: str) -> pd.DataFrame:
    if not engine:
        return pd.DataFrame()

    queries = [
        """
        SELECT COALESCE(emp_code, CAST(id AS TEXT)) AS emp_code,
               emp_name,
               COALESCE(department, dept_name, '未指定') AS department,
               COALESCE(position, '員工') AS position,
               COALESCE(staff_type, '一般員工') AS staff_type,
               COALESCE(base_salary, base_salary_vnd, 0) AS base_salary,
               COALESCE(status, '在職') AS status
        FROM public.employee_profiles
        WHERE COALESCE(status, '在職') <> '離職'
        ORDER BY id ASC
        """,
        """
        SELECT COALESCE(emp_code, CAST(id AS TEXT)) AS emp_code,
               emp_name,
               COALESCE(department, '未指定') AS department,
               COALESCE(position, '員工') AS position,
               COALESCE(staff_type, '一般員工') AS staff_type,
               COALESCE(base_salary, 0) AS base_salary,
               COALESCE(status, '在職') AS status
        FROM public.employee_profiles
        WHERE COALESCE(status, '在職') <> '離職'
        ORDER BY id ASC
        """,
        """
        SELECT COALESCE(emp_code, CAST(id AS TEXT)) AS emp_code,
               emp_name,
               COALESCE(dept_name, '未指定') AS department,
               COALESCE(position, '員工') AS position,
               '一般員工' AS staff_type,
               COALESCE(base_salary_vnd, 0) AS base_salary,
               COALESCE(status, '在職') AS status
        FROM public.employee_profiles
        WHERE COALESCE(status, '在職') <> '離職'
        ORDER BY id ASC
        """,
    ]

    for sql in queries:
        try:
            with engine.connect() as conn:
                rows = conn.execute(text(sql)).fetchall()
                if rows is not None:
                    df = pd.DataFrame([r._asdict() for r in rows])
                    if not df.empty:
                        df["base_salary"] = pd.to_numeric(df["base_salary"], errors="coerce").fillna(0.0)
                    return df
        except Exception:
            continue

    return pd.DataFrame()


def _load_approved_sunday_ot_map(engine, tenant_id: str, pay_month: str) -> dict[str, float]:
    if not engine:
        return {}
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT staff_name, COALESCE(SUM(ot_pay_vnd), 0) AS total_ot
                    FROM public.hr_sunday_maint_overtime
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                      AND approval_status = '已核准'
                      AND TO_CHAR(maint_date, 'YYYY-MM') = :pm
                    GROUP BY staff_name
                """),
                {"tid": tenant_id, "pm": pay_month},
            ).fetchall()
            return {str(r[0]).strip(): float(r[1] or 0.0) for r in rows if r[0]}
    except Exception:
        return {}


def _load_worker_logs_map(engine, tenant_id: str, pay_month: str) -> dict[str, float]:
    if not engine:
        return {}
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT worker_name, COALESCE(SUM(total_amount_vnd), 0) AS total_amt
                    FROM public.hr_daily_worker_logs
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                      AND TO_CHAR(work_date::date, 'YYYY-MM') = :pm
                    GROUP BY worker_name
                """),
                {"tid": tenant_id, "pm": pay_month},
            ).fetchall()
            return {str(r[0]).strip(): float(r[1] or 0.0) for r in rows if r[0]}
    except Exception:
        return {}


def _render_payroll_main_tab(engine, tenant_id: str, default_month: str):
    current_user = st.session_state.get("user_name") or "admin"

    c_top1, c_top2, c_top3, c_top4 = st.columns([1.6, 2.0, 1.7, 1.7])
    with c_top1:
        pay_month = st.text_input("計薪月份 (YYYY-MM)", value=default_month, max_chars=7, key="pay_month_input")
    with c_top2:
        dept_filter = st.text_input("部門／人員篩選（留空全公司）", placeholder="例：設計、生產部、倉庫", key="pay_dept_filter")
    with c_top3:
        emp_si_pct = st.number_input("員工社保扣款比例 (%)", min_value=0.0, max_value=50.0, value=10.5, step=0.5, key="pay_emp_si_pct")
    with c_top4:
        company_si_pct = st.number_input("公司雇主社保比例 (%)", min_value=0.0, max_value=50.0, value=21.5, step=0.5, key="pay_company_si_pct")

    clean_month = (pay_month or "").strip() or default_month
    df_emp = _load_all_employees_df(engine, tenant_id)
    sunday_ot_map = _load_approved_sunday_ot_map(engine, tenant_id, clean_month)
    worker_amt_map = _load_worker_logs_map(engine, tenant_id, clean_month)

    if df_emp.empty:
        st.warning("⚠️ 目前尚未在 `employee_profiles` 查到在職員工資料，請先至「員工資料」新增員工。")
        return

    if dept_filter and dept_filter.strip():
        kw = dept_filter.strip().lower()
        df_emp = df_emp[
            df_emp["department"].astype(str).str.lower().str.contains(kw, na=False)
            | df_emp["emp_name"].astype(str).str.lower().str.contains(kw, na=False)
            | df_emp["position"].astype(str).str.lower().str.contains(kw, na=False)
        ]

    rows_calc = []
    for _, r in df_emp.iterrows():
        ename = str(r.get("emp_name") or "").strip()
        base_sal = float(r.get("base_salary") or 0.0)
        sunday_ot = float(sunday_ot_map.get(ename, 0.0))
        worker_amt = float(worker_amt_map.get(ename, 0.0))
        emp_ded_init = round(base_sal * (float(emp_si_pct) / 100.0), 0)
        company_si_init = round(base_sal * (float(company_si_pct) / 100.0), 0)

        rows_calc.append({
            "emp_code": r.get("emp_code") or "-",
            "emp_name": ename,
            "department": r.get("department") or "-",
            "position": r.get("position") or "-",
            "base_salary": base_sal,
            "pos_allowance": 0.0,
            "site_allowance": 0.0,
            "meal_bonus": 0.0,
            "other_allowance": 0.0,
            "extra_ot_vnd": 0.0,
            "sunday_ot_vnd": sunday_ot,
            "worker_amt_vnd": worker_amt,
            "emp_deduction_vnd": emp_ded_init,
            "company_si_vnd": company_si_init,
        })

    df_pay = pd.DataFrame(rows_calc)

    st.caption("津貼／獎金已拆細；同時分開計算「員工扣款」與「公司雇主負擔社保」，公司負擔部分可一鍵拋轉至財務報表。")

    edit_cols = [
        "emp_code", "emp_name", "department", "position", "base_salary",
        "pos_allowance", "site_allowance", "meal_bonus", "other_allowance",
        "extra_ot_vnd", "sunday_ot_vnd", "worker_amt_vnd",
        "emp_deduction_vnd", "company_si_vnd",
    ]
    edited_df = st.data_editor(
        df_pay[edit_cols],
        use_container_width=True,
        hide_index=True,
        disabled=["emp_code", "emp_name", "department", "position", "sunday_ot_vnd", "worker_amt_vnd"],
        column_config={
            "emp_code": "工號",
            "emp_name": "員工姓名",
            "department": "部門",
            "position": "職稱",
            "base_salary": st.column_config.NumberColumn("底薪 (₫)", format="%d"),
            "pos_allowance": st.column_config.NumberColumn("職務津貼 (₫)", format="%d"),
            "site_allowance": st.column_config.NumberColumn("工程/出差/油費/電話 (₫)", format="%d"),
            "meal_bonus": st.column_config.NumberColumn("伙食/全勤/績效 (₫)", format="%d"),
            "other_allowance": st.column_config.NumberColumn("其他津貼/獎金 (₫)", format="%d"),
            "extra_ot_vnd": st.column_config.NumberColumn("其他加班費 (₫)", format="%d"),
            "sunday_ot_vnd": st.column_config.NumberColumn("週日保養加班費 (₫)", format="%d"),
            "worker_amt_vnd": st.column_config.NumberColumn("點工／臨時工 (₫)", format="%d"),
            "emp_deduction_vnd": st.column_config.NumberColumn("員工社保扣款 (₫)", format="%d"),
            "company_si_vnd": st.column_config.NumberColumn("公司雇主社保 (₫)", format="%d"),
        },
        key="payroll_detail_editor",
    )

    num_cols = [
        "base_salary", "pos_allowance", "site_allowance", "meal_bonus",
        "other_allowance", "extra_ot_vnd", "sunday_ot_vnd", "worker_amt_vnd",
        "emp_deduction_vnd", "company_si_vnd",
    ]
    for col in num_cols:
        edited_df[col] = pd.to_numeric(edited_df[col], errors="coerce").fillna(0.0)

    edited_df["津貼獎金小計 (₫)"] = (
        edited_df["pos_allowance"]
        + edited_df["site_allowance"]
        + edited_df["meal_bonus"]
        + edited_df["other_allowance"]
    )
    edited_df["應發合計 (₫)"] = (
        edited_df["base_salary"]
        + edited_df["津貼獎金小計 (₫)"]
        + edited_df["extra_ot_vnd"]
        + edited_df["sunday_ot_vnd"]
        + edited_df["worker_amt_vnd"]
    )
    edited_df["實發薪資 (₫)"] = edited_df["應發合計 (₫)"] - edited_df["emp_deduction_vnd"]

    total_emp_ded = float(edited_df["emp_deduction_vnd"].sum())
    total_company_si = float(edited_df["company_si_vnd"].sum())
    total_net_pay = float(edited_df["實發薪資 (₫)"].sum())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("員工社保扣款合計", _fmt_vnd(total_emp_ded))
    m2.metric("公司雇主負擔社保（進財報）", _fmt_vnd(total_company_si))
    m3.metric("社保繳納總額（員工＋公司）", _fmt_vnd(total_emp_ded + total_company_si))
    m4.metric("全體實發薪資總計", _fmt_vnd(total_net_pay))

    st.markdown("#### 💰 薪資與社保結算彙總表")
    summary_cols = [
        "emp_code", "emp_name", "department", "base_salary",
        "津貼獎金小計 (₫)", "sunday_ot_vnd", "emp_deduction_vnd",
        "company_si_vnd", "實發薪資 (₫)",
    ]
    disp = edited_df[summary_cols].copy()
    for c in [
        "base_salary", "津貼獎金小計 (₫)", "sunday_ot_vnd",
        "emp_deduction_vnd", "company_si_vnd", "實發薪資 (₫)",
    ]:
        disp[c] = disp[c].apply(_fmt_vnd)

    disp = disp.rename(columns={
        "emp_code": "工號",
        "emp_name": "員工姓名",
        "department": "部門",
        "base_salary": "底薪",
        "sunday_ot_vnd": "週日保養加班費",
        "emp_deduction_vnd": "員工社保扣款",
        "company_si_vnd": "公司雇主社保",
    })
    st.dataframe(disp, use_container_width=True, hide_index=True)

    try:
        from modules.management.hr.payroll.payroll_finance_sync import render_finance_sync_panel

        render_finance_sync_panel(
            engine=engine,
            tenant_id=tenant_id,
            pay_month=clean_month,
            headcount=len(edited_df),
            emp_ded_total=total_emp_ded,
            company_si_total=total_company_si,
            net_pay_total=total_net_pay,
            current_user=current_user,
        )
    except Exception as e:
        st.warning(f"⚠️ 財務報表同步模組載入異常：{e}")


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    today_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
    default_month = today_vn.strftime("%Y-%m")

    st.markdown("### 💵 全體員工薪資管理與計算")

    tab_payroll, tab_sunday_ot = st.tabs([
        "📋 全體員工薪資明細與結算",
        "🔧 週日設備保養與加班登記簽核",
    ])

    with tab_payroll:
        _render_payroll_main_tab(engine=engine, tenant_id=tenant_id, default_month=default_month)

    with tab_sunday_ot:
        try:
            from modules.management.hr.sunday_maintenance_ot import render_sunday_maintenance_overtime_section

            render_sunday_maintenance_overtime_section(engine=engine, tenant_id=tenant_id, show_header=True)
        except Exception as e:
            st.warning(f"⚠️ 週日設備保養簽核模組載入異常：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
