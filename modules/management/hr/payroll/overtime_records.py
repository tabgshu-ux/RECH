# ==========================================
# 檔案路徑：modules/management/hr/payroll/overtime_records.py
# 職責：L2 行政／人事 - 一般加班登記、主管核准與倍率加班費彙整（獨立新功能模組）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text


OT_RATE_CHOICES = {
    "平日加班 (1.5x)": 1.5,
    "夜班／特殊加班 (1.95x)": 1.95,
    "休息日加班 (2.0x)": 2.0,
    "國定假日／例假加班 (3.0x)": 3.0,
}


def _fmt_vnd(val: float | int) -> str:
    try:
        return f"{round(float(val or 0)):,}".replace(",", ".") + " ₫"
    except Exception:
        return "0 ₫"


def ensure_overtime_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS public.hr_overtime_records (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        pay_month VARCHAR(16) NOT NULL,
                        ot_date DATE NOT NULL,
                        emp_code VARCHAR(80),
                        emp_name VARCHAR(150) NOT NULL,
                        dept_name VARCHAR(100),
                        ot_type VARCHAR(80) NOT NULL,
                        multiplier NUMERIC(6, 2) DEFAULT 1.5,
                        hours_worked NUMERIC(8, 2) DEFAULT 1.0,
                        hourly_rate_vnd NUMERIC(18, 2) DEFAULT 0,
                        ot_pay_vnd NUMERIC(18, 2) DEFAULT 0,
                        reason TEXT,
                        submitted_by VARCHAR(100),
                        approval_status VARCHAR(32) DEFAULT '待簽核',
                        approved_by VARCHAR(100),
                        approved_at TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def get_approved_overtime_by_employee(engine, tenant_id: str = "REETECH_VN", pay_month: str | None = None) -> dict[str, float]:
    """回傳 {emp_name: approved_ot_pay_vnd} 供薪資計算帶入一般加班費"""
    result: dict[str, float] = {}
    if not engine:
        return result
    try:
        with engine.connect() as conn:
            sql = """
                SELECT emp_name, COALESCE(SUM(ot_pay_vnd), 0) AS total_ot
                FROM public.hr_overtime_records
                WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                  AND approval_status = '已核准'
            """
            params = {"tid": tenant_id}
            if pay_month:
                sql += " AND pay_month = :pm"
                params["pm"] = pay_month
            sql += " GROUP BY emp_name"
            rows = conn.execute(text(sql), params).fetchall()
            for r in rows:
                ename = str(r[0] or "").strip()
                if ename:
                    result[ename] = float(r[1] or 0.0)
    except Exception:
        pass
    return result


def render_overtime_records_panel(engine, tenant_id: str = "REETECH_VN", default_month: str | None = None, monthly_hours: float = 208.0):
    if not default_month:
        default_month = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().strftime("%Y-%m")

    current_user = st.session_state.get("user_name") or "admin"
    today_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()

    st.markdown("#### ⏱️ 一般加班登記與簽核（1.5x / 1.95x / 2.0x / 3.0x）")
    st.caption("依員工底薪與加班倍率計算加班費；經主管簽名核准後，自動帶入當月薪資表的「其他加班費」。")

    if not engine:
        st.info("尚未連線資料庫，無法儲存加班紀錄。")
        return

    ensure_overtime_table(engine)

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
                    "emp_name": r[1],
                    "dept_name": r[2],
                    "base_salary": float(r[3] or 0.0),
                }
                for r in rows
                if r[1]
            ]
    except Exception:
        emp_rows = []

    emp_names = [e["emp_name"] for e in emp_rows]
    emp_code_map = {e["emp_name"]: e["emp_code"] for e in emp_rows}
    emp_dept_map = {e["emp_name"]: e["dept_name"] for e in emp_rows}
    emp_sal_map = {e["emp_name"]: e["base_salary"] for e in emp_rows}

    with st.expander("➕ 登記員工加班紀錄（送出後待簽核）", expanded=False):
        with st.form("form_hr_overtime_entry"):
            c1, c2, c3 = st.columns(3)
            with c1:
                ot_date = st.date_input("加班日期", value=today_vn, key="ot_date_input")
                sel_emp = st.selectbox("加班員工", emp_names if emp_names else ["（尚無員工資料）"], key="ot_sel_emp")
                dept_disp = emp_dept_map.get(sel_emp, "未指定")
                st.text_input("所屬部門", value=dept_disp, disabled=True, key="ot_dept_disp")
            with c2:
                ot_label = st.selectbox("加班倍率類別", list(OT_RATE_CHOICES.keys()), key="ot_type_sel")
                ot_hours = st.number_input("加班時數", min_value=0.5, max_value=24.0, value=2.0, step=0.5, key="ot_hours_num")
                ot_reason = st.text_input("加班事由／單號", placeholder="例：趕工、機台搶修", key="ot_reason_txt")
            with c3:
                ot_sub = st.text_input("提報人／主管", value=current_user, key="ot_sub_txt")

            mult = float(OT_RATE_CHOICES[ot_label])
            base_sal = float(emp_sal_map.get(sel_emp, 0.0))
            hourly_ot = round((base_sal / float(monthly_hours or 208.0)) * mult, 0) if base_sal > 0 else 0.0
            ot_total = round(float(ot_hours) * hourly_ot, 0)
            pm_val = ot_date.strftime("%Y-%m")

            st.info(
                f"計薪月份：**{pm_val}**｜底薪：**{_fmt_vnd(base_sal)}**｜"
                f"每小時加班費：**{_fmt_vnd(hourly_ot)}**｜本筆試算：**{_fmt_vnd(ot_total)}**"
            )

            if st.form_submit_button("💾 送出加班紀錄（待簽核）", type="primary", use_container_width=True):
                if not emp_names or not sel_emp:
                    st.warning("⚠️ 請先選擇有效的員工。")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO public.hr_overtime_records (
                                        tenant_id, pay_month, ot_date, emp_code, emp_name,
                                        dept_name, ot_type, multiplier, hours_worked,
                                        hourly_rate_vnd, ot_pay_vnd, reason, submitted_by,
                                        approval_status, created_at
                                    )
                                    VALUES (
                                        :tid, :pm, :odt, :ecode, :ename,
                                        :dname, :otype, :mult, :hrs,
                                        :hrate, :opay, :rsn, :sby,
                                        '待簽核', CURRENT_TIMESTAMP
                                    )
                                """),
                                {
                                    "tid": tenant_id,
                                    "pm": pm_val,
                                    "odt": ot_date,
                                    "ecode": emp_code_map.get(sel_emp),
                                    "ename": sel_emp,
                                    "dname": dept_disp,
                                    "otype": ot_label,
                                    "mult": mult,
                                    "hrs": float(ot_hours),
                                    "hrate": float(hourly_ot),
                                    "opay": float(ot_total),
                                    "rsn": ot_reason.strip() or None,
                                    "sby": ot_sub.strip() or current_user,
                                },
                            )
                        st.success("✅ 已送出加班紀錄，等待主管簽核。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 儲存失敗：{e}")

    df_ot = pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT id, pay_month, ot_date::text AS ot_date,
                           COALESCE(dept_name, '-') AS dept_name,
                           emp_name, ot_type,
                           COALESCE(hours_worked, 0) AS hours_worked,
                           COALESCE(ot_pay_vnd, 0) AS ot_pay_vnd,
                           COALESCE(approval_status, '待簽核') AS approval_status,
                           COALESCE(approved_by, '-') AS approved_by,
                           COALESCE(reason, '-') AS reason
                    FROM public.hr_overtime_records
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                    ORDER BY ot_date DESC, id DESC
                """),
                {"tid": tenant_id},
            ).fetchall()
            if rows:
                df_ot = pd.DataFrame([r._asdict() for r in rows])
    except Exception:
        df_ot = pd.DataFrame()

    if df_ot.empty:
        st.info("目前尚無一般加班紀錄。")
        return

    disp_ot = df_ot.copy()
    disp_ot["加班費"] = disp_ot["ot_pay_vnd"].apply(_fmt_vnd)
    st.dataframe(
        disp_ot.rename(columns={
            "id": "編號",
            "pay_month": "計薪月",
            "ot_date": "日期",
            "dept_name": "部門",
            "emp_name": "員工",
            "ot_type": "加班類別",
            "hours_worked": "時數",
            "approval_status": "簽核狀態",
            "approved_by": "簽核人",
            "reason": "事由",
        })[["編號", "計薪月", "日期", "部門", "員工", "加班類別", "時數", "加班費", "簽核狀態", "簽核人", "事由"]],
        use_container_width=True,
        hide_index=True,
    )

    pending = df_ot[df_ot["approval_status"] == "待簽核"]
    if not pending.empty:
        p_opts = {
            f"#{r['id']}｜{r['ot_date']}｜{r['emp_name']}｜{r['ot_type']}｜{_fmt_vnd(r['ot_pay_vnd'])}": int(r["id"])
            for _, r in pending.iterrows()
        }
        sel_p = st.selectbox("選擇待簽核加班單", list(p_opts.keys()), key="ot_pending_sel")
        signer = st.text_input("簽核人", value=current_user, key="ot_signer_txt")
        b1, b2 = st.columns(2)
        if b1.button("✅ 核准加班費（計入薪資）", type="primary", use_container_width=True, key="btn_ot_approve"):
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE public.hr_overtime_records
                        SET approval_status = '已核准', approved_by = :ab, approved_at = CURRENT_TIMESTAMP
                        WHERE id = :rid
                    """),
                    {"ab": signer.strip() or current_user, "rid": p_opts[sel_p]},
                )
            st.success("✅ 已核准加班費。")
            st.rerun()
        if b2.button("❌ 退回", use_container_width=True, key="btn_ot_reject"):
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE public.hr_overtime_records
                        SET approval_status = '已退回', approved_by = :ab, approved_at = CURRENT_TIMESTAMP
                        WHERE id = :rid
                    """),
                    {"ab": signer.strip() or current_user, "rid": p_opts[sel_p]},
                )
            st.warning("⚠️ 已退回該筆加班單。")
            st.rerun()


def render(engine=None, lang="zh", **kwargs):
    tid = st.session_state.get("tenant_id", "REETECH_VN")
    render_overtime_records_panel(engine=engine, tenant_id=tid)


def show(engine=None, lang="zh", **kwargs):
    return render(engine=engine, lang=lang, **kwargs)
