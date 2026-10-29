import streamlit as st
import importlib

def render_management_module(engine=None, lang="繁體中文", **kwargs):
    # 管理部內部的一級子選單（對應您截圖中的資料夾分類）
    sub_menus = {
        "繁體中文": [
            "📢 1. 公告欄與公告管理",
            "👤 2. 員工個人檔案與人事管理",
            "🏢 3. 廠內員工固定打卡與出勤紀錄",
            "📍 4. 外勤位置辦理與工地即時人數",
            "💰 13. 員工薪資計算與保險扣除",
            "🥗 5. 幹部宿舍伙食與採購控管",
            "🏭 6. 工作廠區管理",
            "🚗 7. 廠區車輛進出口門禁與派車審核",
            "🛠️ 8. 車輛維修保養紀錄",
            "🏢 12. 固定資產與設備管理",
            "🛒 9. 採購與應付付款 (AP)",
            "📋 10. 應收帳款與對帳管理中心 (AR)",
            "📊 11. 越南稅務標準財務報表 (Thông tư 200)",
            "📄 14. 電子發票綜合管理與 XML 歸檔"
        ],
        "Tiếng Việt": [
            "📢 1. Quản lý thông báo",
            "👤 2. Hồ sơ nhân sự",
            "🏢 3. Chấm công cố định",
            "📍 4. Quản lý vị trí & Nhân số",
            "💰 13. Tính lương & Bảo hiểm",
            "🥗 5. Ký túc xá & Suất ăn",
            "🏭 6. Quản lý nhà xưởng",
            "🚗 7. Quản lý cổng xe ra vào",
            "🛠️ 8. Bảo trì xe",
            "🏢 12. Quản lý tài sản cố định",
            "🛒 9. Mua hàng & Phải trả (AP)",
            "📋 10. Phải thu (AR)",
            "📊 11. Báo cáo thuế (Thông tư 200)",
            "📄 14. Hóa đơn điện tử XML"
        ],
        "English": [
            "📢 1. Announcements",
            "👤 2. Employee Profile",
            "🏢 3. Internal Attendance",
            "📍 4. Field GPS Attendance & Headcount",
            "💰 13. Payroll & Insurance",
            "🥗 5. Dorm & Catering",
            "🏭 6. Facility Management",
            "🚗 7. Vehicle Gate Log",
            "🛠️ 8. Vehicle Maintenance",
            "🏢 12. Asset Inventory",
            "🛒 9. Procurement & AP",
            "📋 10. Sales Order & AR",
            "📊 11. Vietnam Tax Reports",
            "📄 14. Invoice XML Archive"
        ]
    }

    current_lang = lang if lang in sub_menus else "繁體中文"
    menu_list = sub_menus[current_lang]

    # 在管理部內部使用橫向分頁或側邊選單切換子功能
    selected_sub = st.selectbox("📌 選擇管理部子模選項目 / Select Management Module", menu_list, key="mgmt_sub_menu_select")
    st.markdown("---")

    # 路由分發到對應的子資料夾檔案
    try:
        if "外勤位置辦理" in selected_sub or "Field GPS" in selected_sub or "Vị trí" in selected_sub:
            mod = importlib.import_module("modules.management.hr.field_gps_attendance")
            if hasattr(mod, "render_field_attendance_page"):
                mod.render_field_attendance_page(engine=engine, lang=current_lang, view_mode="all")
            elif hasattr(mod, "show"):
                mod.show(engine=engine, lang=current_lang)

        elif "員工個人檔案" in selected_sub or "Hồ sơ" in selected_sub or "Employee Profile" in selected_sub:
            mod = importlib.import_module("modules.management.hr.employee_profile")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif "薪資計算" in selected_sub or "Payroll" in selected_sub or "Tính lương" in selected_sub:
            mod = importlib.import_module("modules.management.hr.payroll_insurance")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif "公告" in selected_sub or "Announcements" in selected_sub:
            mod = importlib.import_module("modules.management.announcements.announcement_hub")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif "宿舍" in selected_sub or "Dorm" in selected_sub:
            mod = importlib.import_module("modules.management.admin_assets.dom_catering")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif "車輛" in selected_sub or "Vehicle" in selected_sub:
            mod = importlib.import_module("modules.management.admin_assets.vehicle_dispatch")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif "採購" in selected_sub or "AP" in selected_sub:
            mod = importlib.import_module("modules.management.legal_finance.general_purchase")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        else:
            st.info(f"💡 目前選定的模組 [{selected_sub}] 正在載入對應的子資料夾檔案中...")
            
    except Exception as e:
        st.error(f"⚠️ 載入管理部子模組發生異常: {str(e)}")

def show(engine=None, lang="繁體中文", **kwargs):
    render_management_module(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_management_module(engine=engine, lang=lang, **kwargs)
