# ==========================================
# 檔案路徑：modules/engineering/emergency_dispatch.py
# 職責：緊急維修派工與事故公告通知管理
# ==========================================

import streamlit as st
import pandas as pd
import datetime

def show(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🚨 緊急維修派工與事故公告通知中心")
    st.caption("當廠內發生突發事故時，快速發布廣播公告並指派工程師緊急外出至外部廠商/案場維修派工。")

    tab1, tab2 = st.tabs([
        "📢 緊急事故派工公告板", 
        "➕ 發布新的緊急派工任務"
    ])

    with tab1:
        st.markdown("#### 📋 目前進行中的緊急派工與事故清單")
        
        # 模擬緊急派工資料
        dispatch_df = pd.DataFrame({
            "派工單號": ["EMG-2026-01", "EMG-2026-02"],
            "發布時間": ["2026-11-16 08:30", "2026-11-15 14:10"],
            "緊急等級": ["🔴 紅色特急", "🟡 普通緊急"],
            "事故與維修摘要": ["西寧廠一號變壓器跳脫起火，須立即派員前往檢修", "平陽美德廠配電盤控制迴路短路維修"],
            "指派工程師": ["陳志豪、阮文雄", "黎文特"],
            "目標廠商/案場": ["西寧廠動力車間", "平陽美德金屬加工廠"],
            "處理狀態": ["🔧 維修中/處理中", "✅ 已修復完工"]
        })
        st.dataframe(dispatch_df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("#### ✍️ 填寫緊急派工與公告單")
        with st.form("emergency_dispatch_form"):
            col1, col2 = st.columns(2)
            with col1:
                urgency_level = st.selectbox("緊急等級", ["🔴 紅色特急 (立即派工)", "🟡 普通緊急 (當日處理)"])
                target_vendor = st.text_input("外部廠商或案場名稱", placeholder="例如: 平陽美德金屬加工廠")
                assignee = st.text_input("指派帶班工程師/師傅", placeholder="例如: 陳志豪、林建良")
            with col2:
                report_time = st.text_input("事故回報時間", value=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
                required_tools = st.text_input("攜帶工具與備品", placeholder="例如: 三用電表、備用斷路器 100A")

            issue_desc = st.text_area("事故狀況簡述與維修需求", placeholder="請描述發生原因、故障現象及須前往廠商處執行的維修動作...")

            submitted = st.form_submit_button("📢 發布緊急派工公告並通知內部人員", type="primary", use_container_width=True)
            if submitted:
                if not target_vendor or not issue_desc:
                    st.error("⚠️ 請填寫廠商名稱與事故狀況！")
                else:
                    st.success(f"🎉 緊急派工單已成功發布！系統已同步廣播至內部公告欄，指派人員 [{assignee}] 將即刻前往 [{target_vendor}]。")

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
