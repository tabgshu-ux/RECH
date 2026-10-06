import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

AR_I18N = {import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

AR_I18N = {
    "繁體中文": {
        "title": "📋 管理部 - 客戶應收帳款 (AR) & 專案分期進度管理",
        "caption": "記錄客戶工程合約總額、動態分期付款排程管理、專案說明與進度實時追蹤。",
        "tab_list": "📑 客戶應收款項總表與進度",
        "tab_edit": "✍️ 修改進行進度說明與催收歷程",
        "tab_add": "➕ 登記新應收帳款專案"
    },
    "Tiếng Việt": {
        "title": "📋 Khối Quản lý - Phải thu Khách hàng (AR) & Tiến độ Dự án",
        "caption": "Quản lý tổng số tiền hợp đồng, lịch trình thanh toán theo đợt, cập nhật tiến độ.",
        "tab_list": "📑 Danh sách Phải thu & Tiến độ",
        "tab_edit": "✍️ Cập nhật Tiến độ & Lý do thu nợ",
        "tab_add": "➕ Thêm Dự án Phải thu Mới"
    },
    "English": {
        "title": "📋 Admin - Accounts Receivable (AR) & Project Installments",
        "caption": "Track total contract amounts, installment schedules, descriptions, and progress updates.",
        "tab_list": "📑 AR Summary & Progress",
        "tab_edit": "✍️ Update Progress & Collection Audit",
        "tab_add": "➕ Register New AR Project"
    }
}

def format_curr(amt, curr):
    if curr == "越南盾": return f"₫ {amt:,.0f} VND"
    elif curr == "美金": return f"$ {amt:,.3f} USD"
    elif curr == "台幣": return f"NT$ {amt:,.0f} TWD"
    elif curr == "人民幣": return f"¥ {amt:,.2f} CNY"
    return f"{amt:,.3f} {curr}"

def render_sales_order_ar_page(engine=None, lang="繁體中文", **kwargs):
    L = AR_I18N.get(lang, AR_I18N["繁體中文"])
    st.title(L["title"])
    st.caption(L["caption"])

    tab_list, tab_edit, tab_add = st.tabs([L["tab_list"], L["tab_edit"], L["tab_add"]])

    # 1. 應收帳款總覽清單
    with tab_list:
        st.subheader("📋 客戶應收帳款專案清冊")
        if engine:
            try:
                df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
                if not df_ar.empty:
                    display_list = []
                    for idx, r in df_ar.iterrows():
                        display_list.append({
                            "編號": idx + 1,
                            "請款編號": r.get("invoice_id"),
                            "客戶名稱": r.get("entity_name"),
                            "工程名稱": r.get("project_name"),
                            "交易幣別": r.get("currency"),
                            "總帳款": format_curr(r.get("quoted_amount", 0.0), r.get("currency")),
                            "分期類型": r.get("payment_terms", "不分期"),
                            "分期比率": r.get("installment_ratios", "100%"),
                            "進行進度說明": r.get("progress_note", "工程備料中"),
                            "專案說明": r.get("project_desc", "-"),
                            "最新催收理由/歷程": r.get("uncollected_reason", "-")
                        })
                    st.dataframe(pd.DataFrame(display_list), use_container_width=True)
                else:
                    st.info("目前無應收帳款紀錄。")
            except Exception as e:
                st.error(f"讀取資料失敗: {e}")

    # 2. 修改進行進度說明與催收歷程
    with tab_edit:
        st.subheader("✍️ 修改專案進行進度說明與催收紀錄")
        if engine:
            try:
                df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
                if not df_ar.empty:
                    ar_opts = {f"{r['invoice_id']} - {r['entity_name']} ({r['project_name']})": r['invoice_id'] for _, r in df_ar.iterrows()}
                    sel_label = st.selectbox("請選擇要更新進度的請款專案：", list(ar_opts.keys()))
                    target_id = ar_opts[sel_label]
                    target_row = df_ar[df_ar['invoice_id'] == target_id].iloc[0]

                    st.markdown(f"**當前專案**：`{target_row['project_name']}` | **總帳款**：{format_curr(target_row['quoted_amount'], target_row['currency'])}")
                    
                    with st.form("form_update_ar_progress"):
                        new_progress = st.text_area("更新「進行進度說明」*", value=target_row.get("progress_note", ""))
                        new_reason = st.text_area("更新/追加「催收理由與客戶回應」", value=target_row.get("uncollected_reason", ""))
                        modifier = st.text_input("修改人員姓名*", value=st.session_state.get("user_name", "admin"))

                        if st.form_submit_button("💾 儲存並更新專案進度", use_container_width=True):
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            full_reason = f"【{timestamp} 修改人:{modifier}】{new_reason}"
                            
                            with engine.connect() as conn:
                                conn.execute(
                                    text("""
                                        UPDATE invoices 
                                        SET progress_note = :prog,
                                            uncollected_reason = :reason,
                                            quoter_name = :quoter
                                        WHERE invoice_id = :id
                                    """),
                                    {"prog": new_progress, "reason": full_reason, "quoter": modifier, "id": target_id}
                                )
                                conn.commit()
                            st.success(f"請款單 `{target_id}` 之進行進度與催收理由已更新！")
                            st.rerun()
            except Exception as e:
                st.error(f"讀取專案失敗: {e}")

    # 3. 新增請款專案 (具備即時互動分期與自訂百分比)
    with tab_add:
        st.subheader("➕ 登記新應收帳款專案")
        
        c1, c2 = st.columns(2)
        with c1:
            inv_id = st.text_input("請款編號 *", value=f"AR-2026-{datetime.datetime.now().strftime('%m%d%H%M')}")
            entity_name = st.text_input("客戶名稱 *", placeholder="越南樟榜工業區A廠")
            project_name = st.text_input("工程名稱 *", placeholder="西寧廠 2000A 配電櫃新建工程")
            currency = st.selectbox("交易幣別 *", ["越南盾", "美金", "台幣", "人民幣"])
            
            # 支援美金小數點後 3 位
            if currency == "美金":
                total_amount = st.number_input("總帳款 (USD - 精確至小數點後 3 位) *", min_value=0.0, value=10000.000, format="%.3f", step=0.001)
            else:
                total_amount = st.number_input("總帳款 *", min_value=0.0, value=100000.0, step=1000.0)

        with c2:
            plan_type = st.selectbox("付款期數模式 *", ["不分期", "分三期", "分五期"])
            project_desc = st.text_area("專案說明", placeholder="請填寫本工程施工內容與合約細節...")
            progress_note = st.text_input("進行進度說明", value="工程備料中 / 準備施工")

        st.markdown("---")
        st.markdown("##### 💳 分期百分比 (%) 與付款日期細項設定")

        ratios_str = "100%"
        p1_amt, p2_amt, p3_amt, p4_amt, p5_amt = total_amount, 0.0, 0.0, 0.0, 0.0
        d1, d2, d3, d4, d5 = datetime.date.today(), datetime.date.today(), datetime.date.today(), datetime.date.today(), datetime.date.today()

        if plan_type == "不分期":
            d1 = st.date_input("付款日期", value=datetime.date.today() + datetime.timedelta(days=30), key="ar_d_single")
            st.info(f"全額一次付清：{format_curr(total_amount, currency)}")

        elif plan_type == "分三期":
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                r1 = st.number_input("第 1 期比率 (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0, key="ar_3r1")
            with col_r2:
                r2 = st.number_input("第 2 期比率 (%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0, key="ar_3r2")
            with col_r3:
                r3 = st.number_input("第 3 期比率 (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0, key="ar_3r3")
            
            total_pct = r1 + r2 + r3
            if abs(total_pct - 100.0) > 0.01:
                st.warning(f"⚠️ 目前分期總比率為 `{total_pct}%`（請調整至總和 100%）")
            else:
                st.success("✅ 分期比率總和剛好 100%")

            ratios_str = f"{r1}% / {r2}% / {r3}%"
            p1_amt = total_amount * (r1 / 100.0)
            p2_amt = total_amount * (r2 / 100.0)
            p3_amt = total_amount * (r3 / 100.0)

            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"• **第一期金額**：`{format_curr(p1_amt, currency)}`")
                d1 = st.date_input("第一期收款日期", value=datetime.date.today() + datetime.timedelta(days=7), key="ar_3d1")
                st.write(f"• **第二期金額**：`{format_curr(p2_amt, currency)}`")
                d2 = st.date_input("第二期收款日期", value=datetime.date.today() + datetime.timedelta(days=30), key="ar_3d2")
            with col_b:
                st.write(f"• **第三期金額**：`{format_curr(p3_amt, currency)}`")
                d3 = st.date_input("第三期收款日期", value=datetime.date.today() + datetime.timedelta(days=60), key="ar_3d3")

        elif plan_type == "分五期":
            col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
            with col_r1:
                r1 = st.number_input("第 1 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r1")
            with col_r2:
                r2 = st.number_input("第 2 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r2")
            with col_r3:
                r3 = st.number_input("第 3 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r3")
            with col_r4:
                r4 = st.number_input("第 4 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r4")
            with col_r5:
                r5 = st.number_input("第 5 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r5")

            total_pct = r1 + r2 + r3 + r4 + r5
            if abs(total_pct - 100.0) > 0.01:
                st.warning(f"⚠️ 目前分期總比率為 `{total_pct}%`（請調整至總和 100%）")
            else:
                st.success("✅ 分期比率總和剛好 100%")

            ratios_str = f"{r1}% / {r2}% / {r3}% / {r4}% / {r5}%"
            p1_amt = total_amount * (r1 / 100.0)
            p2_amt = total_amount * (r2 / 100.0)
            p3_amt = total_amount * (r3 / 100.0)
            p4_amt = total_amount * (r4 / 100.0)
            p5_amt = total_amount * (r5 / 100.0)

            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"• **第一期金額**：`{format_curr(p1_amt, currency)}`")
                d1 = st.date_input("第一期收款日期", value=datetime.date.today() + datetime.timedelta(days=7), key="ar_5d1")
                st.write(f"• **第二期金額**：`{format_curr(p2_amt, currency)}`")
                d2 = st.date_input("第二期收款日期", value=datetime.date.today() + datetime.timedelta(days=30), key="ar_5d2")
                st.write(f"• **第三期金額**：`{format_curr(p3_amt, currency)}`")
                d3 = st.date_input("第三期收款日期", value=datetime.date.today() + datetime.timedelta(days=60), key="ar_5d3")
            with col_b:
                st.write(f"• **第四期金額**：`{format_curr(p4_amt, currency)}`")
                d4 = st.date_input("第四期收款日期", value=datetime.date.today() + datetime.timedelta(days=90), key="ar_5d4")
                st.write(f"• **第五期金額**：`{format_curr(p5_amt, currency)}`")
                d5 = st.date_input("第五期收款日期", value=datetime.date.today() + datetime.timedelta(days=120), key="ar_5d5")

        st.markdown("")
        if st.button("💾 儲存並建立應收請款專案", type="primary", use_container_width=True):
            if entity_name and project_name:
                if engine:
                    with engine.connect() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO invoices (
                                    invoice_id, entity_name, project_name, currency, amount, quoted_amount, 
                                    payment_terms, installment_ratios, project_desc, progress_note, 
                                    due_date, invoice_type, is_paid
                                ) VALUES (
                                    :id, :entity, :prj, :curr, :amt, :q_amt, 
                                    :terms, :ratios, :desc, :prog, 
                                    :due, 'AR', false
                                )
                            """),
                            {
                                "id": inv_id, "entity": entity_name, "prj": project_name, "curr": currency,
                                "amt": p1_amt, "q_amt": total_amount, "terms": plan_type, "ratios": ratios_str,
                                "desc": project_desc, "prog": progress_note, "due": d1
                            }
                        )
                        conn.commit()
                st.success(f"專案 `{inv_id}` 建立成功！")
                st.rerun()
            else:
                st.warning("⚠️ 請完整填寫客戶名稱與工程名稱！")

def show(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)

def main(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)
    "繁體中文": {
        "title": "📋 管理部 - 客戶應收帳款 (AR) & 專案分期進度管理",
        "caption": "記錄客戶工程合約總額、動態 3期/5期付款排程自訂比率、專案說明與進度實時修改。",
        "tab_list": "📑 客戶應收款項總表與進度",
        "tab_edit": "✍️ 修改進行進度說明與催收歷程",
        "tab_add": "➕ 新增請款專案 (自訂分期比率)"
    },
    "Tiếng Việt": {
        "title": "📋 Khối Quản lý - Phải thu Khách hàng (AR) & Tiến độ Dự án",
        "caption": "Quản lý tổng số tiền hợp đồng, tự định nghĩa tỷ lệ % (3 hoặc 5 đợt), cập nhật tiến độ.",
        "tab_list": "📑 Danh sách Phải thu & Tiến độ",
        "tab_edit": "✍️️ Cập nhật Tiến độ & Lý do thu nợ",
        "tab_add": "➕ Thêm Dự án Thu tiền Mới (Tùy chỉnh %)"
    },
    "English": {
        "title": "📋 Admin - Accounts Receivable (AR) & Project Installments",
        "caption": "Track total contract amounts, custom 3/5 installment percentage schedules, and progress.",
        "tab_list": "📑 AR Summary & Progress",
        "tab_edit": "✍️ Update Progress & Collection Audit",
        "tab_add": "➕ Add New AR Project (Custom Ratios)"
    }
}

def format_curr(amt, curr):
    if curr == "越南盾": return f"₫ {amt:,.0f} VND"
    elif curr == "美金": return f"$ {amt:,.3f} USD"
    elif curr == "台幣": return f"NT$ {amt:,.0f} TWD"
    elif curr == "人民幣": return f"¥ {amt:,.2f} CNY"
    return f"{amt:,.3f} {curr}"

def render_sales_order_ar_page(engine=None, lang="繁體中文", **kwargs):
    L = AR_I18N.get(lang, AR_I18N["繁體中文"])
    st.title(L["title"])
    st.caption(L["caption"])

    tab_list, tab_edit, tab_add = st.tabs([L["tab_list"], L["tab_edit"], L["tab_add"]])

    # 1. 應收帳款總覽清單
    with tab_list:
        st.subheader("📋 客戶應收帳款專案清冊")
        if engine:
            try:
                df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
                if not df_ar.empty:
                    display_list = []
                    for idx, r in df_ar.iterrows():
                        display_list.append({
                            "編號": idx + 1,
                            "請款編號": r.get("invoice_id"),
                            "客戶名稱": r.get("entity_name"),
                            "工程名稱": r.get("project_name"),
                            "交易幣別": r.get("currency"),
                            "總帳款": format_curr(r.get("quoted_amount", 0.0), r.get("currency")),
                            "分期類型": r.get("payment_terms", "不分期"),
                            "分期比率": r.get("installment_ratios", "100%"),
                            "進行進度說明": r.get("progress_note", "工程備料中"),
                            "專案說明": r.get("project_desc", "-"),
                            "最新催收理由/歷程": r.get("uncollected_reason", "-")
                        })
                    st.dataframe(pd.DataFrame(display_list), use_container_width=True)
                else:
                    st.info("目前無應收帳款紀錄。")
            except Exception as e:
                st.error(f"讀取資料失敗: {e}")

    # 2. 修改進行進度說明與催收歷程
    with tab_edit:
        st.subheader("✍️ 修改專案進行進度說明與催收紀錄")
        if engine:
            try:
                df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
                if not df_ar.empty:
                    ar_opts = {f"{r['invoice_id']} - {r['entity_name']} ({r['project_name']})": r['invoice_id'] for _, r in df_ar.iterrows()}
                    sel_label = st.selectbox("請選擇要更新進度的請款專案：", list(ar_opts.keys()))
                    target_id = ar_opts[sel_label]
                    target_row = df_ar[df_ar['invoice_id'] == target_id].iloc[0]

                    st.markdown(f"**當前專案**：`{target_row['project_name']}` | **總帳款**：{format_curr(target_row['quoted_amount'], target_row['currency'])}")
                    
                    with st.form("form_update_ar_progress"):
                        new_progress = st.text_area("更新「進行進度說明」*", value=target_row.get("progress_note", ""))
                        new_reason = st.text_area("更新/追加「催收理由與客戶回應」", value=target_row.get("uncollected_reason", ""))
                        modifier = st.text_input("修改人員姓名*", value=st.session_state.get("user_name", "admin"))

                        if st.form_submit_button("💾 儲存並更新專案進度", use_container_width=True):
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            full_reason = f"【{timestamp} 修改人:{modifier}】{new_reason}"
                            
                            with engine.connect() as conn:
                                conn.execute(
                                    text("""
                                        UPDATE invoices 
                                        SET progress_note = :prog,
                                            uncollected_reason = :reason,
                                            quoter_name = :quoter
                                        WHERE invoice_id = :id
                                    """),
                                    {"prog": new_progress, "reason": full_reason, "quoter": modifier, "id": target_id}
                                )
                                conn.commit()
                            st.success(f"請款單 `{target_id}` 之進行進度與催收理由已更新！")
                            st.rerun()
            except Exception as e:
                st.error(f"讀取專案失敗: {e}")

    # 3. 新增請款專案 (支援自訂 3 期 / 5 期百分比與美金小數點後 3 位)
    with tab_add:
        st.subheader("➕ 登記新應收帳款專案 (支援自訂分期 %) ")
        with st.form("form_add_ar_project_custom"):
            c1, c2 = st.columns(2)
            with c1:
                inv_id = st.text_input("請款編號 *", value=f"AR-2026-{datetime.datetime.now().strftime('%m%d%H%M')}")
                entity_name = st.text_input("客戶名稱 *", placeholder="越南樟榜工業區A廠")
                project_name = st.text_input("工程名稱 *", placeholder="西寧廠 2000A 配電櫃新建工程")
                currency = st.selectbox("交易幣別 *", ["越南盾", "美金", "台幣", "人民幣"])
                
                # 💡 支援美金小數點後 3 位精準輸入
                if currency == "美金":
                    total_amount = st.number_input("總帳款 (USD - 精確至小數點後 3 位) *", min_value=0.0, value=10000.000, format="%.3f", step=0.001)
                else:
                    total_amount = st.number_input("總帳款 *", min_value=0.0, value=100000.0, step=1000.0)

            with c2:
                plan_type = st.selectbox("分期或是不分期 *", ["不分期", "分三期", "分五期"])
                project_desc = st.text_area("專案說明 (人員填寫)", placeholder="請填寫本工程施工內容與合約細節...")
                progress_note = st.text_input("進行進度說明", value="工程備料中 / 準備施工")

            st.markdown("---")
            st.markdown("##### 💳 自訂分期百分比 (%) 與付款日期細項設定")

            ratios_str = "100%"
            p1_amt, p2_amt, p3_amt, p4_amt, p5_amt = total_amount, 0.0, 0.0, 0.0, 0.0
            d1, d2, d3, d4, d5 = datetime.date.today(), datetime.date.today(), datetime.date.today(), datetime.date.today(), datetime.date.today()

            if plan_type == "不分期":
                d1 = st.date_input("付款日期", value=datetime.date.today() + datetime.timedelta(days=30), key="ar_d_single")
                st.info(f"全額一次付清：{format_curr(total_amount, currency)}")

            elif plan_type == "分三期":
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    r1 = st.number_input("第 1 期比率 (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0, key="ar_3r1")
                with col_r2:
                    r2 = st.number_input("第 2 期比率 (%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0, key="ar_3r2")
                with col_r3:
                    r3 = st.number_input("第 3 期比率 (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0, key="ar_3r3")
                
                total_pct = r1 + r2 + r3
                if abs(total_pct - 100.0) > 0.01:
                    st.warning(f"⚠️ 目前分期總比率為 `{total_pct}%`（建議總和為 100%）")
                else:
                    st.success("✅ 分期比率總和剛好 100%")

                ratios_str = f"{r1}% / {r2}% / {r3}%"
                p1_amt = total_amount * (r1 / 100.0)
                p2_amt = total_amount * (r2 / 100.0)
                p3_amt = total_amount * (r3 / 100.0)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"• **第一期金額**：`{format_curr(p1_amt, currency)}`")
                    d1 = st.date_input("第一期收款日期", value=datetime.date.today() + datetime.timedelta(days=7), key="ar_3d1")
                    st.write(f"• **第二期金額**：`{format_curr(p2_amt, currency)}`")
                    d2 = st.date_input("第二期收款日期", value=datetime.date.today() + datetime.timedelta(days=30), key="ar_3d2")
                with col_b:
                    st.write(f"• **第三期金額**：`{format_curr(p3_amt, currency)}`")
                    d3 = st.date_input("第三期收款日期", value=datetime.date.today() + datetime.timedelta(days=60), key="ar_3d3")

            elif plan_type == "分五期":
                col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
                with col_r1:
                    r1 = st.number_input("第 1 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r1")
                with col_r2:
                    r2 = st.number_input("第 2 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r2")
                with col_r3:
                    r3 = st.number_input("第 3 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r3")
                with col_r4:
                    r4 = st.number_input("第 4 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r4")
                with col_r5:
                    r5 = st.number_input("第 5 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r5")

                total_pct = r1 + r2 + r3 + r4 + r5
                if abs(total_pct - 100.0) > 0.01:
                    st.warning(f"⚠️ 目前分期總比率為 `{total_pct}%`（建議總和為 100%）")
                else:
                    st.success("✅ 分期比率總和剛好 100%")

                ratios_str = f"{r1}% / {r2}% / {r3}% / {r4}% / {r5}%"
                p1_amt = total_amount * (r1 / 100.0)
                p2_amt = total_amount * (r2 / 100.0)
                p3_amt = total_amount * (r3 / 100.0)
                p4_amt = total_amount * (r4 / 100.0)
                p5_amt = total_amount * (r5 / 100.0)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"• **第一期金額**：`{format_curr(p1_amt, currency)}`")
                    d1 = st.date_input("第一期收款日期", value=datetime.date.today() + datetime.timedelta(days=7), key="ar_5d1")
                    st.write(f"• **第二期金額**：`{format_curr(p2_amt, currency)}`")
                    d2 = st.date_input("第二期收款日期", value=datetime.date.today() + datetime.timedelta(days=30), key="ar_5d2")
                    st.write(f"• **第三期金額**：`{format_curr(p3_amt, currency)}`")
                    d3 = st.date_input("第三期收款日期", value=datetime.date.today() + datetime.timedelta(days=60), key="ar_5d3")
                with col_b:
                    st.write(f"• **第四期金額**：`{format_curr(p4_amt, currency)}`")
                    d4 = st.date_input("第四期收款日期", value=datetime.date.today() + datetime.timedelta(days=90), key="ar_5d4")
                    st.write(f"• **第五期金額**：`{format_curr(p5_amt, currency)}`")
                    d5 = st.date_input("第五期收款日期", value=datetime.date.today() + datetime.timedelta(days=120), key="ar_5d5")

            if st.form_submit_button("💾 儲存並建立應收請款專案", use_container_width=True):
                if entity_name and project_name:
                    if engine:
                        with engine.connect() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO invoices (
                                        invoice_id, entity_name, project_name, currency, amount, quoted_amount, 
                                        payment_terms, installment_ratios, project_desc, progress_note, 
                                        due_date, invoice_type, is_paid
                                    ) VALUES (
                                        :id, :entity, :prj, :curr, :amt, :q_amt, 
                                        :terms, :ratios, :desc, :prog, 
                                        :due, 'AR', false
                                    )
                                """),
                                {
                                    "id": inv_id, "entity": entity_name, "prj": project_name, "curr": currency,
                                    "amt": p1_amt, "q_amt": total_amount, "terms": plan_type, "ratios": ratios_str,
                                    "desc": project_desc, "prog": progress_note, "due": d1
                                }
                            )
                            conn.commit()
                    st.success(f"專案 `{inv_id}` 建立成功！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫客戶名稱與工程名稱！")

def show(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)

def main(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)
