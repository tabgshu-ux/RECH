import pandas as pd
import streamlit as st

# 🌐 多語系字典 (i18n) - 保留並擴充個人電腦、筆電與車輛項目
ASSET_I18N = {
    "繁體中文": {
        "page_title": "📦 裕豐電機工業 - 生產設備與固定資產管理",
        "sub_title": "管理西寧廠/平陽廠生產機械設備、辦公個人電腦、攜帶式筆電與公務/使用車輛。",
        "tab_overview": "📑 設備與資產總覽",
        "tab_register": "➕ 新增設備與資產登記",
        "lbl_code": "資產/設備編號",
        "lbl_name": "資產/設備名稱",
        "lbl_cat": "資產類別",
        "lbl_site": "存放廠區 / 使用部門",
        "lbl_status": "當前狀態",
        "lbl_cost": "取得成本 (USD)",
        "lbl_brand": "品牌選擇",
        "lbl_custom_model": "型號細節 (手動輸入)",
        "lbl_plate": "車牌號碼 (若為車輛)",
        "btn_add": "💾 儲存資產資料",
        "msg_success": "✅ 已成功登記新資產/設備！",
        "status_in_use": "🟢 在用",
        "status_maint": "🔧 維修中",
        "status_backup": "📦 庫存備用",
        "site_tn": "🇻🇳 越南西寧廠 - 管理/生產部",
        "site_paint": "🇻🇳 越南西寧廠 - 烤漆塗裝組",
        "site_assy": "🇻🇳 越南西寧廠 - 配電盤組裝組",
        "site_tw": "🇹🇼 台灣總部 - 辦公室",
        "cat_busbar": "銅排加工設備",
        "cat_sheet": "板金加工設備",
        "cat_paint": "塗裝設備",
        "cat_qc": "品管與檢測儀器",
        "cat_pc": "個人電腦 (Desktop PC)",
        "cat_laptop": "攜帶式電腦 (Laptop)",
        "cat_vehicle": "使用車輛 (Vehicle)",
    },
    "Tiếng Việt": {
        "page_title": "📦 REETECH INDUSTRIAL - Quản lý Thiết bị & Tài sản Cố định",
        "sub_title": "Quản lý máy móc sản xuất, máy tính để bàn, máy tính xách tay và phương tiện đi lại.",
        "tab_overview": "📑 Tổng quan Thiết bị & Tài sản",
        "tab_register": "➕ Đăng ký Thiết bị / Tài sản Mới",
        "lbl_code": "Mã tài sản",
        "lbl_name": "Tên tài sản",
        "lbl_cat": "Phân loại tài sản",
        "lbl_site": "Nhà máy / Bộ phận",
        "lbl_status": "Trạng thái hiện tại",
        "lbl_cost": "Nguyên giá (USD)",
        "lbl_brand": "Thương hiệu",
        "lbl_custom_model": "Model chi tiết",
        "lbl_plate": "Biển số xe (nếu là xe)",
        "btn_add": "💾 Lưu thông tin tài sản",
        "msg_success": "✅ Đã đăng ký tài sản thành công!",
        "status_in_use": "🟢 Đang sử dụng",
        "status_maint": "🔧 Đang bảo trì",
        "status_backup": "📦 Dự phòng",
        "site_tn": "Nhà máy Tây Ninh - Quản lý/Sản xuất",
        "site_paint": "Nhà máy Tây Ninh - Tổ Sơn",
        "site_assy": "Nhà máy Tây Ninh - Tổ Lắp ráp",
        "site_tw": "Văn phòng Đài Loan",
        "cat_busbar": "Thiết bị gia công thanh cái",
        "cat_sheet": "Thiết bị gia công cơ khí",
        "cat_paint": "Thiết bị sơn tĩnh điện",
        "cat_qc": "Thiết bị đo lường & QC",
        "cat_pc": "Máy tính để bàn (Desktop PC)",
        "cat_laptop": "Laptop / Máy tính xách tay",
        "cat_vehicle": "Phương tiện vận chuyển / Xe",
    },
    "English": {
        "page_title": "📦 REETECH INDUSTRIAL - Equipment & Fixed Asset Management",
        "sub_title": "Manage production machinery, desktop PCs, laptops, and company vehicles.",
        "tab_overview": "📑 Asset Overview",
        "tab_register": "➕ Register New Asset",
        "lbl_code": "Asset Code",
        "lbl_name": "Equipment / Asset Name",
        "lbl_cat": "Category",
        "lbl_site": "Site / Department",
        "lbl_status": "Current Status",
        "lbl_cost": "Acquisition Cost (USD)",
        "lbl_brand": "Brand",
        "lbl_custom_model": "Model Details (Manual Input)",
        "lbl_plate": "License Plate (If Vehicle)",
        "btn_add": "💾 Save Asset Data",
        "msg_success": "✅ Asset registered successfully!",
        "status_in_use": "🟢 In Use",
        "status_maint": "🔧 Maintenance",
        "status_backup": "📦 Backup Stock",
        "site_tn": "Tay Ninh Plant - General/Production",
        "site_paint": "Tay Ninh Plant - Painting",
        "site_assy": "Tay Ninh Plant - Assembly",
        "site_tw": "Taiwan HQ - Office",
        "cat_busbar": "Busbar Fabrication Machine",
        "cat_sheet": "Sheet Metal Equipment",
        "cat_paint": "Powder Coating Equipment",
        "cat_qc": "QC Testing Equipment",
        "cat_pc": "Desktop PC",
        "cat_laptop": "Laptop",
        "cat_vehicle": "Company Vehicle",
    },
}


