import pandas as pd
import streamlit as st


def render_employee_management(engine=None, t=None, lang="繁體中文"):
    st.title("👤 管理部 - 員工與人事管理中心")
    st.caption("維護全廠區員工個人檔案、合約記錄、工作廠區與部門職位分配。")

    # 初始化員工資料庫 (如無資料)
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
                "address": " Tây Ninh, Vietnam",
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
                "address": " Bến Cầu, Tây Ninh",
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
                "address": " Hải Phòng, Vietnam",
            },
        ]

    tab_manage, tab_add = st.tabs(["📑 現有員工名冊與刪除管理", "➕ 新增員工個人檔案"])

    # ----------------------------------------------------
    # 📑 頁籤一：現有員工名冊與刪除管理
    # ----------------------------------------------------
    with tab_manage:
        st.markdown("### 📋 公司現有員工名冊（可依廠區與部門檢視或勾選刪除）")

        df_emp = pd.DataFrame(st.session_state.employees_db)
        if "刪除" not in df_emp.columns:
            df_emp.insert(0, "刪除", False)

        edited_emp_df = st.data_editor(
            df_emp,
            use_container_width=True,
            num_rows="dynamic",
            key="employee_editor"
        )

        c_del1, _ = st.columns(2)
        with c_del1:
            if st.button("🗑️ 刪除勾選的員工資料", type="primary"):
                remaining_emp = []
                for idx, row in edited_emp_df.iterrows():
                    if not row.get("刪除", False):
                        emp_id = row["id"]
                        matched = next((e for e in st.session_state.employees_db if e.get("id") == emp_id), None)
                        if matched:
                            remaining_emp.append(matched)
                st.session_state.employees_db = remaining_emp
                st.success("✅ 已成功刪除選定的員工資料！")
                st.rerun()

    # ----------------------------------------------------
    # ➕ 頁籤二：新增員工個人檔案（去除了跨國與高管誤導字眼）
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


def show(engine=None, t=None, lang="繁體中文"):
    render_employee_management(engine, t, lang)


def main(engine=None, t=None, lang="繁體中文"):
    render_employee_management(engine, t, lang)
