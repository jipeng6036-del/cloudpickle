import asyncio
import contextlib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

source = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
output.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(source))
import cloudpickle


def make_sync():
    events = []
    @contextlib.contextmanager
    def manager(prefix, *, suffix):
        events.append(prefix)
        try:
            yield
        finally:
            events.append(suffix)
    @manager('enter', suffix='exit')
    def target(value):
        events.append(value)
        if value == 'fail':
            raise ValueError(value)
        return list(events)
    return target, lambda: list(events)


def make_async():
    events = []
    @contextlib.asynccontextmanager
    async def manager(prefix, *, suffix):
        events.append(prefix)
        try:
            yield
        finally:
            events.append(suffix)
    @manager('enter', suffix='exit')
    async def target(value):
        events.append(value)
        if value == 'fail':
            raise ValueError(value)
        return list(events)
    return target, lambda: list(events)


child = '''import asyncio,json,os,pickle,sys
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
'''
(output / 'child.py').write_text(child, encoding='utf8')
rows = []
for name, make in [('sync', make_sync), ('async', make_async)]:
    if name == 'async' and sys.version_info < (3, 10):
        rows.append({'case': name, 'status': 'STDLIB_CAPABILITY_SKIP', 'reason': 'asynccontextmanager decorators require Python3.10'})
        continue
    for protocol in (2, cloudpickle.DEFAULT_PROTOCOL):
        label = f'{name}-p{protocol}'
        try:
            payload = cloudpickle.dumps(make(), protocol=protocol)
            (output / (label + '.pickle')).write_bytes(payload)
            result = subprocess.run([sys.executable, '-c', child], input=payload, capture_output=True,
                                    env=dict(os.environ, PYTHONPATH=str(source)), timeout=30)
            (output / (label + '.stdout')).write_bytes(result.stdout)
            (output / (label + '.stderr')).write_bytes(result.stderr)
            assert result.returncode == 0, result.stderr.decode(errors='replace')
            value = json.loads(result.stdout)
            assert value['assertions'] == 'PASS'
            assert value['pid'] != os.getpid(), 'consumer did not run in another process'
            rows.append({'case': label, 'status': 'PASS', 'payloadSha256': hashlib.sha256(payload).hexdigest(), 'consumer': value})
        except Exception as error:
            rows.append({'case': label, 'status': 'FAIL', 'errorType': type(error).__name__, 'error': str(error)})
record = {'python': sys.version, 'source': str(source), 'producerPid': os.getpid(), 'cases': rows}
(output / 'result.json').write_text(json.dumps(record, indent=2), encoding='utf8')
print(json.dumps(record, indent=2))
sys.exit(any(row['status'] == 'FAIL' for row in rows))
