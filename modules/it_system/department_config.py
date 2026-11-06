import streamlit as st

def get_department_module_tree():
    """全域共享的部門與子功能樹狀結構（支援動態掛載與卸載）"""
    if "custom_department_module_tree" not in st.session_state:
        st.session_state.custom_department_module_tree = {
            "📈 總經理室 (Executive Office)": [
                "🔴 原料價格與 Gemini 智慧採購顧問",
                "📊 財務類顯示資料 (AR/AP & P&L)",
                "⚡ 工程專案進度與現場異常監控",
                "📰 越南經營政策與法規每日動態"
            ],
            "👔 管理部 (Management Dept)": [
                "公司公告", "員工檔案", "員工打卡紀錄", "密碼修改", "員工薪資與保險",
                "宿舍與伙食", "工作廠區管理", "車輛進出口", "車輛維修紀錄",
                "固定資產管理", "文件管理", "採購與應付帳款", "應收帳款管理",
                "越南稅務報表", "電子發票管理"
            ],
            "🛠️ 工程與設計管理中心 (Engineering & Design Center)": [
                "⚡ 1. 工程主管戰情室與案場管理", "⚡ 2. 工程專案報價系統",
                "📋 3. 施工日報表與點工點料登記", "🤖 4. AI 施工照片辨識與稽核",
                "⚠️ 5. 工程證照預警與機具檢驗預警", "🎨 6. 配電盤電氣與機構設計圖庫",
                "🔌 7. 配電盤 BOM 零件與採購連動", "👷 8. 外包商計價與偶鐸管理",
                "🧪 9. FAT/SAT 出廠與現場驗收管理"
            ],
            "🏭 生產部 (Production Dept)": [
                "✂️ [板金] 板金加工組工單與條碼",
                "🎨 [塗料] 粉體塗裝烤漆組品管",
                "⚡ [配盤] 配電盤組裝配線組"
            ],
            "📦 倉庫管理 (Warehouse Management)": [
                "📦 [倉儲] 倉庫庫存與資材條碼管理"
            ],
            "📍 外勤工程打卡與工作回報 (Field Attendance)": [
                "📍 現場外勤打卡與工作回報"
            ],
            "✍️ 電子簽核中心 (Approval Center)": [
                "✍️ 提交請假/採購與即時進度追蹤 / 審核"
            ]
        }
    return st.session_state.custom_department_module_tree

def render(engine=None, lang="繁體中文", **kwargs):
    st.title("⚙️ 系統設定與動態模組掛載中心")
    st.caption("供 Admin 管理員進行組織部門的新增、刪除，以及各部門功能模組的動態掛載與卸載。")
    st.markdown("---")

    tree = get_department_module_tree()

    # 1. 新增一級部門表單
    with st.form("add_department_form_unique"):
        st.markdown("#### ➕ 新增一級部門 (Add Department)")
        new_dept_name = st.text_input("新部門名稱 (建議包含圖示)", placeholder="例如: 🛡️ 品質安環部 (QA & HSE)")
        submitted_dept = st.form_submit_button("📁 建立新部門", type="primary")
        if submitted_dept:
            if new_dept_name.strip():
                if new_dept_name.strip() in tree:
                    st.warning("⚠️ 此部門名稱已存在！")
                else:
                    tree[new_dept_name.strip()] = []
                    st.success(f"🎉 成功新增部門：{new_dept_name.strip()}！")
                    st.rerun()
            else:
                st.warning("⚠️ 請輸入部門名稱！")

    st.markdown("---")
    st.markdown("#### 📂 現有部門與模組掛載/卸載管理 (Mount / Unmount Modules)")

    # 2. 針對每一個部門進行模組的掛載與卸載
    for d_name, mods in list(tree.items()):
        with st.expander(f"📁 {d_name} (目前掛載 {len(mods)} 項模組)", expanded=False):
            
            # 刪除整個部門的按鈕
            col_del_d1, col_del_d2 = st.columns([4, 1])
            with col_del_d1:
                st.markdown(f"**部門名稱：** `{d_name}`")
            with col_del_d2:
                if st.button("🗑️ 刪除此部門", key=f"del_dept_{d_name}"):
                    del tree[d_name]
                    st.success(f"已刪除部門：{d_name}")
                    st.rerun()

            st.markdown("##### 現有掛載模組清單：")
            if mods:
                for idx, m_item in enumerate(mods):
                    col_m1, col_m2 = st.columns([4, 1])
                    with col_m1:
                        st.markdown(f"- {m_item}")
                    with col_m2:
                        if st.button("🗑️ 卸載", key=f"unmount_{d_name}_{idx}"):
                            mods.remove(m_item)
                            st.success(f"已從 {d_name} 卸載模組：{m_item}")
                            st.rerun()
            else:
                st.info("💡 此部門目前尚無掛載任何模組。")

            st.markdown("---")
            # 為此部門掛載新模組的表單
            with st.form(f"mount_form_{d_name}"):
                st.markdown(f"**➕ 為 【{d_name}】 掛載新模組**")
                new_mod_name = st.text_input("輸入要掛載的子功能名稱", placeholder="例如: 📋 專案風險評估表", key=f"input_mod_{d_name}")
                submitted_mount = st.form_submit_button("🔗 確認掛載模組")
                if submitted_mount:
                    if new_mod_name.strip():
                        if new_mod_name.strip() in mods:
                            st.warning("⚠️ 此模組已在該部門掛載過了！")
                        else:
                            mods.append(new_mod_name.strip())
                            st.success(f"🎉 成功為 {d_name} 掛載模組：{new_mod_name.strip()}")
                            st.rerun()
                    else:
                        st.warning("⚠️ 請輸入模組名稱！")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
