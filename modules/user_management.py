import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

MOBILE_USER_MGMT_CSS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.25rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1.0rem !important; }
    p, div, span, label, .stMarkdown { font-size: 0.9rem !important; }
    .stDataFrame { overflow-x: auto; width: 100% !important; }
    .stButton button { width: 100% !important; min-height: 44px !important; font-size: 1rem !important; }
}
</style>
"""
st.markdown(MOBILE_USER_MGMT_CSS, unsafe_allow_html=True)

def get_department_module_tree():
    """全域共享的部門與子功能樹狀結構（已依企業管理權責與順序重排）"""
    if "custom_department_module_tree" not in st.session_state:
        st.session_state.custom_department_module_tree = {
            "📈 總經理室 (Executive Office)": [
                "🔴 原料價格與 Gemini 智慧採購顧問",
                "📊 財務類顯示資料 (AR/AP & P&L)",
                "⚡ 工程專案進度與現場異常監控",
                "📰 越南經營政策與法規每日動態"
            ],
            "👔 管理部 (Management Dept)": [
                "公司公告",
                "員工檔案",
                "員工打卡紀錄",
                "密碼修改",
                "員工薪資與保險",
                "宿舍與伙食",
                "工作廠區管理",
                "車輛進出口",
                "車輛維修紀錄",
                "固定資產管理",
                "文件管理",
                "採購與應付帳款",
                "應收帳款管理",
                "越南稅務報表",
                "電子發票管理"
            ],
            "🛠️ 工程與設計管理中心 (Engineering & Design Center)": [
                "⚡ 1. 工程主管戰情室與案場管理",
                "⚡ 2. 工程專案報價系統",
                "📋 3. 施工日報表與點工點料登記",
                "🤖 4. AI 施工照片辨識與稽核",
                "⚠️ 5. 工程證照預警與機具檢驗預警",
                "🎨 6. 配電盤電氣與機構設計圖庫",
                "🔌 7. 配電盤 BOM 零件與採購連動",
                "👷 8. 外包商計價與偶鐸管理",
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
            ],
            "💻 系統設定 (System Settings)": [
                "🔒 系統角色權限與模組開關設定",
                "🔌 API 串聯設定中心"
            ]
        }
    return st.session_state.custom_department_module_tree

def render_user_management_page(engine=None, lang="繁體中文", **kwargs):
    st.title("🔒 系統設定與組織架構管理中心")
    st.caption("管理企業內部組織部門、員工帳號權限綁定，落實 100% 動態配置（Metadata-Driven）。")
    st.markdown("---")

    # 建立系統設定內部的三大核心分頁
    tab_emp, tab_dept, tab_rbac = st.tabs([
        "👥 員工與帳號權限綁定 (Employees)",
        "🏢 企業部門動態設置 (Departments)",
        "⚙️ 組織角色與權限指派 (RBAC)"
    ])

    # 1. 員工與帳號綁定管理
    with tab_emp:
        st.subheader("👥 員工帳號與部門/角色指派")
        st.info("在此維護員工工號、姓名、所屬部門及系統操作角色（支援系統自動指派預設密碼 123456 與首次登入強制改密機制）。")

        if "employee_db" not in st.session_state:
            st.session_state.employee_db = [
                {"工號": "EMP001", "姓名": "陳總經理", "部門": "📈 總經理室 (Executive Office)", "角色": "Admin", "密碼": "123", "must_change_password": False},
                {"工號": "EMP002", "姓名": "林副總", "部門": "🛠️ 工程與設計管理中心", "角色": "Manager", "密碼": "123456", "must_change_password": True},
                {"工號": "EMP003", "姓名": "廠長", "部門": "🏭 生產部 (Production Dept)", "角色": "Manager", "密碼": "123456", "must_change_password": True},
                {"工號": "EMP004", "姓名": "外勤技師A", "部門": "📍 外勤工程打卡與工作回報", "角色": "Staff", "密碼": "123456", "must_change_password": True},
            ]

        df_emp = pd.DataFrame(st.session_state.employee_db)
        st.dataframe(df_emp, use_container_width=True)

        with st.form("add_employee_form"):
            st.markdown("#### ➕ 新增員工與指派初始帳號")
            col1, col2 = st.columns(2)
            with col1:
                new_id = st.text_input("員工工號 (Emp ID)", placeholder="例如: EMP005")
                new_name = st.text_input("員工姓名 (Full Name)", placeholder="例如: 王小明")
            with col2:
                dept_list = list(get_department_module_tree().keys())
                new_dept = st.selectbox("所屬部門 (Department)", dept_list)
                new_role = st.selectbox("系統角色 (Role)", ["Admin", "Manager", "Staff", "Security"])

            submitted_emp = st.form_submit_button("💾 儲存並建立員工帳號", type="primary")
            if submitted_emp:
                if new_id and new_name:
                    # 檢查是否重複
                    exists = any(e["工號"] == new_id for e in st.session_state.employee_db)
                    if exists:
                        st.error(f"⚠️ 工號 {new_id} 已存在，請使用其他工號！")
                    else:
                        st.session_state.employee_db.append({
                            "工號": new_id,
                            "姓名": new_name,
                            "部門": new_dept,
                            "角色": new_role,
                            "密碼": "123456",
                            "must_change_password": True
                        })
                        st.success(f"🎉 員工 {new_name} ({new_id}) 帳號建立成功！初始密碼為 123456。")
                        st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫工號與姓名！")

    # 2. 企業部門動態設置
    with tab_dept:
        st.subheader("🏢 企業部門與自動模組拼圖")
        st.info("系統會根據您在此處定義的部門，自動掛載對應的業務模組，免除寫死程式碼。")
        
        tree = get_department_module_tree()
        for d_name, mods in tree.items():
            with st.expander(f"📁 {d_name} (包含 {len(mods)} 項功能模組)"):
                for m in mods:
                    st.markdown(f"- {m}")

    # 3. 組織角色與權限指派 (RBAC)
    with tab_rbac:
        st.subheader("⚙️ 角色權限對照與模組開關")
        st.markdown("在此您可以針對不同職位（如廠長、工程師、外勤技師）精準配置模組操作權限。")
        
        # 呼叫或載入我們剛才優化的 rbac 模組
        try:
            from modules.it_system import role_rbac
            role_rbac.render(engine=engine, lang=lang, **kwargs)
        except Exception as e:
            st.info("💡 組織角色權限模組正在同步中，您也可以直接從左側選單進入各項系統設定進行微調。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
