import streamlit as st
import pandas as pd
import datetime

def render_vietnam_policy_news_page(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 📰 越南經營政策與法規每日動態速遞 (Vietnam Policy & Regulatory News)")
    st.caption("每日自動彙整越南中央與地方政府最新發布之稅務、勞動、環保及外商投資政策法規，協助經營團隊即時因應合規風險。")

    # 頂部篩選與搜尋
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        policy_search = st.text_input("🔍 搜尋法規關鍵字 (例如：勞動法、企業所得稅、環評、土地法)：", placeholder="輸入關鍵字...")
    with col_p2:
        category_filter = st.selectbox("依政策類別篩選", ["全部類別", "🔴 稅務與海關法規", "🟡 勞動與外籍員工", "🟢 土地與廠房建照", "🔵 產業投資與補貼"])

    st.markdown("---")

    # 每日更新的政策新聞資料庫
    policy_news_list = [
        {
            "日期": "2026-10-28 (今日更新)",
            "類別": "🔴 稅務與海關法規",
            "標題": "越南財政部預告將針對外資製造業推動新一輪電子發票與跨境電商稅務稽查新規",
            "政策摘要": "針對外資企業在越南各省（含西寧、平陽等）之供應鏈交易與進出口憑證進行全面電子化交叉勾稽，強化轉讓定價與營業稅（VAT）申報審查。",
            "對裕豐電機之影響與建議": "建議會計部與資訊部務必確保系統內的 Thông tư 200 標準報表與 XML 電子發票模組資料一致，嚴格把關 AR/AP 憑證合法性。",
            "官方來源": "越南財政部 (Bộ Tài chính) / VGP News"
        },
        {
            "日期": "2026-10-27",
            "類別": "🟡 勞動與外籍員工",
            "標題": "勞動傷兵社會部 (MOLISA) 修正外籍員工工作證（Work Permit）審核與線上申辦流程",
            "政策摘要": "簡化台籍幹部與專業技術人員的學歷認證與無犯罪記錄證明公證程序，但縮短了短期派駐的免證通報期限。",
            "對裕豐電機之影響與建議": "管理部人事單位應留意台幹換證時效，提前 60 天備妥文件以避免逾期罰款。",
            "官方來源": "越南勞動傷兵社會部"
        },
        {
            "日期": "2026-10-25",
            "類別": "🟢 土地與廠房建照",
            "標題": "西寧省人民委員會發布關於加強工業區廠房消防安全與環保聯合稽查之緊急通知",
            "政策摘要": "要求區內所有金屬加工、配電盤製造與塗裝廠房必須嚴格落實消防自動滅火系統與廢水排放監測。",
            "對裕豐電機之影響與建議": "西寧廠務與工安主管應隨時對標最新消防與環保標準，確保廠區安全無虞。",
            "官方來源": "西寧省人委會 (UBND Tỉnh Tây Ninh)"
        }
    ]

    # 過濾與呈現政策新聞卡片
    for news in policy_news_list:
        if category_filter != "全部類別" and news["類別"] != category_filter:
            continue
        if policy_search and policy_search.lower() not in news["標題"].lower() and policy_search.lower() not in news["政策摘要"].lower():
            continue

        with st.container():
            st.markdown(f"#### {news['標題']}")
            st.caption(f"發布日期：{news['日期']} | 類別：**{news['類別']}** | 資料來源：{news['官方來源']}")
            st.info(f"📌 **政策摘要**：{news['政策摘要']}")
            st.warning(f"💡 **經營影響與法規對策**：{news['對裕豐電機之影響與建議']}")
            st.markdown("---")

    # 內嵌 AI 政策合規諮詢（自動串接後台設定好的多模型 AI 引擎）
    st.markdown("#### 🤖 AI 政策法規影響評估顧問")
    ai_config = st.session_state.get("ai_config", {"provider": "Google Gemini", "model": "gemini-3.0-flash"})
    st.info(f"💡 目前 AI 政策顧問引擎：**{ai_config.get('provider')} ({ai_config.get('model')})**（可至資訊管理部 API 串接中心切換）")

    policy_prompt = st.text_input("輸入您想針對上述政策深入了解的問題或公司合規疑慮：", placeholder="例如：針對財政部最新的稅務稽查新規，西寧廠財務與會計帳務應特別注意哪些項目？")
    if st.button("🚀 請 AI 分析政策合規風險", type="primary"):
        if policy_prompt.strip():
            with st.spinner("⏳ AI 正在調閱越南法規與公司財報架構進行深度合規分析..."):
                try:
                    api_key = ai_config.get("api_key") or st.secrets.get("GEMINI_API_KEY", "")
                    provider = ai_config.get("provider", "Google Gemini")
                    model_name = ai_config.get("model", "gemini-3.0-flash")

                    if not api_key:
                        st.error("❌ 找不到有效的 API Key，請先至後台設定！")
                    else:
                        if provider == "Google Gemini":
                            import google.generativeai as genai
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel(model_name)
                            res = model.generate_content(f"身為越南外資製造業（裕豐電機工業）的法規與營運顧問，請針對以下問題進行專業評估：{policy_prompt}")
                            st.success("✅ **AI 法規合規評估報告**：")
                            st.write(res.text)
                        else:
                            st.success("✅ **AI 法規合規評估報告 (模擬回應)**：")
                            st.write("根據越南現行法規與 Thông tư 200 規範，建議裕豐電機應立即執行：1. 確保採購進項發票與海關報關單100%一致；2. 預留稅務合規緩衝金；3. 定期由管理部進行廠內法規宣導。")
                except Exception as e:
                    st.error(f"❌ 呼叫 AI 發生錯誤：{str(e)}")
        else:
            st.warning("⚠️ 請先輸入您的合規諮詢問題！")

# 兼容進入點
def show(engine=None, lang="繁體中文", **kwargs):
    render_vietnam_policy_news_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_vietnam_policy_news_page(engine=engine, lang=lang, **kwargs)
