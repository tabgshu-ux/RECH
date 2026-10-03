import datetime
import pandas as pd
import streamlit as st


def render_vehicle_gate_log_page(engine=None, lang="繁體中文"):
    st.title("🚗 裕豐電機工業 - 廠區車輛門禁與公務車保養管理系統")
    st.caption("管理西寧廠/海防廠大門口車輛進出紀錄，以及公司公務車輛之購買、保養維護履歷與費用追蹤。")

    # 1. 初始化廠區大門車輛進出紀錄資料庫
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

    # 2. 初始化公司公務車保養維護履歷資料庫
    if "company_car_maintenance_db" not in st.session_state or not st.session_state.company_car_maintenance_db:
        st.session_state.company_car_maintenance_db = [
            {
                "car_id": "CAR-01",
                "plate_no": "61A-888.66",
                "brand_model": "Toyota Fortuner 2.8L (商務公務車)",
                "purchase_date": "2023-05-15",
                "maint_date": "2026-09-10",
                "mileage": "65,400 km",
                "maint_content": "更換機油、煞車皮檢查、四輪定位與冷氣濾網更換",
                "cost": "$450 USD",
                "handler": "張偉豪",
            }
        ]

    tab_gate_overview, tab_gate_in, tab_gate_out, tab_car_maint = st.tabs([
        "📑 廠區大門車輛進出動態",
        "➕ 登記車輛進廠 (Check-In)",
        "⏱️ 車輛離廠登記 (Check-Out)",
        "🔧 公司公務車保養與維護履歷"
    ])

    # ----------------------------------------------------
    # 📑 頁籤一：大門車輛動態看板
    # ----------------------------------------------------
    with tab_gate_overview:
        st.markdown("### 📊 廠區大門車輛進出即時動態")
        
        inside_count = sum(1 for x in st.session_state.vehicle_logs_db if x["status"] == "🟡 廠區內執行任務")
        total_today = len(st.session_state.vehicle_logs_db)

        c1, c2, c3 = st.columns(3)
        c1.metric("🚗 今日累計進出車次", f"{total_today} 車次")
        c2.metric("🅿️ 目前滯留廠區內車輛", f"{inside_count} 台")
        c3.metric("⏱️ 門禁系統狀態", "🟢 聯網運作中 (24/7)")

        st.divider()
        st.markdown("#### 📋 車輛進出即時紀錄清單")
        df_logs = pd.DataFrame(st.session_state.vehicle_logs_db)
        st.dataframe(df_logs, use_container_width=True)

    # ----------------------------------------------------
    # ➕ 頁籤二：登記車輛進廠 (Check-In)
    # ----------------------------------------------------
    with tab_gate_in:
        st.markdown("### ➕ 登記廠區大門車輛進廠 (Gate Check-In)")

        with st.form("form_vehicle_entry"):
            c1, c2 = st.columns(2)
            with c1:
                plant = st.selectbox(
                    "進出廠區 *",
                    ["🇻🇳 越南西寧廠 (Tay Ninh Plant)", "🇻🇳 越南海防廠 (Hai Phong Plant)"]
                )
                plate_no = st.text_input("車牌號碼 *", value="", placeholder="例如: 61A-123.45")
                vehicle_type = st.selectbox(
                    "車輛類型 *",
                    ["🚛 運料大貨車 (原材料)", "🚚 成品出貨貨車", "🚐 廠長/公務用車", "🚗 訪客外賓車輛", "🏍️ 員工機車"]
                )
            with c2:
                driver_name = st.text_input("駕駛員 / 司機姓名 *", value="")
                purpose = st.text_input("進廠事由 / 載運內容 *", value="載運配電盤零組件")
                entry_time = st.text_input(
                    "進廠時間 (自動記錄)", 
                    value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

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
                    st.success(f"🎉 【進廠登記成功】車牌 [{plate_no.upper}] 已完成時間紀錄！")
                    st.rerun()
                else:
                    st.error("❌ 請填寫車牌號碼與駕駛員姓名！")

    # ----------------------------------------------------
    # ⏱️ 頁籤三：車輛離廠登記 (Check-Out)
    # ----------------------------------------------------
    with tab_gate_out:
        st.markdown("### ⏱️ 車輛離廠登記 (Gate Check-Out)")
        active_vehicles = [x for x in st.session_state.vehicle_logs_db if x["status"] == "🟡 廠區內執行任務"]

        if active_vehicles:
            for veh in active_vehicles:
                with st.container():
                    st.markdown(f"**🚗 車牌: `{veh['plate_no']}`** | 廠區: {veh['plant']} | 司機: {veh['driver_name']} | 進廠: {veh['entry_time']}")
                    if st.button(f"🏁 登記離廠 ({veh['plate_no']})", key=f"checkout_{veh['log_id']}"):
                        veh["exit_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        veh["status"] = "🟢 已離廠 (Completed)"
                        st.success(f"✅ 車牌 [{veh['plate_no']}] 已完成離廠時間記錄！")
                        st.rerun()
                st.divider()
        else:
            st.success("🎉 目前廠區內所有登記車輛均已離廠！")

        st.markdown("#### 📜 所有進出紀錄總表")
        df_all = pd.DataFrame(st.session_state.vehicle_logs_db)
        st.dataframe(df_all, use_container_width=True)

    # ----------------------------------------------------
    # 🔧 頁籤四：公司公務車保養與維護履歷管理
    # ----------------------------------------------------
    with tab_car_maint:
        st.markdown("### 🔧 公司公務車 / 廠長用車保養維護履歷管理")
        st.caption("完整記錄公司自有公務車輛之品牌型號、購買日期、保養里程、維護內容與保養金額支出。")

        # 顯示現有保養履歷表
        df_maint = pd.DataFrame(st.session_state.company_car_maintenance_db)
        st.dataframe(df_maint, use_container_width=True)

        st.markdown("---")
        st.markdown("#### ➕ 新增公務車保養與維護紀錄")
        with st.form("form_add_car_maintenance"):
            c1, c2, c3 = st.columns(3)
            with c1:
                plate_no = st.text_input("車牌號碼 *", value="61A-888.66")
                brand_model = st.text_input("車輛品牌型號 *", value="Toyota Fortuner 2.8L")
            with c2:
                purchase_date = st.date_input("車輛購買時間", value=datetime.date(2023, 5, 15))
                maint_date = st.date_input("本次保養時間", value=datetime.date.today())
            with c3:
                mileage = st.text_input("保養時行駛公里數 (Mileage) *", value="70,000 km")
                cost = st.text_input("保養維護金額 *", value="$350 USD")

            maint_content = st.text_area("保養維護內容與細節說明 *", value="定期保養：更換機油、機油濾清器、檢查輪胎與煞車系統。")
            handler = st.text_input("經辦人 / 申請人", value="張偉豪")

            if st.form_submit_button("💾 儲存公務車保養紀錄", type="primary", use_container_width=True):
                if plate_no and brand_model and maint_content:
                    st.session_state.company_car_maintenance_db.append({
                        "car_id": f"CAR-{len(st.session_state.company_car_maintenance_db)+1:02d}",
                        "plate_no": plate_no.upper(),
                        "brand_model": brand_model,
                        "purchase_date": str(purchase_date),
                        "maint_date": str(maint_date),
                        "mileage": mileage,
                        "maint_content": maint_content,
                        "cost": cost,
                        "handler": handler,
                    })
                    st.success(f"🎉 【保養紀錄新增成功】已成功建立車牌 [{plate_no.upper}] 的保養履歷！")
                    st.rerun()
                else:
                    st.error("❌ 請完整填寫車牌號碼、品牌型號與保養內容！")


def show(engine=None, lang="繁體中文"):
    render_vehicle_gate_log_page(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_vehicle_gate_log_page(engine, lang)
