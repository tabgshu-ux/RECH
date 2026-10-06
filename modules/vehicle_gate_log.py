import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 車輛門禁與進出紀錄模組多語系字典 (i18n)
# ----------------------------------------------------
GATE_LOG_I18N = {
    "繁體中文": {
        "title": "🚗 警衛室/管理部 - 廠區車輛進出與門禁時間紀錄",
        "caption": "記錄跨國廠區（西寧廠/海防廠）大門口公務車、貨車及訪客車輛進出時間、駕駛與載貨內容。",
        "tab_list": "📑 今日車輛進出門禁總表",
        "tab_record": "➕ 登記車輛進出廠區",
        "table_header": "📋 廠區大門車輛進出即時紀錄清冊",
        "no_records": "目前無車輛進出紀錄。",
        "record_header": "➕ 登記車輛進出廠區門禁",
        "lbl_plate": "車牌號碼 *",
        "lbl_driver": "駕駛姓名與所屬單位 *",
        "driver_placeholder": "例如: Nguyễn Văn B (物流外包)",
        "lbl_type": "車輛類型 *",
        "type_opts": ["貨車 (Truck)", "公務車 (Company Car)", "訪客車 (Visitor)", "外包工程車"],
        "lbl_direction": "進出方向 *",
        "dir_opts": ["車輛入廠 (Check-In)", "車輛出廠 (Check-Out)"],
        "lbl_purpose": "入廠/出廠事由與載貨說明 *",
        "purpose_placeholder": "例如: 運送配電盤原物料銅排入廠",
        "btn_save": "💾 記錄門禁進出時間",
        "success_save": "✅ 車輛 `{plate}` 門禁紀錄已成功登記！",
        "fill_warning": "⚠️ 請完整填寫車牌號碼與駕駛姓名！",
        # 表格動態欄位
        "col_index": "STT",
        "col_plate": "車牌號碼",
        "col_driver": "駕駛與單位",
        "col_type": "車輛類型",
        "col_dir": "進出方向",
        "col_purpose": "載貨與事由",
        "col_time": "登記時間"
    },
    "Tiếng Việt": {
        "title": "🚗 Phòng Bảo vệ - Quản lý Xe ra vào Nhà máy",
        "caption": "Ghi nhận thời gian ra vào cổng của xe công ty, xe tải hàng hóa và xe khách tại Tây Ninh và Hải Phòng.",
        "tab_list": "📑 Danh sách Xe ra vào trong ngày",
        "tab_record": "➕ Đăng ký Xe ra/vào cổng",
        "table_header": "📋 Sổ nhật ký xe ra vào cổng nhà máy",
        "no_records": "Hiện không có bản ghi ra vào nào.",
        "record_header": "➕ Đăng ký xe ra vào cổng nhà máy",
        "lbl_plate": "Biển số xe *",
        "lbl_driver": "Tên tài xế & Đơn vị *",
        "driver_placeholder": "Ví dụ: Nguyễn Văn B (Đơn vị vận chuyển)",
        "lbl_type": "Loại xe *",
        "type_opts": ["Xe tải (Truck)", "Xe công ty (Company Car)", "Xe khách / Khách (Visitor)", "Xe dịch vụ"],
        "lbl_direction": "Hướng di chuyển *",
        "dir_opts": ["Xe vào cổng (Check-In)", "Xe ra cổng (Check-Out)"],
        "lbl_purpose": "Lý do & Hàng hóa vận chuyển *",
        "purpose_placeholder": "Ví dụ: Vận chuyển vật tư đồng thanh cái vào nhà máy",
        "btn_save": "💾 Ghi nhận thời gian ra vào",
        "success_save": "✅ Đã ghi nhận门禁 cho xe `{plate}` thành công!",
        "fill_warning": "⚠️ Vui lòng điền Biển số xe và Tên tài xế!",
        # Tiêu đề bảng
        "col_index": "STT",
        "col_plate": "Biển số xe",
        "col_driver": "Tài xế & Đơn vị",
        "col_type": "Loại xe",
        "col_dir": "Hướng",
        "col_purpose": "Nội dung / Sự việc",
        "col_time": "Thời gian"
    },
    "English": {
        "title": "🚗 Security - Plant Vehicle Gate & Access Log",
        "caption": "Track entry and exit times, drivers, and cargo details for company trucks, cars, and visitors.",
        "tab_list": "📑 Today's Gate Access Log",
        "tab_record": "➕ Register Vehicle Entry/Exit",
        "table_header": "📋 Plant Gate Vehicle Access Registry",
        "no_records": "No vehicle gate logs found.",
        "record_header": "➕ Register Vehicle Access at Gate",
        "lbl_plate": "License Plate *",
        "lbl_driver": "Driver Name & Unit *",
        "driver_placeholder": "Example: Nguyen Van B (Logistics)",
        "lbl_type": "Vehicle Type *",
        "type_opts": ["Truck", "Company Car", "Visitor", "Contractor Van"],
        "lbl_direction": "Direction *",
        "dir_opts": ["Check-In (Entry)", "Check-Out (Exit)"],
        "lbl_purpose": "Purpose & Cargo Description *",
        "purpose_placeholder": "Example: Delivering copper busbar raw materials",
        "btn_save": "💾 Record Gate Access Time",
        "success_save": "✅ Gate log for vehicle `{plate}` recorded successfully!",
        "fill_warning": "⚠️ Please fill in License Plate and Driver Name!",
        # Table headers
        "col_index": "No.",
        "col_plate": "License Plate",
        "col_driver": "Driver & Unit",
        "col_type": "Vehicle Type",
        "col_dir": "Direction",
        "col_purpose": "Cargo & Purpose",
        "col_time": "Timestamp"
    }
}

