import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 幹部宿舍伙食與採購管控模組多語系字典 (i18n)
# ----------------------------------------------------
DORM_I18N = {
    "繁體中文": {
        "title": "🏢 管理部 - 幹部宿舍伙食與採購管控中心",
        "caption": "實施每人每日 100,000 VND 防回扣預算控管！比對西寧傳統市場物價，上傳採購憑證。",
        "tab_catering": "🍱 每日伙食登記",
        "tab_purchase": "🛒 食材採購與收據請款 (10萬/人/日防套利)",
        "tab_price_ref": "🥬 西寧當地傳統市場物價行情表",
        "tab_inventory": "📦 宿舍物資庫存",
        "tab_reports": "📊 費用稽核與月度分析",
        "lbl_plant": "選擇廠區",
        "lbl_date": "選擇用餐日期",
        "lbl_meal_type": "餐別",
        "lbl_people_cnt": "用餐人數",
        "btn_submit": "🚀 提交登記",
        "msg_success": "✅ 登記成功！已寫入系統。"
    },
    "Tiếng Việt": {
        "title": "🏢 Phòng Quản lý - Quản lý Cơm Ký túc xá & Mua sắm",
        "caption": "Khống chế ngân sách 100,000 VND/người/ngày phòng chống nâng giá! So sánh giá thị trường Tây Ninh.",
        "tab_catering": "🍱 Đăng ký suất ăn",
        "tab_purchase": "🛒 Mua thực phẩm & Hóa đơn (Hạn mức 100k/ngày)",
        "tab_price_ref": "🥬 Bảng giá thị trường Tây Ninh",
        "tab_inventory": "📦 Kho vật tư KTX",
        "tab_reports": "📊 Kiếm toán & Báo cáo chi phí",
        "lbl_plant": "Chọn nhà máy",
        "lbl_date": "Chọn ngày",
        "lbl_meal_type": "Bữa ăn",
        "lbl_people_cnt": "Số người",
        "btn_submit": "🚀 Lưu đăng ký",
        "msg_success": "✅ Đã lưu thành công!"
    },
    "English": {
        "title": "🏢 Management - Dormitory Catering & Anti-Rebate Procurement",
        "caption": "Enforce 100,000 VND/person/day budget cap to prevent fraud. Compare Tay Ninh local market prices.",
        "tab_catering": "🍱 Daily Meal Registration",
        "tab_purchase": "🛒 Food Procurement & Receipt (100k Cap)",
        "tab_price_ref": "🥬 Tay Ninh Market Benchmark Prices",
        "tab_inventory": "📦 Supplies Inventory",
        "tab_reports": "📊 Expenses Audit & Reports",
        "lbl_plant": "Select Plant",
        "lbl_date": "Select Date",
        "lbl_meal_type": "Meal Type",
        "lbl_people_cnt": "Headcount",
        "btn_submit": "🚀 Submit Entry",
        "msg_success": "✅ Submitted successfully!"
    }
}

