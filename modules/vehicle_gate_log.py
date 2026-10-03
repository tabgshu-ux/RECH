import datetime
import pandas as pd
import streamlit as st

# ----------------------------------------------------
# 🌐 多語系字典 (i18n)
# ----------------------------------------------------
VEHICLE_I18N = {
    "繁體中文": {
        "title": "🚗 裕豐電機工業 - 廠區車輛門禁與公務車保養管理系統",
        "caption": "管理廠區車輛進出與公務車保養履歷（支援動態即時匯率換算與多語系切換）。",
        "tab1": "📑 廠區大門車輛進出動態",
        "tab2": "➕ 登記車輛進廠 (Check-In)",
        "tab3": "⏱️ 車輛離廠登記 (Check-Out)",
        "tab4": "🔧 公司公務車保養與維護履歷",
        "col_car_id": "車輛編號",
        "col_plate": "車牌號碼",
        "col_brand": "品牌型號",
        "col_purchase": "購買時間",
        "col_maint_date": "保養時間",
        "col_mileage": "行駛里程",
        "col_content": "保養維護內容",
        "col_cost": "保養金額 (雙軌顯示)",
        "col_handler": "經辦人",
        "maint_title": "🔧 公司公務車 / 廠長用車保養維護履歷管理",
        "maint_caption": "完整記錄公務車保養履歷，並自動依當下匯率計算越南盾與美金。",
        "add_maint": "➕ 新增公務車保養與維護紀錄",
    },
    "Tiếng Việt": {
        "title": "🚗 REETECH INDUSTRIAL - Quản lý Cổng xe & Bảo dưỡng Xe công ty",
        "caption": "Quản lý xe ra vào nhà máy và lịch sử bảo dưỡng xe công ty (Hỗ trợ tỷ giá động & đa ngôn ngữ).",
        "tab1": "📑 Theo dõi xe ra vào cổng",
        "tab2": "➕ Đăng ký xe vào cổng (Check-In)",
        "tab3": "⏱️ Đăng ký xe ra cổng (Check-Out)",
        "tab4": "🔧 Lịch sử bảo dưỡng xe công ty",
        "col_car_id": "Mã xe",
        "col_plate": "Biển số",
        "col_brand": "Hãng & Model",
        "col_purchase": "Ngày mua",
        "col_maint_date": "Ngày bảo dưỡng",
        "col_mileage": "Số km",
        "col_content": "Nội dung bảo dưỡng",
        "col_cost": "Chi phí (VND / USD)",
        "col_handler": "Người phụ trách",
        "maint_title": "🔧 Quản lý Lịch sử Bảo dưỡng Xe Công ty",
        "maint_caption": "Ghi lại chi tiết bảo dưỡng và tự động quy đổi tỷ giá VND/USD.",
        "add_maint": "➕ Thêm mới bản ghi bảo dưỡng",
    },
    "English": {
        "title": "🚗 REETECH INDUSTRIAL - Vehicle Gate & Company Car Maintenance",
        "caption": "Manage plant gate logs and company vehicle maintenance history with dynamic exchange rates.",
        "tab1": "📑 Gate Traffic Overview",
        "tab2": "➕ Vehicle Check-In",
        "tab3": "⏱️ Vehicle Check-Out",
        "tab4": "🔧 Company Car Maintenance History",
        "col_car_id": "Car ID",
        "col_plate": "Plate No.",
        "col_brand": "Brand & Model",
        "col_purchase": "Purchase Date",
        "col_maint_date": "Maintenance Date",
        "col_mileage": "Mileage",
        "col_content": "Maintenance Content",
        "col_cost": "Cost (Dual Currency)",
        "col_handler": "Handler",
        "maint_title": "🔧 Company Vehicle Maintenance History",
        "maint_caption": "Complete records of vehicle maintenance with automatic VND/USD calculation.",
        "add_maint": "➕ Add Maintenance Record",
    },
}


def get_lang_dict(lang_param):
    return VEHICLE_I18N.get(lang_param, VEHICLE_I18N["繁體中文"])


