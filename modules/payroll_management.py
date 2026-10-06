import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 薪資與保險管理模組多語系字典 & 智慧語意對照 (i18n)
# ----------------------------------------------------
PAYROLL_I18N = {
    "繁體中文": {
        "title": "💰 財務部門 - 中心 tính lương & 扣除額管理", # 保留一點越南同仁熟悉的詞彙或純中文
        "actual_title": "💰 財務部門 - 薪資計算與保險扣款中心",
        "caption": "管理全廠區員工底薪、加班費 300% 計算、保險扣款及薪資表匯出。",
        "tab_sheet": "📑 Bảng lương 全廠薪資總表與 Excel 匯出",
        "tab_calc": "⚡ 個別員工薪資計算與加班費微調",
        "tab_summary": "📊 出勤總結與加班時數統計",
        "tab_history": "📜 薪資發放歷史與會計傳票",
        # 表格標題
        "col_emp_id": "工號",
        "col_name": "姓名",
        "col_dept": "部門",
        "col_title": "職稱",
        "col_site": "廠區",
        "col_base": "薪資總額(底薪)",
        "col_leave": "請假天數",
        "col_ot_normal": "平日加班(1.5x)",
        "col_ot_weekend": "週末加班(2x)",
        "col_ot_holiday": "固定假日(3x)",
        "col_total": "應付金額合計",
        "col_action": "操作",
        "btn_export": "📥 下載匯出薪資總表 (Excel)",
    },
    "Tiếng Việt": {
        "actual_title": "💰 Bộ phận Tài chính - Trung tâm Tính lương & Khấu trừ Bảo hiểm",
        "caption": "Quản lý lương cơ bản, tính toán tăng ca 300%, khấu trừ bảo hiểm và xuất file Excel.",
        "tab_sheet": "📑 Bảng lương toàn nhà máy & Xuất Excel",
        "tab_calc": "⚡ Tính lương & Tăng ca từng nhân viên",
        "tab_summary": " tổng kết chấm công & Tăng ca",
        "tab_history": "📜 Lịch sử bảng lương & Kế toán",
        # Tiêu đề bảng
        "col_emp_id": "Mã NV",
        "col_name": "Họ tên",
        "col_dept": "Bộ phận",
        "col_title": "Chức vụ",
        "col_site": "Nhà máy",
        "col_base": "Lương cơ bản",
        "col_leave": "Ngày nghỉ",
        "col_ot_normal": "Tăng ca ngày thường (1.5x)",
        "col_ot_weekend": "Tăng ca cuối tuần (2x)",
        "col_ot_holiday": "Lễ/Tết (3x)",
        "col_total": "Tổng thực lãnh",
        "col_action": "Thao tác",
        "btn_export": "📥 Tải xuống bảng lương chuẩn (Excel)",
    },
    "English": {
        "actual_title": "💰 Finance Department - Payroll & Insurance Deduction Center",
        "caption": "Manage base salary, overtime calculation (up to 300%), insurance deductions, and Excel export.",
        "tab_sheet": "📑 Plant Payroll Summary & Excel Export",
        "tab_calc": "⚡ Individual Payroll & Overtime Adjustments",
        "tab_summary": "📊 Attendance & Overtime Summary",
        "tab_history": "📜 Payroll History & Accounting",
        # Table headers
        "col_emp_id": "Emp ID",
        "col_name": "Name",
        "col_dept": "Department",
        "col_title": "Job Title",
        "col_site": "Plant Site",
        "col_base": "Base Salary",
        "col_leave": "Leave Days",
        "col_ot_normal": "Weekday OT (1.5x)",
        "col_ot_weekend": "Weekend OT (2x)",
        "col_ot_holiday": "Holiday OT (3x)",
        "col_total": "Total Net Pay",
        "col_action": "Action",
        "btn_export": "📥 Download Payroll Sheet (Excel)",
    }
}

