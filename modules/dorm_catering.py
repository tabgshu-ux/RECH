import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 幹部宿舍與餐飲採購控管模組多語系字典 (i18n)
# ----------------------------------------------------
CATERING_I18N = {
    "繁體中文": {
        "title": "🥗 總務部 - 幹部宿舍伙食採購與防浮報控管中心 (西寧廠)",
        "caption": "管控幹部宿舍每日買菜預算、食材採購明細、照片存證與單價防浮報稽核 (對照西寧傳統市場/Co.opmart行情)。",
        "tab_daily": "📝 每日買菜記帳與食材拍照存證",
        "tab_summary": "📊 宿舍伙食費月度統計與單價稽核",
        "tab_prices": "⚙️ 西寧在地食材市場參考單價設定 (防浮報基準)",
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
        "alert_price_anomaly": "⚠️ 警告：部分食材採購單價高於西寧市場參考價 20% 以上！可能存在浮報風險！"
    },
    "Tiếng Việt": {
        "title": "🥗 Quản lý Báo cơm & Mua thực phẩm Ký túc xá Cán bộ (Tây Ninh)",
        "caption": "Quản lý chi phí đi chợ hàng ngày, kiểm soát đơn giá thực phẩm và đối soát hình ảnh hóa đơn.",
        "tab_daily": "📝 Nhập chi phí đi chợ & Ảnh chụp",
        "tab_summary": "📊 Báo cáo chi phí ăn uống tháng",
        "tab_prices": "⚙️ Cấu hình đơn giá tham chiếu thị trường Tây Ninh",
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
        "alert_price_anomaly": "⚠️ Cảnh báo: Đơn giá cao hơn giá thị trường Tây Ninh!"
    },
    "English": {
        "title": "🥗 GA - Dormitory Catering & Food Procurement Control (Tay Ninh)",
        "caption": "Manage daily grocery budgets, track food item procurement, enforce photo evidence, and audit market prices.",
        "tab_daily": "📝 Daily Grocery Logging & Photo Upload",
        "tab_summary": "📊 Monthly Expense & Price Anomaly Audit",
        "tab_prices": "⚙️ Tay Ninh Market Benchmark Price Settings",
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
        "alert_price_anomaly": "⚠️ Warning: Item unit price exceeds Tay Ninh benchmark price by 20%+"
    }
}

# ----------------------------------------------------
# 🛒 西寧在地市場與 Co.opmart 預設物價基準 (VND/kg)
# ----------------------------------------------------
DEFAULT_TAY_NINH_MARKET_PRICES = {
    "豬肉 - 腿肉/肩肉 (Thịt heo đùi/vai)":
