import streamlit as st
import pandas as pd
from sqlalchemy import text, create_engine
import os

def get_db_engine(passed_engine):
    """確保即使 st.secrets 沒設定，也能安全取得資料庫連線"""
    if passed_engine is not None:
        return passed_engine
    
    # 嘗試從環境變數讀取
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        try:
            if "database" in st.secrets and "url" in st.secrets["database"]:
                db_url = st.secrets["database"]["url"]
        except Exception:
            pass
            
    if db_url:
        try:
            return create_engine(db_url)
        except Exception:
            pass
    return None

def init_org_table(engine):
    """確保資料庫中存在組織架構表"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_org_units (
                        id SERIAL PRIMARY KEY,
                        parent_id INTEGER REFERENCES sys_org_units(id) ON DELETE CASCADE,
                        unit_name VARCHAR(150) NOT NULL,
                        module_name VARCHAR(255),
                        sort_order INTEGER DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.warning(f"⚠️ 組織架構資料表初始化提示: {e}")

def seed_default_org_data(engine):
    """一鍵將現有標準部門與模組寫入資料庫（Seeding）"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                # 檢查是否已有資料
                res = conn.execute(text("SELECT COUNT(*) FROM sys_org_units")).scalar()
                if res == 0:
                    # 建立根節點與子模組
                    defaults = [
                        (None, "📈 總經理室 (Executive Office)", None),
                        (None, "👔 管理部 (Management Dept)", None),
                        (None, "🛠️ 工程與設計管理中心 (Engineering & Design Center)", None),
                        (None, "🏭 生產部 (Production Dept)", None),
                        (None, "📦 倉庫管理 (Warehouse Management)", None),
                        (None, "📍 外勤工程打卡與工作回報 (Field Attendance)", None),
                        (None, "✍️ 電子簽核中心 (Approval Center)", None),
                    ]
                    for pid, name, mod in defaults:
                        conn.execute(text("""
                            INSERT INTO sys_org_units (parent_id, unit_name, module_name)
                            VALUES (:pid, :name, :mod)
                        """), {"pid": pid, "name": name, "mod": mod})
            return True
        except Exception as e:
            st.error(f"⚠️ 初始化預設部門失敗: {e}")
    return False

def get_department_module_tree(engine=None):
    """相容舊版 app.py 呼叫的樹狀結構轉譯器（支援從資料庫動態讀取）"""
    active_engine = get_db_engine(engine)
    tree = {}
    org_units = []
    
    if active_engine is not None:
        try:
            init_org_table(active_engine)
            with active_engine.connect() as conn:
                df = pd.read_sql(text("SELECT id, parent_id, unit_name, module_name FROM sys_org_units ORDER BY id ASC"), con=conn)
                org_units = df.to_dict(orient="records")
        except Exception:
            pass

    if not org_units:
        # Fallback 預設標準結構
        return {
            "📈 總經理室 (Executive Office)": [
                "🔴 原料價格與 Gemini 智慧採購顧問", "📊 財務類顯示資料 (AR/AP & P&L)",
                "⚡ 工程專案進度與現場異常監控", "📰 越南經營政策與法規每日動態"
            ],
            "👔 管理部 (Management Dept)": [
                "公司公告", "員工檔案", "員工打卡紀錄", "密碼修改", "員工薪資與保險",
                "宿舍與伙食", "工作廠區管理", "車輛進出口", "車輛維修紀錄",
                "固定資產管理", "文件管理", "採購與應付帳款", "應收帳款管理",
                "越南稅務報表", "電子發票管理"
            ],
            "🛠️ 工程與設計管理中心 (Engineering & Design Center)": [
                "⚡ 1. 工程主管戰情室與案場管理", "⚡ 2. 工程專案報價系統",
                "📋 3. 施工日報表與點工點料登記", "🤖 4. AI 施工照片辨識與稽核",
                "⚠️ 5. 工程證照預警與機具檢驗預警", "🎨 6. 配電盤電氣與機構設計圖庫",
                "🔌 7. 配電盤 BOM 零件與採購連動", "👷 8. 外包商計價與偶鐸管理",
                "🧪 9. FAT/SAT 出廠與現場驗收管理"
            ],
            "🏭 生產部 (Production Dept)": [
                "✂️ [板金] 板金加工組工單與條碼", "🎨 [塗料] 粉體塗裝烤漆組品管", "⚡ [配盤] 配電盤組裝配線組"
            ],
            "📦 倉庫管理 (Warehouse Management)": ["📦 [倉儲] 倉庫庫存與資材條碼管理"],
            "📍 外勤工程打卡與工作回報 (Field Attendance)": ["📍 現場外勤打卡與工作回報"],
            "✍️ 電子簽核中心 (Approval Center)": ["✍️ 提交請假/採購與即時進度追蹤 / 審核"]
        }
    
    root_nodes = [u for u in org_units if u['parent_id'] is None or u['parent_id'] == 0]
    for root in root_nodes:
        r_name = root['unit_name']
        tree[r_name] = []
        children = [u for u in org_units if u['parent_id'] == root['id']]
        for child in children:
            if child['module_name']:
                tree[r_name].append(child['module_name'])
            sub_children = [u for u in org_units if u['parent_id'] == child['id']]
            for sc in sub_children:
                if sc['module_name']:
                    tree[r_name].append(f"[{child['unit_name']}] {sc['module_name']}")
        if not tree[r_name] and not children:
            if root['module_name']:
                tree[r_name].append(root['module_name'])
            else:
                tree[r_name] = ["(此部門尚無掛載模組)"]

    return tree

