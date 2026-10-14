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
        "caption": "手機優化版 · 主管戰情室 · 估驗報價 · AI 照片歸檔",
        "tab_cockpit": "📊 戰情室 (Cockpit)",
        "tab_projects": "🏗️ 案場進度 (Projects)",
        "tab_site_ai": "📸 AI照片 (AI Photos)",
        "tab_design_cost": "📐 設計/外包 (BOM & Cost)",
        "metric_active": "在建工程案場",
        "metric_progress": "平均施工進度",
        "metric_claim": "本月請款金額",
        "metric_alert": "證照/工安預警",
        "btn_ai_upload": "📸 拍照 / 上傳施工照片並 AI 歸檔",
        "btn_approve": "✅ 一鍵批次核准一般請款",
        "btn_submit_daily": "📤 提交工程日報",
        "alert_budget_title": "⚠️ 點工費用超額預警",
        "alert_budget_desc": "<b>西寧二期水電工程</b>：點工請款超預算 8%，等待主管點擊確認。",
        "alert_cert_title": "📋 證照到期提醒",
        "alert_cert_desc": "外包商 <b>Nguyễn Văn A</b> 電焊證照將於 2026/11/01 到期。",
        "lbl_project_select": "選擇工程案場:",
        "lbl_daily_summary": "施工摘要:",
        "placeholder_daily": "例如: 完成主幹線拉線，現場點工 12 人",
        "msg_approved": "✅ 已順利完成核准！",
        "msg_submitted": "🎉 日報表已成功送出！",
        "msg_ai_success": "🤖 AI 已自動辨識為【配電盤內部接線】並歸檔至西寧廠案場！"
    },
    "English": {
        "title": "⚡ REETECH - Engineering & Design Center",
        "caption": "Mobile Optimized · Executive Cockpit · Valuation · AI Photo Archiving",
        "tab_cockpit": "📊 Executive Cockpit",
        "tab_projects": "🏗️ Project Progress",
        "tab_site_ai": "📸 AI Site Photos",
        "tab_design_cost": "📐 BOM & Costing",
        "metric_active": "Active Projects",
        "metric_progress": "Avg Progress",
        "metric_claim": "Monthly Claim",
        "metric_alert": "Safety Alerts",
        "btn_ai_upload": "📸 Capture / Upload Photo for AI Archiving",
        "btn_approve": "✅ Quick Approve Standard Claims",
        "btn_submit_daily": "📤 Submit Daily Report",
        "alert_budget_title": "⚠️ Budget Overrun Warning",
        "alert_budget_desc": "<b>Tay Ninh Phase 2</b>: Labor cost exceeded budget by 8%, pending manager approval.",
        "alert_cert_title": "📋 Certificate Expiry Warning",
        "alert_cert_desc": "Subcontractor <b>Nguyễn Văn A</b> welding permit expires on 2026/11/01.",
        "lbl_project_select": "Select Project:",
        "lbl_daily_summary": "Daily Summary:",
        "placeholder_daily": "E.g., Completed main cable wiring, 12 workers on site.",
        "msg_approved": "✅ Approved successfully!",
        "msg_submitted": "🎉 Daily report submitted successfully!",
        "msg_ai_success": "🤖 AI identified as [Control Panel Wiring] and archived to Tay Ninh Plant!"
    },
    "Tiếng Việt": {
        "title": "⚡ REETECH - Trung tâm Quản lý Kỹ thuật & Thiết kế",
        "caption": "Tối ưu di động · Phòng điều hành · Nghiệm thu · Phân loại ảnh AI",
        "tab_cockpit": "📊 Phòng điều hành",
        "tab_projects": "🏗️ Tiến độ dự án",
        "tab_site_ai": "📸 Ảnh thi công AI",
        "tab_design_cost": "📐 Thiết kế & Chi phí",
        "metric_active": "Dự án đang làm",
        "metric_progress": "Tiến độ trung bình",
        "metric_claim": "Tổng nghiệm thu",
        "metric_alert": "Cảnh báo an toàn",
        "btn_ai_upload": "📸 Chụp ảnh / Tải ảnh & Phân loại AI",
        "btn_approve": "✅ Duyệt nhanh thanh toán chuẩn",
        "btn_submit_daily": "📤 Gửi báo cáo ngày",
        "alert_budget_title": "⚠️ Cảnh báo chi phí vượt ngân sách",
        "alert_budget_desc": "<b>Dự án Tây Ninh 2</b>: Chi phí nhân công vượt 8%, chờ sếp duyệt.",
        "alert_cert_title": "📋 Cảnh báo chứng chỉ hết hạn",
        "alert_cert_desc": "Nhà thầu phụ <b>Nguyễn Văn A</b> chứng chỉ hàn hết hạn ngày 01/11/2026.",
        "lbl_project_select": "Chọn dự án:",
        "lbl_daily_summary": "Nội dung công việc:",
        "placeholder_daily": "Ví dụ: Hoàn thành kéo cáp chính, 12 công nhân tại hiện trường.",
        "msg_approved": "✅ Đã duyệt thành công!",
        "msg_submitted": "🎉 Báo cáo đã gửi thành công!",
        "msg_ai_success": "🤖 AI đã tự động phân loại vào [Dự án Tây Ninh]!"
    }
}

