import pandas as pd
import streamlit as st


def render_employee_management(engine=None, t=None, lang="繁體中文"):
    st.title("👤 管理部 - 員工與人事管理中心")
    st.caption("維護全廠區員工個人檔案、合約記錄、工作廠區、離職歸檔與 AI 人臉辨識打卡串接預留。")

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

    tab_manage, tab_add, tab_resigned = st.tabs([
        "📑 現有在職員工名冊",
        "➕ 新增員工個人檔案",
        "📦 離職人員檔案與歷史查詢"
    ])

    # ----------------------------------------------------
    # 📑 頁籤一：現有在職員工名冊
    # ----------------------------------------------------
    with tab_manage:
        st.markdown("### 📋 公司現有在職員工名冊（含 AI 人臉辨識串接欄位）")
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
    with tab_add:
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
                        "工務部 (Engineering - 設計/工程/品管)",
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

            face_token = st.text_input("🤖 AI 臉部辨識特徵代碼 (未來打卡系統串接預留)", value="FACE-PENDING-REGISTRATION")
            role = st.selectbox("系統權限角色 (Role)", ["Staff (一般員工)", "Manager (部門主管)", "Admin (系統管理者)"])

            submitted = st.form_submit_button("💾 儲存並新增個人檔案", type="primary", use_container_width=True)
            if submitted:
                if emp_name and emp_id:
                    # 💡 確保完整欄位寫入 session_state
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
                    st.success(f"🎉 【新增完成】已成功登錄員工 [{emp_name}] (`{emp_id}`)！請點擊上方左側的「現有在職員工名冊」頁籤即可檢視完整名單。")
                    st.rerun()  # 💡 強制重新整理頁面以立即渲染進表格
                else:
                    st.error("❌ 請完整填寫員工編號與姓名！")

    # ----------------------------------------------------
    # 📦 頁籤三：離職人員檔案與歷史查詢
    # ----------------------------------------------------
    with tab_resigned:
        st.markdown("### 📦 離職人員歷史檔案庫 (Resigned Employees Archive)")
        st.caption("所有離職或結案的員工資料均完整保留於此，方便日後隨時搜尋與查閱。")

        if st.session_state.resigned_employees_db:
            df_resigned = pd.DataFrame(st.session_state.resigned_employees_db)
            st.dataframe(df_resigned, use_container_width=True)
        else:
            st.info("目前尚無離職歸檔人員紀錄。")


def show(engine=None, t=None, lang="繁體中文"):
    render_employee_management(engine, t, lang)


def main(engine=None, t=None, lang="繁體中文"):
    render_employee_management(engine, t, lang)
