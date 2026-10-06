import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 固定資產與設備管理模組多語系字典 (i18n)
# ----------------------------------------------------
ASSET_I18N = {
    "繁體中文": {
        "title": "REETECH INDUSTRIAL - 管理部 - 設備與資產管理",
        "caption": "管理廠區生產機具、辦公電腦、伺服器及公務車輛在西寧廠與海防廠之資產清冊與折舊狀態。",
        "tab_list": "📑 資產總覽與折舊狀態",
        "tab_add": "➕ 登記新設備與資產",
        "metric_total": "總登記資產數",
        "metric_cost": "總取得成本",
        "metric_sites": "涵蓋廠區據點",
        "sites_val": "越南西寧廠、越南海防廠",
        "table_header": "📋 廠區固定資產與設備總清冊",
        "no_records": "目前無資產紀錄。",
        "add_header": "➕ 登記全新廠區資產與設備",
        "lbl_code": "資產編號 (Asset ID) *",
        "lbl_name": "資產名稱 *",
        "name_placeholder": "例如: CNC 數控母線排彎折加工機",
        "lbl_category": "資產類別 *",
        "cat_opts": ["生產與加工機具", "辦公電腦與IT設備", "筆記型電腦與行動裝置", "公務車輛與運輸工具", "廠區檢測儀器"],
        "lbl_site": "存放廠區 *",
        "site_opts": ["越南西寧廠 (Tay Ninh Plant)", "越南海防廠 (Hai Phong Plant)", "台灣總部 (Taiwan HQ)"],
        "lbl_brand": "品牌與型號",
        "lbl_barcode": "資產條碼 / 財產編號",
        "lbl_status": "目前狀態 *",
        "status_opts": ["使用中 (In Use)", "維修保養中 (Maintenance)", "閒置備用 (Idle)", "已報廢 (Disposed)"],
        "lbl_cost": "取得成本 (USD) *",
        "btn_save": "💾 儲存並建立資產檔案",
        "success_save": "✅ 資產 `{asset_id}` 已成功建檔！",
        "fill_warning": "⚠️ 請完整填寫資產編號與名稱！",
        # 表格欄位
        "col_index": "STT",
        "col_select": "選擇",
        "col_id": "資產編號",
        "col_name": "資產名稱",
        "col_cat": "資產類別",
        "col_site": "存放廠區",
        "col_brand": "品牌型號",
        "col_barcode": "財產條碼",
        "col_status": "目前狀態",
        "col_cost": "取得成本"
    },
    "Tiếng Việt": {
        "title": "REETECH INDUSTRIAL - Khối Quản lý - Quản lý Thiết bị & Tài sản",
        "caption": "Quản lý máy móc sản xuất, máy tính, thiết bị IT và xe công ty tại nhà máy Tây Ninh và Hải Phòng.",
        "tab_list": "📑 Tổng quan Thiết bị & Tài sản",
        "tab_add": "➕ Đăng ký Thiết bị / Tài sản Mới",
        "metric_total": "Tổng tài sản",
        "metric_cost": "Tổng giá trị đầu tư",
        "metric_sites": "Khu vực nhà máy",
        "sites_val": "Nhà máy Tây Ninh, Nhà máy Hải Phòng",
        "table_header": "📋 Sổ chi tiết Tài sản Cố định & Thiết bị Nhà máy",
        "no_records": "Hiện không có bản ghi tài sản nào.",
        "add_header": "➕ Đăng ký tài sản & thiết bị nhà máy mới",
        "lbl_code": "Mã tài sản (Asset ID) *",
        "lbl_name": "Tên tài sản *",
        "name_placeholder": "Ví dụ: Máy chấn đồng CNC",
        "lbl_category": "Phân loại tài sản *",
        "cat_opts": ["Máy móc sản xuất", "Máy tính để bàn (Desktop)", "Laptop & Thiết bị di động", "Phương tiện vận chuyển / Xe", "Thiết bị đo lường"],
        "lbl_site": "Nhà máy lưu kho *",
        "site_opts": ["Nhà máy Tây Ninh", "Nhà máy Hải Phòng", "Trụ sở Đài Loan (HQ)"],
        "lbl_brand": "Hãng sản xuất & Model",
        "lbl_barcode": "Mã vạch tài sản",
        "lbl_status": "Trạng thái hiện tại *",
        "status_opts": ["Đang sử dụng (In Use)", "Đang bảo trì (Maintenance)", "Dự phòng (Idle)", "Đã thanh lý (Disposed)"],
        "lbl_cost": "Nguyên giá (USD) *",
        "btn_save": "💾 Lưu và tạo hồ sơ tài sản",
        "success_save": "✅ Đã tạo thành công tài sản `{asset_id}`!",
        "fill_warning": "⚠️ Vui lòng điền Mã tài sản và Tên tài sản!",
        # Tiêu đề bảng
        "col_index": "STT",
        "col_select": "Chọn",
        "col_id": "Mã TS",
        "col_name": "Tên tài sản",
        "col_cat": "Phân loại",
        "col_site": "Nhà máy",
        "col_brand": "Hãng/Model",
        "col_barcode": "Mã vạch",
        "col_status": "Trạng thái",
        "col_cost": "Nguyên giá"
    },
    "English": {
        "title": "REETECH INDUSTRIAL - Admin - Equipment & Fixed Assets",
        "caption": "Manage plant machinery, office computers, IT servers, and company vehicles across Tay Ninh and Hai Phong plants.",
        "tab_list": "📑 Assets Overview & Depreciation",
        "tab_add": "➕ Register New Asset",
        "metric_total": "Total Registered Assets",
        "metric_cost": "Total Acquisition Cost",
        "metric_sites": "Covered Plant Locations",
        "sites_val": "Tay Ninh Plant, Hai Phong Plant",
        "table_header": "📋 Plant Fixed Assets & Equipment Registry",
        "no_records": "No asset records found.",
        "add_header": "➕ Register New Plant Asset",
        "lbl_code": "Asset ID *",
        "lbl_name": "Asset Name *",
        "name_placeholder": "Example: CNC Copper Busbar Bending Machine",
        "lbl_category": "Asset Category *",
        "cat_opts": ["Production & Machining Equipment", "Desktop Computers & IT", "Laptops & Mobile Devices", "Company Vehicles & Transport", "Testing Instruments"],
        "lbl_site": "Plant Location *",
        "site_opts": ["Tay Ninh Plant", "Hai Phong Plant", "Taiwan HQ"],
        "lbl_brand": "Brand & Model",
        "lbl_barcode": "Asset Barcode / Tag",
        "lbl_status": "Current Status *",
        "status_opts": ["In Use", "Under Maintenance", "Idle / Backup", "Disposed"],
        "lbl_cost": "Acquisition Cost (USD) *",
        "btn_save": "💾 Save & Create Asset Record",
        "success_save": "✅ Asset `{asset_id}` successfully created!",
        "fill_warning": "⚠️ Please fill in Asset ID and Name!",
        # Table headers
        "col_index": "No.",
        "col_select": "Select",
        "col_id": "Asset ID",
        "col_name": "Asset Name",
        "col_cat": "Category",
        "col_site": "Plant",
        "col_brand": "Brand / Model",
        "col_barcode": "Barcode",
        "col_status": "Status",
        "col_cost": "Cost"
    }
}

