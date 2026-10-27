from pathlib import Path
import json,os,subprocess,hashlib
out=Path('F:/Github-PR/ci-evidence/discovery-20261027-ai');repo=Path('F:/Github-PR/inspection/oct27-ai-cloudpickle509');base=repo.parent/'oct27-ai-cloudpickle509-base';rows=[]
for label in ['310','311','312','313','314']:
 py=repo/'.venv/Scripts/python.exe' if label=='311' else out/'venvs'/('cp'+label)/'Scripts/python.exe'
 for kind,cwd in [('base',base),('candidate',repo)]:
  env=dict(os.environ,PYTHONPATH=str(cwd)+os.pathsep+str(cwd/'tests'));name='v5-final-win'+label+'-'+kind+'-target'
  with (out/(name+'.log')).open('wb') as log:r=subprocess.run([str(py),'-m','pytest','tests/cloudpickle_test.py','-k','contextmanager or generators_remain','-q','--junitxml='+str(out/(name+'.xml'))],cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
  rows.append({'version':label,'kind':kind,'exit':r.returncode,'testSha256':hashlib.sha256((cwd/'tests/cloudpickle_test.py').read_bytes()).hexdigest()});print(label,kind,r.returncode,flush=True)
(out/'v5-v5-final-windows-focused-results.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
