import datetime
import pandas as pd
import streamlit as st

SYSTEM_EXCHANGE_RATE_VND_TO_USD = 0.00003934

# ----------------------------------------------------
# 🌐 多語系字典 (i18n)
# ----------------------------------------------------
VEHICLE_I18N = {
    "繁體中文": {
        "title": "🚗 裕豐電機工業 - 廠區車輛門禁與公務車派車審核系統",
        "caption": "📱 整合廠區大門車輛進出、公務車保養履歷與「公務用車派車單及主管簽核管制」。",
        "tab1": "📑 廠區大門車輛進出動態",
        "tab2": "➕ 登記車輛進廠 (Check-In)",
        "tab3": "⏱️ 車輛離廠登記 (Check-Out)",
        "tab4": "📝 公務派車單與放行管制",
        "tab5": "🔧 公司公務車保養與維護履歷",
        "col_car_id": "車輛編號",
        "col_plate": "車牌號碼",
        "col_brand": "品牌型號",
        "col_purchase": "購買時間",
        "col_maint_date": "保養時間",
        "col_mileage": "行駛里程",
        "col_content": "保養維護內容",
        "col_cost": "保養金額 (財務雙軌換算)",
        "col_handler": "經辦人",
        "maint_title": "🔧 公司公務車 / 廠長用車保養維護履歷管理",
        "maint_caption": "完整記錄公務車保養履歷，輸入金額後由後台自動為財務換算雙幣別。",
        "add_maint": "➕ 新增公務車保養與維護紀錄",
        "plant_label": "進出廠區 *",
        "plate_label": "車牌號碼 *",
        "type_label": "車輛類型 *",
        "driver_label": "駕駛員 / 司機姓名 *",
        "purpose_label": "進廠事由 / 載運內容 *",
        "time_label": "進廠時間 (自動記錄)",
        "submit_in": "💾 記錄車輛進廠",
        "success_in": "🎉 【進廠登記成功】已完成時間紀錄！",
        "error_in": "❌ 請填寫車牌號碼與駕駛員姓名！",
        "checkout_btn": "🏁 登記離廠",
        "success_out": "✅ 已完成離廠時間記錄！",
        "no_active": "🎉 目前廠區內所有登記車輛均已離廠！",
        "history_title": "📜 所有進出紀錄總表",
        "cur_label": "選擇支付幣別 / Tiền tệ",
        "amount_label": "本次維修支付金額 *",
        "content_label": "保養維護內容與細節說明 *",
        "handler_label": "經辦人 / 申請人",
        "save_maint": "💾 儲存公務車保養紀錄",
        "success_maint": "🎉 【新增完成】保養紀錄已儲存，後台已自動完成財務換算！",
        "dispatch_title": "📝 公務派車單申請與保全放行管制中心",
        "dispatch_caption": "員工因公外出需申請公務車，經單位主管簽核通過後，保全大門系統將自動顯示放行授權。",
        "apply_tab": "✍️ 填寫新派車申請單",
        "audit_tab": "🛡️ 主管簽核與保全大門放行檢視",
        "security_list_title": "🛡️ 保全大門管制專用：已核准放行之公務派車清單",
        "security_list_caption": "💡 保全人員在門口放行因公外出車輛時，請核對下方「主管已簽核」之派車單與車牌號碼。",
        "dispatcher_name": "申請人姓名 *",
        "dispatch_plate": "指派公務車牌 *",
        "dispatch_dest": "外出目的地 / 客戶/ 案場 *",
        "dispatch_reason": "因公事由說明 *",
        "submit_dispatch": "📤 送出派車申請並呈報主管",
        "success_dispatch": "🎉 【派車單已送出】已發送至部門主管進行線上簽核！",
        "vehicle_types": [
            "🚛 運料大貨車 (原材料)", 
            "🚚 成品出貨貨車", 
            "🚐 廠長/公務用車", 
            "🚗 訪客外賓車輛", 
            "🏍️ 員工機車"
        ],
        "plants": [
            "🇻🇳 越南西寧廠 (Tay Ninh Plant)", 
            "🇻🇳 越南海防廠 (Hai Phong Plant)"
        ]
    },
    "Tiếng Việt": {
        "title": "🚗 REETECH INDUSTRIAL - Quản lý Cổng xe & Phê duyệt Lệnh điều xe",
        "caption": "📱 Quản lý xe ra vào, bảo dưỡng xe công ty và hệ thống \"Đăng ký & Phê duyệt lệnh điều xe công vụ\".",
        "tab1": "📑 Theo dõi xe ra vào cổng",
        "tab2": "➕ Đăng ký xe vào cổng (Check-In)",
        "tab3": "⏱️ Đăng ký xe ra cổng (Check-Out)",
        "tab4": "📝 Quản lý Lệnh điều xe & Kiểm tra",
        "tab5": "🔧 Lịch sử bảo dưỡng xe công ty",
        "col_car_id": "Mã xe",
        "col_plate": "Biển số",
        "col_brand": "Hãng & Model",
        "col_purchase": "Ngày mua",
        "col_maint_date": "Ngày bảo dưỡng",
        "col_mileage": "Số km",
        "col_content": "Nội dung bảo dưỡng",
        "col_cost": "Chi phí (Quy đổi tự động)",
        "col_handler": "Người phụ trách",
        "maint_title": "🔧 Quản lý Lịch sử Bảo dưỡng Xe Công ty",
        "maint_caption": "Ghi lại chi tiết bảo dưỡng, hệ thống tự động quy đổi VND/USD cho bộ phận tài chính.",
        "add_maint": "➕ Thêm mới bản ghi bảo dưỡng",
        "plant_label": "Khu vực nhà máy *",
        "plate_label": "Biển số xe *",
        "type_label": "Loại xe *",
        "driver_label": "Tên tài xế *",
        "purpose_label": "Lý do vào cổng / Hàng hóa *",
        "time_label": "Thời gian vào (Tự động)",
        "submit_in": "💾 Ghi nhận xe vào cổng",
        "success_in": "🎉 Đăng ký xe vào thành công!",
        "error_in": "❌ Vui lòng nhập biển số và tên tài xế!",
        "checkout_btn": "🏁 Đăng ký ra cổng",
        "success_out": "✅ Đã ghi nhận thời gian xe ra!",
        "no_active": "🎉 Hiện tại không có xe nào trong nhà máy!",
        "history_title": "📜 Tổng hợp lịch sử ra vào",
        "cur_label": "Tiền tệ thanh toán",
        "amount_label": "Số tiền bảo dưỡng thực tế *",
        "content_label": "Nội dung chi tiết bảo dưỡng *",
        "handler_label": "Người phụ trách",
        "save_maint": "💾 Lưu bản ghi bảo dưỡng",
        "success_maint": "🎉 Đã lưu thành công và hệ thống đã tự động quy đổi tài chính!",
        "dispatch_title": "📝 Quản lý Lệnh điều xe công vụ & Kiểm tra cổng bảo vệ",
        "dispatch_caption": "Nhân viên đi công tác cần đăng ký xe, sau khi Quản lý phê duyệt, hệ thống Bảo vệ cổng sẽ tự động cấp phép.",
        "apply_tab": "✍️ Tạo đơn xin sử dụng xe",
        "audit_tab": "🛡️ Quản lý duyệt đơn & Bảo vệ kiểm tra cổng",
        "security_list_title": "🛡️ Danh sách xe công vụ đã được phê duyệt",
        "security_list_caption": "💡 Khi bảo vệ cho phép xe công vụ ra cổng, vui lòng đối chiếu đơn xe và biển số xe đã được Quản lý phê duyệt bên dưới.",
        "dispatcher_name": "Tên nhân viên xin dùng xe *",
        "dispatch_plate": "Biển số xe công vụ *",
        "dispatch_dest": "Điểm đến / Khách hàng / Công trình *",
        "dispatch_reason": "Lý do công tác *",
        "submit_dispatch": "📤 Gửi đơn xin sử dụng xe cho Quản lý",
        "success_dispatch": "🎉 Đã gửi đơn thành công! Đang chờ Quản lý phê duyệt.",
        "vehicle_types": [
            "🚛 Xe tải chở nguyên liệu (Vật liệu thô)", 
            "🚚 Xe tải xuất hàng thành phẩm", 
            "🚐 Xe công vụ / Xe giám đốc", 
            "🚗 Xe khách / Khách vãng lai", 
            "🏍️ Xe máy nhân viên"
        ],
        "plants": [
            "🇻🇳 Nhà máy Tây Ninh (Tay Ninh Plant)", 
            "🇻🇳 Nhà máy Hải Phòng (Hai Phong Plant)"
        ]
    },
    "English": {
        "title": "🚗 REETECH INDUSTRIAL - Vehicle Gate & Dispatch Approval Center",
        "caption": "📱 Manage plant gate traffic, maintenance history, and official vehicle dispatch approval workflows.",
        "tab1": "📑 Gate Traffic Overview",
        "tab2": "➕ Vehicle Check-In",
        "tab3": "⏱️ Vehicle Check-Out",
        "tab4": "📝 Dispatch & Gate Control",
        "tab5": "🔧 Company Car Maintenance History",
        "col_car_id": "Car ID",
        "col_plate": "Plate No.",
        "col_brand": "Brand & Model",
        "col_purchase": "Purchase Date",
        "col_maint_date": "Maintenance Date",
        "col_mileage": "Mileage",
        "col_content": "Maintenance Content",
        "col_cost": "Cost (Backend Converted)",
        "col_handler": "Handler",
        "maint_title": "🔧 Company Vehicle Maintenance History",
        "maint_caption": "Complete records with automatic currency conversion for financial reporting.",
        "add_maint": "➕ Add Maintenance Record",
        "plant_label": "Plant *",
        "plate_label": "Plate No. *",
        "type_label": "Vehicle Type *",
        "driver_label": "Driver Name *",
        "purpose_label": "Purpose / Cargo *",
        "time_label": "Entry Time (Auto)",
        "submit_in": "💾 Check-In Vehicle",
        "success_in": "🎉 Vehicle checked in successfully!",
        "error_in": "❌ Please enter plate number and driver name!",
        "checkout_btn": "🏁 Check-Out",
        "success_out": "✅ Vehicle checked out successfully!",
        "no_active": "🎉 All registered vehicles have left the plant!",
        "history_title": "📜 All Gate Logs Overview",
        "cur_label": "Payment Currency",
        "amount_label": "Actual Maintenance Amount *",
        "content_label": "Maintenance Details *",
        "handler_label": "Handler",
        "save_maint": "💾 Save Maintenance Record",
        "success_maint": "🎉 Maintenance record saved and automatically converted for finance!",
        "dispatch_title": "📝 Official Vehicle Dispatch & Security Gate Control",
        "dispatch_caption": "Submit dispatch orders for official business trips. Security gate will display approved permits for exit.",
        "apply_tab": "✍️ Apply for Vehicle Dispatch",
        "audit_tab": "🛡️ Manager Approval & Security Gate Inspection",
        "security_list_title": "🛡️ Security Gate Control: Approved Official Vehicle Dispatch List",
        "security_list_caption": "💡 Please verify the approved dispatch order and license plate before releasing vehicles.",
        "dispatcher_name": "Applicant Name *",
        "dispatch_plate": "Company Vehicle Plate *",
        "dispatch_dest": "Destination / Client / Site *",
        "dispatch_reason": "Business Purpose *",
        "submit_dispatch": "📤 Submit Dispatch Request to Manager",
        "success_dispatch": "🎉 Dispatch request submitted! Awaiting manager approval.",
        "vehicle_types": [
            "🚛 Raw Material Truck", 
            "🚚 Finished Goods Truck", 
            "🚐 Company / Director Car", 
            "🚗 Visitor Vehicle", 
            "🏍️ Employee Motorcycle"
        ],
        "plants": [
            "🇻🇳 Tay Ninh Plant", 
            "🇻🇳 Hai Phong Plant"
        ]
    },
}


