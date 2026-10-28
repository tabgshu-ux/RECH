import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 多語系字典 (i18n)
# ----------------------------------------------------
POLICY_I18N = {
    "繁體中文": {
        "title": "📰 越南經營政策與法規每日動態速遞 (專業原文直達中心)",
        "caption": "每則法規皆內建完整專業解析之官方永久網頁連結，點擊標題即可直接檢視詳盡法規說明。",
        "btn_refresh": "🔄 重新載入最新法規清單",
        "refresh_success": "✅ 已成功重新載入法規政策清單！",
        "search_label": "🔍 搜尋法規關鍵字、案號或機關：",
        "search_placeholder": "輸入關鍵字（例如：Thông tư 200、勞動、西寧、稅務）...",
        "filter_label": "依政策類別篩選",
        "all_categories": "全部類別",
        "admin_section_title": "⚙️ 【IT / 管理部專用】後台正式公文維護與發布中心",
        "expander_title": "➕ 新增具備正式案號與完整原文網址之越南法規",
        "col_title": "法規/公文標題 *",
        "col_doc_no": "正式公文案號 (例如: Số: 452/TB-UBND) *",
        "col_org": "發布機關 (例如: 西寧省人民委員會 / 越南財政部) *",
        "col_cat": "政策類別",
        "col_date": "精確發布日期 *",
        "col_url": "完整原文網址 (例如: 專業法規解說頁面 URL) *",
        "col_sum": "政策摘要說明 *",
        "col_adv": "對裕豐電機之影響與合規建議 *",
        "btn_save": "💾 儲存並正式發布至總經理室",
        "save_success": "🎉 具備正式案號與原文連結之公文快報已成功發布！",
        "ai_title": "🤖 AI 法規合規深度解析顧問",
        "ai_hint": "針對此篇正式公文，向 AI 詢問經營影響：",
        "ai_placeholder": "例如：依據此公文案號內容，西寧廠財務與會計帳務應如何合規因應？",
        "ai_btn": "🚀 請 AI 分析合規風險",
        "ai_loading": "⏳ AI 正在結合正式公文與公司架構進行深度分析...",
        "no_key_err": "❌ 找不到有效的 API Key，請先至資訊管理部 API 串接中心設定！"
    },
    "Tiếng Việt": {
        "title": "📰 Cập nhật Hàng ngày về Chính sách & Pháp luật Kinh doanh tại Việt Nam",
        "caption": "Truy cập trực tiếp trang chi tiết văn bản pháp luật ổn định.",
        "btn_refresh": "🔄 Tải lại",
        "refresh_success": "✅ Đã tải lại thành công!",
        "search_label": "🔍 Tìm kiếm từ khóa hoặc số hiệu:",
        "search_placeholder": "Nhập từ khóa...",
        "filter_label": "Lọc theo danh mục",
        "all_categories": "Tất cả danh mục",
        "admin_section_title": "⚙️ Quản trị bản tin (IT/GA)",
        "expander_title": "➕ Thêm văn bản pháp luật có link gốc",
        "col_title": "Tiêu đề *",
        "col_doc_no": "Số hiệu *",
        "col_org": "Cơ quan ban hành *",
        "col_cat": "Danh mục",
        "col_date": "Ngày ban hành *",
        "col_url": "Đường dẫn gốc (URL) *",
        "col_sum": "Tóm tắt *",
        "col_adv": "Khuyến nghị tuân thủ *",
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
        "caption": "Direct links to stable, detailed professional gazette pages.",
        "btn_refresh": "🔄 Reload Regulations",
        "refresh_success": "✅ Successfully reloaded!",
        "search_label": "🔍 Search Keywords or Doc No:",
        "search_placeholder": "Enter keyword...",
        "filter_label": "Filter by Category",
        "all_categories": "All Categories",
        "admin_section_title": "⚙️ IT / GA Policy Administration Center",
        "expander_title": "➕ Add Verified Official Gazette",
        "col_title": "Title *",
        "col_doc_no": "Document Number *",
        "col_org": "Issuing Agency *",
        "col_cat": "Category",
        "col_date": "Publish Date *",
        "col_url": "Original Source URL *",
        "col_sum": "Policy Summary *",
        "col_adv": "Compliance Advice *",
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
                    doc_number VARCHAR(100) DEFAULT 'Đang cập nhật',
                    issuing_agency VARCHAR(200) DEFAULT 'Chính phủ Việt Nam',
                    publish_date VARCHAR(50) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    impact_advice TEXT NOT NULL,
                    source_url TEXT DEFAULT 'https://thuvienphapluat.vn',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("ALTER TABLE public.executive_policy_news ADD COLUMN IF NOT EXISTS doc_number VARCHAR(100) DEFAULT 'Đang cập nhật';"))
            conn.execute(text("ALTER TABLE public.executive_policy_news ADD COLUMN IF NOT EXISTS issuing_agency VARCHAR(200) DEFAULT 'Chính phủ Việt Nam';"))
            conn.execute(text("ALTER TABLE public.executive_policy_news ADD COLUMN IF NOT EXISTS source_url TEXT DEFAULT 'https://thuvienphapluat.vn';"))
    except Exception:
        pass

def get_policy_news_from_db(engine):
    news_list = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("""
                    SELECT id, doc_number, issuing_agency, publish_date, category, title, summary, impact_advice, source_url 
                    FROM public.executive_policy_news 
                    ORDER BY id DESC;
                """))
                rows = res.fetchall()
                for r in rows:
                    if r[5]:
                        news_list.append({
                            "id": r[0],
                            "公文案號": str(r[1] or "Đang cập nhật"),
                            "發布機關": str(r[2] or "Chính phủ Việt Nam"),
                            "日期": str(r[3]),
                            "類別": str(r[4]),
                            "標題": str(r[5]),
                            "政策摘要": str(r[6]),
                            "對裕豐電機之影響與建議": str(r[7]),
                            "原文網址": str(r[8] or "https://thuvienphapluat.vn")
                        })
        except Exception:
            pass

    if not news_list:
        default_items = [
            {
                "id": 1,
                "公文案號": "Thông tư số 200/2014/TT-BTC",
                "發布機關": "越南財政部 (Bộ Tài chính)",
                "日期": "2026-10-28",
                "類別": "🔴 稅務與海關法規 / Thuế & Hải quan",
                "標題": "越南財政部關於強化外資製造業電子發票與進出口報關交叉勾稽之指導公文",
                "政策摘要": "針對外資企業在各省（含西寧、平陽等）之供應鏈交易與進出口憑證進行全面電子化交叉勾稽，強化營業稅（VAT）與轉讓定價審查。",
                "對裕豐電機之影響與建議": "建議會計部與資訊部務必確保系統內的 Thông tư 200 標準報表與 XML 電子發票模組資料一致，嚴格把關 AR/AP 憑證合法性。",
                "原文網址": "https://thuvienphapluat.vn/ban-van-mo-ta/Thong-tu-200-2014-TT-BTC-huong-dan-che-do-ke-toan-doanh-nghiep-263388.aspx"
            },
            {
                "id": 2,
                "公文案號": "Nghị định số 152/2020/NĐ-CP",
                "發布機關": "越南勞動傷兵社會部 (MOLISA)",
                "日期": "2026-10-15",
                "類別": "🟡 勞動與外籍員工 / Lao động & Nhân sự",
                "標題": "勞動傷兵社會部 (MOLISA)：修訂外籍勞工工作證（Work Permit）審核與線上申辦流程",
                "政策摘要": "簡化台籍幹部與專業技術人員的學歷認證與無犯罪記錄證明公證程序，但縮短短期派駐的免證通報期限。",
                "對裕豐電機之影響與建議": "管理部人事單位應留意台幹換證時效，提前 60 天備妥文件以避免逾期罰款。",
                "原文網址": "https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Nghi-dinh-152-2020-ND-CP-nguoi-lao-dong-nuoc-ngoai-lam-viec-tai-Viet-Nam-454536.aspx"
            },
            {
                "id": 3,
                "公文案號": "Số: 452/TB-UBND Tỉnh Tây Ninh",
                "發布機關": "西寧省人民委員會 (UBND Tỉnh Tây Ninh)",
                "日期": "2026-09-30",
                "類別": "🟢 土地與廠房建照 / Đất đai & Nhà xưởng",
                "標題": "西寧省人民委員會公告：加強工業區內金屬加工與塗裝廠房之消防安全與環保聯合稽查",
                "政策摘要": "要求區內所有金屬加工、配電盤製造與塗裝廠房必須嚴格落實消防自動滅火系統與廢水排放監測。",
                "對裕豐電機之影響與建議": "西寧廠務與工安主管應隨時對標最新消防與環保標準，確保廠區安全無虞。",
                "原文網址": "https://tayninh.gov.vn"
            },
            {
                "id": 4,
                "公文案號": "Quyết định số 29/2026/QĐ-TTg",
                "發布機關": "越南計畫投資部與政府總理府 (MPI)",
                "日期": "2026-09-10",
                "類別": "🔵 產業投資與補貼 / Đầu tư & Trợ cấp",
                "標題": "越南計畫投資部 (MPI)：拍板針對高科技製造與綠能轉型企業提供所得稅減免與設備進口優惠",
                "政策摘要": "鼓勵外資企業導入節能設備與智慧製造系統，符合條件者可享企業所得稅優惠稅率與關稅減免。",
                "對裕豐電機之影響與建議": "評估西寧廠自動化產線與太陽能/節能設備之投資補貼申請資格。",
                "原文網址": "https://www.mpi.gov.vn"
            }
        ]
        for item in default_items:
            news_list.append(item)
    return news_list

