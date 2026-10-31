import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 車輛門禁、訪客與收发信件模組多語系字典 (i18n)
# ----------------------------------------------------
GATE_LOG_I18N = {
    "繁體中文": {
        "title": "🚗 警衛室/管理部 - 廠區門禁、派車審核、訪客與收發信件管理中心",
        "caption": "記錄工廠車輛進出、訪客登記、包裹信件代收，並即時串聯【固定資產車輛】與【員工檔案】資料庫。",
        "tab_list": "📑 今日車輛門禁總表",
        "tab_approval": "🛡️ 派車審核放行表",
        "tab_visitor": "👥 訪客與外包商登記",
        "tab_parcel": "📦 包裹信件代收管理",
        "table_header": "📋 廠區大門車輛進出即時紀錄清冊",
        "approval_header": "🛡️ 主管已簽核之派車放行與車輛管制清冊",
        "approval_caption": "保全人員請於車輛離廠或入廠時，核對下方由系統主管簽核通過之派車單與車牌號碼。",
        "no_records": "目前無車輛進出紀錄。",
        "no_approvals": "目前無已核准的派車單。",
        "visitor_header": "👥 訪客、外包商與面試者進出登記",
        "visitor_list_header": "📋 今日訪客與外包商進出紀錄",
        "parcel_header": "📦 公司包裹、信件與快遞代收登記",
        "parcel_list_header": "📋 待領取與歷史包裹清單",
        "col_index": "STT",
        "col_plate": "車牌號碼",
        "col_driver": "駕駛與單位",
        "col_type": "車輛類型",
        "col_dir": "進出方向",
        "col_purpose": "載貨與事由",
        "col_time": "登記時間",
        "col_status": "放行狀態"
    },
    "Tiếng Việt": {
        "title": "🚗 Phòng Bảo vệ - Quản lý Cổng, Khách ra vào & Bưu phẩm",
        "caption": "Ghi nhận xe, khách ra vào và quản lý bưu phẩm.",
        "tab_list": "📑 Sổ xe ra vào",
        "tab_approval": "🛡️ Phê duyệt điều xe",
        "tab_visitor": "👥 Đăng ký Khách",
        "tab_parcel": "📦 Quản lý Bưu phẩm",
        "table_header": "📋 Sổ nhật ký xe",
        "approval_header": "🛡️ Danh sách lệnh điều xe",
        "approval_caption": "Kiểm tra biển số xe trước khi qua cổng.",
        "no_records": "Không có dữ liệu.",
        "no_approvals": "Không có lệnh điều xe.",
        "visitor_header": "👥 Đăng ký khách",
        "visitor_list_header": "📋 Lịch sử khách ra vào",
        "parcel_header": "📦 Quản lý bưu phẩm",
        "parcel_list_header": "📋 Danh sách bưu phẩm",
        "col_index": "STT",
        "col_plate": "Biển số",
        "col_driver": "Tài xế",
        "col_type": "Loại xe",
        "col_dir": "Hướng",
        "col_purpose": "Nội dung",
        "col_time": "Thời gian",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "🚗 Security - Gate Access, Dispatch, Visitors & Parcels Center",
        "caption": "Track vehicle entry, visitor logs, and parcel receptions.",
        "tab_list": "📑 Gate Access Log",
        "tab_approval": "🛡️ Dispatch Orders",
        "tab_visitor": "👥 Visitor Registration",
        "tab_parcel": "📦 Parcel Management",
        "table_header": "📋 Vehicle Access Registry",
        "approval_header": "🛡️ Approved Dispatch Registry",
        "approval_caption": "Verify dispatch orders before entry.",
        "no_records": "No records found.",
        "no_approvals": "No approved orders.",
        "visitor_header": "👥 Visitor Registration",
        "visitor_list_header": "📋 Visitor Log",
        "parcel_header": "📦 Parcel & Mail Reception",
        "parcel_list_header": "📋 Parcel Inventory",
        "col_index": "No.",
        "col_plate": "License Plate",
        "col_driver": "Driver",
        "col_type": "Type",
        "col_dir": "Direction",
        "col_purpose": "Purpose",
        "col_time": "Timestamp",
        "col_status": "Status"
    }
}

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

    # 1. 初始化車輛門禁紀錄 Session
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

    # 2. 初始化訪客登記 Session
    if "visitor_gate_db" not in st.session_state:
        st.session_state.visitor_gate_db = [
            {
                "日期時間": "2026-10-31 09:00:00",
                "訪客姓名": "Trần Văn Hùng",
                "單位/公司": "ABC 消防設備工程",
                "拜訪對象": "許福村 (管理部經理)",
                "證件號碼": "079088123456",
                "訪客證編號": "V-01",
                "狀態": "🟢 在廠中 (Checked-In)"
            }
        ]

    # 3. 初始化包裹信件代收 Session
    if "parcel_gate_db" not in st.session_state:
        st.session_state.parcel_gate_db = [
            {
                "登記日期": "2026-10-31 10:30:00",
                "快遞公司": "Viettel Post / 順豐",
                "收件人": "許福村 (Tassos)",
                "物件類型": "文件包裹 (Document/Box)",
                "寄件來源": "胡志明市總公司",
                "領取狀態": "🟡 待領取 (Uncollected)"
            }
        ]

    emp_list = get_employee_options_from_db(engine)
    req_mgr_1 = emp_list[0] if len(emp_list) > 0 else "許福村"
    req_staff_2 = emp_list[1] if len(emp_list) > 1 else "阮文強"

    approved_dispatches = [
        {"工單編號": "APP-DISPATCH-2026-001", "申請部門": "管理部", "申請人": req_mgr_1, "車牌號碼": "61A-888.66", "用途說明": "載送總經理赴胡志明市開會", "主管簽核狀態": "🟢 總經理已核准 (Approved)"}
    ]

    # 📑 四大功能分頁
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
            st.markdown("### ➕ 登記車輛進出廠區門禁")
            available_vehicles = get_vehicle_options_from_assets(engine)
            c1, c2 = st.columns(2)
            with c1:
                selected_vehicle_option = st.selectbox("選擇車牌號碼", available_vehicles)
                plate = selected_vehicle_option.split(" ")[0] if selected_vehicle_option else ""
                driver = st.text_input("駕駛姓名與所屬單位", placeholder="例如: Nguyễn Văn B (物流外包)")
            with c2:
                v_type = st.selectbox("車輛類型", ["貨車 (Truck)", "公務車 (Company Car)", "訪客車 (Visitor)", "外包工程車"])
                direction = st.selectbox("進出方向", ["車輛入廠 (Check-In)", "車輛出廠 (Check-Out)"])

            purpose = st.text_area("入廠/出廠事由與載貨說明", placeholder="例如: 運送配電盤原物料銅排入廠")

            if st.form_submit_button("💾 記錄門禁進出時間", type="primary", use_container_width=True):
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
                    st.success(f"✅ 車輛 `{plate}` 門禁紀錄已成功登記！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫車牌號碼與駕駛姓名！")

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
        with st.form("form_visitor_record"):
            c1, c2 = st.columns(2)
            with c1:
                v_name = st.text_input("訪客 / 外包商姓名 *", placeholder="輸入全名...")
                v_company = st.text_input("所屬公司 / 單位 *", placeholder="例: 宏碁電腦 / 消防工程行")
                v_id = st.text_input("身分證號 / 護照號碼 (留置換證)", placeholder="CCCD / Passport ID...")
            with c2:
                v_target = st.selectbox("拜訪對象 / 員工 *", emp_list)
                v_pass_no = st.text_input("核發訪客證編號 (Visitor Pass)", placeholder="例: V-05")
                v_status = st.selectbox("進出狀態", ["🟢 剛入廠 (Check-In)", "🔴 已離廠 (Check-Out)"])

            v_note = st.text_input("拜訪事由與攜帶工具備註", placeholder="例: 廠區消防灑水系統定期維護...")

            if st.form_submit_button("🚀 登記訪客並發放訪客證", type="primary", use_container_width=True):
                if v_name and v_company:
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.visitor_gate_db.insert(0, {
                        "日期時間": now_str,
                        "訪客姓名": v_name,
                        "單位/公司": v_company,
                        "拜訪對象": v_target,
                        "證件號碼": v_id if v_id else "-",
                        "訪客證編號": v_pass_no if v_pass_no else "-",
                        "狀態": v_status
                    })
                    st.success(f"✅ 訪客 {v_name} ({v_company}) 登記成功！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫訪客姓名與所屬公司！")

        st.markdown("---")
        st.markdown(f"### {L['visitor_list_header']}")
        if st.session_state.visitor_gate_db:
            st.dataframe(pd.DataFrame(st.session_state.visitor_gate_db), use_container_width=True, hide_index=True)
        else:
            st.info("目前尚無訪客紀錄。")

    # Tab 4: 包裹信件代收管理
    with tab_parcel:
        st.markdown(f"### {L['parcel_header']}")
        with st.form("form_parcel_record"):
            c1, c2 = st.columns(2)
            with c1:
                p_courier = st.text_input("快遞公司 / 貨運來源 *", placeholder="例: Shopee Express, Viettel Post, 順豐...")
                p_receiver = st.selectbox("收件人 (連動員工名冊) *", emp_list)
                p_type = st.selectbox("物件類型", ["文件信封 (Envelope)", "包裹箱子 (Box)", "大宗貨物 (Pallet/Cargo)"])
            with c2:
                p_source = st.text_input("寄件人 / 來源公司", placeholder="例: 台北總公司、某某供應商...")
                p_status = st.selectbox("領取狀態", ["🟡 待領取 (Uncollected)", "🟢 已由本人領取 (Delivered)", "🟢 已由部門代收簽名 (Delegated)"])

            p_desc = st.text_input("快遞單號或備註說明", placeholder="例: 貨號 VT-998231，易碎品...")

            if st.form_submit_button("📦 登記代收包裹並通知", type="primary", use_container_width=True):
                if p_courier:
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.parcel_gate_db.insert(0, {
                        "登記日期": now_str,
                        "快遞公司": p_courier,
                        "收件人": p_receiver,
                        "物件類型": p_type,
                        "寄件來源": p_source if p_source else "-",
                        "領取狀態": p_status
                    })
                    st.success(f"✅ 包裹已成功代收登記，收件人：{p_receiver}")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫快遞公司或貨運來源！")

        st.markdown("---")
        st.markdown(f"### {L['parcel_list_header']}")
        if st.session_state.parcel_gate_db:
            st.dataframe(pd.DataFrame(st.session_state.parcel_gate_db), use_container_width=True, hide_index=True)
        else:
            st.info("目前尚無包裹代收紀錄。")

def show(*args, **kwargs):
    render_vehicle_gate_log_page(*args, **kwargs)

def main(*args, **kwargs):
    render_vehicle_gate_log_page(*args, **kwargs)

def render_vehicle_gate_log(*args, **kwargs):
    render_vehicle_gate_log_page(*args, **kwargs)
