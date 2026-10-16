import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 📱 手機優先響應式 CSS 紋理 (Mobile-First UI)
# ----------------------------------------------------
MOBILE_USER_MGMT_CSS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.3rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1.0rem !important; }
    p, div, span, label { font-size: 0.85rem !important; }
    .stDataFrame { overflow-x: auto; }
    .stButton button { width: 100% !important; }
}
</style>
"""
st.markdown(MOBILE_USER_MGMT_CSS, unsafe_allow_html=True)

# ----------------------------------------------------
# 🌐 多語系字典與角色中英越對照表 (i18n & RBAC Localization)
# ----------------------------------------------------
USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 組織角色權限與員工帳號總控台",
        "caption": "裕豐電機雲端高可用架構：RBAC 角色權限管理與系統員工帳號 CRUD。",
        "tab_roles": "⚙️ 組織角色與模組權限設定 (RBAC)",
        "tab_users": "👥 系統員工帳號管理 (CRUD)",
        "tab_audit": "📊 系統稽核日誌 (Audit Logs)",
        "tab_db": "🔌 資料庫連線狀態",
        "success_connected": "PostgreSQL / Supabase 資料庫連線正常！",
        "cloud_roles_count": "已建角色數",
        "search_ph": "輸入角色名稱過濾...",
        "search_label": "🔍 搜尋角色關鍵字",
        "col_role_name": "角色名稱",
        "col_desc": "職責與權限範圍",
        "col_modules_count": "允許開啟之頁面數量",
        "edit_header": "✏️ 角色權限編輯維護 (新增 / 載入修改 / 刪除)",
        "select_role_lbl": "請選擇欲編輯的角色：",
        "create_new_opt": "🆕 建立新角色 (Create New)",
        "step1_title": "1. 輸入角色名稱與說明",
        "role_name_lbl": "職位角色名稱 *",
        "role_name_ph": "例如: 協理、現場工地主任",
        "role_desc_lbl": "部門職責與資料範圍說明",
        "role_desc_ph": "例如: 協助總經理工程支援指派，以及生產車間管理",
        "step2_title": "2. 勾選該職位角色可操作功能頁面：",
        "btn_save_role": "💾 儲存角色權限設定",
        "btn_del_role": "🗑️ 刪除此角色",
        "save_role_success": "🎉 角色 [{name}] 權限設定已成功儲存！",
        "del_role_success": "🗑️ 角色 [{name}] 已成功刪除！",
        "users_header": "📋 系統現有使用者與員工清冊",
        "add_user_header": "➕ 新增系統使用者與權限指派",
        "lbl_username": "登入帳號 (工號) *",
        "lbl_name": "使用者姓名 *",
        "lbl_role": "指派角色 (RBAC) *",
        "lbl_site": "所屬廠區 *",
        "site_opts": ["台灣總部 (Taiwan HQ)", "越南西寧廠 (Tay Ninh)", "越南海防廠 (Hai Phong)"],
        "btn_add_user": "💾 建立使用者帳號",
        "success_add_user": "✅ 系統帳號 `{username}` 已成功建立！",
        "fill_warning": "⚠️ 請完整填寫帳號與姓名！",
        "default_roles": {
            "admin": {"description": "最高決策與全系統總覽權限 (Admin)", "allowed_modules": "ALL"},
            "manager": {"description": "廠區主管，負責考勤審核與日常營運 (Manager)", "allowed_modules": "ALL"},
            "security": {"description": "大門保全組，負責車輛進出登記 (Security)", "allowed_modules": "車輛門禁"},
            "staff": {"description": "一般員工，個人打卡與請假申請 (Staff)", "allowed_modules": "個人打卡"}
        }
    },
    "Tiếng Việt": {
        "title": "🔒 Quản trị IT - Phân quyền Vai trò & Quản lý Tài khoản",
        "caption": "Kiến trúc đám mây Reetech: Quản lý phân quyền RBAC & Tài khoản nhân sự.",
        "tab_roles": "⚙️ Phân quyền Vai trò & Module (RBAC)",
        "tab_users": "👥 Quản lý Tài khoản Nhân sự",
        "tab_audit": "📊 Nhật ký Kiểm toán",
        "tab_db": "🔌 Trạng thái CSDL",
        "success_connected": "Kết nối CSDL thành công!",
        "cloud_roles_count": "Số lượng vai trò",
        "search_ph": "Nhập tên vai trò...",
        "search_label": "🔍 Tìm kiếm",
        "col_role_name": "Tên vai trò",
        "col_desc": "Mô tả",
        "col_modules_count": "Số trang cho phép",
        "edit_header": "✏️ Chỉnh sửa Phân quyền",
        "select_role_lbl": "Chọn vai trò:",
        "create_new_opt": "🆕 Tạo mới",
        "step1_title": "1. Nhập tên và mô tả",
        "role_name_lbl": "Tên vai trò *",
        "role_name_ph": "Ví dụ: Kỹ sư trưởng",
        "role_desc_lbl": "Mô tả",
        "role_desc_ph": "Mô tả chức năng",
        "step2_title": "2. Chọn chức năng được phép:",
        "btn_save_role": "💾 Lưu phân quyền",
        "btn_del_role": "🗑️ Xóa vai trò",
        "save_role_success": "🎉 Đã lưu vai trò [{name}] thành công!",
        "del_role_success": "🗑️ Đã xóa vai trò [{name}] thành công!",
        "users_header": "📋 Danh sách tài khoản",
        "add_user_header": "➕ Thêm tài khoản nhân sự mới",
        "lbl_username": "Tài khoản (Mã NV) *",
        "lbl_name": "Họ tên *",
        "lbl_role": "Vai trò (RBAC) *",
        "lbl_site": "Nhà máy trực thuộc *",
        "site_opts": ["Trụ sở Đài Loan (HQ)", "Nhà máy Tây Ninh", "Nhà máy Hải Phòng"],
        "btn_add_user": "💾 Tạo tài khoản",
        "success_add_user": "✅ Đã tạo tài khoản `{username}`!",
        "fill_warning": "⚠️ Vui lòng điền đầy đủ thông tin!",
        "default_roles": {
            "admin": {"description": "Quản trị viên hệ thống tối cao (Admin)", "allowed_modules": "ALL"},
            "manager": {"description": "Quản đốc nhà máy, duyệt chấm công và vận hành (Manager)", "allowed_modules": "ALL"},
            "security": {"description": "Bảo vệ cổng, đăng ký xe ra vào (Security)", "allowed_modules": "車輛門禁"},
            "staff": {"description": "Nhân viên, chấm công và xin nghỉ phép (Staff)", "allowed_modules": "個人打卡"}
        }
    },
    "English": {
        "title": "🔒 IT Center - RBAC Roles & User Accounts Management",
        "caption": "Reetech Cloud Architecture: RBAC Role Permissions & User CRUD.",
        "tab_roles": "⚙️ RBAC Roles & Permissions",
        "tab_users": "👥 User Accounts (CRUD)",
        "tab_audit": "📊 System Audit Logs",
        "tab_db": "🔌 Database Status",
        "success_connected": "PostgreSQL Database Connected Successfully!",
        "cloud_roles_count": "Total Roles",
        "search_ph": "Filter roles...",
        "search_label": "🔍 Search Roles",
        "col_role_name": "Role Name",
        "col_desc": "Description",
        "col_modules_count": "Allowed Modules",
        "edit_header": "✏️ Edit Role Permissions",
        "select_role_lbl": "Select Role:",
        "create_new_opt": "🆕 Create New Role",
        "step1_title": "1. Enter Role Name & Description",
        "role_name_lbl": "Role Name *",
        "role_name_ph": "e.g., Supervisor",
        "role_desc_lbl": "Description",
        "role_desc_ph": "e.g., Oversee operations",
        "step2_title": "2. Select Allowed Features:",
        "btn_save_role": "💾 Save Role Permissions",
        "btn_del_role": "🗑️ Delete Role",
        "save_role_success": "🎉 Role [{name}] saved successfully!",
        "del_role_success": "🗑️ Role [{name}] deleted successfully!",
        "users_header": "📋 Active User Accounts",
        "add_user_header": "➕ Register New User Account",
        "lbl_username": "Username (Emp ID) *",
        "lbl_name": "Full Name *",
        "lbl_role": "Permission Role (RBAC) *",
        "lbl_site": "Plant Location *",
        "site_opts": ["Taiwan HQ", "Tay Ninh Plant", "Hai Phong Plant"],
        "btn_add_user": "💾 Create User Account",
        "success_add_user": "✅ User account `{username}` created successfully!",
        "fill_warning": "⚠️ Please fill in username and full name!",
        "default_roles": {
            "admin": {"description": "Highest system administration & decision making (Admin)", "allowed_modules": "ALL"},
            "manager": {"description": "Plant manager, attendance approval & daily ops (Manager)", "allowed_modules": "ALL"},
            "security": {"description": "Gate security guard, vehicle access logging (Security)", "allowed_modules": "車輛門禁"},
            "staff": {"description": "General employee, attendance & leave requests (Staff)", "allowed_modules": "個人打卡"}
        }
    }
}

# ----------------------------------------------------
# 🔌 使用 SQLAlchemy 進行資料庫存取 (無 DNS 錯誤)
# ----------------------------------------------------
def fetch_roles(engine, lang_dict):
    fallback_roles = lang_dict["default_roles"]
    if engine is None:
        return fallback_roles, False, "資料庫 Engine 未建立（目前為安全記憶體模式）"
    
    try:
        df = pd.read_sql("SELECT role_name, description, allowed_modules FROM system_roles", con=engine)
        if df.empty:
            return fallback_roles, True, "資料庫連線正常，目前載入多語系預設角色。"
        roles_dict = {}
        for _, row in df.iterrows():
            r_name = row["role_name"]
            # 若資料庫中的角色符合預設角色，優先採用多語系翻譯的說明
            desc = row.get("description", "")
            if r_name in fallback_roles and not desc:
                desc = fallback_roles[r_name]["description"]
            roles_dict[r_name] = {
                "description": desc,
                "allowed_modules": row.get("allowed_modules", "ALL")
            }
        return roles_dict, True, "PostgreSQL 資料庫連線正常！"
    except Exception as e:
        return fallback_roles, False, f"資料庫表格尚未建立（已自動載入多語系預設角色）: {e}"

def save_role_db(engine, role_name, description, allowed_modules):
    if engine is None:
        return False
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO system_roles (role_name, description, allowed_modules) 
                    VALUES (:r, :d, :m) 
                    ON CONFLICT (role_name) 
                    DO UPDATE SET description = :d, allowed_modules = :m
                """),
                {"r": role_name, "d": description, "m": allowed_modules}
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

