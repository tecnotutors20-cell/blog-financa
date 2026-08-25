#!/usr/bin/env python3
import html as html_lib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup, Comment

BLOG_ID = '6682336557114829830'
EXPECTED_HOST = 'receitasparapequenos.site'
API_BASE = 'https://www.googleapis.com/blogger/v3'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
ROOT = Path(__file__).resolve().parents[1] if 'recipes-site' in str(Path(__file__)) else Path.cwd()
SNAPSHOT = Path('recipes-site/current_posts.json')
WRITE_DELAY = 3.2
MAX_RETRIES = 7
BRAND = 'Receitas Para Pequenos'
AUTHOR_URL = '/p/equipe-editorial.html'
MINISTRY_URL = 'https://www.gov.br/saude/pt-br/assuntos/saude-brasil/eu-quero-me-alimentar-melhor/noticias/2021/como-ter-uma-alimentacao-saudavel'
GUIDES_URL = 'https://www.gov.br/saude/pt-br/assuntos/saude-brasil/publicacoes-para-promocao-a-saude/guias-alimentares'

PAGES = {
'Sobre': '''<h2>Sobre o Receitas Para Pequenos</h2><p>O <strong>Receitas Para Pequenos</strong> é um portal editorial independente dedicado a receitas e conteúdos práticos para famílias que estão vivendo a fase da alimentação complementar e os primeiros anos da infância. A proposta é organizar receitas simples, explicar textura e preparo e ajudar o leitor a encontrar ideias de refeições, lanches e preparações sem depender de promessas nutricionais exageradas.</p><p>O site não substitui acompanhamento de pediatra, nutricionista ou outro profissional de saúde que conheça a criança. Alergias, dificuldades de mastigação ou deglutição, condições clínicas, restrições alimentares e dúvidas sobre desenvolvimento precisam de avaliação individual.</p><h2>Como produzimos as receitas</h2><p>Buscamos apresentar ingredientes, modo de preparo, ponto e textura, possibilidades de armazenamento e dúvidas frequentes. Quando o assunto envolve recomendações gerais de alimentação infantil ou segurança, priorizamos fontes públicas e primárias, como materiais do Ministério da Saúde e orientações de órgãos oficiais.</p><h2>Segurança e responsabilidade</h2><p>Não existe uma textura única adequada para todas as crianças. A forma de servir deve considerar desenvolvimento, habilidades orais, histórico alimentar e supervisão de um adulto. Também evitamos transformar um alimento isolado em promessa de prevenção, cura, aumento de imunidade ou ganho de desenvolvimento.</p><h2>Independência editorial</h2><p>O site poderá exibir publicidade ou links comerciais. Quando houver relação comercial relevante, ela deve ser apresentada de forma clara e não deve alterar os critérios de segurança, transparência e utilidade do conteúdo.</p><h2>Atualizações e correções</h2><p>Receitas e textos podem ser revisados para melhorar clareza, corrigir erros ou acompanhar orientações oficiais atualizadas. Consulte também nossa <a href='/p/politica-editorial.html'>Política Editorial</a> e o <a href='/p/aviso-sobre-alimentacao-e-saude.html'>Aviso sobre Alimentação e Saúde</a>.</p>''',
'Contato': '''<h2>Contato</h2><p>Este espaço é destinado a correções editoriais, sugestões de receitas, dúvidas sobre o funcionamento do site, solicitações relacionadas à privacidade e propostas comerciais compatíveis com nossa política editorial.</p><h2>Correções</h2><p>Ao apontar uma informação possivelmente incorreta ou desatualizada, informe o título da página, o trecho e, quando possível, uma fonte oficial que ajude na verificação.</p><h2>Segurança e dados pessoais</h2><p>Não envie em comentários dados médicos detalhados, documentos, senhas, informações bancárias ou dados pessoais de crianças. Questões individuais de saúde, alergia, crescimento, deglutição ou nutrição devem ser tratadas com profissional habilitado.</p><h2>Parcerias</h2><p>Propostas comerciais podem ser avaliadas, mas remuneração não garante publicação, recomendação positiva ou alteração de conclusão editorial. Conteúdo patrocinado deve ser identificado.</p><p>Enquanto um canal dedicado não estiver publicado nesta página, comentários nas próprias receitas podem ser usados para sugerir correções relacionadas ao conteúdo, sem incluir dados pessoais ou sensíveis.</p>''',
'Política de Privacidade': '''<h2>Política de Privacidade</h2><p>Esta política explica como o <strong>Receitas Para Pequenos</strong> pode tratar informações geradas durante a navegação.</p><h2>Dados técnicos</h2><p>Serviços de hospedagem, segurança, métricas e publicidade podem processar informações técnicas como endereço IP, navegador, dispositivo, páginas acessadas, data e horário, origem do acesso e identificadores necessários ao funcionamento e à medição do site.</p><h2>Cookies e tecnologias semelhantes</h2><p>Cookies e tecnologias semelhantes podem ser usados para funcionalidades, medição de audiência, segurança e, quando houver publicidade, seleção e mensuração de anúncios. O usuário pode gerenciar cookies nas configurações do navegador e nos mecanismos de consentimento disponibilizados quando aplicável.</p><h2>Google Analytics e Google AdSense</h2><p>O site poderá utilizar serviços do Google, incluindo ferramentas de métricas e o Google AdSense. Google e parceiros podem utilizar cookies e identificadores para fornecer e medir anúncios de acordo com suas políticas e com as escolhas de consentimento aplicáveis. Saiba mais em <a href='https://policies.google.com/technologies/ads?hl=pt-BR' rel='nofollow noopener' target='_blank'>Tecnologias usadas em publicidade pelo Google</a>.</p><h2>Links externos</h2><p>Podemos indicar páginas do Ministério da Saúde, órgãos públicos e outros serviços. Ao acessar um site externo, passam a valer as políticas daquele terceiro.</p><h2>Dados enviados voluntariamente</h2><p>Comentários ou futuros formulários podem receber nome e mensagem. Evite publicar informações pessoais ou de saúde de crianças. O site não precisa de dados clínicos para disponibilizar suas receitas.</p><h2>LGPD e direitos do usuário</h2><p>Quando aplicável, solicitações relacionadas a acesso, correção, eliminação, oposição ou esclarecimento sobre tratamento de dados poderão ser encaminhadas pelos canais indicados na página de Contato. Podemos solicitar informações mínimas para localizar o dado e verificar a legitimidade do pedido.</p><h2>Alterações</h2><p>Esta política pode ser atualizada para refletir mudanças de serviços, recursos ou legislação. A versão publicada nesta página é a vigente.</p>''',
'Termos de Uso': '''<h2>Termos de Uso</h2><p>Ao utilizar o <strong>Receitas Para Pequenos</strong>, o leitor concorda com estes termos e com as demais políticas do site.</p><h2>Finalidade informativa</h2><p>As receitas e textos têm finalidade educativa e informativa. Não constituem prescrição nutricional, orientação médica individual, diagnóstico ou tratamento.</p><h2>Responsabilidade no preparo</h2><p>O leitor é responsável por verificar validade e conservação dos ingredientes, higiene, cozimento completo quando necessário, possíveis alergênicos e adequação da textura às habilidades da criança. Crianças devem se alimentar sob supervisão de adulto responsável.</p><h2>Substituições e resultados</h2><p>Trocas de ingredientes podem alterar textura, tempo de preparo, sabor e presença de alergênicos. As fotos são ilustrativas e o resultado pode variar conforme ingredientes, utensílios e forno.</p><h2>Informações que mudam</h2><p>Orientações gerais e referências podem ser atualizadas. Quando o tema envolver saúde e segurança, consulte fontes oficiais e profissionais habilitados para situações individuais.</p><h2>Propriedade intelectual</h2><p>Textos, estrutura editorial e materiais originais do site não podem ser reproduzidos integralmente para fins comerciais sem autorização, salvo usos permitidos por lei.</p><h2>Publicidade e terceiros</h2><p>O site poderá exibir anúncios, links de afiliados ou conteúdo patrocinado. A presença de publicidade não representa garantia sobre produto ou serviço de terceiros.</p>''',
'Política Editorial': '''<h2>Política Editorial</h2><p>A Política Editorial do <strong>Receitas Para Pequenos</strong> define critérios para criação, revisão e atualização do conteúdo.</p><h2>1. Utilidade antes de volume</h2><p>Uma receita deve responder à intenção do leitor com ingredientes claros, preparo executável, informação de textura e orientações de armazenamento quando pertinentes. Evitamos publicar variações quase idênticas apenas para aumentar quantidade de páginas.</p><h2>2. Fontes primárias para orientações de saúde</h2><p>Quando uma afirmação depender de orientação geral de alimentação infantil, buscamos materiais oficiais, especialmente do Ministério da Saúde. Fontes secundárias podem complementar contexto, mas não substituem uma referência primária quando ela estiver disponível.</p><h2>3. Sem promessas médicas ou nutricionais</h2><p>Não atribuímos a uma receita capacidade de prevenir, tratar ou curar doenças. Também evitamos promessas sobre imunidade, crescimento ou desenvolvimento baseadas em um alimento isolado.</p><h2>4. Textura e segurança</h2><p>Idade cronológica, sozinha, não determina a forma ideal de servir. O conteúdo deve lembrar que textura, tamanho e consistência precisam ser adaptados às habilidades da criança, com supervisão.</p><h2>5. Alergênicos e substituições</h2><p>Trocas de ingredientes devem ser apresentadas com cautela, pois podem mudar alergênicos e comportamento culinário. Questões individuais de alergia ou restrição exigem orientação profissional.</p><h2>6. Imagens</h2><p>Buscamos usar imagens próprias, licenciadas ou com origem permitida, relacionadas à preparação. Imagens devem apoiar o conteúdo e não induzir o leitor a acreditar que um resultado visual é garantido.</p><h2>7. Correções</h2><p>Erros factuais confirmados devem ser corrigidos. Conteúdos podem ser atualizados para melhorar clareza, segurança ou referências.</p><h2>8. Uso de tecnologia e IA</h2><p>Ferramentas automatizadas podem auxiliar pesquisa, organização e revisão, mas não substituem verificação de informações relevantes. Conteúdo sobre saúde e segurança deve ser confrontado com fontes confiáveis antes da publicação.</p><h2>9. Publicidade</h2><p>Publicidade e relações comerciais devem permanecer distinguíveis do conteúdo editorial. Remuneração não determina conclusão ou recomendação.</p>''',
'Aviso sobre Alimentação e Saúde': '''<h2>Aviso sobre Alimentação e Saúde</h2><p>O conteúdo do <strong>Receitas Para Pequenos</strong> é educativo e não substitui avaliação individual de pediatra, nutricionista, fonoaudiólogo ou outro profissional habilitado.</p><h2>Alimentação complementar</h2><p>As receitas destinadas a bebês pressupõem que a criança já iniciou a alimentação complementar. A forma de servir deve ser adaptada às habilidades de mastigação e deglutição, ao histórico alimentar e à orientação profissional quando necessária.</p><h2>Alergias e restrições</h2><p>Ingredientes comuns como ovo, leite, trigo, peixe e oleaginosas podem ser alergênicos. Uma substituição culinária não equivale a uma orientação clínica. Famílias com histórico de alergia ou reação devem procurar assistência adequada.</p><h2>Engasgo e supervisão</h2><p>Formato, dureza e textura importam. Alimentos inadequados podem aumentar risco de engasgo. A criança deve estar em posição apropriada e acompanhada por adulto responsável durante a refeição.</p><h2>Conservação e higiene</h2><p>Tempo fora de refrigeração, cozimento, resfriamento, congelamento e reaquecimento influenciam segurança. Descarte alimentos com sinais de deterioração e use práticas adequadas de higiene.</p><h2>Fontes gerais</h2><p>Para orientações públicas sobre alimentação de crianças, consulte os <a href='https://www.gov.br/saude/pt-br/assuntos/saude-brasil/publicacoes-para-promocao-a-saude/guias-alimentares' rel='nofollow noopener' target='_blank'>Guias Alimentares do Ministério da Saúde</a>.</p>''',
'Equipe Editorial': '''<h2>Equipe Editorial</h2><p>Os conteúdos do <strong>Receitas Para Pequenos</strong> são organizados pela Equipe Editorial do site. O trabalho envolve seleção de pauta, estruturação de receita, revisão de clareza, verificação de referências e atualização de materiais.</p><h2>Como trabalhamos</h2><p>Receitas são revisadas para que ingredientes, preparo e textura sejam compreensíveis. Informações gerais sobre alimentação infantil e segurança são verificadas em fontes públicas e oficiais quando aplicável.</p><h2>Uso de ferramentas digitais</h2><p>Ferramentas de IA e automação podem auxiliar pesquisa, rascunho, organização e revisão. Elas não são tratadas como fonte de autoridade. Afirmações relevantes devem ser verificadas e não publicamos recomendações clínicas personalizadas.</p><h2>Correções</h2><p>Se uma informação estiver incorreta, ela pode ser revisada. Consulte nossa <a href='/p/politica-editorial.html'>Política Editorial</a> para entender os critérios.</p>'''
}


