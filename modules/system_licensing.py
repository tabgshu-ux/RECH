import streamlit as st

# 🏢 系統所有可販售/可訂閱之功能模組清單
ALL_ERP_MODULES = {
    "📈 營運戰情室 (Executive)": [
        "🔴 原料價格與隨時股市物價/匯率",
        "📊 財務類顯示資料 (AR/AP & P&L)",
        "⚡ 工程專案進度與驗收資料"
    ],
    "🧾 財務會計部 (Finance & Accounting)": [
        "🛒 採購與應付帳款 (AP & 廠商發票)",
        "📋 銷售與應收帳款 (AR & 催收歷史)",
        "📄 越南電子發票 XML 解析與登錄",
        "📧 通用信箱電子發票自動讀取 (IMAP)",
        "📊 電子發票張數監控與預警"
    ],
    "🛠️ 研發工程部 (R&D & Engineering)": [
        "⚡ 配電盤估價與資材報價總合"
    ],
    "🏢 行政總務部 (General Affairs)": [
        "📦 固定資產設備與總務採購",
        "✍️ 電子簽核與請款審核中心"
    ],
    "👥 人力資源部 (Human Resources)": [
        "👤 人事檔案與勞動合約管理"
    ],
    "🏭 生產倉儲部 (Plant & Warehouse)": [
        "📦 倉庫庫存與資材条碼管理",
        "✂️ 板金加工組工單",
        "🎨 烤漆塗裝組品管",
        "⚡ 配電盤組裝配線組"
    ]
}

def render_licensing_control_page():
    st.title("🎛️ 客戶 ERP 模組授權與訂閱勾選中心 (SaaS License Control)")
    st.caption("商業化販售專用：為不同企業客戶客製化勾選開關功能，打勾即可開通使用。")

    # 1. 初始化全域已開通模組狀態 (Session State)
    if "enabled_modules" not in st.session_state:
        # 預設全選 (全功能開放)
        all_features = []
        for dept, feats in ALL_ERP_MODULES.items():
            all_features.extend(feats)
        st.session_state.enabled_modules = set(all_features)

    # 2. 快速預設套裝方案按鈕 (Presets)
    st.markdown("### ⚡ 一鍵載入客戶訂閱方案 (Presets)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📦 載入「標準製造與倉儲版」方案", use_container_width=True):
            st.session_state.enabled_modules = set(
                ALL_ERP_MODULES["🏭 生產倉儲部 (Plant & Warehouse)"] +
                ALL_ERP_MODULES["👥 人力資源部 (Human Resources)"]
            )
            st.success("已載入製造倉儲版方案！")
            st.rerun()

    with col2:
        if st.button("💰 載入「財務與進銷存版」方案", use_container_width=True):
            st.session_state.enabled_modules = set(
                ALL_ERP_MODULES["🧾 財務會計部 (Finance & Accounting)"] +
                ALL_ERP_MODULES["🏢 行政總務部 (General Affairs)"]
            )
            st.success("已載入財務進銷存版方案！")
            st.rerun()

    with col3:
        if st.button("👑 載入「旗艦企業全功能版」方案", use_container_width=True):
            all_features = []
            for dept, feats in ALL_ERP_MODULES.items():
                all_features.extend(feats)
            st.session_state.enabled_modules = set(all_features)
            st.success("已開啟全部功能模組！")
            st.rerun()

    st.divider()

    # 3. 逐項勾選 UI (Checkboxes)
    st.markdown("### 🎯 自訂客製化勾選功能 (勾選以開通)")
    
    updated_enabled = set()

    for dept_name, feature_list in ALL_ERP_MODULES.items():
        with st.expander(f"📌 {dept_name}", expanded=True):
            # 提供部門全選/全不選
            cols = st.columns(2)
            for i, feat in enumerate(feature_list):
                # 判斷當前是否已勾選
                is_checked = feat in st.session_state.enabled_modules
                # 渲染單選勾選框
                checked = st.checkbox(
                    f"開通：{feat}",
                    value=is_checked,
                    key=f"chk_{dept_name}_{i}"
                )
                if checked:
                    updated_enabled.add(feat)

    # 4. 儲存設定
    st.divider()
    if st.button("💾 儲存並更新客戶模組權限", type="primary", use_container_width=True):
        st.session_state.enabled_modules = updated_enabled
        st.success("🎉 客戶模組授權已更新！系統主選單已即時同步連動開關。")
        st.rerun()

def show():
    render_licensing_control_page()
