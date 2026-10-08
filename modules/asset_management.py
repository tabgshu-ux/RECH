import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 固定資產模組多語系字典 (i18n)
# ----------------------------------------------------
ASSET_I18N = {
    "繁體中文": {
        "title": "🏭 裕豐電機工業 - 生產設備與固定資產管理系統",
        "caption": "管理西寧廠/海防廠生產機械設備、辦公個人電腦、行動式筆電與公務車輛/使用車輛之完整資產生命週期。",
        "tab_list": "📑 資產總表與分類檢視",
        "tab_add": "➕ 新增固定資產與設備",
        "tab_edit": "✏️ 修改資產資料",
        "tab_delete": "🗑️ 刪除或報廢資產",
        "table_header": "📋 廠區固定資產與設備分類清冊",
        "cat_all": "🌐 全部資產 (All Assets)",
        "cat_prod": "🏭 生產部設備 (Machinery)",
        "cat_car": "🚗 車輛設備 (Vehicles)",
        "cat_it": "💻 電腦與辦公設備 (IT & Office)",
        "lbl_code": "資產編號 (Asset Code) *",
        "lbl_name": "資產名稱 (Asset Name) *",
        "lbl_category": "品項分類 (Category) *",
        "cat_opts": ["生產與加工機具 (Machinery)", "車輛設備 (Vehicle)", "個人電腦 (Desktop PC)", "筆記型電腦 (Laptop)", "辦公家具與設備 (Office)"],
        "lbl_factory": "存放廠區 (Plant Location) *",
        "factory_opts": ["越南西寧廠 (Tay Ninh)", "越南海防廠 (Hai Phong)"],
        "lbl_brand": "品牌與型號 (Brand & Model)",
        "lbl_plate": "車牌號碼 (若為車輛必填)",
        "lbl_status": "目前狀態 (Status) *",
        "status_opts": ["🟢 在用 (Active)", "🟡 維修中 (Maintenance)", "🔴 報廢/停用 (Disposed)"],
        "lbl_cost": "取得成本 (Cost in USD) *",
        "btn_add": "🚀 確認新增固定資產",
        "success_add": "✅ 成功新增固定資產 `{name}` (編號: `{code}`)！",
        "btn_save_edit": "💾 儲存修改後資產資料",
        "success_edit": "✅ 資產 `{code}` 資料已成功更新！",
        "btn_delete": "🔥 確認刪除或報廢選定資產",
        "success_delete": "✅ 已成功刪除選定的固定資產記錄。",
        "col_index": "STT",
        "col_code": "資產編號",
        "col_name": "資產名稱",
        "col_category": "類別",
        "col_factory": "存放廠區",
        "col_brand": "品牌型號",
        "col_plate": "車牌號碼",
        "col_status": "狀態",
        "col_cost": "取得成本"
    },
    "Tiếng Việt": {
        "title": "🏭 Quản lý Tài sản Cố định & Thiết bị",
        "caption": "Quản lý máy móc sản xuất, máy tính, xe ô tô và thiết bị văn phòng.",
        "tab_list": "📑 Danh sách & Phân loại tài sản",
        "tab_add": "➕ Thêm tài sản mới",
        "tab_edit": "✏️ Sửa thông tin",
        "tab_delete": "🗑️ Xóa / Thanh lý tài sản",
        "table_header": "📋 Danh mục Tài sản Cố định theo phân loại",
        "cat_all": "🌐 Tất cả tài sản",
        "cat_prod": "🏭 Máy móc sản xuất",
        "cat_car": "🚗 Xe cộ",
        "cat_it": "💻 Máy tính & Văn phòng",
        "lbl_code": "Mã tài sản *",
        "lbl_name": "Tên tài sản *",
        "lbl_category": "Phân loại *",
        "cat_opts": ["Máy móc sản xuất", "Thiết bị xe", "Máy tính để bàn", "Laptop", "Thiết bị văn phòng"],
        "lbl_factory": "Nhà máy lưu trữ *",
        "factory_opts": ["Nhà máy Tây Ninh", "Nhà máy Hải Phòng"],
        "lbl_brand": "Thương hiệu & Model",
        "lbl_plate": "Biển số xe",
        "lbl_status": "Trạng thái *",
        "status_opts": ["🟢 Đang sử dụng", "🟡 Đang bảo trì", "🔴 Đã thanh lý"],
        "lbl_cost": "Nguyên giá (USD) *",
        "btn_add": "🚀 Thêm tài sản",
        "success_add": "✅ Đã thêm tài sản `{name}` thành công!",
        "btn_save_edit": "💾 Lưu thay đổi",
        "success_edit": "✅ Đã cập nhật thành công!",
        "btn_delete": "🔥 Xóa tài sản",
        "success_delete": "✅ Đã xóa thành công.",
        "col_index": "STT",
        "col_code": "Mã TS",
        "col_name": "Tên tài sản",
        "col_category": "Phân loại",
        "col_factory": "Nhà máy",
        "col_brand": "Brand/Model",
        "col_plate": "Biển số",
        "col_status": "Trạng thái",
        "col_cost": "Chi phí"
    },
    "English": {
        "title": "🏭 Fixed Assets & Equipment Management",
        "caption": "Manage production machinery, computers, vehicles, and office equipment lifecycle.",
        "tab_list": "📑 Asset Directory & Categories",
        "tab_import": "📥 Batch Import",
        "tab_add": "➕ Add New Asset",
        "tab_edit": "✏️ Edit Asset",
        "tab_delete": "🗑️ Delete / Dispose",
        "table_header": "📋 Fixed Asset Directory by Category",
        "cat_all": "🌐 All Assets",
        "cat_prod": "🏭 Machinery",
        "cat_car": "🚗 Vehicles",
        "cat_it": "💻 IT & Office",
        "lbl_code": "Asset Code *",
        "lbl_name": "Asset Name *",
        "lbl_category": "Category *",
        "cat_opts": ["Machinery & Equipment", "Vehicle", "Desktop PC", "Laptop", "Office Equipment"],
        "lbl_factory": "Plant Location *",
        "factory_opts": ["Tay Ninh Plant", "Hai Phong Plant"],
        "lbl_brand": "Brand & Model",
        "lbl_plate": "License Plate (If vehicle)",
        "lbl_status": "Status *",
        "status_opts": ["🟢 Active", "🟡 Maintenance", "🔴 Disposed"],
        "lbl_cost": "Acquisition Cost (USD) *",
        "btn_add": "🚀 Confirm Add Asset",
        "success_add": "✅ Successfully added asset `{name}`!",
        "btn_save_edit": "💾 Save Changes",
        "success_edit": "✅ Asset updated successfully!",
        "btn_delete": "🔥 Permanently Delete / Dispose",
        "success_delete": "✅ Asset record deleted.",
        "col_index": "No.",
        "col_code": "Asset Code",
        "col_name": "Name",
        "col_category": "Category",
        "col_factory": "Plant",
        "col_brand": "Brand/Model",
        "col_plate": "Plate",
        "col_status": "Status",
        "col_cost": "Cost"
    }
}

