# ==========================================
# 檔案路徑：modules/engineering/design/ecn_control.py
# 職責：設計部 - 圖檔版本控管與工程變更 (ECN/ECO，凍結舊版並連動 BOM/專案)
# ==========================================

from datetime import datetime
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_ecn_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS eng_ecn_records (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        ecn_no VARCHAR(64) UNIQUE NOT NULL,
                        project_id VARCHAR(80),
                        bom_id VARCHAR(80),
                        drawing_no VARCHAR(120) NOT NULL,
                        old_rev VARCHAR(32) NOT NULL,
                        new_rev VARCHAR(32) NOT NULL,
                        freeze_old_rev BOOLEAN DEFAULT TRUE,
                        reason_summary TEXT,
                        status VARCHAR(32) DEFAULT 'FROZEN_OLD_REV',
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def render(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name", "Designer")

    txt = {
        "zh": {
            "title": "🗂️ 圖檔版本控管與工程變更 (ECN / ECO)",
            "sub": "管理工程圖紙版次、登記工程變更（ECN）並自動凍結舊版圖面，避免生產與採購誤用舊版。",
            "t1": "1️⃣ 登記工程變更 (ECN) 與凍結舊版",
            "t2": "2️⃣ 圖檔版次與 ECN 變更紀錄",
            "pid": "關聯專案編號 (project_id)",
            "bid": "關聯 BOM 編號 (bom_id，選填)",
            "dno": "圖紙編號 (Drawing No.)",
            "old_rev": "舊版次 (凍結)",
            "new_rev": "新版次 (生效)",
            "freeze": "同步凍結舊版圖面（防呆阻擋舊圖領料／施工）",
            "reason": "變更原因與設計修改說明",
            "save": "💾 發布 ECN 並凍結舊版圖面",
            "ok": "✅ 已發布 ECN 單號 `{}`，舊版 `{}` 已標記凍結。",
            "empty": "目前尚無 ECN 變更紀錄。",
        },
        "vi": {
            "title": "🗂️ Quản Lý Phiên Bản Bản Vẽ & Thay Đổi Kỹ Thuật (ECN / ECO)",
            "sub": "Quản lý phiên bản bản vẽ kỹ thuật, ghi nhận ECN và khóa bản vẽ cũ để tránh sai sót khi sản xuất và mua hàng.",
            "t1": "1️⃣ Tạo Phiếu ECN & Khóa Bản Cũ",
            "t2": "2️⃣ Lịch Sử Phiên Bản & ECN",
            "pid": "Mã Dự Án (project_id)",
            "bid": "Mã BOM (bom_id)",
            "dno": "Số Hiệu Bản Vẽ",
            "old_rev": "Phiên Bản Cũ",
            "new_rev": "Phiên Bản Mới",
            "freeze": "Khóa phiên bản cũ (chặn dùng nhầm bản cũ)",
            "reason": "Lý do và nội dung thay đổi kỹ thuật",
            "save": "💾 Phát Hành ECN & Khóa Bản Cũ",
            "ok": "✅ Đã phát hành ECN `{}`, phiên bản cũ `{}` đã được khóa.",
            "empty": "Chưa có lịch sử ECN.",
        },
        "en": {
            "title": "🗂️ Drawing Revision Control & Engineering Change (ECN / ECO)",
            "sub": "Track drawing revisions, log ECNs, and freeze superseded revisions to prevent errors in production and procurement.",
            "t1": "1️⃣ Log ECN & Freeze Old Revision",
            "t2": "2️⃣ Drawing Revision & ECN History",
            "pid": "Project ID",
            "bid": "BOM ID (Optional)",
            "dno": "Drawing Number",
            "old_rev": "Old Rev (Freeze)",
            "new_rev": "New Rev (Active)",
            "freeze": "Freeze superseded drawing revision",
            "reason": "Change reason & engineering notes",
            "save": "💾 Publish ECN & Freeze Old Rev",
            "ok": "✅ Published ECN `{}` and froze old revision `{}`.",
            "empty": "No ECN records found.",
        },
    }[code]

    st.markdown(f"### {txt['title']}")
    st.caption(txt["sub"])
    _ensure_ecn_table(engine)

    tab1, tab2 = st.tabs([txt["t1"], txt["t2"]])

    with tab1:
        with st.form("form_ecn_create"):
            c1, c2 = st.columns(2)
            with c1:
                project_id = st.text_input(txt["pid"], value="PRJ-2026-01")
                bom_id = st.text_input(txt["bid"], value="")
                drawing_no = st.text_input(txt["dno"], value="DWG-MCC-01A")
            with c2:
                old_rev = st.text_input(txt["old_rev"], value="Rev.A")
                new_rev = st.text_input(txt["new_rev"], value="Rev.B")
                freeze_old = st.checkbox(txt["freeze"], value=True)

            reason = st.text_area(txt["reason"], value="依業主變更調整主斷路器規格與匯流排間距，舊版 Rev.A 停用。")

            if st.form_submit_button(txt["save"], type="primary", use_container_width=True):
                if not drawing_no.strip() or not new_rev.strip():
                    st.warning("⚠️ 請填寫圖紙編號與新版次。")
                elif not engine:
                    st.error("❌ 尚未連線資料庫。")
                else:
                    ecn_no = f"ECN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO eng_ecn_records (
                                        tenant_id, ecn_no, project_id, bom_id, drawing_no,
                                        old_rev, new_rev, freeze_old_rev, reason_summary, status, created_by
                                    )
                                    VALUES (:tid, :eno, :pid, :bid, :dno, :orev, :nrev, :frz, :rsn, :st, :cby)
                                """),
                                {
                                    "tid": tenant_id,
                                    "eno": ecn_no,
                                    "pid": project_id.strip() or None,
                                    "bid": bom_id.strip() or None,
                                    "dno": drawing_no.strip(),
                                    "orev": old_rev.strip() or "Rev.A",
                                    "nrev": new_rev.strip(),
                                    "frz": bool(freeze_old),
                                    "rsn": reason.strip(),
                                    "st": "FROZEN_OLD_REV" if freeze_old else "ACTIVE",
                                    "cby": user_name,
                                },
                            )
                        st.success(txt["ok"].format(ecn_no, old_rev.strip() or "Rev.A"))
                    except Exception as e:
                        st.error(f"❌ 發布 ECN 失敗：{e}")

    with tab2:
        if not engine:
            st.info(txt["empty"])
            return
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text("""
                        SELECT ecn_no AS "ECN單號", project_id AS "專案編號", bom_id AS "BOM單號",
                               drawing_no AS "圖紙編號", old_rev AS "凍結舊版", new_rev AS "生效新版",
                               status AS "狀態", reason_summary AS "變更說明", created_by AS "建立人"
                        FROM eng_ecn_records
                        WHERE tenant_id = :tid
                        ORDER BY id DESC
                        LIMIT 30
                    """),
                    {"tid": tenant_id},
                ).fetchall()
                if not rows:
                    st.info(txt["empty"])
                else:
                    st.dataframe(pd.DataFrame([r._asdict() for r in rows]), use_container_width=True, hide_index=True)
        except Exception:
            st.info(txt["empty"])


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