def env(name):
    v=os.environ.get(name,'').strip()
    if not v: raise RuntimeError(f'Variável obrigatória ausente: {name}')
    return v

def access_token():
    data=urllib.parse.urlencode({'client_id':env('GOOGLE_CLIENT_ID'),'client_secret':env('GOOGLE_CLIENT_SECRET'),'refresh_token':env('GOOGLE_REFRESH_TOKEN'),'grant_type':'refresh_token'}).encode()
    req=urllib.request.Request(TOKEN_URL,data=data,method='POST',headers={'Content-Type':'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)['access_token']

def api(token,method,path,params=None,body=None):
    url=API_BASE+path
    if params:url+='?'+urllib.parse.urlencode(params)
    data=None if body is None else json.dumps(body,ensure_ascii=False).encode('utf-8')
    for attempt in range(MAX_RETRIES+1):
        req=urllib.request.Request(url,data=data,method=method,headers={'Authorization':f'Bearer {token}','Accept':'application/json'})
        if body is not None:req.add_header('Content-Type','application/json; charset=utf-8')
        try:
            with urllib.request.urlopen(req,timeout=45) as r:
                raw=r.read(); out=json.loads(raw.decode()) if raw else {}
            if method in {'POST','PATCH','PUT','DELETE'}:time.sleep(WRITE_DELAY)
            return out
        except urllib.error.HTTPError as e:
            detail=e.read().decode('utf-8','replace')
            if e.code in {429,500,502,503,504} and attempt<MAX_RETRIES:
                wait=min(5*(2**attempt),60); print(f'API {e.code}; retry em {wait}s',file=sys.stderr); time.sleep(wait); continue
            raise RuntimeError(f'Blogger API {method} {path} falhou ({e.code}): {detail}') from e

def paginate(token,path,extra=None):
    out=[]; page=None
    while True:
        p={'maxResults':500,'fetchBodies':True,'view':'ADMIN'}
        if extra:p.update(extra)
        if page:p['pageToken']=page
        d=api(token,'GET',path,p); out+=d.get('items',[]); page=d.get('nextPageToken')
        if not page:return out

def norm(s):
    return re.sub(r'\s+',' ',(s or '').strip()).casefold()

def labels_for(title,content):
    t=(title+' '+BeautifulSoup(content,'html.parser').get_text(' ')).casefold()
    labels=[]
    if any(x in t for x in ['papinha','purê','pure','creme','sopa']): labels.append('Papinhas e Purês')
    if any(x in t for x in ['bolinho','pão','pao','panqueca','biscoito','omelete','blw','hambúrguer','hamburguer']): labels.append('Lanches e BLW')
    if any(x in t for x in ['frango','carne','peixe','lentilha','feijão','feijao','quinoa','risoto','strogonoff','escondidinho']): labels.append('Refeições')
    if 'sem açúcar' in t or 'sem acucar' in t: labels.append('Sem Açúcar')
    if not labels: labels.append('Receitas para Bebês')
    return list(dict.fromkeys(labels))[:4]

def clean_content(post, all_posts):
    title=post['title']; soup=BeautifulSoup(post.get('content') or '','html.parser')
    for c in soup.find_all(string=lambda x:isinstance(x,Comment)): c.extract()
    for bad in soup.find_all(['script','style']): bad.decompose()
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr in {'class','data-sourcepos','dir','style','data-testid'}: tag.attrs.pop(attr,None)
    for span in soup.find_all('span'): span.unwrap()
    # Remove duplicated recipe title inside body.
    for heading in soup.find_all(['h1','h2','h3'])[:2]:
        if norm(heading.get_text(' ',strip=True)) == norm(title): heading.decompose(); break
    # Replace rigid age claims with skill-based wording.
    for h in soup.find_all(['h2','h3']):
        if 'para que fase serve' in norm(h.get_text()):
            nxt=h.find_next_sibling(['p','div'])
            if nxt: nxt.clear(); nxt.append('Indicada para crianças que já iniciaram a alimentação complementar e conseguem lidar com a textura proposta. Adapte tamanho, maciez e forma de servir às habilidades da criança.')
    text=str(soup)
    text=re.sub(r'(?i)mais fácil de digerir para o bebê','uma alternativa sem fritura',text)
    text=re.sub(r'(?i)mais fácil de digerir','uma alternativa sem fritura',text)
    # Cover image normalization when present.
    first=soup.find('img')
    image_url=''
    if first:
        image_url=first.get('src') or first.get('data-src') or ''
        first['alt']=title
        first['loading']='eager'
        first['style']='display:block;height:auto;max-width:100%;width:100%;border-radius:12px'
        parent=first.parent
        if parent and parent.name=='a': parent['style']='display:block;margin:0 auto 24px'
    # Author and safety blocks.
    author=soup.new_tag('div'); author['style']='margin:0 0 20px;padding:12px 14px;border-left:4px solid #5f8f4e;background:#f6faf3'
    author.append(BeautifulSoup(f"<strong>Por <a href='{AUTHOR_URL}'>Equipe Editorial do Receitas Para Pequenos</a></strong><br/><small>Receita revisada com foco em clareza, preparo e segurança alimentar.</small>",'html.parser'))
    safety=soup.new_tag('div'); safety['style']='margin:18px 0;padding:14px;border-radius:10px;background:#fff8e8'
    safety.append(BeautifulSoup("<strong>Antes de servir:</strong> esta receita é para crianças que já iniciaram a alimentação complementar. Adapte textura, tamanho e consistência às habilidades da criança e aos ingredientes que ela já consome com segurança. Em caso de alergia, dificuldade de mastigação/deglutição ou necessidade específica, procure orientação profissional.",'html.parser'))
    soup.insert(0,safety); soup.insert(0,author)
    # Related posts, using simple shared tokens and labels.
    words={w for w in re.findall(r'[a-záàâãéêíóôõúç]{4,}',title.casefold()) if w not in {'para','bebês','bebes','com','sem','receita','saudável','saudavel'}}
    scored=[]
    for p in all_posts:
        if p['id']==post['id']:continue
        pw={w for w in re.findall(r'[a-záàâãéêíóôõúç]{4,}',p['title'].casefold())}
        score=len(words & pw)
        if score: scored.append((score,p))
    scored.sort(key=lambda x:(-x[0],x[1]['title']))
    related=[p for _,p in scored[:3]]
    if related:
        box=soup.new_tag('div'); box['class']='related-recipes'
        h=soup.new_tag('h2'); h.string='Veja também'; box.append(h)
        ul=soup.new_tag('ul')
        for p in related:
            li=soup.new_tag('li'); a=soup.new_tag('a',href=p['url']); a.string=p['title']; li.append(a); ul.append(li)
        box.append(ul); soup.append(box)
    # Official source / disclaimer.
    src=soup.new_tag('p'); src.append(BeautifulSoup(f"<small><strong>Referência geral:</strong> consulte os <a href='{GUIDES_URL}' rel='nofollow noopener' target='_blank'>Guias Alimentares do Ministério da Saúde</a>. O conteúdo deste site não substitui orientação individual de profissional de saúde.</small>",'html.parser'))
    soup.append(src)
    # Recipe structured data without invented nutrition/time fields.
    ingredients=[]; instructions=[]
    for h in soup.find_all(['h2','h3']):
        ht=norm(h.get_text())
        if ht=='ingredientes':
            ul=h.find_next_sibling(['ul','ol'])
            if ul: ingredients=[li.get_text(' ',strip=True) for li in ul.find_all('li',recursive=False)]
        if 'modo de preparo' in ht:
            ol=h.find_next_sibling(['ol','ul','p'])
            if ol:
                if ol.name in {'ol','ul'}: instructions=[li.get_text(' ',strip=True) for li in ol.find_all('li',recursive=False)]
                else: instructions=[ol.get_text(' ',strip=True)]
    ld={'@context':'https://schema.org','@type':'Recipe','name':title,'author':{'@type':'Organization','name':BRAND,'url':'https://www.receitasparapequenos.site/p/equipe-editorial.html'},'datePublished':post.get('published'),'dateModified':datetime.now(timezone.utc).isoformat(),'mainEntityOfPage':post['url']}
    if image_url: ld['image']=[image_url]
    if ingredients: ld['recipeIngredient']=ingredients
    if instructions: ld['recipeInstructions']=[{'@type':'HowToStep','text':x} for x in instructions]
    script=soup.new_tag('script',type='application/ld+json'); script.string=json.dumps(ld,ensure_ascii=False); soup.append(script)
    return str(soup), labels_for(title,str(soup))

def upsert_pages(token):
    current=paginate(token,f'/blogs/{BLOG_ID}/pages')
    by={norm(p.get('title')):p for p in current}
    for title,content in PAGES.items():
        payload={'title':title,'content':content}
        old=by.get(norm(title))
        if old:
            if (old.get('content') or '').strip()==content.strip(): print('Página já atualizada:',title); continue
            api(token,'PATCH',f"/blogs/{BLOG_ID}/pages/{old['id']}",{'publish':'true'},payload); print('Página atualizada:',title)
        else:
            api(token,'POST',f'/blogs/{BLOG_ID}/pages',{'isDraft':'false'},payload); print('Página criada:',title)

def update_posts(token):
    snapshot=json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    live=paginate(token,f'/blogs/{BLOG_ID}/posts',{'status':'LIVE'})
    live_by_path={urllib.parse.urlparse(p['url']).path:p for p in live}
    snap_by_path={urllib.parse.urlparse(p['url']).path:p for p in snapshot}
    if len(live_by_path)!=45 or len(snap_by_path)!=45: raise RuntimeError(f'Esperava 45 posts; live={len(live_by_path)} snapshot={len(snap_by_path)}')
    updated=0
    for path,source in snap_by_path.items():
        target=live_by_path.get(path)
        if not target: raise RuntimeError('URL não encontrada: '+path)
        content,labels=clean_content(source,snapshot)
        payload={'title':target['title'],'content':content,'labels':labels}
        # Snapshot is the fixed baseline; update in place, preserving title and permalink.
        api(token,'PATCH',f"/blogs/{BLOG_ID}/posts/{target['id']}",{'publish':'true','fetchBody':'false'},payload)
        updated+=1; print(f'Post {updated}/45 atualizado: {target["title"]}')
    return updated

def main():
    token=access_token(); blog=api(token,'GET',f'/blogs/{BLOG_ID}',{'view':'ADMIN'})
    if EXPECTED_HOST not in (blog.get('url') or ''): raise RuntimeError('Blog de destino inesperado: '+str(blog))
    print(f"Destino confirmado: {blog.get('name')} — {blog.get('url')}")
    upsert_pages(token)
    n=update_posts(token)
    Path('recipes-site/publish-result.txt').write_text(f'outcome=success\nblog_id={BLOG_ID}\nposts_updated={n}\npages_target={len(PAGES)}\n',encoding='utf-8')
    print('Publicação concluída.')

if __name__=='__main__':
    try: main()
    except Exception as exc:
        Path('recipes-site/publish-result.txt').write_text('outcome=failed\nerror='+str(exc).replace('\n',' ')+'\n',encoding='utf-8')
        print(exc,file=sys.stderr); sys.exit(1)
