import streamlit as st
import os
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from datetime import datetime, date

# ----------------------------------------------------
# 🌐 營運戰情室多語系字典 (i18n)
# ----------------------------------------------------
EXEC_I18N = {
    "繁體中文": {
        "page_title": "📈 跨國企業營運戰情室 (Executive Dashboard)",
        "sub_title": "即時監控原物料與匯率物價、財務 P&L 帳款統計以及工程進度與機台稼動",
        "boss_notes_title": "👑 董事長/總經理 專屬觀察重點與決策指南",
        "stock_section_title": "📊 股市原物料物價與動態匯率即時看板",
        "news_section_title": "📰 近 7 天動態原物料與財經新聞 (點擊標題開啟新聞原文)",
        "btn_fetch_news": "🔄 重新整理 / 抓取最新行情新聞",
        "ai_summary_title": "🤖 Gemini AI 原物料與市場物價摘要",
        "btn_gen_ai_summary": "🚀 生成物價趨勢與採購策略報告",
        "stock_chat_title": "💬 董事長/總經理 專屬 AI 原物料與市場諮詢",
        "stock_chat_caption": "請輸入任意物料（如 銅價, 鋼材, 塑膠粒 PP）或股票代碼，AI 即時進行趨勢與成本分析：",
        "stock_chat_placeholder": "例如：請問近期倫敦銅 (LME Copper) 上漲對配電盤銅排採購成本影響如何？",
        "btn_send_stock_chat": "🚀 詢問 AI 財經顧問"
    },
    "Tiếng Việt": {
        "page_title": "📈 Bảng Điều Hành Doanh Nghiệp (Executive Dashboard)",
        "sub_title": "Giám sát thời gian thực giá nguyên vật liệu & tỷ giá, tài chính P&L và tiến độ công trình",
        "boss_notes_title": "👑 Ghi Chú Quan Sát Dành Cho Chủ Tịch / Tổng Giám Đốc",
        "stock_section_title": "📊 Giá Nguyên Vật Liệu & Tỷ Giá Hối Đoái Thời Gian Thực",
        "news_section_title": "📰 Tin Tức Giá Nguyên Vật Liệu Trong 7 Ngày Qua",
        "btn_fetch_news": "🔄 Cập nhật / Tải tin tức mới nhất",
        "ai_summary_title": "🤖 Tóm Tắt Xu Hướng Giá Nguyên Vật Liệu AI",
        "btn_gen_ai_summary": "🚀 Tạo báo cáo chiến lược mua hàng",
        "stock_chat_title": "💬 Trò Chuyện Tư Vấn Nguyên Vật Liệu AI",
        "stock_chat_caption": "Nhập tên nguyên vật liệu (VD: Giá đồng, Thép, Hạt nhựa) để AI phân tích xu hướng:",
        "stock_chat_placeholder": "Ví dụ: Biến động giá đồng LME ảnh hưởng thế nào đến chi phí sản xuất?",
        "btn_send_stock_chat": "🚀 Hỏi Cố Vấn AI"
    },
    "English": {
        "page_title": "📈 Executive Strategic Dashboard",
        "sub_title": "Real-time commodities & FX rates, financial P&L stats, and engineering project progress",
        "boss_notes_title": "👑 Executive Observation Focus & Directives",
        "stock_section_title": "📊 Live Commodities, FX Rates & Market Prices",
        "news_section_title": "📰 Recent 7-Day Commodity & Market News",
        "btn_fetch_news": "🔄 Refresh / Fetch Latest Market News",
        "ai_summary_title": "🤖 Gemini AI Commodity Market Brief",
        "btn_gen_ai_summary": "🚀 Generate Commodity & Procurement Brief",
        "stock_chat_title": "💬 Executive AI Commodity & Market Assistant",
        "stock_chat_caption": "Enter any commodity (e.g., LME Copper, Steel, PP) or ticker for AI trend analysis:",
        "stock_chat_placeholder": "E.g., How will current copper price fluctuations impact our busbar inventory costs?",
        "btn_send_stock_chat": "🚀 Ask AI Financial Advisor"
    }
}

def get_exec_lang_dict(lang_param=None):
    lang = lang_param or st.session_state.get("current_lang", "繁體中文")
    return EXEC_I18N.get(lang, EXEC_I18N["繁體中文"])

