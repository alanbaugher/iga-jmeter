#!/usr/bin/env bash
set -euo pipefail
umask 077
cd "$(dirname "$(readlink -f "$0")")"
if [[ -f .env ]]; then
  set -a
  # .env is trusted shell-compatible configuration (do not use untrusted files).
  source ./.env
  set +a
fi
# Pin JMeter to the tested OpenJDK 21 runtime, never the system default.
if ! command -v dpkg >/dev/null 2>&1; then
  echo "This benchmark launcher expects Debian/Ubuntu for the Java 21 path" >&2
  exit 1
fi
export JAVA_HOME="/usr/lib/jvm/java-21-openjdk-$(dpkg --print-architecture)"
if [[ ! -x "$JAVA_HOME/bin/java" ]]; then
  echo "Java 21 missing; run ./000b_install_and_set_java_openjdk_21_for_jmeter.sh" >&2
  exit 1
fi
export PATH="$JAVA_HOME/bin:$PATH"
unset JRE_HOME
export JMETER="$PWD/apache-jmeter-5.6.3/bin/jmeter"
mkdir -p results
exec python3 ./im-benchmark.py "$@"
