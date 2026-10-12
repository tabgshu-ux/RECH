import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 幹部宿舍與餐飲採購控管模組多語系字典 (i18n)
# ----------------------------------------------------
CATERING_I18N = {
    "繁體中文": {
        "title": "🥗 總務部 - 幹部宿舍伙食採購與防浮報控管中心",
        "caption": "管控幹部宿舍每日買菜預算、食材採購明細、照片存證與單價防浮報稽核。",
        "tab_daily": "📝 每日買菜記帳與食材拍照存證",
        "tab_summary": "📊 宿舍伙食費月度統計與單價稽核",
        "tab_prices": "⚙️ 常見食材市場參考單價設定 (防浮報基準)",
        "lbl_date": "買菜/用餐日期",
        "lbl_people": "今日用餐幹部人數 (人)",
        "lbl_budget_cap": "每人每日預算基準 (VND/人)",
        "lbl_buyer": "採購經辦 / 總務人員",
        "lbl_item": "食材品項名稱",
        "lbl_qty": "採購數量 (kg / 包 / 箱)",
        "lbl_unit_price": "採購單價 (VND)",
        "lbl_photo": "📸 上傳攤販收據小票與食材秤重照片 (強制拍照)",
        "btn_add_item": "➕ 新增食材採購明细",
        "btn_submit_daily": "🚀 提交今日買菜支出並進行防浮報稽核",
        "alert_over_budget": "⚠️ 警告：今日買菜總金額超過「幹部人數 × 預算基準」上限！須總務主管簽核。",
        "alert_price_anomaly": "⚠️ 警告：品項 [{item}] 單價 ({price:,.0f} VND) 高於市場參考價 ({ref:,.0f} VND) 達 {diff:.0f}%！可能存在浮報風險！"
    },
    "Tiếng Việt": {
        "title": "🥗 Quản lý Báo cơm & Mua thực phẩm Ký túc xá Cán bộ",
        "caption": "Quản lý chi phí đi chợ hàng ngày, kiểm soát đơn giá thực phẩm và đối soát hình ảnh.",
        "tab_daily": "📝 Nhập chi phí đi chợ & Ảnh chụp",
        "tab_summary": "📊 Báo cáo chi phí ăn uống tháng",
        "tab_prices": "⚙️ Cấu hình đơn giá tham chiếu thị trường",
        "lbl_date": "Ngày đi chợ",
        "lbl_people": "Số lượng cán bộ ăn (Người)",
        "lbl_budget_cap": "Định mức/người/ngày (VND)",
        "lbl_buyer": "Người đi chợ / Tổng vụ",
        "lbl_item": "Tên thực phẩm",
        "lbl_qty": "Số lượng (kg / gói / thùng)",
        "lbl_unit_price": "Đơn giá (VND)",
        "lbl_photo": "📸 Tải ảnh hóa đơn & Ảnh cân thực phẩm",
        "btn_add_item": "➕ Thêm món",
        "btn_submit_daily": "🚀 Lưu chi phí & Kiểm tra đơn giá",
        "alert_over_budget": "⚠️ Cảnh báo: Tổng chi vượt ngân sách định mức!",
        "alert_price_anomaly": "⚠️ Cảnh báo: Đơn giá [{item}] cao hơn giá thị trường!"
    }
}

