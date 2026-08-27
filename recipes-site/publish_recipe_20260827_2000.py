#!/usr/bin/env python3
import hashlib, html, io, json, runpy, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

base = runpy.run_path(str(Path(__file__).with_name('publish_recipe_20260825_1000.py')), run_name='recipe_base')
TITLE = 'Muffin de Maçã e Aveia sem Açúcar para Bebê: Receita Macia'
SLUG_KEY = 'muffin-maca-aveia-sem-acucar-bebe'
CLUSTER = 'Cluster 3 — Café da manhã e lanches sem açúcar'
KEYWORD = 'muffin de maçã e aveia sem açúcar para bebê'
MARKER=base['MARKER']; BLOG_ID=base['BLOG_ID']; COVER_DIR=base['COVER_DIR']; RAW_BASE=base['RAW_BASE']; LOG_PATH=base['LOG_PATH']; RESULT_PATH=base['RESULT_PATH']
W,H=1200,630

def generate_cover(path):
    prompt=("Photorealistic horizontal food photograph for a Brazilian baby-friendly recipe titled 'Muffin de Maçã e Aveia sem Açúcar para Bebê'. "
            "Show five small homemade oat and apple muffins, softly domed and pale golden, in simple paper liners on a light ceramic plate; one muffin cut open to reveal moist apple pieces and tender crumb. "
            "Add a few fresh red apple slices and a small scattering of rolled oats as ingredient cues. Warm evening natural window light, light wood table, neutral linen, realistic home food photography, close three-quarter view, natural imperfections. "
            "No frosting, syrup, honey, sugar, powdered sugar, chocolate, candy or sweet topping. No baby, child, people or hands. No text, logo, watermark, packaging, labels, collage, illustration or cartoon.")
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
      'description':'Muffin macio de maçã e aveia, sem açúcar adicionado, para variar o café da manhã ou o lanche durante a alimentação complementar.',
      'recipeCategory':'Café da manhã e lanche','recipeCuisine':'Brasileira','keywords':'muffin de maçã e aveia sem açúcar para bebê, muffin para bebê, lanche sem açúcar, café da manhã bebê',
      'recipeYield':'6 muffins pequenos','recipeIngredient':['1 maçã pequena ralada','1 ovo','5 colheres (sopa) de farinha de aveia','2 colheres (sopa) de água','1/2 colher (chá) de fermento químico em pó'],
      'recipeInstructions':[{'@type':'HowToStep','text':'Misture a maçã ralada, o ovo e a água.'},{'@type':'HowToStep','text':'Junte a farinha de aveia e, por último, o fermento.'},{'@type':'HowToStep','text':'Distribua em forminhas pequenas e asse até firmar e cozinhar completamente o centro.'}]}
    sj=json.dumps(schema,ensure_ascii=False).replace('</','<\\/'); alt=html.escape(TITLE+' - Receitas Para Pequenos',quote=True)
    return f"""{MARKER}
<div class='separator' style='clear:both;margin:0 0 24px;text-align:center'><img alt='{alt}' data-original-height='630' data-original-width='1200' src='{cover_url}' style='border-radius:14px;height:auto;max-width:100%;width:1200px'/></div>
<p><strong>Por Equipe Editorial do Receitas Para Pequenos</strong></p>
<p>Este muffin de maçã e aveia é uma alternativa assada para variar o café da manhã ou o lanche sem adicionar açúcar. A maçã ralada deixa a massa úmida e macia, e a receita usa poucos ingredientes do dia a dia.</p>
<p><strong>Atenção:</strong> adapte tamanho, formato e textura às habilidades da criança e ofereça sempre com ela sentada e supervisionada. Em caso de alergias, dificuldades de mastigação/deglutição ou necessidades especiais, procure orientação de profissional habilitado.</p>
<h2>Ingredientes</h2><ul><li>1 maçã pequena, lavada, descascada e ralada fina</li><li>1 ovo</li><li>5 colheres (sopa) de farinha de aveia</li><li>2 colheres (sopa) de água</li><li>1/2 colher (chá) de fermento químico em pó</li></ul>
<h2>Modo de preparo</h2><ol><li>Preaqueça o forno a 180 °C e separe 6 forminhas pequenas de muffin.</li><li>Misture a maçã ralada, o ovo e a água até ficar uniforme.</li><li>Acrescente a farinha de aveia e mexa até formar uma massa espessa e úmida.</li><li>Junte o fermento por último e misture apenas o suficiente para incorporar.</li><li>Distribua a massa nas forminhas, sem encher até a borda.</li><li>Asse até os muffins estarem firmes e completamente cozidos no centro. Faça o teste com um palito e deixe amornar antes de servir.</li></ol>
<h2>Como deve ficar a textura</h2><p>O interior deve ficar macio e úmido, sem partes de massa crua e sem formar uma crosta dura. O Guia Alimentar para Crianças Brasileiras Menores de 2 Anos orienta que a consistência dos alimentos evolua gradualmente conforme as habilidades da criança.</p>
<h2>Como servir e adaptar</h2><p>Para a criança que já pega alimentos macios com as mãos, ofereça o muffin em um formato fácil de segurar ou corte em pedaços adequados às habilidades dela. Para quem ainda precisa de textura mais amassada, desmanche o muffin com um garfo antes de oferecer.</p>
<h2>Por que não leva açúcar?</h2><p>A maçã madura fornece sabor naturalmente adocicado. O Ministério da Saúde orienta não oferecer açúcar nem preparações que contenham açúcar para crianças menores de 2 anos.</p>
<h2>Substituições culinárias</h2><p>Uma maçã mais madura e suculenta tende a deixar o muffin mais úmido. Se a massa ficar excessivamente líquida, acrescente uma pequena quantidade de farinha de aveia. Alterações relacionadas a ovo, aveia, alergias ou necessidades específicas devem ser discutidas com profissional habilitado.</p>
<h2>Armazenamento</h2><p>Para melhor textura, consuma depois que esfriar ou mantenha sob refrigeração em recipiente fechado caso sobre uma porção que não teve contato com a boca da criança. Reaqueça apenas o necessário e descarte se houver mudança de cheiro, aparência ou textura.</p>
<h2>Perguntas frequentes</h2>
<h3>Precisa usar açúcar ou adoçante?</h3><p>Não. A receita foi pensada para usar apenas o sabor da maçã. Para menores de 2 anos, o Ministério da Saúde recomenda não oferecer açúcar nem preparações açucaradas.</p>
<h3>Posso usar aveia em flocos no lugar da farinha?</h3><p>Pode triturar aveia em flocos até obter uma farinha caseira. A textura pode variar um pouco, então observe a consistência da massa antes de assar.</p>
<h3>Como evitar que o muffin fique seco?</h3><p>Use maçã bem madura, não aumente demais a quantidade de farinha e retire do forno assim que o centro estiver cozido. O interior deve continuar macio depois de esfriar.</p>
<h2>Receitas relacionadas</h2><ul><li><a href='https://www.receitasparapequenos.site/2026/08/panqueca-de-pera-e-aveia-sem-acucar.html'>Panqueca de Pera e Aveia sem Açúcar para Bebê</a></li><li><a href='https://www.receitasparapequenos.site/2026/08/panqueca-de-maca-e-canela-para-bebes.html'>Panqueca de Maçã e Canela para Bebês</a></li><li><a href='https://www.receitasparapequenos.site/2026/08/paozinho-caseiro-macio-sem-acucar-para.html'>Pãozinho Caseiro Macio sem Açúcar para Bebê</a></li></ul>
<h2>Referências oficiais</h2><ul><li><a href='https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-da-crianca/primeira-infancia/alimentacao-saudavel' rel='nofollow'>Ministério da Saúde — Alimentação saudável na primeira infância</a></li><li><a href='https://www.gov.br/saude/pt-br/composicao/saps/promocao-da-saude/guias-alimentares/publicacoes/guia_da_crianca_2019.pdf/view' rel='nofollow'>Ministério da Saúde — Guia Alimentar para Crianças Brasileiras Menores de 2 Anos</a></li></ul>
<script type='application/ld+json'>{sj}</script>"""