def render(engine=None, lang="繁體中文", **kwargs):
    active_engine = get_db_engine(engine)
    
    st.title("⚙️ 系統設定與動態組織架構管理")
    st.caption("支援資料庫自動同步與現有部門一鍵寫入顯示。")
    st.markdown("---")

    if active_engine is not None:
        init_org_table(active_engine)
        st.success("✅ 資料庫連線正常，所有組織與模組設定將即時同步至 PostgreSQL。")
    else:
        st.error("❌ 資料庫引擎未連線。請檢查 Streamlit Secrets 中的 `database.url` 設定。")

    # 一鍵初始化現有部門按鈕
    if active_engine is not None:
        col_seed1, col_seed2 = st.columns([2, 4])
        with col_seed1:
            if st.button("🚀 一鍵匯入/初始化現有部門到資料庫", type="secondary"):
                if seed_default_org_data(active_engine):
                    st.success("🎉 現有標準部門已成功寫入資料庫！")
                    st.rerun()

    # 讀取現有組織單位
    org_units = []
    if active_engine is not None:
        try:
            with active_engine.connect() as conn:
                df = pd.read_sql(text("SELECT id, parent_id, unit_name, module_name FROM sys_org_units ORDER BY id ASC"), con=conn)
                org_units = df.to_dict(orient="records")
        except Exception as e:
            st.error(f"⚠️ 讀取組織架構失敗: {e}")

    unit_options = {"無 (根節點 / Root)": None}
    for u in org_units:
        unit_options[f"ID: {u['id']} - {u['unit_name']}"] = u['id']

    # 新增表單
    with st.form("add_org_form_v2"):
        st.markdown("#### ➕ 新增組織單位或掛載功能模組")
        col1, col2 = st.columns(2)
        with col1:
            parent_selection = st.selectbox("選擇上級部門 (Parent Unit)", list(unit_options.keys()))
            parent_id = unit_options[parent_selection]
        with col2:
            unit_name = st.text_input("組織/部門名稱 *", placeholder="例如: 總經理室、管理部...")

        module_name = st.text_input("掛載之功能模組名稱 (選填)", placeholder="例如: 員工檔案、專案報價系統...")

        submitted = st.form_submit_button("💾 寫入資料庫並立即顯示", type="primary")
        if submitted:
            if unit_name.strip():
                if active_engine is not None:
                    try:
                        with active_engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO sys_org_units (parent_id, unit_name, module_name)
                                VALUES (:pid, :name, :mod)
                            """), {
                                "pid": parent_id,
                                "name": unit_name.strip(),
                                "mod": module_name.strip() if module_name else None
                            })
                        st.success(f"🎉 成功寫入資料庫：{unit_name.strip()}")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"⚠️ 寫入資料庫失敗：{str(db_err)}")
                else:
                    st.error("⚠️ 資料庫未連線，無法寫入！")
            else:
                st.warning("⚠️ 請填寫部門名稱！")

    st.markdown("---")
    st.markdown("#### 📂 現有企業組織架構與資料庫即時檢視")

    if not org_units:
        st.info("💡 目前資料庫尚無資料，請點擊上方【🚀 一鍵匯入/初始化現有部門】按鈕直接將標準部門寫入資料庫！")
    else:
        for u in org_units:
            if u['parent_id'] is None:
                col_t1, col_t2 = st.columns([5, 1])
                with col_t1:
                    mod_text = f" (模組: {u['module_name']})" if u['module_name'] else ""
                    st.markdown(f"📁 **{u['unit_name']}** (ID: {u['id']}){mod_text}")
                with col_t2:
                    if st.button("🗑️ 刪除", key=f"del_u_{u['id']}"):
                        if active_engine is not None:
                            try:
                                with active_engine.begin() as conn:
                                    conn.execute(text("DELETE FROM sys_org_units WHERE id = :uid"), {"uid": u['id']})
                                st.rerun()
                            except Exception as e:
                                st.error(f"刪除失敗: {e}")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
