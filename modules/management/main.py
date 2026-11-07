# ==========================================
# 檔案路徑：modules/management/main.py
# 職責：管理部 L1 進入點，透過頂部子模組卡片列導覽，實現手機優先的分層架構
# ==========================================

import streamlit as st
import importlib

def render_management_module(engine=None, lang="繁體中文", **kwargs):
    current_lang = lang if lang in ["繁體中文", "Tiếng Việt", "English"] else "繁體中文"

    # 1. 頂部子模組分類卡片導覽（符合手機優先原則，絕不讓選單無限拉長）
    st.markdown("### 🏢 管理部 - 業務模組分層導覽")
    st.markdown("---")

    sub_modules = [
        {"id": "announcement", "name_zh": "📢 公告欄管理", "name_vi": "Quản lý thông báo", "desc": "發布公司公告與佈告欄管理"},
        {"id": "employee", "name_zh": "👤 員工個人檔案", "name_vi": "Hồ sơ nhân sự", "desc": "越籍、外派幹部檔案、護照/TRC與90天預警"},
        {"id": "attendance", "name_zh": "⏱️ 考勤與出勤", "name_vi": "Chấm công cố định", "desc": "上下班固定打卡、GPS外勤與請假審核"},
        {"id": "payroll", "name_zh": "💰 薪資與保險", "name_vi": "Tính lương & Bảo hiểm", "desc": "薪資計算、加班費與BHXH社會保險扣繳"},
        {"id": "asset_dorm", "name_zh": "🥗 宿舍與採購", "name_vi": "Ký túc xá & Suất ăn", "desc": "幹部宿舍伙食與採購控管"},
        {"id": "vehicle", "name_zh": "🚗 車輛與維修", "name_vi": "Quản lý xe & Bảo trì", "desc": "廠區車輛門禁、派車審核與維修保養"},
        {"id": "finance_ap", "name_zh": "🛒 採購與應付 (AP)", "name_vi": "Mua hàng & Phải trả", "desc": "採購單與應付帳款管理"},
        {"id": "finance_ar", "name_zh": "📋 應收與財報 (AR)", "name_vi": "Phải thu & Báo cáo thuế", "desc": "應收帳款對帳與越南 Thông tư 200 財報"},
    ]

    # 初始化當前選中的子模組
    if 'mgmt_active_sub' not in st.session_state:
        st.session_state['mgmt_active_sub'] = 'employee'

    # 以 4 欄式卡片網格呈現頂部導覽
    cols = st.columns(4)
    for idx, sm in enumerate(sub_modules):
        is_active = (st.session_state['mgmt_active_sub'] == sm['id'])
        btn_type = "primary" if is_active else "secondary"
        
        with cols[idx % 4]:
            with st.container(border=True):
                title_text = sm['name_vi'] if current_lang == "Tiếng Việt" else sm['name_zh']
                st.markdown(f"#### {title_text}")
                st.caption(sm['desc'])
                if st.button(f"進入專區 ➡️", key=f"btn_sub_{sm['id']}", use_container_width=True, type=btn_type):
                    st.session_state['mgmt_active_sub'] = sm['id']
                    st.rerun()

    st.markdown("---")

    # 2. 路由分發到對應的子資料夾檔案
    active_sub = st.session_state['mgmt_active_sub']

    try:
        if active_sub == 'announcement':
            mod = importlib.import_module("modules.management.announcements.announcement_hub")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)
            elif hasattr(mod, "show"):
                mod.show(engine=engine, lang=current_lang)

        elif active_sub == 'employee':
            mod = importlib.import_module("modules.management.hr.employee_profile")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)
            elif hasattr(mod, "show"):
                mod.show(engine=engine, lang=current_lang)

        elif active_sub == 'attendance':
            mod = importlib.import_module("modules.management.hr.field_gps_attendance")
            if hasattr(mod, "render_field_attendance_page"):
                mod.render_field_attendance_page(engine=engine, lang=current_lang, view_mode="all")
            elif hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif active_sub == 'payroll':
            mod = importlib.import_module("modules.management.hr.payroll_insurance")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif active_sub == 'asset_dorm':
            mod = importlib.import_module("modules.management.admin_assets.dom_catering")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif active_sub == 'vehicle':
            mod = importlib.import_module("modules.management.admin_assets.vehicle_dispatch")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif active_sub == 'finance_ap':
            mod = importlib.import_module("modules.management.legal_finance.general_purchase")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif active_sub == 'finance_ar':
            mod = importlib.import_module("modules.management.legal_finance.tax_reports") # 對應 Thông tư 200 與 AR
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        else:
            st.info(f"💡 正在載入選定的模組專區...")

    except Exception as e:
        st.error(f"⚠️ 載入管理部子模組發生異常: {str(e)}")

def show(engine=None, lang="繁體中文", **kwargs):
    render_management_module(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_management_module(engine=engine, lang=lang, **kwargs)