def render_dorm_catering_module(lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = CATERING_I18N.get(active_lang, CATERING_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 1. 初始化市場參考價格字典 (防浮報基準)
    if "market_price_ref" not in st.session_state:
        st.session_state.market_price_ref = {
            "豬肉 (Thịt heo)": 120000.0,
            "雞肉 (Thịt gà)": 80000.0,
            "牛肉 (Thịt bò)": 250000.0,
            "鮮魚/海鮮 (Cá/Hải sản)": 90000.0,
            "蔬菜類 (Rau củ)": 25000.0,
            "雞蛋 (Trứng gà)": 35000.0,   # 每打/10顆
            "食用油/調味料 (Gia vị)": 50000.0
        }

    # 2. 初始化買菜歷史數據庫
    if "dorm_catering_db" not in st.session_state:
        st.session_state.dorm_catering_db = [
            {
                "date": "2026-10-12",
                "people_count": 12,
                "budget_cap_per_person": 100000.0,
                "total_budget": 1200000.0,
                "total_actual": 1150000.0,
                "buyer": "阿姨 / 總務李專員",
                "status": "🟢 正常 (符合預算與市場價)",
                "photo_uploaded": True,
                "items": [
                    {"item": "豬肉 (Thịt heo)", "qty": 4.0, "unit_price": 125000.0, "amount": 500000.0, "flag": "🟢 正常"},
                    {"item": "蔬菜類 (Rau củ)", "qty": 6.0, "unit_price": 25000.0, "amount": 150000.0, "flag": "🟢 正常"},
                    {"item": "鮮魚/海鮮 (Cá/Hải sản)", "qty": 5.0, "unit_price": 100000.0, "amount": 500000.0, "flag": "🟡 稍高 (高出11%)"}
                ]
            }
        ]

    tab_daily, tab_summary, tab_prices = st.tabs([
        L["tab_daily"], L["tab_summary"], L["tab_prices"]
    ])

    # ----------------------------------------------------
    # 📝 1. 每日買菜記帳與防浮報審核
    # ----------------------------------------------------
    with tab_daily:
        st.markdown("### 🛒 每日幹部食堂買菜支出登記與防浮報稽核")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            buy_date = st.date_input(L["lbl_date"], value=datetime.date.today())
            buyer_name = st.text_input(L["lbl_buyer"], value="煮菜阿姨 / 總務專員")
        with c2:
            people_cnt = st.number_input(L["lbl_people"], min_value=1, value=12, step=1)
            cap_per_person = st.number_input(L["lbl_budget_cap"], min_value=10000.0, value=100000.0, step=5000.0)
        with c3:
            max_allowed_budget = people_cnt * cap_per_person
            st.metric("今日伙食總預算上限", f"{max_allowed_budget:,.0f} VND")
            st.caption(f"公式：{people_cnt} 人 × {cap_per_person:,.0f} VND")

        st.markdown("---")
        st.markdown("#### 🥦 食材採購明細錄入 (動態防浮報稽核)")

        # 使用 Session State 暫存當次輸入的菜單列表
        if "temp_shopping_cart" not in st.session_state:
            st.session_state.temp_shopping_cart = []

        with st.form("form_add_food_item"):
            col_i1, col_i2, col_i3 = st.columns([2, 1, 1.5])
            with col_i1:
                item_name = st.selectbox(L["lbl_item"], list(st.session_state.market_price_ref.keys()) + ["其他雜項 (Khác)"])
            with col_i2:
                item_qty = st.number_input(L["lbl_qty"], min_value=0.1, value=1.0, step=0.5)
            with col_i3:
                ref_p = st.session_state.market_price_ref.get(item_name, 50000.0)
                item_price = st.number_input(f"{L['lbl_unit_price']} (參考價: {ref_p:,.0f})", min_value=0.0, value=ref_p, step=5000.0)

            add_item_btn = st.form_submit_button(L["btn_add_item"], type="secondary")
            if add_item_btn:
                amt = item_qty * item_price
                flag_status = "🟢 正常"
                if item_name in st.session_state.market_price_ref:
                    ref_price = st.session_state.market_price_ref[item_name]
                    if item_price > ref_price * 1.2:
                        diff_pct = ((item_price - ref_price) / ref_price) * 100
                        flag_status = f"🔴 偏高 (高出 {diff_pct:.0f}%)"
                    elif item_price > ref_price * 1.05:
                        flag_status = "🟡 稍高"

                st.session_state.temp_shopping_cart.append({
                    "item": item_name,
                    "qty": item_qty,
                    "unit_price": item_price,
                    "amount": amt,
                    "flag": flag_status
                })
                st.rerun()

        # 展示已加入的食材列表
        if st.session_state.temp_shopping_cart:
            st.markdown("##### 📋 今日已加入食材清單：")
            df_temp = pd.DataFrame(st.session_state.temp_shopping_cart)
            st.dataframe(df_temp, use_container_width=True)

            total_actual_amt = df_temp["amount"].sum()
            
            # 檢測是否有單價異常
            has_price_anomaly = any("🔴" in row["flag"] for row in st.session_state.temp_shopping_cart)
            is_over_budget = total_actual_amt > max_allowed_budget

            st.markdown("---")
            st.markdown(f"### 💰 採購總金額：`{total_actual_amt:,.0f} VND` / 預算上限：`{max_allowed_budget:,.0f} VND`")

            if is_over_budget:
                st.error(L["alert_over_budget"])
            if has_price_anomaly:
                st.warning("⚠️ 警告：部分食材採購單價高出市場參考價 20% 以上！請確認是否浮報或拍照存證！")

            # 強制照片上傳存證
            uploaded_receipt = st.file_uploader(L["lbl_photo"], type=["jpg", "jpeg", "png"])

            if st.button(L["btn_submit_daily"], type="primary", use_container_width=True):
                if not uploaded_receipt:
                    st.error("❌ 系統防偷與防浮報鐵律：請務必拍照並上傳【菜市場收據小票與食材秤重照片】方可結算！")
                else:
                    status_final = "🟢 正常核銷"
                    if is_over_budget or has_price_anomaly:
                        status_final = "⚠️ 需總務主管審核 (單價偏高或超支)"

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
                    st.success(f"✅ 今日買菜支出已成功登錄！狀態：`{status_final}`")
                    st.rerun()

    # ----------------------------------------------------
    # 📊 2. 宿舍伙食費月度統計與單價稽核
    # ----------------------------------------------------
    with tab_summary:
        st.markdown("### 📊 幹部宿舍伙食費歷史月度報表與異常稽核")
        if st.session_state.dorm_catering_db:
            df_summary = pd.DataFrame(st.session_state.dorm_catering_db)
            st.dataframe(df_summary[["date", "people_count", "total_budget", "total_actual", "buyer", "status"]], use_container_width=True)
            
            st.markdown("---")
            st.markdown("##### 🔍 查看特定日期買菜照片與食材明細穿透")
            sel_date_record = st.selectbox("選擇日期查看明細", [r["date"] + " - " + r["buyer"] for r in st.session_state.dorm_catering_db])
            target_date = sel_date_record.split(" - ")[0]
            target_obj = next((r for r in st.session_state.dorm_catering_db if r["date"] == target_date), None)
            if target_obj:
                st.write(f"**日期**：`{target_obj['date']}` | **用餐人數**：`{target_obj['people_count']} 人` | **實際支出**：`{target_obj['total_actual']:,.0f} VND`")
                st.dataframe(pd.DataFrame(target_obj["items"]), use_container_width=True)
        else:
            st.info("目前尚無買菜支出紀錄。")

    # ----------------------------------------------------
    # ⚙️ 3. 常見食材市場參考單價設定 (防浮報基準)
    # ----------------------------------------------------
    with tab_prices:
        st.markdown("### ⚙️ 當地市場食材參考單價設定 (越南西寧 / 海防菜市場行情)")
        st.caption("總務主管可定期調整此參考單價，當買菜阿姨輸入超過此價格一定比例時，系統會自動警告。")

        with st.form("form_update_market_prices"):
            updated_dict = {}
            for item, p_val in st.session_state.market_price_ref.items():
                updated_dict[item] = st.number_input(f"{item} (VND/kg)", min_value=1000.0, value=float(p_val), step=5000.0)

            if st.form_submit_button("💾 儲存最新市場參考價格字典", type="primary"):
                st.session_state.market_price_ref = updated_dict
                st.success("✅ 市場參考價格已更新！即日起自動套用為最新防浮報基準。")
                st.rerun()

def show(lang="繁體中文", **kwargs):
    render_dorm_catering_module(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_dorm_catering_module(lang, **kwargs)
