# ==========================================
# 檔案路徑：modules/management/hr/employee/labor_contract_management.py
# 職責：L2 行政／人事 - 越南勞動合約建檔、到期提醒與簽約狀態控管（獨立拼圖模組）
# ==========================================

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text


CONTRACT_TYPES = [
    "不定期勞動合約 (HĐLĐ không xác định thời hạn)",
    "定期勞動合約 (HĐLĐ xác định thời hạn)",
    "試用／特定期限合約 (Thử việc / Thời vụ)",
]

CONTRACT_STATUSES = [
    "生效中",
    "即將到期",
    "已到期",
    "已續簽",
    "已終止",
]


def _fmt_vnd(val: float | int) -> str:
    try:
        return f"{round(float(val or 0)):,}".replace(",", ".") + " ₫"
    except Exception:
        return "0 ₫"


def _parse_date(val) -> date | None:
    if not val:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    try:
        return date.fromisoformat(str(val)[:10])
    except Exception:
        return None


def ensure_labor_contract_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS public.hr_labor_contracts (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        contract_no VARCHAR(80) NOT NULL,
                        emp_code VARCHAR(80),
                        emp_name VARCHAR(150) NOT NULL,
                        dept_name VARCHAR(100),
                        position_name VARCHAR(100),
                        contract_type VARCHAR(120) NOT NULL,
                        signed_date DATE,
                        start_date DATE NOT NULL,
                        end_date DATE,
                        agreed_base_salary_vnd NUMERIC(18, 2) DEFAULT 0,
                        work_location VARCHAR(150) DEFAULT 'Tây Ninh, Việt Nam',
                        contract_status VARCHAR(32) DEFAULT '生效中',
                        file_ref VARCHAR(255),
                        notes TEXT,
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def get_unsigned_or_expiring_employees(engine, tenant_id: str = "REETECH_VN", warn_days: int = 30) -> dict[str, list[str]]:
    """
    預留介面：供其他 HR 模組查詢「尚未簽約」與「即將到期／已到期」員工名單
    回傳 {'unsigned': [...], 'expiring_or_expired': [...]}
    """
    out = {"unsigned": [], "expiring_or_expired": []}
    if not engine:
        return out

    today_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
    active_emps: list[str] = []
    contracted_emps: set[str] = set()

    try:
        with engine.connect() as conn:
            e_rows = conn.execute(
                text("""
                    SELECT emp_name
                    FROM public.employee_profiles
                    WHERE COALESCE(status, '在職') <> '離職'
                """)
            ).fetchall()
            active_emps = [str(r[0]).strip() for r in e_rows if r[0]]

            c_rows = conn.execute(
                text("""
                    SELECT emp_name, end_date, COALESCE(contract_status, '生效中') AS cstatus
                    FROM public.hr_labor_contracts
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                """),
                {"tid": tenant_id},
            ).fetchall()

            for r in c_rows:
                ename = str(r[0] or "").strip()
                cstatus = str(r[2] or "生效中")
                if not ename:
                    continue
                if cstatus not in ("已終止",):
                    contracted_emps.add(ename)
                ed = _parse_date(r[1])
                if ed and cstatus in ("生效中", "即將到期"):
                    days_left = (ed - today_vn).days
                    if days_left <= warn_days:
                        tag = f"{ename} (到期:{ed}, 剩餘{days_left}天)" if days_left >= 0 else f"{ename} (已逾期:{ed}, 逾期{abs(days_left)}天)"
                        out["expiring_or_expired"].append(tag)
    except Exception:
        pass

    out["unsigned"] = [n for n in active_emps if n not in contracted_emps]
    return out


def render_labor_contract_panel(engine, tenant_id: str = "REETECH_VN", lang: str = "zh"):
    today_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
    current_user = st.session_state.get("user_name") or "admin"

    st.markdown("### 📄 員工勞動合約管理與簽約合規檢核")
    st.caption("依越南勞動法規管理員工書面合約（簽約日、起迄日、約定底薪與簽約狀態），即時揪出「未簽約」與「即將到期」人員。")

    if not engine:
        st.info("尚未連線資料庫，無法管理勞動合約。")
        return

    ensure_labor_contract_table(engine)

    # 讀取在職員工名冊（含現有底薪供比對）
    emp_list: list[dict] = []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT COALESCE(emp_code, CAST(id AS TEXT)) AS emp_code,
                           emp_name,
                           COALESCE(department, '未指定') AS department,
                           COALESCE(position, '員工') AS position,
                           COALESCE(base_salary, 0) AS base_salary
                    FROM public.employee_profiles
                    WHERE COALESCE(status, '在職') <> '離職'
                    ORDER BY id ASC
                """)
            ).fetchall()
            for r in rows:
                if r[1]:
                    emp_list.append({
                        "emp_code": str(r[0] or "").strip(),
                        "emp_name": str(r[1]).strip(),
                        "department": str(r[2] or "未指定").strip(),
                        "position": str(r[3] or "員工").strip(),
                        "base_salary": float(r[4] or 0.0),
                    })
    except Exception:
        emp_list = []

    emp_names = [e["emp_name"] for e in emp_list]
    emp_map = {e["emp_name"]: e for e in emp_list}

    # 讀取現有合約紀錄
    df_c = pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT id, contract_no, emp_code, emp_name,
                           COALESCE(dept_name, '-') AS dept_name,
                           COALESCE(position_name, '-') AS position_name,
                           contract_type, signed_date, start_date, end_date,
                           COALESCE(agreed_base_salary_vnd, 0) AS agreed_base_salary_vnd,
                           COALESCE(work_location, 'Tây Ninh, Việt Nam') AS work_location,
                           COALESCE(contract_status, '生效中') AS contract_status,
                           COALESCE(file_ref, '-') AS file_ref,
                           COALESCE(notes, '-') AS notes
                    FROM public.hr_labor_contracts
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                    ORDER BY id DESC
                """),
                {"tid": tenant_id},
            ).fetchall()
            if rows:
                df_c = pd.DataFrame([r._asdict() for r in rows])
    except Exception as e:
        st.warning(f"⚠️ 讀取勞動合約紀錄異常：{e}")

    # 計算「尚未簽約」在職員工（合規風險預警）
    active_contracted = set()
    if not df_c.empty:
        active_contracted = {
            str(r["emp_name"]).strip()
            for _, r in df_c.iterrows()
            if str(r.get("contract_status", "生效中")) != "已終止" and str(r.get("emp_name") or "").strip()
        }
    unsigned_emps = [n for n in emp_names if n not in active_contracted]

    # 計算「30天內到期或已逾期」合約
    expiring_alerts: list[str] = []
    if not df_c.empty:
        for _, r in df_c.iterrows():
            st_val = str(r.get("contract_status") or "生效中")
            if st_val not in ("生效中", "即將到期"):
                continue
            ed = _parse_date(r.get("end_date"))
            if ed:
                d_left = (ed - today_vn).days
                if d_left < 0:
                    expiring_alerts.append(f"🔴 **【合約已逾期】** `{r['contract_no']}` - `{r['emp_name']}`（到期日 `{ed}`，逾期 `{abs(d_left)}` 天）")
                elif d_left <= 30:
                    expiring_alerts.append(f"⚠️ **【30天內即將到期】** `{r['contract_no']}` - `{r['emp_name']}`（到期日 `{ed}`，剩餘 `{d_left}` 天）")

    if unsigned_emps:
        st.error(f"🚨 勞動合規提醒：目前有 **{len(unsigned_emps)}** 位在職員工尚無有效勞動合約登記，建議盡速補簽建檔！")
        st.caption("尚未簽約人員：" + "、".join(unsigned_emps[:30]) + (" ..." if len(unsigned_emps) > 30 else ""))

    if expiring_alerts:
        st.warning("⏰ 勞動合約到期預警：")
        for msg in expiring_alerts:
            st.markdown(msg)

    # 頂部指標卡片
    total_active_emp = len(emp_names)
    signed_cnt = len(active_contracted)
    unsigned_cnt = len(unsigned_emps)
    total_contracts = len(df_c) if not df_c.empty else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("在職員工總數", f"{total_active_emp} 人")
    m2.metric("已建立合約人數", f"{signed_cnt} 人")
    m3.metric("尚未簽約人數", f"{unsigned_cnt} 人")
    m4.metric("歷史／現有合約筆數", f"{total_contracts} 份")

    # 新增勞動合約表單
    with st.expander("➕ 新增／簽訂員工勞動合約", expanded=True):
        with st.form("form_add_labor_contract"):
            c1, c2, c3 = st.columns(3)
            with c1:
                sel_emp = st.selectbox("選擇員工*", emp_names if emp_names else ["（尚無在職員工資料）"], key="lc_sel_emp")
                emp_info = emp_map.get(sel_emp, {})
                dept_val = emp_info.get("department", "未指定")
                pos_val = emp_info.get("position", "員工")
                emp_sal_val = float(emp_info.get("base_salary", 0.0))

                st.text_input("部門／職稱", value=f"{dept_val} / {pos_val}", disabled=True, key="lc_dept_pos")
                default_cno = f"HDLD-{today_vn.strftime('%Y%m%d')}-{str(emp_info.get('emp_code') or '001')[-4:]}"
                contract_no = st.text_input("合約編號*", value=default_cno, key="lc_cno_input")
            with c2:
                ctype = st.selectbox("合約類型*", CONTRACT_TYPES, key="lc_ctype_sel")
                signed_dt = st.date_input("簽約日期*", value=today_vn, key="lc_signed_dt")
                start_dt = st.date_input("合約生效日*", value=today_vn, key="lc_start_dt")
            with c3:
                has_end_date = st.checkbox("設定合約到期日（定期／試用合約請勾選）", value=True, key="lc_has_end")
                end_dt = st.date_input("合約到期日", value=start_dt + timedelta(days=365), key="lc_end_dt") if has_end_date else None
                agreed_sal = st.number_input(
                    "合約約定基本薪資 (VND/月)*",
                    min_value=0.0,
                    value=emp_sal_val,
                    step=100000.0,
                    key="lc_agreed_sal",
                )

            c_b1, c_b2, c_b3 = st.columns([2, 2, 2])
            with c_b1:
                work_loc = st.text_input("主要工作地點", value="Tây Ninh, Việt Nam", key="lc_work_loc")
            with c_b2:
                file_ref = st.text_input("紙本／掃描檔編號或連結", placeholder="例：SCAN-2026-11-01.pdf", key="lc_file_ref")
            with c_b3:
                notes_txt = st.text_input("備註", placeholder="例：含試用期約定、薪資調整說明", key="lc_notes_txt")

            if emp_sal_val > 0 and agreed_sal > 0 and abs(float(agreed_sal) - emp_sal_val) > 0:
                st.caption(f"💡 員工名冊現有底薪為 **{_fmt_vnd(emp_sal_val)}**，與本次合約約定底薪 **{_fmt_vnd(agreed_sal)}** 有差異，核對後可同步。")

            if st.form_submit_button("💾 儲存勞動合約紀錄", type="primary", use_container_width=True):
                if not emp_names or not sel_emp:
                    st.warning("⚠️ 請先確認員工名冊已有資料。")
                elif not contract_no.strip():
                    st.warning("⚠️ 請填寫合約編號。")
                elif end_dt and end_dt < start_dt:
                    st.warning("⚠️ 合約到期日不可早於合約生效日。")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO public.hr_labor_contracts (
                                        tenant_id, contract_no, emp_code, emp_name,
                                        dept_name, position_name, contract_type,
                                        signed_date, start_date, end_date,
                                        agreed_base_salary_vnd, work_location,
                                        contract_status, file_ref, notes,
                                        created_by, created_at, updated_at
                                    )
                                    VALUES (
                                        :tid, :cno, :ecode, :ename,
                                        :dname, :pname, :ctype,
                                        :sdt, :st_dt, :ed_dt,
                                        :asal, :wloc,
                                        '生效中', :fref, :notes,
                                        :cby, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                                    )
                                """),
                                {
                                    "tid": tenant_id,
                                    "cno": contract_no.strip(),
                                    "ecode": emp_info.get("emp_code"),
                                    "ename": sel_emp,
                                    "dname": dept_val,
                                    "pname": pos_val,
                                    "ctype": ctype,
                                    "sdt": signed_dt,
                                    "st_dt": start_dt,
                                    "ed_dt": end_dt,
                                    "asal": float(agreed_sal),
                                    "wloc": work_loc.strip() or "Tây Ninh, Việt Nam",
                                    "fref": file_ref.strip() or None,
                                    "notes": notes_txt.strip() or None,
                                    "cby": current_user,
                                },
                            )
                        st.success(f"✅ 已建立【{sel_emp}】的勞動合約（編號：{contract_no.strip()}）。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 儲存勞動合約失敗：{e}")

    # 合約清冊查詢與狀態更新
    st.markdown("---")
    st.markdown("#### 📋 員工勞動合約清冊")

    if df_c.empty:
        st.info("目前尚未建立任何員工勞動合約紀錄。")
        return

    search_kw = st.text_input("🔍 搜尋員工姓名、工號、合約編號或部門", placeholder="輸入關鍵字篩選...", key="lc_search_kw")
    df_view = df_c.copy()
    if search_kw and search_kw.strip():
        kw = search_kw.strip().lower()
        mask = df_view.astype(str).apply(lambda s: s.str.lower().str.contains(kw, na=False)).any(axis=1)
        df_view = df_view[mask]

    df_view["約定底薪"] = df_view["agreed_base_salary_vnd"].apply(_fmt_vnd)
    df_view["到期日顯示"] = df_view["end_date"].apply(lambda d: str(d)[:10] if d else "無期限")

    disp_cols = [
        "id", "contract_no", "emp_code", "emp_name", "dept_name",
        "position_name", "contract_type", "signed_date", "start_date",
        "到期日顯示", "約定底薪", "contract_status", "file_ref", "notes",
    ]
    st.dataframe(
        df_view[disp_cols].rename(columns={
            "id": "編號",
            "contract_no": "合約編號",
            "emp_code": "工號",
            "emp_name": "員工姓名",
            "dept_name": "部門",
            "position_name": "職稱",
            "contract_type": "合約類型",
            "signed_date": "簽約日",
            "start_date": "生效日",
            "到期日顯示": "到期日",
            "contract_status": "合約狀態",
            "file_ref": "檔案編號",
            "notes": "備註",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # 更新既有合約狀態（續簽／終止／到期）
    st.markdown("##### 🔄 合約狀態變更（續簽／終止／註記）")
    c_opts = {
        f"#{r['id']}｜{r['contract_no']}｜{r['emp_name']}（目前：{r['contract_status']}）": int(r["id"])
        for _, r in df_c.iterrows()
    }
    u1, u2, u3 = st.columns([3, 2, 1.5])
    with u1:
        sel_cid = st.selectbox("選擇合約紀錄", list(c_opts.keys()), key="lc_upd_sel")
    with u2:
        new_st = st.selectbox("更新狀態", CONTRACT_STATUSES, key="lc_upd_status")
    with u3:
        st.write("")
        if st.button("更新狀態", type="secondary", use_container_width=True, key="btn_lc_upd"):
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            UPDATE public.hr_labor_contracts
                            SET contract_status = :cst, updated_at = CURRENT_TIMESTAMP
                            WHERE id = :cid
                        """),
                        {"cst": new_st, "cid": c_opts[sel_cid]},
                    )
                st.success("✅ 已更新合約狀態。")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 更新狀態失敗：{e}")


def render(engine=None, lang="zh", **kwargs):
    tid = st.session_state.get("tenant_id", "REETECH_VN")
    cur_lang = lang or st.session_state.get("current_lang", "zh")
    render_labor_contract_panel(engine=engine, tenant_id=tid, lang=cur_lang)


def show(engine=None, lang="zh", **kwargs):
    return render(engine=engine, lang=lang, **kwargs)
