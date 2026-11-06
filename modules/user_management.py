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
    st.title("🔒 系統設定與真實員工帳號綁定中心")
    st.caption("直接從資料庫（Database）抓取真實員工與薪資資料，實現 100% 動態資料驅動與內控綁定。")
    st.markdown("---")

    # 確保資料庫中存在 employees 表格
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS employees (
                        emp_code VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        department VARCHAR(150),
                        role VARCHAR(50) DEFAULT 'Staff',
                        password VARCHAR(100) DEFAULT '123456',
                        must_change_password BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception:
            pass

    # 建立分頁
    tab_emp, tab_dept, tab_rbac = st.tabs([
        "👥 真實員工與帳號權限綁定 (Database Employees)",
        "🏢 企業部門動態設置 (Departments)",
        "⚙️ 組織角色與權限指派 (RBAC)"
    ])

    # 1. 真實員工與帳號綁定管理
    with tab_emp:
        st.subheader("👥 資料庫真實員工名單與部門指派")
        st.info("以下資料直接讀取自您的資料庫 (`employees` 表格)，確保人名與薪資人事模組完全同步。")

        employee_list = []
        if engine is not None:
            try:
                with engine.connect() as conn:
                    query = text("SELECT emp_code, name, department, role, password, must_change_password FROM employees")
                    df_db_emp = pd.read_sql(query, con=conn)
                    for _, row in df_db_emp.iterrows():
                        employee_list.append({
                            "工號": row["emp_code"],
                            "姓名": row["name"],
                            "部門": row["department"],
                            "角色": row["role"],
                            "密碼": row["password"],
                            "須改密碼": row["must_change_password"]
                        })
            except Exception as e:
                st.warning(f"⚠️ 讀取資料庫員工資料發生異常：{str(e)}")

        # 如果資料庫尚無員工，提供快速初始化或提示
        if not employee_list:
            st.warning("⚠️ 目前資料庫中尚未建立員工資料。請透過下方表單新增第一筆真實員工，系統將直接寫入資料庫！")
        else:
            df_emp = pd.DataFrame(employee_list)
            st.dataframe(df_emp, use_container_width=True)

        st.markdown("---")
        with st.form("add_real_employee_form"):
            st.markdown("#### ➕ 新增真實員工至資料庫與權限系統")
            col1, col2 = st.columns(2)
            with col1:
                new_id = st.text_input("員工工號 (Emp ID) *", placeholder="例如: RECH001")
                new_name = st.text_input("員工真實姓名 (Full Name) *", placeholder="例如: 依您薪資資料庫之真實姓名")
            with col2:
                dept_list = list(get_department_module_tree().keys())
                new_dept = st.selectbox("所屬部門 (Department)", dept_list)
                new_role = st.selectbox("系統角色 (Role)", ["Admin", "Manager", "Staff", "Security"])

            submitted_emp = st.form_submit_button("💾 寫入資料庫並建立帳號", type="primary")
            if submitted_emp:
                if new_id and new_name:
                    if engine is not None:
                        try:
                            with engine.begin() as conn:
                                insert_sql = text("""
                                    INSERT INTO employees (emp_code, name, department, role, password, must_change_password)
                                    VALUES (:code, :name, :dept, :role, :pwd, :mpwd)
                                    ON CONFLICT (emp_code) 
                                    DO UPDATE SET name = :name, department = :dept, role = :role;
                                """)
                                conn.execute(insert_sql, {
                                    "code": new_id.strip(),
                                    "name": new_name.strip(),
                                    "dept": new_dept,
                                    "role": new_role,
                                    "pwd": "123456",
                                    "mpwd": True
                                })
                            st.success(f"🎉 真實員工 {new_name.strip()} ({new_id.strip()}) 已成功寫入資料庫！")
                            st.rerun()
                        except Exception as db_err:
                            st.error(f"⚠️ 寫入資料庫失敗：{str(db_err)}")
                    else:
                        st.error("⚠️ 資料庫引擎未連線，無法寫入！")
                else:
                    st.warning("⚠️ 請完整填寫工號與真實姓名！")

    # 2. 企業部門動態設置
    with tab_dept:
        st.subheader("🏢 企業部門與自動模組拼圖")
        st.info("系統會根據在此處定義的部門，自動掛載對應的業務模組。")
        
        tree = get_department_module_tree()
        for d_name, mods in tree.items():
            with st.expander(f"📁 {d_name} (包含 {len(mods)} 項功能模組)"):
                for m in mods:
                    st.markdown(f"- {m}")

    # 3. 組織角色與權限指派 (RBAC)
    with tab_rbac:
        st.subheader("⚙️ 角色權限對照與模組開關")
        try:
            from modules.it_system import role_rbac
            role_rbac.render(engine=engine, lang=lang, **kwargs)
        except Exception:
            st.info("💡 組織角色權限模組準備中。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
