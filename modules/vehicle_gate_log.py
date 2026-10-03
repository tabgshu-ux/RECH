import datetime
import pandas as pd
import streamlit as st


def render_vehicle_gate_log_page(engine=None, lang="繁體中文"):
    st.title("🚗 裕豐電機工業 - 廠區車輛進出與門禁時間紀錄系統")
    st.caption("管理西寧廠與海防廠大門口之貨車、原物料車、公務車與訪客車輛進出紀錄與時間追蹤。")

    # 初始化車輛進出紀錄資料庫
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
            {
                "log_id": "LOG-2026-002",
                "plant": "🇻🇳 越南海防廠 (Hai Phong Plant)",
                "plate_no": "15B-123.89",
                "vehicle_type": "🚐 公務商務車",
                "driver_name": "張偉豪 (經理)",
                "purpose": "廠長前往海防港口海關報關",
                "entry_time": "2026-10-03 09:00:10",
                "exit_time": "-",
                "status": "🟡 廠區內執行任務",
            },
        ]

    tab_overview, tab_register, tab_history = st.tabs([
        "📑 當前廠區車輛動態看板",
        "➕ 登記車輛進廠 (Check-In)",
        "⏱️ 車輛離廠登記與歷史查詢 (Check-Out)"
    ])

    # ----------------------------------------------------
    # 📑 頁籤一：動態看板
    # ----------------------------------------------------
    with tab_overview:
        st.markdown("### 📊 廠區車輛進出即時動態")
        
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
    with tab_register:
        st.markdown("### ➕ 登記車輛進廠 (Gate Check-In)")

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
    # ⏱️ 頁籤三：車輛離廠登記與歷史查詢 (Check-Out)
    # ----------------------------------------------------
    with tab_history:
        st.markdown("### ⏱️ 車輛離廠登記 (Gate Check-Out) 與歷史查詢")
        st.info("💡 請在下方尋找滯留廠區內的車輛，並點擊按鈕完成「離廠時間紀錄」。")

        # 過濾出仍在廠區內的車輛
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


def show(engine=None, lang="繁體中文"):
    render_vehicle_gate_log_page(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_vehicle_gate_log_page(engine, lang)
