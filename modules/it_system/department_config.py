import streamlit as st
import pandas as pd
from sqlalchemy import text

def init_org_table(engine):
    """確保資料庫中存在支援無限階層 (N-Tier) 擴展的組織與模組設定表"""
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

def get_department_module_tree(engine=None):
    """相容舊版 app.py 呼叫的樹狀結構轉譯器（返回標準字典格式）"""
    tree = {}
    org_units = []
    if engine is not None:
        try:
            init_org_table(engine)
            with engine.connect() as conn:
                df = pd.read_sql(text("SELECT id, parent_id, unit_name, module_name FROM sys_org_units ORDER BY id ASC"), con=conn)
                org_units = df.to_dict(orient="records")
        except Exception:
            pass

    if not org_units:
        # 預設標準結構
        return {
            "📈 總經理室 (Executive Office)": [
                "🔴 原料價格與 Gemini 智慧採購顧問",
                "📊 財務類顯示資料 (AR/AP & P&L)",
                "⚡ 工程專案進度與現場異常監控",
                "📰 越南經營政策與法規每日動態"
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
                "✂️ [板金] 板金加工組工單與條碼",
                "🎨 [塗料] 粉體塗裝烤漆組品管",
                "⚡ [配盤] 配電盤組裝配線組"
            ],
            "📦 倉庫管理 (Warehouse Management)": [
                "📦 [倉儲] 倉庫庫存與資材條碼管理"
            ],
            "📍 外勤工程打卡與工作回報 (Field Attendance)": [
                "📍 現場外勤打卡與工作回報"
            ],
            "✍️ 電子簽核中心 (Approval Center)": [
                "✍️ 提交請假/採購與即時進度追蹤 / 審核"
            ]
        }
    
    # 透過資料庫中的無限階層資料動態建構選單字典
    root_nodes = [u for u in org_units if u['parent_id'] is None or u['parent_id'] == 0]
    for root in root_nodes:
        r_name = root['unit_name']
        tree[r_name] = []
        # 尋找第一層子節點或直接掛載模組
        children = [u for u in org_units if u['parent_id'] == root['id']]
        for child in children:
            if child['module_name']:
                tree[r_name].append(child['module_name'])
            # 遞迴抓取更深層的模組
            sub_children = [u for u in org_units if u['parent_id'] == child['id']]
            for sc in sub_children:
                if sc['module_name']:
                    tree[r_name].append(f"[{child['unit_name']}] {sc['module_name']}")
        if not tree[r_name]:
            tree[r_name] = ["(此部門尚無掛載模組)"]

    return tree

def render(engine=None, lang="繁體中文", **kwargs):
    st.title("⚙️ 系統設定與無限階層動態組織管理 (N-Tier SaaS Org Engine)")
    st.caption("支援企業未來任意深度擴張與動態模組掛載，所有設定直接與 PostgreSQL 資料庫同步。")
    st.markdown("---")

    if engine is not None:
        init_org_table(engine)
    else:
        st.warning("⚠️ 目前資料庫引擎未連線。")

    org_units = []
    if engine is not None:
        try:
            with engine.connect() as conn:
                df = pd.read_sql(text("SELECT id, parent_id, unit_name, module_name FROM sys_org_units ORDER BY id ASC"), con=conn)
                org_units = df.to_dict(orient="records")
        except Exception as e:
            st.error(f"⚠️ 讀取組織架構失敗: {e}")

    unit_options = {"無 (根節點 / Root)": None}
    for u in org_units:
        unit_options[f"ID: {u['id']} - {u['unit_name']}"] = u['id']

    with st.form("add_n_tier_org_form"):
        st.markdown("#### ➕ 新增組織單位或掛載功能模組（支援任意擴展深度）")
        
        col1, col2 = st.columns(2)
        with col1:
            parent_selection = st.selectbox("選擇上級部門 (Parent Unit)", list(unit_options.keys()))
            parent_id = unit_options[parent_selection]
        with col2:
            unit_name = st.text_input("組織/部門名稱 *", placeholder="例如: 總經理室、管理部、人事行政課...")

        module_name = st.text_input("掛載之功能模組名稱 (選填)", placeholder="例如: 員工檔案、專案報價系統...")

        submitted = st.form_submit_button("💾 寫入資料庫並擴展組織", type="primary")
        if submitted:
            if unit_name.strip():
                if engine is not None:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO sys_org_units (parent_id, unit_name, module_name)
                                VALUES (:pid, :name, :mod)
                            """), {
                                "pid": parent_id,
                                "name": unit_name.strip(),
                                "mod": module_name.strip() if module_name else None
                            })
                        st.success(f"🎉 成功新增組織單位「{unit_name.strip()}」並同步至資料庫！")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"⚠️ 資料庫寫入失敗：{str(db_err)}")
                else:
                    st.success("🎉 (離線模式) 組織新增成功！")
            else:
                st.warning("⚠️ 請填寫組織/部門名稱！")

    st.markdown("---")
    st.markdown("#### 📂 現有企業組織架構與無限階層樹狀檢視")

    if not org_units:
        st.info("💡 目前資料庫尚無組織架構資料，請透過上方表單建立根節點。")
    else:
        def render_tree(p_id, level=0):
            children = [u for u in org_units if u['parent_id'] == p_id]
            for child in children:
                indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * level
                mod_str = f" ➔ [掛載模組: {child['module_name']}]" if child['module_name'] else ""
                
                col_t1, col_t2 = st.columns([5, 1])
                with col_t1:
                    st.markdown(f"{indent} 📁 **{child['unit_name']}** (ID: {child['id']}){mod_str}", unsafe_allow_html=True)
                with col_t2:
                    if st.button("🗑️ 刪除", key=f"del_unit_{child['id']}"):
                        if engine is not None:
                            try:
                                with engine.begin() as conn:
                                    conn.execute(text("DELETE FROM sys_org_units WHERE id = :uid"), {"uid": child['id']})
                                st.success(f"已刪除節點 ID: {child['id']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"刪除失敗: {e}")
                
                render_tree(child['id'], level + 1)

        root_nodes = [u for u in org_units if u['parent_id'] is None or u['parent_id'] == 0]
        if not root_nodes and org_units:
            root_nodes = org_units

        render_tree(None, 0)

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
