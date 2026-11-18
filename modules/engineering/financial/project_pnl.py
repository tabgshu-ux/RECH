# ==========================================
# 檔案路徑：modules/engineering/project_pnl.py
# 職責：工程專案損益與預算控管（即時毛利、估驗請款、追加減帳管理）
# ==========================================

import streamlit as st
import pandas as pd

def show(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 📈 工程專案損益與預算控管 (Project P&L & Budget Control)")
    st.caption("水電工程核心：自動歸屬材料、外包、工時與雜支，隨時掌握單一案場賺賠、估驗計價請款與追加減帳。")

    tab_pnl, tab_billing, tab_change_order = st.tabs([
        "💰 單一案場即時毛利損益", 
        "📋 估驗計價與請款追蹤", 
        "✍️ 追加減帳管理與簽核"
    ])

    with tab_pnl:
        st.markdown("#### 🔍 選擇要檢視損益的工程案場")
        project_list = [
            "PRJ-2026-01 西寧廠二期配電盤擴建工程",
            "PRJ-2026-02 平陽工業區廠房機電統包",
            "PRJ-2026-03 隆安省光電園區變壓器安裝"
        ]
        selected_proj = st.selectbox("選擇專案", project_list)

        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💵 合約總收入", "12,500,000,000 ₫", "含追加減帳")
        with col2:
            st.metric("🛠️ 實際總成本", "9,450,000,000 ₫", "材料+工資+外包+雜支")
        with col3:
            st.metric("📈 預估即時毛利", "3,050,000,000 ₫", "毛利率 24.4%")
        with col4:
            st.metric("🟢 案場營運狀態", "正常獲利", "績效良好")

        st.markdown("#### 📋 成本歸屬明細表（材料、外包、工時、雜支）")
        cost_df = pd.DataFrame({
            "成本類別": ["材料領用 (電線/開關/管材)", "外包工資 (專業配盤外包)", "內部師傅工時分攤", "工地雜支與交通住宿"],
            "預算金額 (VND)": [4500000000, 3200000000, 1500000000, 300000000],
            "實際發生 (VND)": [4650000000, 3100000000, 1450000000, 250000000],
            "差異數與控管": ["🔴 超支 150萬", "🟢 節省 100萬", "🟢 節省 50萬", "🟢 節省 50萬"]
        })
        st.dataframe(cost_df, use_container_width=True, hide_index=True)

    with tab_billing:
        st.markdown("#### 📋 工程分期估驗計價與請款進度追蹤")
        st.info("💡 支援分期收款（訂金、進場、完工、保固金），老闆可一鍵查看已請款金額與未收保留款。")

        billing_df = pd.DataFrame({
            "計價階段": ["第一期：簽約訂金", "第二期：材料進場", "第三期：配管配線完成", "第四期：試車驗收交機", "第五期：工程保固金"],
            "比例 (%)": ["20%", "30%", "30%", "15%", "5%"],
            "金額 (VND)": [2500000000, 3750000000, 3750000000, 1875000000, 625000000],
            "請款狀態": ["✅ 已收款", "✅ 已收款", "⏳ 審核請款中 (AR)", "❌ 未到期", "❌ 未到期"]
        })
        st.dataframe(billing_df, use_container_width=True, hide_index=True)

    with tab_change_order:
        st.markdown("#### ✍️ 業主設計變更與追加減帳記錄")
        st.caption("業主臨時變更設計或追加插座、管線時，系統可記錄追加報價與簽核，避免師傅做白工。")

        co_df = pd.DataFrame({
            "單號": ["CO-2026-01", "CO-2026-02"],
            "變更內容說明": ["一樓車道追加動力插座 10 組", "三樓控制室管線路徑變更"],
            "追加金額 (VND)": ["+ 150,000,000 ₫", "+ 45,000,000 ₫"],
            "簽核狀態": ["🟢 業主已簽認", "⏳ 審核中"],
            "是否已納入合約": ["已更新", "待確認"]
        })
        st.dataframe(co_df, use_container_width=True, hide_index=True)

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
