import datetime
import pandas as pd
from sqlalchemy import text
import streamlit as st

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


def render(engine, t):
    st.title("💰 管理部 - 財務與應收/應付帳款 (TT200 / 多幣別 / UNC)")
    st.caption("裕豐電機工業 REETECH INDUSTRIAL - 財務會計模組")

    tab_ar, tab_ap, tab_pay, tab_add = st.tabs([
        "📋 TK 131 客戶應收款項 (AR)",
        "🛒 TK 331 採購與廠商應付款項 (AP)",
        "🏦 銀行轉帳水單 (UNC)",
        "➕ 登記新單據/帳款 (含分期 % 拆算)",
    ])

    with tab_ar:
        try:
            df_ar = pd.read_sql(
                "SELECT * FROM invoices WHERE invoice_type='AR'", engine
            )
            st.subheader("📑 TK 131 應收帳款明細表")
            st.dataframe(df_ar, use_container_width=True)
        except Exception as e:
            st.info("尚無應收帳款資料或連線建置中。")

    with tab_ap:
        try:
            df_ap = pd.read_sql(
                "SELECT * FROM invoices WHERE invoice_type='AP'", engine
            )
            st.subheader("🛒 TK 331 採購應付帳款明細表")
            st.dataframe(df_ap, use_container_width=True)
        except Exception as e:
            st.info("尚無應付帳款資料或連線建置中。")

    with tab_pay:
        st.subheader("🏦 銀行轉帳水單登記 (Ủy Nhiệm Chi - UNC)")
        st.info("提供出納登記 Vietcombank / BIDV 轉帳水單號碼與簽核日期。")

    with tab_add:
        st.subheader("➕ 登記新單據/帳款")

        with st.form("add_inv_form"):
            col1, col2 = st.columns(2)
            with col1:
                inv_type = st.selectbox(
                    "帳款類別 *", ["AR - 應收帳款", "AP - 應付帳款"]
                )
                entity_name = st.text_input(
                    "客戶/廠商名稱 *", placeholder="例如: 金寶山"
                )
                project_name = st.text_input(
                    "工程名稱/採購品名 *",
                    placeholder="例如: 金寶山工業區水電工程",
                )
                curr = st.selectbox(
                    "交易幣別 *", ["VND", "USD", "TWD", "CNY"], index=1
                )
                amount = st.number_input(
                    "合約總金額 *", min_value=0.0, value=100000.0, step=1000.0
                )

            with col2:
                plan_option = st.selectbox(
                    "分期付款方案 *",
                    [
                        "分三期 (30% 訂金 / 60% 驗收 / 10% 尾款)",
                        "分二期 (30% 訂金 / 70% 尾款)",
                        "不分期 (100% 全額一次付)",
                        "自訂期數 (%)",
                    ],
                )
                progress_status = st.text_input(
                    "推行進度說明", value="工程備料中 / 準備施工"
                )
                project_desc = st.text_area(
                    "專案詳細說明",
                    placeholder="請填寫本工程施工內容與合約細節...",
                    height=90,
                )

            st.divider()
            st.markdown("### 💳 分期金額拆算與付款日期細項設定")

            today = datetime.date.today()
            installments_data = []

            # ----------------------------------------------------
            # 1. 分三期情境
            # ----------------------------------------------------
            if "分三期" in plan_option:
                st.caption(
                    "💡 系統已為您自動拆算 3 期明細，您可以自由調整 %"
                    " 比與付款日期："
                )
                c_p1, c_p2, c_p3 = st.columns(3)

                with c_p1:
                    st.markdown("##### 【第 1 期 (訂金/首款)】")
                    pct_1 = st.number_input(
                        "第 1 期拆分比例 (%)",
                        value=30.0,
                        min_value=0.0,
                        max_value=100.0,
                        key="p1_pct",
                    )
                    amt_1 = amount * (pct_1 / 100.0)
                    st.info(
                        f"💰 計算金額: **{format_currency_display(amt_1, curr)}**"
                    )
                    date_1 = st.date_input(
                        "第 1 期預計付款日",
                        value=today + datetime.timedelta(days=30),
                        key="p1_date",
                    )
                    installments_data.append({
                        "期數": "第 1 期 (訂金)",
                        "拆分比例": f"{pct_1:.1f}%",
                        "計算金額": format_currency_display(amt_1, curr),
                        "原始金額": amt_1,
                        "預計付款日": str(date_1),
                    })

                with c_p2:
                    st.markdown("##### 【第 2 期 (期中/驗收款)】")
                    pct_2 = st.number_input(
                        "第 2 期拆分比例 (%)",
                        value=60.0,
                        min_value=0.0,
                        max_value=100.0,
                        key="p2_pct",
                    )
                    amt_2 = amount * (pct_2 / 100.0)
                    st.info(
                        f"💰 計算金額: **{format_currency_display(amt_2, curr)}**"
                    )
                    date_2 = st.date_input(
                        "第 2 期預計付款日",
                        value=today + datetime.timedelta(days=60),
                        key="p2_date",
                    )
                    installments_data.append({
                        "期數": "第 2 期 (驗收款)",
                        "拆分比例": f"{pct_2:.1f}%",
                        "計算金額": format_currency_display(amt_2, curr),
                        "原始金額": amt_2,
                        "預計付款日": str(date_2),
                    })

                with c_p3:
                    st.markdown("##### 【第 3 期 (尾款/保固金)】")
                    pct_3 = st.number_input(
                        "第 3 期拆分比例 (%)",
                        value=10.0,
                        min_value=0.0,
                        max_value=100.0,
                        key="p3_pct",
                    )
                    amt_3 = amount * (pct_3 / 100.0)
                    st.info(
                        f"💰 計算金額: **{format_currency_display(amt_3, curr)}**"
                    )
                    date_3 = st.date_input(
                        "第 3 期預計付款日",
                        value=today + datetime.timedelta(days=90),
                        key="p3_date",
                    )
                    installments_data.append({
                        "期數": "第 3 期 (尾款)",
                        "拆分比例": f"{pct_3:.1f}%",
                        "計算金額": format_currency_display(amt_3, curr),
                        "原始金額": amt_3,
                        "預計付款日": str(date_3),
                    })

                sum_pct = pct_1 + pct_2 + pct_3
                if abs(sum_pct - 100.0) > 0.01:
                    st.warning(
                        f"⚠️ 注意：目前 3 期比例總和為 {sum_pct:.1f}%，建議調整為"
                        " 100%！"
                    )

            # ----------------------------------------------------
            # 2. 分二期情境
            # ----------------------------------------------------
            elif "分二期" in plan_option:
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    st.markdown("##### 【第 1 期 (訂金/首款)】")
                    pct_1 = st.number_input(
                        "第 1 期拆分比例 (%)",
                        value=30.0,
                        key="p2_1_pct",
                    )
                    amt_1 = amount * (pct_1 / 100.0)
                    st.info(
                        f"💰 計算金額: **{format_currency_display(amt_1, curr)}**"
                    )
                    date_1 = st.date_input(
                        "第 1 期預計付款日",
                        value=today + datetime.timedelta(days=30),
                        key="p2_1_date",
                    )
                    installments_data.append({
                        "期數": "第 1 期 (訂金)",
                        "拆分比例": f"{pct_1:.1f}%",
                        "計算金額": format_currency_display(amt_1, curr),
                        "原始金額": amt_1,
                        "預計付款日": str(date_1),
                    })

                with c_p2:
                    st.markdown("##### 【第 2 期 (尾款/結案)】")
                    pct_2 = st.number_input(
                        "第 2 期拆分比例 (%)",
                        value=70.0,
                        key="p2_2_pct",
                    )
                    amt_2 = amount * (pct_2 / 100.0)
                    st.info(
                        f"💰 計算金額: **{format_currency_display(amt_2, curr)}**"
                    )
                    date_2 = st.date_input(
                        "第 2 期預計付款日",
                        value=today + datetime.timedelta(days=60),
                        key="p2_2_date",
                    )
                    installments_data.append({
                        "期數": "第 2 期 (尾款)",
                        "拆分比例": f"{pct_2:.1f}%",
                        "計算金額": format_currency_display(amt_2, curr),
                        "原始金額": amt_2,
                        "預計付款日": str(date_2),
                    })

            # ----------------------------------------------------
            # 3. 不分期情境
            # ----------------------------------------------------
            else:
                st.markdown("##### 📌 全額一次付清 (100%)")
                single_date = st.date_input(
                    "約定付款日期",
                    value=today + datetime.timedelta(days=30),
                    key="s_date",
                )
                st.success(
                    f"💰 一次付清總金額:"
                    f" **{format_currency_display(amount, curr)}** (100%) |"
                    f" 付款日: {single_date}"
                )
                installments_data.append({
                    "期數": "全額一次付",
                    "拆分比例": "100.0%",
                    "計算金額": format_currency_display(amount, curr),
                    "原始金額": amount,
                    "預計付款日": str(single_date),
                })

            st.divider()
            st.markdown("##### 📋 預計請款分期明細清單預覽：")
            st.dataframe(
                pd.DataFrame(installments_data), use_container_width=True
            )

            # 💾 寫入資料庫
            if st.form_submit_button("💾 儲存寫入資料庫", type="primary"):
                if entity_name and project_name:
                    type_code = "AR" if "AR" in inv_type else "AP"
                    inv_id = f"{type_code}-2026-{datetime.datetime.now().strftime('%m%d%H%M')}"
                    calc_usd = amount / EXCHANGE_RATES.get(curr, 1.0)
                    first_due_date = (
                        installments_data[0]["預計付款日"]
                        if installments_data
                        else str(today)
                    )

                    try:
                        with engine.connect() as conn:
                            conn.execute(
                                text(
                                    "INSERT INTO invoices (invoice_id,"
                                    " entity_name, project_name, amount,"
                                    " currency, amount_usd, due_date,"
                                    " invoice_type, is_paid) VALUES (:id,"
                                    " :entity, :prj, :amt, :curr, :usd, :due,"
                                    " :type, false)"
                                ),
                                {
                                    "id": inv_id,
                                    "entity": entity_name,
                                    "prj": (
                                        f"{project_name}"
                                        f" ({plan_option.split(' ')[0]})"
                                    ),
                                    "amt": amount,
                                    "curr": curr,
                                    "usd": calc_usd,
                                    "due": first_due_date,
                                    "type": type_code,
                                },
                            )
                            conn.commit()
                        st.success(
                            f"單號 {inv_id} 已成功儲存！共拆算"
                            f" {len(installments_data)} 期明細。"
                        )
                        st.rerun()
                    except Exception as ex:
                        st.error(f"資料庫寫入失敗: {ex}")
                else:
                    st.error("請輸入名稱與項目！")


def show(engine, t):
    render(engine, t)


def main(engine, t):
    render(engine, t)
