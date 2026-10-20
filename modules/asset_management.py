import streamlit as st
import pandas as pd
import datetime
import re
from sqlalchemy import text

ASSETS_I18N = {
    "繁體中文": {
        "title": "🏢 固定資產與設備管理 (Fixed Assets & Equipment)",
        "caption": "支援車輛車牌、條碼掃描、越南土地面積 (m²) 租賃，以及財務自訂折舊年限設定。",
        "tab_add": "➕ 新增固定資產",
        "tab_excel": "📊 Excel 智慧批次匯入",
        "tab_list": "📋 固定資產清冊與折舊試算",
        "lbl_code": "資產/合約編號 *",
        "lbl_name": "資產名稱 *",
        "lbl_status": "目前狀態",
        "lbl_site": "存放廠區 *",
        "lbl_sub_location": "詳細位置 *",
        "lbl_dept": "使用/權責部門 *",
        "lbl_purchase_date": "📅 購買/取得/合約起日 *",
        "lbl_cost": "💰 取得原價成本 / 初始總金額 (VND) *",
        "lbl_useful_life": "⏳ 耐用年限 (年) [依越南會計準則可自訂]",
        "lbl_salvage": "💰 預估殘值 (VND) [預設 10%]",
        "lbl_cat": "資產類別 *",
        "lbl_custodian": "👤 保管人姓名 / 負責人 *",
        "btn_submit": "📌 確認新增固定資產",
        "lbl_search": "🔍 輸入關鍵字查詢資產/車牌/地號/保管人："
    },
    "English": {
        "title": "🏢 Fixed Assets & Equipment Management",
        "caption": "Supports vehicles, barcodes, sqm land leasing, and custom depreciation settings.",
        "tab_add": "➕ Add Asset",
        "tab_excel": "📊 Excel Batch Import",
        "tab_list": "📋 Asset Inventory",
        "lbl_code": "Asset Code *",
        "lbl_name": "Asset Name *",
        "lbl_status": "Status",
        "lbl_site": "Plant Location *",
        "lbl_sub_location": "Specific Location *",
        "lbl_dept": "Department *",
        "lbl_purchase_date": "📅 Purchase / Start Date *",
        "lbl_cost": "💰 Cost / Initial Amount (VND) *",
        "lbl_useful_life": "⏳ Useful Life (Years)",
        "lbl_salvage": "💰 Salvage Value (VND)",
        "lbl_cat": "Asset Category *",
        "lbl_custodian": "👤 Custodian *",
        "btn_submit": "📌 Save Asset",
        "lbl_search": "🔍 Search Asset / Plate / Land No. / Custodian:"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Tài sản cố định & Nhà xưởng",
        "caption": "Quản lý xe, mã vạch, đất đai và cấu hình thời gian khấu hao tùy chỉnh.",
        "tab_add": "➕ Thêm mới tài sản",
        "tab_excel": "📊 Nhập Excel hàng loạt",
        "tab_list": "📋 Danh sách tài sản",
        "lbl_code": "Mã tài sản *",
        "lbl_name": "Tên tài sản *",
        "lbl_status": "Trạng thái",
        "lbl_site": "Nhà xưởng *",
        "lbl_sub_location": "Vị trí chi tiết *",
        "lbl_dept": "Bộ phận sử dụng *",
        "lbl_purchase_date": "📅 Ngày mua / Ngày bắt đầu HĐ *",
        "lbl_cost": "💰 Nguyên giá (VND) *",
        "lbl_useful_life": "⏳ Thời gian khấu hao (Năm)",
        "lbl_salvage": "💰 Giá trị thanh lý (VND)",
        "lbl_cat": "Phân loại tài sản *",
        "lbl_custodian": "👤 Người quản lý *",
        "btn_submit": "📌 Lưu tài sản mới",
        "lbl_search": "🔍 Tìm kiếm tài sản / Biển số / Thửa đất / Người quản lý:"
    }
}

ASSET_CATEGORIES = [
    "🚗 車輛 (Xe công tác / Xe tải / Xe nâng - Khuyến nghị 6年)",
    "🏢 廠房土地與宿舍租賃 (Đất đai, nhà xưởng & Ký túc xá - Khuyến nghị 25年)",
    "🏭 機器設備與配電盤生產線 (Máy móc & Dây chuyền - Khuyến nghị 8年)",
    "💻 資訊IT設備與伺服器 (Thiết bị IT & Server - 具條碼 - 3~5年)",
    "📦 辦公傢俱與其他資產 (Nội thất & Khác - 具條碼 - 3~5年)"
]

