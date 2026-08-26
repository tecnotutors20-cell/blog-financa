#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/'content/automation/2026-08-26-1900.json').read_text(encoding='utf-8'))
posts_path=ROOT/'content/blogger_posts.json'
posts=json.loads(posts_path.read_text(encoding='utf-8'))
if not any(p.get('title','').casefold()==source['title'].casefold() for p in posts):
    posts.append({k:source[k] for k in ('title','labels','content')})
    posts_path.write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
clusters_path=ROOT/'content/seo_clusters.json'
data=json.loads(clusters_path.read_text(encoding='utf-8'))
for c in data['clusters']:
    if c['name']=='Crédito e score':
        if source['title'] not in c['existing']: c['existing'].append(source['title'])
        c['next_long_tails']=[x for x in c.get('next_long_tails',[]) if x.casefold()!=source['title'].casefold()]
clusters_path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pub=ROOT/'scripts/publish_blogger.py'
s=pub.read_text(encoding='utf-8')
key='    "quanto tempo depois de pagar uma dívida o score pode mudar?": f"{COVER_BASE}/score-apos-pagar-divida-20260826.svg",\n'
marker='COVER_BY_TITLE = {\n'
if key not in s: s=s.replace(marker,marker+key)
pub.write_text(s,encoding='utf-8')
