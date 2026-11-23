#!/usr/bin/env python3
"""Free, conservative grant monitoring. No inferred dates or fabricated calls.
Only ARC calendar and AFAANZ official page have automatic parsers; other sources
are in the registry for manual review. Existing data/grants.json is untouched.
"""
import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'grants_v3.json'
SOURCES = ROOT / 'data' / 'grant_sources.json'
HEALTH = ROOT / 'data' / 'grant_source_health.json'
ARC = 'https://www.arc.gov.au/funding-research/scheme-calendar'
AFAANZ = 'https://www.afaanz.org/afaanz-research-grants'
MONTHS = {dt.date(2000, m, 1).strftime('%B').lower(): m for m in range(1, 13)}
PATTERN = re.compile(r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})\b', re.I)

def get_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; AcademicResearchGrantsMonitor/3.0)'})
    with urllib.request.urlopen(req, timeout=35) as response:
        return response.read().decode('utf-8', errors='replace')

def dates(text):
    out = []
    for day, month, year in PATTERN.findall(text):
        try: out.append(dt.date(int(year), MONTHS[month.lower()], int(day)).isoformat())
        except ValueError: pass
    return out

def arc_rows(html):
    soup = BeautifulSoup(html, 'html.parser')
    found = {}
    for row in soup.select('tr'):
        cells = row.find_all(['td', 'th'], recursive=False)
        if len(cells) < 2: continue
        name = ' '.join(cells[0].stripped_strings).lower()
        submission = ' '.join(cells[1].stripped_strings)
        vals = dates(submission)
        if len(vals) < 2: continue
        if 'discovery projects' in name and ('dp28' in name or '2028' in name): found['arc-dp28'] = (vals[0], vals[1])
        if 'industrial transformation' in name and ('ic27' in name or 'ih27' in name or '2027' in name): found['arc-itrp27'] = (vals[0], vals[1])
    return found

def afaanz_date(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(' ', strip=True)
    m = re.search(r'Application Closing Date\s*:?\s*(\d{1,2}\s+[A-Za-z]+\s+20\d{2})', text, re.I)
    return dates(m.group(1))[0] if m and dates(m.group(1)) else None

def main():
    doc = json.loads(DATA.read_text(encoding='utf-8'))
    registry = json.loads(SOURCES.read_text(encoding='utf-8'))['sources']
    items = {g['id']:g for g in doc['grants']}
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    health = []
    for source in registry:
        result = {'source_id':source['id'], 'name':source['name'], 'method':source['method'], 'checked_at':now if source['method']=='official_html' else None, 'status':'manual review required' if source['method']!='official_html' else 'not checked', 'detail':''}
        if source['id'] == 'arc':
            try:
                parsed = arc_rows(get_html(ARC))
                if not parsed: raise ValueError('No matching ARC scheme calendar rows parsed; retaining prior records')
                for key, (start, end) in parsed.items():
                    if key in items:
                        items[key].update(opens=start, deadline=end, verified_at=now[:10], verification_status='Official calendar checked', deadline_status='Official indicative calendar')
                result['status'] = 'parsed'; result['detail'] = f'{len(parsed)} tracked schemes matched'
            except Exception as exc:
                result['status'] = 'error; existing data preserved'; result['detail'] = str(exc)[:200]
        elif source['id'] == 'afaanz':
            try:
                d = afaanz_date(get_html(AFAANZ))
                if not d: raise ValueError('No explicit closing date on official page')
                # Never convert a previous round to a new round without explicit round-year verification.
                if 'afaanz-2026' in items and d.startswith('2026-'):
                    items['afaanz-2026'].update(deadline=d, verified_at=now[:10], verification_status='Official funding page checked')
                result['status'] = 'parsed'; result['detail'] = f'Explicit published date {d}; no future round inferred'
            except Exception as exc:
                result['status'] = 'error; existing data preserved'; result['detail'] = str(exc)[:200]
        health.append(result)
    # Existing records remain intact; never remove or invent calls on a fetch failure.
    doc['grants'] = list(items.values()); doc['updated_at'] = now
    DATA.write_text(json.dumps(doc, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    HEALTH.write_text(json.dumps({'updated_at':now,'sources':health},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Grant records:',len(items),'Sources:',len(registry))
    for x in health:
        if x['method']=='official_html':print(x['name'],x['status'],x['detail'])

if __name__ == '__main__': main()
