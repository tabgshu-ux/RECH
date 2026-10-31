import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def init_factory_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            # 1. 廠區基本資料表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.factories_master (
                    id SERIAL PRIMARY KEY,
                    factory_code VARCHAR(50) UNIQUE NOT NULL,
                    factory_name VARCHAR(150) NOT NULL,
                    manager_title VARCHAR(150),
                    phone VARCHAR(50),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            # 2. 廠區安全與消防巡檢紀錄表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.plant_inspect_logs (
                    id SERIAL PRIMARY KEY,
                    inspect_date DATE NOT NULL,
                    factory_name VARCHAR(150) NOT NULL,
                    inspect_item VARCHAR(250) NOT NULL,
                    inspector VARCHAR(100),
                    result_status VARCHAR(50),
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass

def render_plant_management_page(engine=None, lang="繁體中文", **kwargs):
    PLANT_I18N = {
        "繁體中文": {
            "title": "🏭 廠區安全、消防巡檢與廠籍管理中心",
            "caption": "裕豐電機（越南西寧廠）專用：廠區設施名冊維護、連假前斷電巡檢與消防安全稽核。",
            "tab_factory": "🏢 廠區基本資料與負責人",
            "tab_inspect": "🔍 廠區安全與斷電巡檢",
            "search_label": "🔍 搜尋廠區名稱或編號",
            "search_ph": "輸入廠區名稱或編號搜尋...",
            "table_header": "📋 廠區與負責人名冊總覽",
            "sub_tabs": ["➕ 新增廠區", "✏️ 修改廠區資料", "🗑️ 刪除廠區"],
            "add_header": "### ➕ 新增廠區與負責人",
            "lbl_id": "廠區編號",
            "lbl_name": "廠區名稱 (Factory Name)",
            "lbl_mgr": "選擇負責人與職稱",
            "lbl_tel": "聯絡電話 (Phone)",
            "btn_add": "🚀 確認新增廠區",
            "success_add": "✅ 廠區 {name} 新增成功並已寫入資料庫！",
            "warn_name": "⚠️ 請填寫廠區名稱！",
            "edit_header": "### ✏️ 修改廠區資料與負責人",
            "select_edit": "選擇要修改的廠區",
            "btn_save_edit": "💾 儲存修改",
            "success_edit": "✅ 廠區 {id} 修改成功！",
            "no_fac_edit": "目前無廠區資料可供修改。",
            "del_header": "### 🗑️ 刪除廠區確認",
            "select_del": "選擇要刪除的廠區",
            "del_warn": "確定要刪除廠區 **{id} - {name}** 嗎？此動作無法復原。",
            "btn_del": "🔥 確認刪除",
            "success_del": "✅ 廠區 {id} 已自資料庫永久刪除！",
            "no_fac_del": "目前無廠區資料可供刪除。",
            "inspect_form_header": "📝 新增廠區安全巡檢與消防盤點紀錄",
            "site_lbl": "巡檢廠區",
            "inspector_lbl": "巡檢人員 / 主管",
            "date_lbl": "巡檢日期",
            "item_lbl": "查核項目",
            "status_lbl": "查核結果",
            "note_lbl": "異常狀況說明與處置",
            "btn_submit": "💾 提交巡檢紀錄並歸檔",
            "success_inspect": "🎉 廠區巡檢紀錄已成功建立！",
            "inspect_list": "📋 近期廠區巡檢與安全稽核紀錄"
        },
        "Tiếng Việt": {
            "title": "🏭 Quản lý Nhà máy, Kiểm tra PCCC & An toàn",
            "caption": "Nhà máy Tây Ninh Reetech.",
            "tab_factory": "🏢 Hồ sơ Nhà máy",
            "tab_inspect": "🔍 Kiểm tra An toàn & PCCC",
            "search_label": "🔍 Tìm kiếm nhà máy",
            "search_ph": "Nhập tên nhà máy...",
            "table_header": "📋 Danh sách Nhà máy",
            "sub_tabs": ["➕ Thêm", "✏️ Sửa", "🗑️ Xóa"],
            "add_header": "### ➕ Thêm Nhà máy",
            "lbl_id": "Mã nhà máy",
            "lbl_name": "Tên nhà máy",
            "lbl_mgr": "Người quản lý",
            "lbl_tel": "Số điện thoại",
            "btn_add": "🚀 Xác nhận",
            "success_add": "✅ Thêm thành công!",
            "warn_name": "⚠️ Vui lòng điền tên!",
            "edit_header": "### ✏️ Sửa",
            "select_edit": "Chọn nhà máy",
            "btn_save_edit": "💾 Lưu",
            "success_edit": "✅ Cập nhật thành công!",
            "no_fac_edit": "Không có dữ liệu.",
            "del_header": "### 🗑️ Xóa",
            "select_del": "Chọn xóa",
            "del_warn": "Xác nhận xóa?",
            "btn_del": "🔥 Xóa",
            "success_del": "✅ Đã xóa!",
            "no_fac_del": "Không có dữ liệu.",
            "inspect_form_header": "📝 Thêm biên bản kiểm tra",
            "site_lbl": "Khu vực",
            "inspector_lbl": "Người kiểm tra",
            "date_lbl": "Ngày",
            "item_lbl": "Hạng mục",
            "status_lbl": "Kết quả",
            "note_lbl": "Ghi chú",
            "btn_submit": "💾 Lưu",
            "success_inspect": "🎉 Lưu thành công!",
            "inspect_list": "📋 Lịch sử kiểm tra"
        },
        "English": {
            "title": "🏭 Plant Safety, Fire Inspection & Facility Management",
            "caption": "Reetech Industrial (Tay Ninh Plant): Plant registry, power-off inspection, and fire safety audits.",
            "tab_factory": "🏢 Plant Directory & Registry",
            "tab_inspect": "🔍 Plant Safety & Inspection Records",
            "search_label": "🔍 Search Factory",
            "search_ph": "Enter factory name...",
            "table_header": "📋 Factory Directory",
            "sub_tabs": ["➕ Add Factory", "✏️ Edit Factory", "🗑️ Delete Factory"],
            "add_header": "### ➕ Add Factory",
            "lbl_id": "Factory Code",
            "lbl_name": "Factory Name",
            "lbl_mgr": "Manager & Title",
            "lbl_tel": "Contact Phone",
            "btn_add": "🚀 Confirm Add",
            "success_add": "✅ Added successfully!",
            "warn_name": "⚠️ Please enter factory name!",
            "edit_header": "### ✏️ Edit Factory",
            "select_edit": "Select Factory",
            "btn_save_edit": "💾 Save",
            "success_edit": "✅ Updated successfully!",
            "no_fac_edit": "No records.",
            "del_header": "### 🗑️ Delete Factory",
            "select_del": "Select Factory",
            "del_warn": "Are you sure?",
            "btn_del": "🔥 Delete",
            "success_del": "✅ Permanently deleted!",
            "no_fac_del": "No records.",
            "inspect_form_header": "📝 New Safety & Fire Inspection Record",
            "site_lbl": "Plant Location",
            "inspector_lbl": "Inspector / Supervisor",
            "date_lbl": "Inspection Date",
            "item_lbl": "Inspection Item",
            "status_lbl": "Result",
            "note_lbl": "Remarks & Actions",
            "btn_submit": "💾 Submit & Archive",
            "success_inspect": "🎉 Inspection record saved successfully!",
            "inspect_list": "📋 Recent Inspection Records"
        }
    }

    active_lang = lang if lang in PLANT_I18N else "繁體中文"
    L = PLANT_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])
    st.markdown("---")
    
    init_factory_db(engine)

    # 🏢 透過主分頁將「廠區基本資料」與「安全消防巡檢」完美隔離，告別滾動疲勞
    tab_factory, tab_inspect = st.tabs([L["tab_factory"], L["tab_inspect"]])

    # ----------------------------------------------------
    # Tab 1: 廠區基本資料與負責人管理
    # ----------------------------------------------------
    with tab_factory:
        # 🔗 從資料庫讀取真實員工清單作為負責人選項
        employee_options = []
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT emp_name, position FROM public.employee_profiles WHERE (status IS NULL OR status = '在職');"))
                    for r in res.fetchall():
                        if r[0]:
                            employee_options.append(f"{r[0]} ({r[1] or '員工'})")
            except Exception:
                pass

        if not employee_options:
            employee_options = ["李佑銘 (董事長)", "Nguyễn Văn Quý (財務主管)"]

        # 📥 從資料庫讀取真實廠區資料
        factory_list = []
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT factory_code, factory_name, manager_title, phone FROM public.factories_master ORDER BY id ASC;"))
                    for r in res.fetchall():
                        factory_list.append({
                            "廠區編號": r[0],
                            "廠區名稱": r[1],
                            "負責人與職位": r[2] or "-",
                            "聯絡電話": r[3] or "-"
                        })
            except Exception as e:
                st.error(f"讀取資料庫廠區失敗: {e}")

        search_q = st.text_input(L["search_label"], placeholder=L["search_ph"], key="fac_search_input_unique")
        filtered_fac = [
            f for f in factory_list 
            if search_q.lower() in f["廠區名稱"].lower() or search_q.lower() in f["廠區編號"].lower() or search_q.lower() in f["負責人與職位"].lower()
        ] if search_q else factory_list
        
        st.markdown(L["table_header"])
        if factory_list:
            st.dataframe(pd.DataFrame(filtered_fac), use_container_width=True, hide_index=True)
        else:
            st.info("目前資料庫中尚無廠區資料，請透過下方「新增廠區」進行建立。")
        
        sub_tab_add, sub_tab_edit, sub_tab_del = st.tabs(L["sub_tabs"])
        
        with sub_tab_add:
            with st.form("add_factory_form_unique"):
                st.markdown(L["add_header"])
                default_new_id = f"FAC-{len(factory_list)+1:02d}" if factory_list else "FAC-01"
                fn_id = st.text_input(L["lbl_id"], value=default_new_id, key="add_fn_id_u")
                fn_name = st.text_input(L["lbl_name"], key="add_fn_name_u")
                fn_mgr = st.selectbox(L["lbl_mgr"], employee_options, key="add_fn_mgr_select_u")
                fn_tel = st.text_input(L["lbl_tel"], key="add_fn_tel_u")
                
                if st.form_submit_button(L["btn_add"], type="primary", use_container_width=True):
                    if fn_name and engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.factories_master (factory_code, factory_name, manager_title, phone)
                                    VALUES (:code, :name, :mgr, :phone)
                                    ON CONFLICT (factory_code) DO UPDATE 
                                    SET factory_name = EXCLUDED.factory_name, manager_title = EXCLUDED.manager_title, phone = EXCLUDED.phone;
                                """), {
                                    "code": fn_id.strip(),
                                    "name": fn_name.strip(),
                                    "mgr": fn_mgr,
                                    "phone": fn_tel.strip() if fn_tel else "-"
                                })
                            st.success(L["success_add"].format(name=fn_name))
                            st.rerun()
                        except Exception as e:
                            st.error(f"寫入資料庫失敗: {e}")
                    else:
                        st.warning(L["warn_name"])

        with sub_tab_edit:
            if factory_list:
                fac_options = {f"{f['廠區編號']} - {f['廠區名稱']}": f for f in factory_list}
                selected_fac_key = st.selectbox(L["select_edit"], list(fac_options.keys()), key="edit_fac_select_u")
                target_fac = fac_options[selected_fac_key]
                
                with st.form("edit_factory_form_unique"):
                    st.markdown(L["edit_header"])
                    e_name = st.text_input(L["lbl_name"], value=target_fac["廠區名稱"], key="edit_e_name_u")
                    
                    current_mgr = target_fac["負責人與職位"]
                    mgr_index = employee_options.index(current_mgr) if current_mgr in employee_options else 0
                    e_mgr = st.selectbox(L["lbl_mgr"], employee_options, index=mgr_index, key="edit_e_mgr_select_u")
                    
                    e_tel = st.text_input(L["lbl_tel"], value=target_fac["聯絡電話"], key="edit_e_tel_u")
                    
                    if st.form_submit_button(L["btn_save_edit"], type="primary", use_container_width=True) and engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    UPDATE public.factories_master 
                                    SET factory_name = :name, manager_title = :mgr, phone = :phone
                                    WHERE factory_code = :code;
                                """), {
                                    "name": e_name.strip(),
                                    "mgr": e_mgr,
                                    "phone": e_tel.strip() if e_tel else "-",
                                    "code": target_fac["廠區編號"]
                                })
                            st.success(L["success_edit"].format(id=target_fac['廠區編號']))
                            st.rerun()
                        except Exception as e:
                            st.error(f"更新資料庫失敗: {e}")
            else:
                st.info(L["no_fac_edit"])

        with sub_tab_del:
            if factory_list:
                del_options = {f"{f['廠區編號']} - {f['廠區名稱']}": f for f in factory_list}
                selected_del_key = st.selectbox(L["select_del"], list(del_options.keys()), key="del_fac_select_u")
                target_del = del_options[selected_del_key]
                
                with st.form("delete_factory_form_unique"):
                    st.markdown(L["del_header"])
                    st.warning(L["del_warn"].format(id=target_del['廠區編號'], name=target_del['廠區名稱']))
                    if st.form_submit_button(L["btn_del"], type="primary", use_container_width=True) and engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    DELETE FROM public.factories_master 
                                    WHERE factory_code = :code;
                                """), {"code": target_del["廠區編號"]})
                            st.success(L["success_del"].format(id=target_del['廠區編號']))
                            st.rerun()
                        except Exception as e:
                            st.error(f"刪除資料庫失敗: {e}")
            else:
                st.info(L["no_fac_del"])

    # ----------------------------------------------------
    # Tab 2: 廠區安全與斷電巡檢紀錄
    # ----------------------------------------------------
    with tab_inspect:
        st.markdown(f"### {L['inspect_form_header']}")
        
        # 取得廠區選項名稱供巡檢表單使用
        fac_names_list = [f["廠區名稱"] for f in factory_list] if factory_list else ["越南西寧廠 (Tay Ninh Main Plant)"]

        with st.form("plant_inspect_form_integrated"):
            c1, c2 = st.columns(2)
            with c1:
                p_site = st.selectbox(L["site_lbl"], fac_names_list)
                p_item = st.selectbox(L["item_lbl"], [
                    "連假前總配電盤與斷電巡檢 (Power-off Inspection)",
                    "消防設備與滅火器盤點 (Fire Extinguishers)",
                    "廠區照明與逃生指示燈檢查 (Emergency Lights)",
                    "高低壓配電室安全巡視 (High/Low Voltage Room)"
                ])
            with c2:
                p_date = st.date_input(L["date_lbl"], value=datetime.date.today())
                p_inspector = st.text_input(L["inspector_lbl"], value=st.session_state.get("user_name", "admin"))

            p_status = st.selectbox(L["status_lbl"], ["🟢 正常 (Normal)", "🟡 需注意需改善 (Attention Needed)", "🔴 嚴重異常需立即處理 (Critical)"])
            p_note = st.text_input(L["note_lbl"], placeholder="例: 廠區東側逃生門暢通，不斷電系統運作正常...")

            if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
                # 寫入資料庫或 Session State
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.plant_inspect_logs (inspect_date, factory_name, inspect_item, inspector, result_status, notes)
                                VALUES (:d, :f, :i, :ins, :res, :notes);
                            """), {
                                "d": p_date,
                                "f": p_site,
                                "i": p_item,
                                "ins": p_inspector,
                                "res": p_status,
                                "notes": p_note
                            })
                    except Exception:
                        pass

                # 同步存入 session 以便即時顯示
                if "plant_inspect_db_memory" not in st.session_state:
                    st.session_state.plant_inspect_db_memory = []
                
                st.session_state.plant_inspect_db_memory.insert(0, {
                    "日期": str(p_date),
                    "廠區": p_site,
                    "查核項目": p_item,
                    "巡檢人員": p_inspector,
                    "結果": p_status,
                    "說明": p_note
                })
                st.success(L["success_inspect"])
                st.rerun()

        st.markdown("---")
        st.markdown(f"### {L['inspect_list']}")
        
        # 讀取巡檢紀錄
        inspect_records = st.session_state.get("plant_inspect_db_memory", [
            {
                "日期": "2026-10-09",
                "廠區": "越南西寧廠 (Tay Ninh Main Plant)",
                "查核項目": "連假前總配電盤與斷電巡檢 (Power-off Inspection)",
                "巡檢人員": "許福村 (Tassos)",
                "結果": "🟢 正常 (Normal)",
                "說明": "各車間主斷路器已切斷，消防栓與滅火器盤點完畢。"
            }
        ])

        st.dataframe(pd.DataFrame(inspect_records), use_container_width=True, hide_index=True)

def show(*args, **kwargs):
    render_factory_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_factory_management_page(*args, **kwargs)
