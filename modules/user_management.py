import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 帳號權限與稽核軌跡模組多語系字典 (i18n)
# ----------------------------------------------------
USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 帳號權限與系統稽核軌跡 (Audit Log)",
        "caption": "監控全系統使用者登入歷程、權限異動紀錄、資料庫連線安全與系統級稽核日誌。",
        "tab_audit": "📊 系統稽核日誌 (Audit Logs)",
        "tab_users": "👥 系統使用者與權限控管",
        "tab_manage_users": "✏️ 修改與刪除使用者帳號",
        "audit_header": "🔍 全系統操作軌跡與稽核軌跡日誌",
        "filter_year": "篩選年份 (Year)",
        "filter_month": "篩選月份 (Month)",
        "filter_day": "篩選日期 (Day)",
        "search_placeholder": "輸入關鍵字搜尋稽核紀錄...",
        "no_logs": "目前尚無系統稽核紀錄。",
        "users_header": "👥 系統現有使用者帳號清冊",
        "add_user_header": "➕ 新增系統使用者帳號",
        "lbl_username": "登入帳號 *",
        "lbl_name": "使用者姓名 *",
        "lbl_role": "權限角色 *",
        "role_opts": ["admin", "manager", "security", "staff"],
        "lbl_site": "所屬廠區 *",
        "site_opts": ["台灣總部 (Taiwan HQ)", "越南西寧廠 (Tay Ninh)", "越南海防廠 (Hai Phong)"],
        "btn_add_user": "💾 建立使用者帳號",
        "success_add": "✅ 系統帳號 `{username}` 已成功建立！",
        "fill_warning": "⚠️ 請填寫完整帳號與姓名！",
        "col_time": "時間戳記",
        "col_user": "操作帳號",
        "col_action": "動作行為",
        "col_module": "模組名稱",
        "col_ip": "來源 IP",
        "col_status": "執行狀態"
    },
    "Tiếng Việt": {
        "title": "🔒 Quản trị IT - Phân quyền Tài khoản & Nhật ký Kiểm toán (Audit Log)",
        "caption": "Giám sát lịch sử đăng nhập, thay đổi phân quyền, bảo mật kết nối cơ sở dữ liệu và nhật ký hệ thống.",
        "tab_audit": "📊 Nhật ký Kiểm toán (Audit Logs)",
        "tab_users": "👥 Quản lý Người dùng & Phân quyền",
        "tab_manage_users": "✏️ Sửa & Xóa Tài khoản",
        "audit_header": "🔍 Nhật ký thao tác và kiểm toán toàn hệ thống",
        "filter_year": "Lọc theo Năm",
        "filter_month": "Lọc theo Tháng",
        "filter_day": "Lọc theo Ngày",
        "search_placeholder": "Nhập từ khóa tìm kiếm...",
        "no_logs": "Hiện chưa có nhật ký kiểm toán nào.",
        "users_header": "📋 Danh sách tài khoản người dùng hệ thống",
        "add_user_header": "➕ Thêm tài khoản người dùng mới",
        "lbl_username": "Tài khoản đăng nhập *",
        "lbl_name": "Họ tên người dùng *",
        "lbl_role": "Vai trò phân quyền *",
        "role_opts": ["admin", "manager", "security", "staff"],
        "lbl_site": "Nhà máy trực thuộc *",
        "site_opts": ["Trụ sở Đài Loan (HQ)", "Nhà máy Tây Ninh", "Nhà máy Hải Phòng"],
        "btn_add_user": "💾 Tạo tài khoản",
        "success_add": "✅ Đã tạo thành công tài khoản `{username}`!",
        "fill_warning": "⚠️ Vui lòng điền đầy đủ tài khoản và họ tên!",
        "col_time": "Thời gian",
        "col_user": "Tài khoản",
        "col_action": "Hành động",
        "col_module": "Module",
        "col_ip": "IP nguồn",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "🔒 IT Center - User Permissions & System Audit Logs",
        "caption": "Monitor system login history, permission changes, database security, and system-level audit logs.",
        "tab_audit": "📊 System Audit Logs",
        "tab_users": "👥 Users & Permissions Control",
        "tab_manage_users": "✏️ Edit & Delete Users",
        "audit_header": "🔍 System Operation & Audit Trail Logs",
        "filter_year": "Filter Year",
        "filter_month": "Filter Month",
        "filter_day": "Filter Day",
        "search_placeholder": "Search audit logs...",
        "no_logs": "No audit logs found.",
        "users_header": "👥 Active System User Accounts",
        "add_user_header": "➕ Register New User Account",
        "lbl_username": "Username *",
        "lbl_name": "Full Name *",
        "lbl_role": "Permission Role *",
        "role_opts": ["admin", "manager", "security", "staff"],
        "lbl_site": "Plant Location *",
        "site_opts": ["Taiwan HQ", "Tay Ninh Plant", "Hai Phong Plant"],
        "btn_add_user": "💾 Create User Account",
        "success_add": "✅ User account `{username}` successfully created!",
        "fill_warning": "⚠️ Please fill in username and full name!",
        "col_time": "Timestamp",
        "col_user": "Username",
        "col_action": "Action",
        "col_module": "Module",
        "col_ip": "Source IP",
        "col_status": "Status"
    }
}

