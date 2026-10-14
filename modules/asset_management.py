import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 裕豐電機工業 (Reetech Industrial) 廠區連動規範
# ----------------------------------------------------
DEFAULT_FACTORY = "越南西寧廠 (Tay Ninh)"

def get_active_factories(engine):
    """從 public.factories 主表讀取最新廠區清單，預設僅保留西寧廠"""
    if not engine:
        return [DEFAULT_FACTORY]
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT factory_name FROM public.factories WHERE factory_name NOT LIKE '%海防%' ORDER BY id ASC;"))
            rows = res.fetchall()
            if rows:
                return [r[0] for r in rows if r[0]]
    except Exception:
        pass
    return [DEFAULT_FACTORY]

def init_asset_db(engine):
    """資料庫初始化與歷史資料校正 (自動將海防廠項目修正為西寧廠)"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.fixed_assets (
                    id SERIAL PRIMARY KEY,
                    asset_code VARCHAR(50) UNIQUE NOT NULL,
                    asset_name VARCHAR(200) NOT NULL,
                    category VARCHAR(100) DEFAULT '生產機具',
                    factory VARCHAR(100) DEFAULT '越南西寧廠 (Tay Ninh)',
                    brand_landlord VARCHAR(150),
                    status VARCHAR(50) DEFAULT '🟢 在用/租賃中 (Active)',
                    cost_amount NUMERIC(12,2) DEFAULT 0,
                    start_date DATE,
                    end_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # 🛠️ 自動校正：把所有舊的海防廠資產與租賃合約資料，自動統一更正為『越南西寧廠 (Tay Ninh)』
            conn.execute(text("""
                UPDATE public.fixed_assets 
                SET factory = '越南西寧廠 (Tay Ninh)' 
                WHERE factory LIKE '%海防%' OR factory LIKE '%Hai Phong%' OR factory IS NULL;
            """))
    except Exception as e:
        pass

def render_asset_management_page(engine=None, lang="繁體中文", **kwargs):
    st.title("🏢 管理部 - 固定資產與設備/租賃合約管理中心")
    st.caption("管理西寧廠生產機械、土地房屋租賃合約、車輛、網路、品管儀器與工安設施之完整生命週期。")

    init_asset_db(engine)
    
    # 動態取得最新廠區名冊
    current_factories = get_active_factories(engine)

    tab_list, tab_add, tab_edit, tab_terminate, tab_history = st.tabs([
        "📄 廠區資產總表與分項檢視",
        "➕ 新增固定資產與租賃合約",
        "✏️ 修改資產與租賃資料",
        "🗑️ 辦理資產報廢或合約終止",
        "📜 歷史報廢與停用資產紀錄"
    ])

    # ----------------------------------------------------
    # 📊 頂部動態指標看板
    # ----------------------------------------------------
    if engine:
        try:
            with engine.connect() as conn:
                res_total = conn.execute(text("SELECT COUNT(*) FROM public.fixed_assets WHERE status NOT LIKE '%報廢%';")).fetchone()
                total_cnt = res_total[0] if res_total else 0
                
                res_retired = conn.execute(text("SELECT COUNT(*) FROM public.fixed_assets WHERE status LIKE '%報廢%';")).fetchone()
                retired_cnt = res_retired[0] if res_retired else 0
        except Exception:
            total_cnt, retired_cnt = 0, 0
    else:
        total_cnt, retired_cnt = 4, 1

    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("在用總項目數", f"{total_cnt} 項")
    c_m2.metric("歷史報廢/封存數", f"{retired_cnt} 項")
    c_m3.metric("廠區分布", " | ".join(current_factories))

    st.markdown("---")

    # ----------------------------------------------------
    # 📄 Tab 1: 資產與合約清冊 (純西寧廠)
    # ----------------------------------------------------
    with tab_list:
        st.markdown("### 📋 廠區固定資產與租賃合約清冊")
        
        filter_factory = st.selectbox("請選擇要檢視的廠區：", ["全部廠區 (All Plants)"] + current_factories)
        
        if engine:
            try:
                with engine.connect() as conn:
                    query = "SELECT asset_code, asset_name, category, factory, brand_landlord, start_date, end_date, status FROM public.fixed_assets WHERE status NOT LIKE '%報廢%'"
                    params = {}
                    if filter_factory != "全部廠區 (All Plants)":
                        query += " AND factory = :fac"
                        params["fac"] = filter_factory
                    query += " ORDER BY id ASC;"

                    res = conn.execute(text(query), params)
                    rows = res.fetchall()
                    if rows:
                        df = pd.DataFrame([dict(r._mapping) for r in rows])
                        df.insert(0, "STT", range(len(df)))
                        df.columns = ["STT", "編號", "名稱/合約", "類別", "廠區", "品牌/型號/房東", "租約起始", "租約到期", "狀態"]
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("目前尚無固定資產或租賃合約紀錄。")
            except Exception as e:
                st.error("讀取資產資料失敗: " + str(e))

    # ----------------------------------------------------
    # ➕ Tab 2: 新增固定資產 (連動廠區管理)
    # ----------------------------------------------------
    with tab_add:
        st.markdown("### ➕ 新增固定資產與租賃合約")
        with st.form("form_add_asset"):
            col1, col2 = st.columns(2)
            with col1:
                a_code = st.text_input("資產/合約編號 *", placeholder="例: AST-EQ-005")
                a_name = st.text_input("資產或合約名稱 *", placeholder="例: CNC 數控母線排切加工機")
                a_factory = st.selectbox("存放廠區/據點 *", current_factories)
                a_cat = st.selectbox("資產類別", ["土地與房屋租賃", "生產機具", "車輛", "電腦與資訊設備", "辦公設備", "網路伺服器", "品管儀器", "倉儲物流", "消防工安"])

            with col2:
                a_brand = st.text_input("品牌與型號 / 房東與出租方", placeholder="例: Amada - CNC Busbar 160T")
                a_status = st.selectbox("目前狀態", ["🟢 在用/租賃中 (Active)", "🟡 租約將到期", "🔴 停用/維修中"])
                a_cost = st.number_input("取得成本或月租金/總租金 (USD / VND)", min_value=0.0, value=1500.0, step=100.0)

            st.markdown("##### 📅 租賃合約專用日期 (若非土地房屋租賃可不填)")
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                a_start = st.date_input("租約起始日期 (Lease Start Date)", datetime.date.today())
            with c_d2:
                a_end = st.date_input("租約到期日期 (Lease Expiry Date)", datetime.date.today() + datetime.timedelta(days=1095))

            if st.form_submit_button("📌 確認新增固定資產或合約", type="primary", use_container_width=True):
                if engine and a_code and a_name:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.fixed_assets 
                                (asset_code, asset_name, category, factory, brand_landlord, status, cost_amount, start_date, end_date)
                                VALUES (:code, :name, :cat, :fac, :brand, :st, :cost, :start, :end)
                                ON CONFLICT (asset_code) DO UPDATE
                                SET asset_name = EXCLUDED.asset_name,
                                    category = EXCLUDED.category,
                                    factory = EXCLUDED.factory,
                                    brand_landlord = EXCLUDED.brand_landlord,
                                    status = EXCLUDED.status,
                                    cost_amount = EXCLUDED.cost_amount,
                                    start_date = EXCLUDED.start_date,
                                    end_date = EXCLUDED.end_date;
                            """), {
                                "code": a_code, "name": a_name, "cat": a_cat, "fac": a_factory,
                                "brand": a_brand, "st": a_status, "cost": a_cost, "start": a_start, "end": a_end
                            })
                        st.success(f"🎉 成功新增資產/合約：{a_name} ({a_code})，已綁定至【{a_factory}】！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入資料庫失敗: " + str(e))
                else:
                    st.warning("⚠️ 請填寫資產編號與名稱！")

    # ----------------------------------------------------
    # ✏️ Tab 3: 修改資產與租賃資料
    # ----------------------------------------------------
    with tab_edit:
        st.markdown("### ✏️ 修改現有固定資產與租賃合約資料")
        if engine:
            try:
                with engine.connect() as conn:
                    res_a = conn.execute(text("SELECT asset_code, asset_name, factory FROM public.fixed_assets WHERE status NOT LIKE '%報廢%' ORDER BY asset_code;"))
                    ast_list = res_a.fetchall()
                    if ast_list:
                        ast_opts = {f"{r.asset_code} - {r.asset_name} ({r.factory})": r.asset_code for r in ast_list}
                        selected_ast_label = st.selectbox("請選擇要修改的資產或合約：", list(ast_opts.keys()))
                        target_ast_code = ast_opts[selected_ast_label]

                        ast_detail = conn.execute(text("SELECT * FROM public.fixed_assets WHERE asset_code = :c;"), {"c": target_ast_code}).fetchone()
                        if ast_detail:
                            ad = dict(ast_detail._mapping)
                            with st.form("form_edit_asset_full"):
                                col_ea1, col_ea2 = st.columns(2)
                                with col_ea1:
                                    edit_a_name = st.text_input("資產/合約名稱", value=str(ad.get("asset_name") or ""))
                                    curr_fac = str(ad.get("factory") or "")
                                    fac_idx = current_factories.index(curr_fac) if curr_fac in current_factories else 0
                                    edit_a_factory = st.selectbox("存放廠區/據點", current_factories, index=fac_idx)
                                with col_ea2:
                                    edit_a_brand = st.text_input("品牌與型號 / 房東", value=str(ad.get("brand_landlord") or ""))
                                    edit_a_cost = st.number_input("金額 (USD / VND)", value=float(ad.get("cost_amount") or 0.0))

                                if st.form_submit_button("💾 儲存修改內容", type="primary"):
                                    with engine.begin() as conn_u:
                                        conn_u.execute(text("""
                                            UPDATE public.fixed_assets
                                            SET asset_name = :name, factory = :fac, brand_landlord = :brand, cost_amount = :cost, updated_at = CURRENT_TIMESTAMP
                                            WHERE asset_code = :code;
                                        """), {"name": edit_a_name, "fac": edit_a_factory, "brand": edit_a_brand, "cost": edit_a_cost, "code": target_ast_code})
                                    st.success(f"✅ 已成功更新資產【{edit_a_name}】資料！")
                                    st.rerun()
            except Exception as e:
                st.error("讀取失敗: " + str(e))

    # ----------------------------------------------------
    # 🗑️ Tab 4: 辦理資產報廢或合約終止
    # ----------------------------------------------------
    with tab_terminate:
        st.markdown("### 🗑️ 辦理資產報廢或租賃合約終止")

    # ----------------------------------------------------
    # 📜 Tab 5: 歷史報廢紀錄
    # ----------------------------------------------------
    with tab_history:
        st.markdown("### 📜 歷史報廢與停用資產紀錄")

def render_asset_management(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_asset_management_page(engine=engine, lang=lang, **kwargs)
