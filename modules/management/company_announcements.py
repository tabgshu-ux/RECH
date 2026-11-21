# ==========================================
# 檔案路徑：modules/management/announcements.py
# 職責：L1 管理部 - 公司公告佈告欄（發布、置頂與跨部門公告查詢）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_announcements_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS mgmt_announcements (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        title VARCHAR(200) NOT NULL,
                        target_scope VARCHAR(120) DEFAULT '全公司',
                        priority VARCHAR(32) DEFAULT '一般',
                        content TEXT NOT NULL,
                        posted_by VARCHAR(100),
                        posted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def _load_announcements(engine, tenant_id: str) -> pd.DataFrame:
    fallback = [
        {
            "posted_at": "2026-11-20",
            "priority": "重要",
            "target_scope": "全公司（西寧／平陽／工地）",
            "title": "工地進場安衛與證照查核提醒",
            "content": "外包商與現場工程人員進場前，請先完成證照建檔與 GPS 圍籬打卡設定。",
            "posted_by": "管理部",
        }
    ]
    if not engine:
        return pd.DataFrame(fallback)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT TO_CHAR(posted_at, 'YYYY-MM-DD') AS posted_at,
                           COALESCE(priority, '一般') AS priority,
                           COALESCE(target_scope, '全公司') AS target_scope,
                           title, content,
                           COALESCE(posted_by, '-') AS posted_by
                    FROM mgmt_announcements
                    WHERE tenant_id = :tid
                    ORDER BY id DESC LIMIT 40
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame(fallback)
    except Exception:
        return pd.DataFrame(fallback)


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "Mgmt_Admin"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 📢 公司公告佈告欄（L1 管理部）")
    st.caption("發布與查閱全公司或指定部門／廠區的管理公告。")
    _ensure_announcements_table(engine)

    df = _load_announcements(engine, tenant_id)
    if not df.empty:
        disp = df.rename(columns={
            "posted_at": "發布日期",
            "priority": "等級",
            "target_scope": "發布對象",
            "title": "公告主旨",
            "content": "公告內容",
            "posted_by": "發布人",
        })
        st.dataframe(disp, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### ➕ 發布新公告")
    with st.form("form_mgmt_announcement"):
        c1, c2, c3 = st.columns(3)
        with c1:
            title = st.text_input("公告主旨*", placeholder="例：12 月份盤點與休假通知")
        with c2:
            target_scope = st.text_input("發布對象", value="全公司")
        with c3:
            priority = st.selectbox("公告等級", ["一般", "重要", "緊急"])
        content = st.text_area("公告內容*", placeholder="請輸入公告詳細說明...")

        if st.form_submit_button("💾 發布公告", type="primary", use_container_width=True):
            if not title.strip() or not content.strip():
                st.warning("⚠️ 請填寫公告主旨與內容。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO mgmt_announcements (
                                    tenant_id, title, target_scope, priority, content, posted_by, posted_at
                                )
                                VALUES (:tid, :t, :s, :p, :c, :by, :at)
                            """),
                            {
                                "tid": tenant_id, "t": title.strip(), "s": target_scope.strip() or "全公司",
                                "p": priority, "c": content.strip(), "by": user_name, "at": now_vn,
                            },
                        )
                    st.success("✅ 已發布公告。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 發布失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
