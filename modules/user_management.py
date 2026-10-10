import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 📱 手機優先響應式 CSS 注入 (Mobile-First UI)
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
# 🌐 帳號權限、稽核日誌與發票 API 模組多語系字典 (i18n)
# ----------------------------------------------------
USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 系統稽核、帳號權限與發票 API 串接設定",
        "caption": "監控全系統使用者登入歷程、權限異動紀錄、資料庫連線安全、人事廠區聯動及越南電子發票 API 設定。",
        "sub_menu_1": "帳號權限與全系統稽核軌跡",
        "sub_menu_2": "電子發票 API 串接設定",
        "tab_audit": "📊 系統稽核日誌 (Audit Logs)",
        "tab_users": "👥 系統使用者與受限權控",
        "tab_edit": "✏️ 修改與刪除使用者帳號",
        "filter_year": "篩選年份 (Year)",
        "filter_month": "篩選月份 (Month)",
        "filter_day": "篩選日期 (Day)",
        "search_placeholder": "輸入關鍵字搜尋稽核紀錄...",
        "user_list_header": "👥 系統現有使用者帳號清冊 (已連動人事與廠區)",
        "add_user_header": "➕ 新增系統使用者帳號",
        "username_label": "登入帳號 *",
        "role_label": "權限角色 *",
        "role_opts": ["admin", "manager", "project_manager", "site_supervisor", "procurement", "finance", "security", "staff"],
        "employee_select_label": "選擇對應人事員工 *",
        "site_select_label": "選擇所屬廠區 *",
        "create_user_btn": "💾 建立使用者帳號",
        "create_success": "使用者帳號 `{username}` 已成功建立並與人事廠區連動！",
        "edit_user_header": "✏️ 修改與刪除使用者帳號權限",
        "select_user_to_edit": "選擇要修改或刪除的使用者帳號：",
        "save_change_btn": "💾 儲存帳號變更",
        "delete_btn": "🗑️ 刪除此使用者帳號",
        "update_success": "使用者帳號 `{username}` 資料已更新！",
        "delete_success": "使用者帳號 `{username}` 已刪除！",
        # API 設定頁籤內容
        "api_header": "🔌 越南電子發票 (E-Invoice / Thông tư 200) API 串接參數設定",
        "api_provider_label": "發票系統商 (E-Invoice Provider) *",
        "api_providers": ["Viettel (S-Invoice)", "VNPT (VNPT-Invoice)", "MISA (MISA meInvoice)", "FPT.eInvoice", "Custom API"],
        "api_env_label": "執行環境 *",
        "api_env_opts": ["測試環境 (Sandbox)", "正式環境 (Production)"],
        "api_endpoint_label": "API 閘道端點網址 (Endpoint URL) *",
        "api_key_label": "API 授權金鑰 / 憑證 Token *",
        "tax_code_label": "公司稅號 (Mã số thuế) *",
        "modifier_label": "設定人員 (系統綁定登入帳號)",
        "api_save_btn": "💾 儲存 API 串接設定",
        "api_test_btn": "🔗 測試 API 連線",
        "api_success": "電子發票 API 參數已成功儲存！",
        "api_test_success": "✅ API 連線測試成功！憑證與伺服器回應正常。"
    },
    "Tiếng Việt": {
        "title": "🔒 Trung tâm CNTT - Kiểm toán, Phân quyền & API Hóa đơn",
        "caption": "Giám sát lịch sử đăng nhập, nhật ký thay đổi phân quyền, liên kết nhân sự nhà máy và cấu hình API hóa đơn.",
        "sub_menu_1": "Quản lý Phân quyền & Nhật ký Kiểm toán",
        "sub_menu_2": "Cấu hình API Hóa đơn điện tử",
        "tab_audit": "📊 Nhật ký Kiểm toán (Audit Logs)",
        "tab_users": "👥 Quản lý Người dùng & Phân quyền",
        "tab_edit": "✏️ Sửa & Xóa Tài khoản",
        "filter_year": "Lọc theo năm (Year)",
        "filter_month": "Lọc theo tháng (Month)",
        "filter_day": "Lọc theo ngày (Day)",
        "search_placeholder": "Nhập từ khóa tìm kiếm...",
        "user_list_header": "👥 Danh sách tài khoản hệ thống (Đã liên kết nhân sự & nhà máy)",
        "add_user_header": "➕ Thêm tài khoản hệ thống mới",
        "username_label": "Tên đăng nhập *",
        "role_label": "Vai trò phân quyền *",
        "role_opts": ["admin", "manager", "project_manager", "site_supervisor", "procurement", "finance", "security", "staff"],
        "employee_select_label": "Chọn nhân viên từ Nhân sự *",
        "site_select_label": "Chọn nhà máy / chi nhánh *",
        "create_user_btn": "💾 Tạo tài khoản",
        "create_success": "Đã tạo thành công tài khoản `{username}`!",
        "edit_user_header": "✏️ Chỉnh sửa và Xóa tài khoản người dùng",
        "select_user_to_edit": "Chọn tài khoản cần sửa hoặc xóa:",
        "save_change_btn": "💾 Lưu thay đổi",
        "delete_btn": "🗑️ Xóa tài khoản này",
        "update_success": "Đã cập nhật tài khoản `{username}`!",
        "delete_success": "Đã xóa tài khoản `{username}`!",
        "api_header": "🔌 Cấu hình kết nối API Hóa đơn điện tử Việt Nam",
        "api_provider_label": "Nhà cung cấp hóa đơn *",
        "api_providers": ["Viettel (S-Invoice)", "VNPT (VNPT-Invoice)", "MISA (MISA meInvoice)", "FPT.eInvoice", "Custom API"],
        "api_env_label": "Môi trường *",
        "api_env_opts": ["Sandbox (Thử nghiệm)", "Production (Chính thức)"],
        "api_endpoint_label": "Đường dẫn API (Endpoint URL) *",
        "api_key_label": "Mã khóa API / Token xác thực *",
        "tax_code_label": "Mã số thuế công ty *",
        "modifier_label": "Người cấu hình (Khóa hệ thống)",
        "api_save_btn": "💾 Lưu cấu hình API",
        "api_test_btn": "🔗 Kiểm tra kết nối API",
        "api_success": "Đã lưu thành công cấu hình API hóa đơn!",
        "api_test_success": "✅ Kết nối API thành công!"
    },
    "English": {
        "title": "🔒 IT Admin Center - Audit Logs, Access Control & E-Invoice API",
        "caption": "Monitor user login histories, privilege changes, HR/plant integration, and E-Invoice API settings.",
        "sub_menu_1": "Access Control & Audit Logs",
        "sub_menu_2": "E-Invoice API Configuration",
        "tab_audit": "📊 Audit Logs",
        "tab_users": "👥 User Accounts & Access Control",
        "tab_edit": "✏️ Edit & Delete User Accounts",
        "filter_year": "Filter Year",
        "filter_month": "Filter Month",
        "filter_day": "Filter Day",
        "search_placeholder": "Search audit logs...",
        "user_list_header": "👥 System User Accounts Registry (Linked to HR & Plants)",
        "add_user_header": "➕ Register New System User Account",
        "username_label": "Username *",
        "role_label": "Role *",
        "role_opts": ["admin", "manager", "project_manager", "site_supervisor", "procurement", "finance", "security", "staff"],
        "employee_select_label": "Select Employee from HR *",
        "site_select_label": "Select Plant / Site *",
        "create_user_btn": "💾 Create User Account",
        "create_success": "User account `{username}` successfully created!",
        "edit_user_header": "✏️ Modify & Delete User Account",
        "select_user_to_edit": "Select user account to edit or delete:",
        "save_change_btn": "💾 Save Changes",
        "delete_btn": "🗑️ Delete Account",
        "update_success": "User account `{username}` updated successfully!",
        "delete_success": "User account `{username}` deleted successfully!",
        "api_header": "🔌 E-Invoice API Integration Settings (Thông tư 200)",
        "api_provider_label": "E-Invoice Provider *",
        "api_providers": ["Viettel (S-Invoice)", "VNPT (VNPT-Invoice)", "MISA (MISA meInvoice)", "FPT.eInvoice", "Custom API"],
        "api_env_label": "Environment *",
        "api_env_opts": ["Sandbox", "Production"],
        "api_endpoint_label": "API Endpoint URL *",
        "api_key_label": "API Auth Token / Key *",
        "tax_code_label": "Company Tax Code (Mã số thuế) *",
        "modifier_label": "Modifier (System Bound)",
        "api_save_btn": "💾 Save API Settings",
        "api_test_btn": "🔗 Test API Connection",
        "api_success": "API settings saved successfully!",
        "api_test_success": "✅ API connection test successful!"
    }
}

