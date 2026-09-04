from src.collectors.startups import _parse_markdown
from src.collectors.github import repo_from_url
from src.collectors.jobs import _parse_dt

def test_startup_markdown_parser():
    rows=_parse_markdown('- [Acme](https://acme.example) — AI workflow tool','ai','https://source.example')
    assert rows[0]['name']=='Acme' and rows[0]['website']=='https://acme.example'

def test_github_repo_parser():
    assert repo_from_url('https://github.com/openai/example')=='openai/example'

def test_job_date_parser():
    assert _parse_dt('2026-09-04T08:00:00Z').tzinfo is not None