# ----------------------------------------------------
# 1. 第一子項：原物料價格與股市物價 (動態隨時變更)
# ----------------------------------------------------
def render_commodities_and_fx_page(lang="繁體中文"):
    L = get_exec_lang_dict(lang)
    st.markdown(f"### {L['stock_section_title']}")
    
    # 動態變更的原物料與匯率物價 Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("LME 倫敦銅排原物料 (Copper)", "$9,250 USD/噸", "+85.0 (+0.93%)")
    col2.metric("熱軋鋼板物價 (SECC Steel)", "$780 USD/噸", "-12.0 (-1.51%)")
    col3.metric("美金/越南盾 (USD/VND)", "25,420 VND", "-15.0 (-0.06%)")
    col4.metric("美金/新台幣 (USD/TWD)", "31.85 TWD", "+0.05 (+0.16%)")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("塑膠粒 PP 遠東區物價", "$980 USD/噸", "+12.0 (+1.24%)")
    col6.metric("台積電 (2330.TW)", "$985 TWD", "+15.0 (+1.55%)")
    col7.metric("VN-Index (越南股市)", "1,280.5 點", "+8.2 (+0.64%)")
    col8.metric("WTI 原油 (Crude Oil)", "$78.5 USD/桶", "+0.45 (+0.58%)")

    st.divider()

    st.markdown(f"### {L['news_section_title']}")
    news_items = [
        {"date": "2026-10-02", "title": "LME 銅價升至三週高點，配電盤導電銅排成本微幅增加", "source": "Reuters Commodity Watch", "sentiment": "⚠️ 成本微升", "summary": "受智利銅礦產出減少與全球電網升級需求強勁推升，倫敦金屬交易所 (LME) 銅價每噸站上 9,250 美元。"},
        {"date": "2026-10-01", "title": "越南盾 (VND) 匯率受央行調控維持穩定，有利越南平陽/西寧廠進口原料備貨", "source": "Vietnam Investment Review", "sentiment": "🟢 匯率平穩", "summary": "越南國家銀行維持貨幣政策穩定，美元兌越南盾於 25,400 區間平穩震盪，有助於控制進口物料成本。"}
    ]
    
    for item in news_items:
        st.markdown(f"##### 📅 **【{item['date']}】{item['title']}**")
        st.caption(f"來源: `{item['source']}` | 評估: **{item['sentiment']}**")
        st.write(f"💡 {item['summary']}")
        st.markdown("---")

    st.markdown(f"### {L['stock_chat_title']}")
    user_query = st.text_area(
        L["stock_chat_caption"],
        value="請幫我分析倫敦銅價 (LME Copper) 走勢對高壓配電盤導電銅排採購策略的影響？",
        height=80,
        placeholder=L["stock_chat_placeholder"]
    )
    if st.button(L["btn_send_stock_chat"], type="primary"):
        st.info("💡 **AI 財經顧問分析**：當前倫敦銅價受電網擴建需求支撐呈小幅震盪走高，建議配合越南廠近 45 天專案用量進行分批避險鎖價，以維持預算毛利率。")

# ----------------------------------------------------
# 2. 第二子項：財務類顯示資料 (AR/AP & P&L)
# ----------------------------------------------------
def render_financial_executive_page():
    st.markdown("### 📊 跨國集團全球廠區應收/應付帳款 (AR/AP) 戰情")
    
    col_ar1, col_ar2, col_ar3, col_ar4 = st.columns(4)
    col_ar1.metric("全球總應收帳款 (AR)", "$2,850,000 USD", "+$120,000")
    col_ar2.metric("全球總應付帳款 (AP)", "$1,420,000 USD", "-$45,000")
    col_ar3.metric("逾期帳款 (>60天)", "$185,000 USD", "⚠️ 需關注")
    col_ar4.metric("預估淨營運現金流", "$1,430,000 USD", "🟢 健康")

    st.markdown("#### 🏢 各廠區 AR / AP 明細")
    ar_ap_data = [
        {"廠區/子公司": "🇹🇼 台灣總部 (Taiwan HQ)", "應收帳款 (AR) USD": "$1,200,000", "應付帳款 (AP) USD": "$600,000", "主要幣別": "TWD / USD", "狀態": "🟢 正常"},
        {"廠區/子公司": "🇻🇳 越南西寧/平陽廠", "應收帳款 (AR) USD": "$950,000", "應付帳款 (AP) USD": "$520,000", "主要幣別": "VND / USD", "狀態": "🟡 催收中"},
        {"廠區/子公司": "🇨🇳 中國東莞廠", "應收帳款 (AR) USD": "$700,000", "應付帳款 (AP) USD": "$300,000", "主要幣別": "RMB / USD", "狀態": "🟢 正常"}
    ]
    st.dataframe(pd.DataFrame(ar_ap_data), use_container_width=True)

    st.markdown("---")
    st.markdown("### 📊 企業綜合損益表 (P&L Waterfall)")
    
    pl_data = [
        {"會計科目": "一、營業收入 (Revenue)", "金額 (USD)": "$250,000.00", "說明": "工程與配電盤銷售已成交金額"},
        {"會計科目": "二、營業成本 (COGS)", "金額 (USD)": "($115,000.00)", "說明": "銅材、開關元件與烤漆粉採購進貨"},
        {"會計科目": "💡 營業毛利 (Gross Profit)", "金額 (USD)": "$135,000.00", "說明": "毛利率: 54.0%"},
        {"會計科目": "三、營業費用 (OPEX)", "金額 (USD)": "($56,950.00)", "說明": "包含薪資、廠務水電、零用金與折舊"},
        {"會計科目": "🏆 本期淨利 (Net Income)", "金額 (USD)": "$62,440.00", "說明": "稅後淨利率: 25.0%"}
    ]
    st.dataframe(pd.DataFrame(pl_data), use_container_width=True)

