import streamlit as st
from sqlalchemy import text

# 🌟 使用 try-except 防護，避免因為相對路徑找不到而導致整個頁面報錯
try:
    from modules.management.hr.employee.add_vietnamese import render_add_vietnamese
except ImportError:
    try:
        from .add_vietnamese import render_add_vietnamese
    except:
        render_add_vietnamese = lambda *a, **k: st.info("「新增越南員工」模組建置中")

try:
    from modules.management.hr.employee.add_expat import render_add_expat
except ImportError:
    try:
        from .add_expat import render_add_expat
    except:
        render_add_expat = lambda *a, **k: st.info("「新增外派幹部」模組建置中")

try:
    from modules.management.hr.employee.employee_list import render_employee_list
except ImportError:
    try:
        from .employee_list import render_employee_list
    except:
        render_employee_list = lambda *a, **k: st.info("「員工總名冊」模組建置中")

try:
    from modules.management.hr.employee.edit_profile import render_edit_profile
except ImportError:
    try:
        from .edit_profile import render_edit_profile
    except:
        render_edit_profile = lambda *a, **k: st.info("「編輯員工資料」模組建置中")

try:
    from modules.management.hr.employee.resigned_list import render_resigned_list
except ImportError:
    try:
        from .resigned_list import render_resigned_list
    except:
        render_resigned_list = lambda *a, **k: st.info("「離職名冊管理」模組建置中")
