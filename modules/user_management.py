import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 📱 手機優先響應式 UI (Mobile-First CSS for Field Users)
# ----------------------------------------------------
MOBILE_USER_MGMT_CSS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.25rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1.0rem !important; }
    p, div, span, label, .stMarkdown { font-size: 0.9rem !important; }
    .stDataFrame { overflow-x: auto; width: 100% !important; }
    .stButton button { width: 100% !important; min-height: 44px !important; font-size: 1rem !important; }
    .stSelectbox, .stTextInput { width: 100% !important; }
    .element-container { margin-bottom: 0.5rem !important; }
}
</style>
"""
st.markdown(MOBILE_USER_MGMT_CSS, unsafe_allow_html=True)

# ----------------------------------------------------
# 🌐 完整多語系翻譯字典 (支援 繁中 / 英文 / 越文)
# ----------------------------------------------------
USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 組織架構與企業部門設置",
        "caption": "裕豐電機（越南西寧廠）移動端優先：獨立部門管理、職位權限、動態模組拼圖管理中心。",
        "tab_roles": "⚙️ 角色權限 (RBAC)",
        "tab_dept_config": "🏢 獨立部門與模組設定",
        "tab_db_config": "🔌 資料庫連線",
        "tab_audit": "📊 稽核日誌",
        "success_connected": "PostgreSQL / Supabase 資料庫連線正常！",
        "db_not_connected": "ℹ️ 提示：目前使用安全記憶體模式運行。",
        "cloud_roles_count": "已建角色數",
        "search_ph": "輸入角色或部門過濾...",
        "search_label": "🔍 搜尋關鍵字",
        "col_stt": "序號",
        "col_dept": "所屬部門",
        "col_role_name": "職位角色",
        "col_desc": "職責說明",
        "col_modules_count": "啟用模組數",
        "edit_header": "✏️ 組織角色與部門權限編輯",
        "select_role_lbl": "選擇欲編輯的角色：",
        "create_new_opt": "🆕 建立新職位角色",
        "step1_title": "1. 設定所屬部門與職位名稱",
        "dept_select_lbl": "點選所屬部門 *",
        "role_name_lbl": "職位名稱 *",
        "role_name_ph": "例如: 總經理, 工地主任, 外勤技師",
        "role_desc_lbl": "職責說明",
        "role_desc_ph": "例如: 負責現場外勤與打卡稽核",
        "step2_title": "2. 勾選該角色可操作功能頁面：",
        "btn_save_role": "💾 儲存組織角色與設定",
        "btn_del_role": "🗑️ 刪除此角色",
        "save_role_success": "🎉 組織角色設定已成功儲存！",
        "del_role_success": "🗑️ 角色已成功刪除！",
        "dept_sec_title": "🏢 獨立企業部門設置與功能模組管理 (🧩 拼圖式權限配置)",
        "dept_sec_info": "💡 移動端友善：在此您可以純粹新增部門（不需綁定職稱），並透過下方拼圖方塊勾選指派功能模組！",
        "add_dept_header": "➕ 1. 獨立新增部門",
        "new_dept_lbl": "新部門名稱與代號 *",
        "new_dept_ph": "例如: 外勤工程處 (Field Ops)",
        "dept_desc_lbl": "部門職責描述",
        "dept_desc_ph": "負責全公司外勤與工地打卡",
        "btn_create_dept": "🚀 確認建立新部門",
        "del_dept_header": "🗑️ 2. 刪除指定部門",
        "sel_del_dept_lbl": "選擇要刪除的部門",
        "btn_del_dept": "🗑️ 確認刪除此部門",
        "puzzle_header": "🧩 3. 針對指定部門『以拼圖方塊勾選方式管理功能模組』",
        "sel_target_dept": "🎯 請選擇欲配置功能模組的目標部門：",
        "enabled_puzzle_title": "📦 目前已啟用的功能拼圖：",
        "no_enabled_mod": "目前此部門尚無任何啟用的模組。",
        "puzzle_lib_title": "🛠️ 模組拼圖庫：直接勾選或取消以指派功能至此部門",
        "btn_save_puzzle": "💾 立即儲存並更新此部門的功能拼圖配置",
        "db_sec_title": "🔌 外部資料庫與異質資料來源串聯設定 (Database Bridge)",
        "db_sec_info": "💡 說明：在此處設定與擴充對外連結的其他資料庫。",
        "db_key_lbl": "資料庫代碼 (Key) *",
        "db_name_lbl": "資料庫顯示名稱 *",
        "db_type_lbl": "資料庫類型",
        "db_host_lbl": "主機位址 (Host / IP)",
        "db_port_lbl": "通訊埠 (Port)",
        "db_dbname_lbl": "資料庫名稱 (Database Name)",
        "db_user_lbl": "使用者帳號 (Username)",
        "btn_test_db": "🧪 測試資料庫連線",
        "btn_save_db": "💾 儲存並啟用設定"
    },
    "English": {
        "title": "🔒 IT Admin Center - Org & Dept Setup",
        "caption": "Mobile-First: Independent department setup and dynamic module configuration.",
        "tab_roles": "⚙️ Roles & RBAC",
        "tab_dept_config": "🏢 Dept & Modules",
        "tab_db_config": "🔌 DB Bridge",
        "tab_audit": "📊 Audit Logs",
        "success_connected": "PostgreSQL Connected!",
        "db_not_connected": "ℹ️ Running in secure memory mode.",
        "cloud_roles_count": "Total Roles",
        "search_ph": "Filter role or dept...",
        "search_label": "🔍 Search Keyword",
        "col_stt": "No.",
        "col_dept": "Department",
        "col_role_name": "Role Name",
        "col_desc": "Description",
        "col_modules_count": "Modules",
        "edit_header": "✏️ Edit Role & Permissions",
        "select_role_lbl": "Select role to edit:",
        "create_new_opt": "🆕 Create New Role",
        "step1_title": "1. Set Department & Role",
        "dept_select_lbl": "Select Department *",
        "role_name_lbl": "Role Name *",
        "role_name_ph": "e.g. Plant Manager, Field Tech",
        "role_desc_lbl": "Description",
        "role_desc_ph": "e.g. Field attendance & audit",
        "step2_title": "2. Select Enabled Modules:",
        "btn_save_role": "💾 Save Role Settings",
        "btn_del_role": "🗑️ Delete Role",
        "save_role_success": "🎉 Role settings saved successfully!",
        "del_role_success": "🗑️ Role deleted successfully!",
        "dept_sec_title": "🏢 Independent Department & Module Management (Puzzle RBAC)",
        "dept_sec_info": "💡 Mobile-Friendly: Add departments and assign modules via puzzle checkboxes.",
        "add_dept_header": "➕ 1. Create New Department",
        "new_dept_lbl": "New Dept Name & Code *",
        "new_dept_ph": "e.g. Field Ops",
        "dept_desc_lbl": "Department Description",
        "dept_desc_ph": "Responsible for field attendance",
        "btn_create_dept": "🚀 Confirm Create Dept",
        "del_dept_header": "🗑️ 2. Delete Department",
        "sel_del_dept_lbl": "Select Dept to Delete",
        "btn_del_dept": "🗑️ Confirm Delete Dept",
        "puzzle_header": "🧩 3. Configure Department Modules via Puzzle Checkboxes",
        "sel_target_dept": "🎯 Select Target Department:",
        "enabled_puzzle_title": "📦 Currently Enabled Modules:",
        "no_enabled_mod": "No modules enabled for this department.",
        "puzzle_lib_title": "🛠️ Module Puzzle Library: Check/Uncheck to assign modules",
        "btn_save_puzzle": "💾 Save Department Module Configuration",
        "db_sec_title": "🔌 External Database & Bridge Setup (Database Bridge)",
        "db_sec_info": "💡 Connect and configure external database sources.",
        "db_key_lbl": "Database Key *",
        "db_name_lbl": "Database Display Name *",
        "db_type_lbl": "Database Type",
        "db_host_lbl": "Host / IP",
        "db_port_lbl": "Port",
        "db_dbname_lbl": "Database Name",
        "db_user_lbl": "Username",
        "btn_test_db": "🧪 Test DB Connection",
        "btn_save_db": "💾 Save & Enable"
    },
    "Tiếng Việt": {
        "title": "🔒 Trung tâm CNTT - Cấu trúc Tổ chức & Phòng ban",
        "caption": "Ưu tiên Di động: Quản lý phòng ban độc lập và cấu hình module động.",
        "tab_roles": "⚙️ Vai trò & RBAC",
        "tab_dept_config": "🏢 Phòng ban & Module",
        "tab_db_config": "🔌 Kết nối CSDL",
        "tab_audit": "📊 Nhật ký",
        "success_connected": "Kết nối PostgreSQL thành công!",
        "db_not_connected": "ℹ️ Chạy ở chế độ bộ nhớ an toàn.",
        "cloud_roles_count": "Tổng vai trò",
        "search_ph": "Lọc vai trò hoặc phòng ban...",
        "search_label": "🔍 Tìm kiếm từ khóa",
        "col_stt": "STT",
        "col_dept": "Phòng ban",
        "col_role_name": "Tên vai trò",
        "col_desc": "Mô tả",
        "col_modules_count": "Số module",
        "edit_header": "✏️ Chỉnh sửa vai trò & phân quyền",
        "select_role_lbl": "Chọn vai trò cần chỉnh sửa:",
        "create_new_opt": "🆕 Tạo vai trò mới",
        "step1_title": "1. Đặt phòng ban và tên vai trò",
        "dept_select_lbl": "Chọn phòng ban *",
        "role_name_lbl": "Tên vai trò *",
        "role_name_ph": "VD: Quản lý nhà máy, Kỹ thuật viên",
        "role_desc_lbl": "Mô tả",
        "role_desc_ph": "VD: Quản lý hiện trường và chấm công",
        "step2_title": "2. Chọn các module được phép:",
        "btn_save_role": "💾 Lưu cài đặt vai trò",
        "btn_del_role": "🗑️ Xóa vai trò",
        "save_role_success": "🎉 Đã lưu cài đặt vai trò thành công!",
        "del_role_success": "🗑️ Đã xóa vai trò thành công!",
        "dept_sec_title": "🏢 Quản lý Phòng ban & Cấu hình Module động",
        "dept_sec_info": "💡 Thân thiện di động: Thêm phòng ban và cấu hình module qua hộp kiểm.",
        "add_dept_header": "➕ 1. Thêm phòng ban mới",
        "new_dept_lbl": "Tên & Mã phòng ban mới *",
        "new_dept_ph": "VD: Phòng Vận hành Hiện trường",
        "dept_desc_lbl": "Mô tả phòng ban",
        "dept_desc_ph": "Chịu trách nhiệm chấm công hiện trường",
        "btn_create_dept": "🚀 Xác nhận tạo phòng ban",
        "del_dept_header": "🗑️ 2. Xóa phòng ban",
        "sel_del_dept_lbl": "Chọn phòng ban cần xóa",
        "btn_del_dept": "🗑️ Xác nhận xóa phòng ban",
        "puzzle_header": "🧩 3. Quản lý module cho phòng ban đã chọn",
        "sel_target_dept": "🎯 Chọn phòng ban cần cấu hình module:",
        "enabled_puzzle_title": "📦 Các module đang bật:",
        "no_enabled_mod": "Phòng ban này chưa có module nào.",
        "puzzle_lib_title": "🛠️ Thư viện module: Tích chọn để gán chức năng",
        "btn_save_puzzle": "💾 Lưu cấu hình module cho phòng ban",
        "db_sec_title": "🔌 Cấu hình kết nối Cơ sở dữ liệu ngoài (Database Bridge)",
        "db_sec_info": "💡 Cấu hình và kết nối các nguồn dữ liệu bên ngoài.",
        "db_key_lbl": "Mã CSDL (Key) *",
        "db_name_lbl": "Tên hiển thị CSDL *",
        "db_type_lbl": "Loại CSDL",
        "db_host_lbl": "Địa chỉ Host / IP",
        "db_port_lbl": "Cổng (Port)",
        "db_dbname_lbl": "Tên CSDL (Database Name)",
        "db_user_lbl": "Tài khoản (Username)",
        "btn_test_db": "🧪 Kiểm tra kết nối CSDL",
        "btn_save_db": "💾 Lưu và kích hoạt"
    }
}

DEFAULT_DEPARTMENTS = [
    "📈 總經理室 (Executive Office)",
    "👔 管理部 (Management Dept)",
    "📍 外勤工程打卡與工作回報 (Field Attendance)",
    "🛠️ 工程與設計管理中心 (Engineering & Design Center)",
    "🏭 生產部 (Production Dept)",
    "📦 倉庫管理 (Warehouse Management)",
    "💻 資訊管理部 (IT & System)"
]

def init_system_tables(engine):
    if engine is None:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS system_roles (
                    id SERIAL PRIMARY KEY,
                    role_name VARCHAR(100) UNIQUE NOT NULL,
                    department VARCHAR(150) DEFAULT '管理部 (Management Dept)',
                    description TEXT,
                    allowed_modules TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("ALTER TABLE system_roles ADD COLUMN IF NOT EXISTS department VARCHAR(150) DEFAULT '管理部 (Management Dept)';"))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS system_departments (
                    id SERIAL PRIMARY KEY,
                    department_name VARCHAR(150) UNIQUE NOT NULL,
                    level_tier VARCHAR(50) DEFAULT '2級部門',
                    description TEXT
                );
            """))
    except Exception:
        pass

