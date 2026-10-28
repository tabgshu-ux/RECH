import streamlit as st
import pandas as pd

def render_ai_config_hub_page(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🤖 企業 AI 智慧大模型串接設定中心 (AI Model Integration Hub)")
    st.caption("供 IT 系統管理員動態配置與切換企業 AI 顧問服務供應商（Google Gemini、OpenAI、Anthropic Claude），實現無硬編碼的全域彈性管理。")
    
    # 初始化 session 狀態中的 AI 配置
    if "ai_config" not in st.session_state:
        st.session_state["ai_config"] = {
            "provider": "Google Gemini",
            "model": "gemini-3.0-flash",
            "api_key": ""
        }
    
    with st.form("ai_config_form"):
        st.markdown("#### ⚙️ AI 服務供應商與模型動態配置")
        
        current_provider = st.session_state["ai_config"]["provider"]
        provider_options = ["Google Gemini", "OpenAI (GPT-4o)", "Anthropic (Claude 3.5)"]
        default_provider_index = provider_options.index(current_provider) if current_provider in provider_options else 0
        
        provider = st.selectbox(
            "選擇 AI 服務供應商 (AI Provider)",
            provider_options,
            index=default_provider_index
        )
        
        # 依據選擇的供應商動態顯示對應的模型選項
        if provider == "Google Gemini":
            models = ["gemini-3.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
        elif provider == "OpenAI (GPT-4o)":
            models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
        else:
            models = ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"]
            
        model_name = st.selectbox("選擇模型版本 (Model Name)", models)
        
        api_key = st.text_input(
            f"輸入 {provider} API Key", 
            value=st.session_state["ai_config"]["api_key"], 
            type="password",
            placeholder="請輸入您的 API 金鑰..."
        )
        
        submitted = st.form_submit_button("💾 儲存並套用 AI 串接設定", type="primary")
        if submitted:
            st.session_state["ai_config"] = {
                "provider": provider,
                "model": model_name,
                "api_key": api_key
            }
            st.success(f"✅ 設定已成功更新！系統已將預設 AI 動態切換為【{provider} - {model_name}】")

    st.markdown("---")
    st.info("💡 **架構備註**：此設定會即時生效於全系統所有 AI 顧問模組（如總經理室智慧採購顧問、財報自動審閱等），無需重新部署雲端程式碼。")
