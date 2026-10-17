import streamlit as st
import pandas as pd
import datetime
import re
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 三語系字典 (i18n)
# ----------------------------------------------------
ASSETS_I18N = {
    "繁體中文": {
        "title": "🏢 固定資產與設備管理 (Fixed Assets & Equipment)",
        "caption": "維護廠區機器設備與公務車輛，提供 5 年直線折舊試算、資產殘值查詢與 Excel 智慧批次匯入。",
        "tab_add": "➕ 新增固定資產",
        "tab_excel": "📊 Excel 智慧批次匯入",
        "tab_list": "📋 固定資產清冊與 5 年折舊攤分試算",
        "lbl_code": "資產/合約編號 *",
        "lbl_name": "資產名稱 *",
        "lbl_brand": "品牌與型號 / 廠牌",
        "lbl_status": "目前狀態",
        "lbl_site": "存放廠區/據點 *",
        "lbl_dept": "使用/權責部門 *",
        "lbl_purchase_date": "📅 購買/取得日期 *",
        "lbl_cost": "💰 取得原價成本 (VND) *",
        "lbl_salvage": "💰 預估 5 年後殘值 (VND) [預設 10%]",
        "lbl_cat": "資產類別 *",
        "lbl_custodian": "👤 保管人姓名 / 負責人 *",
        "lbl_plate": "🚗 車牌號碼 (Biển số xe) *",
        "lbl_v_model": "🚗 車輛廠牌與詳細型號 *",
        "lbl_inspection_date": "🚗 車輛驗車/行照到期日",
        "btn_submit": "📌 確認新增固定資產",
        "lbl_search": "🔍 輸入關鍵字查詢資產/車牌/編號/保管人："
    },
    "English": {
        "title": "🏢 Fixed Assets & Equipment Management",
        "caption": "Manage plant equipment and vehicles with depreciation and Excel batch import.",
        "tab_add": "➕ Add Asset",
        "tab_excel": "📊 Excel Batch Import",
        "tab_list": "📋 Asset Inventory & 5-Year Depreciation",
        "lbl_code": "Asset Code *",
        "lbl_name": "Asset Name *",
        "lbl_brand": "Brand & Model",
        "lbl_status": "Status",
        "lbl_site": "Plant Location *",
        "lbl_dept": "Department *",
        "lbl_purchase_date": "📅 Purchase Date *",
        "lbl_cost": "💰 Cost Price (VND) *",
        "lbl_salvage": "💰 Est. Residual Value (VND)",
        "lbl_cat": "Asset Category *",
        "lbl_custodian": "👤 Custodian / Responsible Person *",
        "lbl_plate": "🚗 License Plate No. *",
        "lbl_v_model": "🚗 Vehicle Brand & Model *",
        "lbl_inspection_date": "🚗 Inspection Expiry Date",
        "btn_submit": "📌 Save Asset",
        "lbl_search": "🔍 Search Asset / Plate / Code / Custodian:"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Tài sản cố định & Xe công tác",
        "caption": "Quản lý máy móc, xe công ty, tính khấu hao và nhập Excel tự động.",
        "tab_add": "➕ Thêm mới tài sản",
        "tab_excel": "📊 Nhập Excel hàng loạt",
        "tab_list": "📋 Danh sách tài sản & Khấu hao 5 năm",
        "lbl_code": "Mã tài sản *",
        "lbl_name": "Tên tài sản *",
        "lbl_brand": "Nhãn hiệu & Model",
        "lbl_status": "Trạng thái",
        "lbl_site": "Nhà xưởng / Vị trí *",
        "lbl_dept": "Bộ phận sử dụng *",
        "lbl_purchase_date": "📅 Ngày mua *",
        "lbl_cost": "💰 Nguyên giá (VND) *",
        "lbl_salvage": "💰 Giá trị thanh lý dự kiến (VND)",
        "lbl_cat": "Phân loại tài sản *",
        "lbl_custodian": "👤 Người quản lý / Trách nhiệm *",
        "lbl_plate": "🚗 Biển số xe *",
        "lbl_v_model": "🚗 Hiệu xe & Dòng xe *",
        "lbl_inspection_date": "🚗 Hạn đăng kiểm xe",
        "btn_submit": "📌 Lưu tài sản mới",
        "lbl_search": "🔍 Tìm kiếm tài sản / Biển số / Mã / Người quản lý:"
    }
}

ASSET_CATEGORIES = [
    "🚗 車輛 (公務車/卡車/堆高機)",
    "🏭 機器設備與配電盤生產線",
    "🏢 廠房土地與宿舍 (固定資產)",
    "📄 辦公室租賃合約 / 廠房租賃",
    "💻 資訊IT設備與伺服器",
    "📦 辦公傢俱與其他資產"
]

DEPT_OPTIONS = [
    "總經理室 (Executive Office)",
    "管理部 (Management Dept)",
    "財務部 (Finance Dept)",
    "工程與設計管理中心 (Engineering & Design Center)",
    "生產部 (Production Dept)",
    "資訊管理部 (IT & System)",
    "工務與工地現場 (Site Operations)"
]

SITE_OPTIONS = [
    "越南西寧廠 (Tay Ninh)",
    "越南海防廠 (Hai Phong)",
    "胡志明辦公室 (HCMC Office)"
]

def parse_formatted_amount(val_str):
    if not val_str:
        return 0.0
    clean_str = re.sub(r"[^\d]", "", str(val_str))
    return float(clean_str) if clean_str else 0.0

def format_vnd_input(amount):
    try:
        val = float(amount)
        return f"{val:,.0f}".replace(",", ".")
    except Exception:
        return str(amount)

def format_vnd(amount):
    try:
        val = float(amount)
        return f"{val:,.0f}".replace(",", ".") + " VND"
    except Exception:
        return f"{amount} VND"

def calculate_5y_depreciation(cost, salvage, purchase_date_str):
    try:
        cost_val = float(cost or 0)
        salvage_val = float(salvage or (cost_val * 0.1))
        
        if isinstance(purchase_date_str, (datetime.date, datetime.datetime)):
            p_date = purchase_date_str
        else:
            p_date = datetime.datetime.strptime(str(purchase_date_str)[:10], "%Y-%m-%d").date()
            
        today = datetime.date.today()
        months_used = (today.year - p_date.year) * 12 + (today.month - p_date.month)
        if months_used < 0:
            months_used =
