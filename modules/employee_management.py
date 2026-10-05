import pandas as pd
import streamlit as st


def render_employee_management(engine=None, t=None, lang="繁體中文"):

    st.title("👤 管理部 - 員工與人事管理、智慧打卡及請假簽核中心")
    st.caption(
        "維護全廠區員工個人檔案、合約記錄、工作廠區、離職歸檔、"
        "人臉/指紋打卡機資料彙集。"
    )

    # =========================
    # 初始化員工資料
    # =========================
    if "employees_db" not in st.session_state:
        st.session_state.employees_db = [
            {
                "id": "EMP-001",
                "name": "張董事長",
                "nationality": "🇹🇼 台灣 (Taiwan)",
                "site": "西寧廠",
                "dept": "👑 經營高層 / 董事會與總經理室",
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
                "site": "🇻🇳 越南西寧廠",
                "dept": "👑 經營高層 / 董事會與總經理室",
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
                "site": "🇻🇳 越南西寧廠",
                "dept": "👔 經營主管 / 營運管理中心",
                "title": "副總經理 (Vice General Manager)",
                "role": "ViceManager",
                "phone": "-",
                "address": "-",
                "face_token": "FACE-BIO-300451",
            },
        ]

    # =========================
    # 員工列表
    # =========================
    st.markdown("### 📋 現有在職員工名冊")

    df_emp = pd.DataFrame(st.session_state.employees_db)

    st.dataframe(
        df_emp,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # =========================
    # 新增員工
    # =========================
    st.markdown("### ➕ 新增員工個人檔案")

    with st.form("simple_add_emp", clear_on_submit=False):

        c1, c2 = st.columns(2)

        with c1:
            new_id = st.text_input(
                "員工編號",
                value="EMP-100"
            )

            new_name = st.text_input(
                "員工姓名"
            )

        with c2:
            new_title = st.text_input(
                "職稱",
                value="經理"
            )

            new_role = st.selectbox(
                "系統權限角色",
                [
                    "Chairman",
                    "GeneralManager",
                    "ViceManager",
                    "Director",
                    "Manager",
                    "Supervisor",
                    "Staff",
                    "Admin",
                ]
            )

        submitted = st.form_submit_button(
            "💾 立即新增員工",
            type="primary"
        )

    # =========================
    # 處理新增
    # =========================
    if submitted:

        new_id = new_id.strip()
        new_name = new_name.strip()

        if not new_id or not new_name:
            st.warning("⚠️ 請填寫員工編號與姓名！")
            return

        # 防止員工編號重複
        existing_ids = {
            emp["id"]
            for emp in st.session_state.employees_db
        }

        if new_id in existing_ids:
            st.error(f"❌ 員工編號 {new_id} 已存在！")
            return

        st.session_state.employees_db.append(
            {
                "id": new_id,
                "name": new_name,
                "nationality": "🇹🇼 台灣 (Taiwanese)",
                "site": "西寧廠",
                "dept": "管理部",
                "title": new_title,
                "role": new_role,
                "phone": "-",
                "address": "-",
                "face_token": "FACE-NEW",
            }
        )

        st.success(f"✅ 成功新增員工：{new_name}")

        # 重新執行一次即可
        st.rerun()


def show(engine=None, t=None, lang="繁體中文"):
    render_employee_management(engine, t, lang)
