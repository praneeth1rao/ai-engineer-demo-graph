import os, sys
from dotenv import load_dotenv
from src.collectors.arxiv import collect_papers
from src.collectors.github import enrich_papers
from src.collectors.startups import collect_startups
from src.collectors.products import collect_products
from src.collectors.news import collect_news
from src.collectors.jobs import collect_jobs
from src.storage.csv_store import write_csv
from src.entity.seed import SEED
from src.entity.resolver import resolve
from src.storage.workbook import write_workbook

load_dotenv()

def env_list(name): return [x.strip() for x in os.getenv(name, "").split(";") if x.strip()]

def run():
    out=os.getenv("OUTPUT_DIR","data/processed")
    paper_target=int(os.getenv("PAPER_TARGET","1000")); startup_target=int(os.getenv("STARTUP_TARGET","1000")); product_target=int(os.getenv("PRODUCT_TARGET","1000")); news_target=int(os.getenv("NEWS_TARGET","100")); job_target=int(os.getenv("JOB_TARGET","100"))
    print("[1/6] Collecting startups..."); startups=collect_startups(startup_target); print(f"Startups: {len(startups)}")
    print("[2/6] Collecting product candidates..."); products=collect_products(product_target); print(f"Products: {len(products)}")
    print("[3/6] Collecting research papers from arXiv..."); papers=collect_papers(paper_target); papers=enrich_papers(papers); print(f"Papers: {len(papers)}")
    print("[4/6] Collecting fresh AI news..."); news=collect_news(env_list("NEWS_FEEDS"),news_target); print(f"Fresh news: {len(news)}")
    print("[5/6] Collecting fresh AI jobs..."); jobs=collect_jobs(env_list("JOB_FEEDS"),job_target); print(f"Fresh jobs: {len(jobs)}")
    print("[6/6] Running deterministic entity resolution...")
    mapping=[]
    for row in startups:
        rr=resolve(row.get("name"),SEED); row["entity_status"]=rr["status"]
        mapping.append({"entity_type":"startup","canonical_name":rr["canonical_name"],"match_score":rr["match_score"],"status":rr["status"],"source_url":row.get("source_url","")})
    for row in products:
        rr=resolve(row.get("name"),SEED)
        mapping.append({"entity_type":"product","canonical_name":rr["canonical_name"],"match_score":rr["match_score"],"status":rr["status"],"source_url":row.get("source_url","")})
    datasets={"Startups":startups,"Products":products,"Research Papers":papers,"News":news,"Jobs":jobs,"Entity Mapping Log":mapping}
    for tab,rows in datasets.items(): write_csv(f"{out}/{tab.replace(' ','_').lower()}.csv",rows)
    write_workbook(f"{out}/ai_intelligence_graph.xlsx", datasets)
    print("Collection complete."); print(f"Output: {out}")
    print("Source diagnostics: zero news/jobs is allowed when no qualifying records fall inside the exact 24h window; no synthetic records are created.")

if __name__=="__main__":
    if "--mode" not in sys.argv: print("Usage: python main.py --mode collect"); raise SystemExit(1)
    run()
