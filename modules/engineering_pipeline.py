import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 全球廠區水電工程驗收與進度追蹤模組多語系字典 (i18n)
# ----------------------------------------------------
PROJECT_TRACKING_I18N = {
    "繁體中文": {
        "title": "⚡ 裕豐電機工業 - 水電工程驗收與進度追蹤",
        "caption": "純工程導向：專注監控工程現場施工進度百分比、驗收狀態與合約管控。",
        "kpi1_title": "在手水電專案總數",
        "kpi1_val": "8 件",
        "kpi1_sub": "↑ 執行中 6 件 / 驗收 2 件",
        "kpi2_title": "合約總金額 (USD)",
        "kpi2_sub": "↑ 累計已收: $1,250,000",
        "kpi3_title": "總未收款/應收尾款 (AR)",
        "kpi3_sub": "↑ 需加強催收",
        "kpi4_title": "平均工程進度",
        "kpi4_sub": "● 進度正常",
        
        "table_header": "📋 專案明細、工程進度與驗收狀態管控表",
        "col_code": "專案代碼",
        "col_client": "客戶名稱 / 廠區",
        "col_item": "水電工程項目",
        "col_total": "合約總值 (USD)",
        "col_paid": "已收款金額 (USD)",
        "col_ar": "未收款/尾款 (USD)",
        "col_progress": "工程進度 (%)",
        "col_status": "工程與驗收狀態"
    },
    "Tiếng Việt": {
        "title": "⚡ REETECH INDUSTRIAL - Theo dõi Tiến độ & Nghiệm thu Dự án Cơ điện",
        "caption": "Chuyên dụng kỹ thuật: Tập trung giám sát phần trăm tiến độ thi công, trạng thái nghiệm thu và hợp đồng.",
        "kpi1_title": "Tổng số dự án cơ điện",
        "kpi1_val": "8 dự án",
        "kpi1_sub": "↑ Đang thực hiện 6 / Nghiệm thu 2",
        "kpi2_title": "Tổng giá trị hợp đồng (USD)",
        "kpi2_sub": "↑ Đã thu lũy kế: $1,250,000",
        "kpi3_title": "Tổng công nợ phải thu (AR)",
        "kpi3_sub": "↑ Cần đẩy mạnh thu hồi",
        "kpi4_title": "Tiến độ thi công trung bình",
        "kpi4_sub": "● Tiến độ bình thường",
        
        "table_header": "📋 Bảng chi tiết dự án, tiến độ thi công và trạng thái nghiệm thu",
        "col_code": "Mã dự án",
        "col_client": "Tên khách hàng / Nhà máy",
        "col_item": "Hạng mục cơ điện",
        "col_total": "Giá trị HĐ (USD)",
        "col_paid": "Đã thu (USD)",
        "col_ar": "Còn lại/Phải thu (USD)",
        "col_progress": "Tiến độ (%)",
        "col_status": "Trạng thái thi công & Nghiệm thu"
    },
    "English": {
        "title": "⚡ REETECH INDUSTRIAL - M&E Engineering Progress & Acceptance Tracking",
        "caption": "Engineering focused: Dedicated monitoring of site construction progress, acceptance status, and contract control.",
        "kpi1_title": "Total M&E Projects",
        "kpi1_val": "8 projects",
        "kpi1_sub": "↑ Active: 6 / Acceptance: 2",
        "kpi2_title": "Total Contract Value (USD)",
        "kpi2_sub": "↑ Cumulative Collected: $1,250,000",
        "kpi3_title": "Total Accounts Receivable (AR)",
        "kpi3_sub": "↑ Follow-up Required",
        "kpi4_title": "Average Engineering Progress",
        "kpi4_sub": "● Progress Normal",
        
        "table_header": "📋 Project Details, Progress & Acceptance Status Table",
        "col_code": "Project Code",
        "col_client": "Client / Plant",
        "col_item": "M&E Item",
        "col_total": "Contract Value (USD)",
        "col_paid": "Collected (USD)",
        "col_ar": "Receivable (USD)",
        "col_progress": "Progress (%)",
        "col_status": "Status & Acceptance"
    }
}

def get_active_lang(passed_lang):
    if passed_lang in PROJECT_TRACKING_I18N:
        return passed_lang
    for key in ["current_lang", "lang", "language", "selected_lang"]:
        val = st.session_state.get(key)
        if val in PROJECT_TRACKING_I18N:
            return val
    return "Tiếng Việt"  # 預設越南文

