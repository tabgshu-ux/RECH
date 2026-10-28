import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def init_policy_db(engine):
    """
    初始化越南政策法規新聞資料表
    """
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.executive_policy_news (
                    id SERIAL PRIMARY KEY,
                    publish_date VARCHAR(50) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    impact_advice TEXT NOT NULL,
                    source VARCHAR(200),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception as e:
        st.warning(f"⚠️ 政策資料表初始化提示: {str(e)}")

def get_policy_news_from_db(engine):
    """
    從資料庫動態抓取所有的政策法規新聞，若資料庫無資料則提供初始預設動態
    """
    news_list = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("""
                    SELECT publish_date, category, title, summary, impact_advice, source 
                    FROM public.executive_policy_news 
                    ORDER BY id DESC;
                """))
                rows = res.fetchall()
                for r in rows:
                    if r[2]:  # 若有標題
                        news_list.append({
                            "日期": str(r[0]),
                            "類別": str(r[1]),
                            "標題": str(r[2]),
                            "政策摘要": str(r[3]),
                            "對裕豐電機之影響與建議": str(r[4]),
                            "官方來源": str(r[5] or "越南官方發布")
                        })
        except Exception:
            pass

    # 若資料庫尚無資料，寫入預設示範資料並回傳
    if not news_list:
        news_list = [
            {
                "日期": str(datetime.date.today()),
                "類別": "🔴 稅務與海關法規",
                "標題": "越南財政部預告將針對外資製造業推動新一輪電子發票與跨境電商稅務稽查新規",
                "政策摘要": "針對外資企業在越南各省（含西寧等）之供應鏈交易與進出口憑證進行全面電子化交叉勾稽，強化轉讓定價與營業稅（VAT）申報審查。",
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
            }
        ]
    return news_list

def render_vietnam_policy_news_page(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 📰 越南經營政策與法規每日動態速遞 (Vietnam Policy & Regulatory News)")
    st.caption("每日自動與手動彙整越南中央與地方政府最新發布之稅務、勞動、環保及外商投資政策法規，協助經營團隊即時因應合規風險。")

    # 初始化資料庫
    init_policy_db(engine)

    # 頂部控制列：搜尋與類別篩選
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        policy_search = st.text_input("🔍 搜尋法規關鍵字 (例如：勞動法、企業所得稅、環評、土地法)：", placeholder="輸入關鍵字...")
    with col_p2:
        category_filter = st.selectbox("依政策類別篩選", ["全部類別", "🔴 稅務與海關法規", "🟡 勞動與外籍員工", "🟢 土地與廠房建照", "🔵 產業投資與補貼"])

    # 展開式的新增法規新聞表單（供管理者每日動態新增法規）
    with st.expander("➕ 新增今日越南法規政策快報 (IT / 管理部專用)"):
        with st.form("form_add_policy"):
            new_title = st.text_input("法規新聞標題")
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                new_cat = st.selectbox("政策類別", ["🔴 稅務與海關法規", "🟡 勞動與外籍員工", "🟢 土地與廠房建照", "🔵 產業投資與補貼"])
            with c_col2:
                new_source = st.text_input("官方資料來源", value="越南政府公報 / VGP News")
            
            new_summary = st.text_area("政策摘要說明")
            new_advice = st.text_area("對裕豐電機之經營影響與合規建議")

            if st.form_submit_button("💾 儲存並發布至總經理室動態", type="primary"):
                if new_title and new_summary and engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.executive_policy_news 
                                (publish_date, category, title, summary, impact_advice, source)
                                VALUES (:p_date, :cat, :title, :sum, :adv, :src)
                            """), {
                                "p_date": str(datetime.date.today()),
                                "cat": new_cat,
                                "title": new_title,
                                "sum": new_summary,
                                "adv": new_advice,
                                "src": new_source
                            })
                        st.success("🎉 法規政策快報已成功寫入資料庫並即時發布！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 寫入資料庫失敗: {str(e)}")
                else:
                    st.warning("⚠️ 請填寫完整標題與摘要！")

    st.markdown("---")

    # 動態從資料庫抓取新聞資料
    policy_news_list = get_policy_news_from_db(engine)

    # 過濾與動態呈現政策新聞卡片
    filtered_count = 0
    for news in policy_news_list:
        if category_filter != "全部類別" and news["類別"] != category_filter:
            continue
        if policy_search and policy_search.lower() not in news["標題"].lower() and policy_search.lower() not in news["政策摘要"].lower():
            continue

        filtered_count += 1
        with st.container():
            st.markdown(f"#### {news['標題']}")
            st.caption(f"發布日期：{news['日期']} | 類別：**{news['類別']}** | 資料來源：{news['官方來源']}")
            st.info(f"📌 **政策摘要**：{news['政策摘要']}")
            st.warning(f"💡 **經營影響與法規對策**：{news['對裕豐電機之影響與建議']}")
            st.markdown("---")

    if filtered_count == 0:
        st.info("ℹ️ 目前沒有符合搜尋條件的法規政策快報。")

    # 內嵌 AI 政策合規諮詢（串接後台動態設定的多模型 AI）
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
                        st.error("❌ 找不到有效的 API Key，請先至資訊管理部 API 串接中心設定！")
                    else:
                        if provider == "Google Gemini":
                            import google.generativeai as genai
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel(model_name)
                            res = model.generate_content(f"身為越南外資製造業（裕豐電機工業）的法規與營運顧問，請針對以下問題進行專業評估：{policy_prompt}")
                            st.success("✅ **AI 法規合規評估報告**：")
                            st.write(res.text)
                        elif provider == "OpenAI (GPT-4o)":
                            from openai import OpenAI
                            client = OpenAI(api_key=api_key)
                            completion = client.chat.completions.create(
                                model=model_name,
                                messages=[{"role": "user", "content": f"身為裕豐電機法規顧問：{policy_prompt}"}]
                            )
                            st.success("✅ **AI 法規合規評估報告**：")
                            st.write(completion.choices[0].message.content)
                        else:
                            import anthropic
                            client = anthropic.Anthropic(api_key=api_key)
                            message = client.messages.create(
                                model=model_name,
                                max_tokens=1500,
                                messages=[{"role": "user", "content": f"身為裕豐電機法規顧問：{policy_prompt}"}]
                            )
                            st.success("✅ **AI 法規合規評估報告**：")
                            st.write(message.content[0].text)
                except Exception as e:
                    st.error(f"❌ 呼叫 AI 發生錯誤：{str(e)}")
        else:
            st.warning("⚠️ 請先輸入您的合規諮詢問題！")

# 兼容進入點
def show(engine=None, lang="繁體中文", **kwargs):
    render_vietnam_policy_news_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_vietnam_policy_news_page(engine=engine, lang=lang, **kwargs)
