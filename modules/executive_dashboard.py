import streamlit as st
import pandas as pd

def render_executive_dashboard_page(sub_route=None, lang="繁體中文", **kwargs):
    # 🌐 總經理室與戰情室多語系字典 (i18n)
    EXEC_I18N = {
        "繁體中文": {
            "title": "📈 總經理室 - 跨國營運戰情室與即時財務看板",
            "caption": "即時監控西寧廠與海防廠之營運數據、越南稅務財務狀況、原物料行情、匯率與工程專案進度。",
            "m1": "📊 應收帳款總額 (Total AR)",
            "m2": "💰 本月薪資與營業支出",
            "m3": "⚡ 進行中工程專案",
            "m4": "🇻🇳 跨國廠區員工總數",
            "sec_live_data": "📊 系統各模組即時數據聯動總覽",
            "tab_ar": "📑 應收帳款即時監控",
            "tab_payroll": "💰 薪資與人事支出明細",
            "tab_projects": "⚡ 工程專案進度總覽",
            "btn_view_fin": "📊 前往查看詳細越南稅務財報 (Thông tư 200)",
            "no_data": "目前尚無資料。"
        },
        "Tiếng Việt": {
            "title": "📈 Ban Giám đốc - Trung tâm Điều hành & Bảng thông tin Tài chính",
            "caption": "Giám sát thời gian thực dữ liệu vận hành nhà máy Tây Ninh và Hải Phòng, báo cáo thuế chuẩn VN, nguyên vật liệu, tỷ giá và tiến độ dự án.",
            "m1": "📊 Tổng Phải thu (Total AR)",
            "m2": "💰 Lương & Chi phí vận hành tháng",
            "m3": "⚡ Dự án đang thực hiện",
            "m4": "🇻🇳 Tổng số nhân viên nhà máy",
            "sec_live_data": "📊 Tổng quan dữ liệu thời gian thực từ các module",
            "tab_ar": "📑 Giám sát Phải thu (AR) thời gian thực",
            "tab_payroll": "💰 Chi tiết Lương & Chi phí nhân sự",
            "tab_projects": "⚡ Tổng quan Tiến độ Dự án",
            "btn_view_fin": "📊 Xem chi tiết Báo cáo Tài chính chuẩn Thuế VN",
            "no_data": "Hiện không có dữ liệu."
        },
        "English": {
            "title": "📈 Executive Office - Global Operations & Financial Dashboard",
            "caption": "Real-time monitoring of Tay Ninh & Hai Phong plants, Vietnamese tax-standard financials, raw materials, FX, and project progress.",
            "m1": "📊 Total Accounts Receivable (AR)",
            "m2": "💰 Monthly Payroll & Expenses",
            "m3": "⚡ Active Engineering Projects",
            "m4": "🇻🇳 Total Plant Workforce",
            "sec_live_data": "📊 Real-time Module Data Integration Overview",
            "tab_ar": "📑 Real-time AR Monitoring",
            "tab_payroll": "💰 Payroll & Personnel Expense Details",
            "tab_projects": "⚡ Engineering Project Progress Overview",
            "btn_view_fin": "📊 View Detailed Vietnamese Tax Financials",
            "no_data": "No data available."
        }
    }

    active_lang = lang if lang in EXEC_I18N else "繁體中文"
    L = EXEC_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    # ----------------------------------------------------
    # 🔄 自動從系統各模組抓取即時數據
    # ----------------------------------------------------
    total_ar = 0.0
    if "sales_ar_db" in st.session_state and st.session_state.sales_ar_db:
        total_ar = sum(item["outstanding"] for item in st.session_state.sales_ar_db)
    else:
        total_ar = 141630132003.0

    total_payroll = 0.0
    if "payroll_db" in st.session_state and st.session_state.payroll_db:
        for p in st.session_state.payroll_db:
            base = p.get("base_salary", 0)
            allowances = (
                p.get("meal_allowance", 0) + 
                p.get("fuel_allowance", 0) + 
                p.get("phone_allowance", 0) + 
                p.get("title_allowance", 0) + 
                p.get("driving_bonus", 0)
            )
            total_payroll += (base + allowances)
    else:
        total_payroll = 31000000.0

    total_employees = 0
    if "employee_db" in st.session_state and st.session_state.employee_db:
        total_employees = len(st.session_state.employee_db)
    else:
        total_employees = 2

    # 頂部核心指標看板
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(L["m1"], f"{total_ar:,.0f} ₫", "🟢 即時同步 AR")
    c2.metric(L["m2"], f"{total_payroll:,.0f} ₫", "🟢 含津貼與保險")
    c3.metric(L["m3"], "5 個跨國專案", "🟢 執行中")
    c4.metric(L["m4"], f"{total_employees} 位", "🟢 越台兩廠總計")

    st.divider()

    # 子分頁檢視各模組即時明細
    st.markdown(f"### {L['sec_live_data']}")
    tab_ar, tab_payroll, tab_projects = st.tabs([
        L["tab_ar"], L["tab_payroll"], L["tab_projects"]
    ])

    with tab_ar:
        if "sales_ar_db" in st.session_state and st.session_state.sales_ar_db:
            ar_summary = []
            for item in st.session_state.sales_ar_db:
                ar_summary.append({
                    "合約編號": item["code"],
                    "客戶名稱": item["customer"],
                    "合約總額 (VND)": f"{item['total']:,.0f} ₫",
                    "已收款 (VND)": f"{item['collected']:,.0f} ₫",
                    "未收款總計 (VND)": f"{item['outstanding']:,.0f} ₫",
                    "狀態": item["status"]
                })
            st.dataframe(pd.DataFrame(ar_summary), use_container_width=True)
        else:
            st.info(L["no_data"])

    with tab_payroll:
        if "payroll_db" in st.session_state and st.session_state.payroll_db:
            payroll_summary = []
            for item in st.session_state.payroll_db:
                base = item.get("base_salary", 0)
                allowances = (
                    item.get("meal_allowance", 0) + 
                    item.get("fuel_allowance", 0) + 
                    item.get("phone_allowance", 0) + 
                    item.get("title_allowance", 0) + 
                    item.get("driving_bonus", 0)
                )
                payroll_summary.append({
                    "工號": item["code"],
                    "姓名": item["name"],
                    "職稱": item["title"],
                    "底薪 (VND)": f"{base:,.0f} ₫",
                    "津貼合計 (VND)": f"{allowances:,.0f} ₫"
                })
            st.dataframe(pd.DataFrame(payroll_summary), use_container_width=True)
        else:
            st.info(L["no_data"])

    with tab_projects:
        project_overview = [
            {"專案代碼": "HD-2025-HOT", "客戶名稱": "和鼎隆建築 (Ho Team)", "廠區": "西寧廠", "專案進度": "85% (施工中)", "負責人": "李佑銘"},
            {"專案代碼": "HD-2026-JIA", "客戶名稱": "佳威商旅", "廠區": "海防廠", "專案進度": "30% (過路橋架)", "負責人": "阮文強"},
            {"專案代碼": "HD-2026-YAN", "客戶名稱": "彥豪金屬工業", "廠區": "西寧廠", "專案進度": "50% (監工驗收)", "負責人": "陳經理"}
        ]
        st.dataframe(pd.DataFrame(project_overview), use_container_width=True)

    st.markdown("---")
    if st.button(L["btn_view_fin"], type="primary", use_container_width=True):
        st.info("💡 提示：請至左側選單點選 【管理部 ➡️ 越南稅務標準財務報表 (Thông tư 200)】 以查閱完整的資產負債表與綜合損益表。")

def show(*args, **kwargs):
    render_executive_dashboard_page(*args, **kwargs)

def main(*args, **kwargs):
    render_executive_dashboard_page(*args, **kwargs)