# ----------------------------------------------------
# 🔄 門禁模組專用：中越英智慧語意對照引擎
# ----------------------------------------------------
def smart_translate_gate(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    
    val_lower = text_val.lower()

    if "車輛入廠" in text_val or "check-in" in val_lower or "vào cổng" in val_lower:
        if target_lang == "Tiếng Việt": return "Xe vào cổng (Check-In)"
        elif target_lang == "English": return "Check-In (Entry)"
        return "🟢 車輛入廠 (Check-In)"

    if "車輛出廠" in text_val or "check-out" in val_lower or "ra cổng" in val_lower:
        if target_lang == "Tiếng Việt": return "Xe ra cổng (Check-Out)"
        elif target_lang == "English": return "Check-Out (Exit)"
        return "🔴 車輛出廠 (Check-Out)"

    return text_val

def render_vehicle_gate_log_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = GATE_LOG_I18N.get(active_lang, GATE_LOG_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化門禁資料庫
    if "vehicle_gate_db" not in st.session_state:
        st.session_state.vehicle_gate_db = [
            {
                "plate": "61A-888.66",
                "driver": "Nguyễn Văn An (Logistics)",
                "type": "公務車 (Company Car)",
                "direction": "車輛入廠",
                "purpose": "載送總經理赴胡志明市開會",
                "time": "2026-10-06 08:15:00"
            },
            {
                "plate": "51D-456.78",
                "driver": "Trần Văn Bình (鋼鐵供應商)",
                "type": "貨車 (Truck)",
                "direction": "車輛入廠",
                "purpose": "運送 2000A 銅排母線原料 500kg",
                "time": "2026-10-06 09:30:00"
            }
        ]

    tab_list, tab_record = st.tabs([L["tab_list"], L["tab_record"]])

    with tab_list:
        st.markdown(f"### {L['table_header']}")
        if st.session_state.vehicle_gate_db:
            display_data = []
            for idx, item in enumerate(st.session_state.vehicle_gate_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_plate"]: item["plate"],
                    L["col_driver"]: item["driver"],
                    L["col_type"]: item["type"],
                    L["col_dir"]: smart_translate_gate(item["direction"], active_lang),
                    L["col_purpose"]: item["purpose"],
                    L["col_time"]: item["time"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    with tab_record:
        st.markdown(f"### {L['record_header']}")
        with st.form("form_gate_record"):
            c1, c2 = st.columns(2)
            with c1:
                plate = st.text_input(L["lbl_plate"], value="61A-123.45")
                driver = st.text_input(L["lbl_driver"], placeholder=L["driver_placeholder"])
            with c2:
                v_type = st.selectbox(L["lbl_type"], L["type_opts"])
                direction = st.selectbox(L["lbl_direction"], L["dir_opts"])

            purpose = st.text_area(L["lbl_purpose"], placeholder=L["purpose_placeholder"])

            if st.form_submit_button(L["btn_save"], type="primary", use_container_width=True):
                if plate and driver:
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.vehicle_gate_db.insert(0, {
                        "plate": plate,
                        "driver": driver,
                        "type": v_type,
                        "direction": "車輛入廠" if "入" in direction or "In" in direction else "車輛出廠",
                        "purpose": purpose if purpose else "-",
                        "time": now_str
                    })
                    st.success(L["success_save"].format(plate=plate))
                    st.rerun()
                else:
                    st.warning(L["fill_warning"])

def show(*args, **kwargs):
    render_vehicle_gate_log_page(*args, **kwargs)

def main(*args, **kwargs):
    render_vehicle_gate_log_page(*args, **kwargs)

def render_vehicle_gate_log(*args, **kwargs):
    render_vehicle_gate_log_page(*args, **kwargs)
