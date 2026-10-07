import streamlit as st
import pandas as pd

def render_employee_management(engine=None, t=None, lang="繁體中文", **kwargs):
    if lang == "Tiếng Việt":
        st.title("👤 Quản lý Nhân sự & Hồ sơ Nhân viên")
        st.info("Nơi quản lý hồ sơ nhân viên, bảo hiểm, địa chỉ và thông tin chi tiết toàn nhà máy.")
    elif lang == "English":
        st.title("👤 Management Dept - HR & Employee Records")
        st.info("Manage employee profiles, insurance, addresses, and personnel records across all plants.")
    else:
        st.title("👤 管理部 - 員工個人檔案與人事管理")
        st.info("在此維護全廠區員工個人檔案、保險資料、戶籍/暫住地址、保險醫院與人事資料。")

    if "employee_db" not in st.session_state:
        st.session_state.employee_db = [
            {
                "工號": "EMP-001", "姓名": "張董事長", "國籍": "台灣 (Taiwan)", "工作廠區": "西寧廠 (Tay Ninh)", "部門": "管理部", "職稱": "董事長 (Chairman)", "角色": "Chairman", "電話": "0912345678", 
                "戶籍地址": "台北市信義區...", "暫住地址": "西寧省廠區宿舍", "保險資料": "TW-INS-888899", "保險醫院": "台北榮民總醫院", "生物辨識代碼": "FACE-BIO-888899"
            },
            {
                "工號": "EMP-002", "姓名": "Nguyễn Văn A", "國籍": "越南 (Vietnam)", "工作廠區": "西寧廠 (Tay Ninh)", "部門": "管理部", "職稱": "總經理 (General Manager)", "角色": "GeneralManager", "電話": "0918999080", 
                "戶籍地址": "Tỉnh Tây Ninh, Huyện Trảng Bàng", "暫住地址": "Khu công nghiệp Thành Thành Công", "保險資料": "VN-BHXH-0192834", "保險醫院": "Bệnh viện Đa khoa Tây Ninh", "生物辨識代碼": "FACE-BIO-100234"
            },
            {
                "工號": "EMP-003", "姓名": "李元隆", "國籍": "台灣 (Taiwan)", "工作廠區": "海防廠 (Hai Phong)", "部門": "工程與設計管理中心", "職稱": "副總經理 (Vice General Manager)", "角色": "ViceManager", "電話": "", 
                "戶籍地址": "高雄市左營區...", "暫住地址": "海防市宿舍", "保險資料": "TW-INS-300451", "保險醫院": "高雄醫學大學附設中和紀念醫院", "生物辨識代碼": "FACE-BIO-300451"
            }
        ]

    if "factory_list" not in st.session_state:
        st.session_state.factory_list = [
            {"廠區編號": "FAC-01", "廠區名稱": "西寧廠 (Tay Ninh)", "負責人": "張董事長", "電話": "0912345678"},
            {"廠區編號": "FAC-02", "廠區名稱": "海防廠 (Hai Phong)", "負責人": "阮文強", "電話": "0918999080"}
        ]

    search_label = "🔍 搜尋員工姓名 / 工號 / 職稱" if lang == "繁體中文" else ("🔍 Tìm kiếm nhân viên..." if lang == "Tiếng Việt" else "🔍 Search Employee...")
    search_q = st.text_input(search_label, placeholder="輸入關鍵字搜尋員工...")
    
    filtered_emp = [
        e for e in st.session_state.employee_db 
        if search_q.lower() in e["姓名"].lower() or search_q.lower() in e["工號"].lower() or search_q.lower() in e["職稱"].lower()
    ] if search_q else st.session_state.employee_db

    list_title = "### 📋 現有在職員工名冊" if lang == "繁體中文" else ("### 📋 Danh sách Nhân viên hiện tại" if lang == "Tiếng Việt" else "### 📋 Current Employee Directory")
    st.markdown(list_title)
    st.dataframe(pd.DataFrame(filtered_emp), use_container_width=True)

    tab_names = ["➕ 新增員工", "✏️ 修改員工資料", "🗑️ 刪除員工"] if lang == "繁體中文" else (["➕ Thêm nhân viên", "✏️ Sửa thông tin", "🗑️ Xóa nhân viên"] if lang == "Tiếng Việt" else ["➕ Add Employee", "✏️ Edit Employee", "🗑️ Delete Employee"])
    tab_add, tab_edit, tab_del = st.tabs(tab_names)

    with tab_add:
        with st.form("add_employee_form"):
            st.markdown("### ➕ 新增員工個人檔案與保險/地址資料")
            c1, c2 = st.columns(2)
            with c1:
                e_id = st.text_input("員工工號", value=f"EMP-{len(st.session_state.employee_db)+1:03d}")
                e_name = st.text_input("員工姓名 (Employee Name)")
                e_nat = st.selectbox("國籍", ["台灣 (Taiwan)", "越南 (Vietnam)", "其他 (Other)"])
                e_perm_addr = st.text_input("戶籍地址 (Permanent Address / Hộ khẩu thường trú)")
                e_temp_addr = st.text_input("暫住地址 (Temporary Address / Chỗ ở hiện tại)")
            with c2:
                fac_choices = [f"{fac['廠區名稱']}" for fac in st.session_state.factory_list]
                if not fac_choices:
                    fac_choices = ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"]
                e_fac = st.selectbox("工作廠區 (Factory)", fac_choices)
                
                if lang == "Tiếng Việt":
                    dept_display_map = {
                        "管理部": "Phòng Quản lý (Management Dept)",
                        "營運戰情室": "Ban Giám đốc (Executive)",
                        "工程與設計管理中心": "Trung tâm Kỹ thuật & Thiết kế",
                        "生產部": "Phòng Sản xuất (Production Dept)"
                    }
                elif lang == "English":
                    dept_display_map = {
                        "管理部": "Management Dept",
                        "營運戰情室": "Executive Management",
                        "工程與設計管理中心": "Engineering & Design Center",
                        "生產部": "Production Dept"
                    }
                else:
                    dept_display_map = {
                        "管理部": "管理部",
                        "營運戰情室": "營運戰情室",
                        "工程與設計管理中心": "工程與設計管理中心",
                        "生產部": "生產部"
                    }
                
                dept_keys = list(dept_display_map.keys())
                dept_sel = st.selectbox("部門", dept_keys, format_func=lambda x: dept_display_map[x])
                e_dept = dept_sel

                e_title = st.text_input("職稱 / 職務", placeholder="例如: 現場工程師 / 技術員")

                if lang == "Tiếng Việt":
                    role_display_map = {
                        "staff": "Nhân viên chung (Staff)",
                        "manager": "Quản lý / Chủ quản (Manager)",
                        "security": "Bảo vệ (Security)",
                        "admin": "Quản trị hệ thống (Admin)"
                    }
                elif lang == "English":
                    role_display_map = {
                        "staff": "General Staff",
                        "manager": "Department Manager",
                        "security": "Security Guard",
                        "admin": "System Administrator"
                    }
                else:
                    role_display_map = {
                        "staff": "一般員工 (Staff)",
                        "manager": "部門主管 (Manager)",
                        "security": "保全 (Security)",
                        "admin": "系統管理員 (Admin)"
                    }

                role_keys = list(role_display_map.keys())
                role_sel = st.selectbox("系統權限角色", role_keys, format_func=lambda x: role_display_map[x])
                e_role = role_sel

                e_phone = st.text_input("聯絡電話", placeholder="0912...")
                e_insurance = st.text_input("保險資料 / 社會保險編號 (Insurance / BHXH)")
                e_hospital = st.text_input("保險醫院 / 就醫指定醫院 (Insurance Hospital / Bệnh viện KCB)")

            if st.form_submit_button("🚀 立即新增員工", type="primary"):
                if e_name:
                    st.session_state.employee_db.append({
                        "工號": e_id,
                        "姓名": e_name,
                        "國籍": e_nat,
                        "工作廠區": e_fac,
                        "部門": e_dept,
                        "職稱": e_title,
                        "角色": e_role,
                        "電話": e_phone,
                        "戶籍地址": e_perm_addr,
                        "暫住地址": e_temp_addr,
                        "保險資料": e_insurance,
                        "保險醫院": e_hospital,
                        "生物辨識代碼": f"FACE-BIO-{len(st.session_state.employee_db)+100000}"
                    })
                    success_msg = "Thêm nhân viên thành công!" if lang == "Tiếng Việt" else ("Employee added successfully!" if lang == "English" else f"✅ 員工 {e_name} 新增成功！")
                    st.success(success_msg)
                    st.rerun()
                else:
                    warn_msg = "Vui lòng nhập tên nhân viên!" if lang == "Tiếng Việt" else ("Please enter employee name!" if lang == "English" else "⚠️ 請填寫員工姓名！")
                    st.warning(warn_msg)

    with tab_edit:
        if st.session_state.employee_db:
            emp_opts = {f"{e['工號']} - {e['姓名']}": e for e in st.session_state.employee_db}
            sel_emp_key = st.selectbox("選擇要修改的員工", list(emp_opts.keys()))
            target_emp = emp_opts[sel_emp_key]

            with st.form("edit_employee_form"):
                st.markdown("### ✏️ 修改員工檔案與保險/地址資料")
                ed_name = st.text_input("員工姓名", value=target_emp["姓名"])
                fac_choices = [f"{fac['廠區名稱']}" for fac in st.session_state.factory_list]
                if target_emp["工作廠區"] not in fac_choices:
                    fac_choices.append(target_emp["工作廠區"])
                ed_fac = st.selectbox("工作廠區", fac_choices, index=fac_choices.index(target_emp["工作廠區"]) if target_emp["工作廠區"] in fac_choices else 0)
                ed_title = st.text_input("職稱", value=target_emp["職稱"])
                ed_phone = st.text_input("電話", value=target_emp["電話"])
                ed_perm_addr = st.text_input("戶籍地址", value=target_emp.get("戶籍地址", ""))
                ed_temp_addr = st.text_input("暫住地址", value=target_emp.get("暫住地址", ""))
                ed_insurance = st.text_input("保險資料 / 社會保險編號", value=target_emp.get("保險資料", ""))
                ed_hospital = st.text_input("保險醫院", value=target_emp.get("保險醫院", ""))

                if st.form_submit_button("💾 儲存修改", type="primary"):
                    for e in st.session_state.employee_db:
                        if e["工號"] == target_emp["工號"]:
                            e["姓名"] = ed_name
                            e["工作廠區"] = ed_fac
                            e["職稱"] = ed_title
                            e["電話"] = ed_phone
                            e["戶籍地址"] = ed_perm_addr
                            e["暫住地址"] = ed_temp_addr
                            e["保險資料"] = ed_insurance
                            e["保險醫院"] = ed_hospital
                    st.success(f"✅ 員工 {target_emp['工號']} 資料更新成功！")
                    st.rerun()
        else:
            st.info("目前無員工資料可供修改。")

    with tab_del:
        if st.session_state.employee_db:
            del_opts = {f"{e['工號']} - {e['姓名']}": e for e in st.session_state.employee_db}
            sel_del_key = st.selectbox("選擇要刪除的員工", list(del_opts.keys()))
            target_del = del_opts[sel_del_key]

            with st.form("delete_employee_form"):
                st.markdown("### 🗑️ 刪除員工確認")
                st.warning(f"確定要將員工 **{target_del['工號']} - {target_del['姓名']}** 自系統中刪除嗎？")
                if st.form_submit_button("🔥 確認刪除", type="primary"):
                    st.session_state.employee_db = [e for e in st.session_state.employee_db if e["工號"] != target_del["工號"]]
                    st.success(f"✅ 員工 {target_del['工號']} 已成功刪除！")
                    st.rerun()
        else:
            st.info("目前無員工資料可供刪除。")

def show(*args, **kwargs):
    render_employee_management(*args, **kwargs)

def main(*args, **kwargs):
    render_employee_management(*args, **kwargs)
