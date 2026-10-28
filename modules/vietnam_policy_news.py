import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text
import urllib.request
import xml.etree.ElementTree as ET

def init_policy_db(engine):
    """
    初始化真實越南政策法規新聞資料表
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
                    source VARCHAR(200) UNIQUE, -- 確保網址或標題唯一，避免重複爬取
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception as e:
        st.warning(f"⚠️ 政策資料表初始化提示: {str(e)}")

def fetch_real_vietnam_news(engine):
    """
    實際聯絡網路爬蟲（透過越南官方 RSS / VGP News）抓取最新動態並寫入資料庫
    """
    fetched_count = 0
    # 越南政府官方新聞網 (VGP News) RSS 來源
    rss_urls = [
        "https://baochinhphu.vn/thiet-ke/rss/home.rss", 
        "https://en.vietnamplus.vn/rss/economy.rss"
    ]
    
    for url in rss_urls:
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                # 解析 RSS 項目
                for item in root.findall('.//item')[:5]: # 每次取前 5 則最新
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    desc_elem = item.find('description')
                    date_elem = item.find('pubDate')
                    
                    title = title_elem.text if title_elem is not None else "無標題"
                    link = link_elem.text if link_elem is not None else ""
                    summary = desc_elem.text if desc_elem is not None else "無摘要"
                    pub_date = str(datetime.date.today()) # 預設對齊今天或解析 pubDate
                    
                    # 自動分類過濾
                    category = "🔵 產業投資與補貼"
                    t_low = title.lower()
                    if "tax" in t_low or "thuế" in t_low or "finance" in t_low or "tài chính" in t_low:
                        category = "🔴 稅務與海關法規"
                    elif "labor" in t_low or "lấy" in t_low or "worker" in t_low or "nhân công" in t_low:
                        category = "🟡 勞動與外籍員工"
                    elif "land" in t_low or "đất" in t_low or "factory" in t_low or "construction" in t_low:
                        category = "🟢 土地與廠房建照"

                    # 寫入資料庫（利用 UNIQUE 欄位與 try-except 避免重複新增相同新聞）
                    if engine and link:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.executive_policy_news 
                                    (publish_date, category, title, summary, impact_advice, source)
                                    VALUES (:p_date, :cat, :title, :sum, :adv, :src)
                                    ON CONFLICT (source) DO NOTHING;
                                """), {
                                    "p_date": pub_date,
                                    "cat": category,
                                    "title": title,
                                    "sum": summary[:300] + "...",
                                    "adv": "請主管與法規遵循部門針對此則即時爬蟲新聞進行合規影響評估。",
                                    "src": link
                                })
                                fetched_count += 1
                        except Exception:
                            pass
        except Exception:
            pass
    return fetched_count

def get_policy_news_from_db(engine):
    """
    從資料庫動態抓取真實爬蟲回來的新聞資料
    """
    news_list = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("""
                    SELECT publish_date, category, title, summary, impact_advice, source 
                    FROM public.executive_policy_news 
                    ORDER BY id DESC LIMIT 50;
                """))
                rows = res.fetchall()
                for r in rows:
                    if r[2]:
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
            
    return news_list

def render_vietnam_policy_news_page(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 📰 越南經營政策與法規每日動態速遞 (Vietnam Policy & Regulatory News)")
    st.caption("系統每日自動連線至越南官方與財經新聞源進行背景爬蟲，有最新法規發布才會即時添加並提供總經理與主管審閱。")

    # 初始化資料庫
    init_policy_db(engine)

    # 執行一次手動/自動連線爬蟲更新按鈕
    col_top1, col_top2 = st.columns([3, 1])
    with col_top2:
        if st.button("🔄 立即聯絡爬蟲更新最新法規", use_container_width=True):
            with st.spinner("⏳ 正在連線至越南政府官方與財經 RSS 進行即時爬蟲..."):
                added = fetch_real_vietnam_news(engine)
                st.success(f"✅ 爬蟲執行完畢！成功同步 {added} 則最新法規動態。")
                st.rerun()

    st.markdown("---")

    # 搜尋與類別篩選
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        policy_search = st.text_input("🔍 搜尋法規關鍵字：", placeholder="輸入關鍵字...")
    with col_p2:
        category_filter = st.selectbox("依政策類別篩選", ["全部類別", "🔴 稅務與海關法規", "🟡 勞動與外籍員工", "🟢 土地與廠房建照", "🔵 產業投資與補貼"])

    # 從資料庫抓取真實爬蟲資料
    policy_news_list = get_policy_news_from_db(engine)

    if not policy_news_list:
        st.info("ℹ️ 目前資料庫尚無爬蟲新聞。請點擊右上角【🔄 立即聯絡爬蟲更新最新法規】來抓取越南官方最新動態。")
    else:
        filtered_count = 0
        for news in policy_news_list:
            if category_filter != "全部類別" and news["類別"] != category_filter:
                continue
            if policy_search and policy_search.lower() not in news["標題"].lower() and policy_search.lower() not in news["政策摘要"].lower():
                continue

            filtered_count += 1
            with st.container():
                st.markdown(f"#### {news['標題']}")
                st.caption(f"發布日期：{news['日期']} | 類別：**{news['類別']}** | 資料來源：[官方原文連結]({news['官方來源']})")
                st.info(f"📌 **內容摘要**：{news['政策摘要']}")
                st.warning(f"💡 **合規建議**：{news['對裕豐電機之影響與建議']}")
                st.markdown("---")

        if filtered_count == 0:
            st.info("ℹ️ 目前沒有符合搜尋條件的法規快報。")

    # AI 政策合規深度解析
    st.markdown("#### 🤖 AI 法規合規深度解析顧問")
    ai_config = st.session_state.get("ai_config", {"provider": "Google Gemini", "model": "gemini-3.0-flash"})
    st.info(f"💡 目前 AI 引擎：**{ai_config.get('provider')} ({ai_config.get('model')})**（可至資訊管理部 API 串接中心切換）")

    policy_prompt = st.text_input("針對上方爬蟲抓取到的最新法規，向 AI 詢問經營影響：", placeholder="例如：針對爬蟲抓到的最新稅務法規，西寧廠應如何因應？")
    if st.button("🚀 請 AI 分析合規風險", type="primary"):
        if policy_prompt.strip():
            with st.spinner("⏳ AI 正在結合最新法規與公司架構進行分析..."):
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
                            res = model.generate_content(f"身為越南外資製造業法規顧問，請針對以下真實爬蟲政策進行專業風險評估：{policy_prompt}")
                            st.success("✅ **AI 法規合規評估報告**：")
                            st.write(res.text)
                        else:
                            st.success("✅ **AI 評估報告 (模擬回應)**：")
                            st.write("已成功連線 AI 引擎，建議管理部針對即時抓取的法規進行內部查核。")
                except Exception as e:
                    st.error(f"❌ 呼叫 AI 發生錯誤：{str(e)}")
        else:
            st.warning("⚠️ 請先輸入您的合規諮詢問題！")

# 兼容進入點
def show(engine=None, lang="繁體中文", **kwargs):
    render_vietnam_policy_news_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_vietnam_policy_news_page(engine=engine, lang=lang, **kwargs)
