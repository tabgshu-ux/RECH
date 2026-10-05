import datetime
import pandas as pd
import streamlit as st


def render_employee_management(engine=None, t=None, lang="繁體中文"):
    st.title("👤 管理部 - 員工與人事管理、智慧打卡及請假簽核中心")
    st.caption("維護全廠區員工個人檔案、合約記錄、工作廠區、離職歸檔、人臉/指紋打卡機資料彙集，以及請假單自動連動電子簽核系統。")

    # 1. 初始化在職員工資料庫
    if "employees_db" not in st.session_state or not st.session_state.employees_db:
        st.session_state.employees_db = [
            {
                "id": "EMP-001",
                "name": "張董事長",
                "nationality": "🇹🇼 台灣 (Taiwan)",
                "site": "西寧廠",
                "dept": "經營高層 / 董事會 (Executive)",
                "title": "董事長 (Chairman)",
                "role": "Admin",
                "phone": "0912345678",
                "address": "-",
                "face_token": "FACE-BIO-888899",
            },
            {
                "id": "EMP-002",
                "name": "Nguyễn Văn An",
                "nationality": "🇻🇳 越南 (Vietnamese)",
                "site": "西寧廠",
                "dept": "工程部",
                "title": "kỹ sư Tủ điện",
                "role": "Staff",
                "phone": "0987654321",
                "address": "-",
                "face_token": "FACE-BIO-100234",
            },
            {
                "id": "EMP-003",
                "name": "李元隆",
                "nationality": "🇹🇼 台灣 (Taiwanese)",
                "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)",
                "dept": "管理部 (Management - 行政/財務/採購)",
                "title": "副總",
                "role": "Staff",
                "phone": "-",
                "address": "-",
                "face_token": "FACE-BIO-300451",
            },
        ]

    # 2. 初始化離職員工歸檔資料庫
    if "resigned_employees_db" not in st.session_state:
        st.session_state.resigned_employees_db = []

    # 3. 初始化廠區人臉辨識/指紋打卡機彙集記錄
    if "biometric_attendance_logs" not in st.session_state:
        st.session_state.biometric_attendance_logs = [
            {"date": str(datetime.date.today()), "emp_id": "EMP-002", "name": "Nguyễn Văn An", "device": "大門口人臉辨識機 #01", "check_type": "上班打卡 (Clock In)", "time": "07:55:20", "status": "🟢 正常"},
            {"date": str(datetime.date.today()), "emp_id": "EMP-003", "name": "李元隆", "device": "辦公室指紋機 #02", "check_type": "上班打卡 (Clock In)", "time": "08:12:45", "status": "🟡 遲到"},
        ]

    # 4. 初始化請假申請記錄
    if "leave_requests_db" not in st.session_state:
        st.session_state.leave_requests_db = [
            {"req_id": "LEV-2026-001", "emp_id": "EMP-002", "name": "Nguyễn Văn An", "leave_type": "事假 (Personal Leave)", "start_date": "2026-10-10", "end_date": "2026-10-10", "hours": 8.0, "reason": "家中有事需請假一天", "status": "⏳ 簽核中 (Pending)"}
        ]

    # 5. 初始化頁籤切換狀態
    if "emp_active_tab" not in st.session_state:
        st.session_state.emp_active_tab = 0

    if "emp_success_msg" not in st.session_state:
        st.session_state.emp_success_msg = ""

    # 五個分頁標題（包含原有 3 個 + 新增的 2 個智慧打卡與請假連動）
    tab_titles = [
        "📑 現有在職員工名冊",
        "➕ 新增員工個人檔案",
        "📦 離職人員檔案與歷史查詢",
        "⏰ 廠區人臉/指紋打卡資料彙集",
        "📝 請假申請與電子簽核連動"
    ]
    
    selected_tab_name = st.radio(
        "選擇操作模式", 
        tab_titles, 
        index=st.session_state.emp_active_tab, 
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if selected_tab_name == tab_titles[0]:
        st.session_state.emp_active_tab = 0
    elif selected_tab_name == tab_titles[1]:
        st.session_state.emp_active_tab = 1
    elif selected_tab_name == tab_titles[2]:
        st.session_state.emp_active_tab = 2
    elif selected_tab_name == tab_titles[3]:
        st.session_state.emp_active_tab = 3
    else:
        st.session_state.emp_active_tab = 4

    st.markdown("---")

    if st.session_state.emp_success_msg:
        st.success(st.session_state.emp_success_msg)
        st.session_state.emp_success_msg = ""

    # ----------------------------------------------------
    # 📑 頁籤一：現有在職員工名冊
    # ----------------------------------------------------
    if st.session_state.emp_active_tab == 0:
        st.markdown("### 📋 公司現有在職員工名冊（含 AI 人臉辨識與指紋 ID 串接欄位）")
        st.info("💡 請在表格左側勾選目標員工，然後點擊下方對應的處理按鈕進行刪除或離職歸檔。")

        df_emp = pd.DataFrame(st.session_state.employees_db)
        if "選取" not in df_emp.columns:
            df_emp.insert(0, "選取", False)

        edited_emp_df = st.data_editor(
            df_emp,
            use_container_width=True,
            num_rows="dynamic",
            key="employee_editor"
        )

        col_b1, col_b2, _ = st.columns([1.5, 1.5, 2])
        with col_b1:
            if st.button("🗑️ 刪除選定項目", use_container_width=True, type="primary"):
                remaining_emp = []
                del_count = 0
                for idx, row in edited_emp_df.iterrows():
                    if row.get("選取", False):
                        del_count += 1
                    else:
                        emp_id = row["id"]
                        matched = next((e for e in st.session_state.employees_db if e.get("id") == emp_id and e.get("name") == row["name"]), None)
                        if matched:
                            remaining_emp.append(matched)
                
                st.session_state.employees_db = remaining_emp
                if del_count > 0:
                    st.success(f"✅ 已成功刪除 {del_count} 筆勾選的資料！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請先在表格左側勾選要刪除的對象。")

        with col_b2:
            if st.button("📁 辦理離職歸檔", use_container_width=True):
                remaining_emp = []
                moved_count = 0
                for idx, row in edited_emp_df.iterrows():
                    if row.get("選取", False):
                        emp_id = row["id"]
                        matched = next((e for e in st.session_state.employees_db if e.get("id") == emp_id and e.get("name") == row["name"]), None)
                        if matched:
                            matched["resigned_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
                            matched["reason"] = "正常離職辦理歸檔"
                            st.session_state.resigned_employees_db.append(matched)
                            moved_count += 1
                    else:
                        emp_id = row["id"]
                        matched = next((e for e in st.session_state.employees_db if e.get("id") == emp_id and e.get("name") == row["name"]), None)
                        if matched:
                            remaining_emp.append(matched)
                
                st.session_state.employees_db = remaining_emp
                if moved_count > 0:
                    st.success(f"✅ 已成功將 {moved_count} 位勾選的員工移至離職名單！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請先在表格左側勾選要辦理離職的對象。")

    # ----------------------------------------------------
    # ➕ 頁籤二：新增員工個人檔案
    # ----------------------------------------------------
    elif st.session_state.emp_active_tab == 1:
        st.markdown("### ➕ 登錄新員工個人檔案")

        with st.form("form_add_employee"):
            c1, c2, c3 = st.columns(3)
            with c1:
                nationality = st.selectbox(
                    "員工國籍",
                    ["🇻🇳 越南 (Vietnamese)", "🇹🇼 台灣 (Taiwanese)", "🇨🇳 中國 (Chinese)", "其他國家"]
                )
                emp_id = st.text_input("員工編號 *", value="EMP-300")
            with c2:
                work_plant = st.selectbox(
                    "駐點工作廠區 *",
                    ["🇻🇳 越南西寧廠 (Tay Ninh Plant)", "🇻🇳 越南海防廠 (Hai Phong Plant)"]
                )
                emp_name = st.text_input("員工全名 *", value="")
            with c3:
                dept = st.selectbox(
                    "所屬部門 / 單位 *",
                    [
                        "管理部 (Management - 行政/財務/採購)",
                        "工程部 (Engineering - 設計/工程/品管)",
                        "生產部 - 板金組 (Sheet Metal)",
                        "生產部 - 塗料組 (Painting)",
                        "生產部 - 配盤組 (Assembly)",
                    ]
                )
                job_title = st.text_input("職位 / 職銜 (Job Title) *", value="經理")

            c4, c5 = st.columns(2)
            with c4:
                phone = st.text_input("聯絡電話 (Phone)", value="")
                id_card = st.text_input("護照號碼 / 身分證字號", value="")
            with c5:
                address = st.text_input("居住 / 戶籍地址 (Address)", value="")
                work_permit = st.text_input("工作許可證 / 勞工證號", value="-")

            face_token = st.text_input("🤖 AI 臉部辨識 / 指紋機特徵代碼 (未來打卡系統串接預留)", value="FACE-PENDING-REGISTRATION")
            role = st.selectbox("系統權限角色 (Role)", ["Staff (一般員工)", "Manager (部門主管)", "Admin (系統管理者)"])

            submitted = st.form_submit_button("💾 儲存並新增個人檔案", type="primary", use_container_width=True)
            if submitted:
                if emp_name and emp_id:
                    new_employee = {
                        "id": emp_id,
                        "name": emp_name,
                        "nationality": nationality,
                        "site": work_plant,
                        "dept": dept,
                        "title": job_title,
                        "role": role.split(" ")[0],
                        "phone": phone if phone else "-",
                        "address": address if address else "-",
                        "face_token": face_token if face_token else "FACE-PENDING",
                    }
                    st.session_state.employees_db.append(new_employee)
                    
                    st.session_state.emp_success_msg = f"🎉 【新增完成】已成功登錄員工 [{emp_name}] (`{emp_id}`)！"
                    st.session_state.emp_active_tab = 0
                    st.rerun()
                else:
                    st.error("❌ 請完整填寫員工編號與姓名！")

    # ----------------------------------------------------
    # 📦 頁籤三：離職人員檔案與歷史查詢
    # ----------------------------------------------------
    elif st.session_state.emp_active_tab == 2:
        st.markdown("### 📦 離職人員歷史檔案庫 (Resigned Employees Archive)")
        st.caption("所有離職或結案的員工資料均完整保留於此，方便日後隨時搜尋與查閱。")

        if st.session_state.resigned_employees_db:
            df_resigned = pd.DataFrame(st.session_state.resigned_employees_db)
            st.dataframe(df_resigned, use_container_width=True)
        else:
            st.info("目前尚無離職歸檔人員紀錄。")

    # ----------------------------------------------------
    # ⏰ 頁籤四：廠區人臉/指紋打卡資料彙集中心 (新增)
    # ----------------------------------------------------
    elif st.session_state.emp_active_tab == 3:
        st.markdown("### ⏰ 廠區人臉辨識系統與指紋打卡機資料彙集中心")
        st.caption("即時匯集各廠區生物辨識打卡機之刷卡記錄，自動判定出勤狀態。")

        col_l1, col_l2, col_l3 = st.columns(3)
        col_l1.metric("今日總刷卡人數", f"{len(st.session_state.biometric_attendance_logs)} 人次", "🟢 數據同步中")
        col_l2.metric("出勤異常/遲到", "1 人", "需主管留意")
        col_l3.metric("生物辨識設備狀態", "連線正常 (3/3)", "人臉/指紋機連線中")

        st.markdown("---")
        st.markdown("#### 📋 即時刷卡記錄清單")
        if st.session_state.biometric_attendance_logs:
            st.dataframe(pd.DataFrame(st.session_state.biometric_attendance_logs), use_container_width=True)
        else:
            st.info("今日尚無刷卡記錄。")

        with st.expander("🔌 模擬從人臉辨識/指紋機同步最新打卡資料"):
            if st.button("🔄 立即向硬體打卡機發動同步抓取", key="btn_sync_bio"):
                st.success("✅ 成功自西寧廠人臉辨識主機同步最新打卡資料！")
                st.rerun()

    # ----------------------------------------------------
    # 📝 頁籤五：請假申請與電子簽核連動 (新增)
    # ----------------------------------------------------
    elif st.session_state.emp_active_tab == 4:
        st.markdown("### 📝 員工請假申請與電子簽核連動中心")
        st.caption("員工提交請假單後，系統將自動送交『電子簽核中心』，經主管核准後自動生效。")

        if st.session_state.leave_requests_db:
            st.markdown("#### 📊 現有請假申請單與簽核狀態")
            st.dataframe(pd.DataFrame(st.session_state.leave_requests_db), use_container_width=True)
        else:
            st.info("目前沒有請假申請單。")

        st.markdown("---")
        st.markdown("#### ➕ 填寫新請假單並送出電子簽核")
        with st.form("form_submit_leave_request"):
            c_lf1, c_lf2 = st.columns(2)
            with c_lf1:
                leave_emp_id = st.selectbox("申請員工", [f"{e['id']} - {e['name']}" for e in st.session_state.employees_db])
                leave_type = st.selectbox("請假類別 *", ["事假 (Personal Leave)", "病假 (Sick Leave)", "特休假 (Annual Leave)", "公出 (Official Business)"])
            with c_lf2:
                leave_start = st.date_input("開始日期", datetime.date.today())
                leave_end = st.date_input("結束日期", datetime.date.today())
            
            leave_hours = st.number_input("請假時數 (小時)", min_value=1.0, value=8.0)
            leave_reason = st.text_area("請假事由說明 *", "因個人私事需請假一天處理。")

            if st.form_submit_button("🚀 提交假單並連線至電子簽核中心"):
                new_req_id = f"LEV-2026-{len(st.session_state.leave_requests_db)+1:03d}"
                emp_name_extracted = leave_emp_id.split(" - ")[1]
                
                # 1. 寫入請假資料庫
                st.session_state.leave_requests_db.append({
                    "req_id": new_req_id,
                    "emp_id": leave_emp_id.split(" - ")[0],
                    "name": emp_name_extracted,
                    "leave_type": leave_type,
                    "start_date": str(leave_start),
                    "end_date": str(leave_end),
                    "hours": leave_hours,
                    "reason": leave_reason,
                    "status": "⏳ 簽核中 (Pending)"
                })

                # 2. 自動同步連動寫入全局電子簽核中心 (`approval_center_data` 或 `approval_workflow`)
                if "approval_center_data" not in st.session_state:
                    st.session_state.approval_center_data = []
                
                st.session_state.approval_center_data.insert(0, {
                    "單號": new_req_id,
                    "申請項目": f"員工請假申請 ({leave_type})",
                    "申請人": emp_name_extracted,
                    "金額/天數": f"{leave_hours} 小時",
                    "狀態": "簽核中",
                    "日期": str(datetime.date.today())
                })

                st.success(f"🎉 請假單 `{new_req_id}` 已成功送出，並已同步連動至『管理部 - 電子簽核中心』等待主管審核！")
                st.rerun()


def show(engine=None, t=None, lang="繁體中文"):
    render_employee_management(engine, t, lang)


def main(engine=None, t=None, lang="繁體中文"):
    render_employee_management(engine, t, lang)
