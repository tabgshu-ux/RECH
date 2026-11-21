# ==========================================
# 檔案路徑：modules/management/hr/employee/employee_profile.py
# 職責：L2 行政／人事 - 員工資料整合入口（新增越籍/外派、修改、名冊、離職與證照提醒）
# ==========================================

import importlib
import streamlit as st
from core import ui_theme


def _safe_import(module_path: str):
    try:
        return importlib.import_module(module_path)
    except Exception:
        return None


def _call_module_ui(mod, preferred_names: tuple[str, ...], engine=None, lang="zh", **kwargs) -> bool:
    if mod is None:
        return False
    for name in preferred_names:
        fn = getattr(mod, name, None)
        if callable(fn):
            try:
                fn(engine=engine, lang=lang, **kwargs)
                return True
            except TypeError:
                try:
                    fn(engine, lang)
                    return True
                except TypeError:
                    try:
                        fn(engine)
                        return True
                    except TypeError:
                        fn()
                        return True
    return False


def render_hr_profile_page(engine=None, lang="zh", **kwargs):
    norm_lang = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))

    st.markdown("### 👤 員工資料管理、新增／修改、名冊與離職辦理")
    st.caption("整合越籍與外派／外籍員工建檔、資料修改、在職員工名冊（含證照到期預警）與離職人員管理。")

    mod_list = _safe_import("modules.management.hr.employee.employee_list")
    mod_add_vn = _safe_import("modules.management.hr.employee.add_vietnamese")
    mod_add_expat = _safe_import("modules.management.hr.employee.add_expat")
    mod_edit = _safe_import("modules.management.hr.employee.edit_profile")
    mod_resigned = _safe_import("modules.management.hr.employee.resigned_list")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 在職員工名冊與證照提醒",
        "🇻🇳 新增越籍員工",
        "🌍 新增外派／外籍幹部",
        "✏️ 修改員工資料",
        "🚪 離職人員名單",
    ])

    with tab1:
        if not _call_module_ui(
            mod_list,
            ("render_employee_list", "render", "show", "main"),
            engine=engine,
            lang=norm_lang,
            **kwargs,
        ):
            st.info("找不到或無法載入 `employee_list.py` 的渲染函式。")

    with tab2:
        if not _call_module_ui(
            mod_add_vn,
            ("render_add_vietnamese", "render", "show", "main"),
            engine=engine,
            lang=norm_lang,
            **kwargs,
        ):
            st.info("找不到或無法載入 `add_vietnamese.py` 的渲染函式。")

    with tab3:
        if not _call_module_ui(
            mod_add_expat,
            ("render_add_expat", "render", "show", "main"),
            engine=engine,
            lang=norm_lang,
            **kwargs,
        ):
            st.info("找不到或無法載入 `add_expat.py` 的渲染函式。")

    with tab4:
        if not _call_module_ui(
            mod_edit,
            ("render_edit_profile", "render", "show", "main"),
            engine=engine,
            lang=norm_lang,
            **kwargs,
        ):
            st.info("找不到或無法載入 `edit_profile.py` 的渲染函式。")

    with tab5:
        if not _call_module_ui(
            mod_resigned,
            ("render_resigned_list", "render", "show", "main"),
            engine=engine,
            lang=norm_lang,
            **kwargs,
        ):
            st.info("找不到或無法載入 `resigned_list.py` 的渲染函式。")


def render(engine=None, lang="zh", **kwargs):
    return render_hr_profile_page(engine=engine, lang=lang, **kwargs)


def show(engine=None, lang="zh", **kwargs):
    return render_hr_profile_page(engine=engine, lang=lang, **kwargs)


def main(engine=None, lang="zh", **kwargs):
    return render_hr_profile_page(engine=engine, lang=lang, **kwargs)


def render_employee_profile(engine=None, lang="zh", **kwargs):
    return render_hr_profile_page(engine=engine, lang=lang, **kwargs)
