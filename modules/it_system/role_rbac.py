import streamlit as st
import pandas as pd
from sqlalchemy import text

# 手機優先響應式 UI
MOBILE_CSS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.25rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1.0rem !important; }
    p, div, span, label { font-size: 0.9rem !important; }
    .stButton button { width: 100% !important; min-height: 44px !important; }
}
</style>
"""
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

I18N = {
    "繁體中文": {
        "title": "🔒 IT 系統管理中心 - 組織與權限控制",
        "tab_rbac": "⚙️ 角色權限與模組拼圖",
        "tab_dept": "🏢 獨立企業部門管理",
        "save_success": "🎉 設定已成功儲存！",
    },
    "Tiếng Việt": {
        "title": "🔒 Trung tâm CNTT - Quản lý Tổ chức & Phân quyền",
        "tab_rbac": "⚙️ Vai trò & Module",
        "tab_dept": "🏢 Quản lý Phòng ban",
        "save_success": "🎉 Đã lưu cài đặt thành công!",
    },
    "English": {
        "title": "🔒 IT Admin Center - Org & Permissions",
        "tab_rbac": "⚙️ Roles & Module Puzzles",
        "tab_dept": "🏢 Independent Department Management",
        "save_success": "🎉 Settings saved successfully!",
    }
}

def get_department_module_tree():
    if "custom_department_module_tree" not in st.session_state:
        st.session_state.custom_department_module_tree = {
            "📈 總經理室 (Executive Office)": [
                "🔴 原料價格與 Gemini 智慧採購顧問",
                "📊 財務類顯示資料 (AR/AP & P&L)",
                "⚡ 工程專案進度與現場異常監控",
                "📰 越南經營政策與法規每日動態"
            ],
            "👔 管理部 (Management Dept)": [
                "📢 發送公告佈告欄",
                "👤 員工個人檔案與人事管理",
                "🏢 廠內員工固定打卡與出勤紀錄",
                "📍 外勤位置辦理與工地即時人數",
                "🥗 幹部宿舍伙食與採購控管",
                "🏭 工作廠區管理",
                "🚗 廠區車輛進出口門禁與派車審核",
                "🛠️ 車輛維修保養紀錄",
                "🏢 固定資產與設備管理",
                "🛒 採購與應付帳款 (AP)",
                "📋 應收帳款與對帳管理中心",
                "📊 越南稅務標準財務報表 (Thông tư 200)",
                "💰 員工薪資計算與保險扣除",
                "📄 電子發票綜合管理與 XML 歸檔"
            ],
            "✍️ 全公司電子簽核中心 (Approval Center)": [
                "✍️ 提交請假/採購與即時進度追蹤 / 審核"
            ],
            "🛠️ 工程與設計管理中心 (Engineering & Design Center)": [
                "⚡ 1. 工程主管戰情室與案場管理",
                "⚡ 2. 工程專案報價系統",
                "📍 3. 現場外勤打卡與作業登記",
                "📋 4. 施工日報表與點工點料登記",
                "🤖 5. AI 施工照片辨識與稽核",
                "⚠️ 6. 工程證照預警與機具檢驗預警",
                "🎨 7. 配電盤電氣與機構設計圖庫",
                "🔌 8. 配電盤 BOM 零件與採購連動",
                "👷 9. 外包商計價與偶鐸管理",
                "🧪 10. FAT/SAT 出廠與現場驗收管理"
            ],
            "🏭 生產部 (Production Dept)": [
                "✂️ [板金] 板金加工組工單與條碼",
                "🎨 [塗料] 粉體塗裝烤漆組品管",
                "⚡ [配盤] 配電盤組裝配線組"
            ],
            "📦 倉庫管理 (Warehouse Management)": [
                "📦 [倉儲] 倉庫庫存與資材條碼管理"
            ],
            "💻 資訊管理部 (IT & System)": [
                "🔒 系統角色權限與模組開關設定",
                "🔌 API 串聯設定中心"
            ]
        }
    return st.session_state.custom_department_module_tree

def render(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in I18N else "繁體中文"
    L = I18N[active_lang]

    st.markdown(f"### {L['title']}")

    tab_rbac, tab_dept = st.tabs([L["tab_rbac"], L["tab_dept"]])

    dept_tree = get_department_module_tree()

    # ----------------------------------------------------
    # 🏢 Tab 2: 獨立企業部門管理（純粹新增/刪除部門，不強迫填職位）
    # ----------------------------------------------------
    with tab_dept:
        st.markdown("### 🏢 企業部門純粹新增與管理")
        st.info("💡 在此您可以純粹新增或刪除部門（例如新增『外勤工程處』），完全不需填寫職位名稱。")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("#### ➕ 1. 建立新部門")
            with st.form("form_isolated_dept"):
                new_dept_name = st.text_input("部門名稱與代號 *", placeholder="例如: 外勤工程處 (Field Ops)")
                new_dept_desc = st.text_input("部門職責描述", placeholder="負責全公司外勤與工地打卡")
                if st.form_submit_button("🚀 確認建立新部門", type="primary", use_container_width=True):
                    if new_dept_name:
                        dept_key = f"{new_dept_name.strip()} ({new_dept_desc})" if new_dept_desc else new_dept_name.strip()
                        if dept_key not in dept_tree:
                            dept_tree[dept_key] = []
                            st.success(f"🎉 成功建立新部門：{new_dept_name}！")
                            st.rerun()
                        else:
                            st.warning("⚠️ 此部門名稱已存在！")
                    else:
                        st.warning("⚠️ 請輸入部門名稱！")

        with col_d2:
            st.markdown("#### 🗑️ 2. 刪除部門")
            with st.form("form_delete_isolated_dept"):
                target_del = st.selectbox("選擇要刪除的部門", options=list(dept_tree.keys()))
                if st.form_submit_button("🗑️ 確認刪除此部門", use_container_width=True):
                    if len(dept_tree) > 1:
                        del dept_tree[target_del]
                        st.success(f"🗑️ 已成功刪除部門：{target_del}")
                        st.rerun()
                    else:
                        st.error("🚫 系統至少須保留一個部門！")

        st.markdown("---")
        st.markdown("#### 🧩 3. 針對指定部門指派功能模組拼圖")
        target_mod_dept = st.selectbox("🎯 選擇目標部門：", options=list(dept_tree.keys()), key="sel_dept_puzzle")
        current_mods = dept_tree[target_mod_dept]

        master_all_modules = [
            "🔴 原料價格與 Gemini 智慧採購顧問", "📊 財務類顯示資料 (AR/AP & P&L)",
            "⚡ 工程專案進度與現場異常監控", "📰 越南經營政策與法規每日動態",
            "📢 發送公告佈告欄", "👤 員工個人檔案與人事管理",
            "🏢 廠內員工固定打卡與出勤紀錄", "📍 外勤位置辦理與工地即時人數",
            "🥗 幹部宿舍伙食與採購控管", "🏭 工作廠區管理",
            "🚗 廠區車輛進出口門禁與派車審核", "🛠️ 車輛維修保養紀錄",
            "🏢 固定資產與設備管理", "🛒 採購與應付帳款 (AP)",
            "📋 應收帳款與對帳管理中心", "📊 越南稅務標準財務報表 (Thông tư 200)",
            "💰 員工薪資計算與保險扣除", "📄 電子發票綜合管理與 XML 歸檔",
            "✍️ 提交請假/採購與即時進度追蹤 / 審核", "⚡ 1. 工程主管戰情室與案場管理",
            "⚡ 2. 工程專案報價系統", "📍 3. 現場外勤打卡與作業登記",
            "📋 4. 施工日報表與點工點料登記", "🤖 5. AI 施工照片辨識與稽核",
            "⚠️ 6. 工程證照預警與機具檢驗預警", "🎨 7. 配電盤電氣與機構設計圖庫",
            "🔌 8. 配電盤 BOM 零件與採購連動", "👷 9. 外包商計價與偶鐸管理",
            "🧪 10. FAT/SAT 出廠與現場驗收管理", "📦 [倉儲] 倉庫庫存與資材條碼管理",
            "✂️ [板金] 板金加工組工單與條碼", "🎨 [塗料] 粉體塗裝烤漆組品管",
            "⚡ [配盤] 配電盤組裝配線組", "🔒 系統角色權限與模組開關設定",
            "🔌 API 串聯設定中心"
        ]

        new_selected = []
        cols_pz = st.columns(2)
        for idx, mod_item in enumerate(master_all_modules):
            with cols_pz[idx % 2]:
                puz_key = f"puz_{target_mod_dept}_{idx}_{mod_item}"
                if puz_key not in st.session_state:
                    st.session_state[puz_key] = (mod_item in current_mods)
                if st.checkbox(mod_item, key=puz_key):
                    new_selected.append(mod_item)

        if st.button("💾 儲存此部門的功能拼圖配置", type="primary", use_container_width=True):
            dept_tree[target_mod_dept] = new_selected
            st.success("🎉 部門功能模組配置已成功更新！")
            st.rerun()

    # ----------------------------------------------------
    # ⚙️ Tab 1: 角色權限設定 (RBAC)
    # ----------------------------------------------------
    with tab_rbac:
        st.markdown("### ⚙️ 組織角色與權限指派")
        st.info("💡 在此設定職位角色（如：總經理、外勤技師）所屬部門與可操作頁面。")
        st.write("（此處可維持原有的 RBAC 角色對應邏輯與表格呈現）")
