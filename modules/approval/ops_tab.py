# ==========================================
# 檔案路徑：modules/approval/ops_tab.py
# 職責：2. 採購／倉庫／外出簽核（Mobile-First 三張獨立卡片，點選卡片展開專屬表單）
# ==========================================

from datetime import datetime, time
import streamlit as st
from modules.approval.workflow_repo import create_ops_request


def _fmt_vnd(v: float | int) -> str:
    return f"{round(float(v or 0)):,}".replace(",", ".")


def _render_procurement_card(engine, tenant_id: str, user_name: str, user_role: str, project_id: str | None, now_vn: datetime):
    st.markdown("#### 🛒 採購與請款申請 (PR/PO)")
    st.caption("適用料件採購、設備請款與供應商付款簽核。")
    with st.form("card_form_procurement"):
        title_item = st.text_input("採購品項／請款主旨*", placeholder="例：西寧廠區主配電盤銅排採購")
        vendor_name = st.text_input("供應商／廠商名稱", placeholder="例：Công ty TNHH Thiết Bị Điện...")
        amount_vnd = st.number_input("請購／請款金額 (VND)*", min_value=0, value=0, step=500000)
        exec_date = st.date_input("預計需求／請款日期", value=now_vn.date())
        detail_text = st.text_area("規格數量與用途說明*", placeholder="例：銅排 40x5mm 共 20 支，用於專案 PRJ-2026-01 配電盤組裝。")

        if st.form_submit_button("📨 送出採購請款簽核", type="primary", use_container_width=True):
            if not title_item.strip() or not detail_text.strip():
                st.warning("⚠️ 請填寫採購主旨與詳細說明。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                full_detail = f"廠商：{vendor_name.strip() or '-'}｜說明：{detail_text.strip()}"
                try:
                    req_no = create_ops_request(
                        engine, tenant_id, user_name, user_role, project_id,
                        "PROCUREMENT", "採購與請款申請單 (PR/PO)",
                        title_item.strip(), float(amount_vnd),
                        datetime.combine(exec_date, time(8, 0)), full_detail, now_vn,
                    )
                    st.success(f"✅ 已送出採購單 `{req_no}`（金額：{_fmt_vnd(amount_vnd)} ₫）。")
                except Exception as e:
                    st.error(f"❌ 送出失敗：{e}")


def _render_warehouse_card(engine, tenant_id: str, user_name: str, user_role: str, project_id: str | None, now_vn: datetime):
    st.markdown("#### 🏭 倉庫領料／調撥簽核")
    st.caption("適用工地領料、跨倉調撥與餘料退庫簽核。")
    with st.form("card_form_warehouse"):
        wh_action = st.selectbox("作業類型*", ["工地領料出庫", "跨倉庫／案場調撥", "工地餘料退庫"])
        title_item = st.text_input("料號／材料名稱與數量*", placeholder="例：CV 3x150mm² 電纜 120 公尺")
        wh_route = st.text_input("來源倉／目的案場", placeholder="例：總倉 WH-01 ➔ 西寧案場")
        exec_date = st.date_input("預計領料／調撥日期", value=now_vn.date())
        detail_text = st.text_area("領調事由與專案關聯*", placeholder="請說明施工區段或緊急領料原因...")

        if st.form_submit_button("📨 送出倉庫簽核", type="primary", use_container_width=True):
            if not title_item.strip() or not detail_text.strip():
                st.warning("⚠️ 請填寫材料名稱數量與領調事由。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                subj = f"[{wh_action}] {title_item.strip()}"
                full_detail = f"路徑：{wh_route.strip() or '-'}｜說明：{detail_text.strip()}"
                try:
                    req_no = create_ops_request(
                        engine, tenant_id, user_name, user_role, project_id,
                        "WAREHOUSE", "倉庫領料／跨庫調撥簽核",
                        subj, 0.0, datetime.combine(exec_date, time(8, 0)),
                        full_detail, now_vn,
                    )
                    st.success(f"✅ 已送出倉庫簽核單 `{req_no}`。")
                except Exception as e:
                    st.error(f"❌ 送出失敗：{e}")


def _render_outing_card(engine, tenant_id: str, user_name: str, user_role: str, project_id: str | None, now_vn: datetime):
    st.markdown("#### 🚶 人員外出／差旅簽核")
    st.caption("適用外勤會勘、客戶拜訪、銀行／政府洽公等外出報備。")
    with st.form("card_form_outing"):
        title_item = st.text_input("外出地點／拜訪對象*", placeholder="例：平陽工業區客戶端會勘")
        out_date = st.date_input("外出日期", value=now_vn.date())
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            t_start = st.time_input("出發時間", value=time(8, 30), step=900)
        with c_t2:
            t_end = st.time_input("預計返回", value=time(17, 0), step=900)
        detail_text = st.text_area("外出事由說明*", placeholder="請填寫會勘項目、洽公內容或差旅備註...")

        if st.form_submit_button("📨 送出外出簽核", type="primary", use_container_width=True):
            s_dt = datetime.combine(out_date, t_start)
            e_dt = datetime.combine(out_date, t_end)
            if e_dt <= s_dt:
                st.warning("⚠️ 預計返回時間必須晚於出發時間。")
            elif not title_item.strip() or not detail_text.strip():
                st.warning("⚠️ 請填寫外出地點與事由說明。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                full_detail = f"時段：{s_dt.strftime('%H:%M')} - {e_dt.strftime('%H:%M')}｜事由：{detail_text.strip()}"
                try:
                    req_no = create_ops_request(
                        engine, tenant_id, user_name, user_role, project_id,
                        "OUTING", "人員外出／差旅簽核",
                        title_item.strip(), 0.0, s_dt, full_detail, now_vn,
                    )
                    st.success(f"✅ 已送出外出簽核單 `{req_no}`。")
                except Exception as e:
                    st.error(f"❌ 送出失敗：{e}")


def render(engine, tenant_id: str, user_name: str, user_role: str, project_id: str | None, now_vn: datetime):
    st.markdown("#### 📦 2. 營運簽核卡片中心（採購／倉庫／外出）")
    st.caption("請點選下方功能卡片開啟對應表單，方便手機單手操作。")

    if "ops_active_card" not in st.session_state:
        st.session_state["ops_active_card"] = "PROCUREMENT"

    active_card = st.session_state["ops_active_card"]

    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("### 🛒 採購請款")
            st.caption("PR/PO 採購與請款審核")
            btn_lbl = "✅ 目前選取：採購請款" if active_card == "PROCUREMENT" else "開啟採購請款卡片"
            if st.button(btn_lbl, key="pick_card_proc", type="primary" if active_card == "PROCUREMENT" else "secondary", use_container_width=True):
                st.session_state["ops_active_card"] = "PROCUREMENT"
                st.rerun()

    with c2:
        with st.container(border=True):
            st.markdown("### 🏭 倉庫簽核")
            st.caption("工地領料、調撥與退庫")
            btn_lbl = "✅ 目前選取：倉庫簽核" if active_card == "WAREHOUSE" else "開啟倉庫簽核卡片"
            if st.button(btn_lbl, key="pick_card_wh", type="primary" if active_card == "WAREHOUSE" else "secondary", use_container_width=True):
                st.session_state["ops_active_card"] = "WAREHOUSE"
                st.rerun()

    with c3:
        with st.container(border=True):
            st.markdown("### 🚶 外出簽核")
            st.caption("工地會勘、拜訪與洽公")
            btn_lbl = "✅ 目前選取：外出簽核" if active_card == "OUTING" else "開啟外出簽核卡片"
            if st.button(btn_lbl, key="pick_card_out", type="primary" if active_card == "OUTING" else "secondary", use_container_width=True):
                st.session_state["ops_active_card"] = "OUTING"
                st.rerun()

    st.divider()

    with st.container(border=True):
        if active_card == "WAREHOUSE":
            _render_warehouse_card(engine, tenant_id, user_name, user_role, project_id, now_vn)
        elif active_card == "OUTING":
            _render_outing_card(engine, tenant_id, user_name, user_role, project_id, now_vn)
        else:
            _render_procurement_card(engine, tenant_id, user_name, user_role, project_id, now_vn)
