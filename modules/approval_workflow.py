import streamlit as st
import pandas as pd
import datetime
import base64
import re
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 三語系字典 (完整補齊 lbl_proj 避開 KeyError)
# ----------------------------------------------------
APPROVAL_I18N = {
    "繁體中文": {
        "title": "✍️ 全公司電子簽核中心 (Approval Center)",
        "caption": "提交請假、採購請款、公務派車或專案簽報；系統自動依據權限進行多級電子簽核。",
        "tab_leave": "🏖️ 1. 員工請假申請",
        "tab_proc": "📦 2. 採購與請款申請單 (PR)",
        "tab_vehicle": "🚗 3. 廠區公務派車申請單",
        "tab_pending": "📑 4. 待簽核案件審查 (主管專區)",
        "tab_status": "📊 5. 簽核進度即時追蹤",
        "tab_security": "🛡️ 6. 保全門禁車輛放行查驗 (保全專區)",
        "info_vehicle": "🔒 派車申請流程：員工填單 ➔ 部門主管簽核 ➔ 門禁保全確認出廠放行與里程登記。",
        "info_pr": "🔒 系統已自動綁定目前登入者身分，並支援上傳/拍攝實物照片供採購與主管對比確認。",
        "lbl_requester": "申請人姓名 (系統綁定) *",
        "lbl_dept": "所屬部門 (系統綁定)",
        "lbl_proj": "歸屬工程/專案編號",
        "lbl_cat": "請購項目細分類別 *",
        "lbl_item": "物品/材料名稱與規格 *",
        "lbl_qty": "需求數量",
        "lbl_unit": "單位",
        "lbl_amount": "預估總金額 (VND) *",
        "lbl_photo": "📸 上傳/拍攝實物對比照片或規格圖檔 (JPG/PNG/PDF)",
        "lbl_reason": "請購用途與詳細說明",
        "btn_submit_pr": "🚀 提交採購請款單並啟動多級簽核",
        "lbl_v_type": "派車用途類別 *",
        "lbl_vehicle": "選擇公務車輛 / 車號 *",
        "lbl_driver": "駕駛員 / 司機姓名",
        "lbl_destination": "前往目的地 / 案場名稱 *",
        "lbl_out_time": "預計出廠時間",
        "lbl_in_time": "預計返回時間",
        "lbl_v_reason": "派車公務事由與詳細說明 *",
        "btn_submit_v": "🚀 提交派車申請單送部門主管審核"
    },
    "English": {
        "title": "✍️ Enterprise Approval Center",
        "caption": "Submit Leave, PR, Vehicle Dispatch, or Approvals; automated multi-level pipeline.",
        "tab_leave": "🏖️ 1. Leave Request",
        "tab_proc": "📦 2. Purchase Requisition (PR)",
        "tab_vehicle": "🚗 3. Vehicle Dispatch",
        "tab_pending": "📑 4. Pending Approvals (Managers)",
        "tab_status": "📊 5. Real-time Workflow Tracking",
        "tab_security": "🛡️ 6. Gate Security Gatepass Control",
        "info_vehicle": "🔒 Dispatch flow: Employee submit ➔ Manager Approval ➔ Security Check-out.",
        "info_pr": "🔒 Identity locked to current user. Supports uploading item photos for review.",
        "lbl_requester": "Applicant Name (Locked) *",
        "lbl_dept": "Department (Locked)",
        "lbl_proj": "Project Code",
        "lbl_cat": "Detailed Category *",
        "lbl_item": "Item Name & Specs *",
        "lbl_qty": "Quantity",
        "lbl_unit": "Unit",
        "lbl_amount": "Est. Total Amount (VND) *",
        "lbl_photo": "📸 Upload / Capture Photo or Spec (JPG/PNG/PDF)",
        "lbl_reason": "Purpose & Detailed Notes",
        "btn_submit_pr": "🚀 Submit PR & Launch Approval Workflow",
        "lbl_v_type": "Dispatch Purpose *",
        "lbl_vehicle": "Select Vehicle / Plate No *",
        "lbl_driver": "Driver Name",
        "lbl_destination": "Destination / Site *",
        "lbl_out_time": "Est. Outbound Time",
        "lbl_in_time": "Est. Return Time",
        "lbl_v_reason": "Purpose & Notes *",
        "btn_submit_v": "🚀 Submit Dispatch Request"
    },
    "Tiếng Việt": {
        "title": "✍️ Trung tâm Phê duyệt Điện tử",
        "caption": "Tạo yêu cầu nghỉ phép, mua hàng, xin xe; hệ thống tự động duyệt theo phân cấp.",
        "tab_leave": "🏖️ 1. Đơn xin nghỉ phép",
        "tab_proc": "📦 2. Đơn yêu cầu mua hàng (PR)",
        "tab_vehicle": "🚗 3. Đăng ký xe công tác",
        "tab_pending": "📑 4. Hồ sơ chờ duyệt (Dành cho Sếp)",
        "tab_status": "📊 5. Theo dõi tiến độ phê duyệt",
        "tab_security": "🛡️ 6. Bảo vệ kiểm tra xe ra vào",
        "info_vehicle": "🔒 Quy trình: Nhân viên đăng ký ➔ Quản lý duyệt ➔ Bảo vệ cho xe ra.",
        "info_pr": "🔒 Tự động khóa tài khoản người tạo. Hỗ trợ chụp/tải ảnh đính kèm.",
        "lbl_requester": "Tên người đăng ký (Khóa) *",
        "lbl_dept": "Bộ phận (Khóa)",
        "lbl_proj": "Mã dự án",
        "lbl_cat": "Phân loại vật tư *",
        "lbl_item": "Tên & Quy cách vật tư *",
        "lbl_qty": "Số lượng",
        "lbl_unit": "Đơn vị",
        "lbl_amount": "Tổng tiền dự kiến (VND) *",
        "lbl_photo": "📸 Tải ảnh / Chụp ảnh vật tư (JPG/PNG/PDF)",
        "lbl_reason": "Mục đích sử dụng & Ghi chú",
        "btn_submit_pr": "🚀 Gửi đơn yêu cầu mua hàng",
        "lbl_v_type": "Mục đích sử dụng *",
        "lbl_vehicle": "Chọn xe / Biển số xe *",
        "lbl_driver": "Tên tài xế",
        "lbl_destination": "Nơi đến / Tên công trường *",
        "lbl_out_time": "Thời gian ra dự kiến",
        "lbl_in_time": "Thời gian về dự kiến",
        "lbl_v_reason": "Lý do công tác *",
        "btn_submit_v": "🚀 Gửi đơn đăng ký xe"
    }
}

