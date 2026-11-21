from modules.management.announcements import announcement_hub

__all__ = ["render", "show"]


def render(engine=None, lang="zh", **kwargs):
    for fn_name in ("render", "show", "main", "render_announcement_hub", "render_announcements"):
        fn = getattr(announcement_hub, fn_name, None)
        if callable(fn):
            return fn(engine=engine, lang=lang, **kwargs)
    raise AttributeError("announcement_hub 找不到可呼叫的 render / show 函式")


def show(engine=None, lang="zh", **kwargs):
    return render(engine=engine, lang=lang, **kwargs)
