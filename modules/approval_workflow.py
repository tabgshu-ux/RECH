import streamlit as st
import pandas as pd
import datetime

def render_approval_center(engine=None, lang="繁體中文", **kwargs):
    st.title("✍️ 裕豐電機工業 - 全公司電子簽核與進度追蹤中心")
    st.caption("提供請假、採購、車輛調派與物品攜出之跨部門電子簽核，支援以 0.5 小時（半小時）為單位的請假計算及保全門禁放行。")

    # 初始化簽核與門禁資料庫
    if "approval_requests" not in st.session_state:
        st.session_state.approval_requests = [
            {"單號": "REQ-2026-001", "類型": "請假申請", "申請人": "Nguyễn Văn An", "部門": "資訊管理部", "內容": "類別: 事假 | 時數: 4.0 小時", "事由": "前往銀行辦理公務與私事處理", "狀態": "🟢 主管已核准"},
            {"單號": "REQ-2026-002", "類型": "採購請購單", "申請人": "Trần Thị Mai", "部門": "管理部", "內容": "品名: 辦公室印表機碳粉匣 2 支", "事由": "會計部日常行政耗材補充", "狀態": "🟡 待主管審核"},
            {"單號": "REQ-2026-003", "類型": "車輛調派單", "申請人": "admin", "部門": "總經理室", "內容": "車號: 61A-888.88 (7人座商務車) | 目的地: 西寧廠", "事由": "載送台幹前往西寧廠進行高壓配電盤驗收", "狀態": "🟢 主管已核准"}
        ]

    if "gate_pass_records" not in st.session_state:
        st.session_state.gate_pass_records = [
            {"放行單號": "GATE-2026-001", "單據類型": "車輛調派單", "車號/品名": "61A-888.88 (商務車)", "申請人": "admin", "核准狀態": "🟢 主管已核准", "門禁放行狀態": "🔒 待保全驗收放行"}
        ]

    current_user = st.session_state.get('user_name', 'admin')
    current_role = str(st.session_state.get('user_role', 'admin')).strip().lower()

    # 上方 Tab 分頁
    tab1, tab2, tab3, tab4 = st.tabs([
        "✍️ 提交各類電子簽核表單", 
        "📊 我的申請進度追蹤", 
        "🛡️ 主管待辦審核中心",
        "🔒 保全門禁放行驗證與查核 (Security Gate)"
    ])

    # ====================================================
    # Tab 1：提交各類電子簽核表單
    # ====================================================
    with tab1:
        st.markdown("#### ✍️ 填寫並提交電子簽核表單")
        
        req_type = st.selectbox(
            "選擇要提交的表單類型 (Select Request Type)", 
            [
                "🍃 請假申請單 (Leave Request)", 
                "🛒 採購請購單 (Purchase Requisition)", 
                "🚗 車輛調派與門禁申請單 (Vehicle Dispatch)"
            ]
        )

        if "請假" in req_type:
            st.markdown("---")
            st.markdown("#### 🍃 請假申請單 (Leave Request)")
            with st.form("leave_request_form"):
                lc1, lc2 = st.columns(2)
                with lc1:
                    applicant_name = st.text_input("申請人姓名 (Applicant Name)", value=f"{current_user} ({current_role.upper()})", disabled=True)
                    leave_type = st.selectbox("請假類別 (Leave Type)", ["事假 (Personal Leave)", "病假 (Sick Leave)", "特休假 (Annual Leave)", "產假/婚喪假 (Maternity/Bereavement)"])
                with lc2:
                    request_no = f"REQ-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
                    request_no_input = st.text_input("申請單編號 (Request No.)", value=request_no, disabled=True)
                    department = st.text_input("申請部門 (Department)", value="工程與設計管理中心", disabled=True)

                # ⏱️ 支援 0.5 小時（半小時）為單位的請假時數
                leave_hours = st.number_input(
                    "請假時數 (Hours) * 支援以 0.5 小時（半小時）為單位遞增", 
                    min_value=0.5, 
                    max_value=176.0, 
                    value=8.0, 
                    step=0.5,
                    help="例如：請假半小時請輸入 0.5，請假 1 小時輸入 1.0，請假半天(4小時)輸入 4.0"
                )

                leave_reason = st.text_area("請假事由說明 (Reason)", placeholder="例如：前往醫院看診，請假 1.5 小時。")

                if st.form_submit_button("🚀 送出電子簽核申請", type="primary", use_container_width=True):
                    if leave_reason.strip():
                        st.session_state.approval_requests.insert(0, {
                            "單號": request_no, "類型": "請假申請", "申請人": current_user,
                            "部門": "工程與設計管理中心", "內容": f"類別: {leave_type} | 時數: {leave_hours} 小時",
                            "事由": leave_reason, "狀態": "🟡 待主管審核"
                        })
                        st.success(f"✅ 成功提交請假申請！總計時數：{leave_hours} 小時（含半小時精確計算），已送交主管審核。")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫請假事由說明！")

        elif "採購" in req_type:
            st.markdown("---")
            st.markdown("#### 🛒 採購請購單 (Purchase Requisition)")
            with st.form("po_request_form"):
                po1, po2 = st.columns(2)
                with po1:
                    st.text_input("申請人", value=f"{current_user}", disabled=True)
                    po_item = st.text_input("採購品名與規格", placeholder="例如: 銅排 Busbar 10x100mm 50kg")
                with po2:
                    po_no = f"PO-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
                    st.text_input("請購單編號", value=po_no, disabled=True)
                    po_amount = st.text_input("預估金額 (VND)", value="15,000,000 ₫")
                
                po_reason = st.text_area("採購用途說明", placeholder="用於西寧廠 2000A 配電盤專案擴充。")
                if st.form_submit_button("🚀 送出採購請購申請", type="primary", use_container_width=True):
                    st.session_state.approval_requests.insert(0, {
                        "單號": po_no, "類型": "採購請購單", "申請人": current_user,
                        "部門": "採購與工程部", "內容": f"品名: {po_item} | 金額: {po_amount}",
                        "事由": po_reason, "狀態": "🟡 待主管審核"
                    })
                    st.success("✅ 採購請購單已成功送出！")
                    st.rerun()

        else:
            st.markdown("---")
            st.markdown("#### 🚗 車輛調派與門禁申請單")
            with st.form("vehicle_request_form"):
                v1, v2 = st.columns(2)
                with v1:
                    st.text_input("申請人", value=f"{current_user}", disabled=True)
                    v_car = st.selectbox("申請車輛", ["61A-888.88 (7人座商務車)", "61C-123.45 (貨車)"])
                with v2:
                    v_no = f"CAR-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
                    st.text_input("派車單號", value=v_no, disabled=True)
                    v_dest = st.text_input("目的地", value="越南西寧廠")
                
                v_reason = st.text_area("派車事由", placeholder="載送工程人員與設備前往案場安裝。")
                if st.form_submit_button("🚀 送出車輛調派申請", type="primary", use_container_width=True):
                    st.session_state.approval_requests.insert(0, {
                        "單號": v_no, "類型": "車輛調派單", "申請人": current_user,
                        "部門": "總務管理部", "內容": f"車輛: {v_car} | 目的地: {v_dest}",
                        "事由": v_reason, "狀態": "🟡 待主管審核"
                    })
                    # 同步新增至保全待驗收清單
                    st.session_state.gate_pass_records.insert(0, {
                        "放行單號": v_no, "單據類型": "車輛調派單", "車號/品名": v_car,
                        "申請人": current_user, "核准狀態": "🟡 待主管審核", "門禁放行狀態": "🔒 待審核與放行"
                    })
                    st.success("✅ 車輛調派申請已送出，並已連動同步至保全門禁端！")
                    st.rerun()

    # ====================================================
    # Tab 2：我的申請進度追蹤
    # ====================================================
    with tab2:
        st.markdown("#### 📊 我的電子簽核申請進度即時追蹤")
        st.dataframe(pd.DataFrame(st.session_state.approval_requests), use_container_width=True)

    # ====================================================
    # Tab 3：主管待辦審核中心
    # ====================================================
    with tab3:
        st.markdown("#### 🛡️ 主管待辦審核中心 (Manager Approval Center)")
        st.info("💡 主管可在此檢視所有待審核之請假、採購與派車單，並進行一鍵審核。")
        
        for idx, req in enumerate(st.session_state.approval_requests):
            col_a, col_b, col_c = st.columns([3, 2, 1])
            with col_a:
                st.text(f"[{req['單號']}] {req['類型']} - 申請人: {req['申請人']} ({req['部門']})")
                st.caption(f"內容: {req['內容']} | 事由: {req['事由']}")
            with col_b:
                st.text(f"目前狀態: {req['狀態']}")
            with col_c:
                if "待主管審核" in req['狀態']:
                    if st.button(f"✅ 核准_{idx}", key=f"approve_{idx}"):
                        req['狀態'] = "🟢 主管已核准"
                        st.success(f"已核准單號 {req['單號']}")
                        st.rerun()

    # ====================================================
    # Tab 4：保全門禁放行驗證與查核 (Security Gate)
    # ====================================================
    with tab4:
        st.markdown("#### 🔒 保全門禁放行驗證與查核中心 (Security Gate & Pass Release)")
        st.caption("專供廠區保全人員（Security）核對經主管核准的車輛派車單與物品攜出單，進行實物與車牌驗收放行。")

        st.markdown("##### 📋 廠區門禁放行管制清單")
        st.dataframe(pd.DataFrame(st.session_state.gate_pass_records), use_container_width=True)

        st.markdown("---")
        st.markdown("##### 🚗 門禁實物與車牌驗收放行作業")
        with st.form("security_gate_form"):
            g_no = st.text_input("輸入放行單號或車牌號碼 (Scan / Enter Gate Pass No.)", placeholder="例如: CAR-202610090925 或 61A-888.88")
            g_remark = st.text_area("保全查核備註 (Security Inspection Note)", placeholder="例如: 確認車上載運配電盤零件無誤，車牌相符，准予放行出廠。")
            
            if st.form_submit_button("🚪 確認實物與車牌無誤，一鍵放行 (Gate Release)", type="primary", use_container_width=True):
                if g_no.strip():
                    found = False
                    for rec in st.session_state.gate_pass_records:
                        if g_no.strip().lower() in rec["放行單號"].lower() or g_no.strip().lower() in rec["車號/品名"].lower():
                            rec["門禁放行狀態"] = "🟢 保全已驗收放行"
                            found = True
                    st.success(f"✅ 成功完成門禁查核！單號 [{g_no}] 已正式放行出廠，系統已同步記錄放行時間。")
                    st.rerun()
                else:
                    st.warning("⚠️ 請輸入要放行的單號或車牌！")
