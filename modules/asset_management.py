import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 固定資產與設備管理模組多語系字典 (i18n)
# ----------------------------------------------------
ASSET_I18N = {
    "繁體中文": {
        "title": "📦 裕豐電機工業 - 生產設備與固定資產管理",
        "caption": "管理西寧廠/海防廠生產機械設備、辦公個人電腦、攜帶式筆電與公務/使用車輛。",
        "tab_list": "📑 設備與資產總覽",
        "tab_register": "➕ 新增設備與資產登記",
        "metric_total": "總登記資產數",
        "metric_cost": "總取得成本",
        "metric_sites": "涵蓋廠區據點",
        "sites_val": "越南西寧廠、越南海防廠",
        "table_header": "📋 廠區固定資產與設備總清冊",
        "no_records": "目前無資產紀錄。",
        "add_header": "➕ 登記全新廠區資產與設備",
        "lbl_code": "資產/設備編號 *",
        "lbl_name": "資產/設備名稱 *",
        "name_placeholder": "例如: CNC 數控母線排彎折加工機",
        "lbl_category": "資產類別 *",
        "cat_opts": ["生產與加工機具", "辦公電腦與IT設備", "筆記型電腦與行動裝置", "公務車輛與運輸工具", "廠區檢測儀器"],
        "lbl_site": "存放廠區 *",
        "site_opts": ["越南西寧廠 (Tay Ninh Plant)", "越南海防廠 (Hai Phong Plant)"],
        "lbl_brand": "品牌與型號細節",
        "lbl_barcode": "車牌號碼 / 財產條碼",
        "lbl_status": "目前狀態 *",
        "status_opts": ["🟢 在用", "🔧 維修中", "📦 庫存備用"],
        "lbl_cost": "取得成本 (USD) *",
        "btn_save": "💾 儲存並建立資產檔案",
        "success_save": "✅ 資產已成功建檔！",
        "fill_warning": "⚠️ 請完整填寫資產編號與名稱！",
        "col_index": "STT",
        "col_select": "選擇",
        "col_id": "資產編號",
        "col_name": "資產名稱",
        "col_cat": "類別",
        "col_site": "存放廠區",
        "col_brand": "品牌與型號",
        "col_barcode": "車牌/條碼",
        "col_status": "目前狀態",
        "col_cost": "取得成本",
        "btn_del": "🗑️ 刪除勾選的資產/設備",
        "success_del": "✅ 已成功刪除選定的資產項目！"
    },
    "Tiếng Việt": {
        "title": "📦 REETECH INDUSTRIAL - Quản lý Thiết bị & Tài sản Cố định",
        "caption": "Quản lý máy móc sản xuất, máy tính, laptop và xe công ty tại Tây Ninh và Hải Phòng.",
        "tab_list": "📑 Tổng quan Thiết bị & Tài sản",
        "tab_register": "➕ Đăng ký Thiết bị / Tài sản Mới",
        "metric_total": "Tổng tài sản",
        "metric_cost": "Tổng giá trị đầu tư",
        "metric_sites": "Khu vực nhà máy",
        "sites_val": "Nhà máy Tây Ninh, Nhà máy Hải Phòng",
        "table_header": "📋 Sổ chi tiết Tài sản Cố định & Thiết bị Nhà máy",
        "no_records": "Hiện không có bản ghi tài sản nào.",
        "add_header": "➕ Đăng ký tài sản & thiết bị nhà máy mới",
        "lbl_code": "Mã tài sản *",
        "lbl_name": "Tên tài sản *",
        "name_placeholder": "Ví dụ: Máy chấn đồng CNC",
        "lbl_category": "Phân loại tài sản *",
        "cat_opts": ["Thiết bị gia công", "Máy tính để bàn (PC)", "Laptop", "Phương tiện vận chuyển / Xe", "Thiết bị QC"],
        "lbl_site": "Nhà máy lưu kho *",
        "site_opts": ["Nhà máy Tây Ninh", "Nhà máy Hải Phòng"],
        "lbl_brand": "Thương hiệu & Model",
        "lbl_barcode": "Biển số xe / Mã vạch",
        "lbl_status": "Trạng thái hiện tại *",
        "status_opts": ["🟢 Đang sử dụng", "🔧 Đang bảo trì", "📦 Dự phòng"],
        "lbl_cost": "Nguyên giá (USD) *",
        "btn_save": "💾 Lưu thông tin tài sản",
        "success_save": "✅ Đã đăng ký tài sản thành công!",
        "fill_warning": "⚠️ Vui lòng điền Mã tài sản và Tên tài sản!",
        "col_index": "STT",
        "col_select": "Chọn",
        "col_id": "Mã TS",
        "col_name": "Tên tài sản",
        "col_cat": "Phân loại",
        "col_site": "Nhà máy",
        "col_brand": "Thương hiệu",
        "col_barcode": "Biển số/Mã",
        "col_status": "Trạng thái",
        "col_cost": "Nguyên giá",
        "btn_del": "🗑️ Xóa tài sản đã chọn",
        "success_del": "✅ Đã xóa thành công tài sản đã chọn!"
    },
    "English": {
        "title": "📦 REETECH INDUSTRIAL - Equipment & Fixed Asset Management",
        "caption": "Manage production machinery, PCs, laptops, and vehicles in Tay Ninh and Hai Phong plants.",
        "tab_list": "📑 Asset Overview",
        "tab_register": "➕ Register New Asset",
        "metric_total": "Total Registered Assets",
        "metric_cost": "Total Acquisition Cost",
        "metric_sites": "Covered Plant Locations",
        "sites_val": "Tay Ninh Plant, Hai Phong Plant",
        "table_header": "📋 Plant Fixed Assets & Equipment Registry",
        "no_records": "No asset records found.",
        "add_header": "➕ Register New Plant Asset",
        "lbl_code": "Asset Code *",
        "lbl_name": "Asset Name *",
        "name_placeholder": "Example: CNC Copper Busbar Bending Machine",
        "lbl_category": "Category *",
        "cat_opts": ["Busbar Machine", "Desktop PC", "Laptop", "Company Vehicle", "QC Equipment"],
        "lbl_site": "Plant Location *",
        "site_opts": ["Tay Ninh Plant", "Hai Phong Plant"],
        "lbl_brand": "Brand & Model Details",
        "lbl_barcode": "License Plate / Barcode",
        "lbl_status": "Current Status *",
        "status_opts": ["🟢 In Use", "🔧 Maintenance", "📦 Backup Stock"],
        "lbl_cost": "Acquisition Cost (USD) *",
        "btn_save": "💾 Save Asset Data",
        "success_save": "✅ Asset registered successfully!",
        "fill_warning": "⚠️ Please fill in Asset Code and Name!",
        "col_index": "No.",
        "col_select": "Select",
        "col_id": "Asset Code",
        "col_name": "Asset Name",
        "col_cat": "Category",
        "col_site": "Plant",
        "col_brand": "Brand / Model",
        "col_barcode": "Plate / Barcode",
        "col_status": "Status",
        "col_cost": "Cost",
        "btn_del": "🗑️ Delete Selected Assets",
        "success_del": "✅ Selected assets successfully deleted!"
    }
}

