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
        "tab_add_tw": "🇹🇼 新增外派幹部 (支援雙薪)",
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
    db_roles = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT role_name FROM public.system_roles ORDER BY role_name ASC;"))
                rows = res.fetchall()
                if rows:
                    db_roles = [r[0] for r in rows if r[0]]
        except Exception:
            pass
    if not db_roles:
        db_roles = ["系統管理員 (Admin)", "一般員工 (Staff)"]
    return db_roles

def get_factory_list(engine):
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
                    second_currency VARCHAR(10) DEFAULT 'USD',
                    second_salary NUMERIC(12,2) DEFAULT 0,
                    status VARCHAR(50) DEFAULT '在職',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("""
                ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS second_currency VARCHAR(10) DEFAULT 'USD';
                ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS second_salary NUMERIC(12,2) DEFAULT 0;
            """))
    except Exception:
        pass

def render_employee_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = EMP_I18N.get(active_lang, EMP_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_employee_db(engine)
    available_factories = get_factory_list(engine)
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
                v_factory = st.selectbox("駐點廠區 (Nhà máy)", available_factories, key="vn_fac")
                v_dept = st.selectbox("部門 (Bộ phận)", DEPT_OPTIONS, index=4, key="vn_dept")
                v_pos = st.text_input("職稱 (Chức vụ)", value="廠內固定員工", key="vn_pos")
                v_att = st.selectbox("出勤性質", ["廠內固定員工 (Plant Fixed Staff)", "外勤施工人員 (Site Staff)", "免打卡高階主管 (Exempt Executive)"], key="vn_att")
                v_social_code = st.text_input("社保號碼 (Mã số BHXH)", placeholder="例: 7912345678")

            with col3:
                v_sal_str = st.text_input("越南盾約定底薪 (Lương CB - VND)", value="5,000,000", placeholder="例: 5,000,000")
                try:
                    v_sal = float(v_sal_str.replace(",", "").replace(" ", ""))
                except:
                    v_sal = 5000000.0
                st.markdown(f"**💡 越南盾確認金額：`{v_sal:,.0f} ₫ (VND)`**")
                
                v_role = st.selectbox("系統權限角色 (System Role)", system_roles_options, index=0, key="vn_role")
                v_perm_addr = st.text_input("戶籍地址 (Thường trú)", placeholder="例: Tây Ninh, Việt Nam")
                v_curr_addr = st.text_input("現居地址 (Tạm trú)", placeholder="例: An Tịnh, Trảng Bàng, Tây Ninh")
                v_hosp = st.text_input("看診登記醫院 (Bệnh viện KCB)", placeholder="例: BV Đa khoa Tây Ninh")

            if st.form_submit_button("➕ 儲存並寫入越南員工檔案", type="primary", use_container_width=True):
                if engine and v_code and v_name:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.employee_profiles 
                                (emp_code, emp_name, phone, id_card, tax_code, permanent_address, current_address, social_code, hospital_name, factory, department, position, attendance_type, system_role, base_salary, second_currency, second_salary, status)
                                VALUES (:code, :name, :phone, :id, :tax, :perm, :curr, :social, :hosp, :factory, :dept, :pos, :att, :role, :sal, 'VND', 0, '在職')
                                ON CONFLICT (emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name, phone = EXCLUDED.phone, id_card = EXCLUDED.id_card,
                                    tax_code = EXCLUDED.tax_code, permanent_address = EXCLUDED.permanent_address,
                                    current_address = EXCLUDED.current_address, social_code = EXCLUDED.social_code,
                                    hospital_name = EXCLUDED.hospital_name, factory = EXCLUDED.factory,
                                    department = EXCLUDED.department, position = EXCLUDED.position,
                                    attendance_type = EXCLUDED.attendance_type, system_role = EXCLUDED.system_role,
                                    base_salary = EXCLUDED.base_salary, status = '在職';
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
    # 🇹🇼 Tab 2: 新增外派幹部 (支援外派雙薪與動態幣別)
    # ----------------------------------------------------
    with tab_add_tw:
        st.markdown("### 🇹🇼 TW/CN 新增外派幹部 / 台籍與中籍員工 (支援外派雙薪)")
        with st.form("form_add_tw_emp_full"):
            col1, col2, col3 = st.columns(3)
            with col1:
                t_code = st.text_input("外派工號 *", placeholder="例: TW-005")
                t_name = st.text_input("中文/英文姓名 *", placeholder="例: 王大明 Wang Ta Ming / Tassos")
                t_passport = st.text_input("護照號碼 (Passport No.)", placeholder="例: 312345678")
                t_trc = st.text_input("暫住證 TRC 號碼", placeholder="例: TRC-888999")
                t_phone = st.text_input("聯絡電話", placeholder="例: +886-912345678")

            with col2:
                t_factory = st.selectbox("駐點廠區", available_factories, key="tw_fac")
                t_dept = st.selectbox("所屬部門", DEPT_OPTIONS, index=0, key="tw_dept")
                t_pos = st.text_input("職稱 (Chức vụ)", value="廠長 / 專案經理", key="tw_pos")
                t_att = st.selectbox("出勤性質 (考勤打卡)", ATTENDANCE_TYPES, index=0, key="tw_att")
                t_role = st.selectbox("系統權限角色 (System Role)", system_roles_options, index=0, key="tw_role")

            with col3:
                st.markdown("##### 💰 外派人員雙軌薪資設定")
                
                t_sal_str = st.text_input("越南盾在地底薪 (VND Salary)", value="30,000,000", placeholder="例: 30,000,000")
                try:
                    t_sal_vnd = float(t_sal_str.replace(",", "").replace(" ", ""))
                except:
                    t_sal_vnd = 30000000.0
                st.markdown(f"**💡 越南盾確認金額：`{t_sal_vnd:,.0f} ₫ (VND)`**")
                
                # 先選擇幣別，讓下方輸入框與預覽文字動態讀取
                t_sec_curr = st.selectbox("第二幣別選擇", ["USD", "TWD", "RMB"], key="tw_sec_curr")
                
                # 動態帶入所選幣別，絕不寫死 USD
                t_sec_sal = st.number_input(f"外派第二薪資金額 ({t_sec_curr})", min_value=0.0, value=1500.0, step=100.0, format="%.2f")
                st.markdown(f"**💲 外派薪資即時預覽：`{t_sec_sal:,.2f} {t_sec_curr}`**")

            if st.form_submit_button("💾 儲存外派幹部檔案 (含雙薪設定)", type="primary", use_container_width=True):
                if engine and t_code and t_name:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.employee_profiles 
                                (emp_code, emp_name, phone, id_card, factory, department, position, attendance_type, system_role, base_salary, second_currency, second_salary, status)
                                VALUES (:code, :name, :phone, :id, :factory, :dept, :pos, :att, :role, :sal_vnd, :sec_curr, :sec_sal, '在職')
                                ON CONFLICT (emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name, phone = EXCLUDED.phone, id_card = EXCLUDED.id_card,
                                    factory = EXCLUDED.factory, department = EXCLUDED.department, position = EXCLUDED.position,
                                    attendance_type = EXCLUDED.attendance_type, system_role = EXCLUDED.system_role,
                                    base_salary = EXCLUDED.base_salary, second_currency = EXCLUDED.second_currency, second_salary = EXCLUDED.second_salary, status = '在職';
                            """), {
                                "code": t_code, "name": t_name, "phone": t_phone, "id": f"護照:{t_passport} / TRC:{t_trc}",
                                "factory": t_factory, "dept": t_dept, "pos": t_pos, "att": t_att, "role": t_role,
                                "sal_vnd": t_sal_vnd, "sec_curr": t_sec_curr, "sec_sal": t_sec_sal
                            })
                        st.success(f"🎉 成功新增外派幹部：{t_name} ({t_code})！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入資料庫失敗: " + str(e))
                else:
                    st.warning("⚠️ 請填寫外派工號與姓名！")

    # ----------------------------------------------------
    # ✏️ Tab 3: 修改員工資料 (支援雙薪與動態幣別)
    # ----------------------------------------------------
    with tab_edit:
        st.markdown("### ✏️ 修改現職員工個人檔案與雙薪保險資料")
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
                                st.markdown("##### 1️⃣ 基本職務與雙薪結構設定")
                                col_e1, col_e2, col_e3 = st.columns(3)
                                with col_e1:
                                    edit_name = st.text_input("姓名 (Họ tên)", value=str(e.get("emp_name") or ""))
                                    curr_dept = str(e.get("department") or "")
                                    dept_idx = DEPT_OPTIONS.index(curr_dept) if curr_dept in DEPT_OPTIONS else 0
                                    edit_dept = st.selectbox("部門 (Bộ phận)", DEPT_OPTIONS, index=dept_idx)
                                    edit_phone = st.text_input("電話 (Số ĐT)", value=str(e.get("phone") or ""))
                                with col_e2:
                                    edit_factory = st.selectbox("廠區 (Nhà máy)", available_factories, key="edit_fac")
                                    edit_pos = st.text_input("職稱 (Chức vụ)", value=str(e.get("position") or "廠內固定員工"))
                                    curr_att = str(e.get("attendance_type") or "")
                                    att_idx = ATTENDANCE_TYPES.index(curr_att) if curr_att in ATTENDANCE_TYPES else 0
                                    edit_att = st.selectbox("出勤性質", ATTENDANCE_TYPES, index=att_idx)
                                with col_e3:
                                    edit_status = st.selectbox("在職狀態", ["在職", "離職"])
                                    curr_role = str(e.get("system_role") or "")
                                    role_idx = system_roles_options.index(curr_role) if curr_role in system_roles_options else 0
                                    edit_role = st.selectbox("系統權限角色 (System Role)", system_roles_options, index=role_idx)

                                st.markdown("##### 2️⃣ 薪資結構調整 (支援越南盾與外派雙薪)")
                                col_sal1, col_sal2 = st.columns(2)
                                with col_sal1:
                                    default_sal_val = f"{float(e.get('base_salary') or 0.0):,.0f}"
                                    edit_sal_str = st.text_input("越南盾底薪 (Lương CB - VND)", value=default_sal_val)
                                    try:
                                        edit_sal = float(edit_sal_str.replace(",", "").replace(" ", ""))
                                    except:
                                        edit_sal = float(e.get("base_salary") or 0.0)
                                    st.markdown(f"**💡 越南盾確認金額：`{edit_sal:,.0f} ₫ (VND)`**")
                                with col_sal2:
                                    curr_sec_curr = str(e.get("second_currency") or "USD")
                                    sec_curr_idx = ["USD", "TWD", "RMB"].index(curr_sec_curr) if curr_sec_curr in ["USD", "TWD", "RMB"] else 0
                                    
                                    edit_sec_curr = st.selectbox("第二幣別選擇", ["USD", "TWD", "RMB"], index=sec_curr_idx, key="edit_sec_curr")
                                    edit_sec_sal = st.number_input(f"外派第二薪資金額 ({edit_sec_curr})", value=float(e.get("second_salary") or 0.0), step=100.0, format="%.2f")
                                    st.markdown(f"**💲 外派薪資即時預覽：`{edit_sec_sal:,.2f} {edit_sec_curr}`**")

                                if st.form_submit_button("💾 儲存修改內容", type="primary", use_container_width=True):
                                    with engine.begin() as conn_up:
                                        conn_up.execute(text("""
                                            UPDATE public.employee_profiles
                                            SET emp_name = :name, department = :dept, phone = :phone,
                                                factory = :fac, position = :pos, attendance_type = :att,
                                                system_role = :role, base_salary = :sal, 
                                                second_currency = :sec_curr, second_salary = :sec_sal, 
                                                status = :st, updated_at = CURRENT_TIMESTAMP
                                            WHERE emp_code = :code;
                                        """), {
                                            "name": edit_name, "dept": edit_dept, "phone": edit_phone,
                                            "fac": edit_factory, "pos": edit_pos, "att": edit_att,
                                            "role": edit_role, "sal": edit_sal, 
                                            "sec_curr": edit_sec_curr, "sec_sal": edit_sec_sal,
                                            "st": edit_status, "code": target_code
                                        })
                                    st.success(f"🎉 已成功更新員工資料與雙薪結構！")
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
    # 📄 Tab 5: 全公司現職員工名冊 (含台幹分流)
    # ----------------------------------------------------
    with tab_list:
        st.markdown("### " + L["header_list"])
        
        sub_filter = st.radio(
            "📋 檢視名冊類別分流：",
            ["全部現職員工 (All)", "🇹🇼 外派幹部 / 台籍與中籍 (Expat/TW/CN)", "🇻🇳 越南籍員工 (Local VN)"],
            horizontal=True
        )

        c1, c2 = st.columns([1, 2])
        with c1:
            selected_factory = st.selectbox(L["lbl_filter_factory"], available_factories, key="list_fac")
        with c2:
            search_keyword = st.text_input(L["lbl_search"], value="", key="list_search")

        if engine:
            try:
                with engine.connect() as conn:
                    query = """
                        SELECT emp_code, emp_name, phone, id_card, factory, department, position, attendance_type, system_role, base_salary, second_currency, second_salary, status
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
                        
                        if "外派" in sub_filter:
                            df = df[df["emp_code"].str.upper().str.startswith("TW") | df["emp_code"].str.upper().str.startswith("CN") | df["position"].str.contains("廠長|經理|副理|主任|董事長|外派", na=False)]
                        elif "越南" in sub_filter:
                            df = df[df["emp_code"].str.upper().str.startswith("VN") | ~df["emp_code"].str.upper().str.startswith("TW") & ~df["emp_code"].str.upper().str.startswith("CN")]

                        if not df.empty:
                            df["base_salary_fmt"] = df["base_salary"].apply(lambda x: f"{float(x):,.0f} ₫" if pd.notnull(x) else "0 ₫")
                            df["second_salary_fmt"] = df.apply(lambda r: f"{float(r['second_salary']):,.2f} {r['second_currency']}" if pd.notnull(r['second_salary']) and float(r['second_salary']) > 0 else "-", axis=1)
                            
                            df.insert(0, "STT", range(len(df)))
                            display_df = df[["STT", "emp_code", "emp_name", "phone", "id_card", "factory", "department", "position", "attendance_type", "base_salary_fmt", "second_salary_fmt", "system_role", "status"]].copy()
                            display_df.columns = ["STT", "工號", "姓名", "電話", "身份證/護照與居留證", "廠區", "部門", "職稱", "出勤性質", "越南盾底薪", "外派第二薪資", "系統角色", "狀態"]
                            st.dataframe(display_df, use_container_width=True)
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
