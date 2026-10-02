import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# ----------------------------------------------------
# 1. 載入各獨立業務模組 (Modules)
# ----------------------------------------------------
import modules.executive_dashboard as executive_dashboard
import modules.procurement_ap as procurement_ap
import modules.sales_order_ar as sales_order_ar
import modules.approval_workflow as approval_workflow
import modules.warehouse_management as warehouse_management
import modules.employee_management as employee_management
import modules.asset_management as asset_management
import modules.user_management as user_management
import modules.engineering_pipeline as engineering_pipeline
import modules.invoice_management as invoice_management

st.set_page_config(
    page_title="裕豐電機工業 REETECH INDUSTRIAL - AI ERP",
    page_icon="⚡",
    layout="wide"
)

# ----------------------------------------------------
# 2. 階層式多國語言字典 (i18n Multi-level Navigation)
# ----------------------------------------------------
NAV_STRUCTURE = {
    "繁體中文": {
        "company_name": "⚡ 裕豐電機工業",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ 裕豐電機工業 REETECH INDUSTRIAL - 系統登入",
        "username": "帳號",
        "password": "密碼",
        "login_btn": "🔑 登入系統",
        "logout_btn": "🚪 登出系統",
        "lang_selector": "🌐 語言設定 / Language",
        "parent_header": "請選擇部門/模組分類：",
        "sub_header": "子模組功能清單：",
        "departments": {
            "📈 營運戰情室 (Executive)": {
                "sub_modules": {
                    "📊 營運 KPI & 全球看盤戰情": "exec_dashboard"
                }
            },
            "🧾 財務/帳款 (Finance)": {
                "sub_modules": {
                    "🛒 採購與應付帳款系統 (Procurement & AP)": "procurement_ap",
                    "📋 訂單與應收帳款系統 (Sales Orders & AR)": "sales_order_ar",
                    "📄 越南電子發票 XML 解析與登錄": "vn_invoice_xml",
                    "📧 通用信箱電子發票讀取 (IMAP)": "email_invoice",
                    "📊 電子發票張數監控與預警": "invoice_quota"
                }
            },
            "🛠️ 研發/技術 (R&D & Engineering)": {
                "sub_modules": {
                    "⚡ 配電盤與資材工程估價系統": "engineering_quote"
                }
            },
            "🏢 總務/資產 (General Affairs)": {
                "sub_modules": {
                    "📦 資產設備與總務採購管理": "ga_assets",
                    "✍️ 電子簽核與請款審核中心": "approval_center"
                }
            },
            "👥 人事/行政 (HR & Admin)": {
                "sub_modules": {
                    "👤 員工檔案與勞動合約管理": "hr_employee"
                }
            },
            "🏭 廠務/資材 (Plant & Materials)": {
                "sub_modules": {
                    "📦 倉庫與資材條碼管理": "wh_management",
                    "✂️ 板金加工與現場工單": "sheet_metal",
                    "🎨 烤漆塗裝與品管檢驗": "painting",
                    "⚡ 配電盤組裝與線路配線": "assembly"
                }
            },
            "💻 資訊/IT (IT & System Admin)": {
                "sub_modules": {
                    "🔒 帳號權限與全系統操作軌跡 (Audit Log)": "it_admin"
                }
            }
        }
    },
    "Tiếng Việt": {
        "company_name": "⚡ REETECH INDUSTRIAL",
        "company_sub": "Công ty TNHH REETECH INDUSTRIAL",
        "login_title": "⚡ REETECH INDUSTRIAL - Đăng nhập hệ thống",
        "username": "Tài khoản",
        "password": "Mật khẩu",
        "login_btn": "🔑 Đăng nhập",
        "logout_btn": "🚪 Đăng xuất",
        "lang_selector": "🌐 Chọn ngôn ngữ",
        "parent_header": "Chọn phòng ban / Phân loại:",
        "sub_header": "Danh sách chức năng con:",
        "departments": {
            "📈 Báo cáo Ban Giám đốc (Executive)": {
                "sub_modules": {
                    "📊 Bảng điều hành Doanh nghiệp & KPI": "exec_dashboard"
                }
            },
            "🧾 Phòng Tài Chính (Finance)": {
                "sub_modules": {
                    "🛒 Mua hàng & Phải trả (Procurement & AP)": "procurement_ap",
                    "📋 Đơn hàng & Phải thu (Sales Orders & AR)": "sales_order_ar",
                    "📄 Đọc Hóa đơn Điện tử XML Việt Nam": "vn_invoice_xml",
                    "📧 Tự động đọc Hóa đơn từ Email (IMAP)": "email_invoice",
                    "📊 Cảnh báo & Theo dõi Số lượng Hóa đơn": "invoice_quota"
                }
            },
            "🛠️ Phòng Kỹ Thuật (R&D & Engineering)": {
                "sub_modules": {
                    "⚡ Báo giá Tủ điện & Dự toán Vật tư": "engineering_quote"
                }
            },
            "🏢 Phòng Hậu Cần (General Affairs)": {
                "sub_modules": {
                    "📦 Quản lý Thiết bị & Tài sản Cố định": "ga_assets",
                    "✍️ Trung tâm Phê duyệt Điện tử": "approval_center"
                }
            },
            "👥 Phòng Nhân Sự (HR & Admin)": {
                "sub_modules": {
                    "👤 Hồ sơ Nhân sự & Hợp đồng Lao động": "hr_employee"
                }
            },
            "🏭 Quản lý Kho & Xưởng (Plant & Materials)": {
                "sub_modules": {
                    "📦 Quản lý Kho & Mã vạch Vật tư": "wh_management",
                    "✂️ Tổ Gia công Cơ khí & Lệnh sản xuất": "sheet_metal",
                    "🎨 Tổ Sơn tĩnh điện & Kiểm tra Chất lượng": "painting",
                    "⚡ Tổ Lắp ráp Tủ điện & Đấu nối": "assembly"
                }
            },
            "💻 Phòng IT (IT & System Admin)": {
                "sub_modules": {
                    "🔒 Quản lý Phân quyền & Nhật ký Hệ thống": "it_admin"
                }
            }
        }
    },
    "English": {
        "company_name": "⚡ REETECH INDUSTRIAL",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ REETECH INDUSTRIAL - System Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "🔑 Login",
        "logout_btn": "🚪 Logout",
        "lang_selector": "🌐 Select Language",
        "parent_header": "Select Department / Category:",
        "sub_header": "Sub-module Features:",
        "departments": {
            "📈 Executive Dashboard": {
                "sub_modules": {
                    "📊 Strategic KPI & Tickers": "exec_dashboard"
                }
            },
            "🧾 Finance & Accounts": {
                "sub_modules": {
                    "🛒 Procurement & Accounts Payable (AP)": "procurement_ap",
                    "📋 Sales Orders & Accounts Receivable (AR)": "sales_order_ar",
                    "📄 Vietnam E-Invoice XML Parser": "vn_invoice_xml",
                    "📧 Auto Email Invoice Reader (IMAP)": "email_invoice",
                    "📊 E-Invoice Quota & Alerts": "invoice_quota"
                }
            },
            "🛠️ R&D & Engineering": {
                "sub_modules": {
                    "⚡ Switchgear Quotation & Material Costing": "engineering_quote"
                }
            },
            "🏢 General Affairs & Assets": {
                "sub_modules": {
                    "📦 Equipment & Fixed Asset Management": "ga_assets",
                    "✍️ E-Approval Workflow Center": "approval_center"
                }
            },
            "👥 HR & Administration": {
                "sub_modules": {
                    "👤 Employee Records & Labor Contracts": "hr_employee"
                }
            },
            "🏭 Plant & Warehouse": {
                "sub_modules": {
                    "📦 Warehouse & Barcode Management": "wh_management",
                    "✂️ Sheet Metal & Work Orders": "sheet_metal",
                    "🎨 Powder Coating & QC Inspection": "painting",
                    "⚡ Assembly & Wiring Dept": "assembly"
                }
            },
            "💻 IT & System Admin": {
                "sub_modules": {
                    "🔒 Permissions Matrix & System Audit Logs": "it_admin"
                }
            }
        }
    }
}

