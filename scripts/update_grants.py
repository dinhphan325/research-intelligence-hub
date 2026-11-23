#!/usr/bin/env python3
"""Conservative official ARC scheme-calendar monitor.
Only matches scheme name and explicit submission date from ARC's official HTML.
Preserves existing verified calls if fetch or parsing fails; never guesses dates.
"""
import json,re,urllib.request,datetime,sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];PATH=ROOT/'data/grants.json'
URL='https://www.arc.gov.au/funding-research/scheme-calendar'
SCHEMES=[('Discovery Projects 2028','Discovery Projects','Corporate Finance'),('Industrial Transformation Research Program 2027','Industrial Transformation','Cyber Risk')]
def norm(s):return re.sub(r'\s+',' ',s).strip()
def main():
    existing=json.loads(PATH.read_text()) if PATH.exists() else {'grants':[]}
    req=urllib.request.Request(URL,headers={'User-Agent':'ResearchIntelligenceHub/2.0 (academic research monitoring)'})
    try:
        with urllib.request.urlopen(req,timeout=30) as response:html=response.read()
        soup=BeautifulSoup(html,'html.parser');records=[]
        for tr in soup.select('tr'):
            cells=tr.find_all(['td','th'],recursive=False)
            if len(cells)<2:continue
            name=norm(cells[0].get_text(' ',strip=True));dates=norm(cells[1].get_text(' ',strip=True))
            for display,needle,topic in SCHEMES:
                if needle.lower() not in name.lower():continue
                if 'Industrial Transformation' in display and not any(z in name for z in ('27','2027')):continue
                if 'Discovery Projects' in display and not any(z in name for z in ('28','2028')):continue
                # Date format requires a complete named-month date, not inferred years.
                matches=re.findall(r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})\b',dates,re.I)
                if not matches:continue
                day,month,year=matches[-1];d=datetime.date(int(year),datetime.datetime.strptime(month,'%B').month,int(day)).isoformat()
                if d<datetime.date.today().isoformat():continue
                records.append({'id':'arc-'+re.sub('[^a-z0-9]+','-',display.lower()).strip('-'),'title':display,'funder':'Australian Research Council','discipline':'Interdisciplinary','deadline':d,'date':d,'score':85 if 'Discovery' in display else 88,'topics':[topic,'Interdisciplinary'],'summary':'Official ARC scheme-calendar entry; timing is indicative and subject to change. Confirm scheme guidelines and university internal deadline.','eligibility':'Applications through an eligible administering organisation; verify scheme-specific rules and RMIT Research Office requirements.','amount':'See official scheme guidelines','url':URL,'source':'ARC NCGP Scheme Calendar','deadline_status':'Indicative (official ARC calendar)','verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        if not records:raise ValueError('No matching future scheme dates extracted from ARC calendar')
        other=[g for g in existing.get('grants',[]) if not str(g.get('id','')).startswith('arc-')]
        out={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'grants':records+other,'source_url':URL,'note':'Official ARC calendar dates are indicative, not confirmed final deadlines. No comprehensive monitoring of other funders is claimed. RMIT internal dates unverified.'}
        PATH.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
        print('Updated',len(records),'ARC entries')
    except Exception as e:
        print('ARC monitor could not verify new dates; existing grants preserved:',e,file=sys.stderr)
        # Do not overwrite previously verified records; no fabricated updates.
if __name__=='__main__':main()
