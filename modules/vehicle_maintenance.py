import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 車輛維修保養模組多語系字典 (i18n)
# ----------------------------------------------------
VEHICLE_MAINT_I18N = {
    "繁體中文": {
        "title": "🛠️ 管理部 - 車輛維修保養與 Excel 批次匯入管理",
        "caption": "記錄廠區公務車與貨車之定期保養、維修項目、零件更換成本，支援依車號分組篩選，並自動同步至固定資產模組。",
        "tab_list": "📑 依車號分組之維修保養總表",
        "tab_import": "📥 Excel 批次匯入與自動資產建檔",
        "tab_add": "➕ 登記單筆維修保養",
        "table_header": "📋 各車號專屬維修與保養履歷清冊",
        "no_records": "目前無車輛維修保養紀錄。",
        "import_header": "📥 Excel 多車輛維修明細智慧批次匯入",
        "import_caption": "上傳 Excel 後，系統將自動解析各車牌與維修明細，進行完整專業中文化翻譯，並自動同步新增至固定資產中的車輛資產。",
        "btn_upload": "選擇 Excel 檔案 (.xlsx / .xls)",
        "success_import": "✅ 成功匯入共 `{count}` 筆維修明細，並已自動同步車輛至固定資產清單！",
        "add_header": "➕ 登記新車輛維修與保養項目",
        "lbl_plate": "車牌號碼 *",
        "lbl_type": "維修保養類別 *",
        "type_opts": ["定期保養 ( 定期維護 )", "輪胎更換", "引擎與變速箱檢修", "電機與冷氣維修", "事故板金烤漆"],
        "lbl_cost": "維修費用 (VND) *",
        "lbl_desc": "維修細節與更換零件說明 *",
        "desc_placeholder": "例如: 更換機油、機油濾芯及煞車來令片",
        "lbl_date": "進廠維修日期 *",
        "btn_save": "💾 儲存維修保養紀錄",
        "success_save": "✅ 車輛 `{plate}` 維修紀錄已成功建立，並已自動連動至固定資產！",
        "fill_warning": "⚠️ 請完整填寫車牌號碼與維修說明！",
        "col_index": "STT",
        "col_plate": "車牌號碼",
        "col_type": "維修類別",
        "col_cost": "維修費用",
        "col_desc": "維修細節與零件說明",
        "col_date": "進廠日期"
    },
    "Tiếng Việt": {
        "title": "🛠️ Quản lý Bảo trì Xe & Nhập Excel",
        "caption": "Quản lý bảo dưỡng, lịch sử sửa chữa theo biển số xe, tự động đồng bộ sang Tài sản cố định.",
        "tab_list": "📑 Danh sách theo Biển số xe",
        "tab_import": "📥 Nhập Excel & Đồng bộ tài sản",
        "tab_add": "➕ Thêm Bản ghi Mới",
        "table_header": "📋 Sổ chi tiết Lịch sử Bảo dưỡng theo xe",
        "no_records": "Hiện không có bản ghi nào.",
        "import_header": "📥 Nhập Excel hàng loạt",
        "import_caption": "Hệ thống sẽ tự động thêm xe vào Tài sản cố định nếu chưa có.",
        "btn_upload": "Chọn file Excel (.xlsx)",
        "success_import": "✅ Đã nhập thành công `{count}` bản ghi và đồng bộ tài sản!",
        "add_header": "➕ Đăng ký bảo dưỡng mới",
        "lbl_plate": "Biển số xe *",
        "lbl_type": "Loại bảo dưỡng *",
        "type_opts": ["Bảo dưỡng định kỳ", "Thay lốp xe", "Sửa chữa động cơ", "Sửa chữa điện", "Đồng sơn"],
        "lbl_cost": "Chi phí (VND) *",
        "lbl_desc": "Chi tiết sửa chữa *",
        "desc_placeholder": "Ví dụ: Thay nhớt, lọc nhớt",
        "lbl_date": "Ngày vào xưởng *",
        "btn_save": "💾 Lưu bản ghi",
        "success_save": "✅ Đã lưu lịch sử cho xe `{plate}` và đồng bộ tài sản!",
        "fill_warning": "⚠️ Vui lòng điền đầy đủ thông tin!",
        "col_index": "STT",
        "col_plate": "Biển số xe",
        "col_type": "Loại bảo trì",
        "col_cost": "Chi phí",
        "col_desc": "Chi tiết sửa chữa",
        "col_date": "Ngày vào"
    },
    "English": {
        "title": "🛠️ Vehicle Maintenance & Excel Batch Import",
        "caption": "Track vehicle maintenance grouped by license plate, with automatic Fixed Asset synchronization.",
        "tab_list": "📑 Maintenance by Plate",
        "tab_import": "📥 Excel Import & Asset Sync",
        "tab_add": "➕ Register Maintenance",
        "table_header": "📋 Vehicle Maintenance Log by Plate",
        "no_records": "No records found.",
        "import_header": "📥 Excel Batch Import",
        "import_caption": "Automatically syncs vehicles to Fixed Assets module upon import.",
        "btn_upload": "Choose Excel File (.xlsx)",
        "success_import": "✅ Successfully imported `{count}` records and synced to assets!",
        "add_header": "➕ Register New Maintenance",
        "lbl_plate": "License Plate *",
        "lbl_type": "Maintenance Type *",
        "type_opts": ["Routine Maintenance", "Tire Replacement", "Engine Repair", "Electrical Repair", "Body Paint"],
        "lbl_cost": "Cost (VND) *",
        "lbl_desc": "Repair Details *",
        "desc_placeholder": "Example: Engine oil change",
        "lbl_date": "Maintenance Date *",
        "btn_save": "💾 Save Record",
        "success_save": "✅ Maintenance record for `{plate}` saved & synced to assets!",
        "fill_warning": "⚠️ Please fill in all required fields!",
        "col_index": "No.",
        "col_plate": "License Plate",
        "col_type": "Maintenance Type",
        "col_cost": "Cost",
        "col_desc": "Repair Details",
        "col_date": "Date"
    }
}

