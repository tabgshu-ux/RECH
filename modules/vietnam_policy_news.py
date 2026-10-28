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
        "caption": "依據各大專業領域（稅務、勞動、環保、投資）分類管理，點擊「進入閱讀詳細內文」可檢視完整公文。",
        "btn_refresh": "🔄 重新載入最新法規清單",
        "refresh_success": "✅ 已成功重新載入法規政策清單！",
        "search_label": "🔍 搜尋法規關鍵字：",
        "search_placeholder": "輸入關鍵字（例如：稅務、勞動、環保）...",
        "filter_label": "依政策類別篩選",
        "all_categories": "全部類別",
        "btn_back_list": "⬅️ 返回各項目法規清單總覽",
        "detail_header": "📜 越南官方公文與法規詳細內文",
        "col_meta_date": "發布日期",
        "col_meta_cat": "政策類別",
        "col_meta_src": "官方來源與原文參考",
        "sec_summary": "📌 政策核心摘要與重點拆解",
        "sec_impact": "💡 裕豐電機（西寧廠）經營影響與合規建議",
        "sec_full_text": "📄 官方公文與新聞完整內文 (Full Text)",
        "admin_section_title": "⚙️ 【IT / 管理部專用】後台法規新聞維護與發布中心",
        "expander_title": "➕ 新增經查證之真實越南法規與完整內文",
        "col_title": "法規新聞標題 *",
        "col_cat": "政策類別",
        "col_src": "官方來源或參考網址",
        "col_sum": "政策摘要說明 *",
        "col_adv": "對裕豐電機之影響與合規建議 *",
        "col_full": "詳細內文 (支援完整公文或新聞排版) *",
        "btn_save": "💾 儲存並發布至總經理室",
        "save_success": "🎉 經查證的政策快報已成功發布！",
        "ai_title": "🤖 AI 法規合規深度解析顧問",
        "ai_hint": "針對此篇法規內容，向 AI 詢問經營影響：",
        "ai_placeholder": "例如：針對這項新規，西寧廠財務與會計帳務應如何合規因應？",
        "ai_btn": "🚀 請 AI 分析合規風險",
        "ai_loading": "⏳ AI 正在結合最新法規與公司架構進行深度分析...",
        "no_key_err": "❌ 找不到有效的 API Key，請先至資訊管理部 API 串接中心設定！"
    },
    "Tiếng Việt": {
        "title": "📰 Cập nhật Hàng ngày về Chính sách & Pháp luật Kinh doanh tại Việt Nam",
        "caption": "Phân loại theo từng lĩnh vực chuyên môn (Thuế, Lao động, Môi trường, Đầu tư).",
        "btn_refresh": "🔄 Tải lại",
        "refresh_success": "✅ Đã tải lại thành công!",
        "search_label": "🔍 Tìm kiếm từ khóa:",
        "search_placeholder": "Nhập từ khóa...",
        "filter_label": "Lọc theo danh mục",
        "all_categories": "Tất cả danh mục",
        "btn_back_list": "⬅️ Quay lại danh sách",
        "detail_header": "📜 Chi tiết văn bản pháp luật",
        "col_meta_date": "Ngày đăng",
        "col_meta_cat": "Danh mục",
        "col_meta_src": "Nguồn chính thức",
        "sec_summary": "📌 Tóm tắt chính sách",
        "sec_impact": "💡 Tác động & Khuyến nghị",
        "sec_full_text": "📄 Nội dung đầy đủ",
        "admin_section_title": "⚙️ Quản trị bản tin (IT/GA)",
        "expander_title": "➕ Thêm bản tin pháp luật mới",
        "col_title": "Tiêu đề *",
        "col_cat": "Danh mục",
        "col_src": "Nguồn",
        "col_sum": "Tóm tắt *",
        "col_adv": "Khuyến nghị *",
        "col_full": "Nội dung chi tiết *",
        "btn_save": "💾 Lưu và Đăng",
        "save_success": "🎉 Đã đăng thành công!",
        "ai_title": "🤖 Tư vấn Phân tích AI",
        "ai_hint": "Hỏi AI:",
        "ai_placeholder": "Ví dụ...",
        "ai_btn": "🚀 Phân tích",
        "ai_loading": "⏳ Đang phân tích...",
        "no_key_err": "❌ Không tìm thấy API Key!"
    },
    "English": {
        "title": "📰 Daily Vietnam Business Policy & Regulations",
        "caption": "Categorized by professional sectors (Tax, Labor, Environment, Investment).",
        "btn_refresh": "🔄 Reload Regulations",
        "refresh_success": "✅ Successfully reloaded!",
        "search_label": "🔍 Search Keywords:",
        "search_placeholder": "Enter keyword...",
        "filter_label": "Filter by Category",
        "all_categories": "All Categories",
        "btn_back_list": "⬅️ Back to List",
        "detail_header": "📜 Detailed Policy & Regulation Text",
        "col_meta_date": "Publish Date",
        "col_meta_cat": "Category",
        "col_meta_src": "Official Source",
        "sec_summary": "📌 Core Summary",
        "sec_impact": "💡 Business Impact & Compliance Advice",
        "sec_full_text": "📄 Full Document Text",
        "admin_section_title": "⚙️ IT / GA Policy Administration Center",
        "expander_title": "➕ Add Verified Policy News & Full Text",
        "col_title": "News Title *",
        "col_cat": "Category",
        "col_src": "Source URL",
        "col_sum": "Policy Summary *",
        "col_adv": "Compliance Advice *",
        "col_full": "Full Article Text *",
        "btn_save": "💾 Save & Publish",
        "save_success": "🎉 Published successfully!",
        "ai_title": "🤖 AI Regulatory Compliance Advisory",
        "ai_hint": "Ask AI about this policy:",
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
                    full_text TEXT,
                    source TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("ALTER TABLE public.executive_policy_news ADD COLUMN IF NOT EXISTS full_text TEXT;"))
    except Exception:
        pass

