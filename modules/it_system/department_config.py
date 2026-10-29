import streamlit as st
import pandas as pd
from sqlalchemy import text

# 手機優先響應式設計
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

DEPT_I18N = {
    "繁體中文": {
        "title": "🏢 獨立企業部門管理與模組拼圖配置",
        "caption": "純粹管理企業部門架構與功能模組對應，不與職位角色混淆。",
        "add_header": "➕ 1. 建立新部門",
        "del_header": "🗑️ 2. 刪除指定部門",
        "puzzle_header": "🧩 3. 針對指定部門指派功能模組拼圖",
        "success_add": "🎉 成功建立新部門！",
        "success_del": "🗑️ 已成功刪除部門！",
        "success_save": "🎉 部門功能模組配置已成功更新！"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Phòng ban Độc lập & Cấu hình Module",
        "caption": "Quản lý thuần túy cấu trúc phòng ban và phân bổ module.",
        "add_header": "➕ 1. Thêm phòng ban mới",
        "del_header": "🗑️ 2. Xóa phòng ban",
        "puzzle_header": "🧩 3. Phân bổ module cho phòng ban",
        "success_add": "🎉 Đã tạo phòng ban thành công!",
        "success_del": "🗑️ Đã xóa phòng ban!",
        "success_save": "🎉 Đã cập nhật cấu hình module!"
    },
    "English": {
        "title": "🏢 Independent Department Management & Module Puzzles",
        "caption": "Pure department structure and module mapping management.",
        "add_header": "➕ 1. Create New Department",
        "del_header": "🗑️ 2. Delete Department",
        "puzzle_header": "🧩 3. Assign Module Puzzles to Department",
        "success_add": "🎉 New department created successfully!",
        "success_del": "🗑️ Department deleted successfully!",
        "success_save": "🎉 Department module configuration updated successfully!"
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
    active_lang = lang if lang in DEPT_I18N else "繁體中文"
    L = DEPT_I18N[active_lang]

    st.markdown(f"### {L['title']}")
    st.caption(L['caption'])

    dept_tree = get_department_module_tree()

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown(f"#### {L['add_header']}")
        with st.form("form_create_dept_only"):
            new_d_name = st.text_input("部門名稱與代號 *", placeholder="例如: 外勤工程處 (Field Ops)")
            new_d_desc = st.text_input("部門職責描述", placeholder="負責全公司外勤與工地打卡")
            if st.form_submit_button("🚀 確認建立新部門", type="primary", use_container_width=True):
                if new_d_name:
                    dept_key = f"{new_d_name.strip()} ({new_d_desc})" if new_d_desc else new_d_name.strip()
                    if dept_key not in dept_tree:
                        dept_tree[dept_key] = []
                        if engine:
                            try:
                                with engine.begin() as conn_d:
                                    conn_d.execute(text("INSERT INTO system_departments (department_name, description) VALUES (:n, :d) ON CONFLICT DO NOTHING"),
                                                   {"n": new_d_name.strip(), "d": new_d_desc})
                            except Exception:
                                pass
                        st.success(L['success_add'])
                        st.rerun()
                    else:
                        st.warning("⚠️ 此部門名稱已存在！")
                else:
                    st.warning("⚠️ 請輸入部門名稱！")

    with col_d2:
        st.markdown(f"#### {L['del_header']}")
        with st.form("form_delete_dept_only"):
            target_del_dept = st.selectbox("選擇要刪除的部門", options=list(dept_tree.keys()))
            if st.form_submit_button("🗑️ 確認刪除此部門", use_container_width=True):
                if len(dept_tree) > 1:
                    del dept_tree[target_del_dept]
                    st.success(L['success_del'])
                    st.rerun()
                else:
                    st.error("🚫 系統至少須保留一個部門！")

    st.markdown("---")
    st.markdown(f"#### {L['puzzle_header']}")
    
    target_mod_dept = st.selectbox("🎯 請選擇欲配置功能模組的目標部門：", options=list(dept_tree.keys()), key="select_dept_for_modules_puzzle")
    current_mods = dept_tree[target_mod_dept]

    st.markdown(f"##### 📦 目前【{target_mod_dept}】已啟用的功能拼圖：")
    if current_mods:
        for cm in current_mods:
            st.markdown(f"  - `🧩 {cm}`")
    else:
        st.info("目前此部門尚無任何啟用的模組。")

    st.markdown("---")
    st.markdown("##### 🛠️ 模組拼圖庫：直接勾選或取消以指派功能至此部門")

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

    new_selected_puzzle_mods = []
    cols_pz = st.columns(2)
    for idx, mod_item in enumerate(master_all_modules):
        with cols_pz[idx % 2]:
            puz_chk_key = f"puz_mod_{target_mod_dept}_{idx}_{mod_item}"
            if puz_chk_key not in st.session_state:
                st.session_state[puz_chk_key] = (mod_item in current_mods)
            
            is_checked = st.checkbox(mod_item, key=puz_chk_key)
            if is_checked:
                new_selected_puzzle_mods.append(mod_item)

    st.markdown("")
    if st.button("💾 立即儲存並更新此部門的功能拼圖配置", type="primary", use_container_width=True):
        dept_tree[target_mod_dept] = new_selected_puzzle_mods
        st.success(L['success_save'])
        st.rerun()

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
