# ==========================================
# 檔案路徑：modules/executive/project_analytics.py
# 職責：總經理室專屬 - 工程案場分佈與金額佔比分析（完整程式碼）
# ==========================================

import streamlit as st
import pandas as pd

def show(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🏗️ 工程案場類型分佈與合約金額佔比分析")
    st.caption("專為總經理決策打造的工程營收結構分析，即時掌握廠內接案主力與案值分佈。")

    # 模擬真實工程專案與金額資料
    data = {
        "工程專案類型 (Project Category)": [
            "高低壓配電盤製造與安裝 (Switchgear & Panels)",
            "工業區廠房機電統包工程 (Factory MEP Turnkey)",
            "太陽能光電與節能設備統包 (Solar & Energy)",
            "變壓器與母線排改造工程 (Transformer & Busway)",
            "廠房消防與弱電系統工程 (Fire & ELV Systems)"
        ],
        "承接案場數量 (Count)": [28, 12, 8, 15, 10],
        "合約總金額 (VND)": [
            85450000000, 
            142000000000, 
            68000000000, 
            45000000000, 
            32000000000
        ],
        "平均毛利率 (%)": ["24.5%", "18.2%", "26.0%", "21.5%", "19.0%"],
        "主要案場分佈": ["西寧廠、海防廠", "平陽工業區", "隆安省光電園區", "胡志明市商辦", "同奈省廠房"]
    }

    df = pd.DataFrame(data)

    total_amount = df["合約總金額 (VND)"].sum()
    df["金額佔比 (%)"] = (df["合約總金額 (VND)"] / total_amount * 100).round(2)
    df["合約總金額 (VND)"] = df["合約總金額 (VND)"].apply(lambda x: f"{x:,.0f} ₫")
    df["金額佔比 (%)"] = df["金額佔比 (%)"].astype(str) + "%"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 總承接工程專案數", "73 案", "🟢 案源穩定")
    with col2:
        st.metric("💰 工程合約總金額", f"{total_amount:,.0f} ₫", "📈 較去年同期 +14.2%")
    with col3:
        st.metric("🏆 最大營收佔比類型", "廠房機電統包工程", "佔總金額 38.6%")

    st.markdown("---")

    st.markdown("#### 📋 各工程類別案場數與金額明細對照表")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### 📊 各工程類型合約總金額分佈視覺化")
    chart_data = pd.DataFrame({
        "工程類型": [
            "高低壓配電盤", 
            "廠房機電統包", 
            "太陽能與節能", 
            "變壓器與母線排", 
            "消防與弱電系統"
        ],
        "合約金額 (億 越盾)": [854.5, 1420.0, 680.0, 450.0, 320.0]
    }).set_index("工程類型")
    
    st.bar_chart(chart_data)

    st.info("💡 **AI 經營決策建議**：目前「廠房機電統包工程」與「高低壓配電盤製造」為公司營收兩大主力。建議西寧廠擴大銅排加工與配盤產線人力，以應付第四季交期高峰。")

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