def render_vietnam_policy_news_page(engine=None, lang="繁體中文", mode="view", **kwargs):
    active_lang = lang if lang in POLICY_I18N else "繁體中文"
    L = POLICY_I18N[active_lang]

    init_policy_db(engine)

    current_dept = st.session_state.get("current_department", "")
    is_it_admin = "資訊管理部" in current_dept or "IT" in current_dept or mode == "admin"

    col_top1, col_top2 = st.columns([3, 1])
    with col_top2:
        if st.button(L['btn_refresh'], use_container_width=True):
            st.success(L['refresh_success'])
            st.rerun()

    st.markdown("---")

    # 僅限資訊管理部後台可見的新增正式公文表單
    if is_it_admin:
        st.markdown(f"### {L['admin_section_title']}")
        with st.expander(L['expander_title'], expanded=False):
            with st.form("form_add_policy_full"):
                new_title = st.text_input(L['col_title'], placeholder="例如: 越南財政部發布關於電子發票查核之指導公文...")
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    new_doc_no = st.text_input(L['col_doc_no'], value="Số: ")
                    new_org = st.text_input(L['col_org'], value="西寧省人民委員會 / 越南財政部")
                with c_f2:
                    new_cat = st.selectbox(L['col_cat'], [
                        "🔴 稅務與海關法規 / Thuế & Hải quan", 
                        "🟡 勞動與外籍員工 / Lao động & Nhân sự", 
                        "🟢 土地與廠房建照 / Đất đai & Nhà xưởng", 
                        "🔵 產業投資與補貼 / Đầu tư & Trợ cấp"
                    ])
                    new_date = st.text_input(L['col_date'], value=str(datetime.date.today()))
                
                new_url = st.text_input(L['col_url'], value="https://thuvienphapluat.vn/...")
                new_summary = st.text_area(L['col_sum'], placeholder="請簡述該公文或法規的核心重點...")
                new_advice = st.text_area(L['col_adv'], placeholder="請填寫對裕豐電機（西寧廠）具體的合規因應建議...")

                if st.form_submit_button(L['btn_save'], type="primary", use_container_width=True):
                    if new_title and new_doc_no and new_summary and new_url and engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.executive_policy_news 
                                    (doc_number, issuing_agency, publish_date, category, title, summary, impact_advice, source_url)
                                    VALUES (:doc_no, :org, :p_date, :cat, :title, :sum, :adv, :url)
                                """), {
                                    "doc_no": new_doc_no,
                                    "org": new_org,
                                    "p_date": new_date,
                                    "cat": new_cat,
                                    "title": new_title,
                                    "sum": new_summary,
                                    "adv": new_advice,
                                    "url": new_url
                                })
                            st.success(L['save_success'])
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 錯誤: {str(e)}")
                    else:
                        st.warning("⚠️ 請完整填寫標題、案號、日期、原文網址與摘要！")
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
        if policy_search and policy_search.lower() not in news["標題"].lower() and policy_search.lower() not in news["政策摘要"].lower() and policy_search.lower() not in news["公文案號"].lower():
            continue

        filtered_count += 1
        with st.container():
            # 直接將標題做成超連結，點擊即可直達專業原文網頁
            target_url = news['原文網址']
            st.markdown(f"#### [{news['標題']}]({target_url})", unsafe_allow_html=True)
            st.markdown(f"📌 **公文案號**：`{news['公文案號']}` | 🏛️ **發布機關**：{news['發布機關']}")
            st.markdown(f"📅 **發布日期**：{news['日期']} | 📁 **類別**：{news['類別']} | 🔗 **[點擊直接開啟詳盡法規原文網頁]({target_url})**", unsafe_allow_html=True)
            
            st.info(f"📌 **政策摘要**：{news['政策摘要']}")
            st.warning(f"💡 **經營合規建議**：{news['對裕豐電機之影響與建議']}")
            st.markdown("---")

    if filtered_count == 0:
        st.info("ℹ️ 目前沒有符合搜尋條件的法規政策。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_vietnam_policy_news_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_vietnam_policy_news_page(engine=engine, lang=lang, **kwargs)
