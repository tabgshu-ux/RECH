# ==========================================
# 檔案路徑：modules/it_system/org_puzzle/mount_ui.py
# 職責：系統設定 - Tab 2 功能拼圖掛載（依勾選先後編號 1. 2. 3. 4...）與 Tab 3 拼圖註冊管理
# ==========================================

import streamlit as st
from sqlalchemy import text
from modules.it_system.org_puzzle import repo


def _load_role_landings(engine, tenant_id: str) -> list[dict]:
    if not engine:
        return []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT m.node_code, m.landing_role_code, m.mounted_features, n.node_name, n.level_tier
                    FROM sys_tenant_node_mounts m
                    LEFT JOIN sys_tenant_org_nodes n
                      ON m.tenant_id = n.tenant_id AND m.node_code = n.node_code
                    WHERE m.tenant_id = :tid
                      AND m.landing_role_code IS NOT NULL
                      AND m.landing_role_code <> ''
                    ORDER BY m.landing_role_code ASC
                """),
                {"tid": tenant_id},
            ).fetchall()
            return [r._asdict() for r in rows]
    except Exception:
        return []


def _update_or_toggle_puzzle(
    engine,
    feature_key: str,
    feature_name: str,
    feature_group: str,
    module_path: str | None,
    is_active: bool,
):
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE sys_feature_registry
                SET feature_name = :n,
                    feature_group = :g,
                    module_path = :m,
                    is_active = :act
                WHERE feature_key = :k
            """),
            {"k": feature_key, "n": feature_name, "g": feature_group, "m": module_path, "act": is_active},
        )


def render_mount_tab(engine, tenant_id: str, active_nodes: list[dict], registry: list[dict]):
    repo.sync_default_registry(engine)
    reg_list = repo.load_registry(engine) or registry

    st.markdown("#### 🧩 為指定 L1～L4 節點掛載功能拼圖（依勾選先後排序 1. 2. 3. 4...）")
    if not active_nodes:
        st.info("請先在「1. 組織樹管理」建立或套用組織節點。")
        return

    node_map = {n["node_code"]: n for n in active_nodes}
    options = {}
    for n in active_nodes:
        p_name = node_map.get(n.get("parent_node_code"), {}).get("node_name")
        prefix = f"{p_name} ➔ " if p_name else ""
        options[f"{prefix}{n['node_name']}"] = n

    target = options[st.selectbox("選擇掛載目標節點", list(options.keys()), key="mount_node_sel")]
    node_code = target["node_code"]
    cur_feats, cur_role = repo.load_node_mount(engine, tenant_id, node_code)

    order_state_key = f"mount_order_{tenant_id}_{node_code}"
    node_loaded_flag = f"mount_order_loaded_{tenant_id}_{node_code}"
    valid_keys = [str(f["key"]) for f in reg_list if f.get("key")]
    valid_set = set(valid_keys)
    feat_name_map = {str(f["key"]): str(f.get("name") or f["key"]) for f in reg_list if f.get("key")}

    if node_loaded_flag not in st.session_state:
        st.session_state[node_loaded_flag] = True
        # 保留 cur_feats 原有順序作為初始排序
        st.session_state[order_state_key] = [str(k) for k in (cur_feats or []) if str(k) in valid_set]

    ordered_keys: list[str] = [k for k in st.session_state.get(order_state_key, []) if k in valid_set]
    rank_map: dict[str, int] = {k: idx + 1 for idx, k in enumerate(ordered_keys)}

    # 頂部即時顯示目前勾選順序：1. ... 2. ... 3. ...
    if ordered_keys:
        order_preview = " ".join([f"**{idx + 1}.** {feat_name_map.get(k, k)}" for idx, k in enumerate(ordered_keys)])
        st.markdown(f"📌 **目前勾選排序（1. 2. 3. 4...）：** {order_preview}")
    else:
        st.caption("📌 尚未勾選功能；勾選後會依勾選先後標示 1.、2.、3.、4. 編號。")

    b_col1, b_col2, _ = st.columns([1.6, 1.6, 3.8])
    with b_col1:
        if st.button("🔄 重設為已存檔順序", key=f"reset_order_{tenant_id}_{node_code}"):
            st.session_state[order_state_key] = [str(k) for k in (cur_feats or []) if str(k) in valid_set]
            for k in valid_keys:
                st.session_state[f"m_{node_code}_{k}"] = k in (cur_feats or [])
            st.rerun()
    with b_col2:
        if st.button("🧹 清除全部勾選", key=f"clear_order_{tenant_id}_{node_code}"):
            st.session_state[order_state_key] = []
            for k in valid_keys:
                st.session_state[f"m_{node_code}_{k}"] = False
            st.rerun()

    role_in = st.text_input(
        "登入後自動直達此節點的角色代碼（選填，例如：FIELD_ENGINEER / SECURITY_GUARD）",
        value=cur_role,
        key=f"role_in_{tenant_id}_{node_code}",
    )
    st.divider()

    grouped: dict[str, list[dict]] = {}
    for item in reg_list:
        grouped.setdefault(item.get("group") or "通用拼圖", []).append(item)

    updated_order: list[str] = list(ordered_keys)

    for grp, items in grouped.items():
        st.markdown(f"**{grp}**")
        cols = st.columns(2)
        for idx, feat in enumerate(items):
            fkey = str(feat["key"])
            fname = str(feat.get("name") or fkey)
            chk_key = f"m_{node_code}_{fkey}"

            if chk_key not in st.session_state:
                st.session_state[chk_key] = fkey in rank_map

            seq_num = rank_map.get(fkey)
            label_str = f"**{seq_num}.** {fname} (`{fkey}`)" if seq_num else f"{fname} (`{fkey}`)"

            with cols[idx % 2]:
                is_checked = st.checkbox(label_str, key=chk_key)

            if is_checked and fkey not in updated_order:
                updated_order.append(fkey)
            elif (not is_checked) and fkey in updated_order:
                updated_order.remove(fkey)

    if updated_order != ordered_keys:
        st.session_state[order_state_key] = updated_order
        st.rerun()

    st.divider()
    if st.button("💾 儲存功能掛載與排序設定", type="primary", use_container_width=True, key=f"btn_save_mount_{tenant_id}_{node_code}"):
        try:
            repo.save_node_mount(engine, tenant_id, node_code, updated_order, role_in.strip().upper() or None)
            st.success(f"✅ 已依勾選順序儲存【{target['node_name']}】共 {len(updated_order)} 項功能拼圖。")
            st.rerun()
        except Exception as e:
            st.error(f"❌ 儲存失敗: {e}")

    st.divider()
    st.markdown("#### 🎯 目前已設定「登入後自動直達」的角色清單")
    landings = _load_role_landings(engine, tenant_id)
    if not landings:
        st.caption("目前尚無角色設定登入直達。")
    else:
        for item in landings:
            st.markdown(
                f"- 角色代碼 **`{item['landing_role_code']}`** ➔ "
                f"**{item.get('node_name') or item['node_code']}** "
                f"（掛載：`{item.get('mounted_features') or '無'}`）"
            )


