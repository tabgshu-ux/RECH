import datetime
import pandas as pd
import streamlit as st

def render_employee_management(engine=None, t=None, lang="繁體中文"):
    st.title("👤 管理部 - 員工與人事管理、智慧打卡及請假簽核中心")
    st.caption("維護全廠區員工個人檔案、合約記錄、工作廠區、離職歸檔、人臉/指紋打卡機資料彙集，以及請假單自動連動電子簽核系統。")

    if "employees_db" not in st.session_state or not st.session_state.employees_db:
        st.session_state.employees_db = [
            {
                "id": "EMP-001",
                "name": "張董事長",
                "nationality": "🇹🇼 台灣 (Taiwan)",
                "site": "西寧廠",
                "dept": "👑 經營高層 / 董事會與總經理室 (Executive Board)",
                "title": "董事長 (Chairman)",
                "role": "Chairman",
                "phone": "0912345678",
                "address": "-",
                "face_token": "FACE-BIO-888899",
            },
            {
                "id": "EMP-002",
                "name": "陳智賢",
                "nationality": "🇻🇳 越南 (Vietnamese)",
                "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)",
                "dept": "👑 經營高層 / 董事會與總經理室 (Executive Board)",
                "title": "總經理 (General Manager)",
                "role": "GeneralManager",
                "phone": "0918999080",
                "address": "-",
                "face_token": "FACE-BIO-100234",
            },
            {
                "id": "EMP-003",
                "name": "李元隆",
                "nationality": "🇹🇼 台灣 (Taiwanese)",
                "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)",
                "dept": "👔 經營主管 / 營運管理中心 (Management & Operations)",
                "title": "副總經理 (Vice General Manager)",
                "role": "ViceManager",
                "phone": "-",
                "address": "-",
                "face_token": "FACE-BIO-300451",
            },
        ]

    if "resigned_employees_db" not in st.session_state:
        st.session_state.resigned_employees_db = []

    if "biometric_attendance_logs" not in st.session_state:
        st.session_state.biometric_attendance_logs = [
            {"date": str(datetime.date.today()), "emp_id": "EMP-002", "name": "陳智賢", "device": "大門口人臉辨識機 #01", "check_type": "上班打卡 (Clock In)", "time": "07:55:20", "status": "🟢 正常"},
            {"date": str(datetime.date.today()), "emp_id": "EMP-003", "name": "李元隆", "device": "辦公室指紋機 #02", "check_type": "上班打卡 (Clock In)", "time": "08:12:45", "status": "🟡 遲到"},
        ]

    if "leave_requests_db" not in st.session_state:
        st.session_state.leave_requests_db = [
            {"req_id": "LEV-2026-001", "emp_id": "EMP-002", "name": "陳智賢", "leave_type": "事假 (Personal Leave)", "start_date": "2026-10-10", "end_date": "2026-10-10", "hours": 8.0, "reason": "家中有事需請假一天", "status": "⏳ 簽核中 (Pending)"}
        ]

    menu_mode = st.selectbox(
        "📌 請選擇人事管理功能模組：",
        [
            "📑 1. 現有在職員工名冊與詳細資料修改",
            "➕ 2. 登錄新員工個人檔案",
            "📤 3. Excel 批次匯入員工名冊",
            "📦 4. 離職人員歷史檔案庫",
            "⏰ 5. 廠區人臉/指紋打卡資料彙集",
            "📝 6. 請假申請與電子簽核連動"
        ]
    )

    st.markdown("---")

    if "1." in menu_mode:
        st.markdown("### 📋 公司現有在職員工名冊與詳細資料維護")
        st.info("💡 您可以隨時檢視清單，並在下方選擇特定員工進行詳細資料（電話、地址、人臉代碼等）的修改與更新。")

        df_emp = pd.DataFrame(st.session_state.employees_db)
        st.dataframe(df_emp, use_container_width=True)

        st.markdown("---")
        st.markdown("#### ✏️ 選擇員工並修改詳細資料")
        
        emp_options = [f"{e['id']} - {e['name']} ({e['title']})" for e in st.session_state.employees_db]
        if emp_options:
            selected_emp_str = st.selectbox("請選擇要編輯修改的員工", emp_options, key="edit_emp_select")
            selected_emp_id = selected_emp_str.split(" - ")[0]
            
            current_emp_data = next((e for e in st.session_state.employees_db if e["id"] == selected_emp_id), None)
            
            if current_emp_data:
                with st.form("form_edit_employee_detail"):
                    ec1, ec2, ec3 = st.columns(3)
                    with ec1:
                        edit_name = st.text_input("員工姓名 *", value=current_emp_data["name"])
                        edit_nat = st.selectbox("員工國籍", ["🇻🇳 越南 (Vietnamese)", "🇹🇼 台灣 (Taiwanese)", "🇨🇳 中國 (Chinese)", "其他國家"], index=0 if "越南" in current_emp_data["nationality"] else 1)
                    with ec2:
                        edit_site = st.selectbox("駐點工作廠區 *", ["🇻🇳 越南西寧廠 (Tay Ninh Plant)", "🇻🇳 越南海防廠 (Hai Phong Plant)", "台灣總公司"], index=0)
                        edit_dept = st.selectbox("所屬部門 / 單位 *", [
                            "👑 經營高層 / 董事會與總經理室 (Executive Board)",
                            "👔 經營主管 / 營運管理中心 (Management & Operations)",
                            "管理部 (Management - 行政/財務/採購)",
                            "工務部 (Engineering - 設計/工程/品管)",
                            "生產部 - 板金組 (Sheet Metal)",
                            "生產部 - 塗料組 (Painting)",
                            "生產部 - 配盤組 (Assembly)",
                        ])
                    with ec3:
                        edit_title = st.text_input("職位 / 職銜 *", value=current_emp_data["title"])
                        edit_role = st.selectbox("系統權限角色", ["Chairman", "GeneralManager", "ViceManager", "Director", "Manager", "Supervisor", "Staff", "Admin"])

                    ec4, ec5 = st.columns(2)
                    with ec4:
                        edit_phone = st.text_input("聯絡電話 (Phone)", value=current_emp_data["phone"])
                    with ec5:
                        edit_address = st.text_input("居住 / 戶籍地址 (Address)", value=current_emp_data["address"])

                    edit_face = st.text_input("🤖 AI 臉部辨識 / 指紋機特徵代碼", value=current_emp_data["face_token"])

                    if st.form_submit_button("💾 確認儲存此員工的修改變更", type="primary"):
                        for e in st.session_state.employees_db:
                            if e["id"] == selected_emp_id:
                                e["name"] = edit_name
                                e["nationality"] = edit_nat
                                e["site"] = edit_site
                                e["dept"] = edit_dept
                                e["title"] = edit_title
                                e["role"] = edit_role
                                e["phone"] = edit_phone
                                e["address"] = edit_address
                                e["face_token"] = edit_face
                        
                        st.success(f"🎉 【修改成功】員工 [{edit_name}] (`{selected_emp_id}`) 的詳細資料已更新儲存！")

    elif "2." in menu_mode:
        st.markdown("### ➕ 登錄新員工個人檔案")

        with st.form("form_add_employee"):
            c1, c2, c3 = st.columns(3)
            with c1:
                nationality = st.selectbox("員工國籍", ["🇻🇳 越南 (Vietnamese)", "🇹🇼 台灣 (Taiwanese)", "🇨🇳 中國 (Chinese)", "其他國家"])
                emp_id = st.text_input("員工編號 *", value="EMP-300")
            with c2:
                work_plant = st.selectbox("駐點工作廠區 *", ["🇻🇳 越南西寧廠 (Tay Ninh Plant)", "🇻🇳 越南海防廠 (Hai Phong Plant)", "台灣總公司"])
                emp_name = st.text_input("員工全名 *", value="")
            with c3:
                dept = st.selectbox("所屬部門 / 單位 *", [
                    "👑 經營高層 / 董事會與總經理室 (Executive Board)",
                    "👔 經營主管 / 營運管理中心 (Management & Operations)",
                    "管理部 (Management - 行政/財務/採購)",
                    "工務部 (Engineering - 設計/工程/品管)",
                    "生產部 - 板金組 (Sheet Metal)",
                    "生產部 - 塗料組 (Painting)",
                    "生產部 - 配盤組 (Assembly)",
                ])
                job_title = st.text_input("職位 / 職銜 (Job Title) *", value="經理 / 主管")

            c4, c5 = st.columns(2)
            with c4:
                phone = st.text_input("聯絡電話 (Phone)", value="")
                id_card = st.text_input("護照號碼 / 身分證字號", value="")
            with c5:
                address = st.text_input("居住 / 戶籍地址 (Address)", value="")
                work_permit = st.text_input("工作許可證 / 勞工證號", value="-")

            face_token = st.text_input("🤖 AI 臉部辨識 / 指紋機特徵代碼", value="FACE-PENDING-REGISTRATION")
            
            role_options = [
                "Chairman (董事長)", "GeneralManager (總經理)", "ViceManager (副總經理)",
                "Director (經營主管 / 協理)", "Manager (部門經理 / 主管)", "Supervisor (部門組長 / 課長)",
                "Staff (一般員工)", "Admin (系統管理者)"
            ]
            role_selected = st.selectbox("系統權限角色 (Role)", role_options)
            role_value = role_selected.split(" ")[0]

            submitted = st.form_submit_button("💾 儲存並新增個人檔案", type="primary", use_container_width=True)
            if submitted:
                if emp_name and emp_id:
                    new_employee = {
                        "id": emp_id, "name": emp_name, "nationality": nationality,
                        "site": work_plant, "dept": dept, "title": job_title,
                        "role": role_value, "phone": phone if phone else "-",
                        "address": address if address else "-", "face_token": face_token if face_token else "FACE-PENDING",
                    }
                    st.session_state.employees_db.append(new_employee)
                    st.success(f"🎉 【新增完成】已成功登錄 [{job_title}] [{emp_name}] (`{emp_id}`)！")
                else:
                    st.error("❌ 請完整填寫員工編號與姓名！")

    elif "3." in menu_mode:
        st.markdown("### 📤 上傳 Excel 檔案批次匯入員工資料庫")
        uploaded_file = st.file_uploader("選擇員工名冊 Excel 檔案", type=["xlsx", "csv"])
        
        if uploaded_file is not None:
            try:
                df_upload = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
                st.dataframe(df_upload.head(5), use_container_width=True)

                if st.button("🚀 確認並將資料全部匯入系統資料庫", type="primary"):
                    count = 0
                    for _, row in df_upload.iterrows():
                        emp_id = str(row.get("id", f"EMP-9{count}"))
                        emp_name = str(row.get("name", "未命名"))
                        if not any(e["id"] == emp_id for e in st.session_state.employees_db):
                            st.session_state.employees_db.append({
                                "id": emp_id, "name": emp_name, "nationality": "🇻🇳 越南 (Vietnamese)",
                                "site": "西寧廠", "dept": "👑 經營高層 / 董事會與總經理室 (Executive Board)",
                                "title": "技術員", "role": "Staff", "phone": "-", "address": "-", "face_token": "FACE-BIO"
                            })
                            count += 1
                    st.success(f"🎉 已成功匯入 {count} 筆員工資料！")
            except Exception as e:
                st.error(f"❌ 讀取錯誤: {str(e)}")

    elif "4." in menu_mode:
        st.markdown("### 📦 離職人員歷史檔案庫 (Resigned Employees Archive)")
        if st.session_state.resigned_employees_db:
            st.dataframe(pd.DataFrame(st.session_state.resigned_employees_db), use_container_width=True)
        else:
            st.info("目前尚無離職歸檔人員紀錄。")

    elif "5." in menu_mode:
        st.markdown("### ⏰ 廠區人臉辨識系統與指紋打卡機資料彙集中心")
        col_l1, col_l2, col_l3 = st.columns(3)
        col_l1.metric("今日總刷卡人數", f"{len(st.session_state.biometric_attendance_logs)} 人次")
        col_l2.metric("出勤異常/遲到", "1 人")
        col_l3.metric("設備狀態", "連線正常 (3/3)")
        st.dataframe(pd.DataFrame(st.session_state.biometric_attendance_logs), use_container_width=True)

    elif "6." in menu_mode:
        st.markdown("### 📝 員工請假申請與電子簽核連動中心")
        if st.session_state.leave_requests_db:
            st.dataframe(pd.DataFrame(st.session_state.leave_requests_db), use_container_width=True)
        else:
            st.info("目前沒有請假申請單。")

        st.markdown("---")
        with st.form("form_submit_leave_request"):
            c_lf1, c_lf2 = st.columns(2)
            with c_lf1:
                leave_emp_id = st.selectbox("申請員工", [f"{e['id']} - {e['name']}" for e in st.session_state.employees_db])
                leave_type = st.selectbox("請假類別 *", ["事假 (Personal Leave)", "病假 (Sick Leave)", "特休假 (Annual Leave)", "公出 (Official Business)"])
            with c_lf2:
                start_year = st.selectbox("開始年份", list(range(2000, 2031)), index=26)
                start_month = st.selectbox("開始月份", list(range(1, 13)), index=9)
                start_day = st.selectbox("開始日期", list(range(1, 32)), index=9)

            leave_hours = st.number_input("請假時數 (小時)", min_value=1.0, value=8.0)
            leave_reason = st.text_area("請假事由說明 *", "因個人私事需請假一天處理。")

            if st.form_submit_button("🚀 提交假單並連線至電子簽核中心"):
                leave_start_str = f"{start_year}-{start_month:02d}-{start_day:02d}"
                new_req_id = f"LEV-2026-{len(st.session_state.leave_requests_db)+1:03d}"
                emp_name_extracted = leave_emp_id.split(" - ")[1]
                
                st.session_state.leave_requests_db.append({
                    "req_id": new_req_id, "emp_id": leave_emp_id.split(" - ")[0],
                    "name": emp_name_extracted, "leave_type": leave_type,
                    "start_date": leave_start_str, "end_date": leave_start_str,
                    "hours": leave_hours, "reason": leave_reason, "status": "⏳ 簽核中 (Pending)"
                })
                st.success(f"🎉 請假單 `{new_req_id}` 已成功送出並連線至電子簽核中心！")

def show(engine=None, t=None, lang="繁體中文"):
    render_employee_management(engine, t, lang)

def main(engine=None, t=None, lang="繁體中文"):
    render_employee_management(engine, t, lang)
