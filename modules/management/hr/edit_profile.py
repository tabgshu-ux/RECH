import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def render_edit_profile(engine=None, lang="繁體中文"):
    st.markdown("### ✏️ 編輯與更新現職員工資料")
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
