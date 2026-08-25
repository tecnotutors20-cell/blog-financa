#!/usr/bin/env python3
import concurrent.futures
import hashlib
import importlib.util
import os
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STATUS=ROOT/'recipes-site'/'ai-cover-v2-final.txt'

spec=importlib.util.spec_from_file_location('m', ROOT/'recipes-site'/'migrate_recipe_covers_v2.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def git(*args):
    return subprocess.run(['git',*args],cwd=ROOT,text=True,capture_output=True)


def filename_for(p):
    pid=str(p['id']); title=p.get('title') or 'Receita para pequenos'
    suffix=hashlib.sha1(title.encode()).hexdigest()[:8]
    return m.COVER_DIR/f'{pid}-{suffix}.jpg'


def url_for(p):
    return f"{m.RAW_BASE}/{filename_for(p).name}"


def generate_missing(posts):
    missing=[p for p in posts if not filename_for(p).exists()]
    failures=[]
    # Deliberately conservative concurrency to avoid upstream 429s.
    def one(p):
        pid=str(p['id']); title=p.get('title') or 'Receita para pequenos'; path=filename_for(p)
        m.make_image(title,pid,path)
        time.sleep(4)
        return pid
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futs={pool.submit(one,p):p for p in missing}
        for f in concurrent.futures.as_completed(futs):
            p=futs[f]
            try: f.result()
            except Exception as e: failures.append(f"{p.get('id')}|{p.get('title')}|{type(e).__name__}:{e}")
    return len(missing)-len(failures), failures


def commit_images():
    git('config','user.name','github-actions[bot]'); git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
    git('add','assets/recipes-covers-ai-v2')
    git('commit','-m','Complete remaining recipe-specific AI food covers')
    r=git('pull','--rebase','origin','main')
    if r.returncode!=0: raise RuntimeError('pull failed: '+r.stderr)
    r=git('push','origin','main')
    if r.returncode!=0: raise RuntimeError('push failed: '+r.stderr)


def sync_posts(tok,posts):
    failures=[]; updated=0; already=0
    for p in posts:
        try:
            pid=str(p['id']); title=p.get('title') or 'Receita para pequenos'; content=p.get('content') or ''; url=url_for(p)
            if m.MARKER in content and url in content:
                already+=1; continue
            if not filename_for(p).exists():
                raise RuntimeError('cover file missing')
            new_content=m.cover_block(title,url)+m.clean_old_cover(content)
            m.api(tok,'PATCH',f'/blogs/{m.BLOG_ID}/posts/{pid}',{'publish':'true'},{'title':title,'content':new_content,'labels':p.get('labels') or []})
            updated+=1
            time.sleep(1.3)
        except Exception as e:
            failures.append(f"{p.get('id')}|{p.get('title')}|{type(e).__name__}:{e}")
    return updated,already,failures


def verify(tok):
    live=m.posts(tok); ok=[]; bad=[]
    for p in live:
        content=p.get('content') or ''; expected=url_for(p)
        if m.MARKER in content and expected in content:
            ok.append(str(p['id']))
        else:
            bad.append(f"{p.get('id')}|{p.get('title')}")
    return len(live),len(ok),bad


def save_status(lines):
    STATUS.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    git('add',str(STATUS.relative_to(ROOT)))
    git('commit','-m','Verify all recipe-specific AI covers in Blogger')
    git('pull','--rebase','origin','main')
    git('push','origin','main')


def main():
    tok=m.token(); live=m.posts(tok)
    generated,gen_failures=generate_missing(live)
    if gen_failures:
        save_status(['outcome=failed','phase=generation',f'total={len(live)}',f'generated_now={generated}',f'failures={len(gen_failures)}']+['failure='+x for x in gen_failures])
        raise SystemExit(1)
    commit_images()
    time.sleep(8)
    # Refetch so we never overwrite newer Blogger content with stale bodies.
    live=m.posts(tok)
    updated,already,sync_failures=sync_posts(tok,live)
    total,verified,bad=verify(tok)
    outcome='success' if not sync_failures and not bad and verified==total else 'failed'
    lines=[f'outcome={outcome}',f'total={total}',f'generated_now={generated}',f'updated_now={updated}',f'already_v2={already}',f'verified_v2={verified}',f'failures={len(sync_failures)+len(bad)}']
    lines += ['sync_failure='+x for x in sync_failures]
    lines += ['verification_failure='+x for x in bad]
    save_status(lines)
    if outcome!='success': raise SystemExit(1)

if __name__=='__main__': main()
