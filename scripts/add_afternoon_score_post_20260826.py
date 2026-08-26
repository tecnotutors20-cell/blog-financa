#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/'content/automation/2026-08-26-1400.json').read_text(encoding='utf-8'))
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
        c['next_long_tails']=[x for x in c.get('next_long_tails',[]) if x.casefold()!='consultar o score várias vezes diminui a pontuação?'.casefold()]
clusters_path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pub=ROOT/'scripts/publish_blogger.py'
s=pub.read_text(encoding='utf-8')
key='    "consultar o score várias vezes diminui a pontuação? entenda a diferença entre consulta própria e consulta de empresas": f"{COVER_BASE}/consultar-score-varias-vezes-20260826.svg",\n'
marker='COVER_BY_TITLE = {\n'
if key not in s: s=s.replace(marker,marker+key)
pub.write_text(s,encoding='utf-8')
