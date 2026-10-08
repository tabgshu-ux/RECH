import streamlit as st
import pandas as pd

def render_executive_dashboard_page(sub_route=None, lang="繁體中文", **kwargs):
    # 🌐 總經理室戰情室多語系字典 (i18n)
    EXEC_I18N = {
        "繁體中文": {
            "title": "📈 總經理室 - 跨國營運戰情室與工程總覽",
            "caption": "專為工程背景經營者打造：即時掌握西寧廠與海防廠之工程專案進度、現場異常問題、應收應付盈虧、原物料行情與越南稅務財務。",
            "m1": "📊 應收帳款總額 (Total AR)",
            "m2": "📉 應付帳款與成本 (Total AP)",
            "m3": "💰 本月毛利與稅後淨利",
            "m4": "⚡ 進行中工程專案與異常",
            "sec_project_focus": "⚡ 工程專案進度與現場異常紅綠燈監控",
            "sec_fin_focus": "📊 公司整體盈虧、應收應付與財務戰情",
            "sec_market": "🔴 原物料行情與越盾匯率監控",
            "tab_projects": "🏗️ 工程專案進度與異常回報",
            "tab_fin": "💵 財務盈虧與應收應付總覽",
            "tab_market": "📈 銅價、鋁價與匯率行情",
            "btn_view_fin": "📊 前往查看詳細越南稅務財報 (Thông tư 200)",
            "no_data": "目前尚無資料。"
        },
        "Tiếng Việt": {
            "title": "📈 Ban Giám đốc - Trung tâm Điều hành Kỹ thuật & Tài chính",
            "caption": "Dành cho nhà quản lý: Theo dõi sát sao tiến độ dự án cơ điện, sự cố công trường, lãi lỗ tài chính, giá nguyên vật liệu và báo cáo thuế.",
            "m1": "📊 Tổng Phải thu (Total AR)",
            "m2": "📉 Tổng Phải trả & Chi phí (Total AP)",
            "m3": "💰 Lợi nhuận gộp & Sau thuế tháng",
            "m4": "⚡ Dự án đang thi công & Sự cố",
            "sec_project_focus": "⚡ Tiến độ Dự án Kỹ thuật & Giám sát Sự cố",
            "sec_fin_focus": "📊 Lãi lỗ toàn công ty, Phải thu & Phải trả",
            "sec_market": "📈 Giá Nguyên vật liệu & Tỷ giá VND",
            "tab_projects": "🏗️ Tiến độ dự án & Cảnh báo sự cố",
            "tab_fin": "💵 Lãi lỗ & Phải thu/Phải trả",
            "tab_market": "📈 Giá đồng, nhôm & Tỷ giá",
            "btn_view_fin": "📊 Xem chi tiết Báo cáo Tài chính chuẩn Thuế VN",
            "no_data": "Hiện không có dữ liệu."
        },
        "English": {
            "title": "📈 Executive Office - Operations, Engineering & Financial Dashboard",
            "caption": "Tailored for executive management: Real-time monitoring of M&E project progress, site issues, P&L, raw material prices, and financials.",
            "m1": "📊 Total Accounts Receivable (AR)",
            "m2": "📉 Total Accounts Payable (AP)",
            "m3": "💰 Gross Profit & Net Income",
            "m4": "⚡ Active Projects & Site Issues",
            "sec_project_focus": "sec_project_focus",
            "sec_fin_focus": "sec_fin_focus",
            "sec_market": "sec_market",
            "tab_projects": "🏗️ Project Progress & Site Issues",
            "tab_fin": "💵 P&L & AR/AP Overview",
            "tab_market": "📈 Raw Materials & FX",
            "btn_view_fin": "📊 View Detailed Vietnamese Tax Financials",
            "no_data": "No data available."
        }
    }

    active_lang = lang if lang in EXEC_I18N else "繁體中文"
    L = EXEC_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    # ----------------------------------------------------
    # 🔄 自動從系統各模組抓取即時數據
    # ----------------------------------------------------
    total_ar = sum(item["outstanding"] for item in st.session_state.get("sales_ar_db", [{"outstanding": 141630132003.0}]))
    total_ap = 45200000000.0  # 模擬採購與應付總額
    net_profit = 27600000000.0 # 稅後淨利

    # 頂部核心指標看板（老闆最關注的盈虧與專案）
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(L["m1"], f"{total_ar:,.0f} ₫", "🟢 應收款項安全")
    c2.metric(L["m2"], f"{total_ap:,.0f} ₫", "🟡 應付帳款管控中")
    c3.metric(L["m3"], f"{net_profit:,.0f} ₫", "🟢 營運獲利良好")
    c4.metric(L["m4"], "3 個進行中 / 1 個注意", "🔴 需主管關注")

    st.divider()

    # 標籤頁設計：工程專案重鎮 ＋ 財務盈虧 ＋ 原物料市場
    tab_projects, tab_fin, tab_market = st.tabs([
        L["tab_projects"], L["tab_fin"], L["tab_market"]
    ])

    with tab_projects:
        st.markdown("### 🏗️ 跨國工程專案進度、現場問題與異常監控")
        st.caption("老闆專屬戰情：即時掌握西寧廠與海防廠各案場之配電盤安裝、過路橋架與現場施工異常。")
        
        project_deep_overview = [
            {
                "專案代碼": "HD-2025-HOT", 
                "客戶名稱": "和鼎隆建築 (Ho Team)", 
                "廠區": "西寧廠", 
                "專案合約總額": "45,000,000,000 ₫",
                "專案進度": "85% (設備安裝中)", 
                "現場回報與異常狀態": "🟢 正常施工，預計下週進行無載試車", 
                "負責人": "李佑銘"
            },
            {
                "專案代碼": "HD-2026-JIA", 
                "客戶名稱": "佳威商旅", 
                "廠區": "海防廠", 
                "專案合約總額": "28,500,000,000 ₫",
                "專案進度": "30% (過路橋架配管)", 
                "現場回報與異常狀態": "🔴 現場土木進度延遲 3 天，已指派工務經理協調外包商", 
                "負責人": "阮文強"
            },
            {
                "專案代碼": "HD-2026-YAN", 
                "客戶名稱": "彥豪金屬工業", 
                "廠區": "西寧廠", 
                "專案合約總額": "41,900,000,000 ₫",
                "專案進度": "50% (配電盤出廠檢驗)", 
                "現場回報與異常狀態": "🟢 銅排母線檢驗合格，等待客戶驗收", 
                "負責人": "陳經理"
            }
        ]
        st.dataframe(pd.DataFrame(project_deep_overview), use_container_width=True)

    with tab_fin:
        st.markdown("### 📊 公司整體盈虧、應收帳款 (AR) 與應付帳款 (AP) 整合")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown("#### 📑 應收帳款 (AR) 即時追蹤")
            if "sales_ar_db" in st.session_state and st.session_state.sales_ar_db:
                ar_summary = [{"客戶": item["customer"], "未收款": f"{item['outstanding']:,.0f} ₫", "狀態": item["status"]} for item in st.session_state.sales_ar_db]
                st.dataframe(pd.DataFrame(ar_summary), use_container_width=True)
            else:
                st.info(L["no_data"])
        with col_f2:
            st.markdown("#### 🛒 採購應付帳款 (AP) 與成本")
            ap_summary = [
                {"供應商": "越南銅業股份有限公司", "應付金額": "18,200,000,000 ₫", "付款狀態": "🟢 正常票期"},
                {"供應商": "施耐德電機零組件 (Schneider)", "應付金額": "12,500,000,000 ₫", "付款狀態": "🟢 已列入本月 AP"},
                {"供應商": "在地五金與外包工班", "應付金額": "4,500,000,000 ₫", "付款狀態": "🟡 待主管簽核"}
            ]
            st.dataframe(pd.DataFrame(ap_summary), use_container_width=True)

    with tab_market:
        st.markdown("### 📈 配電盤製造原物料行情與越盾匯率看板")
        market_data = [
            {"項目": "倫敦金屬交易所 - 導電銅價 (Copper LME)", "當前價格": "$9,850 USD / 噸", "漲跌幅": "+1.4% 📈"},
            {"項目": "工業鋁擠型材行情", "當前價格": "$2,420 USD / 噸", "漲跌幅": "-0.3% 📉"},
            {"項目": "美元對越南盾匯率 (USD/VND)", "當前價格": "25,450 ₫", "漲跌幅": "穩定"},
            {"項目": "新台幣對越南盾匯率 (TWD/VND)", "當前價格": "795 ₫", "漲跌幅": "小幅波動"}
        ]
        st.dataframe(pd.DataFrame(market_data), use_container_width=True)

    st.markdown("---")
    if st.button(L["btn_view_fin"], type="primary", use_container_width=True):
        st.info("💡 提示：請至左側選單點選 【管理部 ➡️ 越南稅務標準財務報表 (Thông tư 200)】 以查閱完整的資產負債表與綜合損益表。")

def show(*args, **kwargs):
    render_executive_dashboard_page(*args, **kwargs)

def main(*args, **kwargs):
    render_executive_dashboard_page(*args, **kwargs)
