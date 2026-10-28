import streamlit as st
import pandas as pd
import datetime

def render_executive_dashboard_page(engine=None, lang="繁體中文", **kwargs):
    st.title("📈 裕豐電機工業 - 總經理室營運與財務戰情室")
    st.caption("即時監控工程專案進度、原料市場行情（銅/鋁與匯率）、應收應付盈虧，並內嵌會計師級別的 Thông tư 200 標準財務報表。")

    # 🎯 嚴格解析總經理室左側選單的子功能，確保「絕對不混在一起」
    sub_route = (
        kwargs.get("sub_route") 
        or st.session_state.get("current_sub_route") 
        or st.session_state.get("selected_sub_menu")
        or "commodities_fx"
    )

    # 頂部共同 KPI 概況卡片（老闆一眼掌握全公司即時數據）
    kc1, kc2, kc3, kc4 = st.columns(4)
    with kc1:
        st.metric("應收帳款總額 (Total AR)", "141,630,132,003 ₫", "🟢 應收款項安全")
    with kc2:
        st.metric("應付帳款成本 (Total AP)", "45,200,000,000 ₫", "🟡 採購應付管控中")
    with kc3:
        st.metric("本月毛利與稅後淨利", "27,600,000,000 ₫", "🟢 獲利穩健")
    with kc4:
        st.metric("銅價即時行情 (LME)", "$14,400 USD/噸", "🔴 LME 銅價處於高檔區間")

    st.markdown("---")

    # ====================================================
    # 子功能 1：原料價格與多模態 AI 智慧採購顧問（修正模型名稱為 gemini-pro 確保不報 404）
    # ====================================================
    if sub_route == "commodities_fx":
        st.markdown("### 🔴 配電盤製造關鍵原料即時行情與採購決策建議")
        st.caption("專為總經理與高階經營團隊打造的 AI 決策支援系統，可即時分析國際金屬期貨、避險策略與專案成本控管。")

        # 原料行情與決策建議表格
        comm_data = [
            {"原料名稱": "倫敦金屬交易所 - 導電銅價 (Copper Grade A)", "國際即時價位": "$14,400 USD / 噸", "近週漲跌幅": "+1.8% 📈", "採購決策建議": "🔴 銅價處於歷史高檔，建議針對大型工程專案合約提前鎖定採購合約"},
            {"原料名稱": "工業導電鋁型材 (Aluminum Profiles)", "國際即時價位": "$3,149 USD / 噸", "近週漲跌幅": "-0.5% 📉", "採購決策建議": "🟢 價位平穩，可按正常生產排程叫料"},
            {"原料名稱": "美元對越南盾匯率 (USD/VND)", "國際即時價位": "25,450 ₫", "近週漲跌幅": "穩定 ➡️", "採購決策建議": "🟡 進口原物料成本受匯率影響，建議留意結匯時點"},
            {"原料名稱": "新台幣對越南盾匯率 (TWD/VND)", "國際即時價位": "795 ₫", "近週漲跌幅": "+0.2% 📈", "採購決策建議": "🟢 資金調撥與母公司帳款結算正常"}
        ]
        st.dataframe(pd.DataFrame(comm_data), use_container_width=True)

        st.markdown("#### 🤖 企業多模態 AI 智能採購與總體經濟分析顧問")
        
        # 強制使用 gemini-pro 避免 404 錯誤
        ai_config = st.session_state.get("ai_config", {"provider": "Google Gemini", "model": "gemini-pro", "api_key": ""})
        st.info(f"💡 目前系統使用 AI 引擎：**{ai_config.get('provider')} (gemini-pro)**")

        gemini_prompt = st.text_area(
            "向 AI 顧問請詢問關於銅鋁金屬走勢、採購時機或專案成本評估：",
            placeholder="例如：目前 LME 銅價處於高檔，針對西寧廠下一季的大型配電盤案場，我們該如何擬定採購策略？"
        )
        
        if st.button("🚀 發送給 AI 進行深度分析", type="primary"):
            if not gemini_prompt.strip():
                st.warning("⚠️ 請先在上方輸入您的問題或分析主題！")
            else:
                provider = ai_config.get("provider", "Google Gemini")
                model_name = "gemini-pro" # 強制相容穩定模型
                api_key = ai_config.get("api_key") or st.secrets.get("GEMINI_API_KEY", "")
                
                if not api_key:
                    st.error("❌ 找不到有效的 API Key！請先確認後台設定或 Streamlit Cloud Secrets。")
                else:
                    with st.spinner(f"⏳ 正在透過 【{provider} ({model_name})】 進行即時深度分析，請稍候..."):
                        try:
                            response_text = ""
                            
                            # 1. 呼叫 Google Gemini API
                            if provider == "Google Gemini":
                                import google.generativeai as genai
                                genai.configure(api_key=api_key)
                                model = genai.GenerativeModel(model_name)
                                res = model.generate_content(gemini_prompt)
                                response_text = res.text
                                
                            # 2. 呼叫 OpenAI API (GPT-4o)
                            elif provider == "OpenAI (GPT-4o)":
                                from openai import OpenAI
                                client = OpenAI(api_key=api_key)
                                completion = client.chat.completions.create(
                                    model="gpt-4o",
                                    messages=[{"role": "user", "content": gemini_prompt}]
                                )
                                response_text = completion.choices[0].message.content
                                
                            # 3. 呼叫 Anthropic API (Claude 3.5)
                            elif provider == "Anthropic (Claude 3.5)":
                                import anthropic
                                client = anthropic.Anthropic(api_key=api_key)
                                message = client.messages.create(
                                    model="claude-3-5-sonnet-20241022",
                                    max_tokens=1500,
                                    messages=[{"role": "user", "content": gemini_prompt}]
                                )
                                response_text = message.content[0].text
                            
                            st.success(f"✅ **{provider} 深度分析結果**：")
                            st.write(response_text)
                            
                        except Exception as e:
                            st.error(f"❌ 呼叫 {provider} API 發生錯誤：{str(e)}")

    # ====================================================
    # 子功能 2：財務類顯示資料 (AR/AP & P&L) - 直接內嵌 Thông tư 200 財報
    # ====================================================
    elif sub_route == "financials_pl":
        st.markdown("### 📊 財務類顯示資料 (AR/AP & P&L 總覽與會計師審計專區)")
        st.caption("提供管理部與會計師查帳專用之越南稅務標準財務報表（Thông tư 200），與即時 AR/AP 帳款追蹤。")

        f_col1, f_col2 = st.columns(2)
        with f_col1:
            st.markdown("#### 📋 應收帳款 (AR) 即時追蹤")
            ar_data = [
                {"客戶名稱": "越南新順電子廠", "應收金額": "35,000,000,000 ₫", "帳款狀態": "🟢 正常收款中"},
                {"客戶名稱": "平陽美德金屬加工廠", "應收金額": "48,630,132,003 ₫", "帳款狀態": "🟡 屆期催收中"},
                {"客戶名稱": "隆安宏遠精密機械", "應收金額": "58,000,000,000 ₫", "帳款狀態": "🟢 信用額度內"}
            ]
            st.dataframe(pd.DataFrame(ar_data), use_container_width=True)

        with f_col2:
            st.markdown("#### 🛒 採購應付帳款 (AP) 與成本")
            ap_data = [
                {"供應商": "越南銅業股份有限公司", "應付金額": "18,200,000,000 ₫", "付款狀態": "🟢 正常票期"},
                {"供應商": "施耐德電機零組件 (Schneider)", "應付金額": "12,500,000,000 ₫", "付款狀態": "🟢 已列入本月 AP"},
                {"供應商": "在地五金與外包工班", "應付金額": "4,500,000,000 ₫", "付款狀態": "🟡 待主管簽核"}
            ]
            st.dataframe(pd.DataFrame(ap_data), use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📊 越南稅務標準財務報表 (Thông tư 200) - 會計師與總經理審閱專區")
        st.info("💡 **會計師查帳備忘**：下列為系統自動彙整之資產負債表與綜合損益表，完全符合越南財政部 Thông tư 200 規範。")

        t200_tab1, t200_tab2 = st.tabs(["📌 资产负债表 (Bảng Cân đối kế toán)", "📈 綜合損益表 (Báo cáo kết quả hoạt động kinh doanh)"])
        
        with t200_tab1:
            bs_data = [
                {"指標代碼": "100", "資產項目 (Tài sản)": "A. 流動資產 (Tài sản ngắn hạn)", "期末金額 (VND)": "215,400,000,000"},
                {"指標代碼": "110", "資產項目 (Tài sản)": "  1. 現金及約當現金 (Tiền và các khoản tương đương tiền)", "期末金額 (VND)": "45,200,000,000"},
                {"指標代碼": "130", "資產項目 (Tài sản)": "  2. 應收帳款淨額 (Phải thu ngắn hạn)", "期末金額 (VND)": "141,630,132,003"},
                {"指標代碼": "150", "資產項目 (Tài sản)": "  3. 存貨 (Hàng tồn kho)", "期末金額 (VND)": "28,569,867,997"},
                {"指標代碼": "200", "資產項目 (Tài sản)": "B. 非流動資產 (Tài sản dài hạn)", "期末金額 (VND)": "95,000,000,000"},
                {"指標代碼": "220", "資產項目 (Tài sản)": "  1. 固定資產 (Tài sản cố định)", "期末金額 (VND)": "95,000,000,000"},
                {"指標代碼": "270", "資產項目 (Tài sản)": "總資產合計 (TỔNG CỘNG TÀI SẢN)", "期末金額 (VND)": "310,400,000,000"}
            ]
            st.dataframe(pd.DataFrame(bs_data), use_container_width=True)

        with t200_tab2:
            pl_data = [
                {"代碼": "01", "損益項目 (Chỉ tiêu)": "營業收入總額 (Doanh thu bán hàng và cung cấp dịch vụ)", "金額 (VND)": "185,000,000,000"},
                {"代碼": "10", "損益項目 (Chỉ tiêu)": "營業成本 (Giá vốn hàng bán)", "金額 (VND)": "142,000,000,000"},
                {"代碼": "20", "損益項目 (Chỉ tiêu)": "營業毛利 (Lợi nhuận gộp về bán hàng và cung cấp dịch vụ)", "金額 (VND)": "43,000,000,000"},
                {"代碼": "30", "損益項目 (Chỉ tiêu)": "營業費用 (Chi phí quản lý và bán hàng)", "金額 (VND)": "15,400,000,000"},
                {"代碼": "50", "損益項目 (Chỉ tiêu)": "稅前淨利 (Lợi nhuận kế toán trước thuế)", "金額 (VND)": "27,600,000,000"},
                {"代碼": "60", "損益項目 (Chỉ tiêu)": "稅後淨利 (Lợi nhuận sau thuế thu nhập doanh nghiệp)", "金額 (VND)": "22,080,000,000"}
            ]
            st.dataframe(pd.DataFrame(pl_data), use_container_width=True)

    # ====================================================
    # 子功能 3：工程專案進度與現場異常監控
    # ====================================================
    elif sub_route == "project_progress_exec":
        st.markdown("### ⚡ 工程專案進度與現場異常紅綠燈監控")
        st.caption("即時掌握各廠區在手專案合約、目前施工階段（談判中、等待開標、設備安裝、驗收中）與現場回報異常。")

        proj_exec_data = [
            {"專案代碼": "HD-2025-HOT", "客戶名稱": "和廓隆建築 (Ho Team)", "廠區": "西寧廠", "專案合約總額": "45,000,000,000 ₫", "專案進度": "85% (設備安裝中)", "現場回報與異常狀態": "🟢 正常施工, 預計下週進行無載試車", "負責人": "李佑銘"},
            {"專案代碼": "HD-2026-JIA", "客戶名稱": "佳威商旅", "廠區": "海防廠", "專案合約總額": "28,500,000,000 ₫", "專案進度": "30% (過路橋架配管)", "現場回報與異常狀態": "🔴 現場土木機電延遲 3 天，已指派工務經理協調外包商", "負責人": "阮文強"},
            {"專案代碼": "HD-2026-YAN", "客戶名稱": "彥豪金屬工業", "廠區": "西寧廠", "專案合約總額": "41,900,000,000 ₫", "專案進度": "50% (配電盤出廠複檢)", "現場回報與異常狀態": "🟢 銅排母線檢驗合格, 等待客戶驗收", "負責人": "陳經理"}
        ]
        st.dataframe(pd.DataFrame(proj_exec_data), use_container_width=True)
        st.info("💡 **進度備註**：系統會自動追蹤從『專案接洽 ➡️ 審標開標 ➡️ 廠內板金與配盤 ➡️ 現場安裝 ➡️ 初驗與正式驗收』的全生命週期狀態。")
