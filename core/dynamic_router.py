# ==========================================
# 檔案路徑：core/dynamic_router.py
# 職責：全系統唯一的元數據讀取器與動態模組載入器（100% 驅動側邊欄、首頁卡片、角色直達與功能分發）
# ==========================================

import importlib
import streamlit as st
from sqlalchemy import text
from modules.it_system.org_puzzle import repo


def get_tenant_l1_nodes(engine, tenant_id: str) -> list[dict]:
    """讀取目前租戶啟用中的 L1 節點（包含 L1 部門與 L1 獨立功能入口）"""
    repo.ensure_tables(engine)
    nodes = repo.load_tenant_nodes(engine, tenant_id, include_inactive=False)
    return [n for n in nodes if str(n.get("level_tier")).upper() == "L1"]


def get_child_nodes(engine, tenant_id: str, parent_node_code: str) -> list[dict]:
    """讀取指定父節點底下的下一層啟用子節點（支援 L1->L2->L3->L4 無限下鑽）"""
    nodes = repo.load_tenant_nodes(engine, tenant_id, include_inactive=False)
    return [n for n in nodes if (n.get("parent_node_code") or None) == parent_node_code]


def get_node_mounted_features(engine, tenant_id: str, node_code: str) -> list[dict]:
    """取得指定節點已掛載的完整拼圖資訊（從 sys_tenant_node_mounts JOIN sys_feature_registry）"""
    feat_keys, _ = repo.load_node_mount(engine, tenant_id, node_code)
    if not feat_keys:
        return []
    registry = repo.load_registry(engine)
    reg_map = {item["key"]: item for item in registry}
    result = []
    for fk in feat_keys:
        if fk in reg_map:
            result.append(reg_map[fk])
        else:
            result.append({"key": fk, "name": f"🧩 {fk}", "group": "未註冊拼圖", "module": None, "func": "render"})
    return result


def resolve_role_landing_node(engine, tenant_id: str, role_code: str) -> dict | None:
    """登入時檢查該角色是否有設定直達的功能節點（例如 FIELD_ENGINEER / SECURITY_GUARD）"""
    if not engine or not role_code:
        return None
    try:
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT m.node_code, m.mounted_features, n.node_name, n.node_type
                FROM sys_tenant_node_mounts m
                JOIN sys_tenant_org_nodes n
                  ON m.tenant_id = n.tenant_id AND m.node_code = n.node_code
                WHERE m.tenant_id = :tid
                  AND UPPER(COALESCE(m.landing_role_code, '')) = :rcode
                  AND n.is_active = TRUE
                LIMIT 1
            """), {"tid": tenant_id, "rcode": role_code.strip().upper()}).fetchone()
            if row:
                return row._asdict()
    except Exception:
        pass
    return None


def dispatch_feature(engine, feature_key: str, lang: str = "zh"):
    """依 sys_feature_registry 註冊的 module_path 與 entry_func 動態載入並渲染功能"""
    registry = repo.load_registry(engine)
    target = next((item for item in registry if item["key"] == feature_key), None)

    if not target or not target.get("module"):
        st.info(f"🧩 功能拼圖 `{feature_key}` 尚未綁定實體程式檔案，請先建立模組並於「註冊新功能拼圖」填入模組路徑。")
        return

    mod_path = target["module"].strip()
    func_name = (target.get("func") or "render").strip()

    try:
        mod = importlib.import_module(mod_path)
        entry = getattr(mod, func_name, None) or getattr(mod, "render", None) or getattr(mod, "show", None) or getattr(mod, "main", None)
        if not entry:
            st.error(f"❌ 模組 `{mod_path}` 找不到可執行的入口函式（`{func_name}` / `render` / `show`）。")
            return
        entry(engine=engine, lang=lang)
    except ModuleNotFoundError:
        st.warning(f"⚠️ 模組檔案 `{mod_path}` 尚未建立至專案目錄中，建立完成後無需改設定即可自動載入。")
    except Exception as e:
        st.error(f"❌ 執行功能 `{target.get('name', feature_key)}` 時發生錯誤：{e}")
