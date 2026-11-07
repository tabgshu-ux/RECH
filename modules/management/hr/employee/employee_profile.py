import streamlit as st
import importlib
from sqlalchemy import text

# 🌟 直接以模組方式安全載入，避免函式名稱不對而報錯
try:
    from modules.management.hr.employee import add_vietnamese
except ImportError:
    try:
        import add_vietnamese
    except:
        add_vietnamese = None

try:
    from modules.management.hr.employee import add_expat
except ImportError:
    try:
        import add_expat
    except:
        add_expat = None

try:
    from modules.management.hr.employee import employee_list
except ImportError:
    try:
        import employee_list
    except:
        employee_list = None

try:
    from modules.management.hr.employee import edit_profile
except ImportError:
    try:
        import edit_profile
    except:
        edit_profile = None

try:
    from modules.management.hr.employee import resigned_list
except ImportError:
    try:
        import resigned_list
    except:
        resigned_list = None

def init_hr_profile_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.employee_profiles (
                    id SERIAL PRIMARY KEY,
                    emp_code VARCHAR(50) UNIQUE NOT NULL,
                    emp_name VARCHAR(150) NOT NULL,
                    phone VARCHAR(50),
                    id_card VARCHAR(100),
                    tax_code VARCHAR(50),
                    factory VARCHAR(100),
                    department VARCHAR(150),
                    position VARCHAR(100),
                    staff_type VARCHAR(100) DEFAULT '越南籍員工',
                    attendance_mode VARCHAR(50) DEFAULT '需打卡',
                    base_salary NUMERIC(15, 2) DEFAULT 0,
                    private_allowance NUMERIC(15, 2) DEFAULT 0,
                    visa_expire DATE DEFAULT '2027-12-31',
                    system_role VARCHAR(100),
                    perm_address TEXT,
                    temp_address TEXT,
                    hospital VARCHAR(150),
                    bhxh_no VARCHAR(100),
                    bank_acc VARCHAR(100),
                    bank_name VARCHAR(150),
                    status VARCHAR(50) DEFAULT '在職',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                INSERT INTO public.employee_profiles (emp_code, emp_name, department, factory, base_salary, status)
                SELECT DISTINCT emp_code, emp_name, department, factory, base_salary, '在職'
                FROM public.payroll_records
                ON CONFLICT (emp_code) DO UPDATE 
                SET emp_name = EXCLUDED.emp_name,
                    department = EXCLUDED.department,
                    factory = EXCLUDED.factory,
                    base_salary = EXCLUDED.base_salary;
            """))
    except Exception:
        pass

def render_hr_profile_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")

    st.title("👤 管理部 - 員工個人檔案與人事管理中心")
    st.caption("管理公司在職員工名冊（越南員工與外派外籍幹部合規建檔、護照/TRC上傳、90天證件預警）。")

    init_hr_profile_db(engine)

    tabs = st.tabs([
        "VN 新增越南員工", 
        "🌐 新增外派與外籍幹部 (含證件上傳)", 
        "📑 現職員工總名冊與 90 天預警", 
        "✏️ 編輯與修改員工資料", 
        "📁 離職名冊管理"
    ])

    # 1. 新增越南員工
    with tabs[0]:
        if add_vietnamese:
            func = getattr(add_vietnamese, "render_add_vietnamese", None) or \
                   getattr(add_vietnamese, "render", None) or \
                   getattr(add_vietnamese, "main", None)
            if func:
                func(engine=engine, lang=active_lang)
            else:
                st.info("「新增越南員工」模組找不到可用渲染函式。")
        else:
            st.info("找不到 add_vietnamese 模組。")

    # 2. 新增外派幹部
    with tabs[1]:
        if add_expat:
            func = getattr(add_expat, "render_add_expat", None) or \
                   getattr(add_expat, "render", None) or \
                   getattr(add_expat, "main", None)
            if func:
                func(engine=engine, lang=active_lang)
            else:
                st.info("「新增外派幹部」模組找不到可用渲染函式。")
        else:
            st.info("找不到 add_expat 模組。")

    # 3. 現職員工總名冊
    with tabs[2]:
        if employee_list:
            func = getattr(employee_list, "render_employee_list", None) or \
                   getattr(employee_list, "render", None) or \
                   getattr(employee_list, "main", None)
            if func:
                func(engine=engine, lang=active_lang)
            else:
                st.info("「員工總名冊」模組找不到可用渲染函式。")
        else:
            st.info("找不到 employee_list 模組。")

    # 4. 編輯員工資料
    with tabs[3]:
        if edit_profile:
            func = getattr(edit_profile, "render_edit_profile", None) or \
                   getattr(edit_profile, "render", None) or \
                   getattr(edit_profile, "main", None)
            if func:
                func(engine=engine, lang=active_lang)
            else:
                st.info("「編輯員工資料」模組找不到可用渲染函式。")
        else:
            st.info("找不到 edit_profile 模組。")

    # 5. 離職名冊管理
    with tabs[4]:
        if resigned_list:
            func = getattr(resigned_list, "render_resigned_list", None) or \
                   getattr(resigned_list, "render", None) or \
                   getattr(resigned_list, "main", None)
            if func:
                func(engine=engine, lang=active_lang)
            else:
                st.info("「離職名冊管理」模組找不到可用渲染函式。")
        else:
            st.info("找不到 resigned_list 模組。")

def render(engine=None, lang="繁體中文", **kwargs):
    render_hr_profile_page(engine=engine, lang=lang, **kwargs)

def show(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)

def main(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)

def render_employee_profile(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)

def render_employee_management(*args, **kwargs):
    render_hr_profile_page(*args, **kwargs)
