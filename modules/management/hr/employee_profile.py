import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def init_hr_profile_db(engine):
    """初始化員工數位履歷資料表"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS hr_employees (
                    emp_id VARCHAR(50) PRIMARY KEY,
                    emp_name VARCHAR(100) NOT NULL,
                    department VARCHAR(100),
                    position VARCHAR(100),
                    join_date VARCHAR(50),
                    contract_expire VARCHAR(50),
                    phone VARCHAR(50),
                    status VARCHAR(50) DEFAULT '在職'
                );
            """))
    except Exception as e:
        st.error(f"初始化員工資料表失敗: {e}")

def render_employee_profile(engine, lang="繁體中文"):
    init_hr_profile_db(engine)
    st.markdown("##### 👥 人事與合約生命週期管理 (Employee Profile & Contract)")
    st.info("💡 說明：在此管理全廠員工之數位履歷、部門職稱、到職日與勞動合約到期日，所有資料永久存入資料庫。")

    action = st.radio("選擇操作", ["📋 員工名冊總覽", "➕ 新增員工履歷", "✏️ 編輯/異動員工資料"], horizontal=True, key="hr_profile_action")
    st.markdown("---")

    employees = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT * FROM hr_employees ORDER BY emp_id")).fetchall()
                for r in res:
                    employees.append({
                        "emp_id": r[0], "emp_name": r[1], "department": r[2],
                        "position": r[3], "join_date": r[4], "contract_expire": r[5],
                        "phone": r[6], "status": r[7]
                    })
        except Exception as e:
            st.warning(f"讀取員工資料失敗: {e}")

    if action == "📋 員工名冊總覽":
        if employees:
            st.dataframe(pd.DataFrame(employees), use_container_width=True, hide_index=True)
        else:
            st.info("目前尚無員工資料，請至「新增員工履歷」建立。")

    elif action == "➕ 新增員工履歷":
        with st.form("add_employee_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_id = st.text_input("工號 (Employee ID) *", value="EMP-001")
                e_name = st.text_input("員工姓名 *", value="Nguyễn Văn A")
                e_dept = st.selectbox("部門", ["管理部", "生產部", "工程與設計中心", "總經理室", "資訊部"])
                e_pos = st.text_input("職稱", value="產線技術員")
            with c2:
                e_join = st.date_input("到職日期", value=datetime.date.today())
                e_contract = st.date_input("合約到期日", value=datetime.date.today() + datetime.timedelta(days=365))
                e_phone = st.text_input("聯絡電話", value="0912345678")
                e_status = st.selectbox("在職狀態", ["在職", "留職停薪", "離職"])

            if st.form_submit_button("💾 儲存員工履歷至資料庫", type="primary", use_container_width=True):
                if e_id and e_name:
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO hr_employees (emp_id, emp_name, department, position, join_date, contract_expire, phone, status)
                                    VALUES (:id, :name, :dept, :pos, :join, :con, :phone, :st)
                                    ON CONFLICT (emp_id) DO UPDATE SET
                                    emp_name = EXCLUDED.emp_name, department = EXCLUDED.department, position = EXCLUDED.position,
                                    contract_expire = EXCLUDED.contract_expire, status = EXCLUDED.status
                                """), {
                                    "id": e_id.strip(), "name": e_name.strip(), "dept": e_dept,
                                    "pos": e_pos.strip(), "join": str(e_join), "con": str(e_contract),
                                    "phone": e_phone.strip(), "st": e_status
                                })
                            st.success(f"✅ 成功儲存員工 {e_name} ({e_id}) 的資料！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"寫入失敗: {e}")
                else:
                    st.warning("請填寫必要欄位！")

    elif action == "✏️ 編輯/異動員工資料":
        if not employees:
            st.info("目前無員工資料可供修改。")
        else:
            sel_emp = st.selectbox("選擇要編輯的員工", [f"{e['emp_id']} - {e['emp_name']} ({e['department']})" for e in employees])
            target_id = sel_emp.split(" - ")[0]
            target_obj = next((e for e in employees if e["emp_id"] == target_id), None)

            if target_obj:
                with st.form("edit_employee_form"):
                    ed_name = st.text_input("姓名", value=target_obj["emp_name"])
                    ed_pos = st.text_input("職稱", value=target_obj["position"])
                    ed_phone = st.text_input("電話", value=target_obj["phone"])
                    ed_status = st.selectbox("狀態", ["在職", "留職停薪", "離職"], index=["在職", "留職停薪", "離職"].index(target_obj["status"]) if target_obj["status"] in ["在職", "留職停薪", "離職"] else 0)

                    if st.form_submit_button("💾 更新資料庫"):
                        if engine:
                            try:
                                with engine.begin() as conn:
                                    conn.execute(text("""
                                        UPDATE hr_employees SET emp_name = :name, position = :pos, phone = :phone, status = :st
                                        WHERE emp_id = :id
                                    """), {"name": ed_name, "pos": ed_pos, "phone": ed_phone, "st": ed_status, "id": target_id})
                                st.success("更新成功！")
                                st.rerun()
                            except Exception as e:
                                st.error(f"更新失敗: {e}")
