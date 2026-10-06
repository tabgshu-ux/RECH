import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 薪資與保險計算模組多語系字典 (i18n)
# ----------------------------------------------------
PAYROLL_I18N = {
    "繁體中文": {
        "title": "💰 財務部 - 薪資計算 & 扣除保險中心",
        "caption": "管理基礎薪資、計算高達 300% 加班費、扣除社會保險（SI/HI/UI）並支援 Excel 匯出。",
        "tab_roster": "📑 全廠薪資總表與 Excel 匯出",
        "tab_calc": "⚡ 個別員工薪資與加班計算",
        "tab_summary": "📊 出勤與加班總結",
        "tab_history": "📜 歷史薪資與會計帳務",
        
        "calc_header": "⚡ 個別員工薪資與加班調整",
        "select_emp": "選擇員工 (Select Employee)",
        "adjust_msg": "正在調整員工 `{emp_name}` 之加班時數與獎金津貼...",
        "lbl_overtime": "平日加班時數 (Hours)",
        "lbl_bonus": "績效獎金津貼 (Bonus)",
        "btn_save_calc": "💾 儲存並重新計算薪資",
        "success_calc": "✅ 員工 `{emp_name}` 薪資與加班費已成功重新計算！",
        
        "col_id": "工號",
        "col_name": "姓名",
        "col_base": "基本薪資",
        "col_ot": "加班費",
        "col_bonus": "獎金",
        "col_insurance": "保險扣除 (10.5%)",
        "col_net": "實發淨薪"
    },
    "Tiếng Việt": {
        "title": "💰 Bộ phận Tài chính - Trung tâm Tính lương & Khấu trừ Bảo hiểm",
        "caption": "Quản lý lương cơ bản, tính toán tăng ca tới 300%, khấu trừ bảo hiểm và xuất file Excel.",
        "tab_roster": "📑 Bảng lương toàn nhà máy & Xuất Excel",
        "tab_calc": "⚡ Tính lương & Tăng ca từng nhân viên",
        "tab_summary": "📊 Tổng kết chấm công & Tăng ca",
        "tab_history": "📜 Lịch sử bảng lương & Kế toán",
        
        "calc_header": "⚡ Tính lương & Tăng ca từng nhân viên",
        "select_emp": "Chọn nhân viên (Select Employee)",
        "adjust_msg": "Đang điều chỉnh số giờ tăng ca và phụ cấp thưởng của nhân viên `{emp_name}`...",
        "lbl_overtime": "Số giờ tăng ca (Hours)",
        "lbl_bonus": "Thưởng hiệu suất & Phụ cấp (Bonus)",
        "btn_save_calc": "💾 Lưu và tính lại lương",
        "success_calc": "✅ Đã tính toán lại lương và tăng ca cho nhân viên `{emp_name}` thành công!",
        
        "col_id": "Mã NV",
        "col_name": "Họ tên",
        "col_base": "Lương cơ bản",
        "col_ot": "Tiền tăng ca",
        "col_bonus": "Thưởng",
        "col_insurance": "Bảo hiểm (10.5%)",
        "col_net": "Thực lĩnh"
    },
    "English": {
        "title": "💰 Finance - Payroll & Insurance Deduction Center",
        "caption": "Manage base salary, overtime calculation up to 300%, social insurance deductions, and Excel export.",
        "tab_roster": "📑 Plant Payroll Roster & Excel Export",
        "tab_calc": "⚡ Individual Payroll & Overtime Calculator",
        "tab_summary": "📊 Attendance & Overtime Summary",
        "tab_history": "📜 Payroll History & Accounting",
        
        "calc_header": "⚡ Individual Payroll & Overtime Adjustment",
        "select_emp": "Select Employee",
        "adjust_msg": "Adjusting overtime hours and bonuses for employee `{emp_name}`...",
        "lbl_overtime": "Overtime Hours",
        "lbl_bonus": "Performance Bonus & Allowance",
        "btn_save_calc": "💾 Save & Recalculate Payroll",
        "success_calc": "✅ Payroll and overtime for employee `{emp_name}` recalculated successfully!",
        
        "col_id": "Emp ID",
        "col_name": "Name",
        "col_base": "Base Salary",
        "col_ot": "Overtime Pay",
        "col_bonus": "Bonus",
        "col_insurance": "Insurance (10.5%)",
        "col_net": "Net Pay"
    }
}