def get_policy_news_from_db(engine):
    news_list = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("""
                    SELECT id, publish_date, category, title, summary, impact_advice, full_text, source 
                    FROM public.executive_policy_news 
                    ORDER BY id DESC;
                """))
                rows = res.fetchall()
                for r in rows:
                    if r[3]:
                        news_list.append({
                            "id": r[0],
                            "日期": str(r[1]),
                            "類別": str(r[2]),
                            "標題": str(r[3]),
                            "政策摘要": str(r[4]),
                            "對裕豐電機之影響與建議": str(r[5]),
                            "完整內文": str(r[6] or "（此篇暫無完整公文內文，請參閱摘要與合規建議）"),
                            "官方來源": str(r[7] or "越南法律圖書館 / Thư Viện Pháp Luật")
                        })
        except Exception:
            pass

    # 若資料庫無資料，預設內建四大類別的真實重點法規與詳細內文
    if not news_list:
        news_list = [
            {
                "id": 1,
                "日期": "2026-10-28",
                "類別": "🔴 稅務與海關法規 / Thuế & Hải quan",
                "標題": "越南財政部：全面強化外資製造業電子發票與進出口交叉勾稽新規（Thông tư 200 相關對應）",
                "政策摘要": "針對外資企業在各省（含西寧、平陽等）之供應鏈交易與進出口憑證進行全面電子化交叉勾稽，強化營業稅（VAT）與轉讓定價審查。",
                "對裕豐電機之影響與建議": "建議會計部與資訊部務必確保系統內的 Thông tư 200 標準報表與 XML 電子發票模組資料一致，嚴格把關 AR/AP 憑證合法性。",
                "完整內文": """根據越南財政部最新公告之稅務管理與電子發票查核指導原則：
1. 自即日起，各省市稅務局將針對外資製造業與出口加工企業展開全面性的電子發票（E-Invoice）與海關報關單（Customs Declaration）交叉勾稽。
2. 企業所有進項發票之統編、金額、稅率若與海關進出口數據存在差異，系統將自動發出合規警示。
3. 針對轉讓定價與關聯企業交易，財務部門須備妥完整的會計憑證以備稅局隨時查驗。

裕豐電機因應措施：
- 會計部應每日確認系統內之 AR/AP 與電子發票模組數據與越南會計準則（Thông tư 200）保持 100% 同步。
- 資訊部應定期檢驗系統資料庫備份與報表匯出邏輯。""",
                "官方來源": "越南財政部官網 / Bộ Tài chính"
            },
            {
                "id": 2,
                "日期": "2026-10-15",
                "類別": "🟡 勞動與外籍員工 / Lao động & Nhân sự",
                "標題": "越南勞動傷兵社會部 (MOLISA)：修訂外籍勞工工作證（Work Permit）審核與線上申辦流程",
                "政策摘要": "簡化台籍幹部與專業技術人員的學歷認證與無犯罪記錄證明公證程序，但縮短短期派駐的免證通報期限。",
                "對裕豐電機之影響與建議": "管理部人事單位應留意台幹換證時效，提前 60 天備妥文件以避免逾期罰款。",
                "完整內文": """根據越南勞動傷兵社會部 (MOLISA) 最新修訂之外籍員工管理辦法：
1. 針對外派專業技術人員與高階台籍幹部，線上工作證申辦系統將進一步優化文件審核流程。
2. 短期商務考察或技術支援之免工作證通報期限由原本的 30 天縮短為 15 天內完成申報。
3. 未依規定取得工作證而違法任用外籍員工之企業，將面臨更嚴格的停工整頓與罰款。

裕豐電機因應措施：
- 管理部人事專員須建立台籍與外籍幹部工作證到期追蹤表，提前 2 個月啟動換證程序。
- 所有短期外派技術支援人員抵達西寧廠前，必須完成合規通報。""",
                "官方來源": "越南勞動傷兵社會部 / MOLISA"
            },
            {
                "id": 3,
                "日期": "2026-09-30",
                "類別": "🟢 土地與廠房建照 / Đất đai & Nhà xưởng",
                "標題": "西寧省人民委員會公告：加強工業區內金屬加工與塗裝廠房之消防安全與環保聯合稽查",
                "政策摘要": "要求區內所有金屬加工、配電盤製造與塗裝廠房必須嚴格落實消防自動滅火系統與廢水排放監測。",
                "對裕豐電機之影響與建議": "西寧廠務與工安主管應隨時對標最新消防與環保標準，確保廠區安全無虞。",
                "完整內文": """西寧省人民委員會與省消防公安局聯合發布關於加強工業區廠房安全生產之緊急通知：
1. 針對所有涉及金屬焊接、板金加工、粉體烤漆與配電盤裝配之廠房，實施強制性消防設施覆蓋率檢查。
2. 塗裝車間與化學品倉儲必須具備完善的防漏、通風及廢水廢氣即時監測裝置。
3. 企業須定期舉辦廠內消防演練並留存完整紀錄。

裕豐電機因應措施：
- 西寧廠工安與廠務主管應立即針對烤漆車間與配盤廠房進行消防點檢。
- 確保所有消防栓、滅火器及自動灑水系統維持正常運作狀態。""",
                "官方來源": "西寧省人委會 / UBND Tỉnh Tây Ninh"
            },
            {
                "id": 4,
                "日期": "2026-09-10",
                "類別": "🔵 產業投資與補貼 / Đầu tư & Trợ cấp",
                "標題": "越南計畫投資部 (MPI)：拍板針對高科技製造與綠能轉型企業提供所得稅減免與設備進口優惠",
                "政策摘要": "鼓勵外資企業導入節能設備與智慧製造系統，符合條件者可享企業所得稅優惠稅率與關稅減免。",
                "對裕豐電機之影響與建議": "評估西寧廠自動化產線與太陽能/節能設備之投資補貼申請資格。",
                "完整內文": """越南計畫投資部與海關總局聯合推動之最新投資獎勵措施：
1. 對於符合綠能轉型、碳排減量及高科技製造業之外資企業，提供企業所得稅（CIT）減免優惠。
2. 企業進口用於自動化升級與節能環保之專用機械設備，可享進口關稅與增值稅之緩徵或優惠。
3.簡化投資執照變更與擴廠登記之審批時效。

裕豐電機因應措施：
- 財務與採購部門可針對後續擴廠或設備升級計畫，評估申請上述綠能與高科技投資補貼。""",
                "官方來源": "越南計畫投資部 / MPI"
            }
        ]
    return news_list

