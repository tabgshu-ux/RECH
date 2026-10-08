import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 車輛維修保養模組多語系字典 (i18n)
# ----------------------------------------------------
VEHICLE_MAINT_I18N = {
    "繁體中文": {
        "title": "🛠️ 管理部 - 車輛維修保養與 Excel 批次匯入管理",
        "caption": "記錄廠區公務車與貨車之定期保養、維修項目、零件更換成本，並支援多 Sheet 車輛維修 Excel 智慧批次匯入（含自動多語系翻譯）。",
        "tab_list": "📑 車輛維修保養紀錄總表",
        "tab_import": "📥 Excel 批次匯入保養紀錄",
        "tab_add": "➕ 登記單筆維修保養",
        "table_header": "📋 廠區車輛維修與保養履歷清冊",
        "no_records": "目前無車輛維修保養紀錄。",
        "import_header": "📥 Excel 多車輛維修明細智慧批次匯入",
        "import_caption": "請上傳包含多個車輛分頁（Sheet）之越文維修保養 Excel 檔案（系統將自動解析車牌、金額並智慧轉譯多語系）。",
        "btn_upload": "選擇 Excel 檔案 (.xlsx / .xls)",
        "success_import": "✅ 成功匯入共 `{count}` 筆車輛維修保養明細紀錄！",
        "add_header": "➕ 登記新車輛維修與保養項目",
        "lbl_plate": "車牌號碼 *",
        "lbl_type": "維修保養類別 *",
        "type_opts": ["定期保養 ( 定期維護 )", "輪胎更換", "引擎與變速箱檢修", "電機與冷氣維修", "事故板金烤漆"],
        "lbl_cost": "維修費用 (VND) *",
        "lbl_desc": "維修細節與更換零件說明 *",
        "desc_placeholder": "例如: 更換機油、機油濾芯及煞車來令片",
        "lbl_date": "進廠維修日期 *",
        "btn_save": "💾 儲存維修保養紀錄",
        "success_save": "✅ 車輛 `{plate}` 維修紀錄已成功建立！",
        "fill_warning": "⚠️ 請完整填寫車牌號碼與維修說明！",
        "col_index": "STT",
        "col_plate": "車牌號碼",
        "col_type": "維修類別",
        "col_cost": "維修費用",
        "col_desc": "維修細節說明 (自動對應語系)",
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
        "import_caption": "Tải lên file Excel bảo dưỡng xe...",
        "btn_upload": "Chọn file Excel (.xlsx)",
        "success_import": "✅ Đã nhập thành công `{count}` bản ghi bảo trì xe!",
        "add_header": "➕ Đăng ký bảo dưỡng / sửa chữa xe mới",
        "lbl_plate": "Biển số xe *",
        "lbl_type": "Loại bảo dưỡng *",
        "type_opts": ["Bảo dưỡng định kỳ", "Thay lốp xe", "Sửa chữa động cơ / hộp số", "Sửa chữa điện / điều hòa", "Đồng sơn thân xe"],
        "lbl_cost": "Chi phí (VND) *",
        "lbl_desc": "Chi tiết sửa chữa & phụ tùng thay thế *",
        "desc_placeholder": "Ví dụ: Thay nhớt, lọc nhớt và bố thắng",
        "lbl_date": "Ngày vào xưởng *",
        "btn_save": "💾 Lưu bản ghi bảo trì",
        "success_save": "✅ Đã lưu lịch sử bảo trì cho xe `{plate}`!",
        "fill_warning": "⚠️ Vui lòng điền Biển số xe và Mô tả sửa chữa!",
        "col_index": "STT",
        "col_plate": "Biển số xe",
        "col_type": "Loại bảo trì",
        "col_cost": "Chi phí",
        "col_desc": "Chi tiết sửa chữa",
        "col_date": "Ngày vào"
    },
    "English": {
        "title": "🛠️ GA - Vehicle Maintenance & Excel Batch Import",
        "caption": "Track routine maintenance, repair items, and replacement parts costs for company vehicles.",
        "tab_list": "📑 Vehicle Maintenance Records",
        "tab_import": "📥 Excel Batch Import",
        "tab_add": "➕ Register New Maintenance",
        "table_header": "📋 Company Vehicle Maintenance Log",
        "no_records": "No vehicle maintenance records found.",
        "import_header": "📥 Excel Batch Import for Maintenance",
        "import_caption": "Upload an Excel file containing vehicle maintenance sheets.",
        "btn_upload": "Choose Excel File (.xlsx)",
        "success_import": "✅ Successfully imported `{count}` maintenance records!",
        "add_header": "➕ Register New Vehicle Maintenance",
        "lbl_plate": "License Plate *",
        "lbl_type": "Maintenance Type *",
        "type_opts": ["Routine Maintenance", "Tire Replacement", "Engine & Transmission Repair", "Electrical & AC Repair", "Body Paint & Panel"],
        "lbl_cost": "Cost (VND) *",
        "lbl_desc": "Repair Details & Parts Description *",
        "desc_placeholder": "Example: Engine oil change, oil filter and brake pads replacement",
        "lbl_date": "Maintenance Date *",
        "btn_save": "💾 Save Maintenance Record",
        "success_save": "✅ Maintenance record for vehicle `{plate}` saved successfully!",
        "fill_warning": "⚠️ Please fill in License Plate and Repair Details!",
        "col_index": "No.",
        "col_plate": "License Plate",
        "col_type": "Maintenance Type",
        "col_cost": "Cost",
        "col_desc": "Repair Details",
        "col_date": "Date"
    }
}

