import sys,pathlib,hashlib,json,functools,inspect,contextlib,pickle,asyncio
sys.dont_write_bytecode=True
source=pathlib.Path('F:/Github-PR/inspection/oct27-ai-cloudpickle509');sys.path.insert(0,str(source));import cloudpickle
file=source/'cloudpickle/cloudpickle.py';sha=hashlib.sha256(file.read_bytes()).hexdigest()
class EffectPartial(functools.partial):
 def __call__(self,*args,**kwargs):
  self.calls.append('construct')
  return super().__call__(*args,**kwargs)
class FunctionLike:
 def __init__(self,gen,calls):
  self.gen=gen;self.calls=calls;self.__code__=gen.__code__;self.__name__=gen.__name__;self.__defaults__=None;self.__kwdefaults__=None;self.__annotations__={}
 def __call__(self,*args,**kwargs):
  self.calls.append('construct');return self.gen(*args,**kwargs)
rows=[]
for asynchronous in [False,True]:
 if asynchronous:
  async def generator():yield
  decorate=contextlib.asynccontextmanager
 else:
  def generator():yield
  decorate=contextlib.contextmanager
 for kind in ['partial_subclass','function_like_callable']:
  for protocol in [2,cloudpickle.DEFAULT_PROTOCOL]:
   calls=[]
   if kind=='partial_subclass':factory=EffectPartial(generator);factory.calls=calls
   else:factory=FunctionLike(generator,calls)
   recognized=inspect.isasyncgenfunction(factory) if asynchronous else inspect.isgeneratorfunction(factory)
   cm=decorate(factory)();assert calls==['construct']
   try:
    payload=cloudpickle.dumps((cm,calls),protocol=protocol)
    clone,clonecalls=pickle.loads(payload)
    equivalent=clonecalls==calls
    classification='BUG_REPRODUCED' if not equivalent else 'NO_ADDITIONAL_CONSTRUCTION'
    row={'factory':kind,'asynchronous':asynchronous,'protocol':protocol,'inspectRecognized':recognized,'classification':classification,'originalCalls':list(calls),'loadedCalls':list(clonecalls),'equivalent':equivalent}
    if asynchronous:asyncio.run(clone.gen.aclose())
    else:clone.gen.close()
   except pickle.PicklingError as e:row={'factory':kind,'asynchronous':asynchronous,'protocol':protocol,'inspectRecognized':recognized,'classification':'REJECTED_AS_EXPECTED','error':str(e)}
   except BaseException as e:row={'factory':kind,'asynchronous':asynchronous,'protocol':protocol,'inspectRecognized':recognized,'classification':'PROBE_ERROR','errorType':type(e).__name__,'error':str(e)}
   if asynchronous:asyncio.run(cm.gen.aclose())
   else:cm.gen.close()
   rows.append(row)
assert hashlib.sha256(file.read_bytes()).hexdigest()==sha
result={'sourceSha256':sha,'python':sys.version,'cases':rows,'semanticBugCount':sum(r['classification']=='BUG_REPRODUCED' for r in rows)}
assert all(row['classification']=='REJECTED_AS_EXPECTED' for row in rows), rows
out=pathlib.Path('F:/Github-PR/ci-evidence/discovery-20261027-cloudpickle-review/factory-boundaries-fixed.json');out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2))
