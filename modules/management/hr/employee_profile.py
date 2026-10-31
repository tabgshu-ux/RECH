import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

EMP_PROFILE_I18N = {
    "繁體中文": {
        "title": "👤 管理部 - 員工個人檔案與人事管理中心",
        "caption": "管理公司在職員工數位履歷、合約到期預警與勞動法規合規資料。",
        "tab_list": "📑 現職員工名冊",
        "tab_add": "➕ 新增員工履歷",
        "table_header": "📋 廠區現職員工數位履歷與合約清冊",
        "no_records": "目前尚無員工數位履歷紀錄。",
        "form_title": "➕ 建立新員工數位履歷資料",
        "lbl_emp_id": "工號 (Emp ID) *",
        "lbl_name": "員工姓名 (Full Name) *",
        "lbl_dept": "部門 (Department)",
        "lbl_position": "職稱與職位 (Position)",
        "lbl_join_date": "到職日期 (Join Date)",
        "lbl_contract_expire": "合約到期日 (Contract Expire)",
        "lbl_phone": "聯絡電話 (Phone)",
        "btn_save": "💾 儲存員工數位履歷",
        "success_msg": "🎉 員工 `{name}` 數位履歷已成功儲存！",
        "warn_msg": "⚠️ 請完整填寫工號與員工姓名！"
    },
    "Tiếng Việt": {
        "title": "👤 Phòng Nhân sự - Quản lý Hồ sơ Nhân viên",
        "caption": "Quản lý hồ sơ điện tử, theo dõi hợp đồng và tuân thủ quy định lao động.",
        "tab_list": "📑 Danh sách nhân viên",
        "tab_add": "➕ Thêm hồ sơ mới",
        "table_header": "📋 Danh sách hồ sơ nhân viên hiện tại",
        "no_records": "Chưa có dữ liệu hồ sơ nhân viên.",
        "form_title": "➕ Tạo hồ sơ nhân viên mới",
        "lbl_emp_id": "Mã NV (Emp ID) *",
        "lbl_name": "Họ tên nhân viên *",
        "lbl_dept": "Bộ phận",
        "lbl_position": "Chức vụ",
        "lbl_join_date": "Ngày vào làm",
        "lbl_contract_expire": "Ngày hết hạn hợp đồng",
        "lbl_phone": "Số điện thoại",
        "btn_save": "💾 Lưu hồ sơ nhân viên",
        "success_msg": "🎉 Đã lưu hồ sơ nhân viên `{name}` thành công!",
        "warn_msg": "⚠️ Vui lòng điền đầy đủ Mã NV và Họ tên!"
    },
    "English": {
        "title": "👤 HR Center - Employee Digital Profiles",
        "caption": "Manage employee digital resumes, contract expiration alerts, and compliance data.",
        "tab_list": "📑 Active Employees",
        "tab_add": "➕ Add Profile",
        "table_header": "📋 Employee Digital Profiles Registry",
        "no_records": "No employee records found.",
        "form_title": "➕ Create New Employee Profile",
        "lbl_emp_id": "Employee ID *",
        "lbl_name": "Full Name *",
        "lbl_dept": "Department",
        "lbl_position": "Position",
        "lbl_join_date": "Join Date",
        "lbl_contract_expire": "Contract Expiry",
        "lbl_phone": "Phone Number",
        "btn_save": "💾 Save Employee Profile",
        "success_msg": "🎉 Employee profile for `{name}` successfully saved!",
        "warn_msg": "⚠️ Please fill in Employee ID and Full Name!"
    }
}