DEPT_OPTIONS = [
    "總經理室 / Ban Giám đốc (Executive Office)",
    "管理部 / Phòng Quản lý (Management Dept)",
    "財務部 / Phòng Tài chính (Finance Dept)",
    "工程與設計管理中心 / Trung tâm Kỹ thuật & Thiết kế (Engineering Center)",
    "生產部 / Phòng Sản xuất (Production Dept)",
    "工務與工地現場 / Bộ phận công trường (Site Operations)"
]

DEFAULT_SUB_LOCATIONS = [
    "辦公室 / Văn phòng (Office)",
    "線材倉庫 / Kho dây điện (Wire Warehouse)",
    "板金組 / Nhóm Chấn dập - 板金 (Sheet Metal)",
    "塗裝組 / Nhóm Sơn tĩnh điện (Coating)",
    "裝配組 / Nhóm Lắp ráp (Assembly)",
    "台灣宿舍 / Ký túc xá Đài Loan",
    "越南西寧廠區土地 / Đất nhà máy Tây Ninh",
    "停車場 / Bãi đỗ xe (Parking Lot)"
]

STATUS_OPTIONS = [
    "🟢 在用/租賃中 / Đang sử dụng / Đang thuê (Active)",
    "🟡 維修保養中 / Đang bảo trì bảo dưỡng (Maintenance)",
    "🔴 報廢/封存 / Đã thanh lý / Lưu kho (Retired)"
]

