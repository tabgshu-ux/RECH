# ==========================================
# 檔案路徑：app.py
# 職責：系統主入口，統一管理初始化、Session State、動態品牌識別、全域常駐側邊欄導航與路由分發
# ==========================================

import streamlit as st
import pandas as pd
import importlib
import os
from sqlalchemy import text, create_engine
from modules.it_system.admin_settings import render_admin_settings
from views.login import render_login_page
from views.dashboard import render_dashboard

st.set_page_config(
    page_title="裕豐電機工業 SaaS ERP",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

MOBILE_CSS_AND_JS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.35rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.15rem !important; }
    h3, .stSubheader { font-size: 1.05rem !important; }
    p, div, span, label { font-size: 0.9rem !important; }
    .block-container { padding: 1rem 0.5rem !important; }
}
</style>
"""
st.markdown(MOBILE_CSS_AND_JS, unsafe_allow_html=True)

# 1. 初始化基礎 Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'dashboard'
if 'active_feature_id' not in st.session_state:
    st.session_state['active_feature_id'] = None
if 'selected_module_id' not in st.session_state:
    st.session_state['selected_module_id'] = None
if 'current_lang' not in st.session_state:
    st.session_state['current_lang'] = 'zh'
if 'tenant_id' not in st.session_state:
    st.session_state['tenant_id'] = 'REETECH_VN'
if 'selected_dept' not in st.session_state:
    st.session_state['selected_dept'] = '總經理室'

@st.cache_resource
def get_db_engine():
    db_url = os.environ.get("SUPABASE_DB_URL") or st.secrets.get("SUPABASE_DB_URL", "")
    if db_url:
        clean_url = db_url.strip()
        if "pooler.supabase.com" in clean_url and "?" not in clean_url:
            clean_url += "?sslmode=require"
        try:
            return create_engine(clean_url, pool_pre_ping=True, connect_args={"prepare_threshold": None})
        except Exception:
            return None
    return None

db_engine = get_db_engine()

# 2. 啟動時自動從資料庫載入最新企業品牌識別（Logo 與名稱）
if 'tenant_company_name' not in st.session_state:
    st.session_state['tenant_company_name'] = "裕豐電機工業有限公司"
if 'tenant_company_sub' not in st.session_state:
    st.session_state['tenant_company_sub'] = "CÔNG TY TNHH CN DỮ PHONG"
if 'tenant_logo_url' not in st.session_state:
    st.session_state['tenant_logo_url'] = ""

if db_engine and not st.session_state.get('branding_loaded_from_db', False):
    try:
        with db_engine.connect() as conn:
            res = conn.execute(
                text("SELECT company_name, company_subtitle, logo_url FROM tenant_settings WHERE tenant_id = :tid"),
                {"tid": st.session_state['tenant_id']}
            ).fetchone()
            if res:
                st.session_state['tenant_company_name'] = res[0] or "裕豐電機工業有限公司"
                st.session_state['tenant_company_sub'] = res[1] or "CÔNG TY TNHH CN DỮ PHONG"
                st.session_state['tenant_logo_url'] = res[2] or ""
        st.session_state['branding_loaded_from_db'] = True
    except Exception:
        pass

# 3. 登入檢查
if not st.session_state['logged_in']:
    render_login_page(db_engine)
    st.stop()

# ==========================================
# 🌟 全域常駐側邊欄 (Sidebar)：確保在「任何頁面（包含系統設定與子模組）」左側部門選單都永遠顯示！
# ==========================================
with st.sidebar:
    st.markdown("### 🏢 企業組織樹狀導航")
    st.caption("僅顯示 L1 核心一級部門，點擊即時切換。")
    
    depts = []
    try:
        if db_engine:
            with db_engine.connect() as conn:
                res = conn.execute(text("""
                    SELECT dept_name_zh, dept_name, name, level_tier 
                    FROM sys_departments 
                    WHERE is_active = TRUE
                """)).fetchall()
                
                for r in res:
                    d_name = r[0] or r[1] or r[2] or '未命名部門'
                    tier = str(r[3] or 'L1').upper()
                    is_l1 = ('L1' in tier) or (d_name in ["總經理室", "工程部", "管理部", "生產部", "倉庫管理", "簽核中心"])
                    exclude_l2 = any(sub in d_name for sub in ["人事", "行政", "總務", "採購", "財務", "會計", "設計", "課"])
                    
                    if is_l1 and not exclude_l2:
                        if d_name not in depts:
                            depts.append(d_name)
    except Exception:
        pass
    
    if not depts:
        depts = ["總經理室", "工程部", "管理部", "生產部", "倉庫管理"]

    # 側邊欄 L1 部門按鈕
    for d in depts:
        is_selected = (st.session_state.get('current_view') == 'dashboard' and st.session_state.get('selected_dept') == d)
        btn_type = "primary" if is_selected else "secondary"
        if st.button(f"🏛️ {d}", key=f"global_sidebar_dept_{d}", use_container_width=True, type=btn_type):
            st.session_state['selected_dept'] = d
            st.session_state['current_view'] = 'dashboard'
            st.session_state['active_feature_id'] = None
            st.rerun()

    st.divider()

    # ⚙️ 系統設定按鈕固定在側邊欄下方
    is_settings_active = (st.session_state.get('active_feature_id') == 'feat_it_menu')
    settings_btn_type = "primary" if is_settings_active else "secondary"
    if st.button("⚙️ 系統設定 (Cấu hình hệ thống)", use_container_width=True, type=settings_btn_type):
        st.session_state['current_view'] = 'dynamic_feature'
        st.session_state['active_feature_id'] = 'feat_it_menu'
        st.rerun()

# ==========================================
# 主畫面頂部導覽列
# ==========================================
dynamic_company_name = st.session_state.get('tenant_company_name', "裕豐電機工業有限公司")
dynamic_logo_path = st.session_state.get('tenant_logo_url', "")

col_logo, col_user, col_nav, col_logout = st.columns([5, 2, 2, 1])
with col_logo:
    if dynamic_logo_path and os.path.exists(dynamic_logo_path):
        c_img, c_text = st.columns([1, 4], vertical_alignment="center")
        with c_img:
            st.image(dynamic_logo_path, width=140)
        with c_text:
            st.markdown(f"<h3 style='margin: 0; padding-top: 5px;'>{dynamic_company_name}</h3>", unsafe_allow_html=True)
    else:
        st.subheader(f"🏭 {dynamic_company_name}")

with col_user:
    st.caption(f"👤 {st.session_state['user_name']}")
with col_nav:
    if st.session_state['current_view'] != 'dashboard':
        if st.button("🏠 回部門選單", use_container_width=True):
            st.session_state['current_view'] = 'dashboard'
            st.session_state['active_feature_id'] = None
            st.rerun()
with col_logout:
    if st.button("🚪 登出", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['current_view'] = 'dashboard'
        st.rerun()

# ==========================================
# 🌟 全域置頂顯示：管理部發布的最新公司公告佈告欄
# ==========================================
def render_global_announcements_banner(engine):
    announcements = []
    try:
        if engine:
            with engine.connect() as conn:
                for tbl in ['hr_announcements', 'company_announcements', 'sys_announcements']:
                    try:
                        res = conn.execute(text(f"SELECT title, content, updated_at FROM {tbl} ORDER BY id DESC LIMIT 3")).fetchall()
                        if res:
                            for r in res:
                                announcements.append(f"📢 **{r[0]}**：{r[1]}")
                            break
                    except Exception:
                        continue
    except Exception:
        pass

    if not announcements:
        announcements = [
            "📢 **【管理部公告】** 11月份全廠消防安全演練訂於 11/25 進行，請各部門主管配合轉知同仁。",
            "📢 **【管理部公告】** 越籍員工宿舍冷氣維修申請已開放登記，請至總務課窗口辦理。"
        ]

    with st.container(border=True):
        st.markdown("##### 📢 【管理部佈告欄】全廠即時公告專區")
        cols = st.columns(len(announcements) if len(announcements) <= 3 else 3)
        for idx, ann in enumerate(announcements[:3]):
            with cols[idx]:
                st.info(ann)

render_global_announcements_banner(db_engine)

st.divider()

current_lang = st.session_state.get('current_lang', 'zh')

# 5. 主畫面路由分發
if st.session_state['current_view'] == 'dashboard':
    render_dashboard(db_engine)
elif st.session_state['current_view'] == 'dynamic_feature':
    active_feat_id = str(st.session_state.get('active_feature_id', ''))
    
    # 🌟 IT 系統設定
    if active_feat_id == 'feat_it_menu':
        render_admin_settings(db_engine, lang=current_lang)
        
    # 🌟 管理部主管戰情室
    elif active_feat_id == 'feat_mgmt_supervisor':
        try:
            from modules.management.supervisor_dashboard import render
            render(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入管理部主管總覽發生錯誤: {e}")

    # 🌟 公司公告佈告欄管理模組
    elif active_feat_id == 'feat_announcements':
        try:
            from modules.management import announcements_mgr
            if hasattr(announcements_mgr, "render"):
                announcements_mgr.render(db_engine=db_engine, lang=current_lang)
            else:
                st.markdown("### 📢 公司公告佈告欄管理")
                st.info("在此發布與維護全廠公告，將即時同步顯示於所有頁面頂端。")
        except Exception as e:
            st.markdown("### 📢 公司公告佈告欄管理")
            st.info("📢 管理部公告發布與維護功能運作中。")
            
    # 🌟 智慧判斷：獨立導向員工檔案、考勤、薪資頁面
    elif '員工' in active_feat_id or '履約' in active_feat_id or active_feat_id == 'feat_hr':
        try:
            from modules.management.hr.employee import employee_profile
            if hasattr(employee_profile, "render_hr_profile_page"):
                employee_profile.render_hr_profile_page(engine=db_engine, lang=current_lang)
            elif hasattr(employee_profile, "render"):
                employee_profile.render(db_engine=db_engine, lang=current_lang)
            else:
                st.error("找不到 employee_profile 的渲染入口函式。")
        except Exception as e:
            st.error(f"載入員工檔案管理模組發生錯誤: {e}")

    elif '考勤' in active_feat_id or '打卡' in active_feat_id:
        try:
            from modules.management.hr.attendance import attendance_punch
            if hasattr(attendance_punch, "render"):
                attendance_punch.render(db_engine=db_engine, lang=current_lang)
            elif hasattr(attendance_punch, "main"):
                attendance_punch.main(db_engine=db_engine, lang=current_lang)
            else:
                st.info("⏱️ 考勤打卡模組已載入。")
        except Exception as e:
            st.error(f"載入考勤打卡模組發生錯誤: {e}")

    elif '薪資' in active_feat_id or '保險' in active_feat_id or 'BHXH' in active_feat_id:
        try:
            from modules.management.hr import payroll_management
            if hasattr(payroll_management, "render"):
                payroll_management.render(db_engine=db_engine, lang=current_lang)
            elif hasattr(payroll_management, "render_payroll_management"):
                payroll_management.render_payroll_management(db_engine=db_engine, lang=current_lang)
            else:
                st.info("💰 薪資計算與保險模組已載入。")
        except Exception as e:
            st.error(f"載入薪資保險模組發生錯誤: {e}")

    # 🌟 其他部門模組路由
    elif active_feat_id == 'feat_ga':
        try:
            from modules.procurement_ap import render_procurement_ap_page
            render_procurement_ap_page(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入總務採購模組發生錯誤: {e}")
    elif active_feat_id == 'feat_fi':
        try:
            from modules.financial_tax_reports import render_financial_tax_reports_page
            render_financial_tax_reports_page(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入財務會計模組發生錯誤: {e}")
    elif active_feat_id == 'feat_site_log':
        try:
            from modules.engineering_management import render_engineering_management_page
            render_engineering_management_page(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入工程管理模組發生錯誤: {e}")
    elif active_feat_id == 'feat_panel_build':
        try:
            from modules.assembly import render_assembly_module
            render_assembly_module(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入生產組裝模組發生錯誤: {e}")
    elif active_feat_id == 'feat_material':
        try:
            from modules.warehouse_management import render_warehouse_management
            render_warehouse_management(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入倉庫管理模組發生錯誤: {e}")
    elif active_feat_id == 'feat_my_approvals':
        try:
            from modules.approval_workflow import render_approval_center
            render_approval_center(lang=current_lang)
        except Exception as e:
            st.error(f"載入簽核中心發生錯誤: {e}")
    else:
        st.info(f"💡 功能代碼 [{active_feat_id}] 正在建置中，您可以透過上方按鈕返回部門選單。")
