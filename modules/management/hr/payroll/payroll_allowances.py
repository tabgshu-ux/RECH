# ==========================================
# 檔案路徑：modules/management/hr/payroll/payroll_allowances.py
# 職責：L2 行政／人事 - 員工津貼登錄、批次套用與查詢（獨立新功能模組）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text


ALLOWANCE_CATEGORIES = [
    "其他津貼",
    "職務津貼",
    "工程／出差／油費／電話補貼",
    "伙食／全勤／績效獎金",
    "專業／有毒／看倉津貼",
]


def _fmt_vnd(val: float | int) -> str:
    try:
        return f"{round(float(val or 0)):,}".replace(",", ".") + " ₫"
    except Exception:
        return "0 ₫"


def ensure_allowance_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS public.hr_employee_allowances (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        pay_month VARCHAR(16) NOT NULL,
                        emp_code VARCHAR(80),
                        emp_name VARCHAR(150) NOT NULL,
                        dept_name VARCHAR(100),
                        allowance_type VARCHAR(100) NOT NULL,
                        amount_vnd NUMERIC(18, 2) DEFAULT 0,
                        reason TEXT,
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def get_monthly_allowances_by_employee(engine, tenant_id: str, pay_month: str) -> dict[str, dict[str, float]]:
    """回傳 {emp_name: {'pos': ..., 'site': ..., 'meal': ..., 'other': ...}} 供薪資計算帶入"""
    result: dict[str, dict[str, float]] = {}
    if not engine:
        return result
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT emp_name, allowance_type, COALESCE(SUM(amount_vnd), 0) AS total_amt
                    FROM public.hr_employee_allowances
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                      AND pay_month = :pm
                    GROUP BY emp_name, allowance_type
                """),
                {"tid": tenant_id, "pm": pay_month},
            ).fetchall()
            for r in rows:
                ename = str(r[0] or "").strip()
                atype = str(r[1] or "")
                amt = float(r[2] or 0.0)
                if not ename:
                    continue
                bucket = result.setdefault(ename, {"pos": 0.0, "site": 0.0, "meal": 0.0, "other": 0.0})
                if "職務" in atype:
                    bucket["pos"] += amt
                elif "工程" in atype or "出差" in atype or "油費" in atype or "電話" in atype:
                    bucket["site"] += amt
                elif "伙食" in atype or "全勤" in atype or "績效" in atype:
                    bucket["meal"] += amt
                else:
                    bucket["other"] += amt
    except Exception:
        pass
    return result


def render_allowance_input_panel(engine, tenant_id: str = "REETECH_VN", default_month: str | None = None):
    if not default_month:
        default_month = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().strftime("%Y-%m")

    current_user = st.session_state.get("user_name") or "admin"
    st.markdown("#### 🎁 員工津貼與其他津貼輸入（支援單筆／整部門批次）")
    st.caption("在此登錄各類津貼（特別是「其他津貼」與部門別津貼），儲存後會自動帶入當月全體薪資計算。")

    ensure_allowance_table(engine)

    emp_list: list[dict] = []
    if engine:
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text("""
                        SELECT COALESCE(emp_code, CAST(id AS TEXT)) AS emp_code,
                               emp_name,
                               COALESCE(department, '未指定') AS department
                        FROM public.employee_profiles
                        WHERE COALESCE(status, '在職') <> '離職'
                        ORDER BY id ASC
                    """)
                ).fetchall()
                emp_list = [{"emp_code": r[0], "emp_name": r[1], "department": r[2]} for r in rows if r[1]]
        except Exception:
            emp_list = []

    emp_names = [e["emp_name"] for e in emp_list]
    emp_code_map = {e["emp_name"]: e["emp_code"] for e in emp_list}
    emp_dept_map = {e["emp_name"]: e["department"] for e in emp_list}
    depts = sorted({e["department"] for e in emp_list if e["department"]}) or ["辦公室", "設計", "生產部", "倉庫", "工程部"]

    tab_single, tab_batch = st.tabs(["✍️ 單筆／指定人員津貼輸入", "👥 依部門批次發放津貼"])

    with tab_single:
        with st.form("form_single_allowance"):
            c1, c2, c3 = st.columns(3)
            with c1:
                pm_s = st.text_input("計薪月份 (YYYY-MM)*", value=default_month, max_chars=7, key="alw_pm_s")
                sel_emp = st.selectbox("選擇員工（或選下方自行輸入）", ["（自行輸入姓名）"] + emp_names, key="alw_sel_emp")
                custom_emp = st.text_input("員工姓名*", placeholder="若不在名冊或自行輸入請填姓名", key="alw_custom_emp")
            with c2:
                mapped_dept = emp_dept_map.get(sel_emp, depts[0])
                d_idx = depts.index(mapped_dept) if mapped_dept in depts else 0
                dept_s = st.selectbox("所屬部門", depts, index=d_idx, key="alw_dept_s")
                alw_type = st.selectbox("津貼類別*", ALLOWANCE_CATEGORIES, index=0, key="alw_type_s")
                amount_s = st.number_input("津貼金額 (VND)*", min_value=0.0, value=0.0, step=50000.0, key="alw_amt_s")
            with c3:
                reason_s = st.text_input("發放原因／備註", placeholder="例：特殊任務補助、交通補貼、其他津貼", key="alw_reason_s")

            if st.form_submit_button("💾 儲存津貼紀錄", type="primary", use_container_width=True):
                final_name = custom_emp.strip() if sel_emp == "（自行輸入姓名）" else (custom_emp.strip() or sel_emp)
                if not final_name or float(amount_s) <= 0:
                    st.warning("⚠️ 請填寫員工姓名且津貼金額大於 0。")
                elif not engine:
                    st.error("❌ 尚未連線資料庫。")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO public.hr_employee_allowances (
                                        tenant_id, pay_month, emp_code, emp_name, dept_name,
                                        allowance_type, amount_vnd, reason, created_by, created_at
                                    )
                                    VALUES (
                                        :tid, :pm, :ecode, :ename, :dname,
                                        :atype, :amt, :rsn, :cby, CURRENT_TIMESTAMP
                                    )
                                """),
                                {
                                    "tid": tenant_id,
                                    "pm": (pm_s or default_month).strip(),
                                    "ecode": emp_code_map.get(final_name),
                                    "ename": final_name,
                                    "dname": dept_s,
                                    "atype": alw_type,
                                    "amt": float(amount_s),
                                    "rsn": reason_s.strip() or None,
                                    "cby": current_user,
                                },
                            )
                        st.success(f"✅ 已新增【{final_name}】的「{alw_type}」：{_fmt_vnd(amount_s)}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 儲存失敗：{e}")

    with tab_batch:
        with st.form("form_batch_allowance"):
            b1, b2, b3 = st.columns(3)
            with b1:
                pm_b = st.text_input("計薪月份 (YYYY-MM)*", value=default_month, max_chars=7, key="alw_pm_b")
                target_dept = st.selectbox("選擇目標部門*", depts, key="alw_dept_b")
            with b2:
                alw_type_b = st.selectbox("津貼類別*", ALLOWANCE_CATEGORIES, index=0, key="alw_type_b")
                amount_b = st.number_input("每人津貼金額 (VND)*", min_value=0.0, value=0.0, step=50000.0, key="alw_amt_b")
            with b3:
                reason_b = st.text_input("批次發放說明", placeholder="例：部門專案津貼、其他津貼", key="alw_reason_b")

            target_emps = [e for e in emp_list if e["department"] == target_dept]
            st.caption(f"目前「{target_dept}」在職員工共 **{len(target_emps)}** 人。")

            if st.form_submit_button("👥 批次套用至該部門全員", type="primary", use_container_width=True):
                if not target_emps or float(amount_b) <= 0:
                    st.warning("⚠️ 該部門無在職員工，或金額需大於 0。")
                elif not engine:
                    st.error("❌ 尚未連線資料庫。")
                else:
                    try:
                        with engine.begin() as conn:
                            for e in target_emps:
                                conn.execute(
                                    text("""
                                        INSERT INTO public.hr_employee_allowances (
                                            tenant_id, pay_month, emp_code, emp_name, dept_name,
                                            allowance_type, amount_vnd, reason, created_by, created_at
                                        )
                                        VALUES (
                                            :tid, :pm, :ecode, :ename, :dname,
                                            :atype, :amt, :rsn, :cby, CURRENT_TIMESTAMP
                                        )
                                    """),
                                    {
                                        "tid": tenant_id,
                                        "pm": (pm_b or default_month).strip(),
                                        "ecode": e["emp_code"],
                                        "ename": e["emp_name"],
                                        "dname": target_dept,
                                        "atype": alw_type_b,
                                        "amt": float(amount_b),
                                        "rsn": reason_b.strip() or None,
                                        "cby": current_user,
                                    },
                                )
                        st.success(f"✅ 已為「{target_dept}」{len(target_emps)} 位員工新增「{alw_type_b}」（每人 {_fmt_vnd(amount_b)}）。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 批次儲存失敗：{e}")

    # 顯示當月已登錄津貼明細
    if engine:
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text("""
                        SELECT id, pay_month, COALESCE(dept_name, '-') AS dept_name,
                               emp_name, allowance_type, COALESCE(amount_vnd, 0) AS amount_vnd,
                               COALESCE(reason, '-') AS reason, COALESCE(created_by, '-') AS created_by
                        FROM public.hr_employee_allowances
                        WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                          AND pay_month = :pm
                        ORDER BY id DESC
                    """),
                    {"tid": tenant_id, "pm": default_month},
                ).fetchall()
                if rows:
                    df_a = pd.DataFrame([r._asdict() for r in rows])
                    df_a["金額"] = df_a["amount_vnd"].apply(_fmt_vnd)
                    st.markdown("##### 📄 本月已登錄津貼明細")
                    st.dataframe(
                        df_a.rename(columns={
                            "id": "編號",
                            "pay_month": "月份",
                            "dept_name": "部門",
                            "emp_name": "員工姓名",
                            "allowance_type": "津貼類別",
                            "reason": "備註",
                            "created_by": "登錄人",
                        })[["編號", "月份", "部門", "員工姓名", "津貼類別", "金額", "備註", "登錄人"]],
                        use_container_width=True,
                        hide_index=True,
                    )
        except Exception:
            pass