# ----------------------------------------------------
# 🔄 全方位車輛維修與零件專用對照翻譯庫
# ----------------------------------------------------
MAINT_TRANSLATIONS = {
    # 類別與服務項目
    "bão dưỡng cấp 2": "二級定期保養",
    "bão dưỡng cấp nhỏ": "小型定期保養",
    "bão dưỡng cấp trung bình": "中型定期保養",
    "bão dưỡng cấp lớn": "大型定期保養",
    "bão dưỡng": "定期保養維護",
    "thay vỏ": "更換輪胎/外胎",
    "thay vỏ xe": "更換輪胎",
    "sửa chữa, bảo dưỡng": "綜合維修與保養",
    "sửa chữa bảo dưỡng": "綜合維修與保養",
    "sửa chữa": "綜合維修與零件更換",
    "sữa chữa": "綜合維修與零件更換",
    "thay kính lái": "更換汽車前擋風玻璃",
    "dán phim 3m r70": "貼 3M R70 隔熱膜",
    "bảo dưỡng thay dàn nóng": "更換並保養冷凝器(散熱排)",
    "mua bảo hiểm": "購買車輛保險",
    "thay công tắc mở cốp": "更換後車箱開關",
    "thay gạt mưa": "更換雨刷",
    "thay pin chìa khóa": "更換遙控鑰匙電池",
    "thay sim": "更換通訊SIM卡",
    "thay đèn": "更換車燈總成",
    "đánh bóng": "車身拋光美容",
    "đăng kiểm": "車輛定期檢驗 (驗車)",
    "may bạt xe": "訂製/更換貨車帆布雨蓬",
    "kiểm tra tiếng kêu": "底盤/異音檢修",
    "gia hạn": "合約/服務延期",
    "ok": "一般檢修確認完畢",

    # 常見零件與工項細節
    "công bão dưỡng": "保養人工工資",
    "thay dây curoa": "更換發電機/冷氣皮帶",
    "dây cua roa": "傳動皮帶",
    "dây curoa": "傳動皮帶",
    "bơm nước": "水箱幫浦",
    "máy phát": "發電機",
    "lóc lạnh": "冷氣壓縮機",
    "lọc nhớt": "機油濾清器 (濾心)",
    "thay lọc nhớt": "更換機油濾清器",
    "lọc dầu tinh": "精細柴油濾清器",
    "lọc dầu": "柴油/機油濾清器",
    "lọc gió": "空氣濾清器",
    "lọc nhiên liệu": "燃料濾清器",
    "lọc khí": "冷氣/空氣濾網",
    "nhớt máy dầu cao cấp": "高級柴油機油",
    "nhớt máy": "引擎機油",
    "dầu động cơ": "引擎潤滑油",
    "nhớt cầu": "差速器油 (齒輪油)",
    "nhớt hộp số": "變速箱油",
    "dầu castrol": "嘉實多潤滑油 (Castrol)",
    "nước rửa kính": "擋風玻璃清洗液",
    "dung dịch vệ sinh buồng dốt động cơ": "柴油引擎燃燒室清洗劑",
    "dung dịch súc rửa động cơ": "引擎內部清洗劑",
    "mỡ bò": "潤滑黃油",
    "mỡ sắt xi": "底盤黃油潤滑",
    "nhân công bảo dưỡng": "定期保養人工工資",
    "thay thế dinamo": "更換發電機總成",
    "dinamo": "汽車發電機",
    "công và vật tư": "人工與更換材料費",
    "nước làm mát": "引擎水箱冷卻液",
    "bugi": "火星塞",
    "bạc đạn": "軸承 (培林)",
    "phanh": "煞車系統",
    "má phanh": "煞車來令片",
    "thay nước làm mát": "更換水箱冷卻液",
    "ktra động cơ": "檢修引擎",
    "vỏ yokohama": "橫濱輪胎 (Yokohama)",
    "gia hạn định vị": "延長GPS定位服務",
    "công tháo lắp bánh xì dầu phanh": "拆裝煞車分泵/碟盤工資",
    "cuppen bánh sau": "後輪煞車皮碗/油封",
    "chất tẩy bố thắng": "煞車來令片清潔劑",
    "công tháo tap lô thay giàn lạnh": "拆裝儀錶板更換蒸發器(冷氣排)",
    "dàn lạnh": "冷氣蒸發器 (冷排)",
    "dầu lạnh": "冷氣冷凍油",
    "ga lạnh": "冷氣冷媒",
    "chất rửa bề mặt kim loại": "金屬表面清洗劑",
    "phụ gia dầu động cơ": "引擎機油添加劑",
    "phụ gia xăng": "汽油精/燃油添加劑",
    "gioang": "汽缸床墊片/油封",
    "vòng lót": "墊圈/華司",
    "phuy dầu động cơ": "桶裝引擎機油",
    "thay kính lái": "更換前擋風玻璃",
    "vệ sinh kim phun": "清洗噴油嘴",
    "chất tẩy bec phun xăng": "噴油嘴清洗劑",
    "gioang làm kín ốc xả dầu": "油底殼螺絲華司/墊片",
    "bánh xì dầu phanh": "煞車分泵",
    "thay thế bugi": "更換火星塞",
    "thay roong nắp dàn cò": "更換汽門室蓋墊片",
    "cân chỉnh góc đặt bánh xe": "四輪定位",
    "cao su che bụi": "防塵套",
    "bạc đạn trước": "前輪軸承",
    "piston thắng": "煞車分泵活塞",
    "lốp dunlop": "登祿普輪胎 (Dunlop)",
    "van lốp xe": "輪胎氣嘴",
    "bộ cupen phanh": "煞車修理包",
    "thay thế dinamo": "更換發電機",
    "lọc nhiên liệu thành phần": "柴油濾芯組件",
    "bạc đạn tăng đơ cuaroa": "皮帶調整器軸承",
    "puly dẫn hướng": "導向滑輪",
    "ống thông hơi": "曲軸箱通風管",
    "công xả gió": "煞車/冷氣管路排氣工資",
    "chất vệ sinh phanh": "煞車清潔劑",
    "chất vệ sinh họng ga": "節氣門清洗劑",
    "công tắc mở cốp": "後車廂開關",
    "đèn sương mù": "霧燈",
    "chất vệ sinh thắng": "煞車清洗劑",
    "lõi柴油/機油濾清器": "濾心",
    "công tác mở cốp": "後車廂開關工資",
    "thay đèn cản trước": "更換前保桿燈",
    "bảo dưỡng cấp trung bình": "中級定期保養",
    "mỡ bôi trơn bảo dưỡng": "保養潤滑黃油",
    "chất vệ sinh thắng": "煞車清潔劑",
    "gioang làm kín ốc xả": "油底殼螺絲墊片",
    "lõi 柴油/機油濾清器": "柴油/機油濾芯",
    "lõi lọc nhớt": "機油濾芯",
    "bình ắc quy": "汽車電瓶",
    "công tác mở": "開關",
    "công thay cáp xooán": "更換方向盤游絲(安全氣囊游絲)工資",
    "cao su gạt mưa": "雨刷膠條",
    "dung dịch súc rửa động cơ xăng": "汽油引擎內部清洗劑",
    "hướng dẫn nhân công": "技術工資",
    "phốt pto": "動力輸出軸油封 (PTO油封)",
    "nước làm mát động cơ màu vàng": "長效黃色水箱精",
    "long đền óc xả nhớt": "油底殼螺絲華司",
    "nhân công thay thế dây cáp cẩu": "吊桿鋼索更換工資",
    "phụ gia nhiên liệu": "燃油添加劑",
    "chỉnh đèn cos bị cao": "調整近光燈照射高度",
    "công thay lọc bụi máy lạnh": "更換冷氣濾網工資",
    "công và vật tư": "工資與材料費",
    "phủ ceramic": "車身陶瓷鍍膜",
    "công kiểm tra đăng kiểm": "代驗車檢修工資",
    "Puly tăng đưa máy lạnh": "冷氣調整滑輪",
    "Đèn led biển số": "車牌LED燈",
    "đảo vỏ cân bằng động": "輪胎對調與動平衡",
    "cao su gạt mưa phải": "右側雨刷膠條",
    "yokohama": "橫濱輪胎",
    "dịch vụ nhân công": "維修工資",
    "Nước làm mát": "水箱冷卻液"
}