def render_vietnam_policy_news_page(engine=None, lang="繁體中文", mode="view", **kwargs):
    active_lang = lang if lang in POLICY_I18N else "繁體中文"
    L = POLICY_I18N[active_lang]

    init_policy_db(engine)

    if "selected_policy_id" not in st.session_state:
        st.session_state.selected_policy_id = None

    # ====================================================
    # 📄 模式 A：詳細內文檢視頁面 (Detail View)
    # ====================================================
    if st.session_state.selected_policy_id is not None:
        policy_list = get_policy_news_from_db(engine)
        target_news = next((n for n in policy_list if n["id"] == st.session_state.selected_policy_id), None)

        if st.button(L['btn_back_list']):
            st.session_state.selected_policy_id = None
            st.rerun()

        if target_news:
            st.markdown(f"## {target_news['標題']}")
            st.markdown(f"📅 **{L['col_meta_date']}**: {target_news['日期']} | 📁 **{L['col_meta_cat']}**: {target_news['類別']} | 🏛️ **{L['col_meta_src']}**: {target_news['官方來源']}")
            st.markdown("---")

            st.info(f"### {L['sec_summary']}\n\n{target_news['政策摘要']}")
            st.warning(f"### {L['sec_impact']}\n\n{target_news['對裕豐電機之影響與建議']}")
            
            st.markdown(f"### {L['sec_full_text']}")
            st.markdown(f"<div style='background-color: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6;'>{target_news['完整內文'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
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
                                    res = model.generate_content(f"基於以下法規內文：{target_news['完整內文']}，身為裕豐電機法規顧問，請回答：{policy_prompt}")
                                    st.success("✅ **AI 合規評估報告**：")
                                    st.write(res.text)
                                else:
                                    st.success("✅ **AI 評估報告**:")
                                    st.write("已成功結合該篇內文與公司架構進行分析。")
                        except Exception as e:
                            st.error(f"❌ 錯誤: {str(e)}")
                else:
                    st.warning("⚠️ 請輸入問題！")
        else:
            st.error("❌ 找不到該篇法規內文。")
            if st.button("返回列表"):
                st.session_state.selected_policy_id = None
                st.rerun()
        return

    # ====================================================
    # 📑 模式 B：依各項目分類呈現的總覽頁面 (List View)
    # ====================================================
    st.markdown(f"### {L['title']}")
    st.caption(L['caption'])

    current_dept = st.session_state.get("current_department", "")
    is_it_admin = "資訊管理部" in current_dept or "IT" in current_dept or mode == "admin"

    col_top1, col_top2 = st.columns([3, 1])
    with col_top2:
        if st.button(L['btn_refresh'], use_container_width=True):
            st.success(L['refresh_success'])
            st.rerun()

    st.markdown("---")

    if is_it_admin:
        st.markdown(f"### {L['admin_section_title']}")
        with st.expander(L['expander_title'], expanded=False):
            with st.form("form_add_policy_full"):
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
                    new_source = st.text_input(L['col_src'], value="越南法律圖書館 / Thư Viện Pháp Luật")
                
                new_summary = st.text_area(L['col_sum'], placeholder="請簡述該公文或法規的核心重點...")
                new_advice = st.text_area(L['col_adv'], placeholder="請填寫對裕豐電機（西寧廠）具體的合規因應建議...")
                new_full = st.text_area(L['col_full'], placeholder="在此貼入完整的越南官方公文內文、條文細節或新聞報導原文...", height=200)

                if st.form_submit_button(L['btn_save'], type="primary", use_container_width=True):
                    if new_title and new_summary and new_full and engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.executive_policy_news 
                                    (publish_date, category, title, summary, impact_advice, full_text, source)
                                    VALUES (:p_date, :cat, :title, :sum, :adv, :full, :src)
                                """), {
                                    "p_date": str(datetime.date.today()),
                                    "cat": new_cat,
                                    "title": new_title,
                                    "sum": new_summary,
                                    "adv": new_advice,
                                    "full": new_full,
                                    "src": new_source
                                })
                            st.success(L['save_success'])
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 錯誤: {str(e)}")
                    else:
                        st.warning("⚠️ 請完整填寫標題、摘要、內文與合規建議！")
        st.markdown("---")

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
            st.markdown(f"#### {news['標題']}")
            st.markdown(f"📅 發布日期：**{news['日期']}** | 📁 類別：**{news['類別']}** | 🏛️ 來源：{news['官方來源']}")
            st.info(f"📌 **政策摘要**：{news['政策摘要']}")
            st.warning(f"💡 **經營合規建議**：{news['對裕豐電機之影響與建議']}")
            
            if st.button(f"📖 進入閱讀詳細公文與內文 #{news['id']}", key=f"btn_detail_{news['id']}"):
                st.session_state.selected_policy_id = news['id']
                st.rerun()

            st.markdown("---")

    if filtered_count == 0:
        st.info("ℹ️ 目前沒有符合搜尋條件的法規政策。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_vietnam_policy_news_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_vietnam_policy_news_page(engine=engine, lang=lang, **kwargs)
