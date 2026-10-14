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
    # 讀取子選單動作（預設為 2: 雙層報價與探勘）
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
            "銅排 Busbar 10x100mm (米)": 250000.0,
            "空氣斷路器 ACB 2000A (台)": 45000000.0,
            "塑殼斷路器 MCCB 250A (台)": 3500000.0,
            "2000A 防水不銹鋼機櫃 (座)": 85000000.0,
            "1500A 戶外控制箱體 (座)": 52000000.0,
            "PVC 管 2寸 (50米/捆)": 1200000.0,
            "控制電纜 3.5mm² (100m/卷)": 2800000.0,
            "端子排與五金配件包 (套)": 850000.0
        }

    if "two_tier_quotations_db" not in st.session_state:
        st.session_state.two_tier_quotations_db = []

    if "engineering_projects_db" not in st.session_state:
        st.session_state.engineering_projects_db = [
            {"proj_code": "PRJ-TN-2026-01", "proj_name": "西寧廠高壓配電盤擴建", "factory": "西寧廠", "budget": 1200000000, "status": "進行中"},
            {"proj_code": "PRJ-HP-2026-02", "proj_name": "海防廠動力盤統包工程", "factory": "海防廠", "budget": 850000000, "status": "進行中"}
        ]

    # 下拉選單切換 (將【雙層報價與探勘】設為第一順位預設)
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
        
        tab_prop, tab_review = st.tabs(["✍️ 現場探勘與雙層報價提案", "🔒 主管審核中心 (呈報副總經理)"])

        with tab_prop:
            with st.form("form_engineering_survey_quotation"):
                # ------------------------------------------------
                # A. 基本專案資訊
                # ------------------------------------------------
                st.markdown("##### 📝 1. 專案報價基本資訊")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    p_client = st.text_input("客戶名稱 (Client) *", value="台商越南造紙廠")
                with c2:
                    p_proj = st.text_input("專案/工程名稱 *", value="西寧廠高壓配電盤擴建案")
                with c3:
                    p_prop = st.text_input("提案人 (職稱與姓名) *", value="探勘工程師 - 陳明華")
                with c4:
                    # 💱 幣別選擇：VND, USD, RMB, TWD
                    p_curr = st.selectbox("💱 報價計價幣別 *", ["VND", "USD", "RMB", "TWD"], index=0)

                st.markdown("---")

                # ------------------------------------------------
                # B. 現場探勘材料 BOM (倉庫連線 + 現場手動輸入未在庫)
                # ------------------------------------------------
                st.markdown("##### 📦 2. 現場探勘 BOM 材料清單 (倉庫連線 + 現場手動輸入未在庫材料)")
                st.caption("💡 說明：若為倉庫既有物料請直接選取；若倉庫沒有，請選擇『➕ 現場手動新增未在庫材料』並輸入名稱與單價。")

                num_items = st.number_input("增減材料品項數量格數", min_value=1, max_value=30, value=4, step=1)

                internal_rows = []
                total_cost = 0.0
                available_parts = ["➕ 現場手動新增未在庫材料"] + list(st.session_state.warehouse_master_parts.keys())

                for i in range(1, int(num_items) + 1):
                    ic1, ic2, ic3, ic4, ic5 = st.columns([2.5, 2, 1.2, 1.5, 1.8])
                    
                    with ic1:
                        selected_part = st.selectbox(f"材料/設備品項 #{i}", available_parts, key=f"part_sel_{i}")

                    # 判斷是倉庫連線還是現場手動新增
                    if selected_part == "➕ 現場手動新增未在庫材料":
                        with ic2:
                            custom_name = st.text_input(f"手動材料名稱與規格 #{i}", placeholder="例: 特殊防爆接線盒", key=f"inote_{i}")
                        with ic3:
                            iqty = st.number_input(f"需求數量 #{i}", min_value=0.0, value=1.0, key=f"iqty_{i}")
                        with ic4:
                            c_price = st.number_input(f"手動單價 ({p_curr}) #{i}", min_value=0.0, value=500000.0 if p_curr in ["VND","TWD"] else 20.0, key=f"cprice_{i}")
                        auto_unit_price = c_price
                        part_display_name = custom_name if custom_name else f"手動未在庫材料 #{i}"
                        part_source = "現場手動新增"
                    else:
                        auto_unit_price = st.session_state.warehouse_master_parts[selected_part]
                        with ic2:
                            note_extra = st.text_input(f"規格備註 #{i}", value="", key=f"inote_{i}")
                            part_display_name = f"{selected_part} ({note_extra})" if note_extra else selected_part
                        with ic3:
                            iqty = st.number_input(f"需求數量 #{i}", min_value=0.0, value=10.0 if i <= 2 else 1.0, key=f"iqty_{i}")
                        with ic4:
                            st.text_input(f"倉庫單價 ({p_curr}) #{i}", value=f"{auto_unit_price:,.0f}" if p_curr in ["VND","TWD"] else f"{auto_unit_price:,.2f}", disabled=True, key=f"price_display_{i}")
                        part_source = "倉庫庫存連線"

                    sub = iqty * auto_unit_price
                    with ic5:
                        sub_str = f"{sub:,.0f} {p_curr}" if p_curr in ["VND","TWD"] else f"${sub:,.2f} {p_curr}"
                        st.text_input(f"小計 #{i}", value=sub_str, disabled=True, key=f"sub_display_{i}")

                    if iqty > 0 and part_display_name:
                        total_cost += sub
                        internal_rows.append({
                            "品項名稱": part_display_name,
                            "需求數量": iqty,
                            "單價": auto_unit_price,
                            "小計": sub,
                            "物料來源": part_source
                        })

                st.markdown(f"### 💰 BOM 材料加總金額：`:red[{format_currency_text(total_cost, p_curr)}]`")
                st.markdown("---")

                # ------------------------------------------------
                # C. 預估工程總金額與現場探勘照片 (呈報副總經理)
                # ------------------------------------------------
                st.markdown("##### 📸 3. 專案預估金額與現場探勘照片呈報 (供副總經理審核參考)")
                
                cust_summary = st.text_area("對外工程摘要說明", value="1. 西寧廠高壓配電盤安裝工程\n2. 現場電纜拉線與配管施工")
                
                # 預估工程總報價金額 (符合越南千位符號點號輸入格式)
                default_suggested = f"{total_cost * 1.3:,.0f}".replace(",", ".") if p_curr in ["VND","TWD"] else f"{total_cost * 1.3:,.2f}"
                cust_suggested_price_str = st.text_input(
                    f"💰 預估對外工程總報價金額 ({p_curr}) *", 
                    value=default_suggested,
                    help="直接輸入金額，系統支援越南千位點號格式 (例如: 250.000.000)"
                )

                site_photos = st.file_uploader(
                    "📷 上傳現場探勘與施工現場照片 (呈報副總經理對比審核)",
                    type=["jpg", "jpeg", "png"],
                    accept_multiple_files=True
                )
                site_notes = st.text_area("📝 現場探勘狀況與特殊施工備註", placeholder="例: 現場高壓線路走線受限，需要額外增加 15 米線槽；客戶要求週六停電施工。")

                # 提交按鈕
                if st.form_submit_button("🚀 提交探勘報價單並呈報副總經理審核", type="primary", use_container_width=True):
                    if p_client and p_proj and internal_rows:
                        clean_amt_str = str(cust_suggested_price_str).replace(".", "").replace(",", "")
                        try:
                            final_cust_price = float(clean_amt_str)
                        except Exception:
                            final_cust_price = total_cost * 1.3

                        new_id = f"QUO-2026-{len(st.session_state.two_tier_quotations_db)+1:03d}"
                        st.session_state.two_tier_quotations_db.append({
                            "quot_id": new_id, 
                            "client": p_client, 
                            "project_name": p_proj, 
                            "proposer": p_prop,
                            "currency": p_curr, 
                            "internal_items": internal_rows, 
                            "total_internal_cost": total_cost,
                            "customer_facing_summary": cust_summary, 
                            "customer_price": final_cust_price, 
                            "site_photos_count": len(site_photos) if site_photos else 0,
                            "site_notes": site_notes,
                            "status": "⏳ 待副總經理審核"
                        })
                        st.success(f"🎉 探勘報價提案 [{new_id}] 已成功提交！包含 {len(site_photos) if site_photos else 0} 張現場探勘照片，已呈報給【副總經理】進行審核！")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫客戶、專案名稱及至少一筆有效的材料明細！")

        with tab_review:
            if st.session_state.two_tier_quotations_db:
                for q in st.session_state.two_tier_quotations_db:
                    curr_fmt = q.get('currency', 'VND')
                    with st.expander(f"📌 單號：{q['quot_id']} | 專案：{q['project_name']} | 提案人：{q['proposer']} | 狀態：{q['status']}"):
                        st.write(f"**客戶**：{q['client']} | **計價幣別**：`{curr_fmt}` | **對外報價總金額**：`:red[{format_currency_text(q['customer_price'], curr_fmt)}]`")
                        st.markdown("**📦 探勘 BOM 材料清單 (倉庫連線 + 現場手動品項)：**")
                        st.dataframe(pd.DataFrame(q["internal_items"]), use_container_width=True)
                        st.write(f"**📸 現場探勘照片張數**：{q.get('site_photos_count', 0)} 張")
                        st.write(f"**📝 現場勘查說明**：{q.get('site_notes', '無')}")
                        st.info(f"目前簽核狀態：{q['status']} (副總經理可至【全公司電子簽核中心】進行簽核)")
            else:
                st.info("目前尚無雙層報價與探勘紀錄。")

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