def get_lang_dict(lang_param):
    return VEHICLE_I18N.get(lang_param, VEHICLE_I18N["繁體中文"])


def render_vehicle_gate_log_page(engine=None, lang="繁體中文"):
    current_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = get_lang_dict(current_lang)

    st.title(L["title"])
    st.caption(L["caption"])

    # 取得目前登入者的角色
    user_role = str(st.session_state.get("user_role", "")).strip().lower()
    is_security_guard = (user_role == "security")

    # 初始化大門車輛進出紀錄
    if "vehicle_logs_db" not in st.session_state or not st.session_state.vehicle_logs_db:
        st.session_state.vehicle_logs_db = [
            {
                "log_id": "LOG-2026-001",
                "plant": L["plants"][0],
                "plate_no": "61A-888.66",
                "vehicle_type": L["vehicle_types"][0],
                "driver_name": "Nguyễn Văn Hùng",
                "purpose": "載運 500kg 銅排原料進廠",
                "entry_time": "2026-10-03 08:15:20",
                "exit_time": "2026-10-03 11:30:45",
                "status": "🟢 已離廠 (Completed)",
            },
        ]

    # 初始化公務派車單資料庫
    if "vehicle_dispatch_db" not in st.session_state:
        st.session_state.vehicle_dispatch_db = [
            {
                "dispatch_id": "DISP-2026-001",
                "applicant": "Nguyễn Văn An",
                "plate_no": "61A-888.66",
                "destination": "胡志明市第一工廠 (HCMC Plant)",
                "reason": "拜訪客戶並進行配電盤技術交流",
                "apply_time": "2026-10-03 09:00",
                "approval_status": "🟢 主管已簽核 (Approved)",
                "security_status": "🚗 保安已放行 (Checked Out)",
            }
        ]

    # 初始化公務車保養維護履歷
    if "company_car_maintenance_db" not in st.session_state or not st.session_state.company_car_maintenance_db:
        st.session_state.company_car_maintenance_db = [
            {
                "car_id": "CAR-01",
                "plate_no": "61A-888.66",
                "brand_model": "Toyota Fortuner 2.8L (商務公務車)",
                "purchase_date": "2023-05-15",
                "maint_date": "2026-09-10",
                "mileage": "65,400 km",
                "maint_content": "更換機油、煞車皮檢查",
                "display_cost": "₫11,439,000 VND ($440.40 USD)",
                "handler": "張偉豪",
            }
        ]

    # 💡 權限過濾：若為保全角色，則不顯示車輛維修保養履歷頁籤
    if is_security_guard:
        tab_gate_overview, tab_gate_in, tab_gate_out, tab_dispatch = st.tabs([
            L["tab1"],
            L["tab2"],
            L["tab3"],
            L["tab4"],
        ])
    else:
        tab_gate_overview, tab_gate_in, tab_gate_out, tab_dispatch, tab_car_maint = st.tabs([
            L["tab1"],
            L["tab2"],
            L["tab3"],
            L["tab4"],
            L["tab5"],
        ])

    # ----------------------------------------------------
    # 📑 頁籤一：大門車輛動態看板
    # ----------------------------------------------------
    with tab_gate_overview:
        st.markdown(f"### {L['tab1']}")
        inside_count = sum(1 for x in st.session_state.vehicle_logs_db if x["status"] == "🟡 廠區內執行任務")
        total_today = len(st.session_state.vehicle_logs_db)

        c1, c2, c3 = st.columns(3)
        c1.metric("🚗 車次 / Chuyến xe", f"{total_today}")
        c2.metric("🅿️ 廠內 / Trong kho", f"{inside_count}")
        c3.metric("⏱ 狀態 / Trạng thái", "🟢 24/7")

        st.divider()
        df_logs = pd.DataFrame(st.session_state.vehicle_logs_db)
        st.dataframe(df_logs, use_container_width=True)

    # ----------------------------------------------------
    # ➕ 頁籤二：登記車輛進廠
    # ----------------------------------------------------
    with tab_gate_in:
        st.markdown(f"### {L['tab2']}")
        with st.form("form_vehicle_entry"):
            c1, c2 = st.columns(2)
            with c1:
                plant = st.selectbox(L["plant_label"], L["plants"])
                plate_no = st.text_input(L["plate_label"], value="", placeholder="例如: 61A-123.45")
                vehicle_type = st.selectbox(L["type_label"], L["vehicle_types"])
            with c2:
                driver_name = st.text_input(L["driver_label"], value="")
                purpose = st.text_input(L["purpose_label"], value="載運配電盤零組件")
                entry_time = st.text_input(L["time_label"], value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if st.form_submit_button(L["submit_in"], type="primary", use_container_width=True):
                if plate_no and driver_name:
                    new_id = f"LOG-2026-{len(st.session_state.vehicle_logs_db)+1:03d}"
                    st.session_state.vehicle_logs_db.append({
                        "log_id": new_id,
                        "plant": plant,
                        "plate_no": plate_no.upper(),
                        "vehicle_type": vehicle_type,
                        "driver_name": driver_name,
                        "purpose": purpose,
                        "entry_time": entry_time,
                        "exit_time": "-",
                        "status": "🟡 廠區內執行任務",
                    })
                    st.success(L["success_in"])
                    st.rerun()
                else:
                    st.error(L["error_in"])

    # ----------------------------------------------------
    # ⏱️ 頁籤三：車輛離廠登記
    # ----------------------------------------------------
    with tab_gate_out:
        st.markdown(f"### {L['tab3']}")
        active_vehicles = [x for x in st.session_state.vehicle_logs_db if x["status"] == "🟡 廠區內執行任務"]

        if active_vehicles:
            for veh in active_vehicles:
                with st.container():
                    st.markdown(f"**🚗 車牌: `{veh['plate_no']}`** | 廠區: {veh['plant']} | 司機: {veh['driver_name']}")
                    if st.button(f"{L['checkout_btn']} ({veh['plate_no']})", key=f"checkout_{veh['log_id']}_v"):
                        veh["exit_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        veh["status"] = "🟢 已離廠 (Completed)"
                        st.success(L["success_out"])
                        st.rerun()
                st.divider()
        else:
            st.success(L["no_active"])

        st.markdown(f"#### {L['history_title']}")
        df_all = pd.DataFrame(st.session_state.vehicle_logs_db)
        st.dataframe(df_all, use_container_width=True)

    # ----------------------------------------------------
    # 📝 頁籤四：公務派車單申請與保全放行管制
    # ----------------------------------------------------
    with tab_dispatch:
        st.markdown(f"### {L['dispatch_title']}")
        st.caption(L["dispatch_caption"])

        # 🛡️ 關鍵權限控制：若為保全帳號，直接強制顯示「保全檢視清單」，不顯示任何申請提示與表單！
        if is_security_guard:
            st.markdown(f"#### {L['security_list_title']}")
            st.info(L["security_list_caption"])
            
            for idx, item in enumerate(st.session_state.vehicle_dispatch_db):
                with st.expander(f"🚗 派車單號: `{item['dispatch_id']}` | 申請人: {item['applicant']} | 車牌: {item['plate_no']} ({item['approval_status']})"):
                    st.write(f"- **目的地**: {item['destination']}")
                    st.write(f"- **用車事由**: {item['reason']}")
                    st.write(f"- **主管簽核狀態**: {item['approval_status']}")
                    st.write(f"- **保全放行狀態**: {item['security_status']}")

                    col_sec_btn = st.columns(1)
                    with col_sec_btn[0]:
                        if st.button("🏁 保全確認車輛離廠放行", key=f"sec_out_guard_{idx}", use_container_width=True):
                            if "已簽核" in item["approval_status"]:
                                item["security_status"] = "🚗 保全已放行離廠 (Dispatched)"
                                st.success("✅ 保全已完成車輛離廠放行登記！")
                                st.rerun()
                            else:
                                st.error("❌ 尚未取得主管簽核，保全無法放行！")
        else:
            # 非保全人員（一般員工/主管/Admin）可以看到完整子頁籤：申請表單 + 審核檢視
            sub_tab_apply, sub_tab_audit = st.tabs([L["apply_tab"], L["audit_tab"]])

            with sub_tab_apply:
                with st.form("form_dispatch_apply"):
                    c1, c2 = st.columns(2)
                    with c1:
                        dispatcher_name = st.text_input(L["dispatcher_name"], value=st.session_state.get("user_name", ""))
                        dispatch_plate = st.text_input(L["dispatch_plate"], value="61A-888.66 (Toyota Fortuner)")
                    with c2:
                        dispatch_dest = st.text_input(L["dispatch_dest"], value="胡志明市工業區客戶廠房")
                        apply_time = st.text_input("申請時間 (自動記錄)", value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

                    dispatch_reason = st.text_area(L["dispatch_reason"], value="因公外出拜訪客戶進行配電盤維護與技術支援。")

                    if st.form_submit_button(L["submit_dispatch"], type="primary", use_container_width=True):
                        if dispatcher_name and dispatch_reason:
                            new_dispatch = {
                                "dispatch_id": f"DISP-2026-{len(st.session_state.vehicle_dispatch_db)+1:03d}",
                                "applicant": dispatcher_name,
                                "plate_no": dispatch_plate,
                                "destination": dispatch_dest,
                                "reason": dispatch_reason,
                                "apply_time": apply_time,
                                "approval_status": "⏳ 待主管簽核 (Pending)",
                                "security_status": "🔒 等待主管放行授權",
                            }
                            st.session_state.vehicle_dispatch_db.insert(0, new_dispatch)
                            st.success(L["success_dispatch"])
                            st.rerun()
                        else:
                            st.error("❌ 請完整填寫申請人姓名與用車事由！")

            with sub_tab_audit:
                st.markdown("#### 🛡️ 主管簽核與保全大門放行管理")
                st.info("💡 主管可進行線上簽核，保全人員可於此核對已核准之派車單與車牌號碼。")

                for idx, item in enumerate(st.session_state.vehicle_dispatch_db):
                    with st.expander(f"🚗 派車單號: `{item['dispatch_id']}` | 申請人: {item['applicant']} | 車牌: {item['plate_no']} ({item['approval_status']})"):
                        st.write(f"- **目的地**: {item['destination']}")
                        st.write(f"- **用車事由**: {item['reason']}")
                        st.write(f"- **主管簽核狀態**: {item['approval_status']}")
                        st.write(f"- **保全放行狀態**: {item['security_status']}")

                        col_act1, col_act2, col_act3 = st.columns(3)
                        with col_act1:
                            if st.button("✅ 主管核准簽核", key=f"approve_{idx}"):
                                item["approval_status"] = "🟢 主管已簽核 (Approved)"
                                item["security_status"] = "🟢 授權放行 (Ready to Exit)"
                                st.success("✅ 已完成主管簽核，保全系統已同步顯示放行授權！")
                                st.rerun()
                        with col_act2:
                            if st.button("❌ 主管駁回申請", key=f"reject_{idx}"):
                                item["approval_status"] = "🔴 主管已駁回 (Rejected)"
                                item["security_status"] = "⛔ 禁止通行"
                                st.warning("⚠️ 已駁回該筆派車申請。")
                                st.rerun()
                        with col_act3:
                            if st.button("🏁 保全確認車輛離廠", key=f"sec_out_{idx}"):
                                if "已簽核" in item["approval_status"]:
                                    item["security_status"] = "🚗 保全已放行離廠 (Dispatched)"
                                    st.success("✅ 保全已完成車輛離廠放行登記！")
                                    st.rerun()
                                else:
                                    st.error("❌ 尚未取得主管簽核，保全無法放行！")

    # ----------------------------------------------------
    # 🔧 頁籤五：公司公務車保養與維護履歷管理 (僅限非保全角色顯示)
    # ----------------------------------------------------
    if not is_security_guard:
        with tab_car_maint:
            st.markdown(f"### {L['maint_title']}")
            st.caption(L["maint_caption"])

            display_maint_data = []
            for item in st.session_state.company_car_maintenance_db:
                display_maint_data.append({
                    L["col_car_id"]: item.get("car_id", "CAR-01"),
                    L["col_plate"]: item.get("plate_no", ""),
                    L["col_brand"]: item.get("brand_model", ""),
                    L["col_purchase"]: item.get("purchase_date", ""),
                    L["col_maint_date"]: item.get("maint_date", ""),
                    L["col_mileage"]: item.get("mileage", ""),
                    L["col_content"]: item.get("maint_content", ""),
                    L["col_cost"]: item.get("display_cost", ""),
                    L["col_handler"]: item.get("handler", ""),
                })

            df_maint = pd.DataFrame(display_maint_data)
            st.dataframe(df_maint, use_container_width=True)

            st.markdown("---")
            st.markdown(f"#### {L['add_maint']}")

            with st.form("form_add_car_maintenance_clean"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    plate_no = st.text_input(L["col_plate"] + " *", value="61A-888.66")
                    brand_model = st.text_input(L["col_brand"] + " *", value="Toyota Fortuner 2.8L")
                with c2:
                    purchase_date = st.date_input(L["col_purchase"], value=datetime.date(2023, 5, 15))
                    maint_date = st.date_input(L["col_maint_date"], value=datetime.date.today())
                with c3:
                    mileage = st.text_input(L["col_mileage"] + " *", value="70,000 km")
                    input_currency = st.selectbox(L["cur_label"], ["🇻🇳 越南盾 (VND)", "💵 美金 (USD)"])

                raw_amount = st.number_input(
                    L["amount_label"], 
                    min_value=0.0, 
                    value=1000000.0 if "越南盾" in input_currency else 40.0, 
                    step=10.0
                )

                maint_content = st.text_area(L["content_label"], value="定期保養：更換機油、機油濾清器、煞車系統檢查。")
                handler = st.text_input(L["handler_label"], value="張偉豪")

                if st.form_submit_button(L["save_maint"], type="primary", use_container_width=True):
                    if plate_no and brand_model and maint_content:
                        if "越南盾" in input_currency:
                            final_vnd = raw_amount
                            final_usd = raw_amount * SYSTEM_EXCHANGE_RATE_VND_TO_USD
                            display_str = f"₫{final_vnd:,.0f} VND ($ {final_usd:,.2f} USD)"
                        else:
                            final_usd = raw_amount
                            final_vnd = raw_amount / SYSTEM_EXCHANGE_RATE_VND_TO_USD
                            display_str = f"${final_usd:,.2f} USD (₫{final_vnd:,.0f} VND)"

                        st.session_state.company_car_maintenance_db.append({
                            "car_id": f"CAR-{len(st.session_state.company_car_maintenance_db)+1:02d}",
                            "plate_no": plate_no.upper(),
                            "brand_model": brand_model,
                            "purchase_date": str(purchase_date),
                            "maint_date": str(maint_date),
                            "mileage": mileage,
                            "maint_content": maint_content,
                            "display_cost": display_str,
                            "handler": handler,
                        })
                        st.success(L["success_maint"])
                        st.rerun()
                    else:
                        st.error("❌ 請完整填寫必填欄位！")


def show(engine=None, lang="繁體中文"):
    render_vehicle_gate_log_page(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_vehicle_gate_log_page(engine, lang)
