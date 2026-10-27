import json,pathlib,subprocess,sys
sys.path.insert(0,'F:/Github-PR/ci-evidence');import sol_high_serial_gh as g
repo=pathlib.Path('F:/Github-PR/inspection/oct27-ai-cloudpickle509');out=pathlib.Path('F:/Github-PR/ci-evidence/discovery-20261027-ai');roots=[p for p in subprocess.check_output(['git','ls-tree','--name-only','HEAD'],cwd=repo).decode().splitlines() if not p.startswith('.')];rows=[]
for label,files in [('ci-rootglob',roots),('changed',['CHANGES.md','cloudpickle/cloudpickle.py','tests/cloudpickle_test.py'])]:
 with g.gate():
  with (out/('v5-final-precommit-'+label+'.log')).open('wb') as log:r=subprocess.run([str(repo/'.venv/Scripts/python.exe'),'-m','pre_commit','run','--files',*files],cwd=repo,stdout=log,stderr=subprocess.STDOUT,timeout=180)
 rows.append({'check':label,'exit':r.returncode});print(label,r.returncode,flush=True)
(out/'v5-final-precommit-configured-results.json').write_text(json.dumps(rows,indent=2),encoding='utf8')

