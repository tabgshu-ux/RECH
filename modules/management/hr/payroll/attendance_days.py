# ==========================================
# 檔案路徑：modules/management/hr/payroll/attendance_days.py
# 職責：L2 行政／人事 - 上班天數紀錄、請假天數彙整與出勤天數計算（獨立新功能模組）
# ==========================================

from datetime import date, datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text


def _fmt_vnd(val: float | int) -> str:
    try:
        return f"{round(float(val or 0)):,}".replace(",", ".") + " ₫"
    except Exception:
        return "0 ₫"


def ensure_attendance_days_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS public.hr_monthly_workdays (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        pay_month VARCHAR(16) NOT NULL,
                        emp_code VARCHAR(80),
                        emp_name VARCHAR(150) NOT NULL,
                        dept_name VARCHAR(100),
                        standard_days NUMERIC(6, 2) DEFAULT 22.0,
                        leave_days NUMERIC(6, 2) DEFAULT 0.0,
                        actual_days NUMERIC(6, 2) DEFAULT 22.0,
                        notes TEXT,
                        updated_by VARCHAR(100),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE (tenant_id, pay_month, emp_name)
                    );
                """)
            )
    except Exception:
        pass


def _calc_leave_days_map(engine, tenant_id: str, pay_month: str) -> dict[str, float]:
    """從 hr_leaves 彙整每位員工在指定月份的請假天數"""
    leave_map: dict[str, float] = {}
    if not engine:
        return leave_map
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT emp_name, start_date, end_date
                    FROM public.hr_leaves
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                """),
                {"tid": tenant_id},
            ).fetchall()
            for r in rows:
                ename = str(r[0] or "").strip()
                if not ename:
                    continue
                s_str = str(r[1] or "")[:10]
                e_str = str(r[2] or "")[:10]
                if not (s_str.startswith(pay_month) or e_str.startswith(pay_month)):
                    continue
                try:
                    d1 = date.fromisoformat(s_str)
                    d2 = date.fromisoformat(e_str)
                    days = float(max(1, (d2 - d1).days + 1))
                except Exception:
                    days = 1.0
                leave_map[ename] = leave_map.get(ename, 0.0) + days
    except Exception:
        pass
    return leave_map


def _calc_punch_days_map(engine, tenant_id: str, pay_month: str) -> dict[str, int]:
    """從 hr_attendance_logs 統計當月有打卡／補登紀錄的天數（作為參考出勤天數）"""
    punch_map: dict[str, set[str]] = {}
    if not engine:
        return {}
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT emp_name, punch_time
                    FROM public.hr_attendance_logs
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                """),
                {"tid": tenant_id},
            ).fetchall()
            for r in rows:
                ename = str(r[0] or "").strip()
                ptm = str(r[1] or "")
                if ename and ptm.startswith(pay_month):
                    day_key = ptm[:10]
                    punch_map.setdefault(ename, set()).add(day_key)
    except Exception:
        pass
    return {k: len(v) for k, v in punch_map.items()}


def get_attendance_days_by_employee(
    engine,
    tenant_id: str = "REETECH_VN",
    pay_month: str | None = None,
    default_standard_days: float = 22.0,
) -> dict[str, dict[str, float]]:
    """
    回傳 {emp_name: {'standard_days': ..., 'leave_days': ..., 'actual_days': ..., 'ratio': ...}}
    供薪資計算帶入實際上班天數與出勤比例
    """
    if not pay_month:
        pay_month = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().strftime("%Y-%m")

    result: dict[str, dict[str, float]] = {}
    if not engine:
        return result

    leave_map = _calc_leave_days_map(engine, tenant_id, pay_month)

    # 先讀取人工／已存檔的月出勤天數覆蓋值
    saved_map: dict[str, dict[str, float]] = {}
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT emp_name, COALESCE(standard_days, :std), COALESCE(leave_days, 0), COALESCE(actual_days, :std)
                    FROM public.hr_monthly_workdays
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                      AND pay_month = :pm
                """),
                {"tid": tenant_id, "pm": pay_month, "std": float(default_standard_days)},
            ).fetchall()
            for r in rows:
                ename = str(r[0] or "").strip()
                if ename:
                    std_d = float(r[1] or default_standard_days)
                    lv_d = float(r[2] or 0.0)
                    act_d = max(0.0, float(r[3] if r[3] is not None else (std_d - lv_d)))
                    saved_map[ename] = {
                        "standard_days": std_d,
                        "leave_days": lv_d,
                        "actual_days": act_d,
                        "ratio": (act_d / std_d) if std_d > 0 else 1.0,
                    }
    except Exception:
        pass

    # 再帶出在職員工名冊預設計算
    try:
        with engine.connect() as conn:
            emp_rows = conn.execute(
                text("""
                    SELECT emp_name
                    FROM public.employee_profiles
                    WHERE COALESCE(status, '在職') <> '離職'
                """)
            ).fetchall()
            for r in emp_rows:
                ename = str(r[0] or "").strip()
                if not ename:
                    continue
                if ename in saved_map:
                    result[ename] = saved_map[ename]
                else:
                    std_d = float(default_standard_days)
                    lv_d = float(leave_map.get(ename, leave_map.get(ename, 0.0)))
                    act_d = max(0.0, std_d - lv_d)
                    result[ename] = {
                        "standard_days": std_d,
                        "leave_days": lv_d,
                        "actual_days": act_d,
                        "ratio": (act_d / std_d) if std_d > 0 else 1.0,
                    }
    except Exception:
        pass

    return result


