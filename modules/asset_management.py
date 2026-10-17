import streamlit as st
import pandas as pd
import datetime
import re
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 三語系字典 (i18n)
# ----------------------------------------------------
ASSETS_I18N = {
    "繁體中文": {
        "title": "🏢 固定資產與設備管理 (Fixed Assets & Equipment)",
        "caption": "維護廠區機器設備與公務車輛，提供 5 年直線折舊試算、資產殘值查詢與 Excel 智慧批次匯入。",
        "tab_add": "➕ 新增固定資產",
        "tab_excel": "📊 Excel 智慧批次匯入",
        "tab_list": "📋 固定資產清冊與 5 年折舊攤分試算",
        "lbl_code": "資產/合約編號 *",
        "lbl_name": "資產名稱 *",
        "lbl_brand": "品牌與型號 / 廠牌",
        "lbl_status": "目前狀態",
        "lbl_site": "存放廠區/據點 *",
        "lbl_dept": "使用/權責部門 *",
        "lbl_purchase_date": "📅 購買/取得日期 *",
        "lbl_cost": "💰 取得原價成本 (VND) *",
        "lbl_salvage": "💰 預估 5 年後殘值 (VND) [預設 10%]",
        "lbl_cat": "資產類別 *",
        "lbl_custodian": "👤 保管人姓名 / 負責人 *",
        "lbl_plate": "🚗 車牌號碼 (Biển số xe) *",
        "lbl_v_model": "🚗 車輛廠牌與詳細型號 *",
        "lbl_inspection_date": "🚗 車輛驗車/行照到期日",
        "btn_submit": "📌 確認新增固定資產",
        "lbl_search": "🔍 輸入關鍵字查詢資產/車牌/編號/保管人："
    },
    "English": {
        "title": "🏢 Fixed Assets & Equipment Management",
        "caption": "Manage plant equipment and vehicles with depreciation and Excel batch import.",
        "tab_add": "➕ Add Asset",
        "tab_excel": "📊 Excel Batch Import",
        "tab_list": "📋 Asset Inventory & 5-Year Depreciation",
        "lbl_code": "Asset Code *",
        "lbl_name": "Asset Name *",
        "lbl_brand": "Brand & Model",
        "lbl_status": "Status",
        "lbl_site": "Plant Location *",
        "lbl_dept": "Department *",
        "lbl_purchase_date": "📅 Purchase Date *",
        "lbl_cost": "💰 Cost Price (VND) *",
        "lbl_salvage": "💰 Est. Residual Value (VND)",
        "lbl_cat": "Asset Category *",
        "lbl_custodian": "👤 Custodian / Responsible Person *",
        "lbl_plate": "🚗 License Plate No. *",
        "lbl_v_model": "🚗 Vehicle Brand & Model *",
        "lbl_inspection_date": "🚗 Inspection Expiry Date",
        "btn_submit": "📌 Save Asset",
        "lbl_search": "🔍 Search Asset / Plate / Code / Custodian:"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Tài sản cố định & Xe công tác",
        "caption": "Quản lý máy móc, xe công ty, tính khấu hao và nhập Excel tự động.",
        "tab_add": "➕ Thêm mới tài sản",
        "tab_excel": "📊 Nhập Excel hàng loạt",
        "tab_list": "📋 Danh sách tài sản & Khấu hao 5 năm",
        "lbl_code": "Mã tài sản *",
        "lbl_name": "Tên tài sản *",
        "lbl_brand": "Nhãn hiệu & Model",
        "lbl_status": "Trạng thái",
        "lbl_site": "Nhà xưởng / Vị trí *",
        "lbl_dept": "Bộ phận sử dụng *",
        "lbl_purchase_date": "📅 Ngày mua *",
        "lbl_cost": "💰 Nguyên giá (VND) *",
        "lbl_salvage": "💰 Giá trị thanh lý dự kiến (VND)",
        "lbl_cat": "Phân loại tài sản *",
        "lbl_custodian": "👤 Người quản lý / Trách nhiệm *",
        "lbl_plate": "🚗 Biển số xe *",
        "lbl_v_model": "🚗 Hiệu xe & Dòng xe *",
        "lbl_inspection_date": "🚗 Hạn đăng kiểm xe",
        "btn_submit": "📌 Lưu tài sản mới",
        "lbl_search": "🔍 Tìm kiếm tài sản / Biển số / Mã / Người quản lý:"
    }
}

