import streamlit as st
import pandas as pd

def render_employee_management(engine=None, t=None, lang="繁體中文", **kwargs):
    st.title("👤 裕豐電機工業 - 員工個人檔案與人事管理中心")
    st.caption("管理全公司在職員工名冊、離職歷史檔案、回鍋復職、新增員工與角色權限（嚴格執行 Admin 與 IT 權限隔離）。")

    # 初始化員工資料庫 Mock Data
    if "employee_db" not in st.session_state:
        st.session_state.employee_db = [
            {"工號": "VN-001", "姓名": "Nguyễn Văn An", "角色": "admin", "部門": "資訊管理部", "國籍": "越南 (Vietnam)", "密碼": "123", "must_change_password": False},
            {"工號": "VN-002", "姓名": "Trần Thị Mai", "角色": "Manager", "部門": "管理部", "國籍": "越南 (Vietnam)", "密碼": "123456", "must_change_password": False},
            {"工號": "TW-101", "姓名": "許福村 (James Hsu)", "角色": "Chairman", "部門": "總經理室", "國籍": "台灣 (Taiwan)", "密碼": "123456", "must_change_password": False}
        ]

    # 取得當前登入者角色
    current_role = str(st.session_state.get("user_role", "")).strip().lower()
    is_admin = (current_role == "admin")

    # 上方 Tab 分頁
    tab1, tab2, tab3 = st.tabs([
        "👥 現職員工名冊與維護", 
        "➕ 新增員工與初始帳密設定 (SOP)", 
        "📋 離職與歷史檔案 (Archive)"
    ])

    # ====================================================
    # Tab 1：現職員工名冊與維護
    # ====================================================
    with tab1:
        st.markdown("#### 📋 全公司現職員工名冊 (Danh sách nhân viên)")
        df_emp = pd.DataFrame(st.session_state.employee_db)
        
        # 若不是 admin，隱藏密碼欄位以策安全
        if not is_admin and "密碼" in df_emp.columns:
            df_emp = df_emp.drop(columns=["密碼"])
            
        st.dataframe(df_emp, use_container_width=True)

    # ====================================================
    # Tab 2：新增員工與初始帳密設定 (內含越南文 SOP 與嚴格權限隔離)
    # ====================================================
    with tab2:
        st.markdown("#### ➕ 新增員工個人檔案與初始帳密設定")
        st.info("💡 **SOP 作業規範說明 (Quy trình SOP lập tài khoản nhân viên)**：請確實依照下方權限對照表為新進員工指派角色。**注意：系統管理員 (Admin) 與 IT 權限僅限最高管理者設定，一般人員無法檢視或選取。**")

        with st.form("add_employee_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_code = st.text_input("員工工號 (Mã nhân viên / Login ID) *", placeholder="例如: VN-003")
                new_name = st.text_input("員工姓名 (Họ và tên Employee Name) *", placeholder="例如: Phạm Văn Nam")
                new_pwd = st.text_input("初始登入密碼 (Mật khẩu khởi tạo) *", value="123456", type="password")
            with col2:
                new_nationality = st.selectbox("國籍 (Quốc tịch)", ["越南 (Vietnam)", "台灣 (Taiwan)", "其他 (Other)"])
                
                # 🛡️ 嚴格權限隔離邏輯：非 admin 絕對無法看到或選擇 admin / 資訊管理部
                if is_admin:
                    role_options = [
                        "系統管理員 (Admin / Quản trị hệ thống)",
                        "董事長 (Chairman / Chủ tịch)",
                        "總經理 (General Manager / TGĐ)",
                        "副總經理 / 協理 (Vice Manager / Phó TGĐ)",
                        "部門經理 / 財務主管 / 廠長 (Manager / Trưởng phòng)",
                        "一般員工 / 技術員 (Staff / Technician / Nhân viên)",
                        "廠區警衛 / 門禁 (Security / Bảo vệ)"
                    ]
                else:
                    # 一般人員登入時，強制過濾掉 Admin 相關權限
                    role_options = [
                        "部門經理 / 財務主管 / 廠長 (Manager / Trưởng phòng)",
                        "一般員工 / 技術員 (Staff / Technician / Nhân viên)",
                        "廠區警衛 / 門禁 (Security / Bảo vệ)"
                    ]

                selected_role_label = st.selectbox("指派系統角色與權限 (Phân quyền hệ thống) *", role_options)
                
                # 對應內部代碼
                if "Admin" in selected_role_label:
                    assigned_role = "admin"
                elif "Chairman" in selected_role_label or "董事長" in selected_role_label:
                    assigned_role = "Chairman"
                elif "General Manager" in selected_role_label or "總經理" in selected_role_label:
                    assigned_role = "GeneralManager"
                elif "Vice" in selected_role_label:
                    assigned_role = "ViceManager"
                elif "Manager" in selected_role_label or "經理" in selected_role_label:
                    assigned_role = "Manager"
                elif "Security" in selected_role_label or "警衛" in selected_role_label:
                    assigned_role = "security"
                else:
                    assigned_role = "Staff"

            new_address = st.text_input("現住址 / 地址 (Địa chỉ thường trú)", placeholder="例如: Bến Cát, Bình Dương / Trảng Bàng, Tây Ninh")

            submitted = st.form_submit_button("💾 立即新增員工並建立帳號 (Lưu thông tin)", type="primary")
            if submitted:
                if new_code and new_name:
                    # 檢查工號是否重複
                    exist = any(e["工號"].lower() == new_code.strip().lower() for e in st.session_state.employee_db)
                    if exist:
                        st.error(f"⚠️ 錯誤：工號 [{new_code}] 已經存在系統中，請使用其他工號！")
                    else:
                        st.session_state.employee_db.append({
                            "工號": new_code.strip(),
                            "姓名": new_name.strip(),
                            "角色": assigned_role,
                            "部門": "生產部" if assigned_role == "Staff" else "管理部",
                            "國籍": new_nationality,
                            "密碼": new_pwd,
                            "must_change_password": True  # 強制首次登入修改密碼
                        })
                        st.success(f"✅ 成功新增員工 [{new_name}]（工號: {new_code}），已發派初始密碼與首次登入變更機制！")
                        st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫員工工號與姓名！")

    # ====================================================
    # Tab 3：離職與歷史檔案
    # ====================================================
    with tab3:
        st.markdown("#### 📋 離職與歷史員工檔案 (Hồ sơ nhân viên nghỉ việc / Archive)")
        st.info("目前尚無離職歷史記錄。")