def init_hr_profile_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS hr_employees (
                    emp_id VARCHAR(50) PRIMARY KEY,
                    emp_name VARCHAR(100) NOT NULL,
                    department VARCHAR(100),
                    position VARCHAR(100),
                    join_date VARCHAR(50),
                    contract_expire VARCHAR(50),
                    phone VARCHAR(50),
                    status VARCHAR(50) DEFAULT '在職'
                );
            """))
    except Exception:
        pass

def render_hr_profile_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = EMP_PROFILE_I18N.get(active_lang, EMP_PROFILE_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_hr_profile_db(engine)

    if "hr_employees_db" not in st.session_state:
        st.session_state.hr_employees_db = [
            {
                "emp_id": "VN-001",
                "emp_name": "Nguyễn Văn An",
                "department": "生產部 (Production)",
                "position": "作業員 (Operator)",
                "join_date": "2024-01-10",
                "contract_expire": "2026-12-31",
                "phone": "+84-901234567",
                "status": "在職"
            }
        ]

    tab_list, tab_add = st.tabs([L["tab_list"], L["tab_add"]])

    with tab_list:
        st.markdown(f"### {L['table_header']}")
        records = st.session_state.hr_employees_db
        if engine:
            try:
                df_db = pd.read_sql("SELECT emp_id, emp_name, department, position, join_date, contract_expire, phone, status FROM hr_employees;", con=engine)
                if not df_db.empty:
                    records = df_db.to_dict(orient="records")
            except Exception:
                pass

        if records:
            display_rows = []
            for idx, r in enumerate(records, 1):
                display_rows.append({
                    "STT" if active_lang=="Tiếng Việt" else ("No." if active_lang=="English" else "序號"): idx,
                    "工號" if active_lang=="繁體中文" else ("Mã NV" if active_lang=="Tiếng Việt" else "Emp ID"): r.get("emp_id"),
                    "姓名" if active_lang=="繁體中文" else ("Họ tên" if active_lang=="Tiếng Việt" else "Name"): r.get("emp_name"),
                    "部門" if active_lang=="繁體中文" else ("Bộ phận" if active_lang=="Tiếng Việt" else "Department"): r.get("department"),
                    "職稱" if active_lang=="繁體中文" else ("Chức vụ" if active_lang=="Tiếng Việt" else "Position"): r.get("position"),
                    "到職日" if active_lang=="繁體中文" else ("Ngày vào" if active_lang=="Tiếng Việt" else "Join Date"): r.get("join_date"),
                    "合約到期" if active_lang=="繁體中文" else ("Hết hạn HĐ" if active_lang=="Tiếng Việt" else "Contract Expire"): r.get("contract_expire"),
                    "電話" if active_lang=="繁體中文" else ("Điện thoại" if active_lang=="Tiếng Việt" else "Phone"): r.get("phone"),
                    "狀態" if active_lang=="繁體中文" else ("Trạng thái" if active_lang=="Tiếng Việt" else "Status"): r.get("status")
                })
            st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)
        else:
            st.info(L["no_records"])

    with tab_add:
        st.markdown(f"### {L['form_title']}")
        with st.form("form_add_hr_employee"):
            c1, c2 = st.columns(2)
            with c1:
                emp_id = st.text_input(L["lbl_emp_id"], placeholder="例如: VN-002")
                emp_name = st.text_input(L["lbl_name"], placeholder="例如: Trần Văn B")
                department = st.selectbox(L["lbl_dept"], ["生產部 (Production)", "品管部 (QA/QC)", "倉庫物流 (Logistics)", "管理部 (Management)", "工程部 (Engineering)"])
                position = st.text_input(L["lbl_position"], placeholder="例如: 技術員 / 班長")
            with c2:
                join_date = st.text_input(L["lbl_join_date"], value=str(datetime.date.today()))
                contract_expire = st.text_input(L["lbl_contract_expire"], value=str(datetime.date.today() + datetime.timedelta(days=365)))
                phone = st.text_input(L["lbl_phone"], placeholder="+84-...")

            if st.form_submit_button(L["btn_save"], type="primary", use_container_width=True):
                if emp_id and emp_name:
                    new_rec = {
                        "emp_id": emp_id.strip(),
                        "emp_name": emp_name.strip(),
                        "department": department,
                        "position": position.strip() if position else "-",
                        "join_date": join_date,
                        "contract_expire": contract_expire,
                        "phone": phone.strip() if phone else "-",
                        "status": "在職"
                    }
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO hr_employees (emp_id, emp_name, department, position, join_date, contract_expire, phone, status)
                                    VALUES (:id, :name, :dept, :pos, :jdate, :cdate, :phone, '在職')
                                    ON CONFLICT (emp_id) DO UPDATE SET 
                                    emp_name = :name, department = :dept, position = :pos;
                                """), {
                                    "id": new_rec["emp_id"], "name": new_rec["emp_name"], "dept": new_rec["department"],
                                    "pos": new_rec["position"], "jdate": new_rec["join_date"], "cdate": new_rec["contract_expire"], "phone": new_rec["phone"]
                                })
                        except Exception:
                            pass
                    st.session_state.hr_employees_db.insert(0, new_rec)
                    st.success(L["success_msg"].format(name=emp_name))
                    st.rerun()
                else:
                    st.warning(L["warn_msg"])

def show(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)

def main(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)

def render_employee_profile(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)

def render_employee_management(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)
