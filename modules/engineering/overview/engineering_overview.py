# ==========================================
# 檔案路徑：modules/engineering/engineering_overview.py
# 職責：工程部總覽
# ==========================================

import streamlit as st
import pandas as pd

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

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
