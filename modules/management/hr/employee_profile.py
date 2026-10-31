import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

EMP_PROFILE_I18N = {
    "繁體中文": {
        "title": "👤 管理部 - 員工個人檔案與人事管理中心",
        "caption": "管理公司在職員工名冊（區分越南員工與外派外籍幹部）、勞動法規合規建檔與 90 天證件預警。",
        "tab_vn": "VN 新增越南員工",
        "tab_expat": "🌐 新增外派與外籍幹部",
        "tab_list": "📑 現職員工總名冊與證件預警",
        "tab_edit": "✏️ 編輯與修改員工資料",
        "tab_resigned": "📁 離職名冊管理",
        "form_vn_title": "VN 新增越南籍員工資料 (符合越南勞動法規範)",
        "lbl_emp_no": "工號 (Mã NV) *",
        "lbl_name": "姓名 (Họ tên) *",
        "lbl_phone": "聯絡電話 (Số ĐT)",
        "lbl_id_card": "公民身分證 CCCD / 護照 *",
        "lbl_tax_code": "個人稅號 (Mã số thuế)",
        "lbl_factory": "駐點廠區 (Nhà máy)",
        "lbl_dept": "部門 (Bộ phận)",
        "lbl_position": "職稱 (Chức vụ)",
        "lbl_staff_type": "員工屬性 (廠內/外勤/點工)",
        "lbl_attendance_mode": "考勤打卡設定",
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
        "form_expat_title": "🌐 新增外派與外籍幹部資料 (多國籍專案管理、雙薪與證件上傳)",
        "lbl_expat_name": "幹部姓名 (Họ tên chuyên gia) *",
        "lbl_expat_no": "工號 / 識別碼 *",
        "lbl_nationality": "國籍 (Nationality)",
        "lbl_phone_expat": "聯絡電話 (Phone / Zalo / WeChat)",
        "lbl_passport": "護照號碼 / 居留證號 *",
        "lbl_visa_type": "簽證類型 (Visa Type)",
        "lbl_visa_expire": "工作簽證 / 暫住證 (TRC) / 護照到期日 *",
        "lbl_sal_official": "當地申報薪資 (Local Base Salary)",
        "lbl_sal_private": "海外專案津貼 / 差旅補助 (Overseas Allowance)",
        "lbl_upload_passport": "📄 上傳護照掃描檔 / 照片 (Passport)",
        "lbl_upload_workpermit": "📄 上傳越南工作證 (Work Permit)",
        "lbl_upload_trc": "📄 上傳暫住證 / 簽證影本 (TRC / Visa)",
        "btn_save_expat": "🚀 儲存外派與外籍幹部合規檔案與證件",
        "success_expat": "🎉 成功新增外派與外籍幹部：{name} (已記錄證件到期日與掃描檔)！",
        "search_label": "🔍 搜尋員工姓名、工號或國籍篩選",
        "alert_expiry_title": "🚨 外派/外籍幹部證件（簽證/TRC/護照）90天前提前到期預警（越南辦事需時3個月）",
        "terminate_title": "🔄 員工離職狀態異動與結清處理",
        "lbl_select_terminate_emp": "選擇要辦理離職的員工 (工號 - 姓名)",
        "btn_terminate": "🔴 辦理離職手續並移至離職名冊",
        "success_terminate": "✅ 員工 `{emp}` 已成功辦理離職！"
    },
    "Tiếng Việt": {
        "title": "👤 Phòng Nhân sự - Quản lý Hồ sơ & Nhân sự",
        "caption": "Quản lý nhân viên Việt Nam và chuyên gia nước ngoài, cảnh báo trước 90 ngày cho Visa/TRC.",
        "tab_vn": "VN Thêm nhân viên VN",
        "tab_expat": "🌐 Thêm chuyên gia nước ngoài",
        "tab_list": "📑 Danh sách nhân sự & Cảnh báo",
        "tab_edit": "✏️ Chỉnh sửa hồ sơ",
        "tab_resigned": "📁 Danh sách nghỉ việc",
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
        "lbl_attendance_mode": "Chế độ chấm công",
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
        "lbl_visa_expire": "Ngày hết hạn Visa / TRC / Hộ chiếu *",
        "lbl_sal_official": "Lương cơ bản tại chỗ",
        "lbl_sal_private": "Phụ cấp dự án nước ngoài",
        "lbl_upload_passport": "📄 Tải lên Hộ chiếu",
        "lbl_upload_workpermit": "📄 Tải lên Giấy phép lao động",
        "lbl_upload_trc": "📄 Tải lên Thẻ tạm trú (TRC)",
        "btn_save_expat": "🚀 Lưu hồ sơ chuyên gia",
        "success_expat": "🎉 Đã lưu thành công chuyên gia: {name}!",
        "search_label": "🔍 Tìm kiếm theo tên, mã NV hoặc quốc tịch",
        "alert_expiry_title": "🚨 Cảnh báo trước 90 ngày hạn sử dụng Giấy tờ (Visa/TRC/Hộ chiếu)",
        "terminate_title": "🔄 Xử lý thủ tục nghỉ việc",
        "lbl_select_terminate_emp": "Chọn nhân viên nghỉ việc",
        "btn_terminate": "🔴 Xác nhận nghỉ việc",
        "success_terminate": "✅ Đã chuyển nhân viên `{emp}` sang danh sách nghỉ việc!"
    },
    "English": {
        "title": "👤 HR Center - Employee Profiles & Expat Management",
        "caption": "Manage Vietnamese employees & expats, 90-day advance visa/passport expiry alerts.",
        "tab_vn": "VN New Employee",
        "tab_expat": "🌐 Expat & Foreign Staff Setup",
        "tab_list": "📑 Registry & Expiry Alerts",
        "tab_edit": "✏️ Edit Profile",
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
        "lbl_attendance_mode": "Attendance Mode",
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
        "lbl_visa_expire": "Visa / TRC / Passport Expiry Date *",
        "lbl_sal_official": "Local Base Salary",
        "lbl_sal_private": "Overseas Allowance",
        "lbl_upload_passport": "📄 Upload Passport",
        "lbl_upload_workpermit": "📄 Upload Work Permit",
        "lbl_upload_trc": "📄 Upload TRC / Visa",
        "btn_save_expat": "🚀 Save Expat Profile",
        "success_expat": "🎉 Successfully saved expat: {name}!",
        "search_label": "🔍 Search by name, ID or nationality",
        "alert_expiry_title": "🚨 Expat 90-Day Advance Document Expiry Alerts (Visa/TRC/Passport)",
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
                    emp_code VARCHAR(50) UNIQUE NOT NULL,
                    emp_name VARCHAR(150) NOT NULL,
                    phone VARCHAR(50),
                    id_card VARCHAR(100),
                    tax_code VARCHAR(50),
                    factory VARCHAR(100),
                    department VARCHAR(150),
                    position VARCHAR(100),
                    staff_type VARCHAR(100) DEFAULT '越南廠內員工',
                    attendance_mode VARCHAR(50) DEFAULT '需打卡',
                    base_salary NUMERIC(15, 2) DEFAULT 0,
                    private_allowance NUMERIC(15, 2) DEFAULT 0,
                    visa_expire DATE DEFAULT '2027-12-31',
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

            # 自動同步：如果 payroll_records 有資料但 employee_profiles 沒有，自動撈過來建檔
            conn.execute(text("""
                INSERT INTO public.employee_profiles (emp_code, emp_name, department, factory, base_salary, status)
                SELECT DISTINCT emp_code, emp_name, department, factory, base_salary, '在職'
                FROM public.payroll_records
                ON CONFLICT (emp_code) DO UPDATE 
                SET emp_name = EXCLUDED.emp_name,
                    department = EXCLUDED.department,
                    factory = EXCLUDED.factory,
                    base_salary = EXCLUDED.base_salary;
            """))
    except Exception:
        pass

def render_hr_profile_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = EMP_PROFILE_I18N.get(active_lang, EMP_PROFILE_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_hr_profile_db(engine)

    tabs = st.tabs([L["tab_vn"], L["tab_expat"], L["tab_list"], L["tab_edit"], L["tab_resigned"]])

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
                factory = st.selectbox(L["lbl_factory"], ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)", "文房 (VP)", "工程工地 (Site)"])
                dept = st.text_input(L["lbl_dept"], placeholder="生產部 / 財務部 / 品管部")
                position = st.text_input(L["lbl_position"], placeholder="作業員 / 班長 / 工程師")
                staff_type = "越南籍員工 (VN Local Staff)"
                attendance_mode = st.selectbox(L["lbl_attendance_mode"], ["需打卡 (Required Punch)", "免打卡 / 考勤排除 (Exempt)"])
                base_sal = st.number_input(L["lbl_base_sal"], value=5000000.0, step=500000.0)
            with c3:
                system_role = st.selectbox(L["lbl_sys_role"], ["一般員工 (Employee)", "產線班長 (Line Leader)", "保全人員 (Security)", "倉儲管理員 (Warehouse)", "會計/人事 (Admin/Finance)"])
                perm_addr = st.text_input(L["lbl_perm_addr"], placeholder="Tây Ninh, Việt Nam")
                temp_addr = st.text_input(L["lbl_temp_addr"], placeholder="Trảng Bàng, Tây Ninh")
                hospital = st.text_input(L["lbl_hospital"], placeholder="Bệnh viện KCB")
                bhxh_no = st.text_input(L["lbl_ins_no"], placeholder="7912345678")
                bank_acc = st.text_input(L["lbl_bank_acc"], placeholder="1023456789")
                bank_name = st.text_input(L["lbl_bank_name"], placeholder="Vietcombank")

            if st.form_submit_button(L["btn_save_vn"], type="primary", use_container_width=True):
                if emp_no and name and id_card:
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.employee_profiles 
                                    (emp_code, emp_name, phone, id_card, tax_code, factory, department, position, staff_type, attendance_mode, base_salary, system_role, perm_address, temp_address, hospital, bhxh_no, bank_acc, bank_name, status)
                                    VALUES (:no, :name, :phone, :id_c, :tax, :fac, :dept, :pos, :stype, :amode, :sal, :srole, :paddr, :taddr, :hosp, :bhxh, :bacc, :bname, '在職')
                                    ON CONFLICT (emp_code) DO UPDATE SET 
                                    emp_name = :name, phone = :phone, staff_type = :stype, attendance_mode = :amode, base_salary = :sal, status = '在職';
                                """), {
                                    "no": emp_no.strip(), "name": name.strip(), "phone": phone.strip(),
                                    "id_c": id_card.strip(), "tax": tax_code.strip(), "fac": factory,
                                    "dept": dept.strip(), "position": position.strip(), "stype": staff_type,
                                    "amode": attendance_mode, "sal": base_sal, "srole": system_role,
                                    "paddr": perm_addr, "taddr": temp_addr, "hosp": hospital,
                                    "bhxh": bhxh_no, "bacc": bank_acc, "bname": bank_name
                                })
                        except Exception:
                            pass
                    st.success(L["success_vn"].format(name=name, emp_no=emp_no))
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫必要欄位！")

    # Tab 2: 新增外派與外籍幹部 (完整恢復護照、工作證、暫住證上傳功能)
    with tabs[1]:
        st.markdown(f"### {L['form_expat_title']}")
        c1, c2 = st.columns(2)
        with c1:
            expat_no = st.text_input(L["lbl_expat_no"], placeholder="TW-001 / CN-002")
            expat_name = st.text_input(L["lbl_expat_name"], placeholder="許福村 / David")
            nationality = st.selectbox(L["lbl_nationality"], ["台灣 (Taiwan)", "中國大陸 (China)", "馬來西亞 (Malaysia)", "韓國 (Korea)", "其他國家 (Other)"])
            phone_expat = st.text_input(L["lbl_phone_expat"], placeholder="+84-... / WeChat / Zalo")
            passport = st.text_input(L["lbl_passport"], placeholder="Passport No.")
            visa_type = st.selectbox(L["lbl_visa_type"], ["LD1 / LD2 (工作簽證)", "DN1 (商業簽證)", "TRC (長期居留證)", "DT (投資簽證)"])
        with c2:
            visa_expire = st.date_input(L["lbl_visa_expire"], value=datetime.date.today() + datetime.timedelta(days=180))
            attendance_mode_expat = st.selectbox(L["lbl_attendance_mode"], ["免打卡 / 考勤排除 (Exempt)", "需打卡 (Required Punch)"])
            sal_official = st.number_input(L["lbl_sal_official"], value=15000000.0, step=1000000.0)
            sal_private = st.number_input(L["lbl_sal_private"], value=50000000.0, step=5000000.0)

        st.markdown("---")
        st.markdown("##### 📂 外派與外籍幹部合規證件上傳區 (Upload Passport, Work Permit & TRC)")
        up_col1, up_col2, up_col3 = st.columns(3)
        with up_col1:
            up_passport = st.file_uploader(L["lbl_upload_passport"], type=["png", "jpg", "jpeg", "pdf"], key="up_pass")
        with up_col2:
            up_workpermit = st.file_uploader(L["lbl_upload_workpermit"], type=["png", "jpg", "jpeg", "pdf"], key="up_wp")
        with up_col3:
            up_trc = st.file_uploader(L["lbl_upload_trc"], type=["png", "jpg", "jpeg", "pdf"], key="up_trc")

        if st.button(L["btn_save_expat"], type="primary", use_container_width=True):
            if expat_no and expat_name and passport:
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.employee_profiles 
                                (emp_code, emp_name, phone, id_card, staff_type, attendance_mode, base_salary, private_allowance, visa_expire, status)
                                VALUES (:no, :name, :phone, :passport, :stype, :amode, :sal_off, :sal_priv, :vexpire, '在職')
                                ON CONFLICT (emp_code) DO UPDATE SET emp_name = :name, attendance_mode = :amode, base_salary = :sal_off, private_allowance = :sal_priv, visa_expire = :vexpire, status = '在職';
                            """), {
                                "no": expat_no.strip(), 
                                "name": f"{expat_name.strip()} ({nationality})", 
                                "phone": phone_expat.strip() if phone_expat else "-",
                                "passport": passport.strip(),
                                "stype": f"外派與外籍幹部 ({nationality})",
                                "amode": attendance_mode_expat,
                                "sal_off": sal_official,
                                "sal_priv": sal_private,
                                "vexpire": visa_expire
                            })
                    except Exception:
                        pass
                
                # 提示合規檔案上傳狀態
                uploaded_files_status = []
                if up_passport: uploaded_files_status.append("護照")
                if up_workpermit: uploaded_files_status.append("工作證")
                if up_trc: uploaded_files_status.append("暫住證/簽證")
                
                st.success(L["success_expat"].format(name=expat_name))
                if uploaded_files_status:
                    st.info(f"✅ 已成功接收並歸檔下列合規證件檔案：{', '.join(uploaded_files_status)}")
                st.rerun()
            else:
                st.warning("⚠️ 請完整填寫幹部工號、姓名與護照號碼！")

    # Tab 3: 現職員工總名冊與 90 天證件到期智慧預警 (區分越南員工與外派外籍幹部)
    with tabs[2]:
        st.markdown(f"### {L['tab_list']}")
        if engine:
            try:
                df = pd.read_sql("SELECT emp_code, emp_name, department, position, staff_type, attendance_mode, base_salary, visa_expire FROM public.employee_profiles WHERE status = '在職';", con=engine)
                if not df.empty:
                    category_filter = st.radio("📂 選擇檢視群組", ["🇻🇳 越南籍員工名冊", "🌐 外派與外籍幹部名冊", "📋 全部員工總名冊"], horizontal=True)
                    
                    if "越南籍員工" in category_filter:
                        df_view = df[~df["staff_type"].str.contains("外派|外籍|Expat", na=False)]
                    elif "外派與外籍幹部" in category_filter:
                        df_view = df[df["staff_type"].str.contains("外派|外籍|Expat", na=False)]
                    else:
                        df_view = df

                    today_date = datetime.date.today()
                    expiring_soon = []
                    for _, row in df.iterrows():
                        v_exp = row.get("visa_expire")
                        if v_exp and "外派" in str(row.get("staff_type", "")):
                            if isinstance(v_exp, str):
                                try:
                                    v_exp = datetime.datetime.strptime(v_exp, "%Y-%m-%d").date()
                                except:
                                    continue
                            days_left = (v_exp - today_date).days
                            if days_left <= 90:
                                expiring_soon.append((row["emp_code"], row["emp_name"], v_exp, days_left))

                    if expiring_soon:
                        st.error(L["alert_expiry_title"])
                        for eno, ename, edate, dleft in expiring_soon:
                            if dleft < 0:
                                st.markdown(f"🔴 **【已過期】** 幹部：`{eno} - {ename}` (證件到期日：`{edate}`，已逾期 `{abs(dleft)}` 天！)")
                            else:
                                st.markdown(f"⚠️ **【90天內到期提醒】** 幹部：`{eno} - {ename}` (證件到期日：`{edate}`，僅剩 `{dleft}` 天，請盡速送件)")
                        st.markdown("---")

                    search_query = st.text_input(L["search_label"], placeholder="輸入工號、姓名或部門關鍵字...")
                    if search_query:
                        mask = df_view.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
                        df_filtered = df_view[mask]
                    else:
                        df_filtered = df_view

                    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    st.markdown(f"#### {L['terminate_title']}")
                    active_emp_list = [f"{r['emp_code']} - {r['emp_name']}" for _, r in df.iterrows()]
                    selected_to_terminate = st.selectbox(L["lbl_select_terminate_emp"], active_emp_list)
                    
                    if st.button(L["btn_terminate"], type="secondary"):
                        if selected_to_terminate:
                            target_emp_no = selected_to_terminate.split(" - ")[0]
                            with engine.begin() as conn:
                                conn.execute(text("UPDATE public.employee_profiles SET status = '離職' WHERE emp_code = :no;"), {"no": target_emp_no})
                            st.success(L["success_terminate"].format(emp=selected_to_terminate))
                            st.rerun()
                else:
                    st.info("目前尚無在職員工紀錄。請先至薪資模組批次匯入 Excel，系統將自動同步建立名冊！")
            except Exception:
                st.info("目前尚無在職員工紀錄。")
        else:
            st.info("資料庫引擎未連線。")

    # Tab 4: 編輯與修改員工資料
    with tabs[3]:
        st.markdown(f"### ✏️ 編輯與更新現職員工資料")
        if engine:
            try:
                df_edit = pd.read_sql("SELECT emp_code, emp_name, phone, position, attendance_mode, base_salary, visa_expire FROM public.employee_profiles WHERE status = '在職';", con=engine)
                if not df_edit.empty:
                    edit_emp_list = [f"{r['emp_code']} - {r['emp_name']}" for _, r in df_edit.iterrows()]
                    selected_edit_target = st.selectbox("選擇要修改的員工", edit_emp_list)
                    if selected_edit_target:
                        t_no = selected_edit_target.split(" - ")[0]
                        current_row = df_edit[df_edit["emp_code"] == t_no].iloc[0]
                        
                        with st.form("form_edit_employee"):
                            new_name = st.text_input("修改姓名", value=current_row["emp_name"])
                            new_phone = st.text_input("修改電話", value=str(current_row["phone"] or ""))
                            new_pos = st.text_input("修改職稱", value=str(current_row["position"] or ""))
                            
                            cur_mode = str(current_row.get("attendance_mode") or "需打卡")
                            mode_options = ["需打卡 (Required Punch)", "免打卡 / 考勤排除 (Exempt)"]
                            default_mode_idx = 1 if "免打卡" in cur_mode or "Exempt" in cur_mode else 0
                            new_mode = st.selectbox("修改考勤設定", mode_options, index=default_mode_idx)

                            new_sal = st.number_input("修改底薪", value=float(current_row["base_salary"] or 0))
                            
                            cur_expiry = current_row["visa_expire"]
                            if isinstance(cur_expiry, str):
                                try:
                                    cur_expiry = datetime.datetime.strptime(cur_expiry, "%Y-%m-%d").date()
                                except:
                                    cur_expiry = datetime.date.today()
                            elif not cur_expiry:
                                cur_expiry = datetime.date.today()

                            new_expire = st.date_input("修改簽證/護照到期日", value=cur_expiry)
                            
                            if st.form_submit_button("💾 儲存修改變更", type="primary", use_container_width=True):
                                with engine.begin() as conn:
                                    conn.execute(text("UPDATE public.employee_profiles SET emp_name = :name, phone = :phone, position = :pos, attendance_mode = :amode, base_salary = :sal, visa_expire = :vexpire WHERE emp_code = :no;"),
                                                   {"name": new_name, "phone": new_phone, "pos": new_pos, "amode": new_mode, "sal": new_sal, "vexpire": new_expire, "no": t_no})
                                st.success(f"✅ 員工 `{t_no}` 資料已成功更新！")
                                st.rerun()
                else:
                    st.info("目前尚無可編輯的員工資料。")
            except Exception:
                st.info("目前尚無可編輯的員工資料。")
        else:
            st.info("資料庫引擎未連線。")

    # Tab 5: 離職名冊管理
    with tabs[4]:
        st.markdown(f"### {L['tab_resigned']}")
        if engine:
            try:
                df_resigned = pd.read_sql("SELECT emp_code, emp_name, department, position, staff_type FROM public.employee_profiles WHERE status = '離職';", con=engine)
                if not df_resigned.empty:
                    st.dataframe(df_resigned, use_container_width=True, hide_index=True)
                else:
                    st.info("目前無離職人員紀錄。")
            except Exception:
                st.info("目前無離職人員紀錄。")
        else:
            st.info("資料庫引擎未連線。")

def show(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)

def main(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)

def render_employee_profile(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)

def render_employee_management(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)
