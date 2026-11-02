import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def render_edit_profile(engine=None, lang="繁體中文"):
    st.markdown("### ✏️ 編輯與更新現職員工資料 (支援身分切換與合規證件更新)")
    if engine:
        try:
            # 🛡️ 自動補全所有可能缺少的欄位
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS staff_type VARCHAR(100) DEFAULT '越南籍員工';"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS attendance_mode VARCHAR(50) DEFAULT '需打卡';"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS visa_expire DATE DEFAULT '2027-12-31';"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS private_allowance NUMERIC(15, 2) DEFAULT 0;"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS tax_code VARCHAR(50);"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS perm_address TEXT;"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS temp_address TEXT;"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS hospital VARCHAR(150);"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS bhxh_no VARCHAR(100);"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS bank_acc VARCHAR(100);"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS bank_name VARCHAR(150);"))

            df_edit = pd.read_sql("""
                SELECT emp_code, emp_name, phone, id_card, tax_code, factory, department, 
                       position, staff_type, attendance_mode, base_salary, private_allowance, 
                       visa_expire, perm_address, temp_address, hospital, bhxh_no, bank_acc, bank_name 
                FROM public.employee_profiles 
                WHERE status = '在職';
            """, con=engine)
            
            if not df_edit.empty:
                edit_emp_list = [f"{r['emp_code']} - {r['emp_name']} ({r.get('staff_type', '越南籍員工')})" for _, r in df_edit.iterrows()]
                selected_edit_target = st.selectbox("選擇要修改的員工 (Chọn nhân viên)", edit_emp_list)
                
                if selected_edit_target:
                    t_no = selected_edit_target.split(" - ")[0]
                    current_row = df_edit[df_edit["emp_code"] == t_no].iloc[0]
                    
                    cur_staff_type = str(current_row.get("staff_type", "越南籍員工"))

                    with st.form("form_edit_employee"):
                        st.markdown("#### 📌 員工基本與身分屬性設定")
                        
                        # 💡 允許直接手動切換身分屬性，解決表格不變的問題！
                        staff_type_options = ["越南籍員工", "外派與外籍幹部"]
                        default_type_idx = 1 if any(k in cur_staff_type for k in ["外派", "外籍", "Expat"]) else 0
                        new_staff_type = st.selectbox("員工身分類型 (Staff Type) *", staff_type_options, index=default_type_idx)
                        
                        is_expat_now = "外派" in new_staff_type or "外籍" in new_staff_type

                        col1, col2 = st.columns(2)
                        with col1:
                            new_emp_code = st.text_input("修改員工編號 (工號)", value=str(current_row["emp_code"]))
                            new_name = st.text_input("修改姓名", value=str(current_row["emp_name"] or ""))
                            new_phone = st.text_input("修改電話", value=str(current_row["phone"] or ""))
                            new_pos = st.text_input("修改職稱", value=str(current_row["position"] or ""))
                        with col2:
                            new_sal = st.number_input("修改固定底薪 (VND)", value=float(current_row["base_salary"] or 0), step=500000.0)
                            cur_mode = str(current_row.get("attendance_mode") or "需打卡")
                            mode_options = ["需打卡 (Required Punch)", "免打卡 / 考勤排除 (Exempt)"]
                            default_mode_idx = 1 if "免打卡" in cur_mode or "Exempt" in cur_mode else 0
                            new_mode = st.selectbox("修改考勤設定", mode_options, index=default_mode_idx)

                        st.markdown("---")
                        
                        # 🌐 若為外派/外籍幹部，動態顯示合規欄位與雙面證件更新上傳區
                        if is_expat_now:
                            st.markdown("##### 🌐 外派與外籍幹部專用合規欄位與證件更新")
                            c_ex1, c_ex2 = st.columns(2)
                            with c_ex1:
                                new_passport = st.text_input("修改護照號碼 / 居留證號", value=str(current_row["id_card"] or ""))
                                new_priv_allowance = st.number_input("修改海外專案津貼 / 差旅補助", value=float(current_row["private_allowance"] or 0), step=1000000.0)
                            with c_ex2:
                                cur_expiry = current_row["visa_expire"]
                                if isinstance(cur_expiry, str):
                                    try:
                                        cur_expiry = datetime.datetime.strptime(cur_expiry, "%Y-%m-%d").date()
                                    except:
                                        cur_expiry = datetime.date.today()
                                elif not cur_expiry:
                                    cur_expiry = datetime.date.today()

                                new_expire = st.date_input("修改簽證 / TRC / 護照到期日", value=cur_expiry)
                            
                            st.markdown("##### 📂 更新外籍幹部合規證件與照片 (Passport, Work Permit & TRC Front/Back)")
                            up1, up2, up3, up4 = st.columns(4)
                            with up1:
                                up_pass = st.file_uploader("📄 更新護照", type=["png", "jpg", "jpeg", "pdf"], key="edit_pass")
                            with up2:
                                up_wp = st.file_uploader("📄 更新工作證", type=["png", "jpg", "jpeg", "pdf"], key="edit_wp")
                            with up3:
                                up_trc_f = st.file_uploader("📄 更新暫住證【正面】", type=["png", "jpg", "jpeg", "pdf"], key="edit_trc_f")
                            with up4:
                                up_trc_b = st.file_uploader("📄 更新暫住證【背面】", type=["png", "jpg", "jpeg", "pdf"], key="edit_trc_b")

                            new_perm, new_temp, new_hosp, new_bhxh, new_tax, new_bank_acc, new_bank_name = "", "", "", "", "", "", ""

                        # 🇻🇳 若為越南籍員工，顯示勞動法規與保險欄位
                        else:
                            st.markdown("##### 🇻🇳 越南籍員工專用勞動法規與保險欄位")
                            c_vn1, c_vn2 = st.columns(2)
                            with c_vn1:
                                new_id_card = st.text_input("修改公民身分證 (CCCD)", value=str(current_row["id_card"] or ""))
                                new_tax_code = st.text_input("修改個人稅號 (Mã số thuế)", value=str(current_row["tax_code"] or ""))
                                new_bhxh = st.text_input("修改社保號碼 (Mã số BHXH)", value=str(current_row["bhxh_no"] or ""))
                                new_hosp = st.text_input("修改健保就診醫院 (Bệnh viện KCB)", value=str(current_row["hospital"] or ""))
                            with c_vn2:
                                new_perm = st.text_input("修改戶籍地址 (Thường trú)", value=str(current_row["perm_address"] or ""))
                                new_temp = st.text_input("修改現居地址 (Tạm trú)", value=str(current_row["temp_address"] or ""))
                                new_bank_acc = st.text_input("修改銀行帳號", value=str(current_row["bank_acc"] or ""))
                                new_bank_name = st.text_input("修改銀行分行名稱", value=str(current_row["bank_name"] or ""))

                            new_passport = new_id_card
                            new_priv_allowance = 0.0
                            new_expire = datetime.date(2027, 12, 31)
                            new_tax = new_tax_code

                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.form_submit_button("💾 確認並儲存修改變更", type="primary", use_container_width=True):
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    UPDATE public.employee_profiles 
                                    SET emp_code = :new_code,
                                        emp_name = :name, 
                                        phone = :phone, 
                                        position = :pos, 
                                        staff_type = :stype,
                                        attendance_mode = :amode, 
                                        base_salary = :sal,
                                        id_card = :id_card,
                                        private_allowance = :priv_sal,
                                        visa_expire = :vexpire,
                                        tax_code = :tax,
                                        perm_address = :paddr,
                                        temp_address = :taddr,
                                        hospital = :hosp,
                                        bhxh_no = :bhxh,
                                        bank_acc = :bacc,
                                        bank_name = :bname
                                    WHERE emp_code = :old_code;
                                """), {
                                    "new_code": new_emp_code.strip(),
                                    "name": new_name.strip(),
                                    "phone": new_phone.strip(),
                                    "pos": new_pos.strip(),
                                    "stype": new_staff_type,
                                    "amode": new_mode,
                                    "sal": new_sal,
                                    "id_card": new_passport.strip(),
                                    "priv_sal": new_priv_allowance,
                                    "vexpire": new_expire,
                                    "tax": new_tax if not is_expat_now else "",
                                    "paddr": new_perm,
                                    "taddr": new_temp,
                                    "hosp": new_hosp,
                                    "bhxh": new_bhxh if not is_expat_now else "",
                                    "bacc": new_bank_acc,
                                    "bname": new_bank_name,
                                    "old_code": t_no
                                })
                            st.success(f"✅ 員工 `{new_name}` 資料與身分屬性（`{new_staff_type}`）已成功更新！")
                            st.rerun()
            else:
                st.info("目前尚無可編輯的員工資料。")
        except Exception as e:
            st.warning(f"⚠️ 讀取或更新發生異常：{str(e)}")
    else:
        st.info("資料庫引擎未連線。")
