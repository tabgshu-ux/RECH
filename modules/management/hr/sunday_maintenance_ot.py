# ==========================================
# 檔案路徑：modules/management/hr/sunday_maintenance_ot.py
# 職責：L2 行政／人事 - 週日設備保養簽核（設計/生產部/倉庫）與加班費回流薪資計算
# ==========================================

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _fmt_vnd(val: float | int) -> str:
    return f"{round(float(val or 0)):,}".replace(",", ".")


def _next_sunday(d: date) -> date:
    days_ahead = (6 - d.weekday()) % 7
    return d + timedelta(days=days_ahead)


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
                        hourly_rate_vnd NUMERIC(18, 2) DEFAULT 100000,
                        ot_pay_vnd NUMERIC(18, 2) DEFAULT 800000,
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


def _load_candidate_staff(engine, tenant_id: str) -> list[dict]:
    fallback = [
        {"emp_name": "設計組人員 A", "dept_name": "設計", "ot_hourly_vnd": 120000.0},
        {"emp_name": "生產部技師 B", "dept_name": "生產部", "ot_hourly_vnd": 100000.0},
        {"emp_name": "倉庫人員 C", "dept_name": "倉庫", "ot_hourly_vnd": 100000.0},
    ]
    if not engine:
        return fallback
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT emp_name,
                           COALESCE(department, '生產部') AS dept_name,
                           100000.0 AS ot_hourly_vnd
                    FROM public.employee_profiles
                    WHERE COALESCE(status, '在職') = '在職'
                    ORDER BY id ASC
                """)
            ).fetchall()
            if rows:
                return [
                    {
                        "emp_name": r[0],
                        "dept_name": r[1],
                        "ot_hourly_vnd": float(r[2] or 100000.0),
                    }
                    for r in rows
                    if r[0]
                ]
    except Exception:
        pass
    return fallback


def _load_maint_df(engine, tenant_id: str) -> pd.DataFrame:
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT id, maint_date, staff_name, dept_name, equipment_name,
                           COALESCE(hours_worked, 0) AS hours_worked,
                           COALESCE(hourly_rate_vnd, 0) AS hourly_rate_vnd,
                           COALESCE(ot_pay_vnd, 0) AS ot_pay_vnd,
                           COALESCE(submitted_by, '倉庫主管') AS submitted_by,
                           COALESCE(approval_status, '待簽核') AS approval_status,
                           COALESCE(approved_by, '-') AS approved_by,
                           COALESCE(notes, '-') AS notes
                    FROM public.hr_sunday_maint_overtime
                    WHERE tenant_id = :tid
                    ORDER BY maint_date DESC, id DESC
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def get_approved_sunday_ot_by_employee(engine, tenant_id: str = "REETECH_VN", month_prefix: str | None = None) -> dict[str, float]:
    """供人事薪資計算呼叫：回傳已核准的週日設備保養加班費 {emp_name: ot_pay_vnd}"""
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


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    current_user = st.session_state.get("user_name") or "admin"
    today_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
    default_sun = _next_sunday(today_vn)

    st.markdown("### 🔧 週日設備保養簽核與加班費結算（設計／生產部／倉庫）")
    st.caption("登記週日設備保養人員（設計、生產部、倉庫）與時數，經主管簽名核准後，加班費自動回流人事薪資計算。")
    _ensure_sunday_maint_table(engine)

    df = _load_maint_df(engine, tenant_id)
    pending_df = df[df["approval_status"] == "待簽核"] if not df.empty else pd.DataFrame()
    approved_df = df[df["approval_status"] == "已核准"] if not df.empty else pd.DataFrame()

    m1, m2, m3 = st.columns(3)
    m1.metric("待簽核保養紀錄", f"{len(pending_df)} 筆")
    m2.metric("已核准保養加班費合計", f"{_fmt_vnd(approved_df['ot_pay_vnd'].sum() if not approved_df.empty else 0)} ₫")
    m3.metric("待簽核加班費金額", f"{_fmt_vnd(pending_df['ot_pay_vnd'].sum() if not pending_df.empty else 0)} ₫")

    tab_sign, tab_add, tab_payroll_sync = st.tabs([
        "✍️ 保養紀錄與主管簽核",
        "➕ 登記週日設備保養出勤",
        "💵 核准加班費回流薪資明細",
    ])

    with tab_sign:
        if df.empty:
            st.info("目前尚無週日設備保養紀錄，請先至「➕ 登記週日設備保養出勤」新增。")
        else:
            disp = df.copy()
            disp["加班時薪(₫)"] = disp["hourly_rate_vnd"].apply(_fmt_vnd)
            disp["保養加班費(₫)"] = disp["ot_pay_vnd"].apply(_fmt_vnd)
            disp = disp.rename(columns={
                "id": "編號",
                "maint_date": "保養日期(週日)",
                "staff_name": "保養人員",
                "dept_name": "所屬部門",
                "equipment_name": "保養設備",
                "hours_worked": "保養時數",
                "submitted_by": "提報主管",
                "approval_status": "簽核狀態",
                "approved_by": "簽核人",
                "notes": "說明",
            })
            st.dataframe(
                disp[[
                    "編號", "保養日期(週日)", "所屬部門", "保養人員", "保養設備",
                    "保養時數", "加班時薪(₫)", "保養加班費(₫)", "簽核狀態", "提報主管", "簽核人", "說明",
                ]],
                use_container_width=True,
                hide_index=True,
            )

        if not pending_df.empty and engine:
            st.divider()
            st.markdown("#### ✍️ 管理者簽核／核准區")
            p_map = {
                f"#{r['id']}｜{r['maint_date']}｜{r['dept_name']} - {r['staff_name']}｜{r['equipment_name']}（{r['hours_worked']}h / {_fmt_vnd(r['ot_pay_vnd'])} ₫）": int(r["id"])
                for _, r in pending_df.iterrows()
            }
            sel_p = st.selectbox("選擇待簽核的週日保養紀錄", list(p_map.keys()))
            signer_name = st.text_input("簽核人姓名／職稱（代表簽名確認）", value=current_user)
            c_ok, c_no = st.columns(2)
            with c_ok:
                if st.button("✅ 簽名核准並納入薪資加班費", type="primary", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    UPDATE public.hr_sunday_maint_overtime
                                    SET approval_status = '已核准',
                                        approved_by = :aby,
                                        approved_at = CURRENT_TIMESTAMP
                                    WHERE id = :rid
                                """),
                                {"aby": signer_name.strip() or current_user, "rid": p_map[sel_p]},
                            )
                        st.success("✅ 已簽名核准，該筆加班費已納入人事薪資計算。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 簽核失敗：{e}")
            with c_no:
                if st.button("❌ 退回／不核准", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    UPDATE public.hr_sunday_maint_overtime
                                    SET approval_status = '已退回',
                                        approved_by = :aby,
                                        approved_at = CURRENT_TIMESTAMP
                                    WHERE id = :rid
                                """),
                                {"aby": signer_name.strip() or current_user, "rid": p_map[sel_p]},
                            )
                        st.warning("⚠️ 已標記為退回，不會計入薪資加班費。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 操作失敗：{e}")

    with tab_add:
        staff_list = _load_candidate_staff(engine, tenant_id)
        staff_names = [s["emp_name"] for s in staff_list]
        staff_dept_map = {s["emp_name"]: s["dept_name"] for s in staff_list}
        staff_rate_map = {s["emp_name"]: s["ot_hourly_vnd"] for s in staff_list}

        with st.form("form_sunday_maint_add"):
            f1, f2, f3 = st.columns(3)
            with f1:
                maint_date = st.date_input("週日保養日期*", value=default_sun)
                selected_staff = st.selectbox("保養人員（可從人員名冊選或下方自行輸入）", ["（手動輸入人員）"] + staff_names)
                manual_name = st.text_input("手動填寫人員姓名", placeholder="若不在下拉選單請填寫姓名")
            with f2:
                default_dept = staff_dept_map.get(selected_staff, "倉庫")
                dept_opts = ["設計", "生產部", "倉庫", "工程部"]
                dept_name = st.selectbox("所屬部門*", dept_opts, index=dept_opts.index(default_dept) if default_dept in dept_opts else 2)
                equipment_name = st.text_input("保養設備／項目*", placeholder="例：空壓機、配電盤、吊車、貨架設備")
                submitted_by = st.text_input("提報主管（如倉庫主管）", value=current_user)
            with f3:
                hours_worked = st.number_input("保養時數*", min_value=0.5, max_value=24.0, value=8.0, step=0.5)
                default_rate = staff_rate_map.get(selected_staff, 100000.0)
                hourly_rate = st.number_input("加班每小時費率 (VND)*", min_value=0.0, value=float(default_rate), step=10000.0)
                notes = st.text_input("保養內容／簽單備註", placeholder="例：已完成定期保養與潤滑")

            calc_ot = float(hours_worked) * float(hourly_rate)
            st.info(f"💡 試算本筆週日保養加班費：**{_fmt_vnd(calc_ot)} ₫**（{hours_worked} 小時 × {_fmt_vnd(hourly_rate)} ₫/時）")

            if st.form_submit_button("💾 送出週日保養紀錄（待簽核）", type="primary", use_container_width=True):
                final_staff = manual_staff.strip() if selected_staff == "（手動輸入人員）" else (manual_staff.strip() or selected_staff)
                if not final_staff or not equipment_name.strip():
                    st.warning("⚠️ 請填寫保養人員姓名與保養設備。")
                elif not engine:
                    st.error("❌ 尚未連線資料庫。")
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
                                        :tid, :mdate, :sname, :dname, :ename,
                                        :hrs, :hrate, :otpay, :sby,
                                        '待簽核', :nts, CURRENT_TIMESTAMP
                                    )
                                """),
                                {
                                    "tid": tenant_id,
                                    "mdate": maint_date,
                                    "sname": final_staff,
                                    "dname": dept_name,
                                    "ename": equipment_name.strip(),
                                    "hrs": float(hours_worked),
                                    "hrate": float(hourly_rate),
                                    "otpay": float(calc_ot),
                                    "sby": submitted_by.strip() or current_user,
                                    "nts": notes.strip() or None,
                                },
                            )
                        st.success(f"✅ 已建立【{final_staff}】週日保養紀錄（{_fmt_vnd(calc_ot)} ₫），等待簽核。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 儲存失敗：{e}")

    with tab_payroll_sync:
        st.markdown("#### 💵 已核准之週日保養加班費（供人事薪資計算彙整）")
        if approved_df.empty:
            st.info("目前尚無「已核准」的週日設備保養加班費。")
        else:
            agg = (
                approved_df.groupby(["staff_name", "dept_name"], as_index=False)
                .agg(total_hours=("hours_worked", "sum"), total_ot_vnd=("ot_pay_vnd", "sum"), times=("id", "count"))
            )
            agg["保養次數"] = agg["times"].astype(str) + " 次"
            agg["總保養時數"] = agg["total_hours"]
            agg["應計入薪資加班費(₫)"] = agg["total_ot_vnd"].apply(_fmt_vnd)
            st.dataframe(
                agg.rename(columns={"staff_name": "員工姓名", "dept_name": "部門"})[
                    ["部門", "員工姓名", "保養次數", "總保養時數", "應計入薪資加班費(₫)"]
                ],
                use_container_width=True,
                hide_index=True,
            )


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
