import streamlit as st
import pandas as pd

def render_employee_management(engine=None, t=None, lang="繁體中文", **kwargs):
    st.title("👤 管理部 - 員工個人檔案與人事管理")
    st.info("在此維護全廠區員工個人檔案、合約記錄、工作廠區與人事資料（支援兩國跨國籍與保險/薪資設定）。")

    if "employee_db" not in st.session_state:
        st.session_state.employee_db = [
            {
                "工號": "EMP-001", "姓名": "張董事長", "國籍": "台灣 (Taiwan)", "工作廠區": "西寧廠 (Tay Ninh)", "部門": "管理部", "職稱": "董事長 (Chairman)", "角色": "admin", "電話": "0912345678", 
                "戶籍地址": "台北市信義區...", "保險資料": "TW-INS-888899", "保險醫院": "台北榮民總醫院", "生物辨識代碼": "FACE-BIO-888899"
            },
            {
                "工號": "VN-003", "姓名": "張小華", "國籍": "越南 (Vietnam)", "工作廠區": "西寧廠 (Tay Ninh)", "部門": "生產一課 (射出)", "職稱": "射出工程師", "角色": "staff", "電話": "0912345678", 
                "戶籍地址": "台北市信義區忠孝東路", "身分證字號": "038095009999", "入職日期": "2026/10/07", "醫保指定醫院": "Bệnh viện Quốc tế Hạnh Phúc", "合約原署日期": "2026/10/07", "約定起薪": "9000000.00", "每月社醫保扣繳": "945000.00", "津貼總計": "1530000.00", "生物辨識代碼": "FACE-BIO-100234"
            }
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
            st.markdown("### 📌 步驟 1: 選擇員工國籍/廠區 (選擇後即時切換下方欄位)")[cite: 20]
            nat_choice = st.selectbox("員工國籍 / 所屬廠區 *", ["VN 越南 (Vietnam)", "台灣 (Taiwan)", "其他 (Other)"])
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                e_id = st.text_input("員工工號 (Emp ID) *", value=f"VN-{len(st.session_state.employee_db)+1:03d}" if "越南" in nat_choice else f"TW-{len(st.session_state.employee_db)+1:03d}")
                e_dept = st.selectbox("所屬部門", ["生產一課 (射出)", "管理部", "營運戰情室", "工程與設計管理中心", "生產部"])
                e_phone = st.text_input("聯絡電話 (Phone) *", placeholder="0912345678")
            with c2:
                e_name = st.text_input("員工全名 (Full Name) *", placeholder="請輸入姓名...")
                e_title = st.text_input("職位名稱", placeholder="例如: 射出工程師")
                e_role = st.selectbox("系統權限角色 (Role)", ["staff (一般員工)", "manager (部門主管)", "security (保全)", "admin (系統管理員)"])

            e_addr = st.text_input("居住/戶籍地址 (Address) *", placeholder="請輸入完整地址...")

            # 步驟 2 越南專屬欄位（依據國籍選擇即時顯示）
            if "越南" in nat_choice:
                st.markdown("---")
                st.markdown("### 📌 步驟 2: 輸入【VN 越南 (Vietnam)】專屬身分、起薪與法定保險資訊")[cite: 20]
                
                sc1, sc2, sc3 = st.columns(3)
                with sc1:
                    cccd = st.text_input("身份證字號 (Số CCCD)", placeholder="03809500...")
                    base_salary = st.number_input("約定起薪 / 保險起薪 (VND)", value=9000000.0, step=100000.0)
                with sc2:
                    hire_date = st.date_input("入職/到職日期")
                    monthly_ins = st.number_input("每月社醫保個人扣繳 (10.5% VND)", value=945000.0, step=10000.0)
                with sc3:
                    hospital = st.text_input("醫保指定醫院 (Bệnh viện)", value="Bệnh viện Quốc tế Hạnh Phúc")
                    allowance = st.number_input("各類津貼總計 (VND)", value=1530000.0, step=10000.0)
                
                contract_date = st.date_input("合約原署日期")
            else:
                cccd = ""
                base_salary = 0.0
                hire_date = None
                monthly_ins = 0.0
                hospital = ""
                allowance = 0.0
                contract_date = None

            st.markdown("---")
            if st.form_submit_button("💾 儲存兩國員工檔案 (同步調整與權限)", type="primary"):
                if e_name:
                    st.session_state.employee_db.append({
                        "工號": e_id,
                        "姓名": e_name,
                        "國籍": nat_choice,
                        "工作廠區": "西寧廠 (Tay Ninh)",
                        "部門": e_dept,
                        "職稱": e_title,
                        "角色": e_role.split()[0],
                        "電話": e_phone,
                        "戶籍地址": e_addr,
                        "身分證字號": cccd,
                        "入職日期": str(hire_date) if hire_date else "",
                        "醫保指定醫院": hospital,
                        "合約原署日期": str(contract_date) if contract_date else "",
                        "約定起薪": str(base_salary),
                        "每月社醫保扣繳": str(monthly_ins),
                        "津貼總計": str(allowance),
                        "生物辨識代碼": f"FACE-BIO-{len(st.session_state.employee_db)+100000}"
                    })
                    st.success(f"✅ 員工 {e_name} 檔案儲存成功！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫員工全名！")

    with tab_edit:
        if st.session_state.employee_db:
            emp_opts = {f"{e['工號']} - {e['姓名']}": e for e in st.session_state.employee_db}
            sel_emp_key = st.selectbox("選擇要修改的員工", list(emp_opts.keys()))
            target_emp = emp_opts[sel_emp_key]

            with st.form("edit_employee_form"):
                st.markdown("### ✏️ 修改員工檔案")
                ed_name = st.text_input("員工姓名", value=target_emp["姓名"])
                ed_title = st.text_input("職稱", value=target_emp["職稱"])
                ed_phone = st.text_input("電話", value=target_emp["電話"])
                ed_addr = st.text_input("戶籍地址", value=target_emp.get("戶籍地址", ""))

                if st.form_submit_button("💾 儲存修改", type="primary"):
                    for e in st.session_state.employee_db:
                        if e["工號"] == target_emp["工號"]:
                            e["姓名"] = ed_name
                            e["職稱"] = ed_title
                            e["電話"] = ed_phone
                            e["戶籍地址"] = ed_addr
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
