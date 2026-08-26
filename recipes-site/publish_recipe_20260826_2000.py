#!/usr/bin/env python3
import hashlib, html, io, json, runpy, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

base = runpy.run_path(str(Path(__file__).with_name('publish_recipe_20260825_1000.py')), run_name='recipe_base')
TITLE = 'Pãozinho Caseiro Macio sem Açúcar para Bebê: Receita Assada'
SLUG_KEY = 'paozinho-caseiro-macio-sem-acucar-bebe'
CLUSTER = 'Cluster 2 — BLW e alimentos para pegar com as mãos'
KEYWORD = 'pãozinho caseiro macio sem açúcar para bebê'
MARKER = base['MARKER']; BLOG_ID = base['BLOG_ID']; ROOT = base['ROOT']; COVER_DIR = base['COVER_DIR']; RAW_BASE = base['RAW_BASE']; LOG_PATH = base['LOG_PATH']; RESULT_PATH = base['RESULT_PATH']
W,H = 1200,630

def generate_cover(path):
    prompt = ("Photorealistic horizontal food photograph for a Brazilian baby-friendly recipe titled 'Pãozinho Caseiro Macio sem Açúcar para Bebê'. "
              "Show several small soft homemade baked bread rolls made with sweet potato and oat flour, pale golden outside, tender moist crumb, one roll gently split open to show the soft interior. "
              "Arrange on a matte beige ceramic plate with a folded natural linen napkin on a light wooden family table, soft evening window light, cozy realistic Brazilian home-kitchen atmosphere, three-quarter editorial food photography. "
              "The rolls must look soft, tender and easy to tear, not crusty, glossy, fried, dry or hard. No baby, child, people or hands. No text, logo, watermark, packaging, labels, collage, illustration or cartoon. Realistic imperfections and natural food colors.")
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
      'description':'Pãozinho assado, sem açúcar adicionado, com batata-doce e aveia, preparado para ficar macio e fácil de adaptar às habilidades da criança.',
      'recipeCategory':'Lanche e acompanhamento','recipeCuisine':'Brasileira',
      'keywords':'pãozinho caseiro macio sem açúcar para bebê, BLW, pão macio para bebê, alimentação complementar',
      'recipeYield':'8 pãezinhos pequenos',
      'recipeIngredient':['200 g de batata-doce cozida e amassada','1 ovo','6 colheres (sopa) de farinha de aveia','1 colher (chá) de fermento químico em pó'],
      'recipeInstructions':[{'@type':'HowToStep','text':'Misture a batata-doce amassada com o ovo.'},{'@type':'HowToStep','text':'Junte a farinha de aveia aos poucos e finalize com o fermento.'},{'@type':'HowToStep','text':'Modele porções pequenas e asse apenas até firmarem e dourarem levemente, mantendo o interior macio.'}]}
    sj=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    alt=html.escape(TITLE+' - Receitas Para Pequenos',quote=True)
    return f"""{MARKER}
<div class='separator' style='clear:both;margin:0 0 24px;text-align:center'><img alt='{alt}' data-original-height='630' data-original-width='1200' src='{cover_url}' style='border-radius:14px;height:auto;max-width:100%;width:1200px'/></div>
<p><strong>Por Equipe Editorial do Receitas Para Pequenos</strong></p>
<p>Este pãozinho caseiro macio usa batata-doce, ovo e aveia e não leva açúcar adicionado. A proposta é obter um pão pequeno e assado, com interior úmido e macio, que possa ser partido ou adaptado conforme as habilidades da criança.</p>
<p><strong>Atenção:</strong> adapte tamanho, formato e textura às habilidades individuais, sempre com a criança sentada e supervisionada. Em caso de alergias, dificuldades de mastigação/deglutição ou necessidades especiais, procure orientação de profissional habilitado.</p>
<h2>Ingredientes</h2><ul><li>200 g de batata-doce cozida e amassada</li><li>1 ovo</li><li>6 colheres (sopa) de farinha de aveia</li><li>1 colher (chá) de fermento químico em pó</li></ul>
<h2>Modo de preparo</h2><ol><li>Cozinhe a batata-doce até ficar muito macia, escorra bem e amasse com garfo.</li><li>Misture a batata-doce com o ovo até incorporar.</li><li>Adicione a farinha de aveia aos poucos, apenas até formar uma massa úmida que possa ser modelada. A quantidade pode variar com a umidade da batata.</li><li>Misture o fermento por último, sem trabalhar demais a massa.</li><li>Modele pãezinhos pequenos e coloque em assadeira forrada.</li><li>Asse em forno preaquecido a 180 °C até firmarem e dourarem levemente. Retire antes de ficarem secos ou com crosta dura. Espere amornar.</li></ol>
<h2>Como deve ficar a textura</h2><p>O interior deve permanecer macio e úmido, cedendo com facilidade quando apertado entre os dedos. O objetivo não é formar uma casca crocante. O Guia Alimentar para Crianças Brasileiras Menores de 2 Anos orienta a evolução gradual da consistência e admite alimentos macios em pedaços grandes para a criança pegar com as mãos, conforme suas habilidades.</p>
<h2>Como servir e adaptar</h2><p>Para crianças que já conseguem pegar e levar alimentos macios à boca, o pãozinho pode ser oferecido em formato fácil de segurar. Se ainda houver dificuldade com pedaços, ele pode ser partido em porções menores ou desmanchado e amassado com o garfo. O formato deve acompanhar as habilidades individuais, não apenas a idade cronológica.</p>
<h2>Substituições culinárias</h2><p>A batata-doce pode ser trocada por mandioquinha bem cozida e amassada, mas a quantidade de farinha pode mudar. Alterações relacionadas a ovo, aveia, alergias ou necessidades específicas devem ser discutidas com profissional habilitado.</p>
<h2>Armazenamento</h2><p>Prepare porções pequenas e, se houver sobra que não teve contato com a boca da criança, resfrie e armazene seguindo boas práticas de conservação de alimentos. Ao servir novamente, aqueça quando necessário e confira se o pão continua macio, sem partes ressecadas ou duras.</p>
<h2>Perguntas frequentes</h2>
<h3>Precisa adicionar açúcar?</h3><p>Não. O Ministério da Saúde orienta não oferecer preparações ou produtos com açúcar para crianças menores de 2 anos. Nesta receita, a batata-doce já contribui com sabor naturalmente adocicado.</p>
<h3>O pãozinho precisa crescer como pão tradicional?</h3><p>Não. Esta é uma preparação rápida e macia, não um pão fermentado tradicional. O ponto principal é ficar assado por dentro e manter textura úmida.</p>
<h3>Posso deixar bem dourado para ficar crocante?</h3><p>Não é o objetivo desta receita. Retire do forno quando estiver firme e levemente dourado, preservando o interior macio.</p>
<h2>Receitas relacionadas</h2><ul>
<li><a href='https://www.receitasparapequenos.site/2026/08/bolinho-de-batata-doce-e-frango-assado.html'>Bolinho de Batata-Doce e Frango Assado para Bebê</a></li>
<li><a href='https://www.receitasparapequenos.site/2026/08/palitinhos-de-legumes-assados-para-bebe.html'>Palitinhos de Legumes Assados para Bebê</a></li>
<li><a href='https://www.receitasparapequenos.site/2026/07/panqueca-de-batata-doce-para-bebes.html'>Panqueca de Batata-Doce para Bebês</a></li></ul>
<h2>Referências oficiais</h2><ul><li><a href='https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-da-crianca/primeira-infancia/alimentacao-saudavel' rel='nofollow'>Ministério da Saúde — Alimentação saudável na primeira infância</a></li><li><a href='https://www.gov.br/saude/pt-br/composicao/saps/promocao-da-saude/guias-alimentares/publicacoes/guia_da_crianca_2019.pdf/view' rel='nofollow'>Ministério da Saúde — Guia Alimentar para Crianças Brasileiras Menores de 2 Anos</a></li></ul>
<script type='application/ld+json'>{sj}</script>"""

