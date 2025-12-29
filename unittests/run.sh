#run script
#bash unittests/run.sh
#!/bin/bash
set -e
cd "$(dirname "$0")/.."
if [ -f requirements.txt ]; then pip install -q -r requirements.txt; fi
pip install -q -r unittests/requirements.txt || { echo "Dependency installation failed"; exit 1; }
pip install -q tzdata
pip install -q bosch-thermostat-client
python3 -m pytest --tb=short -q unittests "$@"