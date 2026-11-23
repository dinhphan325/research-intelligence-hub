#!/usr/bin/env python3
"""Best-effort OpenAlex publication refresh; no paid APIs. Fails closed on fetch errors."""
import json, os, re, sys, time, urllib.parse, urllib.request
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
HEAD={'User-Agent':'ResearchIntelligenceHub/1.0 (academic publication monitor)'}

def fetch(url):
    req=urllib.request.Request(url,headers=HEAD)
    with urllib.request.urlopen(req,timeout=25) as r:return json.load(r)

def norm(s):return re.sub(r'[^a-z0-9]','',s.lower())
def get_source(name):
    q=urllib.parse.urlencode({'search':name,'per_page':10})
    res=fetch('https://api.openalex.org/sources?'+q)['results']
    exact=[x for x in res if norm(x.get('display_name',''))==norm(name) and x.get('type')=='journal']
    if len(exact)!=1:raise ValueError('Ambiguous or missing OpenAlex journal: '+name)
    return exact[0]

TOPICS={
 'Cyber Risk':['cyber','cybersecurity','data breach','information security','ransomware','privacy','digital security'],
 'Corporate Finance':['corporate finance','capital structure','debt maturity','cost of debt','financial constraints','financing','liquidity','investment','capital allocation','leverage','bond','credit risk'],
 'ESG':['esg','climate','sustainability','environmental risk','carbon','transition risk','corporate social responsibility'],
 'Trade Credit':['trade credit','supplier financing','accounts payable','supply chain finance','supplier credit'],
 'Derivatives':['derivative','hedging','risk management','futures','options','volatility','tail risk'],
 'AI':['artificial intelligence','machine learning','automation','digital transformation','algorithmic','large language model'],
 'Interdisciplinary':['corporate governance','information asymmetry','innovation','firm performance','regulation','policy uncertainty','economic shocks','intangible capital']}
def score(text):
    s=text.lower()
    hits={k:sum(1 for w in words if w in s) for k,words in TOPICS.items()}
    matched=[k for k,v in hits.items() if v]
    if not matched:return 15,[]
    primary=sum(hits[k] for k in matched if k!='Interdisciplinary')
    interdisciplinary=len([k for k in matched if k!='Interdisciplinary'])
    # Explicit, interpretable heuristic. A score >=80 requires multiple signals.
    value=35+min(40,primary*14)+min(15,max(0,interdisciplinary-1)*8)+min(10,hits['Interdisciplinary']*5)
    return min(100,value),matched

def abstract(inv):
    if not inv:return ''
    words={}
    for w,positions in inv.items():
        for p in positions:words[p]=w
    return ' '.join(words[i] for i in sorted(words))[:1800]

def main():
    cfg=json.loads((DATA/'journals.json').read_text())
    previous=json.loads((DATA/'papers.json').read_text()) if (DATA/'papers.json').exists() else {'papers':[]}
    byid={p['id']:p for p in previous.get('papers',[])}
    errors=[]; success=0
    since=(date.today()-timedelta(days=100)).isoformat()
    for j in cfg['journals']:
        # Monitor only journals confirmed A* when an official rating exists.
        if j.get('abdc_verified') and j.get('abdc_2025_rating') != 'A*':
            continue
        try:
            src=get_source(j['name']); sid=src['id'].split('/')[-1]
            params={'filter':f'primary_location.source.id:{sid},from_publication_date:{since},type:article', 'sort':'publication_date:desc','per_page':100}
            api_key=os.getenv('OPENALEX_API_KEY','').strip()
            if api_key:params['api_key']=api_key
            response=fetch('https://api.openalex.org/works?'+urllib.parse.urlencode(params))
            for w in response.get('results',[]):
                doi=w.get('doi'); uid=(doi or w.get('id') or '').lower()
                if not uid:continue
                title=w.get('display_name') or w.get('title') or ''
                if not title:continue
                abs_text=abstract(w.get('abstract_inverted_index'))
                sc,topics=score(title+' '+abs_text)
                byid[uid]={'id':uid,'title':title,'journal':j['name'],'discipline':j['discipline'],'date':w.get('publication_date') or '', 'authors':', '.join(a.get('author',{}).get('display_name','') for a in w.get('authorships',[])[:8]),'doi':doi or '', 'url':doi or w.get('id') or '', 'abstract':abs_text,'score':sc,'topics':topics,'ranking_status':('ABDC 2025 A* verified' if j.get('abdc_verified') and j.get('abdc_2025_rating')=='A*' else 'ABDC A* unverified'),'ranking_edition':('2025' if j.get('abdc_verified') else None),'source':'OpenAlex','source_id':sid}
            success+=1
        except Exception as exc:errors.append(f"{j['name']}: {str(exc)[:180]}")
        time.sleep(.12)
    if not success:
        print('No journal queries succeeded; preserving existing papers.json',file=sys.stderr)
        print('\n'.join(errors),file=sys.stderr)
        sys.exit(1)
    rows=sorted(byid.values(),key=lambda x:x.get('date',''),reverse=True)[:1500]
    output={'updated_at':datetime.now(timezone.utc).isoformat(),'papers':rows,'journal_queries_succeeded':success,'journal_queries_total':len(cfg['journals']),'errors':errors,'note':'ABDC 2025 verification is per journal, based on official workbook if supplied. Relevance is heuristic, not AI.'}
    (DATA/'papers.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(f'Saved {len(rows)} publications from {success}/{len(cfg["journals"])} journal queries. Errors: {len(errors)}')
    if errors:print('\n'.join(errors),file=sys.stderr)

if __name__=='__main__':main()
