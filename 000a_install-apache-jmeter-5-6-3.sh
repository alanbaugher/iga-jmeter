#!/usr/bin/env bash
# Install the benchmark-tested Apache JMeter 5.6.3, with SHA-512 verification.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
VERSION=5.6.3
PKG="apache-jmeter-${VERSION}.tgz"
BASE="https://archive.apache.org/dist/jmeter/binaries"
usage() { echo "Usage: $0 [--check|--force|--help]"; }
case "${1:-}" in
  --help|-h) usage; exit 0 ;;
  --check) if [[ -x "$ROOT/apache-jmeter-$VERSION/bin/jmeter" ]]; then echo "JMeter $VERSION installed"; exit 0; else echo "JMeter $VERSION missing" >&2; exit 1; fi ;;
  --force) FORCE=1 ;;
  '') FORCE=0 ;;
  *) usage >&2; exit 2 ;;
esac
# Suppress Log4j internal status WARN messages (preserves a one-time .bak backup).
configure_log4j() {
  local config="$ROOT/apache-jmeter-$VERSION/bin/log4j2.xml"
  [[ -f "$config" ]] || { echo "Missing Log4j configuration: $config" >&2; return 1; }
  if grep -Eq '<Configuration[[:space:]][^>]*status="WARN"' "$config"; then
    sed -i.bak '/<Configuration[[:space:]]/s/status="WARN"/status="ERROR"/' "$config"
    echo "Set Log4j status threshold to ERROR: $config"
  else
    echo "Log4j status threshold unchanged (already configured or different format)"
  fi
}
if [[ -x "$ROOT/apache-jmeter-$VERSION/bin/jmeter" && "$FORCE" == 0 ]]; then
  echo "JMeter $VERSION already installed"
  configure_log4j
  exit 0
fi
command -v curl >/dev/null || { echo 'curl is required' >&2; exit 1; }
command -v sha512sum >/dev/null || { echo 'sha512sum is required' >&2; exit 1; }
TMP="$(mktemp -d "$ROOT/.jmeter-download.XXXXXXXX")"
trap 'rm -rf -- "$TMP"' EXIT
curl --fail --show-error --location --retry 3 "$BASE/$PKG" -o "$TMP/$PKG"
curl --fail --show-error --location --retry 3 "$BASE/$PKG.sha512" -o "$TMP/$PKG.sha512"
expected="$(grep -Eo '[[:xdigit:]]{128}' "$TMP/$PKG.sha512" | head -n 1)"
[[ ${#expected} -eq 128 ]] || { echo 'Invalid Apache SHA-512 file' >&2; exit 1; }
printf '%s  %s\n' "$expected" "$TMP/$PKG" | sha512sum --check --status || { echo 'JMeter checksum mismatch' >&2; exit 1; }
# Never replace an existing installation in place, including with --force.
if [[ -e "$ROOT/apache-jmeter-$VERSION" ]]; then
  echo "Existing installation detected: $ROOT/apache-jmeter-$VERSION; move it aside before reinstalling" >&2
  exit 1
fi
tar -xzf "$TMP/$PKG" -C "$ROOT"
echo "Installed $ROOT/apache-jmeter-$VERSION"
configure_log4j
