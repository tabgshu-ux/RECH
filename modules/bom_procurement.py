import streamlit as st
import pandas as pd
import datetime

def render_bom_procurement_page(engine=None, lang="繁體中文", **kwargs):
    texts = {
        "繁體中文": {
            "title": "🔌 配電盤 BOM 零件自動展開與採購/庫存連動中心",
            "caption": "當工程報價經董事長/總經理拍板後，自動展開 BOM 物料清單、比對倉庫庫存，並自動生成採購請購單。",
            "tab1": "📦 已拍板專案 BOM 物料展開與庫存對比",
            "tab2": "🛒 自動生成採購請購單 (PR 審核佇列)"
        },
        "Tiếng Việt": {
            "title": "🔌 Tự động bóc tách BOM tủ điện & Liên kết Kho / Mua hàng",
            "caption": "Tự động tạo BOM, kiểm tra tồn kho và lập đơn mua hàng (PR) sau khi báo giá được phê duyệt.",
            "tab1": "📦 Bóc tách BOM & Đối soát tồn kho",
            "tab2": "🛒 Tự động tạo Đơn mua hàng (PR)"
        },
        "English": {
            "title": "🔌 Panel BOM Auto-Explosion & Procurement Integration",
            "caption": "Automatically explodes BOM, checks warehouse stock, and generates Purchase Requisitions (PR) upon approval.",
            "tab1": "📦 Approved Project BOM & Stock Check",
            "tab2": "🛒 Auto-Generated Purchase Requisitions (PR)"
        }
    }

    active_lang = lang if lang in texts else "繁體中文"
    t = texts[active_lang]

    st.title(t["title"])
    st.caption(t["caption"])

    # 初始化 BOM 與採購資料庫
    if "bom_procurement_db" not in st.session_state:
        st.session_state.bom_procurement_db = [
            {
                "quot_id": "QT-2026-001",
                "project_name": "西寧廠主配電盤 2000A 統包工程",
                "client": "Công ty TNHH Xây lắp Tân Thuận",
                "bom_items": [
                    {"part_code": "PART-CAB-2000", "part_name": "2000A 防水不銹鋼機櫃", "required_qty": 2.0, "stock_qty": 0.0, "shortage": 2.0, "action": "🔴 需採購 (Procurement Required)"},
                    {"part_code": "PART-BUS-100", "part_name": "銅排 Busbar 10x100mm", "required_qty": 450.0, "stock_qty": 500.0, "shortage": 0.0, "action": "🟢 庫存充足 (Stock Sufficient)"},
                    {"part_code": "PART-ACB-2000", "part_name": "空氣斷路器 ACB 2000A", "required_qty": 8.0, "stock_qty": 3.0, "shortage": 5.0, "action": "🔴 需採購 (Procurement Required)"}
                ],
                "status": "🟢 BOM 已展開並生成採購需求"
            }
        ]

    tab1, tab2 = st.tabs([t["tab1"], t["tab2"]])

    with tab1:
        st.markdown("##### 📦 已獲高階主管拍板之專案 BOM 總覽")
        st.info("💡 說明：系統會自動抓取已核准的雙層報價單，將其內部的訂製機櫃與水電材料展開為詳細的 BOM 物料清單，並即時比對越南倉庫（西寧/海防）的現有庫存。")

        if st.session_state.bom_procurement_db:
            for item in st.session_state.bom_procurement_db:
                with st.expander(f"📌 專案單號：{item['quot_id']} | 專案名稱：{item['project_name']} ({item['client']})"):
                    st.write(f"**狀態**：`{item['status']}`")
                    st.markdown("**🔍 BOM 零件需求與倉庫庫存比對表：**")
                    st.dataframe(pd.DataFrame(item["bom_items"]), use_container_width=True)

                    if st.button(f"🚀 將缺料項目轉為正式採購請購單 (PR) {item['quot_id']}", key=f"gen_pr_{item['quot_id']}", type="primary"):
                        st.success("✅ 採購請購單（PR）已成功建立並送至採購部！")
        else:
            st.info("目前尚無已拍板且需展開 BOM 的專案。")

    with tab2:
        st.markdown("##### 🛒 自動化採購請購與預算控管佇列 (PR Queue)")
        st.info("💡 說明：當 BOM 產生缺料時，系統自動轉入此處。採購人員可在此檢視，且系統會自動對比專案預算（超過預算自動觸發主管審核）。")
        
        pr_mock_table = [
            {"PR_No": "PR-2026-001", "專案代號": "PRJ-TN-2026-01", "採購品名": "2000A 防水不銹鋼機櫃 (x2) & ACB 2000A (x5)", "預估金額": "$ 15,250 USD", "預算控管": "🟢 在預算範圍內", "審核狀態": "已送出採購"}
        ]
        st.dataframe(pd.DataFrame(pr_mock_table), use_container_width=True)

def show(engine=None, lang="繁體中文", **kwargs):
    render_bom_procurement_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_bom_procurement_page(engine=engine, lang=lang, **kwargs)
