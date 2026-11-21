# ==========================================
# 檔案路徑：modules/management/announcements/__init__.py
# 職責：公告套件入口與全站共用公告橫幅元件（確保 render / show 永遠可呼叫，並支援內部、外勤打卡、保全頁面顯示）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text

__all__ = ["render", "show", "render_global_announcement_banner"]


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


def _load_announcements_df(engine, tenant_id: str) -> pd.DataFrame:
    fallback = [
        {
            "posted_at": "2026-11-20",
            "priority": "重要",
            "target_scope": "全公司（內部／外勤工程／保全）",
            "title": "工地進場安衛、外勤打卡與保全門禁查核提醒",
            "content": "請外勤工程人員依規定完成打卡與證照查核；保全人員請落實人員與車輛／物品進出登記。",
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
                           title,
                           content,
                           COALESCE(posted_by, '-') AS posted_by
                    FROM mgmt_announcements
                    WHERE tenant_id = :tid
                    ORDER BY id DESC LIMIT 50
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame(fallback)
    except Exception:
        return pd.DataFrame(fallback)


def render_global_announcement_banner(engine=None, tenant_id: str | None = None):
    """全站共用公告提示列：可在內部主頁、外勤打卡頁、保全操作頁上方呼叫"""
    tid = tenant_id or st.session_state.get("tenant_id", "REETECH_VN")
    df = _load_announcements_df(engine, tid)
    if df.empty:
        return
    top = df.iloc[0]
    badge = "🚨 " if top.get("priority") == "緊急" else ("📢 " if top.get("priority") == "重要" else "ℹ️ ")
    st.info(f"{badge}**【最新公告：{top.get('title', '')}】**（{top.get('posted_at', '')}｜{top.get('target_scope', '全公司')}）— {top.get('content', '')}")


def render(engine=None, lang="zh", **kwargs):
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "Mgmt_Admin"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    # 若 announcements/announcement_hub.py 存在且有可用函式，先嘗試呼叫
    try:
        from modules.management.announcements import announcement_hub

        for fn_name in ("render", "show", "main", "render_announcement_hub"):
            fn = getattr(announcement_hub, fn_name, None)
            if callable(fn) and fn is not render:
                return fn(engine=engine, lang=lang, **kwargs)
    except Exception:
        pass

    st.markdown("### 📢 公司公告佈告欄（全站同步）")
    st.caption("公告發布後將同步顯示於管理部公告區與全站提示列（內部／外勤打卡／保全頁面皆可見）。")
    _ensure_announcements_table(engine)

    df = _load_announcements_df(engine, tenant_id)
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
    with st.form("form_mgmt_announcement_init"):
        c1, c2, c3 = st.columns(3)
        with c1:
            title = st.text_input("公告主旨*", placeholder="例：西寧廠與工地安全注意事項")
        with c2:
            target_scope = st.selectbox("發布對象", ["全公司（內部／外勤／保全）", "全公司", "外勤工程人員", "保全／廠區安控", "管理部"])
        with c3:
            priority = st.selectbox("公告等級", ["一般", "重要", "緊急"])
        content = st.text_area("公告內容*", placeholder="請輸入公告內容...")

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
                                "tid": tenant_id,
                                "t": title.strip(),
                                "s": target_scope,
                                "p": priority,
                                "c": content.strip(),
                                "by": user_name,
                                "at": now_vn,
                            },
                        )
                    st.success("✅ 已發布公告，全站皆可看到最新公告。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 發布失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    return render(engine=engine, lang=lang, **kwargs)
