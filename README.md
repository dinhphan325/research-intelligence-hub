# Research Intelligence Hub — free live-publications edition

This package **replaces the prototype** with a real OpenAlex publication feed. It starts empty until the first successful GitHub Actions run. It does **not** yet contain verified ABDC A* ratings or a comprehensive live grants crawler.

## Deploy to existing repository

1. Download and extract the ZIP.
2. Open `https://github.com/dinhphan325/research-intelligence-hub`.
3. Upload the package's **contents** to the repository root, preserving the paths: `index.html`, `data/journals.json`, `data/papers.json`, `data/grants.json`, `scripts/update.py`, `.github/workflows/update-papers.yml`. Do not upload the enclosing `live-update` folder. GitHub's browser upload can be awkward for folders; easiest is to use **Add file → Upload files** and drag the files/folders from your extracted package into the browser, checking the resulting paths. Alternatively use GitHub Desktop to copy the files into a cloned repository and commit/push.
4. Allow GitHub Actions to write to the repository: **Settings → Actions → General → Workflow permissions → Read and write permissions → Save** (if the setting is available).
5. Open **Actions → Update journal publications → Run workflow → Run workflow**. Wait for the run to finish and inspect any error messages.
6. Refresh the Pages website after the successful workflow commits `data/papers.json`.

## API limits

OpenAlex currently offers free API access with usage limits. For reliability, request a free API key if needed and add it to **Settings → Secrets and variables → Actions → New repository secret**, named `OPENALEX_API_KEY`. Never paste a secret into the HTML or commit it to the repository. The script runs without a key where free unauthenticated access is allowed.

## What is real and what is not

- **Real:** publication metadata retrieved from OpenAlex, linked DOI/publisher URLs, dates as supplied by OpenAlex.
- **Provisional:** watchlist journal names; ABDC A* verification is **pending**. No source is labelled verified A*.
- **Heuristic:** relevance score, generated locally from keywords; **not AI**.
- **Not yet implemented:** automatic comprehensive grant discovery, internal RMIT deadline verification, weekly email digests, AI-generated summaries, and authoritative ABDC rating import.
- **Failure behavior:** if all journal requests fail, the workflow fails and retains existing data; if some fail, existing records are retained and the JSON records which journal queries failed. Only up to 100 newest papers per journal within the past 100 days are fetched on each run; this is not a complete historical archive.

## Add verified grants manually

Edit `data/grants.json` in GitHub with objects like:

```json
{"updated_at":"2026-11-23T00:00:00Z","grants":[{"id":"official-call-id","title":"Exact call name","funder":"Funder name","discipline":"Finance","deadline":"2027-05-01","amount":"As stated by funder","eligibility":"Official eligibility text summary","summary":"Research fit","score":85,"topics":["Corporate Finance"],"url":"https://official-funder.example/call"}]}
```

Only add grants whose actual open call, eligibility, deadline and official URL have been checked. Example URL above is a placeholder, not a real grant.

## Cost

GitHub Pages and GitHub Actions may be free within GitHub's applicable plan, usage limits and terms. OpenAlex free usage is limited and subject to change. This package has no paid AI calls or database.
