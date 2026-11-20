# ==========================================
# 檔案路徑：modules/engineering/site_ops/daily_report.py
# 職責：工程部 - 專案分區派工與手機施工日報（案場選單連動 eng_gps_fences 工地設定）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_daily_report_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS eng_daily_reports (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        report_no VARCHAR(64) UNIQUE NOT NULL,
                        project_id VARCHAR(80),
                        site_name VARCHAR(160) NOT NULL,
                        report_date DATE NOT NULL,
                        weather_info VARCHAR(80),
                        tw_staff_cnt INT DEFAULT 0,
                        vn_tech_cnt INT DEFAULT 0,
                        subcon_cnt INT DEFAULT 0,
                        total_workers INT DEFAULT 0,
                        work_zone VARCHAR(160),
                        work_summary TEXT,
                        material_used TEXT,
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def _load_configured_sites(engine, tenant_id: str) -> list[dict]:
    """從工地設定表 eng_gps_fences 讀取啟用中的案場清單（含降級預設）"""
    fallback = [
        {"project_id": "PRJ-2026-01", "site_name": "西寧廠二期配電盤擴建 (Tây Ninh)"},
        {"project_id": "PRJ-2026-02", "site_name": "平陽工業區機電工程 (Bình Dương)"},
    ]
    if not engine:
        return fallback
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT DISTINCT COALESCE(project_id, 'UNASSIGNED') AS project_id,
                           site_name
                    FROM eng_gps_fences
                    WHERE tenant_id = :tid AND COALESCE(is_active, TRUE) = TRUE
                    ORDER BY site_name ASC
                """),
                {"tid": tenant_id},
            ).fetchall()
            if rows:
                return [{"project_id": r.project_id, "site_name": r.site_name} for r in rows]
    except Exception:
        pass
    return fallback


def _load_reports_df(engine, tenant_id: str, keyword: str = "") -> pd.DataFrame:
    fallback = [
        {
            "report_no": "DR-2026-001",
            "project_id": "PRJ-2026-01",
            "site_name": "西寧廠二期配電盤擴建 (Tây Ninh)",
            "report_date": "2026-11-20",
            "weather_info": "晴天 / Nắng",
            "tw_staff_cnt": 2,
            "vn_tech_cnt": 10,
            "subcon_cnt": 3,
            "total_workers": 15,
            "work_zone": "A棟 1F 配電盤主幹線配管",
            "work_summary": "完成 3 迴路 PVC 管路配置與穿線作業。",
            "material_used": "PVC 管 40m、1.5mm² 控制線 120m",
        }
    ]
    if not engine:
        return pd.DataFrame(fallback)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT report_no,
                           COALESCE(project_id, '-') AS project_id,
                           site_name,
                           TO_CHAR(report_date, 'YYYY-MM-DD') AS report_date,
                           COALESCE(weather_info, '-') AS weather_info,
                           COALESCE(tw_staff_cnt, 0) AS tw_staff_cnt,
                           COALESCE(vn_tech_cnt, 0) AS vn_tech_cnt,
                           COALESCE(subcon_cnt, 0) AS subcon_cnt,
                           COALESCE(total_workers, 0) AS total_workers,
                           COALESCE(work_zone, '-') AS work_zone,
                           COALESCE(work_summary, '-') AS work_summary,
                           COALESCE(material_used, '-') AS material_used
                    FROM eng_daily_reports
                    WHERE tenant_id = :tid
                    ORDER BY id DESC
                    LIMIT 50
                """),
                {"tid": tenant_id},
            ).fetchall()
            df = pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame(fallback)
    except Exception:
        df = pd.DataFrame(fallback)

    kw = (keyword or "").strip().lower()
    if kw and not df.empty:
        mask = df.apply(lambda row: kw in " ".join(str(v).lower() for v in row.values), axis=1)
        df = df[mask]
    return df


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "現場工程人員"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 📋 專案分區派工與手機施工日報")
    st.caption("案場清單自動同步自「工地設定」，填報當日出工、施工部位、進度與耗料。")
    _ensure_daily_report_tables(engine)

    search_kw = st.text_input("搜尋日報", placeholder="輸入關鍵字搜尋日報（案場、施工部位、內容、耗料）...", key="dr_search_kw")

    st.markdown("#### 🗂️ 歷史工程日報表總覽")
    df_rep = _load_reports_df(engine, tenant_id, keyword=search_kw)
    if df_rep.empty:
        st.info("目前無符合條件的施工日報紀錄。")
    else:
        disp_rep = df_rep.rename(columns={
            "report_no": "日報編號",
            "project_id": "專案編號",
            "site_name": "案場名稱",
            "report_date": "填報日期",
            "weather_info": "天氣",
            "tw_staff_cnt": "台籍師傅/工程師",
            "vn_tech_cnt": "越籍技術員/技工",
            "subcon_cnt": "外包/點工",
            "total_workers": "總出工人數",
            "work_zone": "施工部位",
            "work_summary": "施工內容",
            "material_used": "耗料紀錄",
        })
        st.dataframe(disp_rep, use_container_width=True, hide_index=True)

    st.divider()
    sites = _load_configured_sites(engine, tenant_id)
    site_labels = [f"{s['site_name']} [{s['project_id']}]" for s in sites]
    site_map = {f"{s['site_name']} [{s['project_id']}]": s for s in sites}

    st.markdown("#### ✍️ 填寫新施工日報")
    with st.form("form_eng_daily_report"):
        st.markdown("##### 📍 步驟 1：選擇工程案場與填報日期")
        c1, c2, c3 = st.columns(3)
        with c1:
            sel_site_lbl = st.selectbox("選擇工程案場 (Project/Site)*", site_labels)
        with c2:
            rep_date = st.date_input("填報日期 (Report Date)*", value=now_vn.date())
        with c3:
            weather_info = st.selectbox("當日天氣狀況 (Weather)", ["晴天 / Nắng", "多雲 / Nhiều mây", "陣雨 / Mưa rào", "陰雨 / Mưa"])

        sel_site = site_map[sel_site_lbl]
        st.caption(f"已連動工地設定：案場「{sel_site['site_name']}」｜專案編號 `{sel_site['project_id']}`")

        st.markdown("##### 👷 步驟 2：當日出工人數統計 (Labor Attendance)")
        l1, l2, l3 = st.columns(3)
        with l1:
            tw_cnt = st.number_input("台籍師傅/工程師人數", min_value=0, max_value=200, value=2, step=1)
        with l2:
            vn_cnt = st.number_input("越籍技術員/技工人數", min_value=0, max_value=500, value=10, step=1)
        with l3:
            sub_cnt = st.number_input("外包/點工工人人數", min_value=0, max_value=500, value=3, step=1)

        total_cnt = int(tw_cnt) + int(vn_cnt) + int(sub_cnt)
        st.info(f"👷 當日總出工人數 (Total Attendance)：**{total_cnt} 人**")

        st.markdown("##### 🛠️ 步驟 3：施工部位、進度與當日耗料記錄")
        work_zone = st.text_input("當日施工部位／樓層 (Location/Zone)*", placeholder="例：A棟 1F 配電盤室 / 區段 Zone B")
        work_summary = st.text_area("當日施工內容與進度*", placeholder="請填寫今日完成項目、測試或派工進度...")
        material_used = st.text_area("當日耗料／領用材料記錄", placeholder="例：電纜、銅排、管材、五金耗用量...")

        if st.form_submit_button("💾 提交當日工程日報", type="primary", use_container_width=True):
            if not work_zone.strip() or not work_summary.strip():
                st.warning("⚠️ 請填寫施工部位與當日施工內容。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                rno = f"DR-{now_vn.strftime('%Y%m%d-%H%M%S')}"
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO eng_daily_reports (
                                    tenant_id, report_no, project_id, site_name,
                                    report_date, weather_info, tw_staff_cnt, vn_tech_cnt,
                                    subcon_cnt, total_workers, work_zone, work_summary,
                                    material_used, created_by, created_at
                                )
                                VALUES (
                                    :tid, :rno, :pid, :sname,
                                    :rdate, :wthr, :twc, :vnc,
                                    :subc, :tot, :wzone, :wsum,
                                    :mat, :cby, :cat
                                )
                            """),
                            {
                                "tid": tenant_id,
                                "rno": rno,
                                "pid": sel_site["project_id"],
                                "sname": sel_site["site_name"],
                                "rdate": rep_date,
                                "wthr": weather_info,
                                "twc": int(tw_cnt),
                                "vnc": int(vn_cnt),
                                "subc": int(sub_cnt),
                                "tot": total_cnt,
                                "wzone": work_zone.strip(),
                                "wsum": work_summary.strip(),
                                "mat": material_used.strip() or "-",
                                "cby": user_name,
                                "cat": now_vn,
                            },
                        )
                    st.success(f"✅ 已提交工程日報 `{rno}`（案場：{sel_site['site_name']}｜總出工 {total_cnt} 人）。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 提交工程日報失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
