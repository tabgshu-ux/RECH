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
        "caption": "維護廠區機器設備與公務車輛，提供 5 年直線折舊試算與資產殘值查詢。",
        "tab_add": "➕ 新增固定資產與車輛",
        "tab_list": "📋 固定資產清冊與 5 年折舊攤分試算",
        "lbl_code": "資產/合約編號 *",
        "lbl_name": "資產或車輛名稱 *",
        "lbl_brand": "品牌與型號 / 廠牌",
        "lbl_status": "目前狀態",
        "lbl_site": "存放廠區/據點 *",
        "lbl_purchase_date": "📅 購買/取得日期 *",
        "lbl_cost": "💰 取得原價成本 (VND) *",
        "lbl_salvage": "💰 預估 5 年後殘值 (VND) [預設 10%]",
        "lbl_cat": "資產類別 *",
        "lbl_plate": "🚗 車牌號碼 (Biển số xe) *",
        "lbl_v_model": "🚗 車輛廠牌與詳細型號 *",
        "lbl_driver": "🚗 預設駕駛員 / 負責保管人",
        "lbl_inspection_date": "🚗 車輛驗車/行照到期日",
        "btn_submit": "📌 確認新增固定資產或車輛",
        "lbl_search": "🔍 輸入關鍵字查詢資產/車牌/編號："
    },
    "English": {
        "title": "🏢 Fixed Assets & Equipment Management",
        "caption": "Manage plant equipment and vehicles with 5-year depreciation calculation.",
        "tab_add": "➕ Add Asset / Vehicle",
        "tab_list": "📋 Asset Inventory & 5-Year Depreciation",
        "lbl_code": "Asset Code *",
        "lbl_name": "Asset Name *",
        "lbl_brand": "Brand & Model",
        "lbl_status": "Status",
        "lbl_site": "Plant Location *",
        "lbl_purchase_date": "📅 Purchase Date *",
        "lbl_cost": "💰 Cost Price (VND) *",
        "lbl_salvage": "💰 Est. Residual Value (VND)",
        "lbl_cat": "Asset Category *",
        "lbl_plate": "🚗 License Plate No. *",
        "lbl_v_model": "🚗 Vehicle Brand & Model *",
        "lbl_driver": "🚗 Default Driver / Custodian",
        "lbl_inspection_date": "🚗 Inspection Expiry Date",
        "btn_submit": "📌 Save Asset / Vehicle",
        "lbl_search": "🔍 Search Asset / Plate / Code:"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Tài sản cố định & Xe công tác",
        "caption": "Quản lý máy móc, xe công ty và tính khấu hao 5 năm.",
        "tab_add": "➕ Thêm mới tài sản / Xe",
        "tab_list": "📋 Danh sách tài sản & Khấu hao 5 năm",
        "lbl_code": "Mã tài sản *",
        "lbl_name": "Tên tài sản / Hợp đồng *",
        "lbl_brand": "Nhãn hiệu & Model",
        "lbl_status": "Trạng thái",
        "lbl_site": "Nhà xưởng / Vị trí *",
        "lbl_purchase_date": "📅 Ngày mua *",
        "lbl_cost": "💰 Nguyên giá (VND) *",
        "lbl_salvage": "💰 Giá trị thanh lý dự kiến (VND)",
        "lbl_cat": "Phân loại tài sản *",
        "lbl_plate": "🚗 Biển số xe *",
        "lbl_v_model": "🚗 Hiệu xe & Dòng xe *",
        "lbl_driver": "🚗 Tài xế / Người quản lý",
        "lbl_inspection_date": "🚗 Hạn đăng kiểm xe",
        "btn_submit": "📌 Lưu tài sản / Xe mới",
        "lbl_search": "🔍 Tìm kiếm tài sản / Biển số / Mã:"
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

def parse_formatted_amount(val_str):
    """將點或逗號千分位字串還原為純數字，例: '850.000.000' -> 850000000"""
    if not val_str:
        return 0.0
    clean_str = re.sub(r"[^\d]", "", str(val_str))
    return float(clean_str) if clean_str else 0.0

def format_vnd(amount):
    """將數字格式化為越南點號千分位格式，例: 850.000.000 VND"""
    try:
        val = float(amount)
        return f"{val:,.0f}".replace(",", ".") + " VND"
    except Exception:
        return f"{amount} VND"

def calculate_5y_depreciation(cost, salvage, purchase_date_str):
    """計算 5 年 (60個月) 直線法折舊金額與目前資產淨值"""
    try:
        cost_val = float(cost or 0)
        salvage_val = float(salvage or (cost_val * 0.1)) # 預設殘值 10%
        
        if isinstance(purchase_date_str, (datetime.date, datetime.datetime)):
            p_date = purchase_date_str
        else:
            p_date = datetime.datetime.strptime(str(purchase_date_str)[:10], "%Y-%m-%d").date()
            
        today = datetime.date.today()
        
        months_used = (today.year - p_date.year) * 12 + (today.month - p_date.month)
        if months_used < 0:
            months_used = 0
            
        total_depreciable_base = max(0.0, cost_val - salvage_val)
        monthly_depreciation = total_depreciable_base / 60.0 # 5 年 = 60 個月
        
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
                    brand_model VARCHAR(150),
                    license_plate VARCHAR(50),
                    driver_custodian VARCHAR(100),
                    purchase_date DATE DEFAULT CURRENT_DATE,
                    inspection_expiry DATE,
                    cost_amount NUMERIC(15,2) DEFAULT 0,
                    salvage_amount NUMERIC(15,2) DEFAULT 0,
                    status VARCHAR(50) DEFAULT '🟢 在用/租賃中',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            cols = [
                ("brand_model", "VARCHAR(150)"),
                ("license_plate", "VARCHAR(50)"),
                ("driver_custodian", "VARCHAR(100)"),
                ("purchase_date", "DATE DEFAULT CURRENT_DATE"),
                ("inspection_expiry", "DATE"),
                ("cost_amount", "NUMERIC(15,2) DEFAULT 0"),
                ("salvage_amount", "NUMERIC(15,2) DEFAULT 0"),
                ("site_location", "VARCHAR(100)")
            ]
            for col_name, col_type in cols:
                try:
                    conn.execute(text(f"ALTER TABLE public.fixed_assets ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                except Exception:
                    pass
    except Exception:
        pass

def render_asset_management_page(engine=None, lang="繁體中文", **kwargs):
    inject_assets_css()

    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = ASSETS_I18N.get(active_lang, ASSETS_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_assets_db(engine)

    tab_add, tab_list = st.tabs([L["tab_add"], L["tab_list"]])

    # ----------------------------------------------------
    # ➕ 頁籤 1: 新增固定資產與車輛
    # ----------------------------------------------------
    with tab_add:
        st.markdown(f"### {L['tab_add']}")
        
        with st.form("form_add_asset"):
            c1, c2 = st.columns(2)
            with c1:
                asset_code = st.text_input(L["lbl_code"], value="AST-VH-001", placeholder="例: AST-VH-001")
                asset_cat = st.selectbox(L["lbl_cat"], ASSET_CATEGORIES)
                asset_name = st.text_input(L["lbl_name"], placeholder="例: 賓士 S450")
                purchase_dt = st.date_input(L["lbl_purchase_date"], datetime.date(2023, 1, 1))
            with c2:
                site_loc = st.selectbox(L["lbl_site"], ["越南西寧廠 (Tay Ninh)"])
                asset_status = st.selectbox(L["lbl_status"], ["🟢 在用/租賃中 (Active)", "🟡 維修保養中 (Maintenance)", "🔴 報廢/封存 (Retired)"])
                
                cost_str = st.text_input(
                    L["lbl_cost"], 
                    value="5.039.000.000",
                    help="直接輸入數字即可，系統會自動轉換為越南千位點號格式"
                )
                cost_val = parse_formatted_amount(cost_str)

                salvage_str = st.text_input(
                    L["lbl_salvage"], 
                    value="85.000.000",
                    help="預設為原價 10%，可手動調整殘值"
                )
                salvage_val = parse_formatted_amount(salvage_str)

            license_plate = ""
            v_model = ""
            driver_name = ""
            inspection_date = None

            if "車輛" in asset_cat:
                st.markdown("""
                <div class="vehicle-box">
                    <h5 style="color:#1E40AF; margin-top:0;">🚗 車輛專屬資料（自動同步至公務派車與保修模組）</h5>
                """, unsafe_allow_html=True)
                
                v_c1, v_c2, v_c3 = st.columns(3)
                with v_c1:
                    license_plate = st.text_input(L["lbl_plate"], value="70A-492.14", placeholder="例: 70A-492.14")
                with v_c2:
                    v_model = st.text_input(L["lbl_v_model"], value="Mercedes-Benz S450", placeholder="例: Toyota Fortuner")
                with v_c3:
                    driver_name = st.text_input(L["lbl_driver"], value="Nguyễn Văn Tài", placeholder="例: 專職司機")

                inspection_date = st.date_input(L["lbl_inspection_date"], datetime.date(2027, 10, 16))
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                v_model = st.text_input(L["lbl_brand"], placeholder="例: 500KVA 變壓器")

            if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
                if not asset_code or not asset_name:
                    st.error("⚠️ 請填寫資產編號與名稱！")
                elif "車輛" in asset_cat and not license_plate:
                    st.error("⚠️ 請填寫車輛的【車牌號碼】！")
                elif cost_val <= 0:
                    st.error("⚠️ 請填寫正確的取得原價成本！")
                else:
                    # 防呆檢查：檢查編號是否重複
                    is_duplicate = False
                    if engine:
                        try:
                            df_check = pd.read_sql("SELECT asset_code FROM public.fixed_assets WHERE asset_code = :code", con=engine, params={"code": asset_code})
                            if not df_check.empty:
                                is_duplicate = True
                        except Exception:
                            pass

                    if is_duplicate:
                        st.warning(f"⚠️ **資料重複提示**：系統中已經存在資產編號 `{asset_code}`！請更換新的資產編號後再試一次。")
                    else:
                        if engine:
                            try:
                                with engine.begin() as conn:
                                    conn.execute(text("""
                                        INSERT INTO public.fixed_assets 
                                        (asset_code, asset_name, category, site_location, brand_model, license_plate, driver_custodian, purchase_date, inspection_expiry, cost_amount, salvage_amount, status)
                                        VALUES (:code, :name, :cat, :site, :bm, :plate, :driver, :pdate, :exp, :cost, :sal, :status);
                                    """), {
                                        "code": asset_code, "name": asset_name, "cat": asset_cat, "site": site_loc,
                                        "bm": v_model, "plate": license_plate, "driver": driver_name, "pdate": purchase_dt,
                                        "exp": inspection_date, "cost": cost_val, "sal": salvage_val, "status": asset_status
                                    })
                                st.success(f"🎉 車輛/資產【{asset_name}】建立成功！原價：{format_vnd(cost_val)}")
                                st.rerun()
                            except Exception as e:
                                st.error("寫入失敗: " + str(e))
                        else:
                            st.success(f"🎉 [展示模式] 車輛/資產【{asset_name}】建立成功！")

    # ----------------------------------------------------
    # 📋 頁籤 2: 清冊查看與 5 年直線折舊攤分試算
    # ----------------------------------------------------
    with tab_list:
        st.markdown(f"### {L['tab_list']}")
        st.markdown("""
        <div class="depr-box">
            <b>📊 5 年直線法折舊計算公式說明：</b><br>
            • <b>每月折舊額</b> = (取得原價 - 預估殘值) ÷ 60 個月<br>
            • <b>累計折舊</b> = 每月折舊額 × 購買至今已使用月份<br>
            • <b>目前剩餘殘值 (資產淨值)</b> = 取得原價 - 累計折舊
        </div>
        """, unsafe_allow_html=True)
        
        search_kw = st.text_input(L["lbl_search"], placeholder="搜尋資產名稱、車牌號碼或編號...")

        if engine:
            try:
                with engine.connect() as conn:
                    query_sql = "SELECT * FROM public.fixed_assets ORDER BY id DESC;"
                    res = conn.execute(text(query_sql))
                    rows = res.fetchall()
                    if rows:
                        data_list = []
                        for r in rows:
                            item = dict(r._mapping)
                            
                            if search_kw:
                                kw = search_kw.lower()
                                match_code = kw in str(item.get("asset_code", "")).lower()
                                match_name = kw in str(item.get("asset_name", "")).lower()
                                match_plate = kw in str(item.get("license_plate", "")).lower()
                                if not (match_code or match_name or match_plate):
                                    continue

                            cost_amt = float(item.get("cost_amount", 0) or 0)
                            salvage_amt = float(item.get("salvage_amount", 0) or (cost_amt * 0.1))
                            p_date = item.get("purchase_date") or datetime.date(2023, 1, 1)

                            months_used, accum_depr, net_value = calculate_5y_depreciation(cost_amt, salvage_amt, p_date)

                            data_list.append({
                                "資產/車輛編號": item.get("asset_code"),
                                "名稱/車牌號碼": item.get("asset_name") or item.get("license_plate"),
                                "資產類別": item.get("category"),
                                "廠牌/型號": item.get("brand_model") or "無",
                                "購買日期": str(p_date)[:10],
                                "取得原價": format_vnd(cost_amt),
                                "已使用月份": f"{months_used} 個月 / 60",
                                "累計折舊 (5年期)": format_vnd(accum_depr),
                                "目前剩餘殘值": format_vnd(net_value),
                                "存放廠區": item.get("site_location"),
                                "狀態": item.get("status")
                            })

                        if data_list:
                            st.dataframe(pd.DataFrame(data_list), use_container_width=True)
                        else:
                            st.warning("查無符合關鍵字的資產或車輛紀錄。")
                    else:
                        st.info("目前尚無固定資產與車輛資料。")
            except Exception as e:
                st.error("讀取失敗: " + str(e))

# ----------------------------------------------------
# 🔗 相容性進入點
# ----------------------------------------------------
def render_assets_page(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)

def render_fixed_assets(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)