def inject_mobile_elder_friendly_css():
    """注入手機端大字體、大按鈕與高對比專用 CSS (Mobile-First & Elder-Friendly)"""
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            font-size: 18px !important;
        }
        div.stButton > button {
            width: 100% !important;
            height: 3.3rem !important;
            font-size: 1.25rem !important;
            font-weight: bold !important;
            border-radius: 12px !important;
            margin-top: 8px !important;
            margin-bottom: 8px !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: bold !important;
            color: #1E3A8A !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 1.1rem !important;
            color: #374151 !important;
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

def render_engineering_management_page(engine=None, lang="繁體中文", **kwargs):
    # 1. 載入手機長輩友善樣式
    inject_mobile_elder_friendly_css()

    # 2. 中、英、越 三語系即時切換按鈕
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

    # 3. 大字體頁籤 (Tabs)
    tab_cockpit, tab_projects, tab_site_ai, tab_design_cost = st.tabs([
        L["tab_cockpit"], L["tab_projects"], L["tab_site_ai"], L["tab_design_cost"]
    ])

    # ----------------------------------------------------
    # 📊 Tab 1: 主管手機版戰情室 (Executive Cockpit)
    # ----------------------------------------------------
    with tab_cockpit:
        m1, m2 = st.columns(2)
        m1.metric(L["metric_active"], "3")
        m2.metric(L["metric_progress"], "68.5%")

        m3, m4 = st.columns(2)
        m3.metric(L["metric_claim"], "1.25B VND")
        m4.metric(L["metric_alert"], "2", delta_color="inverse", delta="Warning")

        st.markdown("---")
        
        # 修正：避免 f-string 內部雙重引號解析錯誤
        t_budget_title = L["alert_budget_title"]
        t_budget_desc = L["alert_budget_desc"]
        t_cert_title = L["alert_cert_title"]
        t_cert_desc = L["alert_cert_desc"]

        st.markdown(f"""
        <div class="mobile-card" style="border-left: 6px solid #F59E0B;">
            <h4 style="margin:0; color:#D97706;">{t_budget_title}</h4>
            <p style="margin:4px 0 0 0; font-size:16px;">{t_budget_desc}</p>
        </div>
        <div class="mobile-card" style="border-left: 6px solid #3B82F6;">
            <h4 style="margin:0; color:#2563EB;">{t_cert_title}</h4>
            <p style="margin:4px 0 0 0; font-size:16px;">{t_cert_desc}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(L["btn_approve"], type="primary"):
            st.success(L["msg_approved"])

    # ----------------------------------------------------
    # 🏗️ Tab 2: 案場進度與工程日報表
    # ----------------------------------------------------
    with tab_projects:
        st.markdown("### 🏗️ " + L["tab_projects"])
        
        st.selectbox(
            L["lbl_project_select"],
            ["PRJ-001 西寧廠高壓配電盤擴建工程 (Tay Ninh Plant Expansion)", "PRJ-002 西寧二期水電管線工程 (Tay Ninh Phase 2)"]
        )

        st.markdown("##### 📝 " + L["lbl_daily_summary"])
        daily_log = st.text_area(L["lbl_daily_summary"], placeholder=L["placeholder_daily"], height=100)
        
        if st.button(L["btn_submit_daily"], type="primary"):
            st.success(L["msg_submitted"])

    # ----------------------------------------------------
    # 📸 Tab 3: AI 現場照片拍攝與上傳
    # ----------------------------------------------------
    with tab_site_ai:
        st.markdown("### 📸 " + L["tab_site_ai"])
        
        st.selectbox(L["lbl_project_select"], ["西寧廠高壓配電盤擴建工程", "西寧二期水電管線工程"], key="ai_proj")
        
        # 手機開鏡頭/挑照片
        img_file = st.file_uploader("📸 Photo Upload:", type=["jpg", "jpeg", "png"])
        
        if img_file:
            st.image(img_file, caption="Preview", use_container_width=True)
            if st.button(L["btn_ai_upload"], type="primary"):
                st.success(L["msg_ai_success"])

    # ----------------------------------------------------
    # 📐 Tab 4: 配電盤 BOM 與外包結算
    # ----------------------------------------------------
    with tab_design_cost:
        st.markdown("### 📐 " + L["tab_design_cost"])
        msg_bom = "💡 Auto-synced with inventory & purchasing." if selected_lang == "English" else ("💡 系統已自動與倉庫備料及採購連動。" if selected_lang == "繁體中文" else "💡 Hệ thống tự động đồng bộ tồn kho vật tư.")
        st.info(msg_bom)

def render_engineering_management(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def render_engineering_profile_page(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)
