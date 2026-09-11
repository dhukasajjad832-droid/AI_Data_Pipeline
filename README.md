# AI Data Pipeline

## Project Kya Karta Hai

Ye project AI-related data ko different public sources se collect karta hai,
use JSON format me convert karta hai, entity names ko normalize karta hai,
freshness check karta hai aur additional information enrich karta hai.

Pipeline:

Source → Async Crawler → Raw Data → Structured JSON → Entity Resolution
→ Enrichment → Final Dataset


## Project Me Kya Collect Kiya Gaya Hai

### Startups
GitHub public organization search se startup candidates collect kiye gaye.

Records:
1000

File:
data/startup_records_1000.json


### Products
Hugging Face Hub API se real AI/ML model records collect kiye gaye.

Records:
1000

File:
data/product_records.json


### Research Papers
arXiv API se research papers collect kiye gaye.

Records:
1000

File:
data/research_papers.json


### AI News
AI news sources se articles collect kiye gaye.

Sources:
- TechCrunch AI
- The Verge AI

Collected articles:
20

Fresh within last 24 hours:
14

File:
data/news_records.json


### AI Jobs
Public job-source pages se records collect kiye gaye.

Sources:
- LinkedIn Jobs
- Indeed
- Wellfound
- Y Combinator Jobs
- Remote OK

File:
data/job_records.json


## Entity Resolution

Different names ko canonical name me convert kiya jata hai.

Example:

OpenAI
Open AI
OpenAI, Inc.

→ OpenAI

Mapping log:

data/entity_mapping_log.json


## LLM Orchestration

Project me LLM extraction architecture aur fallback mechanism included hai.

Files:

src/llm_extractor.py
src/llm_orchestrator.py

Agar primary LLM unavailable ho, fallback extraction path use kiya ja sakta hai.

Production deployment me real LLM provider connect kiya ja sakta hai.


## GitHub Enrichment

Research papers ke available GitHub repositories ko enrich karne ka module included hai.

File:

src/github_enrichment.py

GitHub URL ya star count available na ho to system value ko null rakhta hai.

Fake data generate nahi kiya jata.


## Anti-Bot Handling

Pipeline normal HTTP responses ko respect karta hai.

Agar kisi website se:

403
timeout
connection error

milta hai to system failure ko record karta hai.

Cloudflare, CAPTCHA ya other security mechanisms ko bypass nahi kiya jata.


## Scalability

Current implementation demo-scale data collect karta hai.

Production architecture ko 500K+ records tak scale karne ke liye:

- Async workers
- Task queues
- Pagination
- Rate limiting
- Retry queues
- Checkpointing
- Distributed workers
- PostgreSQL
- Object storage
- Vector database
- Graph database

use kiye ja sakte hain.


## Common Record Structure

```json
{
  "schemaVersion": "1.0",
  "recordType": "TYPE",
  "source": {
    "name": "Source Name",
    "url": "https://example.com"
  },
  "content": {},
  "collectedAt": "timestamp"
}