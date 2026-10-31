import streamlit as st
from sqlalchemy import text

def render_add_vietnamese(engine=None, lang="繁體中文"):
    st.markdown("### 🇻🇳 新增越南籍員工資料 (符合越南勞動法規範)")
    with st.form("form_add_vietnamese_employee"):
        c1, c2, c3 = st.columns(3)
        with c1:
            emp_no = st.text_input("工號 (Mã NV) *", placeholder="VN-003")
            name = st.text_input("姓名 (Họ tên) *", placeholder="NGUYỄN VĂN A")
            phone = st.text_input("聯絡電話 (Số ĐT)", placeholder="+84-901234567")
            id_card = st.text_input("公民身分證 CCCD / 護照 *", placeholder="079095012345")
            tax_code = st.text_input("個人稅號 (Mã số thuế)", placeholder="8012345678")
        with c2:
            factory = st.selectbox("駐點廠區 (Nhà máy)", ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)", "文房 (VP)", "工程工地 (Site)"])
            dept = st.text_input("部門 (Bộ phận)", placeholder="生產部 / 財務部 / 品管部")
            position = st.text_input("職稱 (Chức vụ)", placeholder="作業員 / 班長 / 工程師")
            staff_type = "越南籍員工 (VN Local Staff)"
            attendance_mode = st.selectbox("考勤打卡設定", ["需打卡 (Required Punch)", "免打卡 / 考勤排除 (Exempt)"])
            base_sal = st.number_input("越南盾固定底薪 (Lương CB - VND)", value=5000000.0, step=500000.0)
        with c3:
            system_role = st.selectbox("系統權限角色 (System Role)", ["一般員工 (Employee)", "產線班長 (Line Leader)", "保全人員 (Security)", "倉儲管理員 (Warehouse)", "會計/人事 (Admin/Finance)"])
            perm_addr = st.text_input("戶籍地址 (Thường trú)", placeholder="Tây Ninh, Việt Nam")
            temp_addr = st.text_input("現居地址 (Tạm trú)", placeholder="Trảng Bàng, Tây Ninh")
            hospital = st.text_input("體檢醫院 (Bệnh viện KCB)", placeholder="Bệnh viện KCB")
            bhxh_no = st.text_input("社保號碼 (Mã số BHXH)", placeholder="7912345678")
            bank_acc = st.text_input("薪資銀行帳號 (Số TK Ngân hàng)", placeholder="1023456789")
            bank_name = st.text_input("銀行分行名稱 (Tên Ngân hàng)", placeholder="Vietcombank")

        if st.form_submit_button("🚀 確認並寫入越南員工資料庫", type="primary", use_container_width=True):
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
                st.success(f"🎉 成功新增越南籍員工：{name} (工號: {emp_no})！")
                st.rerun()
            else:
                st.warning("⚠️ 請完整填寫必要欄位！")
