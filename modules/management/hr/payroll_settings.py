    # 2. 應領與應扣項目輕鬆新增區塊 (不需要打英文 Key!)
    st.markdown("---")
    st.markdown("#### 📑 薪資項目自由增修與預設金額設定")
    st.caption("請直接選擇對應的系統核心欄位，或建立全新自訂項目，系統將自動完成底層欄位串聯。")

    # 建立系統核心英文 Key 對照字典，讓使用者用選的，避免手動輸入錯誤
    SYSTEM_KEYS_OPTIONS = {
        "職務津貼 (Position Allowance)": "pos_allowance",
        "評核獎金 (Evaluation Bonus)": "eval_bonus",
        "出差油費 (Gas Allowance)": "gas_allowance",
        "工程補助 (Project Allowance)": "spec_bonus",
        "餐費 (Meal Fee)": "meal_fee",
        "績效獎金 (Production Bonus)": "prod_bonus",
        "電話/網路補貼 (Network Fee)": "network_fee",
        "看倉管 (Warehouse Fee)": "warehouse_fee",
        "全勤獎金 (Attendance Bonus)": "attendance_bonus",
        "所得稅 (Personal Income Tax)": "pit_tax",
        "本月預支 (Advance Pay)": "advance_pay",
        "其他扣款 (Other Deduction)": "other_deduct",
        "➕ 建立全新自訂項目 (由系統自動生成欄位 Key)": "AUTO_GENERATE"
    }

    with st.form("form_quick_add_field"):
        # 使用 Streamlit 的 columns 佈局，在手機版會自動垂直排列，符合 Mobile-First 排版
        c_a, c_b, c_c, c_d = st.columns(4)
        with c_a:
            q_cat = st.selectbox("項目類別", ["應領項目 (Income)", "應扣項目 (Deduct)"])
        with c_b:
            q_zh = st.text_input("中文名稱", placeholder="例如：夜班津貼")
        with c_c:
            q_vn = st.text_input("越文名稱", placeholder="PC ca đêm")
        with c_d:
            q_amt = st.number_input("預設金額 (VND)", min_value=0.0, value=0.0, step=100000.0)

        # 關鍵防呆優化：取代傳統繁瑣的英文 Key 輸入框
        st.markdown("**🔗 系統底層關聯設定 (System Mapping)**")
        selected_label = st.selectbox(
            "請選擇此項目要對應的系統核心英文 Key", 
            list(SYSTEM_KEYS_OPTIONS.keys()),
            help="選擇此項目對應的系統底層計算代號。如果是全新項目，請選擇最後一項。"
        )
        
        chosen_key = SYSTEM_KEYS_OPTIONS[selected_label]

        if st.form_submit_button("➕ 新增薪資項目到系統", type="primary", use_container_width=True):
            if q_zh:
                cat_val = "income" if "應領" in q_cat else "deduct"
                
                # 分流處理：如果是自訂項目，則透過時間戳記自動生成唯一代碼
                if chosen_key == "AUTO_GENERATE":
                    import time
                    final_key = f"custom_field_{int(time.time())}"
                else:
                    final_key = chosen_key
                
                if engine:
                    try:
                        with engine.begin() as conn:
                            # 檢查該 Key 是否已被佔用，防止 ON CONFLICT 錯誤
                            check_exist = conn.execute(
                                text("SELECT COUNT(*) FROM public.erp_dynamic_fields WHERE field_key = :key"), 
                                {"key": final_key}
                            ).scalar()
                            
                            if check_exist > 0:
                                st.error(f"❌ 系統核心欄位 `{final_key}` 已經存在於清單中，無法重複新增！")
                            else:
                                conn.execute(text("""
                                    INSERT INTO public.erp_dynamic_fields (category, field_key, field_name_zh, field_name_vn, default_amount, sort_order)
                                    VALUES (:cat, :key, :zh, :vn, :amt, 99)
                                    ON CONFLICT (field_key) DO NOTHING;
                                """), {"cat": cat_val, "key": final_key, "zh": q_zh, "vn": q_vn, "amt": q_amt})
                                st.success(f"✅ 成功將 [{q_zh}] 串聯至系統核心欄位 `{final_key}`！")
                                st.rerun()
                    except Exception as e:
                        st.error("❌ 新增失敗: " + str(e))
            else:
                st.warning("⚠️ 請至少輸入中文名稱。")

    # 3. 現有項目清單管理（原封不動完整保留你寫的資料庫動態列表與刪除功能）
    st.markdown("---")
    st.markdown("#### 📋 目前啟用的薪資項目清單")
    fields = get_dynamic_fields(engine)
    if fields:
        for f in fields:
            # 支援手機端自適應的行彈性佈局
            col_x1, col_x2, col_x3, col_x4 = st.columns([3, 3, 2, 1])
            col_x1.text(f"[{'應領' if f['category']=='income' else '應扣'}] {f['field_name_zh']}")
            col_x2.text(f"越文: {f['field_name_vn']}")
            col_x3.text(f"預設: {f['default_amount']:,.0f} VND")
            if col_x4.button("🗑️ 刪除", key=f"del_item_{f['id']}"):
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("DELETE FROM public.erp_dynamic_fields WHERE id = :id"), {"id": f['id']})
                        st.success(f"已刪除 {f['field_name_zh']}")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 刪除失敗: " + str(e))
