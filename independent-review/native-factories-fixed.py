import sys,pathlib,hashlib,json,functools,contextlib,pickle,asyncio
sys.dont_write_bytecode=True
source=pathlib.Path('F:/Github-PR/inspection/oct27-ai-cloudpickle509');sys.path.insert(0,str(source));import cloudpickle
file=source/'cloudpickle/cloudpickle.py';sha=hashlib.sha256(file.read_bytes()).hexdigest()
class Managers:
 def __init__(self,events):self.events=events
 def sync(self,value,*,alias):
  assert self.events is alias;self.events.append('enter')
  try:yield value
  finally:self.events.append('exit')
 async def asynchronous(self,value,*,alias):
  assert self.events is alias;self.events.append('enter')
  try:yield value
  finally:self.events.append('exit')
def sync(events,value,*,alias):
 assert events is alias;events.append('enter')
 try:yield value
 finally:events.append('exit')
async def asynchronous(events,value,*,alias):
 assert events is alias;events.append('enter')
 try:yield value
 finally:events.append('exit')
rows=[]
for asyn in [False,True]:
 for kind in ['native_function','bound_method','exact_partial_function','exact_partial_bound_method']:
  for protocol in [2,cloudpickle.DEFAULT_PROTOCOL]:
   events=[];manager=Managers(events);func=asynchronous if asyn else sync
   bound=manager.asynchronous if asyn else manager.sync
   if kind=='native_function':factory=func;args=(events,'value');kwargs={'alias':events}
   elif kind=='bound_method':factory=bound;args=('value',);kwargs={'alias':events}
   elif kind=='exact_partial_function':factory=functools.partial(functools.partial(func,events),'value',alias=events);args=();kwargs={}
   else:factory=functools.partial(functools.partial(bound),'value',alias=events);args=();kwargs={}
   decorate=contextlib.asynccontextmanager if asyn else contextlib.contextmanager
   cm=decorate(factory)(*args,**kwargs);clone,cloned_events=pickle.loads(cloudpickle.dumps((cm,events),protocol=protocol));assert events==cloned_events==[]
   if asyn:
    async def enter():
     async with clone as result:assert result=='value';assert cloned_events==['enter']
    asyncio.run(enter());asyncio.run(cm.gen.aclose())
   else:
    with clone as result:assert result=='value';assert cloned_events==['enter']
    cm.gen.close()
   assert cloned_events==['enter','exit'];assert events==[]
   rows.append({'factory':kind,'asynchronous':asyn,'protocol':protocol,'classification':'NATIVE_FACTORY_ACCEPTED_WITH_ALIAS_AND_NO_EARLY_BODY'})
assert hashlib.sha256(file.read_bytes()).hexdigest()==sha
result={'sourceSha256':sha,'python':sys.version,'cases':rows,'allAssertionsPassed':True}
pathlib.Path('F:/Github-PR/ci-evidence/discovery-20261027-cloudpickle-review/native-factories-fixed.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps({'sourceSha256':sha,'positiveCases':len(rows),'allAssertionsPassed':True}))
