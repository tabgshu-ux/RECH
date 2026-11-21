# ==========================================
# 檔案路徑：modules/management/hr/sunday_maintenance_ot.py
# 職責：L2 行政／人事 - 週日設備保養簽核與加班費結算（依員工底薪 × 倍率自動試算）
# ==========================================

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text


def _fmt_vnd_simple(val) -> str:
    try:
        return f"{round(float(val or 0)):,}".replace(",", ".") + " ₫"
    except Exception:
        return "0 ₫"


def _next_sunday_date(d: date) -> date:
    return d + timedelta(days=(6 - d.weekday()) % 7)


def _calc_hourly_ot_from_base(base_salary: float, multiplier: float = 1.5, monthly_work_hours: float = 208.0) -> float:
    if not base_salary or base_salary <= 0:
        return 0.0
    hourly_base = float(base_salary) / float(monthly_work_hours or 208.0)
    return round(hourly_base * float(multiplier or 1.5), 0)


def _ensure_sunday_maint_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS public.hr_sunday_maint_overtime (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        maint_date DATE NOT NULL,
                        staff_name VARCHAR(150) NOT NULL,
                        dept_name VARCHAR(80) NOT NULL,
                        equipment_name VARCHAR(200) NOT NULL,
                        hours_worked NUMERIC(8, 2) DEFAULT 8.0,
                        hourly_rate_vnd NUMERIC(18, 2) DEFAULT 0,
                        ot_pay_vnd NUMERIC(18, 2) DEFAULT 0,
                        submitted_by VARCHAR(100),
                        approval_status VARCHAR(32) DEFAULT '待簽核',
                        approved_by VARCHAR(100),
                        approved_at TIMESTAMP WITH TIME ZONE,
                        notes TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def get_approved_sunday_ot_by_employee(engine, tenant_id: str = "REETECH_VN", month_prefix: str | None = None) -> dict[str, float]:
    if not engine:
        return {}
    try:
        with engine.connect() as conn:
            sql = """
                SELECT staff_name, COALESCE(SUM(ot_pay_vnd), 0) AS total_ot
                FROM public.hr_sunday_maint_overtime
                WHERE tenant_id = :tid
                  AND approval_status = '已核准'
            """
            params = {"tid": tenant_id}
            if month_prefix:
                sql += " AND TO_CHAR(maint_date, 'YYYY-MM') = :mp"
                params["mp"] = month_prefix
            sql += " GROUP BY staff_name"
            rows = conn.execute(text(sql), params).fetchall()
            return {r[0]: float(r[1] or 0) for r in rows if r[0]}
    except Exception:
        return {}


def render_sunday_maintenance_overtime_section(engine, tenant_id: str = "REETECH_VN", show_header: bool = True):
    if show_header:
        st.markdown("### 🔧 週日設備保養簽核與加班費結算（設計／生產部／倉庫）")
        st.caption("依員工底薪與加班倍率自動計算加班費，經主管簽名核准後自動納入薪資加班費。")

    if not engine:
        st.info("尚未連線資料庫，無法儲存週日保養簽核紀錄。")
        return

    _ensure_sunday_maint_table(engine)

    today_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
    current_user = st.session_state.get("user_name") or "admin"

    staff_rows = []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT emp_name,
                           COALESCE(department, '生產部') AS dept,
                           COALESCE(base_salary, 0) AS base_salary
                    FROM public.employee_profiles
                    WHERE COALESCE(status, '在職') = '在職'
                    ORDER BY id ASC
                """)
            ).fetchall()
            staff_rows = [
                {"name": r[0], "dept": r[1], "base_salary": float(r[2] or 0)}
                for r in rows
                if r[0]
            ]
    except Exception:
        staff_rows = []

    staff_names = [s["name"] for s in staff_rows]
    staff_dept_map = {s["name"]: s["dept"] for s in staff_rows}
    staff_salary_map = {s["name"]: s["base_salary"] for s in staff_rows}

    with st.expander("➕ 登記週日設備保養出勤（送出後待簽核）", expanded=False):
        with st.form("form_sunday_maint_in_payroll"):
            c1, c2, c3 = st.columns(3)
            with c1:
                m_date = st.date_input("週日保養日期", value=_next_sunday_date(today_vn))
                sel_staff = st.selectbox("保養人員（自動帶出員工底薪）", ["（手動輸入）"] + staff_names)
                manual_staff = st.text_input("人員姓名（選「手動輸入」時填寫）", placeholder="若不在名冊請填姓名")
            with c2:
                dept_choices = ["設計", "生產部", "倉庫", "工程部"]
                mapped_dept = staff_dept_map.get(sel_staff, "倉庫")
                d_idx = dept_choices.index(mapped_dept) if mapped_dept in dept_choices else 2
                m_dept = st.selectbox("所屬部門", dept_choices, index=d_idx)
                m_equip = st.text_input("保養設備／項目", placeholder="例：空壓機、配電盤、吊車")
                m_sub = st.text_input("提報主管（如倉庫主管）", value=current_user)
            with c3:
                m_hours = st.number_input("保養時數", min_value=0.5, max_value=24.0, value=8.0, step=0.5)
                ot_mult = st.number_input("加班倍率（例：1.5 倍）", min_value=1.0, max_value=5.0, value=1.5, step=0.1)
                m_note = st.text_input("備註", placeholder="保養內容或簽單說明")

            base_sal = 0.0 if sel_staff == "（手動輸入）" else float(staff_salary_map.get(sel_staff, 0.0))
            hourly_ot_rate = _calc_hourly_ot_from_base(base_sal, multiplier=float(ot_mult))
            ot_calc = round(float(m_hours) * hourly_ot_rate, 0)

            if base_sal > 0:
                st.info(
                    f"底薪 **{_fmt_vnd_simple(base_sal)}** ÷ 208 小時 × **{ot_mult}** 倍 ＝ 每小時加班費 **{_fmt_vnd_simple(hourly_ot_rate)}**｜"
                    f"本筆 {m_hours} 小時試算：**{_fmt_vnd_simple(ot_calc)}**"
                )
            else:
                st.warning("⚠️ 此人員尚無底薪資料，若直接送出將以 0 ₫ 計算（請先於員工資料維護底薪）。")

            if st.form_submit_button("💾 送出保養紀錄（待簽核）", type="primary", use_container_width=True):
                final_name = manual_staff.strip() if sel_staff == "（手動輸入）" else (manual_staff.strip() or sel_staff)
                if not final_name or not m_equip.strip():
                    st.warning("⚠️ 請填寫人員姓名與保養設備。")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO public.hr_sunday_maint_overtime (
                                        tenant_id, maint_date, staff_name, dept_name, equipment_name,
                                        hours_worked, hourly_rate_vnd, ot_pay_vnd, submitted_by,
                                        approval_status, notes, created_at
                                    )
                                    VALUES (
                                        :tid, :md, :sn, :dn, :en,
                                        :hw, :hr, :op, :sb,
                                        '待簽核', :nt, CURRENT_TIMESTAMP
                                    )
                                """),
                                {
                                    "tid": tenant_id, "md": m_date, "sn": final_name,
                                    "dn": m_dept, "en": m_equip.strip(), "hw": float(m_hours),
                                    "hr": float(hourly_ot_rate), "op": float(ot_calc),
                                    "sb": m_sub.strip() or current_user, "nt": m_note.strip() or None,
                                },
                            )
                        st.success("✅ 已送出週日保養紀錄，等待簽核。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 儲存失敗：{e}")

    df_m = pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT id, maint_date, staff_name, dept_name, equipment_name,
                           COALESCE(hours_worked, 0) AS hours_worked,
                           COALESCE(ot_pay_vnd, 0) AS ot_pay_vnd,
                           COALESCE(approval_status, '待簽核') AS approval_status,
                           COALESCE(approved_by, '-') AS approved_by
                    FROM public.hr_sunday_maint_overtime
                    WHERE tenant_id = :tid
                    ORDER BY maint_date DESC, id DESC
                """),
                {"tid": tenant_id},
            ).fetchall()
            if rows:
                df_m = pd.DataFrame([r._asdict() for r in rows])
    except Exception:
        df_m = pd.DataFrame()

    if df_m.empty:
        st.info("目前尚無週日設備保養紀錄。")
        return

    disp_m = df_m.copy()
    disp_m["加班費"] = disp_m["ot_pay_vnd"].apply(_fmt_vnd_simple)
    st.dataframe(
        disp_m.rename(columns={
            "id": "編號", "maint_date": "日期", "dept_name": "部門",
            "staff_name": "人員", "equipment_name": "設備", "hours_worked": "時數",
            "approval_status": "簽核狀態", "approved_by": "簽核人",
        })[["編號", "日期", "部門", "人員", "設備", "時數", "加班費", "簽核狀態", "簽核人"]],
        use_container_width=True,
        hide_index=True,
    )

    pending = df_m[df_m["approval_status"] == "待簽核"]
    if not pending.empty:
        p_opts = {
            f"#{r['id']}｜{r['maint_date']}｜{r['dept_name']}-{r['staff_name']}｜{_fmt_vnd_simple(r['ot_pay_vnd'])}": int(r["id"])
            for _, r in pending.iterrows()
        }
        sel_p = st.selectbox("選擇待簽核紀錄", list(p_opts.keys()))
        signer = st.text_input("簽核人（簽名確認）", value=current_user, key="sunday_ot_signer")
        b1, b2 = st.columns(2)
        if b1.button("✅ 簽名核准（計入薪資加班費）", type="primary", use_container_width=True):
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE public.hr_sunday_maint_overtime
                        SET approval_status = '已核准', approved_by = :ab, approved_at = CURRENT_TIMESTAMP
                        WHERE id = :rid
                    """),
                    {"ab": signer.strip() or current_user, "rid": p_opts[sel_p]},
                )
            st.success("✅ 已簽名核准，加班費已計入薪資計算。")
            st.rerun()
        if b2.button("❌ 退回", use_container_width=True):
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE public.hr_sunday_maint_overtime
                        SET approval_status = '已退回', approved_by = :ab, approved_at = CURRENT_TIMESTAMP
                        WHERE id = :rid
                    """),
                    {"ab": signer.strip() or current_user, "rid": p_opts[sel_p]},
                )
            st.warning("⚠️ 已退回。")
            st.rerun()

    approved = df_m[df_m["approval_status"] == "已核准"]
    if not approved.empty:
        st.markdown("#### 💵 已核准之週日保養加班費（已納入薪資計算）")
        grp = approved.groupby(["staff_name", "dept_name"], as_index=False)["ot_pay_vnd"].sum()
        grp["核准加班費合計"] = grp["ot_pay_vnd"].apply(_fmt_vnd_simple)
        st.dataframe(
            grp.rename(columns={"staff_name": "員工姓名", "dept_name": "部門"})[["部門", "員工姓名", "核准加班費合計"]],
            use_container_width=True,
            hide_index=True,
        )


def render(engine=None, lang="zh", **kwargs):
    tid = st.session_state.get("tenant_id", "REETECH_VN")
    render_sunday_maintenance_overtime_section(engine=engine, tenant_id=tid, show_header=True)


def show(engine=None, lang="zh", **kwargs):
    return render(engine=engine, lang=lang, **kwargs)
