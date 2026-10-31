import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 員工檔案與人事管理模組完整多語系字典 (i18n)
# ----------------------------------------------------
EMP_PROFILE_I18N = {
    "繁體中文": {
        "title": "👤 管理部 - 員工個人檔案與人事管理中心",
        "caption": "管理公司在職員工名冊、越南勞動法規合規建檔、外派幹部雙薪與簽證居留證件管理。",
        "tab_vn": "VN 新增越南員工",
        "tab_tw": "TW 新增外派幹部 (雙薪/簽證)",
        "tab_list": "📑 現職員工總名冊 (含台越分流)",
        "tab_resigned": "📁 離職名冊",
        # 越南員工表單
        "form_vn_title": "VN 新增越南籍員工資料 (符合越南勞動法規範)",
        "lbl_emp_no": "工號 (Mã NV) *",
        "lbl_name": "姓名 (Họ tên) *",
        "lbl_phone": "聯絡電話 (Số ĐT)",
        "lbl_id_card": "公民身分證 CCCD / 護照 *",
        "lbl_tax_code": "個人稅號 (Mã số thuế)",
        "lbl_factory": "駐點廠區 (Nhà máy)",
        "lbl_dept": "部門 (Bộ phận)",
        "lbl_position": "職稱 (Chức vụ)",
        "lbl_staff_type": "出勤性質",
        "lbl_base_sal": "越南盾固定底薪 (Lương CB - VND)",
        "lbl_net_sal": "越南盾確認金額 (VND)",
        "lbl_sys_role": "系統權限角色 (System Role)",
        "lbl_perm_addr": "戶籍地址 (Thường trú)",
        "lbl_temp_addr": "現居地址 (Tạm trú)",
        "lbl_hospital": "體檢醫院 (Bệnh viện KCB)",
        "lbl_ins_no": "社保號碼 (Mã số BHXH)",
        "lbl_bank_acc": "薪資銀行帳號 (Số TK Ngân hàng)",
        "lbl_bank_name": "銀行分行名稱 (Tên Ngân hàng)",
        "btn_save_vn": "🚀 確認並寫入越南員工資料庫",
        "success_vn": "🎉 成功新增越南籍員工：{name} (工號: {emp_no})！",
        # 台幹表單
        "form_tw_title": "TW 新增外派幹部資料 (台幹雙薪、簽證與居留證件管理)",
        "lbl_tw_name": "台幹姓名 (Họ tên chuyên gia) *",
        "lbl_tw_no": "台幹工號 *",
        "lbl_passport": "台灣護照號碼 / 台胞證 *",
        "lbl_visa_type": "簽證類型 (Visa Type)",
        "lbl_visa_expire": "工作簽證/暫住證到期日 (Work Permit/TRC Expire)",
        "lbl_tw_sal_twd": "台灣本薪 (TWD)",
        "lbl_vn_allowance": "越南當地津貼 (USD / VND)",
        "btn_save_tw": "🚀 儲存外派幹部合規檔案",
        "success_tw": "🎉 成功新增外派幹部：{name}！"
    },
    "Tiếng Việt": {
        "title": "👤 Phòng Nhân sự - Quản lý Hồ sơ & Nhân sự",
        "caption": "Quản lý nhân viên, tuân thủ luật lao động VN, lương kép chuyên gia và giấy phép lao động.",
        "tab_vn": "VN Thêm nhân viên VN",
        "tab_tw": "TW Thêm chuyên gia nước ngoài",
        "tab_list": "📑 Danh sách nhân viên toàn công ty",
        "tab_resigned": "📁 Danh sách nghỉ việc",
        # Form VN
        "form_vn_title": "VN Thêm nhân viên người Việt (Đạt chuẩn luật lao động VN)",
        "lbl_emp_no": "Mã NV *",
        "lbl_name": "Họ tên *",
        "lbl_phone": "Số điện thoại",
        "lbl_id_card": "Số CCCD / Hộ chiếu *",
        "lbl_tax_code": "Mã số thuế",
        "lbl_factory": "Nhà máy trực thuộc",
        "lbl_dept": "Bộ phận",
        "lbl_position": "Chức vụ",
        "lbl_staff_type": "Loại nhân sự",
        "lbl_base_sal": "Lương cơ bản (VND)",
        "lbl_net_sal": "Thực nhận (VND)",
        "lbl_sys_role": "Quyền hệ thống",
        "lbl_perm_addr": "Thường trú",
        "lbl_temp_addr": "Tạm trú",
        "lbl_hospital": "Bệnh viện khám sức khỏe",
        "lbl_ins_no": "Mã số BHXH",
        "lbl_bank_acc": "Số tài khoản ngân hàng",
        "lbl_bank_name": "Tên ngân hàng",
        "btn_save_vn": "🚀 Lưu thông tin nhân viên VN",
        "success_vn": "🎉 Đã thêm thành công nhân viên: {name} (Mã: {emp_no})!",
        # Form TW
        "form_tw_title": "TW Quản lý Chuyên gia nước ngoài (Lương kép, Visa, Thẻ tạm trú)",
        "lbl_tw_name": "Họ tên chuyên gia *",
        "lbl_tw_no": "Mã nhân sự *",
        "lbl_passport": "Số hộ chiếu Đài Loan *",
        "lbl_visa_type": "Loại Visa",
        "lbl_visa_expire": "Ngày hết hạn Giấy phép lao động / TRC",
        "lbl_tw_sal_twd": "Lương cơ bản tại Đài Loan (TWD)",
        "lbl_vn_allowance": "Phụ cấp tại Việt Nam (USD/VND)",
        "btn_save_tw": "🚀 Lưu hồ sơ chuyên gia nước ngoài",
        "success_tw": "🎉 Đã lưu hồ sơ chuyên gia: {name} thành công!"
    },
    "English": {
        "title": "👤 HR Center - Employee Profiles & Expat Management",
        "caption": "Manage employee registry, Vietnam labor law compliance, dual-payroll, and work permits.",
        "tab_vn": "VN New Employee",
        "tab_tw": "TW Expat Setup",
        "tab_list": "📑 Employee Registry",
        "tab_resigned": "📁 Resigned List",
        # Form VN
        "form_vn_title": "VN Add Vietnamese Employee (Labor Law Compliant)",
        "lbl_emp_no": "Employee No. *",
        "lbl_name": "Full Name *",
        "lbl_phone": "Phone Number",
        "lbl_id_card": "ID Card / Passport No. *",
        "lbl_tax_code": "Tax Code",
        "lbl_factory": "Factory Location",
        "lbl_dept": "Department",
        "lbl_position": "Position",
        "lbl_staff_type": "Staff Type",
        "lbl_base_sal": "Base Salary (VND)",
        "lbl_net_sal": "Net Salary (VND)",
        "lbl_sys_role": "System Role",
        "lbl_perm_addr": "Permanent Address",
        "lbl_temp_addr": "Temporary Address",
        "lbl_hospital": "Medical Hospital",
        "lbl_ins_no": "Social Insurance (BHXH)",
        "lbl_bank_acc": "Bank Account No.",
        "lbl_bank_name": "Bank Name",
        "btn_save_vn": "🚀 Save Vietnamese Employee",
        "success_vn": "🎉 Successfully added employee: {name} (No: {emp_no})!",
        # Form TW
        "form_tw_title": "TW Expat Setup (Dual Payroll & Visa Management)",
        "lbl_tw_name": "Expat Full Name *",
        "lbl_tw_no": "Expat ID *",
        "lbl_passport": "Passport No. *",
        "lbl_visa_type": "Visa Type",
        "lbl_visa_expire": "Work Permit / TRC Expiry Date",
        "lbl_tw_sal_twd": "Taiwan Salary (TWD)",
        "lbl_vn_allowance": "Vietnam Allowance (USD/VND)",
        "btn_save_tw": "🚀 Save Expat Profile",
        "success_tw": "🎉 Successfully saved expat profile: {name}!"
    }
}

