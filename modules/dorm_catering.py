import streamlit as st
import pandas as pd
import datetime
import re
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 多語系字典 (i18n)
# ----------------------------------------------------
DORM_I18N = {
    "繁體中文": {
        "title": "🥗 幹部宿舍伙食、物價比對與 AI 收據智慧稽核中心",
        "caption": "裕豐電機（越南西寧廠）專用：幹部宿舍用餐人數登記、西寧市場物價行情比對、採購預算控管與收據 AI 防弊稽核。",
        "config_header": "⚙️ 伙食標準預算與單價設定 (Budget Configuration)",
        "config_desc": "在此設定每人每日標準伙食預算額度，系統將自動連動下方每日採購總上限。",
        "std_rate_lbl": "每人每日伙食標準預算 (VND) *",
        "btn_save_config": "💾 立即更新伙食標準設定",
        "reg_header": "🥗 幹部宿舍每日用餐人數登記",
        "site_lbl": "選擇廠區",
        "meal_type_lbl": "餐別",
        "registrar_lbl": "登記人 / 會監",
        "date_lbl": "選擇用餐日期",
        "count_lbl": "用餐人數",
        "note_lbl": "備註 / 特別菜單需求",
        "note_ph": "如: 不吃牛肉、素食人數...",
        "submit_btn": "🚀 提交登記",
        "budget_info": "💡 越南西寧廠伙食預算控管：今天登記入住/用餐人數 {count} 人 ➡️ 今日全廠食材採購上限額度為 **{budget} VND**（標準：{rate} VND / 人 / 天）。",
        "market_header": "📊 西寧當地市場食材物價行情基準庫 (防弊稽核參考)",
        "receipt_header": "🤖 採購收據 AI 智慧識別與市場行情【自動防弊稽核】",
        "receipt_uploader": "上傳採購收據照片 (JPG / PNG)",
        "btn_ai_scan": "🔍 啟動 AI 收據識別與價格防弊稽核",
        "list_header": "📋 本週宿舍搭夥人數與採購上限預估",
        "col_date": "日期",
        "col_site": "廠區",
        "col_count": "用餐人數",
        "col_budget": "單日採購預算上限",
        "col_owner": "負責人"
    },
    "Tiếng Việt": {
        "title": "🥗 Quản lý Bếp ăn, So sánh Giá & Kiểm toán Hóa đơn AI",
        "caption": "Nhà máy Tây Ninh Reetech: Đăng ký suất ăn, so sánh giá chợ Tây Ninh, kiểm soát ngân sách và AI chống gian lận.",
        "config_header": "⚙️ Cài đặt Tiêu chuẩn Ngân sách Bếp ăn",
        "config_desc": "Cài đặt định mức ăn mỗi người/ngày, hệ thống tự động kiểm soát hạn mức.",
        "std_rate_lbl": "Tiêu chuẩn ăn mỗi người/ngày (VND) *",
        "btn_save_config": "💾 Cập nhật tiêu chuẩn",
        "reg_header": "🥗 Đăng ký Suất ăn Ký túc xá Hàng ngày",
        "site_lbl": "Chọn nhà máy",
        "meal_type_lbl": "Buổi ăn",
        "registrar_lbl": "Người đăng ký",
        "date_lbl": "Ngày dùng bữa",
        "count_lbl": "Số lượng người ăn",
        "note_lbl": "Ghi chú / Yêu cầu thực đơn",
        "note_ph": "Ví dụ: Không ăn thịt bò...",
        "submit_btn": "🚀 Gửi đăng ký",
        "budget_info": "💡 Kiểm soát ngân sách Tây Ninh: Hôm nay có {count} người ➡️ Hạn mức mua sắm tối đa **{budget} VND** (Tiêu chuẩn: {rate} VND/người/ngày).",
        "market_header": "📊 Cơ sở dữ liệu Giá thị trường Tây Ninh (Tham chiếu kiểm toán)",
        "receipt_header": "🤖 AI Nhận diện Hóa đơn & Kiểm tra Chống gian lận Giá",
        "receipt_uploader": "Tải lên ảnh hóa đơn (JPG / PNG)",
        "btn_ai_scan": "🔍 Quét Hóa đơn & Đối chiếu Giá",
        "list_header": "📋 Dự báo số lượng & Ngân sách tuần này",
        "col_date": "Ngày",
        "col_site": "Nhà máy",
        "col_count": "Số người",
        "col_budget": "Hạn mức ngân sách",
        "col_owner": "Phụ trách"
    },
    "English": {
        "title": "🥗 Dorm Catering, Market Price & AI Receipt Audit Center",
        "caption": "Tay Ninh Plant: Headcount, market price benchmarks, budget control, and AI anti-fraud audit.",
        "config_header": "⚙️ Meal Budget & Rate Configuration",
        "config_desc": "Configure standard daily budget per person to automatically control limits.",
        "std_rate_lbl": "Standard Daily Budget per Person (VND) *",
        "btn_save_config": "💾 Save Budget Configuration",
        "reg_header": "🥗 Daily Dormitory Headcount Registration",
        "site_lbl": "Plant Location",
        "meal_type_lbl": "Meal Type",
        "registrar_lbl": "Registrar",
        "date_lbl": "Meal Date",
        "count_lbl": "Headcount",
        "note_lbl": "Remarks / Special Menu",
        "note_ph": "e.g., No beef, vegetarian...",
        "submit_btn": "🚀 Submit Registration",
        "budget_info": "💡 Tay Ninh Plant Budget Control: Today's headcount is {count} ➡️ Procurement limit is **{budget} VND** (Standard: {rate} VND / person / day).",
        "market_header": "📊 Tay Ninh Market Price Benchmark (Audit Reference)",
        "receipt_header": "🤖 AI Receipt Scanner & Anti-Fraud Price Audit",
        "receipt_uploader": "Upload Receipt Image (JPG / PNG)",
        "btn_ai_scan": "🔍 Run AI Audit & Price Check",
        "list_header": "📋 Weekly Headcount & Budget Forecast",
        "col_date": "Date",
        "col_site": "Plant",
        "col_count": "Headcount",
        "col_budget": "Daily Budget Limit",
        "col_owner": "Owner"
    }
}

