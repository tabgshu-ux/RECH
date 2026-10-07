import streamlit as st
import pandas as pd
import datetime

APPROVAL_I18N = {
    "繁體中文": {
        "title": "✍️ 管理部 - 電子簽核與請款/請假審核中心",
        "caption": "提交採購申請或請假單，系統自動依據規則（部門主管 ➔ 負責部門負責人 ➔ 請假≧3天經理簽核 ➔ 請假≧5天副總簽核）進行多級簽核，並提供即時進度追蹤。",
        "tab_submit": "📝 提交新簽核申請 (請假/採購)",
        "tab_track": "📊 簽核進度即時追蹤 (Flow Tracker)",
        "tab_review": "🎛️ 主管/經理/副總審核簽章",
        
        "submit_header": "📝 填寫電子簽核單",
        "lbl_type": "申請單類型 *",
        "type_opts": ["請假單 (Leave Request)", "採購申請單 (Purchase Requisition)"],
        "lbl_applicant": "申請人姓名 *",
        "lbl_dept": "所屬部門 *",
        "dept_opts": ["營運戰情室", "管理部", "工程與設計管理中心", "生產部", "資訊管理部"],
        "lbl_reason": "申請事由與說明 *",
        "reason_placeholder": "例如: 因家庭事務請假 4 天 / 採購廠區高壓電纜一批",
        
        # 請假專用
        "lbl_days": "請假天數 (天) *",
        
        # 採購專用
        "lbl_amount": "採購金額 (VND) *",

        "btn_submit": "🚀 提交送出簽核",
        "success_submit": "✅ 簽核單 `{doc_id}` 已成功送出！已進入第一階段簽核。",
        "warning_fill": "⚠️ 請完整填寫所有必填欄位！",

        "track_header": "📊 目前所有簽核單進度與關卡追蹤",
        "no_requests": "目前尚無任何簽核申請紀錄。",
        
        "review_header": "🎛️ 待簽核案件審查 (主管/經理/副總專用)",
        "select_review_item": "選擇要審核的單據 *",
        "lbl_comment": "簽核意見 / 批示內容",
        "btn_approve": "✅ 同意 / 通過 (Pass)",
        "btn_reject": "❌ 駁回 (Reject)",
        "success_approve": "✅ 已成功核准單據 `{doc_id}`，流程已流轉至下一關！",
        "success_reject": "❌ 已駁回單據 `{doc_id}`。",
        
        "col_id": "單號",
        "col_type": "類型",
        "col_applicant": "申請人",
        "col_dept": "部門",
        "col_status": "目前簽核關卡 (Current Stage)",
        "col_result": "審核結果"
    },
    "Tiếng Việt": {
        "title": "✍️ Trung tâm Phê duyệt Điện tử (Approval Center)",
        "caption": "Gửi yêu cầu nghỉ phép hoặc mua hàng; hệ thống tự động định tuyến quy trình phê duyệt đa cấp.",
        "tab_submit": "📝 Gửi Đơn Mới",
        "tab_track": "📊 Theo dõi Tiến độ Trực tiếp",
        "tab_review": "🎛️ Phê duyệt của Quản lý",
        "submit_header": "📝 Điền đơn điện tử",
        "lbl_type": "Loại đơn *",
        "type_opts": ["Đơn nghỉ phép", "Đơn mua hàng"],
        "lbl_applicant": "Người nộp *",
        "lbl_dept": "Phòng ban *",
        "dept_opts": ["Ban Giám đốc", "Phòng Quản lý", "Trung tâm Kỹ thuật", "Phòng Sản xuất", "Phòng IT"],
        "lbl_reason": "Lý do *",
        "reason_placeholder": "Ví dụ: Nghỉ phép 4 ngày...",
        "lbl_days": "Số ngày nghỉ *",
        "lbl_amount": "Giá trị mua (VND) *",
        "btn_submit": "🚀 Gửi duyệt",
        "success_submit": "✅ Đã gửi đơn `{doc_id}` thành công!",
        "warning_fill": "⚠️ Vui lòng điền đầy đủ thông tin!",
        "track_header": "📊 Theo dõi Tiến độ Phê duyệt",
        "no_requests": "Chưa có bản ghi nào.",
        "review_header": "🎛️ Phê duyệt đơn chờ xử lý",
        "select_file_target": "Chọn đơn cần duyệt *",
        "lbl_comment": "Ý kiến",
        "btn_approve": "✅ Phê duyệt",
        "btn_reject": "❌ Từ chối",
        "success_approve": "✅ Đã duyệt đơn `{doc_id}`!",
        "success_reject": "❌ Đã từ chối đơn `{doc_id}`.",
        "col_id": "Mã đơn",
        "col_type": "Loại",
        "col_applicant": "Người nộp",
        "col_dept": "Phòng ban",
        "col_status": "Trạng thái hiện tại",
        "col_result": "Kết quả"
    },
    "English": {
        "title": "✍️ E-Approval & Request Workflow Center",
        "caption": "Submit leave or purchase requests. The system automatically routes through multi-level approvals and tracks progress in real-time.",
        "tab_submit": "📝 Submit New Request",
        "tab_track": "📊 Real-time Flow Tracker",
        "tab_review": "🎛️ Management Review & Sign",
        "submit_header": "📝 Submit Electronic Request Form",
        "lbl_type": "Request Type *",
        "type_opts": ["Leave Request", "Purchase Requisition"],
        "lbl_applicant": "Applicant Name *",
        "lbl_dept": "Department *",
        "dept_opts": ["Executive", "Management Dept", "Engineering & Design", "Production Dept", "IT Dept"],
        "lbl_reason": "Reason / Description *",
        "reason_placeholder": "Example: 4 days personal leave / Purchase cables",
        "lbl_days": "Leave Days (Days) *",
        "lbl_amount": "Purchase Amount (VND) *",
        "btn_submit": "🚀 Submit Request",
        "success_submit": "✅ Request `{doc_id}` successfully submitted!",
        "warning_fill": "⚠️ Please fill in all required fields!",
        "track_header": "📊 Real-time Approval Flow & Stage Tracker",
        "no_requests": "No approval requests found.",
        "review_header": "🎛️ Pending Approvals Review",
        "select_review_item": "Select Request to Review *",
        "lbl_comment": "Review Comments / Instructions",
        "btn_approve": "✅ Approve / Pass",
        "btn_reject": "❌ Reject",
        "success_approve": "✅ Successfully approved `{doc_id}`!",
        "success_reject": "❌ Rejected `{doc_id}`.",
        "col_id": "Doc ID",
        "col_type": "Type",
        "col_applicant": "Applicant",
        "col_dept": "Department",
        "col_status": "Current Stage",
        "col_result": "Result"
    }
}

