# IGA JMeter Benchmark

Repeatable account-provisioning performance tests for **Broadcom/Symantec Identity Governance and Administration (IGA / Identity Manager)** using **Apache JMeter 5.6.3** and **OpenJDK 21** on Ubuntu/Debian.

The benchmark combines a JMeter test plan with a Python orchestration/reporting utility. It supports account creation and modification phases, cleanup and recovery, and correlation of benchmark runs with IGA server, router, and user-store logs. Additional WildFly CLI scripts support JDBC datasource statistics and targeted startup troubleshooting.

> **Use only in an authorized, non-production test environment.** Tests create, modify, and delete benchmark accounts. Review configuration, credentials, cleanup scope, and monitoring overhead before running.

## Repository contents

| File | Purpose |
| --- | --- |
| `iga-benchmark.sh` | Main launcher; loads `.env`, pins Java 21 and JMeter 5.6.3, then invokes Python |
| `im-benchmark.py` | Configuration validation, run orchestration, summaries, log analysis, and recovery |
| `im-benchmark.jmx` | JMeter workload for benchmark account operations and cleanup |
| `000a_install-apache-jmeter-5-6-3.sh` | Installs JMeter 5.6.3 from the Apache archive with SHA-512 verification |
| `000b_install_and_set_java_openjdk_21_for_jmeter.sh` | Installs/checks the OpenJDK 21 runtime on Ubuntu/Debian |
| `.env.example` | Configuration template; copy and customize locally |
| `enable-jdbc-stats-for-apm-monitoring.cli` | Enables WildFly datasource statistics for six IGA datasources |
| `focus_on_jdbc_calls_during_startup.cli` | Enables JDBC spy tracing for six datasources to investigate startup behavior |
| `results/` | Local per-run output (excluded from Git) |

The JMeter distribution (`apache-jmeter-5.6.3/`), local `.env`, and generated results are **not** intended to be committed.

## Requirements

- Ubuntu or Debian with `bash`, `python3`, `curl`, `tar`, `sha512sum`, and `dpkg`.
- `sudo` access to install OpenJDK 21 if necessary.
- Network access to the configured IGA endpoint.
- An authorized IGA test account with the permissions required by the benchmark.
- A dedicated test environment and permission to create, modify, and clean up test accounts.

The launcher uses `/usr/lib/jvm/java-21-openjdk-$(dpkg --print-architecture)` and the repository-local `apache-jmeter-5.6.3/bin/jmeter`. It deliberately overrides `JAVA_HOME` and `JMETER` on each run. Java 21 is pinned to avoid Java 25/Groovy bytecode compatibility problems observed with this test setup; leave the JMeter distribution's Groovy libraries intact.

## Quick start

Clone the repository, then run these commands **from the repository directory**:

```bash
cd ~/testing
git clone git@github.com:alanbaugher/iga-jmeter.git
cd iga-jmeter

./000a_install-apache-jmeter-5-6-3.sh
./000b_install_and_set_java_openjdk_21_for_jmeter.sh

# Preserve any existing .env; create one only if absent.
[ -e .env ] || cp .env.example .env
chmod 600 .env
# Edit .env to match your authorized lab environment.

./iga-benchmark.sh --help
./iga-benchmark.sh check
./iga-benchmark.sh
```

For an existing working checkout at `~/testing/iga_benchmark`, remain in that directory instead of cloning again. Do **not** overwrite an existing `.env` without reviewing and backing it up.

### Local configuration

The launcher sources `.env` as **shell code**; only use a trusted local file. Do not commit it or paste its contents into tickets or chats.

| Variable | Purpose |
| --- | --- |
| `DEPLOYMENT` | Deployment identifier (`IGA` in the provided example) |
| `IM_HOST`, `IM_PORT` | IGA endpoint host and HTTPS port |
| `IM_ENV`, `IM_ORG` | Identity Manager environment and organization |
| `IM_USER`, `IM_PASS` | Authorized benchmark login credentials |
| `USERS` | Concurrent benchmark workers (example: `10`) |
| `SECONDS_PER_PHASE` | Requested duration of each timed phase (example: `60`) |
| `EXTRA` | Additional workload option; see test plan before changing |
| `CLEANUP_WORKERS` | Parallel cleanup workers (example: `32`) |
| `IGA_LOGS_ROOT` | Root directory for IGA diagnostic logs |
| `LOG_PADDING_SECONDS` | Extra time on either side of the run for log correlation |
| `SERVER_TZ`, `ROUTER_TZ`, `USTORE_TZ` | Time zones used to interpret component logs |

The launcher determines `JAVA_HOME` and `JMETER` itself, regardless of values supplied in `.env`. Optional log-path overrides include `SERVER_LOG`, `ROUTER_LOG`, and `USTORE_LOG`.

Use synthetic benchmark identities. Treat `.jmx` files and exported logs as potentially sensitive even when `.env` is ignored.

## Commands

