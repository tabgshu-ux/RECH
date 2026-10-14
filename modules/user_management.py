import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 資料庫連線初始化 (Supabase PostgreSQL)
# ----------------------------------------------------
def get_db_connection():
    try:
        from supabase import create_client, Client
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None

# ----------------------------------------------------
# 🌐 帳號權限與稽核軌跡模組多語系字典 (i18n)
# ----------------------------------------------------
USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 組織職能角色與系統權限範本管理 (資料庫連線版)",
        "caption": "採用 Supabase PostgreSQL 資料庫進行組織角色與權限之永久 CRUD 管理。",
        "tab_audit": "📊 系統稽核日誌 (Audit Logs)",
        "tab_roles": "⚙️ 組織角色與部門功能權限範本 (RBAC)",
        "tab_users": "👥 人事系統員工與系統帳號總覽",
        "tab_api": "🔌 電子發票 API 串接設定",
        "roles_header": "⚙️ 企業組織部門角色與權限範本清冊 (資料庫同步)",
        "btn_save_role": "💾 儲存並寫入資料庫",
        "btn_delete_role": "🗑️ 從資料庫刪除此角色",
        "success_role_save": "✅ 角色已成功寫入並更新至資料庫！",
        "success_role_delete": "🗑️ 角色已從資料庫永久刪除！",
        "success_add_user": "✅ 人事員工系統帳號與權限已成功指派！",
    },
    "English": {
        "title": "🔒 IT Center - Departmental Role RBAC & System Audit Logs (DB Connected)",
        "caption": "Persistent CRUD management of organizational roles via Supabase PostgreSQL.",
        "tab_audit": "📊 System Audit Logs",
        "tab_roles": "⚙️ Departmental Roles (RBAC)",
        "tab_users": "👥 HR & User Accounts",
        "tab_api": "🔌 E-Invoice API Config",
        "roles_header": "⚙️ Departmental Permission Roles (DB Synchronized)",
        "btn_save_role": "💾 Save & Write to Database",
        "btn_delete_role": "🗑️ Delete Role from Database",
        "success_role_save": "✅ Role successfully saved and updated in database!",
        "success_role_delete": "🗑️ Role successfully deleted from database!",
        "success_add_user": "✅ Employee system account & role successfully assigned!",
    },
    "Tiếng Việt": {
        "title": "🔒 Quản trị IT - Phân quyền Doanh nghiệp (Kết nối CSDL)",
        "caption": "Quản lý vai trò và phân quyền qua cơ sở dữ liệu Supabase.",
        "tab_audit": "📊 Nhật ký Kiểm toán",
        "tab_roles": "⚙️ Quản lý Vai trò (RBAC)",
        "tab_users": "👥 Danh sách Nhân sự",
        "tab_api": "🔌 Cấu hình API Hóa đơn",
        "roles_header": "⚙️ Danh sách vai trò (Đồng bộ CSDL)",
        "btn_save_role": "💾 Lưu vào CSDL",
        "btn_delete_role": "🗑️ Xóa khỏi CSDL",
        "success_role_save": "✅ Đã lưu và cập nhật vào CSDL!",
        "success_role_delete": "🗑️ Đã xóa vĩnh viễn khỏi CSDL!",
        "success_add_user": "✅ Thành công!",
    }
}

def load_roles_from_db():
    supabase = get_db_connection()
    default_roles = {
        "董事長 / 總經理 (Chairman / GM)": {"desc": "👑 總經理室：可檢視與審核全系統所有部門與跨模組資料"},
        "副總經理 (Vice General Manager / VP)": {"desc": "👔 副總經理室：負責各部門工程報價、採購叫料與合約專案之跨部門最終審核"},
        "管理部主管 (Admin & Finance Manager)": {"desc": "📋 管理部：負責人事、財務、總務與匯總下方各部門資料"},
        "工程總監 / 設計主管 (Engineering Director)": {"desc": "🛠️ 工程部門：專注於專案報價、工程驗收、日報表與 BOM 展開"},
        "倉庫管理員 / 生產主管 (Warehouse & Production)": {"desc": "🏭 生產與倉管：管理廠區生產線、車間打卡、板金塗料與倉庫庫存"}
    }
    
    if supabase:
        try:
            res = supabase.table("system_roles").select("*").execute()
            if res.data:
                db_roles = {}
                for row in res.data:
                    db_roles[row["role_name"]] = {"desc": row["description"]}
                return db_roles
        except Exception:
            pass
    return default_roles

