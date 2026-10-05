import datetime
import pandas as pd
import streamlit as st

def render_employee_management(engine=None, t=None, lang="繁體中文"):
    st.title("👤 管理部 - 員工與人事管理")
    st.caption("維護全廠區員工個人檔案、合約記錄、工作廠區、離職歸檔、人臉/指紋打卡機資料彙集。")

    # 初始化員工資料庫
    if "employees_db" not in st.session_state:
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

    # 初始化打卡與請假資料庫
    if "attendance_db" not in st.session_state:
        st.session_state.attendance_db = []
    if "leave_requests_db" not in st.session_state:
        st.session_state.leave_requests_db = []

    tab1, tab2, tab3 = st.tabs(["📋 員工名冊與詳細編輯", "⏰ 智慧打卡紀錄", "📝 請假簽核中心"])

    with tab1:
        st.markdown("### 📋 現有在職員工名冊")
        df_emp = pd.DataFrame(st.session_state.employees_db)
        st.dataframe(df_emp, use_container_width=True)

        st.markdown("---")
        st.markdown("### ➕ 新增員工個人檔案")
        with st.form("add_emp_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_id = st.text_input("員工編號", value="EMP-104")
                new_name = st.text_input("員工姓名")
                new_nationality = st.selectbox("國籍", ["🇹🇼 台灣 (Taiwan)", "🇻🇳 越南 (Vietnamese)", "🇨🇳 中國 (Chinese)"])
            with c2:
                new_site = st.selectbox("工作廠區", ["西寧廠", "越南西寧廠 (Tay Ninh Plant)", "平陽廠"])
                new_title = st.text_input("職稱", value="專員")
                new_role = st.selectbox("系統權限角色", ["Chairman", "GeneralManager", "ViceManager", "Director", "Manager", "Supervisor", "Staff", "Admin"])
            
            if st.form_submit_button("💾 立即新增員工", type="primary"):
                if new_name and new_id:
                    st.session_state.employees_db.append({
                        "id": new_id,
                        "name": new_name,
                        "nationality": new_nationality,
                        "site": new_site,
                        "dept": "管理部",
                        "title": new_title,
                        "role": new_role,
                        "phone": "-",
                        "address": "-",
                        "face_token": f"FACE-{new_id}"
                    })
                    st.success(f"✅ 成功新增員工：{new_name}")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫員工編號與姓名！")

    with tab2:
        st.markdown("### ⏰ 廠區人臉 / 指紋打卡紀錄彙集")
        st.info("💡 模擬串接工廠各出入口之生物辨識打卡機資料。")
        
        with st.form("mock_punch"):
            p_id = st.selectbox("選擇打卡員工", [e["id"] + " - " + e["name"] for e in st.session_state.employees_db])
            p_type = st.radio("打卡類型", ["上班簽到 (Clock In)", "下班簽退 (Clock Out)"], horizontal=True)
            if st.form_submit_button("📍 模擬刷臉打卡"):
                emp_name = p_id.split(" - ")[1]
                now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.attendance_db.insert(0, {
                    "時間": now_time,
                    "員工": emp_name,
                    "類型": p_type,
                    "狀態": "✅ 正常"
                })
                st.success(f"✅ {emp_name} 於 {now_time} 紀錄成功！")

        if st.session_state.attendance_db:
            st.dataframe(pd.DataFrame(st.session_state.attendance_db), use_container_width=True)
        else:
            st.info("目前尚無今日打卡紀錄。")

    with tab3:
        st.markdown("### 📝 請假申請與簽核流程")
        with st.form("leave_form"):
            l_emp = st.selectbox("請假員工", [e["name"] for e in st.session_state.employees_db])
            l_type = st.selectbox("假別", ["特休假 (Annual Leave)", "事假 (Personal Leave)", "病假 (Sick Leave)", "公出 (Official Business)"])
            l_reason = st.text_area("請假事由")
            if st.form_submit_button("📤 送出請假申請"):
                st.session_state.leave_requests_db.append({
                    "申請人": l_emp,
                    "假別": l_type,
                    "事由": l_reason,
                    "狀態": "⏳ 待主管簽核"
                })
                st.success("✅ 請假申請已送出，等待主管審核。")
                st.rerun()

        if st.session_state.leave_requests_db:
            st.markdown("#### 📋 目前請假單列表")
            st.dataframe(pd.DataFrame(st.session_state.leave_requests_db), use_container_width=True)

def show(engine=None, t=None, lang="繁體中文"):
    render_employee_management(engine, t, lang)

def main(engine=None, t=None, lang="繁體中文"):
    render_employee_management(engine, t, lang)
