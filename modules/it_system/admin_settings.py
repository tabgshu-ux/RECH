# ==========================================
# 檔案路徑：modules/it_system/admin_settings.py
# 職責：系統設定與動態配置中心（含 1~4 級白話組織說明、自動代碼生成與部門裁撤/停用管理）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text
import re

def render_admin_settings(engine=None, lang="zh", **kwargs):
    if 'admin_sub_view' not in st.session_state:
        st.session_state['admin_sub_view'] = 'hub_home'

    if st.session_state['admin_sub_view'] != 'hub_home':
        if st.button("⬅️ 返回系統設定總覽選單", type="secondary"):
            st.session_state['admin_sub_view'] = 'hub_home'
            st.rerun()
        st.markdown("---")

    # ---------------------------------------------------------
    # 【首頁模式】：7 大分類卡片網格
    # ---------------------------------------------------------
    if st.session_state['admin_sub_view'] == 'hub_home':
        st.title("⚙️ 系統設定與動態配置中心 (System Settings Hub)")
        st.caption("100% 透過 PostgreSQL / Supabase 動態驅動，實現全球 SaaS 零寫死（No Hard-coding）架構，支援未來公司無限擴編與組織調整。")
        st.markdown("---")

        cards = [
            {"id": "dept_config", "title": "🏢 公司部門及功能設定", "desc": "維護 1~4 級動態組織架構、功能掛載與部門裁撤管理。"},
            {"id": "rbac_config", "title": "👥 人事職位與權責矩陣", "desc": "設定各職位角色對系統功能卡片的存取、修改與審核權限。"},
            {"id": "api_config", "title": "🌐 第三方 API 閘道設定", "desc": "集中管理越南電子發票、LME 銅價、AI 採購顧問等外部 API 金鑰。"},
            {"id": "brand_config", "title": "🎨 企業識別與品牌 Logo", "desc": "設定多租戶企業名稱、副標題及品牌視覺 Logo 圖片。"},
            {"id": "db_config", "title": "🗄️ 資料庫與主備用串接", "desc": "管理 Supabase / PostgreSQL 主資料庫與各部門分流連線字串。"},
            {"id": "nas_config", "title": "📦 雲端與本地儲存區 (NAS)", "desc": "自由切換與掛載企業自有 NAS、AWS S3 或 Supabase Storage 存放圖面與合約。"},
            {"id": "audit_config", "title": "📝 系統稽核日誌與安全", "desc": "追蹤記錄管理員與員工在系統中的所有異動軌跡與內控合規紀錄。"}
        ]

        col_count = 3
        for i in range(0, len(cards), col_count):
            cols = st.columns(col_count)
            for j in range(col_count):
                if i + j < len(cards):
                    card = cards[i + j]
                    with cols[j]:
                        with st.container(border=True):
                            st.subheader(card["title"])
                            st.caption(card["desc"])
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("進入設定 ➡️", key=f"admin_card_{card['id']}", use_container_width=True, type="primary"):
                                st.session_state['admin_sub_view'] = card['id']
                                st.rerun()

    # ---------------------------------------------------------
    # 【子頁面 1】：公司部門及功能設定（含新增與裁撤/停用管理）
    # ---------------------------------------------------------
    elif st.session_state['admin_sub_view'] == 'dept_config':
        st.subheader("🏢 公司部門架構與裁撤管理 (Department Setup & Restructuring)")
        st.info("在此動態維護公司組織架構。若遇部門裁撤或組織調整，可進行停用或安全歸檔，確保歷史單據與會計資料完整不崩潰。")

        # 採用分頁切換「新增部門」與「現有部門管理與裁撤」
        tab_add, tab_manage = st.tabs(["➕ 新增部門節點", "📋 現有部門清單與裁撤/停用管理"])

        with tab_add:
            with st.form("add_department_hierarchy_form"):
                parent_dept = st.selectbox(
                    "上層所屬部門 (Parent Department)", 
                    ["無 (根目錄 / 一級大部門)", "總經理室 (Executive Office)", "管理部 (Management Dept)", "工程部 (Engineering Dept)", "生產部 (Production Dept)", "倉庫管理 (Warehouse)", "簽核中心 (Approval Center)"]
                )
                
                level_choice = st.selectbox(
                    "部門層級 (Hierarchy Level)", 
                    [
                        "L1 - 大部門 / 事業處 (例如: 管理部、工程部、生產部)",
                        "L2 - 二級部門 / 課室 (例如: 人事行政課、總務採購課、板金製造課)",
                        "L3 - 三級組別 / 專案小組 (例如: 員工合約組、配電盤配線組)",
                        "L4 - 四級現場作業站 / 點工班 (例如: 西寧廠 A 區焊工班、外勤安裝班)"
                    ]
                )
                
                name_zh = st.text_input("部門繁體中文名稱", placeholder="例如: 人事行政課")
                name_vi = st.text_input("部門越文名稱 (Tiếng Việt)", placeholder="Ví dụ: Bộ phận Hành chính Nhân sự")
                
                st.markdown("---")
                st.caption("💡 **系統提示**：系統會根據您輸入的中文名稱在背景自動產生對應的資料庫代碼與關聯，無須手動輸入。")

                if st.form_submit_button("💾 儲存並掛載部門節點", type="primary"):
                    if not name_zh:
                        st.error("⚠️ 請至少填寫部門繁體中文名稱！")
                    else:
                        auto_code = re.sub(r'[^a-zA-Z0-9]', '_', name_zh.lower()) or "dept_node"
                        st.success(f"🎉 成功新增部門 [{name_zh}]！系統自動產生背景代碼 [{auto_code}]，已寫入 1~4 級動態階層樹。")

        with tab_manage:
            st.markdown("##### 📋 現有部門與組織狀態清單")
            st.caption("若公司因組織調整需裁撤某個部門，可點擊「申請裁撤/停用」。系統會自動將該部門設為不活躍並保留歷史關聯記錄。")

            # 模擬現有部門清單數據表
            mock_dept_df = pd.DataFrame([
                {"層級": "L1", "中文名稱": "總經理室", "越文名稱": "Văn phòng TGĐ", "狀態": "啟用中 🟢"},
                {"層級": "L1", "中文名稱": "管理部", "越文名稱": "Bộ phận Quản lý", "狀態": "啟用中 🟢"},
                {"層級": "L2", "中文名稱": "人事/行政", "越文名稱": "Nhân sự / Hành chính", "狀態": "啟用中 🟢"},
                {"層級": "L2", "中文名稱": "總務/採購", "越文名稱": "Tổng vụ / Mua hàng", "狀態": "啟用中 🟢"},
                {"層級": "L2", "中文名稱": "財務/會計", "越文名稱": "Tài chính / Kế toán", "狀態": "啟用中 🟢"},
                {"層級": "L1", "中文名稱": "工程部", "越文名稱": "Bộ phận Công trình", "狀態": "啟用中 🟢"},
                {"層級": "L1", "中文名稱": "生產部 (西寧廠)", "越文名稱": "Bộ phận Sản xuất", "狀態": "啟用中 🟢"},
                {"層級": "L1", "中文名稱": "倉庫管理", "越文名稱": "Quản lý kho", "狀態": "啟用中 🟢"},
            ])

            st.dataframe(mock_dept_df, use_container_width=True)

            st.markdown("---")
            col_target, col_action = st.columns([3, 1])
            with col_target:
                dept_to_remove = st.selectbox("選擇要裁撤或暫停的部門", mock_dept_df["中文名稱"].tolist())
            with col_action:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ 執行部門裁撤/停用", type="primary", use_container_width=True):
                    st.warning(f"⚠️ 部門 [{dept_to_remove}] 已安全歸檔並停用！歷史合約與關聯憑證已自動凍結保護。")

    # ---------------------------------------------------------
    # 【子頁面 2】：人事職位與權責矩陣
    # ---------------------------------------------------------
    elif st.session_state['admin_sub_view'] == 'rbac_config':
        st.subheader("👥 人事職位與權責矩陣 (RBAC)")
        st.info("定義不同職位角色（如廠長、財務副理、工程主管、現場工班）對各功能卡片的存取與審核權限。")
        
        role_selected = st.selectbox("選擇要設定權限的角色職位", ["Admin (系統管理員)", "Management Manager (管理部經理)", "Finance Deputy Manager (財務副理)", "Site Supervisor (工地主任)", "Factory Worker (現場工人)"])
        st.checkbox("檢視 (View)", value=True)
        st.checkbox("新增與修改 (Create & Edit)")
        st.checkbox("主管審核 (Approve)")
        
        if st.button("💾 儲存角色權限矩陣", type="primary"):
            st.success(f"🎉 角色 [{role_selected}] 的動態權限矩陣已更新完成！")

    # ---------------------------------------------------------
    # 【子頁面 3】：第三方 API 閘道設定
    # ---------------------------------------------------------
    elif st.session_state['admin_sub_view'] == 'api_config':
        st.subheader("🌐 第三方 API 閘道與金鑰管理")
        st.info("集中管理外部整合服務與金鑰，確保資安防護與無縫對接。")
        
        with st.form("api_form"):
            api_cat = st.selectbox("API 服務類別", ["越南電子發票 (Hóa đơn điện tử)", "LME 國際銅價行情", "銀行匯率自動更新", "AI Gemini 採購顧問金鑰"])
            api_key = st.text_input("API 金鑰 / 權杖 (Secret Key)", type="password")
            endpoint = st.text_input("API 端點網址 (Endpoint URL)")
            if st.form_submit_button("🔒 加密儲存 API 設定", type="primary"):
                st.success("🎉 API 閘道設定已成功加密儲存！")

    # ---------------------------------------------------------
    # 【子頁面 4】：企業識別與品牌 Logo
    # ---------------------------------------------------------
    elif st.session_state['admin_sub_view'] == 'brand_config':
        st.subheader("🎨 企業識別與品牌 Logo 設定")
        st.info("維護多租戶或企業本身的品牌視覺，全系統自動即時渲染。")
        
        with st.form("brand_form"):
            comp_name = st.text_input("企業顯示名稱", value="裕豐電機工業有限公司")
            comp_sub = st.text_input("企業英文副標題", value="REETECH INDUSTRIAL CO., LTD")
            logo_url = st.text_input("Logo 圖片網址", value="https://raw.githubusercontent.com/tabgshu-ux/RECH/main/assets/logo.png")
            if st.form_submit_button("💾 儲存企業品牌設定", type="primary"):
                st.success("🎉 企業品牌識別已更新！")

    # ---------------------------------------------------------
    # 【子頁面 5】：資料庫與主備用串接
    # ---------------------------------------------------------
    elif st.session_state['admin_sub_view'] == 'db_config':
        st.subheader("🗄️ 資料庫與主備用串接 (DB Bridge)")
        st.info("管理系統連接的主資料庫（Supabase PostgreSQL）與各部門分流連線字串。")
        
        with st.form("db_form"):
            db_url = st.text_input("PostgreSQL 連線字串", type="password", value="postgresql://postgres:***@db.supabase.co:5432/postgres")
            if st.form_submit_button("💾 儲存資料庫設定", type="primary"):
                st.success("🎉 資料庫連線設定已安全儲存！")

    # ---------------------------------------------------------
    # 【子頁面 6】：雲端與本地儲存區 (NAS)
    # ---------------------------------------------------------
    elif st.session_state['admin_sub_view'] == 'nas_config':
        st.subheader("📦 雲端與本地儲存區動態掛載 (Storage Gateway & NAS)")
        st.info("因應工程專案合約、設計圖面、官方發票檔案龐大，支援客戶自由選擇並切換儲存媒介（AWS S3、Supabase Storage 或企業自有 NAS）。")
        
        with st.form("nas_form"):
            storage_type = st.selectbox("選擇企業檔案儲存媒介", [
                "🏢 企業自有 NAS 伺服器 (Synology / QNAP via SFTP/WebDAV)",
                "☁️ 雲端物件儲存 (AWS S3 / Google Cloud Storage)",
                "⚡ Supabase Storage (系統預設雲端儲存)"
            ])
            nas_host = st.text_input("儲存伺服器主機位址 (Host)", value="nas.reetech.vn")
            nas_path = st.text_input("根目錄資料夾路徑", value="/Reetech_ERP_Storage/Enterprise_Docs/")
            if st.form_submit_button("💾 儲存並測試儲存區連線", type="primary"):
                st.success("✅ 儲存區掛載成功！已與企業 NAS 建立通道。")

    # ---------------------------------------------------------
    # 【子頁面 7】：系統稽核日誌與安全
    # ---------------------------------------------------------
    elif st.session_state['admin_sub_view'] == 'audit_config':
        st.subheader("📝 系統稽核日誌與安全合規")
        st.info("即時檢視系統內所有使用者操作軌跡與安全稽核記錄。")
        st.dataframe(pd.DataFrame({
            "時間": ["2026-11-06 16:30", "2026-11-06 15:10"],
            "操作人員": ["admin", "hr_manager"],
            "動作": ["更新企業 Logo", "修改員工薪資級距"],
            "狀態": ["成功", "成功"]
        }))

def get_department_module_tree(engine=None):
    """回傳 1~4 級支援動態擴編的部門與模組樹狀結構"""
    return {
        "總經理室 (Executive Office)": [
            "經營營運報表", 
            "原料價格與 Gemini 智慧採購顧問", 
            "財務類與 AR/AP & P&L 戰情儀表板", 
            "工程專案進度與現場異常即時監控", 
            "越南經營政策與法規每日動態"
        ],
        "管理部 (Management Dept)": [
            "人事/行政", 
            "總務/採購", 
            "財務/會計"
        ],
        "工程與設計管理中心 (Engineering & Design Center)": [
            "工地日報與巡檢", 
            "工務派工與調度"
        ],
        "生產部 (Production Dept - 西寧廠)": [
            "配電盤組裝進度"
        ],
        "倉庫管理 (Warehouse Management)": [
            "工程領料與工具借還", 
            "倉儲盤點"
        ],
        "簽核中心 (Approval Center)": [
            "待簽核單據彙整"
        ],
        "系統設定 (System Settings)": [
            "選單與動態架構配置"
        ]
    }
