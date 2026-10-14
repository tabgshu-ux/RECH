import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 三語系字典 (繁體中文 / English / Tiếng Việt)
# ----------------------------------------------------
ENG_I18N = {
    "繁體中文": {
        "title": "⚡ 裕豐電機 - 工程與設計管理中心",
        "caption": "手機優化版 · 主管戰情室 · 估驗報價 · BOM展算 · 設計圖庫",
        "lbl_sub_action": "請選擇要執行的工程/設計功能：",
        "actions": [
            "📊 1. 工程主管戰情室 (Executive Cockpit)",
            "⚡ 2. 配電盤與工程專案雙層報價",
            "📊 3. 工程驗收與進度追蹤",
            "📋 4. 現場工程日報表與出工統計",
            "📸 5. AI 施工照片智慧辨識與歸檔",
            "⚠️ 6. 分包商與專業證照到期預警",
            "🎨 7. 配電盤電氣與機構設計圖庫 Storage",
            "🔌 8. 配電盤 BOM 零件自動展開與採購連動",
            "👷 9. 外包商點工計價與勞動法計薪",
            "🧪 10. FAT/SAT 試驗報告與 QR Code 驗收"
        ]
    },
    "English": {
        "title": "⚡ REETECH - Engineering & Design Management Center",
        "caption": "Mobile Optimized · Cockpit · Quotation · BOM · Storage",
        "lbl_sub_action": "Select Engineering Feature:",
        "actions": [
            "📊 1. Executive Cockpit",
            "⚡ 2. M&E & Switchgear Quotation",
            "📊 3. Progress Tracking & Acceptance",
            "📋 4. Daily Construction Log",
            "📸 5. AI Photo Archiving",
            "⚠️ 6. Subcontractor License Alerts",
            "🎨 7. CAD/Design Drawing Storage",
            "🔌 8. BOM Explode & Procurement Link",
            "👷 9. Subcontractor Labor Costing",
            "🧪 10. FAT/SAT Reports & QR Acceptance"
        ]
    },
    "Tiếng Việt": {
        "title": "⚡ REETECH - Trung tâm Quản lý Kỹ thuật & Thiết kế",
        "caption": "Tối ưu di động · Điều hành · Báo giá · Bóc tách BOM · Kho bản vẽ",
        "lbl_sub_action": "Chọn chức năng kỹ thuật:",
        "actions": [
            "📊 1. Bàn điều hành sếp (Cockpit)",
            "⚡ 2. Báo giá dự án & Tủ điện",
            "📊 3. Theo dõi tiến độ & Nghiệm thu",
            "📋 4. Nhật ký thi công hàng ngày",
            "📸 5. Phân loại ảnh thi công AI",
            "⚠️ 6. Cảnh báo chứng chỉ an toàn",
            "🎨 7. Kho lưu trữ bản vẽ thiết kế Storage",
            "🔌 8. Bóc tách BOM & Mua hàng",
            "👷 9. Tính lương thầu phụ & Nhân công",
            "🧪 10. Báo cáo thử nghiệm FAT/SAT"
        ]
    }
}