ASSET_CATEGORIES = [
    "🚗 車輛 (公務車/卡車/堆高機)",
    "🏭 機器設備與配電盤生產線",
    "🏢 廠房土地與宿舍 (固定資產)",
    "📄 辦公室租賃合約 / 廠房租賃",
    "💻 資訊IT設備與伺服器",
    "📦 辦公傢俱與其他資產"
]

DEPT_OPTIONS = [
    "總經理室 (Executive Office)",
    "管理部 (Management Dept)",
    "財務部 (Finance Dept)",
    "工程與設計管理中心 (Engineering & Design Center)",
    "生產部 (Production Dept)",
    "資訊管理部 (IT & System)",
    "工務與工地現場 (Site Operations)"
]

SITE_OPTIONS = [
    "越南西寧廠 (Tay Ninh)",
    "越南海防廠 (Hai Phong)",
    "胡志明辦公室 (HCMC Office)"
]

def parse_formatted_amount(val_str):
    if not val_str:
        return 0.0
    clean_str = re.sub(r"[^\d]", "", str(val_str))
    return float(clean_str) if clean_str else 0.0

def format_vnd_input(amount):
    try:
        val = float(amount)
        return f"{val:,.0f}".replace(",", ".")
    except Exception:
        return str(amount)

def format_vnd(amount):
    try:
        val = float(amount)
        return f"{val:,.0f}".replace(",", ".") + " VND"
    except Exception:
        return f"{amount} VND"

def calculate_5y_depreciation(cost, salvage, purchase_date_str):
    try:
        cost_val = float(cost or 0)
        salvage_val = float(salvage or (cost_val * 0.1))
        
        if isinstance(purchase_date_str, (datetime.date, datetime.datetime)):
            p_date = purchase_date_str
        else:
            p_date = datetime.datetime.strptime(str(purchase_date_str)[:10], "%Y-%m-%d").date()
            
        today = datetime.date.today()
        months_used = (today.year - p_date.year) * 12 + (today.month - p_date.month)
        if months_used < 0:
            months_used = 0
            
        total_depreciable_base = max(0.0, cost_val - salvage_val)
        monthly_depreciation = total_depreciable_base / 60.0
        
        accumulated_depr = min(total_depreciable_base, monthly_depreciation * months_used)
        current_net_value = max(salvage_val, cost_val - accumulated_depr)
        
        return months_used, accumulated_depr, current_net_value
    except Exception:
        return 0, 0.0, float(cost or 0)

