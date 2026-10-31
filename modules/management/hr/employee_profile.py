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
        "caption": "管理公司在職員工名冊、越南勞動法規合規建檔、外派與外籍幹部薪資、簽證、證件歸檔與離職異動。",
        "tab_vn": "VN 新增越南員工",
        "tab_expat": "🌐 新增外派與外籍幹部 (多國籍/雙薪/證件上傳)",
        "tab_list": "📑 現職員工總名冊與異動",
        "tab_resigned": "📁 離職名冊管理",
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
        # 外派/外籍幹部表單
        "form_expat_title": "🌐 新增外派與外籍幹部資料 (多國籍專案管理、雙薪與證件上傳)",
        "lbl_expat_name": "幹部姓名 (Họ tên chuyên gia) *",
        "lbl_expat_no": "工號 / 識別碼 *",
        "lbl_nationality": "國籍 (Nationality)",
        "lbl_phone_expat": "聯絡電話 (Phone / Zalo / WeChat)",
        "lbl_passport": "護照號碼 / 居留證號 *",
        "lbl_visa_type": "簽證類型 (Visa Type)",
        "lbl_visa_expire": "工作簽證 / 暫住證 (TRC) / 工作證到期日",
        "lbl_sal_official": "當地申報薪資 (Local Base Salary)",
        "lbl_sal_private": "海外專案津貼 / 差旅補助 (Overseas Allowance)",
        "lbl_upload_passport": "📄 上傳護照掃描檔 / 照片 (Passport)",
        "lbl_upload_workpermit": "📄 上傳越南工作證 (Work Permit)",
        "lbl_upload_trc": "📄 上傳暫住證 / 簽證影本 (TRC / Visa)",
        "btn_save_expat": "🚀 儲存外派與外籍幹部合規檔案與證件",
        "success_expat": "🎉 成功新增外派與外籍幹部：{name}！",
        # 離職異動
        "terminate_title": "🔄 員工離職狀態異動與結清處理",
        "lbl_select_terminate_emp": "選擇要辦理離職的員工 (工號 - 姓名)",
        "btn_terminate": "🔴 辦理離職手續並移至離職名冊",
        "success_terminate": "✅ 員工 `{emp}` 已成功辦理離職！"
    },
    "Tiếng Việt": {
        "title": "👤 Phòng Nhân sự - Quản lý Hồ sơ & Nhân sự",
        "caption": "Quản lý nhân viên, luật lao động VN, chuyên gia, lương, hồ sơ giấy tờ và thủ tục nghỉ việc.",
        "tab_vn": "VN Thêm nhân viên VN",
        "tab_expat": "🌐 Thêm chuyên gia nước ngoài",
        "tab_list": "📑 Danh sách nhân viên & Xử lý nghỉ việc",
        "tab_resigned": "📁 Danh sách đã nghỉ việc",
        "form_vn_title": "VN Thêm nhân viên người Việt",
        "lbl_emp_no": "Mã NV *",
        "lbl_name": "Họ tên *",
        "lbl_phone": "Số điện thoại",
        "lbl_id_card": "Số CCCD / Hộ chiếu *",
        "lbl_tax_code": "Mã số thuế",
        "lbl_factory": "Nhà máy",
        "lbl_dept": "Bộ phận",
        "lbl_position": "Chức vụ",
        "lbl_staff_type": "Loại nhân sự",
        "lbl_base_sal": "Lương cơ bản (VND)",
        "lbl_net_sal": "Thực nhận (VND)",
        "lbl_sys_role": "Quyền hệ thống",
        "lbl_perm_addr": "Thường trú",
        "lbl_temp_addr": "Tạm trú",
        "lbl_hospital": "Bệnh viện",
        "lbl_ins_no": "Mã số BHXH",
        "lbl_bank_acc": "Số tài khoản",
        "lbl_bank_name": "Tên ngân hàng",
        "btn_save_vn": "🚀 Lưu nhân viên VN",
        "success_vn": "🎉 Đã thêm thành công: {name}!",
        "form_expat_title": "🌐 Quản lý Chuyên gia nước ngoài",
        "lbl_expat_name": "Họ tên chuyên gia *",
        "lbl_expat_no": "Mã nhân sự *",
        "lbl_nationality": "Quốc tịch",
        "lbl_phone_expat": "Số điện thoại",
        "lbl_passport": "Số hộ chiếu *",
        "lbl_visa_type": "Loại Visa",
        "lbl_visa_expire": "Ngày hết hạn Visa/TRC",
        "lbl_sal_official": "Lương cơ bản tại chỗ",
        "lbl_sal_private": "Phụ cấp dự án nước ngoài",
        "lbl_upload_passport": "📄 Tải lên Hộ chiếu",
        "lbl_upload_workpermit": "📄 Tải lên Giấy phép lao động",
        "lbl_upload_trc": "📄 Tải lên Thẻ tạm trú (TRC)",
        "btn_save_expat": "🚀 Lưu hồ sơ chuyên gia",
        "success_expat": "🎉 Đã lưu thành công chuyên gia: {name}!",
        "terminate_title": "🔄 Xử lý thủ tục nghỉ việc nhân sự",
        "lbl_select_terminate_emp": "Chọn nhân viên nghỉ việc",
        "btn_terminate": "🔴 Xác nhận nghỉ việc",
        "success_terminate": "✅ Đã chuyển nhân viên `{emp}` sang danh sách nghỉ việc!"
    },
    "English": {
        "title": "👤 HR Center - Employee Profiles & Expat Management",
        "caption": "Manage employee registry, multinational expats, salaries, document uploads, and termination records.",
        "tab_vn": "VN New Employee",
        "tab_expat": "🌐 Expat & Foreign Staff Setup",
        "tab_list": "📑 Employee Registry & Termination",
        "tab_resigned": "📁 Resigned List",
        "form_vn_title": "VN Add Vietnamese Employee",
        "lbl_emp_id": "Employee No. *",
        "lbl_name": "Full Name *",
        "lbl_phone": "Phone",
        "lbl_id_card": "ID / Passport *",
        "lbl_tax_code": "Tax Code",
        "lbl_factory": "Factory",
        "lbl_dept": "Department",
        "lbl_position": "Position",
        "lbl_staff_type": "Staff Type",
        "lbl_base_sal": "Base Salary (VND)",
        "lbl_net_sal": "Net Salary",
        "lbl_sys_role": "System Role",
        "lbl_perm_addr": "Permanent Address",
        "lbl_temp_addr": "Temporary Address",
        "lbl_hospital": "Hospital",
        "lbl_ins_no": "BHXH No.",
        "lbl_bank_acc": "Bank Account",
        "lbl_bank_name": "Bank Name",
        "btn_save_vn": "🚀 Save Vietnamese Employee",
        "success_vn": "🎉 Successfully added: {name}!",
        "form_expat_title": "🌐 Expat & Foreign Staff Setup",
        "lbl_expat_name": "Expat Full Name *",
        "lbl_expat_no": "Expat ID *",
        "lbl_nationality": "Nationality",
        "lbl_phone_expat": "Phone",
        "lbl_passport": "Passport No. *",
        "lbl_visa_type": "Visa Type",
        "lbl_visa_expire": "Expiry Date",
        "lbl_sal_official": "Local Base Salary",
        "lbl_sal_private": "Overseas Allowance",
        "lbl_upload_passport": "📄 Upload Passport",
        "lbl_upload_workpermit": "📄 Upload Work Permit",
        "lbl_upload_trc": "📄 Upload TRC / Visa",
        "btn_save_expat": "🚀 Save Expat Profile",
        "success_expat": "🎉 Successfully saved expat: {name}!",
        "terminate_title": "🔄 Process Employee Termination",
        "lbl_select_terminate_emp": "Select Employee to Terminate",
        "btn_terminate": "🔴 Confirm Termination",
        "success_terminate": "✅ Employee `{emp}` moved to resigned list!"
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
                    private_allowance NUMERIC(15, 2) DEFAULT 0,
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

    tabs = st.tabs([L["tab_vn"], L["tab_expat"], L["tab_list"], L["tab_resigned"]])

    # Tab 1: 越南員工
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
                                    (emp_no, emp_name, phone, id_card, tax_code, factory, department, position, staff_type, base_salary, private_allowance, system_role, perm_address, temp_address, hospital, bhxh_no, bank_acc, bank_name, status)
                                    VALUES (:no, :name, :phone, :id_c, :tax, :fac, :dept, :pos, :stype, :sal, 0, :srole, :paddr, :taddr, :hosp, :bhxh, :bacc, :bname, '在職')
                                    ON CONFLICT (emp_no) DO UPDATE SET 
                                    emp_name = :name, phone = :phone, base_salary = :sal, status = '在職';
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
                    st.warning("⚠️ 請完整填寫必要欄位！")

    # Tab 2: 外派與外籍幹部 (多國籍、雙薪、聯絡電話、證件檔案上傳)
    with tabs[1]:
        st.markdown(f"### {L['form_expat_title']}")
        c1, c2 = st.columns(2)
        with c1:
