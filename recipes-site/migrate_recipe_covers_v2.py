#!/usr/bin/env python3
import hashlib
import html
import io
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image

BLOG_ID='6682336557114829830'
API='https://www.googleapis.com/blogger/v3'
TOKEN_URL='https://oauth2.googleapis.com/token'
ROOT=Path(__file__).resolve().parents[1]
COVER_DIR=ROOT/'assets'/'recipes-covers-ai-v2'
RESULT=ROOT/'recipes-site'/'ai-cover-v2-result.txt'
RAW_BASE='https://raw.githubusercontent.com/tecnotutors20-cell/blog-financa/main/assets/recipes-covers-ai-v2'
MARKER='<!-- receitas-para-pequenos-ai-v2 -->'
OLD_MARKERS=['<!-- receitas-para-pequenos-cover -->','<!-- receitas-para-pequenos-ai-cover -->']
W,H=1200,630

SCENES=[
 'bright Brazilian home kitchen, pale wood table, soft morning window light',
 'minimal cream tabletop, natural side light, linen napkin, cozy home food styling',
 'light oak dining table, soft afternoon window light, neutral ceramic tableware',
 'clean white stone countertop, airy daylight, subtle kitchen background blur',
 'warm beige table, diffused window light, understated family kitchen',
 'rustic light wood table, natural daylight, handmade neutral ceramic plate',
 'simple modern kitchen island, soft daylight, clean editorial food photography',
 'small family dining table, warm natural light, casual homemade presentation'
]
ANGLES=['overhead food photography','45-degree close-up food photography','three-quarter editorial food photography','natural table-level close-up food photography']
PLATES=['small matte ceramic plate','small shallow stoneware bowl','simple child-sized neutral plate','small handmade ceramic bowl']


def env(name):
    v=os.environ.get(name,'').strip()
    if not v: raise RuntimeError('missing '+name)
    return v

def token():
    data=urllib.parse.urlencode({'client_id':env('GOOGLE_CLIENT_ID'),'client_secret':env('GOOGLE_CLIENT_SECRET'),'refresh_token':env('GOOGLE_REFRESH_TOKEN'),'grant_type':'refresh_token'}).encode()
    req=urllib.request.Request(TOKEN_URL,data=data,method='POST'); req.add_header('Content-Type','application/x-www-form-urlencoded')
    with urllib.request.urlopen(req,timeout=30) as r: return json.load(r)['access_token']

def api(tok,method,path,params=None,body=None):
    url=API+path
    if params: url+='?'+urllib.parse.urlencode(params)
    data=None if body is None else json.dumps(body,ensure_ascii=False).encode('utf-8')
    for attempt in range(6):
        req=urllib.request.Request(url,data=data,method=method)
        req.add_header('Authorization','Bearer '+tok); req.add_header('Accept','application/json')
        if body is not None: req.add_header('Content-Type','application/json; charset=utf-8')
        try:
            with urllib.request.urlopen(req,timeout=60) as r:
                raw=r.read(); return json.loads(raw.decode()) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code in {429,500,502,503,504} and attempt<5:
                time.sleep(min(5*(2**attempt),45)); continue
            raise

def posts(tok):
    out=[]; page=None
    while True:
        p={'maxResults':500,'fetchBodies':True,'status':'LIVE','view':'ADMIN'}
        if page: p['pageToken']=page
        d=api(tok,'GET',f'/blogs/{BLOG_ID}/posts',p); out+=d.get('items',[]); page=d.get('nextPageToken')
        if not page: return out

def prompt_for(title,post_id,attempt):
    d=hashlib.sha256((post_id+title).encode()).digest()
    scene=SCENES[d[0]%len(SCENES)]; angle=ANGLES[d[1]%len(ANGLES)]; plate=PLATES[d[2]%len(PLATES)]
    return (
      "Photorealistic horizontal food photograph of the FINISHED Brazilian recipe described by this exact title: '"+title+"'. "
      "The cooked dish must clearly match the title and visible main ingredients. Homemade, believable, appetizing, realistic texture, not luxury restaurant plating. "
      "Baby/toddler friendly serving style when relevant, but absolutely no baby, no child, no people, no hands. "
      f"Serve on a {plate}. Camera: {angle}. Setting: {scene}. Variation {attempt+1}. "
      "Natural food colors, realistic crumbs and imperfections, professional recipe blog photography. "
      "No text, no typography, no logo, no watermark, no packaging, no labels, no collage, no illustration, no cartoon."
    )

def image_url(title,post_id,attempt):
    q=urllib.parse.quote(prompt_for(title,post_id,attempt),safe='')
    seed=(int(hashlib.sha256((title+post_id).encode()).hexdigest()[:12],16)+attempt*10007)%2147483647
    return f'https://image.pollinations.ai/prompt/{q}?width={W}&height={H}&model=flux&nologo=true&safe=true&enhance=true&seed={seed}'

def make_image(title,post_id,path):
    last=None
    for attempt in range(7):
        try:
            req=urllib.request.Request(image_url(title,post_id,attempt),headers={'User-Agent':'Mozilla/5.0 (compatible; ReceitasParaPequenos/2.0)','Accept':'image/*'})
            with urllib.request.urlopen(req,timeout=240) as r: raw=r.read()
            if len(raw)<15000: raise RuntimeError('small response '+str(len(raw)))
            im=Image.open(io.BytesIO(raw)).convert('RGB')
            if im.width<700 or im.height<350: raise RuntimeError('bad dimensions '+str(im.size))
            tr=W/H; r=im.width/im.height
            if r>tr:
                nw=int(im.height*tr); x=(im.width-nw)//2; im=im.crop((x,0,x+nw,im.height))
            elif r<tr:
                nh=int(im.width/tr); y=(im.height-nh)//2; im=im.crop((0,y,im.width,y+nh))
            im=im.resize((W,H),Image.Resampling.LANCZOS)
            path.parent.mkdir(parents=True,exist_ok=True); im.save(path,'JPEG',quality=92,optimize=True,progressive=True)
            return
        except Exception as e:
            last=e; time.sleep(min(8*(attempt+1),40))
    raise RuntimeError(str(last))

def clean_old_cover(content):
    text=content or ''
    markers=[MARKER]+OLD_MARKERS
    for m in markers:
        text=re.sub(re.escape(m)+r"\s*<div[^>]*class=['\"]separator['\"][^>]*>.*?</div>",'',text,count=1,flags=re.I|re.S)
    return text.lstrip()

def cover_block(title,url):
    alt=html.escape(title+' - Receitas Para Pequenos',quote=True)
    return MARKER+"<div class='separator' style='clear:both;margin:0 0 24px;text-align:center'>"+f"<img alt='{alt}' data-original-height='630' data-original-width='1200' src='{url}' style='border-radius:14px;height:auto;max-width:100%;width:1200px'/>"+"</div>"

def git(*args):
    return subprocess.run(['git',*args],cwd=ROOT,text=True,capture_output=True)

def commit_image(path,title,index,total):
    git('config','user.name','github-actions[bot]'); git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
    git('add',str(path.relative_to(ROOT)))
    r=git('commit','-m',f'AI recipe cover {index}/{total}: {title[:70]}')
    if r.returncode not in (0,1): raise RuntimeError(r.stderr)
    pull=git('pull','--rebase','origin','main')
    if pull.returncode!=0: raise RuntimeError(pull.stderr)
    push=git('push','origin','main')
    if push.returncode!=0: raise RuntimeError(push.stderr)

def write_status(done,total,failures):
    RESULT.write_text(f'completed={done}\ntotal={total}\nfailures={len(failures)}\n'+''.join('failure='+x+'\n' for x in failures),encoding='utf-8')
    git('add',str(RESULT.relative_to(ROOT))); git('commit','-m',f'Record AI cover migration progress {done}/{total}'); git('pull','--rebase','origin','main'); git('push','origin','main')

def main():
    tok=token(); items=posts(tok); total=len(items); done=0; failures=[]
    for index,p in enumerate(items,1):
        post_id=str(p['id']); title=p.get('title') or 'Receita para pequenos'; content=p.get('content') or ''
        suffix=hashlib.sha1(title.encode()).hexdigest()[:8]; path=COVER_DIR/f'{post_id}-{suffix}.jpg'; url=f'{RAW_BASE}/{path.name}'
        try:
            if MARKER in content and url in content and path.exists():
                done+=1; continue
            if not path.exists():
                make_image(title,post_id,path); commit_image(path,title,index,total); time.sleep(5)
            new_content=cover_block(title,url)+clean_old_cover(content)
            api(tok,'PATCH',f'/blogs/{BLOG_ID}/posts/{post_id}',{'publish':'true'},{'title':title,'content':new_content,'labels':p.get('labels') or []})
            done+=1
            if done%5==0: write_status(done,total,failures)
            time.sleep(2)
        except Exception as e:
            failures.append(f'{post_id}|{title}|{type(e).__name__}:{e}')
            write_status(done,total,failures)
    write_status(done,total,failures)
    if failures or done!=total: raise SystemExit(1)

if __name__=='__main__': main()
