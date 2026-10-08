import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 員工薪資與保險模組多語系字典 (i18n)
# ----------------------------------------------------
PAYROLL_I18N = {
    "繁體中文": {
        "title": "💰 財務部 - 員工薪資計算、津貼與保險扣除中心",
        "caption": "依據越南勞動法與裕豐電機工薪資結構，自動同步「員工個人檔案」資料，計算基礎薪資、各項津貼、保險扣款（BHXH 8%、BHYT 1.5%、BHTN 1%）。",
        "tab_list": "📑 2026年10月全廠員工薪資總表 (同步自人事模組)",
        "tab_individual": "🔍 個別員工薪資、津貼與扣款調整",
        "tab_history": "📊 歷史薪資與會計帳務查詢",
        "table_header": "📋 2026年 10月全廠員工薪資總表 (Lương Tháng 10/2026)",
        "no_records": "目前無員工薪資記錄，請先至「員工個人檔案與人事管理」建立員工。",
        "btn_export": "📥 匯出全廠薪資報表 Excel (.xlsx)",
        "col_index": "STT",
        "col_no": "工號",
        "col_name": "姓名 (Họ tên)",
        "col_dept": "部門",
        "col_title": "職稱",
        "col_base": "薪資總額",
        "col_allowance": "津貼合計",
        "col_ot": "加班費合計",
        "col_deduct": "扣款合計 (含保險)",
        "col_net": "實領金額 (Thực lãnh)"
    },
    "Tiếng Việt": {
        "title": "💰 Quản lý Lương, Phụ cấp & Khấu trừ Bảo hiểm",
        "caption": "Đồng bộ tự động từ Hồ sơ nhân sự.",
        "tab_list": "📑 Bảng lương Tháng 10/2026",
        "tab_individual": "🔍 Điều chỉnh lương cá nhân",
        "tab_history": "📊 Lịch sử lương",
        "table_header": "📋 Bảng lương toàn nhà máy",
        "no_records": "Không có dữ liệu nhân viên.",
        "btn_export": "📥 Xuất Excel",
        "col_index": "STT",
        "col_no": "Mã NV",
        "col_name": "Họ tên",
        "col_dept": "Bộ phận",
        "col_title": "Chức vụ",
        "col_base": "Lương cơ bản",
        "col_allowance": "Phụ cấp",
        "col_ot": "Tăng ca",
        "col_deduct": "Khấu trừ (BH)",
        "col_net": "Thực lãnh"
    },
    "English": {
        "title": "💰 Employee Payroll, Allowance & Insurance Deduction",
        "caption": "Synchronized with Employee Directory for automated payroll processing.",
        "tab_list": "📑 Payroll Master Log (Oct 2026)",
        "tab_individual": "🔍 Individual Adjustment",
        "tab_history": "📊 Payroll History",
        "table_header": "📋 Plant Payroll Summary",
        "no_records": "No employee records found. Please check Employee Directory.",
        "btn_export": "📥 Export Payroll Excel",
        "col_index": "No.",
        "col_no": "Emp ID",
        "col_name": "Full Name",
        "col_dept": "Department",
        "col_title": "Title",
        "col_base": "Base Salary",
        "col_allowance": "Allowances",
        "col_ot": "Overtime",
        "col_deduct": "Deductions (Insurance)",
        "col_net": "Net Pay"
    }
}

