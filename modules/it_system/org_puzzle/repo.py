# ==========================================
# 檔案路徑：modules/it_system/org_puzzle/repo.py
# 職責：SaaS 組織樹與拼圖元數據純資料層（完整對齊系統功能說明書 + 多語系自動產碼）
# ==========================================

import hashlib
import re
import unicodedata
from sqlalchemy import text

DEFAULT_PUZZLE_REGISTRY = [
    # 總經理室與經營決策
    {"key": "feat_executive", "name": "👑 總經理室總覽", "group": "總經理室", "module": "modules.executive.overview", "func": "show"},
    {"key": "feat_ai_raw_advisor", "name": "🤖 AI 原料採購顧問與金屬行情", "group": "總經理室", "module": "modules.executive.commodities_fx", "func": "show"},
    {"key": "feat_eng_live_monitor", "name": "🚨 工程進度與異常即時監控", "group": "總經理室", "module": "modules.engineering.overview.dashboard", "func": "render"},
    {"key": "feat_exec_finance_flow", "name": "💸 財務與金流總覽", "group": "總經理室", "module": "modules.executive.financials_pl", "func": "show"},
    {"key": "feat_analytics", "name": "🏗️ 工程案場與金額占比分析", "group": "總經理室", "module": "modules.executive.project_analytics", "func": "show"},
    {"key": "feat_project_pnl", "name": "📊 工程專案損益與單一案場毛利", "group": "總經理室", "module": "modules.engineering.financial.project_pnl", "func": "render"},
    {"key": "feat_progress_billing", "name": "🧾 工程進度與請款追蹤（估驗計價）", "group": "總經理室", "module": "modules.engineering.financial.progress_billing", "func": "render"},
    {"key": "feat_change_orders", "name": "➕➖ 追加減帳管理", "group": "總經理室", "module": "modules.engineering.financial.change_orders", "func": "render"},
    {"key": "feat_multi_wh_tracking", "name": "🏭 多倉庫與工地料件追蹤（領退料警示）", "group": "總經理室", "module": "modules.warehouse.site_stock_alert", "func": "render"},
    {"key": "feat_sales_quote_retail", "name": "🛒 買賣零售與報價管理（分級/組合商品）", "group": "總經理室", "module": "modules.sales.quote_retail", "func": "render"},
    {"key": "feat_ar_ap_reconcile", "name": "💳 資金流、票據與廠商對帳審核", "group": "總經理室", "module": "modules.finance.ar_ap_reconcile", "func": "render"},

    # 工程部與設計
    {"key": "feat_eng_quotation", "name": "📐 估價中心", "group": "工程部", "module": "modules.engineering.financial.quotation", "func": "render"},
    {"key": "feat_field_gps_clockin", "name": "📍 行動定位打卡與領班代點工", "group": "工程部", "module": "modules.engineering.site_ops.gps_attendance", "func": "render"},
    {"key": "feat_eng_gps_fence", "name": "🧭 設定工程打卡施工範圍（GPS 圍籬）", "group": "工程部", "module": "modules.engineering.site_ops.gps_fence_config", "func": "render"},
    {"key": "feat_eng_attendance_map", "name": "🗺️ 員工打卡位置與各案場人數統計", "group": "工程部", "module": "modules.engineering.site_ops.attendance_stats", "func": "render"},
    {"key": "feat_eng_certs", "name": "🪪 外包公司與工程人員證照管理", "group": "工程部", "module": "modules.engineering.compliance.cert_registry", "func": "render"},
    {"key": "feat_site_log", "name": "📋 專案分區派工與手機施工日報", "group": "工程部", "module": "modules.engineering.site_ops.daily_report", "func": "render"},
    {"key": "feat_labor_subcon_billing", "name": "👷 點工計薪與外包估驗", "group": "工程部", "module": "modules.engineering.financial.subcon_billing", "func": "render"},
    {"key": "feat_site_material_transfer", "name": "🚚 工地叫料與跨案場餘料調撥", "group": "工程部", "module": "modules.engineering.procurement_qc.site_transfer", "func": "render"},
    {"key": "feat_cad_bom_sync", "name": "📐 CAD 圖面轉 BOM 與料號編碼", "group": "設計", "module": "modules.engineering.design.cad_bom", "func": "render"},
    {"key": "feat_blueprint_ecn", "name": "🗂️ 圖檔版本控管與工程變更 (ECN/ECO)", "group": "設計", "module": "modules.engineering.procurement_qc.testing_acceptance", "func": "render"},
    {"key": "feat_bom_procurement", "name": "📦 工程 BOM 算料與 MRP 採購需求", "group": "設計", "module": "modules.engineering.procurement_qc.bom_procurement", "func": "render"},

    # 管理部（人事、總務、財務）
    {"key": "feat_mgmt_overview", "name": "🏢 管理部總覽", "group": "管理部", "module": "modules.management.overview", "func": "render"},
    {"key": "feat_announcements", "name": "📢 公司公告佈告欄", "group": "管理部", "module": "modules.management.announcements", "func": "render"},
    {"key": "feat_hr_attendance_leave", "name": "🕒 考勤排班、請假加班與專案工時", "group": "人事", "module": "modules.hr.attendance_leave", "func": "render"},
    {"key": "feat_hr_payroll_bhxh", "name": "💵 自動化薪資計算、津貼與社保扣繳", "group": "人事", "module": "modules.hr.payroll", "func": "render"},
    {"key": "feat_hr_staff_cert_tools", "name": "🪪 員工資料、證照到期提醒與工具借用", "group": "人事", "module": "modules.hr.staff_cert_tools", "func": "render"},
    {"key": "feat_ga_procurement", "name": "🛍️ 總務請購、供應商比價與核銷", "group": "總務", "module": "modules.ga.procurement", "func": "render"},
    {"key": "feat_ga_assets_dorm", "name": "🏗️ 固定資產、折舊、耗材、公務車與宿舍", "group": "總務", "module": "modules.ga.assets_facilities", "func": "render"},
    {"key": "feat_fin_gl_ar_ap", "name": "📘 核心會計 (GL / AR / AP / 現金 / 票據)", "group": "財務", "module": "modules.finance.core_accounting", "func": "render"},
    {"key": "feat_fin_budget_tax_bi", "name": "📈 預算控管、越南稅務/發票與多維度財報", "group": "財務", "module": "modules.finance.budget_tax_bi", "func": "render"},

    # 生產部與倉庫管理
    {"key": "feat_prod_overview", "name": "🏭 生產部總覽", "group": "生產部", "module": "modules.production.overview", "func": "render"},
    {"key": "feat_production_schedule", "name": "📅 工單管理、生產排程 (CRP) 與 MRP", "group": "生產部", "module": "modules.production.schedule_mrp", "func": "render"},
    {"key": "feat_prod_qc_cost", "name": "🔬 品質檢驗 (QC/QA)、批號追溯與工單成本", "group": "生產部", "module": "modules.production.qc_cost", "func": "render"},
    {"key": "feat_material", "name": "📦 庫存管理、出入庫、調撥與盤點", "group": "倉庫管理", "module": "modules.warehouse.inventory", "func": "render"},
    {"key": "feat_barcode_pda", "name": "🏷️ 條碼/QR/PDA 掃描與庫存週轉分析", "group": "倉庫管理", "module": "modules.warehouse.barcode_analytics", "func": "render"},

    # 全公司共用與系統設定／安全
    {"key": "feat_my_approvals", "name": "✍️ 簽核中心（請假／採購／文書／估價）", "group": "全公司共用", "module": "modules.approval_workflow", "func": "render_approval_center"},
    {"key": "feat_security_guard_ops", "name": "🛡️ 保全操作頁面", "group": "廠區安控", "module": "modules.management.security_gate", "func": "render"},
    {"key": "feat_role_permissions", "name": "🔐 角色權限與員工頁面指派", "group": "系統設定", "module": "modules.it_system.role_permissions", "func": "render"},
    {"key": "feat_api_gateway", "name": "🔌 第三方 API 閘道設定", "group": "系統設定", "module": "modules.it_system.api_gateway", "func": "render"},
    {"key": "feat_brand_logo", "name": "🎨 企業識別與品牌 LOGO", "group": "系統設定", "module": "modules.it_system.brand_logo", "func": "render"},
    {"key": "feat_db_connection", "name": "🗄️ 資料庫串接設定", "group": "系統設定", "module": "modules.it_system.db_connection", "func": "render"},
    {"key": "feat_storage_nas", "name": "☁️ 雲端與本地 NAS / Storage 儲存區", "group": "系統設定", "module": "modules.it_system.storage_nas", "func": "render"},
    {"key": "feat_audit_logs", "name": "📜 系統稽核日誌與安全", "group": "系統設定", "module": "modules.it_system.audit_logs", "func": "render"},
]

