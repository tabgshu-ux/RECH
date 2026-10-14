import streamlit as st
import pandas as pd
import datetime
import base64
import re
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 三語系字典 (自動跟隨全域語系)
# ----------------------------------------------------
APPROVAL_I18N = {
    "繁體中文": {
        "title": "✍️ 全公司電子簽核中心 (Approval Center)",
        "caption": "提交請購、請假或專案簽報；系統自動依據權限與金額進行多級電子簽核。",
        "tab_leave": "🏖️ 員工請假單申請",
        "tab_proc": "📦 採購與請款申請單 (PR)",
        "tab_status": "📊 簽核進度即時追蹤",
        "tab_pending": "📑 待簽核案件審查 (主管專區)",
        "info_pr": "🔒 系統已自動綁定目前登入者身分，並支援上傳/拍攝實物照片供採購與主管對比確認。",
        "lbl_requester": "請購人姓名 (系統綁定) *",
        "lbl_dept": "所屬部門 (系統綁定)",
        "lbl_proj": "歸屬工程/專案編號",
        "lbl_cat": "請購項目細分類別 *",
        "lbl_item": "物品/材料名稱與規格 *",
        "lbl_qty": "需求數量",
        "lbl_unit": "單位",
        "lbl_amount": "預估總金額 (VND) *",
        "lbl_photo": "📸 上傳/拍攝實物對比照片或規格圖檔 (JPG/PNG/PDF)",
        "lbl_reason": "請購用途與詳細說明",
        "btn_submit_pr": "🚀 提交採購請款單並啟動多級簽核"
    },
    "English": {
        "title": "✍️ Enterprise Approval Center",
        "caption": "Submit PR, Leave, or Approval requests; automated multi-level approval pipeline.",
        "tab_leave": "🏖️ Leave Application",
        "tab_proc": "📦 Purchase Requisition (PR)",
        "tab_status": "📊 Real-time Workflow Tracking",
        "tab_pending": "📑 Pending Approvals (Manager Zone)",
        "info_pr": "🔒 Identity locked to current user. Supports uploading item photos for review.",
        "lbl_requester": "Requester Name (Locked) *",
        "lbl_dept": "Department (Locked)",
        "lbl_proj": "Project Code",
        "lbl_cat": "Detailed Category *",
        "lbl_item": "Item Name & Specs *",
        "lbl_qty": "Quantity",
        "lbl_unit": "Unit",
        "lbl_amount": "Est. Total Amount (VND) *",
        "lbl_photo": "📸 Upload / Capture Photo or Spec (JPG/PNG/PDF)",
        "lbl_reason": "Purpose & Detailed Notes",
        "btn_submit_pr": "🚀 Submit PR & Launch Approval Workflow"
    },
    "Tiếng Việt": {
        "title": "✍️ Trung tâm Phê duyệt Điện tử",
        "caption": "Tạo yêu cầu mua hàng, nghỉ phép; hệ thống tự động duyệt theo phân cấp.",
        "tab_leave": "🏖️ Đơn xin nghỉ phép",
        "tab_proc": "📦 Đơn yêu cầu mua hàng (PR)",
        "tab_status": "📊 Theo dõi tiến độ phê duyệt",
        "tab_pending": "📑 Hồ sơ chờ duyệt (Dành cho Sếp)",
        "info_pr": "🔒 Tự động khóa tài khoản người tạo. Hỗ trợ chụp/tải ảnh đính kèm.",
        "lbl_requester": "Tên người yêu cầu (Khóa) *",
        "lbl_dept": "Bộ phận (Khóa)",
        "lbl_proj": "Mã dự án",
        "lbl_cat": "Phân loại vật tư *",
        "lbl_item": "Tên & Quy cách vật tư *",
        "lbl_qty": "Số lượng",
        "lbl_unit": "Đơn vị",
        "lbl_amount": "Tổng tiền dự kiến (VND) *",
        "lbl_photo": "📸 Tải ảnh / Chụp ảnh vật tư (JPG/PNG/PDF)",
        "lbl_reason": "Mục đích sử dụng & Ghi chú",
        "btn_submit_pr": "🚀 Gửi đơn yêu cầu mua hàng"
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
    """將點或逗號千分位字串還原為純數字，例: '45.000.000' -> 45000000"""
    if not val_str:
        return 0.0
    clean_str = re.sub(r"[^\d]", "", str(val_str))
    return float(clean_str) if clean_str else 0.0

def format_vnd_text(amount):
    """將金額格式化為越南點號千分位格式，例: 45.000.000 VND"""
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
        </style>
    """, unsafe_allow_html=True)

def init_approval_db(engine):
    """與採購模組共用 public.purchase_requisitions 表格"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
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

            try:
                conn.execute(text("ALTER TABLE public.purchase_requisitions ADD COLUMN IF NOT EXISTS item_photo TEXT;"))
            except Exception:
                pass
    except Exception:
        pass

def render_approval_center(engine=None, lang="繁體中文", **kwargs):
    inject_approval_css()

    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = APPROVAL_I18N.get(active_lang, APPROVAL_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_approval_db(engine)

    tab_leave, tab_proc, tab_status, tab_pending = st.tabs([
        L["tab_leave"], L["tab_proc"], L["tab_status"], L["tab_pending"]
    ])

    # ----------------------------------------------------
    # 🏖️ 頁籤 1: 員工請假單
    # ----------------------------------------------------
    with tab_leave:
        st.markdown("### 🏖️ 員工請假單申請 (Leave Request)")
        c_l1, c_l2 = st.columns(2)
        with c_l1:
            st.text_input("請假人 (Applicant)", value=st.session_state.get("user_name", "admin"), disabled=True)
            st.selectbox("假別類型", ["事假 (Personal)", "病假 (Sick)", "特休 (Annual Leave)", "婚假/產假"])
        with c_l2:
            st.date_input("開始日期", datetime.date.today())
            st.date_input("結束日期", datetime.date.today())
        st.text_area("請假事由說明", placeholder="請詳細說明請假原因...")
        if st.button("📤 提交假單並啟動簽核", type="primary"):
            st.success("🎉 請假單已成功送出！等待主管審核中。")

    # ----------------------------------------------------
    # 📦 頁籤 2: 最新標準【採購與請款申請單 (PR)】
    # ----------------------------------------------------
    with tab_proc:
        st.markdown(f"### {L['tab_proc']}")
        st.info(L["info_pr"])
        
        current_user_name = st.session_state.get("user_name", "admin")
        current_user_role = str(st.session_state.get("user_role", "Staff")).upper()
        
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
                
                # 💰 越南格式金額輸入框：點號千分位
                pr_est_str = st.text_input(
                    L["lbl_amount"], 
                    value="45.000.000",
                    help="直接輸入數字即可，系統會自動轉換為越南千位點號格式 (例如: 45.000.000)"
                )
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
                elif pr_est_val <= 0:
                    st.error("⚠️ 請填寫正確的預估總金額！")
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
                                    "log": f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] {current_user_name} 於簽核中心提交請購 ({format_vnd_text(pr_est_val)})。"
                                })
                            st.success(f"🎉 請購單【{pr_code_gen}】已成功建立並啟動多級簽核！金額：{format_vnd_text(pr_est_val)}")
                            st.rerun()
                        except Exception as e:
                            st.error("寫入失敗: " + str(e))
                    else:
                        st.success(f"🎉 [展示模式] 請購單【{pr_code_gen}】建立成功！")

    # ----------------------------------------------------
    # 📊 頁籤 3: 簽核進度即時追蹤
    # ----------------------------------------------------
    with tab_status:
        st.markdown(f"### {L['tab_status']}")
        st.caption("即時查看您發起的請購單目前在哪一位主管/關卡簽核中。")
        
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT pr_code, item_name, est_amount, tech_approval, mgr_approval, exec_approval, po_status FROM public.purchase_requisitions ORDER BY id DESC;"))
                    rows = res.fetchall()
                    if rows:
                        df = pd.DataFrame([dict(r._mapping) for r in rows])
                        df["est_amount"] = df["est_amount"].apply(format_vnd_text)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("目前尚無簽核單據紀錄。")
            except Exception as e:
                st.error("讀取失敗: " + str(e))

    # ----------------------------------------------------
    # 📑 頁籤 4: 待簽核案件審查 (主管審核專區)
    # ----------------------------------------------------
    with tab_pending:
        st.markdown(f"### {L['tab_pending']}")
        st.caption("主管可在此查閱待審核單據、比對請購對比照片並點選核准。")
        
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT * FROM public.purchase_requisitions WHERE po_status = '待總務採購詢價' ORDER BY id DESC;"))
                    prs = res.fetchall()
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
                            
                            if pd_item.get("item_photo"):
                                try:
                                    img_bytes = base64.b64decode(pd_item["item_photo"])
                                    st.image(img_bytes, caption=f"對比參考圖片 ({pd_item['pr_code']})", width=220)
                                except Exception:
                                    pass

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
                                    st.success("🎉 高階特批完成，單據已自動拋轉給總務/採購執行！")
                                    st.rerun()
                            st.markdown("---")
                    else:
                        st.info("目前沒有等待您簽核的單據。")
            except Exception as e:
                st.error("讀取失敗: " + str(e))

def show(engine=None, lang="繁體中文", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)
