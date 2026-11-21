# ==========================================
# 檔案路徑：modules/management/legal_finance/ar_ap_ledger.py
# 職責：L2 財務／會計 - 應收帳款 (AR)、應付帳款 (AP) 與帳務明細建檔及查詢
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _fmt_vnd(val: float | int) -> str:
    return f"{round(float(val or 0)):,}".replace(",", ".")


def _ensure_ledger_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS fin_ledger_entries (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        doc_no VARCHAR(64) UNIQUE NOT NULL,
                        project_id VARCHAR(80),
                        category VARCHAR(48) NOT NULL,
                        counterparty VARCHAR(160) NOT NULL,
                        summary VARCHAR(255) NOT NULL,
                        amount_vnd NUMERIC(18, 2) NOT NULL,
                        status VARCHAR(32) DEFAULT 'UNPAID_AR',
                        invoice_id VARCHAR(80),
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def _load_ledger_df(engine, tenant_id: str) -> pd.DataFrame:
    fallback = [
        {
            "doc_no": "AR-202611-01",
            "project_id": "PRJ-2026-01",
            "category": "應收帳款 (AR)",
            "counterparty": "西寧廠二期工程業主",
            "summary": "配電盤設備第一期估驗請款",
            "amount_vnd": 380000000.0,
            "status": "UNPAID_AR",
        },
        {
            "doc_no": "AP-202611-01",
            "project_id": "PRJ-2026-01",
            "category": "應付帳款 (AP)",
            "counterparty": "Công Ty TNHH Thiết Bị Điện",
            "summary": "主斷路器與銅排採購應付",
            "amount_vnd": 145000000.0,
            "status": "UNPAID_AP",
        },
        {
            "doc_no": "AP-202611-02",
            "project_id": "PRJ-2026-02",
            "category": "應付帳款 (AP)",
            "counterparty": "Công Ty TNHH Cơ Điện Tây Ninh",
            "summary": "電纜橋架外包估驗款項",
            "amount_vnd": 45000000.0,
            "status": "PENDING_PAY",
        },
    ]
    if not engine:
        return pd.DataFrame(fallback)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT doc_no,
                           COALESCE(project_id, '-') AS project_id,
                           category,
                           COALESCE(counterparty, '-') AS counterparty,
                           COALESCE(summary, '-') AS summary,
                           COALESCE(amount_vnd, 0) AS amount_vnd,
                           COALESCE(status, 'OPEN') AS status
                    FROM fin_ledger_entries
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
    user_name = st.session_state.get("user_name") or "Fin_Admin"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 💳 財務應收／應付與帳務明細（L2 財務／會計）")
    st.caption("登記與查詢應收帳款 (AR)、應付帳款 (AP) 與帳務摘要，同步連動「管理部總覽」。")
    _ensure_ledger_table(engine)

    df = _load_ledger_df(engine, tenant_id)
    ar_sum = float(df[df["category"].str.contains("AR|應收", case=False, na=False)]["amount_vnd"].sum()) if not df.empty else 0.0
    ap_sum = float(df[df["category"].str.contains("AP|應付", case=False, na=False)]["amount_vnd"].sum()) if not df.empty else 0.0

    m1, m2, m3 = st.columns(3)
    m1.metric("應收帳款合計 (AR)", f"{_fmt_vnd(ar_sum)} ₫")
    m2.metric("應付帳款合計 (AP)", f"{_fmt_vnd(ap_sum)} ₫")
    m3.metric("應收減應付淨額", f"{_fmt_vnd(ar_sum - ap_sum)} ₫")

    if not df.empty:
        disp = df.copy()
        disp["金額(₫)"] = disp["amount_vnd"].apply(_fmt_vnd)
        disp = disp.rename(columns={
            "doc_no": "單據編號",
            "project_id": "專案",
            "category": "帳務類別",
            "counterparty": "往來對象",
            "summary": "帳務摘要",
            "status": "狀態",
        })
        st.dataframe(
            disp[["單據編號", "專案", "帳務類別", "往來對象", "帳務摘要", "金額(₫)", "狀態"]],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.markdown("#### ➕ 新增應收／應付帳務單")
    with st.form("form_fin_ar_ap"):
        f1, f2 = st.columns(2)
        with f1:
            cat_choice = st.selectbox("帳務類別*", ["應收帳款 (AR)", "應付帳款 (AP)"])
            pid = st.text_input("專案編號 (project_id)", value=st.session_state.get("active_project_id") or "PRJ-2026-01")
            counterparty = st.text_input("往來對象（客戶／供應商／外包商）*", placeholder="例：西寧廠二期工程業主 或 Công Ty TNHH...")
        with f2:
            summary = st.text_input("帳務摘要*", placeholder="例：配電盤設備第二期估驗請款")
            amount_vnd = st.number_input("金額 (VND)*", min_value=0.0, value=0.0, step=1000000.0)
            status = st.selectbox(
                "帳務狀態",
                ["UNPAID_AR", "UNPAID_AP", "PENDING_PAY", "PAID"],
            )

        if st.form_submit_button("💾 儲存帳務單", type="primary", use_container_width=True):
            if not counterparty.strip() or not summary.strip():
                st.warning("⚠️ 請填寫往來對象與帳務摘要。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                prefix = "AR" if "AR" in cat_choice else "AP"
                doc_no = f"{prefix}-{now_vn.strftime('%Y%m%d-%H%M%S')}"
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO fin_ledger_entries (
                                    tenant_id, doc_no, project_id, category,
                                    counterparty, summary, amount_vnd, status,
                                    created_by, created_at
                                )
                                VALUES (
                                    :tid, :dno, :pid, :cat,
                                    :cparty, :sum, :amt, :st,
                                    :cby, :cat_ts
                                )
                            """),
                            {
                                "tid": tenant_id, "dno": doc_no, "pid": pid.strip() or None,
                                "cat": cat_choice, "cparty": counterparty.strip(),
                                "sum": summary.strip(), "amt": float(amount_vnd),
                                "st": status, "cby": user_name, "cat_ts": now_vn,
                            },
                        )
                    st.success(f"✅ 已建立帳務單 `{doc_no}`（{_fmt_vnd(amount_vnd)} ₫）。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存帳務單失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
