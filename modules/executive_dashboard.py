import datetime
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------
# 🌐 營運戰情室多語系字典 (i18n)
# ----------------------------------------------------
EXEC_I18N = {
    "繁體中文": {
        "page_title": "👑 裕豐電機工業 - 董事長 / 總經理 戰情看板",
        "sub_title": (
            "REETECH INDUSTRIAL Co., Ltd. - 綜合營運、物價與財務管理系統 (📱"
            " 手機優先版)"
        ),
        "boss_notes_title": "👑 董事長/總經理 專屬觀察重點與決策指南",
        "sec_commodities": (
            "🔴 1. 原料價格與動態股市物價 / 匯率即時看板"
        ),
        "sec_finance": (
            "📊 2. 全球廠區財務類顯示資料 (AR/AP & P&L 損益)"
        ),
        "sec_engineering": "⚡ 3. 配電盤工程專案進度與驗收資料",
        "news_title": "📰 近 7 天動態原物料與財經新聞",
        "chat_title": "💬 董事長/總經理 專屬 AI 原物料與市場諮詢",
        "chat_caption": (
            "請輸入任意物料（如 銅價, 鋼材, 塑膠粒 PP）或股票代碼，AI"
            " 即時進行趨勢與成本分析："
        ),
    },
    "Tiếng Việt": {
        "page_title": "👑 REETECH INDUSTRIAL - Báo cáo Ban Giám đốc",
        "sub_title": (
            "Hệ thống Báo cáo Quản trị Doanh nghiệp, Giá cả & Tài chính"
        ),
        "boss_notes_title": (
            "👑 Ghi Chú Quan Sát Dành Cho Chủ Tịch / Tổng Giám Đốc"
        ),
        "sec_commodities": (
            "🔴 1. Giá Nguyên liệu & Tỷ giá Chứng khoán Thời gian thực"
        ),
        "sec_finance": (
            "📊 2. Dữ liệu Tài chính (Phải thu AR/ Phải trả AP & P&L)"
        ),
        "sec_engineering": (
            "⚡ 3. Tiến độ Dự án Kỹ thuật Tủ điện & Bàn giao"
        ),
        "news_title": "📰 Tin Tức Giá Nguyên Vật Liệu Trong 7 Ngày Qua",
        "chat_title": "💬 Trò Chuyện Tư Vấn Nguyên Vật Liệu AI",
        "chat_caption": (
            "Nhập tên nguyên vật liệu (VD: Giá đồng, Thép, Hạt nhựa) để AI phân"
            " tích xu hướng:"
        ),
    },
    "English": {
        "page_title": "👑 REETECH INDUSTRIAL - Executive Dashboard",
        "sub_title": (
            "Comprehensive Operations, Commodity & Financial Management System"
        ),
        "boss_notes_title": "👑 Executive Observation Focus & Directives",
        "sec_commodities": (
            "🔴 1. Raw Material Prices & Dynamic FX/Market Rates"
        ),
        "sec_finance": (
            "📊 2. Global Financial Analytics (AR/AP & P&L Waterfall)"
        ),
        "sec_engineering": (
            "⚡ 3. Engineering Project Progress & Acceptance Status"
        ),
        "news_title": "📰 Recent 7-Day Commodity & Market News",
        "chat_title": "💬 Executive AI Commodity & Market Assistant",
        "chat_caption": (
            "Enter any commodity (e.g., LME Copper, Steel, PP) or ticker for AI"
            " trend analysis:"
        ),
    },
}


def get_exec_lang_dict(lang_param=None):
    lang = lang_param or st.session_state.get("current_lang", "繁體中文")
    return EXEC_I18N.get(lang, EXEC_I18N["繁體中文"])


