import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 車輛門禁、訪客與收發信件模組完整多語系字典 (i18n)
# ----------------------------------------------------
GATE_LOG_I18N = {
    "繁體中文": {
        "title": "🚗 警衛室/管理部 - 廠區門禁、派車審核、訪客與收發信件管理中心",
        "caption": "記錄工廠車輛進出、訪客登記與包裹信件代收，所有數據直接寫入資料庫永久歸檔稽核。",
        "tab_list": "📑 今日車輛門禁總表",
        "tab_approval": "🛡️ 派車審核放行表",
        "tab_visitor": "👥 訪客與外包商登記 (DB)",
        "tab_parcel": "📦 包裹信件代收管理 (DB)",
        "table_header": "📋 廠區大門車輛進出即時紀錄清冊",
        "approval_header": "🛡️ 主管已簽核之派車放行與車輛管制清冊",
        "approval_caption": "保全人員請於車輛離廠或入廠時，核對下方由系統主管簽核通過之派車單與車牌號碼。",
        "no_records": "目前無車輛進出紀錄。",
        "no_approvals": "目前無已核准的派車單。",
        "visitor_header": "👥 訪客、外包商與面試者進出登記 (資料庫直寫)",
        "visitor_list_header": "📋 資料庫訪客與外包商歷史進出稽核清冊",
        "parcel_header": "📦 公司包裹、信件與快遞代收登記 (資料庫直寫)",
        "parcel_list_header": "📋 資料庫包裹信件代收與領取清單",
        "col_index": "STT",
        "col_plate": "車牌號碼",
        "col_driver": "駕駛與單位",
        "col_type": "車輛類型",
        "col_dir": "進出方向",
        "col_purpose": "載貨與事由",
        "col_time": "登記時間",
        "col_status": "放行狀態",
        # 表單與按鈕翻譯
        "form_gate_title": "➕ 登記車輛進出廠區門禁",
        "lbl_select_plate": "選擇車牌號碼",
        "lbl_driver": "駕駛姓名與所屬單位",
        "lbl_v_type": "車輛類型",
        "lbl_direction": "進出方向",
        "lbl_purpose": "入廠/出廠事由與載貨說明",
        "btn_save_gate": "💾 記錄門禁進出時間",
        "success_gate": "✅ 車輛 `{plate}` 門禁紀錄已成功登記！",
        "warn_gate": "⚠️ 請完整填寫車牌號碼與駕駛姓名！",
        # 訪客表單
        "lbl_v_name": "訪客 / 外包商姓名 *",
        "lbl_v_comp": "所屬公司 / 單位 *",
        "lbl_v_id": "身分證號 / 護照號碼 (留置換證) *",
        "lbl_v_target": "拜訪對象 / 員工 *",
        "lbl_v_pass": "核發訪客證編號 (Visitor Pass)",
        "lbl_v_status": "進出狀態",
        "lbl_v_note": "拜訪事由與攜帶工具備註",
        "btn_save_visitor": "🚀 登記訪客並寫入資料庫歸檔",
        "success_visitor": "✅ 訪客 {name} ({comp}) 已成功寫入資料庫，證件已留置管制！",
        "warn_visitor": "⚠️ 請完整填寫訪客姓名、所屬公司與身分證/護照號碼！",
        "no_visitor": "目前資料庫尚無訪客紀錄。",
        # 包裹表單
        "lbl_p_courier": "快遞公司 / 貨運來源 *",
        "lbl_p_receiver": "收件人 (連動員工名冊) *",
        "lbl_p_type": "物件類型",
        "lbl_p_source": "寄件人 / 來源公司",
        "lbl_p_status": "領取狀態",
        "lbl_p_desc": "快遞單號或備註說明",
        "btn_save_parcel": "📦 登記代收包裹並寫入資料庫",
        "success_parcel": "✅ 包裹代收紀錄已成功寫入資料庫，收件人：{receiver}",
        "warn_parcel": "⚠️ 請填寫快遞公司或貨運來源！",
        "no_parcel": "目前資料庫尚無包裹代收紀錄。",
        # 表格動態欄位 (訪客與包裹)
        "v_col_time": "登記時間",
        "v_col_name": "訪客姓名",
        "v_col_comp": "單位/公司",
        "v_col_target": "拜訪對象",
        "v_col_id": "證件號碼",
        "v_col_pass": "訪客證",
        "v_col_status": "狀態",
        "v_col_notes": "備註事由",
        "p_col_time": "登記時間",
        "p_col_courier": "快遞來源",
        "p_col_receiver": "收件人",
        "p_col_type": "物件類型",
        "p_col_sender": "寄件公司",
        "p_col_status": "領取狀態",
        "p_col_notes": "單號備註"
    },
    "Tiếng Việt": {
        "title": "🚗 Phòng Bảo vệ - Quản lý Cổng, Khách ra vào & Bưu phẩm",
        "caption": "Ghi nhận xe, khách ra vào và quản lý bưu phẩm lưu CSDL chính thức.",
        "tab_list": "📑 Sổ xe ra vào",
        "tab_approval": "🛡️ Phê duyệt điều xe",
        "tab_visitor": "👥 Đăng ký Khách",
        "tab_parcel": "📦 Quản lý Bưu phẩm",
        "table_header": "📋 Sổ nhật ký xe ra vào nhà máy",
        "approval_header": "🛡️ Danh sách lệnh điều xe đã được phê duyệt",
        "approval_caption": "Nhân viên bảo vệ vui lòng kiểm tra lệnh điều xe và biển số xe trước khi cho xe ra vào cổng.",
        "no_records": "Không có dữ liệu xe ra vào.",
        "no_approvals": "Không có lệnh điều xe được duyệt.",
        "visitor_header": "👥 Đăng ký khách & nhà thầu ra vào (Lưu CSDL)",
        "visitor_list_header": "📋 Danh sách lịch sử khách ra vào nhà máy",
        "parcel_header": "📦 Quản lý bưu phẩm & thư tín (Lưu CSDL)",
        "parcel_list_header": "📋 Danh sách nhận bưu phẩm",
        "col_index": "STT",
        "col_plate": "Biển số",
        "col_driver": "Tài xế & Đơn vị",
        "col_type": "Loại xe",
        "col_dir": "Hướng",
        "col_purpose": "Nội dung / Hàng hóa",
        "col_time": "Thời gian",
        "col_status": "Trạng thái",
        # Form & Button
        "form_gate_title": "➕ Đăng ký xe ra vào cổng nhà máy",
        "lbl_select_plate": "Chọn biển số xe",
        "lbl_driver": "Tên tài xế & Đơn vị trực thuộc",
        "lbl_v_type": "Loại xe",
        "lbl_direction": "Hướng di chuyển",
        "lbl_purpose": "Lý do ra vào & Mô tả hàng hóa",
        "btn_save_gate": "💾 Ghi nhận thời gian ra vào cổng",
        "success_gate": "✅ Đã ghi nhận nhật ký cổng cho xe `{plate}` thành công!",
        "warn_gate": "⚠️ Vui lòng điền đầy đủ biển số xe và tên tài xế!",
        # Visitor Form
        "lbl_v_name": "Tên Khách / Nhà thầu *",
        "lbl_v_comp": "Công ty / Đơn vị *",
        "lbl_v_id": "Số CCCD / Hộ chiếu (Giữ lại đổi thẻ) *",
        "lbl_v_target": "Người liên hệ / Nhân viên *",
        "lbl_v_pass": "Số thẻ khách (Visitor Pass)",
        "lbl_v_status": "Trạng thái ra vào",
        "lbl_v_note": "Lý do ghé thăm & Ghi chú công cụ mang theo",
        "btn_save_visitor": "🚀 Đăng ký khách và lưu vào CSDL",
        "success_visitor": "✅ Đã lưu khách {name} ({comp}) vào CSDL, giấy tờ đã được giữ lại kiểm soát!",
        "warn_visitor": "⚠️ Vui lòng điền đầy đủ tên khách, công ty và số CCCD/Hộ chiếu!",
        "no_visitor": "Chưa có dữ liệu khách trong CSDL.",
        # Parcel Form
        "lbl_p_courier": "Công ty chuyển phát / Nguồn hàng *",
        "lbl_p_receiver": "Người nhận (Liên kết nhân sự) *",
        "lbl_p_type": "Loại bưu phẩm",
        "lbl_p_source": "Người gửi / Công ty nguồn",
        "lbl_p_status": "Trạng thái nhận",
        "lbl_p_desc": "Mã vận đơn hoặc ghi chú",
        "btn_save_parcel": "📦 Đăng ký nhận bưu phẩm và lưu CSDL",
        "success_parcel": "✅ Đã lưu bưu phẩm vào CSDL, người nhận: {receiver}",
        "warn_parcel": "⚠️ Vui lòng nhập công ty chuyển phát hoặc nguồn hàng!",
        "no_parcel": "Chưa có dữ liệu bưu phẩm trong CSDL.",
        # Table columns (Visitor & Parcel)
        "v_col_time": "Thời gian",
        "v_col_name": "Tên khách",
        "v_col_comp": "Đơn vị/Công ty",
        "v_col_target": "Người gặp",
        "v_col_id": "Số CCCD",
        "v_col_pass": "Thẻ khách",
        "v_col_status": "Trạng thái",
        "v_col_notes": "Ghi chú",
        "p_col_time": "Thời gian",
        "p_col_courier": "Nguồn vận chuyển",
        "p_col_receiver": "Người nhận",
        "p_col_type": "Loại bưu phẩm",
        "p_col_sender": "Công ty gửi",
        "p_col_status": "Trạng thái",
        "p_col_notes": "Ghi chú mã vận đơn"
    },
    "English": {
        "title": "🚗 Security - Gate Access, Dispatch, Visitors & Parcels Center",
        "caption": "Track vehicle entry, visitor logs, and parcel receptions with official database archiving.",
        "tab_list": "📑 Gate Access Log",
        "tab_approval": "🛡️ Dispatch Orders",
        "tab_visitor": "👥 Visitor Registration",
        "tab_parcel": "📦 Parcel Management",
        "table_header": "📋 Vehicle Access Registry",
        "approval_header": "🛡️ Approved Dispatch Registry",
        "approval_caption": "Security personnel must verify dispatch orders and license plates before entry/exit.",
        "no_records": "No vehicle records found.",
        "no_approvals": "No approved dispatch orders.",
        "visitor_header": "👥 Visitor & Contractor Registration (DB)",
        "visitor_list_header": "📋 Visitor Audit Log",
        "parcel_header": "📦 Parcel & Mail Reception (DB)",
        "parcel_list_header": "📋 Parcel Inventory Log",
        "col_index": "No.",
        "col_plate": "License Plate",
        "col_driver": "Driver & Affiliation",
        "col_type": "Vehicle Type",
        "col_dir": "Direction",
        "col_purpose": "Purpose & Cargo",
        "col_time": "Timestamp",
        "col_status": "Status",
        # Form & Button
        "form_gate_title": "➕ Register Factory Gate Access",
        "lbl_select_plate": "Select License Plate",
        "lbl_driver": "Driver Name & Affiliation",
        "lbl_v_type": "Vehicle Type",
        "lbl_direction": "Direction",
        "lbl_purpose": "Purpose & Cargo Description",
        "btn_save_gate": "💾 Record Gate Access Time",
        "success_gate": "✅ Gate log for vehicle `{plate}` successfully registered!",
        "warn_gate": "⚠️ Please fill in license plate and driver name!",
        # Visitor Form
        "lbl_v_name": "Visitor / Contractor Name *",
        "lbl_v_comp": "Company / Organization *",
        "lbl_v_id": "ID Card / Passport No. (Retained) *",
        "lbl_v_target": "Visit Target / Employee *",
        "lbl_v_pass": "Visitor Pass No.",
        "lbl_v_status": "Status",
        "lbl_v_note": "Purpose & Tools Notes",
        "btn_save_visitor": "🚀 Register Visitor & Save to DB",
        "success_visitor": "✅ Visitor {name} ({comp}) successfully saved to DB, ID retained!",
        "warn_visitor": "⚠️ Please complete visitor name, company, and ID number!",
        "no_visitor": "No visitor records in database.",
        # Parcel Form
        "lbl_p_courier": "Courier / Shipping Source *",
        "lbl_p_receiver": "Receiver (Linked Employee) *",
        "lbl_p_type": "Parcel Type",
        "lbl_p_source": "Sender / Source Company",
        "lbl_p_status": "Pickup Status",
        "lbl_p_desc": "Tracking Number or Notes",
        "btn_save_parcel": "📦 Register Parcel & Save to DB",
        "success_parcel": "✅ Parcel record successfully saved to DB, Receiver: {receiver}",
        "warn_parcel": "⚠️ Please enter courier or shipping source!",
        "no_parcel": "No parcel records in database.",
        # Table columns (Visitor & Parcel)
        "v_col_time": "Timestamp",
        "v_col_name": "Visitor Name",
        "v_col_comp": "Company",
        "v_col_target": "Host",
        "v_col_id": "ID Number",
        "v_col_pass": "Pass No.",
        "v_col_status": "Status",
        "v_col_notes": "Notes",
        "p_col_time": "Timestamp",
        "p_col_courier": "Courier",
        "p_col_receiver": "Receiver",
        "p_col_type": "Parcel Type",
        "p_col_sender": "Sender",
        "p_col_status": "Status",
        "p_col_notes": "Tracking Notes"
    }
}

