import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
item=json.loads((root/'content/automation/2026-08-28-0900.json').read_text())
p=root/'content/blogger_posts.json'; posts=json.loads(p.read_text())
if not any(x.get('title')==item['title'] for x in posts):
    posts.append({k:item[k] for k in ('title','labels','content')}); p.write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n')
c=root/'content/seo_clusters.json'; data=json.loads(c.read_text())
for cluster in data['clusters']:
    if cluster['name']=='Organização financeira':
        if item['title'] not in cluster['existing']: cluster['existing'].append(item['title'])
        cluster['next_long_tails']=['Como montar um orçamento mensal simples sem planilha complicada','Quanto da renda deve sobrar no fim do mês?','Como separar dinheiro para contas anuais e imprevistos?']
c.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
pub=root/'scripts/publish_blogger.py'; s=pub.read_text(); key='orçamento mensal: como organizar o dinheiro e saber quanto realmente sobra'
if key not in s:
    marker='COVER_BY_TITLE = {'
    s=s.replace(marker, marker+'\n    "'+key+'": f"{COVER_BASE}/orcamento-mensal-guia-20260828.svg",')
    pub.write_text(s)