# ----------------------------------------------------
# 1. 區塊一：原料價格與股市物價/匯率 (📱 手機卡片優化)
# ----------------------------------------------------
def render_commodities_section(L):
    st.markdown(f"### {L['sec_commodities']}")

    # 手機上以 2 欄垂直顯示物價與指標
    c1, c2 = st.columns(2)
    c1.metric(
        "LME 倫敦銅排 (Copper)", "$9,250 USD/噸", "+85.0 (+0.93%)"
    )
    c2.metric(
        "熱軋鋼板物價 (SECC)", "$780 USD/噸", "-12.0 (-1.51%)"
    )

    c3, c4 = st.columns(2)
    c3.metric("美金/越南盾 (USD/VND)", "25,420 VND", "-15.0")
    c4.metric("美金/新台幣 (USD/TWD)", "31.85 TWD", "+0.05")

    c5, c6 = st.columns(2)
    c5.metric("塑膠粒 PP 物價", "$980 USD/噸", "+12.0")
    c6.metric("台積電 (2330.TW)", "$985 TWD", "+15.0")

    c7, c8 = st.columns(2)
    c7.metric("VN-Index (越南股市)", "1,280.5 點", "+8.2")
    c8.metric("WTI 原油 (Crude)", "$78.5 USD/桶", "+0.45")

    st.markdown(f"#### {L['news_title']}")
    news_items = [
        {
            "date": "2026-10-02",
            "title": (
                "LME 銅價升至三週高點，配電盤導電銅排成本微幅增加"
            ),
            "source": "Reuters",
            "sentiment": "⚠️ 成本微升",
            "summary": (
                "受智利銅礦產出減少與全球電網升級需求強勁推升，倫敦金屬交易所"
                " (LME) 銅價每噸站上 9,250 美元。"
            ),
        },
        {
            "date": "2026-10-01",
            "title": (
                "越南盾 (VND)"
                " 匯率受央行調控維持穩定，有利越南平陽/西寧廠進口原料備貨"
            ),
            "source": "VIR",
            "sentiment": "🟢 匯率平穩",
            "summary": (
                "越南國家銀行維持貨幣政策穩定，美元兌越南盾於 25,400"
                " 區間平穩震盪，有助於控制進口物料成本。"
            ),
        },
    ]
    for item in news_items:
        with st.container():
            st.markdown(
                f"• **【{item['date']}】{item['title']}** (`{item['source']}`)"
            )
            st.warning(
                f"💡 **評估**: {item['sentiment']} \n\n{item['summary']}"
            )

    st.markdown(f"#### {L['chat_title']}")
    user_query = st.text_area(
        L["chat_caption"],
        value=(
            "請幫我分析倫敦銅價 (LME Copper)"
            " 走勢對高壓配電盤導電銅排採購策略的影響？"
        ),
        height=80,
    )
    if st.button("🚀 詢問 AI 財經顧問", type="primary", use_container_width=True):
        st.info(
            "💡 **AI 財經顧問分析**：當前倫敦銅價受電網擴建需求支撐呈小幅震盪走高，建議配合越南廠近"
            " 45 天專案用量進行分批避險鎖價，以維持預算毛利率。"
        )


# ----------------------------------------------------
# 2. 區塊二：財務類顯示資料 (📱 廠區 AR/AP 手機卡片連動)
# ----------------------------------------------------
def render_finance_section(L):
    st.markdown(f"### {L['sec_finance']}")

    col_ar1, col_ar2 = st.columns(2)
    col_ar1.metric("全球總應收 (AR)", "$2.85M USD", "+$120K")
    col_ar2.metric("全球總應付 (AP)", "$1,42M USD", "-$45K")

    col_ar3, col_ar4 = st.columns(2)
    col_ar3.metric("逾期帳款 (>60天)", "$185K USD", "⚠️ 關注", delta_color="inverse")
    col_ar4.metric("淨營運現金流", "$1.43M USD", "🟢 健康")

    st.markdown("---")
    st.markdown("##### 🏢 各廠區 AR / AP 明細 (📱 手機卡片直立檢視)")

    # 🔗 動態連動：讀取 st.session_state.factory_list
    if "factory_list" in st.session_state and st.session_state.factory_list:
        dynamic_factories = st.session_state.factory_list
    else:
        dynamic_factories = [
            {"name": "🇹🇼 台灣總部研發中心", "status": "🟢 正常"},
            {"name": "🇻🇳 越南平陽/西寧廠", "status": "🟡 催收中"},
            {"name": "🇨🇳 東莞一廠", "status": "🟢 正常"},
        ]

    view_mode_fin = st.radio(
        "選擇檢視模式：",
        ["📱 手機直立卡片", "💻 電腦表格"],
        horizontal=True,
        key="view_mode_fin",
    )

    if "📱" in view_mode_fin:
        for idx, fact in enumerate(dynamic_factories):
            f_name = fact.get("name", f"廠區-{idx+1}")
            ar_val = (
                "$1,200,000"
                if idx == 0
                else ("$950,000" if idx == 1 else "$700,000")
            )
            ap_val = (
                "$600,000"
                if idx == 0
                else ("$520,000" if idx == 1 else "$300,000")
            )
            status_val = (
                "🟢 正常" if idx != 1 else fact.get("status", "🟡 催收中")
            )

            with st.container():
                st.markdown(f"#### 🏭 {f_name}")
                if "催收" in status_val or "⚠️" in status_val:
                    st.warning(f"🚨 **營運狀態**: {status_val}")
                else:
                    st.success(f"🟢 **營運狀態**: {status_val}")

                c_a, c_b = st.columns(2)
                c_a.write(f"• **應收帳款 (AR)**:\n  `{ar_val}`")
                c_b.write(f"• **應付帳款 (AP)**:\n  `{ap_val}`")
                st.divider()
    else:
        ar_ap_rows = []
        for idx, fact in enumerate(dynamic_factories):
            f_name = fact.get("name", f"廠區-{idx+1}")
            ar_val = (
                "$1,200,000"
                if idx == 0
                else ("$950,000" if idx == 1 else "$700,000")
            )
            ap_val = (
                "$600,000"
                if idx == 0
                else ("$520,000" if idx == 1 else "$300,000")
            )
            status_val = (
                "🟢 正常" if idx != 1 else fact.get("status", "🟡 催收中")
            )
            ar_ap_rows.append({
                "廠區": f_name,
                "AR (USD)": ar_val,
                "AP (USD)": ap_val,
                "狀態": status_val,
            })
        st.dataframe(pd.DataFrame(ar_ap_rows), use_container_width=True)

    st.markdown("##### 📊 企業綜合損益摘要 (P&L)")
    pl_data = [
        {"項目": "營業收入 (Revenue)", "金額 (USD)": "$250,000.00"},
        {"項目": "營業成本 (COGS)", "金額 (USD)": "($115,000.00)"},
        {
            "項目": "營業毛利 (Gross Profit)",
            "金額 (USD)": "$135,000.00 (毛利率 54%)",
        },
        {"項目": "營業費用 (OPEX)", "金額 (USD)": "($56,950.00)"},
        {
            "項目": "本期淨利 (Net Income)",
            "金額 (USD)": "$62,440.00 (淨利率 25%)",
        },
    ]
    st.dataframe(pd.DataFrame(pl_data), use_container_width=True)


