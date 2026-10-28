import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 多語系字典 (i18n)
# ----------------------------------------------------
POLICY_I18N = {
    "繁體中文": {
        "title": "📰 越南經營政策與法規每日動態速遞 (真實公文與新聞詳情)",
        "caption": "即時掌握越南中央與地方政府最新發布之法規，點擊「詳細原文」可直接開啟該篇新聞與公文內容。",
        "btn_refresh": "🔄 重新載入最新法規清單",
        "refresh_success": "✅ 已成功載入最新法規政策！",
        "search_label": "🔍 搜尋法規關鍵字：",
        "search_placeholder": "輸入關鍵字（例如：稅務、勞動、環保）...",
        "filter_label": "依政策類別篩選",
        "all_categories": "全部類別",
        "expander_title": "➕ 新增真實法規與詳細原文連結 (管理部/IT專用)",
        "col_title": "法規新聞標題",
        "col_cat": "政策類別",
        "col_src": "真實新聞與公文詳細網址 (URL)",
        "col_sum": "政策摘要說明",
        "col_adv": "對裕豐電機之經營影響與合規建議",
        "btn_save": "💾 儲存並發布至總經理室",
        "save_success": "🎉 政策快報已成功發布！",
        "ai_title": "🤖 AI 法規合規深度解析顧問",
        "ai_hint": "針對上方列出的法規與詳細內容，向 AI 詢問經營影響：",
        "ai_placeholder": "例如：針對最新稅務與電子發票新規，西寧廠會計應如何合規因應？",
        "ai_btn": "🚀 請 AI 分析合規風險",
        "ai_loading": "⏳ AI 正在結合最新法規與公司架構進行深度分析...",
        "no_key_err": "❌ 找不到有效的 API Key，請先至資訊管理部 API 串接中心設定！"
    },
    "Tiếng Việt": {
        "title": "📰 Cập nhật Hàng ngày về Chính sách & Pháp luật Kinh doanh tại Việt Nam",
        "caption": "Nắm bắt chính sách mới nhất kèm liên kết chi tiết văn bản gốc.",
        "btn_refresh": "🔄 Tải lại",
        "refresh_success": "✅ Đã tải lại thành công!",
        "search_label