# ----------------------------------------------------
# 🔄 智慧語意對照引擎
# ----------------------------------------------------
def smart_translate_asset(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    
    val_lower = text_val.lower()

    if "西寧廠" in text_val or "tay ninh" in val_lower:
        if target_lang == "Tiếng Việt": return "Nhà máy Tây Ninh"
        elif target_lang == "English": return "Tay Ninh Plant"
        return "越南西寧廠"
    if "海防廠" in text_val or "hai phong" in val_lower:
        if target_lang == "Tiếng Việt": return "Nhà máy Hải Phòng"
        elif target_lang == "English": return "Hai Phong Plant"
        return "越南海防廠"

    if "使用中" in text_val or "in use" in val_lower or "đang sử dụng" in val_lower:
        if target_lang == "Tiếng Việt": return "🟢 Đang sử dụng"
        elif target_lang == "English": return "🟢 In Use"
        return "🟢 在用"

    return text_val

def render_asset_management_page(*args, **kwargs):
    lang = kwargs.get("lang") or st.session_state.get("current_lang", "繁體中文")
    L = ASSET_I18N.get(lang, ASSET_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "assets_db" not in st.session_state or not st.session_state.assets_db:
        st.session_state.assets_db = [
            {
                "id": "EQ-TN-001",
                "name": "CNC 數控母線銅排彎折加工機",
                "category": "生產與加工機具",
                "site": "越南西寧廠",
                "brand_model": "Amada - CNC Busbar 160T",
                "plate_no": "-",
                "status": "🟢 在用",
                "cost": 45000.0,
            },
            {
                "id": "AST-PC-001",
                "name": "西寧廠財務主管辦公電腦",
                "category": "個人電腦 (Desktop PC)",
                "site": "越南西寧廠",
                "brand_model": "Dell - OptiPlex 7090 i7",
                "plate_no": "-",
                "status": "🟢 在用",
                "cost": 1200.0,
            },
            {
                "id": "AST-CAR-001",
                "name": "西寧廠廠長商務公務車",
                "category": "使用車輛 (Vehicle)",
                "site": "越南西寧廠",
                "brand_model": "Toyota - Fortuner 2.8L",
                "plate_no": "61A-888.66",
                "status": "🟢 在用",
                "cost": 28000.0,
            },
        ]
    else:
        for item in st.session_state.assets_db:
            if "brand_model" not in item and "brand" in item:
                item["brand_model"] = item["brand"]
            if "brand_model" not in item:
                item["brand_model"] = "-"
            if "plate_no" not in item:
                item["plate_no"] = "-"

    tab1, tab2 = st.tabs([L["tab_list"], L["tab_register"]])

    with tab1:
        total_assets = len(st.session_state.assets_db)
        total_val = sum(item.get("cost", 0) for item in st.session_state.assets_db)

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(L["metric_total"], f"{total_assets} 項")
        col_m2.metric(L["metric_cost"], f"${total_val:,.0f} USD")
        col_m3.metric(L["metric_sites"], L["sites_val"])

        st.divider()
        st.markdown(f"### {L['table_header']}")

        display_data = []
        for item in st.session_state.assets_db:
            display_data.append({
                L["col_select"]: False,
                L["col_id"]: item.get("id", ""),
                L["col_name"]: item.get("name", ""),
                L["col_cat"]: item.get("category", ""),
                L["col_site"]: smart_translate_asset(item.get("site", ""), lang),
                L["col_brand"]: item.get("brand_model", "-"),
                L["col_barcode"]: item.get("plate_no", "-"),
                L["col_status"]: smart_translate_asset(item.get("status", ""), lang),
                L["col_cost"]: f"${item.get('cost', 0):,.0f} USD",
            })

        df_assets = pd.DataFrame(display_data)
        
        edited_df = st.data_editor(
            df_assets,
            use_container_width=True,
            num_rows="dynamic",
            key="asset_editor"
        )

        if st.button(L["btn_del"], type="primary"):
            remaining_assets = []
            for idx, row in edited_df.iterrows():
                if not row.get(L["col_select"], False):
                    orig_id = row[L["col_id"]]
                    matched = next((a for a in st.session_state.assets_db if a.get("id") == orig_id), None)
                    if matched:
                        remaining_assets.append(matched)
            st.session_state.assets_db = remaining_assets
            st.success(L["success_del"])
            st.rerun()

    with tab2:
        st.markdown(f"### {L['add_header']}")
        c1, c2 = st.columns(2)
        code = c1.text_input(L["lbl_code"], value="AST-DEV-005")
        name = c2.text_input(L["lbl_name"], placeholder=L["name_placeholder"])

        c3, c4 = st.columns(2)
        cat = c3.selectbox(L["lbl_category"], L["cat_opts"])
        site = c4.selectbox(L["lbl_site"], L["site_opts"])

        c5, c6 = st.columns(2)
        status = c5.selectbox(L["lbl_status"], L["status_opts"])
        cost = c6.number_input(L["lbl_cost"], min_value=0.0, value=1500.0, step=100.0)

        st.divider()
        c_b1, c_b2 = st.columns(2)
        with c_b1:
            brand_model = st.text_input(L["lbl_brand"], value="", placeholder="例如: Dell Latitude / Toyota")
        with c_b2:
            plate_no = st.text_input(L["lbl_barcode"], value="-", placeholder="例如: 61A-123.45")

        if st.button(L["btn_save"], type="primary"):
            st.session_state.assets_db.append({
                "id": code,
                "name": name if name else "未命名資產",
                "category": cat,
                "site": site,
                "brand_model": brand_model if brand_model else "-",
                "plate_no": plate_no,
                "status": status,
                "cost": cost,
            })
            st.success(L["success_save"])
            st.rerun()

def show(*args, **kwargs):
    render_asset_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_asset_management_page(*args, **kwargs)
