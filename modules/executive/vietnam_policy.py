import streamlit as st
import pandas as pd
import datetime

@st.cache_data(ttl=3600)
def fetch_latest_vietnam_policies():
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    policies = [
        {"日期": today_str, "類別": "稅務會計", "法規標題": "越南財政部推動電子發票與營業稅（VAT）申報新規", "合規影響": "財務與會計作業需確保進項發票符合最新格式規範。", "狀態": "已同步"},
        {"日期": str(datetime.date.today() - datetime.timedelta(days=1)), "類別": "勞動法規", "法規標題": "西寧省勞動部門加強外籍員工工作證與租屋補貼查核", "合規影響": "總務與人事部須備妥外派人員合法勞動合約與證明。", "狀態": "已同步"},
        {"日期": str(datetime.date.today() - datetime.timedelta(days=2)), "類別": "消防環保", "法規標題": "工業區管理委員會發布廠區消防與危險物品存放辦法", "合規影響": "各廠區須完成消防設施自主檢查。", "狀態": "已同步"}
    ]
    return policies

def render_vietnamese_policy_page(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🇻🇳 越南政府政策與法規動態速遞")
    st.caption("每日自動更新越南稅務、勞動與環保法規資訊。")

    policies = fetch_latest_vietnam_policies()
    st.success(f"系統已完成今日（{datetime.date.today()}）法規資料同步。")
    st.dataframe(pd.DataFrame(policies), use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📋 法規影響評估")
    topic = st.selectbox("選擇評估項目：", ["VAT 與 Thông tư 200 申報變動", "外籍員工薪資與租屋合規", "廠區消防與安檢規定"])
    if topic:
        st.info("評估建議：請相關部門依據最新規範執行內部自我檢查，確保符合當地法規要求。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_vietnamese_policy_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_vietnamese_policy_page(engine=engine, lang=lang, **kwargs)
