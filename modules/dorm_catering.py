import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 幹部宿舍與餐飲採購控管模組多語系字典 (i18n)
# ----------------------------------------------------
CATERING_I18N = {
    "繁體中文": {
        "title": "🥗 總務部 - 幹部宿舍伙食採購與防浮報控管中心 (西寧廠)",
        "caption": "管控幹部宿舍每日買菜預算、食材採購明細、照片存證與西寧在地物價即時浮動比對。",
        "tab_daily": "📝 每日買菜記帳與食材拍照存證",
        "tab_summary": "📊 宿舍伙食費月度統計與單價稽核",
        "tab_prices": "⚙️ 西寧在地物價即時浮動與參考單價維護",
        "lbl_date": "買菜/用餐日期",
        "lbl_people": "今日用餐幹部人數 (人)",
        "lbl_budget_cap": "每人每日預算基準 (VND/人)",
        "lbl_buyer": "採購經辦 / 總務人員",
        "lbl_item": "食材品項名稱",
        "lbl_qty": "採購數量 (kg / 包 / 箱)",
        "lbl_unit_price": "採購單價 (VND)",
        "lbl_photo": "📸 上傳攤販收據小票與食材秤重照片 (強制拍照存證)",
        "btn_add_item": "➕ 新增食材採購明細",
        "btn_submit_daily": "🚀 提交今日買菜支出並進行防浮報稽核",
        "alert_over_budget": "⚠️ 警告：今日買菜總金額超過「幹部人數 × 預算基準」上限！須總務主管簽核。",
        "alert_price_anomaly": "⚠️ 警告：部分食材採購單價高於西寧市場參考價與容許浮動區間！可能存在浮報風險！"
    },
    "Tiếng Việt": {
        "title": "🥗 Quản lý Báo cơm & Mua thực phẩm Ký túc xá Cán bộ (Tây Ninh)",
        "caption": "Quản lý chi phí đi chợ hàng ngày, kiểm soát đơn giá thực phẩm và đối soát biến động giá thị trường Tây Ninh.",
        "tab_daily": "📝 Nhập chi phí đi chợ & Ảnh chụp",
        "tab_summary": "📊 Báo cáo chi phí ăn uống tháng",
        "tab_prices": "⚙️ Cấu hình đơn giá & Biến động giá thị trường Tây Ninh",
        "lbl_date": "Ngày đi chợ",
        "lbl_people": "Số lượng cán bộ ăn (Người)",
        "lbl_budget_cap": "Định mức/người/ngày (VND)",
        "lbl_buyer": "Người đi chợ / Tổng vụ",
        "lbl_item": "Tên thực phẩm",
        "lbl_qty": "Số lượng (kg / gói / thùng)",
        "lbl_unit_price": "Đơn giá (VND)",
        "lbl_photo": "📸 Tải ảnh hóa đơn & Ảnh cân thực phẩm (Bắt buộc)",
        "btn_add_item": "➕ Thêm món",
        "btn_submit_daily": "🚀 Lưu chi phí & Kiểm tra đơn giá",
        "alert_over_budget": "⚠️ Cảnh báo: Tổng chi vượt ngân sách định mức!",
        "alert_price_anomaly": "⚠️ Cảnh báo: Đơn giá cao hơn biến động cho phép của thị trường Tây Ninh!"
    },
    "English": {
        "title": "🥗 GA - Dormitory Catering & Food Procurement Control (Tay Ninh)",
        "caption": "Manage daily grocery budgets, track food item procurement, enforce photo evidence, and monitor real-time Tay Ninh market price trends.",
        "tab_daily": "📝 Daily Grocery Logging & Photo Upload",
        "tab_summary": "📊 Monthly Expense & Price Anomaly Audit",
        "tab_prices": "⚙️ Tay Ninh Real-time Market Price & Trend Settings",
        "lbl_date": "Date",
        "lbl_people": "Number of Staff Dining",
        "lbl_budget_cap": "Daily Cap per Person (VND)",
        "lbl_buyer": "Buyer / GA Staff",
        "lbl_item": "Food Item",
        "lbl_qty": "Quantity (kg / pack / box)",
        "lbl_unit_price": "Unit Price (VND)",
        "lbl_photo": "📸 Upload Receipt & Food Weighing Photo (Mandatory)",
        "btn_add_item": "➕ Add Food Item",
        "btn_submit_daily": "🚀 Submit Daily Expense & Perform Audit",
        "alert_over_budget": "⚠️ Warning: Total grocery cost exceeds the budget cap!",
        "alert_price_anomaly": "⚠️ Warning: Item unit price exceeds Tay Ninh benchmark price & allowed fluctuation margin!"
    }
}

