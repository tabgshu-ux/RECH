elif st.session_state['current_view'] == 'dynamic_feature':
    active_feat_id = str(st.session_state.get('active_feature_id', ''))
    
    # 🌟 IT 系統設定
    if active_feat_id == 'feat_it_menu':
        render_admin_settings(db_engine, lang=current_lang)
        
    # 🌟 管理部主管戰情室
    elif active_feat_id == 'feat_mgmt_supervisor':
        try:
            from modules.management.supervisor_dashboard import render
            render(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入管理部主管戰情室發生錯誤: {e}")
            
    # 🌟 智慧判斷：不管資料庫代碼是什麼，只要文字包含特定關鍵字就導向對應的獨立頁面
    elif '員工' in active_feat_id or '履約' in active_feat_id or active_feat_id == 'feat_hr':
        try:
            from modules.management.hr import employee_profile
            if hasattr(employee_profile, "render_hr_profile_page"):
                employee_profile.render_hr_profile_page(engine=db_engine, lang=current_lang)
            elif hasattr(employee_profile, "render"):
                employee_profile.render(db_engine=db_engine, lang=current_lang)
            else:
                st.error("找不到 employee_profile 的渲染入口函式。")
        except Exception as e:
            st.error(f"載入員工檔案管理模組發生錯誤: {e}")

    elif '考勤' in active_feat_id or '打卡' in active_feat_id:
        try:
            from modules.management.hr.attendance import attendance_punch
            if hasattr(attendance_punch, "render"):
                attendance_punch.render(db_engine=db_engine, lang=current_lang)
            elif hasattr(attendance_punch, "main"):
                attendance_punch.main(db_engine=db_engine, lang=current_lang)
            else:
                st.info("⏱️ 考勤打卡模組已載入。")
        except Exception as e:
            st.error(f"載入考勤打卡模組發生錯誤: {e}")

    elif '薪資' in active_feat_id or '保險' in active_feat_id or 'BHXH' in active_feat_id:
        try:
            from modules.management.hr import payroll_management
            if hasattr(payroll_management, "render"):
                payroll_management.render(db_engine=db_engine, lang=current_lang)
            elif hasattr(payroll_management, "render_payroll_management"):
                payroll_management.render_payroll_management(db_engine=db_engine, lang=current_lang)
            else:
                st.info("💰 薪資計算與保險模組已載入。")
        except Exception as e:
            st.error(f"載入薪資保險模組發生錯誤: {e}")

    # 🌟 其他部門模組路由
    elif active_feat_id == 'feat_ga':
        try:
            from modules.procurement_ap import render_procurement_ap_page
            render_procurement_ap_page(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入總務採購模組發生錯誤: {e}")
    elif active_feat_id == 'feat_fi':
        try:
            from modules.financial_tax_reports import render_financial_tax_reports_page
            render_financial_tax_reports_page(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入財務會計模組發生錯誤: {e}")
    elif active_feat_id == 'feat_site_log':
        try:
            from modules.engineering_management import render_engineering_management_page
            render_engineering_management_page(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入工程管理模組發生錯誤: {e}")
    elif active_feat_id == 'feat_panel_build':
        try:
            from modules.assembly import render_assembly_module
            render_assembly_module(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入生產組裝模組發生錯誤: {e}")
    elif active_feat_id == 'feat_material':
        try:
            from modules.warehouse_management import render_warehouse_management
            render_warehouse_management(db_engine, lang=current_lang)
        except Exception as e:
            st.error(f"載入倉庫管理模組發生錯誤: {e}")
    elif active_feat_id == 'feat_my_approvals':
        try:
            from modules.approval_workflow import render_approval_center
            render_approval_center(lang=current_lang)
        except Exception as e:
            st.error(f"載入簽核中心發生錯誤: {e}")
    else:
        st.info(f"💡 功能代碼 [{active_feat_id}] 正在建置中，您可以透過上方按鈕返回部門選單。")