# ----------------------------------------------------
# 🔄 智慧語意與多語系即時翻譯字典
# ----------------------------------------------------
MAINT_TRANSLATIONS = {
    "bão dưỡng cấp 2": {
        "繁體中文": "二級定期保養",
        "Tiếng Việt": "Bảo dưỡng cấp 2",
        "English": "Level 2 Routine Maintenance"
    },
    "bão dưỡng": {
        "繁體中文": "定期保養維護",
        "Tiếng Việt": "Bảo dưỡng định kỳ",
        "English": "Routine Maintenance"
    },
    "thay vỏ": {
        "繁體中文": "更換輪胎/外胎",
        "Tiếng Việt": "Thay vỏ xe",
        "English": "Tire Replacement"
    },
    "sửa chữa": {
        "繁體中文": "綜合維修與零件更換",
        "Tiếng Việt": "Sửa chữa & Thay thế phụ tùng",
        "English": "General Repair & Parts Replacement"
    },
    "thay kính lái": {
        "繁體中文": "更換汽車前擋風玻璃",
        "Tiếng Việt": "Thay kính lái",
        "English": "Windshield Replacement"
    },
    "dán phim 3m r70": {
        "繁體中文": "貼 3M R70 隔熱膜",
        "Tiếng Việt": "Dán phim 3M R70",
        "English": "Install 3M R70 Window Film"
    }
}

def smart_translate(text, target_lang):
    if not text or not isinstance(text, str):
        return text
    t_lower = text.strip().lower()
    for key, trans in MAINT_TRANSLATIONS.items():
        if key in t_lower:
            return trans.get(target_lang, text)
    return text

