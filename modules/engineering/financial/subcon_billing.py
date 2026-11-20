# ==========================================
# 檔案路徑：modules/engineering/financial/subcon_billing.py
# 職責：工程部 - 點工計薪與外包估驗（登記、自動試算金額與狀態追蹤）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _fmt_vnd(val: float | int) -> str:
    return f"{round(float(val or 0)):,}".replace(",", ".")


def _ensure_subcon_billing_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS eng_subcon_billing (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        billing_no VARCHAR(64) UNIQUE NOT NULL,
                        project_id VARCHAR(80),
                        site_name VARCHAR(160),
                        billing_type VARCHAR(32) NOT NULL,
                        vendor_or_worker VARCHAR(160) NOT NULL,
                        work_scope VARCHAR(200) NOT NULL,
                        qty_or_days NUMERIC(10, 2) NOT NULL,
                        unit_rate_vnd NUMERIC(18, 2) NOT NULL,
                        total_amount_vnd NUMERIC(18, 2) NOT NULL,
                        status VARCHAR(32) DEFAULT 'SUBMITTED',
                        po_id VARCHAR(80),
                        approval_id VARCHAR(80),
                        notes TEXT,
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def _load_billing_df(engine, tenant_id: str) -> pd.DataFrame:
    fallback = [
        {
            "billing_no": "LAB-202611-01",
            "project_id": "PRJ-2026-01",
            "site_name": "西寧廠二期配電盤擴建",
            "billing_type": "DAILY_LABOR",
            "vendor_or_worker": "點工班組 A（電工 3 人）",
            "work_scope": "A棟 1F 配電盤穿線與端子整理",
            "qty_or_days": 5.0,
            "unit_rate_vnd": 1500000.0,
            "total_amount_vnd": 7500000.0,
            "status": "APPROVED",
            "notes": "依當日施工日報核對出工",
        },
        {
            "billing_no": "VAL-202611-01",
            "project_id": "PRJ-2026-01",
            "site_name": "西寧廠二期配電盤擴建",
            "billing_type": "SUBCON_VALUATION",
            "vendor_or_worker": "Công Ty TNHH Cơ Điện Tây Ninh",
            "work_scope": "主幹線電纜橋架安裝第一期估驗 (40%)",
            "qty_or_days": 1.0,
            "unit_rate_vnd": 45000000.0,
            "total_amount_vnd": 45000000.0,
            "status": "SUBMITTED",
            "notes": "待工程主管確認估驗比例",
        },
    ]
    if not engine:
        return pd.DataFrame(fallback)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT billing_no,
                           COALESCE(project_id, '-') AS project_id,
                           COALESCE(site_name, '-') AS site_name,
                           billing_type,
                           vendor_or_worker,
                           work_scope,
                           COALESCE(qty_or_days, 0) AS qty_or_days,
                           COALESCE(unit_rate_vnd, 0) AS unit_rate_vnd,
                           COALESCE(total_amount_vnd, 0) AS total_amount_vnd,
                           COALESCE(status, 'SUBMITTED') AS status,
                           COALESCE(notes, '-') AS notes
                    FROM eng_subcon_billing
                    WHERE tenant_id = :tid
                    ORDER BY id DESC
                    LIMIT 50
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame(fallback)
    except Exception:
        return pd.DataFrame(fallback)


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "Eng_Billing"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 👷 點工計薪與外包估驗")
    st.caption("建立工地點工計薪與外包商工程估驗單，自動試算金額並追蹤核准狀態。")
    _ensure_subcon_billing_table(engine)

    df = _load_billing_df(engine, tenant_id)

    btype_filter = st.selectbox(
        "篩選單據類別",
        ["ALL", "DAILY_LABOR", "SUBCON_VALUATION"],
        format_func=lambda x: {
            "ALL": "全部單據（點工計薪＋外包估驗）",
            "DAILY_LABOR": "🔨 點工計薪",
            "SUBCON_VALUATION": "📄 外包估驗",
        }[x],
    )

    view_df = df if btype_filter == "ALL" else df[df["billing_type"] == btype_filter]

    c1, c2, c3 = st.columns(3)
    c1.metric("單據筆數", f"{len(view_df)} 筆")
    c2.metric("累計金額 (VND)", f"{_fmt_vnd(view_df['total_amount_vnd'].sum() if not view_df.empty else 0)} ₫")
    c3.metric("待審核筆數", f"{int((view_df['status'] == 'SUBMITTED').sum()) if not view_df.empty else 0} 筆")

    if view_df.empty:
        st.info("目前無符合條件的計薪或估驗紀錄。")
    else:
        disp = view_df.copy()
        disp["單價(₫)"] = disp["unit_rate_vnd"].apply(_fmt_vnd)
        disp["總金額(₫)"] = disp["total_amount_vnd"].apply(_fmt_vnd)
        disp = disp.rename(columns={
            "billing_no": "單據編號",
            "project_id": "專案編號",
            "site_name": "案場名稱",
            "billing_type": "類別",
            "vendor_or_worker": "點工人員／外包商",
            "work_scope": "施作項目／估驗內容",
            "qty_or_days": "工天／數量",
            "status": "狀態",
            "notes": "備註",
        })
        st.dataframe(
            disp[["單據編號", "專案編號", "案場名稱", "類別", "點工人員／外包商", "施作項目／估驗內容", "工天／數量", "單價(₫)", "總金額(₫)", "狀態", "備註"]],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.markdown("#### ➕ 新增點工計薪或外包估驗單")

    with st.form("form_eng_subcon_billing"):
        f1, f2 = st.columns(2)
        with f1:
            btype = st.selectbox(
                "計價類別*",
                [("DAILY_LABOR", "🔨 點工計薪"), ("SUBCON_VALUATION", "📄 外包估驗")],
                format_func=lambda x: x[1],
            )[0]
            pid = st.text_input("專案編號 (project_id)", value=st.session_state.get("active_project_id") or "PRJ-2026-01")
            sname = st.text_input("工地／案場名稱*", placeholder="例：西寧廠二期配電盤擴建")
            party_name = st.text_input("點工人員／外包公司名稱*", placeholder="例：點工班組 B 或 Công Ty TNHH...")
        with f2:
            wscope = st.text_input("施作項目／估驗進度說明*", placeholder="例：配電盤安裝與測試第一期估驗")
            qty_days = st.number_input("工天／數量／估驗單位*", min_value=0.5, max_value=10000.0, value=1.0, step=0.5)
            unit_rate = st.number_input("單價 (VND)*", min_value=0.0, value=1500000.0, step=100000.0)
            po_ref = st.text_input("關聯採購／合約單號 (選填)", placeholder="例：PO-2026-015")

        notes = st.text_area("備註／驗收依據", placeholder="例：已對照當日出工與現場進度")
        est_total = float(qty_days) * float(unit_rate)
        st.info(f"💰 自動試算總金額：**{_fmt_vnd(est_total)} ₫**")

        if st.form_submit_button("💾 建立計薪／估驗單", type="primary", use_container_width=True):
            if not sname.strip() or not party_name.strip() or not wscope.strip():
                st.warning("⚠️ 請填寫案場名稱、點工人員／外包公司與施作項目。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                prefix = "LAB" if btype == "DAILY_LABOR" else "VAL"
                bno = f"{prefix}-{now_vn.strftime('%Y%m%d-%H%M%S')}"
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO eng_subcon_billing (
                                    tenant_id, billing_no, project_id, site_name,
                                    billing_type, vendor_or_worker, work_scope,
                                    qty_or_days, unit_rate_vnd, total_amount_vnd,
                                    status, po_id, notes, created_by, created_at
                                )
                                VALUES (
                                    :tid, :bno, :pid, :sname,
                                    :btype, :party, :wscope,
                                    :qty, :urate, :tot,
                                    'SUBMITTED', :poid, :notes, :cby, :cat
                                )
                            """),
                            {
                                "tid": tenant_id,
                                "bno": bno,
                                "pid": pid.strip() or None,
                                "sname": sname.strip(),
                                "btype": btype,
                                "party": party_name.strip(),
                                "wscope": wscope.strip(),
                                "qty": float(qty_days),
                                "urate": float(unit_rate),
                                "tot": est_total,
                                "poid": po_ref.strip() or None,
                                "notes": notes.strip() or None,
                                "cby": user_name,
                                "cat": now_vn,
                            },
                        )
                    st.success(f"✅ 已建立單據 `{bno}`（金額：{_fmt_vnd(est_total)} ₫）。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 建立單據失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
