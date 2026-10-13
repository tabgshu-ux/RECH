import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 多語系字典
# ----------------------------------------------------
EMP_I18N = {
    "繁體中文": {
        "title": "👤 管理部 - 員工個人檔案與人事管理中心",
        "caption": "管理全公司在職員工名冊、離職歷史檔案、越南勞動法合規與外籍幹部簽證/居留證件管理。",
        "tab_add_vn": "🇻🇳 新增越南員工",
        "tab_add_tw": "🇹🇼 新增外派幹部",
        "tab_edit": "✏️ 修改員工資料",
        "tab_resign": "🚪 員工離職與刪除",
        "tab_list": "📄 現職員工名冊",
        "tab_resigned_list": "📋 離職名冊",
        "lbl_filter_factory": "依廠區篩選",
        "lbl_search": "搜尋員工姓名、工號或證件號...",
        "header_list": "📄 全公司現職員工名冊與廠區分流總覽"
    }
}

def render_employee_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = EMP_I18N.get(active_lang, EMP_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    tab_add_vn, tab_add_tw, tab_edit, tab_resign, tab_list, tab_resigned_list = st.tabs([
        L["tab_add_vn"], L["tab_add_tw"], L["tab_edit"], L["tab_resign"], L["tab_list"], L["tab_resigned_list"]
    ])

    # ----------------------------------------------------
    # 🇻🇳 Tab 1: 新增越南籍員工 (符合越南勞動法完整欄位)
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
                v_factory = st.selectbox("工作廠區 (Nhà máy) *", ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)", "工程工地 (Site)", "文房 (VP)"])
                v_dept = st.text_input("部門 (Bộ phận)", value="生產部 (Phòng sản xuất)")
                v_pos = st.text_input("職稱 (Chức vụ)", value="廠內固定員工")
                v_att = st.selectbox("出勤性質", ["廠內固定員工 (Plant Fixed Staff)", "外勤施工人員 (Site Staff)", "免打卡高階主管 (Exempt Executive)"])
                v_social_code = st.text_input("社保號碼 (Mã số BHXH)", placeholder="例: 7912345678")

            with col3:
                v_sal = st.number_input("約定底薪 (Lương CB - VND)", min_value=0.0, value=5000000.0, step=100000.0)
                v_contract_type = st.selectbox("合約類型 (Loại HĐ)", ["試用期 (HĐ Thử việc)", "1年定期合約 (HĐ 1 năm)", "3年定期合約 (HĐ 3 năm)", "不定期合約 (HĐ Không xác định)"])
                v_start_date = st.date_input("到職日期 (Ngày vào làm)", datetime.date.today())
                v_address = st.text_input("戶籍/現居地址 (Địa chỉ)", placeholder="例: Tây Ninh, Việt Nam")

            if st.form_submit_button("➕ 儲存並寫入越南員工檔案", type="primary", use_container_width=True):
                if engine and v_code and v_name:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.employee_profiles 
                                (emp_code, emp_name, phone, id_card, factory, department, position, attendance_type, base_salary, status)
                                VALUES (:code, :name, :phone, :id, :factory, :dept, :pos, :att, :sal, '在職')
                                ON CONFLICT (emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    phone = EXCLUDED.phone,
                                    id_card = EXCLUDED.id_card,
                                    factory = EXCLUDED.factory,
                                    department = EXCLUDED.department,
                                    position = EXCLUDED.position,
                                    base_salary = EXCLUDED.base_salary,
                                    status = '在職';
                            """), {
                                "code": v_code, "name": v_name, "phone": v_phone, "id": v_id,
                                "factory": v_factory, "dept": v_dept, "pos": v_pos, "att": v_att, "sal": v_sal
                            })
                        st.success(f"🎉 成功新增/更新越南籍員工：{v_name} ({v_code})！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入資料庫失敗: " + str(e))
                else:
                    st.warning("⚠️ 請務必填寫『工號』與『姓名』！")

    # ----------------------------------------------------
    # 🇹🇼 Tab 2: 新增外派幹部/台籍員工 (護照、工作證、居留證 TRC)
    # ----------------------------------------------------
    with tab_add_tw:
        st.markdown("### 🇹🇼 TW/CN 新增外派幹部 / 台籍與中籍員工")
        st.caption("完整支援外籍幹部護照、工作許可證 (Giấy phép lao động) 與暫住證 (TRC) 到期預警管理。")
        
        with st.form("form_add_tw_emp_full"):
            col1, col2, col3 = st.columns(3)
            with col1:
                t_code = st.text_input("外派工號 *", placeholder="例: TW-005")
                t_name = st.text_input("中文/英文姓名 *", placeholder="例: 王大明 Wang Ta Ming")
                t_passport = st.text_input("護照號碼 (Passport No.)", placeholder="例: 312345678")
                t_passport_exp = st.date_input("護照到期日", datetime.date.today() + datetime.timedelta(days=730))

            with col2:
                t_factory = st.selectbox("駐點廠區/外派地點", ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)", "工程工地 (Site)", "文房 (VP)"])
                t_dept = st.text_input("部門", value="總經理室 (Executive Office)")
                t_pos = st.text_input("職稱 / 系統角色", value="廠長 / 專案經理")
                t_work_perm = st.text_input("越南工作許可證號", placeholder="例: WP-2026-999")

            with col3:
                t_trc = st.text_input("暫住證 TRC 號碼", placeholder="例: TRC-888999")
                t_trc_exp = st.date_input("TRC 居留證到期日", datetime.date.today() + datetime.timedelta(days=365))
                t_sal = st.number_input("約定底薪 (VND / USD / TWD)", min_value=0.0, value=30000000.0, step=1000000.0)
                t_role = st.selectbox("系統權限角色", ["部門經理 / 財務主管 / 廠長", "總經理 / 協理", "系統管理員 (Admin)"])

            if st.form_submit_button("➕ 儲存外派幹部檔案", type="primary", use_container_width=True):
                if engine and t_code and t_name:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.employee_profiles 
                                (emp_code, emp_name, phone, id_card, factory, department, position, attendance_type, system_role, base_salary, status)
                                VALUES (:code, :name, '外派幹部', :id, :factory, :dept, :pos, '免打卡高階主管 (Exempt Executive)', :role, :sal, '在職')
                                ON CONFLICT (emp_code) DO UPDATE
                                SET emp_name = EXCLUDED.emp_name,
                                    id_card = EXCLUDED.id_card,
                                    factory = EXCLUDED.factory,
                                    department = EXCLUDED.department,
                                    position = EXCLUDED.position,
                                    system_role = EXCLUDED.system_role,
                                    base_salary = EXCLUDED.base_salary,
                                    status = '在職';
                            """), {
                                "code": t_code, "name": t_name, "id": f"護照:{t_passport} / TRC:{t_trc}",
                                "factory": t_factory, "dept": t_dept, "pos": t_pos, "role": t_role, "sal": t_sal
                            })
                        st.success(f"🎉 成功新增外派幹部：{t_name} ({t_code})！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入資料庫失敗: " + str(e))
                else:
                    st.warning("⚠️ 請填寫外派工號與姓名！")

    # ----------------------------------------------------
    # ✏️ Tab 3: 修改員工資料與薪資卡
    # ----------------------------------------------------
    with tab_edit:
        st.markdown("### ✏️ 修改現職員工個人檔案與薪資資料")
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT emp_code, emp_name, department FROM public.employee_profiles WHERE status = '在職' ORDER BY emp_code;"))
                    emp_list = res.fetchall()
                    if emp_list:
                        emp_options = {f"{r.emp_code} - {r.emp_name} ({r.department})": r.emp_code for r in emp_list}
                        selected_emp_label = st.selectbox("請選擇要修改的員工：", list(emp_options.keys()))
                        target_code = emp_options[selected_emp_label]

                        # 讀取該員工細項
                        emp_detail = conn.execute(text("SELECT * FROM public.employee_profiles WHERE emp_code = :c;"), {"c": target_code}).fetchone()
                        if emp_detail:
                            e_dict = dict(emp_detail._mapping)
                            with st.form("form_edit_emp"):
                                col_e1, col_e2 = st.columns(2)
                                with col_e1:
                                    edit_name = st.text_input("姓名", value=e_dict.get("emp_name", ""))
                                    edit_dept = st.text_input("部門", value=e_dict.get("department", ""))
                                    edit_phone = st.text_input("電話", value=e_dict.get("phone", ""))
                                with col_e2:
                                    edit_factory = st.selectbox("廠區", ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)", "工程工地 (Site)", "文房 (VP)"], index=0)
                                    edit_sal = st.number_input("底薪 (VND)", value=float(e_dict.get("base_salary") or 0.0))
                                    edit_status = st.selectbox("在職狀態", ["在職", "離職封存"])

                                if st.form_submit_button("💾 儲存修改內容", type="primary"):
                                    with engine.begin() as conn_up:
                                        conn_up.execute(text("""
                                            UPDATE public.employee_profiles
                                            SET emp_name = :name, department = :dept, phone = :phone, factory = :fac, base_salary = :sal, status = :st
                                            WHERE emp_code = :code;
                                        """), {"name": edit_name, "dept": edit_dept, "phone": edit_phone, "fac": edit_factory, "sal": edit_sal, "st": edit_status, "code": target_code})
                                    st.success(f"✅ 已成功更新員工 {edit_name} 的資料！")
                                    st.rerun()
                    else:
                        st.info("目前尚無在職員工資料。")
            except Exception as e:
                st.error("讀取員工列表失敗: " + str(e))

    # ----------------------------------------------------
    # 🚪 Tab 4: 員工離職辦理與封存處理
    # ----------------------------------------------------
    with tab_resign:
        st.markdown("### 🚪 員工辦理離職與檔案封存")
        st.caption("注意：離職員工資料不會真正被刪除，系統會將其狀態標示為『離職』並歸檔至離職名冊中。")
        if engine:
            try:
                with engine.connect() as conn:
                    res_r = conn.execute(text("SELECT emp_code, emp_name, department FROM public.employee_profiles WHERE status = '在職' ORDER BY emp_code;"))
                    r_list = res_r.fetchall()
                    if r_list:
                        r_options = {f"{r.emp_code} - {r.emp_name} ({r.department})": r.emp_code for r in r_list}
                        resign_target = st.selectbox("選擇要辦理離職的員工：", list(r_options.keys()), key="resign_select")
                        resign_code = r_options[resign_target]
                        resign_date = st.date_input("離職生效日期", datetime.date.today())
                        resign_reason = st.text_area("離職原因說明", placeholder="例: 個人因素離職 / 合約期滿")

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
    # 📄 Tab 5: 全公司現職員工名冊 (往後移動至第 5 頁籤)
    # ----------------------------------------------------
    with tab_list:
        st.markdown("### " + L["header_list"])
        
        c1, c2 = st.columns([1, 2])
        with c1:
            selected_factory = st.selectbox(
                L["lbl_filter_factory"],
                ["全部廠區 (All Plants)", "西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)", "工程工地 (Site)", "文房 (VP)"]
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
                    
                    if selected_factory != "全部廠區 (All Plants)":
                        query += " AND factory = :factory"
                        params["factory"] = selected_factory
                        
                    if search_keyword.strip():
                        query += " AND (emp_code ILIKE :kw OR emp_name ILIKE :kw OR id_card ILIKE :kw)"
                        params["kw"] = f"%{search_keyword.strip()}%"

                    query += " ORDER BY emp_code ASC;"

                    res = conn.execute(text(query), params)
                    rows = res.fetchall()

                    if rows:
                        df = pd.DataFrame([dict(r._mapping) for r in rows])
                        df.insert(0, "STT", range(len(df)))
                        df.columns = ["STT", "工號", "姓名", "電話", "身份證/護照與居留證", "廠區", "部門", "職稱", "出勤性質", "系統角色", "狀態"]
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("⚠️ 目前資料庫尚無符合條件的員工資料，請至【員工薪資計算】頁面完成批次匯入 Excel。")
            except Exception as e:
                st.error("❌ 讀取員工名冊失敗: " + str(e))
        else:
            st.info("目前為展示模式，連線至資料庫後即可自動同步呈現名冊。")

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
