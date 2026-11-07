import streamlit as st
import pandas as pd
import datetime

def render_bom_procurement_page(engine=None, lang="繁體中文", **kwargs):
    texts = {
        "繁體中文": {
            "title": "🔌 配電盤 BOM 零件自動展開與採購/庫存連動中心",
            "caption": "當工程報價經董事長/總經理拍板後，自動展開 BOM 物料清單、比對倉庫庫存，並自動生成採購請購單。",
            "tab1": "📦 已拍板專案 BOM 物料展開與庫存對比",
            "tab2": "🛒 自動生成採購請購單 (PR 審核佇列)",
            "tab3": "➕ 新增專案 BOM 需求與單位設定"
        },
        "Tiếng Việt": {
            "title": "🔌 Tự động bóc tách BOM tủ điện & Liên kết Kho / Mua hàng",
            "caption": "Tự động tạo BOM, kiểm tra tồn kho và lập đơn mua hàng (PR) sau khi báo giá được phê duyệt.",
            "tab1": "📦 Bóc tách BOM & Đối soát tồn kho",
            "tab2": "🛒 Tự động tạo Đơn mua hàng (PR)",
            "tab3": "➕ Thêm nhu cầu BOM dự án & Đơn vị tính"
        },
        "English": {
            "title": "🔌 Panel BOM Auto-Explosion & Procurement Integration",
            "caption": "Automatically explodes BOM, checks warehouse stock, and generates Purchase Requisitions (PR) upon approval.",
            "tab1": "📦 Approved Project BOM & Stock Check",
            "tab2": "🛒 Auto-Generated Purchase Requisitions (PR)",
            "tab3": "➕ Add Project BOM & Unit Setup"
        }
    }

    active_lang = lang if lang in texts else "繁體中文"
    t = texts[active_lang]

    st.title(t["title"])
    st.caption(t["caption"])

    # 初始化 BOM 與採購資料庫 (支援單位與小數點數量)
    if "bom_procurement_db" not in st.session_state:
        st.session_state.bom_procurement_db = [
            {
                "quot_id": "QT-2026-001",
                "project_name": "西寧廠主配電盤 2000A 統包工程",
                "client": "Công ty TNHH Xây lắp Tân Thuận",
                "bom_items": [
                    {"part_code": "PART-CAB-2000", "part_name": "2000A 防水不銹鋼機櫃", "unit": "個 (Cái)", "required_qty": 2.0, "stock_qty": 0.0, "shortage": 2.0, "action": "🔴 需採購 (Procurement Required)"},
                    {"part_code": "PART-BUS-100", "part_name": "銅排 Busbar 10x100mm", "unit": "公尺 (Mét)", "required_qty": 450.5, "stock_qty": 500.0, "shortage": 0.0, "action": "🟢 庫存充足 (Stock Sufficient)"},
                    {"part_code": "PART-WIR-25", "part_name": "控制電纜 2.5mm² (多芯絞線)", "unit": "捆 (Cuộn)", "required_qty": 2.5, "stock_qty": 1.0, "shortage": 1.5, "action": "🔴 需採購 (Procurement Required)"}
                ],
                "status": "🟢 BOM 已展開並生成採購需求"
            }
        ]

    tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

    # ----------------------------------------------------
    # 📦 Tab 1: 已拍板專案 BOM 物料展開與庫存對比
    # ----------------------------------------------------
    with tab1:
        st.markdown("##### 📦 已獲高階主管拍板之專案 BOM 總覽")
        st.info("💡 說明：系統自動抓取已核准的報價單，將訂製機櫃與水電材料展開為詳細 BOM。數量支援小數點（例如：2.5 捆、1.5 公尺），並明確標示單位。")

        if st.session_state.bom_procurement_db:
            for item in st.session_state.bom_procurement_db:
                with st.expander(f"📌 專案單號：{item['quot_id']} | 專案名稱：{item['project_name']} ({item['client']})"):
                    st.write(f"**狀態**：`{item['status']}`")
                    st.markdown("**🔍 BOM 零件需求、單位與倉庫庫存比對表：**")
                    
                    # 呈現帶有單位的清晰表格
                    df_bom = pd.DataFrame(item["bom_items"])
                    df_bom.columns = ["料號", "品名規格", "單位 (Unit)", "需求數量", "現有庫存", "缺口數量", "狀態判定"]
                    st.dataframe(df_bom, use_container_width=True, hide_index=True)

                    if st.button(f"🚀 將缺料項目轉為正式採購請購單 (PR) {item['quot_id']}", key=f"gen_pr_{item['quot_id']}", type="primary"):
                        st.success("✅ 採購請購單（PR）已成功建立並送至採購部！")
        else:
            st.info("目前尚無已拍板且需展開 BOM 的專案。")

    # ----------------------------------------------------
    # 🛒 Tab 2: 自動生成採購請購單 (PR 審核佇列)
    # ----------------------------------------------------
    with tab2:
        st.markdown("##### 🛒 自動化採購請購與預算控管佇列 (PR Queue)")
        st.info("💡 說明：當 BOM 產生缺料時，系統自動轉入此處。採購人員可在此檢視，且系統會自動對比專案預算。")
        
        pr_mock_table = [
            {"PR_No": "PR-2026-001", "專案代號": "PRJ-TN-2026-01", "採購品名": "2000A 防水不銹鋼機櫃 (2 個) & 控制電纜 (2.5 捆)", "預估金額": "$ 15,250 USD", "預算控管": "🟢 在預算範圍內", "審核狀態": "已送出採購"}
        ]
        st.dataframe(pd.DataFrame(pr_mock_table), use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # ➕ Tab 3: 新增專案 BOM 需求與單位設定 (支援 2.5 捆小數點)
    # ----------------------------------------------------
    with tab3:
        st.markdown("##### ➕ 手動新增或調整專案 BOM 物料需求")
        st.info("💡 在這裡您可以直接建立新的 BOM 需求項目，數量支援小數點（如 2.5），並可自由選擇材料單位（捆、個、公尺、式等）。")

        with st.form("form_add_bom_item"):
            c1, c2, c3 = st.columns(3)
            with c1:
                sel_quot = st.text_input("專案報價單號", value="QT-2026-002")
                p_code = st.text_input("材料料號", value="PART-CBL-04")
            with c2:
                p_name = st.text_input("材料名稱與規格", value="XLPE 電力電纜 4x16mm²")
                # 單位選擇下拉選單
                unit_choice = st.selectbox("單位 (Unit)", ["捆 (Cuộn)", "個 (Cái)", "公尺 (Mét)", "條 (Sợi)", "公斤 (Kg)", "式 (Bộ)", "片 (Tấm)"])
            with c3:
                # 數量支援小數點 (step=0.1，允許輸入 2.5 等小數)
                req_qty = st.number_input("需求數量 (支援小數，如 2.5)", min_value=0.1, value=2.5, step=0.1, format="%.2f")
                stock_q = st.number_input("現有倉庫庫存", min_value=0.0, value=1.0, step=0.1, format="%.2f")

            if st.form_submit_button("💾 儲存並加入 BOM 需求清單", type="primary", use_container_width=True):
                shortage_val = max(0.0, req_qty - stock_q)
                action_str = "🔴 需採購 (Procurement Required)" if shortage_val > 0 else "🟢 庫存充足 (Stock Sufficient)"
                
                new_bom_row = {
                    "part_code": p_code,
                    "part_name": p_name,
                    "unit": unit_choice,
                    "required_qty": float(req_qty),
                    "stock_qty": float(stock_q),
                    "shortage": float(shortage_val),
                    "action": action_str
                }

                # 找找看有沒有同單號的專案，若有就直接append進去
                found = False
                for proj in st.session_state.bom_procurement_db:
                    if proj["quot_id"] == sel_quot:
                        proj["bom_items"].append(new_bom_row)
                        found = True
                        break
                
                if not found:
                    st.session_state.bom_procurement_db.append({
                        "quot_id": sel_quot,
                        "project_name": "新建立專案統包工程",
                        "client": "一般客戶",
                        "bom_items": [new_bom_row],
                        "status": "🟢 BOM 已展開"
                    })

                st.success(f"✅ 成功新增 BOM 項目：`{p_name}`，數量 `{req_qty}` `{unit_choice}`！")
                st.rerun()

def show(engine=None, lang="繁體中文", **kwargs):
    render_bom_procurement_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_bom_procurement_page(engine=engine, lang=lang, **kwargs)