if "current_lang" not in st.session_state:
    st.session_state.current_lang = "繁體中文"

# ----------------------------------------------------
# 3. Supabase 資料庫連線
# ----------------------------------------------------
DB_URL = "postgresql+psycopg2://postgres.wvsqbefyeykmueffcbwd:Reetech2026@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

@st.cache_resource
def get_db_engine():
    eng = create_engine(DB_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
    try:
        with eng.connect() as conn:
            conn.execute(text("ALTER TABLE invoices ADD COLUMN IF NOT EXISTS installment_ratios TEXT;"))
            conn.execute(text("ALTER TABLE invoices ADD COLUMN IF NOT EXISTS progress_note TEXT;"))
            conn.execute(text("ALTER TABLE invoices ADD COLUMN IF NOT EXISTS project_desc TEXT;"))
            conn.commit()
    except Exception:
        pass
    return eng

engine = get_db_engine()

# ----------------------------------------------------
# 4. 登入頁面
# ----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_name = ""

lang_dict = NAV_STRUCTURE[st.session_state.current_lang]

if not st.session_state.logged_in:
    st.title(lang_dict["login_title"])
    st.caption(lang_dict["company_sub"])
    st.markdown("---")
    col1, _ = st.columns([1, 2])
    with col1:
        username = st.text_input(f"{lang_dict['username']} (admin / manager / staff)")
        password = st.text_input(f"{lang_dict['password']} (123)", type="password")
        if st.button(lang_dict["login_btn"], use_container_width=True):
            if password == "123":
                st.session_state.logged_in = True
                st.session_state.user_role = "admin" if username == "admin" else ("manager" if username == "manager" else "staff")
                st.session_state.user_name = username
                st.rerun()
            else:
                st.error("帳號或密碼錯誤 / Incorrect password")
    st.stop()

# ----------------------------------------------------
# 5. 側邊欄階層式動態選單 (Two-Level Dynamic Navigation)
# ----------------------------------------------------
st.sidebar.title(lang_dict["company_name"])
st.sidebar.caption(lang_dict["company_sub"])

# (1) 語系切換
lang_list = ["繁體中文", "Tiếng Việt", "English"]
selected_lang = st.sidebar.selectbox(
    lang_dict["lang_selector"],
    lang_list,
    index=lang_list.index(st.session_state.current_lang)
)

if selected_lang != st.session_state.current_lang:
    st.session_state.current_lang = selected_lang
    st.rerun()

st.sidebar.markdown(f"**👤 {st.session_state.user_name}** ({st.session_state.user_role.upper()})")
if st.sidebar.button(lang_dict["logout_btn"]):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

# (2) 第一階層：主部門選單 (Radio Group 1)
dept_options = list(lang_dict["departments"].keys())

# RBAC 權限保護：若非 admin，隱藏戰情室選項
if st.session_state.user_role != "admin":
    dept_options = [d for d in dept_options if "Executive" not in d]

selected_parent_dept = st.sidebar.radio(lang_dict["parent_header"], dept_options)

st.sidebar.markdown("---")

# (3) 第二階層：依第一階層選取的部門，動態渲染子模組選單 (Radio Group 2)
sub_modules_dict = lang_dict["departments"][selected_parent_dept]["sub_modules"]
sub_module_labels = list(sub_modules_dict.keys())

st.sidebar.caption(f"**{selected_parent_dept.split('(')[0].strip()}**")
selected_sub_label = st.sidebar.radio(lang_dict["sub_header"], sub_module_labels)

# 取得最終路由標記
target_route = sub_modules_dict[selected_sub_label]

# ----------------------------------------------------
# 6. 模組安全路由分流
# ----------------------------------------------------
curr_lang = st.session_state.current_lang

if target_route == "exec_dashboard":
    if hasattr(executive_dashboard, "render_executive_dashboard_page"):
        executive_dashboard.render_executive_dashboard_page(lang=curr_lang)
    elif hasattr(executive_dashboard, "render"):
        executive_dashboard.render(engine, t=lang_dict, lang=curr_lang)

elif target_route == "procurement_ap":
    procurement_ap.render_procurement_ap_page(engine=engine, lang=curr_lang)

elif target_route == "sales_order_ar":
    sales_order_ar.render_sales_order_ar_page(engine=engine, lang=curr_lang)

elif target_route in ["vn_invoice_xml", "email_invoice", "invoice_quota"]:
    invoice_management.render_invoice_management()

elif target_route == "engineering_quote":
    engineering_pipeline.render_engineering_page()

elif target_route == "ga_assets":
    asset_management.render_asset_management_page(lang=curr_lang)

elif target_route == "approval_center":
    approval_workflow.render_approval_center(lang=curr_lang)

elif target_route == "hr_employee":
    employee_management.render_employee_management(engine=engine, t=lang_dict, lang=curr_lang)

elif target_route == "wh_management":
    warehouse_management.render_warehouse_management(engine=engine, t=lang_dict, lang=curr_lang)

elif target_route in ["sheet_metal", "painting", "assembly"]:
    st.title(selected_sub_label)
    st.info("Hệ thống đang hoạt động bình thường / 現場工單追蹤與 QC 品質檢驗模組順利運作中。")

elif target_route == "it_admin":
    user_management.render_user_management_page(lang=curr_lang)