def smart_translate(text, target_lang):
    if not text or not isinstance(text, str):
        return text
    
    if target_lang == "繁體中文":
        translated = text
        # 依照詞彙長度排序（優先替換較長的複合詞）
        sorted_keys = sorted(MAINT_TRANSLATIONS.keys(), key=len, reverse=True)
        for key in sorted_keys:
            if key in translated.lower():
                import re
                pattern = re.compile(re.escape(key), re.IGNORECASE)
                translated = pattern.sub(MAINT_TRANSLATIONS[key], translated)
        return translated
    
    return text

def auto_sync_to_fixed_assets(plate_no):
    if "asset_db" not in st.session_state:
        st.session_state.asset_db = [
            {"資產編號": "AST-001", "資產名稱": "主管公務車 (Toyota Camry)", "類別": "車輛設備 (Vehicles)", "保管廠區": "西寧廠", "狀態": "使用中"}
        ]
    
    existing_plates = [str(a.get("資產編號", "")) + str(a.get("資產名稱", "")) for a in st.session_state.asset_db]
    is_exists = any(plate_no in p for p in existing_plates)
    
    if not is_exists:
        new_asset_id = f"AST-VEH-{len(st.session_state.asset_db)+1:03d}"
        st.session_state.asset_db.append({
            "資產編號": new_asset_id,
            "資產名稱": f"公務車/貨車 ({plate_no})",
            "類別": "車輛設備 (Vehicles)",
            "保管廠區": "西寧廠 / 海防廠",
            "狀態": "使用中 (Active)"
        })