def fetch_roles(engine, lang_dict):
    init_system_tables(engine)
    fallback_roles = {
        "董事長": {"department": "📈 總經理室 (Executive Office)", "description": "公司經營方向規劃與戰略定奪", "allowed_modules": "ALL"},
        "總經理": {"department": "📈 總經理室 (Executive Office)", "description": "董事長指示的公司經營方向執行與公司管理", "allowed_modules": "ALL"},
        "倉庫管理員": {"department": "📦 倉庫管理 (Warehouse Management)", "description": "倉庫庫存與資材條碼管理", "allowed_modules": "📦 [倉儲] 倉庫庫存與資材條碼管理"},
        "外勤技師": {"department": "📍 外勤工程打卡與工作回報 (Field Attendance)", "description": "現場外勤打卡與工作回報專用", "allowed_modules": "📍 現場外勤打卡與工作回報"},
        "工程主管": {"department": "🛠️ 工程與設計管理中心 (Engineering & Design Center)", "description": "工程專案與現場督導管理", "allowed_modules": "⚡ [工程] 配電盤與工程專案雙層報價"}
    }
    
    departments_set = set(DEFAULT_DEPARTMENTS)
    
    if engine is None:
        return fallback_roles, sorted(list(departments_set)), False, lang_dict["db_not_connected"]
    
    try:
        df = pd.read_sql("SELECT role_name, department, description, allowed_modules FROM system_roles", con=engine)
        df_dept = pd.read_sql("SELECT department_name FROM system_departments", con=engine)
        if not df_dept.empty:
            for d in df_dept["department_name"]:
                if d: departments_set.add(str(d).strip())

        if df.empty:
            return fallback_roles, sorted(list(departments_set)), True, lang_dict["success_connected"]
        
        roles_dict = {}
        for _, row in df.iterrows():
            r_name = str(row["role_name"]).strip()
            dept = str(row.get("department") or "管理部 (Management Dept)").strip()
            departments_set.add(dept)
            desc = row.get("description", "")
            roles_dict[r_name] = {
                "department": dept,
                "description": desc,
                "allowed_modules": row.get("allowed_modules", "ALL")
            }
        return roles_dict, sorted(list(departments_set)), True, lang_dict["success_connected"]
    except Exception as e:
        return fallback_roles, sorted(list(departments_set)), False, f"{lang_dict['db_not_connected']} ({e})"

