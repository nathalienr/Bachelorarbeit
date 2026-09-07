**Security Testing Framework**

A Kali Linux toolset for verifying countermeasures CM-001 to CM-010

>*An add-on to the "ifm Cybersecurity Test Process" document (IEC 62443-4-1 / 4-2) — so that developers can run the tests on their own*

# 1. Purpose and Context

This document adds ready-to-run test instructions for each countermeasure (CM) to the "ifm Cybersecurity Test Process". The goal is simple: any developer — even without deep penetration-testing experience — can run the required security tests on their own with one defined Kali Linux tool, read the result, and check it against the acceptance criteria.

Where this fits in the overall process (from the Cybersecurity Test Process):

*SUC → Threat / Vulnerability / Risk → Risk Mitigation → Countermeasure → Security Test Module (STM) →* *Review*

Every countermeasure with the label "security-func" needs a technical check through its Security Test Module (STM) at the required Security Test Grade (STG). For each of the ten project-relevant CMs, this framework gives you exactly one Kali Linux tool, one ready-to-run command, and one pass/fail rule.

# 2. Test Environment and Safety Rules

- Run all tests only in the approved test environment (staging / test lab) — never against production systems, unless this has been explicitly approved.

- Use Kali Linux (current rolling release) as the base test system, ideally as a dedicated VM connected to the relevant test zone.

- Before every test: get written approval / a test window and reference it in the test log.

- Tools that can actively affect a system (Hydra, boofuzz) must only be used with a watchdog / monitoring on the target system.

