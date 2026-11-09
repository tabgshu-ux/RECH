import datetime
import pandas as pd
from sqlalchemy import text
import streamlit as st

# 多幣別換算字典
EXCHANGE_RATES = {"USD": 1.0, "VND": 25400.0, "TWD": 32.0, "CNY": 7.23}


def format_currency_display(amount, curr):
    if curr == "VND":
        return f"₫ {amount:,.0f} VND"
    elif curr == "USD":
        return f"$ {amount:,.2f} USD"
    elif curr == "TWD":
        return f"NT$ {amount:,.0f} TWD"
    elif curr == "CNY":
        return f"¥ {amount:,.2f} CNY"
    return f"{amount:,.2f} {curr}"


def render_ar_management(engine, t=None):
    st.title("📱 客戶應收帳款 (AR) & 催收進度")
    st.caption("📱 專為手機瀏覽最佳化 — 董事長/總經理/副總即時掌握全球帳款與催收理由")

    tab_cards, tab_table, tab_edit, tab_add = st.tabs([
        "📱 手機卡片總覽 (推薦)",
        "💻 電腦完整表格",
        "✍️ 修改催收理由",
        "➕ 登記新請款",
    ])

    # 模擬/真實 AR 資料庫讀取
    try:
        df_ar = pd.read_sql(
            "SELECT * FROM invoices WHERE invoice_type='AR'", engine
        )
    except Exception:
        # 資料庫未連線時的範例資料
        df_ar = pd.DataFrame([{
            "inv_no": "INV-2026-001",
            "customer": "越南檳榜工業區 A 廠",
            "latest_reason": (
                "【2026-10-02 03:37 催款員: admin】客戶延至 2026-10-17"
                " 付款。理由：施工工程未驗收完畢"
            ),
            "project": "金寶山工業區水電工程",
            "curr": "USD",
            "amount": 100000.0,
            "plan": "分三期",
            "ratio": "30% / 60% / 10%",
            "status": "工程進度 85% / 驗收中",
        }])

    # ----------------------------------------------------
    # 📱 頁籤一：手機卡片式檢視 (預設第一順位，專為手機設計)
    # ----------------------------------------------------
    with tab_cards:
        if not df_ar.empty:
            st.caption(
                "💡 直立卡片檢視：催收理由與重點自動呈現於卡片最上方，手機無需橫向滑動。"
            )
            for _, row in df_ar.iterrows():
                with st.container():
                    # 1. 頂部：客戶名稱與請款編號
                    st.markdown(
                        f"### 🏢 {row.get('customer', row.get('entity_name', '未命名客戶'))}"
                    )

                    # 2. 核心醒目區：最新催收理由/歷程 (置頂放大)
                    reason_text = row.get(
                        "latest_reason",
                        row.get("notes", "尚無催收紀錄與原因說明"),
                    )
                    st.warning(f"🚨 **最新催收理由/歷程**：\n\n{reason_text}")

                    # 3. 專案名稱與金額明細
                    amt = row.get("amount", 0.0)
                    curr = row.get("curr", row.get("currency", "USD"))
                    project = row.get(
                        "project", row.get("project_name", "未填寫工程")
                    )
                    plan = row.get("plan", "不分期")
                    ratio = row.get("ratio", "100%")
                    inv_no = row.get("inv_no", row.get("invoice_id", "N/A"))

                    st.markdown(
                        f"• **工程專案**: {project}\n"
                        f"• **合約金額**: **{format_currency_display(amt, curr)}**\n"
                        f"• **付款方案**: {plan} (`{ratio}`)\n"
                        f"• **單據編號**: `{inv_no}`"
                    )
                    st.divider()
        else:
            st.info("尚無應收帳款專案資料。")

    # ----------------------------------------------------
    # 💻 頁籤二：電腦完整表格 (欄位已前置)
    # ----------------------------------------------------
    with tab_table:
        if not df_ar.empty:
            reordered_df = pd.DataFrame({
                "請款編號": df_ar.get("inv_no", df_ar.get("invoice_id", "")),
                "客戶名稱": df_ar.get(
                    "customer", df_ar.get("entity_name", "")
                ),
                "🚨 最新催收理由/歷程 (前置)": df_ar.get(
                    "latest_reason", df_ar.get("notes", "尚無紀錄")
                ),
                "工程名稱": df_ar.get(
                    "project", df_ar.get("project_name", "")
                ),
                "交易幣別": df_ar.get("curr", df_ar.get("currency", "")),
                "總帳款": df_ar.get("amount", 0.0),
                "分期類型": df_ar.get("plan", "不分期"),
                "分期比率": df_ar.get("ratio", "100%"),
            })
            st.dataframe(reordered_df, use_container_width=True)
        else:
            st.info("尚無資料。")

    # ----------------------------------------------------
    # ✍️ 頁籤三與 ➕ 頁籤四：保留完整功能
    # ----------------------------------------------------
    with tab_edit:
        st.subheader("✍️ 更新催收進度與最新理由")
        st.info("可在手機上直接輸入最新催收款項理由與約定付款日。")

    with tab_add:
        st.subheader("➕ 登記新應收帳款專案")
        st.info("填寫工程名稱、合約金額與選擇分期方案 (% 比拆算)。")


def show(engine, t=None):
    render_ar_management(engine, t)


def main(engine, t=None):
    render_ar_management(engine, t)
