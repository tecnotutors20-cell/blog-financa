#!/usr/bin/env python3
import hashlib, html, io, json, runpy, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

base = runpy.run_path(str(Path(__file__).with_name('publish_recipe_20260825_1000.py')), run_name='recipe_base')
TITLE = 'Panqueca de Pera e Aveia sem Açúcar para Bebê: Receita Macia'
SLUG_KEY = 'panqueca-pera-aveia-sem-acucar-bebe'
CLUSTER = 'Cluster 3 — Café da manhã e lanches sem açúcar'
KEYWORD = 'panqueca de pera e aveia sem açúcar para bebê'
MARKER=base['MARKER']; BLOG_ID=base['BLOG_ID']; COVER_DIR=base['COVER_DIR']; RAW_BASE=base['RAW_BASE']; LOG_PATH=base['LOG_PATH']; RESULT_PATH=base['RESULT_PATH']
W,H=1200,630

def generate_cover(path):
    prompt=("Photorealistic horizontal food photograph for a Brazilian baby-friendly recipe titled 'Panqueca de Pera e Aveia sem Açúcar para Bebê'. "
            "Show four small soft oat pancakes made with ripe pear, pale golden with tiny natural pear flecks, stacked loosely on a matte cream ceramic plate; one pancake torn open showing a moist tender interior. "
            "Add a few thin fresh pear slices beside the pancakes only as visual ingredient cue. Soft afternoon window light, light stone table, subtle linen napkin, realistic home food photography, three-quarter close-up, natural imperfections. "
            "No syrup, honey, sugar, powdered sugar, chocolate, whipped cream or sweet toppings. No baby, child, people or hands. No text, logo, watermark, packaging, labels, collage, illustration or cartoon.")
    encoded=urllib.parse.quote(prompt,safe=''); seed=int(hashlib.sha256(TITLE.encode()).hexdigest()[:12],16)%2147483647; last=None
    for attempt in range(8):
        try:
            url=f'https://image.pollinations.ai/prompt/{encoded}?width={W}&height={H}&model=flux&nologo=true&safe=true&enhance=true&seed={seed+attempt*10007}'
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
      'description':'Panqueca macia de pera e aveia, sem açúcar adicionado, para café da manhã ou lanche durante a alimentação complementar.',
      'recipeCategory':'Café da manhã e lanche','recipeCuisine':'Brasileira','keywords':'panqueca de pera e aveia sem açúcar para bebê, panqueca para bebê, café da manhã bebê, lanche sem açúcar',
      'recipeYield':'6 panquecas pequenas','recipeIngredient':['1 pera pequena bem madura','1 ovo','4 colheres (sopa) de farinha de aveia'],
      'recipeInstructions':[{'@type':'HowToStep','text':'Rale ou amasse a pera madura.'},{'@type':'HowToStep','text':'Misture a pera com o ovo e a farinha de aveia até formar massa espessa.'},{'@type':'HowToStep','text':'Cozinhe pequenas porções em frigideira antiaderente em fogo baixo, virando para cozinhar os dois lados.'}]}
    sj=json.dumps(schema,ensure_ascii=False).replace('</','<\\/'); alt=html.escape(TITLE+' - Receitas Para Pequenos',quote=True)
    return f"""{MARKER}
<div class='separator' style='clear:both;margin:0 0 24px;text-align:center'><img alt='{alt}' data-original-height='630' data-original-width='1200' src='{cover_url}' style='border-radius:14px;height:auto;max-width:100%;width:1200px'/></div>
<p><strong>Por Equipe Editorial do Receitas Para Pequenos</strong></p>
<p>Esta panqueca de pera e aveia é uma opção simples para variar o café da manhã ou o lanche sem adicionar açúcar. A pera madura ajuda a deixar a massa úmida e macia, enquanto a aveia dá estrutura para formar panquecas pequenas.</p>
<p><strong>Atenção:</strong> adapte tamanho, formato e textura às habilidades individuais da criança e ofereça sempre com ela sentada e supervisionada. Em caso de alergias, dificuldades de mastigação/deglutição ou necessidades especiais, procure orientação de profissional habilitado.</p>
<h2>Ingredientes</h2><ul><li>1 pera pequena bem madura</li><li>1 ovo</li><li>4 colheres (sopa) de farinha de aveia</li></ul>
<h2>Modo de preparo</h2><ol><li>Lave e descasque a pera. Rale no lado fino do ralador ou amasse muito bem com um garfo.</li><li>Misture a pera com o ovo.</li><li>Acrescente a farinha de aveia e mexa até obter uma massa espessa, mas ainda úmida. Se a pera estiver muito suculenta, espere um minuto para a aveia absorver parte da umidade antes de decidir se precisa de um pouco mais de farinha.</li><li>Aqueça uma frigideira antiaderente em fogo baixo. Coloque pequenas porções e espalhe levemente.</li><li>Cozinhe até a parte de cima começar a firmar e a base se soltar com facilidade. Vire e cozinhe o outro lado até não haver massa crua no centro.</li><li>Deixe amornar antes de servir.</li></ol>
<h2>Como deve ficar a textura</h2><p>A panqueca deve ficar macia, flexível e úmida por dentro, sem bordas duras ou crocantes. O Guia Alimentar para Crianças Brasileiras Menores de 2 Anos orienta que a consistência dos alimentos evolua gradualmente conforme as habilidades da criança, evitando preparações excessivamente líquidas.</p>
<h2>Como servir e adaptar</h2><p>Para a criança que já consegue pegar alimentos macios com as mãos, corte ou ofereça a panqueca em formato que seja fácil de segurar. Para quem ainda precisa de textura mais amassada, ela pode ser desmanchada com garfo. O formato deve acompanhar as habilidades individuais.</p>
<h2>Substituições culinárias</h2><p>Uma pera bem madura funciona melhor porque fornece umidade à massa. A farinha de aveia pode variar um pouco em quantidade conforme o tamanho e a suculência da fruta. Alterações relacionadas a ovo, aveia, alergias ou necessidades específicas devem ser discutidas com profissional habilitado.</p>
<h2>Armazenamento</h2><p>Para melhor textura, sirva logo após o preparo. Se houver sobra que não teve contato com a boca da criança, resfrie e mantenha sob refrigeração em recipiente fechado, seguindo boas práticas de conservação. Antes de servir novamente, confira cheiro, aparência e textura e descarte em caso de dúvida.</p>
<h2>Perguntas frequentes</h2>
<h3>Precisa colocar açúcar para a pera aparecer no sabor?</h3><p>Não. Use uma pera madura. O Ministério da Saúde orienta não oferecer açúcar nem preparações que contenham açúcar para crianças menores de 2 anos.</p>
<h3>Posso bater a massa no liquidificador?</h3><p>Não é necessário. Ralar ou amassar a pera deixa pequenos pedaços macios e permite controlar melhor a consistência da massa.</p>
<h3>Como saber se a panqueca não ficou seca?</h3><p>Ela deve dobrar ou ceder facilmente ao toque e permanecer úmida no centro, embora completamente cozida. Fogo baixo ajuda a cozinhar o interior sem endurecer a superfície.</p>
<h2>Receitas relacionadas</h2><ul><li><a href='https://www.receitasparapequenos.site/2026/08/panqueca-de-maca-e-canela-para-bebes.html'>Panqueca de Maçã e Canela para Bebês</a></li><li><a href='https://www.receitasparapequenos.site/2026/08/paozinho-caseiro-macio-sem-acucar-para.html'>Pãozinho Caseiro Macio sem Açúcar para Bebê</a></li><li><a href='https://www.receitasparapequenos.site/2026/07/panqueca-de-batata-doce-para-bebes.html'>Panqueca de Batata-Doce para Bebês</a></li></ul>
<h2>Referências oficiais</h2><ul><li><a href='https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-da-crianca/primeira-infancia/alimentacao-saudavel' rel='nofollow'>Ministério da Saúde — Alimentação saudável na primeira infância</a></li><li><a href='https://www.gov.br/saude/pt-br/composicao/saps/promocao-da-saude/guias-alimentares/publicacoes/guia_da_crianca_2019.pdf/view' rel='nofollow'>Ministério da Saúde — Guia Alimentar para Crianças Brasileiras Menores de 2 Anos</a></li></ul>
<script type='application/ld+json'>{sj}</script>"""