- Store all tool output unchanged as evidence (see the project's evidence folder) and reference it in the test log.

# 3. Tool Assignment — Overview

Each countermeasure has exactly one primary Kali Linux tool. The details, commands, and pass/fail logic for each CM follow in Chapter 4.

| **CM ID** | **Title** | **Kali Tool** | **Category** |
|----|----|----|----|
| CM-001 | Network Exposure vs. Architecture | Nmap | Information Gathering / Port Scanning |
| CM-002 | Network Segmentation (Cross-Segment Exposure) | Nmap | Information Gathering / Network Reachability |
| CM-003 | Default / Weak Credentials | Hydra | Password Attacks |
| CM-004 | RBAC / Privilege Escalation | OWASP ZAP | Web Application Analysis |
| CM-005 | TLS Configuration | SSLscan | Information Gathering / SSL-TLS Analysis |
| CM-006 | Hardening Validation | Lynis | Vulnerability Analysis / System Audit |
| CM-007 | Debug / Service Interface Exposure | Nikto | Web Application Analysis |
| CM-008 | Patch Level / Known CVEs | OpenVAS (Greenbone Vulnerability Manager, GVM) | Vulnerability Analysis |
| CM-009 | Load Behavior & Logging | Siege | Stress / Load Test |
| CM-010 | Fuzzing / Robustness | boofuzz | Fuzzing Framework |

# 4. Test Instructions for Each Countermeasure

## CM-001 — Network Exposure vs. Architecture

<table>
<colgroup>
<col style="width: 24%" />
<col style="width: 76%" />
</colgroup>
<thead>
<tr>
<th><strong>Countermeasure</strong></th>
<th><strong>CM-001 — Network Exposure vs. Architecture</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Reference</strong></td>
<td>STM: STM-2 | STG: STG1-3 | SVV: SVV-4b</td>
</tr>
<tr>
<td><strong>Kali Tool</strong></td>
<td>Nmap</td>
</tr>
<tr>
<td><strong>Category</strong></td>
<td>Information Gathering / Port Scanning</td>
</tr>
<tr>
<td><strong>Test Goal</strong></td>
<td>Check that the services actually reachable in each network zone match the approved architecture / port matrix.</td>
</tr>
<tr>
<td><strong>Prerequisites</strong></td>
<td>Architecture / port-matrix document (the list of ports that are allowed per zone), IP address plan, approved test window.</td>
</tr>
<tr>
<td><strong>Command(s)</strong></td>
<td><p># Full TCP scan (all 65535 ports) for each target system / zone</p>
<p>sudo nmap -sS -sV -p- -T3 -oA cm001_&lt;target&gt; &lt;Target-IP or -Range&gt;</p>
<p># Additional UDP scan (top ports, because a full UDP scan is very slow)</p>
<p>sudo nmap -sU --top-ports 200 -oA cm001_&lt;target&gt;_udp &lt;Target-IP or -Range&gt;</p></td>
</tr>
<tr>
<td><strong>How to Read the Result</strong></td>
<td><ul>
<li><p>Compare the result list (open ports / services per host) against the target port matrix from the architecture.</p></li>
<li><p>Any open port or service that is not on the allowed list is a deviation and is noted in the report.</p></li>
</ul></td>
</tr>
<tr>
<td><strong>Evidence to Store</strong></td>
<td>Store cm001_&lt;target&gt;.nmap / .xml as the evidence file (project evidence folder).</td>
</tr>
<tr>
<td><strong>Acceptance Criteria</strong></td>
<td><strong>PASS if no unintended exposed services are found compared to the design; otherwise FAIL.</strong></td>
</tr>
</tbody>
</table>

## CM-002 — Network Segmentation (Cross-Segment Exposure)

<table>
<colgroup>
<col style="width: 24%" />
<col style="width: 76%" />
</colgroup>
<thead>
<tr>
<th><strong>Countermeasure</strong></th>
<th><strong>CM-002 — Network Segmentation (Cross-Segment Exposure)</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Reference</strong></td>
<td>STM: STM-5-7 | STG: STG1-3 | SVV: SVV-4b</td>
</tr>
<tr>
<td><strong>Kali Tool</strong></td>
<td>Nmap</td>
</tr>
<tr>
<td><strong>Category</strong></td>
<td>Information Gathering / Network Reachability</td>
</tr>
<tr>
<td><strong>Test Goal</strong></td>
<td>Prove that network zones (for example, following the Purdue model) cannot be reached across zones when they should not be.</td>
</tr>
<tr>
<td><strong>Prerequisites</strong></td>
<td>Zone / conduit model (IEC 62443-3-2), a test host with access to Zone A, an export of the firewall rules for comparison.</td>
</tr>
<tr>
<td><strong>Command(s)</strong></td>
<td><p># Run from a test host INSIDE Zone A against target systems in Zone B</p>
<p>sudo nmap -sS -Pn -p 1-65535 -e &lt;interface_zone_a&gt; -oA cm002_zoneA_to_zoneB &lt;Target-IP(s)_Zone_B&gt;</p>
<p># Optional: targeted check of the specific ports that are expected to be open (conduit ports)</p>
<p>sudo nmap -sS -Pn -p &lt;allowed_conduit_ports&gt; &lt;Target-IP_Zone_B&gt;</p></td>
</tr>
<tr>
<td><strong>How to Read the Result</strong></td>
<td><ul>
<li><p>If a host in Zone B answers on ports that are NOT allowed by the zone / conduit model, the segmentation is leaking (a bypass exists).</p></li>
<li><p>Also compare the result against the exported firewall rules (target vs. actual).</p></li>
</ul></td>
</tr>
<tr>
<td><strong>Evidence to Store</strong></td>
<td>cm002_zoneA_to_zoneB.nmap / .xml + a table comparing the firewall rules.</td>
</tr>
<tr>
<td><strong>Acceptance Criteria</strong></td>
<td><strong>PASS if no cross-segment exposure is found; FAIL if a segmentation bypass is possible.</strong></td>
</tr>
</tbody>
</table>

## CM-003 — Default / Weak Credentials

<table>
<colgroup>
<col style="width: 24%" />
<col style="width: 76%" />
</colgroup>
<thead>
<tr>
<th><strong>Countermeasure</strong></th>
<th><strong>CM-003 — Default / Weak Credentials</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Reference</strong></td>
<td>STM: STM-4 | STG: STG1-3 | SVV: SVV-4a</td>
</tr>
<tr>
<td><strong>Kali Tool</strong></td>
<td>Hydra</td>
</tr>
<tr>
<td><strong>Category</strong></td>
<td>Password Attacks</td>
</tr>
<tr>
<td><strong>Test Goal</strong></td>
<td>Check whether default or trivial login details are still active on any reachable login interface.</td>
</tr>
<tr>
<td><strong>Prerequisites</strong></td>
<td>A list of all login interfaces (Web/SSH/Telnet/FTP/DB) and a credential list from the manufacturer documentation. ONLY in the isolated test lab, never against production systems.</td>
</tr>
<tr>
<td><strong>Command(s)</strong></td>
<td><p># Example: web login (HTTP POST form)</p>
<p>hydra -L users.txt -P passwords.txt &lt;Target-IP&gt; http-post-form \</p>
<p>"/login:username=^USER^&amp;password=^PASS^:Login failed"</p>
<p># Example: SSH</p>
<p>hydra -L users.txt -P passwords.txt ssh://&lt;Target-IP&gt;</p></td>
</tr>
<tr>
<td><strong>How to Read the Result</strong></td>
<td><ul>
<li><p>Fill users.txt / passwords.txt in advance with known manufacturer defaults (for example admin/admin, root/&lt;serial number&gt;).</p></li>
<li><p>Every successful login with a default or trivial credential is a finding and is documented (account, interface, time).</p></li>
</ul></td>
</tr>
<tr>
<td><strong>Evidence to Store</strong></td>
<td>Hydra log (console output as .txt) + a screenshot of the successful login (if applicable).</td>
</tr>
<tr>
<td><strong>Acceptance Criteria</strong></td>
<td><strong>PASS if no default / weak credentials can be used; FAIL if access is possible.</strong></td>
</tr>
</tbody>
</table>

## CM-004 — RBAC / Privilege Escalation

<table>
<colgroup>
<col style="width: 24%" />
<col style="width: 76%" />
</colgroup>
<thead>
<tr>
<th><strong>Countermeasure</strong></th>
<th><strong>CM-004 — RBAC / Privilege Escalation</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Reference</strong></td>
<td>STM: STM-13 | STG: STG2-3 | SVV: SVV-4a</td>
</tr>
<tr>
<td><strong>Kali Tool</strong></td>
<td>OWASP ZAP</td>
</tr>
<tr>
<td><strong>Category</strong></td>
<td>Web Application Analysis</td>
</tr>
<tr>
<td><strong>Test Goal</strong></td>
<td>Prove that roles and permissions are enforced as specified and that no horizontal or vertical privilege escalation is possible.</td>
</tr>
<tr>
<td><strong>Prerequisites</strong></td>
<td>The role / permission matrix (target state), one test account per role, and the target application reachable through the ZAP proxy. OWASP ZAP is pre-installed in Kali (package: zaproxy).</td>
</tr>
<tr>
<td><strong>Command(s)</strong></td>
<td><p># 1) Start ZAP in the background (daemon); API key disabled for local test use</p>
<p>zaproxy -daemon -host 127.0.0.1 -port 8090 -config api.disablekey=true</p>
<p># 2) Route the browser through the ZAP proxy (127.0.0.1:8090) and click through</p>
<p># the application FOR EACH ROLE so that ZAP records all endpoints.</p>
<p># 3) Start an active scan for each recorded context via the official ZAP API</p>
<p>curl "http://127.0.0.1:8090/JSON/ascan/action/scan/?url=&lt;target_url&gt;"</p>
<p># 4) Export the HTML report via the API</p>
<p>curl "http://127.0.0.1:8090/OTHER/core/other/htmlreport/" -o cm004_&lt;role&gt;_report.html</p></td>
</tr>
<tr>
<td><strong>How to Read the Result</strong></td>
<td><ul>
<li><p>The core of this test is MANUAL: take the session/request of a low-privilege role and insert object IDs / endpoints that belong to a higher-privilege role (IDOR / privilege-escalation test). The active scan alone will not find this reliably.</p></li>
<li><p>Any successful action outside a role's intended permissions is a finding.</p></li>
</ul></td>
</tr>
<tr>
<td><strong>Evidence to Store</strong></td>
<td>ZAP report (HTML) per role + a test log with the target-vs-actual permission comparison.</td>
</tr>
<tr>
<td><strong>Acceptance Criteria</strong></td>
<td><strong>PASS if roles are correctly enforced and no privilege escalation is possible; otherwise FAIL.</strong></td>
</tr>
</tbody>
</table>

## CM-005 — TLS Configuration

<table>
<colgroup>
<col style="width: 24%" />
<col style="width: 76%" />
</colgroup>
<thead>
<tr>
<th><strong>Countermeasure</strong></th>
<th><strong>CM-005 — TLS Configuration</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Reference</strong></td>
<td>STM: STM-11 | STG: STG1-3 | SVV: SVV-4b</td>
</tr>
<tr>
<td><strong>Kali Tool</strong></td>
<td>SSLscan</td>
</tr>
<tr>
<td><strong>Category</strong></td>
<td>Information Gathering / SSL-TLS Analysis</td>
</tr>
<tr>
<td><strong>Test Goal</strong></td>
<td>Check that only secure protocol versions and cipher suites are active on all TLS endpoints.</td>
</tr>
<tr>
<td><strong>Prerequisites</strong></td>
<td>A list of all TLS endpoints (Host:Port).</td>
</tr>
<tr>
<td><strong>Command(s)</strong></td>
<td>sslscan &lt;Target-IP&gt;:&lt;Port&gt; --show-certificate &gt; cm005_&lt;target&gt;.txt</td>
</tr>
<tr>
<td><strong>How to Read the Result</strong></td>
<td><ul>
<li><p>Check the output for active SSLv2 / SSLv3 / TLS1.0 / TLS1.1 (insecure) and for weak ciphers (for example RC4, EXPORT, NULL).</p></li>
<li><p>Also check the certificate chain (validity, key length, signature algorithm).</p></li>
</ul></td>
</tr>
<tr>
<td><strong>Evidence to Store</strong></td>
<td>cm005_&lt;target&gt;.txt as the evidence file.</td>
</tr>
<tr>
<td><strong>Acceptance Criteria</strong></td>
<td><strong>PASS if only secure protocols / configuration are found; FAIL if a weak configuration or a cleartext fallback exists.</strong></td>
</tr>
</tbody>
</table>

## CM-006 — Hardening Validation

<table>
<colgroup>
<col style="width: 24%" />
<col style="width: 76%" />
</colgroup>
<thead>
<tr>
<th><strong>Countermeasure</strong></th>
<th><strong>CM-006 — Hardening Validation</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Reference</strong></td>
<td>STM: STM-4 | STG: STG1-3 | SVV: SVV-4a</td>
</tr>
<tr>
<td><strong>Kali Tool</strong></td>
<td>Lynis</td>
</tr>
<tr>
<td><strong>Category</strong></td>
<td>Vulnerability Analysis / System Audit</td>
</tr>
<tr>
<td><strong>Test Goal</strong></td>
<td>Check that the system is configured according to the defined hardening baseline (IEC 62443-4-2 / CIS reference).</td>
</tr>
<tr>
<td><strong>Prerequisites</strong></td>
<td>Root / admin access to the target system (local or over SSH) and the project's hardening-baseline checklist.</td>
</tr>
<tr>
<td><strong>Command(s)</strong></td>
<td><p># Run locally on the target system (Kali is the base; Lynis runs on any Linux target)</p>
<p>sudo lynis audit system --no-colors --logfile cm006_&lt;target&gt;.log --report-file cm006_&lt;target&gt;_report.dat</p></td>
</tr>
<tr>
<td><strong>How to Read the Result</strong></td>
<td><ul>
<li><p>Compare the Lynis hardening index and all 'Warnings' and 'Suggestions' against the project baseline.</p></li>
<li><p>Document each deviation individually (for example unnecessary services running, missing kernel hardening, open auto-start entries).</p></li>
</ul></td>
</tr>
<tr>
<td><strong>Evidence to Store</strong></td>
<td>cm006_&lt;target&gt;.log + cm006_&lt;target&gt;_report.dat + the completed baseline checklist.</td>
</tr>
<tr>
<td><strong>Acceptance Criteria</strong></td>
<td><strong>PASS if secure defaults are applied; FAIL if the configuration is insecure.</strong></td>
</tr>
</tbody>
</table>

## CM-007 — Debug / Service Interface Exposure

<table>
<colgroup>
<col style="width: 24%" />
<col style="width: 76%" />
</colgroup>
<thead>
<tr>
<th><strong>Countermeasure</strong></th>
<th><strong>CM-007 — Debug / Service Interface Exposure</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Reference</strong></td>
<td>STM: STM-2 | STG: STG1-3 | SVV: SVV-4b</td>
</tr>
<tr>
<td><strong>Kali Tool</strong></td>
<td>Nikto</td>
</tr>
<tr>
<td><strong>Category</strong></td>
<td>Web Application Analysis</td>
</tr>
<tr>
<td><strong>Test Goal</strong></td>
<td>Make sure that no debug, maintenance, or management interfaces are reachable during operation.</td>
</tr>
<tr>
<td><strong>Prerequisites</strong></td>
<td>The list of allowed web / management interfaces. For embedded devices, also plan hardware access for a UART/JTAG check (outside this tool).</td>
</tr>
<tr>
<td><strong>Command(s)</strong></td>
<td>nikto -h &lt;Target-IP or URL&gt; -output cm007_&lt;target&gt;.html -Format html</td>
</tr>
<tr>
<td><strong>How to Read the Result</strong></td>
<td><ul>
<li><p>Check the result list for debug endpoints, open admin / management panels, outdated server banners, and common default paths.</p></li>
<li><p>For non-web debug interfaces (for example a Telnet console), additionally use the Nmap service scan from CM-001.</p></li>
</ul></td>
</tr>
<tr>
<td><strong>Evidence to Store</strong></td>
<td>cm007_&lt;target&gt;.html as the evidence file.</td>
</tr>
<tr>
<td><strong>Acceptance Criteria</strong></td>
<td><strong>PASS if no debug / service interface is exposed; otherwise FAIL.</strong></td>
</tr>
</tbody>
</table>

## CM-008 — Patch Level / Known CVEs

<table>
<colgroup>
<col style="width: 24%" />
<col style="width: 76%" />
</colgroup>
<thead>
<tr>
<th><strong>Countermeasure</strong></th>
<th><strong>CM-008 — Patch Level / Known CVEs</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Reference</strong></td>
<td>STM: STM-12 | STG: STG2-3 | SVV: SVV-4a/4b</td>
</tr>
<tr>
<td><strong>Kali Tool</strong></td>
<td>OpenVAS (Greenbone Vulnerability Manager, GVM)</td>
</tr>
<tr>
<td><strong>Category</strong></td>
<td>Vulnerability Analysis</td>
</tr>
<tr>
<td><strong>Test Goal</strong></td>
<td>Prove that all known weaknesses in the software / firmware components in use are fixed or assessed.</td>
</tr>
<tr>
<td><strong>Prerequisites</strong></td>
<td>An up-to-date GVM feed (Community Feed), approval to scan the target system, and the current SBOM as a cross-check.</td>
</tr>
<tr>
<td><strong>Command(s)</strong></td>
<td><p># Start the GVM services (set up once per Kali instance)</p>
<p>sudo gvm-start</p>
<p># Create and start a scan in the web interface (https://127.0.0.1:9392),</p>
<p># or use the CLI (gvm-cli / gvm-tools) against the GMP API</p>
<p>gvm-cli --gmp-username admin --gmp-password &lt;pw&gt; socket --xml \</p>
<p>"&lt;create_target&gt;&lt;name&gt;cm008_&lt;target&gt;&lt;/name&gt;&lt;hosts&gt;&lt;target-ip&gt;&lt;/hosts&gt;&lt;/create_target&gt;"</p></td>
</tr>
<tr>
<td><strong>How to Read the Result</strong></td>
<td><ul>
<li><p>Filter the scan report by CVE ID, CVSS score, and whether the component is affected.</p></li>
<li><p>Compare open CVEs against the SBOM; note any finding that cannot be fixed with a reason (not reachable / compensating control) in the report and align with PSIRT.</p></li>
</ul></td>
</tr>
<tr>
<td><strong>Evidence to Store</strong></td>
<td>GVM scan report (PDF/XML export) + a CVE comparison list against the SBOM.</td>
</tr>
<tr>
<td><strong>Acceptance Criteria</strong></td>
<td><strong>PASS if the system is fully patched; FAIL if known CVEs remain open.</strong></td>
</tr>
</tbody>
</table>

## CM-009 — Load Behavior & Logging

<table>
<colgroup>
<col style="width: 24%" />
<col style="width: 76%" />
</colgroup>
<thead>
<tr>
<th><strong>Countermeasure</strong></th>
<th><strong>CM-009 — Load Behavior &amp; Logging</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Reference</strong></td>
<td>STM: STM-9 | STG: STG1-3 | SVV: SVV-5a</td>
</tr>
<tr>
<td><strong>Kali Tool</strong></td>
<td>Siege</td>
</tr>
<tr>
<td><strong>Category</strong></td>
<td>Stress / Load Test (Not pre-installed in every Kali build: sudo apt install siege)</td>
</tr>
<tr>
<td><strong>Test Goal</strong></td>
<td>Check that the system stays stable under a defined load and that events are logged without gaps.</td>
</tr>
<tr>
<td><strong>Prerequisites</strong></td>
<td>A defined load profile (normal/peak, number of concurrent users, duration) and system / application logging that is enabled and visible to the tester.</td>
</tr>
<tr>
<td><strong>Command(s)</strong></td>
<td><p># Example: 50 simulated users, duration 10 minutes, against a defined endpoint</p>
<p>siege -c 50 -t 10M -v &lt;Target-URL&gt; -l cm009_&lt;target&gt;.log</p></td>
</tr>
<tr>
<td><strong>How to Read the Result</strong></td>
<td><ul>
<li><p>Evaluate the Siege summary (availability, response times, error rate).</p></li>
<li><p>In parallel, check the system / application logs for completeness (no log gaps, no unhandled exceptions) and for any crash / restart events.</p></li>
</ul></td>
</tr>
<tr>
<td><strong>Evidence to Store</strong></td>
<td>cm009_&lt;target&gt;.log (Siege output) + a log extract from the target system for the test period.</td>
</tr>
<tr>
<td><strong>Acceptance Criteria</strong></td>
<td><strong>PASS if the system stays stable and logs are generated; FAIL on a crash or missing logging.</strong></td>
</tr>
</tbody>
</table>

## CM-010 — Fuzzing / Robustness

<table>
<colgroup>
<col style="width: 24%" />
<col style="width: 76%" />
</colgroup>
<thead>
<tr>
<th><strong>Countermeasure</strong></th>
<th><strong>CM-010 — Fuzzing / Robustness</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Reference</strong></td>
<td>STM: STM-8 | STG: STG1-3 | SVV: SVV-5b</td>
</tr>
<tr>
<td><strong>Kali Tool</strong></td>
<td>boofuzz</td>
</tr>
<tr>
<td><strong>Category</strong></td>
<td>Fuzzing Framework (Actively maintained fuzzing framework (successor to Sulley). Install: pip install boofuzz)</td>
</tr>
<tr>
<td><strong>Test Goal</strong></td>
<td>Prove that no crashes or undefined behavior occur when the system receives malformed or unexpected input.</td>
</tr>
<tr>
<td><strong>Prerequisites</strong></td>
<td>The protocol specification of the interface to be tested (for example Modbus, OPC UA, HTTP API) and an isolated test instance with crash monitoring / a watchdog. NEVER fuzz against production systems.</td>
</tr>
<tr>
<td><strong>Command(s)</strong></td>
<td><p># boofuzz fuzzing script (example skeleton, adapt to your protocol)</p>
<p># File: cm010_fuzz.py</p>
<p>from boofuzz import *</p>
<p>session = Session(target=Target(connection=TCPSocketConnection("&lt;Target-IP&gt;", &lt;Port&gt;)))</p>
<p>s_initialize("request")</p>
<p>s_string("USER") # field to fuzz</p>
<p>s_delim(" ")</p>
<p>s_string("value")</p>
<p>session.connect(s_get("request"))</p>
<p>session.fuzz()</p>
<p># Run it:</p>
<p>python3 cm010_fuzz.py</p></td>
</tr>
<tr>
<td><strong>How to Read the Result</strong></td>
<td><ul>
<li><p>Watch the target system during the run for crashes, hangs, or memory errors (boofuzz logs crashes automatically in its web interface at http://127.0.0.1:26000).</p></li>
<li><p>Log every crash with its payload, timestamp, and target state; then start a root-cause analysis.</p></li>
</ul></td>
</tr>
<tr>
<td><strong>Evidence to Store</strong></td>
<td>boofuzz database / session log (boofuzz-results/) + the crash log.</td>
</tr>
<tr>
<td><strong>Acceptance Criteria</strong></td>
<td><strong>PASS if no crash / undefined behavior occurs; FAIL if an</strong> <strong>exploitable issue is found.</strong></td>
</tr>
</tbody>
</table>

# 5. Documenting the Results

For every test performed, record the following per CM in the test log (or the project test plan / test-management tool):

- CM ID, tester, date, and the tool used including its version

- Where the evidence is stored / the evidence file name

- Result: PASS / FAIL according to the acceptance criteria

- If FAIL: a description of the finding, its severity (for example CVSS), and the recommended action

## Escalation on FAIL

Every FAIL is reported to the Test Manager (TM) and fed back into the risk analysis. The Test Manager, together with the security owner (GSS), decides whether a finding must be fixed before release or whether it can be accepted through a compensating control / exception (with a documented reason) — mirroring the final review step in the Cybersecurity Test Process.
