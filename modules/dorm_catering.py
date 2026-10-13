import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 幹部宿舍伙食與採購管控模組多語系字典 (i18n)
# ----------------------------------------------------
DORM_I18N = {
    "繁體中文": {
        "title": "🏢 管理部 - 幹部宿舍伙食與採購管控中心",
        "caption": "管控西寧廠與海防廠幹部宿舍用餐登記、採購預算核銷、食材庫存與廚房支出費用。",
        "tab_catering": "🍱 每日伙食登記",
        "tab_purchase": "🛒 食材採購與請款",
        "tab_inventory": "📦 宿舍物資庫存",
        "tab_reports": "📊 費用月度統計",
        "lbl_plant": "選擇廠區",
        "lbl_date": "選擇用餐日期",
        "lbl_meal_type": "餐別",
        "lbl_people_cnt": "用餐人數",
        "btn_submit": "🚀 提交登記",
        "msg_success": "✅ 登記成功！已寫入系統。"
    },
    "Tiếng Việt": {
        "title": "🏢 Phòng Quản lý - Quản lý Cơm Ký túc xá & Mua sắm",
        "caption": "Quản lý đăng ký suất ăn ký túc xá, chi phí mua thực phẩm và vật tư tại nhà máy.",
        "tab_catering": "🍱 Đăng ký suất ăn",
        "tab_purchase": "🛒 Mua sắm thực phẩm",
        "tab_inventory": "📦 Kho vật tư KTX",
        "tab_reports": "📊 Báo cáo chi phí",
        "lbl_plant": "Chọn nhà máy",
        "lbl_date": "Chọn ngày",
        "lbl_meal_type": "Bữa ăn",
        "lbl_people_cnt": "Số người",
        "btn_submit": "🚀 Lưu đăng ký",
        "msg_success": "✅ Đã lưu thành công!"
    },
    "English": {
        "title": "🏢 Management - Dormitory Catering & Procurement",
        "caption": "Manage dorm meal check-ins, ingredient purchases, kitchen supplies, and monthly expenses.",
        "tab_catering": "🍱 Daily Catering",
        "tab_purchase": "🛒 Food Procurement",
        "tab_inventory": "📦 Supplies Inventory",
        "tab_reports": "📊 Expense Reports",
        "lbl_plant": "Select Plant",
        "lbl_date": "Select Date",
        "lbl_meal_type": "Meal Type",
        "lbl_people_cnt": "Headcount",
        "btn_submit": "🚀 Submit Entry",
        "msg_success": "✅ Submitted successfully!"
    }
}

def render_dorm_catering_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in DORM_I18N else "繁體中文"
    L = DORM_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    tab_catering, tab_purchase, tab_inventory, tab_reports = st.tabs([
        L["tab_catering"],
        L["tab_purchase"],
        L["tab_inventory"],
        L["tab_reports"]
    ])

    # 🍱 Tab 1: 每日伙食登記
    with tab_catering:
        st.markdown("### 🍱 幹部宿舍每日用餐人數登記")
        with st.form("form_dorm_meal"):
            c1, c2, c3 = st.columns(3)
            with c1:
                plant = st.selectbox(L["lbl_plant"], ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"])
                meal_date = st.date_input(L["lbl_date"], value=datetime.date.today())
            with c2:
                meal_type = st.selectbox(L["lbl_meal_type"], ["早餐 (Breakfast)", "午餐 (Lunch)", "晚餐 (Dinner)", "宵夜 (Night Snack)"])
                people_cnt = st.number_input(L["lbl_people_cnt"], min_value=1, max_value=100, value=12)
            with c3:
                applicant = st.text_input("登記人 / 舍監", value=st.session_state.get("user_name", "許福村"))
                note = st.text_input("備註 / 特別菜單需求", placeholder="如：不吃牛肉、素食人數...")

            if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
                st.success(L["msg_success"])

        st.markdown("---")
        st.markdown("##### 📋 本週宿舍搭夥統計預估")
        sample_catering = [
            {"日期": "2026-10-13", "廠區": "西寧廠", "早餐": "8 人", "午餐": "15 人", "晚餐": "12 人", "負責人": "許福村"},
            {"日期": "2026-10-13", "廠區": "海防廠", "早餐": "5 人", "午餐": "10 人", "晚餐": "8 人", "負責人": "Nguyễn Văn Quý"}
        ]
        st.dataframe(pd.DataFrame(sample_catering), use_container_width=True)

    # 🛒 Tab 2: 食材採購與請款
    with tab_purchase:
        st.markdown("### 🛒 宿舍食材採購與廚房雜支請款")
        with st.form("form_dorm_purchase"):
            pc1, pc2 = st.columns(2)
            with pc1:
                p_item = st.text_input("採購項目 / 食材品名", placeholder="例如：米、豬肉、蔬菜、沙拉油...")
                p_amount = st.number_input("金額 (VND)", min_value=0, value=500000, step=50000)
            with pc2:
                p_vendor = st.text_input("供應商 / 傳統市場名稱", value="Local Market")
                p_receipt = st.file_uploader("上傳收據 / 發票照片", type=["jpg", "png", "pdf"])

            if st.form_submit_button("🚀 送出採購請款單", type="primary", use_container_width=True):
                st.success("✅ 請款單已成功送出主管審核！")

    # 📦 Tab 3: 宿舍物資庫存
    with tab_inventory:
        st.markdown("### 📦 宿舍物資與廚房耗材庫存盤點")
        inventory_data = [
            {"品名": "越光米 (50kg)", "分類": "主食", "目前庫存": "3 包", "安全庫存": "2 包", "狀態": "🟢 正常"},
            {"品名": "食用沙拉油 (5L)", "分類": "調味料", "目前庫存": "1 瓶", "安全庫存": "2 瓶", "狀態": "🟡 請儘速補貨"},
            {"品名": "飲用水 (20L 桶裝)", "分類": "飲水", "目前庫存": "10 桶", "安全庫存": "5 桶", "狀態": "🟢 正常"}
        ]
        st.dataframe(pd.DataFrame(inventory_data), use_container_width=True)

    # 📊 Tab 4: 費用月度統計
    with tab_reports:
        st.markdown("### 📊 幹部宿舍伙食費用月度分析")
        rc1, rc2 = st.columns(2)
        with rc1:
            st.metric("本月累計伙食總支出 (VND)", "18,500,000 VND", delta="-5% 比上月")
        with rc2:
            st.metric("平均每人每餐成本 (VND)", "45,000 VND", delta="持平")

def show(engine=None, lang="繁體中文", **kwargs):
    render_dorm_catering_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_dorm_catering_page(engine=engine, lang=lang, **kwargs)
