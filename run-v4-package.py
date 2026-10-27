from pathlib import Path
import subprocess,json,zipfile,hashlib
root=Path('F:/Github-PR');out=root/'ci-evidence/discovery-20261027-ai';repo=root/'inspection/oct27-ai-cloudpickle509';py=out/'venvs/wheel/Scripts/python.exe';wheel=out/'dist-v4/cloudpickle-3.2.0.dev0-py3-none-any.whl';rows=[]
steps=[('export',['E:/Python/Python311/python.exe',str(out/'export-package-source.py')]),('build',['uv','build','--directory',str(out/'canonical-package-source'),'--out-dir',str(out/'dist-v4')]),('install',['uv','pip','install','--force-reinstall','--python',str(py),str(wheel)]),('consumer',[str(py),str(out/'contextmanager-runtime.py'),str(out/'venvs/wheel/Lib/site-packages'),str(out/'v4-runtime-wheel-py311')])]
for label,cmd in steps:
 with (out/('v4-package-'+label+'.log')).open('wb') as log:result=subprocess.run(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=180)
 rows.append({'step':label,'exit':result.returncode});assert result.returncode==0,(label,result.returncode)
source=[]
with zipfile.ZipFile(wheel) as z:
 for name in z.namelist():
  if name.startswith('cloudpickle/') and name.endswith('.py'):
   b=z.read(name);gitblob=subprocess.check_output(['git','cat-file','blob',':'+name],cwd=repo);installed=(out/'venvs/wheel/Lib/site-packages'/name).read_bytes();assert b==gitblob==installed,name;source.append({'path':name,'sha256':hashlib.sha256(b).hexdigest(),'matchesGitAndInstalled':True})
record={'steps':rows,'wheelSha256':hashlib.sha256(wheel.read_bytes()).hexdigest(),'sdistSha256':hashlib.sha256(next((out/'dist-v4').glob('*.tar.gz')).read_bytes()).hexdigest(),'packagedSources':source};(out/'V4-PACKAGE.json').write_text(json.dumps(record,indent=2),encoding='utf8');print(record)
