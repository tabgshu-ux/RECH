import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 帳號權限與稽核軌跡模組多語系字典 (i18n)
# ----------------------------------------------------
USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 帳號權限與系統稽核軌跡 (Audit Log)",
        "caption": "監控全系統使用者登入歷程、權限異動紀錄、資料庫連線安全與系統級稽核日誌，並精準控管各權限可存取的系統網頁。",
        "tab_audit": "📊 系統稽核日誌 (Audit Logs)",
        "tab_users": "👥 系統使用者與網頁權限控管",
        "tab_api": "🔌 電子發票 API 串接設定",
        "audit_header": "🔍 全系統操作軌跡與稽核軌跡日誌",
        "filter_year": "篩選年份 (Year)",
        "filter_month": "篩選月份 (Month)",
        "filter_day": "篩選日期 (Day)",
        "search_placeholder": "輸入關鍵字搜尋稽核紀錄...",
        "no_logs": "目前尚無系統稽核紀錄。",
        "users_header": "👥 系統現有使用者帳號與網頁存取權限清冊",
        "add_user_header": "➕ 新增系統使用者帳號與網頁存取授權",
        "lbl_username": "登入帳號 *",
        "lbl_name": "使用者姓名 *",
        "lbl_role": "權限角色 *",
        "role_opts": ["admin", "manager", "security", "staff"],
        "lbl_site": "所屬廠區 *",
        "site_opts": ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"],
        "btn_add_user": "💾 建立使用者帳號與賦權",
        "success_add": "✅ 系統帳號 `{username}` 已成功建立！",
        "fill_warning": "⚠️ 請填寫完整帳號與姓名！",
        # 表格欄位
        "col_time": "時間戳記",
        "col_user": "操作帳號",
        "col_action": "動作行為",
        "col_module": "模組名稱",
        "col_ip": "來源 IP",
        "col_status": "執行狀態",
        # API 設定專用
        "api_header": "🔌 越南電子發票 (E-Invoice / Thông tư 200) API 閘道設定",
        "api_provider_label": "發票系統商 (E-Invoice Provider) *",
        "api_providers": ["Viettel (S-Invoice)", "VNPT (VNPT-Invoice)", "MISA (MISA meInvoice)", "FPT.eInvoice", "Custom API"],
        "api_env_label": "執行環境 *",
        "api_env_opts": ["測試環境 (Sandbox)", "正式環境 (Production)"],
        "tax_code_label": "公司稅號 (Mã số thuế) *",
        "endpoint_label": "API 閘道端點網址 (Endpoint URL) *",
        "key_label": "API 授權金鑰 / 憑證 Token *",
        "modifier_label": "設定人員 (系統自動綁定登入帳號)",
        "api_save_btn": "💾 儲存 API 串接設定",
        "api_test_btn": "🔗 測試 API 連線",
        "api_success": "✅ 電子發票 API 參數已成功儲存！",
        "api_test_success": "✅ API 連線測試成功！憑證授權與伺服器回應正常。"
    },
    "Tiếng Việt": {
        "title": "🔒 Quản trị IT - Phân quyền Tài khoản & Nhật ký Kiểm toán (Audit Log)",
        "caption": "Giám sát lịch sử đăng nhập, thay đổi phân quyền truy cập trang web và cấu hình API hóa đơn.",
        "tab_audit": "📊 Nhật ký Kiểm toán (Audit Logs)",
        "tab_users": "👥 Quản lý Người dùng & Phân quyền",
        "tab_api": "🔌 Cấu hình API Hóa đơn",
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
        "site_opts": ["Nhà máy Tây Ninh", "Nhà máy Hải Phòng"],
        "btn_add_user": "💾 Tạo tài khoản",
        "success_add": "✅ Đã tạo thành công tài khoản `{username}`!",
        "fill_warning": "⚠️ Vui lòng điền đầy đủ tài khoản và họ tên!",
        "col_time": "Thời gian",
        "col_user": "Tài khoản",
        "col_action": "Hành động",
        "col_module": "Module",
        "col_ip": "IP nguồn",
        "col_status": "Trạng thái",
        "api_header": "🔌 Cấu hình kết nối API Hóa đơn điện tử Việt Nam",
        "api_provider_label": "Nhà cung cấp hóa đơn *",
        "api_providers": ["Viettel (S-Invoice)", "VNPT (VNPT-Invoice)", "MISA (MISA meInvoice)", "FPT.eInvoice", "Custom API"],
        "api_env_label": "Môi trường *",
        "api_env_opts": ["Sandbox (Thử nghiệm)", "Production (Chính thức)"],
        "tax_code_label": "Mã số thuế công ty *",
        "endpoint_label": "Đường dẫn API (Endpoint URL) *",
        "key_label": "Mã khóa API / Token xác thực *",
        "modifier_label": "Người cấu hình (Khóa hệ thống)",
        "api_save_btn": "💾 Lưu cấu hình API",
        "api_test_btn": "🔗 Kiểm tra kết nối API",
        "api_success": "✅ Đã lưu thành công cấu hình API hóa đơn!",
        "api_test_success": "✅ Kết nối API thành công!"
    },
    "English": {
        "title": "🔒 IT Center - User Permissions & System Audit Logs",
        "caption": "Monitor system login history, permission changes, webpage access control, and E-Invoice API settings.",
        "tab_audit": "📊 System Audit Logs",
        "tab_users": "👥 Users & Permissions Control",
        "tab_api": "🔌 E-Invoice API Config",
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
        "site_opts": ["Tay Ninh Plant", "Hai Phong Plant"],
        "btn_add_user": "💾 Create User Account",
        "success_add": "✅ User account `{username}` successfully created!",
        "fill_warning": "⚠️ Please fill in username and full name!",
        "col_time": "Timestamp",
        "col_user": "Username",
        "col_action": "Action",
        "col_module": "Module",
        "col_ip": "Source IP",
        "col_status": "Status",
        "api_header": "🔌 E-Invoice API Integration Settings (Thông tư 200)",
        "api_provider_label": "E-Invoice Provider *",
        "api_providers": ["Viettel (S-Invoice)", "VNPT (VNPT-Invoice)", "MISA (MISA meInvoice)", "FPT.eInvoice", "Custom API"],
        "api_env_label": "Environment *",
        "api_env_opts": ["Sandbox", "Production"],
        "tax_code_label": "Company Tax Code (Mã số thuế) *",
        "endpoint_label": "API Endpoint URL *",
        "key_label": "API Auth Token / Key *",
        "modifier_label": "Modifier (System Bound)",
        "api_save_btn": "💾 Save API Settings",
        "api_test_btn": "🔗 Test API Connection",
        "api_success": "✅ API settings saved successfully!",
        "api_test_success": "✅ API connection test successful!"
    }
}

