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
        "tab_list": "👨‍💼 現職員工名冊",
        "tab_add_vn": "🇻🇳 新增越南員工",
        "tab_add_tw": "TW/CN 新增外派員工",
        "tab_edit": "✏️ 修改員工資料",
        "tab_resign": "🚪 員工離職與刪除",
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

    tab_list, tab_add_vn, tab_add_tw, tab_edit, tab_resign, tab_resigned_list = st.tabs([
        L["tab_list"], L["tab_add_vn"], L["tab_add_tw"], L["tab_edit"], L["tab_resign"], L["tab_resigned_list"]
    ])

    # ----------------------------------------------------
    # 👨‍💼 Tab 1: 全公司現職員工名冊 (動態連結 PostgreSQL 資料庫)
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

def render_employee_management(engine=None, lang="繁體中文", **kwargs):
    render_employee_management_page(engine=engine, lang=lang, **kwargs)

def render_employee_profile_page(engine=None, lang="繁體中文", **kwargs):
    render_employee_management_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_employee_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_employee_management_page(engine=engine, lang=lang, **kwargs)
