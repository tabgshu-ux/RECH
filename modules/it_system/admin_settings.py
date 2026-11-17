# ==========================================
# 檔案路徑：modules/it_system/admin_settings.py
# 職責：系統設定純路由分發中心（落實鬆耦合，絕不把子功能塞在同一個檔案）
# ==========================================# ==========================================
# 檔案路徑：modules/it_system/admin_settings.py
# 職責：系統設定純路由分發中心（正確對接 modules.it_system.API 底下的所有獨立 API 模組）
# ==========================================

import streamlit as st
import importlib

def render_admin_settings(engine=None, lang="zh", **kwargs):
    if 'admin_sub_view' not in st.session_state:
        st.session_state['admin_sub_view'] = 'hub_home'

    st.title("⚙️ 系統設定與動態配置中心 (System Settings Hub)")
    st.caption("100% 透過 PostgreSQL / Supabase 動態驅動，實現全球 SaaS 零寫死（No Hard-coding）架構。")
    st.markdown("---")

    # 1. 上方固定功能導覽按鈕列
    nav_cols = st.columns(7)
    nav_items = [
        {"id": "hub_home", "name": "🏠 設定總覽"},
        {"id": "dept_config", "name": "🏢 公司部門"},
        {"id": "role_rbac", "name": "👥 權責矩陣"},
        {"id": "api_config", "name": "🌐 API 閘道"},
        {"id": "brand_config", "name": "🎨 品牌 Logo"},
        {"id": "db_config", "name": "🗄️ 資料庫"},
        {"id": "nas_config", "name": "📦 雲端儲存"}
    ]

    for idx, item in enumerate(nav_items):
        with nav_cols[idx]:
            is_active = (st.session_state['admin_sub_view'] == item['id'])
            if st.button(item['name'], use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state['admin_sub_view'] = item['id']
                st.rerun()

    st.markdown("---")

    current_view = st.session_state['admin_sub_view']

    # 2. 👑 設定總覽首頁（顯示 7 大功能卡片）
    if current_view == 'hub_home':
        cards = [
            {"id": "dept_config", "title": "🏢 公司部門及功能設定", "desc": "維護 1~4 級動態組織架構、功能掛載與部門裁撤管理。"},
            {"id": "role_rbac", "title": "👥 人事職位與權責矩陣", "desc": "設定各職位角色對系統功能卡片的存取與審核權限。"},
            {"id": "api_config", "title": "🌐 第三方 API 閘道設定", "desc": "集中管理越南電子發票、Zalo/LINE、LME 銅價、硬體與 Gemini AI 等外部 API。"},
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

    # 3. 🛡️ 各子模組路由分發
    elif current_view == 'dept_config':
        load_sub_module("modules.it_system.department_config", engine, lang)

    elif current_view == 'role_rbac':
        load_sub_module("modules.it_system.role_rbac", engine, lang)

    # 🌟 核心修正：在 API 閘道頁面中，透過分頁將 modules.it_system.API 底下的所有模組完美串接進來
    elif current_view == 'api_config':
        st.markdown("#### 🌐 全方位第三方 API 閘道與外部系統整合中心")
        st.caption("集中管理所有置於 modules/it_system/API/ 底下的獨立外部 API 與硬體串接模組。")
        
        api_tabs = st.tabs([
            "🧾 越南電子發票", 
            "💬 Zalo / LINE 通知", 
            "📈 LME 銅價與外匯", 
            "🔌 硬體設備與 POS", 
            "🤖 Gemini AI 智慧"
        ])

        with api_tabs[0]:
            load_sub_module("modules.it_system.API.it_invoice_config", engine, lang)
        with api_tabs[1]:
            load_sub_module("modules.it_system.API.zalo_line_api", engine, lang)
        with api_tabs[2]:
            load_sub_module("modules.it_system.API.lme_market_api", engine, lang)
        with api_tabs[3]:
            load_sub_module("modules.it_system.API.hardware_device_api", engine, lang)
        with api_tabs[4]:
            load_sub_module("modules.it_system.API.ai_gemini_api", engine, lang)

    elif current_view == 'brand_config':
        load_sub_module("modules.it_system.branding_config", engine, lang)

    elif current_view == 'db_config':
        load_sub_module("modules.it_system.db_bridge", engine, lang)

    elif current_view == 'nas_config':
        st.markdown("#### 📦 雲端與本地儲存區設定 (NAS / S3)")
        st.info("💡 該模組正在獨立維護中。")

    elif current_view == 'audit_config':
        load_sub_module("modules.it_system.audit_logs", engine, lang)

    else:
        st.info(f"💡 子模組 [{current_view}] 正在對接中...")

def load_sub_module(module_path, engine, lang):
    """安全動態載入獨立子模組的通用輔助函式"""
    try:
        mod = importlib.import_module(module_path)
        importlib.reload(mod)
        if hasattr(mod, "render"):
            mod.render(engine=engine, lang=lang)
        elif hasattr(mod, "show"):
            mod.show(engine=engine, lang=lang)
        elif hasattr(mod, "render_page"):
            mod.render_page(engine=engine, lang=lang)
        else:
            st.info(f"💡 模組 [{module_path}] 已成功載入，但未偵測到標準渲染函式。")
    except Exception as e:
        st.error(f"❌ 載入獨立模組 [{module_path}] 發生異常: {e}")

def get_department_module_tree(engine=None):
    return {
        "總經理室 (Executive Office)": ["經營營運報表", "原料價格與 Gemini 智慧採購顧問"],
        "管理部 (Management Dept)": ["人事/行政", "總務/採購", "財務/會計"],
        "工程與設計管理中心 (Engineering & Design Center)": ["工地日報與巡檢", "工務派工與調度"],
        "系統設定 (System Settings)": ["選單與動態架構配置"]
    }

import streamlit as st
import importlib

def render_admin_settings(engine=None, lang="zh", **kwargs):
    if 'admin_sub_view' not in st.session_state:
        st.session_state['admin_sub_view'] = 'hub_home'

    st.title("⚙️ 系統設定與動態配置中心 (System Settings Hub)")
    st.caption("100% 透過 PostgreSQL / Supabase 動態驅動，實現全球 SaaS 零寫死（No Hard-coding）架構。")
    st.markdown("---")

    # 1. 上方固定功能導覽按鈕列（只負責切換分頁狀態）
    nav_cols = st.columns(7)
    nav_items = [
        {"id": "hub_home", "name": "🏠 設定總覽"},
        {"id": "dept_config", "name": "🏢 公司部門"},
        {"id": "role_rbac", "name": "👥 權責矩陣"},
        {"id": "api_config", "name": "🌐 API 閘道"},
        {"id": "brand_config", "name": "🎨 品牌 Logo"},
        {"id": "db_config", "name": "🗄️ 資料庫"},
        {"id": "nas_config", "name": "📦 雲端儲存"}
    ]

    for idx, item in enumerate(nav_items):
        with nav_cols[idx]:
            is_active = (st.session_state['admin_sub_view'] == item['id'])
            if st.button(item['name'], use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state['admin_sub_view'] = item['id']
                st.rerun()

    st.markdown("---")

    current_view = st.session_state['admin_sub_view']

    # 2. 👑 設定總覽首頁（顯示 7 大功能卡片）
    if current_view == 'hub_home':
        cards = [
            {"id": "dept_config", "title": "🏢 公司部門及功能設定", "desc": "維護 1~4 級動態組織架構、功能掛載與部門裁撤管理。"},
            {"id": "role_rbac", "title": "👥 人事職位與權責矩陣", "desc": "設定各職位角色對系統功能卡片的存取與審核權限。"},
            {"id": "api_config", "title": "🌐 第三方 API 閘道設定", "desc": "集中管理越南電子發票、Zalo/LINE 訊息、LME 銅價與硬體裝置等外部 API 金鑰。"},
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

    # 3. 🛡️ 路由分發：嚴格將請求轉發給各自獨立的模組檔案（不把程式碼寫在主控台裡）
    elif current_view == 'dept_config':
        load_sub_module("modules.it_system.department_config", engine, lang)

    elif current_view == 'role_rbac':
        load_sub_module("modules.it_system.role_rbac", engine, lang)

    elif current_view == 'api_config':
        # 直接對接您專案內既有的 it_invoice_config 獨立模組
        load_sub_module("modules.it_system.it_invoice_config", engine, lang)

    elif current_view == 'brand_config':
        load_sub_module("modules.it_system.branding_config", engine, lang)

    elif current_view == 'db_config':
        load_sub_module("modules.it_system.db_bridge", engine, lang)

    elif current_view == 'nas_config':
        st.markdown("#### 📦 雲端與本地儲存區設定 (NAS / S3)")
        st.info("💡 該模組正在獨立維護中。您可以於 `modules/it_system/` 建立專屬的獨立設定檔案。")

    elif current_view == 'audit_config':
        load_sub_module("modules.it_system.audit_logs", engine, lang)

    else:
        st.info(f"💡 子模組 [{current_view}] 正在對接中...")

def load_sub_module(module_path, engine, lang):
    """安全動態載入獨立子模組的通用輔助函式"""
    try:
        mod = importlib.import_module(module_path)
        importlib.reload(mod)
        if hasattr(mod, "render"):
            mod.render(engine=engine, lang=lang)
        elif hasattr(mod, "show"):
            mod.show(engine=engine, lang=lang)
        elif hasattr(mod, "render_page"):
            mod.render_page(engine=engine, lang=lang)
        else:
            st.info(f"💡 模組 [{module_path}] 已成功載入，但未偵測到標準渲染函式。")
    except Exception as e:
        st.error(f"❌ 載入獨立模組 [{module_path}] 發生異常: {e}")

def get_department_module_tree(engine=None):
    return {
        "總經理室 (Executive Office)": ["經營營運報表", "原料價格與 Gemini 智慧採購顧問"],
        "管理部 (Management Dept)": ["人事/行政", "總務/採購", "財務/會計"],
        "工程與設計管理中心 (Engineering & Design Center)": ["工地日報與巡檢", "工務派工與調度"],
        "系統設定 (System Settings)": ["選單與動態架構配置"]
    }