def render_approval_center(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = APPROVAL_I18N.get(active_lang, APPROVAL_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "approval_db" not in st.session_state:
        st.session_state.approval_db = [
            {
                "id": "REQ-2026-001",
                "type": "請假單 (Leave Request)",
                "applicant": "陳裕民 (Staff)",
                "dept": "工程與設計管理中心",
                "days": 4,
                "amount": 0.0,
                "reason": "家屬婚喪喜慶請假 4 天",
                "stage_idx": 2, 
                "stages": ["1. 部門主管簽核", "2. 負責部門負責人", "3. 經理簽核 (≧3天)", "4. 副總簽核 (≧5天)", "5. 簽核完成 (Approved)"],
                "status": "進行中 (等待經理簽核)",
                "history": [
                    {"stage": "1. 部門主管簽核", "status": "已通過", "by": "張課長", "time": "2026-10-06 10:00"},
                    {"stage": "2. 負責部門負責人", "status": "已通過", "by": "王經理 (代)", "time": "2026-10-06 14:30"},
                    {"stage": "3. 經理簽核 (≧3天)", "status": "審核中 (等待中)", "by": "林協理/經理", "time": "未審核"}
                ]
            },
            {
                "id": "REQ-2026-002",
                "type": "採購申請單 (Purchase Requisition)",
                "applicant": "阮文強 (Tech)",
                "dept": "生產部",
                "days": 0,
                "amount": 150000000.0,
                "reason": "廠區配電盤銅排與斷路器採購",
                "stage_idx": 1,
                "stages": ["1. 部門主管簽核", "2. 負責部門負責人", "3. 採購總監簽核", "4. 簽核完成 (Approved)"],
                "status": "進行中 (等待負責部門負責人)",
                "history": [
                    {"stage": "1. 部門主管簽核", "status": "已通過", "by": "黎主任", "time": "2026-10-07 09:15"},
                    {"stage": "2. 負責部門負責人", "status": "審核中 (等待中)", "by": "財務採購主管", "time": "未審核"}
                ]
            }
        ]

    tab_submit, tab_track, tab_review = st.tabs([
        L["tab_submit"], L["tab_track"], L["tab_review"]
    ])

    with tab_submit:
        st.markdown(f"### {L['submit_header']}")
        with st.form("form_submit_approval"):
            c1, c2 = st.columns(2)
            with c1:
                req_type = st.selectbox(L["lbl_type"], L["type_opts"])
                applicant = st.text_input(L["lbl_applicant"], value=st.session_state.get("user_name", "員工"))
            with c2:
                dept = st.selectbox(L["lbl_dept"], L["dept_opts"])
                
            days = 0.0
            amount = 0.0
            if "請假" in req_type or "Leave" in req_type:
                days = st.number_input(L["lbl_days"], min_value=0.5, value=3.0, step=0.5)
            else:
                amount = st.number_input(L["lbl_amount"], min_value=0.0, value=50000000.0, step=10000000.0)

            reason = st.text_area(L["lbl_reason"], placeholder=L["reason_placeholder"])

            if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
                if applicant and reason:
                    new_id = f"REQ-2026-{len(st.session_state.approval_db)+1:03d}"
                    
                    if "請假" in req_type or "Leave" in req_type:
                        stages = ["1. 部門主管簽核", "2. 負責部門負責人"]
                        if days >= 3:
                            stages.append("3. 經理簽核 (≧3天)")
                        if days >= 5:
                            stages.append("4. 副總簽核 (≧5天)")
                        stages.append("5. 簽核完成 (Approved)")
                    else:
                        stages = ["1. 部門主管簽核", "2. 負責部門負責人", "3. 財務/採購總監簽核", "4. 簽核完成 (Approved)"]

                    st.session_state.approval_db.insert(0, {
                        "id": new_id,
                        "type": req_type,
                        "applicant": applicant,
                        "dept": dept,
                        "days": days,
                        "amount": amount,
                        "reason": reason,
                        "stage_idx": 0,
                        "stages": stages,
                        "status": f"進行中 (等待 {stages[0]})",
                        "history": [
                            {"stage": stages[0], "status": "審核中 (等待中)", "by": f"{dept} 主管", "time": "未審核"}
                        ]
                    })
                    st.success(L["success_submit"].format(doc_id=new_id))
                    st.rerun()
                else:
                    st.warning(L["warning_fill"])

    with tab_track:
        st.markdown(f"### {L['track_header']}")
        if st.session_state.approval_db:
            for item in st.session_state.approval_db:
                with st.expander(f"📌 [{item['id']}] {item['type']} - 申請人: {item['applicant']} ({item['status']})"):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"**部門**: {item['dept']}")
                    c2.markdown(f"**事由**: {item['reason']}")
                    if item['days'] > 0:
                        c3.markdown(f"**請假天數**: {item['days']} 天")
                    else:
                        c3.markdown(f"**採購金額**: {item['amount']:,.0f} VND")

                    st.markdown("#### 🔄 即時簽核進度與關卡 (Flow Status)")
                    
                    total_stages = len(item['stages'])
                    current_idx = item['stage_idx']
                    
                    progress_val = min(float(current_idx) / max(1.0, float(total_stages - 1)), 1.0)
                    st.progress(progress_val)
                    
                    history_df = pd.DataFrame(item['history'])
                    st.dataframe(history_df, use_container_width=True)
        else:
            st.info(L["no_requests"])

    with tab_review:
        st.markdown(f"### {L['review_header']}")
        pending_items = [item for item in st.session_state.approval_db if item['stage_idx'] < len(item['stages']) - 1]
        
        if pending_items:
            review_opts = {f"{item['id']} - {item['type']} ({item['applicant']})": item for item in pending_items}
            selected_rev_key = st.selectbox(L["select_review_item"], list(review_opts.keys()))
            target_item = review_opts[selected_rev_key]

            st.markdown(f"**目前關卡**: `{target_item['stages'][target_item['stage_idx']]}`")
            st.markdown(f"**申請事由**: {target_item['reason']}")
            
            comment = st.text_input(L["lbl_comment"], value="同意辦理")

            col_a, col_b = st.columns(2)
            if col_a.button(L["btn_approve"], type="primary", use_container_width=True):
                curr_idx = target_item['stage_idx']
                target_item['history'][curr_idx]['status'] = "已通過"
                target_item['history'][curr_idx]['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                target_item['history'][curr_idx]['by'] = st.session_state.get("user_name", "主管")

                target_item['stage_idx'] += 1
                if target_item['stage_idx'] >= len(target_item['stages']) - 1:
                    target_item['stage_idx'] = len(target_item['stages']) - 1
                    target_item['status'] = "簽核完成 (Approved)"
                else:
                    next_stage = target_item['stages'][target_item['stage_idx']]
                    target_item['status'] = f"進行中 (等待 {next_stage})"
                    target_item['history'].append({
                        "stage": next_stage,
                        "status": "審核中 (等待中)",
                        "by": "指定簽核人",
                        "time": "未審核"
                    })

                st.success(L["success_approve"].format(doc_id=target_item['id']))
                st.rerun()

            if col_b.button(L["btn_reject"], type="secondary", use_container_width=True):
                target_item['status'] = "已駁回 (Rejected)"
                target_item['history'][target_item['stage_idx']]['status'] = "已駁回"
                target_item['history'][target_item['stage_idx']]['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                st.error(L["success_reject"].format(doc_id=target_item['id']))
                st.rerun()
        else:
            st.info("目前沒有需要您簽核的待辦案件。")

def show(*args, **kwargs):
    render_approval_center(*args, **kwargs)

def main(*args, **kwargs):
    render_approval_center(*args, **kwargs)

def render_approval_center(*args, **kwargs):
    render_approval_center(*args, **kwargs)