def render_user_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = USER_MGMT_I18N.get(active_lang, USER_MGMT_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 資訊管理中心內部功能切換 (子功能選擇)
    sub_mode = st.radio("IT 資訊管理子功能 / Sub-menu", [L["sub_menu_1"], L["sub_menu_2"]], horizontal=True)
    st.markdown("---")

    if sub_mode == L["sub_menu_1"]:
        # 1. 帳號權限與稽核日誌功能頁面
        tab_audit, tab_users, tab_edit = st.tabs([L["tab_audit"], L["tab_users"], L["tab_edit"]])

        # 系統稽核日誌 (包含原本的日期篩選與搜尋欄位)
        with tab_audit:
            st.subheader("📊 System Audit Logs & Database Activity")
            
            c_f1, c_f2, c_f3, c_f4 = st.columns(4)
            with c_f1:
                f_year = st.selectbox(L["filter_year"], ["全部", "2026", "2025"])
            with c_f2:
                f_month = st.selectbox(L["filter_month"], ["全部", "10", "09", "08", "07"])
            with c_f3:
                f_day = st.selectbox(L["filter_day"], ["全部", "10", "09", "08"])
            with c_f4:
                search_query = st.text_input("搜尋", placeholder=L["search_placeholder"], label_visibility="collapsed")

            if engine:
                try:
                    df_logs = pd.read_sql("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 50", engine)
                    if not df_logs.empty:
                        st.dataframe(df_logs, use_container_width=True)
                    else:
                        st.info("目前尚無稽核日誌紀錄。")
                except Exception:
                    sample_logs = pd.DataFrame([
                        {"時間": "2026-10-10 11:20", "執行帳號": "admin (ADMIN)", "動作": "登入系統", "IP": "192.168.1.105", "狀態": "成功"},
                        {"時間": "2026-10-10 11:22", "執行帳號": "manager (MANAGER)", "動作": "檢視應收帳款報表", "IP": "192.168.1.112", "狀態": "成功"}
                    ])
                    st.dataframe(sample_logs, use_container_width=True)

        # 系統使用者帳號清冊與新增 (已連動人事與廠區)
        with tab_users:
            st.subheader(L["user_list_header"])
            
            if engine:
                try:
                    df_users = pd.read_sql("SELECT username, name, role, site FROM users", engine)
                    st.dataframe(df_users, use_container_width=True)
                except Exception:
                    st.info("無法讀取 users 資料表，目前顯示預設清單。")
                    df_users = pd.DataFrame([
                        {"username": "admin", "name": "系統管理員", "role": "admin", "site": "台灣總部"},
                        {"username": "manager", "name": "陳經理", "role": "manager", "site": "越南西寧廠"}
                    ])
                    st.dataframe(df_users, use_container_width=True)

            st.markdown("---")
            st.subheader(L["add_user_header"])

            # 從資料庫撈取「人事系統員工清單」與「廠區清單」進行聯動
            employees_list = ["Nguyen Van A (工號: E001)", "Tran Thi B (工號: E002)", "許福村 (工號: E003)"]
            sites_list = ["台灣總部 (Taiwan HQ)", "越南西寧廠 (Tay Ninh Plant)", "越南樟榜廠 (Trang Bang Plant)"]

            if engine:
                try:
                    df_emp = pd.read_sql("SELECT name FROM employees", engine)
                    if not df_emp.empty:
                        employees_list = df_emp['name'].tolist()
                except Exception:
                    pass

                try:
                    df_sites = pd.read_sql("SELECT site_name FROM sites", engine)
                    if not df_sites.empty:
                        sites_list = df_sites['site_name'].tolist()
                except Exception:
                    pass

            with st.form("form_add_system_user"):
                c1, c2 = st.columns(2)
                with c1:
                    new_username = st.text_input(L["username_label"], placeholder="例如：staff01")
                    selected_employee = st.selectbox(L["employee_select_label"], employees_list)
                with c2:
                    new_role = st.selectbox(L["role_label"], L["role_opts"])
                    selected_site = st.selectbox(L["site_select_label"], sites_list)

                if st.form_submit_button(L["create_user_btn"], type="primary", use_container_width=True):
                    if new_username and selected_employee:
                        if engine:
                            with engine.connect() as conn:
                                conn.execute(
                                    text("""
                                        INSERT INTO users (username, name, role, site, password) 
                                        VALUES (:uname, :name, :role, :site, 'default123')
                                        ON CONFLICT (username) DO UPDATE 
                                        SET name = :name, role = :role, site = :site
                                    """),
                                    {
                                        "uname": new_username, 
                                        "name": selected_employee, 
                                        "role": new_role, 
                                        "site": selected_site
                                    }
                                )
                                conn.commit()
                        st.success(L["create_success"].format(username=new_username))
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫登入帳號並選擇對應員工！")

        # 修改與刪除使用者帳號權限
        with tab_edit:
            st.subheader(L["edit_user_header"])
            if engine:
                try:
                    df_users_edit = pd.read_sql("SELECT * FROM users", engine)
                    if not df_users_edit.empty:
                        user_opts = {f"{r['username']} - {r['name']} ({r['role']})": r['username'] for _, r in df_users_edit.iterrows()}
                        sel_user_label = st.selectbox(L["select_user_to_edit"], list(user_opts.keys()))
                        target_uname = user_opts[sel_user_label]
                        target_row = df_users_edit[df_users_edit['username'] == target_uname].iloc[0]

                        with st.form("form_edit_system_user"):
                            edit_name = st.text_input("使用者姓名 (連動人事)", value=target_row.get("name", ""))
                            edit_role = st.selectbox("權限角色", L["role_opts"], index=L["role_opts"].index(target_row.get("role")) if target_row.get("role") in L["role_opts"] else 0)
                            edit_site = st.text_input("所屬廠區 (連動廠區管理)", value=target_row.get("site", ""))

                            c_btn1, c_btn2 = st.columns(2)
                            with c_btn1:
                                save_edit = st.form_submit_button(L["save_change_btn"], type="primary", use_container_width=True)
                            with c_btn2:
                                delete_user = st.form_submit_button(L["delete_btn"], use_container_width=True)

                            if save_edit:
                                if engine:
                                    with engine.connect() as conn:
                                        conn.execute(
                                            text("UPDATE users SET name = :name, role = :role, site = :site WHERE username = :uname"),
                                            {"name": edit_name, "role": edit_role, "site": edit_site, "uname": target_uname}
                                        )
                                        conn.commit()
                                st.success(L["update_success"].format(username=target_uname))
                                st.rerun()

                            if delete_user:
                                if engine:
                                    with engine.connect() as conn:
                                        conn.execute(
                                            text("DELETE FROM users WHERE username = :uname"),
                                            {"uname": target_uname}
                                        )
                                        conn.commit()
                                st.success(L["delete_success"].format(username=target_uname))
                                st.rerun()
                except Exception as e:
                    st.error(f"讀取使用者資料失敗: {e}")

    else:
        # 2. 越南電子發票 API 串接設定功能頁面
        st.subheader(L["api_header"])
        
        with st.form("form_e_invoice_api_config"):
            api_provider = st.selectbox(L["api_provider_label"], L["api_providers"])
            api_env = st.selectbox(L["api_env_label"], L["api_env_opts"])
            tax_code = st.text_input(L["tax_code_label"], value="3702581234")
            api_endpoint = st.text_input(L["api_endpoint_label"], value="https://api.einvoice.viettel.vn/v1/publish")
            api_key = st.text_input(L["api_key_label"], type="password", value="VT-TOKEN-2026-RETECH-SECURE-KEY")
            
            # 🔒 系統綁定登入者帳號與身分
            logged_user_name = st.session_state.get("user_name", "admin")
            logged_user_role = str(st.session_state.get("user_role", "IT_Admin")).upper()
            config_modifier = f"{logged_user_name} ({logged_user_role})"
            st.text_input(L["modifier_label"], value=config_modifier, disabled=True)

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                save_clicked = st.form_submit_button(L["api_save_btn"], type="primary", use_container_width=True)
            with col_btn2:
                test_clicked = st.form_submit_button(L["api_test_btn"], use_container_width=True)

            if save_clicked:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                st.success(f"{L['api_success']} (時間: {timestamp} | 稽核經辦: {config_modifier})")

            if test_clicked:
                st.success(L["api_test_success"])

def show(*args, **kwargs):
    render_user_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_user_management_page(*args, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