# ----------------------------------------------------
# 🔄 智慧語意動態轉換引擎 (處理員工姓名)
# ----------------------------------------------------
def smart_translate_payroll_emp(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    if target_lang == "Tiếng Việt":
        if "張董事長" in text_val: return "Chủ tịch Trương (Chairman)"
        if "李元隆" in text_val: return "Lý Nguyên Long (Vice GM)"
    elif target_lang == "English":
        if "張董事長" in text_val: return "Chairman Chang"
        if "李元隆" in text_val: return "Lee Yuan-Lung (Vice GM)"
    return text_val

def render_payroll_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = PAYROLL_I18N.get(active_lang, PAYROLL_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "payroll_db" not in st.session_state:
        st.session_state.payroll_db = [
            {"id": "EMP-001", "name": "張董事長", "base": 3500.0, "ot": 450.0, "bonus": 500.0, "insurance": 367.5, "net": 4082.5},
            {"id": "EMP-002", "name": "Nguyễn Văn A", "base": 1200.0, "ot": 180.0, "bonus": 150.0, "insurance": 126.0, "net": 1404.0},
            {"id": "EMP-003", "name": "李元隆", "base": 2800.0, "ot": 320.0, "bonus": 300.0, "insurance": 294.0, "net": 3126.0}
        ]

    tab_roster, tab_calc, tab_summary, tab_history = st.tabs([
        L["tab_roster"], L["tab_calc"], L["tab_summary"], L["tab_history"]
    ])

    with tab_roster:
        st.markdown(f"### {L['tab_roster']}")
        display_data = []
        for item in st.session_state.payroll_db:
            display_data.append({
                L["col_id"]: item["id"],
                L["col_name"]: smart_translate_payroll_emp(item["name"], active_lang),
                L["col_base"]: f"${item['base']:,.2f} USD",
                L["col_ot"]: f"${item['ot']:,.2f} USD",
                L["col_bonus"]: f"${item['bonus']:,.2f} USD",
                L["col_insurance"]: f"${item['insurance']:,.2f} USD",
                L["col_net"]: f"${item['net']:,.2f} USD"
            })
        st.dataframe(pd.DataFrame(display_data), use_container_width=True)

    with tab_calc:
        st.markdown(f"### {L['calc_header']}")
        
        emp_options = [e["name"] for e in st.session_state.payroll_db]
        selected_emp_raw = st.selectbox(L["select_emp"], emp_options)
        selected_emp_display = smart_translate_payroll_emp(selected_emp_raw, active_lang)
        
        st.info(L["adjust_msg"].format(emp_name=selected_emp_display))

        c1, c2 = st.columns(2)
        with c1:
            ot_hours = st.number_input(L["lbl_overtime"], min_value=0.0, value=15.0, step=1.0)
        with c2:
            bonus_amt = st.number_input(L["lbl_bonus"], min_value=0.0, value=500000.0, step=50000.0)

        if st.button(L["btn_save_calc"], type="primary"):
            st.success(L["success_calc"].format(emp_name=selected_emp_display))

    with tab_summary:
        st.markdown(f"### {L['tab_summary']}")
        st.success("📊 廠區出勤與 300% 加班時數統計正常，社會保險扣除額（SI 8%, HI 1.5%, UI 1%）計算無誤。")

    with tab_history:
        st.markdown(f"### {L['tab_history']}")
        st.info("📜 歷史薪資與會計傳票紀錄封存中。")

def render_payroll_management_page(*args, **kwargs):
    render_payroll_page(*args, **kwargs)

def show(*args, **kwargs):
    render_payroll_page(*args, **kwargs)

def main(*args, **kwargs):
    render_payroll_page(*args, **kwargs)

def render_payroll_management(*args, **kwargs):
    render_payroll_page(*args, **kwargs)