def get_factory_options_from_db(engine):
    factories = ["西寧廠 / Nhà máy Tây Ninh"]
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT factory_name FROM public.factories_master;"))
                rows = res.fetchall()
                if rows:
                    db_facs = [r[0] for r in rows if r[0]]
                    if db_facs:
                        factories = db_facs
        except Exception:
            pass
    return factories

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
                    category VARCHAR(150) NOT NULL,
                    site_location VARCHAR(100) DEFAULT '西寧廠 / Nhà máy Tây Ninh',
                    sub_location VARCHAR(150) DEFAULT '辦公室 / Văn phòng (Office)',
                    department VARCHAR(150) DEFAULT '管理部 / Phòng Quản lý (Management Dept)',
                    brand_model VARCHAR(150),
                    license_plate VARCHAR(50),
                    barcode_serial VARCHAR(100),
                    land_address TEXT,
                    land_plot_no VARCHAR(100),
                    land_area_sqm NUMERIC(12,2) DEFAULT 0,
                    lease_start_date DATE,
                    lease_end_date DATE,
                    renewal_date DATE,
                    renewal_amount NUMERIC(18,2) DEFAULT 0,
                    driver_custodian VARCHAR(100),
                    purchase_date DATE DEFAULT CURRENT_DATE,
                    inspection_expiry DATE,
                    cost_amount NUMERIC(18,2) DEFAULT 0,
                    salvage_amount NUMERIC(18,2) DEFAULT 0,
                    useful_life_years INT DEFAULT 5,
                    status VARCHAR(100) DEFAULT '🟢 在用/租賃中 / Đang sử dụng (Active)',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            for col_name, col_type in [
                ("useful_life_years", "INT DEFAULT 5"),
                ("license_plate", "VARCHAR(50)"),
                ("barcode_serial", "VARCHAR(100)"),
                ("land_address", "TEXT"),
                ("land_plot_no", "VARCHAR(100)"),
                ("land_area_sqm", "NUMERIC(12,2) DEFAULT 0"),
                ("lease_start_date", "DATE"),
                ("lease_end_date", "DATE"),
                ("renewal_date", "DATE"),
                ("renewal_amount", "NUMERIC(18,2) DEFAULT 0"),
                ("driver_custodian", "VARCHAR(100)")
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE public.fixed_assets ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                except Exception:
                    pass
    except Exception:
        pass

def calculate_custom_depreciation(cost, salvage, purchase_date_str, useful_years):
    try:
        cost_val = float(cost or 0)
        years = int(useful_years or 5)
        if years < 1:
            years = 1
        total_months = years * 12
        salvage_val = float(salvage if salvage is not None else (cost_val * 0.1))
        
        if isinstance(purchase_date_str, (datetime.date, datetime.datetime)):
            p_date = purchase_date_str
        else:
            p_date = datetime.datetime.strptime(str(purchase_date_str)[:10], "%Y-%m-%d").date()
            
        today = datetime.date.today()
        months_used = (today.year - p_date.year) * 12 + (today.month - p_date.month)
        if months_used < 0:
            months_used = 0
            
        total_depreciable_base = max(0.0, cost_val - salvage_val)
        monthly_depreciation = total_depreciable_base / float(total_months)
        
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
        .dynamic-box {
            background-color: #F0FDF4;
            border: 2px dashed #10B981;
            border-radius: 8px;
            padding: 16px;
            margin-top: 10px;
            margin-bottom: 15px;
        }
        .land-box {
            background-color: #FEF3C7;
            border: 2px dashed #D97706;
            border-radius: 8px;
            padding: 16px;
            margin-top: 10px;
            margin-bottom: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_asset_management_page(engine=None, lang="繁體中文", **kwargs):
    inject_assets_css()

    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = ASSETS_I18N.get(active_lang, ASSETS_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_assets_db(engine)

    site_options = get_factory_options_from_db(engine)

    tab_add, tab_excel, tab_list = st.tabs([L["tab_add"], L["tab_excel"], L["tab_list"]])

    with tab_add:
        st.markdown(f"### {L['tab_add']}")
        asset_cat = st.selectbox(L["lbl_cat"], ASSET_CATEGORIES, key="dynamic_asset_cat_selector")

        default_years = 5
        if "車輛" in asset_cat or "Xe" in asset_cat:
            default_years = 6
        elif "土地" in asset_cat or "廠房" in asset_cat or "Đất" in asset_cat:
            default_years = 25
        elif "機器" in asset_cat or "Máy" in asset_cat:
            default_years = 8
        elif "資訊" in asset_cat or "IT" in asset_cat or "辦公" in asset_cat:
            default_years = 3

        with st.form("form_add_asset"):
            c1, c2 = st.columns(2)
            with c1:
                asset_code = st.text_input(L["lbl_code"], value="AST-001", placeholder="例: CAR-001 / LAND-001 / IT-001")
                asset_name = st.text_input(L["lbl_name"], placeholder="例: 廠房建築物 / 賓士 S450 / 機器設備")
                site_loc = st.selectbox(L["lbl_site"], site_options)
                
                sub_loc_choice = st.selectbox(L["lbl_sub_location"], DEFAULT_SUB_LOCATIONS + ["➕ 自訂新位置 / Thêm vị trí mới..."])
                if sub_loc_choice == "➕ 自訂新位置 / Thêm vị trí mới...":
                    custom_sub_loc = st.text_input("請輸入自訂詳細位置 (中越文):")
                    sub_loc = custom_sub_loc if custom_sub_loc else DEFAULT_SUB_LOCATIONS[0]
                else:
                    sub_loc = sub_loc_choice

                purchase_dt = st.date_input(L["lbl_purchase_date"], datetime.date(2023, 1, 1))
            with c2:
                asset_dept = st.selectbox(L["lbl_dept"], DEPT_OPTIONS)
                asset_status = st.selectbox(L["lbl_status"], STATUS_OPTIONS)
                
                cost_str = st.text_input(L["lbl_cost"], value="5.039.000.000")
                cost_val = parse_formatted_amount(cost_str)
                st.caption(f"💡 金額即時預覽: **{cost_val:,.0f} VND**".replace(",", "."))

                useful_life = st.number_input(L["lbl_useful_life"], min_value=1, max_value=50, value=default_years, step=1)

                salvage_str = st.text_input(L["lbl_salvage"], value=str(int(cost_val * 0.1)))
                salvage_val = parse_formatted_amount(salvage_str)
                st.caption(f"💡 殘值預覽: **{salvage_val:,.0f} VND** (折舊期: {useful_life}年)".replace(",", "."))

            general_custodian = st.text_input(L["lbl_custodian"], value="Nguyễn Văn Tài")

            license_plate = ""
            v_model = ""
            inspection_date = None
            barcode_serial = ""
            land_address = ""
            land_plot_no = ""
            land_area = 0.0
            lease_start = None
            lease_end = None
            renewal_dt = None
            renewal_amt = 0.0

            if "車輛" in asset_cat or "Xe" in asset_cat:
                st.markdown("""<div class="dynamic-box"><h5 style="color:#047857; margin-top:0;">🚗 車輛專屬補充資料</h5>""", unsafe_allow_html=True)
                v_c1, v_c2 = st.columns(2)
                with v_c1:
                    license_plate = st.text_input("車牌號碼 (Biển số xe) *", value="70A-492.14")
                with v_c2:
                    v_model = st.text_input("車輛廠牌與型號", value="Mercedes-Benz S450")
                inspection_date = st.date_input("車輛驗車到期日", datetime.date(2027, 10, 16))
                st.markdown("</div>", unsafe_allow_html=True)
            elif "土地" in asset_cat or "廠房" in asset_cat or "Đất" in asset_cat:
                st.markdown("""<div class="land-box"><h5 style="color:#B45309; margin-top:0;">🏢 越南土地與廠房不動產專屬資料</h5>""", unsafe_allow_html=True)
                l_c1, l_c2 = st.columns(2)
                with l_c1:
                    land_address = st.text_input("不動產詳細地址", value="Khu công nghiệp Trảng Bàng, Tây Ninh")
                    land_plot_no = st.text_input("地號 / 圖號", value="Thửa đất số 45, Tờ bản đồ số 12")
                    land_area = st.number_input("總面積 ($m^2$)", min_value=0.0, value=5000.0, step=10.0, format="%.2f")
                with l_c2:
                    lease_start = st.date_input("租賃起日", datetime.date(2020, 1, 1))
                    lease_end = st.date_input("租賃到期日", datetime.date(2050, 12, 31))
                    renewal_dt = st.date_input("預定續約日", datetime.date(2030, 1, 1))
                    ren_str = st.text_input("預估續約金額 (VND)", value="150.000.000")
                    renewal_amt = parse_formatted_amount(ren_str)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("""<div class="dynamic-box"><h5 style="color:#047857; margin-top:0;">📦 財產條碼與序號認證</h5>""", unsafe_allow_html=True)
                barcode_serial = st.text_input("資產條碼 / 序號", value="BC-IT-2026-9988")
                v_model = st.text_input("品牌與型號", placeholder="例: Dell PowerEdge R750")
                st.markdown("</div>", unsafe_allow_html=True)

            if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
                if not asset_code or not asset_name:
                    st.error("⚠️ 請填寫資產編號與名稱！")
                elif not general_custodian:
                    st.error("⚠️ 請填寫保管人姓名！")
                else:
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.fixed_assets 
                                    (asset_code, asset_name, category, site_location, sub_location, department, brand_model, license_plate, barcode_serial, land_address, land_plot_no, land_area_sqm, lease_start_date, lease_end_date, renewal_date, renewal_amount, driver_custodian, purchase_date, inspection_expiry, cost_amount, salvage_amount, useful_life_years, status)
                                    VALUES (:code, :name, :cat, :site, :sub_loc, :dept, :bm, :plate, :bc, :l_addr, :l_plot, :l_area, :l_start, :l_end, :r_dt, :r_amt, :driver, :pdate, :exp, :cost, :sal, :life, :status);
                                """), {
                                    "code": asset_code, "name": asset_name, "cat": asset_cat, "site": site_loc, "sub_loc": sub_loc, "dept": asset_dept,
                                    "bm": v_model, "plate": license_plate, "bc": barcode_serial, "l_addr": land_address, "l_plot": land_plot_no,
                                    "l_area": land_area, "l_start": lease_start, "l_end": lease_end, "r_dt": renewal_dt, "r_amt": renewal_amt,
                                    "driver": general_custodian, "pdate": purchase_dt, "exp": inspection_date, "cost": cost_val, "sal": salvage_val, "life": useful_life, "status": asset_status
                                })
                            st.success(f"🎉 成功新增資產【{asset_name}】 | 年限：{useful_life}年")
                            st.rerun()
                        except Exception as e:
                            st.error("寫入資料庫失敗: " + str(e))

    with tab_excel:
        st.markdown(f"### {L['tab_excel']}")
        uploaded_file = st.file_uploader("選擇 Excel 檔案上傳", type=["xlsx", "xls"])
        if uploaded_file is not None:
            try:
                df_upload = pd.read_excel(uploaded_file)
                st.dataframe(df_upload.head(5), use_container_width=True)
                if st.button("🚀 確認執行 Excel 智慧識別並寫入資料庫", type="primary"):
                    success_count = 0
                    if engine:
                        with engine.begin() as conn:
                            for _, row in df_upload.iterrows():
                                try:
                                    code = str(row.get("資產編號") or f"AST-{datetime.datetime.now().strftime('%H%M%S%f')}")
                                    name = str(row.get("資產名稱") or "未命名資產")
                                    cat = str(row.get("資產類別") or ASSET_CATEGORIES[2])
                                    cost = float(row.get("取得原價") or 0)
                                    conn.execute(text("""
                                        INSERT INTO public.fixed_assets 
                                        (asset_code, asset_name, category, cost_amount, salvage_amount, useful_life_years, status)
                                        VALUES (:code, :name, :cat, :cost, :sal, 8, '🟢 在用/租賃中')
                                        ON CONFLICT (asset_code) DO NOTHING;
                                    """), {"code": code.strip(), "name": name, "cat": cat, "cost": cost, "sal": cost * 0.1})
                                    success_count += 1
                                except Exception:
                                    pass
                    st.success(f"🎉 批次匯入完成！成功寫入 {success_count} 筆。")
                    st.rerun()
            except Exception as e:
                st.error("❌ 解析 Excel 失敗: " + str(e))

    with tab_list:
        st.markdown(f"### {L['tab_list']}")
        search_kw = st.text_input(L["lbl_search"], placeholder="搜尋資產名稱、車牌、地號、條碼、保管人...")

        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT * FROM public.fixed_assets ORDER BY id DESC;"))
                    rows = res.fetchall()
                    if rows:
                        data_list = []
                        raw_items = []
                        for r in rows:
                            item = dict(r._mapping)
                            if search_kw:
                                kw = search_kw.lower()
                                match_str = f"{item.get('asset_code')} {item.get('asset_name')} {item.get('license_plate')} {item.get('barcode_serial')} {item.get('land_plot_no')} {item.get('driver_custodian')}".lower()
                                if kw not in match_str:
                                    continue

                            raw_items.append(item)
                            cost_amt = float(item.get("cost_amount", 0) or 0)
                            salvage_amt = float(item.get("salvage_amount", 0) or (cost_amt * 0.1))
                            p_date = item.get("purchase_date") or datetime.date(2023, 1, 1)
                            life_years = int(item.get("useful_life_years") or 5)

                            _, _, net_value = calculate_custom_depreciation(cost_amt, salvage_amt, p_date, life_years)

                            data_list.append({
                                "資產編號": item.get("asset_code"),
                                "資產名稱": item.get("asset_name"),
                                "資產類別": item.get("category"),
                                "耐用年限": f"{life_years}年",
                                "保管人": item.get("driver_custodian"),
                                "取得原價": format_vnd(cost_amt),
                                "目前淨值": format_vnd(net_value),
                                "狀態": item.get("status")
                            })

                        if data_list:
                            st.dataframe(pd.DataFrame(data_list), use_container_width=True)
                            
                            st.markdown("---")
                            st.markdown("### ✏️ 財務資產資料修改與折舊年限調整")
                            asset_options = [f"{item['asset_code']} - {item['asset_name']} [年限: {item.get('useful_life_years',5)}年]" for item in raw_items]
                            selected_target = st.selectbox("選擇要修改年限或刪除的資產", asset_options)
                            
                            if selected_target:
                                target_code = selected_target.split(" - ")[0]
                                target_item = next((i for i in raw_items if i["asset_code"] == target_code), None)
                                
                                if target_item:
                                    with st.form("form_edit_asset"):
                                        ec1, ec2 = st.columns(2)
                                        with ec1:
                                            ed_code = st.text_input("資產編號", value=target_item.get("asset_code", ""))
                                            ed_name = st.text_input("資產名稱", value=target_item.get("asset_name", ""))
                                        with ec2:
                                            ed_life = st.number_input("耐用年限 (年)", min_value=1, max_value=50, value=int(target_item.get("useful_life_years") or 5), step=1)
                                            ed_cost = st.text_input("取得原價成本 (VND)", value=format_vnd_input(target_item.get("cost_amount", 0)))

                                        eb1, eb2 = st.columns(2)
                                        with eb1:
                                            btn_update = st.form_submit_button("💾 儲存資產變更", type="primary", use_container_width=True)
                                        with eb2:
                                            btn_delete = st.form_submit_button("🔥 刪除此筆資產", type="secondary", use_container_width=True)

                                        if btn_update:
                                            try:
                                                final_cost = parse_formatted_amount(ed_cost)
                                                with engine.begin() as conn:
                                                    conn.execute(text("""
                                                        UPDATE public.fixed_assets 
                                                        SET asset_code = :new_code, asset_name = :name, 
                                                            useful_life_years = :life, cost_amount = :cost
                                                        WHERE asset_code = :old_code;
                                                    """), {
                                                        "new_code": ed_code.strip(), "name": ed_name,
                                                        "life": ed_life, "cost": final_cost, "old_code": target_code
                                                    })
                                                st.success(f"🎉 資產更新成功！")
                                                st.rerun()
                                            except Exception as e:
                                                st.error("更新失敗: " + str(e))

                                        if btn_delete:
                                            try:
                                                with engine.begin() as conn:
                                                    conn.execute(text("DELETE FROM public.fixed_assets WHERE asset_code = :code;"), {"code": target_code})
                                                st.success(f"🗑️ 已刪除！")
                                                st.rerun()
                                            except Exception as e:
                                                st.error("刪除失敗: " + str(e))
            except Exception as e:
                st.error("讀取失敗: " + str(e))

def render_assets_page(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)

def render_fixed_assets(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)