def main():
    tok=base['token'](); posts=base['list_posts'](tok)
    for p in posts:
        t=(p.get('title') or '').casefold()
        if t==TITLE.casefold() or ('muffin' in t and 'maçã' in t and 'aveia' in t):
            RESULT_PATH.write_text(f'outcome=skipped_duplicate\ntitle={p.get("title","")}\nurl={p.get("url","")}\n',encoding='utf-8'); base['git_commit_push']([RESULT_PATH],'Record duplicate prevention for apple oat muffin'); return
    suffix=hashlib.sha1(TITLE.encode()).hexdigest()[:10]; cp=COVER_DIR/f'{SLUG_KEY}-{suffix}.jpg'; cu=f'{RAW_BASE}/{cp.name}'
    if not cp.exists(): generate_cover(cp); base['git_commit_push']([cp],'Add unique AI food photo for apple oat muffin'); time.sleep(8)
    content=article_html(cu)
    if MARKER not in content or cu not in content: raise RuntimeError('cover marker verification failed before publish')
    created=base['api'](tok,'POST',f'/blogs/{BLOG_ID}/posts',{'isDraft':'false','fetchBody':'true'},{'kind':'blogger#post','blog':{'id':BLOG_ID},'title':TITLE,'content':content,'labels':['Alimentação complementar','Café da manhã','Lanche','Muffin','Sem açúcar']})
    pid=str(created.get('id','')); url=created.get('url','')
    if not pid: raise RuntimeError('Blogger did not return post id')
    verified=base['api'](tok,'GET',f'/blogs/{BLOG_ID}/posts/{pid}',{'view':'ADMIN'}); vc=verified.get('content') or ''
    if MARKER not in vc or cu not in vc: raise RuntimeError('live Blogger post failed cover verification')
    log=base['load_log'](); log.append({'published_at':created.get('published'),'title':TITLE,'url':url,'post_id':pid,'cluster':CLUSTER,'keyword':KEYWORD,'cover_url':cu,'marker':MARKER}); LOG_PATH.write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    RESULT_PATH.write_text('outcome=success\n'+f'title={TITLE}\nurl={url}\npost_id={pid}\ncluster={CLUSTER}\ncover_url={cu}\nmarker_verified=true\n',encoding='utf-8'); base['git_commit_push']([LOG_PATH,RESULT_PATH],'Record published apple oat sugar-free muffin recipe')

if __name__=='__main__': main()