def smart_translate_project_data(text, target_lang):
    if not text or not isinstance(text, str):
        return text
    
    if target_lang == "Tiếng Việt":
        text = text.replace("越南新順楠梓電子廠", "Nhà máy Điện tử Tân Thuận, TP.HCM")
        text = text.replace("平陽美德金屬加工廠", "Nhà máy Cơ khí Meide Bình Dương")
        text = text.replace("隆安宏遠精密機械廠", "Nhà máy Cơ khí chính xác Hồng Viễn, Long An")
        text = text.replace("北寧富泰光電科技", "Công ty Công nghệ Quang điện FuTai, Bắc Ninh")
        text = text.replace("無塵室高低壓配電安裝與強弱電配管", "Lắp đặt tủ điện trung/hạ thế phòng sạch & ống đi dây điện nhẹ")
        text = text.replace("廠房動力配電、給排水系統與照明工程", "Hệ thống điện động lực nhà máy, cấp thoát nước & chiếu sáng")
        text = text.replace("變電站統包工程、銅排配置與空調系統配電", "Dự án trạm biến áp EPC, lắp đặt thanh cái & điện hệ thống điều hòa")
        text = text.replace("廠房大樓消防警報系統與機房不間斷電源(UPS)配電", "Hệ thống báo cháy tòa nhà & nguồn điện dự phòng UPS phòng máy")
        text = text.replace("🟢 設備安裝完成，待驗收", "🟢 Hoàn thành lắp đặt thiết bị, chờ nghiệm thu")
        text = text.replace("🟡 正在進行主幹管配線", "🟡 Đang thi công hệ thống cáp chính")
        text = text.replace("🟢 變電站主體完工", "🟢 Hoàn thành trạm biến áp chính")
        text = text.replace("🟡 機架架設與線槽施工", "🟡 Lắp đặt tủ rack và máng cáp")
    elif target_lang == "English":
        text = text.replace("越南新順楠梓電子廠", "Tan Thuan Electronics Plant, HCMC")
        text = text.replace("平陽美德金屬加工廠", "Meide Metal Processing Plant, Binh Duong")
        text = text.replace("隆安宏遠精密機械廠", "HongYuan Precision Machinery, Long An")
        text = text.replace("北寧富泰光電科技", "FuTai Optoelectronics, Bac Ninh")
        text = text.replace("無塵室高低壓配電安裝與強弱電配管", "Cleanroom switchboard installation & wiring")
        text = text.replace("廠房動力配電、給排水系統與照明工程", "Plant power distribution, plumbing & lighting")
        text = text.replace("變電站統包工程、銅排配置與空調系統配電", "Substation EPC, busbars & HVAC power")
        text = text.replace("廠房大樓消防警報系統與機房不間斷電源(UPS)配電", "Building fire alarm & server room UPS power")
        text = text.replace("🟢 設備安裝完成，待驗收", "🟢 Equipment Installed, Pending Acceptance")
        text = text.replace("🟡 正在進行主幹管配線", "🟡 Main Trunk Cabling in Progress")
        text = text.replace("🟢 變電站主體完工", "🟢 Substation Main Structure Completed")
        text = text.replace("🟡 機架架設與線槽施工", "🟡 Rack Installation & Cable Tray Works")
        
    return text

def render_engineering_page(engine=None, lang=None, **kwargs):
    active_lang = get_active_lang(lang)
    L = PROJECT_TRACKING_I18N.get(active_lang, PROJECT_TRACKING_I18N["Tiếng Việt"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 純工程專案 KPI 統計區塊
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label=L["kpi1_title"], value=L["kpi1_val"], delta=L["kpi1_sub"])
    with c2:
        st.metric(label=L["kpi2_title"], value="$1,850,000", delta=L["kpi2_sub"])
    with c3:
        st.metric(label=L["kpi3_title"], value="$600,000", delta=L["kpi3_sub"])
    with c4:
        st.metric(label=L["kpi4_title"], value="76.5%", delta=L["kpi4_sub"])

    st.markdown("---")
    st.markdown(f"### {L['table_header']}")

    raw_data = [
        {
            "code": "PRJ-2026-01",
            "client": "越南新順楠梓電子廠 (XinShun Electronics)",
            "item": "無塵室高低壓配電安裝與強弱電配管",
            "total": 450000,
            "paid": 315000,
            "ar": 135000,
            "progress": 90,
            "status": "🟢 設備安裝完成，待驗收"
        },
        {
            "code": "PRJ-2026-02",
            "client": "平陽美德金屬加工廠 (Meide Metal)",
            "item": "廠房動力配電、給排水系統與照明工程",
            "total": 380000,
            "paid": 228000,
            "ar": 152000,
            "progress": 75,
            "status": "🟡 正在進行主幹管配線"
        },
        {
            "code": "PRJ-2026-03",
            "client": "隆安宏遠精密機械廠 (HongYuan Precision)",
            "item": "變電站統包工程、銅排配置與空調系統配電",
            "total": 620000,
            "paid": 434000,
            "ar": 186000,
            "progress": 85,
            "status": "🟢 變電站主體完工"
        },
        {
            "code": "PRJ-2026-04",
            "client": "北寧富泰光電科技 (FuTai Optoelectronics)",
            "item": "廠房大樓消防警報系統與機房不間斷電源(UPS)配電",
            "total": 400000,
            "paid": 273000,
            "ar": 127000,
            "progress": 55,
            "status": "🟡 機架架設與線槽施工"
        }
    ]

    display_data = []
    for item in raw_data:
        display_data.append({
            L["col_code"]: item["code"],
            L["col_client"]: smart_translate_project_data(item["client"], active_lang),
            L["col_item"]: smart_translate_project_data(item["item"], active_lang),
            L["col_total"]: f"${item['total']:,.0f}",
            L["col_paid"]: f"${item['paid']:,.0f}",
            L["col_ar"]: f"${item['ar']:,.0f}",
            L["col_progress"]: f"{item['progress']}%",
            L["col_status"]: smart_translate_project_data(item["status"], active_lang)
        })

    st.dataframe(pd.DataFrame(display_data), use_container_width=True)

# 完整補齊所有路由分身函式
def render_project_tracking(*args, **kwargs):
    render_engineering_page(*args, **kwargs)

def render_project_tracking_page(*args, **kwargs):
    render_engineering_page(*args, **kwargs)

def show(*args, **kwargs):
    render_engineering_page(*args, **kwargs)

def main(*args, **kwargs):
    render_engineering_page(*args, **kwargs)