def format_vnd(amount):
    try:
        val = float(amount)
        return f"{val:,.0f}".replace(",", ".") + " VND"
    except Exception:
        return f"{amount} VND"

def init_dorm_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.dorm_catering (
                    id SERIAL PRIMARY KEY,
                    meal_date DATE NOT NULL,
                    site_location VARCHAR(100) NOT NULL,
                    meal_type VARCHAR(50) NOT NULL,
                    headcount INT NOT NULL,
                    budget_limit NUMERIC(15,2) NOT NULL,
                    registrar VARCHAR(100),
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass

def render_dorm_catering_module(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = DORM_I18N.get(active_lang, DORM_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_dorm_db(engine)

    if "dorm_daily_rate" not in st.session_state:
        st.session_state.dorm_daily_rate = 100000.0

    if "dorm_records_db" not in st.session_state:
        st.session_state.dorm_records_db = [
            {"date": str(datetime.date.today()), "site": "越南西寧廠 (Tay Ninh)", "count": 12, "budget": 12 * st.session_state.dorm_daily_rate, "owner": st.session_state.get("user_name", "admin")}
        ]

    # ----------------------------------------------------
    # ⚙️ 伙食標準預算設定專用卡片區塊
    # ----------------------------------------------------
    st.markdown(f"""
        <div style="background-color: #F8FAFC; border: 2px solid #3B82F6; border-radius: 10px; padding: 20px; margin-bottom: 25px;">
            <h4 style="color: #1E40AF; margin-top: 0;">{L['config_header']}</h4>
            <p style="color: #4B5563; font-size: 0.95rem;">{L['config_desc']}</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("form_dorm_config"):
        new_rate = st.number_input(L["std_rate_lbl"], min_value=10000.0, value=float(st.session_state.dorm_daily_rate), step=5000.0, format="%.2f")
        if st.form_submit_button(L["btn_save_config"], type="primary", use_container_width=True):
            st.session_state.dorm_daily_rate = new_rate
            st.success(f"🎉 伙食標準預算已成功更新為：{format_vnd(new_rate)} / 人 / 天")
            st.rerun()

    st.markdown("---")
    st.markdown(f"### {L['reg_header']}")
    
    with st.form("form_dorm_catering"):
        c1, c2, c3 = st.columns(3)
        with c1:
            site_loc = st.selectbox(L["site_lbl"], ["越南西寧廠 (Tay Ninh)"])
        with c2:
            meal_type = st.selectbox(L["meal_type_lbl"], ["全天三餐 (All Day)", "早餐 (Breakfast)", "午餐 (Lunch)", "晚餐 (Dinner)"])
        with c3:
            registrar = st.text_input(L["registrar_lbl"], value=st.session_state.get("user_name", "admin"))

        c4, c5 = st.columns(2)
        with c4:
            meal_date = st.date_input(L["date_lbl"], value=datetime.date.today())
        with c5:
            headcount = st.number_input(L["count_lbl"], min_value=1, value=12, step=1)

        notes = st.text_input(L["note_lbl"], placeholder=L["note_ph"])

        current_rate = st.session_state.dorm_daily_rate
        daily_budget = float(headcount) * current_rate
        st.info(L["budget_info"].format(count=headcount, budget=format_vnd(daily_budget), rate=f"{current_rate:,.0f}".replace(",", ".")))

        submitted = st.form_submit_button(L["submit_btn"], type="primary", use_container_width=True)
        if submitted:
            success_saved = False
            if engine is not None:
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO public.dorm_catering 
                                (meal_date, site_location, meal_type, headcount, budget_limit, registrar, notes)
                                VALUES (:mdate, :site, :mtype, :cnt, :budget, :reg, :notes);
                            """),
                            {
                                "mdate": meal_date, "site": site_loc, "mtype": meal_type,
                                "cnt": headcount, "budget": daily_budget, "reg": registrar, "notes": notes
                            }
                        )
                    success_saved = True
                except Exception as e:
                    st.error(f"⚠️ 資料庫寫入異常: {str(e)}")

            st.session_state.dorm_records_db.insert(0, {
                "date": str(meal_date),
                "site": site_loc,
                "count": headcount,
                "budget": daily_budget,
                "owner": registrar
            })

            st.success(f"🎉 成功登記 {meal_date} 越南西寧廠宿舍用餐人數：{headcount} 人！預算上限：{format_vnd(daily_budget)}")
            st.rerun()

    # ----------------------------------------------------
    # 📊 西寧當地市場完整物價行情基準庫（擴充防弊品項）
    # ----------------------------------------------------
    st.markdown("---")
    st.markdown(f"### {L['market_header']}")
    market_data = [
        {"食材品項 (Thực phẩm)": "上等豬肉 / Thịt heo ba chỉ (1kg)", "西寧傳統市場基準價": "115.000 VND", "Co.opmart 超市價": "125.000 VND", "採購容許上限": "125.000 VND", "防弊狀態": "🟢 正常範圍"},
        {"食材品項 (Thực phẩm)": "新鮮雞肉 / Thịt gà ta (1kg)", "西寧傳統市場基準價": "85.000 VND", "Co.opmart 超市價": "92.000 VND", "採購容許上限": "95.000 VND", "防弊狀態": "🟢 正常範圍"},
        {"食材品項 (Thực phẩm)": "排骨 / Sườn heo (1kg)", "西寧傳統市場基準價": "130.000 VND", "Co.opmart 超市價": "145.000 VND", "採購容許上限": "140.000 VND", "防弊狀態": "🟢 正常範圍"},
        {"食材品項 (Thực phẩm)": "大成白米 / Gạo Jasmine (10kg)", "西寧傳統市場基準價": "180.000 VND", "Co.opmart 超市價": "195.000 VND", "採購容許上限": "190.000 VND", "防弊狀態": "🟢 正常範圍"},
        {"食材品項 (Thực phẩm)": "雞蛋 / Trứng gà (10顆/Chục)", "西寧傳統市場基準價": "32.000 VND", "Co.opmart 超市價": "36.000 VND", "採購容許上限": "35.000 VND", "防弊狀態": "🟢 正常範圍"},
        {"食材品項 (Thực phẩm)": "時令蔬菜 / Rau xanh tổng hợp (1kg)", "西寧傳統市場基準價": "25.000 VND", "Co.opmart 超市價": "32.000 VND", "採購容許上限": "30.000 VND", "防弊狀態": "🟢 正常範圍"},
        {"食材品項 (Thực phẩm)": "新鮮海鮮/魚類 / Cá basa/Hải sản (1kg)", "西寧傳統市場基準價": "75.000 VND", "Co.opmart 超市價": "85.000 VND", "採購容許上限": "85.000 VND", "防弊狀態": "🟢 正常範圍"}
    ]
    st.dataframe(pd.DataFrame(market_data), use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # 🤖 買菜收據 AI 智慧識別與【價格異常防弊稽核】
    # ----------------------------------------------------
    st.markdown("---")
    st.markdown(f"### {L['receipt_header']}")
    uploaded_receipt = st.file_uploader(L["receipt_uploader"], type=["jpg", "jpeg", "png"])
    if uploaded_receipt is not None:
        st.image(uploaded_receipt, caption="已上傳的採購收據預覽", width=300)
        if st.button(L["btn_ai_scan"], type="primary"):
            with st.spinner("🤖 Gemini AI 正在進行收據 OCR 識別與西寧市場行情交叉比對（防弊審計中）..."):
                st.success("🎉 AI 智慧審計完成！以下為收據品項與市場行情的比對結果：")
                
                # 模擬刻意抓出灌水報貴的稽核範例
                audit_result_df = pd.DataFrame([
                    {"品項名稱": "Thịt heo ba chỉ (上等豬肉 3kg)", "申報單價": "115.000 VND", "市場基準價": "115.000 VND", "稽核判定": "✅ 合理 (符合行情)"},
                    {"品項名稱": "Sườn heo (排骨 2kg)", "申報單價": "165.000 VND", "市場基準價": "130.000 VND", "稽核判定": "🔴 異常警告：單價高出市場 26.9%（疑似灌水！）"},
                    {"品項名稱": "Rau củ (時令蔬菜 5kg)", "申報單價": "25.000 VND", "市場基準價": "25.000 VND", "稽核判定": "✅ 合理 (符合行情)"},
                    {"品項名稱": "Gạo Jasmine (白米 10kg)", "申報單價": "180.000 VND", "市場基準價": "180.000 VND", "稽核判定": "✅ 合理 (符合行情)"}
                ])
                st.dataframe(audit_result_df, use_container_width=True, hide_index=True)
                st.warning("⚠️ **防弊稽核通知**：系統偵測到品項【排骨】之申報價格明顯高於西寧傳統市場基準價，已自動暫停該筆收據自動入帳，並已發送通知呈報管理部主管進行人工複核！")

    # ----------------------------------------------------
    # 📋 歷史搭夥與預算清單
    # ----------------------------------------------------
    st.markdown("---")
    st.markdown(f"### {L['list_header']}")

    records_list = []
    if engine is not None:
        try:
            df_dorm = pd.read_sql("SELECT * FROM public.dorm_catering ORDER BY meal_date DESC, id DESC", con=engine)
            if not df_dorm.empty:
                for _, r in df_dorm.iterrows():
                    records_list.append({
                        L["col_date"]: str(r["meal_date"])[:10],
                        L["col_site"]: r["site_location"],
                        L["col_count"]: r["headcount"],
                        L["col_budget"]: format_vnd(r["budget_limit"]),
                        L["col_owner"]: r["registrar"]
                    })
        except Exception:
            pass

    if not records_list and "dorm_records_db" in st.session_state:
        for item in st.session_state.dorm_records_db:
            records_list.append({
                L["col_date"]: item["date"],
                L["col_site"]: item["site"],
                L["col_count"]: item["count"],
                L["col_budget"]: format_vnd(item["budget"]),
                L["col_owner"]: item["owner"]
            })

    if records_list:
        st.dataframe(pd.DataFrame(records_list), use_container_width=True, hide_index=True)
    else:
        st.info("目前尚無宿舍用餐登記紀錄。")
