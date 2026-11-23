import streamlit as st


def render_numbered_puzzle_selector(
    puzzle_items: list[dict],
    initial_selected_keys: list[str] | None = None,
    state_prefix: str = "puzzle_order",
) -> list[str]:
    """
    依勾選先後順序自動標示 1. 2. 3. 4... 編號，並回傳有序的已勾選 key 清單。
    puzzle_items 每筆需包含: {"key": ..., "name": ..., "group": ...}
    """
    order_key = f"{state_prefix}_ordered_keys"
    init_flag = f"{state_prefix}_initialized"

    if init_flag not in st.session_state:
        st.session_state[init_flag] = True
        st.session_state[order_key] = list(initial_selected_keys or [])

    valid_keys = [str(item.get("key")) for item in puzzle_items if item.get("key")]
    valid_set = set(valid_keys)
    name_map = {str(item.get("key")): str(item.get("name") or item.get("key")) for item in puzzle_items if item.get("key")}

    # 過濾掉已不存在的 key，維持既有順序
    ordered_keys: list[str] = [k for k in st.session_state.get(order_key, []) if k in valid_set]

    # 頂部即時顯示目前勾選順序：1. ... 2. ... 3. ...
    if ordered_keys:
        preview_line = " ".join([f"**{idx + 1}.** {name_map.get(k, k)}" for idx, k in enumerate(ordered_keys)])
        st.markdown(f"📌 **目前勾選排序（依勾選先後）：** {preview_line}")
    else:
        st.caption("📌 尚未勾選任何功能，勾選後將依先後顯示 1.、2.、3.、4. 排序編號。")

    c_ctrl1, c_ctrl2 = st.columns([1.5, 5.5])
    with c_ctrl1:
        if st.button("🔄 清除全部勾選", key=f"{state_prefix}_clear_all"):
            st.session_state[order_key] = []
            for k in valid_keys:
                st.session_state[f"{state_prefix}_chk_{k}"] = False
            st.rerun()

    # 依群組分區渲染勾選框；已勾選項目在標籤前加上「1.」「2.」
    current_rank_map = {k: idx + 1 for idx, k in enumerate(ordered_keys)}
    groups: list[str] = []
    for item in puzzle_items:
        g = str(item.get("group") or "其他")
        if g not in groups:
            groups.append(g)

    updated_order: list[str] = list(ordered_keys)

    for grp in groups:
        st.markdown(f"#### {grp}")
        grp_items = [it for it in puzzle_items if str(it.get("group") or "其他") == grp]
        cols = st.columns(2)

        for idx_in_grp, item in enumerate(grp_items):
            pkey = str(item.get("key"))
            pname = str(item.get("name") or pkey)
            chk_state_key = f"{state_prefix}_chk_{pkey}"

            if chk_state_key not in st.session_state:
                st.session_state[chk_state_key] = pkey in current_rank_map

            rank_num = current_rank_map.get(pkey)
            label_text = f"**{rank_num}.** {pname} (`{pkey}`)" if rank_num else f"{pname} (`{pkey}`)"

            with cols[idx_in_grp % 2]:
                checked = st.checkbox(label_text, key=chk_state_key)

            if checked and pkey not in updated_order:
                updated_order.append(pkey)
            elif (not checked) and pkey in updated_order:
                updated_order.remove(pkey)

    # 若勾選順序有變動，立即更新 state 並刷新標籤編號（1. 2. 3. ...）
    if updated_order != ordered_keys:
        st.session_state[order_key] = updated_order
        st.rerun()

    return updated_order
