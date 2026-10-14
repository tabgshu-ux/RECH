import streamlit as st
import pandas as pd
import datetime
import re

# ----------------------------------------------------
# 🌐 工具函式：金額格式化與千位符號處理
# ----------------------------------------------------
def parse_formatted_amount(val_str):
    if not val_str:
        return 0.0
    clean_str = re.sub(r"[^\d]", "", str(val_str))
    return float(clean_str) if clean_str else 0.0

def format_currency_text(amount, currency="VND"):
    try:
        val = float(amount)
        if currency in ["VND", "TWD"]:
            return f"{val:,.0f}".replace(",", ".") + f" {currency}"
        else:
            return f"${val:,.2f} {currency}"
    except Exception:
        return f"{amount} {currency}"

def render_engineering_management_page(engine=None, lang="繁體中文", **kwargs):
    sub_action = (
        kwargs.get("sub_action")
        or st.session_state.get("current_sub_action")
        or st.session_state.get("selected_sub_menu")
        or st.session_state.get("sub_menu")
        or "2"
    )
    sub_str = str(sub_action).strip()

    st.title("⚡ 裕豐電機 - 工程與設計管理中心")
    st.caption("水電工程、配電盤製造、現場探勘與雙層報價系統")

    # 倉庫連線物料庫（預設標準品項與單價）
    if "warehouse_master_parts" not in st.session_state:
        st.session_state.warehouse_master_parts = {
            "MCCB 3P 400AF 315AT 50KA 380V - TBX-400L": 3842670.0,
            "銅排及固定座熱縮套膜 CU BAR BUS": 4130000.0,
            "控制配線另料 Phụ liệu": 1180000.0,
            "配盤組裝工資 Tiền công lắp ráp": 2360000.0,
            "CASE (W)800mm*(H)1200mm*(D)350mm SPCC T=2.0": 9605200.0,
            "過電流電驛 OC+EF (MK1000A-240A)": 8075920.0,
            "高低電壓電驛保護器 OV+UV (MU 250-415)": 2349887.0,
            "PVC 管 2寸 (50米/捆)": 1200000.0,
            "控制電纜 3.5mm² (100m/卷)": 2800000.0,
            "端子排與五金配件包 (套)": 850000.0
        }

    if "two_tier_quotations_db" not in st.session_state:
        st.session_state.two_tier_quotations_db = []

    # 全公司簽核中心資料庫連線
    if "pending_approvals_db" not in st.session_state:
        st.session_state.pending_approvals_db = []

    if "engineering_projects_db" not in st.session_state:
        st.session_state.engineering_projects_db = [
            {"proj_code": "PRJ-TN-2026-01", "proj_name": "西寧廠高壓配電盤擴建", "factory": "西寧廠", "budget": 1200000000, "status": "進行中"},
            {"proj_code": "PRJ-HP-2026-02", "proj_name": "海防廠動力盤統包工程", "factory": "海防廠", "budget": 850000000, "status": "進行中"}
        ]

    # 下拉選單切換
    sub_options = [
        "⚡ 2. 配電盤與工程專案雙層報價",
        "📊 1. 工程主管戰情室 (Executive Cockpit)"
    ]
    
    selected_option = st.selectbox("請選擇要執行的工程/設計功能：", sub_options, index=0)

    # ====================================================
    # ⚡ 配電盤與工程專案雙層報價與現場探勘系統
    # ====================================================
    if "雙層報價" in selected_option or sub_str in ["1", "2"]:
        st.markdown("### ⚡ 配電盤與工程專案雙層報價與探勘系統")
        
        tab_prop, tab_edit, tab_review = st.tabs(["✍️ 建立/提交報價提案", "✏️ 修改與刪除報價單", "🔒 主管審核與報價單樣式預覽"])

        # ------------------------------------------------
        # TAB 1: 建立報價提案
        # ------------------------------------------------
        with tab_prop:
            with st.form("form_engineering_survey_quotation"):
                st.markdown("##### 📝 1. 報價單基本資訊 (BẢNG BÁO GIÁ)")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    p_client = st.text_input("客戶公司名稱 (CÔNG TY) *", value="CÔNG TY TNHH LEADER ART INDUSTRIES (VIETNAM)")
                with c2:
                    p_attn = st.text_input("聯絡對象 (ATTN)", value="James & LIU KUAN HSIN")
                with c3:
                    p_proj = st.text_input("工程名稱 (Tên công trình) *", value="新增設備機電系統供電工程")
                with c4:
                    p_curr = st.selectbox("報價幣別 (Đơn vị tiền tệ) *", ["VND", "USD", "RMB", "TWD"], index=0)

                c5, c6, c7 = st.columns(3)
                with c5:
                    p_prop = st.text_input("提案負責人 (From) *", value="陳智賢")
                with c6:
                    p_ref = st.text_input("報價單號 (Ref)", value=f"09092026/LA/BG{len(st.session_state.two_tier_quotations_db)+1:02d}")
                with c7:
                    p_vat_rate = st.number_input("增值稅率 VAT (%)", min_value=0.0, max_value=20.0, value=8.0, step=1.0)

                st.markdown("---")

                st.markdown("##### 📦 2. 工程 BOM 材料明細清單 (CHI TIẾT HẠNG MỤC)")
                st.caption("💡 說明：倉庫既有物料請直接選取；若倉庫無此品項，請選取『➕ 新增未在庫材料』並直接輸入名稱與單價。")

                num_items = st.number_input("增加工程項目格數", min_value=1, max_value=30, value=4, step=1)

                internal_rows = []
                total_cost = 0.0
                available_parts = ["➕ 新增未在庫材料"] + list(st.session_state.warehouse_master_parts.keys())

                for i in range(1, int(num_items) + 1):
                    ic1, ic2, ic3, ic4, ic5, ic6 = st.columns([2.2, 1.8, 0.8, 1.0, 1.3, 1.5])
                    
                    with ic1:
                        selected_part = st.selectbox(f"工程項目/材料 #{i}", available_parts, key=f"part_sel_{i}")

                    if selected_part == "➕ 新增未在庫材料":
                        with ic2:
                            custom_name = st.text_input(f"材料名稱與規格 #{i}", placeholder="例: 供電給設備 Cấp nguồn cho máy", key=f"inote_{i}")
                        with ic3:
                            iunit = st.text_input(f"單位 #{i}", value="式", key=f"iunit_{i}")
                        with ic4:
                            iqty = st.number_input(f"數量 #{i}", min_value=0.0, value=1.0, key=f"iqty_{i}")
                        with ic5:
                            c_price = st.number_input(f"單價 ({p_curr}) #{i}", min_value=0.0, value=747901962.0 if p_curr in ["VND","TWD"] else 1000.0, key=f"cprice_{i}")
                        auto_unit_price = c_price
                        part_display_name = custom_name if custom_name else f"工程項目 #{i}"
                        part_source = "現場工程新增"
                    else:
                        auto_unit_price = st.session_state.warehouse_master_parts[selected_part]
                        with ic2:
                            note_extra = st.text_input(f"規格與備註 #{i}", value="台商越南專業廠 / TECO", key=f"inote_{i}")
                            part_display_name = f"{selected_part} ({note_extra})" if note_extra else selected_part
                        with ic3:
                            iunit = st.text_input(f"單位 #{i}", value="只", key=f"iunit_{i}")
                        with ic4:
                            iqty = st.number_input(f"數量 #{i}", min_value=0.0, value=1.0, key=f"iqty_{i}")
                        with ic5:
                            st.text_input(f"單價 ({p_curr}) #{i}", value=f"{auto_unit_price:,.0f}" if p_curr in ["VND","TWD"] else f"{auto_unit_price:,.2f}", disabled=True, key=f"price_display_{i}")
                        part_source = "倉庫連線物料"

                    sub = iqty * auto_unit_price
                    with ic6:
                        sub_str = f"{sub:,.0f} {p_curr}" if p_curr in ["VND","TWD"] else f"${sub:,.2f} {p_curr}"
                        st.text_input(f"複價 #{i}", value=sub_str, disabled=True, key=f"sub_display_{i}")

                    if iqty > 0 and part_display_name:
                        total_cost += sub
                        internal_rows.append({
                            "stt": i,
                            "desc": part_display_name,
                            "unit": iunit,
                            "qty": iqty,
                            "unit_price": auto_unit_price,
                            "subtotal": sub,
                            "source": part_source
                        })

                st.markdown(f"### 💰 材料與設備基本小計：`:red[{format_currency_text(total_cost, p_curr)}]`")
                st.markdown("---")

                # 附加費用計算 (運雜費、利管費、折扣)
                st.markdown("##### 📊 3. 附加費用與稅務試算 (Phí vận chuyển, quản lý & VAT)")
                fc1, fc2, fc3 = st.columns(3)
                with fc1:
                    freight_fee = st.number_input(f"運雜費 (Phí vận chuyển) ({p_curr})", min_value=0.0, value=total_cost * 0.015)
                with fc2:
                    manage_fee = st.number_input(f"利管費 (Phí quản lý) ({p_curr})", min_value=0.0, value=total_cost * 0.035)
                with fc3:
                    discount_amt = st.number_input(f"折扣金額 (Giảm giá) ({p_curr})", min_value=0.0, value=0.0)

                subtotal_before_tax = total_cost + freight_fee + manage_fee - discount_amt
                vat_amount = subtotal_before_tax * (p_vat_rate / 100.0)
                final_total_amount = subtotal_before_tax + vat_amount

                st.markdown(f"##### 🧮 試算結果：未稅合計 `:blue[{format_currency_text(subtotal_before_tax, p_curr)}]` | 增值稅 ({p_vat_rate}%) `:orange[{format_currency_text(vat_amount, p_curr)}]` | 報價總計 `:red[{format_currency_text(final_total_amount, p_curr)}]`")

                st.markdown("---")
                st.markdown("##### 📸 4. 現場探勘照片與說明 (呈報副總經理參考)")
                site_photos = st.file_uploader("📷 上傳現場探勘與工程現場照片", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
                site_notes = st.text_area("📝 現場探勘狀況與特殊備註", placeholder="例: 供電線路需跨越廠區過路橋架，相關管線已於明細中編列。")

                if st.form_submit_button("🚀 提交報價單並同步至電子簽核中心", type="primary", use_container_width=True):
                    if p_client and p_proj and internal_rows:
                        new_id = p_ref if p_ref else f"QUO-2026-{len(st.session_state.two_tier_quotations_db)+1:03d}"
                        
                        quotation_record = {
                            "quot_id": new_id,
                            "client": p_client,
                            "attn": p_attn,
                            "project_name": p_proj,
                            "proposer": p_prop,
                            "currency": p_curr,
                            "date": str(datetime.date.today()),
                            "internal_items": internal_rows,
                            "total_cost": total_cost,
                            "freight_fee": freight_fee,
                            "manage_fee": manage_fee,
                            "discount_amt": discount_amt,
                            "subtotal_before_tax": subtotal_before_tax,
                            "vat_rate": p_vat_rate,
                            "vat_amount": vat_amount,
                            "customer_price": final_total_amount,
                            "site_photos_count": len(site_photos) if site_photos else 0,
                            "site_notes": site_notes,
                            "status": "⏳ 待副總經理審核"
                        }

                        # 1. 存入工程報價資料庫
                        st.session_state.two_tier_quotations_db.append(quotation_record)

                        # 2. 自動同步連線至【全公司電子簽核中心】
                        st.session_state.pending_approvals_db.append({
                            "approval_id": f"APV-{new_id}",
                            "title": f"⚡ 工程報價審核：{p_proj} ({p_client})",
                            "category": "工程報價與專案簽核",
                            "applicant": p_prop,
                            "dept": "工程管理部",
                            "amount": f"{format_currency_text(final_total_amount, p_curr)}",
                            "target_approver": "副總經理 (Vice General Manager)",
                            "status": "⏳ 待簽核",
                            "submit_date": str(datetime.date.today()),
                            "detail_data": quotation_record
                        })

                        st.success(f"🎉 報價單 [{new_id}] 已成功建立！金額：{format_currency_text(final_total_amount, p_curr)}，已同步傳送至【全公司電子簽核中心】呈報副總經理簽核！")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫客戶名稱、工程名稱及至少一筆有效的明細！")

        # ------------------------------------------------
        # TAB 2: 修改與刪除報價單
        # ------------------------------------------------
        with tab_edit:
            st.markdown("##### ✏️ 既有工程報價單修改與維護")
            if st.session_state.two_tier_quotations_db:
                q_options = [f"{q['quot_id']} | {q['project_name']} ({q['client']}) - {q['status']}" for q in st.session_state.two_tier_quotations_db]
                selected_q_target = st.selectbox("選擇欲修改或刪除的工程報價單", q_options)
                
                target_id = selected_q_target.split(" | ")[0]
                q_data = next((q for q in st.session_state.two_tier_quotations_db if q["quot_id"] == target_id), None)

                if q_data:
                    with st.form("form_edit_quotation"):
                        eq1, eq2, eq3 = st.columns(3)
                        with eq1:
                            e_client = st.text_input("客戶名稱", value=q_data["client"])
                        with eq2:
                            e_proj = st.text_input("工程名稱", value=q_data["project_name"])
                        with eq3:
                            e_curr = st.selectbox("幣別", ["VND", "USD", "RMB", "TWD"], index=["VND", "USD", "RMB", "TWD"].index(q_data.get("currency", "VND")))

                        st.markdown("**明細項目預覽與編輯：**")
                        df_edit = pd.DataFrame(q_data["internal_items"])
                        edited_df = st.data_editor(df_edit, use_container_width=True, num_rows="dynamic")

                        e_notes = st.text_area("現場勘查說明與備註", value=q_data.get("site_notes", ""))
                        e_status = st.selectbox("簽核狀態修改", ["⏳ 待副總經理審核", "✅ 副總經理已核准", "❌ 簽核退回修改"], index=0 if "待" in q_data["status"] else (1 if "已核准" in q_data["status"] else 2))

                        btn_c1, btn_c2 = st.columns(2)
                        with btn_c1:
                            save_btn = st.form_submit_button("💾 儲存修改內容", type="primary", use_container_width=True)
                        with btn_c2:
                            del_btn = st.form_submit_button("🔥 刪除此筆報價單", type="secondary", use_container_width=True)

                        if save_btn:
                            q_data["client"] = e_client
                            q_data["project_name"] = e_proj
                            q_data["currency"] = e_curr
                            q_data["site_notes"] = e_notes
                            q_data["status"] = e_status
                            q_data["internal_items"] = edited_df.to_dict("records")
                            st.success(f"✅ 報價單 [{target_id}] 已成功更新！")
                            st.rerun()

                        if del_btn:
                            st.session_state.two_tier_quotations_db = [q for q in st.session_state.two_tier_quotations_db if q["quot_id"] != target_id]
                            st.session_state.pending_approvals_db = [a for a in st.session_state.pending_approvals_db if target_id not in a["approval_id"]]
                            st.success(f"🗑️ 報價單 [{target_id}] 及簽核紀錄已成功刪除！")
                            st.rerun()
            else:
                st.info("目前尚無工程報價單資料。")

        # ------------------------------------------------
        # TAB 3: 主管審核與標準 Excel 樣式預覽
        # ------------------------------------------------
        with tab_review:
            if st.session_state.two_tier_quotations_db:
                for q in st.session_state.two_tier_quotations_db:
                    curr_fmt = q.get('currency', 'VND')
                    with st.expander(f"📋 單號：{q['quot_id']} | 專案：{q['project_name']} | 客戶：{q['client']} | 狀態：{q['status']}", expanded=True):
                        
                        # Excel 標準框線報價單樣式 HTML 渲染
                        items_html = ""
                        for idx, item in enumerate(q["internal_items"], 1):
                            items_html += f"""
                            <tr>
                                <td style="text-align:center; border: 1px solid #333; padding: 6px;">{idx}</td>
                                <td style="border: 1px solid #333; padding: 6px;">{item.get('desc','')}</td>
                                <td style="text-align:center; border: 1px solid #333; padding: 6px;">{item.get('unit','式')}</td>
                                <td style="text-align:right; border: 1px solid #333; padding: 6px;">{item.get('qty', 1)}</td>
                                <td style="text-align:right; border: 1px solid #333; padding: 6px;">{format_currency_text(item.get('unit_price', 0), curr_fmt)}</td>
                                <td style="text-align:right; border: 1px solid #333; padding: 6px; font-weight:bold;">{format_currency_text(item.get('subtotal', 0), curr_fmt)}</td>
                                <td style="border: 1px solid #333; padding: 6px;">{item.get('source','工程項目')}</td>
                            </tr>
                            """

                        excel_quotation_html = f"""
                        <div style="border: 2px solid #111; padding: 18px; background-color: #ffffff; color: #111; font-family: Arial, sans-serif; margin-bottom: 15px;">
                            <h2 style="text-align: center; margin-bottom: 2px; color: #000;">報價單 / BẢNG BÁO GIÁ</h2>
                            <p style="text-align: center; font-size: 13px; margin-top: 0px; color: #444;">裕豐電機工業有限公司 REETECH INDUSTRIAL CO., LTD</p>
                            
                            <table style="width: 100%; border-collapse: collapse; margin-bottom: 12px; font-size: 13px;">
                                <tr>
                                    <td style="width: 50%;"><b>敬函 (Kính gửi):</b> {q['client']}</td>
                                    <td style="width: 50%;"><b>日期 (Date):</b> {q.get('date', str(datetime.date.today()))}</td>
                                </tr>
                                <tr>
                                    <td><b>ATTN:</b> {q.get('attn', 'James & LIU KUAN HSIN')}</td>
                                    <td><b>負責人 (From):</b> {q['proposer']}</td>
                                </tr>
                                <tr>
                                    <td><b>工程名稱 (Tên công trình):</b> {q['project_name']}</td>
                                    <td><b>報價單號 (Ref):</b> {q['quot_id']}</td>
                                </tr>
                            </table>

                            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                                <thead>
                                    <tr style="background-color: #f2f2f2;">
                                        <th style="border: 1px solid #333; padding: 6px; text-align:center;">項序<br>STT</th>
                                        <th style="border: 1px solid #333; padding: 6px; text-align:left;">材料與項目名稱<br>HẠNG MỤC</th>
                                        <th style="border: 1px solid #333; padding: 6px; text-align:center;">單位<br>Đ.VỊ</th>
                                        <th style="border: 1px solid #333; padding: 6px; text-align:right;">數量<br>S.LƯỢNG</th>
                                        <th style="border: 1px solid #333; padding: 6px; text-align:right;">單價<br>ĐƠN GIÁ</th>
                                        <th style="border: 1px solid #333; padding: 6px; text-align:right;">複價<br>THÀNH TIỀN</th>
                                        <th style="border: 1px solid #333; padding: 6px; text-align:left;">備註<br>GHI CHÚ</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {items_html}
                                    <tr>
                                        <td colspan="5" style="border: 1px solid #333; padding: 6px; text-align:right; font-weight:bold;">小計 / Cộng:</td>
                                        <td style="border: 1px solid #333; padding: 6px; text-align:right; font-weight:bold;">{format_currency_text(q.get('total_cost',0), curr_fmt)}</td>
                                        <td style="border: 1px solid #333;"></td>
                                    </tr>
                                    <tr>
                                        <td colspan="5" style="border: 1px solid #333; padding: 6px; text-align:right;">運雜費 / Phí vận chuyển:</td>
                                        <td style="border: 1px solid #333; padding: 6px; text-align:right;">{format_currency_text(q.get('freight_fee',0), curr_fmt)}</td>
                                        <td style="border: 1px solid #333;"></td>
                                    </tr>
                                    <tr>
                                        <td colspan="5" style="border: 1px solid #333; padding: 6px; text-align:right;">利管費 / Phí quản lý:</td>
                                        <td style="border: 1px solid #333; padding: 6px; text-align:right;">{format_currency_text(q.get('manage_fee',0), curr_fmt)}</td>
                                        <td style="border: 1px solid #333;"></td>
                                    </tr>
                                    {"<tr><td colspan='5' style='border: 1px solid #333; padding: 6px; text-align:right; color:red;'>折扣 / Giảm giá:</td><td style='border: 1px solid #333; padding: 6px; text-align:right; color:red;'>-" + format_currency_text(q.get('discount_amt',0), curr_fmt) + "</td><td style='border: 1px solid #333;'></td></tr>" if q.get('discount_amt',0) > 0 else ""}
                                    <tr>
                                        <td colspan="5" style="border: 1px solid #333; padding: 6px; text-align:right; font-weight:bold;">未稅合計 / Tổng cộng trước thuế:</td>
                                        <td style="border: 1px solid #333; padding: 6px; text-align:right; font-weight:bold; color:#0000aa;">{format_currency_text(q.get('subtotal_before_tax', q.get('customer_price',0)), curr_fmt)}</td>
                                        <td style="border: 1px solid #333;"></td>
                                    </tr>
                                    <tr>
                                        <td colspan="5" style="border: 1px solid #333; padding: 6px; text-align:right;">增值稅 / Thuế VAT ({q.get('vat_rate', 8)}%):</td>
                                        <td style="border: 1px solid #333; padding: 6px; text-align:right;">{format_currency_text(q.get('vat_amount',0), curr_fmt)}</td>
                                        <td style="border: 1px solid #333;"></td>
                                    </tr>
                                    <tr style="background-color: #fff3cd;">
                                        <td colspan="5" style="border: 1px solid #333; padding: 8px; text-align:right; font-weight:bold; font-size:15px;">總計 / TỔNG CỘNG:</td>
                                        <td style="border: 1px solid #333; padding: 8px; text-align:right; font-weight:bold; font-size:15px; color:red;">{format_currency_text(q.get('customer_price',0), curr_fmt)}</td>
                                        <td style="border: 1px solid #333;"></td>
                                    </tr>
                                </tbody>
                            </table>
                            <p style="font-size: 12px; margin-top: 10px;"><b>現場勘查備註：</b> {q.get('site_notes', '無')}</p>
                        </div>
                        """
                        
                        st.markdown(excel_quotation_html, unsafe_allow_html=True)
                        st.info(f"📌 目前簽核狀態：{q['status']} (已自動連線送至【全公司電子簽核中心】呈報副總經理)")
            else:
                st.info("目前尚無工程報價單資料。")

    # ====================================================
    # 📊 工程主管戰情室 (備用)
    # ====================================================
    else:
        st.markdown("### 📊 工程主管戰情室 (Executive Cockpit)")
        c1, c2, c3 = st.columns(3)
        c1.metric("在建工程案場", "3 案場")
        c2.metric("平均施工進度", "68.5%")
        c3.metric("本月請款金額", "1.25B VND")
        st.dataframe(pd.DataFrame(st.session_state.engineering_projects_db), use_container_width=True)

# ----------------------------------------------------
# 🔗 相容進入點
# ----------------------------------------------------
def render_engineering_page(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)
