from src.collectors.arxiv import collect_papers
from src.collectors.jobs import _recent

def test_recent_accepts_missing_date():
    assert _recent("") is False

def test_arxiv_empty_is_safe(monkeypatch):
    import src.collectors.arxiv as a
    class R:
        text = "<feed></feed>"
        def raise_for_status(self): pass
    monkeypatch.setattr(a.requests, "get", lambda *args, **kwargs: R())
    assert collect_papers(5) == []