def render_asset_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = ASSET_I18N.get(active_lang, ASSET_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化固定資產資料庫 (若無則建立預設值)
    if "asset_db" not in st.session_state:
        st.session_state.asset_db = [
            {
                "資產編號": "EQ-TN-001",
                "資產名稱": "CNC 數控母線銅排彎折加工機",
                "類別": "生產與加工機具 (Machinery)",
                "存放廠區": "越南西寧廠 (Tay Ninh)",
                "品牌型號": "Amada - CNC Busbar 160T",
                "車牌號碼": "-",
                "目前狀態": "🟢 在用 (Active)",
                "取得成本": 45000.0
            },
            {
                "資產編號": "AST-PC-001",
                "資產名稱": "西寧廠財務主管辦公電腦",
                "類別": "個人電腦 (Desktop PC)",
                "存放廠區": "越南西寧廠 (Tay Ninh)",
                "品牌型號": "Dell - OptiPlex 7090 i7",
                "車牌號碼": "-",
                "目前狀態": "🟢 在用 (Active)",
                "取得成本": 1200.0
            },
            {
                "資產編號": "AST-CAR-001",
                "資產名稱": "西寧廠廠長商務公務車",
                "類別": "車輛設備 (Vehicle)",
                "存放廠區": "越南西寧廠 (Tay Ninh)",
                "品牌型號": "Toyota - Fortuner 2.8L",
                "車牌號碼": "61A-888.66",
                "目前狀態": "🟢 在用 (Active)",
                "取得成本": 28000.0
            }
        ]

    # 🛡️ 欄位相容防護：確保現有 session 資料都有標準欄位，避免 KeyError
    for asset in st.session_state.asset_db:
        if "存放廠區" not in asset:
            asset["存放廠區"] = asset.get("廠區", asset.get("位置", "越南西寧廠"))
        if "類別" not in asset:
            asset["類別"] = asset.get("資產類別", "生產與加工機具 (Machinery)")
        if "目前狀態" not in asset:
            asset["目前狀態"] = asset.get("狀態", "🟢 在用 (Active)")
        if "取得成本" not in asset:
            asset["取得成本"] = asset.get("成本", 0.0)

    # 頂部統計指標
    total_assets = len(st.session_state.asset_db)
    total_cost = sum([float(a.get("取得成本", 0)) for a in st.session_state.asset_db])
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("總登記資產數 (Total Assets)", f"{total_assets} 項")
    with col_m2:
        st.metric("總取得成本 (Total Cost)", f"${total_cost:,.2f} USD")
    with col_m3:
        st.metric("覆蓋廠區據點 (Plants)", "越南西寧廠、越南海防廠")

    st.markdown("---")

    # 建立頁籤
    tab_list, tab_add, tab_edit, tab_delete = st.tabs([
        L["tab_list"], L["tab_add"], L["tab_edit"], L["tab_delete"]
    ])

    # 1. 📑 資產總表與分類檢視
    with tab_list:
        st.markdown(f"### {L['table_header']}")
        
        cat_tab_all, cat_tab_prod, cat_tab_car, cat_tab_it = st.tabs([
            L["cat_all"], L["cat_prod"], L["cat_car"], L["cat_it"]
        ])

        def display_asset_table(filtered_data):
            if filtered_data:
                display_list = []
                for idx, asset in enumerate(filtered_data, 1):
                    display_list.append({
                        L["col_index"]: idx,
                        L["col_code"]: asset.get("資產編號", "-"),
                        L["col_name"]: asset.get("資產名稱", "-"),
                        L["col_category"]: asset.get("類別", "-"),
                        L["col_factory"]: asset.get("存放廠區", "-"),
                        L["col_brand"]: asset.get("品牌型號", "-"),
                        L["col_plate"]: asset.get("車牌號碼", "-"),
                        L["col_status"]: asset.get("目前狀態", "-"),
                        L["col_cost"]: f"${float(asset.get('取得成本', 0)):,.2f} USD"
                    })
                st.dataframe(pd.DataFrame(display_list), use_container_width=True)
            else:
                st.info("目前此分類中尚無固定資產記錄。")

        with cat_tab_all:
            display_asset_table(st.session_state.asset_db)

        with cat_tab_prod:
            prod_data = [a for a in st.session_state.asset_db if "生產" in str(a.get("類別", "")) or "Machinery" in str(a.get("類別", "")) or "機具" in str(a.get("類別", ""))]
            display_asset_table(prod_data)

        with cat_tab_car:
            car_data = [a for a in st.session_state.asset_db if "車輛" in str(a.get("類別", "")) or "Vehicle" in str(a.get("類別", "")) or "車" in str(a.get("類別", ""))]
            display_asset_table(car_data)

        with cat_tab_it:
            it_data = [a for a in st.session_state.asset_db if any(k in str(a.get("類別", "")) for k in ["電腦", "筆電", "PC", "Laptop", "Office", "辦公"])]
            display_asset_table(it_data)

    # 2. ➕ 新增固定資產
    with tab_add:
        st.markdown(f"### {L['tab_add']}")
        auto_code = f"AST-EQ-{len(st.session_state.asset_db) + 1:03d}"

        with st.form("form_add_asset"):
            c1, c2 = st.columns(2)
            with c1:
                a_code = st.text_input(L["lbl_code"], value=auto_code)
                a_name = st.text_input(L["lbl_name"])
                a_cat = st.selectbox(L["lbl_category"], L["cat_opts"])
                a_factory = st.selectbox(L["lbl_factory"], L["factory_opts"])
            with c2:
                a_brand = st.text_input(L["lbl_brand"], placeholder="例如: Dell OptiPlex / Amada / Toyota")
                a_plate = st.text_input(L["lbl_plate"], value="-")
                a_status = st.selectbox(L["lbl_status"], L["status_opts"])
                a_cost = st.number_input(L["lbl_cost"], min_value=0.0, value=1500.0, step=100.0)

            submitted = st.form_submit_button(L["btn_add"], type="primary", use_container_width=True)
            if submitted:
                if a_code and a_name:
                    existing_codes = [a["資產編號"] for a in st.session_state.asset_db]
                    if a_code in existing_codes:
                        st.error(f"⚠️ 錯誤：資產編號 `{a_code}` 已經存在！")
                    else:
                        st.session_state.asset_db.append({
                            "資產編號": a_code,
                            "資產名稱": a_name,
                            "類別": a_cat,
                            "存放廠區": a_factory,
                            "品牌型號": a_brand if a_brand else "-",
                            "車牌號碼": a_plate if a_plate else "-",
                            "目前狀態": a_status,
                            "取得成本": a_cost
                        })
                        st.success(L["success_add"].format(name=a_name, code=a_code))
                        st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫資產編號與資產名稱！")

    # 3. ✏️ 修改資產資料
    with tab_edit:
        st.markdown(f"### {L['tab_edit']}")
        if st.session_state.asset_db:
            asset_options = {f"{a.get('資產編號', '')} - {a.get('資產名稱', '')} ({a.get('類別', '')})": a for a in st.session_state.asset_db}
            sel_edit_key = st.selectbox("選擇要修改的資產 (Select Asset to Edit)", list(asset_options.keys()))
            target_asset = asset_options[sel_edit_key]

            with st.form("form_edit_asset"):
                ed_name = st.text_input(L["lbl_name"], value=target_asset.get("資產名稱", ""))
                
                curr_cat = target_asset.get("類別", L["cat_opts"][0])
                cat_idx = L["cat_opts"].index(curr_cat) if curr_cat in L["cat_opts"] else 0
                ed_cat = st.selectbox(L["lbl_category"], L["cat_opts"], index=cat_idx)
                
                ed_brand = st.text_input(L["lbl_brand"], value=target_asset.get("品牌型號", "-"))
                ed_plate = st.text_input(L["lbl_plate"], value=target_asset.get("車牌號碼", "-"))
                
                curr_status = target_asset.get("目前狀態", L["status_opts"][0])
                status_idx = L["status_opts"].index(curr_status) if curr_status in L["status_opts"] else 0
                ed_status = st.selectbox(L["lbl_status"], L["status_opts"], index=status_idx)
                
                ed_cost = st.number_input(L["lbl_cost"], min_value=0.0, value=float(target_asset.get("取得成本", 0)), step=100.0)

                if st.form_submit_button(L["btn_save_edit"], type="primary", use_container_width=True):
                    target_asset["資產名稱"] = ed_name
                    target_asset["類別"] = ed_cat
                    target_asset["品牌型號"] = ed_brand
                    target_asset["車牌號碼"] = ed_plate
                    target_asset["目前狀態"] = ed_status
                    target_asset["取得成本"] = ed_cost
                    st.success(L["success_edit"].format(code=target_asset.get("資產編號", "")))
                    st.rerun()
        else:
            st.info("目前無固定資產可供修改。")

    # 4. 🗑️ 刪除或報廢資產
    with tab_delete:
        st.markdown(f"### {L['tab_delete']}")
        if st.session_state.asset_db:
            del_options = {f"{a.get('資產編號', '')} - {a.get('資產名稱', '')} ({a.get('存放廠區', '')})": a for a in st.session_state.asset_db}
            sel_del_key = st.selectbox("選擇要刪除或報廢的資產", list(del_options.keys()))
            target_del = del_options[sel_del_key]

            st.warning(f"⚠️ 您確定要刪除或報廢資產 **{target_del.get('資產編號', '')} - {target_del.get('資產名稱', '')}** 嗎？此動作無法復原。")
            
            if st.button(L["btn_delete"], type="primary"):
                target_code = target_del.get("資產編號", "")
                st.session_state.asset_db = [a for a in st.session_state.asset_db if a.get("資產編號", "") != target_code]
                st.success(L["success_delete"])
                st.rerun()
        else:
            st.info("目前系統中無任何資產記錄可供刪除。")

def show(*args, **kwargs):
    render_asset_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_asset_management_page(*args, **kwargs)

def render_asset_management(*args, **kwargs):
    render_asset_management_page(*args, **kwargs)
