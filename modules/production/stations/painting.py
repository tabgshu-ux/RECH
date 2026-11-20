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
    user_name = st.session_state.get("user_name") or "塗裝工段"
    project_id = st.session_state.get("active_project_id")
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 🎨 塗裝烤漆工作站")
    st.caption("接收設計圖表面塗裝要求與待烤料件，登記前處理、粉體烤漆與完工數量。")
    ensure_station_tables(engine)

    df = load_station_orders(engine, tenant_id, "PAINTING")
    disp = df.rename(columns={
        "wo_no": "工單號", "project_id": "專案", "drawing_no": "設計圖號",
        "drawing_rev": "圖版", "item_name": "生產料件", "spec_summary": "色號／膜厚規格",
        "required_qty": "需求數", "completed_qty": "已完工", "station_status": "工站狀態",
        "ecn_alert": "ECN變更提示", "updated_by": "經辦",
    })
    st.dataframe(disp, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("#### 📥 接收設計圖建立塗裝工單")
            with st.form("pt_recv_form"):
                dno = st.text_input("設計圖號*", placeholder="例：DWG-PNL-630A-02")
                drev = st.text_input("圖面版本", value="Rev.A")
                iname = st.text_input("待塗裝料件名稱*", placeholder="例：630A 配電盤櫃體與門板")
                spec = st.text_input("烤漆色號／膜厚規格", placeholder="例：RAL 7032 粉體烤漆 80μm")
                rqty = st.number_input("需求數量*", min_value=1, value=1, step=1)
                ecn = st.text_input("ECN 變更註記（選填）", placeholder="無則免填")
                if st.form_submit_button("✅ 確認接圖並開立塗裝工單", type="primary", use_container_width=True):
                    if not dno.strip() or not iname.strip() or not engine:
                        st.warning("⚠️ 請填寫設計圖號、待塗裝料件名稱並確認資料庫連線。")
                    else:
                        wono = dispatch_from_design(engine, tenant_id, project_id, dno.strip(), drev.strip() or "Rev.A", iname.strip(), spec.strip() or "-", int(rqty), "PAINTING", ecn.strip() or None, user_name, now_vn)
                        st.success(f"✅ 已建立塗裝工單 `{wono}`。")
                        st.rerun()

    with c2:
        with st.container(border=True):
            st.markdown("#### 🎨 塗裝完工進度回報")
            wono_list = df["wo_no"].tolist()
            with st.form("pt_prog_form"):
                sel_wo = st.selectbox("選擇塗裝工單", wono_list)
                cqty = st.number_input("累計完工數量", min_value=0, value=0, step=1)
                st_val = st.selectbox("工站狀態", ["WAITING_START", "IN_PROGRESS", "COMPLETED_FOR_WIRING"])
                if st.form_submit_button("💾 更新塗裝完工進度", type="primary", use_container_width=True):
                    if not engine:
                        st.error("❌ 尚未連線資料庫。")
                    else:
                        update_station_progress(engine, tenant_id, sel_wo, int(cqty), st_val, user_name, now_vn)
                        st.success(f"✅ 已更新工單 `{sel_wo}` 進度。")
                        st.rerun()


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
