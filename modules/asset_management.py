import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 固定資產模組多語系字典 (i18n)
# ----------------------------------------------------
ASSET_I18N = {
    "繁體中文": {
        "title": "🏭 裕豐電機工業 - 生產設備與固定資產管理系統",
        "caption": "管理西寧廠與海防廠生產機械、土地房屋租賃合約、車輛、網通、品管儀器與工安設施之完整生命週期。",
        "tab_list": "📑 廠區資產總表與分類檢視",
        "tab_add": "➕ 新增固定資產與租賃合約",
        "tab_edit": "✏️ 修改資產與租約資料",
        "tab_delete": "🗑️ 刪除或報廢資產",
        "table_header": "📋 廠區固定資產與租賃合約清冊",
        "plant_all": "🌐 全部廠區 (All Plants)",
        "plant_tn": "🏭 越南西寧廠 (Tay Ninh)",
        "plant_hp": "⚓ 越南海防廠 (Hai Phong)",
        "cat_all": "🌐 全部類別",
        "cat_lease": "🏢 土地與房屋租賃",
        "cat_prod": "🏭 生產機具",
        "cat_car": "🚗 車輛",
        "cat_it": "💻 電腦",
        "cat_office": "🖨️ 辦公設備",
        "cat_net": "📡 網通伺服",
        "cat_qa": "🔬 品管儀器",
        "cat_wh": "📦 倉儲物流",
        "cat_safety": "🧯 消防工安",
        "lbl_code": "資產/合約編號 *",
        "lbl_name": "資產或合約名稱 *",
        "lbl_category": "品項分類 *",
        "cat_opts": [
            "土地與房屋租賃 (Land & Building Lease)",
            "生產與加工機具 (Machinery)",
            "車輛設備 (Vehicle)",
            "個人電腦與筆電 (PC & Laptop)",
            "辦公家具與設備 (Office Equipment)",
            "網通與伺服器 (Network & Servers)",
            "檢測與品管儀器 (Testing & QA)",
            "倉儲與物流設備 (Warehouse & Logistics)",
            "消防與工安設施 (Safety & Firefighting)"
        ],
        "lbl_factory": "存放廠區/據點 *",
        "factory_opts": ["越南西寧廠 (Tay Ninh)", "越南海防廠 (Hai Phong)"],
        "lbl_brand": "品牌與型號 / 房東與出租方",
        "lbl_plate": "車牌號碼 (若為車輛必填)",
        "lbl_status": "目前狀態 *",
        "status_opts": ["🟢 在用/租賃中 (Active)", "🟡 租約將到期 (Expiring Soon)", "🔴 停用/退租 (Disposed)"],
        "lbl_cost": "取得成本或月租金/總租金 (USD) *",
        "lbl_start_date": "租約起始日期 (Lease Start Date)",
        "lbl_end_date": "租約到期日期 (Lease Expiry Date)",
        "btn_add": "🚀 確認新增固定資產或合約",
        "success_add": "✅ 成功新增記錄 `{name}` (編號: `{code}`)！",
        "btn_save_edit": "💾 儲存修改後資料",
        "success_edit": "✅ 記錄 `{code}` 資料已成功更新！",
        "btn_delete": "🔥 確認刪除或報廢選定記錄",
        "success_delete": "✅ 已成功刪除選定的記錄。",
        "col_index": "STT",
        "col_code": "編號",
        "col_name": "名稱/合約",
        "col_category": "類別",
        "col_factory": "廠區",
        "col_brand": "品牌/房東",
        "col_lease_period": "租約期限 (起 ~ 訖)",
        "col_status": "狀態",
        "col_cost": "成本/租金"
    },
    "Tiếng Việt": {
        "title": "🏭 Quản lý Tài sản Cố định & Hợp đồng thuê",
        "caption": "Quản lý máy móc, hợp đồng thuê đất/nhà xưởng.",
        "tab_list": "📑 Danh sách tài sản & Hợp đồng",
        "tab_add": "➕ Thêm mới",
        "tab_edit": "✏️ Sửa thông tin",
        "tab_delete": "🗑️ Xóa / Thanh lý",
        "table_header": "📋 Danh mục Tài sản & Hợp đồng thuê",
        "plant_all": "🌐 Tất cả nhà máy",
        "plant_tn": "🏭 Tây Ninh",
        "plant_hp": "⚓ Hải Phòng",
        "cat_all": "🌐 Tất cả",
        "cat_lease": "🏢 Thuê đất/nhà",
        "cat_prod": "🏭 Máy móc",
        "cat_car": "🚗 Xe cộ",
        "cat_it": "💻 Máy tính",
        "cat_office": "🖨️ Văn phòng",
        "cat_net": "📡 Mạng",
        "cat_qa": "🔬 QA/QC",
        "cat_wh": "📦 Kho",
        "cat_safety": "🧯 An toàn",
        "lbl_code": "Mã tài sản/Hợp đồng *",
        "lbl_name": "Tên *",
        "lbl_category": "Phân loại *",
        "cat_opts": [
            "土地與房屋租賃 (Land & Building Lease)",
            "生產與加工機具 (Machinery)",
            "車輛設備 (Vehicle)",
            "個人電腦與筆電 (PC & Laptop)",
            "辦公家具與設備 (Office Equipment)",
            "網通與伺服器 (Network & Servers)",
            "檢測與品管儀器 (Testing & QA)",
            "倉儲與物流設備 (Warehouse & Logistics)",
            "消防與工安設施 (Safety & Firefighting)"
        ],
        "lbl_factory": "Nhà máy *",
        "factory_opts": ["越南西寧廠 (Tay Ninh)", "越南海防廠 (Hai Phong)"],
        "lbl_brand": "Brand / Chủ cho thuê",
        "lbl_plate": "Biển số xe",
        "lbl_status": "Trạng thái *",
        "status_opts": ["🟢 Đang sử dụng", "🟡 Sắp hết hạn", "🔴 Đã thanh lý"],
        "lbl_cost": "Chi phí / Tiền thuê (USD) *",
        "lbl_start_date": "Ngày bắt đầu thuê",
        "lbl_end_date": "Ngày hết hạn hợp đồng",
        "btn_add": "🚀 Thêm",
        "success_add": "✅ Thành công!",
        "btn_save_edit": "💾 Lưu",
        "success_edit": "✅ Cập nhật thành công!",
        "btn_delete": "🔥 Xóa",
        "success_delete": "✅ Đã xóa.",
        "col_index": "STT",
        "col_code": "Mã",
        "col_name": "Tên",
        "col_category": "Phân loại",
        "col_factory": "Nhà máy",
        "col_brand": "Brand/Chủ nhà",
        "col_lease_period": "Thời hạn thuê",
        "col_status": "Trạng thái",
        "col_cost": "Chi phí"
    },
    "English": {
        "title": "🏭 Fixed Assets & Lease Management",
        "caption": "Manage plant assets and land/building lease contracts.",
        "tab_list": "📑 Asset & Lease Directory",
        "tab_add": "➕ Add Asset/Lease",
        "tab_edit": "✏️ Edit Record",
        "tab_delete": "🗑️ Delete / Dispose",
        "table_header": "📋 Asset & Lease Directory",
        "plant_all": "🌐 All Plants",
        "plant_tn": "🏭 Tay Ninh",
        "plant_hp": "⚓ Hai Phong",
        "cat_all": "🌐 All",
        "cat_lease": "🏢 Land/Building Lease",
        "cat_prod": "🏭 Machinery",
        "cat_car": "🚗 Vehicles",
        "cat_it": "💻 IT & PC",
        "cat_office": "🖨️ Office",
        "cat_net": "📡 Network",
        "cat_qa": "🔬 QA/QC",
        "cat_wh": "📦 Warehouse",
        "cat_safety": "🧯 Safety",
        "lbl_code": "Code *",
        "lbl_name": "Name/Contract *",
        "lbl_category": "Category *",
        "cat_opts": [
            "土地與房屋租賃 (Land & Building Lease)",
            "生產與加工機具 (Machinery)",
            "車輛設備 (Vehicle)",
            "個人電腦與筆電 (PC & Laptop)",
            "辦公家具與設備 (Office Equipment)",
            "網通與伺服器 (Network & Servers)",
            "檢測與品管儀器 (Testing & QA)",
            "倉儲與物流設備 (Warehouse & Logistics)",
            "消防與工安設施 (Safety & Firefighting)"
        ],
        "lbl_factory": "Plant Location *",
        "factory_opts": ["越南西寧廠 (Tay Ninh)", "越南海防廠 (Hai Phong)"],
        "lbl_brand": "Brand / Landlord",
        "lbl_plate": "License Plate",
        "lbl_status": "Status *",
        "status_opts": ["🟢 Active", "🟡 Expiring Soon", "🔴 Disposed"],
        "lbl_cost": "Cost / Rent (USD) *",
        "lbl_start_date": "Lease Start Date",
        "lbl_end_date": "Lease Expiry Date",
        "btn_add": "🚀 Confirm Add",
        "success_add": "✅ Added successfully!",
        "btn_save_edit": "💾 Save Changes",
        "success_edit": "✅ Updated successfully!",
        "btn_delete": "🔥 Delete",
        "success_delete": "✅ Record deleted.",
        "col_index": "No.",
        "col_code": "Code",
        "col_name": "Name",
        "col_category": "Category",
        "col_factory": "Plant",
        "col_brand": "Brand/Landlord",
        "col_lease_period": "Lease Term",
        "col_status": "Status",
        "col_cost": "Cost"
    }
}