def render_register_tab(engine):
    repo.sync_default_registry(engine)
    st.markdown("#### ➕ 註冊新功能拼圖")
    with st.form("form_reg_puzzle"):
        c1, c2 = st.columns(2)
        with c1:
            fkey = st.text_input("拼圖代碼 (feature_key)", placeholder="例如: feat_custom_tool")
            fname = st.text_input("拼圖顯示名稱", placeholder="例如: 🔧 自訂工具")
        with c2:
            fgrp = st.text_input("功能群組分類", value="擴充拼圖")
            fmod = st.text_input("模組路徑（選填）", placeholder="例如: modules.custom.tool")

        if st.form_submit_button("🧩 註冊新拼圖", type="primary", use_container_width=True):
            if not fkey.strip() or not fname.strip():
                st.warning("⚠️ 請填寫拼圖代碼與名稱。")
            else:
                try:
                    repo.register_puzzle(engine, fkey.strip(), fname.strip(), fgrp.strip() or "擴充拼圖", fmod.strip() or None)
                    st.success(f"✅ 已註冊【{fname.strip()}】。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 註冊失敗: {e}")

    st.divider()
    st.markdown("#### ✏️ 修改或停用已註冊拼圖")
    if not engine:
        return
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT feature_key, feature_name, feature_group, module_path, is_active FROM sys_feature_registry ORDER BY id ASC")
            ).fetchall()
            all_reg = [r._asdict() for r in rows]
    except Exception:
        all_reg = []

    if not all_reg:
        st.caption("目前無已註冊拼圖。")
        return

    reg_map = {f"{r['feature_name']} ({r['feature_key']}){'' if r.get('is_active', True) else ' [已停用]'}": r for r in all_reg}
    chosen_reg = reg_map[st.selectbox("選擇要編輯的拼圖", list(reg_map.keys()), key="edit_reg_sel")]

    with st.form(f"form_edit_reg_{chosen_reg['feature_key']}"):
        u_name = st.text_input("拼圖名稱", value=chosen_reg["feature_name"])
        u_grp = st.text_input("群組分類", value=chosen_reg.get("feature_group") or "擴充拼圖")
        u_mod = st.text_input("模組路徑", value=chosen_reg.get("module_path") or "")
        u_act = st.checkbox("啟用此拼圖", value=bool(chosen_reg.get("is_active", True)))

        if st.form_submit_button("💾 儲存拼圖設定", use_container_width=True):
            if not u_name.strip():
                st.warning("⚠️ 拼圖名稱不可為空。")
            else:
                try:
                    _update_or_toggle_puzzle(
                        engine,
                        chosen_reg["feature_key"],
                        u_name.strip(),
                        u_grp.strip() or "擴充拼圖",
                        u_mod.strip() or None,
                        u_act,
                    )
                    st.success("✅ 已更新拼圖設定。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 更新失敗: {e}")
