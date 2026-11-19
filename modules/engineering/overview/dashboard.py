# ==========================================
# 檔案路徑：modules/engineering/overview/dashboard.py
# 職責：工程部總覽戰情與動態掛載功能卡片（只做總覽與卡片導流，不塞子模組業務邏輯）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text


def _get_mounted_engineering_features(engine):
    """從 sys_department_modules 讀取工程部已掛載功能代碼（兼容 dept_name / department_name）"""
    default_feats = [
        "feat_eng_quotation",
        "feat_site_log",
        "feat_blueprint",
        "feat_bom_procurement",
        "feat_project_pnl",
    ]
    if not engine:
        return default_feats

    try:
        with engine.connect() as conn:
            res = conn.execute(
                text("""
                    SELECT mounted_features
                    FROM sys_department_modules
                    WHERE dept_name = :d OR department_name = :d
                    LIMIT 1
                """),
                {"d": "工程部"},
            ).fetchone()
            if res and res[0]:
                feats = [f.strip() for f in str(res[0]).split(",") if f.strip()]
                # 排除總覽本身，避免總覽首頁再疊一張總覽卡
                filtered = [f for f in feats if f != "feat_eng_overview"]
                return filtered if filtered else default_feats
    except Exception:
        pass

    return default_feats


def show(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🛠️ 工程部總覽 (Engineering Department Overview)")
    st.caption("即時掌控西寧廠、平陽廠與各大工業區案場施工進度、GPS 圍籬打卡及人工成本預算。")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏗️ 進行中案場數", "12 案", "🟢 施工順暢")
    with col2:
        st.metric("👷 今日出勤人數", "86 人", "包含點工 18 人")
    with col3:
        st.metric("⚠️ 進度落後警示", "1 案", "須調派人力支援")
    with col4:
        st.metric("💰 本月工程總合約", "325.5億 ₫", "📈 執行率 78%")

    st.markdown("---")

    st.markdown("#### 📋 各工業區主要案場執行進度一覽表")
    project_data = pd.DataFrame({
        "案場編號": ["PRJ-2026-01", "PRJ-2026-02", "PRJ-2026-03", "PRJ-2026-04"],
        "案場名稱": ["西寧廠二期配電盤擴建工程", "平陽工業區廠房機電統包", "隆安省光電園區變壓器安裝", "胡志明市商辦大樓消防弱電"],
        "負責經理": ["陳志豪", "阮文雄", "林建良", "張國華"],
        "預定完工日": ["2026-11-30", "2026-12-15", "2027-01-10", "2026-12-01"],
        "目前進度": ["85%", "62%", "40%", "92%"],
        "狀態": ["🟢 正常", "🟡 需留意工期", "🟢 正常", "🟢 即將驗收"]
    })
    st.dataframe(project_data, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### 🧩 工程部已掛載功能模組")

    feature_cards = {
        "feat_eng_quotation": {
            "title": "📐 估價中心",
            "desc": "查詢倉庫數量與成本試算毛利，建立報價單並送交共用簽核中心。",
            "target_module": "modules.engineering.financial.quotation",
        },
        "feat_site_log": {
            "title": "📋 工地巡檢與施工日報",
            "desc": "填報現場巡檢、施工進度與異常回報（預留 project_id 關聯）。",
            "target_module": "modules.engineering.site_ops.daily_report",
        },
        "feat_blueprint": {
            "title": "📐 設計圖紙與審查",
            "desc": "管理配電盤與機電圖紙版本及審查狀態。",
            "target_module": "modules.engineering.procurement_qc.testing_acceptance",
        },
        "feat_bom_procurement": {
            "title": "📦 工程 BOM 與採購需求",
            "desc": "串聯估價/專案用料與請購、採購單（預留 quote_id / pr_id / po_id）。",
            "target_module": "modules.engineering.procurement_qc.bom_procurement",
        },
        "feat_project_pnl": {
            "title": "📊 專案損益追蹤",
            "desc": "對照核定報價金額、倉庫成本與實際支出毛利（預留 project_id / quote_id）。",
            "target_module": "modules.engineering.financial.project_pnl",
        },
    }

    mounted_ids = _get_mounted_engineering_features(engine)
    cols = st.columns(2)
    for idx, feat_id in enumerate(mounted_ids):
        meta = feature_cards.get(
            feat_id,
            {
                "title": f"🧩 {feat_id}",
                "desc": "工程部動態掛載模組。",
                "target_module": None,
            },
        )
        with cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"**{meta['title']}**")
                st.caption(meta["desc"])
                if st.button("進入功能 ➡️", key=f"eng_dash_open_{feat_id}_{idx}", use_container_width=True):
                    st.session_state["current_view"] = "dynamic_feature"
                    st.session_state["active_feature_id"] = feat_id
                    if meta.get("target_module"):
                        st.session_state["active_module_path"] = meta["target_module"]
                    st.rerun()


def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)


def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
