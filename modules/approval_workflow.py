import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 全公司電子簽核與審核中心多語系字典 (i18n)
# ----------------------------------------------------
APPROVAL_I18N = {
    "繁體中文": {
        "title": "🔐 裕豐電機工業 - 全公司電子簽核與保全門禁放行中心",
        "caption": "統一管理請假、採購、派車單、物品攜出單與各類審核，並與保全門禁系統連動進行放行管制。",
        "tab_apply": "✍️ 提交各類申請單 (Leave, PO, Dispatch, GatePass)",
        "tab_my_requests": "📊 我的申請進度追蹤",
        "tab_manager_review": "🔔 主管待辦審核與紅點提醒",
        "tab_security_gate": "🛡️ 保全門禁放行驗證與查核 (Security Gate)",
        "form_select": "選擇要提交的表單類型 (Select Request Type)",
        "type_leave": "🌴 請假申請單 (Leave Request)",
        "type_po": "🛒 採購與請款申請單 (Purchase Order)",
        "type_vehicle": "🚗 廠區車輛調派與派車申請單 (Vehicle Dispatch)",
        "type_gate": "📦 物品攜出與設備放行單 (Material Gate Pass)",
        "btn_submit": "🚀 送出電子簽核申請",
        "success_submit": "✅ 您的申請單已成功送出！系統已自動發送紅點通知給部門主管。",
        "col_index": "STT",
        "col_no": "單號",
        "col_type": "表單類型",
        "col_applicant": "申請人",
        "col_content": "申請內容摘要",
        "col_date": "提交日期",
        "col_status": "簽核狀態"
    },
    "Tiếng Việt": {
        "title": "🔐 Trung tâm Phê duyệt Điện tử & Kiểm soát Cổng An ninh",
        "caption": "Quản lý đơn nghỉ phép, mua hàng, điều xe, mang tài sản ra cổng và phân quyền phê duyệt.",
        "tab_apply": "✍️ Tạo đơn mới",
        "tab_my_requests": "📊 Theo dõi đơn của tôi",
        "tab_manager_review": "🔔 Phê duyệt của Quản lý",
        "tab_security_gate": "🛡️ Kiểm tra cổng bảo vệ (Security Gate)",
        "form_select": "Chọn loại đơn",
        "type_leave": "🌴 Đơn nghỉ phép",
        "type_po": "🛒 Đơn mua hàng",
        "type_vehicle": "🚗 Đơn điều xe",
        "type_gate": "📦 Đơn mang tài sản ra ngoài",
        "btn_submit": "🚀 Gửi đơn",
        "success_submit": "✅ Gửi đơn thành công!",
        "col_index": "STT",
        "col_no": "Mã đơn",
        "col_type": "Loại đơn",
        "col_applicant": "Người gửi",
        "col_content": "Nội dung",
        "col_date": "Ngày gửi",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "🔐 E-Approval & Security Gate Pass Center",
        "caption": "Unified workflow management for leave, POs, vehicle dispatch, gate passes, and security verification.",
        "tab_apply": "✍️ Submit Request",
        "tab_my_requests": "📊 My Requests Status",
        "tab_manager_review": "🔔 Manager Pending Reviews",
        "tab_security_gate": "🛡️ Security Gate Pass Verification",
        "form_select": "Select Request Type",
        "type_leave": "🌴 Leave Request",
        "type_po": "🛒 Purchase Order",
        "type_vehicle": "🚗 Vehicle Dispatch Request",
        "type_gate": "📦 Material & Asset Gate Pass",
        "btn_submit": "🚀 Submit Request",
        "success_submit": "✅ Request submitted successfully! Manager notification sent.",
        "col_index": "No.",
        "col_no": "Req No.",
        "col_type": "Type",
        "col_applicant": "Applicant",
        "col_content": "Summary",
        "col_date": "Date",
        "col_status": "Status"
    }
}

