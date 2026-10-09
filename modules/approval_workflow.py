import streamlit as st
import pandas as pd
import datetime

def render_approval_center(engine=None, lang="繁體中文", **kwargs):
    st.title("✍️ 裕豐電機工業 - 全公司電子簽核與進度追蹤中心")
    st.caption("提供請假、採購、車輛調派（含里程數記錄防偷油機制）與物品攜出之跨部門電子簽核與保全放行管制。")

    if "approval_requests" not in st.session_state:
        st.session_state.approval_requests = [
            {"單號": "REQ-2026-001", "類型": "請假申請", "申請人": "Nguyễn Văn An", "部門": "資訊管理部", "內容": "類別: 病假 | 時數: 8.0 小時", "事由": "身體不適前往醫院就診", "狀態": "🟢 主管已核准"},
            {"單號": "CAR-2026-002", "類型": "車輛調派單", "申請人": "admin", "部門": "總務管理部", "內容": "車號: 61A-888.88 | 出發廠區: 越南西寧廠 | 起始里程: 45,200 km", "事由": "載送台幹前往案場安裝", "狀態": "🟢 主管已核准"}
        ]

    if "gate_pass_records" not in st.session_state:
        st.session_state.gate_pass_records = [
            {"放行單號": "CAR-2026-002", "單據類型": "車輛調派單", "車號/品名": "61A-888.88 (起始里程: 45,200 km)", "申請人": "admin", "核准狀態": "🟢 主管已核准", "門禁放行狀態": "🟢 保全已驗收放行"}
        ]

    current_user = st.session_state.get('user_name', 'admin')
    current_role = str(st.session_state.get('user_role', 'admin')).strip().upper()

    tab1, tab2, tab3, tab4 = st.tabs([
        "✍️ 提交各類電子簽核表單", 
        "📊 我的申請進度追蹤", 
        "🛡️ 主管待辦審核中心",
        "🔒 保全門禁放行驗證與查核 (Security Gate)"
    ])

    with tab1:
        st.markdown("#### ✍️ 填寫並提交電子簽核表單")
        
        req_type = st.selectbox(
            "選擇要提交的表單類型 (Select Request Type)", 
            [
                "請假申請單", 
                "採購請購單", 
                "車輛調派與門禁申請單",
                "物品攜出放行單"
            ]
        )

        if "請假申請單" in req_type:
            st.markdown("---")
            st.markdown("#### 🍃 請假申請單 (Đơn xin nghỉ phép)")
            with st.form("leave_request_form"):
                lc1, lc2 = st.columns(2)
                with lc1:
                    st.text_input("申請人姓名", value=f"{current_user} ({current_role})", disabled=True)
                    leave_type = st.selectbox("請假類別", ["事假", "病假", "特休假", "喪假", "產假 / 婚假"])
                with lc2:
                    request_no = f"REQ-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
                    st.text_input("申請單編號", value=request_no, disabled=True)
                    st.text_input("申請部門", value="工程與設計管理中心", disabled=True)

                leave_hours = st.number_input("請假時數 (Hours) * 支援以 0.5 小時（半小時）為單位遞增", min_value=0.5, max_value=176.0, value=8.0, step=0.5)
                uploaded_proof = st.file_uploader("📤 上傳證明文件 (病歷單、醫生證明、喪假訃聞等)", type=["png", "jpg", "jpeg", "pdf"])
                leave_reason = st.text_area("請假事由說明", placeholder="例如：前往醫院看診，請假 1.5 小時。")

                if st.form_submit_button("🚀 送出請假電子簽核", type="primary", use_container_width=True):
                    if leave_reason.strip():
                        proof_status = "已附證明" if uploaded_proof else "無附證明"
                        st.session_state.approval_requests.insert(0, {
                            "單號": request_no, "類型": "請假申請", "申請人": current_user,
                            "部門": "工程與設計管理中心", "內容": f"類別: {leave_type} | 時數: {leave_hours} 小時 ({proof_status})",
                            "事由": leave_reason, "狀態": "🟡 待主管審核"
                        })
                        st.success(f"✅ 成功提交請假申請！總計時數：{leave_hours} 小時。")
                        st.rerun()

        elif "採購請購單" in req_type:
            st.markdown("---")
            st.markdown("#### 🛒 採購請購單 (Đơn đề nghị mua hàng)")
            with st.form("po_request_form"):
                po1, po2 = st.columns(2)
                with po1:
                    st.text_input("申請人", value=f"{current_user}", disabled=True)
                    po_category = st.selectbox("採購科目大類", ["辦公文具與事務用品", "會計發票與憑證耗材", "資訊設備與電腦零配件", "廠務與工安防護裝備", "工程專案機電零件"])
                with po2:
                    po_no = f"PO-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
                    st.text_input("請購單編號", value=po_no, disabled=True)
                    po_item_name = st.text_input("採購品名與詳細規格 *", placeholder="例如: 辦公用 A4 紙或特定零配件")

                po_amount = st.text_input("預估金額 *", value="2,500,000 ₫")
                uploaded_file = st.file_uploader("📤 上傳物料/設備照片或型錄截圖", type=["png", "jpg", "jpeg"])
                po_reason = st.text_area("採購用途說明 *", placeholder="請說明採購用途與部門。")
                
                if st.form_submit_button("🚀 送出採購請購申請", type="primary", use_container_width=True):
                    if po_item_name.strip() and po_reason.strip():
                        img_status = "已附圖片" if uploaded_file else "無附圖"
                        st.session_state.approval_requests.insert(0, {
                            "單號": po_no, "類型": "採購請購單", "申請人": current_user,
                            "部門": "管理部", "內容": f"分類: {po_category} | 品名: {po_item_name} | 金額: {po_amount} ({img_status})",
                            "事由": po_reason, "狀態": "🟡 待主管審核"
                        })
                        st.success("✅ 採購請購單已成功送出！")
                        st.rerun()

        # 💡 車輛調派與門禁申請單：加入里程數記錄（防偷油與油資審核）
        elif "車輛調派與門禁申請單" in req_type:
            st.markdown("---")
            st.markdown("#### 🚗 車輛調派與門禁申請單 (Đơn điều phối xe - 含里程數防偷油機制)")
            st.info("💡 **AI ERP 防弊機制**：出發前必須記錄車輛當前儀表板【起始里程數 (Km)】，保全出廠時將進行複核，未來將串聯 GPS 與油費報銷比對，防止油資浮報與偷油。")

            with st.form("vehicle_request_form"):
                v1, v2 = st.columns(2)
                with v1:
                    st.text_input("申請人", value=f"{current_user}", disabled=True)
                    v_car = st.selectbox("申請車輛", ["61A-888.88 (7人座商務車)", "61C-123.45 (貨車)"])
                    v_origin = st.selectbox("出發廠區 / 派車廠區", ["越南西寧廠", "越南海防廠"])
                with v2:
                    v_no = f"CAR-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
                    st.text_input("派車單號", value=v_no, disabled=True)
                    # 🛡️ 關鍵新增：出發里程數填寫
                    v_start_km = st.number_input("出發時儀表板里程數 (Start Odometer in KM) *", min_value=0, max_value=999999, value=45200, step=1, help="請填寫車輛出發當下的實際儀表板總公里數")

                v_dest = st.text_input("目的地 (Destination) *", value="客戶端 / 外部工程工地")
                uploaded_odo_img = st.file_uploader("📤 上傳出發時儀表板里程數照片 (防偷油查核用) *", type=["png", "jpg", "jpeg"])
                v_reason = st.text_area("派車事由說明 *", placeholder="載送工程人員與設備前往案場安裝。")

                if st.form_submit_button("🚀 送出車輛調派申請 (含里程紀錄)", type="primary", use_container_width=True):
                    if v_dest.strip() and v_reason.strip():
                        odo_status = f"起始里程: {v_start_km} km (已附儀表板照片)" if uploaded_odo_img else f"起始里程: {v_start_km} km (⚠️ 未附照片)"
                        st.session_state.approval_requests.insert(0, {
                            "單號": v_no, "類型": "車輛調派單", "申請人": current_user,
                            "部門": "總務管理部", "內容": f"車輛: {v_car} | 出發: {v_origin} ➔ 目的: {v_dest} | {odo_status}",
                            "事由": v_reason, "狀態": "🟡 待主管審核"
                        })
                        st.session_state.gate_pass_records.insert(0, {
                            "放行單號": v_no, "單據類型": "車輛調派單", "車號/品名": f"{v_car} ({v_origin}出發 | {v_start_km} km)",
                            "申請人": current_user, "核准狀態": "🟡 待主管審核", "門禁放行狀態": "🔒 待審核與放行"
                        })
                        st.success("✅ 車輛調派申請已送出！保全門檢時將核對里程數與儀表板照片。")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫目的地與派車事由！")

        else:
            st.markdown("---")
            st.markdown("#### 📦 物品攜出放行單 (Giấy phép mang tài sản/vật tư ra ngoài)")
            with st.form("carryout_request_form"):
                co1, co2 = st.columns(2)
                with co1:
                    st.text_input("申請人", value=f"{current_user}", disabled=True)
                    co_origin = st.selectbox("出發廠區 / 物品所在地", ["越南西寧廠", "越南海防廠"])
                    co_items = st.text_input("攜出物品名稱、型號與數量 *", placeholder="例如: 筆電、測試儀器 2 台")
                with co2:
                    co_no = f"OUT-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
                    st.text_input("攜出單號", value=co_no, disabled=True)
                    co_dest = st.text_input("攜出目的地/用途", value="外部工地現場檢測")
                
                uploaded_carryout_img = st.file_uploader("📤 上傳攜出物品照片、設備外觀與序號圖 (防弊查核用) *", type=["png", "jpg", "jpeg"])
                co_reason = st.text_area("攜出事由說明 *", placeholder="因專案工程需要，攜出工具進行現場測試，預計當日攜回。")
                
                if st.form_submit_button("🚀 送出物品攜出申請", type="primary", use_container_width=True):
                    if co_items.strip() and co_reason.strip():
                        img_status = "已附防弊照片" if uploaded_carryout_img else "⚠️ 未附照片"
                        st.session_state.approval_requests.insert(0, {
                            "單號": co_no, "類型": "物品攜出單", "申請人": current_user,
                            "部門": "工程部", "內容": f"物品: {co_items} | 出發: {co_origin} ➔ 目的: {co_dest} ({img_status})",
                            "事由": co_reason, "狀態": "🟡 待主管審核"
                        })
                        st.session_state.gate_pass_records.insert(0, {
                            "放行單號": co_no, "單據類型": "物品攜出單", "車號/品名": f"{co_items} ({co_origin}發)",
                            "申請人": current_user, "核准狀態": "🟡 待主管審核", "門禁放行狀態": "🔒 待審核與放行"
                        })
                        st.success("✅ 物品攜出申請已送出！")
                        st.rerun()

    with tab2:
        st.markdown("#### 📊 我的電子簽核申請進度即時追蹤")
        st.dataframe(pd.DataFrame(st.session_state.approval_requests), use_container_width=True)

    with tab3:
        st.markdown("#### 🛡️ 主管待辦審核中心")
        for idx, req in enumerate(st.session_state.approval_requests):
            col_a, col_b, col_c = st.columns([3, 2, 1])
            with col_a:
                st.text(f"[{req['單號']}] {req['類型']} - 申請人: {req['申請人']}")
                st.caption(f"內容: {req['內容']}")
            with col_b:
                st.text(f"狀態: {req['狀態']}")
            with col_c:
                if "待主管審核" in req['狀態']:
                    if st.button(f"✅ 核准_{idx}", key=f"approve_{idx}"):
                        req['狀態'] = "🟢 主管已核准"
                        for g in st.session_state.gate_pass_records:
                            if g["放行單號"] == req["單號"]:
                                g["核准狀態"] = "🟢 主管已核准"
                                g["門禁放行狀態"] = "🔓 待保全驗收放行"
                        st.success(f"已核准單號 {req['單號']}")
                        st.rerun()

    with tab4:
        st.markdown("#### 🔒 保全門禁放行驗證與查核中心 (Security Gate)")
        st.dataframe(pd.DataFrame(st.session_state.gate_pass_records), use_container_width=True)
        with st.form("security_gate_form"):
            g_no = st.text_input("輸入放行單號或車號進行查核放行")
            if st.form_submit_button("🚪 核對里程照片與實物無誤，一鍵放行 (Gate Release)", type="primary", use_container_width=True):
                if g_no.strip():
                    for rec in st.session_state.gate_pass_records:
                        if g_no.strip().lower() in rec["放行單號"].lower():
                            rec["門禁放行狀態"] = "🟢 保全已驗收放行"
                    st.success(f"✅ 單號 [{g_no}] 已完成門禁放行與里程登記！")
                    st.rerun()
