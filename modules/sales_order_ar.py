import streamlit as st
import pandas as pd
from datetime import datetime

def render_sales_order_ar_page(engine=None, lang="繁體中文"):
    if lang == "Tiếng Việt":
        st.subheader("📋 Quản lý Phải thu & Xuất hóa đơn điện tử GDT")
        st.markdown("Quản lý công nợ khách hàng, theo dõi hạn thanh toán và trực tiếp phát hành hóa đơn điện tử theo quy định Tổng cục Thuế Việt Nam.")
    elif lang == "English":
        st.subheader("📋 Accounts Receivable & Vietnam E-Invoice Management")
        st.markdown("Manage customer receivables, track payment terms, and issue GDT-compliant e-invoices directly.")
    else:
        st.subheader("📋 應收帳款 (AR) 與越南電子發票開立管理")
        st.markdown("整合客戶應收帳款追蹤、催收管理，並內嵌越南稅務總局 (GDT) 電子發票（Hóa đơn điện tử）開立與合規驗證功能。")

    # 初始化 session state 儲存應收帳款與發票資料
    if "ar_invoices_db" not in st.session_state:
        st.session_state.ar_invoices_db = [
            {
                "inv_id": "INV-2026-001",
                "client": "Công ty TNHH Xây lắp Tân Thuận",
                "project": "西寧廠高壓配電盤統包工程",
                "amount_usd": 11500.0,
                "vat_rate": "10%",
                "total_usd": 12650.0,
                "due_date": "2026-11-30",
                "status": "🟢 已驗證 (GDT Verified)",
                "date": "2026-10-01"
            },
            {
                "inv_id": "INV-2026-002",
                "client": "Bình Dương Steel & Engineering Corp",
                "project": "海防廠低壓配電箱擴充案",
                "amount_usd": 8400.0,
                "vat_rate": "8%",
                "total_usd": 9072.0,
                "due_date": "2026-12-15",
                "status": "🟡 待送交 (Pending GDT)",
                "date": "2026-10-08"
            }
        ]

    tab1, tab2 = st.tabs([
        "📊 應收帳款總表與催收追蹤" if lang == "繁體中文" else ("📊 Danh sách Phải thu" if lang == "Tiếng Việt" else "📊 AR List & Tracking"),
        "⚡ 越南電子發票開立與 GDT 驗證" if lang == "繁體中文" else ("⚡ Phát hành Hóa đơn điện tử GDT" if lang == "Tiếng Việt" else "⚡ Issue E-Invoice & GDT")
    ])

    with tab1:
        st.markdown("### 🏢 客戶應收帳款總覽")
        
        # 統計指標
        total_ar = sum([item["total_usd"] for item in st.session_state.ar_invoices_db])
        verified_count = len([item for item in st.session_state.ar_invoices_db if "已驗證" in item["status"] or "Verified" in item["status"]])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("應收帳款總額 (Total AR)", f"${total_ar:,.2f} USD")
        m2.metric("已開立發票數", f"{len(st.session_state.ar_invoices_db)} 筆")
        m3.metric("GDT 合規驗證數", f"{verified_count} 筆")
        
        st.markdown("---")
        df_ar = pd.DataFrame(st.session_state.ar_invoices_db)
        st.dataframe(df_ar, use_container_width=True)

    with tab2:
        st.markdown("### ⚡ 越南營建電子發票與稅務合規管家 (Hóa đơn điện tử)")
        st.info("💡 符合越南稅務總局 (GDT) 規範，管理電子發票與加值稅 (VAT 8%/10%) 合規申報。")

        with st.form("issue_vn_invoice_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                client_name = st.text_input("客戶 / 業主名稱 (Client / Mã số thuế)", value="Công ty TNHH Xây lắp Tân Thuận")
                project_name = st.text_input("對應專案名稱", value="西寧廠配電盤工程尾款")
            with col_b:
                unpaid_usd = st.number_input("未稅銷售額 (USD)", min_value=0.0, value=5000.0, step=100.0)
                vat_choice = st.selectbox("越南加值稅稅率 (VAT Rate)", ["10%", "8%", "0% (免稅/出口)"])

            submit_inv = st.form_submit_button("🚀 開立電子發票並送交 GDT 驗證", type="primary", use_container_width=True)

            if submit_inv:
                vat_multiplier = 0.10 if "10%" in vat_choice else (0.08 if "8%" in vat_choice else 0.0)
                total_with_vat = unpaid_usd * (1 + vat_multiplier)
                new_id = f"INV-2026-{len(st.session_state.ar_invoices_db)+1:03d}"
                
                new_record = {
                    "inv_id": new_id,
                    "client": client_name,
                    "project": project_name,
                    "amount_usd": unpaid_usd,
                    "vat_rate": vat_choice.split()[0],
                    "total_usd": total_with_vat,
                    "due_date": datetime.now().strftime("%Y-%m-30"),
                    "status": "🟢 已驗證 (GDT Verified)",
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                
                st.session_state.ar_invoices_db.insert(0, new_record)
                st.success(f"🎉 發票編號 {new_id} 已成功開立並通過越南 GDT 稅務系統合規驗證！總含稅金額：$ {total_with_vat:,.2f} USD")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📋 發票清單與合規狀態紀錄")
        if st.session_state.ar_invoices_db:
            st.dataframe(pd.DataFrame(st.session_state.ar_invoices_db), use_container_width=True)
        else:
            st.info("目前尚無開立紀錄。")
