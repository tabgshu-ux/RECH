import inspect
import modules.approval_workflow as approval_workflow
import modules.asset_management as asset_management
import modules.db_connection as db_conn
import modules.employee_management as employee_management
import modules.engineering_pipeline as engineering_pipeline
import modules.executive_dashboard as executive_dashboard
import modules.field_attendance as field_attendance  # 外勤工程人員 GPS 與拍照打卡模組
import modules.invoice_management as invoice_management
import modules.payroll_management as payroll_management
import modules.procurement_ap as procurement_ap
import modules.sales_order_ar as sales_order_ar
import modules.system_licensing as system_licensing
import modules.user_management as user_management
import modules.vehicle_gate_log as vehicle_gate_log  # 車輛進出與門禁時間紀錄模組
import modules.warehouse_management as warehouse_management
import pandas as pd
from sqlalchemy import text
import streamlit as st

# 📱 100% 移動優先：設定頁面並預設手機側邊欄展開
st.set_page_config(
    page_title="裕豐電機工業 REETECH INDUSTRIAL AI ERP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------
# 📱 注入手機優先 RWD CSS 與 側邊欄滑動/點擊手勢優化 JS
# ----------------------------------------------------
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

<script>
// 📱 手機板側邊欄手勢優化：支援在側邊欄內向左滑動直接收回目錄，免回頂部
document.addEventListener('DOMContentLoaded', () => {
    let touchstartX = 0;
    let touchendX = 0;

    function handleGesure() {
        if (touchendX < touchstartX - 50) {
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (sidebar && window.innerWidth <= 768) {
                const closeBtn = document.querySelector('[data-testid="stSidebar"] button[kind="tertiary"], [data-testid="stSidebar"] button');
                if (closeBtn) {
                    closeBtn.click();
                }
            }
        }
    }

    document.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX;
    }, false);

    document.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX;
        handleGesure();
    }, false);
});
</script>
"""
st.markdown(MOBILE_CSS_AND_JS, unsafe_allow_html=True)

# ----------------------------------------------------
# 🏢 RECH 企業品牌 Logo 橫幅
# ----------------------------------------------------
RECH_LOGO_HTML = """
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 15px; padding: 6px 8px; background: transparent; border-bottom: 2px solid rgba(15, 23, 42, 0.15);">
    <div style="font-size: 28px; font-weight: 900; color: #000055; letter-spacing: -1px; line-height: 1; font-family: 'Segoe UI', Arial, sans-serif;">RECH</div>
    <div style="border-left: 2px solid #000055; padding-left: 8px; line-height: 1.15; font-family: 'Segoe UI', Arial, sans-serif;">
        <div style="font-size: 13px; font-weight: 800; color: #000055; letter-spacing: 0.5px;">裕豐電機工業有限公司</div>
        <div style="font-size: 8.5px; font-weight: 700; color: #1E293B; letter-spacing: 0.2px;">REETECH INDUSTRIAL CO., LTD</div>
        <div style="font-size: 8px; font-weight: 700; color: #334155; letter-spacing: 0.1px;">CÔNG TY TNHH CN DŨ PHONG</div>
    </div>
