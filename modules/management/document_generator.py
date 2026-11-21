# ==========================================
# 檔案路徑：modules/management/document_generator.py
# 職責：L1 管理部 - 公文、合約通知與行政公告草稿產生與留存
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_doc_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS mgmt_generated_docs (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        doc_no VARCHAR(64) UNIQUE NOT NULL,
                        doc_type VARCHAR(80) NOT NULL,
                        recipient VARCHAR(160) NOT NULL,
                        subject VARCHAR(200) NOT NULL,
                        body_text TEXT NOT NULL,
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def _load_docs(engine, tenant_id: str) -> pd.DataFrame:
    if not engine:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT doc_no, doc_type, recipient, subject,
                           TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI') AS created_at
                    FROM mgmt_generated_docs
                    WHERE tenant_id = :tid
                    ORDER BY id DESC LIMIT 30
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "Mgmt_Doc"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 📄 公文與行政通知單產生器（L1 管理部）")
    st.caption("快速產生行政通知、外包／廠商函文或內部備忘錄並留存紀錄。")
    _ensure_doc_table(engine)

    with st.form("form_mgmt_doc_gen"):
        c1, c2 = st.columns(2)
        with c1:
            doc_type = st.selectbox("文件類型*", ["行政通知單", "廠商／外包函文", "人事／薪資說明函", "廠務／宿舍公告"])
            recipient = st.text_input("受文對象*", placeholder="例：全體員工 或 Công Ty TNHH...")
        with c2:
            subject = st.text_input("主旨*", placeholder="例：施工安全與出勤管理規定通知")
            ref_code = st.text_input("關聯案場／單號 (選填)", placeholder="例：PRJ-2026-01")

        key_points = st.text_area("重點內容／辦理事項*", placeholder="請輸入要交代的事項、時間或金額條件...")

        if st.form_submit_button("📝 生成公文草稿並存檔", type="primary", use_container_width=True):
            if not recipient.strip() or not subject.strip() or not key_points.strip():
                st.warning("⚠️ 請完整填寫受文對象、主旨與重點內容。")
            else:
                dno = f"DOC-{now_vn.strftime('%Y%m%d-%H%M%S')}"
                draft = (
                    f"【{doc_type}】編號：{dno}\n"
                    f"日期：{now_vn.strftime('%Y-%m-%d')}\n"
                    f"受文者：{recipient.strip()}\n"
                    f"關聯編號：{ref_code.strip() or '-'}\n"
                    f"主旨：{subject.strip()}\n"
                    f"----------------------------------------\n"
                    f"{key_points.strip()}\n"
                    f"----------------------------------------\n"
                    f"發文字號：管理部／承辦人：{user_name}"
                )
                st.text_area("已產生之公文草稿（可直接全選複製）", value=draft, height=220)
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO mgmt_generated_docs (
                                        tenant_id, doc_no, doc_type, recipient, subject, body_text, created_by, created_at
                                    )
                                    VALUES (:tid, :dno, :dt, :rec, :sub, :btxt, :cby, :cat)
                                """),
                                {
                                    "tid": tenant_id, "dno": dno, "dt": doc_type,
                                    "rec": recipient.strip(), "sub": subject.strip(),
                                    "btxt": draft, "cby": user_name, "cat": now_vn,
                                },
                            )
                        st.success(f"✅ 已留存公文紀錄 `{dno}`。")
                    except Exception as e:
                        st.error(f"❌ 存檔失敗：{e}")

    df_docs = _load_docs(engine, tenant_id)
    if not df_docs.empty:
        st.divider()
        st.markdown("#### 🗂️ 近期已產生文件紀錄")
        st.dataframe(
            df_docs.rename(columns={"doc_no": "文件編號", "doc_type": "類型", "recipient": "受文對象", "subject": "主旨", "created_at": "建立時間"}),
            use_container_width=True,
            hide_index=True,
        )


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
