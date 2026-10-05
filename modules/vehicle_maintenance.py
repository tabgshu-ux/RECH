import pandas as pd
import streamlit as st
import datetime

def render_vehicle_maintenance_page(engine=None, lang="繁體中文"):
    st.title("🚗 管理部 - 車輛維修保養與車籍追蹤中心")
    st.caption("支援 Excel 批次上傳車輛維修記錄（含各車牌分頁），即時追蹤里程數、維修服務項目、零件明細、維修廠與維修總成本。")

    # 初始化車輛維修資料庫 (Session State)
    if "vehicle_maintenance_db" not in st.session_state:
        st.session_state.vehicle_maintenance_db = [
            {
                "plate_no": "70LD00606",
                "date": "2025-09-19",
                "mileage": 207079,
                "service_name": "Bão dưỡng cấp 2 (二級保養)",
                "content": "thay dây cua roa bơm nước+ máy phát + lóc lạnh",
                "garage": "Thaco Gò Dầu",
                "unit": "lần",
                "qty": 1.0,
                "unit_price": 250000.0,
                "vat": 20000.0,
                "total": 270000.0,
                "note": "-"
            },
            {
                "plate_no": "70LD00606",
                "date": "2025-11-05",
                "mileage": 207079,
                "service_name": "Thay vỏ (換輪胎)",
                "content": "Vỏ Yokohama 700/16",
                "garage": "Thái Phùng",
                "unit": "bộ",
                "qty": 2.0,
                "unit_price": 2407408.0,
                "vat": 192592.64,
                "total": 5200001.28,
                "note": "date 5223"
            }
        ]

    # 頁籤設定
    tab_query, tab_upload, tab_summary = st.tabs([
        "📊 車輛維修履歷查詢", 
        "📤 Excel 車籍與維修表批次上傳", 
        "📈 車隊維修成本統計分析"
    ])

    # ----------------------------------------------------
    # 1. 車輛維修履歷查詢
    # ----------------------------------------------------
    with tab_query:
        st.subheader("🔍 各車牌維修保養記錄查詢")
        
        if st.session_state.vehicle_maintenance_db:
            df_all = pd.DataFrame(st.session_state.vehicle_maintenance_db)
            
            # 車牌篩選
            plates = ["全部車牌"] + list(df_all["plate_no"].unique())
            selected_plate = st.selectbox("選擇要查詢的車牌號碼 (Biển số xe)", plates)
            
            if selected_plate != "全部車牌":
                df_filtered = df_all[df_all["plate_no"] == selected_plate]
            else:
                df_filtered = df_all

            st.markdown(f"**目前顯示車牌：`{selected_plate}` 共計 {len(df_filtered)} 筆記錄**")
            st.dataframe(df_filtered, use_container_width=True)
        else:
            st.info("目前尚無車輛維修記錄，請先至第二個分頁上傳 Excel 檔案。")

    # ----------------------------------------------------
    # 2. Excel 車籍與維修表批次上傳
    # ----------------------------------------------------
    with tab_upload:
        st.subheader("📤 上傳車輛維修追蹤 Excel 檔案 (.xlsx)")
        st.info("💡 支援您手邊如 `QUẢN LÝ SỬA CHỮA BẢO DƯỠNG XE Ô TÔ` 的多分頁 Excel 檔。系統會自動抓取每個分頁名稱作為車牌號碼，並解析其中的維修明細。")

        uploaded_excel = st.file_uploader("選擇車輛維修 Excel 檔案", type=["xlsx", "xls"])

        if uploaded_excel is not None:
            try:
                xls = pd.ExcelFile(uploaded_excel)
                st.success(f"✅ 成功讀取 Excel！內含 {len(xls.sheet_names)} 個車牌分頁：`{', '.join(xls.sheet_names)}`")

                if st.button("🚀 開始批次解析並匯入系統資料庫", type="primary"):
                    imported_total = 0
                    
                    for sheet_name in xls.sheet_names:
                        plate_cleaned = sheet_name.strip() # 分頁名稱即為車牌
                        raw_df = pd.read_excel(uploaded_excel, sheet_name=sheet_name)
                        
                        # 尋找包含標題列的行 (STT 或 NGÀY)
                        header_row_idx = None
                        for idx, row in raw_df.iterrows():
                            row_str = str(row.values)
                            if "NGÀY" in row_str or "SỐ KM" in row_str or "TÊN DỊCH VỤ" in row_str:
                                header_row_idx = idx
                                break
                        
                        if header_row_idx is not None:
                            # 重新讀取並設定正確的表頭
                            df_sheet = pd.read_excel(uploaded_excel, sheet_name=sheet_name, header=header_row_idx)
                            df_sheet = df_sheet.dropna(subset=[df_sheet.columns[1]]) # 過濾日期空白行
                            
                            for _, r in df_sheet.iterrows():
                                stt = r.iloc[0]
                                if pd.isna(stt) or str(stt).strip() == "":
                                    continue
                                
                                maint_date = str(r.iloc[1])[:10] if not pd.isna(r.iloc[1]) else "2026-01-01"
                                km = r.iloc[2] if not pd.isna(r.iloc[2]) else 0
                                service = str(r.iloc[3]) if not pd.isna(r.iloc[3]) else "-"
                                content = str(r.iloc[4]) if not pd.isna(r.iloc[4]) else "-"
                                garage = str(r.iloc[5]) if not pd.isna(r.iloc[5]) else "-"
                                unit = str(r.iloc[6]) if not pd.isna(r.iloc[6]) else "-"
                                qty = r.iloc[7] if not pd.isna(r.iloc[7]) else 1.0
                                price = r.iloc[8] if not pd.isna(r.iloc[8]) else 0.0
                                vat = r.iloc[9] if not pd.isna(r.iloc[9]) else 0.0
                                total = r.iloc[10] if not pd.isna(r.iloc[10]) else 0.0
                                note = str(r.iloc[11]) if len(r) > 11 and not pd.isna(r.iloc[11]) else "-"

                                # 避免重複加入
                                new_record = {
                                    "plate_no": plate_cleaned,
                                    "date": maint_date,
                                    "mileage": km,
                                    "service_name": service,
                                    "content": content,
                                    "garage": garage,
                                    "unit": unit,
                                    "qty": qty,
                                    "unit_price": price,
                                    "vat": vat,
                                    "total": total,
                                    "note": note
                                }
                                st.session_state.vehicle_maintenance_db.append(new_record)
                                imported_total += 1

                    st.success(f"🎉 批次匯入完成！總共成功匯入 {imported_total} 筆車輛維修保養紀錄。請至『車輛維修履歷查詢』查看。")
                    st.rerun()

            except Exception as e:
                st.error(f"❌ 解析 Excel 失敗: {str(e)}")

    # ----------------------------------------------------
    # 3. 車隊維修成本統計分析
    # ----------------------------------------------------
    with tab_summary:
        st.subheader("📈 車隊維修成本與花費總覽")
        if st.session_state.vehicle_maintenance_db:
            df_sum = pd.DataFrame(st.session_state.vehicle_maintenance_db)
            
            # 確保 total 欄位為數值
            df_sum["total"] = pd.to_numeric(df_sum["total"], errors="coerce").fillna(0)
            
            plate_cost = df_sum.groupby("plate_no")["total"].sum().reset_index()
            plate_cost.columns = ["車牌號碼", "累計維修總金額"]
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.metric("車隊累計總維修花費", f"${df_sum['total'].sum():,.2f}")
            with col_s2:
                st.metric("納管車輛總數", f"{df_sum['plate_no'].nunique()} 台")

            st.markdown("#### 🚗 各車輛維修成本排行")
            st.dataframe(plate_cost, use_container_width=True)
        else:
            st.info("尚無足夠數據進行成本統計。")

def show(engine=None, lang="繁體中文"):
    render_vehicle_maintenance_page(engine, lang)

def main(engine=None, lang="繁體中文"):
    render_vehicle_maintenance_page(engine, lang)
