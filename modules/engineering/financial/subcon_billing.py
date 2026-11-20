# ==========================================
# 檔案路徑：modules/engineering/financial/subcon_billing.py
# 職責：工程部 - 外包估驗與臨時工／點工逐人出工、表現調薪登記（串接人事薪資計算）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _fmt_vnd(val: float | int) -> str:
    return f"{round(float(val or 0)):,}".replace(",", ".")


def _ensure_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS eng_subcon_valuations (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        val_no VARCHAR(64) UNIQUE NOT NULL,
                        project_id VARCHAR(80),
                        site_name VARCHAR(160) NOT NULL,
                        subcon_company VARCHAR(160) NOT NULL,
                        work_scope VARCHAR(200) NOT NULL,
                        qty_or_pct NUMERIC(10, 2) NOT NULL,
                        unit_rate_vnd NUMERIC(18, 2) NOT NULL,
                        total_amount_vnd NUMERIC(18, 2) NOT NULL,
                        status VARCHAR(32) DEFAULT 'SUBMITTED',
                        po_id VARCHAR(80),
                        ap_invoice_id VARCHAR(80),
                        notes TEXT,
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
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


def _load_valuations(engine, tenant_id: str) -> pd.DataFrame:
    fallback = [
        {
            "val_no": "VAL-202611-01",
            "project_id": "PRJ-2026-01",
            "site_name": "西寧廠二期配電盤擴建",
            "subcon_company": "Công Ty TNHH Cơ Điện Tây Ninh",
            "work_scope": "主幹線電纜橋架安裝第一期估驗 (40%)",
            "qty_or_pct": 1.0,
            "unit_rate_vnd": 45000000.0,
            "total_amount_vnd": 45000000.0,
            "status": "SUBMITTED",
            "notes": "待工程主管確認估驗比例後轉 AP",
        }
    ]
    if not engine:
        return pd.DataFrame(fallback)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT val_no, COALESCE(project_id, '-') AS project_id, site_name,
                           subcon_company, work_scope, qty_or_pct, unit_rate_vnd,
                           total_amount_vnd, status, COALESCE(notes, '-') AS notes
                    FROM eng_subcon_valuations
                    WHERE tenant_id = :tid
                    ORDER BY id DESC LIMIT 40
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame(fallback)
    except Exception:
        return pd.DataFrame(fallback)


def _load_daily_workers(engine, tenant_id: str) -> pd.DataFrame:
    fallback = [
        {
            "log_no": "DW-20261120-01",
            "project_id": "PRJ-2026-01",
            "site_name": "西寧廠二期配電盤擴建",
            "worker_name": "Trần Văn Nam",
            "worker_role": "點工電工",
            "work_date": "2026-11-20",
            "work_days": 1.0,
            "base_daily_rate_vnd": 500000.0,
            "rate_adj_vnd": 50000.0,
            "effective_rate_vnd": 550000.0,
            "total_amount_vnd": 550000.0,
            "performance_rating": "GOOD_UP",
            "performance_note": "配線速度快、施工整齊，日薪調升 +50.000 ₫",
            "payroll_status": "PENDING_PAYROLL",
        },
        {
            "log_no": "DW-20261120-02",
            "project_id": "PRJ-2026-01",
            "site_name": "西寧廠二期配電盤擴建",
            "worker_name": "Lê Hoàng Phúc",
            "worker_role": "臨時雜工",
            "work_date": "2026-11-20",
            "work_days": 1.0,
            "base_daily_rate_vnd": 400000.0,
            "rate_adj_vnd": -50000.0,
            "effective_rate_vnd": 350000.0,
            "total_amount_vnd": 350000.0,
            "performance_rating": "POOR_DOWN",
            "performance_note": "遲到且需重工整理，日薪調降 -50.000 ₫",
            "payroll_status": "PENDING_PAYROLL",
        },
    ]
    if not engine:
        return pd.DataFrame(fallback)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT log_no, COALESCE(project_id, '-') AS project_id, site_name,
                           worker_name, COALESCE(worker_role, '點工') AS worker_role,
                           TO_CHAR(work_date, 'YYYY-MM-DD') AS work_date,
                           work_days, base_daily_rate_vnd, rate_adj_vnd,
                           effective_rate_vnd, total_amount_vnd,
                           performance_rating, COALESCE(performance_note, '-') AS performance_note,
                           payroll_status
                    FROM hr_daily_worker_logs
                    WHERE tenant_id = :tid
                    ORDER BY id DESC LIMIT 60
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame(fallback)
    except Exception:
        return pd.DataFrame(fallback)


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "Eng_Ops"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 👷 外包估驗與臨時工／點工出工登記")
    st.caption("臨時工／點工採「逐人記名＋表現調薪／調降」登記，並同步送往「管理部 ➡️ 自動化薪資計算」結算；外包估驗則保留於工程／財務請款。")
    _ensure_tables(engine)

    mode = st.radio(
        "選擇作業區塊",
        ["DAILY_WORKER", "SUBCON_VAL"],
        format_func=lambda x: "🙋 臨時工／點工逐人出工與表現調薪（串接人事薪資）" if x == "DAILY_WORKER" else "📄 外包商工程估驗（串接採購／財務 AP）",
        horizontal=True,
    )

    if mode == "DAILY_WORKER":
        df_w = _load_daily_workers(engine, tenant_id)
        c1, c2, c3 = st.columns(3)
        c1.metric("點工出工筆數", f"{len(df_w)} 筆")
        c2.metric("待發薪資合計", f"{_fmt_vnd(df_w[df_w['payroll_status'] == 'PENDING_PAYROLL']['total_amount_vnd'].sum() if not df_w.empty else 0)} ₫")
        c3.metric("調薪／調降紀錄", f"{int((df_w['rate_adj_vnd'] != 0).sum()) if not df_w.empty else 0} 筆")

        if not df_w.empty:
            disp_w = df_w.copy()
            for col in ["base_daily_rate_vnd", "rate_adj_vnd", "effective_rate_vnd", "total_amount_vnd"]:
                disp_w[col] = disp_w[col].apply(_fmt_vnd)
            disp_w = disp_w.rename(columns={
                "log_no": "出工單號", "project_id": "專案", "site_name": "案場",
                "worker_name": "點工姓名", "worker_role": "工種", "work_date": "出工日期",
                "work_days": "工天", "base_daily_rate_vnd": "基準日薪(₫)",
                "rate_adj_vnd": "表現調整(₫)", "effective_rate_vnd": "核定日薪(₫)",
                "total_amount_vnd": "應付小計(₫)", "performance_rating": "表現評等",
                "performance_note": "表現與調薪說明", "payroll_status": "薪資狀態",
            })
            st.dataframe(disp_w, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### ➕ 逐人登記臨時工／點工出工與表現日薪調整")
        with st.form("form_daily_worker_individual"):
            f1, f2, f3 = st.columns(3)
            with f1:
                worker_name = st.text_input("點工／臨時工姓名*", placeholder="例：Nguyễn Văn An（務必填寫個人姓名）")
                worker_role = st.selectbox("工種／職稱", ["點工電工", "臨時雜工", "焊接／配管點工", "搬運／輔助點工"])
                work_date = st.date_input("出工日期*", value=now_vn.date())
            with f2:
                pid = st.text_input("專案編號 (project_id)", value=st.session_state.get("active_project_id") or "PRJ-2026-01")
                sname = st.text_input("工地／案場名稱*", value="西寧廠二期配電盤擴建")
                work_days = st.number_input("出工天數（可填 0.5 半天）*", min_value=0.5, max_value=31.0, value=1.0, step=0.5)
            with f3:
                base_rate = st.number_input("基準日薪 (VND)*", min_value=0.0, value=450000.0, step=50000.0)
                perf_rating = st.selectbox(
                    "當日工作表現評等*",
                    [
                        ("NORMAL", "⚖️ 表現正常（維持基準日薪）"),
                        ("GOOD_UP", "⬆️ 表現優良（日薪調升）"),
                        ("POOR_DOWN", "⬇️ 表現不佳（日薪調降）"),
                    ],
                    format_func=lambda x: x[1],
                )[0]
                rate_adj = st.number_input(
                    "日薪調整額 (VND，調升填正數、調降填負數)",
                    min_value=-500000.0,
                    max_value=500000.0,
                    value=0.0,
                    step=10000.0,
                )

            perf_note = st.text_input("表現與調薪／調降原因*", placeholder="例：獨立完成盤內配線且零缺失，調升 +50.000 ₫；或遲到／返工調降 -50.000 ₫")

            eff_rate = float(base_rate) + float(rate_adj)
            tot_amt = float(work_days) * eff_rate
            st.info(f"💵 核定日薪：**{_fmt_vnd(eff_rate)} ₫/天**（基準 {_fmt_vnd(base_rate)} ₫ ＋ 調整 {_fmt_vnd(rate_adj)} ₫）｜本次應付：**{_fmt_vnd(tot_amt)} ₫**")

            if st.form_submit_button("💾 儲存點工出工並送交人事薪資計算", type="primary", use_container_width=True):
                if not worker_name.strip() or not sname.strip() or not perf_note.strip():
                    st.warning("⚠️ 請填寫點工姓名、案場名稱與表現／調薪說明。")
                elif eff_rate < 0:
                    st.warning("⚠️ 核定日薪不可小於 0。")
                elif not engine:
                    st.error("❌ 尚未連線資料庫。")
                else:
                    lno = f"DW-{now_vn.strftime('%Y%m%d-%H%M%S')}"
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO hr_daily_worker_logs (
                                        tenant_id, log_no, project_id, site_name,
                                        worker_name, worker_role, work_date, work_days,
                                        base_daily_rate_vnd, rate_adj_vnd, effective_rate_vnd,
                                        total_amount_vnd, performance_rating, performance_note,
                                        payroll_status, created_by, created_at
                                    )
                                    VALUES (
                                        :tid, :lno, :pid, :sname,
                                        :wname, :wrole, :wdate, :wdays,
                                        :brate, :radj, :erate,
                                        :tamt, :prating, :pnote,
                                        'PENDING_PAYROLL', :cby, :cat
                                    )
                                """),
                                {
                                    "tid": tenant_id, "lno": lno, "pid": pid.strip() or None, "sname": sname.strip(),
                                    "wname": worker_name.strip(), "wrole": worker_role, "wdate": work_date,
                                    "wdays": float(work_days), "brate": float(base_rate), "radj": float(rate_adj),
                                    "erate": eff_rate, "tamt": tot_amt, "prating": perf_rating,
                                    "pnote": perf_note.strip(), "cby": user_name, "cat": now_vn,
                                },
                            )
                        st.success(f"✅ 已登記【{worker_name.strip()}】出工單 `{lno}`（應付 {_fmt_vnd(tot_amt)} ₫），已同步至人事薪資計算待結算清單。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 儲存點工紀錄失敗：{e}")

    else:
        df_v = _load_valuations(engine, tenant_id)
        if not df_v.empty:
            disp_v = df_v.copy()
            disp_v["單價(₫)"] = disp_v["unit_rate_vnd"].apply(_fmt_vnd)
            disp_v["估驗總額(₫)"] = disp_v["total_amount_vnd"].apply(_fmt_vnd)
            disp_v = disp_v.rename(columns={
                "val_no": "估驗單號", "project_id": "專案", "site_name": "案場",
                "subcon_company": "外包公司", "work_scope": "估驗項目",
                "qty_or_pct": "期數/比例", "status": "狀態", "notes": "備註",
            })
            st.dataframe(disp_v[["估驗單號", "專案", "案場", "外包公司", "估驗項目", "期數/比例", "單價(₫)", "估驗總額(₫)", "狀態", "備註"]], use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### ➕ 新增外包商工程估驗單")
        with st.form("form_subcon_valuation"):
            v1, v2 = st.columns(2)
            with v1:
                pid = st.text_input("專案編號 (project_id)", value=st.session_state.get("active_project_id") or "PRJ-2026-01")
                sname = st.text_input("工地／案場名稱*", value="西寧廠二期配電盤擴建")
                subcon_co = st.text_input("外包公司名稱*", placeholder="例：Công Ty TNHH Cơ Điện...")
            with v2:
                wscope = st.text_input("估驗工程部位／項目*", placeholder="例：主幹線電纜橋架安裝第一期估驗")
                qval = st.number_input("估驗數量／期數*", min_value=0.1, value=1.0, step=0.1)
                urate = st.number_input("估驗單價 (VND)*", min_value=0.0, value=10000000.0, step=500000.0)
            notes = st.text_area("驗收／計價說明", placeholder="例：已依現場進度核對")
            est_amt = float(qval) * float(urate)
            st.info(f"💰 估驗金額：**{_fmt_vnd(est_amt)} ₫**")

            if st.form_submit_button("💾 建立外包估驗單", type="primary", use_container_width=True):
                if not sname.strip() or not subcon_co.strip() or not wscope.strip():
                    st.warning("⚠️ 請填寫案場、外包公司與估驗項目。")
                elif not engine:
                    st.error("❌ 尚未連線資料庫。")
                else:
                    vno = f"VAL-{now_vn.strftime('%Y%m%d-%H%M%S')}"
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO eng_subcon_valuations (
                                        tenant_id, val_no, project_id, site_name,
                                        subcon_company, work_scope, qty_or_pct,
                                        unit_rate_vnd, total_amount_vnd, status, notes, created_by, created_at
                                    )
                                    VALUES (
                                        :tid, :vno, :pid, :sname,
                                        :sco, :wscope, :qval,
                                        :urate, :tamt, 'SUBMITTED', :notes, :cby, :cat
                                    )
                                """),
                                {
                                    "tid": tenant_id, "vno": vno, "pid": pid.strip() or None,
                                    "sname": sname.strip(), "sco": subcon_co.strip(), "wscope": wscope.strip(),
                                    "qval": float(qval), "urate": float(urate), "tamt": est_amt,
                                    "notes": notes.strip() or None, "cby": user_name, "cat": now_vn,
                                },
                            )
                        st.success(f"✅ 已建立外包估驗單 `{vno}`（{_fmt_vnd(est_amt)} ₫）。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 建立失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