# ----------------------------------------------------
# 🛒 西寧在地市場與 Co.opmart 即時物價與浮動趨勢基準
# ----------------------------------------------------
DEFAULT_TAY_NINH_DYNAMIC_PRICES = {
    "豬肉 - 腿肉/肩肉 (Thịt heo đùi/vai)": {"price": 105000.0, "delta": "+5,000 VND (雨季微漲)", "status": "up"},
    "豬肉 - 五花肉 (Thịt ba rọi)": {"price": 135000.0, "delta": "0 VND (平穩)", "status": "stable"},
    "雞肉 - 全雞/土雞 (Thịt gà)": {"price": 85000.0, "delta": "0 VND (平穩)", "status": "stable"},
    "牛肉 (Thịt bò)": {"price": 240000.0, "delta": "-10,000 VND (供給充沛)", "status": "down"},
    "鮮魚 - 吳郭魚/雷魚 (Cá diêu hồng/lóc)": {"price": 60000.0, "delta": "+2,000 VND (微漲)", "status": "up"},
    "鮮蝦 (Tôm tươi)": {"price": 160000.0, "delta": "0 VND (平穩)", "status": "stable"},
    "常見葉菜類 (Rau cải / Rau muống)": {"price": 22000.0, "delta": "+4,000 VND (雨季蔬菜減產)", "status": "up"},
    "根莖類/高麗菜 (Bắp cải / Củ quả)": {"price": 25000.0, "delta": "0 VND (平穩)", "status": "stable"},
    "雞蛋 (Trứng gà - 10顆)": {"price": 32000.0, "delta": "-1,000 VND (微跌)", "status": "down"},
    "白米 (Gạo thơm / Nàng Hoa)": {"price": 22000.0, "delta": "0 VND (平穩)", "status": "stable"},
    "食用油/調味料 (Dầu ăn / Gia vị)": {"price": 45000.0, "delta": "0 VND (平穩)", "status": "stable"}
}

def render_dorm_catering_module(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = CATERING_I18N.get(active_lang, CATERING_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 1. 初始化西寧即時動態物價與趨勢
    if "market_price_dynamic" not in st.session_state:
        st.session_state.market_price_dynamic = DEFAULT_TAY_NINH_DYNAMIC_PRICES.copy()

    # 2. 物價容許浮動範圍百分比 (預設允許市場波動 15%)
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
                "buyer": "阿姨 / 總務專員",
                "status": "🟢 正常 (符合預算與西寧物價浮動範圍)",
                "photo_uploaded": True,
                "items": [
                    {"item": "豬肉 - 腿肉/肩肉 (Thịt heo đùi/vai)", "qty": 4.0, "unit_price": 105000.0, "amount": 420000.0, "flag": "🟢 正常 (符合浮動行情)"},
                    {"item": "常見葉菜類 (Rau cải / Rau muống)", "qty": 6.0, "unit_price": 22000.0, "amount": 132000.0, "flag": "🟢 正常 (因雨季微漲)"},
                    {"item": "鮮魚 - 吳郭魚/雷魚 (Cá diêu hồng/lóc)", "qty": 5.0, "unit_price": 62000.0, "amount": 310000.0, "flag": "🟢 正常"}
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
        st.markdown("#### 🥦 食材採購明細錄入 (即時比對西寧物價浮動)")

        # 展示幾項熱門食材的西寧即時物價趨勢看板
        with st.expander("📈 點此展開【西寧當地最新食材物價行情與漲跌趨勢看板】", expanded=False):
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
                item_name = st.selectbox(L["lbl_item"], list(st.session_state.market_price_dynamic.keys()) + ["其他雜項 (Khác)"])
            with col_i2:
                item_qty = st.number_input(L["lbl_qty"], min_value=0.1, value=1.0, step=0.5)
            with col_i3:
                ref_info = st.session_state.market_price_dynamic.get(item_name, {"price": 50000.0, "delta": "0 VND"})
                ref_p = ref_info["price"]
                item_