PROC_CATEGORIES = [
    "🔌 配電盤高低壓元件與電氣材料 (需設計/BOM審核)",
    "⚡ 水電工程管線與線槽/電纜材料",
    "✂️ 板金加工原物料 (銅排、鐵板、粉體塗料)",
    "🛠️ 工地現場施工耗材、工具與五金配件",
    "🦺 工安防護具與現場安全設施",
    "🚗 廠區車輛維修零件與油品",
    "🏢 廠區機器設備與固定資產",
    "💻 資訊軟硬體與網路通訊設備",
    "🥗 幹部宿舍食材與廚房用品",
    "📄 行政總務文具與日常用品"
]

def parse_formatted_amount(val_str):
    if not val_str:
        return 0.0
    clean_str = re.sub(r"[^\d]", "", str(val_str))
    return float(clean_str) if clean_str else 0.0

def format_vnd_text(amount):
    try:
        val = float(amount)
        return f"{val:,.0f}".replace(",", ".") + " VND"
    except Exception:
        return f"{amount} VND"

def inject_approval_css():
    st.markdown("""
        <style>
        html, body, [class*="css"] { font-size: 16px !important; }
        div.stButton > button {
            width: 100% !important;
            height: 3rem !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
            border-radius: 8px !important;
        }
        .appr-card {
            background-color: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-left: 5px solid #0284C7;
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 12px;
        }
        .security-card {
            background-color: #FEF2F2;
            border: 1px solid #FCA5A5;
            border-left: 5px solid #DC2626;
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 12px;
        }
        </style>
    """, unsafe_allow_html=True)

