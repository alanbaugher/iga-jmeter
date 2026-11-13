# IGA JMeter Performance Testing

Performance and load-testing framework for Symantec Identity Governance and Administration (IGA), using Apache JMeter, DX Operational Observability (DX O2), JBoss datasource JMX statistics, and Oracle database monitoring.

## Objectives

- Measure account creation and modification throughput.
- Identify JDBC connection pool exhaustion and connection acquisition delays.
- Investigate IGA startup delays, including database version checks.
- Correlate JMeter response times with JBoss, JVM, and Oracle metrics.
- Establish performance baselines and identify scalability bottlenecks.

## Technology Stack

- Symantec IGA / Identity Manager
- Apache JMeter
- DX Operational Observability (DX O2)
- DX Application Performance Management (APM)
- JBoss / WildFly datasource monitoring
- Oracle Database
- JMX

## Test Scenarios

| Scenario | Description | Duration |
|---|---|---|
| Baseline | Low-concurrency account operations | 60 seconds |
| Create | Maximum sustainable account creation | 60 seconds |
| Modify | Account attribute modifications | 60 seconds |
| Mixed | Concurrent account creation and modification | 60 seconds |
| Startup | IGA initialization and version-check timing | Startup lifecycle |

## Primary Datasource Under Investigation

JBoss datasource: `pool-idm`

JMX metric path:

`jboss.as / data-source=pool-idm / statistics=pool / subsystem=datasources`

### Key Metrics

**Pool utilization**
- InUseCount
- AvailableCount
- ActiveCount
- IdleCount
- MaxUsedCount

**Pool contention**
- WaitCount
- AverageBlockingTime
- MaxWaitTime
- TimedOut
- BlockingFailureCount

**Connection lifecycle**
- CreatedCount
- DestroyedCount
- AverageCreationTime
- MaxCreationTime

**Connection usage**
- AverageGetTime
- MaxGetTime
- AverageUsageTime
- MaxUsageTime

## JMeter Performance Indicators

Collect the following for each test:

- Successful account operations per second
- Request throughput
- Average response time
- P95 and P99 response times
- Error rate
- Concurrent virtual users
- Provisioning completion time

## Test Execution

1. Configure the test environment using local configuration files or environment variables.
2. Confirm that test accounts and endpoints belong to an authorized non-production environment.
3. Start DX O2 and Oracle monitoring.
4. Run the JMeter workload.
5. Allow outstanding provisioning operations to complete.
6. Compare JMeter performance with datasource and database metrics.
7. Document bottlenecks and proposed remediation.

Example command:

```bash
jmeter -n \
  -t jmeter/create-accounts.jmx \
  -l results/create-test.jtl \
  -j results/jmeter.log
```

The example assumes the test plan exists and the `results` directory has been created.

## Performance Investigation

The initial investigation focuses on:

1. JDBC pool saturation.
2. Oracle connection creation latency.
3. Long-held database connections.
4. Database locking and SQL performance.
5. JBoss worker thread contention.
6. JVM CPU and garbage collection.
7. IGA provisioning and connector throughput.

## Security

- Do not commit passwords, API tokens, or connection secrets.
- Do not commit real user identity data or unredacted diagnostic exports.
- Use synthetic test accounts.
- Store environment-specific settings outside source control.
- Review JMeter scripts for embedded credentials before committing.

## Repository Usage

Intended for authorized internal performance testing and troubleshooting. No public open-source license is granted.

## Current Status

Initial investigation and baseline development. Performance findings will be documented as test results become available.
