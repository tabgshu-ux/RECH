import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 幹部宿舍與餐飲採購控管模組完整多語系字典 (i18n)
# ----------------------------------------------------
CATERING_I18N = {
    "繁體中文": {
        "title": "🥗 總務部 - 幹部宿舍伙食採購與防浮報控管中心 (西寧廠)",
        "caption": "管控幹部宿舍每日買菜預算、食材採購明細、照片存證與西寧在地物價即時浮動比對。",
        "tab_daily": "📝 每日買菜記帳與食材拍照存證",
        "tab_summary": "📊 宿舍伙食費月度統計與單價稽核",
        "tab_prices": "⚙️ 西寧在地物價即時浮動與參考單價維護",
        "header_daily": "🛒 每日幹部食堂買菜支出登記與防浮報稽核",
        "header_items": "🥦 食材採購明細錄入 (即時比對西寧物價浮動)",
        "expander_trends": "📈 點此展開【西寧當地最新食材物價行情與漲跌趨勢看板】",
        "lbl_date": "買菜/用餐日期",
        "lbl_people": "今日用餐幹部人數 (人)",
        "lbl_budget_cap": "每人每日預算基準 (VND/人)",
        "lbl_buyer": "採購經辦 / 總務人員",
        "buyer_default": "煮菜阿姨 / 總務專員",
        "lbl_item": "食材品項名稱",
        "lbl_qty": "採購數量 (kg / 包 / 箱)",
        "lbl_unit_price": "採購單價 (VND)",
        "lbl_ref_price": "西寧即時參考價",
        "lbl_photo": "📸 上傳攤販收據小票與食材秤重照片 (強制拍照存證)",
        "btn_add_item": "➕ 新增食材採購明細",
        "btn_submit_daily": "🚀 提交今日買菜支出並進行防浮報稽核",
        "total_budget_cap": "今日伙食總預算上限",
        "formula_cap": "公式：{people} 人 × {cap:,.0f} VND",
        "lbl_cart": "📋 今日已加入食材清單：",
        "lbl_total_actual": "💰 採購總金額：`{actual:,.0f} VND` / 預算上限：`{cap:,.0f} VND`",
        "alert_over_budget": "⚠️ 警告：今日買菜總金額超過「幹部人數 × 預算基準」上限！須總務主管簽核。",
        "alert_price_anomaly": "⚠️ 警告：部分食材採購單價高於西寧市場參考價與容許浮動區間！可能存在浮報風險！",
        "alert_no_photo": "❌ 系統防偷與防浮報鐵律：請務必拍照並上傳【菜市場收據小票與食材秤重照片】方可結算！",
        "success_submit": "✅ 今日買菜支出已成功登錄！狀態：`{status}`",
        "header_summary": "📊 幹部宿舍伙食費歷史月度報表與異常稽核",
        "header_drilldown": "🔍 查看特定日期買菜照片與食材明細穿透",
        "sel_record_date": "選擇日期查看明細",
        "no_records": "目前尚無買菜支出紀錄。",
        "header_prices": "⚙️ 西寧在地物價即時浮動與容許誤差門檻設定",
        "caption_prices": "💡 總務主管可根據西寧菜市場（Trảng Bàng, Gò Dầu...）與 Co.opmart 最新行情，調整參考單價與浮動趨勢標記。",
        "lbl_slider_margin": "🛡️ 防浮報系統容許之物價波動上限 (%)",
        "help_slider_margin": "當阿姨買菜單價高於西寧參考價超過此百分比時，系統將自動亮紅燈警告！",
        "header_adjust_prices": "📝 調整各品項即時參考單價與漲跌說明",
        "lbl_trend_tag": "漲跌趨勢標記",
        "btn_save_prices": "💾 儲存西寧即時物價行情與趨勢",
        "success_save_prices": "✅ 西寧即時物價與趨勢標記已成功更新！",
        "flag_normal": "🟢 正常",
        "flag_high": "🔴 偏高 (高出西寧行情 {pct:.0f}%)",
        "flag_slight_high": "🟡 微漲 (+{pct:.0f}%)",
        "status_ok": "🟢 正常核銷",
        "status_need_audit": "⚠️ 需總務主管審核 (單價高於市場浮動區間或超支)"
    },
    "Tiếng Việt": {
        "title": "🥗 Phòng Quản lý - Mua thực phẩm & Kiểm soát Ký túc xá Cán bộ (Tây Ninh)",
        "caption": "Quản lý chi phí đi chợ hàng ngày, kiểm soát đơn giá thực phẩm và đối soát biến động giá thị trường Tây Ninh.",
        "tab_daily": "📝 Nhập chi phí đi chợ & Ảnh chụp",
        "tab_summary": "📊 Báo cáo chi phí ăn uống tháng",
        "tab_prices": "⚙️ Cấu hình đơn giá & Biến động giá thị trường Tây Ninh",
        "header_daily": "🛒 Nhập chi phí đi chợ hàng ngày & Kiểm soát đơn giá",
        "header_items": "🥦 Nhập chi tiết thực phẩm (So sánh với biến động giá Tây Ninh)",
        "expander_trends": "📈 Bấm để xem 【Bảng biến động giá thực phẩm mới nhất tại Tây Ninh】",
        "lbl_date": "Ngày đi chợ / Dùng bữa",
        "lbl_people": "Số lượng cán bộ ăn (Người)",
        "lbl_budget_cap": "Định mức/người/ngày (VND)",
        "lbl_buyer": "Người đi chợ / Tổng vụ",
        "buyer_default": "Dì nấu ăn / Chuyên viên Tổng vụ",
        "lbl_item": "Tên thực phẩm",
        "lbl_qty": "Số lượng (kg / gói / thùng)",
        "lbl_unit_price": "Đơn giá mua (VND)",
        "lbl_ref_price": "Giá tham chiếu Tây Ninh",
        "lbl_photo": "📸 Tải ảnh hóa đơn & Ảnh cân thực phẩm (Bắt buộc chụp ảnh)",
        "btn_add_item": "➕ Thêm món",
        "btn_submit_daily": "🚀 Lưu chi phí & Kiểm tra đơn giá",
        "total_budget_cap": "Hạn mức ngân sách tiền ăn hôm nay",
        "formula_cap": "Công thức: {people} người × {cap:,.0f} VND",
        "lbl_cart": "📋 Danh sách thực phẩm đã nhập hôm nay:",
        "lbl_total_actual": "💰 Tổng tiền mua: `{actual:,.0f} VND` / Hạn mức: `{cap:,.0f} VND`",
        "alert_over_budget": "⚠️ Cảnh báo: Tổng chi vượt ngân sách định mức! Cần Trưởng phòng duyệt.",
        "alert_price_anomaly": "⚠️ Cảnh báo: Đơn giá cao hơn biến động cho phép của thị trường Tây Ninh!",
        "alert_no_photo": "❌ Bắt buộc: Vui lòng chụp và tải ảnh hóa đơn/ảnh cân thực phẩm!",
        "success_submit": "✅ Đã lưu chi phí đi chợ thành công! Trạng thái: `{status}`",
        "header_summary": "📊 Báo cáo lịch sử chi phí ăn uống & Kiểm toán bất thường",
        "header_drilldown": "🔍 Xem chi tiết thực phẩm & Ảnh chụp theo ngày",
        "sel_record_date": "Chọn ngày để xem chi tiết",
        "no_records": "Chưa có bản ghi chi phí đi chợ nào.",
        "header_prices": "⚙️ Cấu hình đơn giá & Ngưỡng biến động giá Tây Ninh",
        "caption_prices": "💡 Quản lý có thể điều chỉnh giá tham chiếu theo thị trường Tây Ninh (Trảng Bàng, Gò Dầu, Co.opmart...).",
        "lbl_slider_margin": "🛡️ Biên độ biến động giá cho phép (%)",
        "help_slider_margin": "Khi đơn giá mua vượt quá tỷ lệ này so với giá tham chiếu, hệ thống sẽ cảnh báo đỏ!",
        "header_adjust_prices": "📝 Điều chỉnh đơn giá tham chiếu & Ghi chú xu hướng",
        "lbl_trend_tag": "Ghi chú biến động giá",
        "btn_save_prices": "💾 Lưu giá tham chiếu & Xu hướng",
        "success_save_prices": "✅ Đã cập nhật giá tham chiếu Tây Ninh thành công!",
        "flag_normal": "🟢 Bình thường",
        "flag_high": "🔴 Cao (Cao hơn thị trường {pct:.0f}%)",
        "flag_slight_high": "🟡 Tăng nhẹ (+{pct:.0f}%)",
        "status_ok": "🟢 Đã duyệt bình thường",
        "status_need_audit": "⚠️ Cần Trưởng phòng duyệt (Đơn giá cao hoặc vượt ngân sách)"
    },
    "English": {
        "title": "🥗 GA - Dormitory Catering & Food Procurement Control (Tay Ninh)",
        "caption": "Manage daily grocery budgets, track food item procurement, enforce photo evidence, and monitor real-time Tay Ninh market price trends.",
        "tab_daily": "📝 Daily Grocery Logging & Photo Upload",
        "tab_summary": "📊 Monthly Expense & Price Anomaly Audit",
        "tab_prices": "⚙️ Tay Ninh Real-time Market Price & Trend Settings",
        "header_daily": "🛒 Daily Grocery Expense Entry & Price Control",
        "header_items": "🥦 Food Item Procurement Entry (Compared with Tay Ninh Prices)",
        "expander_trends": "📈 Click to view 【Tay Ninh Latest Food Price Trends & Board】",
        "lbl_date": "Date",
        "lbl_people": "Number of Staff Dining",
        "lbl_budget_cap": "Daily Cap per Person (VND)",
        "lbl_buyer": "Buyer / GA Staff",
        "buyer_default": "Cook / GA Specialist",
        "lbl_item": "Food Item",
        "lbl_qty": "Quantity (kg / pack / box)",
        "lbl_unit_price": "Unit Price (VND)",
        "lbl_ref_price": "Tay Ninh Ref Price",
        "lbl_photo": "📸 Upload Receipt & Food Weighing Photo (Mandatory)",
        "btn_add_item": "➕ Add Food Item",
        "btn_submit_daily": "🚀 Submit Daily Expense & Perform Audit",
        "total_budget_cap": "Today's Total Budget Cap",
        "formula_cap": "Formula: {people} persons × {cap:,.0f} VND",
        "lbl_cart": "📋 Today's Added Grocery Items:",
        "lbl_total_actual": "💰 Total Spent: `{actual:,.0f} VND` / Budget Cap: `{cap:,.0f} VND`",
        "alert_over_budget": "⚠️ Warning: Total grocery cost exceeds the budget cap!",
        "alert_price_anomaly": "⚠️ Warning: Item unit price exceeds Tay Ninh benchmark price & allowed margin!",
        "alert_no_photo": "❌ Mandatory: Please upload receipt and food weighing photo!",
        "success_submit": "✅ Daily grocery expense successfully submitted! Status: `{status}`",
        "header_summary": "📊 Monthly Expense History & Price Anomaly Audit",
        "header_drilldown": "🔍 View Item Details & Photos by Date",
        "sel_record_date": "Select Date to View Details",
        "no_records": "No grocery expense records found.",
        "header_prices": "⚙️ Tay Ninh Real-time Market Price & Fluctuation Threshold Settings",
        "caption_prices": "💡 GA Manager can adjust reference prices according to latest Tay Ninh market trends.",
        "lbl_slider_margin": "🛡️ Allowed Price Fluctuation Margin (%)",
        "help_slider_margin": "If purchase price exceeds reference price by more than this percentage, a red alert is triggered!",
        "header_adjust_prices": "📝 Adjust Reference Prices & Trend Tags",
        "lbl_trend_tag": "Trend Tag",
        "btn_save_prices": "💾 Save Tay Ninh Market Prices & Trends",
        "success_save_prices": "✅ Tay Ninh market prices and trends successfully updated!",
        "flag_normal": "🟢 Normal",
        "flag_high": "🔴 High (+{pct:.0f}% above market)",
        "flag_slight_high": "🟡 Slightly High (+{pct:.0f}%)",
        "status_ok": "🟢 Approved Normally",
        "status_need_audit": "⚠️ Requires GA Manager Approval (Over budget or high unit price)"
    }
}