# ----------------------------------------------------
# 🔄 智慧語意對照引擎 (資產名稱與廠區互轉)
# ----------------------------------------------------
def smart_translate_asset(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    
    val_lower = text_val.lower()

    # 廠區智慧對應
    if "西寧廠" in text_val or "tay ninh" in val_lower:
        if target_lang == "Tiếng Việt": return "Nhà máy Tây Ninh"
        elif target_lang == "English": return "Tay Ninh Plant"
        return "越南西寧廠"
    if "海防廠" in text_val or "hai phong" in val_lower:
        if target_lang == "Tiếng Việt": return "Nhà máy Hải Phòng"
        elif target_lang == "English": return "Hai Phong Plant"
        return "越南海防廠"

    # 資產狀態對應
    if "使用中" in text_val or "in use" in val_lower or "đang sử dụng" in val_lower:
        if target_lang == "Tiếng Việt": return "🟢 Đang sử dụng (In Use)"
        elif target_lang == "English": return "🟢 In Use"
        return "🟢 使用中 (In Use)"

    return text_val

def render_asset_management(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = ASSET_I18N.get(active_lang, ASSET_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化資產資料庫
    if "assets_db" not in st.session_state:
        st.session_state.assets_db = [
            {
                "id": "EQ-TN-001",
                "name": "CNC 數控母線排彎折加工機",
                "category": "生產與加工機具",
                "site": "越南西寧廠",
                "brand": "Amada - CNC Busbar 160T",
                "barcode": "-",
                "status": "使用中",
                "cost": 45000.0
            },
            {
                "id": "AST-PC-001",
                "name": "西寧廠財務主管辦公電腦",
                "category": "辦公電腦與IT設備",
                "site": "越南西寧廠",
                "brand": "Dell - OptiPlex 7090 i7",
                "barcode": "-",
                "status": "使用中",
                "cost": 1200.0
            },
            {
                "id": "AST-LAP-001",
                "name": "海防廠工程部攜帶式筆電",
                "category": "筆記型電腦與行動裝置",
                "site": "越南海防廠",
                "brand": "Apple - MacBook Pro 16 M3",
                "barcode": "-",
                "status": "使用中",
                "cost": 2200.0
            },
            {
                "id": "AST-CAR-001",
                "name": "西寧廠廠長商務公務車",
                "category": "公務車輛與運輸工具",
                "site": "越南西寧廠",
                "brand": "Toyota - Fortuner 2.8L",
                "barcode": "61A-888.66",
                "status": "使用中",
                "cost": 28000.0
            }
        ]

    tab_list, tab_add = st.tabs([L["tab_list"], L["tab_add"]])

    with tab_list:
        total_cost = sum([item["cost"] for item in st.session_state.assets_db])
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric(L["metric_total"], f"{len(st.session_state.assets_db)} 項")
        with c2: st.metric(L["metric_cost"], f"${total_cost:,.0f} USD")
        with c3: st.metric(L["metric_sites"], L["sites_val"])

        st.markdown(f"### {L['table_header']}")
        if st.session_state.assets_db:
            display_data = []
            for idx, item in enumerate(st.session_state.assets_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_id"]: item["id"],
                    L["col_name"]: item["name"],
                    L["col_cat"]: item["category"],
                    L["col_site"]: smart_translate_asset(item["site"], active_lang),
                    L["col_brand"]: item["brand"],
                    L["col_barcode"]: item["barcode"],
                    L["col_status"]: smart_translate_asset(item["status"], active_lang),
                    L["col_cost"]: f"${item['cost']:,.0f} USD"
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    with tab_add:
        st.markdown(f"### {L['add_header']}")
        with st.form("form_add_asset"):
            c1, c2 = st.columns(2)
            with c1:
                asset_id = st.text_input(L["lbl_code"], value="AST-HP-002")
                asset_name = st.text_input(L["lbl_name"], placeholder=L["name_placeholder"])
                category = st.selectbox(L["lbl_category"], L["cat_opts"])
                site = st.selectbox(L["lbl_site"], L["site_opts"])
            with c2:
                brand = st.text_input(L["lbl_brand"], value="HP / Dell / Schneider")
                barcode = st.text_input(L["lbl_barcode"], value="-")
                status = st.selectbox(L["lbl_status"], L["status_opts"])
                cost = st.number_input(L["lbl_cost"], min_value=0.0, value=1500.0, step=100.0)

            if st.form_submit_button(L["btn_save"], type="primary", use_container_width=True):
                if asset_id and asset_name:
                    st.session_state.assets_db.insert(0, {
                        "id": asset_id,
                        "name": asset_name,
                        "category": category,
                        "site": site,
                        "brand": brand,
                        "barcode": barcode,
                        "status": "使用中" if "使用" in status or "In Use" in status else status,
                        "cost": cost
                    })
                    st.success(L["success_save"].format(asset_id=asset_id))
                    st.rerun()
                else:
                    st.warning(L["fill_warning"])

def show(*args, **kwargs):
    render_asset_management(*args, **kwargs)

def main(*args, **kwargs):
    render_asset_management(*args, **kwargs)

def render_asset_management_page(*args, **kwargs):
    render_asset_management(*args, **kwargs)
