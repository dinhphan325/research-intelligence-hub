Research Intelligence Hub — Academic Grants V3
This is an additive upgrade for the existing GitHub Pages repository `dinhphan325/research-intelligence-hub`. It preserves your original `data/papers.json`, `data/journals.json`, `data/grants.json`, journal collector, and existing workflow.
Upload these seven files at exact paths
`grants.html` (new interactive global grant dashboard)
`index.html` (modified to link to grants.html and load `data/grants_v3.json`; publication data still loads from existing `data/papers.json`)
`data/grant_sources.json` (28-source registry, including La Trobe and other universities)
`data/grants_v3.json` (three official-source seed rounds, including a closed historical AFAANZ round)
`scripts/update_grants_v3.py` (conservative automated official-source monitor)
`.github/workflows/update-grants-v3.yml` (daily scheduled and manual GitHub Actions)
`README-V3.md` (these instructions)
Do not upload or replace `data/papers.json`, `data/journals.json`, `data/grants.json`, `scripts/update.py`, or `.github/workflows/update-papers.yml`.
Beginner-friendly GitHub upload
For a new file, open `https://github.com/dinhphan325/research-intelligence-hub/new/main`, enter the entire path above in the filename box, paste the contents from the extracted file opened in Notepad, then click Commit changes. For existing `index.html`, open `https://github.com/dinhphan325/research-intelligence-hub/edit/main/index.html`, select all code, replace with the V3 `index.html` content, and commit.
For nested paths, type the full path such as `data/grant_sources.json`, not just `grant_sources.json`. GitHub creates folders automatically. Never upload a ZIP file as a website file.
After committing, open `https://github.com/dinhphan325/research-intelligence-hub/actions/workflows/update-grants-v3.yml`, select Run workflow, choose `main`, and run. GitHub Actions needs repository Read and write permissions (Settings → Actions → General). Inspect the `Monitor official funding sources` log, then open `https://dinhphan325.github.io/research-intelligence-hub/grants.html` and hard refresh (Ctrl+F5).
Coverage and verification limitations
28 sources in registry; only ARC and AFAANZ currently have automated official-page parsers. Others are manual-review sources, not falsely described as automated feeds.
ARC calendar deadlines are indicative. Source: https://www.arc.gov.au/funding-research/scheme-calendar
AFAANZ 2026 deadline was 14 April 2026 (closed). Source: https://www.afaanz.org/afaanz-research-grants. No new round is fabricated.
Internal university grants (including La Trobe) may require that institution's employment/affiliation. RMIT researchers are not automatically eligible.
HERDC is a candidate classification, not confirmed without institutional research-income guidance.
Relevance scores are transparent illustrative topic-fit heuristics for the three seeded records; they are not paid AI evaluations or evidence of eligibility.
GrantConnect and international sources are in the discovery registry, not yet connected to comprehensive automated ingestion. Login-only portals are not scraped.
The monitor preserves prior grant records on failed requests. Check the Monitoring status tab for parser errors and manually review all live calls.
GitHub Actions scheduled runs may be delayed or disabled after prolonged inactivity.
Next phase
Build dedicated, source-specific adapters for publicly accessible official opportunity feeds, with tests, deduplication, eligibility constraints and editorial verification. Do not claim complete worldwide coverage without these adapters.
