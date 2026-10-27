from pathlib import Path
import datetime, hashlib, json, subprocess, xml.etree.ElementTree as ET

out = Path('F:/Github-PR/ci-evidence/discovery-20261027-ai')
repo = Path('F:/Github-PR/inspection/oct27-ai-cloudpickle509')
def sha(raw): return hashlib.sha256(raw).hexdigest()
def git(*args): return subprocess.check_output(['git', *args], cwd=repo)
def load(name): return json.loads((out / name).read_text(encoding='utf-8-sig'))
bridge = []
for path in ['cloudpickle/__init__.py','cloudpickle/cloudpickle.py','cloudpickle/cloudpickle_fast.py','tests/cloudpickle_test.py','CHANGES.md']:
    raw=(repo/path).read_bytes(); canonical=git('cat-file','blob',':'+path)
    assert raw.replace(b'\r\n', b'\n') == canonical, path
    bridge.append({'path':path,'windowsRawSha256':sha(raw),'canonicalGitLfSha256':sha(canonical),'rawBytes':len(raw),'canonicalBytes':len(canonical),'crlfCount':raw.count(b'\r\n'),'onlyCrlfToLfEqualsGit':True,'gitBlob':git('rev-parse',':'+path).decode().strip()})
(out/'FINAL-EOL-BRIDGE.json').write_text(json.dumps(bridge,indent=2),encoding='utf8')
def result(name, contains_target=False):
    root=ET.parse(out/name).getroot(); rows=list(root.iter('testcase'))
    if contains_target:
        rows=[c for c in rows if 'contextmanager' in c.attrib.get('name','') or 'generators_remain' in c.attrib.get('name','')]
    counts={'total':len(rows),'pass':0,'fail':0,'error':0,'skip':0,'xfail':0}
    for case in rows:
        if case.find('failure') is not None: key='fail'
        elif case.find('error') is not None:key='error'
        elif case.find('skipped') is not None:
            key='xfail' if case.find('skipped').attrib.get('type')=='pytest.xfail' else 'skip'
        else:key='pass'
        counts[key]+=1
    return {'file':name,'sha256':sha((out/name).read_bytes()),**counts}
matrix=[]
old_test='d93f15160cf166c6dc56027771f5e9bedeb848a03f036524ba356259bc4b6bf1'
final_test=next(r for r in bridge if r['path']=='tests/cloudpickle_test.py')['canonicalGitLfSha256']
for tag in ['win310','win311','win312','win313','win314','linux-py38','linux-py39','linux-pypy39']:
    core=result('v4-'+tag+'-candidate-core.xml')
    assert core['fail']==core['error']==0
    prefix='v4-linux-py38' if tag=='linux-py38' else 'v5-final-'+tag
    base=result(prefix+'-base-target.xml')
    focused=result('v4-linux-py38-candidate-core.xml',True) if tag=='linux-py38' else result(prefix+'-candidate-target.xml')
    assert focused['fail']==focused['error']==0 and focused['total']==48
    assert base['fail'] in (14,16) and base['pass']==32 and base['error']==0
    row={'interpreter':tag,'fullSuite':core,'fullSuiteTestsLfSha256':final_test if tag=='linux-py38' else old_test,'finalRegression':focused,'baselineFinalRegression':base,'finalRegressionTestsLfSha256':final_test}
    if tag.startswith('linux'):
        for suffix in ['before','after']:
            m=load(prefix+'-source-'+suffix+'.json');assert m['matched']==65
            expected={r['path']:r['sha256'] for r in load('candidate-manifest.json')}
            assert {r['path']:r['sha256'] for r in m['files']}==expected
        row['finalCanonicalSourceVerification']=prefix+'-source-{before,after}.json: all65 SHA256 equal staged Git manifest'
    matrix.append(row)
runtimes=[]
for folder in ['v4-runtime-win'+v for v in ['310','311','312','313','314']]+['v4-linux-py38-runtime','v5-final-linux-py39-runtime','v5-final-linux-pypy39-runtime','v4-runtime-wheel-py311']:
    data=load(folder+'/result.json')
    for r in data['cases']:
        assert r['status'] in ('PASS','STDLIB_CAPABILITY_SKIP')
        if r['status']=='PASS':assert r['consumer']['assertions']=='PASS' and r['consumer']['pid'] != data['producerPid']
    runtimes.append({'file':folder+'/result.json','python':data['python'],'passes':sum(r['status']=='PASS' for r in data['cases']),'stdlibCapabilitySkips':sum(r['status']=='STDLIB_CAPABILITY_SKIP' for r in data['cases'])})
hooks=load('v5-final-precommit-configured-results.json');assert all(r['exit']==0 for r in hooks)
package=load('V4-PACKAGE.json');assert all(r['exit']==0 for r in package['steps'])
receipt={'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':'cloudpipe/cloudpickle','issue':509,'branch':git('branch','--show-current').decode().strip(),'frozenSource':load('FROZEN-SOURCE.json'),'sourceEncodingBridge':bridge,'matrix':matrix,'lastTestOnlyDelta':'Two return-value assertions changed from identity with False to falsiness, matching Python3.8 asynccontextmanager normal-exit contract. All final48 cases rerun on every8 interpreter; LinuxCPython3.8 full suite also ran final tree. Other7 complete-suite results retain earlier test hash and are not represented as final-tree full reruns. Production unchanged.','strictFreshProcessConsumers':runtimes,'packaging':package,'hooks':{'finalResults':hooks,'exactConfiguredCommand':'pre-commit run --files *','changedFiles':['CHANGES.md','cloudpickle/cloudpickle.py','tests/cloudpickle_test.py'],'broaderAllFiles':'Optional broader --all-files finds same preexisting Black formatting failure in unmodified tests/cloudpickle_ipykernel_test.py on base/candidate; original blob restored and excluded.'},'coverage':'ci/install_coverage_subprocess_pth.py, COVERAGE_PROCESS_START, PYTHONPATH, complete pytest, coverage combine --append and coverage xml -i actually executed for Linux3.8/3.9/PyPy3.9 and Windows3.11. OtherWindows full suites execute pytest project entry. No codecov upload.','independentReview':'../discovery-20261027-cloudpickle-review/verification.json:40 assertion cases PASS at Windows raw5b08349f; no confirmed design blocker. Root activity assessment permits stable foundation dependency with latest real human merge Sep10 (about6weeks), not claimed active in past30days.','policyAndDuplicateEvidence':['cloudpickle-platform.json:pull_request_creation_policy=all','cloudpickle509-fresh.json','cloudpickle509-comments-fresh.json','cloudpickle509-timeline-fresh.json','cloudpickle-open-prs-fresh.json:complete30OPEN','cloudpickle-pr606-actual-files.json','cloudpickle-pr616-actual-files.json','cloudpickle-pr617-actual-files.json','cloudpipe-org-defaults.json:publicdefault404'],'notLocallyExecuted':['macOS hosted matrix and remaining OS/version combinations','label-conditional downstream suites','codecov upload/release'],'status':'LOCAL_GATES_COMPLETE; parent final pre-publication review pending'}
(out/'FINAL-RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
git('diff','--cached','--binary')
(out/'FINAL.patch').write_bytes(git('diff','--cached','--binary'))
print(json.dumps({'source':bridge[1],'finalTests':final_test,'matrix':[{k:r[k] for k in ['interpreter','fullSuite','finalRegression','baselineFinalRegression']} for r in matrix]},indent=2))
