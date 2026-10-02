import datetime
import os
import pandas as pd
import psycopg2
import streamlit as st

# 🌐 多語系字典 (i18n)
IT_I18N = {
    "繁體中文": {
        "page_title": "💻 資訊/IT 部門 — 權限與系統管理中心",
        "sub_title": "管理集團部門結構、全球廠區據點擴建，以及跨國 ERP 模組授權 (RBAC) 與全系統操作軌跡稽核",
        "tab_sites": "🏢 跨國廠區與子公司管理",
        "tab_users": "👥 人員帳號與網頁授權",
        "tab_rbac": "🔒 模組權限矩陣設定 (ACL)",
        "tab_audit": "📜 全系統操作軌跡與稽核 (Audit Trail)",
        # 廠區管理
        "site_sub_header": "🌐 全球廠區與海外子公司據點維護",
        "site_caption": "支援跨國企業動態擴張，隨時新增、修改或刪除海外新設廠房、研發中心或子公司",
        "sec_add_site": "➕ 新增海外廠房/分公司據點",
        "sec_edit_site": "✏️ 修改現有廠區據點資料",
        "sec_delete_site": "🗑️ 刪除/撤銷廠區據點",
        "lbl_site_id": "廠區代碼*",
        "lbl_site_name": "廠區/子公司名稱*",
        "lbl_country": "所在國家/區域*",
        "lbl_currency": "當地記帳本位幣*",
        "lbl_status": "廠區營運狀態",
        "btn_add_site": "💾 儲存並將新廠區加入集團戰情室",
        "btn_update_site": "💾 儲存修改內容",
        "btn_delete_site": "🗑️ 確定刪除此廠區據點",
        "exist_sites": "🌍 現有全球廠區據點一覽 (可直接在表格內雙擊修改)",
        "btn_save_table": "💾 儲存表格修改結果",
        "lbl_select_edit_site": "請選擇欲修改的廠區據點：",
        "lbl_select_del_site": "請選擇欲刪除的廠區據點：",
        "msg_site_added": "🎉 新廠區據點已成功建立！集團戰情室與 KPI 面板已同步更新連動。",
        "msg_site_updated": "✅ 已成功更新廠區據點資料！",
        "msg_site_deleted": "🗑️ 已成功刪除該廠區據點！",
        # 人員授權專區
        "user_auth_title": "👤 選擇人事建立之員工並開通系統授權",
        "lbl_select_emp": "選擇人事 (HR) 檔案建立之人員：",
        "lbl_username": "登入帳號 (Email 或 工號)*",
        "lbl_password": "登入密碼*",
        "lbl_dept": "歸屬部門 (由 HR 自動帶入)",
        "lbl_role": "系統權限角色 (Role)",
        "lbl_auth_modules": "🔓 可開啟之網頁/模組授權",
        "btn_save_user_auth": "🔑 儲存並開通/更新帳號權限",
        "table_users_title": "📋 目前全集團開通帳號與權限清單",
        "msg_user_auth_success": "✅ 已成功為人員設定系統登入權限與網頁授權！",
        # 矩陣專區
        "matrix_title": "🔒 全企業角色與跨模組 Access Control List (ACL) 存取控制矩陣",
        "matrix_caption": "可依照企業內部各部門職務角色設定細粒度模組存取權限，支援動態擴充角色欄位。",
        "sec_add_role": "➕ 新增自訂職務角色",
        "lbl_new_role_name": "新角色名稱 (例如: Quality Control 品保主管)",
        "btn_add_role": "➕ 新增角色至矩陣",
        "btn_save_acl": "💾 儲存權限矩陣設定",
        "msg_acl_saved": "✅ 已成功更新並生效全系統 ACL 模組權限矩陣！",
        "msg_role_added": "✅ 已成功新增系統角色欄位！",
    },
    "Tiếng Việt": {
        "page_title": "💻 Phòng IT - Quản lý Phân quyền & Hệ thống ERP",
        "sub_title": "Quản lý cơ cấu phòng ban, mở rộng nhà máy toàn cầu, phân quyền ERP (RBAC) và nhật ký thao tác.",
        "tab_sites": "🏢 Quản lý Nhà máy & Chi nhánh Quốc tế",
        "tab_users": "👥 Tài khoản & Phân quyền Trang Web",
        "tab_rbac": "🔒 Cấu hình Ma trận Phân quyền (ACL)",
        "tab_audit": "📜 Nhật ký Thao tác & Kiểm toán (Audit Trail)",
        # 廠區管理
        "site_sub_header": "🌐 Quản lý Chi nhánh & Nhà máy Toàn cầu",
        "site_caption": "Hỗ trợ mở rộng doanh nghiệp đa quốc gia, bạn có thể Thêm, Sửa hoặc Xóa nhà máy/chi nhánh mới bất kỳ lúc nào.",
        "sec_add_site": "➕ Thêm Nhà máy / Chi nhánh Mới",
        "sec_edit_site": "✏️ Chỉnh sửa Thông tin Nhà máy",
        "sec_delete_site": "🗑️ Xóa Nhà máy / Chi nhánh",
        "lbl_site_id": "Mã nhà máy*",
        "lbl_site_name": "Tên nhà máy / Chi nhánh*",
        "lbl_country": "Quốc gia / Khu vực*",
        "lbl_currency": "Tiền tệ chính*",
        "lbl_status": "Trạng thái hoạt động",
        "btn_add_site": "💾 Lưu và Tạo Chi nhánh Mới",
        "btn_update_site": "💾 Lưu Thay đổi",
        "btn_delete_site": "🗑 Xác nhận Xóa Nhà máy này",
        "exist_sites": "🌍 Danh sách Nhà máy Toàn cầu (Có thể nhấp đúp vào bảng để sửa trực tiếp)",
        "btn_save_table": "💾 Lưu Kết quả Sửa Bảng",
        "lbl_select_edit_site": "Chọn nhà máy cần chỉnh sửa:",
        "lbl_select_del_site": "Chọn nhà máy cần xóa:",
        "msg_site_added": "🎉 Đã thêm chi nhánh nhà máy mới thành công!",
        "msg_site_updated": "✅ Đã cập nhật thông tin nhà máy thành công!",
        "msg_site_deleted": "🗑️ Đã xóa chi nhánh nhà máy thành công!",
        # 人員授權專區
        "user_auth_title": "👤 Chọn Nhân viên từ Nhân sự (HR) để Cấp quyền",
        "lbl_select_emp": "Chọn nhân viên do HR đã tạo hồ sơ:",
        "lbl_username": "Tài khoản đăng nhập (Email/Mã NV)*",
        "lbl_password": "Mật khẩu đăng nhập*",
        "lbl_dept": "Phòng ban (Tự động tải từ HR)",
        "lbl_role": "Vai trò hệ thống (Role)",
        "lbl_auth_modules": "🔓 Các trang web / Module được phép truy cập",
        "btn_save_user_auth": "🔑 Lưu & Cấp quyền Phân quyền",
        "table_users_title": "📋 Danh sách Tài khoản & Phân quyền Hiện tại",
        "msg_user_auth_success": "✅ Đã cấp quyền đăng nhập thành công cho nhân viên!",
        # 矩陣專區
        "matrix_title": "🔒 Ma trận Phân quyền Truy cập (ACL) Theo Vai trò toàn Doanh nghiệp",
        "matrix_caption": "Cấu hình quyền truy cập module chi tiết theo vai trò phòng ban, hỗ trợ thêm vai trò mới động.",
        "sec_add_role": "➕ Thêm Vai trò / Chức danh Mới",
        "lbl_new_role_name": "Tên vai trò mới (Ví dụ: QC Manager - Quản lý Quản chất)",
        "btn_add_role": "➕ Thêm Vai trò vào Ma trận",
        "btn_save_acl": "💾 Lưu Cấu hình Ma trận Phân quyền",
        "msg_acl_saved": "✅ Đã cập nhật ma trận phân quyền ACL thành công!",
        "msg_role_added": "✅ Đã thêm vai trò mới thành công!",
    },
    "English": {
        "page_title": "💻 IT Dept - Permissions & System Management Center",
        "sub_title": "Manage organization structure, global plant sites, RBAC access matrix, and system audit trail logs.",
        "tab_sites": "🏢 Global Sites & Subsidiaries",
        "tab_users": "👥 Users & Web Authorization",
        "tab_rbac": "🔒 Access Control Matrix (ACL)",
        "tab_audit": "📜 System Audit Trail Logs",
        # 廠區管理
        "site_sub_header": "🌐 Global Sites & Overseas Subsidiaries Management",
        "site_caption": "Supports multinational expansion with full Add, Edit, and Delete capabilities for sites.",
        "sec_add_site": "➕ Add Overseas Plant / Subsidiary",
        "sec_edit_site": "✏️ Edit Existing Site Details",
        "sec_delete_site": "🗑️ Delete Site Location",
        "lbl_site_id": "Site ID*",
        "lbl_site_name": "Site / Subsidiary Name*",
        "lbl_country": "Country / Region*",
        "lbl_currency": "Base Currency*",
        "lbl_status": "Operating Status",
        "btn_add_site": "💾 Save & Add Site to Command Center",
        "btn_update_site": "💾 Save Changes",
        "btn_delete_site": "🗑️ Confirm Delete Site",
        "exist_sites": "🌍 Global Sites Overview (Double click cells to edit directly)",
        "btn_save_table": "💾 Save Table Edits",
        "lbl_select_edit_site": "Select site to edit:",
        "lbl_select_del_site": "Select site to delete:",
        "msg_site_added": "🎉 New site created successfully!",
        "msg_site_updated": "✅ Site details updated successfully!",
        "msg_site_deleted": "🗑️ Site deleted successfully!",
        # 人員授權專區
        "user_auth_title": "👤 Select Employee Created by HR & Grant Access",
        "lbl_select_emp": "Select employee profile from HR records:",
        "lbl_username": "Login Account (Email / Staff ID)*",
        "lbl_password": "Login Password*",
        "lbl_dept": "Department (Auto-filled from HR)",
        "lbl_role": "System Permission Role",
        "lbl_auth_modules": "🔓 Authorized Pages / Modules",
        "btn_save_user_auth": "🔑 Save & Grant Permissions",
        "table_users_title": "📋 Authorized System Users & Access List",
        "msg_user_auth_success": "✅ User permissions saved and granted successfully!",
        # 矩陣專區
        "matrix_title": "🔒 Enterprise Access Control List (ACL) Permissions Matrix",
        "matrix_caption": "Configure fine-grained module permissions per department role with dynamic role creation.",
        "sec_add_role": "➕ Add Custom Role",
        "lbl_new_role_name": "New Role Title (e.g. Quality Control Supervisor)",
        "btn_add_role": "➕ Add Role to Matrix",
        "btn_save_acl": "💾 Save Access Matrix Settings",
        "msg_acl_saved": "✅ ACL Permissions matrix saved and applied successfully!",
        "msg_role_added": "✅ New role added to matrix successfully!",
    },
}


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "global_erp"),
        user=os.getenv("DB_USER", "erp_user"),
        password=os.getenv("DB_PASSWORD", "your_password"),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "5432"),
    )


