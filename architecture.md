# Architecture

```text
RSS / public JSON / public startup directory / arXiv
                |
        Async-friendly collectors
                |
      validation + normalization
                |
      +---------+---------+
      |                   |
   entity resolver     LLM orchestrator
      |             Gemini -> Groq -> DeepSeek
      |             429 backoff / 413 chunking
      +---------+---------+
                |
        canonical records
                |
        CSV / Google Sheet
```

## Scale and fault tolerance
Collectors are isolated so one external source can fail without stopping the run. Production deployment should use a queue, bounded concurrency, retry budgets, raw-object storage, and idempotency keys.

## Freshness
News and jobs are filtered against the current UTC time with a strict 24-hour window. Missing/undated job records are not treated as fresh.

## Storage
For the demo, CSVs are Google-Sheet-ready. A production design would use PostgreSQL as the system of record, object storage for raw pages, a vector database for retrieval, and a graph store for entity relationships.
