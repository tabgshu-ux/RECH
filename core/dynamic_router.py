# ==========================================
# 檔案路徑：core/dynamic_router.py
# 職責：讀取租戶元數據、L1~L4 子節點、已掛載拼圖與動態模組載入
# ==========================================

import importlib
import streamlit as st
from sqlalchemy import text
from modules.it_system.org_puzzle import repo


def get_l1_nodes(engine, tenant_id: str) -> list[dict]:
    repo.ensure_tables(engine)
    nodes = repo.load_tenant_nodes(engine, tenant_id, include_inactive=False)
    return [n for n in nodes if str(n.get("level_tier")).upper() == "L1"]


def get_child_nodes(engine, tenant_id: str, parent_code: str) -> list[dict]:
    nodes = repo.load_tenant_nodes(engine, tenant_id, include_inactive=False)
    return [n for n in nodes if (n.get("parent_node_code") or None) == parent_code]


def get_mounted_features(engine, tenant_id: str, node_code: str) -> list[dict]:
    feat_keys, _ = repo.load_node_mount(engine, tenant_id, node_code)
    if not feat_keys:
        return []
    reg_map = {item["key"]: item for item in repo.load_registry(engine)}
    return [
        reg_map.get(fk, {"key": fk, "name": f"🧩 {fk}", "group": "通用拼圖", "module": None, "func": "render"})
        for fk in feat_keys
    ]


def get_role_landing(engine, tenant_id: str, role_code: str) -> dict | None:
    if not engine or not role_code:
        return None
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("""
                    SELECT m.node_code, m.mounted_features, n.node_name, n.node_type
                    FROM sys_tenant_node_mounts m
                    JOIN sys_tenant_org_nodes n
                      ON m.tenant_id = n.tenant_id AND m.node_code = n.node_code
                    WHERE m.tenant_id = :tid
                      AND UPPER(COALESCE(m.landing_role_code, '')) = :rcode
                      AND n.is_active = TRUE
                    LIMIT 1
                """),
                {"tid": tenant_id, "rcode": role_code.strip().upper()},
            ).fetchone()
            return row._asdict() if row else None
    except Exception:
        return None


def dispatch_feature(engine, feature_key: str, lang: str = "zh"):
    target = next((item for item in repo.load_registry(engine) if item["key"] == feature_key), None)
    if not target or not target.get("module"):
        st.info(f"🧩 `{feature_key}` 尚未綁定模組路徑。")
        return

    mod_path = target["module"].strip()
    func_name = (target.get("func") or "render").strip()
    try:
        mod = importlib.import_module(mod_path)
        entry = (
            getattr(mod, func_name, None)
            or getattr(mod, "render", None)
            or getattr(mod, "show", None)
            or getattr(mod, "main", None)
        )
        if not entry:
            st.error(f"❌ `{mod_path}` 找不到可呼叫的函式。")
            return
        entry(engine=engine, lang=lang)
    except ModuleNotFoundError:
        st.warning(f"⚠️ 尚未建立模組檔案 `{mod_path}`。")
    except Exception as e:
        st.error(f"❌ 執行 `{target.get('name', feature_key)}` 失敗：{e}")