ORG_TEMPLATES = {
    "裕豐電機完整模板（L1~L2 + 現場入口）": [
        {"code": "DEPT_EXEC", "name": "總經理室", "tier": "L1", "parent": None, "type": "DEPT", "sort": 10},
        {"code": "DEPT_ENG", "name": "工程部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 20},
        {"code": "DEPT_ENG_DESIGN", "name": "設計", "tier": "L2", "parent": "DEPT_ENG", "type": "DEPT", "sort": 21},
        {"code": "DEPT_MGMT", "name": "管理部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 30},
        {"code": "DEPT_MGMT_HR", "name": "行政/人事", "tier": "L2", "parent": "DEPT_MGMT", "type": "DEPT", "sort": 31},
        {"code": "DEPT_MGMT_GA", "name": "總務/採購", "tier": "L2", "parent": "DEPT_MGMT", "type": "DEPT", "sort": 32},
        {"code": "DEPT_MGMT_FIN", "name": "財務/會計", "tier": "L2", "parent": "DEPT_MGMT", "type": "DEPT", "sort": 33},
        {"code": "DEPT_PROD", "name": "生產部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 40},
        {"code": "DEPT_PROD_SHEET", "name": "板金", "tier": "L2", "parent": "DEPT_PROD", "type": "DEPT", "sort": 41},
        {"code": "DEPT_PROD_PAINT", "name": "塗裝", "tier": "L2", "parent": "DEPT_PROD", "type": "DEPT", "sort": 42},
        {"code": "DEPT_PROD_PANEL", "name": "配盤", "tier": "L2", "parent": "DEPT_PROD", "type": "DEPT", "sort": 43},
        {"code": "DEPT_PROD_WH", "name": "倉庫管理", "tier": "L2", "parent": "DEPT_PROD", "type": "DEPT", "sort": 44},
        {"code": "FUNC_APPROVAL_CENTER", "name": "簽核中心", "tier": "L1", "parent": None, "type": "L1_FUNC", "sort": 50},
        {"code": "FUNC_FIELD_CLOCKIN", "name": "外勤工程人員線上打卡", "tier": "L1", "parent": None, "type": "L1_FUNC", "sort": 60},
        {"code": "FUNC_SECURITY_GATE", "name": "保全操作頁面", "tier": "L1", "parent": None, "type": "L1_FUNC", "sort": 70},
    ],
    "通用製造／工程精簡模板": [
        {"code": "DEPT_EXEC", "name": "總經理室", "tier": "L1", "parent": None, "type": "DEPT", "sort": 10},
        {"code": "DEPT_ENG", "name": "工程部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 20},
        {"code": "DEPT_ENG_DESIGN", "name": "設計組", "tier": "L2", "parent": "DEPT_ENG", "type": "DEPT", "sort": 21},
        {"code": "DEPT_OPS", "name": "營運管理部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 30},
        {"code": "FUNC_APPROVAL_CENTER", "name": "簽核中心", "tier": "L1", "parent": None, "type": "L1_FUNC", "sort": 40},
    ],
}


def generate_auto_node_code(tier: str, name: str, parent_code: str | None = None, node_type: str = "DEPT") -> str:
    clean_name = (name or "").strip()
    vn_mapped = clean_name.replace("đ", "d").replace("Đ", "D")
    normalized = unicodedata.normalize("NFD", vn_mapped)
    without_accents = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    ascii_slug = re.sub(r"[^A-Za-z0-9]+", "_", without_accents).strip("_").upper()
    ascii_slug = re.sub(r"_+", "_", ascii_slug)[:14]

    digest_source = f"{tier}|{parent_code or ''}|{node_type}|{clean_name}".encode("utf-8")
    short_hash = hashlib.sha1(digest_source).hexdigest()[:4].upper()
    prefix = "FUNC" if node_type == "L1_FUNC" else (tier or "L1").upper()
    return f"{prefix}_{ascii_slug}_{short_hash}" if ascii_slug else f"{prefix}_NODE_{short_hash}"


def ensure_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sys_feature_registry (
                    id SERIAL PRIMARY KEY,
                    feature_key VARCHAR(120) UNIQUE NOT NULL,
                    feature_name VARCHAR(160) NOT NULL,
                    feature_group VARCHAR(100) DEFAULT '通用拼圖',
                    module_path VARCHAR(255),
                    entry_func VARCHAR(100) DEFAULT 'render',
                    is_active BOOLEAN DEFAULT TRUE
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sys_tenant_org_nodes (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(64) NOT NULL,
                    node_code VARCHAR(80) NOT NULL,
                    node_name VARCHAR(120) NOT NULL,
                    level_tier VARCHAR(16) DEFAULT 'L1',
                    parent_node_code VARCHAR(80),
                    node_type VARCHAR(32) DEFAULT 'DEPT',
                    sort_order INT DEFAULT 100,
                    is_active BOOLEAN DEFAULT TRUE,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (tenant_id, node_code)
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sys_tenant_node_mounts (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(64) NOT NULL,
                    node_code VARCHAR(80) NOT NULL,
                    mounted_features TEXT DEFAULT '',
                    landing_role_code VARCHAR(80),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (tenant_id, node_code)
                );
            """))
            for item in DEFAULT_PUZZLE_REGISTRY:
                conn.execute(text("""
                    INSERT INTO sys_feature_registry (feature_key, feature_name, feature_group, module_path, entry_func, is_active)
                    VALUES (:k, :n, :g, :m, :f, TRUE)
                    ON CONFLICT (feature_key) DO UPDATE SET
                        feature_group = EXCLUDED.feature_group,
                        module_path = COALESCE(sys_feature_registry.module_path, EXCLUDED.module_path),
                        entry_func = COALESCE(sys_feature_registry.entry_func, EXCLUDED.entry_func),
                        is_active = TRUE
                """), {"k": item["key"], "n": item["name"], "g": item["group"], "m": item["module"], "f": item["func"]})
    except Exception:
        pass


def load_tenant_nodes(engine, tenant_id: str, include_inactive: bool = False) -> list[dict]:
    if not engine:
        return []
    try:
        with engine.connect() as conn:
            sql = "SELECT node_code, node_name, level_tier, parent_node_code, node_type, sort_order, is_active FROM sys_tenant_org_nodes WHERE tenant_id = :tid"
            if not include_inactive:
                sql += " AND is_active = TRUE"
            sql += " ORDER BY sort_order ASC, id ASC"
            return [r._asdict() for r in conn.execute(text(sql), {"tid": tenant_id}).fetchall()]
    except Exception:
        return []


def upsert_node(engine, tenant_id: str, node_code: str, node_name: str, level_tier: str, parent_code: str | None, node_type: str, sort_order: int, is_active: bool = True):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO sys_tenant_org_nodes (
                tenant_id, node_code, node_name, level_tier, parent_node_code, node_type, sort_order, is_active, updated_at
            )
            VALUES (:tid, :c, :n, :tier, :p, :nt, :s, :act, CURRENT_TIMESTAMP)
            ON CONFLICT (tenant_id, node_code) DO UPDATE SET
                node_name = EXCLUDED.node_name,
                level_tier = EXCLUDED.level_tier,
                parent_node_code = EXCLUDED.parent_node_code,
                node_type = EXCLUDED.node_type,
                sort_order = EXCLUDED.sort_order,
                is_active = EXCLUDED.is_active,
                updated_at = CURRENT_TIMESTAMP
        """), {"tid": tenant_id, "c": node_code, "n": node_name, "tier": level_tier, "p": parent_code, "nt": node_type, "s": sort_order, "act": is_active})


def apply_org_template(engine, tenant_id: str, template_items: list[dict]):
    with engine.begin() as conn:
        conn.execute(text("UPDATE sys_tenant_org_nodes SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP WHERE tenant_id = :tid"), {"tid": tenant_id})
        for item in template_items:
            conn.execute(text("""
                INSERT INTO sys_tenant_org_nodes (
                    tenant_id, node_code, node_name, level_tier, parent_node_code, node_type, sort_order, is_active, updated_at
                )
                VALUES (:tid, :c, :n, :tier, :p, :nt, :s, TRUE, CURRENT_TIMESTAMP)
                ON CONFLICT (tenant_id, node_code) DO UPDATE SET
                    node_name = EXCLUDED.node_name,
                    level_tier = EXCLUDED.level_tier,
                    parent_node_code = EXCLUDED.parent_node_code,
                    node_type = EXCLUDED.node_type,
                    sort_order = EXCLUDED.sort_order,
                    is_active = TRUE,
                    updated_at = CURRENT_TIMESTAMP
            """), {"tid": tenant_id, "c": item["code"], "n": item["name"], "tier": item["tier"], "p": item["parent"], "nt": item["type"], "s": item["sort"]})


def delete_node_permanently(engine, tenant_id: str, node_code: str):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM sys_tenant_node_mounts WHERE tenant_id = :tid AND node_code = :c"), {"tid": tenant_id, "c": node_code})
        conn.execute(text("DELETE FROM sys_tenant_org_nodes WHERE tenant_id = :tid AND node_code = :c"), {"tid": tenant_id, "c": node_code})


def load_registry(engine) -> list[dict]:
    registry = list(DEFAULT_PUZZLE_REGISTRY)
    if not engine:
        return registry
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT feature_key, feature_name, feature_group, module_path, entry_func FROM sys_feature_registry WHERE is_active = TRUE ORDER BY id ASC")).fetchall()
            if rows:
                merged = {}
                for item in registry:
                    merged[item["key"]] = dict(item)
                for r in rows:
                    d = r._asdict()
                    fk = d["feature_key"]
                    base = merged.get(fk, {"key": fk, "name": d["feature_name"], "group": "擴充拼圖", "module": None, "func": "render"})
                    merged[fk] = {
                        "key": fk,
                        "name": d["feature_name"] or base["name"],
                        "group": d.get("feature_group") or base["group"],
                        "module": d.get("module_path") or base["module"],
                        "func": d.get("entry_func") or base["func"],
                    }
                return list(merged.values())
    except Exception:
        pass
    return registry


def load_node_mount(engine, tenant_id: str, node_code: str) -> tuple[list[str], str]:
    try:
        with engine.connect() as conn:
            row = conn.execute(text("SELECT mounted_features, landing_role_code FROM sys_tenant_node_mounts WHERE tenant_id = :tid AND node_code = :c"), {"tid": tenant_id, "c": node_code}).fetchone()
            if row:
                return [x.strip() for x in str(row[0] or "").split(",") if x.strip()], (row[1] or "")
    except Exception:
        pass
    return [], ""


def save_node_mount(engine, tenant_id: str, node_code: str, feature_keys: list[str], landing_role: str | None):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO sys_tenant_node_mounts (tenant_id, node_code, mounted_features, landing_role_code, updated_at)
            VALUES (:tid, :c, :feats, :lrole, CURRENT_TIMESTAMP)
            ON CONFLICT (tenant_id, node_code) DO UPDATE SET
                mounted_features = EXCLUDED.mounted_features,
                landing_role_code = EXCLUDED.landing_role_code,
                updated_at = CURRENT_TIMESTAMP
        """), {"tid": tenant_id, "c": node_code, "feats": ",".join(feature_keys), "lrole": landing_role})


def register_puzzle(engine, feature_key: str, feature_name: str, feature_group: str, module_path: str | None):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO sys_feature_registry (feature_key, feature_name, feature_group, module_path, entry_func, is_active)
            VALUES (:k, :n, :g, :m, 'render', TRUE)
            ON CONFLICT (feature_key) DO UPDATE SET
                feature_name = EXCLUDED.feature_name,
                feature_group = EXCLUDED.feature_group,
                module_path = COALESCE(:m, sys_feature_registry.module_path),
                is_active = TRUE
        """), {"k": feature_key, "n": feature_name, "g": feature_group, "m": module_path})