def render_vehicle_maintenance_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = VEHICLE_MAINT_I18N.get(active_lang, VEHICLE_MAINT_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "vehicle_maint_db" not in st.session_state:
        st.session_state.vehicle_maint_db = [
            {"plate": "70LD-00606", "type": "bão dưỡng cấp 2", "cost": 378000.0, "desc": "công bão dưỡng (Thaco Gò Dầu)", "date": "2025-09-19"},
            {"plate": "70LD-00670", "type": "bão dưỡng", "cost": 178200.0, "desc": "công bão dưỡng (Honda Bình Dương)", "date": "2025-11-14"}
        ]

    tab_list, tab_import, tab_add = st.tabs([
        L["tab_list"], L["tab_import"], L["tab_add"]
    ])

    # 1. 依車號分組篩選之總表
    with tab_list:
        st.markdown(f"### {L['table_header']}")
        if st.session_state.vehicle_maint_db:
            all_plates = sorted(list(set([item["plate"] for item in st.session_state.vehicle_maint_db])))
            selected_plate_filter = st.selectbox("🚗 快速篩選車牌號碼 (Filter by License Plate)", ["全部車輛 (All Vehicles)"] + all_plates)

            filtered_db = st.session_state.vehicle_maint_db
            if selected_plate_filter != "全部車輛 (All Vehicles)":
                filtered_db = [item for item in filtered_db if item["plate"] == selected_plate_filter]

            display_data = []
            for idx, item in enumerate(filtered_db, 1):
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

    # 2. 智慧批次匯入 Excel 並自動同步至固定資產
    with tab_import:
        st.markdown(f"### {L['import_header']}")
        st.caption(L["import_caption"])
        uploaded_file = st.file_uploader(L["btn_upload"], type=["xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                xls = pd.ExcelFile(uploaded_file)
                st.info(f"📂 成功讀取 Excel 檔案，共發現 {len(xls.sheet_names)} 個車輛分頁 (Sheets): {', '.join(xls.sheet_names)}")
                
                if st.button("🚀 確認上傳並同步至固定資產", type="primary"):
                    imported_count = 0
                    new_records = []
                    synced_plates = set()
                    
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
                        
                        auto_sync_to_fixed_assets(plate_no)
                        synced_plates.add(plate_no)
                        
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
                        st.info(f"✨ 已自動為以下車號在「固定資產與設備管理」中建立資產代號：{', '.join(synced_plates)}")
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
                    auto_sync_to_fixed_assets(plate)
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
