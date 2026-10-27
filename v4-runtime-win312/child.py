import asyncio,json,os,pickle,sys
f, read_events = pickle.loads(sys.stdin.buffer.read())
async def run_async():
 one = await f('one')
 try: await f('fail')
 except ValueError as error: assert str(error) == 'fail'
 else: raise AssertionError('exception was swallowed')
 two = await f('two')
 return one, two
if asyncio.iscoroutinefunction(f):
 one, two = asyncio.run(run_async())
else:
 one = f('one')
 try: f('fail')
 except ValueError as error: assert str(error) == 'fail'
 else: raise AssertionError('exception was swallowed')
 two = f('two')
assert one == ['enter', 'one'], one
assert two == ['enter','one','exit','enter','fail','exit','enter','two'], two
assert read_events() == two + ['exit'], read_events()
print(json.dumps({'pid': os.getpid(), 'one': one, 'two': two, 'events': read_events(), 'assertions': 'PASS'}))
