#!/usr/bin/env bash
# Install OpenJDK 21 on Debian/Ubuntu; JMeter launcher pins this runtime.
set -euo pipefail
usage() { echo "Usage: $0 [--check|--help]"; }
case "${1:-}" in --help|-h) usage; exit 0;; --check|'') ;; *) usage >&2; exit 2;; esac
command -v dpkg >/dev/null || { echo 'This script targets Debian/Ubuntu (dpkg/apt).' >&2; exit 1; }
JAVA_HOME="/usr/lib/jvm/java-21-openjdk-$(dpkg --print-architecture)"
if [[ ! -x "$JAVA_HOME/bin/java" ]]; then
  [[ "${1:-}" != --check ]] || { echo "Missing $JAVA_HOME/bin/java" >&2; exit 1; }
  sudo apt-get update
  sudo apt-get install -y openjdk-21-jre-headless
fi
[[ -x "$JAVA_HOME/bin/java" ]] || { echo "Java 21 missing at $JAVA_HOME" >&2; exit 1; }
"$JAVA_HOME/bin/java" -version
printf 'Java 21 installed at %s\nThe benchmark launcher pins JAVA_HOME on each run.\n' "$JAVA_HOME"