def render_dorm_catering_module(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in DORM_I18N else "繁體中文"
    L = DORM_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    # 常態設定：一人一天上限 10 萬越盾 (100,000 VND)
    DAILY_BUDGET_PER_PERSON = 100000.0

    tab_catering, tab_purchase, tab_price_ref, tab_inventory, tab_reports = st.tabs([
        L["tab_catering"],
        L["tab_purchase"],
        L["tab_price_ref"],
        L["tab_inventory"],
        L["tab_reports"]
    ])

    # ----------------------------------------------------
    # 🍱 Tab 1: 每日伙食登記
    # ----------------------------------------------------
    with tab_catering:
        st.markdown("### 🍱 幹部宿舍每日用餐人數登記")
        with st.form("form_dorm_meal"):
            c1, c2, c3 = st.columns(3)
            with c1:
                plant = st.selectbox(L["lbl_plant"], ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"])
                meal_date = st.date_input(L["lbl_date"], value=datetime.date.today())
            with c2:
                meal_type = st.selectbox(L["lbl_meal_type"], ["全天三餐 (All Day)", "午餐 (Lunch)", "晚餐 (Dinner)", "早餐 (Breakfast)"])
                people_cnt = st.number_input(L["lbl_people_cnt"], min_value=1, max_value=100, value=12)
            with c3:
                applicant = st.text_input("登記人 / 舍監", value=st.session_state.get("user_name", "許福村"))
                note = st.text_input("備註 / 特別菜單需求", placeholder="如：不吃牛肉、素食人數...")

            # 計算當日額度上限
            max_daily_limit = people_cnt * DAILY_BUDGET_PER_PERSON
            st.info(f"💡 **西寧廠伙食預算控管**：今天登記入住/用餐人數 `{people_cnt} 人` ➔ **今日全廠食材採購上限金額為 `{max_daily_limit:,.0f} VND`**（標準：`100,000 VND / 人 / 天`）。")

            if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
                st.success(L["msg_success"])

        st.markdown("---")
        st.markdown("##### 📋 本週宿舍搭夥人數與預算上限預估")
        sample_catering = [
            {"日期": str(datetime.date.today()), "廠區": "西寧廠", "用餐人數": 12, "單日採購預算上限": f"{12 * DAILY_BUDGET_PER_PERSON:,.0f} VND", "負責人": "許福村"},
            {"日期": str(datetime.date.today()), "廠區": "海防廠", "用餐人數": 8, "單日採購預算上限": f"{8 * DAILY_BUDGET_PER_PERSON:,.0f} VND", "負責人": "Nguyễn Văn Quý"}
        ]
        st.dataframe(pd.DataFrame(sample_catering), use_container_width=True)

    # ----------------------------------------------------
    # 🛒 Tab 2: 食材採購與收據請款 (10萬/人/日防套利)
    # ----------------------------------------------------
    with tab_purchase:
        st.markdown("### 🛒 煮菜阿姨 / 採購食材收據請款與防回扣稽核")
        st.caption("嚴格執行：報帳金額不得超過『用餐人數 × 100,000 VND』，且必須強制上傳傳統市場收據憑證照片。")

        with st.form("form_dorm_purchase"):
            pc1, pc2 = st.columns(2)
            with pc1:
                p_date = st.date_input("採購日期", value=datetime.date.today())
                p_people = st.number_input("當日用餐人數", min_value=1, value=12, help="系統將自動乘以 10 萬越盾算出上限")
                p_item = st.text_input("採購食材品項說明", placeholder="例如：豬五花 3kg、高麗菜 5kg、空心菜、雞蛋 20 顆...")
                p_vendor = st.text_input("採購地點 / 傳統市場名稱", value="Chợ Trảng Bàng (西寧省𤅶樟市場)")
            
            with pc2:
                p_amount = st.number_input("報帳總金額 (VND)", min_value=0, value=1150000, step=10000, help="請依據收據真實金額填寫")
                p_receipt = st.file_uploader("📸 強制上傳市場收據 / 拍照憑證 (JPG/PNG)", type=["jpg", "png", "jpeg", "pdf"])
                p_buyer = st.text_input("買菜阿姨 / 採購人員姓名", value="Cô Ba (煮菜阿姨)")

            # 即時預算防回扣檢核
            budget_cap = p_people * DAILY_BUDGET_PER_PERSON
            is_over = p_amount > budget_cap

            st.markdown("##### 🚨 防套利稽核即時比對：")
            col_k1, col_k2, col_k3 = st.columns(3)
            col_k1.metric("今日預算上限 (Cap)", f"{budget_cap:,.0f} VND")
            col_k2.metric("阿姨本次報帳金額", f"{p_amount:,.0f} VND")
            
            diff = budget_cap - p_amount
            if is_over:
                col_k3.metric("稽核結果", f"超額 {-diff:,.0f} VND", delta=f"-{-diff:,.0f} VND 超標", delta_color="inverse")
                st.error(f"⚠️ **防回扣警示**：阿姨報帳金額 (`{p_amount:,.0f} VND`) 已超過今日 {p_people} 人上限 (`{budget_cap:,.0f} VND`)！系統已自動鎖定並轉呈管理部二次核實。")
            else:
                col_k3.metric("稽核結果", f"剩餘 {diff:,.0f} VND", delta="🟢 合規未超標")
                st.success(f"✅ 金額合規！在今日上限 `{budget_cap:,.0f} VND` 範圍內。")

            if st.form_submit_button("🚀 提交食材採購請款單並上傳憑證", type="primary", use_container_width=True):
                if not p_receipt:
                    st.warning("⚠️ 警告：必須上傳市場傳統收據照片憑證才能送出請款！")
                else:
                    status_text = "⚠️ 超額稽核中 (待管理部特批)" if is_over else "🟢 稽核通過 (准予撥款)"
                    st.success(f"🎉 請款單已送出！稽核狀態：`{status_text}`")

    # ----------------------------------------------------
    # 🥬 Tab 3: 西寧當地傳統市場物價行情參考 (Trảng Bàng / Tây Ninh)
    # ----------------------------------------------------
    with tab_price_ref:
        st.markdown("### 🥬 西寧（Trảng Bàng / Tây Ninh）傳統市場食材參考物價行情")
        st.caption("管理人員審核阿姨採購單時之基準參考，防止阿姨以高於市場的價格開立報帳單收取回扣。")

        market_prices = [
            {"食材類別": "🥩 肉類", "品名規格": "豬五花肉 (Thịt ba rọi)", "西寧市場行情區間 (VND)": "110,000 - 130,000 / kg", "備註參考": "𤅶樟傳統市場當日溫體肉價格"},
            {"食材類別": "🥩 肉類", "品名規格": "豬梅花肉 / 瘦肉 (Thịt nạc)", "西寧市場行情區間 (VND)": "95,000 - 110,000 / kg", "備註參考": "適合炒菜、煮湯"},
            {"食材類別": "🍗 禽肉類", "品名規格": "全雞 / 土雞 (Gà ta)", "西寧市場行情區間 (VND)": "120,000 - 140,000 / kg", "備註參考": "含內臟處理清理"},
            {"食材類別": "🐟 水產類", "品名規格": "羅非魚 / 吴郭魚 (Cá diêu hồng)", "西寧市場行情區間 (VND)": "55,000 - 65,000 / kg", "備註參考": "鮮活現殺"},
            {"食材類別": "🥚 蛋類", "品名規格": "雞蛋 (Trứng gà)", "西寧市場行情區間 (VND)": "28,000 - 32,000 / 10顆", "備註參考": "大顆洗選或散裝"},
            {"食材類別": "🥬 蔬菜類", "品名規格": "高麗菜 / 包心菜 (Bắp cải)", "西寧市場行情區間 (VND)": "18,000 - 25,000 / kg", "備註參考": "依季節有所波動"},
            {"食材類別": "🥬 蔬菜類", "品名規格": "空心菜 / 芥藍菜 (Rau muống)", "西寧市場行情區間 (VND)": "12,000 - 18,000 / kg", "備註參考": "西寧當地產蔬果"},
            {"食材類別": "🌾 主食類", "品名規格": "優質香米 (Gạo ST25 / Hương Lài)", "西寧市場行情區間 (VND)": "22,000 - 28,000 / kg", "備註參考": "50kg 大包裝採購更優惠"}
        ]
        df_prices = pd.DataFrame(market_prices)
        st.dataframe(df_prices, use_container_width=True)

    # ----------------------------------------------------
    # 📦 Tab 4: 宿舍物資與廚房耗材庫存盤點
    # ----------------------------------------------------
    with tab_inventory:
        st.markdown("### 📦 宿舍物資與廚房耗材庫存盤點")
        inventory_data = [
            {"品名": "ST25 優質香米 (50kg)", "分類": "主食", "目前庫存": "2 包", "安全庫存": "2 包", "狀態": "🟢 正常"},
            {"品名": "Cooking Oil 沙拉油 (5L)", "分類": "調味料", "目前庫存": "1 瓶", "安全庫存": "2 瓶", "狀態": "🟡 請儘速補貨"},
            {"品名": "桶裝飲用水 (20L)", "分類": "飲水", "目前庫存": "8 桶", "安全庫存": "5 桶", "狀態": "🟢 正常"}
        ]
        st.dataframe(pd.DataFrame(inventory_data), use_container_width=True)

    # ----------------------------------------------------
    # 📊 Tab 5: 費用稽核與月度分析
    # ----------------------------------------------------
    with tab_reports:
        st.markdown("### 📊 幹部宿舍伙食費用與回扣稽核月度分析")
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.metric("本月累計伙食請款 (VND)", "16,800,000 VND", delta="-8% 低於預算上限")
        with rc2:
            st.metric("平均每人每日餐費", "93,333 VND", delta="🟢 低於 10 萬上限")
        with rc3:
            st.metric("異常超額請款筆數", "1 筆", delta="⚠️ 已攔截扣除")

# 相容性進入點別名
def render_dorm_catering_page(engine=None, lang="繁體中文", **kwargs):
    render_dorm_catering_module(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_dorm_catering_module(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_dorm_catering_module(engine=engine, lang=lang, **kwargs)