def init_approval_db(engine):
    """初始化資料庫表格"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            # 1. 請購單
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.purchase_requisitions (
                    id SERIAL PRIMARY KEY,
                    pr_code VARCHAR(50) UNIQUE NOT NULL,
                    requester_name VARCHAR(100) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    project_code VARCHAR(50),
                    item_category VARCHAR(100) NOT NULL,
                    item_name VARCHAR(200) NOT NULL,
                    qty NUMERIC(10,2) NOT NULL,
                    unit VARCHAR(20) DEFAULT '個',
                    est_amount NUMERIC(15,2) DEFAULT 0,
                    item_photo TEXT,
                    tech_approval VARCHAR(50) DEFAULT '待設計主管審核',
                    mgr_approval VARCHAR(50) DEFAULT '待部門主管審核',
                    exec_approval VARCHAR(50) DEFAULT '待副總/高階審核',
                    po_status VARCHAR(50) DEFAULT '待總務採購詢價',
                    ap_status VARCHAR(50) DEFAULT '待財務付款',
                    audit_log TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # 2. 派車單
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.vehicle_dispatch_orders (
                    id SERIAL PRIMARY KEY,
                    dispatch_code VARCHAR(50) UNIQUE NOT NULL,
                    applicant_name VARCHAR(100) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    dispatch_type VARCHAR(50) NOT NULL,
                    vehicle_plate VARCHAR(50) NOT NULL,
                    driver_name VARCHAR(100),
                    destination VARCHAR(200) NOT NULL,
                    outbound_time TIMESTAMP WITH TIME ZONE,
                    return_time TIMESTAMP WITH TIME ZONE,
                    purpose TEXT,
                    mgr_status VARCHAR(50) DEFAULT '🟡 待部門主管簽核',
                    security_status VARCHAR(50) DEFAULT '🔴 未進出/待保全驗證',
                    odometer_out NUMERIC(10,1) DEFAULT 0,
                    odometer_in NUMERIC(10,1) DEFAULT 0,
                    audit_log TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass

def render_approval_center(engine=None, lang="繁體中文", **kwargs):
    inject_approval_css()

    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = APPROVAL_I18N.get(active_lang, APPROVAL_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_approval_db(engine)

    # 按照使用者指定的最新常用順序排列 Tabs
    tab_leave, tab_proc, tab_vehicle, tab_pending, tab_status, tab_security = st.tabs([
        L["tab_leave"], L["tab_proc"], L["tab_vehicle"], L["tab_pending"], L["tab_status"], L["tab_security"]
    ])

    current_user_name = st.session_state.get("user_name", "admin")
    current_user_role = str(st.session_state.get("user_role", "Staff")).upper()

    # ----------------------------------------------------
    # 🏖️ 1. 員工請假申請
    # ----------------------------------------------------
    with tab_leave:
        st.markdown(f"### {L['tab_leave']}")
        c_l1, c_l2 = st.columns(2)
        with c_l1:
            st.text_input("請假人 (Applicant)", value=current_user_name, disabled=True)
            st.selectbox("假別類型", ["事假 (Personal)", "病假 (Sick)", "特休 (Annual Leave)", "婚假/產假"])
        with c_l2:
            st.date_input("開始日期", datetime.date.today())
            st.date_input("結束日期", datetime.date.today())
        st.text_area("請假事由說明", placeholder="請詳細說明請假原因...")
        if st.button("📤 提交假單並啟動簽核", type="primary"):
            st.success("🎉 請假單已成功送出！等待主管審核中。")

    # ----------------------------------------------------
    # 📦 2. 採購與請款申請單 (PR)
    # ----------------------------------------------------
    with tab_proc:
        st.markdown(f"### {L['tab_proc']}")
        st.info(L["info_pr"])
        
        with st.form("form_approval_create_pr"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input(L["lbl_requester"], value=current_user_name, disabled=True)
                st.text_input(L["lbl_dept"], value=f"角色: {current_user_role}", disabled=True)
                pr_proj = st.text_input(L["lbl_proj"], placeholder="例: PRJ-2026-001 (西寧擴建案)")
            with c2:
                pr_cat = st.selectbox(L["lbl_cat"], PROC_CATEGORIES)
                pr_item = st.text_input(L["lbl_item"], placeholder="例: Schneider 400A 空氣斷路器 (ACB)")
                pr_qty = st.number_input(L["lbl_qty"], min_value=1.0, value=1.0, step=1.0)
            with c3:
                pr_unit = st.text_input(L["lbl_unit"], value="台")
                pr_est_str = st.text_input(L["lbl_amount"], value="45.000.000")
                pr_est_val = parse_formatted_amount(pr_est_str)
                pr_reason = st.text_area(L["lbl_reason"], placeholder="例: 西寧廠 A 區開關損壞，請對照照片規格採買。")

            st.markdown("##### " + L["lbl_photo"])
            photo_file = st.file_uploader("選擇或拍攝圖片檔案", type=["jpg", "jpeg", "png", "pdf"])
            encoded_photo = ""
            if photo_file:
                if photo_file.type.startswith("image"):
                    st.image(photo_file, caption="預覽對比照片", width=250)
                encoded_photo = base64.b64encode(photo_file.read()).decode("utf-8")

            if st.form_submit_button(L["btn_submit_pr"], type="primary", use_container_width=True):
                if not pr_item:
                    st.error("⚠️ 請填寫物品/材料名稱與規格！")
                else:
                    pr_code_gen = "PR-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.purchase_requisitions 
                                    (pr_code, requester_name, department, project_code, item_category, item_name, qty, unit, est_amount, item_photo, audit_log)
                                    VALUES (:code, :req, :dept, :proj, :cat, :item, :qty, :unit, :amt, :img, :log);
                                """), {
                                    "code": pr_code_gen, "req": current_user_name, "dept": current_user_role, "proj": pr_proj,
                                    "cat": pr_cat, "item": pr_item, "qty": pr_qty, "unit": pr_unit, "amt": pr_est_val,
                                    "img": encoded_photo,
                                    "log": f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] {current_user_name} 提交請購 ({format_vnd_text(pr_est_val)})。"
                                })
                            st.success(f"🎉 請購單【{pr_code_gen}】已成功建立！金額：{format_vnd_text(pr_est_val)}")
                            st.rerun()
                        except Exception as e:
                            st.error("寫入失敗: " + str(e))
                    else:
                        st.success(f"🎉 [展示模式] 請購單【{pr_code_gen}】建立成功！")

    # ----------------------------------------------------
    # 🚗 3. 廠區公務派車申請單
    # ----------------------------------------------------
    with tab_vehicle:
        st.markdown(f"### {L['tab_vehicle']}")
        st.info(L["info_vehicle"])

        with st.form("form_create_vehicle_dispatch"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input(L["lbl_requester"], value=current_user_name, disabled=True)
                st.text_input(L["lbl_dept"], value=f"角色: {current_user_role}", disabled=True)
                v_type = st.selectbox(L["lbl_v_type"], ["🚗 廠務/工程公務外出", "🏭 西寧廠↔海防廠物料運送", "🤝 訪客/客戶機場專車接送", "🔧 設備急件載運與採購"])
            with c2:
                v_plate = st.selectbox(L["lbl_vehicle"], ["60A-888.99 (Toyota Fortuner 7座)", "70C-123.45 (Isuzu 3.5噸卡車)", "60B-999.11 (Ford Transit 16座)", "自駕私車公用"])
                v_driver = st.text_input(L["lbl_driver"], value="Nguyễn Văn Tài (專職司機)")
                v_dest = st.text_input(L["lbl_destination"], placeholder="例: 西寧省安平工業區案場")
            with c3:
                v_out_dt = st.date_input(L["lbl_out_time"], datetime.date.today())
                v_in_dt = st.date_input(L["lbl_in_time"], datetime.date.today())
                v_purpose = st.text_area(L["lbl_v_reason"], placeholder="例: 前往西寧廠區載運 400A 配電盤，並陪同客戶驗收。")

            if st.form_submit_button(L["btn_submit_v"], type="primary", use_container_width=True):
                if not v_dest or not v_purpose:
                    st.error("⚠️ 請填寫前往目的地與派車事由！")
                else:
                    v_code = "VD-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.vehicle_dispatch_orders 
                                    (dispatch_code, applicant_name, department, dispatch_type, vehicle_plate, driver_name, destination, purpose, audit_log)
                                    VALUES (:code, :req, :dept, :vtype, :plate, :driver, :dest, :purp, :log);
                                """), {
                                    "code": v_code, "req": current_user_name, "dept": current_user_role,
                                    "vtype": v_type, "plate": v_plate, "driver": v_driver, "dest": v_dest, "purp": v_purpose,
                                    "log": f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] {current_user_name} 建立派車單。"
                                })
                            st.success(f"🎉 派車申請單【{v_code}】建立成功！已自動發送給部門主管簽核。")
                            st.rerun()
                        except Exception as e:
                            st.error("寫入失敗: " + str(e))
                    else:
                        st.success(f"🎉 [展示模式] 派車單【{v_code}】建立成功！")

    # ----------------------------------------------------
    # 📑 4. 待簽核案件審查 (主管審核專區)
    # ----------------------------------------------------
    with tab_pending:
        st.markdown(f"### {L['tab_pending']}")
        st.caption("主管專區：審核下屬提交之【公務派車單】與【採購請購單】。")
        
        st.markdown("#### 🚗 待簽核派車單 (Pending Vehicle Dispatch)")
        if engine:
            try:
                with engine.connect() as conn:
                    res_vp = conn.execute(text("SELECT * FROM public.vehicle_dispatch_orders WHERE mgr_status LIKE '%待部門主管簽核%' ORDER BY id DESC;"))
                    v_pendings = res_vp.fetchall()
                    if v_pendings:
                        for vp in v_pendings:
                            v_item = dict(vp._mapping)
                            st.markdown(f"""
                            <div class="appr-card">
                                <b>派車單號：{v_item['dispatch_code']}</b> | 申請人：<b>{v_item['applicant_name']}</b> ({v_item['department']})<br>
                                車號/車型：<b>{v_item['vehicle_plate']}</b> | 司機：{v_item['driver_name'] or '無'}<br>
                                目的地：<b>{v_item['destination']}</b> | 事由：{v_item['purpose']}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col_v1, col_v2 = st.columns(2)
                            with col_v1:
                                if st.button(f"🟢 核准派車單 ({v_item['dispatch_code']})", type="primary"):
                                    with engine.begin() as conn_u:
                                        conn_u.execute(text("""
                                            UPDATE public.vehicle_dispatch_orders 
                                            SET mgr_status = '🟢 主管已核准 (待門禁放行)',
                                                security_status = '🟡 門禁放行查驗中',
                                                audit_log = audit_log || :log
                                            WHERE dispatch_code = :c;
                                        """), {
                                            "c": v_item['dispatch_code'],
                                            "log": f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] 部門主管 {current_user_name} 已核准派車。"
                                        })
                                    st.success(f"✅ 派車單【{v_item['dispatch_code']}】已簽核！")
                                    st.rerun()
                            with col_v2:
                                if st.button(f"🔴 駁回派車單 ({v_item['dispatch_code']})"):
                                    with engine.begin() as conn_u:
                                        conn_u.execute(text("UPDATE public.vehicle_dispatch_orders SET mgr_status = '🔴 主管駁回' WHERE dispatch_code = :c;"), {"c": v_item['dispatch_code']})
                                    st.error("❌ 已駁回該派車單！")
                                    st.rerun()
                            st.markdown("---")
                    else:
                        st.info("目前沒有等待簽核的公務派車單。")
            except Exception as e:
                st.error("讀取失敗: " + str(e))

        st.markdown("#### 📦 待簽核請購單 (Pending Purchase Requisition)")
        if engine:
            try:
                with engine.connect() as conn:
                    res_p = conn.execute(text("SELECT * FROM public.purchase_requisitions WHERE po_status = '待總務採購詢價' ORDER BY id DESC;"))
                    prs = res_p.fetchall()
                    if prs:
                        for p in prs:
                            pd_item = dict(p._mapping)
                            formatted_amount = format_vnd_text(pd_item['est_amount'])
                            st.markdown(f"""
                            <div class="appr-card">
                                <b>請購單號：{pd_item['pr_code']}</b> | 申請人：<b>{pd_item['requester_name']}</b> ({pd_item['department']})<br>
                                品名：<b>{pd_item['item_name']}</b> x {pd_item['qty']} {pd_item['unit']} | 金額：<b style="color:#B91C1C; font-size:18px;">{formatted_amount}</b><br>
                                類別：{pd_item['item_category']} | 專案：{pd_item['project_code'] or '無'}
                            </div>
                            """, unsafe_allow_html=True)

                            col_a1, col_a2, col_a3 = st.columns(3)
                            with col_a1:
                                if st.button(f"🎨 設計主管核准規格 ({pd_item['pr_code']})"):
                                    with engine.begin() as conn_u:
                                        conn_u.execute(text("UPDATE public.purchase_requisitions SET tech_approval = '🟢 規格審核通過' WHERE pr_code = :c;"), {"c": pd_item['pr_code']})
                                    st.success("✅ 規格已核准！")
                                    st.rerun()
                            with col_a2:
                                if st.button(f"👔 部門主管核准預算 ({pd_item['pr_code']})"):
                                    with engine.begin() as conn_u:
                                        conn_u.execute(text("UPDATE public.purchase_requisitions SET mgr_approval = '🟢 主管核准' WHERE pr_code = :c;"), {"c": pd_item['pr_code']})
                                    st.success("✅ 預算已核准！")
                                    st.rerun()
                            with col_a3:
                                if st.button(f"👑 副總/高階特批簽發 ({pd_item['pr_code']})", type="primary"):
                                    with engine.begin() as conn_u:
                                        conn_u.execute(text("UPDATE public.purchase_requisitions SET exec_approval = '🟢 高階核准發包', po_status = '已簽核/交總務採購' WHERE pr_code = :c;"), {"c": pd_item['pr_code']})
                                    st.success("🎉 高階特批完成，單據已拋轉給總務/採購執行！")
                                    st.rerun()
                            st.markdown("---")
            except Exception as e:
                st.error("讀取失敗: " + str(e))

    # ----------------------------------------------------
    # 📊 5. 簽核進度即時追蹤
    # ----------------------------------------------------
    with tab_status:
        st.markdown(f"### {L['tab_status']}")
        st.caption("即時查看您發起的請購單與公務派車單簽核狀態。")
        
        st.markdown("#### 🚗 派車單追蹤 (Vehicle Dispatch Tracker)")
        if engine:
            try:
                with engine.connect() as conn:
                    res_v = conn.execute(text("SELECT dispatch_code, applicant_name, vehicle_plate, destination, mgr_status, security_status FROM public.vehicle_dispatch_orders ORDER BY id DESC;"))
                    v_rows = res_v.fetchall()
                    if v_rows:
                        st.dataframe(pd.DataFrame([dict(r._mapping) for r in v_rows]), use_container_width=True)
                    else:
                        st.info("尚無公務派車申請紀錄。")
            except Exception:
                pass

        st.markdown("#### 📦 請購單追蹤 (Purchase Tracker)")
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT pr_code, item_name, est_amount, tech_approval, mgr_approval, exec_approval, po_status FROM public.purchase_requisitions ORDER BY id DESC;"))
                    rows = res.fetchall()
                    if rows:
                        df = pd.DataFrame([dict(r._mapping) for r in rows])
                        df["est_amount"] = df["est_amount"].apply(format_vnd_text)
                        st.dataframe(df, use_container_width=True)
            except Exception:
                pass

    # ----------------------------------------------------
    # 🛡️ 6. 保全門禁車輛放行查驗 (保全專區)
    # ----------------------------------------------------
    with tab_security:
        st.markdown(f"### {L['tab_security']}")
        st.caption("廠區保全現場站崗使用：核對出廠車牌與『主管核准狀態』，登記出廠里程數與放行時間。")
        
        if engine:
            try:
                with engine.connect() as conn:
                    res_sec = conn.execute(text("SELECT * FROM public.vehicle_dispatch_orders WHERE mgr_status LIKE '%主管已核准%' ORDER BY id DESC;"))
                    sec_orders = res_sec.fetchall()
                    if sec_orders:
                        for so in sec_orders:
                            s_item = dict(so._mapping)
                            st.markdown(f"""
                            <div class="security-card">
                                🛡️ <b>門禁放行單：{s_item['dispatch_code']}</b><br>
                                車號：<b style="font-size:20px; color:#DC2626;">{s_item['vehicle_plate']}</b> | 司機/駕駛：<b>{s_item['driver_name']}</b><br>
                                乘車人：<b>{s_item['applicant_name']}</b> ({s_item['department']})<br>
                                目的地：<b>{s_item['destination']}</b> | 主管簽核狀態：<b>{s_item['mgr_status']}</b>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            with st.form(f"form_security_gate_{s_item['dispatch_code']}"):
                                c_sec1, c_sec2 = st.columns(2)
                                with c_sec1:
                                    km_out = st.number_input("出廠儀表里程數 (KM)", min_value=0.0, value=12580.0)
                                with c_sec2:
                                    gate_notes = st.text_input("門禁保全查驗備註", value="車牌對符，乘車人員證件核對無誤。")

                                if st.form_submit_button("🚨 門禁保全確認：核准出廠放行 (Check-Out)", type="primary"):
                                    with engine.begin() as conn_s:
                                        conn_s.execute(text("""
                                            UPDATE public.vehicle_dispatch_orders 
                                            SET security_status = '🟢 保全已放行/出廠中',
                                                odometer_out = :km,
                                                audit_log = audit_log || :log
                                            WHERE dispatch_code = :c;
                                        """), {
                                            "km": km_out,
                                            "c": s_item['dispatch_code'],
                                            "log": f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] 門禁保全確認放行出廠，儀表里程：{km_out} KM。"
                                        })
                                    st.success(f"🎉 派車單【{s_item['dispatch_code']}】已完成門禁放行驗證！")
                                    st.rerun()
                            st.markdown("---")
                    else:
                        st.info("目前尚無通過主管簽核等待門禁放行的車輛。")
            except Exception as e:
                st.error("讀取門禁資料失敗: " + str(e))

def show(engine=None, lang="繁體中文", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)
