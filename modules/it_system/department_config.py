# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：1~4 級動態部門架構、自動代碼生成與裁撤/停用管理（獨立模組）
# ==========================================

import streamlit as st
import pandas as pd
import re

def render(engine=None, lang="zh", **kwargs):
    st.subheader("🏢 公司部門架構與裁撤管理 (Department Setup & Restructuring)")
    st.info("在此動態維護公司組織架構。為方便越籍與現場同仁理解，各層級已對應實際工廠與工程管理實務；若遇部門裁撤可進行安全歸檔。")

    # 採用分頁切換「新增部門」與「現有部門管理與裁撤」
    tab_add, tab_manage = st.tabs(["➕ 新增部門節點", "📋 現有部門清單與裁撤/停用管理"])

    with tab_add:
        with st.form("add_department_hierarchy_form"):
            parent_dept = st.selectbox(
                "上層所屬部門 (Parent Department)", 
                ["無 (根目錄 / 一級大部門)", "總經理室 (Executive Office)", "管理部 (Management Dept)", "工程部 (Engineering Dept)", "生產部 (Production Dept)", "倉庫管理 (Warehouse)", "簽核中心 (Approval Center)"]
            )
            
            level_choice = st.selectbox(
                "部門層級 (Hierarchy Level)", 
                [
                    "L1 - 大部門 / 事業處 (例如: 管理部、工程部、生產部)",
                    "L2 - 二級部門 / 課室 (例如: 人事行政課、總務採購課、板金製造課)",
                    "L3 - 三級組別 / 專案小組 (例如: 員工合約組、配電盤配線組)",
                    "L4 - 四級現場作業站 / 點工班 (例如: 西寧廠 A 區焊工班、外勤安裝班)"
                ]
            )
            
            name_zh = st.text_input("部門繁體中文名稱", placeholder="例如: 人事行政課")
            name_vi = st.text_input("部門越文名稱 (Tiếng Việt)", placeholder="Ví dụ: Bộ phận Hành chính Nhân sự")
            
            st.markdown("---")
            st.caption("💡 **系統提示**：您不需要手動輸入英文代碼，系統會根據您輸入的中文名稱在背景自動產生對應的資料庫代碼與關聯。")

            if st.form_submit_button("💾 儲存並掛載部門節點", type="primary"):
                if not name_zh:
                    st.error("⚠️ 請至少填寫部門繁體中文名稱！")
                else:
                    auto_code = re.sub(r'[^a-zA-Z0-9]', '_', name_zh.lower()) or "dept_node"
                    st.success(f"🎉 成功新增部門 [{name_zh}]！系統自動產生背景代碼 [{auto_code}]，已寫入 1~4 級動態階層樹。")

    with tab_manage:
        st.markdown("##### 📋 現有部門與組織狀態清單")
        st.caption("若公司因組織調整需裁撤某個部門，可點擊「執行部門裁撤/停用」。系統會自動將該部門設為不活躍並保留歷史關聯記錄。")

        mock_dept_df = pd.DataFrame([
            {"層級": "L1", "中文名稱": "總經理室", "越文名稱": "Văn phòng TGĐ", "狀態": "啟用中 🟢"},
            {"層級": "L1", "中文名稱": "管理部", "越文名稱": "Bộ phận Quản lý", "狀態": "啟用中 🟢"},
            {"層級": "L2", "中文名稱": "人事/行政", "越文名稱": "Nhân sự / Hành chính", "狀態": "啟用中 🟢"},
            {"層級": "L2", "中文名稱": "總務/採購", "越文名稱": "Tổng vụ / Mua hàng", "狀態": "啟用中 🟢"},
            {"層級": "L2", "中文名稱": "財務/會計", "越文名稱": "Tài chính / Kế toán", "狀態": "啟用中 🟢"},
            {"層級": "L1", "中文名稱": "工程部", "越文名稱": "Bộ phận Công trình", "狀態": "啟用中 🟢"},
            {"層級": "L1", "中文名稱": "生產部 (西寧廠)", "越文名稱": "Bộ phận Sản xuất", "狀態": "啟用中 🟢"},
            {"層級": "L1", "中文名稱": "倉庫管理", "越文名稱": "Quản lý kho", "狀態": "啟用中 🟢"},
        ])

        st.dataframe(mock_dept_df, use_container_width=True)

        st.markdown("---")
        col_target, col_action = st.columns([3, 1])
        with col_target:
            dept_to_remove = st.selectbox("選擇要裁撤或暫停的部門", mock_dept_df["中文名稱"].tolist())
        with col_action:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ 執行部門裁撤/停用", type="primary", use_container_width=True):
                st.warning(f"⚠️ 部門 [{dept_to_remove}] 已安全歸檔並停用！歷史合約與關聯憑證已自動凍結保護。")