def main():
    tok=base['token'](); posts=base['list_posts'](tok)
    for p in posts:
        t=(p.get('title') or '').casefold()
        if t==TITLE.casefold() or ('panqueca' in t and 'pera' in t and 'aveia' in t):
            RESULT_PATH.write_text(f'outcome=skipped_duplicate\ntitle={p.get("title","")}\nurl={p.get("url","")}\n',encoding='utf-8'); base['git_commit_push']([RESULT_PATH],'Record duplicate prevention for pear oat pancake'); return
    suffix=hashlib.sha1(TITLE.encode()).hexdigest()[:10]; cp=COVER_DIR/f'{SLUG_KEY}-{suffix}.jpg'; cu=f'{RAW_BASE}/{cp.name}'
    if not cp.exists(): generate_cover(cp); base['git_commit_push']([cp],'Add unique AI food photo for pear oat pancake'); time.sleep(8)
    content=article_html(cu)
    if MARKER not in content or cu not in content: raise RuntimeError('cover marker verification failed before publish')
    created=base['api'](tok,'POST',f'/blogs/{BLOG_ID}/posts',{'isDraft':'false','fetchBody':'true'},{'kind':'blogger#post','blog':{'id':BLOG_ID},'title':TITLE,'content':content,'labels':['Alimentação complementar','Café da manhã','Lanche','Panqueca','Sem açúcar']})
    pid=str(created.get('id','')); url=created.get('url','')
    if not pid: raise RuntimeError('Blogger did not return post id')
    verified=base['api'](tok,'GET',f'/blogs/{BLOG_ID}/posts/{pid}',{'view':'ADMIN'}); vc=verified.get('content') or ''
    if MARKER not in vc or cu not in vc: raise RuntimeError('live Blogger post failed cover verification')
    log=base['load_log'](); log.append({'published_at':created.get('published'),'title':TITLE,'url':url,'post_id':pid,'cluster':CLUSTER,'keyword':KEYWORD,'cover_url':cu,'marker':MARKER}); LOG_PATH.write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    RESULT_PATH.write_text('outcome=success\n'+f'title={TITLE}\nurl={url}\npost_id={pid}\ncluster={CLUSTER}\ncover_url={cu}\nmarker_verified=true\n',encoding='utf-8'); base['git_commit_push']([LOG_PATH,RESULT_PATH],'Record published pear oat sugar-free pancake recipe')

if __name__=='__main__': main()
