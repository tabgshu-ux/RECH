import streamlit as st
import pandas as pd

def render_employee_management(engine=None, t=None, lang="繁體中文", **kwargs):
    st.title("👤 裕豐電機工業 - 員工個人檔案與人事管理中心")
    st.caption("管理全公司在職員工名冊、離職歷史、回鍋復職、帳號密碼與出勤性質分流（廠內固定打卡 vs. 外勤GPS工地打卡）。")

    # 初始化員工資料庫 Mock Data (加入出勤性質欄位)
    if "employee_db" not in st.session_state:
        st.session_state.employee_db = [
            {"工號": "VN-001", "姓名": "Nguyễn Văn An", "角色": "admin", "部門": "資訊管理部", "出勤性質": "廠內固定員工", "國籍": "越南 (Vietnam)", "密碼": "123", "must_change_password": False},
            {"工號": "VN-002", "姓名": "Trần Thị Mai", "角色": "Manager", "部門": "管理部", "出勤性質": "廠內固定員工", "國籍": "越南 (Vietnam)", "密碼": "123456", "must_change_password": False},
            {"工號": "VN-003", "姓名": "Phạm Văn Nam", "角色": "Staff", "部門": "工程與設計管理中心", "出勤性質": "外勤GPS工地人員", "國籍": "越南 (Vietnam)", "密碼": "123456", "must_change_password": True},
            {"工號": "TW-101", "姓名": "許福村 (James Hsu)", "角色": "Chairman", "部門": "總經理室", "出勤性質": "廠內固定員工", "國籍": "台灣 (Taiwan)", "密碼": "123456", "must_change_password": False}
        ]

    # 取得當前登入者角色
    current_role = str(st.session_state.get("user_role", "")).strip().lower()
    is_admin = (current_role == "admin")

    # 上方 Tab 分頁
    tab1, tab2, tab3 = st.tabs([
        "👥 現職員工名冊與出勤性質分流", 
        "➕ 新增員工與出勤屬性設定 (SOP)", 
        "📋 離職與歷史檔案 (Archive)"
    ])

    # ====================================================
    # Tab 1：現職員工名冊與維護
    # ====================================================
    with tab1:
        st.markdown("#### 📋 全公司現職員工名冊 (含出勤性質歸屬)")
        st.info("💡 **權責提示**：系統會自動依據員工的「出勤性質」，將其歸納至【廠內固定打卡】或【外勤GPS工地打卡】模組中。")
        
        df_emp = pd.DataFrame(st.session_state.employee_db)
        if not is_admin and "密碼" in df_emp.columns:
            df_emp = df_emp.drop(columns=["密碼"])
            
        st.dataframe(df_emp, use_container_width=True)

    # ====================================================
    # Tab 2：新增員工與初始帳密設定 (內含出勤性質分流)
    # ====================================================
    with tab2:
        st.markdown("#### ➕ 新增員工個人檔案與出勤屬性設定")
        st.info("💡 **SOP 作業規範說明**：若為每天在外部案場施工的工程師或工班，請務必將出勤性質選擇為『外勤GPS工地人員』，其系統權限將自動串聯至外勤 GPS 打卡與工地即時人數追蹤。")

        with st.form("add_employee_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_code = st.text_input("員工工號 (Mã nhân viên / Login ID) *", placeholder="例如: VN-004")
                new_name = st.text_input("員工姓名 (Họ và tên Employee Name) *", placeholder="例如: Nguyễn Văn Bình")
                new_pwd = st.text_input("初始登入密碼 (Mật khẩu khởi tạo) *", value="123456", type="password")
            with col2:
                new_nationality = st.selectbox("國籍 (Quốc tịch)", ["越南 (Vietnam)", "台灣 (Taiwan)", "其他 (Other)"])
                
                # 💡 關鍵新增：出勤性質分流選擇（廠內固定 vs 外勤GPS）
                attendance_type = st.selectbox(
                    "員工出勤性質歸屬 (Attendance Type) *",
                    [
                        "廠內固定員工 (Plant Fixed Attendance - 西寧/海防廠固定打卡)",
                        "外勤GPS工地人員 (Field GPS Site Staff - 每日外部工地GPS打卡)"
                    ],
                    help="外勤GPS人員將強制串聯至左側選單的【外勤 GPS 打卡與工地即時人數】模組"
                )

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

            new_address = st.text_input("現住址 / 聯絡地址 (Địa chỉ thường trú)", placeholder="例如: Trảng Bàng, Tây Ninh")

            submitted = st.form_submit_button("💾 立即新增員工並建立帳號 (Lưu thông tin)", type="primary")
            if submitted:
                if new_code and new_name:
                    exist = any(e["工號"].lower() == new_code.strip().lower() for e in st.session_state.employee_db)
                    if exist:
                        st.error(f"⚠️ 錯誤：工號 [{new_code}] 已經存在系統中！")
                    else:
                        st.session_state.employee_db.append({
                            "工號": new_code.strip(),
                            "姓名": new_name.strip(),
                            "角色": assigned_role,
                            "部門": "工程與設計管理中心" if "外勤" in attendance_type else "生產部",
                            "出勤性質": "外勤GPS工地人員" if "外勤" in attendance_type else "廠內固定員工",
                            "國籍": new_nationality,
                            "密碼": new_pwd,
                            "must_change_password": True
                        })
                        st.success(f"✅ 成功新增員工 [{new_name}]（工號: {new_code}），已成功歸納至【{attendance_type}】！")
                        st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫員工工號與姓名！")

    # ====================================================
    # Tab 3：離職與歷史檔案
    # ====================================================
    with tab3:
        st.markdown("#### 📋 離職與歷史員工檔案 (Archive)")
        st.info("目前尚無離職歷史記錄。")
