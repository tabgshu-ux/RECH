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

def render(engine=None, lang="繁體中文", **kwargs):
    st.title("⚙️ 系統設定與無限階層動態組織管理 (N-Tier SaaS Org Engine)")
    st.caption("落實 Global SaaS 規範：不綁死部門層級，支援企業未來任意深度擴張與動態模組掛載。")
    st.markdown("---")

    if engine is not None:
        init_org_table(engine)
    else:
        st.warning("⚠️ 目前資料庫引擎未連線。")

    # 讀取現有組織單位
    org_units = []
    if engine is not None:
        try:
            with engine.connect() as conn:
                df = pd.read_sql(text("SELECT id, parent_id, unit_name, module_name FROM sys_org_units ORDER BY id ASC"), con=conn)
                org_units = df.to_dict(orient="records")
        except Exception as e:
            st.error(f"⚠️ 讀取組織架構失敗: {e}")

    # 建立上級部門選項對照
    unit_options = {"無 (根節點 / Root)": None}
    for u in org_units:
        unit_options[f"ID: {u['id']} - {u['unit_name']}"] = u['id']

    # 1. 動態新增組織與模組掛載表單
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
        st.info("💡 目前資料庫尚無組織架構資料，請透過上方表單建立根節點（例如：總經理室、管理部）。")
    else:
        # 簡易遞迴渲染函式 (Recursive Tree Viewer)
        def render_tree(p_id, level=0):
            children = [u for u in org_units if u['parent_id'] == p_id]
            for child in children:
                indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * level
                mod_str = f" ➔ [掛載模組: {child['module_name']}]" if child['module_name'] else ""
                
                col_t1, col_t2 = st.columns([5, 1])
                with col_t1:
                    st.markdown(f"{indent} 📁 **{child['unit_name']}** (ID: {child['id']}){mod_str}rit", unsafe_allow_html=True)
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
                
                # 遞迴渲染子節點
                render_tree(child['id'], level + 1)

        # 從根節點 (parent_id IS NULL) 開始渲染
        root_nodes = [u for u in org_units if u['parent_id'] is None or u['parent_id'] == 0]
        if not root_nodes and org_units:
            # 相容性防護：若沒有明確的 NULL，直接抓取第一層
            root_nodes = org_units

        render_tree(None, 0)

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