def render_asset_management_page(*args, **kwargs):
    # 自動讀取全局語系設定
    lang = (
        kwargs.get("lang")
        or kwargs.get("curr_lang")
        or st.session_state.get("current_lang", "繁體中文")
    )
    L = ASSET_I18N.get(lang, ASSET_I18N["繁體中文"])

    st.title(L["page_title"])
    st.caption(L["sub_title"])

    tab1, tab2 = st.tabs([L["tab_overview"], L["tab_register"]])

    # 初始化資產資料庫 (包含生產設備、電腦與車輛範例)
    if "assets_db" not in st.session_state or not st.session_state.assets_db:
        st.session_state.assets_db = [
            {
                "id": "EQ-TN-001",
                "name": "CNC 數控母線銅排彎折加工機",
                "category": L["cat_busbar"],
                "site": L["site_tn"],
                "brand_model": "Amada - CNC Busbar 160T",
                "plate_no": "-",
                "status": L["status_in_use"],
                "cost": 45000,
            },
            {
                "id": "EQ-TN-002",
                "name": "AMADA 數控液壓折床 150T",
                "category": L["cat_sheet"],
                "site": L["site_tn"],
                "brand_model": "AMADA - Press Brake HFE",
                "plate_no": "-",
                "status": L["status_in_use"],
                "cost": 78000,
            },
            {
                "id": "AST-PC-001",
                "name": "財務部會計主管辦公電腦",
                "category": L["cat_pc"],
                "site": L["site_tn"],
                "brand_model": "Dell - OptiPlex 7090 i7",
                "plate_no": "-",
                "status": L["status_in_use"],
                "cost": 1200,
            },
            {
                "id": "AST-LAP-001",
                "name": "總經理攜帶式筆記型電腦",
                "category": L["cat_laptop"],
                "site": L["site_tw"],
                "brand_model": "Apple - MacBook Pro 16 M3",
                "plate_no": "-",
                "status": L["status_in_use"],
                "cost": 2200,
            },
            {
                "id": "AST-CAR-001",
                "name": "越南西寧廠商務公務車",
                "category": L["cat_vehicle"],
                "site": L["site_tn"],
                "brand_model": "Toyota - Fortuner 2.8L",
                "plate_no": "61A-888.66",
                "status": L["status_in_use"],
                "cost": 28000,
            },
        ]

    # ----------------------------------------------------
    # 📑 頁籤一：設備與資產總覽
    # ----------------------------------------------------
    with tab1:
        total_assets = len(st.session_state.assets_db)
        total_val = sum(item["cost"] for item in st.session_state.assets_db)

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("📦 總登錄資產數", f"{total_assets} 項")
        col_m2.metric("💰 總取得成本", f"${total_val:,.0f} USD")
        col_m3.metric("🚗 涵蓋範圍", "生產設備、電腦與車輛")

        st.divider()

        # 轉換 DataFrame 呈現
        display_data = []
        for item in st.session_state.assets_db:
            display_data.append({
                "編號": item["id"],
                "名稱": item["name"],
                "類別": item["category"],
                "存放廠區/部門": item["site"],
                "品牌與型號": item["brand_model"],
                "車牌號碼": item.get("plate_no", "-"),
                "目前狀態": item["status"],
                "取得成本": f"${item['cost']:,.0f} USD",
            })

        df_assets = pd.DataFrame(display_data)
        st.dataframe(df_assets, use_container_width=True)

    # ----------------------------------------------------
    # ➕ 頁籤二：新增設備與資產登記 (支援電腦與車輛細節)
    # ----------------------------------------------------
    with tab2:
        c1, c2 = st.columns(2)
        code = c1.text_input(L["lbl_code"], value="AST-DEV-005")
        name = c2.text_input(L["lbl_name"], value="")

        c3, c4 = st.columns(2)
        cat = c3.selectbox(
            L["lbl_cat"],
            [
                L["cat_busbar"],
                L["cat_sheet"],
                L["cat_paint"],
                L["cat_qc"],
                L["cat_pc"],
                L["cat_laptop"],
                L["cat_vehicle"],
            ],
        )
        site = c4.selectbox(
            L["lbl_site"],
            [L["site_tn"], L["site_paint"], L["site_assy"], L["site_tw"]],
        )

        c5, c6 = st.columns(2)
        status = c5.selectbox(
            L["lbl_status"],
            [L["status_in_use"], L["status_maint"], L["status_backup"]],
        )
        cost = c6.number_input(
            L["lbl_cost"], min_value=0.0, value=1500.0, step=100.0
        )

        st.divider()
        st.markdown("#### 🏷️ 詳細規格登記（電腦品牌型號 / 車輛牌照號碼）")

        c_b1, c_b2, c_b3 = st.columns(3)
        with c_b1:
            brand_options = [
                "其他 (手動輸入)",
                "Toyota",
                "Honda",
                "Ford",
                "Dell",
                "HP",
                "Apple",
                "Lenovo",
                "Asus",
                "Amada",
            ]
            brand = st.selectbox(L["lbl_brand"], brand_options)
        with c_b2:
            custom_model = st.text_input(
                L["lbl_custom_model"], value="", placeholder="例如: Latitude 5530 / Vios"
            )
        with c_b3:
            plate_no = st.text_input(
                L["lbl_plate"], value="-", placeholder="例如: 61A-123.45"
            )

        if st.button(L["btn_add"], type="primary"):
            final_brand_model = (
                f"{brand} - {custom_model}"
                if brand != "其他 (手動輸入)" and custom_model
                else (custom_model if custom_model else brand)
            )

            st.session_state.assets_db.append(
                {
                    "id": code,
                    "name": name if name else "未命名資產",
                    "category": cat,
                    "site": site,
                    "brand_model": final_brand_model,
                    "plate_no": plate_no if L["cat_vehicle"] in cat else "-",
                    "status": status,
                    "cost": cost,
                }
            )
            st.success(L["msg_success"])
            st.rerun()


def show(*args, **kwargs):
    render_asset_management_page(*args, **kwargs)


def main(*args, **kwargs):
    render_asset_management_page(*args, **kwargs)
