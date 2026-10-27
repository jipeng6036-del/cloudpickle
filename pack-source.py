import hashlib,io,json,pathlib,subprocess,tarfile
repo=pathlib.Path('F:/Github-PR/inspection/oct27-ai-cloudpickle509');out=pathlib.Path('F:/Github-PR/ci-evidence/discovery-20261027-ai')
def git(*args): return subprocess.check_output(['git',*args],cwd=repo)
head=git('rev-parse','HEAD').decode().strip();tree=git('write-tree').decode().strip();mtime=int(git('show','-s','--format=%ct','HEAD').decode().strip())
def entries(ref):
 rows={}
 for entry in git('ls-tree','-rz',ref).split(b'\0'):
  if not entry:continue
  meta,path=entry.split(b'\t',1);mode,kind,oid=meta.split();assert kind==b'blob';rows[path.decode()]=(mode.decode(),oid.decode())
 return rows
candidate=entries(tree);base=entries(head);base['tests/cloudpickle_test.py']=candidate['tests/cloudpickle_test.py']
for label,rows in [('candidate',candidate),('base-with-regressions',base)]:
 manifest=[]
 with tarfile.open(out/(label+'.tar'),'w') as tar:
  for path,(mode,oid) in rows.items():
   raw=git('cat-file','blob',oid);assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==oid
   item=tarfile.TarInfo(path);item.mode=int(mode,8)&0o777;item.mtime=mtime
   if mode=='120000':item.type=tarfile.SYMTYPE;item.linkname=raw.decode()
   else:item.size=len(raw)
   tar.addfile(item,None if mode=='120000' else io.BytesIO(raw));manifest.append({'path':path,'mode':mode,'blob':oid,'sha256':hashlib.sha256(raw).hexdigest()})
 (out/(label+'-manifest.json')).write_text(json.dumps(manifest,indent=2),encoding='utf8')
 print(label,len(manifest))
(out/'FROZEN-SOURCE.json').write_text(json.dumps({'base':head,'candidateTree':tree,'modifiedPaths':[p for p in candidate if candidate[p]!=entries(head)[p]],'regressionFile':candidate['tests/cloudpickle_test.py'][1]},indent=2),encoding='utf8')
