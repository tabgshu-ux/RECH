from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
from core import ui_theme
from modules.production.stations.station_repo import (
    dispatch_from_design,
    ensure_station_tables,
    load_station_orders,
    update_station_progress,
)


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "鈑金工段"
    project_id = st.session_state.get("active_project_id")
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 🔩 鈑金加工工作站")
    st.caption("接收設計部設計圖與鈑金料件需求，進行剪折、沖孔、焊接與完工數量回報。")
    ensure_station_tables(engine)

    df = load_station_orders(engine, tenant_id, "SHEET_METAL")
    disp = df.rename(columns={
        "wo_no": "工單號", "project_id": "專案", "drawing_no": "設計圖號",
        "drawing_rev": "圖版", "item_name": "生產料件", "spec_summary": "材質／規格",
        "required_qty": "需求數", "completed_qty": "已完工", "station_status": "工站狀態",
        "ecn_alert": "ECN變更提示", "updated_by": "經辦",
    })
    st.dataframe(disp, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("#### 📥 接收設計圖建立鈑金生產單")
            with st.form("sm_recv_form"):
                dno = st.text_input("設計圖號*", placeholder="例：DWG-PNL-630A-01")
                drev = st.text_input("圖面版本", value="Rev.A")
                iname = st.text_input("生產料件名稱*", placeholder="例：630A 配電盤櫃體")
                spec = st.text_input("板材規格／備註", placeholder="例：SPCC 2.0mm 折彎焊接")
                rqty = st.number_input("需求數量*", min_value=1, value=1, step=1)
                ecn = st.text_input("ECN 變更註記（選填）", placeholder="無則免填")
                if st.form_submit_button("✅ 確認接圖並開立鈑金工單", type="primary", use_container_width=True):
                    if not dno.strip() or not iname.strip() or not engine:
                        st.warning("⚠️ 請填寫設計圖號、生產料件名稱並確認資料庫連線。")
                    else:
                        wono = dispatch_from_design(engine, tenant_id, project_id, dno.strip(), drev.strip() or "Rev.A", iname.strip(), spec.strip() or "-", int(rqty), "SHEET_METAL", ecn.strip() or None, user_name, now_vn)
                        st.success(f"✅ 已建立鈑金工單 `{wono}`。")
                        st.rerun()

    with c2:
        with st.container(border=True):
            st.markdown("#### 🔧 鈑金生產進度回報")
            wono_list = df["wo_no"].tolist()
            with st.form("sm_prog_form"):
                sel_wo = st.selectbox("選擇鈑金工單", wono_list)
                cqty = st.number_input("累計完工數量", min_value=0, value=0, step=1)
                st_val = st.selectbox("工站狀態", ["WAITING_START", "IN_PROGRESS", "COMPLETED_FOR_PAINT"])
                if st.form_submit_button("💾 更新鈑金完工進度", type="primary", use_container_width=True):
                    if not engine:
                        st.error("❌ 尚未連線資料庫。")
                    else:
                        update_station_progress(engine, tenant_id, sel_wo, int(cqty), st_val, user_name, now_vn)
                        st.success(f"✅ 已更新工單 `{sel_wo}` 進度。")
                        st.rerun()


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