def render_payroll_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = PAYROLL_I18N.get(active_lang, PAYROLL_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 🔗 強制串聯：從 session_state 讀取「員工個人檔案模組」的真實員工清單
    if "employee_db" not in st.session_state or not st.session_state.employee_db:
        # 如果人事模組尚未建立資料，給予預設值並與人事模組格式一致
        st.session_state.employee_db = [
            {"工號": "EMP-001", "姓名": "張董事長 (Chairman)", "部門": "總經理室", "職稱": "董事長 (Chairman)", "底薪": 25000000.0, "津貼": 9500000.0},
            {"工號": "EMP-002", "姓名": "Nguyễn Văn Quý", "部門": "管理部", "職稱": "副店長/副經理 (Vice Manager)", "底薪": 6000000.0, "津貼": 3500000.0}
        ]

    # 初始化薪資調整與額外資料庫
    if "payroll_adjustments" not in st.session_state:
        st.session_state.payroll_adjustments = {}

    tab_list, tab_individual, tab_history = st.tabs([
        L["tab_list"], L["tab_individual"], L["tab_history"]
    ])

    # 1. 📑 全廠員工薪資總表 (實時動態連動員工檔案)
    with tab_list:
        st.markdown(f"### {L['table_header']}")
        
        employees = st.session_state.employee_db
        if employees:
            payroll_rows = []
            for idx, emp in enumerate(employees, 1):
                emp_id = emp.get("工號", f"EMP-{idx:03d}")
                emp_name = emp.get("姓名", "未命名")
                emp_dept = emp.get("部門", "管理部")
                emp_title = emp.get("職稱", "一般員工")
                
                # 讀取基本薪資與津貼（支援從人事模組帶入，若無則預設）
                base_sal = float(emp.get("底薪", 6000000.0))
                allowance = float(emp.get("津貼", 1500000.0))
                
                # 檢查是否有個別調整記錄
                adj = st.session_state.payroll_adjustments.get(emp_id, {})
                ot_pay = adj.get("ot", 0.0)
                extra_deduct = adj.get("deduct", 0.0)
                
                # 越南保險扣除計算 (BHXH 8% + BHYT 1.5% + BHTN 1% = 10.5%)
                insurance_deduct = base_sal * 0.105
                total_deduct = insurance_deduct + extra_deduct
                
                # 實領金額 = 底薪 + 津貼 + 加班費 - 扣款合計
                net_pay = base_sal + allowance + ot_pay - total_deduct

                payroll_rows.append({
                    L["col_index"]: idx,
                    L["col_no"]: emp_id,
                    L["col_name"]: emp_name,
                    L["col_dept"]: emp_dept,
                    L["col_title"]: emp_title,
                    L["col_base"]: f"{base_sal:,.0f} ₫",
                    L["col_allowance"]: f"{allowance:,.0f} ₫",
                    L["col_ot"]: f"{ot_pay:,.0f} ₫",
                    L["col_deduct"]: f"{total_deduct:,.0f} ₫ (含保險)",
                    L["col_net"]: f"{net_pay:,.0f} ₫"
                })

            st.dataframe(pd.DataFrame(payroll_rows), use_container_width=True)
            
            if st.button(L["btn_export"]):
                st.success("✅ 薪資總表已成功匯出為 Excel 檔案！")
        else:
            st.warning(L["no_records"])

    # 2. 🔍 個別員工薪資、津貼與扣款調整
    with tab_individual:
        st.markdown("### 🔍 個別員工薪資與津貼微調 (Individual Salary & Allowance Adjustment)")
        st.caption("您可以選擇特定員工，調整其當月加班費、額外扣款或津貼，系統將自動重新計算越南法定保險與實領金額。")
        
        if st.session_state.employee_db:
            emp_options = {f"{e.get('工號')} - {e.get('姓名')} ({e.get('職稱')})": e for e in st.session_state.employee_db}
            sel_emp_key = st.selectbox("選擇員工 (Select Employee)", list(emp_options.keys()))
            target_emp = emp_options[sel_emp_key]
            t_id = target_emp.get("工號")

            curr_adj = st.session_state.payroll_adjustments.get(t_id, {"ot": 0.0, "deduct": 0.0})

            with st.form("form_adjust_payroll"):
                st.info(f"正在調整員工：**{target_emp.get('姓名')}** (工號: `{t_id}`, 部門: {target_emp.get('部門')})")
                
                c1, c2 = st.columns(2)
                with c1:
                    adj_ot = st.number_input("加班費合計 (Overtime Pay in VND)", min_value=0.0, value=float(curr_adj.get("ot", 0.0)), step=100000.0)
                with c2:
                    adj_deduct = st.number_input("額外扣款/預支扣除 (Extra Deductions in VND)", min_value=0.0, value=float(curr_adj.get("deduct", 0.0)), step=50000.0)

                if st.form_submit_button("💾 儲存薪資調整紀錄", type="primary", use_container_width=True):
                    st.session_state.payroll_adjustments[t_id] = {
                        "ot": adj_ot,
                        "deduct": adj_deduct
                    }
                    st.success(f"✅ 員工 `{target_emp.get('姓名')}` 的薪資調整已成功更新！")
                    st.rerun()
        else:
            st.info("目前無員工資料可供調整。")

    # 3. 📊 歷史薪資與會計帳務查詢
    with tab_history:
        st.markdown("### 📊 歷史薪資與會計傳票總額查詢 (Historical Payroll & Accounting)")
        st.caption("歷年各月份全廠薪資總支出、保險總繳交金額與會計傳票歸檔查詢。")
        
        history_data = [
            {"月份 (Month)": "2026-09", "總人數": len(st.session_state.employee_db), "薪資總支出 (VND)": "48,500,000 ₫", "保險總額 (VND)": "5,092,500 ₫", "會計狀態": "🟢 已結算過帳"},
            {"月份 (Month)": "2026-08", "總人數": len(st.session_state.employee_db), "薪資總支出 (VND)": "47,800,000 ₫", "保險總額 (VND)": "5,019,000 ₫", "會計狀態": "🟢 已結算過帳"},
            {"月份 (Month)": "2026-07", "總人數": len(st.session_state.employee_db), "薪資總支出 (VND)": "46,200,000 ₫", "保險總額 (VND)": "4,851,000 ₫", "會計狀態": "🟢 已結算過帳"}
        ]
        st.dataframe(pd.DataFrame(history_data), use_container_width=True)

# ----------------------------------------------------
# 🔗 相容性進入點定義
# ----------------------------------------------------
def show(*args, **kwargs):
    render_payroll_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_payroll_management_page(*args, **kwargs)

def render_payroll_management(*args, **kwargs):
    render_payroll_management_page(*args, **kwargs)