def main():
    tok=base['token'](); posts=base['list_posts'](tok)
    for p in posts:
        t=(p.get('title') or '').casefold()
        if t==TITLE.casefold() or ('pãozinho' in t and 'macio' in t and 'açúcar' in t):
            RESULT_PATH.write_text(f'outcome=skipped_duplicate\ntitle={p.get("title","")}\nurl={p.get("url","")}\n',encoding='utf-8'); base['git_commit_push']([RESULT_PATH],'Record duplicate prevention for evening BLW bread recipe'); return
    suffix=hashlib.sha1(TITLE.encode()).hexdigest()[:10]; cp=COVER_DIR/f'{SLUG_KEY}-{suffix}.jpg'; cu=f'{RAW_BASE}/{cp.name}'
    if not cp.exists(): generate_cover(cp); base['git_commit_push']([cp],'Add unique AI food photo for soft sugar-free baby bread'); time.sleep(8)
    content=article_html(cu)
    if MARKER not in content or cu not in content: raise RuntimeError('cover marker verification failed before publish')
    created=base['api'](tok,'POST',f'/blogs/{BLOG_ID}/posts',{'isDraft':'false','fetchBody':'true'},{'kind':'blogger#post','blog':{'id':BLOG_ID},'title':TITLE,'content':content,'labels':['Alimentação complementar','BLW','Pãozinho','Sem açúcar','Receitas assadas']})
    pid=str(created.get('id','')); url=created.get('url','')
    if not pid: raise RuntimeError('Blogger did not return post id')
    verified=base['api'](tok,'GET',f'/blogs/{BLOG_ID}/posts/{pid}',{'view':'ADMIN'}); vc=verified.get('content') or ''
    if MARKER not in vc or cu not in vc: raise RuntimeError('live Blogger post failed cover verification')
    log=base['load_log'](); log.append({'published_at':created.get('published'),'title':TITLE,'url':url,'post_id':pid,'cluster':CLUSTER,'keyword':KEYWORD,'cover_url':cu,'marker':MARKER}); LOG_PATH.write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    RESULT_PATH.write_text('outcome=success\n'+f'title={TITLE}\nurl={url}\npost_id={pid}\ncluster={CLUSTER}\ncover_url={cu}\nmarker_verified=true\n',encoding='utf-8'); base['git_commit_push']([LOG_PATH,RESULT_PATH],'Record published soft sugar-free baby bread recipe')

if __name__=='__main__': main()
