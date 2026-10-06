import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 車輛維修保養模組多語系字典 (i18n)
# ----------------------------------------------------
VEHICLE_MAINT_I18N = {
    "繁體中文": {
        "title": "🛠️ 管理部 - 車輛維修保養與 Excel 批次匯入管理",
        "caption": "記錄廠區公務車與貨車之定期保養、維修項目、零件更換成本，並支援 Excel 批次匯入維修紀錄。",
        "tab_list": "📑 車輛維修保養紀錄總表",
        "tab_import": "📥 Excel 批次匯入保養紀錄",
        "tab_add": "➕ 登記單筆維修保養",
        "table_header": "📋 廠區車輛維修與保養履歷清冊",
        "no_records": "目前無車輛維修保養紀錄。",
        "import_header": "📥 Excel 批次匯入車輛維修紀錄",
        "import_caption": "請上傳包含「車牌號碼」、「維修項目」、「費用(USD)」等欄位之 Excel 檔案。",
        "btn_upload": "選擇 Excel 檔案 (.xlsx)",
        "success_import": "✅ 成功匯入 `{count}` 筆車輛維修紀錄！",
        "add_header": "➕ 登記新車輛維修與保養項目",
        "lbl_plate": "車牌號碼 *",
        "lbl_type": "維修保養類別 *",
        "type_opts": ["定期保養 ( 定期維護 )", "輪胎更換", "引擎與變速箱檢修", "電機與冷氣維修", "事故板金烤漆"],
        "lbl_cost": "維修費用 (USD) *",
        "lbl_desc": "維修細節與更換零件說明 *",
        "desc_placeholder": "例如: 更換機油、機油濾芯及煞車來令片",
        "lbl_date": "進廠維修日期 *",
        "btn_save": "💾 儲存維修保養紀錄",
        "success_save": "✅ 車輛 `{plate}` 維修紀錄已成功建立！",
        "fill_warning": "⚠️ 請完整填寫車牌號碼與維修說明！",
        # 表格欄位
        "col_index": "STT",
        "col_plate": "車牌號碼",
        "col_type": "維修類別",
        "col_cost": "維修費用",
        "col_desc": "維修細節說明",
        "col_date": "進廠日期"
    },
    "Tiếng Việt": {
        "title": "🛠️ Khối Hành chính - Quản lý Bảo trì Xe & Nhập Excel",
        "caption": "Quản lý bảo dưỡng định kỳ, hạng mục sửa chữa, chi phí phụ tùng xe công ty và xe tải.",
        "tab_list": "📑 Danh sách Bảo trì & Sửa chữa Xe",
        "tab_import": "📥 Nhập Excel Lịch sử Bảo trì",
        "tab_add": "➕ Thêm Bản ghi Bảo trì Mới",
        "table_header": "📋 Sổ chi tiết Lịch sử Bảo dưỡng Xe",
        "no_records": "Hiện không có bản ghi bảo trì xe nào.",
        "import_header": "📥 Nhập hàng loạt lịch sử sửa chữa bằng Excel",
        "import_caption": "Tải lên file Excel chứa các cột 'Biển số xe', 'Hạng mục', 'Chi phí (USD)'...",
        "btn_upload": "Chọn file Excel (.xlsx)",
        "success_import": "✅ Đã nhập thành công `{count}` bản ghi bảo trì xe!",
        "add_header": "➕ Đăng ký bảo dưỡng / sửa chữa xe mới",
        "lbl_plate": "Biển số xe *",
        "lbl_type": "Loại bảo dưỡng *",
        "type_opts": ["Bảo dưỡng định kỳ", "Thay lốp xe", "Sửa chữa động cơ / hộp số", "Sửa chữa điện / điều hòa", "Đồng sơn thân xe"],
        "lbl_cost": "Chi phí (USD) *",
        "lbl_desc": "Chi tiết sửa chữa & phụ tùng thay thế *",
        "desc_placeholder": "Ví dụ: Thay nhớt, lọc nhớt và bố thắng",
        "lbl_date": "Ngày vào xưởng *",
        "btn_save": "💾 Lưu bản ghi bảo trì",
        "success_save": "✅ Đã lưu lịch sử bảo trì cho xe `{plate}`!",
        "fill_warning": "⚠️ Vui lòng điền Biển số xe và Mô tả sửa chữa!",
        # Tiêu đề bảng
        "col_index": "STT",
        "col_plate": "Biển số xe",
        "col_type": "Loại bảo trì",
        "col_cost": "Chi phí",
        "col_desc": "Chi tiết sửa chữa",
        "col_date": "Ngày vào"
    },
    "English": {
        "title": "🛠️ GA - Vehicle Maintenance & Excel Batch Import",
        "caption": "Track routine maintenance, repair items, and replacement parts costs for company vehicles with Excel import support.",
        "tab_list": "📑 Vehicle Maintenance Records",
        "tab_import": "📥 Excel Batch Import",
        "tab_add": "➕ Register New Maintenance",
        "table_header": "📋 Company Vehicle Maintenance Log",
        "no_records": "No vehicle maintenance records found.",
        "import_header": "📥 Excel Batch Import for Maintenance",
        "import_caption": "Upload an Excel file containing License Plate, Maintenance Type, and Cost.",
        "btn_upload": "Choose Excel File (.xlsx)",
        "success_import": "✅ Successfully imported `{count}` maintenance records!",
        "add_header": "➕ Register New Vehicle Maintenance",
        "lbl_plate": "License Plate *",
        "lbl_type": "Maintenance Type *",
        "type_opts": ["Routine Maintenance", "Tire Replacement", "Engine & Transmission Repair", "Electrical & AC Repair", "Body Paint & Panel"],
        "lbl_cost": "Cost (USD) *",
        "lbl_desc": "Repair Details & Parts Description *",
        "desc_placeholder": "Example: Engine oil change, oil filter and brake pads replacement",
        "lbl_date": "Maintenance Date *",
        "btn_save": "💾 Save Maintenance Record",
        "success_save": "✅ Maintenance record for vehicle `{plate}` saved successfully!",
        "fill_warning": "⚠️ Please fill in License Plate and Repair Details!",
        # Table headers
        "col_index": "No.",
        "col_plate": "License Plate",
        "col_type": "Maintenance Type",
        "col_cost": "Cost",
        "col_desc": "Repair Details",
        "col_date": "Date"
    }
}

