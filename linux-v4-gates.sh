#!/bin/sh
set -eu
TAG=v4-linux-$LANE_TAG
mkdir -p /tmp/candidate /tmp/base /evidence/$TAG-coverage
tar -xf /evidence/candidate.tar -C /tmp/candidate
tar -xf /evidence/base-with-regressions.tar -C /tmp/base
if [ "$LANE_TAG" != "py38" ] && [ -f /evidence/final-v5-focused.flag ]; then
 TAG=v5-final-linux-$LANE_TAG
 python /evidence/verify-source.py /tmp/candidate /evidence/candidate-manifest.json /evidence/$TAG-source-before.json
 cd /tmp/base
 set +e
 PYTHONPATH=.:tests python -m pytest tests/cloudpickle_test.py -k 'contextmanager or generators_remain' -q --junitxml=/evidence/$TAG-base-target.xml > /evidence/$TAG-base-target.log 2>&1
 BASE_EXIT=$?
 set -e
 cd /tmp/candidate
 PYTHONPATH=.:tests python -m pytest tests/cloudpickle_test.py -k 'contextmanager or generators_remain' -q --junitxml=/evidence/$TAG-candidate-target.xml > /evidence/$TAG-candidate-target.log 2>&1
 PYTHONPATH=.:tests python -c "import json;from tests.cloudpickle_test import test_contextmanager_preserves_pickleable_iterators as check;[check(p,a,e) for p in range(6) for a in (False,True) for e in (False,True)];print(json.dumps({'cases':24,'status':'PASS'}))" > /evidence/$TAG-all-protocols.json
 python /evidence/contextmanager-runtime.py /tmp/candidate /evidence/$TAG-runtime > /evidence/$TAG-runtime.log 2>&1
 python /evidence/verify-source.py /tmp/candidate /evidence/candidate-manifest.json /evidence/$TAG-source-after.json
 printf 'TAG=%s BASE=%s FOCUSED=0\n' "$TAG" "$BASE_EXIT"
 exit 0
fi
python -V > /evidence/$TAG-version.txt 2>&1
python /evidence/verify-source.py /tmp/candidate /evidence/candidate-manifest.json /evidence/$TAG-source-before.json
cd /tmp/candidate
python -m pip install -e . -r dev-requirements.txt > /evidence/$TAG-install.log 2>&1
python -m pip freeze > /evidence/$TAG-freeze.txt
cd /tmp/base
set +e
PYTHONPATH=.:tests python -m pytest tests/cloudpickle_test.py -k 'contextmanager or generators_remain' -q --junitxml=/evidence/$TAG-base-target.xml > /evidence/$TAG-base-target.log 2>&1
BASE_EXIT=$?
set -e
cd /tmp/candidate
export COVERAGE_FILE=/evidence/$TAG-coverage/.coverage
python ci/install_coverage_subprocess_pth.py > /evidence/$TAG-coverage-install.log 2>&1
set +e
COVERAGE_PROCESS_START=/tmp/candidate/.coveragerc PYTHONPATH=.:tests python -m pytest -q --junitxml=/evidence/$TAG-candidate-core.xml > /evidence/$TAG-candidate-core.log 2>&1
CORE_EXIT=$?
set -e
python -m coverage combine --append > /evidence/$TAG-coverage.log 2>&1
python -m coverage xml -i -o /evidence/$TAG-coverage.xml >> /evidence/$TAG-coverage.log 2>&1
python /evidence/contextmanager-runtime.py /tmp/candidate /evidence/$TAG-runtime > /evidence/$TAG-runtime.log 2>&1
PYTHONPATH=.:tests python -c "import json;from tests.cloudpickle_test import test_contextmanager_preserves_pickleable_iterators as check;[check(p,a,e) for p in range(6) for a in (False,True) for e in (False,True)];print(json.dumps({'cases':24,'protocols':[0,1,2,3,4,5],'status':'PASS'}))" > /evidence/$TAG-all-protocols.json
python /evidence/verify-source.py /tmp/candidate /evidence/candidate-manifest.json /evidence/$TAG-source-after.json
printf 'TAG=%s BASE=%s CORE=%s\n' "$TAG" "$BASE_EXIT" "$CORE_EXIT"
exit "$CORE_EXIT"
