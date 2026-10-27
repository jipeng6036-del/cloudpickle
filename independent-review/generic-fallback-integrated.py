import sys,pathlib,hashlib,json,contextlib,pickle,asyncio,types,io,importlib
sys.dont_write_bytecode=True
source=pathlib.Path('F:/Github-PR/inspection/oct27-ai-cloudpickle509');sys.path.insert(0,str(source));import cloudpickle
core=importlib.import_module('cloudpickle.cloudpickle');file=source/'cloudpickle/cloudpickle.py';sha=hashlib.sha256(file.read_bytes()).hexdigest()
class AsyncIterator:
 def __init__(self,values):self.values=iter(values)
 async def __anext__(self):
  try:return next(self.values)
  except StopIteration:raise StopAsyncIteration
rows=[]
for asyn in [False,True]:
 for advanced in [False,True]:
  for protocol in [2,cloudpickle.DEFAULT_PROTOCOL]:
   calls=[];holder=[]
   def factory(holder,calls):
    calls.append('construct')
    return AsyncIterator([7,8] if advanced else [7]) if asyn else iter([7,8] if advanced else [7])
   decorate=contextlib.asynccontextmanager if asyn else contextlib.contextmanager
   cm=decorate(factory)(holder,calls);holder.append(cm);cm.self=cm
   if advanced:
    if asyn:assert asyncio.run(cm.gen.__anext__())==7
    else:assert next(cm.gen)==7
   data=io.BytesIO();cloudpickle.CloudPickler(data,protocol=protocol).dump((cm,calls,holder));clone,cloned_calls,cloned_holder=pickle.loads(data.getvalue())
   assert calls==cloned_calls==['construct'];assert clone.self is cloned_holder[0] is clone
   assert clone.args[0] is cloned_holder and clone.args[1] is cloned_calls
   expected=8 if advanced else 7
   if asyn:
    async def check():
     async with clone as value:assert value==expected
    asyncio.run(check())
   else:
    with clone as value:assert value==expected
   assert calls==cloned_calls==['construct']
   rows.append({'asynchronous':asyn,'iteratorAdvancedBeforePickle':advanced,'protocol':protocol,'classification':'FALLBACK_PRESERVES_ITERATOR_POSITION_FACTORY_COUNT_ALIAS_CYCLES','value':expected})
assert hashlib.sha256(file.read_bytes()).hexdigest()==sha
result={'python':sys.version,'sourceSha256':sha,'scope':'Actual worker source with ordinary CloudPickler; reviewer did not modify reducer or dispatch.','cases':rows,'allAssertionsPassed':True}
pathlib.Path('F:/Github-PR/ci-evidence/discovery-20261027-cloudpickle-review/generic-fallback-integrated.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps({'sourceSha256':sha,'cases':len(rows),'allAssertionsPassed':True}))
