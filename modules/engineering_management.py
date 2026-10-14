import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def init_engineering_db(engine):
    """工程資料庫初始化"""
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

def render_engineering_management_page(engine=None, lang="繁體中文", **kwargs):
    st.title("⚡ 裕豐電機工業 - 工程與設計管理中心")
    st.caption("水電工程與配電盤製造 ERP 系統：提供主管一站式工程戰情室、進度追蹤、AI 施工照片與預算串聯審核。")

    init_engineering_db(engine)

    # ----------------------------------------------------
    # 🎯 將 10 個子功能整合為 4 個高階主管核心頁籤 (Tabs)
    # ----------------------------------------------------
    tab_cockpit, tab_projects, tab_site_ai, tab_design_cost = st.tabs([
        "📊 ⚡ 工程主管戰情室 (Executive Cockpit)",
        "🏗️ 📑 案場專案、估驗與進度追蹤",
        "🤖 🛠️ 施工現場、AI 照片與工安證照",
        "📐 ⚡ 配電盤設計、BOM 與外包結算"
    ])

    # ----------------------------------------------------
    # 📊 Tab 1: 工程主管戰情室 (主管專用核心頁)
    # ----------------------------------------------------
    with tab_cockpit:
        st.markdown("### 📊 專案進度、估驗金額與工安預警總覽")
        
        # 核心 KPI 數據卡
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("在建工程案場", "3 案場", delta="西寧廠區核心")
        m2.metric("全案場平均進度", "68.5%", delta="+5.2% 本月")
        m3.metric("本月工程請款總額", "1,250,000,000 VND", delta="待財務核發")
        m4.metric("工安/證照到期預警", "2 筆須處理", delta_color="inverse", delta="請主管核閱")

        st.markdown("---")
        
        c_left, c_right = st.columns([3, 2])
        with c_left:
            st.markdown("##### 📌 各案場最新施工進度與預算執行率")
            mock_projects = [
                {"案場編號": "PRJ-2026-01", "案場名稱": "西寧廠高壓配電盤擴建工程", "預算 (VND)": "2,500,000,000", "已執行請款": "1,800,000,000", "進度 %": 72.0, "狀態": "🟢 正常施工"},
                {"案場編號": "PRJ-2026-02", "案場名稱": "海防廠低壓控制箱更新案", "預算 (VND)": "1,200,000,000", "已執行請款": "950,000,000", "進度 %": 85.0, "狀態": "🟡 請款核對中"},
                {"案場編號": "PRJ-2026-03", "案場名稱": "西寧二期廠區水電管線工程", "預算 (VND)": "4,000,000,000", "進度 %": 45.0, "已執行請款": "1,500,000,000", "狀態": "🟢 正常施工"}
            ]
            st.dataframe(pd.DataFrame(mock_projects), use_container_width=True)

        with c_right:
            st.markdown("##### ⚠️ 待主管審核與預警事項 (Approval Needed)")
            st.warning("⚠️ **外包商請款超額預警**：『西寧二期水電工程』點工計價超過預算 8%，請主管核准。")
            st.info("📋 **證照到期通知**：外包商『阮文A』高壓電焊證照將於 2026/11/01 到期。")
            st.success("✅ **AI 照片歸檔**：今日已自動智慧歸檔 12 張施工現場品質照片。")

    # ----------------------------------------------------
    # 🏗️ Tab 2: 案場專案、估驗報價與進度追蹤
    # ----------------------------------------------------
    with tab_projects:
        st.markdown("### 🏗️ 案場估驗報價、工程日報表與 FAT/SAT 驗收")
        
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["⚡ 估驗報價與工程專案", "📝 現場工程日報表與打卡", "📜 FAT/SAT 試驗報告與 QR Code"])
        
        with sub_tab1:
            st.markdown("##### 1️⃣ 工程估驗報價與專案建立")
            st.info("在此進行工程工項編號建立、預算編列與客戶估驗請款。")
        with sub_tab2:
            st.markdown("##### 2️⃣ 現場工程日報表與點工人數統計")
            st.text_input("選擇工程案場", value="西寧廠高壓配電盤擴建工程")
            st.text_area("今日施工進度說明", placeholder="完成 A 區主幹線拉線與配電盤本體定位。")
        with sub_tab3:
            st.markdown("##### 3️⃣ FAT / SAT 工廠與現場試驗報驗")
            st.caption("支援生成掃描驗收 QR Code，出廠與現場一鍵驗收。")

    # ----------------------------------------------------
    # 🤖 Tab 3: 施工現場、AI 照片與工安證照
    # ----------------------------------------------------
    with tab_site_ai:
        st.markdown("### 🤖 🛠️ 施工現場管理、AI 智慧照片辨識與工安證照")
        
        c_ai1, c_ai2 = st.columns([1, 1])
        with c_ai1:
            st.markdown("##### 📸 上傳施工現場照片進行 AI 辨識")
            st.selectbox("選擇工程案場", ["西寧廠高壓配電盤擴建工程", "西寧二期廠區水電管線工程"])
            st.file_uploader("上傳施工現場照片 (JPG, PNG)", type=["jpg", "png"])
            st.button("🤖 開始 AI 智慧辨識並歸檔", type="primary")
        with c_ai2:
            st.markdown("##### ⚠️ 外包商與專業證照到期預警")
            st.caption("自動比對越南勞動法與工安法規，確保現場施工安全。")
            st.dataframe(pd.DataFrame([
                {"外包商/人員": "Nguyễn Văn A", "證照名稱": "高壓電焊作業證", "到期日": "2026-11-01", "狀態": "⚠️ 30天內到期"},
                {"外包商/人員": "Tran Van B", "證照名稱": "高空作業安全證", "到期日": "2027-05-15", "狀態": "🟢 有效"}
            ]), use_container_width=True)

    # ----------------------------------------------------
    # 📐 Tab 4: 配電盤設計、BOM 與外包結算
    # ----------------------------------------------------
    with tab_design_cost:
        st.markdown("### 📐 ⚡ 配電盤電氣設計、BOM 採購連動與外包點工結算")
        
        st.markdown("##### 1️⃣ 配電盤 BOM 零件自動展開與採購庫存連動")
        st.caption("當專案 BOM 展開後，自動對比內部庫存，不足料件自動觸發【採購請購單】。")
        
        st.markdown("##### 2️⃣ 外包商點工計價與應付帳款 (AP) 串聯")
        st.caption("連結現場驗收進度，確認無誤後自動拋轉至財務【應付帳款 AP】系統。")

def render_engineering_management(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def render_engineering_profile_page(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)
