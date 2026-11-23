# ==========================================
# 檔案路徑：modules/management/hr/employee/child_education_subsidy.py
# 職責：L2 行政／人事 - 員工子女登記、年齡自動計算與學費補助申請審核（獨立模組）
# ==========================================

from datetime import date, datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text


SCHOOL_STAGES = [
    "學齡前 / 幼兒園 (Mầm non)",
    "國小 (Tiểu học)",
    "國中 (Trung học cơ sở)",
    "高中 (Trung học phổ thông)",
    "大專院校 / 其他 (Đại học / Khác)",
]


def _fmt_vnd(val: float | int) -> str:
    try:
        return f"{round(float(val or 0)):,}".replace(",", ".") + " ₫"
    except Exception:
        return "0 ₫"


def _calc_age(birth_date_val, ref_date: date) -> int:
    if not birth_date_val:
        return 0
    try:
        if isinstance(birth_date_val, str):
            b_date = date.fromisoformat(birth_date_val[:10])
        elif isinstance(birth_date_val, datetime):
            b_date = birth_date_val.date()
        else:
            b_date = birth_date_val
        age = ref_date.year - b_date.year - ((ref_date.month, ref_date.day) < (b_date.month, b_date.day))
        return max(0, age)
    except Exception:
        return 0


def ensure_child_subsidy_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS public.hr_employee_children (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        emp_code VARCHAR(80),
                        emp_name VARCHAR(150) NOT NULL,
                        dept_name VARCHAR(100),
                        has_children BOOLEAN DEFAULT TRUE,
                        child_name VARCHAR(150) NOT NULL,
                        birth_date DATE NOT NULL,
                        school_stage VARCHAR(100),
                        school_name VARCHAR(200),
                        tuition_fee_vnd NUMERIC(18, 2) DEFAULT 0,
                        requested_subsidy_vnd NUMERIC(18, 2) DEFAULT 0,
                        is_tax_dependent BOOLEAN DEFAULT FALSE,
                        approval_status VARCHAR(32) DEFAULT '待審核',
                        approved_by VARCHAR(100),
                        approved_at TIMESTAMP WITH TIME ZONE,
                        notes TEXT,
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def get_approved_child_subsidy_by_employee(engine, tenant_id: str = "REETECH_VN") -> dict[str, float]:
    """預留介面：供薪資模組查詢每位員工已核准的子女學費補助金額 {emp_name: total_subsidy_vnd}"""
    result: dict[str, float] = {}
    if not engine:
        return result
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT emp_name, COALESCE(SUM(requested_subsidy_vnd), 0) AS total_sub
                    FROM public.hr_employee_children
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                      AND approval_status = '已核准'
                    GROUP BY emp_name
                """),
                {"tid": tenant_id},
            ).fetchall()
            for r in rows:
                ename = str(r[0] or "").strip()
                if ename:
                    result[ename] = float(r[1] or 0.0)
    except Exception:
        pass
    return result


def render_child_education_subsidy_panel(engine, tenant_id: str = "REETECH_VN", lang: str = "zh"):
    today_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
    current_user = st.session_state.get("user_name") or "admin"

    st.markdown("### 🎓 員工子女登記與就學學費補助申請")
    st.caption("登記同仁子女出生年月（系統自動計算實歲）、就讀階段與實際學費金額，作為公司申請福利補助與扶養扣除額依據。")

    if not engine:
        st.info("尚未連線資料庫，無法儲存子女與學費補助資料。")
        return

    ensure_child_subsidy_table(engine)

    # 讀取在職員工名冊
    emp_list: list[dict] = []
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
            emp_list = [{"emp_code": r[0], "emp_name": str(r[1]).strip(), "department": str(r[2]).strip()} for r in rows if r[1]]
    except Exception:
        emp_list = []

    emp_names = [e["emp_name"] for e in emp_list]
    emp_code_map = {e["emp_name"]: e["emp_code"] for e in emp_list}
    emp_dept_map = {e["emp_name"]: e["department"] for e in emp_list}

    with st.expander("➕ 新增／登記員工子女與學費明細", expanded=True):
        with st.form("form_register_child_subsidy"):
            c1, c2, c3 = st.columns(3)
            with c1:
                sel_emp = st.selectbox("選擇員工姓名*", emp_names if emp_names else ["（尚無在職員工資料）"], key="ch_sel_emp")
                dept_disp = emp_dept_map.get(sel_emp, "未指定")
                st.text_input("所屬部門", value=dept_disp, disabled=True, key="ch_dept_disp")
                child_name = st.text_input("子女姓名*", placeholder="例：Nguyễn Minh Anh", key="ch_name_input")
            with c2:
                birth_dt = st.date_input(
                    "子女出生年月日（自動算年齡）*",
                    value=date(today_vn.year - 6, 1, 1),
                    min_value=date(1995, 1, 1),
                    max_value=today_vn,
                    key="ch_birth_input",
                )
                calc_age = _calc_age(birth_dt, today_vn)
                st.info(f"目前實歲計算：**{calc_age} 歲**")
                school_stage = st.selectbox("就讀階段*", SCHOOL_STAGES, index=1, key="ch_stage_sel")
            with c3:
                school_name = st.text_input("就讀學校名稱", placeholder="例：Trường Tiểu học An Tịnh", key="ch_school_input")
                tuition_vnd = st.number_input("實際學費金額 (VND/學期或月)*", min_value=0.0, value=0.0, step=100000.0, key="ch_tuition_num")
                subsidy_vnd = st.number_input("申請補助金額 (VND)*", min_value=0.0, value=0.0, step=100000.0, key="ch_subsidy_num")

            c_sub1, c_sub2 = st.columns([2, 3])
            with c_sub1:
                is_tax_dep = st.checkbox("同時登記為越南個人所得稅扶養親屬", value=True, key="ch_tax_dep")
            with c_sub2:
                notes_txt = st.text_input("備註／繳費單據說明", placeholder="例：已附學校繳費通知單", key="ch_notes_txt")

            if st.form_submit_button("💾 送出子女與學費補助登記", type="primary", use_container_width=True):
                if not emp_names or not sel_emp:
                    st.warning("⚠️ 請先確認員工名冊已有資料。")
                elif not child_name.strip():
                    st.warning("⚠️ 請填寫子女姓名。")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO public.hr_employee_children (
                                        tenant_id, emp_code, emp_name, dept_name, has_children,
                                        child_name, birth_date, school_stage, school_name,
                                        tuition_fee_vnd, requested_subsidy_vnd, is_tax_dependent,
                                        approval_status, notes, created_by, created_at
                                    )
                                    VALUES (
                                        :tid, :ecode, :ename, :dname, TRUE,
                                        :cname, :bdate, :stage, :sname,
                                        :tuition, :sub, :taxdep,
                                        '待審核', :notes, :cby, CURRENT_TIMESTAMP
                                    )
                                """),
                                {
                                    "tid": tenant_id,
                                    "ecode": emp_code_map.get(sel_emp),
                                    "ename": sel_emp,
                                    "dname": dept_disp,
                                    "cname": child_name.strip(),
                                    "bdate": birth_dt,
                                    "stage": school_stage,
                                    "sname": school_name.strip() or None,
                                    "tuition": float(tuition_vnd),
                                    "sub": float(subsidy_vnd),
                                    "taxdep": bool(is_tax_dep),
                                    "notes": notes_txt.strip() or None,
                                    "cby": current_user,
                                },
                            )
                        st.success(f"✅ 已完成登記：【{sel_emp}】子女「{child_name.strip()}」（{calc_age} 歲），學費 {_fmt_vnd(tuition_vnd)}。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 儲存失敗：{e}")

    # 讀取全公司已登記子女清冊與統計
    df_ch = pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT id, emp_code, emp_name, COALESCE(dept_name, '-') AS dept_name,
                           child_name, birth_date, COALESCE(school_stage, '-') AS school_stage,
                           COALESCE(school_name, '-') AS school_name,
                           COALESCE(tuition_fee_vnd, 0) AS tuition_fee_vnd,
                           COALESCE(requested_subsidy_vnd, 0) AS requested_subsidy_vnd,
                           COALESCE(is_tax_dependent, FALSE) AS is_tax_dependent,
                           COALESCE(approval_status, '待審核') AS approval_status,
                           COALESCE(notes, '-') AS notes
                    FROM public.hr_employee_children
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                    ORDER BY emp_name ASC, birth_date ASC
                """),
                {"tid": tenant_id},
            ).fetchall()
            if rows:
                df_ch = pd.DataFrame([r._asdict() for r in rows])
    except Exception as e:
        st.warning(f"⚠️ 讀取子女登記清冊異常：{e}")

    if df_ch.empty:
        st.info("目前尚未有員工登記子女與學費資料。")
        return

    df_ch["實歲"] = df_ch["birth_date"].apply(lambda d: f"{_calc_age(d, today_vn)} 歲")
    df_ch["學費金額"] = df_ch["tuition_fee_vnd"].apply(_fmt_vnd)
    df_ch["申請補助"] = df_ch["requested_subsidy_vnd"].apply(_fmt_vnd)
    df_ch["稅務扶養"] = df_ch["is_tax_dependent"].apply(lambda x: "✅ 是" if x else "否")

    # 頂部統計指標（方便向管理層彙報總預算需求）
    total_parents = df_ch["emp_name"].nunique()
    total_kids = len(df_ch)
    total_tuition = float(df_ch["tuition_fee_vnd"].sum())
    total_req_sub = float(df_ch["requested_subsidy_vnd"].sum())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("有子女申請員工人數", f"{total_parents} 人")
    m2.metric("登記子女總人數", f"{total_kids} 名")
    m3.metric("申報學費總金額", _fmt_vnd(total_tuition))
    m4.metric("申請補助預算總計", _fmt_vnd(total_req_sub))

    st.markdown("#### 📋 全公司員工子女與學費補助清冊")
    disp_cols = [
        "id", "emp_code", "emp_name", "dept_name", "child_name",
        "birth_date", "實歲", "school_stage", "school_name",
        "學費金額", "申請補助", "稅務扶養", "approval_status", "notes",
    ]
    st.dataframe(
        df_ch[disp_cols].rename(columns={
            "id": "編號",
            "emp_code": "工號",
            "emp_name": "員工姓名",
            "dept_name": "部門",
            "child_name": "子女姓名",
            "birth_date": "出生日期",
            "school_stage": "就讀階段",
            "school_name": "學校名稱",
            "approval_status": "審核狀態",
            "notes": "備註",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # 匯出清冊（方便呈報總經理室或財務部評估預算）
    csv_export = df_ch[disp_cols].to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 匯出員工子女學費補助統計清冊 (CSV)",
        data=csv_export,
        file_name=f"REETECH_Child_Education_Subsidy_{today_vn.strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

    # 主管審核與一鍵拋轉當月薪資津貼
    st.divider()
    st.markdown("#### ✅ 主管審核與連動薪資津貼發放")
    pending_df = df_ch[df_ch["approval_status"] == "待審核"]
    if not pending_df.empty:
        p_opts = {
            f"#{r['id']}｜{r['emp_name']}｜子女:{r['child_name']}({r['實歲']})｜補助:{_fmt_vnd(r['requested_subsidy_vnd'])}": int(r["id"])
            for _, r in pending_df.iterrows()
        }
        sel_pid = st.selectbox("選擇待審核申請單", list(p_opts.keys()), key="ch_pending_sel")
        b_app, b_rej = st.columns(2)
        if b_app.button("✅ 核准補助申請", type="primary", use_container_width=True, key="btn_ch_approve"):
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE public.hr_employee_children
                        SET approval_status = '已核准', approved_by = :ab, approved_at = CURRENT_TIMESTAMP
                        WHERE id = :rid
                    """),
                    {"ab": current_user, "rid": p_opts[sel_pid]},
                )
            st.success("✅ 已核准該筆子女學費補助。")
            st.rerun()
        if b_rej.button("❌ 退回申請", use_container_width=True, key="btn_ch_reject"):
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE public.hr_employee_children
                        SET approval_status = '已退回', approved_by = :ab, approved_at = CURRENT_TIMESTAMP
                        WHERE id = :rid
                    """),
                    {"ab": current_user, "rid": p_opts[sel_pid]},
                )
            st.warning("⚠️ 已退回申請。")
            st.rerun()

    approved_df = df_ch[df_ch["approval_status"] == "已核准"]
    if not approved_df.empty:
        st.caption("已核准的學費補助，可一鍵寫入指定月份的「員工津貼表（其他津貼）」，自動併入當月薪資發放。")
        c_sync1, c_sync2 = st.columns([1.5, 2.5])
        with c_sync1:
            target_pay_month = st.text_input("發放計薪月份 (YYYY-MM)", value=today_vn.strftime("%Y-%m"), max_chars=7, key="ch_sync_month")
        with c_sync2:
            st.write("")
            if st.button("📤 將已核准學費補助轉入當月薪資津貼", use_container_width=True, key="btn_ch_sync_allowance"):
                try:
                    from modules.management.hr.payroll.payroll_allowances import ensure_allowance_table

                    ensure_allowance_table(engine)
                    clean_pm = (target_pay_month or "").strip() or today_vn.strftime("%Y-%m")
                    grouped = approved_df.groupby(["emp_code", "emp_name", "dept_name"], as_index=False)["requested_subsidy_vnd"].sum()
                    with engine.begin() as conn:
                        # 先清除同月份已轉入的子女學費補助，防止重複按按鈕導致金額加倍
                        conn.execute(
                            text("""
                                DELETE FROM public.hr_employee_allowances
                                WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                                  AND pay_month = :pm
                                  AND allowance_type = '其他津貼'
                                  AND reason LIKE '【子女學費補助】%'
                            """),
                            {"tid": tenant_id, "pm": clean_pm},
                        )
                        for _, gr in grouped.iterrows():
                            sub_amt = float(gr["requested_subsidy_vnd"] or 0.0)
                            if sub_amt <= 0:
                                continue
                            conn.execute(
                                text("""
                                    INSERT INTO public.hr_employee_allowances (
                                        tenant_id, pay_month, emp_code, emp_name, dept_name,
                                        allowance_type, amount_vnd, reason, created_by, created_at
                                    )
                                    VALUES (
                                        :tid, :pm, :ecode, :ename, :dname,
                                        '其他津貼', :amt, :rsn, :cby, CURRENT_TIMESTAMP
                                    )
                                """),
                                {
                                    "tid": tenant_id,
                                    "pm": clean_pm,
                                    "ecode": gr["emp_code"],
                                    "ename": gr["emp_name"],
                                    "dname": gr["dept_name"],
                                    "amt": sub_amt,
                                    "rsn": f"【子女學費補助】{clean_pm} 核准發放",
                                    "cby": current_user,
                                },
                            )
                    st.success(f"✅ 已將 {len(grouped)} 位員工的核准學費補助轉入【{clean_pm}】薪資津貼，請至薪資計算頁檢視。")
                except Exception as e:
                    st.error(f"❌ 轉入薪資津貼失敗：{e}")


def render(engine=None, lang="zh", **kwargs):
    tid = st.session_state.get("tenant_id", "REETECH_VN")
    cur_lang = lang or st.session_state.get("current_lang", "zh")
    render_child_education_subsidy_panel(engine=engine, tenant_id=tid, lang=cur_lang)


def show(engine=None, lang="zh", **kwargs):
    return render(engine=engine, lang=lang, **kwargs)