# ----------------------------------------------------
# 🌳 水電工程部門模組清單樹狀結構
# ----------------------------------------------------
DEPARTMENT_MODULE_TREE = {
    "📈 總經理室 (Executive Office)": [
        "🔴 原料價格與 Gemini 智慧採購顧問",
        "📊 財務類顯示資料 (AR/AP & P&L)",
        "⚡ 工程專案進度與現場異常監控"
    ],
    "👔 管理部 (Management Dept)": [
        "📢 公司重要公告與佈告欄",
        "👤 員工個人檔案與人事管理",
        "🏢 廠內員工固定打卡與出勤紀錄",
        "📍 外勤位置驗證與工地即時人數",
        "🏭 廠區與工作廠區管理",
        "🚗 廠區車輛進出口門禁與派車審核",
        "🛠️ 車輛維修保養紀錄",
        "🏢 固定資產與設備管理",
        "🛒 採購與應付帳款 (AP)",
        "📋 應收帳款",
        "📊 越南稅務標準財務報表 (Thông tư 200)",
        "💰 員工薪資計算與保險扣除",
        "📄 電子發票綜合管理"
    ],
    "✍️ 全公司電子簽核中心 (Approval Center)": [
        "✍️ 提交請假/採購與即時進度追蹤 / 審核"
    ],
    "🛠️ 工程與設計管理中心 (Engineering & Design Center)": [
        "⚡ [工程] 配電盤與工程專案雙層報價",
        "📊 [工程] 工程驗收與進度追蹤",
        "📋 [工程] 現場工程日報表與出工統計",
        "🤖 [工程] AI 施工照片智慧辨識與歸檔",
        "⚠️ [工程] 分包商與專業證照到期預警",
        "🎨 [設計] 配電盤電氣與機構設計圖庫 Storage",
        "🔌 [工程] 配電盤 BOM 零件自動展開與採購連動",
        "👷 [工程] 外包商點工計價與越南勞動法計薪",
        "🧪 [工程] FAT/SAT 試驗報告與 QR Code 驗收",
        "📊 [工程] 越南營建電子發票與稅務合規管家"
    ],
    "🏭 生產部 (Production Dept)": [
        "📦 [倉儲] 倉庫庫存與資材條碼管理",
        "✂️ [板金] 板金加工組工單與條碼",
        "🎨 [塗料] 粉體塗裝烤漆組品管",
        "⚡ [配盤] 配電盤組裝配線組"
    ],
    "💻 資訊管理部 (IT & System)": [
        "🔒 帳號權限與全系統稽核軌跡",
        "🎛️ 客戶 ERP 模組授權與功能開關"
    ]
}