# ----------------------------------------------------
# 🛒 西寧在地市場與 Co.opmart 即時物價與浮動趨勢基準
# ----------------------------------------------------
DEFAULT_TAY_NINH_DYNAMIC_PRICES = {
    "Thịt heo đùi/vai (豬肉腿/肩肉)": {"price": 105000.0, "delta": "+5,000 VND (Mùa mưa tăng nhẹ)", "status": "up"},
    "Thịt ba rọi (五花肉)": {"price": 135000.0, "delta": "0 VND (Ổn định)", "status": "stable"},
    "Thịt gà nguyên con (全雞/土雞)": {"price": 85000.0, "delta": "0 VND (Ổn định)", "status": "stable"},
    "Thịt bò (牛肉)": {"price": 240000.0, "delta": "-10,000 VND (Nguồn cung dồi dào)", "status": "down"},
    "Cá diêu hồng/Cá lóc (鮮魚)": {"price": 60000.0, "delta": "+2,000 VND (Tăng nhẹ)", "status": "up"},
    "Tôm tươi (鮮蝦)": {"price": 160000.0, "delta": "0 VND (Ổn định)", "status": "stable"},
    "Rau cải / Rau muống (葉菜類)": {"price": 22000.0, "delta": "+4,000 VND (Mùa mưa rau giảm)", "status": "up"},
    "Bắp cải / Củ quả (根莖類)": {"price": 25000.0, "delta": "0 VND (Ổn định)", "status": "stable"},
    "Trứng gà - 10 quả (雞蛋)": {"price": 32000.0, "delta": "-1,000 VND (Giảm nhẹ)", "status": "down"},
    "Gạo thơm / Nàng Hoa (白米)": {"price": 22000.0, "delta": "0 VND (Ổn định)", "status": "stable"},
    "Dầu ăn / Gia vị (食用油/調料)": {"price": 45000.0, "delta": "0 VND (Ổn định)", "status": "stable"}
}

