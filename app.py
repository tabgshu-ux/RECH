elif "管理部" in selected_dept:
        st.title("👔 管理部營運管理中心")
        st.info(f"當前選定功能：{selected_sub_mod}")
        
        # 根據選擇的子功能動態載入對應模組
        if "公司公告" in selected_sub_mod:
            try:
                from modules.management import company_announcements
                company_announcements.show(engine=engine, lang=curr_lang)
            except Exception as e:
                st.error(f"無法載入公司公告模組: {e}")
                
        elif "員工檔案" in selected_sub_mod:
            try:
                from modules.management import employee_profile
                employee_profile.show(engine=engine, lang=curr_lang)
            except Exception as e:
                st.info("💡 員工檔案模組正在進行資料庫對接...")
                st.write(f"正在執行：{selected_sub_mod} 的業務邏輯與表單介面...")
        else:
            st.write(f"正在執行：{selected_sub_mod} 的業務邏輯與表單介面...")
