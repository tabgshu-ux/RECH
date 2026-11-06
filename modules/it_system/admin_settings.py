# ==========================================
# 檔案路徑：modules/it_system/admin_settings.py
# 職責：系統設定總覽卡片中心（嚴格遵循模組化，調度獨立子模組）
# ==========================================

import streamlit as st
import importlib

def render_admin_settings(engine=None, lang="zh", **kwargs):
    if 'admin_sub_view' not in st.session_state:
        st.session_state['admin_sub_view'] = 'hub_home'

    # 若非在首頁，提供返回系統設定總覽選單的按鈕
    if st.session_state['admin_sub_view'] != 'hub_home':
        if st.button("⬅️ 返回系統設定總覽選單", type="secondary"):
            st.session_state['admin_sub_view'] = 'hub_home'
            st.rerun()
        st.markdown("---")

    # ---------------------------------------------------------
    # 【模式 A】：7 大分類卡片總覽 Hub
    # ---------------------------------------------------------
    if st.session_state['admin_sub_view'] == 'hub_home':
        st.title("⚙️ 系統設定與動態配置中心 (System Settings Hub)")
        st.caption("100% 透過 PostgreSQL / Supabase 動態驅動，實現全球 SaaS 零寫死（No Hard-coding）架構，支援未來公司無限擴編。")
        st.markdown("---")

        cards = [
            {"id": "dept_config", "title": "🏢 公司部門及功能設定", "desc": "維護 1~4 級動態組織架構、功能掛載與部門裁撤管理。"},
            {"id": "role_rbac", "title": "👥 人事職位與權責矩陣", "desc": "設定各職位角色對系統功能卡片的存取與審核權限。"},
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
    # 【模式 B】：透過獨立模組檔案動態載入對應子功能
    # ---------------------------------------------------------
    elif st.session_state['admin_sub_view'] == 'role_rbac':
        try:
            mod = importlib.import_module("modules.it_system.role_rbac")
            importlib.reload(mod)
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=lang)
            elif hasattr(mod, "render_role_rbac_page"):
                mod.render_role_rbac_page(engine=engine, lang=lang)
            else:
                st.info("💡 role_rbac 模組已成功載入。")
        except Exception as e:
            st.error(f"載入獨立模組 [modules.it_system.role_rbac] 發生異常: {e}")

    elif st.session_state['admin_sub_view'] == 'dept_config':
        try:
            mod = importlib.import_module("modules.it_system.department_config")
            importlib.reload(mod)
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=lang)
            else:
                st.info("💡 department_config 模組已成功載入。")
        except Exception as e:
            st.error(f"載入獨立模組 [modules.it_system.department_config] 發生異常: {e}")

    else:
        st.info(f"💡 子模組 [{st.session_state['admin_sub_view']}] 正在對接中...")

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
