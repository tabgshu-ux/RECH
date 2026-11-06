import streamlit as st
import pandas as pd
from sqlalchemy import text

def init_department_table(engine):
    """確保資料庫中存在支援多階層 (1~4級) 的部門與模組設定表"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_departments (
                        id SERIAL PRIMARY KEY,
                        level_1 VARCHAR(100) NOT NULL,
                        level_2 VARCHAR(100),
                        level_3 VARCHAR(100),
                        level_4 VARCHAR(100),
                        module_name VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.warning(f"⚠️ 資料庫部門表初始化提示: {e}")

def get_department_module_tree_from_db(engine):
    """從資料庫讀取 1~4 級的組織與模組樹狀結構"""
    tree = {}
    if engine is not None:
        try:
            init_department_table(engine)
            with engine.connect() as conn:
                df = pd.read_sql(text("SELECT level_1, level_2, level_3, level_4, module_name FROM sys_departments"), con=conn)
                if not df.empty:
                    for _, row in df.iterrows():
                        l1 = row["level_1"]
                        l2 = row["level_2"]
                        l3 = row["level_3"]
                        l4 = row["level_4"]
                        mod = row["module_name"]

                        if l1 not in tree:
                            tree[l1] = {"sub": {}, "modules": []}
                        
                        current_dict = tree[l1]
                        
                        # 處理 2~4 級階層
                        if l2:
                            if l2 not in current_dict["sub"]:
                                current_dict["sub"][l2] = {"sub": {}, "modules": []}
                            current_dict = current_dict["sub"][l2]
                            if l3:
                                if l3 not in current_dict["sub"]:
                                    current_dict["sub"][l3] = {"sub": {}, "modules": []}
                                current_dict = current_dict["sub"][l3]
                                if l4:
                                    if l4 not in current_dict["sub"]:
                                        current_dict["sub"][l4] = {"sub": {}, "modules": []}
                                    current_dict = current_dict["sub"][l4]
                        
                        if mod and mod not in current_dict["modules"]:
                            current_dict["modules"].append(mod)
                    return tree
        except Exception as e:
            st.error(f"⚠️ 讀取資料庫部門樹失敗: {e}")

    # Fallback 預設架構（若資料庫尚無資料時的初始 1~4 級標準結構）
    return {
        "📈 總經理室 (Executive Office)": {
            "sub": {
                "經營決策支援": {
                    "sub": {
                        "智慧採購與行情": {
                            "sub": {},
                            "modules": ["🔴 原料價格與 Gemini 智慧採購顧問", "📰 越南經營政策與法規每日動態"]
                        }
                    },
                    "modules": ["📊 財務類顯示資料 (AR/AP & P&L)", "⚡ 工程專案進度與現場異常監控"]
                }
            },
            "modules": []
        },
        "👔 管理部 (Management Dept)": {
            "sub": {
                "人事行政課": {
                    "sub": {},
                    "modules": ["公司公告", "員工檔案", "員工打卡紀錄", "密碼修改", "員工薪資與保險"]
                },
                "總務後勤課": {
                    "sub": {
                        "廠區與生活": {
                            "sub": {},
                            "modules": ["宿舍與伙食", "工作廠區管理", "固定資產管理", "文件管理"]
                        },
                        "車輛管理": {
                            "sub": {},
                            "modules": ["車輛進出口", "車輛維修紀錄"]
                        }
                    },
                    "modules": []
                },
                "財務會計課": {
                    "sub": {},
                    "modules": ["採購與應付帳款", "應收帳款管理", "越南稅務報表", "電子發票管理"]
                }
            },
            "modules": []
        },
        "🛠️ 工程與設計管理中心 (Engineering & Design Center)": {
            "sub": {
                "案場與專案管理": {
                    "sub": {},
                    "modules": ["⚡ 1. 工程主管戰情室與案場管理", "⚡ 2. 工程專案報價系統", "📋 3. 施工日報表與點工點料登記"]
                },
                "技術與安衛管理": {
                    "sub": {},
                    "modules": ["🤖 4. AI 施工照片辨識與稽核", "⚠️ 5. 工程證照預警與機具檢驗預警", "🎨 6. 配電盤電氣與機構設計圖庫", "🔌 7. 配電盤 BOM 零件與採購連動", "👷 8. 外包商計價與偶鐸管理", "🧪 9. FAT/SAT 出廠與現場驗收管理"]
                }
            },
            "modules": []
        }
    }

def render(engine=None, lang="繁體中文", **kwargs):
    st.title("⚙️ 系統設定與 1~4 級動態組織架構管理")
    st.caption("完整支援 1~4 級組織階層與模組掛載，所有設定直接與 PostgreSQL 資料庫同步。")
    st.markdown("---")

    # 確保資料庫表格就緒
    if engine is not None:
        init_department_table(engine)
    else:
        st.warning("⚠️ 目前資料庫引擎未連線，操作將僅暫存於記憶體中。")

    tree = get_department_module_tree_from_db(engine)

    # 1. 新增/擴充 1~4 級部門與模組表單
    with st.form("add_multi_level_dept_form"):
        st.markdown("#### ➕ 新增 / 掛載 1~4 級組織與模組")
        col1, col2 = st.columns(2)
        with col1:
            lvl_1 = st.text_input("第一級部門 (Level 1) *", placeholder="例如: 👔 管理部 (Management Dept)")
            lvl_2 = st.text_input("第二級部門 (Level 2 - 選填)", placeholder="例如: 人事行政課")
        with col2:
            lvl_3 = st.text_input("第三級部門 (Level 3 - 選填)", placeholder="例如: 薪資福利組")
            lvl_4 = st.text_input("第四級部門 (Level 4 - 選填)", placeholder="例如: 考勤與投保")

        new_module = st.text_input("掛載之功能模組名稱 *", placeholder="例如: 📋 員工保險明細查詢")
        
        submitted = st.form_submit_button("💾 寫入資料庫並掛載模組", type="primary")
        if submitted:
            if lvl_1 and new_module:
                if engine is not None:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO sys_departments (level_1, level_2, level_3, level_4, module_name)
                                VALUES (:l1, :l2, :l3, :l4, :mod)
                            """), {
                                "l1": lvl_1.strip(),
                                "l2": lvl_2.strip() if lvl_2 else None,
                                "l3": lvl_3.strip() if lvl_3 else None,
                                "l4": lvl_4.strip() if lvl_4 else None,
                                "mod": new_module.strip()
                            })
                        st.success(f"🎉 成功將模組「{new_module}」掛載至 1~4 級組織架構中，並已同步至資料庫！")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"⚠️ 資料庫寫入失敗：{str(db_err)}")
                else:
                    st.success("🎉 (離線模式) 模組掛載成功！")
            else:
                st.warning("⚠️ 請至少填寫【第一級部門】與【功能模組名稱】！")

    st.markdown("---")
    st.markdown("#### 📂 現有 1~4 級組織架構與資料庫連線檢視")

    # 顯示目前資料庫中的結構
    for l1, data in tree.items():
        with st.expander(f"📁 1級: {l1}"):
            if data["modules"]:
                st.markdown("**[直屬模組]**")
                for m in data["modules"]:
                    st.markdown(f" - {m}")
            
            for l2, sub_data_2 in data["sub"].items():
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;└── 📁 **2級: {l2}**")
                if sub_data_2["modules"]:
                    for m in sub_data_2["modules"]:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• {m}")
                
                for l3, sub_data_3 in sub_data_2["sub"].items():
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── 📁 **3級: {l3}**")
                    if sub_data_3["modules"]:
                        for m in sub_data_3["modules"]:
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• {m}")
                    
                    for l4, sub_data_4 in sub_data_3["sub"].items():
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── 📁 **4級: {l4}**")
                        if sub_data_4["modules"]:
                            for m in sub_data_4["modules"]:
                                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• {m}")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
