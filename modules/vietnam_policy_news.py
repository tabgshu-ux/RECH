import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text
import urllib.request
import xml.etree.ElementTree as ET

# ----------------------------------------------------
# 🌐 多語系字典 (i18n)
# ----------------------------------------------------
POLICY_I18N = {
    "繁體中文": {
        "title": "📰 越南經營政策與法規每日動態速遞",
        "caption": "系統每日自動連線至越南官方與財經新聞源進行背景爬蟲，有最新法規發布才會即時添加並提供總經理與主管審閱。",
        "btn_crawl": "🔄 立即聯絡爬蟲更新最新法規",
        "crawling_msg": "⏳ 正在連線至越南政府官方與財經 RSS 進行即時爬蟲...",
        "crawl_success": "✅ 成功同步最新法規動態！",
        "search_label": "🔍 搜尋法規關鍵字：",
        "search_placeholder": "輸入關鍵字...",
        "filter_label": "依政策類別篩選",
        "all_categories": "全部類別",
        "no_data": "ℹ️ 目前資料庫尚無爬蟲新聞。請點擊右上角按鈕抓取最新動態。",
        "ai_title": "🤖 AI 法規合規深度解析顧問",
        "ai_hint": "針對上方爬蟲抓取到的最新法規，向 AI 詢問經營影響：",
        "ai_placeholder": "例如：針對爬蟲抓到的最新稅務法規，西寧廠應如何因應？",
        "ai_btn": "🚀 請 AI 分析合規風險",
        "ai_loading": "⏳ AI 正在結合最新法規與公司架構進行分析...",
        "no_key_err": "❌ 找不到有效的 API Key，請先至資訊管理部 API 串接中心設定！"
    },
    "Tiếng Việt": {
        "title": "📰 Cập nhật Hàng ngày về Chính sách & Pháp luật Kinh doanh tại Việt Nam",
        "caption": "Hệ thống tự động kết nối nguồn tin chính thức và tài chính Việt Nam, chỉ cập nhật khi có quy định mới nhất.",
        "btn_crawl": "🔄 Cập nhật quy định mới qua Web Crawl",
        "crawling_msg": "⏳ Đang kết nối RSS chính phủ Việt Nam...",
        "crawl_success": "✅ Đã đồng bộ thông tin mới thành công!",
        "search_label": "🔍 Tìm kiếm từ khóa:",
        "search_placeholder": "Nhập từ khóa...",
        "filter_label": "Lọc theo danh mục",
        "all_categories": "Tất cả danh mục",
        "no_data": "ℹ️ Chưa có tin tức. Vui lòng bấm nút phía trên để cập nhật.",
        "ai_title": "🤖 Tư vấn Phân tích Tuân thủ Pháp luật AI",
        "ai_hint": "Hỏi AI về tác động kinh doanh của các quy định mới:",
        "ai_placeholder": "Ví dụ: Nhà máy Tây Ninh cần ứng phó thế nào với quy định thuế mới?",
        "ai_btn": "🚀 Yêu cầu AI phân tích rủi ro",
        "ai_loading": "⏳ AI đang phân tích...",
        "no_key_err": "❌ Không tìm thấy API Key, vui lòng cấu hình tại Trung tâm API!"
    },
    "English": {
        "title": "📰 Daily Vietnam Business Policy & Regulations",
        "caption": "Automatically crawls official Vietnam news and regulatory sources daily for management review.",
        "btn_crawl": "🔄 Update Latest Regulations via Crawler",
        "crawling_msg": "⏳ Connecting to Vietnam official RSS sources...",
        "crawl_success": "✅ Successfully synchronized latest regulations!",
        "search_label": "🔍 Search Keywords:",
        "search_placeholder": "Enter keyword...",
        "filter_label": "Filter by Category",
        "all_categories": "All Categories",
        "no_data": "ℹ️ No news available. Click the button above to fetch latest updates.",
        "ai_title": "🤖 AI Regulatory Compliance Advisory",
        "ai_hint": "Ask AI about the business impact of the latest crawled regulations:",
        "ai_placeholder": "e.g., How should the Tay Ninh plant respond to new tax regulations?",
        "ai_btn": "🚀 Request AI Risk Analysis",
        "ai_loading": "⏳ AI is analyzing with company context...",
        "no_key_err": "❌ API Key not found. Please configure it in the API Integration Hub!"
    }
}

def init_policy_db(engine):
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
                    source VARCHAR(200) UNIQUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass

