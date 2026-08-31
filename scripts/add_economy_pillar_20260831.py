import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
item=json.loads((root/'content/automation/2026-08-31-0900.json').read_text())
p=root/'content/blogger_posts.json'; posts=json.loads(p.read_text())
if not any(x.get('title')==item['title'] for x in posts):
    posts.append({k:item[k] for k in ('title','labels','content')})
    p.write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n')
c=root/'content/seo_clusters.json'; data=json.loads(c.read_text())
cluster=next((x for x in data['clusters'] if x['name']=='Economia e inflação'),None)
if cluster is None:
    cluster={'name':'Economia e inflação','existing':[],'next_long_tails':['Por que meu salário aumenta e mesmo assim parece que compro menos?','IPCA e INPC: qual a diferença e qual índice afeta seu bolso?','Inflação acumulada: como calcular e entender reajustes na prática?']}
    data['clusters'].append(cluster)
if item['title'] not in cluster['existing']:
    cluster['existing'].append(item['title'])
cluster['next_long_tails']=['Por que meu salário aumenta e mesmo assim parece que compro menos?','IPCA e INPC: qual a diferença e qual índice afeta seu bolso?','Inflação acumulada: como calcular e entender reajustes na prática?']
c.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
pub=root/'scripts/publish_blogger.py'; s=pub.read_text(); key='inflação e ipca: como a alta dos preços afeta seu dinheiro e seu poder de compra'
if key not in s:
    marker='COVER_BY_TITLE = {'
    s=s.replace(marker, marker+'\n    "'+key+'": f"{COVER_BASE}/inflacao-ipca-poder-compra-20260831.svg",')
    pub.write_text(s)