```bash
./iga-benchmark.sh                 # Default: full run, report, and log analysis
./iga-benchmark.sh menu            # Interactive menu
./iga-benchmark.sh check           # Validate configuration and runtime
./iga-benchmark.sh run             # Benchmark, cleanup, and report
./iga-benchmark.sh latest          # Show most recent run directory
./iga-benchmark.sh report          # Report latest run
./iga-benchmark.sh logs            # Analyze latest run logs
./iga-benchmark.sh logs --all-entries
./iga-benchmark.sh recover         # Preview recovery for latest run
./iga-benchmark.sh recover --apply # Apply recovery after confirmation
./iga-benchmark.sh --help
```

`report`, `logs`, and `recover` also accept a specific run-directory path. Recovery changes account state: **preview the target run and verify its account scope before using `--apply`**. The `--yes` option bypasses interactive confirmation and should be reserved for carefully controlled automation.

## Benchmark workflow and output

The JMeter plan performs preflight/login-related checks, coordinates account creation, runs a modification phase, and attempts cleanup. The Python runner creates a unique run directory such as:

```text
results/minute-YYYYMMDD-HHMMSS-XXXXXXXX/
```

Artifacts include `results.jtl`, `jmeter.log`, and (for the default `all` command) `log-analysis.txt`; reporting and recovery may produce additional run-specific files. Results remain local under `results/`.

The Python runner checks for cleanup inventory markers in the JMeter log and can attempt run-scoped recovery when remaining benchmark accounts are reported. **Always verify cleanup results**; a failed preflight or unreachable server can prevent both the workload and cleanup from completing.

### Interpreting results

Compare successful, completed account operations—not just submitted HTTP requests—with latency, errors, and the duration of the measured phase. Record the worker count and test configuration for each run.

**An HTTP 503 during preflight is an application availability failure, not a throughput measurement.** Do not interpret zero created accounts in that situation as the system's sustainable provisioning rate. Restore endpoint health, validate a single-user run, and only then increase concurrency.

## JDBC pool monitoring and startup diagnostics

Two WildFly CLI files are included for separate purposes:

1. **Datasource statistics:** `enable-jdbc-stats-for-apm-monitoring.cli` enables `statistics-enabled=true` on `pool-idm`, `pool-objectstore`, `pool-archive`, `pool-auditDbDataSource`, `pool-reportsnapshot`, and `pool-WPDS`, then reloads WildFly.
2. **JDBC spy tracing:** `focus_on_jdbc_calls_during_startup.cli` adds the `jboss.jdbc.spy` TRACE logger and enables `spy=true` on all six datasources. This is invasive tracing for startup investigation, **not a default setting for load tests**.

Run these only with appropriate administrative authorization and a maintenance plan. The scripts take a WildFly configuration snapshot and can reload the application. Review existing logger settings and rollback steps before execution. The comments in the CLI files document the environment-specific `jboss-cli.sh` connection command.

For `pool-idm` analysis in DX Operational Observability / DX APM, correlate JMeter phase timestamps with datasource metrics such as `InUseCount`, `AvailableCount`, `ActiveCount`, `MaxUsedCount`, `WaitCount`, `TimedOut`, `AverageBlockingTime`, `AverageGetTime`, and `MaxGetTime` where exposed. Use deltas/rates for cumulative counters. **Do not assume `pool-idm` is the same as another IGA datasource or has the same maximum pool size without checking its runtime configuration.**

JDBC spy tracing can increase logging volume and affect timings; disable it before establishing an unbiased performance baseline.

<img width="1912" height="909" alt="image" src="https://github.com/user-attachments/assets/a9774c88-f98b-4bec-9b51-fd2bad239c23" />  




## Installation notes

The JMeter installer downloads the official 5.6.3 archive and verifies its SHA-512 checksum. It does not overwrite an existing installation in place. When run against an existing installation, it also checks the Log4j configuration.

To suppress the JMeter Log4j package-scanning status warning, `000a_install-apache-jmeter-5-6-3.sh` changes the `status="WARN"` setting to `status="ERROR"` in `apache-jmeter-5.6.3/bin/log4j2.xml`, retaining a `.bak` backup when the change is made. Re-running the installer applies this adjustment to an existing installation as well.

## Security and source control

- Keep the GitHub repository **private** unless publication is explicitly approved.
- Never commit `.env`, passwords, access tokens, production identities, unredacted JMeter results, or raw IGA diagnostic logs.
- Review `im-benchmark.jmx`, Python scripts, and CLI files for embedded endpoints and secrets before each release.
- Rotate any credential accidentally exposed in logs, chats, or version control.
- Use `.env.example` only as a placeholder template.
- Keep generated `results/`, the downloaded JMeter installation, and packaged archives out of Git.
- No open-source license is granted by this repository unless a license is explicitly added by the authorized owner.

## Updating GitHub

```bash
git status
git add README.md
git commit -m "Document IGA benchmark setup, commands, and diagnostics"
git push origin main
```

If you change other source files, review the staged diff before committing them.
