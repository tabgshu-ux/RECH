import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 裕豐電機工業 (Reetech Industrial) 組織規格
# ----------------------------------------------------
DEFAULT_FACTORY = "西寧廠 (Tay Ninh)"

DEPT_OPTIONS = [
    "總經理室 (Executive Office)",
    "管理部 (Management Dept)",
    "財務部 (Finance Dept)",
    "工程與設計管理中心 (Engineering & Design Center)",
    "生產部 (Production Dept)",
    "資訊管理部 (IT & System)",
    "工務與工地現場 (Site Operations)"
]

ATTENDANCE_TYPES = [
    "免打卡高階主管 (Exempt Executive)",
    "廠內固定員工 (Plant Fixed Staff)",
    "外勤施工人員 (Site Staff)",
    "外派輪休幹部 (Expat Staff)"
]

EMP_I18N = {
    "繁體中文": {
        "title": "👤 管理部 - 員工個人檔案與人事管理中心",
        "caption": "管理全公司在職員工名冊、離職歷史檔案、越南勞動法合規與外籍幹部簽證/居留證件管理。",
        "tab_add_vn": "🇻🇳 新增越南員工",
        "tab_add_tw": "🇹🇼 新增外派幹部",
        "tab_edit": "✏️ 修改員工資料",
        "tab_resign": "🚪 員工離職與刪除",
        "tab_list": "📄 現職員工名冊 (含台幹分流)",
        "tab_resigned_list": "📋 離職名冊",
        "lbl_filter_factory": "依廠區篩選",
        "lbl_search": "搜尋員工姓名、工號或證件號...",
        "header_list": "📄 全公司現職員工名冊與外派幹部獨立分流總覽"
    }
}

def get_system_roles_from_db(engine):
    """🔌 核心連線：直接從 Supabase 資料庫中的 public.system_roles 讀取 IT 設定的動態角色與正確階級順序"""
    default_roles = [
        "系統管理員 (Admin)",
        "董事長 / 總經理 (Executive)",
        "財務副理 / 財務主管 (Finance Manager)",
        "廠長 / 工務經理 (Plant/Project Manager)",
        "現場工地主任 / 組長 (Site Supervisor)",
        "採購 / 倉管 / 兼任會計 (Purchasing/Inventory)",
        "一般員工 (Staff)"
    ]
    if not engine:
        return default_roles
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT role_name FROM public.system_roles ORDER BY role_name;"))
            rows = res.fetchall()
            if rows:
                db_roles = [r[0] for r in rows if r[0]]
                for r in default_roles:
                    if r not in db_roles:
                        db_roles.append(r)
                return db_roles
    except Exception:
        pass
    return default_roles

def get_factory_list(engine):
    """取得資料庫中定義的廠區"""
    if not engine:
        return [DEFAULT_FACTORY]
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT DISTINCT factory_name FROM public.factories WHERE factory_name IS NOT NULL AND factory_name != '';"))
            rows = res.fetchall()
            if rows:
                return [r[0] for r in rows]
    except Exception:
        pass
    return [DEFAULT_FACTORY]