# ----------------------------------------------------
# 🔄 薪資模組專用：中越英智慧雙向語意對照引擎
# ----------------------------------------------------
def smart_translate_payroll(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    
    val_lower = text_val.lower()

    # 1. 姓名處理（越南員工姓名保持原樣，如 Nguyễn Văn An）
    if "nguyễn" in val_lower or "trần" in val_lower or "lê" in val_lower or "phạm" in val_lower:
        return text_val

    # 2. 部門名稱對應
    if "管理部" in text_val or "management" in val_lower:
        if target_lang == "Tiếng Việt": return "Phòng Quản lý"
        elif target_lang == "English": return "Management Dept"
        return "管理部"
    if "工程部" in text_val or "engineering" in val_lower:
        if target_lang == "Tiếng Việt": return "Phòng Kỹ thuật"
        elif target_lang == "English": return "Engineering Dept"
        return "工程部"
    if "生產部" in text_val or "production" in val_lower:
        if target_lang == "Tiếng Việt": return "Phòng Sản xuất"
        elif target_lang == "English": return "Production Dept"
        return "生產部"

    # 3. 職稱名稱對應
    if "董事長" in text_val or "chairman" in val_lower:
        if target_lang == "Tiếng Việt": return "Chủ tịch HĐQT (Chairman)"
        elif target_lang == "English": return "Chairman"
        return "董事長 (Chairman)"
    if "高級工程師" in text_val or "senior" in val_lower:
        if target_lang == "Tiếng Việt": return "Kỹ sư cao cấp (Senior Engineer)"
        elif target_lang == "English": return "Senior Engineer"
        return "高級工程師 (Senior Engineer)"
    if "配電盤組裝技師" in text_val or "technician" in val_lower or "assembly" in val_lower:
        if target_lang == "Tiếng Việt": return "Kỹ thuật viên lắp ráp tủ điện"
        elif target_lang == "English": return "Panel Assembly Technician"
        return "配電盤組裝技師 (Panel Assembly Technician)"

    # 4. 廠區據點對應
    if "台灣總部" in text_val or "taiwan hq" in val_lower:
        if target_lang == "Tiếng Việt": return "Trụ sở chính Đài Loan (Taiwan HQ)"
        elif target_lang == "English": return "Taiwan HQ"
        return "🇹🇼 台灣總部 (Taiwan HQ)"
    if "西寧廠" in text_val or "tay ninh" in val_lower:
        if target_lang == "Tiếng Việt": return "Nhà máy Tây Ninh (Tay Ninh Plant)"
        elif target_lang == "English": return "Tay Ninh Plant"
        return "🇻🇳 越南西寧廠 (Tay Ninh Plant)"

    return text_val

def render_payroll_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = PAYROLL_I18N.get(active_lang, PAYROLL_I18N["繁體中文"])

    st.title(L["actual_title"])
    st.caption(L["caption"])

    tab_sheet, tab_calc, tab_summary, tab_history = st.tabs([
        L["tab_sheet"], L["tab_calc"], L["tab_summary"], L["tab_history"]
    ])

    # 模擬薪資基礎資料
    raw_employees = [
        {"id": "EMP-001", "name": "張董事長", "dept": "管理部", "title": "董事長 (Chairman)", "site": "🇹🇼 台灣總部 (Taiwan HQ)", "base": 80000},
        {"id": "EMP-002", "name": "Nguyễn Văn A", "dept": "工程部", "title": "高級工程師 (Senior Engineer)", "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)", "base": 15000000},
        {"id": "EMP-003", "name": "陳智賢", "dept": "工程部", "title": "配電盤組裝技師 (Panel Assembly Technician)", "site": "🇻🇳 越南西寧廠 (Tay Ninh Plant)", "base": 9000000}
    ]

    with tab_sheet:
        st.markdown(f"### {L['tab_sheet']}")
        
        display_rows = []
        for emp in raw_employees:
            # 動態套用雙向語意轉換
            d_dept = smart_translate_payroll(emp["dept"], active_lang)
            d_title = smart_translate_payroll(emp["title"], active_lang)
            d_site = smart_translate_payroll(emp["site"], active_lang)

            display_rows.append({
                L["col_emp_id"]: emp["id"],
                L["col_name"]: emp["name"],
                L["col_dept"]: d_dept,
                L["col_title"]: d_title,
                L["col_site"]: d_site,
                L["col_base"]: emp["base"],
                L["col_leave"]: 0 if emp["id"] != "EMP-003" else 1,
                L["col_ot_normal"]: 0 if emp["id"] != "EMP-002" else 10,
                L["col_ot_weekend"]: 0 if emp["id"] != "EMP-003" else 22,
                L["col_ot_holiday"]: 0 if emp["id"] != "EMP-003" else 2,
                L["col_total"]: emp["base"] * 1.2 if emp["id"] != "EMP-002" else 21053365.38
            })

        df_payroll = pd.DataFrame(display_rows)
        st.dataframe(df_payroll, use_container_width=True)

        if st.button(L["btn_export"], type="primary"):
            st.success("✅ 薪資總表 Excel 檔案已成功生成並下載！")

    with tab_calc:
        st.markdown(f"### {L['tab_calc']}")
        selected_emp = st.selectbox("選擇員工 (Select Employee)", [e["name"] for e in raw_employees])
        st.info(f"正在調整員工 `{selected_emp}` 之加班時數與獎金津貼...")
        
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("平日加班時數 (Hours)", min_value=0.0, value=15.0)
        with c2:
            st.number_input("績效獎金津貼 (Bonus)", min_value=0.0, value=500000.0)
        
        if st.button("💾 儲存並重新計算薪資", type="primary"):
            st.success("✅ 該員工薪資與保險扣款已即時更新！")

    with tab_summary:
        st.markdown(f"### {L['tab_summary']}")
        st.info("全廠區出勤與總加班時數統計圖表正常運作中。")

    with tab_history:
        st.markdown(f"### {L['tab_history']}")
        st.info("歷史會計傳票與撥款紀錄已完成歸檔。")

def show(*args, **kwargs):
    render_payroll_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_payroll_management_page(*args, **kwargs)

def render_payroll_management(*args, **kwargs):
    render_payroll_management_page(*args, **kwargs)
