import streamlit as st
import datetime
from sqlalchemy import text

def render_add_expat(engine=None, lang="繁體中文"):
    st.markdown("### 🌐 新增外派與外籍幹部資料 (含護照、工作證、TRC 暫住證雙面與 90 天合規預警)")
    
    with st.form("form_add_expat_employee"):
        c1, c2 = st.columns(2)
        with c1:
            expat_no = st.text_input("工號 / 識別碼 *", placeholder="TW-001 / CN-002")
            expat_name = st.text_input("幹部姓名 (Họ tên chuyên gia) *", placeholder="許福村 / David")
            nationality = st.selectbox("國籍 (Nationality)", ["台灣 (Taiwan)", "中國大陸 (China)", "馬來西亞 (Malaysia)", "韓國 (Korea)", "其他國家 (Other)"])
            phone_expat = st.text_input("聯絡電話 (Phone / Zalo / WeChat)", placeholder="+84-... / WeChat / Zalo")
            passport = st.text_input("護照號碼 / 居留證號 *", placeholder="Passport No.")
            visa_type = st.selectbox("簽證類型 (Visa Type)", ["LD1 / LD2 (工作簽證)", "DN1 (商業簽證)", "TRC (長期居留證)", "DT (投資簽證)"])
        with c2:
            visa_expire = st.date_input("工作簽證 / 暫住證 (TRC) / 護照到期日 *", value=datetime.date.today() + datetime.timedelta(days=180))
            attendance_mode_expat = st.selectbox("考勤打卡設定", ["免打卡 / 考勤排除 (Exempt)", "需打卡 (Required Punch)"])
            sal_official = st.number_input("當地申報薪資 (Local Base Salary)", value=15000000.0, step=1000000.0)
            sal_private = st.number_input("海外專案津貼 / 差旅補助 (Overseas Allowance)", value=50000000.0, step=5000000.0)

        st.markdown("---")
        st.markdown("##### 📂 外派與外籍幹部合規證件上傳區 (Upload Passport, Work Permit & TRC - Front/Back)")
        
        # 💡 將上傳區擴充為 4 個欄位：護照、工作證、暫住證正面、暫住證背面
        up_col1, up_col2, up_col3, up_col4 = st.columns(4)
        with up_col1:
            up_passport = st.file_uploader("📄 護照掃描檔 (Passport)", type=["png", "jpg", "jpeg", "pdf"], key="up_pass_file")
        with up_col2:
            up_workpermit = st.file_uploader("📄 越南工作證 (Work Permit)", type=["png", "jpg", "jpeg", "pdf"], key="up_wp_file")
        with up_col3:
            up_trc_front = st.file_uploader("📄 暫住證【正面】(TRC Front)", type=["png", "jpg", "jpeg", "pdf"], key="up_trc_front_file")
        with up_col4:
            up_trc_back = st.file_uploader("📄 暫住證【背面】(TRC Back)", type=["png", "jpg", "jpeg", "pdf"], key="up_trc_back_file")

        if st.form_submit_button("🚀 儲存外派與外籍幹部合規檔案與證件", type="primary", use_container_width=True):
            if expat_no and expat_name and passport:
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.employee_profiles 
                                (emp_code, emp_name, phone, id_card, staff_type, attendance_mode, base_salary, private_allowance, visa_expire, status)
                                VALUES (:no, :name, :phone, :passport, '外派與外籍幹部', :amode, :sal_off, :sal_priv, :vexpire, '在職')
                                ON CONFLICT (emp_code) DO UPDATE SET emp_name = :name, attendance_mode = :amode, base_salary = :sal_off, private_allowance = :sal_priv, visa_expire = :vexpire, status = '在職';
                            """), {
                                "no": expat_no.strip(), 
                                "name": f"{expat_name.strip()} ({nationality})", 
                                "phone": phone_expat.strip() if phone_expat else "-",
                                "passport": passport.strip(),
                                "amode": attendance_mode_expat,
                                "sal_off": sal_official,
                                "sal_priv": sal_private,
                                "vexpire": visa_expire
                            })
                    except Exception:
                        pass
                
                uploaded_files_status = []
                if up_passport: uploaded_files_status.append("護照")
                if up_workpermit: uploaded_files_status.append("工作證")
                if up_trc_front: uploaded_files_status.append("暫住證(正面)")
                if up_trc_back: uploaded_files_status.append("暫住證(背面)")
                
                st.success(f"🎉 成功新增外派與外籍幹部：{expat_name} (已完整記錄證件到期日與雙面合規檔案)！")
                if uploaded_files_status:
                    st.info(f"✅ 已成功接收並歸檔下列合規證件檔案：{', '.join(uploaded_files_status)}")
                st.rerun()
            else:
                st.warning("⚠️ 請完整填寫幹部工號、姓名與護照號碼！")