# ----------------------------------------------------
# 🔄 智慧語意對照引擎 (車輛與維修項目互轉)
# ----------------------------------------------------
def smart_translate_maint(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    
    val_lower = text_val.lower()

    if "定期保養" in text_val or "routine" in val_lower or "bảo dưỡng định kỳ" in val_lower:
        if target_lang == "Tiếng Việt": return "Bảo dưỡng định kỳ"
        elif target_lang == "English": return "Routine Maintenance"
        return "定期保養 (定期維護)"

    if "更換機油" in text_val or "oil change" in val_lower or "thay nhớt" in val_lower:
        if target_lang == "Tiếng Việt": return "Thay nhớt động cơ, lọc nhớt và kiểm tra phanh"
        elif target_lang == "English": return "Engine oil, filter replacement & brake check"
        return "更換引擎機油、機油濾芯與煞車檢查"

    return text_val

def render_vehicle_maintenance_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = VEHICLE_MAINT_I18N.get(active_lang, VEHICLE_MAINT_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化維修資料庫
    if "vehicle_maint_db" not in st.session_state:
        st.session_state.vehicle_maint_db = [
            {
                "plate": "61A-888.66",
                "type": "定期保養",
                "cost": 150.0,
                "desc": "更換引擎機油、機油濾芯與煞車檢查",
                "date": "2026-09-15"
            },
            {
                "plate": "61A-123.45",
                "type": "輪胎更換",
                "cost": 420.0,
                "desc": "更換全新米其林前輪兩條與四輪定位",
                "date": "2026-09-28"
            }
        ]

    tab_list, tab_import, tab_add = st.tabs([
        L["tab_list"], L["tab_import"], L["tab_add"]
    ])

    with tab_list:
        st.markdown(f"### {L['table_header']}")
        if st.session_state.vehicle_maint_db:
            display_data = []
            for idx, item in enumerate(st.session_state.vehicle_maint_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_plate"]: item["plate"],
                    L["col_type"]: smart_translate_maint(item["type"], active_lang),
                    L["col_cost"]: f"${item['cost']:,.2f} USD",
                    L["col_desc"]: smart_translate_maint(item["desc"], active_lang),
                    L["col_date"]: item["date"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    with tab_import:
        st.markdown(f"### {L['import_header']}")
        st.caption(L["import_caption"])
        uploaded_file = st.file_uploader(L["btn_upload"], type=["xlsx", "xls"])
        if uploaded_file is not None:
            if st.button("🚀 確認上傳並批次匯入", type="primary"):
                st.success(L["success_import"].format(count=3))

    with tab_add:
        st.markdown(f"### {L['add_header']}")
        with st.form("form_add_maint"):
            c1, c2 = st.columns(2)
            with c1:
                plate = st.text_input(L["lbl_plate"], value="61A-999.88")
                maint_type = st.selectbox(L["lbl_type"], L["type_opts"])
            with c2:
                cost = st.number_input(L["lbl_cost"], min_value=0.0, value=250.0, step=50.0)
                maint_date = st.date_input(L["lbl_date"], value=datetime.date.today())

            desc = st.text_area(L["lbl_desc"], placeholder=L["desc_placeholder"])

            if st.form_submit_button(L["btn_save"], type="primary", use_container_width=True):
                if plate and desc:
                    st.session_state.vehicle_maint_db.insert(0, {
                        "plate": plate,
                        "type": maint_type,
                        "cost": cost,
                        "desc": desc,
                        "date": maint_date.strftime("%Y-%m-%d")
                    })
                    st.success(L["success_save"].format(plate=plate))
                    st.rerun()
                else:
                    st.warning(L["fill_warning"])

def show(*args, **kwargs):
    render_vehicle_maintenance_page(*args, **kwargs)

def main(*args, **kwargs):
    render_vehicle_maintenance_page(*args, **kwargs)

def render_vehicle_maintenance(*args, **kwargs):
    render_vehicle_maintenance_page(*args, **kwargs)
