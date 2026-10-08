import streamlit as st
import pandas as pd

def render_executive_dashboard_page(sub_route=None, lang="繁體中文", **kwargs):
    # 🌐 總經理室戰情室多語系字典 (i18n)
    EXEC_I18N = {
        "繁體中文": {
            "title": "📈 總經理室 - 跨國營運戰情室與 Gemini 智能顧問",
            "caption": "即時監控西寧廠與海防廠之工程專案進度、材料市場行情（銅/鋁價與匯率）、應收應付盈虧，並內建 Gemini 智能決策顧問。",
            "m1": "📊 應收帳款總額 (Total AR)",
            "m2": "📉 應付帳款與成本 (Total AP)",
            "m3": "💰 本月毛利與稅後淨利",
            "m4": "🔴 銅價即時行情 (LME)",
            "tab_gemini": "🤖 Gemini 智能採購與總體經濟分析顧問",
            "tab_market": "🔴 原料行情與買進決策看板",
            "tab_projects": "🏗️ 跨國工程專案進度與異常回報",
            "tab_fin": "💵 公司盈虧、應收應付與財務總覽",
            "gemini_prompt_label": "💬 請向 Gemini 諮詢關於銅鋁金屬走勢、採購時機或專案成本評估：",
            "gemini_ph": "例如：目前 LME 銅價處於高檔，針對西寧廠下一季的大型配電盤案場，我們該如何擬定採購策略？",
            "btn_ask": "🚀 發送給 Gemini 進行深度分析",
            "btn_view_fin": "📊 前往查看詳細越南稅務財報 (Thông tư 200)",
            "no_data": "目前尚無資料。"
        },
        "Tiếng Việt": {
            "title": "📈 Ban Giám đốc - Trung tâm Điều hành & Cố vấn Thông minh Gemini",
            "caption": "Giám sát tiến độ dự án, giá nguyên vật liệu, lãi lỗ tài chính và tích hợp Cố vấn AI Gemini hỗ trợ quyết định.",
            "m1": "📊 Tổng Phải thu (Total AR)",
            "m2": "📉 Tổng Phải trả & Chi phí (Total AP)",
            "m3": "💰 Lợi nhuận gộp & Sau thuế",
            "m4": "🔴 Giá đồng LME",
            "tab_gemini": "🤖 Cố vấn AI Gemini - Phân tích Mua hàng & Thị trường",
            "tab_market": "🔴 Giá Nguyên vật liệu & Quyết định Mua",
            "tab_projects": "🏗️ Tiến độ Dự án & Cảnh báo sự cố",
            "tab_fin": "💵 Lãi lỗ, Phải thu & Phải trả",
            "gemini_prompt_label": "💬 Hỏi Gemini về xu hướng kim loại, thời điểm mua hàng hoặc chi phí dự án:",
            "gemini_ph": "Ví dụ: Giá đồng đang ở mức cao, chúng ta nên có chiến lược mua hàng thế nào cho nhà máy Tây Ninh?",
            "btn_ask": "🚀 Gửi cho Gemini phân tích chuyên sâu",
            "btn_view_fin": "📊 Xem chi tiết Báo cáo Tài chính chuẩn Thuế VN",
            "no_data": "Hiện không có dữ liệu."
        },
        "English": {
            "title": "📈 Executive Office - Operations, Raw Materials & Gemini AI Advisor",
            "caption": "Real-time monitoring of project progress, raw material markets, P&L, and built-in Gemini AI strategic advisor.",
            "m1": "📊 Total Accounts Receivable (AR)",
            "m2": "📉 Total Accounts Payable (AP)",
            "m3": "💰 Gross Profit & Net Income",
            "m4": "🔴 Live LME Copper Price",
            "tab_gemini": "🤖 Gemini AI Purchasing & Market Advisor",
            "tab_market": "🔴 Raw Materials & Purchasing Decisions",
            "tab_projects": "🏗️ Project Progress & Site Issues",
            "tab_fin": "💵 P&L & AR/AP Overview",
            "gemini_prompt_label": "💬 Ask Gemini about metal trends, purchasing timing, or project cost evaluation:",
            "gemini_ph": "E.g., Copper is high; what purchasing strategy should we adopt for the Tay Ninh switchgear project?",
            "btn_ask": "🚀 Send to Gemini for Deep Analysis",
            "btn_view_fin": "📊 View Detailed Vietnamese Tax Financials",
            "no_data": "No data available."
        }
    }

    active_lang = lang if lang in EXEC_I18N else "繁體中文"
    L = EXEC_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    # ----------------------------------------------------
    # 🔄 自動抓取系統即時數據
    # ----------------------------------------------------
    total_ar = sum(item["outstanding"] for item in st.session_state.get("sales_ar_db", [{"outstanding": 141630132003.0}]))
    total_ap = 45200000000.0
    net_profit = 27600000000.0

    # 頂部核心指標看板
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(L["m1"], f"{total_ar:,.0f} ₫", "🟢 應收款項安全")
    c2.metric(L["m2"], f"{total_ap:,.0f} ₫", "🟡 採購應付管控中")
    c3.metric(L["m3"], f"{net_profit:,.0f} ₫", "🟢 獲利穩健")
    c4.metric(L["m4"], "$14,400 USD/噸", "🔴 LME 銅價處于高檔區間")

    st.divider()

    # 標籤頁：Gemini 智慧顧問放在第一位，隨後是原料行情、工程與財務
    tab_gemini, tab_market, tab_projects, tab_fin = st.tabs([
        L["tab_gemini"], L["tab_market"], L["tab_projects"], L["tab_fin"]
    ])

    with tab_gemini:
        st.markdown("### 🤖 Gemini 智能採購與總體經濟分析顧問")
        st.caption("專為總經理與高階經營團隊打造的 AI 決策支援系統，可即時分析國際金屬期貨、避險策略與專案成本控管。")
        
        user_query = st.text_area(L["gemini_prompt_label"], placeholder=L["gemini_ph"], height=100)
        
        if st.button(L["btn_ask"], type="primary"):
            if user_query:
                with st.spinner("🤖 Gemini 正在結合 LME 金屬行情與裕豐 ERP 財務數據進行深度分析..."):
                    # 模擬智慧分析回應
                    st.success("✅ 分析完成！以下為 Gemini 提供的專業決策建議：")
                    st.markdown(f"""
                    > **💡 針對您提出的問題：** *「{user_query}」*
                    >
                    > **1. 國際原物料趨勢分析：**
                    > 目前倫敦金屬交易所 (LME) 銅價期貨約在 **$14,400 USD/噸** 附近震盪，受全球能源轉型及電力基建需求支撐，短期內回檔空間有限。
                    > 
                    > **2. 裕豐電機採購與接案建議：**
                    > * **鎖定合約價差**：建議西寧廠與海防廠針對已得標的大型配電盤專案（如和鼎隆、彥豪專案），立即透過【採購與應付帳款模組】與主要銅排供應商洽談固定總價合約，避免成本遭到侵蝕。
                    > * **分批進貨避險**：針對尚未開工的案場，建議採用分批次下單（分 3 期）以分散原物料波動風險。
                    > 
                    > **3. 現金流與 AR/AP 聯動提醒：**
                    > 目前公司未收應收款 (AR) 充沛，足以支應短期大宗原物料備貨，但仍需留意匯率（USD/VND、TWD/VND）波動對跨境結匯造成的微幅成本影響。
                    """)
            else:
                st.warning("⚠️ 請輸入您的諮詢問題或採購評估方向！")

    with tab_market:
        st.markdown("### 🔴 配電盤製造關鍵原料即時行情與採購決策建議")
        market_decision_data = [
            {"原料名稱": "倫敦金屬交易所 - 導電銅價 (Copper Grade A)", "國際即時價位": "$14,400 USD / 噸", "近週漲跌幅": "+1.8% 📈", "採購決策建議": "🔴 銅價處於歷史高檔，建議針對大型工程專案合約提前鎖定採購合約"},
            {"原料名稱": "工業導電鋁擠型材 (Aluminum Profiles)", "國際即時價位": "$3,149 USD / 噸", "近週漲跌幅": "-0.5% 📉", "採購決策建議": "🟢 價位平穩，可按正常生產排程叫料"},
            {"原料名稱": "美元對越南盾匯率 (USD/VND)", "國際即時價位": "25,450 ₫", "近週漲跌幅": "穩定 ➡️", "採購決策建議": "🟡 進口原物料成本受匯率影響，建議留意結匯時點"},
            {"原料名稱": "新台幣對越南盾匯率 (TWD/VND)", "國際即時價位": "795 ₫", "近週漲跌幅": "+0.2%", "採購決策建議": "🟢 跨國資金調撥與母子公司帳款結算正常"}
        ]
        st.dataframe(pd.DataFrame(market_decision_data), use_container_width=True)

    with tab_projects:
        st.markdown("### 🏗️ 跨國工程專案進度與現場異常紅綠燈監控")
        project_deep_overview = [
            {"專案代碼": "HD-2025-HOT", "客戶名稱": "和鼎隆建築 (Ho Team)", "廠區": "西寧廠", "專案合約總額": "45,000,000,000 ₫", "專案進度": "85% (設備安裝中)", "現場回報與異常狀態": "🟢 正常施工，預計下週進行無載試車", "負責人": "李佑銘"},
            {"專案代碼": "HD-2026-JIA", "客戶名稱": "佳威商旅", "廠區": "海防廠", "專案合約總額": "28,500,000,000 ₫", "專案進度": "30% (過路橋架配管)", "現場回報與異常狀態": "🔴 現場土木進度延遲 3 天，已指派工務經理協調外包商", "負責人": "阮文強"},
            {"專案代碼": "HD-2026-YAN", "客戶名稱": "彥豪金屬工業", "廠區": "西寧廠", "專案合約總額": "41,900,000,000 ₫", "專案進度": "50% (配電盤出廠檢驗)", "現場回報與異常狀態": "🟢 銅排母線檢驗合格，等待客戶驗收", "負責人": "陳經理"}
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

    st.markdown("---")
    if st.button(L["btn_view_fin"], type="primary", use_container_width=True):
        st.info("💡 提示：請至左側選單點選 【管理部 ➡️ 越南稅務標準財務報表 (Thông tư 200)】 以查閱完整的資產負債表與綜合損益表。")

def show(*args, **kwargs):
    render_executive_dashboard_page(*args, **kwargs)

def main(*args, **kwargs):
    render_executive_dashboard_page(*args, **kwargs)
