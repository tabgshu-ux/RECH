import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 三語系字典
# ----------------------------------------------------
ASSETS_I18N = {
    "繁體中文": {
        "title": "🏢 固定資產與設備管理 (Fixed Assets & Equipment)",
        "caption": "維護廠區機器設備、公務車輛、廠房土地與租賃合約，並串聯派車與維修紀錄。",
        "tab_add": "➕ 新增固定資產與租賃合約",
        "tab_list": "📋 固定資產與車輛清冊",
        "lbl_code": "資產/合約編號 *",
        "lbl_name": "資產或合約名稱 *",
        "lbl_brand": "品牌與型號 / 廠牌",
        "lbl_status": "目前狀態",
        "lbl_site": "存放廠區/據點 *",
        "lbl_cost": "取得成本或月租金 (VND / USD)",
        "lbl_cat": "資產類別 *",
        "lbl_plate": "🚗 車牌號碼 (Biển số xe) *",
        "lbl_v_model": "🚗 車輛廠牌與詳細型號 *",
        "lbl_driver": "🚗 預設駕駛員 / 負責保管人",
        "lbl_inspection_date": "🚗 車輛驗車/行照到期日",
        "btn_submit": "📌 確認新增固定資產或車輛"
    },
    "English": {
        "title": "🏢 Fixed Assets & Equipment Management",
        "caption": "Manage plant equipment, vehicles, lands, and lease contracts.",
        "tab_add": "➕ Add Asset / Vehicle",
        "tab_list": "📋 Asset & Vehicle Inventory",
        "lbl_code": "Asset Code *",
        "lbl_name": "Asset Name *",
        "lbl_brand": "Brand & Model",
        "lbl_status": "Status",
        "lbl_site": "Plant Location *",
        "lbl_cost": "Cost or Monthly Rent",
        "lbl_cat": "Asset Category *",
        "lbl_plate": "🚗 License Plate No. *",
        "lbl_v_model": "🚗 Vehicle Brand & Model *",
        "lbl_driver": "🚗 Default Driver / Custodian",
        "lbl_inspection_date": "🚗 Inspection Expiry Date",
        "btn_submit": "📌 Save Asset / Vehicle"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Tài sản cố định & Xe công tác",
        "caption": "Quản lý máy móc, xe công ty, nhà xưởng và hợp đồng thuê.",
        "tab_add": "➕ Thêm mới tài sản / Xe",
        "tab_list": "📋 Danh sách tài sản & Xe",
        "lbl_code": "Mã tài sản *",
        "lbl_name": "Tên tài sản / Hợp đồng *",
        "lbl_brand": "Nhãn hiệu & Model",
        "lbl_status": "Trạng thái",
        "lbl_site": "Nhà xưởng / Vị trí *",
        "lbl_cost": "Nguyên giá / Tiền thuê hàng tháng",
        "lbl_cat": "Phân loại tài sản *",
        "lbl_plate": "🚗 Biển số xe *",
        "lbl_v_model": "🚗 Hiệu xe & Dòng xe *",
        "lbl_driver": "🚗 Tài xế / Người quản lý",
        "lbl_inspection_date": "🚗 Hạn đăng kiểm xe",
        "btn_submit": "📌 Lưu tài sản / Xe mới"
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
                    inspection_expiry DATE,
                    cost_amount NUMERIC(15,2) DEFAULT 0,
                    status VARCHAR(50) DEFAULT '🟢 在用/租賃中',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            try:
                conn.execute(text("ALTER TABLE public.fixed_assets ADD COLUMN IF NOT EXISTS license_plate VARCHAR(50);"))
                conn.execute(text("ALTER TABLE public.fixed_assets ADD COLUMN IF NOT EXISTS driver_custodian VARCHAR(100);"))
                conn.execute(text("ALTER TABLE public.fixed_assets ADD COLUMN IF NOT EXISTS inspection_expiry DATE;"))
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
                asset_name = st.text_input(L["lbl_name"], placeholder="例: 70LD-006.06 (公司總經理專車)")
            with c2:
                site_loc = st.selectbox(L["lbl_site"], ["越南西寧廠 (Tay Ninh)", "海防辦事處 (Hai Phong)", "胡志明總部 (HCMC)"])
                asset_status = st.selectbox(L["lbl_status"], ["🟢 在用/租賃中 (Active)", "🟡 維修保養中 (Maintenance)", "🔴 報廢/封存 (Retired)"])
                cost_val = st.number_input(L["lbl_cost"], min_value=0.0, value=850000000.0, step=10000000.0)

            # 🚗 動態檢測：若類別屬於「車輛」，自動展開藍色車輛專用欄位區！
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
                    license_plate = st.text_input(L["lbl_plate"], value="70LD-006.06", placeholder="例: 70LD-006.06 或 60A-888.99")
                with v_c2:
                    v_model = st.text_input(L["lbl_v_model"], value="Toyota Fortuner 2.7V", placeholder="例: Isuzu 3.5噸卡車 / Ford Transit 16座")
                with v_c3:
                    driver_name = st.text_input(L["lbl_driver"], value="Nguyễn Văn Tài", placeholder="例: 專職司機 / 廠長")

                inspection_date = st.date_input(L["lbl_inspection_date"], datetime.date.today() + datetime.timedelta(days=365))
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                v_model = st.text_input(L["lbl_brand"], placeholder="例: Amada CNC Busbar 160T")

            if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
                if not asset_code or not asset_name:
                    st.error("⚠️ 請填寫資產編號與名稱！")
                elif "車輛" in asset_cat and not license_plate:
                    st.error("⚠️ 請填寫車輛的【車牌號碼】！")
                else:
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.fixed_assets 
                                    (asset_code, asset_name, category, site_location, brand_model, license_plate, driver_custodian, inspection_expiry, cost_amount, status)
                                    VALUES (:code, :name, :cat, :site, :bm, :plate, :driver, :exp, :cost, :status);
                                """), {
                                    "code": asset_code, "name": asset_name, "cat": asset_cat, "site": site_loc,
                                    "bm": v_model, "plate": license_plate, "driver": driver_name, "exp": inspection_date,
                                    "cost": cost_val, "status": asset_status
                                })
                            st.success(f"🎉 車輛/資產【{asset_name}】建立成功！車牌：{license_plate or '無'}")
                            st.rerun()
                        except Exception as e:
                            st.error("寫入失敗: " + str(e))
                    else:
                        st.success(f"🎉 [展示模式] 車輛/資產【{asset_name}】（車牌: {license_plate}）建立成功！")

    # ----------------------------------------------------
    # 📋 頁籤 2: 清冊查看
    # ----------------------------------------------------
    with tab_list:
        st.markdown(f"### {L['tab_list']}")
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT asset_code, asset_name, category, license_plate, brand_model, driver_custodian, site_location, status FROM public.fixed_assets ORDER BY id DESC;"))
                    rows = res.fetchall()
                    if rows:
                        st.dataframe(pd.DataFrame([dict(r._mapping) for r in rows]), use_container_width=True)
                    else:
                        st.info("目前尚無固定資產與車輛資料。")
            except Exception as e:
                st.error("讀取失敗: " + str(e))

# ----------------------------------------------------
# 🔗 相容性進入點 (對接主程式任何名稱呼叫)
# ----------------------------------------------------
def render_assets_page(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)

def render_fixed_assets(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)
