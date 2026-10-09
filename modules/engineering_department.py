import streamlit as st
import pandas as pd
import datetime

def render_engineering_department_page(engine=None, lang="繁體中文", **kwargs):
    sub_action = (
        kwargs.get("sub_action")
        or st.session_state.get("current_sub_action")
        or st.session_state.get("selected_sub_menu")
        or st.session_state.get("sub_menu")
        or "1"
    )
    sub_str = str(sub_action).strip()

    texts = {
        "繁體中文": {
            "title": "⚡ 裕豐電機工業 - 工程管理中心與設計部門",
            "caption": "水電工程雙層報價系統（內部成本明細與對外業主報價）、協理提案與副總/總經理多級核決。",
            "sub1": "⚡ [工程] 配電盤與工程專案雙層報價系統",
            "sub2": "⚡ [工程] 工程驗收與進度追蹤",
            "sub3": "⚡ [工程] 現場工程日報表與出工統計",
            "sub4": "🤖 [工程] AI 施工照片智慧辨識與歸檔",
            "sub5": "⚠️ [工程] 分包商與專業證照到期預警",
            "sub6": "🎨 [設計] 配電盤電氣與機構設計圖庫 Storage"
        },
        "Tiếng Việt": {
            "title": "⚡ Công ty TNHH Kỹ thuật Điện Reetech - Trung tâm Kỹ thuật",
            "caption": "Hệ thống báo giá 2 lớp, phê duyệt đa cấp.",
            "sub1": "⚡ [KT] Báo giá tủ điện 2 lớp & Phê duyệt",
            "sub2": "⚡ [KT] Theo dõi tiến độ & Nghiệm thu",
            "sub3": "⚡ [KT] Nhật ký công trình & Nhân công",
            "sub4": "🤖 [KT] AI Nhận diện & Lưu trữ ảnh thi công",
            "sub5": "⚠️ [KT] Cảnh báo hết hạn chứng chỉ",
            "sub6": "🎨 [TK] Kho bản vẽ thiết kế tủ điện Storage"
        },
        "English": {
            "title": "⚡ Reetech Industrial - Engineering Management Center",
            "caption": "Two-tier quotation system, multi-level approval workflow.",
            "sub1": "⚡ [Eng] Two-Tier Quotation & Approval",
            "sub2": "⚡ [Eng] Acceptance & Progress Tracking",
            "sub3": "⚡ [Eng] Daily Site Reports & Labor",
            "sub4": "🤖 [Eng] AI Field Photo Recognition & Archiving",
            "sub5": "⚠️ [Eng] Subcontractor & License Expiry Alerts",
            "sub6": "🎨 [Design] Electrical & Mechanical Drawing Storage"
        }
    }

    active_lang = lang if lang in texts else "繁體中文"
    t = texts[active_lang]

    st.title(t["title"])
    st.caption(t["caption"])

    # 🏭 倉庫標準零件與單價成本資料庫
    if "warehouse_master_parts" not in st.session_state:
        st.session_state.warehouse_master_parts = {
            "銅排 Busbar 10x100mm": 2.5,
            "空氣斷路器 ACB 2000A": 1850.0,
            "塑殼斷路器 MCCB 250A": 145.0,
            "2000A 防水不銹鋼機櫃": 3500.0,
            "1500A 戶外控制箱體": 2800.0,
            "PVC 管 2寸 (50米)": 45.0,
            "控制電纜 3.5mm² (100m)": 120.0,
            "端子排與五金配件組": 85.0
        }

    if "two_tier_quotations_db" not in st.session_state:
        st.session_state.two_tier_quotations_db = [
            {
                "quot_id": "QT-2026-001",
                "client": "Công ty TNHH Xây lắp Tân Thuận",
                "project_name": "西寧廠主配電盤 2000A 統包工程",
                "proposer": "協理 - 陳明華",
                "currency": "USD",
                "internal_items": [
                    {"type": "訂製機櫃", "desc": "2000A 防水不銹鋼機櫃", "qty": 2.0, "unit_price": 3500.0, "subtotal": 7000.0},
                    {"type": "水電材料", "desc": "銅排 Busbar 10x100mm", "qty": 450.0, "unit_price": 2.5, "subtotal": 1125.0}
                ],
                "total_internal_cost": 8125.0,
                "customer_facing_summary": "1. 西寧廠 2000A 主配電盤及箱體統包工程",
                "customer_price": 11500.0,
                "status": "🟢 副總已核准，待總經理/董事長確認"
            }
        ]

    if "engineering_projects_db" not in st.session_state:
        st.session_state.engineering_projects_db = [
            {"proj_code": "PRJ-TN-2026-01", "proj_name": "西寧廠高壓配電盤擴建", "factory": "西寧廠", "budget": 1200000000, "status": "進行中"}
        ]

    if "license_db" not in st.session_state:
        st.session_state.license_db = [
            {"emp_id": "EMP-001", "name": "張董事長", "license_name": "甲種電匠", "status": "🔴 30天內即將到期"}
        ]

    if "ai_photo_archive_db" not in st.session_state:
        st.session_state.ai_photo_archive_db = []

    if "drawing_storage_db" not in st.session_state:
        st.session_state.drawing_storage_db = []

    # ----------------------------------------------------
    # 1. 配電盤與工程專案雙層報價系統
    # ----------------------------------------------------
    if "1" in sub_str or "報價" in sub_str or "Quotation" in sub_str:
        st.markdown(f"### ⚙️ 1. {t['sub1']}")

        tab_prop, tab_review = st.tabs(["✍️ 建立報價提案 (內部成本與對外報價)", "🔒 主管審核與價格核定中心"])

        with tab_prop:
            with st.form("tier_quotation_form"):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    p_client = st.text_input("客戶名稱 (Client)", value="Công ty TNHH Xây lắp Tân Thuận")
                with c2:
                    p_proj = st.text_input("整體工程名稱 / 專案名稱 *", value="海防廠動力盤擴建 1500A 統包工程")
                with c3:
                    p_prop = st.text_input("提案人 (職稱與姓名) *", value="協理 - 陳明華")
                with c4:
                    p_curr = st.selectbox("計價幣別", ["USD", "VND", "NTD"])

                st.markdown("---")
                st.markdown("##### 📦 內部成本明細清單 (自動對應倉庫標準單價)")
                
                num_items = st.number_input("項目數量 (可自由增減格數)", min_value=1, max_value=30, value=5, step=1)

                internal_rows = []
                total_cost = 0.0
                available_parts = list(st.session_state.warehouse_master_parts.keys())

                for i in range(1, int(num_items) + 1):
                    ic1, ic2, ic3, ic4, ic5 = st.columns([2.5, 2, 1.5, 1.5, 1.5])
                    with ic1:
                        selected_part = st.selectbox(f"材料/機櫃 #{i}", available_parts, key=f"part_sel_{i}")
                        auto_unit_price = st.session_state.warehouse_master_parts[selected_part]
                    with ic2:
                        note_extra = st.text_input(f"規格備註 #{i}", value="", key=f"inote_{i}")
                    with ic3:
                        iqty = st.number_input(f"數量 #{i}", min_value=0.0, value=10.0 if i <= 3 else 0.0, key=f"iqty_{i}")
                    with ic4:
                        st.text_input(f"單價 #{i}", value=f"$ {auto_unit_price:,.2f}", disabled=True, key=f"price_display_{i}")
                    with ic5:
                        sub = iqty * auto_unit_price
                        st.text_input(f"小計 #{i}", value=f"$ {sub:,.2f}", disabled=True, key=f"sub_display_{i}")

                    if iqty > 0:
                        total_cost += sub
                        internal_rows.append({
                            "type": "訂製機櫃" if "機櫃" in selected_part or "箱體" in selected_part else "水電材料",
                            "desc": selected_part,
                            "note": note_extra,
                            "qty": iqty,
                            "unit_price": auto_unit_price,
                            "subtotal": sub
                        })

                st.markdown(f"### 💰 內部總成本總和：`$ {total_cost:,.2f} {p_curr}`")
                
                st.markdown("---")
                st.markdown("##### 📄 對外業主報價摘要與金額")
                cust_summary = st.text_area("對外合約摘要 (顯示給業主看的工程內容)", value="1. 專案機櫃訂製與組裝工程\n2. 廠房高低壓配電盤安裝與測試")
                cust_suggested_price = st.number_input("建議對外報價金額 (Customer Price)", min_value=0.0, value=total_cost * 1.35, step=100.0)

                if st.form_submit_button("🚀 提交報價提案", type="primary"):
                    if p_client and p_proj and internal_rows:
                        new_id = f"QT-2026-{len(st.session_state.two_tier_quotations_db)+1:03d}"
                        st.session_state.two_tier_quotations_db.append({
                            "quot_id": new_id,
                            "client": p_client,
                            "project_name": p_proj,
                            "proposer": p_prop,
                            "currency": p_curr,
                            "internal_items": internal_rows,
                            "total_internal_cost": total_cost,
                            "customer_facing_summary": cust_summary,
                            "customer_price": cust_suggested_price,
                            "status": "⏳ 待副總經理審核與價格核定"
                        })
                        st.success(f"✅ 報價提案 [{new_id}] 已成功提交！")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫客戶、專案名稱及至少一筆有效的數量明細！")

        with tab_review:
            if st.session_state.two_tier_quotations_db:
                for q in st.session_state.two_tier_quotations_db:
                    with st.expander(f"📌 單號：{q['quot_id']} | 專案：{q['project_name']} | 提案人：{q['proposer']} | 狀態：{q['status']}"):
                        st.write(f"**客戶名稱**：{q['client']} | **幣別**：{q.get('currency', 'USD')}")
                        st.write(f"**內部成本總和**：`$ {q['total_internal_cost']:,.2f}`")
                        
                        st.markdown("**📦 內部成本明細表：**")
                        st.dataframe(pd.DataFrame(q["internal_items"]), use_container_width=True)

                        st.markdown("---")
                        st.markdown(f"**對外業主報價金額**：`$ {q['customer_price']:,.2f}`")
                        st.text_area(f"對外業主合約摘要預覽 ({q['quot_id']})", value=q["customer_facing_summary"], disabled=True)

                        if "待副總經理審核" in q["status"]:
                            rc1, rc2 = st.columns(2)
                            with rc1:
                                if st.button(f"🔒 副總已核准，呈報總經理/董事長確認 {q['quot_id']}", key=f"vp_pass_{q['quot_id']}"):
                                    q["status"] = "🟢 副總已核准，待總經理/董事長最終確認"
                                    st.success(f"✅ 單號 {q['quot_id']} 已通過副總審核，已呈報總經理與董事長！")
                                    st.rerun()
                            with rc2:
                                if st.button(f"❌ 駁回並退回修改 {q['quot_id']}", key=f"vp_rej_{q['quot_id']}"):
                                    q["status"] = "🔴 已被副總退回修改"
                                    st.warning("已退回。")
                                    st.rerun()
                        elif "待總經理" in q["status"] or "待總經理/董事長" in q["status"]:
                            bc1, bc2 = st.columns(2)
                            with bc1:
                                if st.button(f"👑 總經理/董事長最終確認並拍板發行 {q['quot_id']}", key=f"board_pass_{q['quot_id']}"):
                                    q["status"] = "🎉 董事長/總經理已最終拍板發行"
                                    st.success(f"🎉 報價單 {q['quot_id']} 已獲董事長與總經理確認，可發行給業主！")
                                    st.rerun()
                            with bc2:
                                if st.button(f"❌ 退回複查 {q['quot_id']}", key=f"board_rej_{q['quot_id']}"):
                                    q["status"] = "🔴 要求重新評估成本"
                                    st.warning("已退回複查。")
                                    st.rerun()
                        else:
                            st.info(f"目前狀態：{q['status']}")
            else:
                st.info("目前尚無雙層報價紀錄。")

    # ----------------------------------------------------
    # 2. 工程驗收與進度追蹤
    # ----------------------------------------------------
    elif "2" in sub_str or "驗收" in sub_str or "Acceptance" in sub_str:
        st.markdown(f"### 📊 2. {t['sub2']}")
        st.info("即時監控工程進度與預定驗收時間。")

    # ----------------------------------------------------
    # 3. 現場工程日報表與出工統計
    # ----------------------------------------------------
    elif "3" in sub_str or "日報" in sub_str or "Daily" in sub_str:
        st.markdown(f"### 📝 3. {t['sub3']}")
        st.info("記錄每日台幹與越籍工人人數及施工進度。")

    # ----------------------------------------------------
    # 4. 🤖 AI 施工照片智慧辨識與歸檔
    # ----------------------------------------------------
    elif "4" in sub_str or "AI" in sub_str or "照片" in sub_str:
        st.markdown(f"### 🤖 4. {t['sub4']}")
        st.info("上傳施工現場照片進行 AI 辨識與歸檔。")

    # ----------------------------------------------------
    # 5. ⚠️ 分包商與專業證照到期主動預警
    # ----------------------------------------------------
    elif "5" in sub_str or "證照" in sub_str or "License" in sub_str:
        st.markdown(f"### ⚠️ 5. {t['sub5']}")
        st.info("技師與外包商專業證照到期監控。")

    # ----------------------------------------------------
    # 6. 配電盤電氣與機構設計圖庫 Storage
    # ----------------------------------------------------
    elif "6" in sub_str or "圖庫" in sub_str or "Storage" in sub_str:
        st.markdown(f"### 🎨 6. {t['sub6']}")
        st.info("管理 2D/3D 設計圖檔與 CAD 藍圖。")

    else:
        st.markdown(f"### ⚙️ 1. {t['sub1']}")
        st.info("請透過左側選單選擇工程部的各項子功能。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_engineering_department_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_engineering_department_page(engine=engine, lang=lang, **kwargs)