def render_user_management_page(*args, **kwargs):
    # 自動偵測多語系
    lang = (
        kwargs.get("lang")
        or kwargs.get("curr_lang")
        or st.session_state.get("current_lang", "繁體中文")
    )
    L = IT_I18N.get(lang, IT_I18N["繁體中文"])

    st.title(L["page_title"])
    st.caption(L["sub_title"])

    # ----------------------------------------------------
    # 🗄️️ 1. 初始化 Session State
    # ----------------------------------------------------
    if "system_audit_logs" not in st.session_state:
        st.session_state.system_audit_logs = [
            {
                "log_id": "AUD-20260927-001",
                "timestamp": "2026-09-27 14:32:10",
                "year": "2026",
                "month": "09",
                "day": "27",
                "operator": "admin (Alex Chen)",
                "dept_module": "💻 資訊/IT",
                "action_type": "🔑 權限變更",
                "target": "ga_user (李總務)",
                "detail": "開通 [🏢 總務與倉儲] 模組編輯權限",
                "status": "🟢 正常",
            }
        ]

    if "system_users_db" not in st.session_state:
        st.session_state.system_users_db = [
            {
                "id": "EMP-001",
                "username": "admin@reetech.com",
                "name": "張董事長",
                "dept": "經營高層 / 董事會",
                "title": "董事長 (Chairman)",
                "role": "Executive",
                "auth_modules": "全系統 (All Modules)",
            },
            {
                "id": "EMP-002",
                "username": "nguyen.a@reetech.com",
                "name": "Nguyễn Văn A",
                "dept": "工程部",
                "title": "Kỹ sư Tủ điện",
                "role": "Engineer",
                "auth_modules": "研發/技術, 倉儲管理",
            },
        ]

    # 初始化專業級 ACL 矩陣資料表
    if "acl_matrix_db" not in st.session_state:
        st.session_state.acl_matrix_db = pd.DataFrame({
            "系統模組與功能頁面": [
                "📈 營運戰情室 (Executive Dashboard)",
                "💼 業務/報價/AR (Sales & Billing)",
                "🛠️ 研發/工程估價 (R&D & BOM)",
                "🛒 採購/外協/AP (Procurement)",
                "📦 倉儲/領料/盤點 (Warehouse)",
                "🧾 財務/會計/成本 (Finance & Tax)",
                "👥 人事/假勤/薪酬 (HR & Payroll)",
                "💻 資訊/IT/權限 (IT Administration)",
            ],
            "Admin (系統管理)": [
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
            ],
            "Executive (高層/董事會)": [
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                False,
            ],
            "Sales (業務/行銷)": [
                False,
                True,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "Engineer (研發/工程)": [
                False,
                False,
                True,
                False,
                True,
                False,
                False,
                False,
            ],
            "Buyer (採購/外協)": [
                False,
                False,
                False,
                True,
                True,
                False,
                False,
                False,
            ],
            "Warehouse (倉儲/物流)": [
                False,
                False,
                False,
                False,
                True,
                False,
                False,
                False,
            ],
            "Accountant (財務/會計)": [
                False,
                True,
                False,
                True,
                False,
                True,
                False,
                False,
            ],
            "HR (人事/行政)": [
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                False,
            ],
            "Operator (現場作業員)": [
                False,
                False,
                False,
                False,
                True,
                False,
                False,
                False,
            ],
        })

    tabs = st.tabs(
        [L["tab_sites"], L["tab_users"], L["tab_rbac"], L["tab_audit"]]
    )

    # ----------------------------------------------------
    # TAB 1: 跨國廠區與子公司動態管理
    # ----------------------------------------------------
    with tabs[0]:
        st.subheader(L["site_sub_header"])
        st.caption(L["site_caption"])

        if "factory_list" not in st.session_state:
            st.session_state.factory_list = [
                {
                    "id": "FACT-TW-01",
                    "name": "🇹🇼 台灣總部研發中心",
                    "country": "台灣",
                    "currency": "TWD",
                    "revenue": "NT$ 12.5M",
                    "status": "🟢 營運中",
                },
                {
                    "id": "FACT-DG-01",
                    "name": "🇨🇳 東莞一廠 (橡膠/塑膠)",
                    "country": "中國",
                    "currency": "RMB",
                    "revenue": "¥ 3.4M",
                    "status": "🟢 營運中",
                },
                {
                    "id": "FACT-BH-01",
                    "name": "🇻🇳 越南平陽/西寧廠 (配電盤/板金)",
                    "country": "越南",
                    "currency": "VND",
                    "revenue": "₫ 12.8B",
                    "status": "🟢 營運中",
                },
            ]

        with st.expander(L["sec_add_site"], expanded=True):
            with st.form("add_factory_form", clear_on_submit=True):
                col_a1, col_a2 = st.columns(2)
                f_id = col_a1.text_input(
                    L["lbl_site_id"], placeholder="例如: FACT-ID-01 (印尼廠)"
                )
                f_name = col_a2.text_input(
                    L["lbl_site_name"], placeholder="例如: 🇮🇩 印尼爪哇新廠"
                )

                col_a3, col_a4, col_a5 = st.columns(3)
                f_country = col_a3.text_input(
                    L["lbl_country"], placeholder="例如: 印尼 (Indonesia)"
                )
                f_currency = col_a4.selectbox(
                    L["lbl_currency"],
                    ["USD", "VND", "TWD", "RMB", "IDR", "MXN", "EUR"],
                )
                f_status = col_a5.selectbox(
                    L["lbl_status"],
                    ["🟢 營運中", "🏗️ 建廠/試產中", "🟡 規劃中"],
                )

                if st.form_submit_button(L["btn_add_site"]):
                    if not f_id or not f_name:
                        st.warning("請輸入廠區代碼與名稱！")
                    else:
                        st.session_state.factory_list.append({
                            "id": f_id,
                            "name": f_name,
                            "country": f_country,
                            "currency": f_currency,
                            "revenue": "$0.00",
                            "status": f_status,
                        })
                        st.success(L["msg_site_added"])
                        st.rerun()

        st.divider()
        st.markdown(f"#### {L['exist_sites']}")
        df_factories = pd.DataFrame(st.session_state.factory_list)
        edited_factories = st.data_editor(
            df_factories,
            use_container_width=True,
            num_rows="dynamic",
            key="factories_editor",
        )

        if st.button(L["btn_save_table"]):
            st.session_state.factory_list = edited_factories.to_dict("records")
            st.success(L["msg_site_updated"])
            st.rerun()

    # ----------------------------------------------------
    # TAB 2: 人員帳號與網頁授權（連動 HR 人事資料）
    # ----------------------------------------------------
    with tabs[1]:
        st.subheader(L["user_auth_title"])
        col_form, col_list = st.columns([1.1, 1])

        hr_employees = st.session_state.get("employees_db", [])
        emp_options_map = {}
        if hr_employees:
            for emp in hr_employees:
                label = f"{emp.get('id', '')} - {emp.get('name', '')} ({emp.get('dept', '')} / {emp.get('title', '')})"
                emp_options_map[label] = emp
        else:
            emp_options_map["EMP-001 - 張董事長 (經營高層 / 董事長)"] = {
                "id": "EMP-001",
                "name": "張董事長",
                "dept": "經營高層",
                "title": "董事長",
            }

        with col_form:
            st.markdown(f"#### ➕ 開通/維護帳號與網頁權限")
            selected_emp_label = st.selectbox(
                L["lbl_select_emp"], list(emp_options_map.keys())
            )
            selected_emp_data = emp_options_map[selected_emp_label]

            with st.form("auth_user_form", clear_on_submit=False):
                col_u1, col_u2 = st.columns(2)
                u_name = col_u1.text_input(
                    "員工姓名 (HR 帶入)",
                    value=selected_emp_data.get("name", ""),
                    disabled=True,
                )
                u_dept = col_u2.text_input(
                    L["lbl_dept"],
                    value=selected_emp_data.get("dept", ""),
                    disabled=True,
                )

                col_u3, col_u4 = st.columns(2)
                u_account = col_u3.text_input(
                    L["lbl_username"],
                    value=f"{selected_emp_data.get('id', '').lower()}@reetech.com",
                )
                u_password = col_u4.text_input(
                    L["lbl_password"], value="123456", type="password"
                )

                # 讀取動態角色欄位
                role_columns = [
                    col
                    for col in st.session_state.acl_matrix_db.columns
                    if col != "系統模組與功能頁面"
                ]
                u_role = st.selectbox(L["lbl_role"], role_columns)

                st.markdown(f"**{L['lbl_auth_modules']}**")
                c_m1, c_m2 = st.columns(2)
                auth_exec = c_m1.checkbox("📈 營運戰情室 (Executive)", value=True)
                auth_sales = c_m1.checkbox(
                    "💼 業務/應收帳款 (Sales & AR)", value=True
                )
                auth_eng = c_m1.checkbox(
                    "🛠️ 研發/工程估價 (R&D & Engineering)", value=True
                )
                auth_proc = c_m2.checkbox(
                    "🛒 採購與應付帳款 (Procurement & AP)", value=False
                )
                auth_hr = c_m2.checkbox("👥 人力資源 (HR & Admin)", value=False)
                auth_it = c_m2.checkbox("💻 資訊/IT 管理 (IT Admin)", value=False)

                submit_user = st.form_submit_button(L["btn_save_user_auth"])
                if submit_user:
                    selected_mods = []
                    if auth_exec:
                        selected_mods.append("營運戰情")
                    if auth_sales:
                        selected_mods.append("銷售/AR")
                    if auth_eng:
                        selected_mods.append("工程估價")
                    if auth_proc:
                        selected_mods.append("採購/AP")
                    if auth_hr:
                        selected_mods.append("人事")
                    if auth_it:
                        selected_mods.append("IT")

                    user_entry = {
                        "id": selected_emp_data.get("id", "EMP-000"),
                        "username": u_account,
                        "name": selected_emp_data.get("name", ""),
                        "dept": selected_emp_data.get("dept", ""),
                        "title": selected_emp_data.get("title", ""),
                        "role": u_role,
                        "auth_modules": ", ".join(selected_mods)
                        if selected_mods
                        else "無權限",
                    }

                    st.session_state.system_users_db = [
                        u
                        for u in st.session_state.system_users_db
                        if u["id"] != user_entry["id"]
                    ]
                    st.session_state.system_users_db.append(user_entry)

                    now_dt = datetime.datetime.now()
                    st.session_state.system_audit_logs.append({
                        "log_id": "AUD-" + now_dt.strftime("%Y%m%d-%H%M%S"),
                        "timestamp": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "year": str(now_dt.year),
                        "month": str(now_dt.month).zfill(2),
                        "day": str(now_dt.day).zfill(2),
                        "operator": "IT Admin",
                        "dept_module": "💻 資訊/IT",
                        "action_type": "🔑 帳號授權開通",
                        "target": f"{user_entry['name']} ({u_account})",
                        "detail": f"部門: {user_entry['dept']} | 角色: {user_entry['role']} | 開通模組: {user_entry['auth_modules']}",
                        "status": "🟢 正常",
                    })

                    st.success(L["msg_user_auth_success"])
                    st.rerun()

        with col_list:
            st.markdown(f"#### {L['table_users_title']}")
            st.dataframe(
                pd.DataFrame(st.session_state.system_users_db),
                use_container_width=True,
            )

    # ----------------------------------------------------
    # TAB 3: 模組權限矩陣設定 (ACL 升級版 - 製造業完整角色 + 動態新增)
    # ----------------------------------------------------
    with tabs[2]:
        st.subheader(L["matrix_title"])
        st.caption(L["matrix_caption"])

        # 1. 動態新增新角色欄位區塊
        with st.expander(L["sec_add_role"], expanded=False):
            c_r1, c_r2 = st.columns([3, 1])
            new_role_title = c_r1.text_input(
                L["lbl_new_role_name"], key="add_role_title"
            )
            if c_r2.button(L["btn_add_role"], type="primary"):
                if (
                    new_role_title
                    and new_role_title not in st.session_state.acl_matrix_db.columns
                ):
                    st.session_state.acl_matrix_db[new_role_title] = False
                    st.success(L["msg_role_added"])
                    st.rerun()
                elif new_role_title in st.session_state.acl_matrix_db.columns:
                    st.warning("⚠️️ 該角色已存在於權限矩陣中！")

        st.divider()

        # 2. 可互動勾選編輯之完整權限矩陣表格
        edited_acl = st.data_editor(
            st.session_state.acl_matrix_db,
            use_container_width=True,
            key="acl_editor_table",
        )

        if st.button(L["btn_save_acl"], type="primary"):
            st.session_state.acl_matrix_db = edited_acl
            now_dt = datetime.datetime.now()
            st.session_state.system_audit_logs.append({
                "log_id": "AUD-" + now_dt.strftime("%Y%m%d-%H%M%S"),
                "timestamp": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "year": str(now_dt.year),
                "month": str(now_dt.month).zfill(2),
                "day": str(now_dt.day).zfill(2),
                "operator": "IT Admin",
                "dept_module": "💻 資訊/IT",
                "action_type": "🔒 ACL 權限矩陣更新",
                "target": "全系統 Access Control Matrix",
                "detail": "系統管理員修改並更新了角色與模組存取矩陣設定",
                "status": "🟢 正常",
            })
            st.success(L["msg_acl_saved"])
            st.rerun()

    # ----------------------------------------------------
    # TAB 4: 📜 全系統操作軌跡與稽核中心
    # ----------------------------------------------------
    with tabs[3]:
        st.subheader("📜 系統操作與異動歷史紀錄 (System Audit Logs)")
        st.caption(
            "即時追蹤與稽核全系統跨模組操作軌跡，支援依「年、月、日」分類篩選與全文關鍵字搜尋。"
        )

        logs_data = st.session_state.system_audit_logs

        st.markdown("##### 🔎 紀錄搜尋與日期時間分類過濾")
        col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1, 1, 1])

        with col_f1:
            search_kw = (
                st.text_input(
                    "🔍 關鍵字搜尋 (帳號/動作/品項/備註)：",
                    "",
                    key="audit_kw_search",
                )
                .strip()
                .lower()
            )

        available_years = sorted(
            list({str(l["year"]) for l in logs_data}), reverse=True
        )
        with col_f2:
            selected_year = st.selectbox(
                "📅 選擇年份 (Year)", ["全部年份 (All)"] + available_years
            )

        months_list = ["全部月份 (All)"] + [
            str(i).zfill(2) for i in range(1, 13)
        ]
        with col_f3:
            selected_month = st.selectbox(
                "📆 選擇月份 (Month)", months_list
            )

        with col_f4:
            selected_module = st.selectbox(
                "🏢 篩選系統模組",
                [
                    "全部模組 (All)",
                    "📦 倉儲管理",
                    "👥 人事/行政",
                    "🧾 財務管理",
                    "💻 資訊/IT",
                    "💼 業務/行銷",
                ],
            )

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            use_exact_date = st.checkbox(
                "🎯 啟用特定單日精確過濾 (Specific Day Filter)", value=False
            )
        with col_d2:
            exact_date_val = st.date_input(
                "選擇特定年月日",
                value=datetime.date(2026, 9, 27),
                disabled=not use_exact_date,
            )

        st.markdown("---")

        filtered_logs = []
        for log in logs_data:
            match_kw = True
            if search_kw:
                combined_text = (
                    str(log["log_id"])
                    + " "
                    + str(log["operator"])
                    + " "
                    + str(log["dept_module"])
                    + " "
                    + str(log["action_type"])
                    + " "
                    + str(log["target"])
                    + " "
                    + str(log["detail"])
                ).lower()
                match_kw = search_kw in combined_text

            match_year = (
                selected_year == "全部年份 (All)"
                or str(log["year"]) == selected_year
            )
            match_month = (
                selected_month == "全部月份 (All)"
                or str(log["month"]) == selected_month
            )
            match_module = (
                selected_module == "全部模組 (All)"
                or log["dept_module"] == selected_module
            )

            match_exact_date = True
            if use_exact_date:
                match_exact_date = (
                    str(log["year"]) == str(exact_date_val.year)
                    and str(log["month"]).zfill(2)
                    == str(exact_date_val.month).zfill(2)
                    and str(log["day"]).zfill(2)
                    == str(exact_date_val.day).zfill(2)
                )

            if (
                match_kw
                and match_year
                and match_month
                and match_module
                and match_exact_date
            ):
                filtered_logs.append({
                    "紀錄編號": log["log_id"],
                    "時間 (YYYY-MM-DD HH:MM:SS)": log["timestamp"],
                    "年份": log["year"],
                    "月份": log["month"] + "月",
                    "日期": log["day"] + "日",
                    "操作人員 (User)": log["operator"],
                    "系統模組": log["dept_module"],
                    "動作類型": log["action_type"],
                    "操作對象/標的": log["target"],
                    "詳細內容與備註": log["detail"],
                    "狀態": log.get("status", "🟢 正常"),
                })

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("📜 總記錄筆數", str(len(logs_data)) + " 筆")
        col_m2.metric("🔍 符合條件紀錄", str(len(filtered_logs)) + " 筆")
        col_m3.metric(
            "🚨 警示與異動事件",
            str(len([l for l in filtered_logs if "🚨" in l["狀態"]]))
            + " 筆",
        )

        if filtered_logs:
            df_display = pd.DataFrame(filtered_logs)
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info(
                "💡 查無符合目前日期（年/月/日）或關鍵字條件的操作紀錄。"
            )


def show(*args, **kwargs):
    render_user_management_page(*args, **kwargs)


def main(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
