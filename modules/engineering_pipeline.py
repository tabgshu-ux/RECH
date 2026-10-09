import streamlit as st
import pandas as pd
import datetime

def render_engineering_page(engine=None, lang="繁體中文", **kwargs):
    # 多語言字典
    texts = {
        "繁體中文": {
            "title": "⚡ 裕豐電機工業 - 工程管理中心與設計部門",
            "caption": "涵蓋工程報價系統、工程驗收與進度追蹤（連動財務應收帳款 AR）、現場日報表與設計圖庫 Storage，以及 AI 現場照片辨識與證照預警。",
            "sub1": "⚡ [工程] 配電盤與工程專案報價",
            "sub2": "⚡ [工程] 工程驗收與進度追蹤",
            "sub3": "⚡ [工程] 現場工程日報表與出工統計",
            "sub4": "🤖 [工程] AI 施工照片智慧辨識與歸檔",
            "sub5": "⚠️ [工程] 分包商與專業證照到期預警",
            "sub6": "🎨 [設計] 配電盤電氣與機構設計圖庫 Storage"
        },
        "Tiếng Việt": {
            "title": "⚡ Công ty TNHH Kỹ thuật Điện Reetech - Trung tâm Kỹ thuật",
            "caption": "Hệ thống báo giá, tiến độ nghiệm thu, nhật ký công trình, kho lưu trữ và AI nhận diện ảnh / cảnh báo chứng chỉ.",
            "sub1": "⚡ [KT] Báo giá tủ điện & Dự án",
            "sub2": "⚡ [KT] Theo dõi tiến độ & Nghiệm thu",
            "sub3": "⚡ [KT] Nhật ký công trình & Nhân công",
            "sub4": "🤖 [KT] AI Nhận diện & Lưu trữ ảnh thi công",
            "sub5": "⚠️ [KT] Cảnh báo hết hạn chứng chỉ",
            "sub6": "🎨 [TK] Kho bản vẽ thiết kế tủ điện Storage"
        },
        "English": {
            "title": "⚡ Reetech Industrial - Engineering Management Center",
            "caption": "Quotation, project milestone tracking, daily site reports, design storage, AI photo archiving, and license alerts.",
            "sub1": "⚡ [Eng] Quotation & Project Pricing",
            "sub2": "⚡ [Eng] Acceptance & Progress Tracking",
            "sub3": "⚡ [Eng] Daily Site Reports & Labor",
            "sub4": "🤖 [Eng] AI Field Photo Recognition & Archiving",
            "sub5": "⚠️ [Eng] Subcontractor & License Expiry Alerts",
            "sub6": "🎨 [Design] Electrical & Mechanical Drawing Storage"
        }
    }

    active_lang = lang if lang in texts else "繁體中文"
    t = texts[active_lang]

    st.title(t["title"])
    st.caption(t["caption"])

    # 初始化工程資料庫 (含證照與AI照片庫)
    if "engineering_projects_db" not in st.session_state:
        st.session_state.engineering_projects_db = [
            {"proj_code": "PRJ-TN-2026-01", "proj_name": "西寧廠高壓配電盤與消防管線擴建工程", "factory": "西寧廠 (Tay Ninh)", "budget": 1200000000, "status": "進行中 (Active)"},
            {"proj_code": "PRJ-HP-2026-02", "proj_name": "海防廠無塵室空調與照明管線配置", "factory": "海防廠 (Hai Phong)", "budget": 850000000, "status": "進行中 (Active)"}
        ]

    if "license_db" not in st.session_state:
        st.session_state.license_db = [
            {"emp_id": "EMP-001", "name": "張董事長", "license_name": "甲種電匠 (Class A Electrician)", "issue_date": "2023-01-10", "expiry_date": "2026-10-15", "status": "🔴 30天內即將到期 (Expiring Soon)"},
            {"emp_id": "VN-002", "name": "Nguyễn Văn Quý", "license_name": "乙種電匠 (Class B Electrician)", "issue_date": "2022-05-20", "expiry_date": "2027-05-20", "status": "🟢 有效 (Valid)"},
            {"emp_id": "VN-003", "name": "Trần Văn Nam", "license_name": "自來水管配管工 (Plumbing Specialist)", "issue_date": "2021-03-12", "expiry_date": "2026-09-30", "status": "❌ 已過期 (Expired - Action Required)"}
        ]

    if "ai_photo_archive_db" not in st.session_state:
        st.session_state.ai_photo_archive_db = [
            {"photo_id": "IMG-8821", "proj": "PRJ-TN-2026-01", "category": "配電盤配線 (Electrical Panel)", "ai_tag": "🟢 規格相符 / 壓接良好", "uploader": "現場工程師 (李佑銘)", "time": "2026-10-08 14:20"}
        ]

    if "drawing_storage_db" not in st.session_state:
        st.session_state.drawing_storage_db = [
            {"drawing_no": "DWG-01", "proj_name": "越南新順電子廠", "file_name": "MSB_2000A.pdf", "upload_time": "2026-10-01", "uploader": "An"}
        ]

    # 🎯 側邊欄子部門導航列（完全符合您原有的 UI 結構，並新增 AI 與證照預警子選項）
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ 工程與設計管理中心")
    sub_choice = st.sidebar.radio(
        "選擇子部門與功能：",
        [
            t["sub1"],
            t["sub2"],
            t["sub3"],
            t["sub4"], # 🤖 新增：AI 照片辨識與歸檔
            t["sub5"], # ⚠️ 新增：證照到期主動預警
            t["sub6"]
        ]
    )

    # ----------------------------------------------------
    # 1. 配電盤與工程專案報價
    # ----------------------------------------------------
    if sub_choice == t["sub1"]:
        st.markdown(f"### ⚙️ 1. {t['sub1']}")
        st.info("💡 說明：直接連動到後端的採購成本資料庫，並支援多語系與一鍵轉入應收帳款 AR。")
        
        with st.form("quotation_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input("客戶名稱 (Client Name)", value="Công ty TNHH Xây lắp Tân Thuận")
            with c2:
                st.text_input("工程名稱 / 專案名稱", value="Nhà máy dệt Tây Ninh - Tủ điện chính 2000A")
            with c3:
                st.selectbox("計價幣別", ["USD", "VND", "NTD"])

            st.markdown("##### 📦 報價內容明細 (連動倉庫庫存與單價)")
            st.text_input("項目 1", value="CU-BUS-10100  |  銅排 Busbar 10x100mm", disabled=True)
            st.number_input("數量 1", value=450.0, key="q1")
            
            st.text_input("項目 2", value="CB-ACB-2000A  |  空氣斷路器 ACB 2000A", disabled=True)
            st.number_input("數量 2", value=8.0, key="q2")

            st.text_input("項目 3", value="CB-MCCB-250A  |  塑殼斷路器 MCCB 250A", disabled=True)
            st.number_input("數量 3", value=35.0, key="q3")

            st.markdown("---")
            st.markdown("**未稅金額總計 (Subtotal)**")
            st.markdown("### `$2,120.00`")
            if st.form_submit_button("🚀 確認報價並轉入專案與財務 AR", type="primary"):
                st.success("✅ 報價單已成功建立，並同步連動至財務 AR 應收帳款與採購成本庫！")

    # ----------------------------------------------------
    # 2. 工程驗收與進度追蹤
    # ----------------------------------------------------
    elif sub_choice == t["sub2"]:
        st.markdown(f"### 📊 2. {t['sub2']}")
        st.info("💡 即時監控工程進度、預定驗收時間，並與財務部應收帳款 (AR) 即時通訊連動進行請款催收。")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("在手水電專案", "4 件", "執行中 3 / 待驗收 1")
        with m2:
            st.metric("合約總金額", "$1,850,000", "USD")
        with m3:
            st.metric("總未收 AR", "$600,000", "🔴 加強催收")
        with m4:
            st.metric("平均工程進度", "76.5%", "🟢 正常")

        st.markdown("---")
        st.markdown("##### 📋 專案資料搜尋與過濾")
        st.text_input("輸入專案代碼、客戶或項目關鍵字搜尋")
        
        demo_proj_table = [
            {"代碼": "PRJ-01", "客戶": "越南新順梓電子廠", "項目": "無塵室高低壓配電安裝", "合約總值": "$450,000", "已收": "$315,000", "未收AR": "$135,000", "進度": "90%", "驗收日": "2026-10-15 (初驗)", "狀態": "🟢 待驗收"},
            {"代碼": "PRJ-02", "客戶": "平陽美德金屬加工廠", "項目": "廠房動力配電與照明工程", "合約總值": "$380,000", "已收": "$228,000", "未收AR": "$152,000", "進度": "75%", "驗收日": "2026-10-28 (複驗)", "狀態": "🟡 施工中"},
            {"代碼": "PRJ-03", "客戶": "隆安宏達