ALL_MODULE_LIST = [mod for dept in DEPARTMENT_MODULE_TREE.values() for mod in dept]

# ----------------------------------------------------
# 🖥️ 主渲染函式
# ----------------------------------------------------
def render_user_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in USER_MGMT_I18N else "繁體中文"
    L = USER_MGMT_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化本地備援資料庫
    if "system_users_db" not in st.session_state or not isinstance(st.session_state.system_users_db, list):
        st.session_state.system_users_db = [
            {"username": "admin", "name": "系統管理員", "role": "admin", "site": "台灣總部"},
            {"username": "manager", "name": "陳經理", "role": "manager", "site": "越南西寧廠"},
            {"username": "security", "name": "大門保全組", "role": "security", "site": "越南西寧廠"}
        ]

    if "audit_logs_db" not in st.session_state:
        st.session_state.audit_logs_db = [
            {"time": "2026-10-06 13:00:15", "user": "admin", "action": "登入系統 (Login)", "module": "Auth", "ip": "192.168.1.50", "status": "成功"}
        ]

    roles_dict, is_connected, msg = fetch_roles(engine, L)

    tab_roles, tab_users, tab_audit, tab_db = st.tabs([
        L["tab_roles"], L["tab_users"], L["tab_audit"], L["tab_db"]
    ])

    # ----------------------------------------------------
    # Tab 1: 組織角色與模組權限設定 (RBAC)
    # ----------------------------------------------------
    with tab_roles:
        st.markdown(f"### {L['tab_roles']}")
        if is_connected:
            st.success(f"🟢 {L['success_connected']} ({msg})")
        else:
            st.info(f"ℹ️ {msg}")

        col_search, col_stats = st.columns([3, 1])
        with col_search:
            search_kw = st.text_input(L["search_label"], placeholder=L["search_ph"])
        with col_stats:
            st.metric(L["cloud_roles_count"], len(roles_dict))

        table_rows = []
        for r_name, r_info in roles_dict.items():
            if not search_kw or (search_kw.lower() in r_name.lower() or search_kw.lower() in r_info["description"].lower()):
                mod_count_str = "全開 (ALL)" if r_info["allowed_modules"] == "ALL" else f"{len(r_info['allowed_modules'].split(','))} 個頁面"
                table_rows.append({
                    L["col_role_name"]: r_name,
                    L["col_desc"]: r_info["description"],
                    L["col_modules_count"]: mod_count_str
                })

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown(f"### {L['edit_header']}")

        role_opts = [L["create_new_opt"]] + list(roles_dict.keys())
        sel_role = st.selectbox(L["select_role_lbl"], options=role_opts, index=0)

        is_edit = sel_role != L["create_new_opt"]
        default_name = sel_role if is_edit else ""
        default_desc = roles_dict.get(sel_role, {}).get("description", "") if is_edit else ""

        curr_set = set(ALL_MODULE_LIST) if (is_edit and roles_dict.get(sel_role, {}).get("allowed_modules") == "ALL") else (set(roles_dict.get(sel_role, {}).get("allowed_modules", "").split(",")) if is_edit else set(ALL_MODULE_LIST))

        st.markdown(f"#### {L['step1_title']}")
        in_name = st.text_input(L["role_name_lbl"], value=default_name, placeholder=L["role_name_ph"])
        in_desc = st.text_input(L["role_desc_lbl"], value=default_desc, placeholder=L["role_desc_ph"])

        st.markdown(f"#### {L['step2_title']}")
        selected_mods = []
        for dept, mods in DEPARTMENT_MODULE_TREE.items():
            st.markdown(f"##### {dept}")
            cols = st.columns(3)
            for idx, m in enumerate(mods):
                with cols[idx % 3]:
                    chk = st.checkbox(m, value=(m in curr_set), key=f"chk_rbac_{active_lang}_{sel_role}_{dept}_{idx}_{m}")
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
            if t_name:
                mod_str = "ALL" if len(selected_mods) == len(ALL_MODULE_LIST) else (",".join(selected_mods) if selected_mods else "")
                save_role_db(engine, t_name, in_desc, mod_str)
                st.success(L["save_role_success"].format(name=t_name))
                st.rerun()
            else:
                st.warning("⚠️ 請輸入角色名稱！")

        if btn_del:
            t_name = in_name.strip() or (sel_role if is_edit else "")
            if t_name and t_name != L["create_new_opt"]:
                if t_name in ["admin", "董事長 / 總經理"]:
                    st.error("🚫 系統保護：最高管理者角色無法被刪除！")
                else:
                    delete_role_db(engine, t_name)
                    st.success(L["del_role_success"].format(name=t_name))
                    st.rerun()

    # ----------------------------------------------------
    # Tab 2: 系統員工帳號管理 (CRUD)
    # ----------------------------------------------------
    with tab_users:
        st.markdown(f"### {L['users_header']}")
        st.dataframe(pd.DataFrame(st.session_state.system_users_db), use_container_width=True)

        st.markdown("---")
        st.markdown(f"### {L['add_user_header']}")
        with st.form("form_add_system_user_crud"):
            c1, c2 = st.columns(2)
            with c1:
                username = st.text_input(L["lbl_username"], value="staff02")
                name = st.text_input(L["lbl_name"], placeholder="例如: Nguyễn Văn A")
            with c2:
                available_roles = list(roles_dict.keys()) if roles_dict else ["admin", "manager", "security", "staff"]
                role = st.selectbox(L["lbl_role"], available_roles)
                site = st.selectbox(L["lbl_site"], L["site_opts"])

            if st.form_submit_button(L["btn_add_user"], type="primary", use_container_width=True):
                if username and name:
                    existing_usernames = [u["username"] for u in st.session_state.system_users_db]
                    if username in existing_usernames:
                        st.error(f"⚠️ 錯誤：帳號 `{username}` 已經存在！")
                    else:
                        st.session_state.system_users_db.append({
                            "username": username,
                            "name": name,
                            "role": role,
                            "site": site
                        })
                        st.session_state.audit_logs_db.insert(0, {
                            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "user": st.session_state.get("user_name", "admin"),
                            "action": f"新增系統帳號 [{username}] {name}",
                            "module": "UserMgmt",
                            "ip": "192.168.1.50",
                            "status": "成功"
                        })
                        st.success(L["success_add_user"].format(username=username))
                        st.rerun()
                else:
                    st.warning(L["fill_warning"])

        st.markdown("---")
        st.markdown("### ✏️ 修改與刪除現有使用者帳號")
        if st.session_state.system_users_db:
            user_options = [f"{u['username']} - {u['name']} ({u['role']})" for u in st.session_state.system_users_db]
            sel_target_user = st.selectbox("選擇要修改或刪除的員工帳號", user_options)
            target_uname = sel_target_user.split(" - ")[0]
            target_user_obj = next((u for u in st.session_state.system_users_db if u["username"] == target_uname), None)

            if target_user_obj:
                with st.form("form_edit_system_user_crud"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        ed_name = st.text_input("使用者姓名", value=target_user_obj["name"])
                        available_roles = list(roles_dict.keys()) if roles_dict else ["admin", "manager", "security", "staff"]
                        current_role_idx = available_roles.index(target_user_obj["role"]) if target_user_obj["role"] in available_roles else 0
                        ed_role = st.selectbox("權限角色", available_roles, index=current_role_idx)
                    with ec2:
                        site_list = L["site_opts"]
                        current_site_idx = site_list.index(target_user_obj["site"]) if target_user_obj["site"] in site_list else 0
                        ed_site = st.selectbox("所屬廠區", site_list, index=current_site_idx)

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        update_user_btn = st.form_submit_button("💾 儲存帳號變更", type="primary", use_container_width=True)
                    with col_b2:
                        delete_user_btn = st.form_submit_button("🔥 刪除此員工帳號", type="secondary", use_container_width=True)

                    if update_user_btn:
                        target_user_obj["name"] = ed_name
                        target_user_obj["role"] = ed_role
                        target_user_obj["site"] = ed_site
                        st.success(f"🎉 員工帳號 [{target_uname}] 資料已更新！")
                        st.rerun()

                    if delete_user_btn:
                        if target_uname == "admin":
                            st.error("⚠️ 系統安全保護：最高管理者帳號 [admin] 無法被刪除！")
                        else:
                            st.session_state.system_users_db = [u for u in st.session_state.system_users_db if u["username"] != target_uname]
                            st.success(f"🗑️ 帳號 [{target_uname}] 已刪除！")
                            st.rerun()
        else:
            st.info("目前尚無員工帳號可供修改。")

    # ----------------------------------------------------
    # Tab 3: 系統稽核日誌 (Audit Logs)
    # ----------------------------------------------------
    with tab_audit:
        st.markdown(f"### {L['tab_audit']}")
        if st.session_state.audit_logs_db:
            st.dataframe(pd.DataFrame(st.session_state.audit_logs_db), use_container_width=True)
        else:
            st.info("目前尚無稽核日誌紀錄。")

    # ----------------------------------------------------
    # Tab 4: 資料庫連線狀態
    # ----------------------------------------------------
    with tab_db:
        st.markdown(f"### {L['tab_db']}")
        if is_connected:
            st.success("🟢 PostgreSQL 資料庫連線正常！")
        else:
            st.info(f"ℹ️ 系統狀態提示: {msg}")

def show(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
