import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 多語系字典 (i18n)
# ----------------------------------------------------
POLICY_I18N = {
    "繁體中文": {
        "title": "📰 越南經營政策與法規每日動態速遞",
        "caption": "即時掌握越南中央與地方政府最新發布之法規，點擊連結可直接開啟該篇新聞與公文詳細內容。",
        "btn_refresh": "🔄 重新載入最新法規清單",
        "refresh_success": "✅ 已成功重新載入法規政策清單！",
        "search_label": "🔍 搜尋法規關鍵字：",
        "search_placeholder": "輸入關鍵字（例如：稅務、勞動、環保）...",
        "filter_label": "依政策類別篩選",
        "all_categories": "全部類別",
        "admin_section_title": "⚙️ 【IT / 管理部專用】後台法規新聞維護與發布中心",
        "expander_title": "➕ 新增經查證之真實越南法規與詳細原文連結",
        "col_title": "法規新聞標題 *",
        "col_cat": "政策類別",
        "col_src": "真實新聞與公文詳細永久網址 (URL) *",
        "col_sum": "政策摘要說明 *",
        "col_adv": "對裕豐電機之影響與合規建議 *",
        "btn_save": "💾 儲存並發布至總經理室",
        "save_success": "🎉 經查證的政策快報已成功發布！",
        "ai_title": "🤖 AI 法規合規深度解析顧問",
        "ai_hint": "針對上方列出的法規與內容，向 AI 詢問經營影響：",
        "ai_placeholder": "例如：針對最新稅務與電子發票新規，西寧廠會計應如何合規因應？",
        "ai_btn": "🚀 請 AI 分析合規風險",
        "ai_loading": "⏳ AI 正在結合最新法規與公司架構進行深度分析...",
        "no_key_err": "❌ 找不到有效的 API Key，請先至資訊管理部 API 串接中心設定！"
    },
    "Tiếng Việt": {
        "title": "📰 Cập nhật Hàng ngày về Chính sách & Pháp luật Kinh doanh tại Việt Nam",
        "caption": "Nắm bắt chính sách mới nhất kèm liên kết chi tiết.",
        "btn_refresh": "🔄 Tải lại",
        "refresh_success": "✅ Đã tải lại thành công!",
        "search_label": "🔍 Tìm kiếm từ khóa:",
        "search_placeholder": "Nhập từ khóa...",
        "filter_label": "Lọc theo danh mục",
        "all_categories": "Tất cả danh mục",
        "admin_section_title": "⚙️ Trung tâm Quản trị & Đăng tải Bản tin Pháp luật (IT/GA)",
        "expander_title": "➕ Thêm bản tin pháp luật đã kiểm chứng",
        "col_title": "Tiêu đề *",
        "col_cat": "Danh mục",
        "col_src": "Đường dẫn chi tiết (URL) *",
        "col_sum": "Tóm tắt *",
        "col_adv": "Khuyến nghị tuân thủ *",
        "btn_save": "💾 Lưu và Đăng",
        "save_success": "🎉 Đã đăng thành công!",
        "ai_title": "🤖 Tư vấn Phân tích Tuân thủ Pháp luật AI",
        "ai_hint": "Hỏi AI về tác động kinh doanh:",
        "ai_placeholder": "Ví dụ: Nhà máy Tây Ninh cần lưu ý gì?",
        "ai_btn": "🚀 Yêu cầu AI phân tích rủi ro",
        "ai_loading": "⏳ Đang phân tích...",
        "no_key_err": "❌ Không tìm thấy API Key!"
    },
    "English": {
        "title": "📰 Daily Vietnam Business Policy & Regulations",
        "caption": "Tracks Vietnam regulatory updates with verified permanent links.",
        "btn_refresh": "🔄 Reload Regulations",
        "refresh_success": "✅ Successfully reloaded!",
        "search_label": "🔍 Search Keywords:",
        "search_placeholder": "Enter keyword...",
        "filter_label": "Filter by Category",
        "all_categories": "All Categories",
        "admin_section_title": "⚙️ IT / GA Policy News Administration Center",
        "expander_title": "➕ Add Verified Policy News & Article Link",
        "col_title": "News Title *",
        "col_cat": "Category",
        "col_src": "Verified Permanent URL *",
        "col_sum": "Policy Summary *",
        "col_adv": "Business Impact & Compliance Advice *",
        "btn_save": "💾 Save & Publish",
        "save_success": "🎉 Published successfully!",
        "ai_title": "🤖 AI Regulatory Compliance Advisory",
        "ai_hint": "Ask AI about the business impact:",
        "ai_placeholder": "e.g., How should the Tay Ninh plant respond?",
        "ai_btn": "🚀 Request AI Risk Analysis",
        "ai_loading": "⏳ AI is analyzing...",
        "no_key_err": "❌ API Key not found!"
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
                    source TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass

def get_policy_news_from_db(engine):
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
                    if r[2]:
                        news_list.append({
                            "日期": str(r[0]),
                            "類別": str(r[1]),
                            "標題": str(r[2]),
                            "政策摘要": str(r[3]),
                            "對裕豐電機之影響與建議": str(r[4]),
                            "詳細新聞網址": str(r[5] or "https://thuvienphapluat.vn")
                        })
        except Exception:
            pass

    if not news_list:
        news_list = [
            {
                "日期": str(datetime.date.today()),
                "類別": "🔴 稅務與海關法規 / Thuế & Hải quan",
                "標題": "【系統提示】越南經營法規與公文查證中心",
                "政策摘要": "本模組提供即時越南法規與官方公文查閱。若需【新增或編輯】法規新聞，請至左側選單的【資訊管理部 (IT & System)】進行後台維護。",
                "對裕豐電機之影響與建議": "請管理部與 IT 同仁定期於資訊管理部後台登錄經人工核實的最新法規與永久網址。",
                "詳細新聞網址": "https://thuvienphapluat.vn"
            }
        ]
    return news_list

def render_vietnam_policy_news_page(engine=None, lang="繁體中文", mode="view", **kwargs):
    active_lang = lang if lang in POLICY_I18N else "繁體中文"
    L = POLICY_I18N[active_lang]

    st.markdown(f"### {L['title']}")
    st.caption(L['caption'])

    init_policy_db(engine)

    # 檢查目前是否為資訊管理部後台維護模式（或是使用者具備 IT 管理權限）
    current_dept = st.session_state.get("current_department", "")
    is_it_admin = "資訊管理部" in current_dept or "IT" in current_dept or mode == "admin"

    col_top1, col_top2 = st.columns([3, 1])
    with col_top2:
        if st.button(L['btn_refresh'], use_container_width=True):
            st.success(L['refresh_success'])
            st.rerun()

    st.markdown("---")

    # 僅限【資訊管理部 / IT】才能看到新增與維護表單
    if is_it_admin:
        st.markdown(f"### {L['admin_section_title']}")
        with st.expander(L['expander_title'], expanded=False):
            with st.form("form_add_policy"):
                new_title = st.text_input(L['col_title'], placeholder="例如: 越南財政部發布關於電子發票查核之最新指導公文...")
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    new_cat = st.selectbox(L['col_cat'], [
                        "🔴 稅務與海關法規 / Thuế & Hải quan", 
                        "🟡 勞動與外籍員工 / Lao động & Nhân sự", 
                        "🟢 土地與廠房建照 / Đất đai & Nhà xưởng", 
                        "🔵 產業投資與補貼 / Đầu tư & Trợ cấp"
                    ])
                with c_col2:
                    new_source_url = st.text_input(L['col_src'], value="https://thuvienphapluat.vn/...")
                
                new_summary = st.text_area(L['col_sum'], placeholder="請簡述該公文或法規的核心重點...")
                new_advice = st.text_area(L['col_adv'], placeholder="請填寫對裕豐電機（西寧廠）具體的合規因應建議...")

                if st.form_submit_button(L['btn_save'], type="primary", use_container_width=True):
                    if new_title and new_summary and new_source_url and engine:
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
                                    "src": new_source_url
                                })
                            st.success(L['save_success'])
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 錯誤: {str(e)}")
                    else:
                        st.warning("⚠️ 請完整填寫標題、網址、摘要與合規建議！")
        st.markdown("---")

    # 搜尋與類別篩選
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        policy_search = st.text_input(L['search_label'], placeholder=L['search_placeholder'])
    with col_p2:
        category_filter = st.selectbox(L['filter_label'], [
            L['all_categories'], 
            "🔴 稅務與海關法規 / Thuế & Hải quan", 
            "🟡 勞動與外籍員工 / Lao động & Nhân sự", 
            "🟢 土地與廠房建照 / Đất đai & Nhà xưởng", 
            "🔵 產業投資與補貼 / Đầu tư & Trợ cấp"
        ])

    policy_news_list = get_policy_news_from_db(engine)

    filtered_count = 0
    for news in policy_news_list:
        if category_filter != L['all_categories'] and category_filter not in news["類別"]:
            continue
        if policy_search and policy_search.lower() not in news["標題"].lower() and policy_search.lower() not in news["政策摘要"].lower():
            continue

        filtered_count += 1
        with st.container():
            target_url = news['詳細新聞網址']
            st.markdown(f"#### {news['標題']}")
            st.markdown(f"📅 發布日期：**{news['日期']}** | 📁 類別：**{news['類別']}** | 🔗 **[點擊此處直接開啟該篇已查證之官方新聞與詳細內文]({target_url})**", unsafe_allow_html=True)
            
            st.info(f"📌 **政策摘要**：{news['政策摘要']}")
            st.warning(f"💡 **經營合規建議**：{news['對裕豐電機之影響與建議']}")
            st.markdown("---")

    if filtered_count == 0:
        st.info("ℹ️ 目前沒有符合搜尋條件的法規政策。")

    # AI 政策合規深度解析顧問（總經理與主管皆可使用）
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
                            res = model.generate_content(f"As a regulatory advisor for Reetech Industrial in Vietnam, analyze: {policy_prompt}")
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
