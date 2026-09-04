from src.entity.resolver import normalize, resolve
from src.entity.seed import SEED
from src.llm.orchestrator import LLMOrchestrator

def test_normalize(): assert normalize("OpenAI, Inc.") == "openaiinc"
def test_seed_has_50_records(): assert len(SEED) == 50
def test_resolver_exact(): assert resolve("OpenAI", SEED)["status"] == "matched"
def test_chunking(): assert len(LLMOrchestrator.chunk_text("a"*25000, 10000)) == 3