def render_attendance_days_panel(engine, tenant_id: str = "REETECH_VN", default_month: str | None = None):
    if not default_month:
        default_month = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().strftime("%Y-%m")

    current_user = st.session_state.get("user_name") or "admin"
    st.markdown("#### 📅 上班天數紀錄與出勤彙整")
    st.caption("彙整每月標準應出勤天數、請假天數與實際上班天數，並可調整／存檔後回流薪資計算。")

    if not engine:
        st.info("尚未連線資料庫，無法彙整上班天數。")
        return

    ensure_attendance_days_table(engine)

    c1, c2 = st.columns([2, 2])
    with c1:
        pay_month = st.text_input("出勤月份 (YYYY-MM)", value=default_month, max_chars=7, key="att_days_month")
    with c2:
        std_days_default = st.number_input("本月標準應出勤天數", min_value=1.0, max_value=31.0, value=22.0, step=0.5, key="att_std_days")

    clean_month = (pay_month or "").strip() or default_month
    leave_map = _calc_leave_days_map(engine, tenant_id, clean_month)
    punch_map = _calc_punch_days_map(engine, tenant_id, clean_month)

    emp_rows = []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT COALESCE(emp_code, CAST(id AS TEXT)) AS emp_code,
                           emp_name,
                           COALESCE(department, '未指定') AS dept_name,
                           COALESCE(base_salary, 0) AS base_salary
                    FROM public.employee_profiles
                    WHERE COALESCE(status, '在職') <> '離職'
                    ORDER BY id ASC
                """)
            ).fetchall()
            emp_rows = [
                {
                    "emp_code": r[0],
                    "emp_name": str(r[1] or "").strip(),
                    "dept_name": r[2],
                    "base_salary": float(r[3] or 0.0),
                }
                for r in rows
                if r[1]
            ]
    except Exception:
        emp_rows = []

    if not emp_rows:
        st.info("目前尚未查到在職員工資料。")
        return

    table_rows = []
    for e in emp_rows:
        ename = e["emp_name"]
        lv_d = float(leave_map.get(ename, 0.0))
        act_d = max(0.0, float(std_days_default) - lv_d)
        table_rows.append({
            "emp_code": e["emp_code"],
            "emp_name": ename,
            "dept_name": e["dept_name"],
            "standard_days": float(std_days_default),
            "leave_days": lv_d,
            "actual_days": act_d,
            "punch_days": int(punch_map.get(ename, 0)),
            "base_salary": e["base_salary"],
        })

    df_att = pd.DataFrame(table_rows)

    edited_att = st.data_editor(
        df_att[["emp_code", "emp_name", "dept_name", "standard_days", "leave_days", "actual_days", "punch_days"]],
        use_container_width=True,
        hide_index=True,
        disabled=["emp_code", "emp_name", "dept_name", "punch_days"],
        column_config={
            "emp_code": "工號",
            "emp_name": "員工姓名",
            "dept_name": "部門",
            "standard_days": st.column_config.NumberColumn("應出勤天數", format="%.1f"),
            "leave_days": st.column_config.NumberColumn("請假天數", format="%.1f"),
            "actual_days": st.column_config.NumberColumn("實際上班天數", format="%.1f"),
            "punch_days": "打卡/補登天數",
        },
        key="hr_workdays_editor",
    )

    if st.button("💾 儲存本月上班天數紀錄", type="primary", use_container_width=True, key="btn_save_workdays"):
        try:
            with engine.begin() as conn:
                for _, r in edited_att.iterrows():
                    ename = str(r["emp_name"] or "").strip()
                    if not ename:
                        continue
                    std_v = float(r["standard_days"] or std_days_default)
                    lv_v = float(r["leave_days"] or 0.0)
                    act_v = max(0.0, float(r["actual_days"] if r["actual_days"] is not None else (std_v - lv_v)))
                    conn.execute(
                        text("""
                            INSERT INTO public.hr_monthly_workdays (
                                tenant_id, pay_month, emp_code, emp_name, dept_name,
                                standard_days, leave_days, actual_days, updated_by, updated_at
                            )
                            VALUES (
                                :tid, :pm, :ecode, :ename, :dname,
                                :std, :lv, :act, :uby, CURRENT_TIMESTAMP
                            )
                            ON CONFLICT (tenant_id, pay_month, emp_name) DO UPDATE SET
                                standard_days = EXCLUDED.standard_days,
                                leave_days = EXCLUDED.leave_days,
                                actual_days = EXCLUDED.actual_days,
                                updated_by = EXCLUDED.updated_by,
                                updated_at = CURRENT_TIMESTAMP
                        """),
                        {
                            "tid": tenant_id,
                            "pm": clean_month,
                            "ecode": str(r["emp_code"] or ""),
                            "ename": ename,
                            "dname": str(r["dept_name"] or ""),
                            "std": std_v,
                            "lv": lv_v,
                            "act": act_v,
                            "uby": current_user,
                        },
                    )
            st.success(f"✅ 已儲存【{clean_month}】全體員工上班天數紀錄。")
            st.rerun()
        except Exception as e:
            st.error(f"❌ 儲存上班天數失敗：{e}")


def render(engine=None, lang="zh", **kwargs):
    tid = st.session_state.get("tenant_id", "REETECH_VN")
    render_attendance_days_panel(engine=engine, tenant_id=tid)


def show(engine=None, lang="zh", **kwargs):
    return render(engine=engine, lang=lang, **kwargs)
