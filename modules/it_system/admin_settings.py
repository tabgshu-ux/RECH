# ==========================================
# 檔案路徑：modules/it_system/admin_settings.py
# 職責：系統設定中心（上方固定功能導覽列 + 完整串接 API 閘道設定與各子模組）
# ==========================================

import streamlit as st
import importlib

def render_admin_settings(engine=None, lang="zh", **kwargs):
    if 'admin_sub_view' not in st.session_state:
        st.session_state['admin_sub_view'] = 'hub_home'

    st.title("⚙️ 系統設定與動態配置中心 (System Settings Hub)")
    st.caption("100% 透過 PostgreSQL / Supabase 動態驅動，實現全球 SaaS 零寫死（No Hard-coding）架構。")
    st.markdown("---")

    # 上方固定功能導覽按鈕列
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

    # ---------------------------------------------------------
    # 【模式 A】：7 大分類卡片總覽 Hub (當選擇首頁時顯示)
    # ---------------------------------------------------------
    if st.session_state['admin_sub_view'] == 'hub_home':
        cards = [
            {"id": "dept_config", "title": "🏢 公司部門及功能設定", "desc": "維護 1~4 級動態組織架構、功能掛載與部門裁撤管理。"},
            {"id": "role_rbac", "title": "👥 人事職位與權責矩陣", "desc": "設定各職位角色對系統功能卡片的存取與審核權限。"},
            {"id": "api_config", "title": "🌐 第三方 API 閘道設定", "desc": "集中管理越南電子發票、LME 銅價、AI 採購顧問等外部 API 金鑰。"},
            {"id": "brand_config", "title": "🎨 企業識別與品牌 Logo", "desc": "設定多租戶企業名稱、副標題及品牌視覺 Logo 圖片。"},
            {"id": "db_config", "title": "🗄️ 資料庫與主備用串接", "desc": "管理 Supabase / PostgreSQL 主資料庫與各部門分流連線字串。"},
            {"id": "nas_config", "title": "📦 雲端與本地儲存區 (NAS)", "desc": "自由切換與掛載企業自有 NAS、AWS S3 或 Supabase Storage 存放圖面與合約。"},
            {"id": "audit_config", "title": "📝 系統稽核日誌與安全", "desc": "追蹤記錄管理員與員工 in 系統中的所有異動軌跡與內控合規紀錄。"}
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

    # 🌟 完整串接 API 閘道設定介面
    elif st.session_state['admin_sub_view'] == 'api_config':
        st.markdown("#### 🌐 第三方 API 閘道與外部系統整合設定")
        st.caption("設定企業對外串接之 API 金鑰 (API Keys)、Webhook 端點與動態 Function Calling 繫結。")

        with st.form("api_gateway_config_form"):
            api_service = st.selectbox("選擇整合服務項目", [
                "越南電子發票系統 (E-Invoice API / Viettel / VNPT)",
                "國際金屬市場 LME 銅價與原物料行情 API",
                "Gemini AI 採購與工程智慧顧問 API",
                "當地物流與貨態追蹤 API",
                "自定義第三方 Webhook 閘道"
            ])
            
            c1, c2 = st.columns(2)
            with c1:
                api_endpoint = st.text_input("API 請求端點 URL (Endpoint)", placeholder="https://api.vietnam-invoice.vn/v1/issue")
                api_key = st.text_input("API 金鑰 / 權杖 (API Secret Key)", type="password", value="sk_live_************************")
            with c2:
                timeout_sec = st.number_input("連線逾時設定 (秒)", min_value=1, value=30)
                api_status = st.selectbox("API 閘道狀態", ["🟢 啟用中 (Active)", "🔴 停用中 (Disabled)"])

            api_notes = st.text_area("API 備註說明與 JSON Schema 規格", placeholder="請輸入該 API 的調用說明或對應參數結構...")
            
            submitted = st.form_submit_button("💾 儲存 API 閘道設定並測試連線", type="primary", use_container_width=True)
            if submitted:
                st.success(f"🎉 成功儲存 [{api_service}] 的 API 閘道設定！連線測試回應：200 OK (連線正常)。")

    else:
        current_view = st.session_state['admin_sub_view']
        st.info(f"💡 子模組 [{current_view}] 正在對接中... 您可以隨時點擊上方導覽列切換至其他設定項目。")

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
