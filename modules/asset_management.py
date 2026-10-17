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
                                        (asset_code, asset_name, category, site_location, department, brand_model, license_plate, driver_custodian, purchase_date, inspection_expiry, cost_amount, salvage_amount, status)
                                        VALUES (:code, :name, :cat, :site, :dept, :bm, :plate, :driver, :pdate, :exp, :cost, :sal, :status);
                                    """), {
                                        "code": asset_code, "name": asset_name, "cat": asset_cat, "site": site_loc, "dept": asset_dept,
                                        "bm": v_model, "plate": license_plate, "driver": general_custodian, "pdate": purchase_dt,
                                        "exp": inspection_date, "cost": cost_val, "sal": salvage_val, "status": asset_status
                                    })
                                st.success(f"🎉 成功新增固定資產【{asset_name}】 | 部門：{asset_dept} | 保管人：{general_custodian}")
                                st.rerun()
                            except Exception as e:
                                st.error("寫入失敗: " + str(e))
                        else:
                            st.success(f"🎉 [展示模式] 固定資產【{asset_name}】建立成功！")

    # ----------------------------------------------------
    # 📊 頁籤 2: Excel 智慧批次匯入
    # ----------------------------------------------------
    with tab_excel:
        st.markdown(f"### {L['tab_excel']}")
        st.info("請上傳包含固定資產資料的 Excel 檔案 (.xlsx)。支援欄位包含：資產編號、資產名稱、資產類別、廠區、部門、保管人、取得原價等。")
        
        uploaded_file = st.file_uploader("選擇 Excel 檔案上傳", type=["xlsx", "xls"])
        if uploaded_file is not None:
            try:
                df_upload = pd.read_excel(uploaded_file)
                st.markdown("##### 📄 預覽上傳的 Excel 數據內容：")
                st.dataframe(df_upload.head(5), use_container_width=True)

                if st.button("🚀 確認執行 Excel 智慧識別並寫入資料庫", type="primary"):
                    success_count = 0
                    error_count = 0
                    if engine:
                        with engine.begin() as conn:
                            for _, row in df_upload.iterrows():
                                try:
                                    code = str(row.get("資產編號") or row.get("Asset Code") or row.get("Mã tài sản") or f"AST-{datetime.datetime.now().strftime('%H%M%S%f')}")
                                    name = str(row.get("資產名稱") or row.get("Asset Name") or row.get("Tên tài sản") or "未命名資產")
                                    raw_cat = str(row.get("資產類別") or row.get("Category") or "")
                                    cat = raw_cat if raw_cat in ASSET_CATEGORIES else auto_detect_category(name)
                                    site = str(row.get("廠區") or row.get("Location") or "越南西寧廠 (Tay Ninh)")
                                    dept = str(row.get("部門") or row.get("Department") or "管理部 (Management Dept)")
                                    plate = str(row.get("車牌號碼") or row.get("License Plate") or "")
                                    brand = str(row.get("廠牌型號") or row.get("Brand") or "")
                                    driver = str(row.get("保管人") or row.get("Driver") or row.get("Custodian") or "管理部")
                                    
                                    cost = float(row.get("取得原價") or row.get("Cost") or 0)
                                    salvage = float(row.get("預估殘值") or row.get("Salvage") or (cost * 0.1))
                                    
                                    conn.execute(text("""
                                        INSERT INTO public.fixed_assets 
                                        (asset_code, asset_name, category, site_location, department, brand_model, license_plate, driver_custodian, cost_amount, salvage_amount, status)
                                        VALUES (:code, :name, :cat, :site, :dept, :bm, :plate, :driver, :cost, :sal, '🟢 在用/租賃中')
                                        ON CONFLICT (asset_code) DO NOTHING;
                                    """), {
                                        "code": code.strip(), "name": name, "cat": cat, "site": site, "dept": dept,
                                        "bm": brand, "plate": plate if plate != "nan" else "", 
                                        "driver": driver if driver != "nan" else "管理部", "cost": cost, "sal": salvage
                                    })
                                    success_count += 1
                                except Exception:
                                    error_count += 1
                    
                    st.success(f"🎉 Excel 批次匯入完成！成功寫入：{success_count} 筆，略過/錯誤：{error_count} 筆。")
                    st.rerun()
            except Exception as e:
                st.error("❌ 解析 Excel 失敗: " + str(e))

    # ----------------------------------------------------
    # 📋 頁籤 3: 清冊查看、5 年直線折舊攤分試算、修改與刪除
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
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_site = st.selectbox("📍 依存放位置/廠區過濾", ["全部廠區 (All Locations)"] + SITE_OPTIONS)
        with col_f2:
            filter_dept = st.selectbox("📂 依使用部門過濾", ["全部部門 (All Departments)"] + DEPT_OPTIONS)

        search_kw = st.text_input(L["lbl_search"], placeholder="搜尋資產名稱、車牌號碼、編號或保管人...")

        if engine:
            try:
                with engine.connect() as conn:
                    query_sql = "SELECT * FROM public.fixed_assets ORDER BY id DESC;"
                    res = conn.execute(text(query_sql))
                    rows = res.fetchall()
                    if rows:
                        data_list = []
                        raw_items = []
                        for r in rows:
                            item = dict(r._mapping)
                            
                            if filter_site != "全部廠區 (All Locations)" and item.get("site_location") != filter_site:
                                continue
                            if filter_dept != "全部部門 (All Departments)" and item.get("department") != filter_dept:
                                continue

                            if search_kw:
                                kw = search_kw.lower()
                                match_code = kw in str(item.get("asset_code", "")).lower()
                                match_name = kw in str(item.get("asset_name", "")).lower()
                                match_plate = kw in str(item.get("license_plate", "")).lower()
                                match_driver = kw in str(item.get("driver_custodian", "")).lower()
                                if not (match_code or match_name or match_plate or match_driver):
                                    continue

                            raw_items.append(item)
                            cost_amt = float(item.get("cost_amount", 0) or 0)
                            salvage_amt = float(item.get("salvage_amount", 0) or (cost_amt * 0.1))
                            p_date = item.get("purchase_date") or datetime.date(2023, 1, 1)

                            months_used, accum_depr, net_value = calculate_5y_depreciation(cost_amt, salvage_amt, p_date)

                            data_list.append({
                                "資產編號": item.get("asset_code"),
                                "資產名稱": item.get("asset_name") or item.get("license_plate"),
                                "資產類別": item.get("category"),
                                "存放廠區": item.get("site_location"),
                                "使用部門": item.get("department") or "未指定",
                                "廠牌/型號": item.get("brand_model") or "無",
                                "保管人": item.get("driver_custodian") or "未指定",
                                "購買日期": str(p_date)[:10],
                                "取得原價": format_vnd(cost_amt),
                                "已使用月份": f"{months_used} 個月 / 60",
                                "累計折舊 (5年期)": format_vnd(accum_depr),
                                "目前剩餘殘值": format_vnd(net_value),
                                "狀態": item.get("status")
                            })

                        if data_list:
                            st.dataframe(pd.DataFrame(data_list), use_container_width=True)
                            
                            st.markdown("---")
                            st.markdown("### ✏️ 固定資產資料修改 / 刪除管理")
                            asset_options = [f"{item['asset_code']} - {item['asset_name'] or item['license_plate']} [部門: {item.get('department','無')}] (保管人: {item.get('driver_custodian', '無')})" for item in raw_items]
                            selected_target = st.selectbox("選擇要修改或刪除的資產", asset_options)
                            
                            if selected_target:
                                target_code = selected_target.split(" - ")[0]
                                target_item = next((i for i in raw_items if i["asset_code"] == target_code), None)
                                
                                if target_item:
                                    with st.form("form_edit_asset"):
                                        ec1, ec2 = st.columns(2)
                                        with ec1:
                                            ed_code = st.text_input("資產/合約編號 (可修改)", value=target_item.get("asset_code", ""))
                                            ed_name = st.text_input("資產名稱", value=target_item.get("asset_name", ""))
                                            
                                            curr_site = target_item.get("site_location", SITE_OPTIONS[0])
                                            site_idx = SITE_OPTIONS.index(curr_site) if curr_site in SITE_OPTIONS else 0
                                            ed_site = st.selectbox("存放廠區/據點", SITE_OPTIONS, index=site_idx)

                                            curr_dept = target_item.get("department", DEPT_OPTIONS[0])
                                            dept_idx = DEPT_OPTIONS.index(curr_dept) if curr_dept in DEPT_OPTIONS else 0
                                            ed_dept = st.selectbox("使用/權責部門", DEPT_OPTIONS, index=dept_idx)

                                            ed_plate = st.text_input("車牌號碼 (若為車輛)", value=target_item.get("license_plate", ""))
                                            ed_driver = st.text_input("保管人姓名 / 負責人", value=target_item.get("driver_custodian", ""))

                                        with ec2:
                                            ed_brand = st.text_input("廠牌型號", value=target_item.get("brand_model", ""))
                                            
                                            raw_pdate = target_item.get("purchase_date")
                                            if isinstance(raw_pdate, (datetime.date, datetime.datetime)):
                                                default_date = raw_pdate
                                            else:
                                                try:
                                                    default_date = datetime.datetime.strptime(str(raw_pdate)[:10], "%Y-%m-%d").date()
                                                except Exception:
                                                    default_date = datetime.date(2023, 1, 1)
                                            ed_pdate = st.date_input("購買/取得日期", value=default_date)

                                            default_cost_str = format_vnd_input(target_item.get("cost_amount", 0))
                                            ed_cost = st.text_input("取得原價成本 (VND)", value=default_cost_str)
                                            
                                            default_sal_str = format_vnd_input(target_item.get("salvage_amount", 0))
                                            ed_salvage = st.text_input("預估殘值 (VND)", value=default_sal_str)

                                        eb1, eb2 = st.columns(2)
                                        with eb1:
                                            btn_update = st.form_submit_button("💾 儲存資產變更", type="primary", use_container_width=True)
                                        with eb2:
                                            btn_delete = st.form_submit_button("🔥 刪除此筆資產", type="secondary", use_container_width=True)

                                        if btn_update:
                                            try:
                                                final_cost = parse_formatted_amount(ed_cost)
                                                final_salvage = parse_formatted_amount(ed_salvage)
                                                with engine.begin() as conn:
                                                    conn.execute(text("""
                                                        UPDATE public.fixed_assets 
                                                        SET asset_code = :new_code, asset_name = :name, site_location = :site, 
                                                            department = :dept, license_plate = :plate, brand_model = :bm, 
                                                            driver_custodian = :driver, purchase_date = :pdate, 
                                                            cost_amount = :cost, salvage_amount = :sal
                                                        WHERE asset_code = :old_code;
                                                    """), {
                                                        "new_code": ed_code.strip(), "name": ed_name, "site": ed_site, "dept": ed_dept,
                                                        "plate": ed_plate, "bm": ed_brand, "driver": ed_driver, "pdate": ed_pdate,
                                                        "cost": final_cost, "sal": final_salvage, "old_code": target_code
                                                    })
                                                st.success(f"🎉 固定資產編號 [{ed_code}] 資料更新成功！")
                                                st.rerun()
                                            except Exception as e:
                                                st.error("更新失敗 (可能是編號與其他資產重複): " + str(e))

                                        if btn_delete:
                                            try:
                                                with engine.begin() as conn:
                                                    conn.execute(text("DELETE FROM public.fixed_assets WHERE asset_code = :code;"), {"code": target_code})
                                                st.success(f"🗑️ 固定資產編號 [{target_code}] 已成功刪除！")
                                                st.rerun()
                                            except Exception as e:
                                                st.error("刪除失敗: " + str(e))
                        else:
                            st.warning("⚠️ 依照目前的廠區與部門過濾條件，查無符合的固定資產紀錄。")
                    else:
                        st.info("目前尚無固定資產資料。")
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
