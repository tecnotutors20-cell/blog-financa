#!/usr/bin/env python3
import hashlib, html, io, json, runpy, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

base = runpy.run_path(str(Path(__file__).with_name('publish_recipe_20260825_1000.py')), run_name='recipe_base')
TITLE = 'Palitinhos de Legumes Assados para Bebê: Receita Macia para Pegar com as Mãos'
SLUG_KEY = 'palitinhos-legumes-assados-bebe'
CLUSTER = 'Cluster 2 — BLW e alimentos para pegar com as mãos'
KEYWORD = 'palitinhos de legumes assados para bebê'
MARKER = base['MARKER']; BLOG_ID = base['BLOG_ID']; ROOT = base['ROOT']; COVER_DIR = base['COVER_DIR']; RAW_BASE = base['RAW_BASE']; LOG_PATH = base['LOG_PATH']; RESULT_PATH = base['RESULT_PATH']
W,H = 1200,630

def generate_cover(path):
    prompt = ("Photorealistic horizontal food photograph for a Brazilian baby-friendly recipe titled 'Palitinhos de Legumes Assados para Bebê'. "
              "Show soft oven-roasted thick finger-sized sticks of sweet potato, carrot and zucchini arranged separately on a matte light ceramic plate. "
              "Vegetables should look tender, lightly browned only at the edges, moist and easy to squash, never crispy, fried, hard or charred. "
              "Natural family dining setting, light oak table, soft afternoon window light, three-quarter editorial food photography, subtle home kitchen blur. "
              "No baby, no child, no people, no hands. No text, typography, logo, watermark, packaging, labels, collage, illustration or cartoon. "
              "Realistic imperfections, natural food colors, professional recipe blog photography.")
    encoded = urllib.parse.quote(prompt, safe='')
    seed = int(hashlib.sha256(TITLE.encode()).hexdigest()[:12],16) % 2147483647
    last=None
    for attempt in range(8):
        url=f'https://image.pollinations.ai/prompt/{encoded}?width={W}&height={H}&model=flux&nologo=true&safe=true&enhance=true&seed={seed+attempt*10007}'
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; ReceitasParaPequenos/3.0)','Accept':'image/*'})
            with urllib.request.urlopen(req,timeout=240) as r: raw=r.read()
            if len(raw)<15000: raise RuntimeError('small image response')
            im=Image.open(io.BytesIO(raw)).convert('RGB'); tr=W/H; cr=im.width/im.height
            if cr>tr:
                nw=int(im.height*tr); x=(im.width-nw)//2; im=im.crop((x,0,x+nw,im.height))
            elif cr<tr:
                nh=int(im.width/tr); y=(im.height-nh)//2; im=im.crop((0,y,im.width,y+nh))
            im=im.resize((W,H),Image.Resampling.LANCZOS); path.parent.mkdir(parents=True,exist_ok=True); im.save(path,'JPEG',quality=92,optimize=True,progressive=True); return
        except Exception as e:
            last=e; time.sleep(min(10*(attempt+1),45))
    raise RuntimeError(f'cover generation failed: {last}')

def article_html(cover_url):
    schema={'@context':'https://schema.org','@type':'Recipe','name':TITLE,'image':[cover_url],
      'author':{'@type':'Organization','name':'Equipe Editorial do Receitas Para Pequenos'},
      'description':'Palitinhos macios de batata-doce, cenoura e abobrinha assados, com formato fácil de adaptar para a criança pegar com as mãos.',
      'recipeCategory':'Almoço, jantar e lanche','recipeCuisine':'Brasileira',
      'keywords':'palitinhos de legumes assados para bebê, BLW, legumes macios para bebê, alimentação complementar',
      'recipeYield':'1 assadeira pequena',
      'recipeIngredient':['1/2 batata-doce pequena','1 cenoura pequena','1/2 abobrinha pequena','1 colher (chá) de azeite para untar ou pincelar levemente'],
      'recipeInstructions':[{'@type':'HowToStep','text':'Corte os legumes em palitos grossos e regulares.'},{'@type':'HowToStep','text':'Asse até ficarem completamente macios por dentro, sem formar crosta dura.'},{'@type':'HowToStep','text':'Espere amornar e teste a maciez antes de servir.'}]}
    sj=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    alt=html.escape(TITLE+' - Receitas Para Pequenos',quote=True)
    return f"""{MARKER}
<div class='separator' style='clear:both;margin:0 0 24px;text-align:center'><img alt='{alt}' data-original-height='630' data-original-width='1200' src='{cover_url}' style='border-radius:14px;height:auto;max-width:100%;width:1200px'/></div>
<p><strong>Por Equipe Editorial do Receitas Para Pequenos</strong></p>
<p>Estes palitinhos de legumes assados são uma forma simples de oferecer vegetais macios em pedaços que podem ser segurados com as mãos. A receita usa batata-doce, cenoura e abobrinha, cortadas em formatos grossos e assadas somente até ficarem bem macias.</p>
<p><strong>Atenção:</strong> o tamanho, o formato e a maciez devem ser adaptados às habilidades individuais da criança, sempre sentada e supervisionada durante a refeição. Em caso de alergias, dificuldades de mastigação/deglutição ou necessidades especiais, procure orientação de profissional habilitado.</p>
<h2>Ingredientes</h2><ul><li>1/2 batata-doce pequena</li><li>1 cenoura pequena</li><li>1/2 abobrinha pequena</li><li>1 colher (chá) de azeite para untar ou pincelar levemente</li></ul>
<h2>Modo de preparo</h2><ol><li>Lave e descasque a batata-doce e a cenoura. Lave a abobrinha.</li><li>Corte os legumes em palitos grossos e compridos, evitando peças muito finas que ressequem no forno.</li><li>Disponha em uma assadeira e pincele uma quantidade pequena de azeite apenas para evitar que grudem.</li><li>Asse em forno preaquecido a 200 °C, virando quando necessário, até que todos estejam completamente macios por dentro. Retire antes de criar uma crosta dura.</li><li>Espere amornar e pressione cada palito entre os dedos ou com um garfo para confirmar que está macio antes de servir.</li></ol>
<h2>Como deve ficar a textura</h2><p>O ponto ideal é macio o suficiente para ceder facilmente à pressão dos dedos ou do garfo. Não procure uma textura crocante. O Guia Alimentar para Crianças Brasileiras Menores de 2 Anos orienta que alguns alimentos macios podem ser oferecidos em pedaços grandes o suficiente para a criança pegar com as próprias mãos, conforme suas habilidades.</p>
<h2>Como servir e adaptar</h2><p>Os palitos podem ser oferecidos separados para que a criança explore cores e texturas diferentes. Se ela ainda não lida bem com pedaços, os mesmos legumes podem ser amassados com o garfo. O formato não deve ser definido apenas pela idade cronológica: adapte à capacidade de pegar, levar à boca e lidar com a textura.</p>
<h2>Substituições culinárias</h2><p>A batata-doce pode ser trocada por mandioquinha ou abóbora em pedaços grossos, desde que o alimento asse até ficar realmente macio. A cenoura e a abobrinha também podem ser oferecidas separadamente. Alterações relacionadas a alergias ou necessidades específicas devem ser discutidas com profissional habilitado.</p>
<h2>Armazenamento</h2><p>Como a textura é o ponto principal desta receita, o melhor resultado costuma ser logo após o preparo. Se houver sobra que não teve contato com a boca da criança, resfrie e armazene de acordo com boas práticas de conservação de alimentos; reaqueça completamente e confira novamente a maciez antes de servir.</p>
<h2>Perguntas frequentes</h2>
<h3>Os palitinhos precisam ficar dourados?</h3><p>Não. Um leve dourado nas bordas pode acontecer, mas o objetivo é manter o interior muito macio, sem formar casca dura.</p>
<h3>Posso fazer na air fryer?</h3><p>É possível, mas o ar mais intenso pode ressecar peças finas rapidamente. Use cortes grossos, acompanhe o ponto e priorize maciez, não crocância.</p>
<h3>Preciso temperar?</h3><p>Não é obrigatório. A proposta é simples e permite que o sabor dos próprios legumes fique evidente. Se a família usar temperos naturais, mantenha a preparação adequada à alimentação da criança.</p>
<h2>Receitas relacionadas</h2><ul>
<li><a href='https://www.receitasparapequenos.site/2026/08/bolinho-de-batata-doce-e-frango-assado.html'>Bolinho de Batata-Doce e Frango Assado para Bebê</a></li>
<li><a href='https://www.receitasparapequenos.site/2026/07/bolinho-de-arroz-e-legumes-para-bebes.html'>Bolinho de Arroz e Legumes para Bebês</a></li>
<li><a href='https://www.receitasparapequenos.site/2026/07/panqueca-de-batata-doce-para-bebes.html'>Panqueca de Batata-Doce para Bebês</a></li></ul>
<h2>Referências oficiais</h2><ul><li><a href='https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-da-crianca/primeira-infancia/alimentacao-saudavel' rel='nofollow'>Ministério da Saúde — Alimentação saudável na primeira infância</a></li><li><a href='https://www.gov.br/saude/pt-br/composicao/saps/promocao-da-saude/guias-alimentares/publicacoes/guia_da_crianca_2019.pdf/view' rel='nofollow'>Ministério da Saúde — Guia Alimentar para Crianças Brasileiras Menores de 2 Anos</a></li></ul>
<script type='application/ld+json'>{sj}</script>"""

def main():
    tok=base['token'](); posts=base['list_posts'](tok)
    for p in posts:
        t=(p.get('title') or '').casefold()
        if t==TITLE.casefold() or ('palitinhos' in t and 'legumes' in t and 'bebê' in t):
            RESULT_PATH.write_text(f'outcome=skipped_duplicate\ntitle={p.get("title","")}\nurl={p.get("url","")}\n',encoding='utf-8'); base['git_commit_push']([RESULT_PATH],'Record duplicate prevention for afternoon BLW recipe'); return
    suffix=hashlib.sha1(TITLE.encode()).hexdigest()[:10]; cp=COVER_DIR/f'{SLUG_KEY}-{suffix}.jpg'; cu=f'{RAW_BASE}/{cp.name}'
    if not cp.exists(): generate_cover(cp); base['git_commit_push']([cp],'Add unique AI food photo for roasted vegetable sticks'); time.sleep(8)
    content=article_html(cu)
    if MARKER not in content or cu not in content: raise RuntimeError('cover marker verification failed before publish')
    created=base['api'](tok,'POST',f'/blogs/{BLOG_ID}/posts',{'isDraft':'false','fetchBody':'true'},{'kind':'blogger#post','blog':{'id':BLOG_ID},'title':TITLE,'content':content,'labels':['Alimentação complementar','BLW','Legumes','Receitas assadas']})
    pid=str(created.get('id','')); url=created.get('url','')
    if not pid: raise RuntimeError('Blogger did not return post id')
    verified=base['api'](tok,'GET',f'/blogs/{BLOG_ID}/posts/{pid}',{'view':'ADMIN'}); vc=verified.get('content') or ''
    if MARKER not in vc or cu not in vc: raise RuntimeError('live Blogger post failed cover verification')
    log=base['load_log'](); log.append({'published_at':created.get('published'),'title':TITLE,'url':url,'post_id':pid,'cluster':CLUSTER,'keyword':KEYWORD,'cover_url':cu,'marker':MARKER}); LOG_PATH.write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    RESULT_PATH.write_text('outcome=success\n'+f'title={TITLE}\nurl={url}\npost_id={pid}\ncluster={CLUSTER}\ncover_url={cu}\nmarker_verified=true\n',encoding='utf-8'); base['git_commit_push']([LOG_PATH,RESULT_PATH],'Record published roasted vegetable sticks BLW recipe')

if __name__=='__main__': main()