def render_approval_center_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = APPROVAL_I18N.get(active_lang, APPROVAL_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化全公司電子簽核資料庫
    if "approval_db" not in st.session_state:
        st.session_state.approval_db = [
            {
                "單號": "REQ-2026-001",
                "表單類型": "🌴 請假申請單 (Leave Request)",
                "申請人": "Nguyễn Văn Quý",
                "部門": "管理部",
                "申請內容摘要": "事假 3 天 (因家裡喜事請假)",
                "提交日期": "2026-10-06",
                "簽核狀態": "⏳ 待主管審核 (Pending Manager)"
            },
            {
                "單號": "REQ-2026-002",
                "表單類型": "🚗 廠區車輛調派與派車申請單 (Vehicle Dispatch)",
                "申請人": "張董事長 (Chairman)",
                "部門": "總經理室",
                "申請內容摘要": "西寧廠至海防廠商務出差 (用車：Toyota Fortuner 61A-888.66)",
                "提交日期": "2026-10-07",
                "簽核狀態": "🟢 主管已核准，待保全放行 (Approved)"
            },
            {
                "單號": "REQ-2026-003",
                "表單類型": "📦 物品攜出與設備放行單 (Material Gate Pass)",
                "申請人": "工程部工程師",
                "部門": "工程設計管理中心",
                "申請內容摘要": "攜出筆電與測量儀器至工地維修 (數量: 2件)",
                "提交日期": "2026-10-08",
                "簽核狀態": "🟢 主管已核准，待保全放行 (Approved)"
            }
        ]

    # 計算待主管審核的數量（用於紅點提示）
    pending_count = len([r for r in st.session_state.approval_db if "待主管" in r["簽核狀態"]])
    manager_tab_label = f"🔔 主管待辦審核 ({pending_count} 🔴)" if pending_count > 0 else "🔔 主管待辦審核"

    tab_apply, tab_my_requests, tab_manager_review, tab_security_gate = st.tabs([
        L["tab_apply"], L["tab_my_requests"], manager_tab_label, L["tab_security_gate"]
    ])

    # 1. ✍️ 提交各類申請單
    with tab_apply:
        st.markdown("### ✍️ 填寫並提交電子簽核表單")
        
        req_type = st.selectbox(L["form_select"], [
            L["type_leave"],
            L["type_po"],
            L["type_vehicle"],
            L["type_gate"]
        ])

        with st.form("form_submit_request"):
            c1, c2 = st.columns(2)
            with c1:
                applicant_name = st.text_input("申請人姓名 (Applicant Name) *", value="admin (ADMIN)")
                applicant_dept = st.selectbox("申請部門 (Department)", ["總經理室 (Executive Office)", "管理部 (Management Dept)", "工程與設計管理中心", "生產部 (Production Dept)", "資訊管理部"])
            with c2:
                auto_req_no = f"REQ-{datetime.date.today().year}-{len(st.session_state.approval_db)+1:03d}"
                req_no_display = st.text_input("申請單編號 (Request No.)", value=auto_req_no, disabled=True)

            summary_content = ""
            if req_type == L["type_leave"]:
                l_days = st.number_input("請假天數 (Days)", min_value=0.5, value=1.0, step=0.5)
                l_reason = st.text_area("請假事由說明 (Reason)", placeholder="例如: 個人休假或事假")
                summary_content = f"請假 {l_days} 天 - {l_reason}"

            elif req_type == L["type_po"]:
                po_amt = st.number_input("採購預估金額 (Amount in USD)", min_value=0.0, value=1500.0, step=100.0)
                po_desc = st.text_area("採購項目說明 (PO Description)", placeholder="例如: 採購西寧廠車間五金耗材一批")
                summary_content = f"採購金額: ${po_amt:,.2f} USD - {po_desc}"

            elif req_type == L["type_vehicle"]:
                v_dest = st.text_input("目的地與行程 (Destination)", placeholder="例如: 越南西寧廠 ⇄ 海防廠")
                v_car = st.text_input("指定車號/車型 (Vehicle)", placeholder="例如: Toyota Fortuner (61A-888.66)")
                summary_content = f"派車申請: {v_dest} (車號: {v_car})"

            elif req_type == L["type_gate"]:
                g_item = st.text_input("攜出物品名稱與編號 (Items & Asset Code)", placeholder="例如: 筆電 Dell (AST-PC-001) 與測試儀器")
                g_reason = st.text_area("攜出原因與預計回廠日 (Reason & Return Date)", placeholder="例如: 攜至外部授權維修中心，預計 3 天後帶回")
                summary_content = f"物品攜出放行申請: {g_item} ({g_reason})"

            submitted = st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True)
            if submitted:
                if summary_content:
                    st.session_state.approval_db.append({
                        "單號": auto_req_no,
                        "表單類型": req_type,
                        "申請人": applicant_name,
                        "部門": applicant_dept,
                        "申請內容摘要": summary_content,
                        "提交日期": str(datetime.date.today()),
                        "簽核狀態": "⏳ 待主管審核 (Pending Manager)"
                    })
                    st.success(L["success_submit"])
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫表單內容！")

    # 2. 📊 我的申請進度追蹤
    with tab_my_requests:
        st.markdown("### 📊 我的送出申請與即時進度追蹤")
        if st.session_state.approval_db:
            my_display = []
            for idx, r in enumerate(st.session_state.approval_db, 1):
                my_display.append({
                    L["col_index"]: idx,
                    L["col_no"]: r.get("單號"),
                    L["col_type"]: r.get("表單類型"),
                    L["col_applicant"]: r.get("申請人"),
                    L["col_content"]: r.get("申請內容摘要"),
                    L["col_date"]: r.get("提交日期"),
                    L["col_status"]: r.get("簽核狀態")
                })
            st.dataframe(pd.DataFrame(my_display), use_container_width=True)
        else:
            st.info("目前尚無申請紀錄。")

    # 3. 🔔 主管待辦審核與紅點提醒
    with tab_manager_review:
        st.markdown(f"### 🔔 主管待辦審核中心 (Pending Approvals for Managers)")
        st.caption("主管登入後可在此檢視所有同仁提交的請假、採購、派車與物品攜出申請，支援一鍵核准或駁回。")

        pending_requests = [r for r in st.session_state.approval_db if "待主管" in r["簽核狀態"]]
        if pending_requests:
            for idx, req in enumerate(pending_requests):
                with st.expander(f"🔴 [{req.get('單號')}] {req.get('表單類型')} - 申請人: {req.get('申請人')} ({req.get('提交日期')})", expanded=True):
                    st.write(f"**申請部門**：{req.get('部門')}")
                    st.write(f"**詳細內容**：{req.get('申請內容摘要')}")
                    
                    c_btn1, c_btn2, _ = st.columns([1, 1, 3])
                    with c_btn1:
                        if st.button("✅ 核准 (Approve)", key=f"app_{req.get('單號')}", type="primary"):
                            req["簽核狀態"] = "🟢 主管已核准，待保全放行 (Approved)"
                            st.success(f"✅ 單號 `{req.get('單號')}` 已核准！若為派車或攜出單已同步至保全門禁。")
                            st.rerun()
                    with c_btn2:
                        if st.button("❌ 駁回 (Reject)", key=f"rej_{req.get('單號')}"):
                            req["簽核狀態"] = "🔴 主管已駁回 (Rejected)"
                            st.warning(f"❌ 單號 `{req.get('單號')}` 已被駁回。")
                            st.rerun()
        else:
            st.info("🎉 目前沒有需要您審核的待辦事項！")

    # 4. 🛡️ 保全門禁放行驗證與查核 (Security Gate Pass Check)
    with tab_security_gate:
        st.markdown("### 🛡️ 保全門禁放行驗證中心 (Security Gate Verification)")
        st.caption("保全人員於廠區門口執勤時，可在此輸入或掃描「派車單」或「物品攜出單」編號，核對無誤後執行放行。")

        # 篩選出已經主管核准的派車單與物品攜出單
        gate_passes = [r for r in st.session_state.approval_db if ("派車" in r["表單類型"] or "物品攜出" in r["表單類型"]) and "已核准" in r["簽核狀態"]]

        if gate_passes:
            pass_options = {f"{p.get('單號')} - {p.get('表單類型')} ({p.get('申請人')})": p for p in gate_passes}
            sel_pass_key = st.selectbox("🔍 選擇或掃描放行單號 (Select Gate Pass)", list(pass_options.keys()))
            target_pass = pass_options[sel_pass_key]

            st.warning("⚠️ **保全安管查核須知**：請務必核對現場實物、車牌號碼與攜出數量是否與系統記錄完全相符，確認無誤後再點擊下方按鈕放行。")
            st.write(f"* **單號**：`{target_pass.get('單號')}`")
            st.write(f"* **表單類型**：{target_pass.get('表單類型')}")
            st.write(f"* **申請人**：{target_pass.get('申請人')} ({target_pass.get('部門')})")
            st.write(f"* **內容摘要**：{target_pass.get('申請內容摘要')}")
            st.write(f"* **目前狀態**：{target_pass.get('簽核狀態')}")

            if st.button("🚪 確認實物無誤，執行門口放行 (Gate Pass Released)", type="primary", use_container_width=True):
                target_pass["簽核狀態"] = f"🟢 已由保全放行 (Released at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})"
                st.success(f"✅ 單號 `{target_pass.get('單號')}` 已成功放行！門禁記錄已封存。")
                st.rerun()
        else:
            st.info("目前尚無等待保全放行的派車單或物品攜出單。")

# ----------------------------------------------------
# 🔗 相容性進入點定義
# ----------------------------------------------------
def show(*args, **kwargs):
    render_approval_center_page(*args, **kwargs)

def main(*args, **kwargs):
    render_approval_center_page(*args, **kwargs)

def render_approval_center(*args, **kwargs):
    render_approval_center_page(*args, **kwargs)
