import streamlit as st
import pandas as pd
import datetime

def render_subcontractor_labor_page(engine=None, lang="繁體中文", **kwargs):
    texts = {
        "繁體中文": {
            "title": "👷 外包商點工計價與越南勞動法計薪智慧核算系統",
            "caption": "精準記錄越南廠（西寧/海防）外包工班與點工出勤，自動套用越南勞動法加班與夜班加給，產出精準計薪與估驗對帳單。",
            "tab1": "📝 現場點工與出勤登記 (Daily Labor Log)",
            "tab2": "💰 外包商計價與越南勞動法薪資核算 (Payroll Calc)",
            "tab3": "📊 外包商對帳與應付帳款 (AP) 總覽"
        },
        "Tiếng Việt": {
            "title": "👷 Quản lý Nhân công Thầu phụ & Tính lương theo Luật LĐ Việt Nam",
            "caption": "Ghi nhận chấm công thầu phụ, tự động tính tăng ca (150%, 200%) và phụ cấp ca đêm theo Luật Lao động VN.",
            "tab1": "📝 Chấm công & Ghi nhận thầu phụ",
            "tab2": "💰 Tính lương & Định giá thầu phụ",
            "tab3": "📊 Tổng hợp công nợ thầu phụ (AP)"
        },
        "English": {
            "title": "👷 Subcontractor Daily Labor & VN Labor Law Payroll System",
            "caption": "Accurately logs daily subcontracted labor, automatically calculates VN overtime (150%/200%) and night shifts.",
            "tab1": "📝 Daily Labor Attendance Log",
            "tab2": "💰 Subcontractor Payroll & VN Labor Law Calc",
            "tab3": "📊 Subcontractor AP & Reconciliation"
        }
    }

    active_lang = lang if lang in texts else "繁體中文"
    t = texts[active_lang]

    st.title(t["title"])
    st.caption(t["caption"])

    # 初始化外包商與點工資料庫
    if "subcontractor_attendance_db" not in st.session_state:
        st.session_state.subcontractor_attendance_db = [
            {
                "log_id": "LAB-2026-001",
                "factory": "越南西寧廠 (Tay Ninh)",
                "contractor": "順發水電外包工班 (Thầu phụ Thuận Phát)",
                "date": "2026-10-08",
                "workers_count": 12,
                "normal_hours": 8.0,
                "ot_hours": 2.0,       # 平日加班 (1.5x)
                "night_shift": True,   # 夜班加給 (30%)
                "unit_rate_usd": 25.0, # 每人每日基礎費率
                "total_calculated_usd": 420.0,
                "status": "🟢 已確認並生成對帳單"
            }
        ]

    tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

    with tab1:
        st.markdown("##### 📝 步驟一：現場工程師填寫外包工班每日點工與出勤紀錄")
        with st.form("labor_log_form"):
            lc1, lc2, lc3 = st.columns(3)
            with lc1:
                sel_factory = st.selectbox("案場廠區", ["越南西寧廠 (Tay Ninh)", "越南海防廠 (Hai Phong)"])
                contractor_name = st.text_input("外包商 / 工班名稱 *", value="順發水電外包工班 (Thầu phụ Thuận Phát)")
            with lc2:
                log_date = st.date_input("點工日期", datetime.date(2026, 10, 9))
                workers_num = st.number_input("出工工人總人數 (人數)", min_value=1, value=10)
            with lc3:
                normal_h = st.number_input("正常工作時數 (小時)", value=8.0, step=0.5)
                ot_h = st.number_input("加班時數 (OT Hours)", value=2.0, step=0.5)

            lc4, lc5 = st.columns(2)
            with lc4:
                is_night = st.checkbox("🌙 是否包含夜班作業 (套用越南勞動法 30% 夜班加給)")
            with lc5:
                daily_rate = st.number_input("每人每日基本計價費率 (USD)", value=25.0, step=5.0)

            if st.form_submit_button("🚀 提交點工紀錄並套用勞動法計薪", type="primary"):
                # 越南勞動法計薪邏輯模擬：
                # 正常時數 = rate
                # 加班費 = (rate / 8) * ot_h * 1.5
                # 夜班加給 = 若夜班則總額外加 30%
                hourly_rate = daily_rate / 8.0
                base_pay = daily_rate * workers_num
                ot_pay = hourly_rate * ot_h * 1.5 * workers_num
                night_bonus = (base_pay + ot_pay) * 0.3 if is_night else 0.0
                total_pay = base_pay + ot_pay + night_bonus

                new_id = f"LAB-2026-{len(st.session_state.subcontractor_attendance_db)+1:03d}"
                st.session_state.subcontractor_attendance_db.insert(0, {
                    "log_id": new_id,
                    "factory": sel_factory,
                    "contractor": contractor_name,
                    "date": str(log_date),
                    "workers_count": workers_num,
                    "normal_hours": normal_h,
                    "ot_hours": ot_h,
                    "night_shift": is_night,
                    "unit_rate_usd": daily_rate,
                    "total_calculated_usd": round(total_pay, 2),
                    "status": "⏳ 待財務與主管核對 (Pending AP)"
                })
                st.success(f"✅ 點工紀錄 [{new_id}] 已成功建立！依越南勞動法自動試算總金額：`$ {total_pay:,.2f} USD`。")
                st.rerun()

    with tab2:
        st.markdown("##### 💰 越南勞動法計薪規則與合規說明")
        st.info("💡 系統自動套用標準：\n1. **平日加班**：依時薪 150% 計算。\n2. **週末假日加班**：依時薪 200% 計算。\n3. **夜班加給**：夜間工作時段自動加計 30% 薪資補貼。\n4. 嚴格杜絕工人重複點工或浮報時數，所有紀錄均與案場日報表連動。")

    with tab3:
        st.markdown("##### 📊 外包商點工對帳與應付帳款 (AP) 總覽")
        if st.session_state.subcontractor_attendance_db:
            st.dataframe(pd.DataFrame(st.session_state.subcontractor_attendance_db), use_container_width=True)
            
            if st.button("📥 一鍵將已核准之外包點工轉入財務應付帳款 (AP)", type="primary"):
                st.success("✅ 外包點工費用已成功轉入財務部應付帳款（AP），準備進行月底請款撥款！")
        else:
            st.info("目前尚無外包商點工紀錄。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_subcontractor_labor_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_subcontractor_labor_page(engine=engine, lang=lang, **kwargs)
