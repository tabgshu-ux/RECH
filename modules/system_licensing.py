import pandas as pd
import streamlit as st


def render_licensing_control_page(engine=None, lang="繁體中文"):
    st.title("🎛️ 資訊管理部 - 客戶 ERP 模組授權與廠區設定")
    st.caption("管理全集團全球廠區據點、模組授權開關與資料刪除維護。")

    # 初始化廠區與授權資料庫
    if "global_plants_db" not in st.session_state or not st.session_state.global_plants_db:
        st.session_state.global_plants_db = [
            {"id": "FACT-VN-01", "name": "西寧廠", "country": "越南", "currency": "VND", "revenue": "NT$ 12.5M", "status": "🟢 營運中"},
            {"id": "FACT-VN-02", "name": "CN 東莞一廠 (線材/塑膠)", "country": "中國", "currency": "RMB", "revenue": "¥ 3.4M", "status": "🟢 營運中"},
            {"id": "FACT-BH-01", "name": "VN 越南平陽/西寧廠 (配電盤/板金)", "country": "越南", "currency": "VND", "revenue": "₫ 12.8B", "status": "🟢 營運中"},
        ]

    tab_manage, tab_add = st.tabs(["📑 現有廠區據點與刪除管理", "➕ 新增海外廠區/分公司據點"])

    # ----------------------------------------------------
    # 📑 頁籤一：現有據點與刪除功能
    # ----------------------------------------------------
    with tab_manage:
        st.markdown("### 📋 全球廠區據點一覽（可勾選欲刪除的項目）")
        
        # 使用 Data Editor 讓使用者可以直接勾選刪除，或透過下方按鈕整筆移除
        df_plants = pd.DataFrame(st.session_state.global_plants_db)
        
        # 加上選取刪除欄位
        if "刪除" not in df_plants.columns:
            df_plants.insert(0, "刪除", False)

        edited_df = st.data_editor(
            df_plants,
            use_container_width=True,
            num_rows="dynamic",
            key="plant_editor"
        )

        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("🗑️ 刪除勾選的廠區據點", type="primary"):
                # 過濾掉被勾選刪除的列
                remaining_rows = []
                for idx, row in edited_df.iterrows():
                    if not row.get("刪除", False):
                        # 移除輔助的「刪除」欄位再存回
                        clean_row = {k: v for k, v in row.items() if k != "刪除"}
                        remaining_rows.append(clean_row)
                
                st.session_state.global_plants_db = remaining_rows
                st.success("✅ 已成功刪除選定的廠區據點資料！")
                st.rerun()

        with col_act2:
            if st.button("💾 儲存表格修改結果"):
                updated_rows = []
                for idx, row in edited_df.iterrows():
                    clean_row = {k: v for k, v in row.items() if k != "刪除"}
                    updated_rows.append(clean_row)
                st.session_state.global_plants_db = updated_rows
                st.success("✅ 廠區資料修改已成功儲存！")
                st.rerun()

    # ----------------------------------------------------
    # ➕ 頁籤二：新增據點
    # ----------------------------------------------------
    with tab_add:
        st.markdown("### ➕ 新增全球廠區據點")
        with st.form("form_add_plant"):
            c1, c2 = st.columns(2)
            plant_id = c1.text_input("廠區代碼 *", value="FACT-ID-01 (印尼廠)")
            plant_name = c2.text_input("廠區/子公司名稱 *", value="印尼雅加達新廠")

            c3, c4, c5 = st.columns(3)
            country = c3.text_input("所在國家/區域", value="印尼 (Indonesia)")
            currency = c4.selectbox("當地記帳本位幣", ["USD", "VND", "RMB", "TWD", "IDR"])
            status = c5.selectbox("廠區營運狀態", ["🟢 營運中", "🔧 籌備中", "⏸️ 暫停營運"])

            if st.form_submit_button("💾 儲存並將新廠區加入集團戰情室", type="primary"):
                if plant_id and plant_name:
                    st.session_state.global_plants_db.append({
                        "id": plant_id,
                        "name": plant_name,
                        "country": country,
                        "currency": currency,
                        "revenue": "0.0",
                        "status": status
                    })
                    st.success(f"🎉 已成功新增廠區 [{plant_name}]！")
                    st.rerun()
                else:
                    st.error("請填寫廠區代碼與名稱！")


def show(engine=None, lang="繁體中文"):
    render_licensing_control_page(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_licensing_control_page(engine, lang)
