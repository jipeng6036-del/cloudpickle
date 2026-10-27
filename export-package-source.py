from pathlib import Path
import hashlib,json,subprocess
repo=Path('F:/Github-PR/inspection/oct27-ai-cloudpickle509');out=Path('F:/Github-PR/ci-evidence/discovery-20261027-ai');target=out/'canonical-package-source';target.mkdir(exist_ok=True)
raw=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=repo);entries=[]
for row in raw.split(b'\0'):
 if not row:continue
 meta,path=row.split(b'\t',1);mode,oid,stage=meta.split();assert stage==b'0';assert mode in [b'100644',b'100755'];entries.append((path.decode(),mode.decode(),oid.decode()))
data=subprocess.run(['git','cat-file','--batch'],cwd=repo,input=('\n'.join(row[2] for row in entries)+'\n').encode(),capture_output=True,check=True).stdout
pos=0;manifest=[]
for path,mode,oid in entries:
 eol=data.index(b'\n',pos);header=data[pos:eol].split();size=int(header[2]);blob=data[eol+1:eol+1+size];pos=eol+size+2
 assert hashlib.sha1(b'blob '+str(size).encode()+b'\0'+blob).hexdigest()==oid
 f=target/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(blob);assert f.read_bytes()==blob
 manifest.append({'path':path,'mode':mode,'blob':oid,'sha256':hashlib.sha256(blob).hexdigest()})
old={r['path']:r for r in json.loads((out/'full-gates-v1-candidate-manifest.json').read_text())};delta=[r['path'] for r in manifest if r['blob']!=old[r['path']]['blob']];assert delta==['CHANGES.md','cloudpickle/cloudpickle.py','tests/cloudpickle_test.py'],delta
(out/'canonical-package-manifest.json').write_text(json.dumps({'finalTree':subprocess.check_output(['git','write-tree'],cwd=repo).decode().strip(),'changesFromTestedTree':delta,'files':manifest},indent=2),encoding='utf8');print('canonical files',len(manifest),'delta',delta)
