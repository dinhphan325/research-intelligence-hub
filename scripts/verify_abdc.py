#!/usr/bin/env python3
"""Verify candidate journals against user-provided official ABDC 2025 XLS/XLSX list.
No rating is inferred when the workbook or a matching record is missing.
"""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'
def norm(v):return re.sub('[^a-z0-9]','',str(v or '').lower())
def main():
    cfg=json.loads((DATA/'journals.json').read_text())
    books=list(DATA.glob('ABDC*2025*.xlsx'))+list(DATA.glob('ABDC*2025*.xls'))
    if not books:
        print('No official 2025 ABDC workbook supplied; all rankings remain unverified')
        return
    import pandas as pd
    book=books[0]
    excel=pd.ExcelFile(book)
    sheets=[s for s in excel.sheet_names if '2025' in str(s)]
    if not sheets:raise RuntimeError('Official workbook has no identifiable 2025 sheet; no ratings changed')
    df=pd.read_excel(book,sheet_name=sheets[0],header=None,dtype=str).fillna('')
    header=None
    for i,row in df.head(30).iterrows():
        vals=[norm(x) for x in row]
        names=[k for k,v in enumerate(vals) if any(z in v for z in ('journalname','journaltitle','journal')) and 'issn' not in v]
        ranks=[k for k,v in enumerate(vals) if '2025' in v and ('rating' in v or 'rank' in v) or v in ('abdc rating','rating','2025')]
        if names and ranks:header=(i,names[0],ranks[0]);break
    if header is None:raise RuntimeError('Could not identify journal and 2025 rating columns; no ratings changed')
    idx,namecol,rankcol=header
    mapping={}
    for _,r in df.iloc[idx+1:].iterrows():
        n=norm(r.iloc[namecol]);v=str(r.iloc[rankcol]).strip().upper().replace(' ','')
        if n and v in ('A*','A','B','C'):mapping.setdefault(n,set()).add(v)
    verified=0
    for j in cfg['journals']:
        hits=mapping.get(norm(j['name']),set())
        j['abdc_2025_rating']=next(iter(hits)) if len(hits)==1 else None
        j['abdc_verified']=len(hits)==1
        if j['abdc_verified']:verified+=1
    cfg['ranking_edition']='2025';cfg['ranking_verified']=verified==len(cfg['journals'])
    cfg['verification_source']='https://abdc.edu.au/abdc-journal-quality-list/'
    cfg['note']=f'{verified}/{len(cfg["journals"])} journals matched uniquely against supplied official ABDC 2025 workbook; unmatched journals unverified.'
    (DATA/'journals.json').write_text(json.dumps(cfg,indent=2,ensure_ascii=False)+'\n')
    print(cfg['note'])
if __name__=='__main__':main()
