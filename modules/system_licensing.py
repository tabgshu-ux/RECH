import streamlit as st

# ----------------------------------------------------
# 🏢 全系統可供販售/勾選之功能模組目錄 (SaaS Catalog)
# ----------------------------------------------------
ALL_ERP_MODULES = {
    "📈 營運戰情室 (Executive)": [
        "🔴 原料價格與隨時股市物價/匯率",
        "📊 財務類顯示資料 (AR/AP & P&L)",
        "⚡ 工程專案進度與驗收資料",
    ],
    "🧾 財務會計部 (Finance & Accounting)": [
        "🛒 採購與應付帳款 (AP & 廠商發票)",
        "📋 銷售與應收帳款 (AR & 催收歷史)",
        "📄 越南電子發票 XML 解析與登錄",
        "📧 通用信箱電子發票自動讀取 (IMAP)",
        "📊 電子發票張數監控與預警",
    ],
    "🛠️ 研發工程部 (R&D & Engineering)": [
        "⚡ 配電盤估價與資材報價總合"
    ],
    "🏢 行政總務部 (General Affairs)": [
        "📦 固定資產設備與總務採購",
        "✍️ 電子簽核與請款審核中心",
    ],
    "👥 人力資源部 (Human Resources)": [
        "👤 人事檔案與勞動合約管理"
    ],
    "🏭 生產倉儲部 (Plant & Warehouse)": [
        "📦 倉庫庫存與資材條碼管理",
        "✂️ 板金加工組工單",
        "🎨 烤漆塗裝組品管",
        "⚡ 配電盤組裝配線組",
    ],
}


def render_licensing_control_page(lang="繁體中文"):
    st.title("🎛️ 客戶 ERP 模組授權與功能開關中心 (SaaS Control)")
    st.caption(
        "專為商業化販售設計：在此勾選客戶購買的功能，未勾選的功能將自動從主選單隱藏。"
    )

    # 1. 初始化全域已開通模組 (預設全選開放)
    if "enabled_modules" not in st.session_state:
        all_feats = []
        for dept, feats in ALL_ERP_MODULES.items():
            all_feats.extend(feats)
        st.session_state.enabled_modules = set(all_feats)

    # 2. 快速預設套裝方案按鈕 (Preset Packages)
    st.markdown("### ⚡ 快速一鍵載入客戶訂閱方案")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📦 載入「製造與倉儲專業版」", use_container_width=True):
            st.session_state.enabled_modules = set(
                ALL_ERP_MODULES["🏭 生產倉儲部 (Plant & Warehouse)"]
                + ALL_ERP_MODULES["👥 人力資源部 (Human Resources)"]
            )
            st.success("已自動載入「製造與倉儲版」勾選設定！")
            st.rerun()

    with col2:
        if st.button("💰 載入「財務與進銷存版」", use_container_width=True):
            st.session_state.enabled_modules = set(
                ALL_ERP_MODULES["🧾 財務會計部 (Finance & Accounting)"]
                + ALL_ERP_MODULES["🏢 行政總務部 (General Affairs)"]
            )
            st.success("已自動載入「財務與進銷存版」勾選設定！")
            st.rerun()

    with col3:
        if st.button("👑 載入「旗艦企業全功能版」", use_container_width=True):
            all_feats = []
            for dept, feats in ALL_ERP_MODULES.items():
                all_feats.extend(feats)
            st.session_state.enabled_modules = set(all_feats)
            st.success("已自動開通全部功能模組！")
            st.rerun()

    st.divider()

    # 3. 逐項勾選 UI (Checkboxes)
    st.markdown("### 🎯 客製化功能勾選清單 (勾選即開啟)")

    updated_enabled = set()

    for dept_name, feature_list in ALL_ERP_MODULES.items():
        with st.expander(f"📌 {dept_name}", expanded=True):
            cols = st.columns(2)
            for idx, feat in enumerate(feature_list):
                col_idx = idx % 2
                is_checked = feat in st.session_state.enabled_modules
                with cols[col_idx]:
                    checked = st.checkbox(
                        f"開通：{feat}",
                        value=is_checked,
                        key=f"chk_{dept_name}_{idx}",
                    )
                    if checked:
                        updated_enabled.add(feat)

    st.divider()

    # 4. 儲存設定按鈕
    if st.button(
        "💾 儲存並更新客戶模組授權", type="primary", use_container_width=True
    ):
        st.session_state.enabled_modules = updated_enabled
        st.success("🎉 客戶模組授權設定已成功儲存！系統主選單已連動更新。")
        st.rerun()


def render(*args, **kwargs):
    render_licensing_control_page()


def show(*args, **kwargs):
    render_licensing_control_page()


def main(*args, **kwargs):
    render_licensing_control_page()