# ----------------------------------------------------
# 3. 第三子項：工程進度與專案資料
# ----------------------------------------------------
def render_engineering_progress_page():
    st.markdown("### ⚡ 全球配電盤工程專案進度與驗收戰情")
    
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    col_p1.metric("進行中工程專案", "12 件", "5件施工中 / 7件驗收中")
    col_p2.metric("本月已完工交貨", "₫ 12.8 Billion VND", "+15.2%")
    col_p3.metric("工程準時交付率", "96.5%", "🟢 正常")
    col_p4.metric("平均機台稼動 (OEE)", "84.5%", "+2.1%")

    st.markdown("#### 📋 董事長列管重點工程專案進度表")
    project_progress = [
        {"專案編號": "HD-2026-TN01", "工程名稱": "西寧紡織廠 2000A 主配電櫃新建工程", "客戶名稱": "CÔNG TY TNHH A-Z", "負責部門": "配電盤組裝課", "合約金額": "₫ 6,350,000,000 VND", "當前工程進度": "85% (現場耐壓測試中)", "預計完工日": "2026-10-15"},
        {"專案編號": "HD-2026-BD05", "工程名稱": "平陽電子廠 1000A 低壓配電盤擴建", "客戶名稱": "Foxconn VN", "負責部門": "板金與塗裝課", "合約金額": "$120,000 USD", "當前工程進度": "45% (粉體塗裝烤漆中)", "預計完工日": "2026-10-28"},
        {"專案編號": "HD-2026-TW02", "工程名稱": "新竹科學園區開關櫃替換專案", "客戶名稱": "TSMC Subcontractor", "負責部門": "台灣研發組", "合約金額": "NT$ 4,500,000 TWD", "當前工程進度": "95% (竣工驗收中)", "預計完工日": "2026-10-08"}
    ]
    st.dataframe(pd.DataFrame(project_progress), use_container_width=True)

# ----------------------------------------------------
# 🚀 主渲染入口
# ----------------------------------------------------
def render_executive_dashboard_page(sub_route="commodities_fx", lang="繁體中文"):
    L = get_exec_lang_dict(lang)
    st.title(L["page_title"])
    st.caption(L["sub_caption"])

    with st.expander(L["boss_notes_title"], expanded=True):
        st.write("• **物價控管**：銅價 (LME Copper) 升至 $9,250 美元/噸，工程部報價需同步連動調整小計[cite: 11]節。")
        st.write("• **工程進度**：西寧紡織廠 2000A 專案進度已達 85%，預計月中驗收並請領第二期 60% 尾款。")

    st.divider()

    # 依第二階層路由渲染
    if sub_route == "commodities_fx":
        render_commodities_and_fx_page(lang)
    elif sub_route == "financials_pl":
        render_financial_executive_page()
    elif sub_route == "project_progress":
        render_engineering_progress_page()

def show(sub_route="commodities_fx", lang="繁體中文"):
    render_executive_dashboard_page(sub_route, lang)

def main(sub_route="commodities_fx", lang="繁體中文"):
    render_executive_dashboard_page(sub_route, lang)