# ----------------------------------------------------
# 3. 區塊三：工程專案進度與驗收資料 (📱 手機直立卡片)
# ----------------------------------------------------
def render_engineering_section(L):
    st.markdown(f"### {L['sec_engineering']}")

    col_p1, col_p2 = st.columns(2)
    col_p1.metric("進行中工程專案", "12 件", "5施工/7驗收")
    col_p2.metric("本月完工交貨", "₫ 12.8B VND", "+15.2%")

    col_p3, col_p4 = st.columns(2)
    col_p3.metric("工程準時交付率", "96.5%", "🟢 正常")
    col_p4.metric("平均機台稼動 (OEE)", "84.5%", "+2.1%")

    st.markdown("---")
    st.markdown("##### 📋 董事長列管重點工程專案進度 (📱 手機卡片直立模式)")

    if (
        "project_progress_db" in st.session_state
        and st.session_state.project_progress_db
    ):
        projects_list = st.session_state.project_progress_db
    else:
        projects_list = [
            {
                "專案編號": "HD-2026-TN01",
                "工程名稱": "西寧紡織廠 2000A 主配電櫃工程",
                "客戶": "CÔNG TY TNHH A-Z",
                "合約金額": "₫ 6,350,000,000 VND",
                "工程進度": "85% (現場耐壓測試中)",
                "預計完工": "2026-10-15",
            },
            {
                "專案編號": "HD-2026-BD05",
                "工程名稱": "平陽電子廠 1000A 低壓配電盤擴建",
                "客戶": "Foxconn VN",
                "合約金額": "$120,000 USD",
                "工程進度": "45% (粉體塗裝烤漆中)",
                "預計完工": "2026-10-28",
            },
            {
                "專案編號": "HD-2026-TW02",
                "工程名稱": "新竹科學園區開關櫃替換專案",
                "客戶": "TSMC Subcontractor",
                "合約金額": "NT$ 4,500,000 TWD",
                "工程進度": "95% (竣工驗收中)",
                "預計完工": "2026-10-08",
            },
        ]

    for prj in projects_list:
        with st.container():
            st.markdown(f"#### ⚡ {prj.get('工程名稱', '工程專案')}")
            
            # 🚨 將工程進度與施工狀態置頂放大顯示
            progress_str = prj.get("工程進度", "進度推進中")
            st.info(f"📊 **目前工程進度與狀態**：\n\n**{progress_str}**")

            c1, c2 = st.columns(2)
            c1.write(f"• **客戶**: {prj.get('客戶', 'N/A')}")
            c1.write(f"• **編號**: `{prj.get('專案編號', 'N/A')}`")
            c2.write(f"• **金額**: {prj.get('合約金額', 'N/A')}")
            c2.write(f"• **完工日**: `{prj.get('預計完工', 'N/A')}`")
            st.divider()


# ----------------------------------------------------
# 🚀 容錯進入點
# ----------------------------------------------------
def render_executive_dashboard_page(*args, **kwargs):
    lang = kwargs.get(
        "lang", st.session_state.get("current_lang", "繁體中文")
    )
    sub_route = kwargs.get("sub_route", kwargs.get("sub_option", "all"))
    L = get_exec_lang_dict(lang)

    st.title(L["page_title"])
    st.caption(L["sub_title"])

    with st.expander(L["boss_notes_title"], expanded=True):
        st.write(
            "• **物價控管**：倫敦銅價 (LME Copper) 升至 $9,250"
            " 美元/噸，工程部報價已同步連動資材小計成本。"
        )
        st.write(
            "• **工程驗收**：西寧紡織廠 2000A 專案進度達"
            " 85%，預計月中驗收並請領第二期 60% 尾款。"
        )

    st.divider()

    if sub_route == "commodities_fx":
        render_commodities_section(L)
    elif sub_route == "financials_pl":
        render_finance_section(L)
    elif sub_route == "project_progress":
        render_engineering_section(L)
    else:
        render_commodities_section(L)
        st.divider()
        render_finance_section(L)
        st.divider()
        render_engineering_section(L)


def render(*args, **kwargs):
    render_executive_dashboard_page(*args, **kwargs)


def show(*args, **kwargs):
    render_executive_dashboard_page(*args, **kwargs)


def main(*args, **kwargs):
    render_executive_dashboard_page(*args, **kwargs)
