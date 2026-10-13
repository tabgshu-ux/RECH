import streamlit as st
import pandas as pd
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 多語系字典
# ----------------------------------------------------
EMP_I18N = {
    "繁體中文": {
        "title": "👤 管理部 - 員工個人檔案與人事管理中心",
        "caption": "管理全公司在職員工名冊、離職歷史檔案、越南勞動法合規與外籍幹部簽證/居留證件管理。",
        "tab_add_vn": "🇻🇳 新增越南員工",
        "tab_add_tw": "🇹🇼 TW/CN 新增外派員工",
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

    # 依照使用者習慣重新排列頁籤順序：新增/修改在前，查詢名冊在後
    tab_add_vn, tab_add_tw, tab_edit, tab_resign, tab_list, tab_resigned_list = st.tabs([
        L["tab_add_vn"], L["tab_add_tw"], L["tab_edit"], L["tab_resign"], L["tab_list"], L["tab_resigned_list"]
    ])

    # ----------------------------------------------------
    # 🇻🇳 Tab 1: 新增越南員工 (新增作業最常用)
    # ----------------------------------------------------
    with tab_add_vn:
        st.markdown("### 🇻🇳 新增越南籍員工資料")
        with st.form("form_add_vn_emp"):
            c1, c2, c3 = st.columns(3)
            with c1:
                v_code = st.text_input("工號 (Mã NV)", placeholder="例: 2026100101")
                v_name = st.text_input("姓名 (Họ tên)", placeholder="例: NGUYỄN VĂN A")
                v_phone = st.text_input("電話 (Số ĐT)", placeholder="例: +84-901234567")
            with c2:
                v_id = st.text_input("身分證 CCCD", placeholder="例: 079095012345")
                v_factory = st.selectbox("廠區 (Nhà máy)", ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)", "工程工地 (Site)", "文房 (VP)"])
                v_dept = st.text_input("部門 (Bộ phận)", value="生產部 (Phòng sản xuất)")
            with c3:
                v_pos = st.text_input("職稱 (Chức vụ)", value="廠內固定員工")
                v_sal = st.number_input("底薪 (Lương CB)", min_value=0.0, value=5000000.0, step=100000.0)
                v_att = st.selectbox("出勤性質", ["廠內固定員工 (Plant Fixed Staff)", "免打卡高階主管 (Exempt Executive)"])

            if st.form_submit_button("➕ 新增越南員工", type="primary", use_container_width=True):
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
                                    base_salary = EXCLUDED.base_salary;
                            """), {
                                "code": v_code, "name": v_name, "phone": v_phone, "id": v_id,
                                "factory": v_factory, "dept": v_dept, "pos": v_pos, "att": v_att, "sal": v_sal
                            })
                        st.success(f"✅ 成功新增/更新越南員工：{v_name} ({v_code})")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入失敗: " + str(e))
                else:
                    st.warning("請填寫工號與姓名！")

    # ----------------------------------------------------
    # 🇹🇼 Tab 2: 新增外派員工
    # ----------------------------------------------------
    with tab_add_tw:
        st.markdown("### 🇹🇼 TW/CN 新增外派幹部/台籍員工")
        st.info("外派幹部包含護照號碼、工作證與居留證 (TRC) 管理功能。")

    # ----------------------------------------------------
    # ✏️ Tab 3: 修改員工資料
    # ----------------------------------------------------
    with tab_edit:
        st.markdown("### ✏️ 修改員工個人資料與薪資卡")

    # ----------------------------------------------------
    # 🚪 Tab 4: 員工離職與刪除
    # ----------------------------------------------------
    with tab_resign:
        st.markdown("### 🚪 員工辦理離職與封存處理")

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
    # 📋 Tab 6: 離職名冊
    # ----------------------------------------------------
    with tab_resigned_list:
        st.markdown("### 📋 歷史離職員工封存檔案")

def render_employee_management(engine=None, lang="繁體中文", **kwargs):
    render_employee_management_page(engine=engine, lang=lang, **kwargs)

def render_employee_profile_page(engine=None, lang="繁體中文", **kwargs):
    render_employee_management_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_employee_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_employee_management_page(engine=engine, lang=lang, **kwargs)
