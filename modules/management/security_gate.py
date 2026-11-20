# ==========================================
# 檔案路徑：modules/management/security_gate.py
# 職責：保全操作頁面（Mobile-First 四張獨立卡片：車輛進出與攜帶物品查驗、人員進出管制、訪客登記、郵件登記）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
from core import ui_theme
from modules.security import gate_repo


def _card_vehicle_cargo(engine, tenant_id: str, project_id: str | None, guard_name: str, now_vn: datetime):
    st.markdown("#### 🚗 車輛進出與攜帶物品查驗")
    st.caption("登記車輛進／出廠、里程數與隨車攜帶物品查驗結果，防範未核准物品進出。")

    approved = gate_repo.fetch_approved_dispatches(engine, tenant_id)
    disp_map = {f"{d['dispatch_no']} | {d['vehicle_plate']} ➔ {d['destination']}": d for d in approved}

    with st.form("sec_form_vehicle"):
        sel_disp_lbl = st.selectbox("關聯已核准派車單（選填）", ["無（一般進出／載貨車）"] + list(disp_map.keys()))
        sel_disp = disp_map.get(sel_disp_lbl)

        c1, c2, c3 = st.columns(3)
        with c1:
            direction = st.selectbox("進出方向*", [("OUT", "⬆️ 出廠放行"), ("IN", "⬇️ 入廠登記")], format_func=lambda x: x[1])[0]
            vehicle_plate = st.text_input("車牌號碼*", value=sel_disp["vehicle_plate"] if sel_disp else "60A-888.99")
        with c2:
            driver_user = st.text_input("駕駛／隨車人員*", value=sel_disp["driver_name"] if sel_disp and sel_disp.get("driver_name") else "")
            mileage_km = st.text_input("目前里程數 (KM)", placeholder="例：45280 km")
        with c3:
            cargo_status = st.selectbox(
                "攜帶物品查驗結果*",
                [
                    ("VERIFIED_OK", "✅ 已查驗相符／無異常"),
                    ("CARGO_WITH_SLIP", "📋 載運料件／設備（已核對單據）"),
                    ("ABNORMAL_HOLD", "🚨 物品異常／待主管確認"),
                ],
                format_func=lambda x: x[1],
            )[0]

        carried_items = st.text_area(
            "攜帶物品／載貨明細查驗*",
            value=sel_disp["reason_detail"] if sel_disp and sel_disp.get("reason_detail") else "",
            placeholder="請填寫車內攜帶工具、設備、材料或空車無載貨；若有未列單物品請註明。",
        )

        if st.form_submit_button("🚦 登記車輛進出與查驗", type="primary", use_container_width=True):
            if not vehicle_plate.strip() or not driver_user.strip() or not carried_items.strip():
                st.warning("⚠️ 請填寫車牌、駕駛／隨車人員與攜帶物品查驗明細。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                try:
                    gate_repo.log_vehicle_gate(
                        engine, tenant_id,
                        sel_disp["dispatch_no"] if sel_disp else None,
                        project_id, vehicle_plate.strip(), driver_user.strip(),
                        direction, mileage_km.strip() or "-",
                        carried_items.strip(), cargo_status, guard_name, now_vn,
                    )
                    st.success(f"✅ 已登記車輛 `{vehicle_plate.strip()}`（{'出廠' if direction == 'OUT' else '入廠'}）與攜帶物品查驗。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 登記失敗：{e}")

    df_v = gate_repo.fetch_vehicle_gate_df(engine, tenant_id)
    if not df_v.empty:
        disp_v = df_v.rename(columns={
            "t_str": "時間", "direction": "方向", "vehicle_plate": "車牌",
            "driver_or_user": "人員", "mileage_km": "里程",
            "carried_items": "攜帶物品查驗", "cargo_check_status": "查驗狀態", "dispatch_no": "派車單號",
        })
        st.dataframe(disp_v, use_container_width=True, hide_index=True)


def _card_personnel_gate(engine, tenant_id: str, project_id: str | None, guard_name: str, now_vn: datetime):
    st.markdown("#### 🪪 人員進出管制")
    st.caption("登記員工、外包人員或點工人員入廠／出廠時段與隨身攜帶物品備註。")
    with st.form("sec_form_personnel"):
        c1, c2, c3 = st.columns(3)
        with c1:
            ptype = st.selectbox("人員類別*", ["正式員工", "外包人員", "點工人員", "廠商／其他"])
            pname = st.text_input("人員姓名*", placeholder="請輸入姓名")
        with c2:
            cdept = st.text_input("部門／外包商名稱", placeholder="例：工程部／SUB-01")
            direction = st.selectbox("進出方向*", [("IN", "⬇️ 入廠"), ("OUT", "⬆️ 出廠")], format_func=lambda x: x[1])[0]
        with c3:
            note = st.text_input("隨身物品／備註", placeholder="例：工具箱／無攜帶")

        if st.form_submit_button("✅ 登記人員進出", type="primary", use_container_width=True):
            if not pname.strip():
                st.warning("⚠️ 請輸入人員姓名。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                try:
                    gate_repo.log_personnel_gate(
                        engine, tenant_id, project_id, ptype, pname.strip(),
                        cdept.strip() or "-", direction, note.strip() or "-", guard_name, now_vn,
                    )
                    st.success(f"✅ 已登記【{pname.strip()}】{'入廠' if direction == 'IN' else '出廠'}。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 登記失敗：{e}")

    df_p = gate_repo.fetch_personnel_gate_df(engine, tenant_id)
    if not df_p.empty:
        disp_p = df_p.rename(columns={
            "t_str": "時間", "direction": "方向", "person_type": "類別",
            "person_name": "姓名", "company_or_dept": "部門／單位", "note": "備註",
        })
        st.dataframe(disp_p, use_container_width=True, hide_index=True)


def _card_visitor_reg(engine, tenant_id: str, guard_name: str, now_vn: datetime):
    st.markdown("#### 🧾 訪客登記")
    st.caption("登記來賓／客戶／廠商入廠資訊、配發識別證，並於離廠時辦理簽退。")
    with st.form("sec_form_visitor"):
        c1, c2 = st.columns(2)
        with c1:
            vname = st.text_input("訪客姓名*", placeholder="請輸入來賓姓名")
            cname = st.text_input("來賓公司名稱*", placeholder="例：西寧工業區客戶")
            hcont = st.text_input("接待人員／分機*", placeholder="例：陳總／工程部")
        with c2:
            bno = st.text_input("訪客證編號", placeholder="例：V-08")
            vpur = st.text_input("來訪事由*", placeholder="例：配電盤驗收／設備洽談")

        if st.form_submit_button("📥 訪客入廠登記", type="primary", use_container_width=True):
            if not vname.strip() or not cname.strip() or not hcont.strip() or not vpur.strip():
                st.warning("⚠️ 請填寫訪客姓名、公司、接待人員與來訪事由。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                try:
                    vid = gate_repo.create_visitor_log(
                        engine, tenant_id, vname.strip(), cname.strip(),
                        hcont.strip(), vpur.strip(), bno.strip() or "-", guard_name, now_vn,
                    )
                    st.success(f"✅ 已登記訪客 `{vid}`（{vname.strip()}）入廠。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 登記失敗：{e}")

    df_vis = gate_repo.fetch_visitor_df(engine, tenant_id)
    if not df_vis.empty:
        disp_vis = df_vis.rename(columns={
            "visitor_id": "訪客單號", "visitor_name": "訪客姓名", "company_name": "公司",
            "host_contact": "接待人", "visit_purpose": "事由", "badge_no": "證號",
            "status": "狀態", "cin_str": "入廠時間",
        })
        st.dataframe(disp_vis, use_container_width=True, hide_index=True)

        in_site = df_vis[df_vis["status"] == "IN_SITE"]["visitor_id"].tolist()
        if in_site:
            sel_vid = st.selectbox("選擇離廠訪客單號辦理簽退", in_site, key="sec_vis_out_sel")
            if st.button("🚪 確認訪客離廠簽退", key="sec_vis_out_btn", use_container_width=True):
                gate_repo.checkout_visitor_log(engine, tenant_id, sel_vid, now_vn)
                st.success(f"✅ 已完成訪客 `{sel_vid}` 離廠簽退。")
                st.rerun()


def _card_mail_package(engine, tenant_id: str, guard_name: str, now_vn: datetime):
    st.markdown("#### 📦 郵件／包裹登記")
    st.caption("登記快遞、掛號信件或廠區包裹收件，並於收件人領取時完成簽收。")
    with st.form("sec_form_mail"):
        c1, c2 = st.columns(2)
        with c1:
            sender = st.text_input("寄件人／快遞業者*", placeholder="例：Giao Hàng Nhanh / 郵局掛號")
            rname = st.text_input("收件人姓名*", placeholder="請輸入收件人")
        with c2:
            rdept = st.text_input("收件人部門", placeholder="例：管理部／工程部")
            isum = st.text_input("郵件／包裹內容摘要*", placeholder="例：合約文件／樣品零件箱")

        if st.form_submit_button("📬 登記收件入庫", type="primary", use_container_width=True):
            if not sender.strip() or not rname.strip() or not isum.strip():
                st.warning("⚠️ 請填寫寄件／快遞、收件人與內容摘要。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                try:
                    pid = gate_repo.create_mail_package_log(
                        engine, tenant_id, sender.strip(), rname.strip(),
                        rdept.strip() or "-", isum.strip(), guard_name, now_vn,
                    )
                    st.success(f"✅ 已登記郵件／包裹 `{pid}` 收件。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 登記失敗：{e}")

    df_m = gate_repo.fetch_mail_package_df(engine, tenant_id)
    if not df_m.empty:
        disp_m = df_m.rename(columns={
            "package_id": "包裹單號", "carrier_or_sender": "寄件／快遞",
            "recipient_name": "收件人", "recipient_dept": "部門",
            "item_summary": "內容摘要", "status": "狀態",
            "picked_by": "領取人", "r_str": "收件時間",
        })
        st.dataframe(disp_m, use_container_width=True, hide_index=True)

        waiting = df_m[df_m["status"] == "RECEIVED"]["package_id"].tolist()
        if waiting:
            sel_pid = st.selectbox("選擇待領取包裹單號", waiting, key="sec_pkg_pick_sel")
            picked_who = st.text_input("實際領取人姓名*", placeholder="請輸入領取人姓名", key="sec_pkg_picker")
            if st.button("✍️ 確認包裹領取簽收", key="sec_pkg_pick_btn", type="primary", use_container_width=True):
                if not picked_who.strip():
                    st.warning("⚠️ 請填寫實際領取人姓名。")
                else:
                    gate_repo.mark_package_picked(engine, tenant_id, sel_pid, picked_who.strip(), now_vn)
                    st.success(f"✅ 已完成包裹 `{sel_pid}` 領取簽收（領取人：{picked_who.strip()}）。")
                    st.rerun()


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    guard_name = st.session_state.get("user_name") or "保全人員"
    project_id = st.session_state.get("active_project_id")
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 🛡️ 保全操作頁面")
    st.caption("請點選下方功能卡片操作車輛進出與攜帶物品查驗、人員進出、訪客登記或郵件包裹登記。")
    gate_repo.ensure_security_tables(engine)

    if "sec_active_card" not in st.session_state:
        st.session_state["sec_active_card"] = "VEHICLE"

    active = st.session_state["sec_active_card"]

    cards = [
        ("VEHICLE", "🚗 車輛與物品查驗", "進出廠、里程與攜帶物品"),
        ("PERSONNEL", "🪪 人員進出管制", "員工、外包與點工進出"),
        ("VISITOR", "🧾 訪客登記", "來賓入廠登記與離廠簽退"),
        ("MAIL", "📦 郵件／包裹登記", "快遞信件收件與領取簽收"),
    ]

    cols = st.columns(4)
    for idx, (ckey, ctitle, csub) in enumerate(cards):
        with cols[idx]:
            with st.container(border=True):
                st.markdown(f"**{ctitle}**")
                st.caption(csub)
                is_sel = active == ckey
                lbl = "✅ 使用中" if is_sel else "開啟卡片"
                if st.button(
                    lbl,
                    key=f"sec_card_btn_{ckey}",
                    type="primary" if is_sel else "secondary",
                    use_container_width=True,
                ):
                    st.session_state["sec_active_card"] = ckey
                    st.rerun()

    st.divider()

    with st.container(border=True):
        if active == "PERSONNEL":
            _card_personnel_gate(engine, tenant_id, project_id, guard_name, now_vn)
        elif active == "VISITOR":
            _card_visitor_reg(engine, tenant_id, guard_name, now_vn)
        elif active == "MAIL":
            _card_mail_package(engine, tenant_id, guard_name, now_vn)
        else:
            _card_vehicle_cargo(engine, tenant_id, project_id, guard_name, now_vn)


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