def init_employee_db(engine):
    """確保員工表具備完整欄位"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.employee_profiles (
                    id SERIAL PRIMARY KEY,
                    emp_code VARCHAR(50) UNIQUE NOT NULL,
                    emp_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(50),
                    id_card VARCHAR(100),
                    tax_code VARCHAR(50),
                    permanent_address TEXT,
                    current_address TEXT,
                    social_code VARCHAR(50),
                    health_code VARCHAR(50),
                    hospital_name VARCHAR(200),
                    factory VARCHAR(100) DEFAULT '西寧廠 (Tay Ninh)',
                    department VARCHAR(100),
                    position VARCHAR(100),
                    attendance_type VARCHAR(100) DEFAULT '免打卡高階主管 (Exempt Executive)',
                    system_role VARCHAR(100) DEFAULT '一般員工 (Staff)',
                    base_salary NUMERIC(12,2) DEFAULT 0,
                    status VARCHAR(50) DEFAULT '在職',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            alter_cols = [
                ("tax_code", "VARCHAR(50)"),
                ("permanent_address", "TEXT"),
                ("current_address", "TEXT"),
                ("social_code", "VARCHAR(50)"),
                ("health_code", "VARCHAR(50)"),
                ("hospital_name", "VARCHAR(200)"),
                ("factory", "VARCHAR(100) DEFAULT '西寧廠 (Tay Ninh)'"),
                ("attendance_type", "VARCHAR(100) DEFAULT '免打卡高階主管 (Exempt Executive)'"),
                ("system_role", "VARCHAR(100) DEFAULT '一般員工 (Staff)'"),
                ("base_salary", "NUMERIC(12,2) DEFAULT 0"),
                ("status", "VARCHAR(50) DEFAULT '在職'")
            ]
            for col_name, col_type in alter_cols:
                try:
                    conn.execute(text(f"ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                except Exception:
                    pass

            conn.execute(text("UPDATE public.employee_profiles SET factory = '西寧廠 (Tay Ninh)' WHERE factory IS NULL OR factory NOT IN ('西寧廠 (Tay Ninh)');"))
    except Exception:
        pass

def render_employee_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = EMP_I18N.get(active_lang, EMP_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_employee_db(engine)
    available_factories = get_factory_list(engine)
    
    # 🔌 動態連線：從 Supabase 資料庫即時撈取 IT 設定的最新系統權限角色
    system_roles_options = get_system_roles_from_db(engine)

    tab_add_vn, tab_add_tw, tab_edit, tab_resign, tab_list, tab_resigned_list = st.tabs([
        L["tab_add_vn"], L["tab_add_tw"], L["tab_edit"], L["tab_resign"], L["tab_list"], L["tab_resigned_list"]
    ])

    # ----------------------------------------------------
    # 🇻🇳 Tab 1: 新增越南籍員工
    # ----------------------------------------------------
    with tab_add_vn:
        st.markdown("### 🇻🇳 新增越南籍員工資料 (符合越南勞動法合規規格)")
        with st.form("form_add_vn_emp_full"):
            col1, col2, col3 = st.columns(3)
            with col1:
                v_code = st.text_input("工號 (Mã NV) *", placeholder="例: VN-003")
                v_name = st.text_input("姓名 (Họ tên) *", placeholder="例: NGUYỄN VĂN A")
                v_phone = st.text_input("聯絡電話 (Số ĐT)", placeholder="例: +84-901234567")
                v_id = st.text_input("公民身分證 CCCD / 護照 *", placeholder="例: 079095012345")
                v_tax_code = st.text_input("個人稅號 (Mã số thuế)", placeholder="例: 8012345678")

            with col2:
                v_factory = st.selectbox("駐點廠區 (Nhà máy)", available_factories)
                v_dept = st.selectbox("部門 (Bộ phận)", DEPT_OPTIONS, index=4)
                v_pos = st.text_input("職稱 (Chức vụ)", value="廠內固定員工")
                v_att = st.selectbox("出勤性質", ["廠內固定員工 (Plant Fixed Staff)", "外勤施工人員 (Site Staff)", "免打卡高階主管 (Exempt Executive)"])
                v_social_code = st.text_input("社保號碼 (Mã số BHXH)", placeholder="例: 7912345678")

            with col3:
                v_sal = st.number_input("約定底薪 (Lương CB - VND)", min_value=0.0, value=5000000.0, step=100000.0)
                v_role = st.selectbox("系統權限角色 (System Role)", system_roles_options, index=0)
                v_perm_addr = st.text_input("戶籍地址 (Thường trú)", placeholder="例: Tây Ninh, Việt Nam")
                v_curr_addr = st.text_input("現居地址 (Tạm trú)", placeholder="例: An Tịnh, Trảng Bàng, Tây Ninh")
                v_hosp = st.text_input("看診登記醫院 (Bệnh viện KCB)", placeholder="例: BV Đa khoa Tây Ninh")

            if st.form_submit_button("➕ 儲存並寫入越南員工檔案", type="primary", use_container_width=True):
                if engine and v_code and v_name:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.employee_profiles 
                                (emp_code, emp_name, phone, id_card, tax_code, permanent_address, current_address, social_code, hospital_name, factory, department, position, attendance_type, system_role, base_salary, status)
                                VALUES (:code, :name, :phone, :id, :tax, :perm, :curr, :social, :hosp, :factory, :dept, :pos, :att, :role, :sal, '在職')
                                ON CONFLICT (emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    phone = EXCLUDED.phone,
                                    id_card = EXCLUDED.id_card,
                                    tax_code = EXCLUDED.tax_code,
                                    permanent_address = EXCLUDED.permanent_address,
                                    current_address = EXCLUDED.current_address,
                                    social_code = EXCLUDED.social_code,
                                    hospital_name = EXCLUDED.hospital_name,
                                    factory = EXCLUDED.factory,
                                    department = EXCLUDED.department,
                                    position = EXCLUDED.position,
                                    attendance_type = EXCLUDED.attendance_type,
                                    system_role = EXCLUDED.system_role,
                                    base_salary = EXCLUDED.base_salary,
                                    status = '在職';
                            """), {
                                "code": v_code, "name": v_name, "phone": v_phone, "id": v_id, "tax": v_tax_code,
                                "perm": v_perm_addr, "curr": v_curr_addr, "social": v_social_code, "hosp": v_hosp,
                                "factory": v_factory, "dept": v_dept, "pos": v_pos, "att": v_att, "role": v_role, "sal": v_sal
                            })
                        st.success(f"🎉 成功新增/更新越南籍員工：{v_name} ({v_code})！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入資料庫失敗: " + str(e))
                else:
                    st.warning("⚠️ 請務必填寫『工號』與『姓名』！")

    # ----------------------------------------------------
    # 🇹🇼 Tab 2: 新增外派幹部 (連動 IT 設定之系統權限角色)
    # ----------------------------------------------------
    with tab_add_tw:
        st.markdown("### 🇹🇼 TW/CN 新增外派幹部 / 台籍與中籍員工")
        with st.form("form_add_tw_emp_full"):
            col1, col2, col3 = st.columns(3)
            with col1:
                t_code = st.text_input("外派工號 *", placeholder="例: TW-005")
                t_name = st.text_input("中文/英文姓名 *", placeholder="例: 王大明 Wang Ta Ming / Tassos")
                t_passport = st.text_input("護照號碼 (Passport No.)", placeholder="例: 312345678")
                t_trc = st.text_input("暫住證 TRC 號碼", placeholder="例: TRC-888999")

            with col2:
                t_factory = st.selectbox("駐點廠區", available_factories)
                t_dept = st.selectbox("所屬部門", DEPT_OPTIONS, index=0)
                t_pos = st.text_input("職稱 (Chức vụ)", value="廠長 / 專案經理")
                t_att = st.selectbox("出勤性質 (考勤打卡)", ATTENDANCE_TYPES, index=0)

            with col3:
                t_sal = st.number_input("約定底薪 (VND / USD / TWD)", min_value=0.0, value=30000000.0, step=1000000.0)
                t_role = st.selectbox("系統權限角色 (System Role)", system_roles_options, index=0)
                t_phone = st.text_input("聯絡電話", placeholder="例: +886-912345678")

            if st.form_submit_button("💾 儲存外派幹部檔案", type="primary", use_container_width=True):
                if engine and t_code and t_name:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.employee_profiles 
                                (emp_code, emp_name, phone, id_card, factory, department, position, attendance_type, system_role, base_salary, status)
                                VALUES (:code, :name, :phone, :id, :factory, :dept, :pos, :att, :role, :sal, '在職')
                                ON CONFLICT (emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    phone = EXCLUDED.phone,
                                    id_card = EXCLUDED.id_card,
                                    factory = EXCLUDED.factory,
                                    department = EXCLUDED.department,
                                    position = EXCLUDED.position,
                                    attendance_type = EXCLUDED.attendance_type,
                                    system_role = EXCLUDED.system_role,
                                    base_salary = EXCLUDED.base_salary,
                                    status = '在職';
                            """), {
                                "code": t_code, "name": t_name, "phone": t_phone, "id": f"護照:{t_passport} / TRC:{t_trc}",
                                "factory": t_factory, "dept": t_dept, "pos": t_pos, "att": t_att, "role": t_role, "sal": t_sal
                            })
                        st.success(f"🎉 成功新增外派幹部：{t_name} ({t_code})！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入資料庫失敗: " + str(e))
                else:
                    st.warning("⚠️ 請填寫外派工號與姓名！")

    # ----------------------------------------------------
    # ✏️ Tab 3: 修改員工資料
    # ----------------------------------------------------
    with tab_edit:
        st.markdown("### ✏️ 修改現職員工個人檔案與薪資保險資料")
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT emp_code, emp_name, department FROM public.employee_profiles WHERE (status IS NULL OR status = '在職') ORDER BY emp_code;"))
                    emp_list = res.fetchall()
                    if emp_list:
                        emp_options = {f"{r.emp_code} - {r.emp_name} ({r.department})": r.emp_code for r in emp_list}
                        selected_emp_label = st.selectbox("請選擇要修改的員工：", list(emp_options.keys()))
                        target_code = emp_options[selected_emp_label]

                        emp_detail = conn.execute(text("SELECT * FROM public.employee_profiles WHERE emp_code = :c;"), {"c": target_code}).fetchone()
                        if emp_detail:
                            e = dict(emp_detail._mapping)
                            with st.form("form_edit_emp_full"):
                                st.markdown("##### 1️⃣ 基本職務與薪資 (Thông tin công việc & Lương)")
                                col_e1, col_e2, col_e3 = st.columns(3)
                                with col_e1:
                                    edit_name = st.text_input("姓名 (Họ tên)", value=str(e.get("emp_name") or ""))
                                    curr_dept = str(e.get("department") or "")
                                    dept_idx = DEPT_OPTIONS.index(curr_dept) if curr_dept in DEPT_OPTIONS else 0
                                    edit_dept = st.selectbox("部門 (Bộ phận)", DEPT_OPTIONS, index=dept_idx)
                                    edit_phone = st.text_input("電話 (Số ĐT)", value=str(e.get("phone") or ""))
                                with col_e2:
                                    edit_factory = st.selectbox("廠區 (Nhà máy)", available_factories)
                                    edit_pos = st.text_input("職稱 (Chức vụ)", value=str(e.get("position") or "廠內固定員工"))
                                    curr_att = str(e.get("attendance_type") or "")
                                    att_idx = ATTENDANCE_TYPES.index(curr_att) if curr_att in ATTENDANCE_TYPES else 0
                                    edit_att = st.selectbox("出勤性質", ATTENDANCE_TYPES, index=att_idx)
                                with col_e3:
                                    edit_sal = st.number_input("底薪 (Lương CB - VND)", value=float(e.get("base_salary") or 0.0), step=100000.0)
                                    curr_role = str(e.get("system_role") or "")
                                    role_idx = system_roles_options.index(curr_role) if curr_role in system_roles_options else 0
                                    edit_role = st.selectbox("系統權限角色 (System Role)", system_roles_options, index=role_idx)
                                    edit_status = st.selectbox("在職狀態", ["在職", "離職"])

                                st.markdown("##### 2️⃣ 身分證、稅號與地址 (Giấy tờ & Địa chỉ)")
                                col_a1, col_a2, col_a3 = st.columns(3)
                                with col_a1:
                                    edit_id = st.text_input("身分證 CCCD / 護照", value=str(e.get("id_card") or ""))
                                    edit_tax = st.text_input("個人稅號 (Mã số thuế)", value=str(e.get("tax_code") or ""))
                                with col_a2:
                                    edit_perm_addr = st.text_area("戶籍地址 (Địa chỉ thường trú)", value=str(e.get("permanent_address") or ""), height=70)
                                with col_a3:
                                    edit_curr_addr = st.text_area("現居地址 (Địa chỉ tạm trú)", value=str(e.get("current_address") or ""), height=70)

                                st.markdown("##### 3️⃣ 社保、醫保與看診醫院 (Bảo hiểm xã hội & Bệnh viện)")
                                col_b1, col_b2, col_b3 = st.columns(3)
                                with col_b1:
                                    edit_social_code = st.text_input("社保號碼 (Mã số BHXH)", value=str(e.get("social_code") or ""))
                                with col_b2:
                                    edit_health_code = st.text_input("醫保卡號 (Mã số BHYT)", value=str(e.get("health_code") or ""))
                                with col_b3:
                                    edit_hospital = st.text_input("看診登記醫院 (Nơi đăng ký KCB)", value=str(e.get("hospital_name") or ""))

                                if st.form_submit_button("💾 儲存修改內容", type="primary", use_container_width=True):
                                    with engine.begin() as conn_up:
                                        conn_up.execute(text("""
                                            UPDATE public.employee_profiles
                                            SET emp_name = :name,
                                                department = :dept,
                                                phone = :phone,
                                                factory = :fac,
                                                position = :pos,
                                                attendance_type = :att,
                                                system_role = :role,
                                                base_salary = :sal,
                                                id_card = :id_card,
                                                tax_code = :tax,
                                                permanent_address = :perm,
                                                current_address = :curr,
                                                social_code = :social,
                                                health_code = :health,
                                                hospital_name = :hosp,
                                                status = :st,
                                                updated_at = CURRENT_TIMESTAMP
                                            WHERE emp_code = :code;
                                        """), {
                                            "name": edit_name, "dept": edit_dept, "phone": edit_phone,
                                            "fac": edit_factory, "pos": edit_pos, "att": edit_att, "role": edit_role,
                                            "sal": edit_sal, "id_card": edit_id, "tax": edit_tax,
                                            "perm": edit_perm_addr, "curr": edit_curr_addr,
                                            "social": edit_social_code, "health": edit_health_code,
                                            "hosp": edit_hospital, "st": edit_status, "code": target_code
                                        })
                                    st.success(f"🎉 已成功更新員工【{edit_name}】的個人與系統權限資料！")
                                    st.rerun()
                    else:
                        st.info("目前尚無在職員工資料。")
            except Exception as e:
                st.error("讀取員工列表失敗: " + str(e))

    # ----------------------------------------------------
    # 🚪 Tab 4: 員工離職辦理
    # ----------------------------------------------------
    with tab_resign:
        st.markdown("### 🚪 員工辦理離職與檔案封存")
        if engine:
            try:
                with engine.connect() as conn:
                    res_r = conn.execute(text("SELECT emp_code, emp_name, department FROM public.employee_profiles WHERE (status IS NULL OR status = '在職') ORDER BY emp_code;"))
                    r_list = res_r.fetchall()
                    if r_list:
                        r_options = {f"{r.emp_code} - {r.emp_name} ({r.department})": r.emp_code for r in r_list}
                        resign_target = st.selectbox("選擇要辦理離職的員工：", list(r_options.keys()), key="resign_select")
                        resign_code = r_options[resign_target]

                        if st.button("⚠️ 確認辦理離職並歸檔", type="primary"):
                            with engine.begin() as conn_r:
                                conn_r.execute(text("""
                                    UPDATE public.employee_profiles
                                    SET status = '離職'
                                    WHERE emp_code = :code;
                                """), {"code": resign_code})
                            st.success(f"✅ 已成功辦理離職歸檔！")
                            st.rerun()
                    else:
                        st.info("目前尚無可辦理離職的在職員工。")
            except Exception as e:
                st.error("讀取失敗: " + str(e))

    # ----------------------------------------------------
    # 📄 Tab 5: 全公司現職員工名冊 (加入台幹獨立分流)
    # ----------------------------------------------------
    with tab_list:
        st.markdown("### " + L["header_list"])
        
        # 👑 新增：台幹與越南員工獨立分流檢視過濾器
        sub_filter = st.radio(
            "📋 檢視名冊類別分流：",
            ["全部現職員工 (All)", "🇹🇼 外派幹部 / 台籍與中籍 (Expat/TW/CN)", "🇻🇳 越南籍員工 (Local VN)"],
            horizontal=True
        )

        c1, c2 = st.columns([1, 2])
        with c1:
            selected_factory = st.selectbox(
                L["lbl_filter_factory"],
                available_factories
            )
        with c2:
            search_keyword = st.text_input(L["lbl_search"], value="")

        if engine:
            try:
                with engine.connect() as conn:
                    query = """
                        SELECT emp_code, emp_name, phone, id_card, factory, department, position, attendance_type, system_role, status
                        FROM public.employee_profiles
                        WHERE (status IS NULL OR status = '在職')
                    """
                    params = {}
                    
                    if selected_factory:
                        query += " AND factory = :fac"
                        params["fac"] = selected_factory

                    if search_keyword.strip():
                        query += " AND (emp_code ILIKE :kw OR emp_name ILIKE :kw OR id_card ILIKE :kw)"
                        params["kw"] = f"%{search_keyword.strip()}%"

                    query += " ORDER BY emp_code ASC;"

                    res = conn.execute(text(query), params)
                    rows = res.fetchall()

                    if rows:
                        df = pd.DataFrame([dict(r._mapping) for r in rows])
                        
                        # 依據上方分流按鈕進行資料篩選
                        if "外派" in sub_filter:
                            df = df[df["emp_code"].str.upper().str.startswith("TW") | df["emp_code"].str.upper().str.startswith("CN") | df["position"].str.contains("廠長|經理|副理|主任|董事長|外派", na=False)]
                        elif "越南" in sub_filter:
                            df = df[df["emp_code"].str.upper().str.startswith("VN") | ~df["emp_code"].str.upper().str.startswith("TW") & ~df["emp_code"].str.upper().str.startswith("CN")]

                        if not df.empty:
                            df.insert(0, "STT", range(len(df)))
                            df.columns = ["STT", "工號", "姓名", "電話", "身份證/護照與居留證", "廠區", "部門", "職稱", "出勤性質", "系統角色", "狀態"]
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("ℹ️ 此分流類別目前尚無符合的員工資料。")
                    else:
                        st.warning("⚠️ 目前資料庫尚無符合條件的員工資料。")
            except Exception as e:
                st.error("❌ 讀取員工名冊失敗: " + str(e))
        else:
            st.info("目前為展示模式。")

    # ----------------------------------------------------
    # 📋 Tab 6: 離職名冊歷史封存
    # ----------------------------------------------------
    with tab_resigned_list:
        st.markdown("### 📋 歷史離職員工封存檔案總覽")
        if engine:
            try:
                with engine.connect() as conn:
                    res_resigned = conn.execute(text("""
                        SELECT emp_code, emp_name, phone, factory, department, position
                        FROM public.employee_profiles
                        WHERE status = '離職'
                        ORDER BY emp_code ASC;
                    """))
                    rows_r = res_resigned.fetchall()
                    if rows_r:
                        df_r = pd.DataFrame([dict(r._mapping) for r in rows_r])
                        df_r.insert(0, "STT", range(len(df_r)))
                        df_r.columns = ["STT", "工號", "姓名", "電話", "原廠區", "原部門", "原職稱"]
                        st.dataframe(df_r, use_container_width=True)
                    else:
                        st.info("目前尚無離職歸檔紀錄。")
            except Exception as e:
                st.error("讀取離職紀錄失敗: " + str(e))

def render_employee_management(engine=None, lang="繁體中文", **kwargs):
    render_employee_management_page(engine=engine, lang=lang, **kwargs)

def render_employee_profile_page(engine=None, lang="繁體中文", **kwargs):
    render_employee_management_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_employee_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_employee_management_page(engine=engine, lang=lang, **kwargs)