def fetch_real_vietnam_news(engine):
    fetched_count = 0
    rss_urls = [
        "https://baochinhphu.vn/thiet-ke/rss/home.rss", 
        "https://en.vietnamplus.vn/rss/economy.rss"
    ]
    for url in rss_urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                root = ET.fromstring(response.read())
                for item in root.findall('.//item')[:5]:
                    title = item.find('title').text if item.find('title') is not None else "No Title"
                    link = item.find('link').text if item.find('link') is not None else ""
                    summary = item.find('description').text if item.find('description') is not None else "No Summary"
                    pub_date = str(datetime.date.today())
                    
                    category = "🔵 產業投資與補貼 / Đầu tư & Trợ cấp"
                    t_low = title.lower()
                    if "tax" in t_low or "thuế" in t_low or "finance" in t_low or "tài chính" in t_low:
                        category = "🔴 稅務與海關法規 / Thuế & Hải quan"
                    elif "labor" in t_low or "lấy" in t_low or "worker" in t_low:
                        category = "🟡 勞動與外籍員工 / Lao động & Nhân sự"
                    elif "land" in t_low or "đất" in t_low or "factory" in t_low:
                        category = "🟢 土地與廠房建照 / Đất đai & Nhà xưởng"

                    if engine and link:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.executive_policy_news 
                                    (publish_date, category, title, summary, impact_advice, source)
                                    VALUES (:p_date, :cat, :title, :sum, :adv, :src)
                                    ON CONFLICT (source) DO NOTHING;
                                """), {
                                    "p_date": pub_date, "cat": category, "title": title,
                                    "sum": summary[:300] + "...", "adv": "請主管與法規部門評估合規影響 / Vui lòng đánh giá tác động tuân thủ.", "src": link
                                })
                                fetched_count += 1
                        except Exception:
                            pass
        except Exception:
            pass
    return fetched_count

def get_policy_news_from_db(engine):
    news_list = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("""
                    SELECT publish_date, category, title, summary, impact_advice, source 
                    FROM public.executive_policy_news 
                    ORDER BY id DESC LIMIT 50;
                """))
                for r in res.fetchall():
                    if r[2]:
                        news_list.append({
                            "日期": str(r[0]), "類別": str(r[1]), "標題": str(r[2]),
                            "政策摘要": str(r[3]), "對裕豐電機之影響與建議": str(r[4]), "官方來源": str(r[5] or "")
                        })
        except Exception:
            pass
    return news_list

def render_vietnam_policy_news_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = POLICY_I18N.get(active_lang, POLICY_I18N["繁體中文"])

    st.markdown(f"### {L['title']}")
    st.caption(L['caption'])

    init_policy_db(engine)

    col_top1, col_top2 = st.columns([3, 1])
    with col_top2:
        if st.button(L['btn_crawl'], use_container_width=True):
            with st.spinner(L['crawling_msg']):
                added = fetch_real_vietnam_news(engine)
                st.success(f"{L['crawl_success']} (+{added})")
                st.rerun()

    st.markdown("---")

    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        policy_search = st.text_input(L['search_label'], placeholder=L['search_placeholder'])
    with col_p2:
        category_filter = st.selectbox(L['filter_label'], [L['all_categories'], "🔴 稅務與海關法規 / Thuế & Hải quan", "🟡 勞動與外籍員工 / Lao động & Nhân sự", "🟢 土地與廠房建照 / Đất đai & Nhà xưởng", "🔵 產業投資與補貼 / Đầu tư & Trợ cấp"])

    policy_news_list = get_policy_news_from_db(engine)

    if not policy_news_list:
        st.info(L['no_data'])
    else:
        filtered_count = 0
        for news in policy_news_list:
            if category_filter != L['all_categories'] and category_filter not in news["類別"]:
                continue
            if policy_search and policy_search.lower() not in news["標題"].lower() and policy_search.lower() not in news["政策摘要"].lower():
                continue

            filtered_count += 1
            with st.container():
                st.markdown(f"#### {news['標題']}")
                st.caption(f"Date: {news['日期']} | Category: **{news['類別']}** | Source: [Link]({news['官方來源']})")
                st.info(f"📌 **Summary**: {news['政策摘要']}")
                st.warning(f"💡 **Compliance Advice**: {news['對裕豐電機之影響與建議']}")
                st.markdown("---")

        if filtered_count == 0:
            st.info("ℹ️ No matching policy news found.")

    st.markdown(f"#### {L['ai_title']}")
    ai_config = st.session_state.get("ai_config", {"provider": "Google Gemini", "model": "gemini-3.0-flash"})
    st.info(f"💡 AI Engine: **{ai_config.get('provider')} ({ai_config.get('model')})**")

    policy_prompt = st.text_input(L['ai_hint'], placeholder=L['ai_placeholder'])
    if st.button(L['ai_btn'], type="primary"):
        if policy_prompt.strip():
            with st.spinner(L['ai_loading']):
                try:
                    api_key = ai_config.get("api_key") or st.secrets.get("GEMINI_API_KEY", "")
                    provider = ai_config.get("provider", "Google Gemini")
                    model_name = ai_config.get("model", "gemini-3.0-flash")

                    if not api_key:
                        st.error(L['no_key_err'])
                    else:
                        if provider == "Google Gemini":
                            import google.generativeai as genai
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel(model_name)
                            res = model.generate_content(f"As a regulatory advisor for Reetech Industrial, analyze: {policy_prompt}")
                            st.success("✅ **AI Compliance Assessment Report**: ")
                            st.write(res.text)
                        else:
                            st.success("✅ **AI Assessment (Mock)**:")
                            st.write("Successfully connected to AI engine.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter your query!")

def show(engine=None, lang="繁體中文", **kwargs):
    render_vietnam_policy_news_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_vietnam_policy_news_page(engine=engine, lang=lang, **kwargs)
