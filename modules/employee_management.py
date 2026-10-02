import pandas as pd
import streamlit as st

# 🌐 人事管理多語系字典 (i18n)
EMP_I18N = {
    "繁體中文": {
        "page_title": "👥 跨國員工檔案與人事管理",
        "tab_profiles": "👤 跨國員工檔案管理",
        "tab_leave": "🌴 請假系統",
        "tab_permissions": "🔑 權限系統後台",
        "tab_dept_setting": "🏢 部門組織維護 (新增/編輯/刪除)",
        "expander_add_emp": "➕ 新增跨國員工個人檔案",
        "step_1": "📍 步驟 1：選擇員工國籍/廠區 (選擇後即時切換下方欄位)",
        "lbl_site": "員工所屬國籍/廠區",
        "lbl_dept": "所屬部門/單位",
        "lbl_name": "員工姓名 *",
        "lbl_job_title": "職位名稱",
        "lbl_role": "系統權限角色 (Role)",
        "lbl_phone": "聯絡電話 (Phone) *",
        "lbl_address": "居住/戶籍地址 (Address) *",
        "lbl_passport": "護照號碼 / 身份證字號",
        "lbl_work_permit": "工作許可證 / 勞工證號",
        "btn_save_emp": "💾 儲存員工個人檔案",
        "msg_emp_added": "✅ 已成功新增員工檔案！",
        "table_title": "📋 公司現有員工名冊",
        "dept_mgr_title": "⚙️ 企業部門組織動態管理 (全自由編修)",
        "dept_mgr_caption": "您在此新增、修改或刪除的部門，將會即時同步至全系統的下拉選單中。",
        "section_add": "➕ 新增新部門",
        "section_edit": "✏️ 修改現有部門名稱",
        "section_delete": "🗑️ 刪除廢止部門",
        "lbl_select_edit_dept": "請選擇欲修改的部門：",
        "lbl_select_del_dept": "請選擇欲刪除的部門：",
        "lbl_new_dept_zh": "部門名稱 (中文)",
        "lbl_new_dept_vn": "部門名稱 (越南文 Tiếng Việt)",
        "lbl_new_dept_en": "部門名稱 (英文 English)",
        "btn_add_dept": "➕ 確定新增部門",
        "btn_update_dept": "💾 儲存修改內容",
        "btn_delete_dept": "🗑️ 確定刪除此部門",
        "msg_dept_added": "✅ 已成功新增部門！",
        "msg_dept_updated": "✅ 已順利更新部門名稱！",
        "msg_dept_deleted": "🗑️ 已成功刪除該部門！",
        "exist_depts": "📌 目前系統完整部門清單 (可直接在表格內雙擊修改)",
        "btn_save_table": "💾 儲存表格修改結果",
    },
    "Tiếng Việt": {
        "page_title": "👥 Quản lý Hồ sơ Nhân sự & Nhân viên Đa quốc gia",
        "tab_profiles": "👤 Hồ sơ Nhân viên Đa quốc gia",
        "tab_leave": "🌴 Hệ thống Nghỉ phép",
        "tab_permissions": "🔑 Phân quyền Hệ thống",
        "tab_dept_setting": "🏢 Quản lý Cấu hình Phòng ban (Thêm/Sửa/Xóa)",
        "expander_add_emp": "➕ Thêm Hồ sơ Nhân viên Đa quốc gia Mới",
        "step_1": "📍 Bước 1: Chọn Quốc tịch / Nhà máy của Nhân viên",
        "lbl_site": "Quốc tịch / Nhà máy trực thuộc",
        "lbl_dept": "Phòng ban / Bộ phận trực thuộc",
        "lbl_name": "Họ và tên Nhân viên *",
        "lbl_job_title": "Chức danh / Vị trí",
        "lbl_role": "Vai trò Phân quyền (Role)",
        "lbl_phone": "Số điện thoại liên hệ *",
        "lbl_address": "Địa chỉ thường trú / Tạm trú *",
        "lbl_passport": "Số Hộ chiếu / CMND / CCCD",
        "lbl_work_permit": "Số Giấy phép Lao động (Work Permit)",
        "btn_save_emp": "💾 Lưu Hồ sơ Nhân viên",
        "msg_emp_added": "✅ Đã thêm hồ sơ nhân viên thành công!",
        "table_title": "📋 Danh sách Nhân viên Hiện tại",
        "dept_mgr_title": "⚙️ Quản lý Động Cơ cấu Tổ chức Phòng ban",
        "dept_mgr_caption": "Các thay đổi (Thêm/Sửa/Xóa) phòng ban tại đây sẽ tự động đồng bộ vào tất cả các menu chọn trong hệ thống.",
        "section_add": "➕ Thêm Phòng ban Mới",
        "section_edit": "✏️ Chỉnh sửa Tên Phòng ban Hiện có",
        "section_delete": "🗑️ Xóa Phòng ban",
        "lbl_select_edit_dept": "Chọn phòng ban cần chỉnh sửa:",
        "lbl_select_del_dept": "Chọn phòng ban cần xóa:",
        "lbl_new_dept_zh": "Tên phòng ban (Tiếng Trung)",
        "lbl_new_dept_vn": "Tên phòng ban (Tiếng Việt)",
        "lbl_new_dept_en": "Tên phòng ban (Tiếng Anh)",
        "btn_add_dept": "➕ Xạc nhận Thêm Phòng ban",
        "btn_update_dept": "💾 Lưu Thay đổi",
        "btn_delete_dept": "🗑️ Xóa Phòng ban này",
        "msg_dept_added": "✅ Đã thêm phòng ban mới thành công!",
        "msg_dept_updated": "✅ Đã cập nhật tên phòng ban thành công!",
        "msg_dept_deleted": "🗑️ Đã xóa phòng ban thành công!",
        "exist_depts": "📌 Danh sách Phòng ban Hiện có (Có thể nhấp đúp trực tiếp vào bảng để sửa)",
        "btn_save_table": "💾 Lưu Kết quả Sửa Bảng",
    },
    "English": {
        "page_title": "👥 Global Employee Profiles & HR Management",
        "tab_profiles": "👤 Employee Profiles",
        "tab_leave": "🌴 Leave System",
        "tab_permissions": "🔑 Permissions Management",
        "tab_dept_setting": "🏢 Department Organization (Add/Edit/Delete)",
        "expander_add_emp": "➕ Add New International Employee Profile",
        "step_1": "📍 Step 1: Select Employee Nationality / Site Location",
        "lbl_site": "Nationality / Site Location",
        "lbl_dept": "Department / Unit",
        "lbl_name": "Full Name *",
        "lbl_job_title": "Job Title",
        "lbl_role": "System Permission Role",
        "lbl_phone": "Contact Phone *",
        "lbl_address": "Residential / Permanent Address *",
        "lbl_passport": "Passport / National ID No.",
        "lbl_work_permit": "Work Permit No.",
        "btn_save_emp": "💾 Save Employee Profile",
        "msg_emp_added": "✅ Employee profile added successfully!",
        "table_title": "📋 Existing Employee List",
        "dept_mgr_title": "⚙️ Dynamic Department Management (Full CRUD)",
        "dept_mgr_caption": "Any additions, edits, or deletions here will immediately update all system dropdowns.",
        "section_add": "➕ Add New Department",
        "section_edit": "✏️ Edit Existing Department",
        "section_delete": "🗑️ Delete Department",
        "lbl_select_edit_dept": "Select department to edit:",
        "lbl_select_del_dept": "Select department to delete:",
        "lbl_new_dept_zh": "Department Name (Chinese)",
        "lbl_new_dept_vn": "Department Name (Vietnamese)",
        "lbl_new_dept_en": "Department Name (English)",
        "btn_add_dept": "➕ Confirm Add Department",
        "btn_update_dept": "💾 Save Changes",
        "btn_delete_dept": "🗑️ Confirm Delete",
        "msg_dept_added": "✅ New department added successfully!",
        "msg_dept_updated": "✅ Department updated successfully!",
        "msg_dept_deleted": "🗑️ Department deleted successfully!",
        "exist_depts": "📌 Current Department List (Double click cells to edit directly)",
        "btn_save_table": "💾 Save Table Edits",
    },
}


