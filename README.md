IGA benchmark (pinned JMeter 5.6.3 + OpenJDK 21, Ubuntu/Debian)

1. cd ~/testing
2. ./000a_install-apache-jmeter-5-6-3.sh
3. ./000b_install_and_set_java_openjdk_21_for_jmeter.sh
4. ./iga-benchmark.sh --help
5. ./iga-benchmark.sh check
6. ./iga-benchmark.sh

The shell launcher always pins JAVA_HOME and JMETER to the tested versions.
The JMeter distribution's Groovy libraries remain intact; Java 21 avoids
observed Java 25/Groovy bytecode compatibility failures.

Do not overwrite your existing .env without reviewing the supplied sample.
The scripts use results/ for benchmark output. Keep backups of prior scripts.

Log4j: 000a sets status="ERROR" in JMeter 5.6.3 bin/log4j2.xml (backing up as .bak) to suppress the Log4j package-scanning status warning. Re-running 000a applies this setting to an existing installation too.
