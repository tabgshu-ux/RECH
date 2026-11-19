# ==========================================
# 檔案路徑：modules/it_system/org_puzzle/mount_ui.py
# 職責：Tab 2 功能拼圖掛載與 Tab 3 新拼圖註冊介面
# ==========================================

import streamlit as st
from modules.it_system.org_puzzle import repo


def render_mount_tab(engine, tenant_id: str, active_nodes: list[dict], registry: list[dict]):
    st.markdown("#### 🧩 為指定 L1～L4 節點掛載功能拼圖")
    if not active_nodes:
        st.info("請先建立或套用組織節點。")
        return

    node_map = {n["node_code"]: n for n in active_nodes}
    options = {}
    for n in active_nodes:
        p_name = node_map.get(n.get("parent_node_code"), {}).get("node_name")
        prefix = f"{p_name} ➔ " if p_name else ""
        options[f"[{n['level_tier']}] {prefix}{n['node_name']}"] = n

    target = options[st.selectbox("選擇目標節點", list(options.keys()), key="mount_node_sel")]
    cur_feats, cur_role = repo.load_node_mount(engine, tenant_id, target["node_code"])

    with st.form(f"form_mount_{target['node_code']}"):
        role_in = st.text_input("登入後直達角色代碼（選填，如 FIELD_ENGINEER / SECURITY_GUARD）", value=cur_role)
        st.divider()

        grouped = {}
        for item in registry:
            grouped.setdefault(item.get("group") or "通用拼圖", []).append(item)

        picked = []
        for grp, items in grouped.items():
            st.markdown(f"**{grp}**")
            cols = st.columns(2)
            for idx, feat in enumerate(items):
                with cols[idx % 2]:
                    if st.checkbox(feat["name"], value=(feat["key"] in cur_feats), key=f"m_{target['node_code']}_{feat['key']}"):
                        picked.append(feat["key"])

        if st.form_submit_button("💾 儲存功能掛載", type="primary", use_container_width=True):
            try:
                repo.save_node_mount(engine, tenant_id, target["node_code"], picked, role_in.strip().upper() or None)
                st.success(f"✅ 已儲存【{target['node_name']}】的拼圖掛載。")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 儲存失敗: {e}")


def render_register_tab(engine):
    st.markdown("#### ➕ 註冊新功能拼圖")
    with st.form("form_reg_puzzle"):
        c1, c2 = st.columns(2)
        with c1:
            fkey = st.text_input("拼圖代碼", placeholder="例如: feat_warehouse_stock_check")
            fname = st.text_input("拼圖名稱", placeholder="例如: 📦 即時庫存查詢")
        with c2:
            fgrp = st.text_input("群組分類", value="擴充拼圖")
            fmod = st.text_input("模組路徑（選填）", placeholder="例如: modules.warehouse.stock_check")

        if st.form_submit_button("🧩 註冊拼圖", type="primary", use_container_width=True):
            if not fkey.strip() or not fname.strip():
                st.warning("⚠️ 請填寫拼圖代碼與名稱。")
            else:
                try:
                    repo.register_puzzle(engine, fkey.strip(), fname.strip(), fgrp.strip() or "擴充拼圖", fmod.strip() or None)
                    st.success(f"✅ 已註冊【{fname.strip()}】。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 註冊失敗: {e}")