def render_employee_management(*args, **kwargs):
    # 自動偵測全域語系
    lang = (
        kwargs.get("lang")
        or kwargs.get("curr_lang")
        or st.session_state.get("current_lang", "繁體中文")
    )
    L = EMP_I18N.get(lang, EMP_I18N["繁體中文"])

    st.title(L["page_title"])

    # 初始化預設自訂部門資料庫（保存在 Session State 中）
    if "custom_departments" not in st.session_state:
        st.session_state.custom_departments = [
            {
                "zh": "生產一課 (射出)",
                "vn": "Tổ Sản xuất 1 (Ép nhựa)",
                "en": "Production Dept 1 (Injection)",
            },
            {
                "zh": "品質保證部 (QA)",
                "vn": "Phòng Quản lý Chất lượng (QA)",
                "en": "Quality Assurance (QA)",
            },
            {
                "zh": "總務行政部 (GA)",
                "vn": "Phòng Hành chính Hậu cần (GA)",
                "en": "General Affairs (GA)",
            },
            {
                "zh": "財務部 (Finance)",
                "vn": "Phòng Tài chính (Finance)",
                "en": "Finance Dept",
            },
            {"zh": "研發部 (R&D)", "vn": "Phòng Nghiên cứu & Phát triển (R&D)", "en": "R&D Dept"},
            {
                "zh": "配電盤組裝課",
                "vn": "Tổ Lắp ráp Tủ điện",
                "en": "Switchgear Assembly Dept",
            },
            {
                "zh": "板金加工課",
                "vn": "Tổ Gia công Cơ khí",
                "en": "Sheet Metal Dept",
            },
            {
                "zh": "烤漆塗裝課",
                "vn": "Tổ Sơn tĩnh điện",
                "en": "Powder Coating Dept",
            },
        ]

    # 依當前語言動態組裝下拉選單內容
    if lang == "Tiếng Việt":
        dept_options = [d["vn"] for d in st.session_state.custom_departments]
    elif lang == "English":
        dept_options = [d["en"] for d in st.session_state.custom_departments]
    else:
        dept_options = [d["zh"] for d in st.session_state.custom_departments]

    # 初始化預設員工清單
    if "employees_db" not in st.session_state:
        st.session_state.employees_db = [
            {
                "id": "EMP-001",
                "name": "張小華",
                "site": "🇹🇼 台灣總部",
                "dept": dept_options[0],
                "title": "射出工程師",
                "phone": "0912345678",
            },
            {
                "id": "EMP-002",
                "name": "Nguyễn Văn A",
                "site": "🇻🇳 越南西寧廠",
                "dept": dept_options[5] if len(dept_options) > 5 else dept_options[0],
                "title": "Kỹ sư Tủ điện",
                "phone": "0987654321",
            },
        ]

    tab1, tab2, tab3, tab4 = st.tabs(
        [L["tab_profiles"], L["tab_leave"], L["tab_permissions"], L["tab_dept_setting"]]
    )

    # ----------------------------------------------------
    # 頁籤 1：跨國員工檔案管理
    # ----------------------------------------------------
    with tab1:
        with st.expander(L["expander_add_emp"], expanded=True):
            st.markdown(f"#### {L['step_1']}")
            c1, c2 = st.columns(2)
            site = c1.selectbox(
                L["lbl_site"],
                ["🇹🇼 台灣總部 (Taiwan HQ)", "🇻🇳 越南西寧廠 (Tay Ninh Plant)", "🇨🇳 中國東莞廠 (Dongguan Plant)"],
            )
            dept = c2.selectbox(L["lbl_dept"], dept_options)

            c3, c4, c5 = st.columns(3)
            name = c3.text_input(L["lbl_name"], value="張小華")
            title = c4.text_input(L["lbl_job_title"], value="射出工程師")
            role = c5.selectbox(L["lbl_role"], ["User (一般員工)", "Manager (主管)", "Admin (系統管理者)"])

            c6, c7 = st.columns(2)
            phone = c6.text_input(L["lbl_phone"], value="0912345678")
            address = c7.text_input(L["lbl_address"], value="台北市信義區忠孝東路")

            c8, c9 = st.columns(2)
            passport = c8.text_input(L["lbl_passport"], value="A123456789")
            work_permit = c9.text_input(L["lbl_work_permit"], value="WP-2026-8888")

            if st.button(L["btn_save_emp"], type="primary"):
                st.session_state.employees_db.append(
                    {
                        "id": f"EMP-00{len(st.session_state.employees_db)+1}",
                        "name": name,
                        "site": site,
                        "dept": dept,
                        "title": title,
                        "phone": phone,
                    }
                )
                st.success(L["msg_emp_added"])
                st.rerun()

        st.markdown(f"### {L['table_title']}")
        st.dataframe(pd.DataFrame(st.session_state.employees_db), use_container_width=True)

    with tab2:
        st.info("🌴 請假審核與假勤管理模組運作中。")

    with tab3:
        st.info("🔑 RBAC 權限矩陣控制台運作中。")

    # ----------------------------------------------------
    # 頁籤 4：部門組織動態維護 (新增 / 編輯 / 刪除 CRUD)
    # ----------------------------------------------------
    with tab4:
        st.markdown(f"### {L['dept_mgr_title']}")
        st.caption(L["dept_mgr_caption"])

        # 1. 互動式可直接修改的表格 (st.data_editor)
        st.markdown(f"#### {L['exist_depts']}")
        df_depts = pd.DataFrame(st.session_state.custom_departments)
        edited_df = st.data_editor(
            df_depts,
            use_container_width=True,
            num_rows="dynamic",
            key="dept_editor",
        )

        if st.button(L["btn_save_table"], type="primary"):
            st.session_state.custom_departments = edited_df.to_dict("records")
            st.success(L["msg_dept_updated"])
            st.rerun()

        st.divider()

        # 2. 精準控制選單：新增、編輯與刪除專區
        col_act1, col_act2 = st.columns(2)

        # (A) 編輯現有部門區塊
        with col_act1:
            st.markdown(f"#### {L['section_edit']}")
            all_zh_names = [d["zh"] for d in st.session_state.custom_departments]
            if all_zh_names:
                selected_edit_zh = st.selectbox(
                    L["lbl_select_edit_dept"], all_zh_names
                )
                # 找出選取的部門物件
                target_dept = next(
                    d
                    for d in st.session_state.custom_departments
                    if d["zh"] == selected_edit_zh
                )

                edit_zh = st.text_input(
                    L["lbl_new_dept_zh"], value=target_dept["zh"], key="edit_zh"
                )
                edit_vn = st.text_input(
                    L["lbl_new_dept_vn"], value=target_dept["vn"], key="edit_vn"
                )
                edit_en = st.text_input(
                    L["lbl_new_dept_en"], value=target_dept["en"], key="edit_en"
                )

                if st.button(L["btn_update_dept"]):
                    target_dept["zh"] = edit_zh
                    target_dept["vn"] = edit_vn
                    target_dept["en"] = edit_en
                    st.success(L["msg_dept_updated"])
                    st.rerun()

        # (B) 刪除舊部門區塊
        with col_act2:
            st.markdown(f"#### {L['section_delete']}")
            if all_zh_names:
                selected_del_zh = st.selectbox(
                    L["lbl_select_del_dept"], all_zh_names
                )
                if st.button(L["btn_delete_dept"], type="secondary"):
                    st.session_state.custom_departments = [
                        d
                        for d in st.session_state.custom_departments
                        if d["zh"] != selected_del_zh
                    ]
                    st.success(L["msg_dept_deleted"])
                    st.rerun()


def show(*args, **kwargs):
    render_employee_management(*args, **kwargs)


def main(*args, **kwargs):
    render_employee_management(*args, **kwargs)