def inject_assets_css():
    st.markdown("""
        <style>
        html, body, [class*="css"] { font-size: 16px !important; }
        div.stButton > button {
            width: 100% !important;
            height: 3rem !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
            border-radius: 8px !important;
        }
        .vehicle-box {
            background-color: #EFF6FF;
            border: 2px dashed #3B82F6;
            border-radius: 8px;
            padding: 16px;
            margin-top: 10px;
            margin-bottom: 15px;
        }
        .depr-box {
            background-color: #FEF3C7;
            border-left: 5px solid #D97706;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

def init_assets_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.fixed_assets (
                    id SERIAL PRIMARY KEY,
                    asset_code VARCHAR(50) UNIQUE NOT NULL,
                    asset_name VARCHAR(200) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    site_location VARCHAR(100) NOT NULL,
                    department VARCHAR(100) DEFAULT '管理部 (Management Dept)',
                    brand_model VARCHAR(150),
                    license_plate VARCHAR(50),
                    driver_custodian VARCHAR(100),
                    purchase_date DATE DEFAULT CURRENT_DATE,
                    inspection_expiry DATE,
                    cost_amount NUMERIC(18,2) DEFAULT 0,
                    salvage_amount NUMERIC(18,2) DEFAULT 0,
                    status VARCHAR(50) DEFAULT '🟢 在用/租賃中',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("ALTER TABLE public.fixed_assets ALTER COLUMN cost_amount TYPE NUMERIC(18,2);"))
            conn.execute(text("ALTER TABLE public.fixed_assets ALTER COLUMN salvage_amount TYPE NUMERIC(18,2);"))
            conn.execute(text("ALTER TABLE public.fixed_assets ADD COLUMN IF NOT EXISTS driver_custodian VARCHAR(100);"))
            conn.execute(text("ALTER TABLE public.fixed_assets ADD COLUMN IF NOT EXISTS department VARCHAR(100) DEFAULT '管理部 (Management Dept)';"))
    except Exception:
        pass

def auto_detect_category(name_str):
    name_lower = str(name_str).lower()
    if any(k in name_lower for k in ["車", "car", "benz", "toyota", "ford", "truck", "堆高機", "卡車"]):
        return ASSET_CATEGORIES[0]
    elif any(k in name_lower for k in ["機", "設備", "線", "變壓器", "transformer", "generator"]):
        return ASSET_CATEGORIES[1]
    elif any(k in name_lower for k in ["廠房", "土地", "宿舍", "building", "land"]):
        return ASSET_CATEGORIES[2]
    elif any(k in name_lower for k in ["租賃", "合約", "lease", "contract"]):
        return ASSET_CATEGORIES[3]
    elif any(k in name_lower for k in ["電腦", "伺服器", "it", "server", "pc", "laptop"]):
        return ASSET_CATEGORIES[4]
    else:
        return ASSET_CATEGORIES[5]

def render_asset_management_page(engine=None, lang="繁體中文", **kwargs):
    inject_assets_css()

    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = ASSETS_I18N.get(active_lang, ASSETS_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_assets_db(engine)

    tab_add, tab_excel, tab_list = st.tabs([L["tab_add"], L["tab_excel"], L["tab_list"]])

    # ----------------------------------------------------
    # ➕ 頁籤 1: 新增固定資產
    # ----------------------------------------------------
    with tab_add:
        st.markdown("### ➕ 新增固定資產")
        
        with st.form("form_add_asset"):
            c1, c2 = st.columns(2)
            with c1:
                asset_code = st.text_input(L["lbl_code"], value="AST-VH-002", placeholder="例: AST-VH-001")
                asset_cat = st.selectbox(L["lbl_cat"], ASSET_CATEGORIES)
                asset_name = st.text_input(L["lbl_name"], placeholder="例: 賓士 S450 / 500KVA變壓器")
                site_loc = st.selectbox(L["lbl_site"], SITE_OPTIONS)
                purchase_dt = st.date_input(L["lbl_purchase_date"], datetime.date(2023, 1, 1))
            with c2:
                asset_dept = st.selectbox(L["lbl_dept"], DEPT_OPTIONS)
                asset_status = st.selectbox(L["lbl_status"], ["🟢 在用/租賃中 (Active)", "🟡 維修保養中 (Maintenance)", "🔴 報廢/封存 (Retired)"])
                
                cost_str = st.text_input(L["lbl_cost"], value="5.039.000.000")
                cost_val = parse_formatted_amount(cost_str)

                salvage_str = st.text_input(L["lbl_salvage"], value="85.000.000")
                salvage_val = parse_formatted_amount(salvage_str)

            general_custodian = st.text_input(L["lbl_custodian"], value="Nguyễn Văn Tài", placeholder="例: 阮文財 / 王大明")

            license_plate = ""
            v_model = ""
            inspection_date = None

            if "車輛" in asset_cat:
                st.markdown("""
                <div class="vehicle-box">
                    <h5 style="color:#1E40AF; margin-top:0;">🚗 車輛專屬補充資料（自動同步至公務派車與保修模組）</h5>
                """, unsafe_allow_html=True)
                
                v_c1, v_c2 = st.columns(2)
                with v_c1:
                    license_plate = st.text_input(L["lbl_plate"], value="70A-492.14")
                with v_c2:
                    v_model = st.text_input(L["lbl_v_model"], value="Mercedes-Benz S450")

                inspection_date = st.date_input(L["lbl_inspection_date"], datetime.date(2027, 10, 16))
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                v_model = st.text_input(L["lbl_brand"], placeholder="例: 廠牌型號 / 規格")

            if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
                if not asset_code or not asset_name:
                    st.error("⚠️ 請填寫資產編號與名稱！")
                elif not general_custodian:
                    st.error("⚠️ 請填寫資產保管人姓名！")
                elif "車輛" in asset_cat and not license_plate:
                    st.error("⚠️ 請填寫車輛的【車牌號碼】！")
                elif cost_val <= 0:
                    st.error("⚠️ 請填寫正確的取得原價成本！")
                else:
                    is_duplicate = False
                    if engine:
                        try:
