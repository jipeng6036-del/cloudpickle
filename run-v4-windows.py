from pathlib import Path
import subprocess,os,json,hashlib,time
out=Path('F:/Github-PR/ci-evidence/discovery-20261027-ai');repo=Path('F:/Github-PR/inspection/oct27-ai-cloudpickle509');base=repo.parent/'oct27-ai-cloudpickle509-base';results=[]
for version in ['310','311','312','313','314']:
 py=repo/'.venv/Scripts/python.exe' if version=='311' else out/'venvs'/('cp'+version)/'Scripts/python.exe';row={'version':version,'steps':[]};results.append(row)
 steps=[('base-target',base,[str(py),'-m','pytest','tests/cloudpickle_test.py','-k','contextmanager or generators_remain','-q','--junitxml='+str(out/('v4-win'+version+'-base-target.xml'))]),('candidate-core',repo,[str(py),'-m','pytest','-q','--junitxml='+str(out/('v4-win'+version+'-candidate-core.xml'))]),('runtime',repo,[str(py),str(out/'contextmanager-runtime.py'),str(repo),str(out/('v4-runtime-win'+version))])]
 if version=='311':steps.insert(0,('coverage-install',repo,[str(py),'ci/install_coverage_subprocess_pth.py']));steps.extend([('coverage-combine',repo,[str(py),'-m','coverage','combine','--append']),('coverage-xml',repo,[str(py),'-m','coverage','xml','-i','-o',str(out/'v4-win311-coverage.xml')])]);(out/'v4-win311-coverage').mkdir(exist_ok=True)
 for label,cwd,cmd in steps:
  env=dict(os.environ,PYTHONPATH=str(cwd)+os.pathsep+str(cwd/'tests'))
  if version=='311':env['COVERAGE_FILE']=str(out/'v4-win311-coverage/.coverage')
  if version=='311' and label=='candidate-core':env['COVERAGE_PROCESS_START']=str(repo/'.coveragerc')
  test_before=hashlib.sha256((cwd/'tests/cloudpickle_test.py').read_bytes()).hexdigest();source_before=hashlib.sha256((cwd/'cloudpickle/cloudpickle.py').read_bytes()).hexdigest()
  with (out/('v4-win'+version+'-'+label+'.log')).open('wb') as log:r=subprocess.run(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600)
  assert test_before==hashlib.sha256((cwd/'tests/cloudpickle_test.py').read_bytes()).hexdigest();assert source_before==hashlib.sha256((cwd/'cloudpickle/cloudpickle.py').read_bytes()).hexdigest();row['steps'].append({'name':label,'exit':r.returncode,'sourceRawSha256':source_before,'testsRawSha256':test_before});(out/'V4-WINDOWS-PROGRESS.json').write_text(json.dumps(results,indent=2),encoding='utf8');print(version,label,r.returncode,flush=True)
  if r.returncode and label!='base-target':break
