#!/usr/bin/env bash
# xcj parity 7-red diagnostic: bootstrap exactly like ci-parity.sh, run ONLY the
# seven files that died in the timeout round, keep every log under $MLRUN_OUT.
set -u
export DEBIAN_FRONTEND=noninteractive
OUT="${MLRUN_OUT:-/tmp}/diag"
mkdir -p "$OUT"
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq git curl ca-certificates tar xz-utils rsync python3-pip openssh-client >/dev/null 2>&1
git config --global --add safe.directory '*'
ARCH=$(dpkg --print-architecture)
case "$ARCH" in amd64) NA=x64 ;; arm64) NA=arm64 ;; *) NA=$ARCH ;; esac
curl -fsSL "https://nodejs.org/dist/v22.18.0/node-v22.18.0-linux-$NA.tar.xz" -o /tmp/node.tar.xz \
  && tar -xJf /tmp/node.tar.xz -C /opt \
  && ln -sf /opt/node-v22.18.0-linux-$NA/bin/node /usr/local/bin/node \
  && ln -sf /opt/node-v22.18.0-linux-$NA/bin/npm /usr/local/bin/npm
python3 -m pip install -q --break-system-packages uv >/dev/null 2>&1
git clone -q https://github.com/NousResearch/hermes-agent /tmp/hermes-agent
git -C /tmp/hermes-agent checkout -q 3b421578588243f920886e6fe79a6faa87ea026e
uv sync --python 3.14 --directory /tmp/hermes-agent >/dev/null 2>&1 && echo "bootstrap: uv sync OK" || echo "bootstrap: uv sync FAILED"
cd "$(pwd)"   # the staged repo copy is the crun job cwd
for t in test_11_integration_crash_resume test_11_integration_lane_supervisor test_argv_residency_7ncu0 test_hooks_outbound_bridge test_personal_path_scrub_867 test_run_binding test_scrub_surface_1w0hoy; do
  echo "=== $t ==="
  timeout 420 uv run --project /tmp/hermes-agent python3 "tests/$t.py" > "$OUT/$t.log" 2>&1
  echo "rc=$? log=$OUT/$t.log"
  tail -5 "$OUT/$t.log"
done
echo DIAG7_DONE