def render_asset_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = ASSET_I18N.get(active_lang, ASSET_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化固定資產與租賃合約資料庫
    if "asset_db" not in st.session_state:
        st.session_state.asset_db = [
            {
                "資產編號": "LEASE-TN-01",
                "資產名稱": "越南西寧廠廠房與基地長期租賃合約",
                "類別": "土地與房屋租賃 (Land & Building Lease)",
                "存放廠區": "越南西寧廠 (Tay Ninh)",
                "品牌型號": "An Tinh Industrial Park Corp (房東)",
                "車牌號碼": "-",
                "目前狀態": "🟢 在用/租賃中 (Active)",
                "取得成本": 12000.0,
                "租約起始日期": "2023-01-01",
                "租約到期日期": "2033-12-31"
            },
            {
                "資產編號": "EQ-TN-001",
                "資產名稱": "CNC 數控母線銅排彎折加工機",
                "類別": "生產與加工機具 (Machinery)",
                "存放廠區": "越南西寧廠 (Tay Ninh)",
                "品牌型號": "Amada - CNC Busbar 160T",
                "車牌號碼": "-",
                "目前狀態": "🟢 在用 (Active)",
                "取得成本": 45000.0,
                "租約起始日期": "-",
                "租約到期日期": "-"
            },
            {
                "資產編號": "AST-CAR-001",
                "資產名稱": "西寧廠廠長商務公務車",
                "類別": "車輛設備 (Vehicle)",
                "存放廠區": "越南西寧廠 (Tay Ninh)",
                "品牌型號": "Toyota - Fortuner 2.8L",
                "车牌号": "61A-888.66",
                "目前狀態": "🟢 在用 (Active)",
                "取得成本": 28000.0,
                "租約起始日期": "-",
                "租約到期日期": "-"
            },
            {
                "資產編號": "LEASE-HP-01",
                "資產名稱": "越南海防廠辦公處所租賃合約",
                "類別": "土地與房屋租賃 (Land & Building Lease)",
                "存放廠區": "越南海防廠 (Hai Phong)",
                "品牌型號": "Haiphong Industrial Property Ltd",
                "車牌號碼": "-",
                "目前狀態": "🟡 租約將到期 (Expiring Soon)",
                "取得成本": 5500.0,
                "租約起始日期": "2024-05-01",
                "租約到期日期": "2026-12-31"
            }
        ]

    # 🛡️ 欄位相容防護
    for asset in st.session_state.asset_db:
        if "存放廠區" not in asset:
            asset["存放廠區"] = asset.get("廠區", asset.get("位置", "越南西寧廠 (Tay Ninh)"))
        if "類別" not in asset:
            asset["類別"] = asset.get("資產類別", "生產與加工機具 (Machinery)")
        if "目前狀態" not in asset:
            asset["目前狀態"] = asset.get("狀態", "🟢 在用 (Active)")
        if "取得成本" not in asset:
            asset["取得成本"] = asset.get("成本", 0.0)
        if "租約起始日期" not in asset:
            asset["租約起始日期"] = "-"
        if "租約到期日期" not in asset:
            asset["租約到期日期"] = "-"

    # 頂部統計指標
    total_assets = len(st.session_state.asset_db)
    total_cost = sum([float(a.get("取得成本", 0)) for a in st.session_state.asset_db])
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("總登記項目數", f"{total_assets} 項")
    with col_m2:
        st.metric("總金額 / 總租金", f"${total_cost:,.2f} USD")
    with col_m3:
        st.metric("廠區分布", "西寧廠 ｜ 海防廠")

    st.markdown("---")

    # 建立主頁籤
    tab_list, tab_add, tab_edit, tab_delete = st.tabs([
        L["tab_list"], L["tab_add"], L["tab_edit"], L["tab_delete"]
    ])

    # 1. 📑 廠區資產與合約總表與分類檢視
    with tab_list:
        st.markdown(f"### {L['table_header']}")
        
        # 第一層：廠區大分類 (Tab)
        plant_tab_all, plant_tab_tn, plant_tab_hp = st.tabs([
            L["plant_all"], L["plant_tn"], L["plant_hp"]
        ])

        def render_category_subtabs(plant_filter_name):
            if plant_filter_name == "all":
                plant_data = st.session_state.asset_db
            else:
                plant_data = [a for a in st.session_state.asset_db if plant_filter_name in str(a.get("存放廠區", ""))]

            # 第二層：品項分類子分頁 (加入土地房屋租賃)
            cat_all, cat_lease, cat_prod, cat_car, cat_it, cat_office, cat_net, cat_qa, cat_wh, cat_safety = st.tabs([
                L["cat_all"], L["cat_lease"], L["cat_prod"], L["cat_car"], L["cat_it"], L["cat_office"], L["cat_net"], L["cat_qa"], L["cat_wh"], L["cat_safety"]
            ])

            def display_table(data_list):
                if data_list:
                    display_list = []
                    for idx, asset in enumerate(data_list, 1):
                        start_d = asset.get("租約起始日期", "-")
                        end_d = asset.get("租約到期日期", "-")
                        lease_str = f"{start_d} ~ {end_d}" if start_d != "-" and end_d != "-" else "-"
                        
                        display_list.append({
                            L["col_index"]: idx,
                            L["col_code"]: asset.get("資產編號", "-"),
                            L["col_name"]: asset.get("資產名稱", "-"),
                            L["col_category"]: asset.get("類別", "-"),
                            L["col_factory"]: asset.get("存放廠區", "-"),
                            L["col_brand"]: asset.get("品牌型號", "-"),
                            L["col_lease_period"]: lease_str,
                            L["col_status"]: asset.get("目前狀態", "-"),
                            L["col_cost"]: f"${float(asset.get('取得成本', 0)):,.2f} USD"
                        })
                    st.dataframe(pd.DataFrame(display_list), use_container_width=True)
                else:
                    st.info("目前此分類與廠區中尚無記錄。")

            with cat_all:
                display_table(plant_data)
            with cat_lease:
                display_table([a for a in plant_data if "租賃" in str(a.get("類別", "")) or "Lease" in str(a.get("類別", ""))])
            with cat_prod:
                display_table([a for a in plant_data if "生產" in str(a.get("類別", "")) or "Machinery" in str(a.get("類別", ""))])
            with cat_car:
                display_table([a for a in plant_data if "車輛" in str(a.get("類別", "")) or "Vehicle" in str(a.get("類別", ""))])
            with cat_it:
                display_table([a for a in plant_data if "電腦" in str(a.get("類別", "")) or "PC" in str(a.get("類別", ""))])
            with cat_office:
                display_table([a for a in plant_data if "辦公" in str(a.get("類別", "")) or "Office" in str(a.get("類別", ""))])
            with cat_net:
                display_table([a for a in plant_data if "網通" in str(a.get("類別", "")) or "Network" in str(a.get("類別", ""))])
            with cat_qa:
                display_table([a for a in plant_data if "品管" in str(a.get("類別", "")) or "Testing" in str(a.get("類別", ""))])
            with cat_wh:
                display_table([a for a in plant_data if "倉儲" in str(a.get("類別", "")) or "Warehouse" in str(a.get("類別", ""))])
            with cat_safety:
                display_table([a for a in plant_data if "消防" in str(a.get("類別", "")) or "Safety" in str(a.get("類別", ""))])

        with plant_tab_all:
            render_category_subtabs("all")
        with plant_tab_tn:
            render_category_subtabs("西寧")
        with plant_tab_hp:
            render_category_subtabs("海防")

    # 2. ➕ 新增固定資產與租賃合約
    with tab_add:
        st.markdown(f"### {L['tab_add']}")
        auto_code = f"AST-EQ-{len(st.session_state.asset_db) + 1:03d}"

        with st.form("form_add_asset"):
            c1, c2 = st.columns(2)
            with c1:
                a_code = st.text_input(L["lbl_code"], value=auto_code)
                a_name = st.text_input(L["lbl_name"])
                a_factory = st.selectbox(L["lbl_factory"], L["factory_opts"])
                a_cat = st.selectbox(L["lbl_category"], L["cat_opts"])
            with c2:
                a_brand = st.text_input(L["lbl_brand"], placeholder="例如: Dell / Amada / 房東名稱")
                a_status = st.selectbox(L["lbl_status"], L["status_opts"])
                a_cost = st.number_input(L["lbl_cost"], min_value=0.0, value=1500.0, step=100.0)

            st.markdown("#### 🏢 租賃合約專用日期（若非土地房屋租賃可不填）")
            d1, d2 = st.columns(2)
            with d1:
                a_start = st.date_input(L["lbl_start_date"], value=datetime.date.today())
            with d2:
                a_end = st.date_input(L["lbl_end_date"], value=datetime.date.today() + datetime.timedelta(days=365*3))

            submitted = st.form_submit_button(L["btn_add"], type="primary", use_container_width=True)
            if submitted:
                if a_code and a_name:
                    existing_codes = [a["資產編號"] for a in st.session_state.asset_db]
                    if a_code in existing_codes:
                        st.error(f"⚠️ 錯誤：編號 `{a_code}` 已經存在！")
                    else:
                        is_lease = "租賃" in a_cat
                        st.session_state.asset_db.append({
                            "資產編號": a_code,
                            "資產名稱": a_name,
                            "類別": a_cat,
                            "存放廠區": a_factory,
                            "品牌型號": a_brand if a_brand else "-",
                            "車牌號碼": "-",
                            "目前狀態": a_status,
                            "取得成本": a_cost,
                            "租約起始日期": a_start.strftime("%Y-%m-%d") if is_lease else "-",
                            "租約到期日期": a_end.strftime("%Y-%m-%d") if is_lease else "-"
                        })
                        st.success(L["success_add"].format(name=a_name, code=a_code))
                        st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫編號與名稱！")

    # 3. ✏️ 修改資產與租約資料
    with tab_edit:
        st.markdown(f"### {L['tab_edit']}")
        if st.session_state.asset_db:
            asset_options = {f"[{a.get('存放廠區', '')[:2]}] {a.get('資產編號', '')} - {a.get('資產名稱', '')}": a for a in st.session_state.asset_db}
            sel_edit_key = st.selectbox("選擇要修改的記錄 (Select Record to Edit)", list(asset_options.keys()))
            target_asset = asset_options[sel_edit_key]

            with st.form("form_edit_asset"):
                ed_name = st.text_input(L["lbl_name"], value=target_asset.get("資產名稱", ""))
                
                curr_factory = target_asset.get("存放廠區", L["factory_opts"][0])
                factory_idx = L["factory_opts"].index(curr_factory) if curr_factory in L["factory_opts"] else 0
                ed_factory = st.selectbox(L["lbl_factory"], L["factory_opts"], index=factory_idx)

                curr_cat = target_asset.get("類別", L["cat_opts"][0])
                cat_idx = L["cat_opts"].index(curr_cat) if curr_cat in L["cat_opts"] else 0
                ed_cat = st.selectbox(L["lbl_category"], L["cat_opts"], index=cat_idx)
                
                ed_brand = st.text_input(L["lbl_brand"], value=target_asset.get("品牌型號", "-"))
                
                curr_status = target_asset.get("目前狀態", L["status_opts"][0])
                status_idx = L["status_opts"].index(curr_status) if curr_status in L["status_opts"] else 0
                ed_status = st.selectbox(L["lbl_status"], L["status_opts"], index=status_idx)
                
                ed_cost = st.number_input(L["lbl_cost"], min_value=0.0, value=float(target_asset.get("取得成本", 0)), step=100.0)

                st.markdown("#### 🏢 租賃合約日期維護")
                existing_start = target_asset.get("租約起始日期", "-")
                existing_end = target_asset.get("租約到期日期", "-")
                
                try:
                    def_start = datetime.datetime.strptime(existing_start, "%Y-%m-%d").date() if existing_start != "-" else datetime.date.today()
                except:
                    def_start = datetime.date.today()
                
                try:
                    def_end = datetime.datetime.strptime(existing_end, "%Y-%m-%d").date() if existing_end != "-" else datetime.date.today()
                except:
                    def_end = datetime.date.today()

                ed1, ed2 = st.columns(2)
                with ed1:
                    ed_start = st.date_input(L["lbl_start_date"], value=def_start)
                with ed2:
                    ed_end = st.date_input(L["lbl_end_date"], value=def_end)

                if st.form_submit_button(L["btn_save_edit"], type="primary", use_container_width=True):
                    is_lease = "租賃" in ed_cat
                    target_asset["資產名稱"] = ed_name
                    target_asset["存放廠區"] = ed_factory
                    target_asset["類別"] = ed_cat
                    target_asset["品牌型號"] = ed_brand
                    target_asset["目前狀態"] = ed_status
                    target_asset["取得成本"] = ed_cost
                    target_asset["租約起始日期"] = ed_start.strftime("%Y-%m-%d") if is_lease else "-"
                    target_asset["租約到期日期"] = ed_end.strftime("%Y-%m-%d") if is_lease else "-"
                    st.success(L["success_edit"].format(code=target_asset.get("資產編號", "")))
                    st.rerun()
        else:
            st.info("目前無記錄可供修改。")

    # 4. 🗑️ 刪除或報廢資產
    with tab_delete:
        st.markdown(f"### {L['tab_delete']}")
        if st.session_state.asset_db:
            del_options = {f"[{a.get('存放廠區', '')[:2]}] {a.get('資產編號', '')} - {a.get('資產名稱', '')}": a for a in st.session_state.asset_db}
            sel_del_key = st.selectbox("選擇要刪除或報廢的記錄", list(del_options.keys()))
            target_del = del_options[sel_del_key]

            st.warning(f"⚠️ 您確定要刪除或報廢記錄 **{target_del.get('資產編號', '')} - {target_del.get('資產名稱', '')}** 嗎？此動作無法復原。")
            
            if st.button(L["btn_delete"], type="primary"):
                target_code = target_del.get("資產編號", "")
                st.session_state.asset_db = [a for a in st.session_state.asset_db if a.get("資產編號", "") != target_code]
                st.success(L["success_delete"])
                st.rerun()
        else:
            st.info("目前系統中無任何記錄可供刪除。")

def show(*args, **kwargs):
    render_asset_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_asset_management_page(*args, **kwargs)

def render_asset_management(*args, **kwargs):
    render_asset_management_page(*args, **kwargs)