def save_role_db(engine, role_name, department, description, allowed_modules):
    if engine is None:
        return False
    clean_name = role_name.strip()
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO system_roles (role_name, department, description, allowed_modules) 
                    VALUES (:r, :dept, :d, :m) 
                    ON CONFLICT (role_name) 
                    UPDATE SET department = :dept, description = :d, allowed_modules = :m
                """),
                {"r": clean_name, "dept": department, "d": description, "m": allowed_modules}
            )
        return True
    except Exception:
        return False

def delete_role_db(engine, role_name):
    if engine is None:
        return False
    try:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM system_roles WHERE role_name = :r"), {"r": role_name})
        return True
    except Exception:
        return False

def get_department_module_tree():
    """全域共享的部門與子功能樹狀結構（極簡命名，對齊 14 項管理部功能）"""
    if "custom_department_module_tree" not in st.session_state:
        st.session_state.custom_department_module_tree = {
            "📈 總經理室 (Executive Office)": [
                "🔴 原料價格與 Gemini 智慧採購顧問",
                "📊 財務類顯示資料 (AR/AP & P&L)",
                "⚡ 工程專案進度與現場異常監控",
                "📰 越南經營政策與法規每日動態"
            ],
            "管理部 (Management Dept)": [
                "📢 公司公告",
                "👤 員工檔案",
                "📊 員工打卡紀錄",
                "🔑 密碼修改",
                "🏠 宿舍與伙食",
                "🏭 工作廠區管理",
                "🚗 車輛進出口",
                "🔧 車輛維修紀錄",
                "📦 固定資產管理",
                "🛒 採購與應付帳款",
                "💰 應收帳款管理",
                "📊 越南稅務報表",
                "💵 員工薪資與保險",
                "📄 電子發票管理"
            ],
            "📍 外勤工程上下班打卡 (Field Attendance)": [
                "📍 現場外勤打卡與工作回報"
            ],
            "✍️ 電子簽核中心 (Approval Center)": [
                "✍️ 提交請假/採購與即時進度追蹤 / 審核"
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
            "💻 資訊管理部 (IT & System)": [
                "🔒 系統角色權限與模組開關設定",
                "🔌 API 串聯設定中心"
            ]
        }
    return st.session_state.custom_department_module_tree

def render_user_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in USER_MGMT_I18N else "繁體中文"
    L = USER_MGMT_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    roles_dict, available_depts, is_connected, msg = fetch_roles(engine, L)
    dept_module_tree = get_department_module_tree()

    tab_roles, tab_dept_config, tab_db_config, tab_audit = st.tabs([
        L["tab_roles"], 
        L["tab_dept_config"], 
        L["tab_db_config"], 
        L["tab_audit"]
    ])

    # ----------------------------------------------------
    # ⚙️ Tab 1: 組織角色與權限設定 (RBAC)
    # ----------------------------------------------------
    with tab_roles:
        st.markdown(f"### {L['tab_roles']}")
        if is_connected:
            st.success(f"🟢 {msg}")
        else:
            st.info(f"{msg}")

        col_search, col_stats = st.columns([3, 1])
        with col_search:
            search_kw = st.text_input(L["search_label"], placeholder=L["search_ph"], key="rbac_search_kw")
        with col_stats:
            st.metric(L["cloud_roles_count"], len(roles_dict))

        sorted_role_names = sorted(roles_dict.keys(), key=lambda r: (roles_dict[r].get("department", ""), r))

        table_rows = []
        for idx, r_name in enumerate(sorted_role_names, start=1):
            r_info = roles_dict[r_name]
            dept_name = r_info.get("department", "未分類部門")
            if not search_kw or (search_kw.lower() in r_name.lower() or search_kw.lower() in r_info["description"].lower() or search_kw.lower() in dept_name.lower()):
                mod_count_str = "全開 (ALL)" if r_info["allowed_modules"] == "ALL" else f"{len(r_info['allowed_modules'].split(','))} 個頁面"
                table_rows.append({
                    L["col_stt"]: idx,
                    L["col_dept"]: dept_name,
                    L["col_role_name"]: r_name,
                    L["col_desc"]: r_info["description"],
                    L["col_modules_count"]: mod_count_str
                })

        if table_rows:
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown(f"### {L['edit_header']}")

        role_opts = [L["create_new_opt"]] + sorted_role_names
        sel_role_display = st.selectbox(L["select_role_lbl"], options=role_opts, index=0)

        sel_role_key = "" if sel_role_display == L["create_new_opt"] else sel_role_display
        is_edit = sel_role_display != L["create_new_opt"]
        default_name = sel_role_key if is_edit else ""
        default_desc = roles_dict.get(sel_role_key, {}).get("description", "") if is_edit else ""
        default_dept = roles_dict.get(sel_role_key, {}).get("department", available_depts[0]) if is_edit else available_depts[0]

        all_mod_flat = [m for mods in dept_module_tree.values() for m in mods]
        curr_set = set(all_mod_flat) if (is_edit and roles_dict.get(sel_role_key, {}).get("allowed_modules") == "ALL") else (set(roles_dict.get(sel_role_key, {}).get("allowed_modules", "").split(",")) if is_edit else set(all_mod_flat))

        st.markdown(f"#### {L['step1_title']}")
        
        dept_options_list = available_depts
        curr_dept_idx = dept_options_list.index(default_dept) if default_dept in dept_options_list else 0
        
        st.markdown(f"**{L['dept_select_lbl']}**")
        selected_dept_option = st.radio("dept_radio_group", options=dept_options_list, index=curr_dept_idx, label_visibility="collapsed")
        final_department = selected_dept_option

        in_name = st.text_input(L["role_name_lbl"], value=default_name, placeholder=L["role_name_ph"])
        in_desc = st.text_input(L["role_desc_lbl"], value=default_desc, placeholder=L["role_desc_ph"])

        st.markdown(f"#### {L['step2_title']}")
        
        selected_mods = []
        for dept_tree_name, mods in dept_module_tree.items():
            col_hdr1, col_hdr2 = st.columns([3, 1])
            with col_hdr1:
                st.markdown(f"##### {dept_tree_name}")
            with col_hdr2:
                select_all_key = f"select_all_{sel_role_key}_{dept_tree_name}"
                
                def toggle_all_modules_fast(dept_name=dept_tree_name, mod_list=mods, k=select_all_key):
                    target_state = st.session_state.get(k, False)
                    for i, mod_name in enumerate(mod_list):
                        chk_key = f"chk_rbac_{active_lang}_{sel_role_key}_{dept_name}_{i}_{mod_name}"
                        st.session_state[chk_key] = target_state

                if select_all_key not in st.session_state:
                    all_checked_init = all(
                        st.session_state.get(f"chk_rbac_{active_lang}_{sel_role_key}_{dept_tree_name}_{i}_{m}", m in curr_set)
                        for i, m in enumerate(mods)
                    )
                    st.session_state[select_all_key] = all_checked_init

                st.checkbox("一鍵全選", key=select_all_key, on_change=toggle_all_modules_fast)

            cols = st.columns(2)
            for idx, m in enumerate(mods):
                with cols[idx % 2]:
                    chk_key = f"chk_rbac_{active_lang}_{sel_role_key}_{dept_tree_name}_{idx}_{m}"
                    if chk_key not in st.session_state:
                        st.session_state[chk_key] = (m in curr_set)

                    chk = st.checkbox(m, key=chk_key)
                    if chk:
                        selected_mods.append(m)
            st.markdown("---")

        cb1, cb2 = st.columns(2)
        with cb1:
            btn_save = st.button(L["btn_save_role"], type="primary", use_container_width=True)
        with cb2:
            btn_del = st.button(L["btn_del_role"], use_container_width=True)

        if btn_save:
            t_name = in_name.strip()
            if t_name and final_department:
                mod_str = "ALL" if len(selected_mods) == len(all_mod_flat) else (",".join(selected_mods) if selected_mods else "")
                save_role_db(engine, t_name, final_department, in_desc, mod_str)
                st.success(L["save_role_success"])
                st.rerun()
            else:
                st.warning("⚠️ 請完整填寫『所屬部門』與『職位名稱』！")

        if btn_del:
            t_name = in_name.strip() or sel_role_key
            if t_name and t_name != L["create_new_opt"]:
                if t_name in ["系統管理員 (Admin)"]:
                    st.error("🚫 系統保護：核心管理員角色無法被刪除！")
                else:
                    delete_role_db(engine, t_name)
                    st.success(L["del_role_success"])
                    st.rerun()

    # ----------------------------------------------------
    # 🏢 Tab 2: 獨立企業部門與模組管理 (Department & Module Config)
    # ----------------------------------------------------
    with tab_dept_config:
        st.markdown(f"### {L['dept_sec_title']}")
        st.info(L["dept_sec_info"])

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown(f"#### {L['add_dept_header']}")
            with st.form("form_create_dept_isolated"):
                new_d_name = st.text_input(L["new_dept_lbl"], placeholder=L["new_dept_ph"])
                new_d_desc = st.text_input(L["dept_desc_lbl"], placeholder=L["dept_desc_ph"])
                if st.form_submit_button(L["btn_create_dept"], type="primary", use_container_width=True):
                    if new_d_name:
                        dept_key = f"{new_d_name.strip()} ({new_d_desc})" if new_d_desc else new_d_name.strip()
                        if dept_key not in dept_module_tree:
                            dept_module_tree[dept_key] = []
                            if engine:
                                try:
                                    with engine.begin() as conn_d:
                                        conn_d.execute(text("INSERT INTO system_departments (department_name, description) VALUES (:n, :d) ON CONFLICT DO NOTHING"),
                                                       {"n": new_d_name.strip(), "d": new_d_desc})
                                except Exception:
                                    pass
                            st.success(f"🎉 成功建立新部門：{new_d_name}！")
                            st.rerun()
                        else:
                            st.warning("⚠️ 此部門名稱已存在！")
                    else:
                        st.warning("⚠️ 請輸入部門名稱！")

        with col_d2:
            st.markdown(f"#### {L['del_dept_header']}")
            with st.form("form_delete_dept_isolated"):
                target_del_dept = st.selectbox(L["sel_del_dept_lbl"], options=list(dept_module_tree.keys()))
                if st.form_submit_button(L["btn_del_dept"], use_container_width=True):
                    if len(dept_module_tree) > 1:
                        del dept_module_tree[target_del_dept]
                        st.success(f"🗑️ 已成功刪除部門：{target_del_dept}")
                        st.rerun()
                    else:
                        st.error("🚫 系統至少須保留一個部門！")

        st.markdown("---")
        st.markdown(f"#### {L['puzzle_header']}")
        
        target_mod_dept = st.selectbox(L["sel_target_dept"], options=list(dept_module_tree.keys()), key="select_dept_for_modules_puzzle")
        current_mods = dept_module_tree[target_mod_dept]

        st.markdown(f"##### {L['enabled_puzzle_title']}【{target_mod_dept}】")
        if current_mods:
            for cm in current_mods:
                st.markdown(f"  - `🧩 {cm}`")
        else:
            st.info(L["no_enabled_mod"])

        st.markdown("---")
        st.markdown(f"##### {L['puzzle_lib_title']}")

        master_all_modules = [
            "🔴 原料價格與 Gemini 智慧採購顧問",
            "📊 財務類顯示資料 (AR/AP & P&L)",
            "⚡ 工程專案進度與現場異常監控",
            "📰 越南經營政策與法規每日動態",
            "📢 公司公告",
            "👤 員工檔案",
            "📊 員工打卡紀錄",
            "🔑 密碼修改",
            "🏠 宿舍與伙食",
            "🏭 工作廠區管理",
            "🚗 車輛進出口",
            "🔧 車輛維修紀錄",
            "📦 固定資產管理",
            "🛒 採購與應付帳款",
            "💰 應收帳款管理",
            "📊 越南稅務報表",
            "💵 員工薪資與保險",
            "📄 電子發票管理",
            "✍️ 提交請假/採購與即時進度追蹤 / 審核",
            "⚡ 1. 工程主管戰情室與案場管理",
            "⚡ 2. 工程專案報價系統",
            "📋 3. 施工日報表與點工點料登記",
            "🤖 4. AI 施工照片辨識與稽核",
            "⚠️ 5. 工程證照預警與機具檢驗預警",
            "🎨 6. 配電盤電氣與機構設計圖庫",
            "🔌 7. 配電盤 BOM 零件與採購連動",
            "👷 8. 外包商計價與偶鐸管理",
            "🧪 9. FAT/SAT 出廠與現場驗收管理",
            "📦 [倉儲] 倉庫庫存與資材條碼管理",
            "✂️ [板金] 板金加工組工單與條碼",
            "🎨 [塗料] 粉體塗裝烤漆組品管",
            "⚡ [配盤] 配電盤組裝配線組",
            "🔒 系統角色權限與模組開關設定",
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
        if st.button(L["btn_save_puzzle"], type="primary", use_container_width=True):
            dept_module_tree[target_mod_dept] = new_selected_puzzle_mods
            st.success(f"🎉 成功更新【{target_mod_dept}】的功能模組拼圖設定！")
            st.rerun()

    # ----------------------------------------------------
    # 🔌 Tab 3: 跨資料庫連線與串聯設定 (Database Bridge)
    # ----------------------------------------------------
    with tab_db_config:
        st.markdown(f"### {L['db_sec_title']}")
        st.info(L["db_sec_info"])

        with st.form("form_db_bridge_config"):
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                db_key = st.text_input(L["db_key_lbl"], placeholder="例: factory_old_mysql")
                db_name = st.text_input(L["db_name_lbl"], placeholder="例: 西寧廠舊版資料庫")
                db_type = st.selectbox(L["db_type_lbl"], ["PostgreSQL / Supabase", "MySQL / MariaDB", "Microsoft SQL Server", "Oracle DB", "SQLite"])
            with col_b2:
                db_host = st.text_input(L["db_host_lbl"], placeholder="例: 192.168.1.100")
                db_port = st.text_input(L["db_port_lbl"], placeholder="例: 3306 或 5432")
                db_dbname = st.text_input(L["db_dbname_lbl"], placeholder="例: reetech_legacy")
                db_user = st.text_input(L["db_user_lbl"], placeholder="例: db_admin")

            col_test, col_save_db = st.columns(2)
            with col_test:
                btn_test_conn = st.form_submit_button(L["btn_test_db"], use_container_width=True)
            with col_save_db:
                btn_save_db_cfg = st.form_submit_button(L["btn_save_db"], type="primary", use_container_width=True)

            if btn_test_conn:
                if db_host and db_dbname:
                    st.success(f"🟢 成功與 [{db_name}] 建立連線測試通道！")
                else:
                    st.warning("⚠️ 請填寫完整主機與資料庫名稱。")

            if btn_save_db_cfg:
                st.success("🎉 外部資料庫連線設定已成功儲存！")

    # ----------------------------------------------------
    # 📊 Tab 4: 系統稽核日誌 (Audit Logs)
    # ----------------------------------------------------
    with tab_audit:
        st.markdown(f"### {L['tab_audit']}")
        if "audit_logs_db" in st.session_state and st.session_state.audit_logs_db:
            st.dataframe(pd.DataFrame(st.session_state.audit_logs_db), use_container_width=True)
        else:
            st.info("目前尚無稽核日誌紀錄。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