</div>
"""

# ----------------------------------------------------
# 三階組織架構選單字典（已將工務部更名為工程部）
# ----------------------------------------------------
NAV_STRUCTURE = {
    "繁體中文": {
        "company_name": "裕豐電機工業有限公司",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ 裕豐電機工業 REETECH INDUSTRIAL - 系統登入",
        "username": "帳號",
        "password": "密碼",
        "login_btn": "🔑 登入系統",
        "logout_btn": "🚪 登出系統",
        "lang_selector": "🌐 語言設定 / Language",
        "parent_header": "請選擇一級部門：",
        "sub_header": "選擇子部門與功能：",
        "departments": {
            "📈 營運戰情室 (Executive)": {
                "features": {
                    "🔴 原料價格與隨時股市物價/匯率": "commodities_fx",
                    "📊 財務類顯示資料 (AR/AP & P&L)": "financials_pl",
                    "⚡ 工程專案進度與驗收資料": "project_progress",
                }
            },
            "👔 管理部 (Management Dept)": {
                "features": {
                    "🏢 [行政] 固定資產設備與總務採購": "ga_assets",
                    "✍️ [行政] 電子簽核與請款審核中心": "approval_center",
                    "👤 [行政] 員工個人檔案與人事管理 (人事)": "hr_employee",
                    "🚗 [行政] 廠區車輛進出與門禁時間紀錄": "vehicle_gate",
                    "📍 [外勤] 工程人員 GPS 拍照打卡": "field_attendance",
                    "🧾 [財務] 採購與應付帳款 (AP)": "procurement_ap",
                    "📋 [財務] 銷售與應收帳款 (AR)": "sales_order_ar",
                    "💰 [財務] 全球員工薪資與保險扣款試算": "payroll_calc",
                    "📄 [財務] 越南電子發票綜合管理中心": "invoice_management",
                }
            },
            "🛠️ 工程部 (Engineering Dept)": {
                "features": {
                    "📐 [設計] 配電盤電氣與機構設計圖庫": "engineering_quote",
                    "⚡ [工程] 配電盤估價與資材報價總合": "engineering_quote",
                    "🔍 [品管] 工程驗收與品質檢驗紀錄": "project_progress",
                }
            },
            "🏭 生產部 (Production Dept)": {
                "features": {
                    "📦 [倉儲] 倉庫庫存與資材條碼管理": "wh_management",
                    "✂️ [板金] 板金加工組工單與條碼": "sheet_metal",
                    "🎨 [塗料] 粉體塗裝烤漆組品管": "painting",
                    "⚡ [配盤] 配電盤組裝配線組": "assembly",
                }
            },
            "💻 資訊管理部 (IT & System)": {
                "features": {
                    "🔒 帳號權限與全系統稽核軌跡": "it_admin",
                    "🎛️ 客戶 ERP 模組授權與功能開關": "it_licensing",
                }
            },
        },
    },
    "Tiếng Việt": {
        "company_name": "CÔNG TY TNHH CN DŨ PHONG",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ REETECH INDUSTRIAL - Đăng nhập hệ thống",
        "username": "Tài khoản",
        "password": "Mật khẩu",
        "login_btn": "🔑 Đăng nhập",
        "logout_btn": "🚪 Đăng xuất",
        "lang_selector": "🌐 Chọn ngôn ngữ",
        "parent_header": "Chọn phòng ban chính:",
        "sub_header": "Chọn bộ phận trực thuộc:",
        "departments": {
            "📈 Ban Giám đốc (Executive)": {
                "features": {
                    "🔴 Giá Nguyên liệu & Tỷ giá": "commodities_fx",
                    "📊 Dữ liệu Tài chính": "financials_pl",
                    "⚡ Tiến độ Dự án Kỹ thuật": "project_progress",
                }
            },
            "👔 Phòng Quản lý (Management Dept)": {
                "features": {
                    "🏢 [Hành chính] Quản lý Tài sản Cố định": "ga_assets",
                    "✍️️ [Hành chính] Trung tâm Phê duyệt": "approval_center",
                    "👤 [Nhân sự] Hồ sơ Nhân sự & Hợp đồng": "hr_employee",
                    "🚗 [Bảo vệ] Quản lý xe ra vào nhà máy": "vehicle_gate",
                    "📍 [Hiện trường] Chấm công GPS kỹ sư": "field_attendance",
                    "🛒 [Tài chính] Mua hàng & Phải trả (AP)": "procurement_ap",
                    "📋 [Tài chính] Quản lý Bán hàng (AR)": "sales_order_ar",
                    "💰 [Tài chính] Tính Lương & Khấu trừ": "payroll_calc",
                    "📄 [Tài chính] Quản lý Hóa đơn điện tử tổng hợp": "invoice_management",
                }
            },
            "🛠️ Phòng Kỹ thuật (Engineering Dept)": {
                "features": {
                    "📐 [Thiết kế] Bản vẽ Tủ điện": "engineering_quote",
                    "⚡ [Kỹ thuật] Báo giá Tủ điện & Dự toán": "engineering_quote",
                    "🔍 [QC] Kiểm tra Chất lượng": "project_progress",
                }
            },
            "🏭 Phòng Sản xuất (Production Dept)": {
                "features": {
                    "📦 [Kho] Quản lý Kho & Mã vạch": "wh_management",
                    "✂️️ [Gia công] Tổ Gia công Cơ khí": "sheet_metal",
                    "🎨 [Sơn] Tổ Sơn tĩnh điện": "painting",
                    "⚡ [Lắp ráp] Tổ Lắp ráp Tủ điện": "assembly",
                }
            },
            "💻 Phòng IT (IT & System)": {
                "features": {
                    "🔒 Quản lý Phân quyền": "it_admin",
                    "🎛️ Phân quyền Bản quyền ERP": "it_licensing",
                }
            },
        },
    },
    "English": {
        "company_name": "REETECH INDUSTRIAL CO., LTD",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ REETECH INDUSTRIAL - System Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "🔑 Login",
        "logout_btn": "🚪 Logout",
        "lang_selector": "🌐 Select Language",
        "parent_header": "Select Department:",
        "sub_header": "Select Unit & Features:",
        "departments": {
            "📈 Executive Management": {
                "features": {
                    "🔴 Raw Material Prices & FX": "commodities_fx",
                    "📊 Financial Analytics": "financials_pl",
                    "⚡ Engineering Project Progress": "project_progress",
                }
            },
            "👔 Management Dept (GA & Finance)": {
                "features": {
                    "🏢 [GA] Asset Management": "ga_assets",
                    "✍️ [GA] E-Approval Center": "approval_center",
                    "👤 [HR] Employee Records": "hr_employee",
                    "🚗 [Security] Vehicle Gate Log": "vehicle_gate",
                    "📍 [Field] Engineer GPS Attendance": "field_attendance",
                    "🛒 [Finance] Procurement & AP": "procurement_ap",
                    "📋 [Finance] Sales & AR": "sales_order_ar",
                    "💰 [Finance] Payroll & Insurance": "payroll_calc",
                    "📄 [Finance] E-Invoice Comprehensive Center": "invoice_management",
                }
            },
            "🛠️ Engineering Dept": {
                "features": {
                    "📐 [Design] Switchgear Drawings": "engineering_quote",
                    "⚡ [Engineering] Costing & Quotation": "engineering_quote",
                    "🔍 [QC] Quality Inspection": "project_progress",
                }
            },
            "🏭 Production Dept": {
                "features": {
                    "📦 [Warehouse] Material Barcodes": "wh_management",
                    "✂️ [Sheet Metal] Processing Dept": "sheet_metal",
                    "🎨 [Coating] Powder Coating Dept": "painting",
                    "⚡ [Assembly] Switchgear Assembly": "assembly",
                }
            },
            "💻 Information Technology (IT)": {
                "features": {
                    "🔒 User Permissions": "it_admin",
                    "🎛️ Client ERP Licensing": "it_licensing",
                }
            },
        },
    },
}

if "current_lang" not in st.session_state:
    st.session_state.current_lang = "繁體中文"

# ----------------------------------------------------
# 取得資料庫引擎
# ----------------------------------------------------
engine = db_conn.get_db_engine()

def safe_call_module(func, *args, **kwargs):
    if not callable(func):
        return
    try:
        sig = inspect.signature(func)
        valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        if "engine" in sig.parameters and "engine" not in valid_kwargs:
            valid_kwargs["engine"] = engine
        func(*args, **valid_kwargs)
    except Exception:
        try:
            func()
        except Exception as e:
            st.error(f"模組載入異常: {str(e)}")

# ----------------------------------------------------
# 登入系統
# ----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_name = ""

lang_dict = NAV_STRUCTURE.get(
    st.session_state.current_lang, NAV_STRUCTURE["繁體中文"]
)

if not st.session_state.logged_in:
    st.markdown(RECH_LOGO_HTML, unsafe_allow_html=True)
    st.title(lang_dict["login_title"])
    st.caption(lang_dict["company_sub"])
    st.markdown("---")
    col1, _ = st.columns([1, 2])
    with col1:
        username = st.text_input(
            f"{lang_dict['username']} (admin / manager / security / staff)"
        )
        password = st.text_input(
            f"{lang_dict['password']} (123)", type="password"
        )
        if st.button(lang_dict["login_btn"], use_container_width=True):
            if password == "123":
                st.session_state.logged_in = True
                u_clean = username.strip().lower()
                
                if u_clean in ["admin", "executive", "boss"]:
                    st.session_state.user_role = "admin"
                elif u_clean in ["manager", "supervisor"]:
                    st.session_state.user_role = "manager"
                elif u_clean in ["security", "guard", "門禁保全"]:
                    st.session_state.user_role = "security"
                else:
                    st.session_state.user_role = "staff"

                st.session_state.user_name = username
                st.rerun()
            else:
                st.error("帳號或密碼錯誤 / Incorrect password")
    st.stop()

# ----------------------------------------------------
# 側邊欄選單
# ----------------------------------------------------
st.sidebar.markdown(RECH_LOGO_HTML, unsafe_allow_html=True)

lang_list = ["繁體中文", "Tiếng Việt", "English"]
selected_lang = st.sidebar.selectbox(
    lang_dict["lang_selector"],
    lang_list,
    index=(
        lang_list.index(st.session_state.current_lang)
        if st.session_state.current_lang in lang_list
        else 0
    ),
)

if selected_lang != st.session_state.current_lang:
    st.session_state.current_lang = selected_lang
    st.rerun()

st.sidebar.markdown(
    f"**👤 {st.session_state.user_name}** ({st.session_state.user_role.upper()})"
)
if st.sidebar.button(lang_dict["logout_btn"], use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

dept_options = list(lang_dict["departments"].keys())
current_user_clean = str(st.session_state.user_name).strip().lower()
current_role_clean = str(st.session_state.user_role).strip().lower()

if current_role_clean == "security":
    dept_options = ["👔 管理部 (Management Dept)"]
    selected_parent_dept = dept_options[0]
    st.sidebar.markdown(f"**{lang_dict['parent_header']}**")
    feature_labels = ["🚗 [行政] 廠區車輛進出與門禁時間紀錄"] if st.session_state.current_lang == "繁體中文" else (
        ["🚗 [Bảo vệ] Quản lý xe ra vào nhà máy"] if st.session_state.current_lang == "Tiếng Việt" else ["🚗 [Security] Vehicle Gate Log"]
    )
    selected_feature_label = feature_labels[0]
    target_route = "vehicle_gate"
else:
    is_executive_access = (
        current_user_clean in ["admin", "executive", "boss", "ceo", "gm"]
        or current_role_clean in ["admin", "executive", "manager"]
    )

    if not is_executive_access:
        dept_options = [d for d in dept_options if "Executive" not in d]

    selected_parent_dept = st.sidebar.radio(
        lang_dict["parent_header"], dept_options, index=0
    )

    st.sidebar.markdown("---")
    features_dict = lang_dict["departments"][selected_parent_dept]["features"]
    feature_labels = list(features_dict.keys())

    st.sidebar.caption(f"**{selected_parent_dept.split('(')[0].strip()}**")
    selected_feature_label = st.sidebar.radio(
        lang_dict["sub_header"], feature_labels
    )
    target_route = features_dict[selected_feature_label]

# ----------------------------------------------------
# 模組安全路由分流
# ----------------------------------------------------
curr_lang = st.session_state.current_lang

if target_route in ["commodities_fx", "financials_pl", "project_progress"]:
    if hasattr(executive_dashboard, "render_executive_dashboard_page"):
        safe_call_module(
            executive_dashboard.render_executive_dashboard_page,
            sub_route=target_route,
            lang=curr_lang,
        )
    elif hasattr(executive_dashboard, "show"):
        safe_call_module(
            executive_dashboard.show, sub_route=target_route, lang=curr_lang
        )

elif target_route == "procurement_ap":
    safe_call_module(
        procurement_ap.render_procurement_ap_page,
        engine=engine,
        lang=curr_lang,
    )

elif target_route == "sales_order_ar":
    safe_call_module(
        sales_order_ar.render_sales_order_ar_page,
        engine=engine,
        lang=curr_lang,
    )

elif target_route == "payroll_calc":
    safe_call_module(
        payroll_management.render_payroll_management_page,
        engine=engine,
        lang=curr_lang,
    )

elif target_route == "invoice_management":
    safe_call_module(
        invoice_management.render_invoice_management,
        engine=engine,
        lang=curr_lang,
    )

elif target_route == "field_attendance":
    safe_call_module(
        field_attendance.render_field_attendance_page,
        engine=engine,
        lang=curr_lang,
    )

elif target_route == "engineering_quote":
    safe_call_module(engineering_pipeline.render_engineering_page)

elif target_route == "ga_assets":
    safe_call_module(
        asset_management.render_asset_management_page, lang=curr_lang
    )

elif target_route == "approval_center":
    safe_call_module(approval_workflow.render_approval_center, lang=curr_lang)

elif target_route == "hr_employee":
    safe_call_module(
        employee_management.render_employee_management,
        engine=engine,
        t=lang_dict,
        lang=curr_lang,
    )

elif target_route == "vehicle_gate":
    safe_call_module(
        vehicle_gate_log.render_vehicle_gate_log_page,
        engine=engine,
        lang=curr_lang,
    )

elif target_route == "wh_management":
    safe_call_module(
        warehouse_management.render_warehouse_management,
        engine=engine,
        lang=curr_lang,
    )

elif target_route in ["sheet_metal", "painting", "assembly"]:
    st.title(selected_feature_label)
    st.info(
        "Hệ thống đang hoạt động bình thường /"
        " 現場工單追蹤與 QC 品質檢驗模組順利運作中。"
    )

elif target_route == "it_admin":
    safe_call_module(
        user_management.render_user_management_page, lang=curr_lang
    )

elif target_route == "it_licensing":
    safe_call_module(
        system_licensing.render_licensing_control_page, lang=curr_lang
    )