def save_role_to_db(role_name, description, old_role_name=None):
    supabase = get_db_connection()
    if supabase:
        try:
            if old_role_name and old_role_name != role_name:
                supabase.table("system_roles").delete().eq("role_name", old_role_name).execute()
            
            # Upsert role
            supabase.table("system_roles").upsert({
                "role_name": role_name,
                "description": description
            }, on_conflict="role_name").execute()
            return True
        except Exception as e:
            st.error(f"資料庫寫入失敗: {e}")
    return False

def delete_role_from_db(role_name):
    supabase = get_db_connection()
    if supabase:
        try:
            supabase.table("system_roles").delete().eq("role_name", role_name).execute()
            return True
        except Exception as e:
            st.error(f"資料庫刪除失敗: {e}")
    return False

def render_user_management_page(lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = USER_MGMT_I18N.get(active_lang, USER_MGMT_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 從資料庫加載角色
    st.session_state.system_roles_db = load_roles_from_db()

    if "audit_logs_db" not in st.session_state:
        st.session_state.audit_logs_db = [
            {"time": "2026-10-06 13:00:15", "user": "admin", "action": "登入系統 (Login)", "module": "Auth", "ip": "192.168.1.50", "status": "成功"}
        ]

    if "system_users_db" not in st.session_state:
        st.session_state.system_users_db = [
            {"username": "admin", "name": "許福村", "role": "董事長 / 總經理 (Chairman / GM)", "site": "西寧廠 (Tay Ninh)"},
            {"username": "vgm", "name": "副總經理", "role": "副總經理 (Vice General Manager / VP)", "site": "西寧廠 (Tay Ninh)"}
        ]

    tab_audit, tab_roles, tab_users, tab_api = st.tabs([L["tab_audit"], L["tab_roles"], L["tab_users"], L["tab_api"]])

    with tab_audit:
        st.markdown(f"### 全系統操作軌跡與稽核日誌")
        st.dataframe(pd.DataFrame(st.session_state.audit_logs_db), use_container_width=True)

    with tab_roles:
        st.markdown(f"### {L['roles_header']}")
        role_list_display = [{"角色名稱": r_name, "部門職責與資料範圍說明": r_info.get("desc", "")} for r_name, r_info in st.session_state.system_roles_db.items()]
        st.dataframe(pd.DataFrame(role_list_display), use_container_width=True)

        st.markdown("---")
        st.markdown("### ✏️ 資料庫角色 CRUD 維護 (新增、修改、刪除)")
        role_action_mode = st.radio("選擇操作模式", ["修改現有部門角色範本", "新增全新部門角色範本"], horizontal=True)

        if role_action_mode == "修改現有部門角色範本":
            existing_role_names = list(st.session_state.system_roles_db.keys())
            if existing_role_names:
                selected_edit_role = st.selectbox("🎯 選擇要修改的角色名稱", existing_role_names)
                
                with st.form("form_edit_department_role"):
                    new_role_title = st.text_input("修改後的角色名稱", value=selected_edit_role)
                    role_desc_input = st.text_input("部門職責與檢視權限說明", value=st.session_state.system_roles_db[selected_edit_role].get("desc", ""))
                    
                    col_btn_r1, col_btn_r2 = st.columns(2)
                    with col_btn_r1:
                        save_role_btn = st.form_submit_button(L["btn_save_role"], type="primary", use_container_width=True)
                    with col_btn_r2:
                        delete_role_btn = st.form_submit_button(L["btn_delete_role"], use_container_width=True)

                    if save_role_btn:
                        success = save_role_to_db(new_role_title, role_desc_input, selected_edit_role)
                        if success:
                            st.success(L["success_role_save"])
                            st.rerun()

                    if delete_role_btn:
                        if len(st.session_state.system_roles_db) > 1:
                            del_success = delete_role_from_db(selected_edit_role)
                            if del_success:
                                st.success(L["success_role_delete"])
                                st.rerun()
                        else:
                            st.warning("⚠️ 系統至少需保留一個角色範本！")
        else:
            with st.form("form_add_department_role"):
                new_role_title = st.text_input("新部門角色名稱 (例如: 副總經理、行政主管、設計主管...)")
                role_desc_input = st.text_input("部門職責與資料範圍說明")

                if st.form_submit_button("💾 寫入資料庫建立新角色", type="primary", use_container_width=True):
                    if new_role_title:
                        success = save_role_to_db(new_role_title, role_desc_input)
                        if success:
                            st.success("✅ 新部門角色已成功寫入資料庫！")
                            st.rerun()
                    else:
                        st.warning("⚠️ 請輸入角色名稱！")

    with tab_users:
        st.markdown(f"### {L['users_header']}")
        st.dataframe(pd.DataFrame(st.session_state.system_users_db), use_container_width=True)

    with tab_api:
        st.markdown(f"### 🔌 越南電子發票 API 參數設定")
        st.info("API 閘道設定已與系統資料庫連線。")

def show(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