def smart_translate_user(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    
    val_lower = text_val.lower()
    if "成功" in text_val or "success" in val_lower or "thành công" in val_lower:
        if target_lang == "Tiếng Việt": return "🟢 Thành công (Success)"
        elif target_lang == "English": return "🟢 Success"
        return "🟢 執行成功 (Success)"

    return text_val

def render_user_management_page(lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = USER_MGMT_I18N.get(active_lang, USER_MGMT_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "audit_logs_db" not in st.session_state:
        st.session_state.audit_logs_db = [
            {"time": "2026-10-06 13:00:15", "user": "admin", "action": "登入系統 (Login)", "module": "Auth", "ip": "192.168.1.50", "status": "成功"},
            {"time": "2026-10-06 13:05:22", "user": "manager", "action": "審核電子簽核單 [APP-2026-001]", "module": "Approval", "ip": "192.168.1.88", "status": "成功"},
            {"time": "2026-10-06 13:10:40", "user": "security", "action": "登記廠區車輛進出 [61A-888.66]", "module": "VehicleGate", "ip": "192.168.1.102", "status": "成功"}
        ]

    if "system_users_db" not in st.session_state or not isinstance(st.session_state.system_users_db, list):
        st.session_state.system_users_db = [
            {"username": "admin", "name": "系統管理員", "role": "admin", "site": "台灣總部"},
            {"username": "manager", "name": "陳經理", "role": "manager", "site": "越南西寧廠"},
            {"username": "security", "name": "大門保全組", "role": "security", "site": "越南西寧廠"}
        ]

    tab_audit, tab_users, tab_manage = st.tabs([L["tab_audit"], L["tab_users"], L["tab_manage_users"]])

    with tab_audit:
        st.markdown(f"### {L['audit_header']}")
        c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
        with c1: f_year = st.selectbox(L["filter_year"], ["全部", "2026", "2025"])
        with c2: f_month = st.selectbox(L["filter_month"], ["全部", "10", "09", "08"])
        with c3: f_day = st.selectbox(L["filter_day"], ["全部", "06", "05", "04"])
        with c4: search_kw = st.text_input("搜尋關鍵字", placeholder=L["search_placeholder"])

        if st.session_state.audit_logs_db:
            display_logs = []
            for log in st.session_state.audit_logs_db:
                display_logs.append({
                    L["col_time"]: log["time"],
                    L["col_user"]: log["user"],
                    L["col_action"]: log["action"],
                    L["col_module"]: log["module"],
                    L["col_ip"]: log["ip"],
                    L["col_status"]: smart_translate_user(log["status"], active_lang)
                })
            st.dataframe(pd.DataFrame(display_logs), use_container_width=True)
        else:
            st.info(L["no_logs"])

    with tab_users:
        st.markdown(f"### {L['users_header']}")
        st.dataframe(pd.DataFrame(st.session_state.system_users_db), use_container_width=True)

        st.markdown("---")
        st.markdown(f"### {L['add_user_header']}")
        with st.form("form_add_system_user"):
            c1, c2 = st.columns(2)
            with c1:
                username = st.text_input(L["lbl_username"], value="staff01")
                name = st.text_input(L["lbl_name"], placeholder="例如: Nguyễn Văn A")
            with c2:
                role = st.selectbox(L["lbl_role"], L["role_opts"])
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
                        st.success(L["success_add"].format(username=username))
                        st.rerun()
                else:
                    st.warning(L["fill_warning"])

    with tab_manage:
        st.markdown("### ✏️ 修改與刪除使用者帳號權限")
        if st.session_state.system_users_db:
            user_options = [f"{u['username']} - {u['name']} ({u['role']})" for u in st.session_state.system_users_db]
            sel_target_user = st.selectbox("選擇要修改或刪除的使用者帳號", user_options)
            target_uname = sel_target_user.split(" - ")[0]
            target_user_obj = next((u for u in st.session_state.system_users_db if u["username"] == target_uname), None)

            if target_user_obj:
                with st.form("form_edit_system_user"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        ed_name = st.text_input("使用者姓名", value=target_user_obj["name"])
                        role_list = ["admin", "manager", "security", "staff"]
                        current_role_idx = role_list.index(target_user_obj["role"]) if target_user_obj["role"] in role_list else 3
                        ed_role = st.selectbox("權限角色", role_list, index=current_role_idx)
                    with ec2:
                        site_list = ["台灣總部 (Taiwan HQ)", "越南西寧廠 (Tay Ninh)", "越南海防廠 (Hai Phong)"]
                        current_site_idx = site_list.index(target_user_obj["site"]) if target_user_obj["site"] in site_list else 0
                        ed_site = st.selectbox("所屬廠區", site_list, index=current_site_idx)

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        update_user_btn = st.form_submit_button("💾 儲存帳號變更", type="primary", use_container_width=True)
                    with col_b2:
                        delete_user_btn = st.form_submit_button("🔥 刪除此使用者帳號", type="secondary", use_container_width=True)

                    if update_user_btn:
                        target_user_obj["name"] = ed_name
                        target_user_obj["role"] = ed_role
                        target_user_obj["site"] = ed_site
                        st.success(f"🎉 帳號 [{target_uname}] 的權限與資料已成功更新！")
                        st.rerun()

                    if delete_user_btn:
                        if target_uname == "admin":
                            st.error("⚠️ 系統安全保護：最高管理者帳號 [admin] 無法被刪除！")
                        else:
                            st.session_state.system_users_db = [u for u in st.session_state.system_users_db if u["username"] != target_uname]
                            st.success(f"🗑️ 帳號 [{target_uname}] 已從系統中徹底刪除！")
                            st.rerun()
        else:
            st.info("目前尚無系統使用者帳號可供修改。")

def show(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
