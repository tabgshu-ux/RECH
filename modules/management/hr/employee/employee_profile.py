import streamlit as st
from sqlalchemy import text

# 🌟 正確的相對路徑引入同資料夾底下的子模組
try:
    from .add_vietnamese import render_add_vietnamese
except ImportError:
    from add_vietnamese import render_add_vietnamese

try:
    from .add_expat import render_add_expat
except ImportError:
    from add_expat import render_add_expat

try:
    from .employee_list import render_employee_list
except ImportError:
    from employee_list import render_employee_list

try:
    from .edit_profile import render_edit_profile
except ImportError:
    from edit_profile import render_edit_profile

try:
    from .resigned_list import render_resigned_list
except ImportError:
    try:
        from resigned_list import render_resigned_list
    except:
        render_resigned_list = lambda *a, **k: st.info("離職名冊模組建置中")

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

    with tabs[0]:
        render_add_vietnamese(engine=engine, lang=active_lang)
    with tabs[1]:
        render_add_expat(engine=engine, lang=active_lang)
    with tabs[2]:
        render_employee_list(engine=engine, lang=active_lang)
    with tabs[3]:
        render_edit_profile(engine=engine, lang=active_lang)
    with tabs[4]:
        render_resigned_list(engine=engine, lang=active_lang)

# 🌟 提供所有可能的標準呼叫入口，確保 100% 完美對接
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
