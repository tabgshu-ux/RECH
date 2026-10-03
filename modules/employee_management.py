import pandas as pd
import streamlit as st


def render_employee_management(engine=None, t=None, lang="繁體中文"):
    st.title("👤 管理部 - 員工與人事管理中心")
    st.caption("維護全廠區員工個人檔案、合約記錄、工作廠區與離職人員歸檔查詢。")

    # 1. 初始化在職員工資料庫
    if "employees_db" not in st.session_state or not st.session_state.employees_db:
        st.session_state.employees_db = [
            {
                "id": "EMP-001",
                "name": "張偉豪",
                "nationality": "🇹🇼 台灣 (Taiwan)",
                "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)",
                "dept": "管理部 (Management)",
                "title": "廠長 / 專案經理",
                "role": "Manager",
                "phone": "+84 90 123 4567",
                "address": "Tây Ninh, Vietnam",
            },
            {
                "id": "EMP-002",
                "name": "Nguyễn Văn An",
                "nationality": "🇻🇳 越南 (Vietnamese)",
                "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)",
                "dept": "生產部 - 板金組 (Sheet Metal)",
                "title": "CNC 操作技術員",
                "role": "Staff",
                "phone": "+84 98 765 4321",
                "address": "Bến Cầu, Tây Ninh",
            },
            {
                "id": "EMP-003",
                "name": "Trần Thị Mai",
                "nationality": "🇻🇳 越南 (Vietnamese)",
                "site": "🇻🇳 越南海防廠 (Hai Phong Plant)",
                "dept": "工務部 - 品管組 (QC)",
                "title": "品管檢驗員",
                "role": "Staff",
                "phone": "+84 91 234 5678",
                "address": "Hải Phòng, Vietnam",
            },
        ]

    # 2. 初始化離職員工歸檔資料庫
    if "resigned_employees_db" not in st.session_state:
        st.session_state.resigned_employees_db = [
            {
                "id": "EMP-999",
                "name": "陳舊員工",
                "nationality": "🇻🇳 越南 (Vietnamese)",
                "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)",
                "dept": "生產部 - 塗料組 (Painting)",
                "title": "噴漆技術員",
                "resigned_date": "2026-06-30",
                "reason": "個人生涯規劃離職",
            }
        ]

    tab_manage, tab_add, tab_resigned = st.tabs([
        "📑 現有在職員工名冊",
        "➕ 新增員工個人檔案",
        "📦 離職人員檔案與歷史查詢"
    ])

    # ----------------------------------------------------
    # 📑 頁籤一：現有在職員工名冊（支援勾選移至離職名單）
    # ----------------------------------------------------
    with tab_manage:
        st.markdown("### 📋 公司現有在職員工名冊")
        st.info("💡 勾選欲離職的員工後，點擊下方按鈕即可將其完整資料移至「離職人員檔案與歷史查詢」中永久保存。")

        df_emp = pd.DataFrame(st.session_state.employees_db)
        if "離職辦理" not in df_emp.columns:
            df_emp.insert(0, "離職辦理", False)

        edited_emp_df = st.data_editor(
            df_emp,
            use_container_width=True,
            num_rows="dynamic",
            key="employee_editor"
        )

        c_btn1, _ = st.columns(2)
        with c_btn1:
            if st.button("📁 將勾選的員工移至離職名單", type="primary"):
                remaining_emp = []
                moved_count = 0
                for idx, row in edited_emp_df.iterrows():
                    if row.get("離職辦理", False):
                        emp_id = row["id"]
                        matched = next((e for e in st.session_state.employees_db if e.get("id") == emp_id), None)
                        if matched:
                            # 加上離職歸檔標記
                            matched["resigned_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
                            matched["reason"] = "正常離職辦理歸檔"
                            st.session_state.resigned_employees_db.append(matched)
                            moved_count += 1
                    else:
                        emp_id = row["id"]
                        matched = next((e for e in st.session_state.employees_db if e.get("id") == emp_id), None)
                        if matched:
                            remaining_emp.append(matched)
                
                st.session_state.employees_db = remaining_emp
                if moved_count > 0:
                    st.success(f"✅ 已成功將 {moved_count} 位員工移至離職人員名單並完成歸檔！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請先在表格左側勾選要辦理離職的員工。")

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
                emp_id = st.text_input("員工編號 *", value="EMP-004")
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
                job_title = st.selectbox(
                    "職位 / 職銜 (Job Title)",
                    ["工程師 / 技術員", "組長 / 主管", "行政 / 財務專員", "品管檢驗員", "作業員"]
                )

            c4, c5 = st.columns(2)
            with c4:
                phone = st.text_input("聯絡電話 (Phone)", value="")
                id_card = st.text_input("護照號碼 / 身分證字號", value="")
            with c5:
                address = st.text_input("居住 / 戶籍地址 (Address)", value="")
                work_permit = st.text_input("工作許可證 / 勞工證號", value="-")

            role = st.selectbox("系統權限角色 (Role)", ["Staff (一般員工)", "Manager (部門主管)", "Admin (系統管理者)"])

            if st.form_submit_button("💾 儲存個人檔案", type="primary", use_container_width=True):
                if emp_name and emp_id:
                    st.session_state.employees_db.append({
                        "id": emp_id,
                        "name": emp_name,
                        "nationality": nationality,
                        "site": work_plant,
                        "dept": dept,
                        "title": job_title,
                        "role": role.split(" ")[0],
                        "phone": phone if phone else "-",
                        "address": address if address else "-",
                    })
                    st.success(f"🎉 已成功登錄員工 [{emp_name}] 的個人檔案！")
                    st.rerun()
                else:
                    st.error("請填寫員工編號與姓名！")

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