def init_hr_profile_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.employee_profiles (
                    id SERIAL PRIMARY KEY,
                    emp_no VARCHAR(50) UNIQUE NOT NULL,
                    emp_name VARCHAR(150) NOT NULL,
                    phone VARCHAR(50),
                    id_card VARCHAR(100),
                    tax_code VARCHAR(50),
                    factory VARCHAR(100),
                    department VARCHAR(150),
                    position VARCHAR(100),
                    staff_type VARCHAR(100),
                    base_salary NUMERIC(15, 2) DEFAULT 0,
                    system_role VARCHAR(100),
                    perm_address TEXT,
                    temp_address TEXT,
                    hospital VARCHAR(150),
                    bhxh_no VARCHAR(100),
                    bank_acc VARCHAR(100),
                    bank_name VARCHAR(150),
                    status VARCHAR(50) DEFAULT '在職',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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

    tabs = st.tabs([L["tab_vn"], L["tab_tw"], L["tab_list"], L["tab_resigned"]])

    # Tab 1: 新增越南員工
    with tabs[0]:
        st.markdown(f"### {L['form_vn_title']}")
        with st.form("form_add_vietnamese_employee"):
            c1, c2, c3 = st.columns(3)
            with c1:
                emp_no = st.text_input(L["lbl_emp_no"], placeholder="VN-003")
                name = st.text_input(L["lbl_name"], placeholder="NGUYỄN VĂN A")
                phone = st.text_input(L["lbl_phone"], placeholder="+84-901234567")
                id_card = st.text_input(L["lbl_id_card"], placeholder="079095012345")
                tax_code = st.text_input(L["lbl_tax_code"], placeholder="8012345678")
            with c2:
                factory = st.selectbox(L["lbl_factory"], ["西寧廠 (Tay Ninh)", "胡志明辦事處 (HCMC)"])
                dept = st.selectbox(L["lbl_dept"], ["生產部 (Production Dept)", "品管部 (QA/QC)", "倉儲物流 (Logistics)", "管理部 (Management)", "工程部 (Engineering)"])
                position = st.text_input(L["lbl_position"], placeholder="作業員 / 班長 / 工程師")
                staff_type = st.selectbox(L["lbl_staff_type"], ["廠內固定員工 (Plant Fixed Staff)", "外包派遣員工 (Contractor)", "產學合作實習生"])
                base_sal = st.number_input(L["lbl_base_sal"], value=5000000.0, step=500000.0)
                st.markdown(f"**{L['lbl_net_sal']}**：`{base_sal:,.0f} ₫ (VND)`")
            with c3:
                system_role = st.selectbox(L["lbl_sys_role"], ["一般員工 (Employee)", "產線班長 (Line Leader)", "保全人員 (Security)", "倉儲管理員 (Warehouse)", "會計/人事 (Admin/Finance)"])
                perm_addr = st.text_input(L["lbl_perm_addr"], placeholder="Tây Ninh, Việt Nam")
                temp_addr = st.text_input(L["lbl_temp_addr"], placeholder="An Tinh, Trảng Bàng, Tây Ninh")
                hospital = st.text_input(L["lbl_hospital"], placeholder="Bệnh viện KCB Tây Ninh")
                bhxh_no = st.text_input(L["lbl_ins_no"], placeholder="7912345678")
                bank_acc = st.text_input(L["lbl_bank_acc"], placeholder="1023456789")
                bank_name = st.text_input(L["lbl_bank_name"], placeholder="Vietcombank - Chi nhánh Tây Ninh")

            if st.form_submit_button(L["btn_save_vn"], type="primary", use_container_width=True):
                if emp_no and name and id_card:
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.employee_profiles 
                                    (emp_no, emp_name, phone, id_card, tax_code, factory, department, position, staff_type, base_salary, system_role, perm_address, temp_address, hospital, bhxh_no, bank_acc, bank_name, status)
                                    VALUES (:no, :name, :phone, :id_c, :tax, :fac, :dept, :pos, :stype, :sal, :srole, :paddr, :taddr, :hosp, :bhxh, :bacc, :bname, '在職')
                                    ON CONFLICT (emp_no) DO UPDATE SET 
                                    emp_name = :name, phone = :phone, base_salary = :sal;
                                """), {
                                    "no": emp_no.strip(), "name": name.strip(), "phone": phone.strip(),
                                    "id_c": id_card.strip(), "tax": tax_code.strip(), "fac": factory,
                                    "dept": dept, "position": position.strip(), "stype": staff_type,
                                    "sal": base_sal, "srole": system_role, "paddr": perm_addr,
                                    "taddr": temp_addr, "hosp": hospital, "bhxh": bhxh_no,
                                    "bacc": bank_acc, "bname": bank_name
                                })
                        except Exception:
                            pass
                    st.success(L["success_vn"].format(name=name, emp_no=emp_no))
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫必要欄位 (工號、姓名、身分證)！")

    # Tab 2: 新增外派幹部 (台幹)
    with tabs[1]:
        st.markdown(f"### {L['form_tw_title']}")
        with st.form("form_add_tw_expat"):
            c1, c2 = st.columns(2)
            with c1:
                tw_no = st.text_input(L["lbl_tw_no"], placeholder="TW-001")
                tw_name = st.text_input(L["lbl_tw_name"], placeholder="許福村 (Tassos)")
                passport = st.text_input(L["lbl_passport"], placeholder="Taiwan Passport No.")
                visa_type = st.selectbox(L["lbl_visa_type"], ["LD1 / LD2 (工作簽證)", "DN1 (商業簽證)", "TRC (長期居留證)"])
            with c2:
                visa_expire = st.text_input(L["lbl_visa_expire"], value="2027-12-31")
                tw_sal = st.number_input(L["lbl_tw_sal_twd"], value=60000.0, step=5000.0)
                vn_allow = st.text_input(L["lbl_vn_allowance"], placeholder="USD $1,500 + 宿舍/配車")

            if st.form_submit_button(L["btn_save_tw"], type="primary", use_container_width=True):
                if tw_no and tw_name:
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.employee_profiles 
                                    (emp_no, emp_name, position, staff_type, base_salary, status)
                                    VALUES (:no, :name, '外派幹部 (Expat)', '台幹雙薪', :sal, '在職')
                                    ON CONFLICT (emp_no) DO UPDATE SET emp_name = :name;
                                """), {"no": tw_no.strip(), "name": tw_name.strip(), "sal": tw_sal})
                        except Exception:
                            pass
                    st.success(L["success_tw"].format(name=tw_name))
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫台幹工號與姓名！")

    # Tab 3: 現職員工總名冊
    with tabs[2]:
        st.markdown(f"### {L['tab_list']}")
        if engine:
            try:
                df = pd.read_sql("SELECT emp_no, emp_name, department, position, staff_type, base_salary, system_role FROM public.employee_profiles WHERE status = '在職';", con=engine)
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("目前尚無員工資料紀錄。")
            except Exception:
                st.info("資料庫表格尚未初始化或無資料。")
        else:
            st.info("DB engine not connected.")

    # Tab 4: 離職名冊
    with tabs[3]:
        st.markdown("### 📁 離職名冊 (Resigned Registry)")
        st.info("目前無離職人員紀錄。")

def show(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)

def main(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)

def render_employee_profile(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)

def render_employee_management(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)
