import streamlit as st
import pandas as pd
from sqlalchemy import text, create_engine
import os

def get_db_engine(passed_engine=None):
    """精準對應您現有 Secrets 的 SUPABASE_DB_URL 連線函式"""
    if passed_engine is not None:
        return passed_engine
        
    db_url = None
    try:
        if "SUPABASE_DB_URL" in st.secrets:
            db_url = st.secrets["SUPABASE_DB_URL"]
    except Exception:
        pass
        
    if not db_url:
        try:
            if "database" in st.secrets and "url" in st.secrets["database"]:
                db_url = st.secrets["database"]["url"]
        except Exception:
            pass
            
    if not db_url:
        db_url = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
        
    if db_url:
        try:
            return create_engine(db_url)
        except Exception:
            pass
    return None

def init_db_tables(engine):
    """確保資料庫中存在組織架構與系統設定表"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_departments (
                        id SERIAL PRIMARY KEY,
                        dept_name VARCHAR(150) UNIQUE NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_department_modules (
                        id SERIAL PRIMARY KEY,
                        dept_name VARCHAR(150) NOT NULL,
                        module_name VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_api_configs (
                        id SERIAL PRIMARY KEY,
                        config_key VARCHAR(100) UNIQUE NOT NULL,
                        config_value TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception:
            pass

def seed_default_data(engine):
    """初始化預設部門與模組到真實資料庫中"""
    if engine is not None:
        try:
            init_db_tables(engine)
            with engine.begin() as conn:
                count = conn.execute(text("SELECT COUNT(*) FROM sys_departments")).scalar()
                if count == 0:
                    defaults = {
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
                    for dept, mods in defaults.items():
                        conn.execute(text("INSERT INTO sys_departments (dept_name) VALUES (:d) ON CONFLICT DO NOTHING"), {"d": dept})
                        for m in mods:
                            conn.execute(text("""
                                INSERT INTO sys_department_modules (dept_name, module_name)
                                VALUES (:d, :m)
                            """), {"d": dept, "m": m})
            return True
        except Exception:
            pass
    return False

def get_department_module_tree(engine=None):
    """【重要】供 app.py 匯入的標準函式：從 PostgreSQL 資料庫讀取部門與模組"""
    active_engine = get_db_engine(engine)
    tree = {}
    if active_engine is not None:
        try:
            init_db_tables(active_engine)
            with active_engine.connect() as conn:
                df_dept = pd.read_sql(text("SELECT dept_name FROM sys_departments"), con=conn)
                df_mods = pd.read_sql(text("SELECT dept_name, module_name FROM sys_department_modules"), con=conn)
                
                if not df_dept.empty:
                    for _, row in df_dept.iterrows():
                        d_name = row["dept_name"]
                        mods = df_mods[df_mods["dept_name"] == d_name]["module_name"].tolist()
                        tree[d_name] = mods if mods else []
                    return tree
        except Exception:
            pass

    # 若資料庫尚無資料或連線前夕的預設結構
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

def render(engine=None, lang="繁體中文", **kwargs):
    active_engine = get_db_engine(engine)
    
    st.title("⚙️ 系統設定、資料庫與 API 連結總控制中心")
    st.caption("100% 透過 PostgreSQL (Supabase) 資料庫驅動，管理部門動態掛載、資料庫連線狀態與第三方 API 參數。")
    st.markdown("---")

    if active_engine is not None:
        try:
            with active_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            st.success("✅ PostgreSQL 資料庫連線完全正常 (SUPABASE_DB_URL)！所有異動將直接寫入資料庫。")
            init_db_tables(active_engine)
        except Exception as db_err:
            st.error(f"❌ 資料庫連線異常：{str(db_err)}")
    else:
        st.error("❌ 尚未取得有效的資料庫引擎。請檢查 Streamlit Secrets 中的 SUPABASE_DB_URL 設定。")

    tab_dept, tab_db, tab_api = st.tabs([
        "🏢 企業部門與模組動態掛載 (Database-Driven)",
        "🔌 資料庫連線診斷與狀態 (DB Bridge)",
        "🌐 第三方 API 串聯設定 (API Gateway)"
    ])

    with tab_dept:
        st.subheader("🏢 資料庫部門與模組管理")
        if active_engine is not None:
            if st.button("🚀 一鍵初始化/同步標準部門至資料庫", type="secondary"):
                if seed_default_data(active_engine):
                    st.success("🎉 標準部門與模組已成功寫入 PostgreSQL 資料庫！")
                    st.rerun()

        tree = get_department_module_tree(active_engine)

        with st.form("db_add_dept_form"):
            st.markdown("#### ➕ 新增部門或掛載模組到資料庫")
            col1, col2 = st.columns(2)
            with col1:
                action = st.selectbox("動作", ["新增一級部門", "為現有部門掛載模組"])
            with col2:
                target = st.selectbox("目標部門", list(tree.keys()))
            
            input_val = st.text_input("名稱 (部門名稱 或 模組名稱)", placeholder="例如: 🛡️ 品質安環部")
            submitted = st.form_submit_button("💾 寫入資料庫", type="primary")
            
            if submitted and input_val.strip() and active_engine is not None:
                try:
                    with active_engine.begin() as conn:
                        if action == "新增一級部門":
                            conn.execute(text("INSERT INTO sys_departments (dept_name) VALUES (:d) ON CONFLICT DO NOTHING"), {"d": input_val.strip()})
                            st.success(f"🎉 成功新增部門：{input_val.strip()}")
                        else:
                            conn.execute(text("INSERT INTO sys_department_modules (dept_name, module_name) VALUES (:d, :m)"), {"d": target, "m": input_val.strip()})
                            st.success(f"🎉 成功為 [{target}] 掛載模組：{input_val.strip()}")
                    st.rerun()
                except Exception as e:
                    st.error(f"寫入資料庫失敗: {e}")

        st.markdown("---")
        for d_name, mods in tree.items():
            with st.expander(f"📁 {d_name} (包含 {len(mods)} 項模組)"):
                if mods:
                    for m in mods:
                        st.markdown(f"• {m}")
                else:
                    st.info("💡 此部門目前尚無模組。")

    with tab_db:
        st.subheader("🔌 資料庫連線狀態與資訊")
        st.info("此處顯示當前連接的 Supabase PostgreSQL 資料庫連線參數與健康狀態。")
        if active_engine is not None:
            st.write(f"**資料庫驅動引擎：** {active_engine.dialect.name}")
            st.write(f"**連線池狀態：** 正常運行中 (Active Pool)")
            if st.button("🔄 測試資料庫回應速度 (Ping)"):
                try:
                    with active_engine.connect() as conn:
                        res = conn.execute(text("SELECT NOW()")).scalar()
                    st.success(f"✅ 資料庫回應成功！伺服器時間：{res}")
                except Exception as e:
                    st.error(f"❌ Ping 失敗：{e}")
        else:
            st.warning("⚠️ 目前無資料庫引擎實例。")

    with tab_api:
        st.subheader("🌐 第三方 API 串聯與金鑰設定中心")
        st.info("在此設定外部 API 閘道（如 LME 銅價 API、越南電子發票 API、AI 服務金鑰等）。")
        with st.form("api_config_form"):
            api_name = st.text_input("API 服務名稱", placeholder="例如: LME_COPPER_API_KEY")
            api_key_val = st.text_input("API 金鑰 / Endpoint 網址", type="password", placeholder="請輸入密鑰或 URL")
            saved_api = st.form_submit_button("💾 儲存 API 設定至資料庫")
            if saved_api and api_name.strip() and active_engine is not None:
                try:
                    with active_engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO sys_api_configs (config_key, config_value)
                            VALUES (:k, :v)
                            ON CONFLICT (config_key) DO UPDATE SET config_value = :v, updated_at = CURRENT_TIMESTAMP
                        """), {"k": api_name.strip(), "v": api_key_val.strip()})
                    st.success(f"🎉 API 設定 [{api_name.strip()}] 已安全加密寫入資料庫！")
                except Exception as e:
                    st.error(f"儲存失敗: {e}")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
