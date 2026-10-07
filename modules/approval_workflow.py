import streamlit as st
import pandas as pd
import datetime

APPROVAL_I18N = {
    "繁體中文": {
        "title": "✍️ 管理部 - 電子簽核與請款/請假審核中心",
        "caption": "提交採購申請或請假單，系統自動依據規則進行多級簽核，並提供即時進度追蹤。",
        "tab_leave": "📝 員工請假申請單",
        "tab_po": "🛒 採購與請款申請單",
        "tab_track": "📊 簽核進度即時追蹤",
        "tab_review": "🎛️ 主管/經理/副總審核簽章",
        
        "leave_header": "📝 填寫請假申請單",
        "po_header": "🛒 填寫採購與請款申請單",
        
        "lbl_applicant": "申請人 (已鎖定登入帳號)",
        "lbl_dept": "所屬部門 (依帳號自動對應)",
        "lbl_reason": "申請事由與說明 *",
        
        "lbl_days": "請假天數 (天) *",
        "lbl_item_name": "採購項目名稱 *",
        "lbl_qty": "採購數量 *",
        "lbl_amount": "採購金額 (VND) *",
        "lbl_photo": "上傳參考照片 / 報價單 / 規格圖檔",

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
                "item_name": "",
                "qty": 0,
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
                "item_name": "高壓電纜一批與銅排",
                "qty": 5,
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

    # 上方分頁：明確拆分為請假、採購、追蹤、審核
    tab_leave, tab_po, tab_track, tab_review = st.tabs([
        L["tab_leave"], L["tab_po"], L["tab_track"], L["tab_review"]
    ])

    current_user = st.session_state.get("user_name", "admin")
    role = st.session_state.get("user_role", "admin")
    
    default_dept = "管理部"
    if role == "admin":
        default_dept = "營運戰情室"
    elif "生產" in current_user or role == "staff":
        default_dept = "生產部"

    # 1. 請假申請專用 Tab
    with tab_leave:
        st.markdown(f"### {L['leave_header']}")
        with st.form("form_submit_leave"):
            c1, c2 = st.columns(2)
            with c1:
                applicant = st.text_input(L["lbl_applicant"], value=current_user, disabled=True)
            with c2:
                dept = st.text_input(L["lbl_dept"], value=default_dept, disabled=True)
                
            days = st.number_input(L["lbl_days"], min_value=0.5, value=3.0, step=0.5)
            reason = st.text_area(L["lbl_reason"], placeholder="例如: 因家庭事務請假 4 天...")

            if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
                if current_user and reason:
                    new_id = f"REQ-2026-{len(st.session_state.approval_db)+1:03d}"
                    stages = ["1. 部門主管簽核", "2. 負責部門負責人"]
                    if days >= 3:
                        stages.append("3. 經理簽核 (≧3天)")
                    if days >= 5:
                        stages.append("4. 副總簽核 (≧5天)")
                    stages.append("5. 簽核完成 (Approved)")

                    st.session_state.approval_db.insert(0, {
                        "id": new_id,
                        "type": "請假單 (Leave Request)",
                        "applicant": current_user,
                        "dept": default_dept,
                        "days": days,
                        "item_name": "",
                        "qty": 0,
                        "amount": 0.0,
                        "reason": reason,
                        "has_photo": False,
                        "stage_idx": 0,
                        "stages": stages,
                        "status": f"進行中 (等待 {stages[0]})",
                        "history": [
                            {"stage": stages[0], "status": "審核中 (等待中)", "by": f"{default_dept} 主管", "time": "未審核"}
                        ]
                    })
                    st.success(L["success_submit"].format(doc_id=new_id))
                    st.rerun()
                else:
                    st.warning(L["warning_fill"])

    # 2. 採購申請專用 Tab
    with tab_po:
        st.markdown(f"### {L['po_header']}")
        with st.form("form_submit_po"):
            c1, c2 = st.columns(2)
            with c1:
                applicant = st.text_input(L["lbl_applicant"] + "_po", value=current_user, disabled=True)
            with c2:
                dept = st.text_input(L["lbl_dept"] + "_po", value=default_dept, disabled=True)
                
            c_i1, c_i2 = st.columns(2)
            with c_i1:
                item_name = st.text_input(L["lbl_item_name"], placeholder="例如: 高壓電纜 / 斷路器")
            with c_i2:
                qty = st.number_input(L["lbl_qty"], min_value=1, value=1, step=1)
            
            amount = st.number_input(L["lbl_amount"], min_value=0.0, value=50000000.0, step=10000000.0)
            uploaded_photo = st.file_uploader(L["lbl_photo"], type=["jpg", "png", "jpeg", "pdf"])
            reason = st.text_area(L["lbl_reason"] + "_po", placeholder="例如: 廠區配電盤銅排與斷路器採購說明...")

            if st.form_submit_button(L["btn_submit"] + "_po", type="primary", use_container_width=True):
                if current_user and reason and item_name:
                    new_id = f"REQ-2026-{len(st.session_state.approval_db)+1:03d}"
                    stages = ["1. 部門主管簽核", "2. 負責部門負責人", "3. 財務/採購總監簽核", "4. 簽核完成 (Approved)"]

                    st.session_state.approval_db.insert(0, {
                        "id": new_id,
                        "type": "採購申請單 (Purchase Requisition)",
                        "applicant": current_user,
                        "dept": default_dept,
                        "days": 0,
                        "item_name": item_name,
                        "qty": qty,
                        "amount": amount,
                        "reason": reason,
                        "has_photo": uploaded_photo is not None,
                        "stage_idx": 0,
                        "stages": stages,
                        "status": f"進行中 (等待 {stages[0]})",
                        "history": [
                            {"stage": stages[0], "status": "審核中 (等待中)", "by": f"{default_dept} 主管", "time": "未審核"}
                        ]
                    })
                    st.success(L["success_submit"].format(doc_id=new_id))
                    st.rerun()
                else:
                    st.warning(L["warning_fill"])

    # 3. 進度追蹤 Tab
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
                        c3.markdown(f"**採購項目**: {item.get('item_name', 'N/A')} (數量: {item.get('qty', 1)})<br>**採購金額**: {item['amount']:,.0f} VND", unsafe_allow_html=True)

                    st.markdown("#### 🔄 即時簽核進度與關卡 (Flow Status)")
                    
                    total_stages = len(item['stages'])
                    current_idx = item['stage_idx']
                    
                    progress_val = min(float(current_idx) / max(1.0, float(total_stages - 1)), 1.0)
                    st.progress(progress_val)
                    
                    history_df = pd.DataFrame(item['history'])
                    st.dataframe(history_df, use_container_width=True)
        else:
            st.info(L["no_requests"])

    # 4. 主管審核 Tab
    with tab_review:
        st.markdown(f"### {L['review_header']}")
        pending_items = [item for item in st.session_state.approval_db if item['stage_idx'] < len(item['stages']) - 1]
        
        if pending_items:
            review_opts = {f"{item['id']} - {item['type']} ({item['applicant']})": item for item in pending_items}
            selected_rev_key = st.selectbox(L["select_review_item"], list(review_opts.keys()))
            target_item = review_opts[selected_rev_key]

            st.markdown(f"**目前關卡**: `{target_item['stages'][target_item['stage_idx']]}`")
            st.markdown(f"**申請事由**: {target_item['reason']}")
            if target_item.get('item_name'):
                st.markdown(f"**採購項目**: {target_item['item_name']} | **數量**: {target_item.get('qty', 1)} | **金額**: {target_item['amount']:,.0f} VND")
            
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