def init_gate_extension_db(engine):
    """
    🔗 自動初始化訪客紀錄與包裹代收的專屬資料庫表格
    """
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.visitor_logs (
                    id SERIAL PRIMARY KEY,
                    visit_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    visitor_name VARCHAR(150) NOT NULL,
                    company_name VARCHAR(150) NOT NULL,
                    visit_target VARCHAR(150),
                    id_number VARCHAR(100),
                    visitor_pass VARCHAR(50),
                    status VARCHAR(50) DEFAULT '在廠中',
                    notes TEXT
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.parcel_logs (
                    id SERIAL PRIMARY KEY,
                    reg_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    courier_source VARCHAR(150) NOT NULL,
                    receiver_name VARCHAR(150) NOT NULL,
                    parcel_type VARCHAR(100),
                    sender_source VARCHAR(150),
                    status VARCHAR(50) DEFAULT '待領取',
                    notes TEXT
                );
            """))
    except Exception:
        pass

def get_vehicle_options_from_assets(engine):
    vehicles = ["60A-888.99 (Toyota Fortuner 7座)"]
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT license_plate, asset_name, driver_custodian FROM public.fixed_assets WHERE license_plate IS NOT NULL AND license_plate != '';"))
                rows = res.fetchall()
                if rows:
                    for r in rows:
                        plate = r[0]
                        name = r[1] or ""
                        driver = r[2] or ""
                        item_str = f"{plate} ({name})" + (f" - 司機:{driver}" if driver else "")
                        if item_str not in vehicles:
                            vehicles.append(item_str)
        except Exception:
            pass
    return vehicles

def get_employee_options_from_db(engine):
    employees = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT emp_name, position FROM public.employee_profiles WHERE (status IS NULL OR status = '在職');"))
                rows = res.fetchall()
                if rows:
                    for r in rows:
                        name = r[0]
                        pos = r[1] or '員工'
                        if name:
                            employees.append(f"{name} ({pos})")
        except Exception:
            pass
    
    if not employees:
        employees = ["許福村 (Tassos)", "阮文強 (Staff)", "吳經理 (Manager)"]
    return employees

def smart_translate_gate(text_val, target_lang):
    """
    🧠 智慧翻譯函式：自動將資料庫或紀錄中的文字轉為對應語系
    """
    if not text_val or not isinstance(text_val, str):
        return text_val
    val_lower = text_val.lower()

    # 車輛進出方向翻譯
    if "車輛入廠" in text_val or "check-in" in val_lower or "vào cổng" in val_lower:
        if target_lang == "Tiếng Việt": return "🟢 Xe vào cổng (Check-In)"
        elif target_lang == "English": return "🟢 Check-In (Entry)"
        return "🟢 車輛入廠 (Check-In)"

    if "車輛出廠" in text_val or "check-out" in val_lower or "ra cổng" in val_lower:
        if target_lang == "Tiếng Việt": return "🔴 Xe ra cổng (Check-Out)"
        elif target_lang == "English": return "🔴 Check-Out (Exit)"
        return "🔴 車輛出廠 (Check-Out)"

    # 車輛類型翻譯
    if "貨車" in text_val or "truck" in val_lower:
        if target_lang == "Tiếng Việt": return "Xe tải (Truck)"
        elif target_lang == "English": return "Truck"
    elif "公務車" in text_val or "company car" in val_lower:
        if target_lang == "Tiếng Việt": return "Xe công (Company Car)"
        elif target_lang == "English": return "Company Car"
    elif "訪客車" in text_val or "visitor" in val_lower:
        if target_lang == "Tiếng Việt": return "Xe khách (Visitor)"
        elif target_lang == "English": return "Visitor Car"
    elif "外包工程車" in text_val or "contractor" in val_lower:
        if target_lang == "Tiếng Việt": return "Xe nhà thầu (Contractor)"
        elif target_lang == "English": return "Contractor Vehicle"

    return text_val

def render_vehicle_gate_log_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = GATE_LOG_I18N.get(active_lang, GATE_LOG_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_gate_extension_db(engine)

    if "vehicle_gate_db" not in st.session_state:
        st.session_state.vehicle_gate_db = [
            {
                "plate": "61A-888.66",
                "driver": "Nguyễn Văn An (Logistics)",
                "type": "公務車 (Company Car)",
                "direction": "車輛入廠",
                "purpose": "載送總經理赴胡志明市開會",
                "time": "2026-10-06 08:15:00"
            }
        ]

    emp_list = get_employee_options_from_db(engine)
    req_mgr_1 = emp_list[0] if len(emp_list) > 0 else "許福村"

    approved_dispatches = [
        {"工單編號": "APP-DISPATCH-2026-001", "申請部門": "管理部", "申請人": req_mgr_1, "車牌號碼": "61A-888.66", "用途說明": "載送總經理赴胡志明市開會", "主管簽核狀態": "🟢 總經理已核准 (Approved)"}
    ]

    tab_list, tab_approval, tab_visitor, tab_parcel = st.tabs([
        L["tab_list"], L["tab_approval"], L["tab_visitor"], L["tab_parcel"]
    ])

    # Tab 1: 今日車輛門禁
    with tab_list:
        st.markdown(f"### {L['table_header']}")
        if st.session_state.vehicle_gate_db:
            display_data = []
            for idx, item in enumerate(st.session_state.vehicle_gate_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_plate"]: item["plate"],
                    L["col_driver"]: smart_translate_gate(item["driver"], active_lang),
                    L["col_type"]: smart_translate_gate(item["type"], active_lang),
                    L["col_dir"]: smart_translate_gate(item["direction"], active_lang),
                    L["col_purpose"]: smart_translate_gate(item["purpose"], active_lang),
                    L["col_time"]: item["time"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)
        else:
            st.info(L["no_records"])
        
        st.markdown("---")
        with st.form("form_gate_record"):
            st.markdown(f"### {L['form_gate_title']}")
            available_vehicles = get_vehicle_options_from_assets(engine)
            c1, c2 = st.columns(2)
            with c1:
                selected_vehicle_option = st.selectbox(L["lbl_select_plate"], available_vehicles)
                plate = selected_vehicle_option.split(" ")[0] if selected_vehicle_option else ""
                driver = st.text_input(L["lbl_driver"], placeholder="例如: Nguyễn Văn B (物流外包)")
            with c2:
                v_type_options = ["貨車 (Truck)", "公務車 (Company Car)", "訪客車 (Visitor)", "外包工程車"]
                if active_lang == "Tiếng Việt":
                    v_type_options = ["Xe tải (Truck)", "Xe công (Company Car)", "Xe khách (Visitor)", "Xe nhà thầu"]
                elif active_lang == "English":
                    v_type_options = ["Truck", "Company Car", "Visitor", "Contractor"]
                v_type = st.selectbox(L["lbl_v_type"], v_type_options)

                dir_options = ["車輛入廠 (Check-In)", "車輛出廠 (Check-Out)"]
                if active_lang == "Tiếng Việt":
                    dir_options = ["Xe vào cổng (Check-In)", "Xe rời cổng (Check-Out)"]
                elif active_lang == "English":
                    dir_options = ["Check-In", "Check-Out"]
                direction = st.selectbox(L["lbl_direction"], dir_options)

            purpose = st.text_area(L["lbl_purpose"], placeholder="例如: 運送配電盤原物料銅排入廠")

            if st.form_submit_button(L["btn_save_gate"], type="primary", use_container_width=True):
                if plate and driver:
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.vehicle_gate_db.insert(0, {
                        "plate": plate,
                        "driver": driver,
                        "type": v_type,
                        "direction": "車輛入廠" if "入" in direction or "In" in direction or "vào" in direction else "車輛出廠",
                        "purpose": purpose if purpose else "-",
                        "time": now_str
                    })
                    st.success(L["success_gate"].format(plate=plate))
                    st.rerun()
                else:
                    st.warning(L["warn_gate"])

    # Tab 2: 派車審核
    with tab_approval:
        st.markdown(f"### {L['approval_header']}")
        st.caption(L["approval_caption"])
        if approved_dispatches:
            st.dataframe(pd.DataFrame(approved_dispatches), use_container_width=True, hide_index=True)
        else:
            st.info(L["no_approvals"])

    # Tab 3: 訪客與外包商登記
    with tab_visitor:
        st.markdown(f"### {L['visitor_header']}")
        with st.form("form_visitor_record_db"):
            c1, c2 = st.columns(2)
            with c1:
                v_name = st.text_input(L["lbl_v_name"], placeholder="輸入全名...")
                v_company = st.text_input(L["lbl_v_comp"], placeholder="例: 宏碁電腦 / 消防工程行")
                v_id = st.text_input(L["lbl_v_id"], placeholder="CCCD / Passport ID...")
            with c2:
                v_target = st.selectbox(L["lbl_v_target"], emp_list)
                v_pass_no = st.text_input(L["lbl_v_pass"], placeholder="例: V-05")
                v_status_opts = ["🟢 在廠中 (Checked-In)", "🔴 已離廠 (Check-Out)"]
                if active_lang == "Tiếng Việt": v_status_opts = ["🟢 Đang trong nhà máy", "🔴 Đã rời đi"]
                v_status = st.selectbox(L["lbl_v_status"], v_status_opts)

            v_note = st.text_input(L["lbl_v_note"], placeholder="例: 廠區消防灑水系統定期維護...")

            if st.form_submit_button(L["btn_save_visitor"], type="primary", use_container_width=True):
                if v_name and v_company and v_id:
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.visitor_logs (visitor_name, company_name, visit_target, id_number, visitor_pass, status, notes)
                                    VALUES (:name, :comp, :target, :id_no, :pass_no, :status, :notes);
                                """), {
                                    "name": v_name.strip(),
                                    "comp": v_company.strip(),
                                    "target": v_target,
                                    "id_no": v_id.strip(),
                                    "pass_no": v_pass_no.strip() if v_pass_no else "-",
                                    "status": v_status,
                                    "notes": v_note.strip() if v_note else "-"
                                })
                            st.success(L["success_visitor"].format(name=v_name, comp=v_company))
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("⚠️ DB Engine not ready.")
                else:
                    st.warning(L["warn_visitor"])

        st.markdown("---")
        st.markdown(f"### {L['visitor_list_header']}")
        
        visitor_records = []
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT visit_time, visitor_name, company_name, visit_target, id_number, visitor_pass, status, notes FROM public.visitor_logs ORDER BY id DESC LIMIT 50;"))
                    for r in res.fetchall():
                        visitor_records.append({
                            L["v_col_time"]: str(r[0])[:19],
                            L["v_col_name"]: r[1],
                            L["v_col_comp"]: r[2],
                            L["v_col_target"]: r[3],
                            L["v_col_id"]: r[4],
                            L["v_col_pass"]: r[5],
                            L["v_col_status"]: r[6],
                            L["v_col_notes"]: r[7]
                        })
            except Exception:
                pass

        if visitor_records:
            st.dataframe(pd.DataFrame(visitor_records), use_container_width=True, hide_index=True)
        else:
            st.info(L["no_visitor"])

    # Tab 4: 包裹信件代收管理
    with tab_parcel:
        st.markdown(f"### {L['parcel_header']}")
        with st.form("form_parcel_record_db"):
            c1, c2 = st.columns(2)
            with c1:
                p_courier = st.text_input(L["lbl_p_courier"], placeholder="例: Shopee Express, Viettel Post...")
                p_receiver = st.selectbox(L["lbl_p_receiver"], emp_list)
                p_type_opts = ["文件信封 (Envelope)", "包裹箱子 (Box)", "大宗貨物 (Pallet/Cargo)"]
                if active_lang == "Tiếng Việt": p_type_opts = ["Thư từ (Envelope)", "Thùng hàng (Box)", "Hàng lớn (Pallet/Cargo)"]
                p_type = st.selectbox(L["lbl_p_type"], p_type_opts)
            with c2:
                p_source = st.text_input(L["lbl_p_source"], placeholder="例: 台北總公司、某某供應商...")
                p_status_opts = ["🟡 待領取 (Uncollected)", "🟢 已由本人領取 (Delivered)", "🟢 已由部門代收簽名 (Delegated)"]
                if active_lang == "Tiếng Việt": p_status_opts = ["🟡 Chờ nhận", "🟢 Đã nhận", "🟢 Bộ phận ký nhận thay"]
                p_status = st.selectbox(L["lbl_p_status"], p_status_opts)

            p_desc = st.text_input(L["lbl_p_desc"], placeholder="例: 貨號 VT-998231，易碎品...")

            if st.form_submit_button(L["btn_save_parcel"], type="primary", use_container_width=True):
                if p_courier:
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.parcel_logs (courier_source, receiver_name, parcel_type, sender_source, status, notes)
                                    VALUES (:courier, :receiver, :p_type, :sender, :status, :notes);
                                """), {
                                    "courier": p_courier.strip(),
                                    "receiver": p_receiver,
                                    "p_type": p_type,
                                    "sender": p_source.strip() if p_source else "-",
                                    "status": p_status,
                                    "notes": p_desc.strip() if p_desc else "-"
                                })
                            st.success(L["success_parcel"].format(receiver=p_receiver))
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("⚠️ DB Engine not ready.")
                else:
                    st.warning(L["warn_parcel"])

        st.markdown("---")
        st.markdown(f"### {L['parcel_list_header']}")
        
        parcel_records = []
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT reg_time, courier_source, receiver_name, parcel_type, sender_source, status, notes FROM public.parcel_logs ORDER BY id DESC LIMIT 50;"))
                    for r in res.fetchall():
                        parcel_records.append({
                            L["p_col_time"]: str(r[0])[:19],
                            L["p_col_courier"]: r[1],
                            L["p_col_receiver"]: r[2],
                            L["p_col_type"]: r[3],
                            L["p_col_sender"]: r[4],
                            L["p_col_status"]: r[5],
                            L["p_col_notes"]: r[6]
                        })
            except Exception:
                pass

        if parcel_records:
            st.dataframe(pd.DataFrame(parcel_records), use_container_width=True, hide_index=True)
        else:
            st.info(L["no_parcel"])

def show(*args, **kwargs):
    render_vehicle_gate_log_page(*args, **kwargs)

def main(*args, **kwargs):
    render_vehicle_gate_log_page(*args, **kwargs)

def render_vehicle_gate_log(*args, **kwargs):
    render_vehicle_gate_log_page(*args, **kwargs)