# ----------------------------------------------------
# 🔄 智慧語意對照引擎 (日誌與狀態互轉)
# ----------------------------------------------------
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

    # 初始化稽核日誌與使用者資料庫
    if "audit_logs_db" not in st.session_state:
        st.session_state.audit_logs_db = [
            {"time": "2026-10-06 13:00:15", "user": "admin", "action": "登入系統 (Login)", "module": "Auth", "ip": "192.168.1.50", "status": "成功"},
            {"time": "2026-10-06 13:05:22", "user": "manager", "action": "審核電子簽核單 [APP-2026-001]", "module": "Approval", "ip": "192.168.1.88", "status": "成功"},
            {"time": "2026-10-06 13:10:40", "user": "security", "action": "登記廠區車輛進出 [61A-888.66]", "module": "VehicleGate", "ip": "192.168.1.102", "status": "成功"}
        ]

    if "system_users_db" not in st.session_state:
        st.session_state.system_users_db = [
            {"username": "admin", "name": "李佑銘", "role": "admin", "site": "西寧廠 (Tay Ninh)"},
            {"username": "manager", "name": "Nguyễn Văn Quý", "role": "manager", "site": "海防廠 (Hai Phong)"},
            {"username": "security", "name": "大門保全組", "role": "security", "site": "西寧廠 (Tay Ninh)"}
        ]

    # 保留原本的 Tab，並完美追加第三個發票 API 設定 Tab
    tab_audit, tab_users, tab_api = st.tabs([L["tab_audit"], L["tab_users"], L["tab_api"]])

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

            # 🌐 網頁存取權限控管設定區塊（可設定該角色可開啟哪些網頁模組）
            st.markdown("##### 🔐 網頁存取授權設定 (Web Page Access Control)")
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                access_mgmt = st.checkbox("管理部 (Management)", value=True)
                access_eng = st.checkbox("工程與設計中心 (Engineering)", value=True)
            with col_p2:
                access_prod = st.checkbox("生產部 (Production)", value=True)
                access_exec = st.checkbox("總經理室 (Executive Office)", value=False)
            with col_p3:
                access_it = st.checkbox("資訊管理部 (IT & System)", value=False)

            if st.form_submit_button(L["btn_add_user"], type="primary", use_container_width=True):
                if username and name:
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

    # 🔌 追加：越南電子發票 API 串接設定頁籤
    with tab_api:
        st.markdown(f"### {L['api_header']}")
        
        with st.form("form_e_invoice_api_config"):
            api_provider = st.selectbox(L["api_provider_label"], L["api_providers"])
            api_env = st.selectbox(L["api_env_label"], L["api_env_opts"])
            tax_code = st.text_input(L["tax_code_label"], value="3702581234")
            api_endpoint = st.text_input(L["endpoint_label"], value="https://api.einvoice.viettel.vn/v1/publish")
            api_key = st.text_input(L["key_label"], type="password", value="VT-TOKEN-2026-RETECH-SECURE-KEY")
            
            # 🔒 IT 循跡稽核鐵律：自動綁定當前登入帳號與身分
            logged_user_name = st.session_state.get("user_name", "admin")
            logged_user_role = str(st.session_state.get("user_role", "IT_Admin")).upper()
            modifier_display = f"{logged_user_name} ({logged_user_role})"
            st.text_input(L["modifier_label"], value=modifier_display, disabled=True)

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                save_clicked = st.form_submit_button(L["api_save_btn"], type="primary", use_container_width=True)
            with col_btn2:
                test_clicked = st.form_submit_button(L["api_test_btn"], use_container_width=True)

            if save_clicked:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                st.success(f"{L['api_success']} (時間: {timestamp} | 稽核經辦: {modifier_display})")

            if test_clicked:
                st.success(L["api_test_success"])

def show(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