def render_dorm_catering_module(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = CATERING_I18N.get(active_lang, CATERING_I18N.get("繁體中文", {}))

    st.title(L.get("title", "🥗 Dorm Catering"))
    st.caption(L.get("caption", ""))

    # 1. 初始化西寧即時動態物價與趨勢
    if "market_price_dynamic" not in st.session_state:
        st.session_state.market_price_dynamic = DEFAULT_TAY_NINH_DYNAMIC_PRICES.copy()

    # 2. 物價容許浮動範圍百分比
    if "allowed_price_margin_pct" not in st.session_state:
        st.session_state.allowed_price_margin_pct = 15.0

    # 3. 初始化買菜歷史數據庫
    if "dorm_catering_db" not in st.session_state:
        st.session_state.dorm_catering_db = [
            {
                "date": "2026-10-12",
                "people_count": 12,
                "budget_cap_per_person": 100000.0,
                "total_budget": 1200000.0,
                "total_actual": 1150000.0,
                "buyer": L.get("buyer_default", "Cook"),
                "status": L.get("status_ok", "🟢 OK"),
                "photo_uploaded": True,
                "items": [
                    {"item": "Thịt heo đùi/vai (豬肉腿/肩肉)", "qty": 4.0, "unit_price": 105000.0, "amount": 420000.0, "flag": L.get("flag_normal", "🟢 OK")},
                    {"item": "Rau cải / Rau muống (葉菜類)", "qty": 6.0, "unit_price": 22000.0, "amount": 132000.0, "flag": L.get("flag_normal", "🟢 OK")},
                    {"item": "Cá diêu hồng/Cá lóc (鮮魚)", "qty": 5.0, "unit_price": 62000.0, "amount": 310000.0, "flag": L.get("flag_normal", "🟢 OK")}
                ]
            }
        ]

    tab_daily, tab_summary, tab_prices = st.tabs([
        L.get("tab_daily", "Tab 1"), L.get("tab_summary", "Tab 2"), L.get("tab_prices", "Tab 3")
    ])

    # ----------------------------------------------------
    # 📝 1. 每日買菜記帳與防浮報審核
    # ----------------------------------------------------
    with tab_daily:
        st.markdown(f"### {L.get('header_daily', '')}")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            buy_date = st.date_input(L.get("lbl_date", "Date"), value=datetime.date.today())
            buyer_name = st.text_input(L.get("lbl_buyer", "Buyer"), value=L.get("buyer_default", ""))
        with c2:
            people_cnt = st.number_input(L.get("lbl_people", "People"), min_value=1, value=12, step=1)
            cap_per_person = st.number_input(L.get("lbl_budget_cap", "Cap"), min_value=10000.0, value=100000.0, step=5000.0)
        with c3:
            max_allowed_budget = people_cnt * cap_per_person
            st.metric(L.get("total_budget_cap", "Budget Cap"), f"{max_allowed_budget:,.0f} VND")
            st.caption(L.get("formula_cap", "").format(people=people_cnt, cap=cap_per_person))

        st.markdown("---")
        st.markdown(f"#### {L.get('header_items', '')}")

        # 看板
        with st.expander(L.get("expander_trends", "Trends"), expanded=False):
            m_cols = st.columns(4)
            items_keys = list(st.session_state.market_price_dynamic.keys())
            for idx, k in enumerate(items_keys[:4]):
                data_info = st.session_state.market_price_dynamic[k]
                m_cols[idx % 4].metric(
                    label=k.split(" (")[0],
                    value=f"{data_info['price']:,.0f} VND",
                    delta=data_info['delta']
                )

        if "temp_shopping_cart" not in st.session_state:
            st.session_state.temp_shopping_cart = []

        with st.form("form_add_food_item"):
            col_i1, col_i2, col_i3 = st.columns([2, 1, 1.5])
            with col_i1:
                item_name = st.selectbox(L.get("lbl_item", "Item"), list(st.session_state.market_price_dynamic.keys()) + ["Khác / 其他"])
            with col_i2:
                item_qty = st.number_input(L.get("lbl_qty", "Qty"), min_value=0.1, value=1.0, step=0.5)
            with col_i3:
                ref_info = st.session_state.market_price_dynamic.get(item_name, {"price": 50000.0, "delta": "0 VND"})
                ref_p = ref_info["price"]
                item_price = st.number_input(f"{L.get('lbl_unit_price', 'Price')} ({L.get('lbl_ref_price', 'Ref')}: {ref_p:,.0f})", min_value=0.0, value=ref_p, step=5000.0)

            add_item_btn = st.form_submit_button(L.get("btn_add_item", "Add"), type="secondary")
            if add_item_btn:
                amt = item_qty * item_price
                flag_status = L.get("flag_normal", "🟢 OK")
                
                if item_name in st.session_state.market_price_dynamic:
                    ref_price = st.session_state.market_price_dynamic[item_name]["price"]
                    margin_pct = st.session_state.allowed_price_margin_pct / 100.0
                    
                    if item_price > ref_price * (1 + margin_pct):
                        diff_pct = ((item_price - ref_price) / ref_price) * 100
                        flag_status = L.get("flag_high", "🔴 High").format(pct=diff_pct)
                    elif item_price > ref_price:
                        diff_pct = ((item_price - ref_price) / ref_price) * 100
                        flag_status = L.get("flag_slight_high", "🟡 High").format(pct=diff_pct)

                st.session_state.temp_shopping_cart.append({
                    "item": item_name,
                    "qty": item_qty,
                    "unit_price": item_price,
                    "amount": amt,
                    "flag": flag_status
                })
                st.rerun()

        # 展示當次採購清單
        if st.session_state.temp_shopping_cart:
            st.markdown(f"##### {L.get('lbl_cart', '')}")
            df_temp = pd.DataFrame(st.session_state.temp_shopping_cart)
            st.dataframe(df_temp, use_container_width=True)

            total_actual_amt = df_temp["amount"].sum()
            has_price_anomaly = any("🔴" in str(row["flag"]) or "Cao" in str(row["flag"]) or "High" in str(row["flag"]) for row in st.session_state.temp_shopping_cart)
            is_over_budget = total_actual_amt > max_allowed_budget

            st.markdown("---")
            st.markdown(L.get("lbl_total_actual", "").format(actual=total_actual_amt, cap=max_allowed_budget))

            if is_over_budget:
                st.error(L.get("alert_over_budget", ""))
            if has_price_anomaly:
                st.warning(L.get("alert_price_anomaly", ""))

            # 強制照片上傳存證
            uploaded_receipt = st.file_uploader(L.get("lbl_photo", "Photo"), type=["jpg", "jpeg", "png"])

            if st.button(L.get("btn_submit_daily", "Submit"), type="primary", use_container_width=True):
                if not uploaded_receipt:
                    st.error(L.get("alert_no_photo", ""))
                else:
                    status_final = L.get("status_ok", "🟢 OK")
                    if is_over_budget or has_price_anomaly:
                        status_final = L.get("status_need_audit", "⚠️ Audit")

                    st.session_state.dorm_catering_db.insert(0, {
                        "date": str(buy_date),
                        "people_count": people_cnt,
                        "budget_cap_per_person": cap_per_person,
                        "total_budget": max_allowed_budget,
                        "total_actual": total_actual_amt,
                        "buyer": buyer_name,
                        "status": status_final,
                        "photo_uploaded": True,
                        "items": st.session_state.temp_shopping_cart.copy()
                    })
                    st.session_state.temp_shopping_cart = []
                    st.success(L.get("success_submit", "").format(status=status_final))
                    st.rerun()

    # ----------------------------------------------------
    # 📊 2. 宿舍伙食費月度統計與單價稽核
    # ----------------------------------------------------
    with tab_summary:
        st.markdown(f"### {L.get('header_summary', '')}")
        if st.session_state.get("dorm_catering_db"):
            df_summary = pd.DataFrame(st.session_state.dorm_catering_db)
            st.dataframe(df_summary[["date", "people_count", "total_budget", "total_actual", "buyer", "status"]], use_container_width=True)
            
            st.markdown("---")
            st.markdown(f"##### {L.get('header_drilldown', '')}")
            records_list = [str(r.get("date", "")) + " - " + str(r.get("buyer", "")) for r in st.session_state.dorm_catering_db]
            if records_list:
                sel_date_record = st.selectbox(L.get("sel_record_date", "Select"), records_list)
                target_date = sel_date_record.split(" - ")[0]
                target_obj = next((r for r in st.session_state.dorm_catering_db if r.get("date") == target_date), None)
                if target_obj:
                    st.write(f"**{L.get('lbl_date', 'Date')}**：`{target_obj.get('date', '')}` | **{L.get('lbl_people', 'People')}**：`{target_obj.get('people_count', 0)}` | **{L.get('lbl_total_actual', 'Total').split('/')[0]}**：`{target_obj.get('total_actual', 0):,.0f} VND`")
                    if target_obj.get("items"):
                        st.dataframe(pd.DataFrame(target_obj["items"]), use_container_width=True)
        else:
            st.info(L.get("no_records", "No records."))

    # ----------------------------------------------------
    # ⚙️ 3. 西寧在地食材市場參考單價與趨勢設定
    # ----------------------------------------------------
    with tab_prices:
        st.markdown(f"### {L.get('header_prices', '')}")
        st.info(L.get("caption_prices", ""))

        # 設定容許浮動門檻
        st.session_state.allowed_price_margin_pct = st.slider(
            L.get("lbl_slider_margin", "Margin %"), 
            min_value=5.0, max_value=30.0, value=float(st.session_state.get("allowed_price_margin_pct", 15.0)), step=1.0,
            help=L.get("help_slider_margin", "")
        )

        st.markdown("---")
        st.markdown(f"#### {L.get('header_adjust_prices', '')}")

        with st.form("form_update_dynamic_prices"):
            updated_dict = {}
            for food_item, info in st.session_state.market_price_dynamic.items():
                col_p1, col_p2 = st.columns([2, 1])
                with col_p1:
                    new_p = st.number_input(f"{food_item} (VND/kg)", min_value=1000.0, value=float(info.get("price", 10000.0)), step=5000.0)
                with col_p2:
                    short_label = food_item.split(" (")[0]
                    new_delta = st.text_input(f"{L.get('lbl_trend_tag', 'Trend')} ({short_label})", value=str(info.get("delta", "0 VND")))

                updated_dict[food_item] = {"price": new_p, "delta": new_delta, "status": "updated"}

            if st.form_submit_button(L.get("btn_save_prices", "Save"), type="primary"):
                st.session_state.market_price_dynamic = updated_dict
                st.success(L.get("success_save_prices", "Saved."))
                st.rerun()

def show(engine=None, lang="繁體中文", **kwargs):
    render_dorm_catering_module(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_dorm_catering_module(engine=engine, lang=lang, **kwargs)
