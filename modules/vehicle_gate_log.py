import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 車輛門禁與派車審核模組多語系字典 (i18n)
# ----------------------------------------------------
GATE_LOG_I18N = {
    "繁體中文": {
        "title": "🚗 警衛室/管理部 - 廠區車輛進出與派車審核放行中心",
        "caption": "記錄西寧廠與海防廠大門口公務車、貨車及訪客車輛進出時間，並即時查核由【全公司電子簽核中心】主管審核通過之派車放行單。",
        "tab_list": "📑 今日車輛進出門禁總表",
        "tab_approval": "🛡️ 派車審核放行表 (保全專用核對)",
        "tab_record": "➕ 登記車輛進出廠區",
        "table_header": "📋 廠區大門車輛進出即時紀錄清冊",
        "approval_header": "🛡️ 主管已簽核之派車放行與車輛管制清冊",
        "approval_caption": "保全人員請於車輛離廠或入廠時，核對下方由系統主管簽核通過之派車單與車牌號碼。",
        "no_records": "目前無車輛進出紀錄。",
        "no_approvals": "目前無已核准的派車單。",
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
        "col_index": "STT",
        "col_plate": "車牌號碼",
        "col_driver": "駕駛與單位",
        "col_type": "車輛類型",
        "col_dir": "進出方向",
        "col_purpose": "載貨與事由",
        "col_time": "登記時間",
        "col_requester": "申請部門/人員",
        "col_status": "放行狀態"
    },
    "Tiếng Việt": {
        "title": "🚗 Phòng Bảo vệ - Quản lý Xe ra vào & Phê duyệt Điều xe",
        "caption": "Ghi nhận xe ra vào cổng nhà máy Tây Ninh và Hải Phòng, kết nối trực tiếp với Trung tâm Phê duyệt điện tử để kiểm tra lệnh điều xe.",
        "tab_list": "📑 Danh sách Xe ra vào trong ngày",
        "tab_approval": "🛡️ Danh sách Xe được phép điều động (Dành cho Bảo vệ)",
        "tab_record": "➕ Đăng ký Xe ra/vào cổng",
        "table_header": "📋 Sổ nhật ký xe ra vào cổng nhà máy",
        "approval_header": "🛡️ Danh sách lệnh điều xe đã được cấp trên phê duyệt",
        "approval_caption": "Bảo vệ vui lòng kiểm tra biển số và lệnh điều xe được phê duyệt dưới đây trước khi cho xe qua cổng.",
        "no_records": "Hiện không có bản ghi ra vào nào.",
        "no_approvals": "Hiện chưa có lệnh điều xe nào được duyệt.",
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
        "col_index": "STT",
        "col_plate": "Biển số xe",
        "col_driver": "Tài xế & Đơn vị",
        "col_type": "Loại xe",
        "col_dir": "Hướng",
        "col_purpose": "Nội dung / Sự việc",
        "col_time": "Thời gian",
        "col_requester": "Người yêu cầu",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "🚗 Security - Plant Vehicle Gate & Dispatch Approval Center",
        "caption": "Track entry/exit times and verify vehicle dispatch orders approved via the E-Approval Center.",
        "tab_list": "📑 Today's Gate Access Log",
        "tab_approval": "🛡️ Approved Dispatch Orders (Security Verification)",
        "tab_record": "➕ Register Vehicle Entry/Exit",
        "table_header": "📋 Plant Gate Vehicle Access Registry",
        "approval_header": "🛡️ Manager-Approved Vehicle Dispatch Registry",
        "approval_caption": "Security guards must verify approved dispatch orders and license plates before granting entry/exit.",
        "no_records": "No vehicle gate logs found.",
        "no_approvals": "No approved dispatch orders found.",
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
        "col_index": "No.",
        "col_plate": "License Plate",
        "col_driver": "Driver & Unit",
        "col_type": "Vehicle Type",
        "col_dir": "Direction",
        "col_purpose": "Cargo & Purpose",
        "col_time": "Timestamp",
        "col_requester": "Requester",
        "col_status": "Status"
    }
}

def smart_translate_gate(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    val_lower = text_val.lower()

    if "車輛入廠" in text_val or "check-in" in val_lower or "vào cổng" in val_lower:
        if target_lang == "Tiếng Việt": return "🟢 Xe vào cổng (Check-In)"
        elif target_lang == "English": return "🟢 Check-In (Entry)"
        return "🟢 車輛入廠 (Check-In)"

    if "車輛出廠" in text_val or "check-out" in val_lower or "ra cổng" in val_lower:
        if target_lang == "Tiếng Việt": return "🔴 Xe ra cổng (Check-Out)"
        elif target_lang == "English": return "🔴 Check-Out (Exit)"
        return "🔴 車輛出廠 (Check-Out)"

    return text_val

def render_vehicle_gate_log_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = GATE_LOG_I18N.get(active_lang, GATE_LOG_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

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

    # 模擬從電子簽核中心 (Approval Center) 審核通過之派車放行清單
    approved_dispatches = [
        {"工單編號": "APP-DISPATCH-2026-001", "申請部門": "管理部", "申請人": "陳經理", "車牌號碼": "61A-888.66", "用途說明": "載送總經理赴胡志明市開會", "主管簽核狀態": "🟢 總經理已核准 (Approved)"},
        {"工單編號": "APP-DISPATCH-2026-002", "申請部門": "生產部", "申請人": "阮文強", "車牌號碼": "51D-456.78", "用途說明": "運送 2000A 銅排母線原料 500kg", "主管簽核狀態": "🟢 生產主管已核准 (Approved)"}
    ]

    tab_list, tab_approval, tab_record = st.tabs([
        L["tab_list"], L["tab_approval"], L["tab_record"]
    ])

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
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    with tab_approval:
        st.markdown(f"### {L['approval_header']}")
        st.caption(L["approval_caption"])
        if approved_dispatches:
            st.dataframe(pd.DataFrame(approved_dispatches), use_container_width=True)
        else:
            st.info(L["no_approvals"])

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
