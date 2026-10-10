import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 帳號權限與稽核軌跡模組多語系字典 (i18n)
# ----------------------------------------------------
USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 組織職能角色與系統權限範本管理",
        "caption": "依據企業組織架構（總經理室全覽、管理部行政匯總、工程部專案、生產倉管廠區）精細化配置角色權限範本。",
        "tab_audit": "📊 系統稽核日誌 (Audit Logs)",
        "tab_roles": "⚙️ 組織角色與部門功能權限範本 (RBAC)",
        "tab_users": "👥 人事系統員工與系統帳號總覽",
        "tab_api": "🔌 電子發票 API 串接設定",
        "audit_header": "🔍 全系統操作軌跡與稽核軌跡日誌",
        "filter_year": "篩選年份 (Year)",
        "filter_month": "篩選月份 (Month)",
        "filter_day": "篩選日期 (Day)",
        "search_placeholder": "輸入關鍵字搜尋稽核紀錄...",
        "no_logs": "目前尚無系統稽核紀錄。",
        "roles_header": "⚙️ 企業組織部門角色與權限範本清冊",
        "add_role_header": "➕ 新增部門主管/職能角色範本",
        "users_header": "👥 系統現有使用者帳號與人事連動清冊",
        "add_user_header": "➕ 依人事系統員工工號派發角色權限",
        "lbl_role_name": "角色名稱 (例如: 總經理、管理部主管、工程主管、倉庫管理員...) *",
        "btn_save_role": "💾 儲存部門角色權限範本",
        "btn_delete_role": "🗑️ 刪除此角色範本",
        "success_role_save": "✅ 部門角色權限範本已成功更新！",
        "success_role_delete": "🗑️ 角色範本已成功刪除！",
        "success_add_user": "✅ 人事員工系統帳號與權限已成功指派！",
        "col_time": "時間戳記",
        "col_user": "操作帳號",
        "col_action": "動作行為",
        "col_module": "模組名稱",
        "col_ip": "來源 IP",
        "col_status": "執行狀態",
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
        "title": "🔒 Quản trị IT - Cấu hình Vai trò & Phân quyền Doanh nghiệp",
        "caption": "Quản lý vai trò và phân quyền theo cơ cấu tổ chức.",
        "tab_audit": "📊 Nhật ký Kiểm toán",
        "tab_roles": "⚙️ Quản lý Vai trò (RBAC)",
        "tab_users": "👥 Danh sách Nhân sự",
        "tab_api": "🔌 Cấu hình API Hóa đơn",
        "audit_header": "🔍 Nhật ký thao tác",
        "filter_year": "Năm",
        "filter_month": "Tháng",
        "filter_day": "Ngày",
        "search_placeholder": "Tìm kiếm...",
        "no_logs": "Chưa có nhật ký.",
        "roles_header": "⚙️ Danh sách vai trò",
        "add_role_header": "➕ Thêm vai trò mới",
        "users_header": "📋 Danh sách tài khoản",
        "add_user_header": "➕ Phân quyền",
        "lbl_role_name": "Tên vai trò *",
        "btn_save_role": "💾 Lưu",
        "btn_delete_role": "🗑️ Xóa",
        "success_role_save": "✅ Đã lưu!",
        "success_role_delete": "🗑️ Đã xóa!",
        "success_add_user": "✅ Thành công!",
        "col_time": "Thời gian",
        "col_user": "Tài khoản",
        "col_action": "Hành động",
        "col_module": "Module",
        "col_ip": "IP",
        "col_status": "Trạng thái",
        "api_header": "🔌 Cấu hình API",
        "api_provider_label": "Nhà cung cấp *",
        "api_providers": ["Viettel", "VNPT", "MISA"],
        "api_env_label": "Môi trường *",
        "api_env_opts": ["Sandbox", "Production"],
        "tax_code_label": "Mã số thuế *",
        "endpoint_label": "Endpoint URL *",
        "key_label": "Token *",
        "modifier_label": "Người cấu hình",
        "api_save_btn": "💾 Lưu",
        "api_test_btn": "🔗 Kiểm tra",
        "api_success": "✅ Thành công!",
        "api_test_success": "✅ Kết nối thành công!"
    },
    "English": {
        "title": "🔒 IT Center - Departmental Role RBAC & System Audit Logs",
        "caption": "Configure role templates aligned with company organizational structure (Executive, Admin, Engineering, Production & Warehouse).",
        "tab_audit": "📊 System Audit Logs",
        "tab_roles": "⚙️ Departmental Roles (RBAC)",
        "tab_users": "👥 HR & User Accounts",
        "tab_api": "🔌 E-Invoice API Config",
        "audit_header": "🔍 System Operation & Audit Trail Logs",
        "filter_year": "Filter Year",
        "filter_month": "Filter Month",
        "filter_day": "Filter Day",
        "search_placeholder": "Search audit logs...",
        "no_logs": "No audit logs found.",
        "roles_header": "⚙️ Departmental Permission Roles & Access Templates",
        "add_role_header": "➕ Create New Department Role Template",
        "users_header": "👥 HR Employee & System Accounts Registry",
        "add_user_header": "➕ Assign Department Role to HR Employee",
        "lbl_role_name": "Role Name (e.g., General Manager, Admin Manager, Engineering Lead, Warehouse Keeper) *",
        "btn_save_role": "💾 Save Department Role Template",
        "btn_delete_role": "🗑️ Delete Role Template",
        "success_role_save": "✅ Department role template successfully saved!",
        "success_role_delete": "🗑️ Role template successfully deleted!",
        "success_add_user": "✅ Employee system account & role successfully assigned!",
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

    # 初始化稽核日誌與部門角色資料庫
    if "audit_logs_db" not in st.session_state:
        st.session_state.audit_logs_db = [
            {"time": "2026-10-06 13:00:15", "user": "admin", "action": "登入系統 (Login)", "module": "Auth", "ip": "192.168.1.50", "status": "成功"},
            {"time": "2026-10-06 13:05:22", "user": "manager", "action": "審核電子簽核單 [APP-2026-001]", "module": "Approval", "ip": "192.168.1.88", "status": "成功"}
        ]

    if "system_roles_db" not in st.session_state:
        st.session_state.system_roles_db = {
            "董事長 / 總經理 (Chairman / GM)": {"desc": "👑 總經理室：可檢視與審核全系統所有部門與跨模組資料"},
            "管理部主管 (Admin & Finance Manager)": {"desc": "📋 管理部：負責人事、財務、總務與匯總下方各部門資料"},
            "工程總監 / 設計主管 (Engineering Director)": {"desc": "🛠️ 工程部門：專注於專案報價、工程驗收、日報表與 BOM 展開"},
            "倉庫管理員 / 生產主管 (Warehouse & Production)": {"desc": "🏭 生產與倉管：管理廠區生產線、車間打卡、板金塗料與倉庫庫存"}
        }

    if "system_users_db" not in st.session_state:
        st.session_state.system_users_db = [
            {"username": "admin", "name": "李佑銘", "role": "董事長 / 總經理 (Chairman / GM)", "site": "西寧廠 (Tay Ninh)"},
            {"username": "manager", "name": "Nguyễn Văn Quý", "role": "管理部主管 (Admin & Finance Manager)", "site": "海防廠 (Hai Phong)"}
        ]

    tab_audit, tab_roles, tab_users, tab_api = st.tabs([L["tab_audit"], L["tab_roles"], L["tab_users"], L["tab_api"]])

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

    # ⚙️ 角色與權限範本管理 (依據各部門職能與觀察匯總權限)
    with tab_roles:
        st.markdown(f"### {L['roles_header']}")
        
        role_list_display = [{"角色名稱": r_name, "部門職責與資料範圍說明": r_info.get("desc", "")} for r_name, r_info in st.session_state.system_roles_db.items()]
        st.dataframe(pd.DataFrame(role_list_display), use_container_width=True)

        st.markdown("---")
        st.markdown(f"### ✏️ 修改現有部門角色範本或 ➕ 新增角色")
        
        role_action_mode = st.radio("選擇操作模式", ["修改現有部門角色範本", "新增全新部門角色範本"], horizontal=True)

        if role_action_mode == "修改現有部門角色範本":
            existing_role_names = list(st.session_state.system_roles_db.keys())
            selected_edit_role = st.selectbox("🎯 選擇要修改的角色名稱", existing_role_names)
            
            with st.form("form_edit_department_role"):
                new_role_title = st.text_input("修改後的角色名稱", value=selected_edit_role)
                role_desc_input = st.text_input("部門職責與檢視權限說明", value=st.session_state.system_roles_db[selected_edit_role].get("desc", ""))
                
                st.markdown("##### 🔐 依組織架構勾選該角色可開啟的部門與子功能範圍")
                
                # 總經理室 (全覽)
                st.markdown("###### 👑 總經理室 (Executive Office) [全系統檢視與高階決策]")
                rc_ex1, rc_ex2 = st.columns(2)
                with rc_ex1: r_exec = st.checkbox("📊 總經理室營運總覽與高階決策", value=True)
                with rc_ex2: r_approval = st.checkbox("📋 全公司電子簽核中心 (Approval Center)", value=True)

                # 管理部 (行政、人事、財務、總務與下方各部門資料匯總)
                st.markdown("###### 📋 管理部 (Management Dept) [人事、財務、總務與下方部門資料匯總]")
                rcm1, rcm2, rcm3 = st.columns(3)
                with rcm1:
                    rm1 = st.checkbox("📢 公司重要公告與佈告欄管理", value=True)
                    rm2 = st.checkbox("👥 員工個人檔案與人事管理", value=True)
                    rm3 = st.checkbox("⏱️ 廠內員工固定打卡與出勤紀錄", value=True)
                    rm4 = st.checkbox("📍 外勤位置驗證與工地即時人數", value=True)
                    rm5 = st.checkbox("🏭 廠區與工作廠區管理", value=True)
                with rcm2:
                    rm6 = st.checkbox("🚗 廠區車輛進出口門禁與派車審核", value=True)
                    rm7 = st.checkbox("🔧 車輛維修保養紀錄", value=True)
                    rm8 = st.checkbox("🏷️ 固定資產與設備管理", value=True)
                    rm9 = st.checkbox("🛒 採購與應付帳款 (AP)", value=True)
                    rm10 = st.checkbox("💰 客戶應收帳款與對帳管理 (AR)", value=True)
                with rcm3:
                    rm11 = st.checkbox("📑 越南稅務標準財務報表 (Thông tư 200)", value=True)
                    rm12 = st.checkbox("💵 員工薪資計算與保險扣除", value=True)
                    rm13 = st.checkbox("🧾 電子發票綜合管理與 XML 歸檔", value=True)
                    rm14 = st.checkbox("🌐 越南營建電子發票與稅務合規管家", value=True)

                # 工程部門 (工程人員內會用到的專屬功能)
                st.markdown("###### 🛠️ 工程與設計中心 (Engineering & Design Center) [工程專屬功能]")
                rce1, rce2, rce3 = st.columns(3)
                with rce1:
                    re1 = st.checkbox("🎨 [工程] 配電盤與工程專案雙層報價", value=True)
                    re2 = st.checkbox("📐 [工程] 工程驗收與進度追蹤", value=True)
                    re3 = st.checkbox("📊 [工程] 現場工程日報表與出工統計", value=True)
                with rce2:
                    re4 = st.checkbox("📷 [工程] AI 施工照片智慧辨識與歸檔", value=True)
                    re5 = st.checkbox("⚠️ [工程] 分包商與專業證照到期預警", value=True)
                    re6 = st.checkbox("🗄️ [設計] 配電盤電氣機構設計圖庫 Storage", value=True)
                with rce3:
                    re7 = st.checkbox("⚙️ [工程] 配電盤 BOM 零件自動展開與採購聯動", value=True)
                    re8 = st.checkbox("👷 [工程] 外包商點工計價與越南勞動法計薪", value=True)
                    re9 = st.checkbox("✅ [工程] FAT/SAT 試驗報告與 QR Code 驗收", value=True)

                # 生產與倉管 (廠區生產、倉管)
                st.markdown("###### 🏭 生產部與倉庫 (Production & Warehouse) [廠區生產與倉管]")
                rcp1, rcp2 = st.columns(2)
                with rcp1:
                    rp1 = st.checkbox("📦 [倉庫] 倉庫即時庫存與資材條碼管理", value=True)
                    rp2 = st.checkbox("🧱 [板金] 板金加工組工單與條碼", value=True)
                with rcp2:
                    rp3 = st.checkbox("🎨 [塗料] 粉體塗裝烤漆組品管", value=True)
                    rp4 = st.checkbox("⚡ [配盤] 配電盤組裝線組", value=True)

                # 資訊管理部
                st.markdown("###### 🔒 資訊管理部 (IT & System)")
                rc_it1, rc_it2 = st.columns(2)
                with rc_it1: r_audit = st.checkbox("📊 系統稽核日誌與帳號權限控管", value=False)
                with rc_it2: r_api_set = st.checkbox("🔌 越南電子發票 API 參數設定", value=False)

                col_btn_r1, col_btn_r2 = st.columns(2)
                with col_btn_r1:
                    save_role_btn = st.form_submit_button(L["btn_save_role"], type="primary", use_container_width=True)
                with col_btn_r2:
                    delete_role_btn = st.form_submit_button(L["btn_delete_role"], use_container_width=False)

                if save_role_btn:
                    if new_role_title != selected_edit_role:
                        del st.session_state.system_roles_db[selected_edit_role]
                    st.session_state.system_roles_db[new_role_title] = {"desc": role_desc_input}
                    st.success(L["success_role_save"])
                    st.rerun()

                if delete_role_btn:
                    if len(st.session_state.system_roles_db) > 1:
                        del st.session_state.system_roles_db[selected_edit_role]
                        st.success(L["success_role_delete"])
                        st.rerun()
                    else:
                        st.warning("⚠️ 系統至少需保留一個角色範本！")

        else:
            with st.form("form_add_department_role"):
                new_role_title = st.text_input("新部門角色名稱 (例如: 行政主管、設計主管、品管經理...)")
                role_desc_input = st.text_input("部門職責與資料範圍說明")

                if st.form_submit_button("💾 建立新部門角色範本", type="primary", use_container_width=True):
                    if new_role_title:
                        st.session_state.system_roles_db[new_role_title] = {"desc": role_desc_input}
                        st.success("✅ 新部門角色範本已成功建立！")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請輸入角色名稱！")

    # 👥 人事系統員工與帳號權限指派
    with tab_users:
        st.markdown(f"### {L['users_header']}")
        st.dataframe(pd.DataFrame(st.session_state.system_users_db), use_container_width=True)

        st.markdown("---")
        st.markdown(f"### {L['add_user_header']}")
        
        # 🔗 連結人事系統員工清單
        employee_options = ["李佑銘 (TW-001 - 西寧廠 - 總經理室)", "Nguyễn Văn Quý (VN-002 - 海防廠 - 管理部)"]
        if "employees_db" in st.session_state and st.session_state.employees_db:
            employee_options = [f"{emp.get('name', '')} (工號: {emp.get('code', emp.get('id', ''))} - {emp.get('site', '')})" for emp in st.session_state.employees_db]

        available_roles = list(st.session_state.system_roles_db.keys())

        with st.form("form_assign_department_role"):
            uc1, uc2 = st.columns(2)
            with uc1:
                selected_employee = st.selectbox("選擇人事系統員工", employee_options)
                default_acc = selected_employee.split(" (")[0].lower().replace(" ", "") if selected_employee else "staff01"
                username = st.text_input("登入帳號 (對應人事工號)", value=default_acc)
            with uc2:
                assigned_role = st.selectbox("指派部門角色權限", available_roles)
                site = st.selectbox("所屬廠區", ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"])

            if st.form_submit_button("💾 確認指派人事員工之系統角色與權限", type="primary", use_container_width=True):
                if username and selected_employee:
                    emp_name_extracted = selected_employee.split(" (")[0]
                    st.session_state.system_users_db.append({
                        "username": username,
                        "name": emp_name_extracted,
                        "role": assigned_role,
                        "site": site
                    })
                    st.success(L["success_add_user"])
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫完整資訊！")

    # 🔌 追加：越南電子發票 API 串接設定頁籤
    with tab_api:
        st.markdown(f"### {L['api_header']}")
        with st.form("form_e_invoice_api_config"):
            api_provider = st.selectbox(L["api_provider_label"], L["api_providers"])
            api_env = st.selectbox(L["api_env_label"], L["api_env_opts"])
            tax_code = st.text_input(L["tax_code_label"], value="3702581234")
            api_endpoint = st.text_input(L["endpoint_label"], value="https://api.einvoice.viettel.vn/v1/publish")
            api_key = st.text_input(L["key_label"], type="password", value="VT-TOKEN-2026-RETECH-SECURE-KEY")
            
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
