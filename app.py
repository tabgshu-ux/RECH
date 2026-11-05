# ----------------------------------------------------
# 🚀 3. 已登入側邊欄與動態功能選單（改回完全動態配置）
# ----------------------------------------------------
st.sidebar.markdown(RECH_LOGO_HTML, unsafe_allow_html=True)

lang_list = ["繁體中文", "Tiếng Việt", "English"]
selected_lang = st.sidebar.selectbox(
    ui_t["lang_selector"],
    lang_list,
    index=(lang_list.index(curr_lang) if curr_lang in lang_list else 0),
    key="sidebar_lang_select"
)

if selected_lang != curr_lang:
    st.session_state.current_lang = selected_lang
    st.rerun()

u_name_display = st.session_state.get("user_name", "User")
u_role_display = str(st.session_state.get("user_role", "Staff")).upper()
st.sidebar.markdown(f"**👤 {u_name_display}** ({u_role_display})")

if st.sidebar.button(ui_t["logout_btn"], use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.must_change_pwd = False
    st.rerun()

st.sidebar.markdown("---")

current_role_clean = str(st.session_state.get("user_role", "")).strip().lower()

# 📌 關鍵：透過模組化函數動態取得系統設定中定義的部門樹狀結構
dept_module_tree = get_department_module_tree()
department_names = list(dept_module_tree.keys()) if dept_module_tree else [
    "總經理室 (Executive Office)",
    "管理部 (Management Dept)",
    "工程與設計管理中心 (Engineering & Design Center)",
    "生產部 (Production Dept)",
    "倉庫管理 (Warehouse Management)",
    "外勤工程打卡與工作回報 (Field Attendance)",
    "電子簽核中心 (Approval Center)",
    "系統設定 (System Settings)"
]

# 權限過濾
available_dept_names = []
for d_name in department_names:
    if current_role_clean != "admin" and "系統設定" in d_name:
        continue
    if current_role_clean == "security" and "管理部" not in d_name:
        continue
    available_dept_names.append(d_name)

if not available_dept_names:
    available_dept_names = department_names

# 渲染左側動態部門選單
selected_dept_label = st.sidebar.radio(
    ui_t["parent_header"],
    available_dept_names,
    index=st.session_state.get("selected_dept_index", 0),
    key="dept_radio_idx"
)

selected_dept_index = available_dept_names.index(selected_dept_label)
if selected_dept_index != st.session_state.get("selected_dept_index", 0):
    st.session_state.selected_dept_index = selected_dept_index
    st.session_state.selected_feat_index = 0
    st.rerun()

selected_feat_label = selected_dept_label