def render_vehicle_maintenance_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = VEHICLE_MAINT_I18N.get(active_lang, VEHICLE_MAINT_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "vehicle_maint_db" not in st.session_state:
        st.session_state.vehicle_maint_db = [
            {
                "plate": "70LD-00606",
                "type": "bão dưỡng cấp 2",
                "cost": 378000.0,
                "desc": "công bão dưỡng (Thaco Gò Dầu)",
                "date": "2025-09-19"
            },
            {
                "plate": "70LD-00670",
                "type": "bão dưỡng",
                "cost": 178200.0,
                "desc": "công bão dưỡng (Honda Bình Dương)",
                "date": "2025-11-14"
            }
        ]

    tab_list, tab_import, tab_add = st.tabs([
        L["tab_list"], L["tab_import"], L["tab_add"]
    ])

    # 1. 列表總表（帶多語系即時轉換）
    with tab_list:
        st.markdown(f"### {L['table_header']}")
        if st.session_state.vehicle_maint_db:
            display_data = []
            for idx, item in enumerate(st.session_state.vehicle_maint_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_plate"]: item["plate"],
                    L["col_type"]: smart_translate(item["type"], active_lang),
                    L["col_cost"]: f"{item['cost']:,.0f} VND",
                    L["col_desc"]: smart_translate(item["desc"], active_lang),
                    L["col_date"]: item["date"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    # 2. 智慧批次匯入 Excel
    with tab_import:
        st.markdown(f"### {L['import_header']}")
        st.caption(L["import_caption"])
        uploaded_file = st.file_uploader(L["btn_upload"], type=["xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                xls = pd.ExcelFile(uploaded_file)
                st.info(f"📂 成功讀取 Excel 檔案，共發現 {len(xls.sheet_names)} 個車輛分頁 (Sheets): {', '.join(xls.sheet_names)}")
                
                if st.button("🚀 確認上傳並解析全部車輛明細", type="primary"):
                    imported_count = 0
                    new_records = []
                    
                    for sheet_name in xls.sheet_names:
                        df_raw = pd.read_excel(xls, sheet_name=sheet_name)
                        
                        header_row_idx = None
                        for r_idx in range(min(5, len(df_raw))):
                            row_str = str(df_raw.iloc[r_idx].values)
                            if "STT" in row_str or "NGÀY" in row_str or "TÊN DỊCH VỤ" in row_str:
                                header_row_idx = r_idx
                                break
                        
                        if header_row_idx is not None:
                            df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=header_row_idx+1)
                            df.columns = [str(c).strip().upper() for c in df.columns]
                        else:
                            df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=2)
                            df.columns = [str(c).strip().upper() for c in df.columns]
                        
                        plate_no = sheet_name.strip()
                        if not plate_no.startswith("70"):
                            plate_no = f"70LD-{plate_no}"
                        
                        date_col = next((c for c in df.columns if 'NGÀY' in c or 'DATE' in c), None)
                        type_col = next((c for c in df.columns if 'TÊN DỊCH VỤ' in c or 'TYPE' in c), None)
                        desc_col = next((c for c in df.columns if 'NỘI DUNG' in c or 'DESC' in c), None)
                        cost_col = next((c for c in df.columns if 'THÀNH TIỀN' in c or 'COST' in c or 'GIÁ' in c), None)
                        
                        for _, row in df.iterrows():
                            if type_col and pd.notna(row.get(type_col)):
                                d_val = str(row.get(date_col, ''))[:10] if date_col else str(datetime.date.today())
                                t_val = str(row.get(type_col, 'bảo dưỡng'))
                                desc_val = str(row.get(desc_col, '')) if desc_col else ''
                                
                                c_val = 0.0
                                if cost_col:
                                    try:
                                        c_val = float(row.get(cost_col, 0))
                                    except:
                                        c_val = 0.0
                                
                                new_records.append({
                                    "plate": plate_no,
                                    "type": t_val,
                                    "cost": c_val if c_val > 0 else 100000.0,
                                    "desc": desc_val,
                                    "date": d_val if len(d_val) == 10 else str(datetime.date.today())
                                })
                                imported_count += 1

                    if new_records:
                        st.session_state.vehicle_maint_db = new_records + st.session_state.vehicle_maint_db
                        st.success(L["success_import"].format(count=imported_count))
                        st.rerun()
                    else:
                        st.warning("⚠️ 未能在 Excel 中解析出有效的維修明細資料。")
            except Exception as e:
                st.error(f"❌ 檔案解析發生錯誤: {e}")

    # 3. 單筆登記
    with tab_add:
        st.markdown(f"### {L['add_header']}")
        with st.form("form_add_maint"):
            c1, c2 = st.columns(2)
            with c1:
                plate = st.text_input(L["lbl_plate"], value="70LD-00606")
                maint_type = st.selectbox(L["lbl_type"], L["type_opts"])
            with c2:
                cost = st.number_input(L["lbl_cost"], min_value=0.0, value=350000.0, step=50000.0)
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
