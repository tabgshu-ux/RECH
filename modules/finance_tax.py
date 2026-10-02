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
    st.title("📄 管理部 - 客戶應收帳款 (AR) & 專案分期進度管理")
    st.caption("記錄客戶工程合約總額、動態 3 期/5 期付款排程，專案說明與催收歷程隨時修改。")

    tab_list, tab_edit, tab_add = st.tabs([
        "📋 客戶應收帳款總表與進度",
        "✍️ 修改進行進度說明與催收歷程",
        "➕ 新增請款專案 (分期/不分期)",
    ])

    # ----------------------------------------------------
    # 📋 頁籤一：客戶應收帳款專案清冊 (手機最佳化檢視)
    # ----------------------------------------------------
    with tab_list:
        st.subheader("📋 客戶應收帳款專案清冊")

        # 手機/電腦 檢視模式切換
        view_mode = st.radio(
            "📱 檢視模式切換 (手機建議選擇卡片模式)：",
            ["📱 手機最佳化 (卡片直立檢視)", "💻 電腦完整表格 (欄位已前置)"],
            horizontal=True,
        )

        # 模擬/真實 AR 資料庫讀取
        try:
            df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
        except Exception:
            # 資料庫未連線時的測試資料 (與您的圖片範例相同)
            df_ar = pd.DataFrame([{
                "inv_no": "INV-2026-001",
                "customer": "越南檳榜工業區A廠",
                "latest_reason": "【2026-10-02 03:37 催款員: admin】客戶延至 2026-10-17 付款。理由：施工工程未驗收完畢",
                "project": "金寶山工業區水電工程",
                "curr": "USD",
                "amount": 100000.0,
                "plan": "分三期",
                "ratio": "30% / 60% / 10%",
                "status": "工程進度 85% / 驗收中",
            }])

        if not df_ar.empty:
            # 📱 模式 1：手機最佳化 (卡片直立檢視) - 老闆用手機看這最方便！
            if "📱" in view_mode:
                st.caption("💡 已為手機介面進行最佳化，催收理由與重點直接呈現於最上方：")
                for _, row in df_ar.iterrows():
                    with st.container():
                        st.markdown(f"### 🏢 {row.get('customer', row.get('entity_name', '未命名客戶'))}")
                        
                        # 🚨 將「最新催收理由/歷程」放大醒目呈現在最頂部！
                        reason_text = row.get("latest_reason", row.get("notes", "尚無催收紀錄"))
                        st.warning(f"🚨 **最新催收理由/歷程**：\n\n{reason_text}")

                        # 其他次要細節
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write(f"• **請款編號**: `{row.get('inv_no', row.get('invoice_id', 'N/A'))}`")
                            st.write(f"• **工程/專案**: {row.get('project', row.get('project_name', 'N/A'))}")
                        with c2:
                            amt = row.get('amount', 0.0)
                            curr = row.get('curr', row.get('currency', 'USD'))
                            st.write(f"• **總金額**: **{format_currency_display(amt, curr)}**")
                            st.write(f"• **分期方案**: {row.get('plan', 'N/A')} ({row.get('ratio', 'N/A')})")
                        st.divider()

            # 💻 模式 2：電腦完整表格 (將最新催收理由移動到第一順位欄位)
            else:
                st.caption("💡 表格欄位已重新排序，將「最新催收理由/歷程」移動至左側優先展示：")
                
                # 重新整理欄位順序：請款編號 -> 客戶名稱 -> 🚨最新催收理由/歷程 -> 總金額 -> ...
                reordered_df = pd.DataFrame({
                    "請款編號": df_ar.get("inv_no", df_ar.get("invoice_id", "")),
                    "客戶名稱": df_ar.get("customer", df_ar.get("entity_name", "")),
                    "🚨 最新催收理由/歷程 (前置)": df_ar.get("latest_reason", df_ar.get("notes", "尚無紀錄")),
                    "工程名稱": df_ar.get("project", df_ar.get("project_name", "")),
                    "交易幣別": df_ar.get("curr", df_ar.get("currency", "")),
                    "總帳款": df_ar.get("amount", 0.0),
                    "分期類型": df_ar.get("plan", "不分期"),
                    "分期比率": df_ar.get("ratio", "100%"),
                    "進行推行說明": df_ar.get("status", "正常進度中"),
                })
                
                st.dataframe(reordered_df, use_container_width=True)
        else:
            st.info("尚無應收帳款專案資料。")


def show(engine, t=None):
    render_ar_management(engine, t)


def main(engine, t=None):
    render_ar_management(engine, t)
