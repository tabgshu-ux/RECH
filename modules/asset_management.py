import pandas as pd
import streamlit as st

# 🌐 多語系字典 (i18n)
ASSET_I18N = {
    "繁體中文": {
        "page_title": "📦 裕豐電機工業 - 生產設備與資產管理",
        "sub_title": "管理西寧廠/平陽廠 CNC 銅排加工機、數控折床、自動烤漆塗裝線與檢測設備。",
        "tab_overview": "📑 設備與資產總覽",
        "tab_register": "➕ 新增設備登記",
        "lbl_code": "設備編號",
        "lbl_name": "設備名稱",
        "lbl_cat": "資產類別",
        "lbl_site": "存放廠區 / 車間",
        "lbl_status": "當前狀態",
        "lbl_cost": "取得成本 (USD)",
        "btn_add": "💾 儲存資產資料",
        "msg_success": "✅ 已成功登記新設備！",
        "status_in_use": "在用",
        "status_maint": "維修中",
        "site_tn": "VN 西寧廠 - 板金組",
        "site_paint": "VN 西寧廠 - 烤漆組",
        "site_assy": "VN 西寧廠 - 組裝組",
        "cat_busbar": "銅排加工設備",
        "cat_sheet": "板金加工設備",
        "cat_paint": "塗裝設備",
        "cat_qc": "品管與檢測儀器",
    },
    "Tiếng Việt": {
        "page_title": "📦 REETECH INDUSTRIAL - Quản lý Thiết bị & Tài sản",
        "sub_title": "Quản lý máy gia công thanh cái CNC, máy chấn, dây chuyền sơn tĩnh điện và thiết bị kiểm thử.",
        "tab_overview": "📑 Tổng quan Thiết bị & Tài sản",
        "tab_register": "➕ Đăng ký Thiết bị Mới",
        "lbl_code": "Mã thiết bị",
        "lbl_name": "Tên thiết bị",
        "lbl_cat": "Phân loại tài sản",
        "lbl_site": "Nhà máy / Xưởng",
        "lbl_status": "Trạng thái hiện tại",
        "lbl_cost": "Nguyên giá (USD)",
        "btn_add": "💾 Lưu thông tin tài sản",
        "msg_success": "✅ Đã đăng ký thiết bị thành công!",
        "status_in_use": "Đang sử dụng",
        "status_maint": "Đang bảo trì",
        "site_tn": "Nhà máy Tây Ninh - Tổ Gia công",
        "site_paint": "Nhà máy Tây Ninh - Tổ Sơn",
        "site_assy": "Nhà máy Tây Ninh - Tổ Lắp ráp",
        "cat_busbar": "Thiết bị gia công thanh cái",
        "cat_sheet": "Thiết bị gia công cơ khí",
        "cat_paint": "Thiết bị sơn tĩnh điện",
        "cat_qc": "Thiết bị đo lường & QC",
    },
    "English": {
        "page_title": "📦 REETECH INDUSTRIAL - Equipment & Fixed Asset Management",
        "sub_title": "Manage Tay Ninh plant CNC busbar processing machines, press brakes, powder coating lines, and testing equipment.",
        "tab_overview": "📑 Asset Overview",
        "tab_register": "➕ Register New Asset",
        "lbl_code": "Asset Code",
        "lbl_name": "Equipment Name",
        "lbl_cat": "Category",
        "lbl_site": "Site / Department",
        "lbl_status": "Current Status",
        "lbl_cost": "Acquisition Cost (USD)",
        "btn_add": "💾 Save Asset Data",
        "msg_success": "✅ Asset registered successfully!",
        "status_in_use": "In Use",
        "status_maint": "Maintenance",
        "site_tn": "Tay Ninh Plant - Sheet Metal",
        "site_paint": "Tay Ninh Plant - Painting",
        "site_assy": "Tay Ninh Plant - Assembly",
        "cat_busbar": "Busbar Fabrication Machine",
        "cat_sheet": "Sheet Metal Equipment",
        "cat_paint": "Powder Coating Equipment",
        "cat_qc": "QC Testing Equipment",
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

    if "assets_db" not in st.session_state:
        st.session_state.assets_db = [
            {
                "id": "EQ-TN-001",
                "name": "CNC 數控母線銅排彎折加工機",
                "category": L["cat_busbar"],
                "site": L["site_tn"],
                "status": L["status_in_use"],
                "cost": 45000,
            },
            {
                "id": "EQ-TN-002",
                "name": "AMADA 數控液壓折床 150T",
                "category": L["cat_sheet"],
                "site": L["site_tn"],
                "status": L["status_in_use"],
                "cost": 78000,
            },
            {
                "id": "EQ-TN-003",
                "name": "懸掛式半自動粉體塗裝烤漆線",
                "category": L["cat_paint"],
                "site": L["site_paint"],
                "status": L["status_in_use"],
                "cost": 120000,
            },
            {
                "id": "EQ-TN-004",
                "name": "高壓耐壓與絕緣測試儀 (5kV)",
                "category": L["cat_qc"],
                "site": L["site_assy"],
                "status": L["status_in_use"],
                "cost": 12000,
            },
        ]

    with tab1:
        df_assets = pd.DataFrame(st.session_state.assets_db)
        df_assets["cost"] = df_assets["cost"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(df_assets, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        code = c1.text_input(L["lbl_code"], value="EQ-TN-005")
        name = c2.text_input(L["lbl_name"], value="")

        c3, c4 = st.columns(2)
        cat = c3.selectbox(
            L["lbl_cat"],
            [L["cat_busbar"], L["cat_sheet"], L["cat_paint"], L["cat_qc"]],
        )
        site = c4.selectbox(
            L["lbl_site"], [L["site_tn"], L["site_paint"], L["site_assy"]]
        )

        c5, c6 = st.columns(2)
        status = c5.selectbox(
            L["lbl_status"], [L["status_in_use"], L["status_maint"]]
        )
        cost = c6.number_input(
            L["lbl_cost"], min_value=0.0, value=15000.0, step=1000.0
        )

        if st.button(L["btn_add"], type="primary"):
            st.session_state.assets_db.append(
                {
                    "id": code,
                    "name": name,
                    "category": cat,
                    "site": site,
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
