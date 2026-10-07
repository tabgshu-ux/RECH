import streamlit as st
import pandas as pd

def render_employee_management(engine=None, t=None, lang="繁體中文", **kwargs):
    st.title("👤 管理部 - 員工個人檔案與人事管理")
    st.info("在此維護全廠區員工個人檔案、合約記錄、工作廠區與人事資料（支援動態廠區聯動與搜尋）。")

    if "employee_db" not in st.session_state:
        st.session_state.employee_db = [
            {"工號": "EMP-001", "姓名": "張董事長", "國籍": "台灣 (Taiwan)", "工作廠區": "西寧廠 (Tay Ninh)", "部門": "管理部", "職稱": "董事長 (Chairman)", "角色": "Chairman", "電話": "0912345678", "生物辨識代碼": "FACE-BIO-888899"},
            {"工號": "EMP-002", "姓名": "Nguyễn Văn A", "國籍": "越南 (Vietnam)", "工作廠區": "西寧廠 (Tay Ninh)", "部門": "管理部", "職稱": "總經理 (General Manager)", "角色": "GeneralManager", "電話": "0918999080", "生物辨識代碼": "FACE-BIO-100234"},
            {"工號": "EMP-003", "姓名": "李元隆", "國籍": "台灣 (Taiwan)", "工作廠區": "海防廠 (Hai Phong)", "部門": "工程與設計管理中心", "職稱": "副總經理 (Vice General Manager)", "角色": "ViceManager", "電話": "", "生物辨識代碼": "FACE-BIO-300451"}
        ]

    if "factory_list" not in st.session_state:
        st.session_state.factory_list = [
            {"廠區編號": "FAC-01", "廠區名稱": "西寧廠 (Tay Ninh)", "負責人": "張董事長", "電話": "0912345678"},
            {"廠區編號": "FAC-02", "廠區名稱": "海防廠 (Hai Phong)", "負責人": "阮文強", "電話": "0918999080"}
        ]

    search_q = st.text_input("🔍 搜尋員工姓名 / 工號 / 職稱", placeholder="輸入關鍵字搜尋員工...")
    filtered_emp = [
        e for e in st.session_state.employee_db 
        if search_q.lower() in e["姓名"].lower() or search_q.lower() in e["工號"].lower() or search_q.lower() in e["職稱"].lower()
    ] if search_q else st.session_state.employee_db

    st.markdown("### 📋 現有在職員工名冊")
    st.dataframe(pd.DataFrame(filtered_emp), use_container_width=True)

    tab_add, tab_edit, tab_del = st.tabs(["➕ 新增員工", "✏️ 修改員工資料", "🗑️ 刪除員工"])

    with tab_add:
        with st.form("add_employee_form"):
            st.markdown("### ➕ 新增員工個人檔案")
            c1, c2 = st.columns(2)
            with c1:
                e_id = st.text_input("員工工號", value=f"EMP-{len(st.session_state.employee_db)+1:03d}")
                e_name = st.text_input("員工姓名 (Employee Name)")
                e_nat = st.selectbox("國籍", ["台灣 (Taiwan)", "越南 (Vietnam)", "其他 (Other)"])
            with c2:
                # 動態讀取廠區清單！實現跨模組完美聯動
                fac_choices = [f"{fac['廠區名稱']}" for fac in st.session_state.factory_list]
                if not fac_choices:
                    fac_choices = ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"]
                e_fac = st.selectbox("工作廠區 (Factory)", fac_choices)
                e_dept = st.selectbox("部門", ["管理部", "營運戰情室", "工程與設計管理中心", "生產部", "資訊管理部"])
                e_title = st.text_input("職稱 / 職務", placeholder="例如: 現場工程師 / 技術員")
                e_role = st.selectbox("系統權限角色", ["staff", "manager", "security", "admin"])
                e_phone = st.text_input("聯絡電話", placeholder="0912...")

            if st.form_submit_button("🚀 立即新增員工", type="primary"):
                if e_name:
                    st.session_state.employee_db.append({
                        "工號": e_id,
                        "姓名": e_name,
                        "國籍": e_nat,
                        "工作廠區": e_fac,
                        "部門": e_dept,
                        "職稱": e_title,
                        "角色": e_role,
                        "電話": e_phone,
                        "生物辨識代碼": f"FACE-BIO-{len(st.session_state.employee_db)+100000}"
                    })
                    st.success(f"✅ 員工 {e_name} 新增成功！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫員工姓名！")

    with tab_edit:
        if st.session_state.employee_db:
            emp_opts = {f"{e['工號']} - {e['姓名']}": e for e in st.session_state.employee_db}
            sel_emp_key = st.selectbox("選擇要修改的員工", list(emp_opts.keys()))
            target_emp = emp_opts[sel_emp_key]

            with st.form("edit_employee_form"):
                st.markdown("### ✏️ 修改員工檔案")
                ed_name = st.text_input("員工姓名", value=target_emp["姓名"])
                fac_choices = [f"{fac['廠區名稱']}" for fac in st.session_state.factory_list]
                if target_emp["工作廠區"] not in fac_choices:
                    fac_choices.append(target_emp["工作廠區"])
                ed_fac = st.selectbox("工作廠區", fac_choices, index=fac_choices.index(target_emp["工作廠區"]) if target_emp["工作廠區"] in fac_choices else 0)
                ed_title = st.text_input("職稱", value=target_emp["職稱"])
                ed_phone = st.text_input("電話", value=target_emp["電話"])

                if st.form_submit_button("💾 儲存修改", type="primary"):
                    for e in st.session_state.employee_db:
                        if e["工號"] == target_emp["工號"]:
                            e["姓名"] = ed_name
                            e["工作廠區"] = ed_fac
                            e["職稱"] = ed_title
                            e["電話"] = ed_phone
                    st.success(f"✅ 員工 {target_emp['工號']} 資料更新成功！")
                    st.rerun()
        else:
            st.info("目前無員工資料可供修改。")

    with tab_del:
        if st.session_state.employee_db:
            del_opts = {f"{e['工號']} - {e['姓名']}": e for e in st.session_state.employee_db}
            sel_del_key = st.selectbox("選擇要刪除的員工", list(del_opts.keys()))
            target_del = del_opts[sel_del_key]

            with st.form("delete_employee_form"):
                st.markdown("### 🗑️ 刪除員工確認")
                st.warning(f"確定要將員工 **{target_del['工號']} - {target_del['姓名']}** 自系統中刪除嗎？")
                if st.form_submit_button("🔥 確認刪除", type="primary"):
                    st.session_state.employee_db = [e for e in st.session_state.employee_db if e["工號"] != target_del["工號"]]
                    st.success(f"✅ 員工 {target_del['工號']} 已成功刪除！")
                    st.rerun()
        else:
            st.info("目前無員工資料可供刪除。")

def show(*args, **kwargs):
    render_employee_management(*args, **kwargs)

def main(*args, **kwargs):
    render_employee_management(*args, **kwargs)