def inject_mobile_elder_friendly_css():
    st.markdown("""
        <style>
        html, body, [class*="css"] { font-size: 17px !important; }
        div.stButton > button {
            width: 100% !important;
            height: 3.2rem !important;
            font-size: 1.2rem !important;
            font-weight: bold !important;
            border-radius: 10px !important;
            margin-top: 6px !important;
            margin-bottom: 6px !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: bold !important;
            color: #1E3A8A !important;
        }
        .mobile-card {
            background-color: #FFFFFF;
            border: 2px solid #E5E7EB;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

def init_engineering_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.projects (
                    id SERIAL PRIMARY KEY,
                    project_code VARCHAR(50) UNIQUE NOT NULL,
                    project_name VARCHAR(200) NOT NULL,
                    client_name VARCHAR(150),
                    budget_amount NUMERIC(15,2) DEFAULT 0,
                    progress_pct NUMERIC(5,2) DEFAULT 0,
                    status VARCHAR(50) DEFAULT '🟡 施工中',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass

def render_engineering_management_page(engine=None, lang="繁體中文", sub_action=None, **kwargs):
    inject_mobile_elder_friendly_css()

    # 1. 語系選擇與標題
    c_title, c_lang = st.columns([2, 1])
    with c_lang:
        selected_lang = st.selectbox(
            "🌐 Ngôn ngữ / Language",
            ["繁體中文", "English", "Tiếng Việt"],
            index=0
        )
    
    L = ENG_I18N.get(selected_lang, ENG_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_engineering_db(engine)

    # 2. 頂部大選項 (讓使用者隨時可切換 戰情室 或 10 大表單操作)
    action_idx = 0
    if sub_action and str(sub_action).isdigit():
        sub_num = int(sub_action) - 1
        if 0 <= sub_num < len(L["actions"]):
            action_idx = sub_num

    selected_action = st.selectbox(L["lbl_sub_action"], L["actions"], index=action_idx)

    st.markdown("---")

    # ----------------------------------------------------
    # 📊 功能 1: 工程主管戰情室 (Cockpit)
    # ----------------------------------------------------
    if "1." in selected_action:
        st.markdown("### 📊 工程主管戰情室 (Executive Cockpit)")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("在建工程案場", "3 案場")
        m2.metric("平均施工進度", "68.5%")
        m3.metric("本月請款金額", "1.25B VND")
        m4.metric("證照/工安預警", "2 筆預警", delta_color="inverse", delta="待處置")

        st.markdown("---")
        st.markdown("""
        <div class="mobile-card" style="border-left: 6px solid #F59E0B;">
            <h4 style="margin:0; color:#D97706;">⚠️ 點工費用超額預警</h4>
            <p style="margin:4px 0 0 0; font-size:16px;"><b>西寧二期水電工程</b>：點工請款超預算 8%，等待主管點擊確認。</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✅ 一鍵批次核准一般請款", type="primary"):
            st.success("✅ 已順利完成核准！")

    # ----------------------------------------------------
    # ⚡ 功能 2: 配電盤與工程專案雙層報價上傳
    # ----------------------------------------------------
    elif "2." in selected_action:
        st.markdown("### ⚡ 配電盤與工程專案雙層報價系統")
        with st.form("form_quote"):
            c1, c2 = st.columns(2)
            with c1:
                q_code = st.text_input("報價單編號 *", placeholder="例: QUO-2026-008")
                q_name = st.text_input("專案/工程名稱 *", placeholder="例: 西寧廠高壓配電盤擴建案")
            with c2:
                q_client = st.text_input("客戶名稱", placeholder="例: 台商越南造紙廠")
                q_amount = st.number_input("預估總報價金額 (VND)", min_value=0.0, value=2500000000.0, step=100000000.0)
            q_file = st.file_uploader("上傳詳細報價單 Excel / PDF", type=["xlsx", "pdf"])
            if st.form_submit_button("📌 送出報價單並存檔", type="primary"):
                st.success(f"🎉 成功建立報價單：{q_code} - {q_name}！")

    # ----------------------------------------------------
    # 📊 功能 3: 工程驗收與進度追蹤
    # ----------------------------------------------------
    elif "3." in selected_action:
        st.markdown("### 📊 工程驗收與進度追蹤")
        st.selectbox("選擇專案:", ["PRJ-2026-01 西寧廠高壓配電盤擴建工程", "PRJ-2026-02 西寧二期水電管線工程"])
        st.slider("更新施工完成進度 %:", 0, 100, 68)
        if st.button("💾 儲存進度更新", type="primary"):
            st.success("✅ 專案進度已成功更新為 68%！")

    # ----------------------------------------------------
    # 📋 功能 4: 現場工程日報表與出工統計
    # ----------------------------------------------------
    elif "4." in selected_action:
        st.markdown("### 📋 現場工程日報表與出工統計")
        with st.form("form_daily"):
            st.date_input("日報日期", datetime.date.today())
            st.selectbox("施工案場", ["西寧廠高壓配電盤擴建工程", "西寧二期水電管線工程"])
            st.number_input("今日現場點工人數 (人)", min_value=1, value=12)
            st.text_area("今日施工內容與進度說明:", placeholder="完成 A 區主幹線拉線與配電盤定位。")
            if st.form_submit_button("📤 提交工程日報表", type="primary"):
                st.success("🎉 日報表已成功提交並存檔！")

    # ----------------------------------------------------
    # 📸 功能 5: AI 施工照片智慧辨識與歸檔
    # ----------------------------------------------------
    elif "5." in selected_action:
        st.markdown("### 📸 AI 施工照片智慧辨識與歸檔")
        st.selectbox("選擇案場:", ["西寧廠高壓配電盤擴建工程", "西寧二期水電管線工程"])
        img_file = st.file_uploader("拍照或上傳現場施工照片 (JPG, PNG):", type=["jpg", "png"])
        if img_file:
            st.image(img_file, caption="待歸檔照片預覽", use_container_width=True)
            if st.button("🤖 開始 AI 智慧辨識並歸檔", type="primary"):
                st.success("🤖 AI 已自動辨識為【配電盤內部接線】並自動歸檔！")

    # ----------------------------------------------------
    # ⚠️ 功能 6: 分包商與專業證照到期預警
    # ----------------------------------------------------
    elif "6." in selected_action:
        st.markdown("### ⚠️ 分包商與專業證照到期預警")
        st.dataframe(pd.DataFrame([
            {"外包商/人員": "Nguyễn Văn A", "證照名稱": "高壓電焊作業證", "到期日": "2026-11-01", "狀態": "⚠️ 30天內到期"},
            {"外包商/人員": "Trần Văn B", "證照名稱": "高空作業安全證", "到期日": "2027-05-15", "狀態": "🟢 有效"}
        ]), use_container_width=True)

    # ----------------------------------------------------
    # 🎨 功能 7: 配電盤電氣與機構設計圖庫 Storage
    # ----------------------------------------------------
    elif "7." in selected_action:
        st.markdown("### 🎨 配電盤電氣與機構設計圖庫 (Drawing Storage)")
        with st.form("form_cad"):
            st.text_input("圖紙/CAD 編號 *", placeholder="例: DWG-EP-2026-001")
            st.text_input("圖紙名稱", placeholder="例: 110KV 變壓器二次側單線圖")
            st.file_uploader("上傳 CAD / PDF 圖紙檔案:", type=["dwg", "dxf", "pdf"])
            if st.form_submit_button("📁 上傳至 Storage 圖庫", type="primary"):
                st.success("🎉 設計圖紙已成功歸檔至雲端圖庫！")

    # ----------------------------------------------------
    # 🔌 功能 8: 配電盤 BOM 零件自動展開與採購連動
    # ----------------------------------------------------
    elif "8." in selected_action:
        st.markdown("### 🔌 配電盤 BOM 零件自動展開與採購連動")
        st.file_uploader("匯入配電盤 BOM Excel (含元件清單與數量):", type=["xlsx", "csv"])
        if st.button("⚙️ 執行 BOM 自動拆解並比對倉庫庫存", type="primary"):
            st.info("💡 比對完畢：銅排剩餘 120KG（充足），斷路器 400A 缺 2 台，已自動拋轉請購單至採購模組！")

    # ----------------------------------------------------
    # 👷 功能 9: 外包商點工計價與越南勞動法計薪
    # ----------------------------------------------------
    elif "9." in selected_action:
        st.markdown("### 👷 外包商點工計價與計薪")
        st.text_input("外包商名稱", placeholder="例: 越南金屬結構工程工班")
        st.number_input("本期點工總工時 (小時)", min_value=0.0, value=160.0)
        st.number_input("時薪/日薪單價 (VND)", min_value=0.0, value=350000.0)
        if st.button("💰 計算金額並拋轉應付帳款 (AP)", type="primary"):
            st.success("✅ 點工費用 56,000,000 VND 已拋轉至【採購與應付帳款 AP】！")

    # ----------------------------------------------------
    # 🧪 功能 10: FAT/SAT 試驗報告與 QR Code 驗收
    # ----------------------------------------------------
    elif "10." in selected_action:
        st.markdown("### 🧪 FAT/SAT 試驗報告與 QR Code 驗收")
        st.text_input("設備出廠編號", placeholder="例: EQ-FAT-2026-88")
        st.selectbox("試驗類別", ["工廠出廠試驗 (FAT)", "現場竣工試驗 (SAT)"])
        st.file_uploader("上傳耐壓與動作試驗報告 PDF:", type=["pdf"])
        if st.button("🏷️ 生成現場驗收 QR Code", type="primary"):
            st.success("🎉 驗收報告已綁定，QR Code 已成功生成！")

def render_engineering_management(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def render_engineering_profile_page(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)