def render_vehicle_gate_log_page(engine=None, lang="繁體中文"):
    L = get_lang_dict(lang)

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化大門車輛進出紀錄
    if "vehicle_logs_db" not in st.session_state or not st.session_state.vehicle_logs_db:
        st.session_state.vehicle_logs_db = [
            {
                "log_id": "LOG-2026-001",
                "plant": "🇻🇳 越南西寧廠 (Tay Ninh Plant)",
                "plate_no": "61A-888.66",
                "vehicle_type": "🚛 運料大貨車 (原材料進廠)",
                "driver_name": "Nguyễn Văn Hùng",
                "purpose": "載運 500kg 銅排原料進廠",
                "entry_time": "2026-10-03 08:15:20",
                "exit_time": "2026-10-03 11:30:45",
                "status": "🟢 已離廠 (Completed)",
            },
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
                "exchange_rate_used": 0.0000385,
                "display_cost": "₫11,439,000 VND ($440.40 USD)",
                "handler": "張偉豪",
            }
        ]

    tab_gate_overview, tab_gate_in, tab_gate_out, tab_car_maint = st.tabs([
        L["tab1"],
        L["tab2"],
        L["tab3"],
        L["tab4"],
    ])

    # ----------------------------------------------------
    # 📑 頁籤一：大門車輛動態看板
    # ----------------------------------------------------
    with tab_gate_overview:
        st.markdown(f"### {L['tab1']}")
        inside_count = sum(1 for x in st.session_state.vehicle_logs_db if x["status"] == "🟡 廠區內執行任務")
        total_today = len(st.session_state.vehicle_logs_db)

        c1, c2, c3 = st.columns(3)
        c1.metric("🚗 今日累計進出車次", f"{total_today} 車次")
        c2.metric("🅿️️ 目前滯留廠區內車輛", f"{inside_count} 台")
        c3.metric("⏱️ 門禁系統狀態", "🟢 聯網運作中 (24/7)")

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
                plant = st.selectbox("進出廠區 *", ["🇻🇳 越南西寧廠 (Tay Ninh Plant)", "🇻🇳 越南海防廠 (Hai Phong Plant)"])
                plate_no = st.text_input("車牌號碼 *", value="", placeholder="例如: 61A-123.45")
                vehicle_type = st.selectbox("車輛類型 *", ["🚛 運料大貨車 (原材料)", "🚚 成品出貨貨車", "🚐 廠長/公務用車", "🚗 訪客外賓車輛", "🏍️ 員工機車"])
            with c2:
                driver_name = st.text_input("駕駛員 / 司機姓名 *", value="")
                purpose = st.text_input("進廠事由 / 載運內容 *", value="載運配電盤零組件")
                entry_time = st.text_input("進廠時間 (自動記錄)", value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if st.form_submit_button("💾 記錄車輛進廠", type="primary", use_container_width=True):
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
                    st.success("🎉 【進廠登記成功】已完成時間紀錄！")
                    st.rerun()
                else:
                    st.error("❌ 請填寫車牌號碼與駕駛員姓名！")

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
                    if st.button(f"🏁 登記離廠 ({veh['plate_no']})", key=f"checkout_{veh['log_id']}_v"):
                        veh["exit_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        veh["status"] = "🟢 已離廠 (Completed)"
                        st.success("✅ 已完成離廠時間記錄！")
                        st.rerun()
                st.divider()
        else:
            st.success("🎉 目前廠區內所有登記車輛均已離廠！")

        df_all = pd.DataFrame(st.session_state.vehicle_logs_db)
        st.dataframe(df_all, use_container_width=True)

    # ----------------------------------------------------
    # 🔧 頁籤四：公司公務車保養與維護履歷管理（自動對應語系表頭）
    # ----------------------------------------------------
    with tab_car_maint:
        st.markdown(f"### {L['maint_title']}")
        st.caption(L["maint_caption"])

        # 整理顯示資料：將英文資料庫欄位名稱轉換為當前選擇的語系名稱
        display_maint_data = []
        for item in st.session_state.company_car_maintenance_db:
            display_maint_data.append({
                L["col_car_id"]: item["car_id"],
                L["col_plate"]: item["plate_no"],
                L["col_brand"]: item["brand_model"],
                L["col_purchase"]: item["purchase_date"],
                L["col_maint_date"]: item["maint_date"],
                L["col_mileage"]: item["mileage"],
                L["col_content"]: item["maint_content"],
                L["col_cost"]: item["display_cost"],
                L["col_handler"]: item["handler"],
            })

        df_maint = pd.DataFrame(display_maint_data)
        st.dataframe(df_maint, use_container_width=True)

        st.markdown("---")
        st.markdown(f"#### {L['add_maint']}")

        with st.form("form_add_car_maintenance_dynamic"):
            c1, c2, c3 = st.columns(3)
            with c1:
                plate_no = st.text_input("車牌號碼 / Biển số *", value="61A-888.66")
                brand_model = st.text_input("車輛品牌型號 / Hãng *", value="Toyota Fortuner 2.8L")
            with c2:
                purchase_date = st.date_input("購買時間 / Ngày mua", value=datetime.date(2023, 5, 15))
                maint_date = st.date_input("保養時間 / Ngày bảo dưỡng", value=datetime.date.today())
            with c3:
                mileage = st.text_input("行駛公里數 / Số km *", value="70,000 km")
                input_currency = st.selectbox("原始幣別 / Tiền tệ", ["🇻🇳 越南盾 (VND)", "💵 美金 (USD)"])

            st.markdown("##### 💱 當下匯率設定 / Tỷ giá hiện tại")
            rc1, rc2 = st.columns(2)
            with rc1:
                current_rate = st.number_input(
                    "當下匯率 (1 VND = ? USD)", 
                    min_value=0.000001, 
                    value=0.000038, 
                    format="%.7f"
                )
            with rc2:
                raw_amount = st.number_input(
                    "保養維護原始金額 / Số tiền *", 
                    min_value=0.0, 
                    value=1000000.0 if "越南盾" in input_currency else 38.48, 
                    step=10.0
                )

            if "越南盾" in input_currency:
                calc_vnd = raw_amount
                calc_usd = raw_amount * current_rate
                preview_str = f"₫{calc_vnd:,.0f} VND ➔ ${calc_usd:.2f} USD"
            else:
                calc_usd = raw_amount
                calc_vnd = raw_amount / current_rate if current_rate > 0 else 0
                preview_str = f"${calc_usd:,.2f} USD ➔ ₫{calc_vnd:,.0f} VND"

            st.info(f"📊 **匯率換算預覽 / Xem trước quy đổi**：{preview_str}")

            maint_content = st.text_area("保養維護內容與細節說明 / Nội dung bảo dưỡng *", value="定期保養：更換機油、機油濾清器、煞車系統檢查。")
            handler = st.text_input("經辦人 / Người phụ trách", value="張偉豪")

            if st.form_submit_button("💾 儲存公務車保養紀錄 / Lưu", type="primary", use_container_width=True):
                if plate_no and brand_model and maint_content:
                    if "越南盾" in input_currency:
                        final_vnd = raw_amount
                        final_usd = raw_amount * current_rate
                        display_str = f"₫{final_vnd:,.0f} VND (${final_usd:.2f} USD)"
                    else:
                        final_usd = raw_amount
                        final_vnd = raw_amount / current_rate if current_rate > 0 else 0
                        display_str = f"${final_usd:.2f} USD (₫{final_vnd:,.0f} VND)"

                    st.session_state.company_car_maintenance_db.append({
                        "car_id": f"CAR-{len(st.session_state.company_car_maintenance_db)+1:02d}",
                        "plate_no": plate_no.upper(),
                        "brand_model": brand_model,
                        "purchase_date": str(purchase_date),
                        "maint_date": str(maint_date),
                        "mileage": mileage,
                        "maint_content": maint_content,
                        "exchange_rate_used": current_rate,
                        "display_cost": display_str,
                        "handler": handler,
                    })
                    st.success("🎉 【新增完成】已依照當下匯率精算並儲存！")
                    st.rerun()
                else:
                    st.error("❌ 請完整填寫必填欄位！")


def show(engine=None, lang="繁體中文"):
    render_vehicle_gate_log_page(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_vehicle_gate_log_page(engine, lang)
