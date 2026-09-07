**Step 1: Theoretical Validation**

- Requirement & Mapping: Mapping from the EU Machinery Regulation to the IEC 62443-4-2 Component Requirement (CR).

- Assets & STRIDE: Evaluate identified Target Assets and STRIDE (threats). Are they plausible for this specific device and requirement?

- Security Functions & Gaps: Cross-reference my Security Functions and Gaps with the device documentation. Are the mitigations accurately described? Are the identified gaps realistic?

Step 2: Methodological Test Planning

- Based on the validated Security Functions and Gaps, derive concrete test scenarios to verify the mitigations or prove the gaps.

- Scientific Justification: Justify the chosen test methods using established technical guidelines (e.g., NIST SP 800-115 for network/port scanning, MITRE ATT&CK for ICS for active exploitation/sniffing, or OWASP for the IoT-Core web interface).

- IEC 62443-4-1 Categorization (SVV): Assign each test to the correct SVV category:

  - SVV-1 (Requirements-based Testing): Verifying functional implementation in normal operation.

  - SVV-2 (Threat Mitigation Testing): Verifying the effectiveness of countermeasures under attack/fault conditions.

  - SVV-3 (Vulnerability Testing): Searching for known vulnerabilities or open attack surface (e.g., Nmap).

  - SVV-4 (Penetration Testing): Active exploitation or protocol manipulation (e.g., Scapy, Fuzzing).

Step 3: Two-Level Test Catalog Generation

Generate the final test catalog entries for the planned tests. Each test must be structured in two levels:

- Level 1: Abstract Test Scenario (Product-neutral).

> Must include: Test Case ID, Traceability (RQ -\> CR -\> Asset), Target Threat, SVV Category, Test Objective, Abstract Test Steps, and strict Pass/Fail Criteria.

- Level 2: Concrete Test Execution (Specific to my test environment).

> Must include: Referenced Test Case ID, Hardware/Network Setup (Kali, Kali 192.168.0.80 (Port 3), Target IPs), Concrete Tools (Nmap, Wireshark, Scapy, etc.), Specific Commands/Scripts to be executed, and placeholders for the Result and Evidence (e.g., PCAP, XML logs).

<span class="mark">NV1</span> - Direct access (IP-based): Kali resp. the laptop communicate as a regular participant directly through the switch with SRIO and/or PLC (normal switching/routing). No extension needed. Covers all IoT-Core/HTTP-based tests as well as any test where Kali itself acts as a (unauthorized) communication partner.

<span class="mark">NV2</span> - Passive tap (mirror/SPAN): For traffic that is NOT addressed to Kali (e.g. the PROFINET/PROFIsafe cyclic traffic between PLC and SRIO), this traffic must be made visible to Kali. Prerequisite: switch 192.168.0.91 supports a mirror/SPAN function (mirror ports 1+2 🡪 3) - verify this in the switch management interface before testing. IMPORTANT: ARP spoofing does NOT work here, since PROFINET/PROFIsafe is not an IP protocol (EtherType 0x8892) and devices identify each other via DCP/MAC addresses rather than ARP.

<span class="mark">NV3</span> - Inline bridge (active MITM): For tests that require genuinely suppressing/replacing frames in real time (e.g. taking over the consecutive number, TC-RQ001-04), Kali must be physically inserted between SRIO and the switch: disconnect the SRIO cable from switch port 2 and connect it instead to Kali's internal/onboard network card; plug the USB3 Gigabit dongle (previously Kali↔switch) into switch port 2. Kali then acts transparently as a Linux bridge („ip link … type bridge“) with an optional NFQUEUE/ebtables hook to selectively manipulate individual frames before forwarding. This variant is the only notable hardware extension - it needs no additional device, since it reuses the laptop's existing second network interface (onboard NIC) together with the already-available USB dongle.

USB3-zu-Gigabit-Ethernet-Dongle von kali zu switch

switch 192.168.0.91, eine sps 192.168.0.1, das safe remote i/o 192.168.0.2, den kali linux rechner mit 192.168.0.80 und meinen firmenlaptop mit 192.168.0.7.

sps ist mit port1 ,

safe remote i/o ist mit port2,

kali-rechner mit port3 und laptop mit port4 vom switch verbunden

**REQUIREMENT 1**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-001

- **MVO Requirement Text:** The system shall be designed so that the connection of another device, including any remote device that communicates with it, does not lead to a hazardous situation.

- **IEC 62443-4-2 CR Mapping:** CR 3.1, CR 3.1 RE (1), CR 1.2 (secondary), CR 3.6

- **Target Assets:** Asset A (Trusted Safety Function), Asset C (Integrity/Authenticity of Safety-Relevant Process Data), (Asset E (Safety Monitoring)) Asset F (Domain Separation),

- **STRIDE:** Spoofing, Tampering, Denial of Service

- **Security Function (Mitigation):**

  - Black-channel architecture: COM (CPU3) is non-safety (QM) and only tunnels the FSCP frame; the safety logic and the PROFIsafe consumer run on the SCPU (SRIO categorization, black-channel principle).

  - Consumer-ID / F_Dest_Add check: Under Address Type 1 the PROFIsafe CRC is seeded with the F-codename (incl. F_Dest_Add). A telegram destined for a different address therefore fails CRC at the real consumer (SRIO-7830, SRIO-10807, SRIO-15799).

  - 4-byte CRC + CRC-Seed24/32: Detects accidental/most malicious payload modification of the cyclic frame (SRIO-2998).

  - F_WD_Time watchdog + consecutive number 🡪 passivation (CR 3.6): Loss/staleness of the legitimate producer beyond F_WD_Time (default 150 ms, SRIO-1210/1857) drives channel- or device-granular passivation (SRIO-9021); re-integration requires explicit acknowledgement.

  - Environmental control (CCSC-2): “Safe zone behind a firewall” (SRIO-9402). This is an organisational/compensating control, not a device function.

- **Identified Gap:**

  - G-1 (device-level, TESTABLE): Freedom-from-hazard against a connecting device is a device function to be positively demonstrated: a mis-addressed or CRC-invalid telegram is rejected, and loss of the legitimate channel resolves to passivation.

  - G-2 (environmental, boundary only): Authenticity ultimately rests on the black-channel assumption. Because F_Source_Add is not checked under Address Type 1 and CRC-Seed24/32 is a public, non-secret value in the GSD, the CRC is not a cryptographic authenticity barrier.

> Technical refinement: a naive side-injection of a valid replayed frame while the genuine producer is still active does not succeed, two producers collide on the consecutive number, and the consumer passivates. The genuine residual risk is therefore a full in-path MITM that suppresses the legitimate producer and takes over the consecutive number, not simple parallel injection. Device-level testing can only characterize this boundary; it cannot close it.

**Step 2: Methodological Test Planning**

<table>
<colgroup>
<col style="width: 4%" />
<col style="width: 42%" />
<col style="width: 20%" />
<col style="width: 22%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td><p>Baseline PROFIsafe exchange with correct F_Dest_Add;</p>
<p>verify qualifier = good, outputs follow control byte</p></td>
<td>Functional implementation of CR 3.1 in normal operation</td>
<td>Requirements-based verification</td>
<td>SVV-1</td>
</tr>
<tr>
<td>2</td>
<td>Enumerate what a connecting device reaches on the DUT (services/ports on the non-safety path) vs. the approved matrix</td>
<td>Attack-surface of the non-safety path = evidence for Gap G-2</td>
<td><p>NIST SP 800-115 §4.2/4.3;</p>
<p>ifm framework CM-001 (Nmap)</p></td>
<td>SVV-3</td>
</tr>
<tr>
<td>3</td>
<td><p>CRC-mismatch injection:</p>
<p>(a) mis-addressed telegram,</p>
<p>(b) bit-flipped payload/CRC</p></td>
<td>Effectiveness of CRC + consumer-ID verification 🡪 passivation</td>
<td><p>MITRE ATT&amp;CK for ICS T0842/1692.002;</p>
<p>NIST SP 800-115 §5.2</p></td>
<td>SVV-4</td>
</tr>
<tr>
<td>4</td>
<td>In-path MITM boundary: suppress genuine producer, take over consecutive number, inject valid-CRC frame</td>
<td>Demonstrates the true residual boundary of G-2 (documented, not scored as device FAIL)</td>
<td>MITRE ATT&amp;CK for ICS T0830; PROFIsafe theory</td>
<td>SVV-4</td>
</tr>
<tr>
<td>5</td>
<td><p>Disrupt the black channel &gt; F_WD_Time;</p>
<p>observe passivation + acknowledged re-integration</p></td>
<td>Connection-induced disruption resolves to the safe state (fail-safe outcome of RQ-001)</td>
<td>MITRE ATT&amp;CK for ICS: T0814; PROFIsafe watchdog theory</td>
<td>SVV-2</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ001-01 - Baseline Safety Exchange</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-001 🡪 CR 3.1 / CR 3.6 🡪 Asset A, Asset C</td>
</tr>
<tr>
<td>Target Threat</td>
<td>N/A, functional verification (reference baseline)</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Show that with correct F_Dest_Add and valid CRC the consumer exchanges cyclic data, qualifier=good, DO follows the control byte, no passivation.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Configure controller with matching F_Dest_Add; establish safe connection.</p></li>
<li><p>Toggle a safe input and command a safe output.</p></li>
<li><p>Observe qualifier + DO read-back over a sustained interval.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if the qualifier remains good throughout, outputs mirror the commanded control data, and no passivation occurs under nominal conditions.</p>
<p>FAIL if the qualifier becomes bad, or any output/command mismatch is observed.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ001-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>TIA laptop against PLC and SRIO</td>
</tr>
<tr>
<td>Tools</td>
<td>TIA Online &amp; Diagnose;</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>TIA watch table monitoring F-DI/F-DO value + PROFIsafe qualifier;</p>
<p># toggle DI button, command DO from PLC, record DO read-back.</p></td>
</tr>
<tr>
<td>Result</td>
<td>TIA watch table monitoring F-DI/F-DO value + PROFIsafe qualifier;</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ001-02 - Attack-Surface Enumeration on the Non-Safety Path</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-001 🡪 CR 3.1 🡪 Asset F</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Spoofing / Tampering 🡪 Domain Separation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Enumerate services a connecting device reaches on the non-safety path; compare to the approved port matrix.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>From the position of a connecting device, perform a full service/port discovery against the device.</p></li>
<li><p>Perform service and version identification on any responding port.</p></li>
<li><p>Compile the reachable-service list.</p></li>
<li><p>Compare the list against the approved design matrix.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if only design-approved services are reachable.</p>
<p>FAIL if any service outside the approved matrix is reachable. (Confidentiality of an exposed service is recorded as a defense-in-depth observation; EN 50742 FR4 target = none.)</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ001-02</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Kali on P3.</td>
</tr>
<tr>
<td>Tools</td>
<td>Nmap (ifm CM-001), Nikto (CM-007)</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>sudo nmap -sS -sV -p- -T3 -oA cm_rq001-02_tcp_srio $SRIO</p>
<p>sudo nmap -sU --top-ports 200 -oA cm_rq001-02 _udp_srio $SRIO</p>
<p>nikto -h http://$SRIO -output cm_rq001-02 _srio.html -Format html</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Port 80/tcp open</p>
<p>Port 161/udp open snmp, Port 49152/udp open/filtered unknown</p>
<p>HTMl-Nikto Report?:</p>
<p>Risk?: Spring Boot Actuator endpoint exposed (valid JSON response)?</p></td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ001-03 - Integrity-Value Mismatch Rejection</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-001 🡪 CR 3.1 (+RE1) / CR 3.6 🡪 Asset A, Asset C</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Spoofing + Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td>Prove that a safety telegram whose consumer identity / integrity-check value does not match the legitimate parameters is rejected, resolving to the safe state rather than to an uncommanded output.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>With cyclic safety traffic running, inject crafted telegrams that violate the consumer identity or the integrity-check value (mis-addressed telegram; bit-flipped payload/integrity value).</p></li>
<li><p>Observe the qualifier, output state, and diagnostics.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if the device rejects the crafted telegrams and either continues on legitimate traffic or passivates to the safe state (outputs de-energized, qualifier bad), with no uncommanded actuation.</p>
<p>FAIL if any crafted telegram causes an uncommanded or hazardous output change.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ001-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV2 (mirror ports 1+2 🡪 3 on switch)</td>
</tr>
<tr>
<td>Tools</td>
<td>Wireshark/tshark, Scapy, TIA Portal (Online &amp; Diagnostics).</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># Step 0: on the switch web/CLI management interface, configure port mirroring</p>
<p># Source ports: 1 (PLC) + 2 (SRIO); Destination port: 3 (Kali).</p>
<p># Step 1: on the TIA laptop, establish the normal PROFIsafe connection</p>
<p># TIA Portal &gt; Online &gt; 'Go online' &gt; Watch table with F-DI1/F-DI2/F-DO1/F-DO2 + Qualifier bits</p>
<p># Step 2: on Kali, identify the dongle interface</p>
<p>ip a</p>
<p># assume eth1 for the remaining commands</p>
<p># Step 3: capture cyclic PROFINET/PROFIsafe traffic (EtherType 0x8892)</p>
<p>sudo tshark -i eth1 -f "ether proto 0x8892" -w cm_rq001-03_baseline.pcapng</p>
<p># let it run ~30s, then Ctrl+C</p>
<p># Step 4: identify the SRIO's MAC address from the capture</p>
<p>tshark -r cm_rq001-03_baseline.pcapng -T fields -e eth.src -e eth.dst | sort -u</p>
<p># Step 5: open the capture in Wireshark and note the byte offsets of the</p>
<p># F_Dest_Add-related area and the 4-byte CRC field (per PROFIsafe frame layout,</p>
<p>wireshark cm_rq001-03_baseline.pcapng &amp;</p>
<p># Step 6: build the injection script cm_rq001-03_inject.py</p>
<p>cat &gt; cm_rq001-03_inject.py &lt;&lt; 'PYEOF'</p>
<p>from scapy.all import Ether, Raw, sendp</p>
<p>iface = "eth1"</p>
<p>target_mac = "AA:BB:CC:DD:EE:FF" # &lt;- replace with the SRIO MAC found in Step 4</p>
<p># (a) mis-addressed telegram: copy a real captured payload and flip a byte in</p>
<p># the F_Dest_Add-related region identified in Step 5</p>
<p>bad_addr_payload = bytes.fromhex("REPLACE_WITH_MODIFIED_HEX_PAYLOAD")</p>
<p>sendp(Ether(dst=target_mac, type=0x8892)/Raw(load=bad_addr_payload),</p>
<p>iface=iface, count=5, inter=0.05)</p>
<p># (b) bit-flipped payload with stale (unmodified) CRC</p>
<p>flipped_payload = bytes.fromhex("REPLACE_WITH_BITFLIPPED_HEX_PAYLOAD")</p>
<p>sendp(Ether(dst=target_mac, type=0x8892)/Raw(load=flipped_payload),</p>
<p>iface=iface, count=5, inter=0.05)</p>
<p>PYEOF</p>
<p># Step 7: run the injection</p>
<p>sudo python3 cm_rq001-03_inject.py</p>
<p># Step 8: on the TIA laptop, observe the watch table (Qualifier bits) and</p>
<p># Online &amp; Diagnostics &gt; Diagnostics buffer for any reaction</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Expected PASS</p>
<p>- telegrams with a wrong destination address or an invalid/stale CRC are rejected by the SRIO (the qualifier stays „good“ based on the legitimate traffic; no unauthorized state change occurs).</p>
<p>Evidence: cm_rq001-03_baseline.pcapng, cm_rq001-03_inject.py, TIA screenshot of the watch table / diagnostics buffer.</p></td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ001-04 - In-Path Adversary-in-the-Middle Boundary</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-001 🡪 CR 3.1 (+RE1) 🡪 Asset C, Asset F</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Spoofing + Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td>Characterize the true residual boundary of the authenticity mitigation: because authenticity ultimately rests on the black-channel assumption, determine whether an in-path adversary that suppresses the legitimate producer and assumes control of the consecutive-number sequence can present a telegram the consumer cannot distinguish from a legitimate one.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Insert a controlled in-path element between the legitimate producer and the safe consumer.</p></li>
<li><p>Suppress the legitimate producer's telegrams.</p></li>
<li><p>Continue the consecutive-number sequence and inject a fully valid-integrity telegram carrying modified process data.</p></li>
<li><p>Observe whether the consumer accepts the substituted stream or detects the takeover</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Boundary-characterization test (not scored as a device FAIL).</p>
<p>Expected: a full in-path takeover is accepted, demonstrating that authenticity depends on the black-channel/environmental assumption; this is documented as a residual risk covered by the network-segregation control.</p>
<p>A device FAIL is recorded only if a parallel (non-in-path) injection, without producer suppression, is accepted, which would indicate a genuine consumer-side defect.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ001-04</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV3 (inline bridge)</td>
</tr>
<tr>
<td>Tools</td>
<td>Linux bridging (iproute2), ebtables + NetfilterQueue, Scapy (pip install NetfilterQueue scapy), Wireshark.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># Step 1: build a transparent bridge on Kali</p>
<p>sudo ip link add name br0 type bridge</p>
<p>sudo ip link set eth0 master br0 # onboard NIC, now connected to SRIO</p>
<p>sudo ip link set eth1 master br0 # USB dongle, now connected to switch port 2</p>
<p>sudo ip link set eth0 up</p>
<p>sudo ip link set eth1 up</p>
<p>sudo ip link set br0 up</p>
<p># Verify transparency first: TIA watch table must show the PROFIsafe connection</p>
<p># running unmodified through the bridge before proceeding.</p>
<p># Step 2: baseline capture of the consecutive-number sequence + CRC</p>
<p>sudo tshark -i br0 -f "ether proto 0x8892" -w cm_rq001-04_baseline.pcapng</p>
<p># Step 3: redirect frames of interest into userspace via NFQUEUE</p>
<p>sudo ebtables -A FORWARD -p 0x8892 -j NFQUEUE --queue-num 0</p>
<p># Step 4: NFQUEUE handler cm_rq001-04_mitm.py: drop the legitimate</p>
<p># producer's frames and inject a replacement frame with the continued</p>
<p># consecutive number and a freshly recomputed, valid CRC</p>
<p>cat &gt; cm_rq001-04_mitm.py &lt;&lt; 'PYEOF'</p>
<p>from netfilterqueue import NetfilterQueue</p>
<p>from scapy.all import Ether, Raw</p>
<p>last_seq = None # track/continue the consecutive number here</p>
<p>def callback(pkt):</p>
<p>global last_seq</p>
<p>frame = Ether(pkt.get_payload())</p>
<p># TODO: parse consecutive number + process data from frame per</p>
<p># PROFIsafe layout (SRIO-2998); build 'modified' with continued seq</p>
<p># number and process data changed, then recompute the 4-byte CRC</p>
<p># using the documented algorithm + CRC-Seed24/32 (public, from GSD file)</p>
<p>modified = frame # placeholder - replace with actually modified frame</p>
<p>pkt.set_payload(bytes(modified))</p>
<p>pkt.accept() # 'accept' here re-injects the REPLACED frame;</p>
<p># use pkt.drop() on the original producer frame in a</p>
<p># separate rule/queue to fully suppress it</p>
<p>nfqueue = NetfilterQueue()</p>
<p>nfqueue.bind(0, callback)</p>
<p>try:</p>
<p>nfqueue.run()</p>
<p>except KeyboardInterrupt:</p>
<p>pass</p>
<p>PYEOF</p>
<p>sudo python3 cm_rq001-04_mitm.py</p>
<p># Step 5: observe whether the consumer (SRIO) accepts the substituted</p>
<p># stream (TIA watch table stays 'good') or detects the takeover (qualifier</p>
<p># bad / diagnostic alarm)</p>
<p># Step 6: cleanup</p>
<p>sudo ebtables -D FORWARD -p 0x8892 -j NFQUEUE --queue-num 0</p>
<p>sudo ip link set br0 down</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Boundary-characterization test (not scored as a device FAIL).</p>
<p>Expected: the takeover is accepted as long as the legitimate producer is fully suppressed (confirms the documented residual-risk statement G-2 for RQ-001).</p>
<p>If the takeover is not accepted despite full suppression, this must be investigated and documented separately as a positive finding.</p></td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ001-05 - Channel-Disruption Watchdog Response</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-001 🡪 CR 3.1 / CR 3.6 🡪 Asset A, Asset C, Asset E</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Denial of Service</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-2</td>
</tr>
<tr>
<td>Objective</td>
<td>Verify that interruption of the safe channel beyond the watchdog time causes passivation to the defined safe state, and that re-integration requires explicit acknowledgement, i.e., a connection-induced disruption resolves to a safe, not hazardous, state.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Reach normal operating state with a known watchdog time.</p></li>
<li><p>Interrupt the safe-communication path for longer than the watchdog time.</p></li>
<li><p>Measure the time to reach the safe state;</p></li>
</ol>
<blockquote>
<p>confirm outputs de-energized and qualifier bad.</p>
</blockquote>
<ol start="4" type="1">
<li><p>Restore the link; confirm no automatic re-integration occurs without acknowledgement.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if passivation occurs within the specified device response time, outputs are de-energized, the qualifier is bad, and re-integration is gated by acknowledgement.</p>
<p>FAIL if outputs remain energized beyond the watchdog time, or the device auto-re-integrates without acknowledgement.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ001-05</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1</td>
</tr>
<tr>
<td>Tools</td>
<td>TIA Online &amp; Diagnostics, Wireshark timestamps</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># Step 1: baseline</p>
<p># TIA Portal: confirm SRIO is in Operate and note F_WD_Time (default 150 ms,</p>
<p># SRIO-1857 / GSD F_WD_Time) under: Hardware configuration &gt; SRIO module &gt;</p>
<p># Properties &gt; PROFIsafe &gt; F-Parameters</p>
<p># Step 2: interrupt the communication path for &gt; F_WD_Time</p>
<p># physically disconnect the SRIO's fieldbus cable for ~2s.</p>
<p># Step 3: in the TIA watch table, record the exact time of passivation</p>
<p># TIA Portal &gt; Online &amp; Diagnostics &gt; Watch table:</p>
<p># - Qualifier bit -&gt; bad</p>
<p># - F-DO outputs -&gt; Low</p>
<p># TIA Portal &gt; Online &amp; Diagnostics &gt; Diagnostics buffer: note the connection-loss entry</p>
<p># Step 4: restore the connection</p>
<p># Re-enable the port / reconnect the cable.</p>
<p># Step 5: verify that re-integration requires explicit acknowledgement</p>
<p># TIA watch table: confirm the module does NOT automatically return to Operate;</p>
<p># send the acknowledge command (ChF_ACK, Control-Byte Bit 6) from the PLC</p>
<p># program / watch table, then confirm the module returns to Operate.</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Expected PASS</p>
<p>passivation occurs within the specified device response time, outputs de-energized/Low, qualifier bad; re-integration only after acknowledgement.</p>
<p>Evidence: TIA diagnostics-buffer export, timestamps from switch log or stopwatch measurement.</p></td>
</tr>
</tbody>
</table>

**REQUIREMENT 2**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-002

- **MVO Requirement Text:** The system shall protect hardware components transmitting signal or data relevant to connection or access to safety-critical software against corruption, whether accidental or intentional.

- **IEC 62443-4-2 CR Mapping :** CR 3.1, CR 3.1 RE (1), CR 3.4, EDR 3.11

- **Target Assets:** C (Transmitted Safety Frame), G (physical F-address interface)

- **STRIDE:** (Spoofing,) Tampering

- **Security Function (Mitigation):**

  - 4-byte CRC + CRC-Seed24/32: Frame-level accidental-corruption detection (SRIO-2998).

  - iParCRC (UINT32) + F_ParCRC (UINT16): Parameter-transfer protection; a mismatch is rejected as EC3 (SRIO-2998, SRIO-8574/8575, SRIO-12627).

  - Certified CRC-Tool (T2, TÜV Süd): iParCRC generated by an externally certified off-line tool (SRIO-9023).

  - Rotary Switch 192.168.0.91 read only at Init: A runtime change of the F-address is ignored until reboot (SRIO-8803, SRIO-10812), a temporal protection of the running safety function.

  - Physical seals: Plastic/metal sleeve seals on the Switch 192.168.0.91 housing (SRIO-11000/11001), passive resistance only.

- **Identified Gap:**

  - G-1: The CRC is a checksum, not a MAC. With a public, non-secret seed an attacker who modifies the payload and recomputes a valid CRC is not detected, protection against accidental but not intentional corruption. (prEN 50742 §7.4.3.4 would require SRSL3 cryptographic integrity for this

  - G-2: Same limitation for iParCRC/F_ParCRC. F_ParCRC is only 16-bit (a 2¹⁶ space, no forgery resistance); iParCRC is 32-bit but still non-cryptographic and recomputable from the public layout.

  - G-3: The seals provide passive, visual tamper-resistance only; there is no active tamper-detection that triggers a protective response (EDR 3.11 detection limb unmet). The one genuine device-level protection is temporal (Switch 192.168.0.91 read only at Init): the running address cannot be corrupted live, but the stored/next-boot address can be, with the seal as the sole barrier.

**Step 2: Methodological Test Planning**

<table>
<colgroup>
<col style="width: 4%" />
<col style="width: 42%" />
<col style="width: 20%" />
<col style="width: 22%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td><p>Present a configuration with a wrong iParCRC / F_ParCRC;</p>
<p>verify rejection (EC3, stays in Parametrization)</p></td>
<td>Functional CR 3.4 in normal operation</td>
<td>Requirements-based verification</td>
<td>SVV-1</td>
</tr>
<tr>
<td>2</td>
<td>Bit-flip the payload leaving CRC stale 🡪 CRC mismatch 🡪 passivation</td>
<td>Effectiveness of the CRC countermeasure under fault</td>
<td><p>NIST SP 800-115 §5.2;</p>
<p>PROFIsafe CRC theory</p></td>
<td>SVV-2</td>
</tr>
<tr>
<td>3</td>
<td>Recompute a VALID CRC over MODIFIED process data and inject</td>
<td>Proves G-1: intentional corruption undetected</td>
<td><p>MITRE ATT&amp;CK for ICS T0836;</p>
<p>NIST SP 800-115 §5.2</p></td>
<td>SVV-4</td>
</tr>
<tr>
<td>4</td>
<td>F_ParCRC forgery feasibility, analyse the 16-bit F_ParCRC / 32-bit iParCRC forgeability</td>
<td>Proves G-2: parameter CRCs are not authentication</td>
<td>NIST SP 800-115 §4.3</td>
<td>SVV-3</td>
</tr>
<tr>
<td>5</td>
<td><p>Physical tamper-resistance: remove seal, alter rotary switch, reboot;</p>
<p>(a) runtime change is ignored</p>
<p>(b) the next-boot address can be corrupted</p></td>
<td>Proves G-3 (resistance-only physical protection)</td>
<td><p>OWASP ISTG ISTG-PHY;</p>
<p>EDR 3.11</p></td>
<td>SVV-4</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ002-01 - Parameter-CRC Rejection (iParCRC / F_ParCRC)</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-002 🡪 CR 3.4 🡪 Asset C</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that the device validates the safety parameter set and rejects a configuration whose parameter integrity values do not match, remaining in the safe (parametrization) state.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Establish a valid baseline configuration.</p></li>
<li><p>Present a configuration whose parameter integrity value is deliberately incorrect.</p></li>
<li><p>Observe device state, diagnostics, and qualifiers.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if the mismatch triggers a configuration error, the device remains in the safe/parametrization state, qualifiers remain bad, and no operating handshake completes.</p>
<p>FAIL if a configuration with a mismatched integrity value is accepted.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ002-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>PLC with TIA Portal, SRIO, TIA laptop</td>
</tr>
<tr>
<td>Tools</td>
<td>TIA Portal, ifm-CRC-Tool</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Baseline: parametrize a valid iPar set.</p>
<p># TIA Portal &gt; Hardware/network view &gt; select AL400S &gt;</p>
<p># Properties &gt; Module parameters (e.g. Filter F-DI 1 = 10 ms).</p>
<p># 2. Calculate the iParCRC:</p>
<p># Right-click the module &gt; 'Start device tool' &gt; select 'ifm-CRC-Tool' &gt; Start</p>
<p># In the ifm-CRC-Tool: compare the displayed parameter list against the TIA</p>
<p># configuration; if correct, check 'I have checked all device parameters.</p>
<p># They are set correctly.' &gt; the tool computes F_iPar_CRC (hex) &gt;</p>
<p># click 'Copy to clipboard'.</p>
<p># Paste the value into: Properties &gt; PROFIsafe &gt; F-Parameters &gt; F_iPar_CRC</p>
<p># 3. Compile and download: Project &gt; Compile (Ctrl+Shift+B) &gt; Online &gt; Download</p>
<p># to device (Ctrl+D). Confirm the connection establishes successfully.</p>
<p># 4. NOW deliberately break it: in TIA, manually change ONE hex digit of</p>
<p># F_iPar_CRC (Properties &gt; PROFIsafe &gt; F-Parameters &gt; F_iPar_CRC) WITHOUT</p>
<p># recalculating it via the ifm-CRC-Tool.</p>
<p># 5. Compile (Ctrl+Shift+B) and download again (Ctrl+D); observe the</p>
<p># connection-establishment behaviour in Online &amp; Diagnostics.</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Expected PASS the configuration with the incorrect iParCRC/F_ParCRC is rejected (EC3), the device remains in Parametrization, qualifier stays bad.</p>
<p>Evidence: TIA diagnostic message / rejection code (screenshot).</p></td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ002-02 - Stale Integrity-Value Fault Detection</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-002 🡪 CR 3.1 🡪 Asset C</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-2</td>
</tr>
<tr>
<td>Objective</td>
<td>Verify the effectiveness of the transmission integrity-check countermeasure by modifying payload while leaving the integrity value stale, producing a detectable mismatch that resolves to passivation.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Establish cyclic safety traffic.</p></li>
<li><p>Modify a payload field while leaving the integrity value unchanged.</p></li>
<li><p>Observe detection and the resulting device state.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if the mismatch is detected and the device passivates (outputs de-energized, qualifier bad) or continues on legitimate traffic without acting on the corrupted data.</p>
<p>FAIL if the modified payload is acted upon.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ002-02</td>
</tr>
<tr>
<td>HW/Network</td>
<td>baseline capture via NV2, injection via NV1</td>
</tr>
<tr>
<td>Tools</td>
<td>Wireshark/tshark, Scapy.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Baseline capture of one PROFIsafe cyclic telegram (as in TC-RQ001-03,</p>
<p># steps 1-5), identify the byte offset of the process-data field (e.g.</p>
<p># digital-output channel bits) and of the 4-byte CRC field.</p>
<p># 2. Build cm_rq002-02_inject.py:</p>
<p>cat &gt; cm_rq002-02_inject.py &lt;&lt; 'PYEOF'</p>
<p>from scapy.all import Ether, Raw, sendp</p>
<p>iface = "eth1"</p>
<p>target_mac = "AA:BB:CC:DD:EE:FF" # &lt;- SRIO MAC</p>
<p># take a captured legitimate payload, flip one bit in the process-data</p>
<p># field, but leave the CRC bytes UNCHANGED (stale CRC)</p>
<p>payload = bytearray.fromhex("REPLACE_WITH_CAPTURED_PAYLOAD_HEX")</p>
<p>payload[&lt;PD_BYTE_OFFSET&gt;] ^= 0x01 # flip one bit in the process-data byte</p>
<p>sendp(Ether(dst=target_mac, type=0x8892)/Raw(load=bytes(payload)),</p>
<p>iface=iface, count=5, inter=0.05)</p>
<p>PYEOF</p>
<p>sudo python3 cm_rq002-02_inject.py</p>
<p># 3. Observe TIA watch table (Qualifier, outputs) and Wireshark for the</p>
<p># device's reaction.</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Expected PASS: the CRC mismatch is detected, telegram discarded or passivation triggered; no reaction to the manipulated process data.</p>
<p>Evidence: PCAP showing the mismatch, TIA diagnostics excerpt.</p></td>
</tr>
</tbody>
</table>

**TC-RQ002-03 - Valid-Integrity-Value Injection over Modified Data**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-002 🡪 CR 3.1 (+RE1) 🡪 Asset C</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate the central residual risk: because the transmission integrity value is a non-secret checksum, an attacker who modifies the process data and recomputes a matching integrity value produces a telegram the consumer cannot distinguish from a legitimate one, protection against accidental but not intentional corruption.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Capture a legitimate telegram and extract the parameters needed to reproduce the integrity value.</p></li>
<li><p>Modify the process data.</p></li>
<li><p>Recompute a valid integrity value over the modified data.</p></li>
<li><p>Inject and observe the qualifier and outputs.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Gap-characterization test.</p>
<p>Expected: the recomputed-integrity telegram is accepted, confirming that authenticity depends on the black channel (residual risk documented).</p>
<p>A positive finding (rejection) would indicate an undocumented cryptographic authenticity control and must be investigated.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ002-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV3</td>
</tr>
<tr>
<td>Tools</td>
<td>Scapy, Wireshark; own implementation of the PROFIsafe CRC computation (4-byte CRC, CRC-Seed24/32, documented in the GSD file / PROFIsafe specification)</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Capture a legitimate telegram (as in TC-RQ001-03, Step 3-4).</p>
<p># 2. Modify the process-data field.</p>
<p># 3. Recompute the 4-byte CRC over the modified data using the documented</p>
<p># algorithm and the public CRC-Seed24/32 (from the GSDML file):</p>
<p>cat &gt; cm_rq002-03_crc_recalc.py &lt;&lt; 'PYEOF'</p>
<p># implement the PROFIsafe CRC algorithm here (seed = CRC-Seed24/32 from GSD)</p>
<p># input: modified process-data bytes + F-parameters</p>
<p># output: valid 4-byte CRC value for the modified payload</p>
<p>PYEOF</p>
<p>python3 cm_rq002-03_crc_recalc.py</p>
<p># 4a. Parallel injection WITHOUT producer suppression (NV1, collision test):</p>
<p>sudo python3 - &lt;&lt; 'PYEOF'</p>
<p>from scapy.all import Ether, Raw, sendp</p>
<p>sendp(Ether(dst="AA:BB:CC:DD:EE:FF", type=0x8892)/Raw(load=b"..."),</p>
<p>iface="eth1", count=5, inter=0.05)</p>
<p>PYEOF</p>
<p># 4b. If NV3 is available: repeat with full producer suppression (reuse the</p>
<p># bridge/NFQUEUE setup from TC-RQ001-04).</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: parallel injection without suppression causes a collision/rejection (no device fault); with full in-path suppression (NV3) the telegram is accepted - confirms G-1 (black-channel boundary of authenticity).</td>
</tr>
</tbody>
</table>

**TC-RQ002-4 - Parameter-Integrity Forgeability Assessment**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-002 🡪 CR 3.4 🡪 Asset C</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Establish analytically that F_ParCRC (16-bit) is exhaustively searchable and iParCRC (32-bit) is recomputable, both error-detection, not authentication.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Determine the bit-length and algorithm class of each parameter integrity value from documentation.</p></li>
<li><p>Argue the computational feasibility of forging each (search space vs. deterministic recomputation).</p></li>
<li><p>Conclude on cryptographic forgery resistance.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Analytical finding.</p>
<p>Expected: both parameter integrity values are forgeable (no cryptographic resistance), confirming they are error-detection, not authentication, mechanisms.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ002-04</td>
</tr>
<tr>
<td>HW/Network</td>
<td>document review</td>
</tr>
<tr>
<td>Tools</td>
<td>No special tools required</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. F_ParCRC = UINT16, iParCRC = UINT32 and 4-byte CRC, CRC-Seed24/32, publicly documented in the GSD file, record the value ranges / computation basis.</p>
<p># 2. Estimate the search space, e.g.:</p>
<p>python3 -c "print('F_ParCRC search space:', 2**16); print('iParCRC search space:', 2**32)"</p>
<p># 3. Conclude: F_ParCRC (2^16 = 65,536 values) is exhaustively searchable in</p>
<p># milliseconds; iParCRC (2^32) is directly, deterministically recomputable</p>
<p># from the publicly known iParameters (no brute-force needed, since the</p>
<p># algorithm + seed are publicly documented).</p>
<p># 4. Document the conclusion.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: both values are forgeable (no cryptographic forgery resistance) - confirms G-2 (error-detection only, not authentication).</td>
</tr>
</tbody>
</table>

**TC-RQ002-05 - Physical Tamper-Resistance of the Address/Mode Interface**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-002 🡪 EDR 3.11 🡪 Asset G</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td><p>Assess the protection against physical corruption of the safety address/mode interface:</p>
<p>(a) confirm the temporal protection (a runtime change is ignored until restart, so the running safety address cannot be corrupted live), and</p>
<p>(b) determine whether the stored/next-restart value can be corrupted by physically altering the interface, with the seal as the only resisting barrier.</p></td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Record the baseline address and seal state.</p></li>
<li><p>In normal operating state, defeat the physical seal and alter the interface; verify the running address is unchanged.</p></li>
<li><p>Perform a cold restart; confirm whether the altered value now takes effect.</p></li>
<li><p>Assess whether the alteration required visible seal damage.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Gap-characterization test. Expected:</p>
<ol type="i">
<li><p>runtime change ignored (temporal protection = a genuine partial mitigation to credit);</p></li>
<li><p>after restart the altered value applies 🡪 the stored value is physically corruptible;</p></li>
<li><p>the only resistance is the passive seal, with no active tamper-detection/response 🡪 confirms resistance-only physical protection (partial EDR 3.11 result).</p></li>
</ol></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ002-05</td>
</tr>
<tr>
<td>HW/Network</td>
<td>physical, on the SRIO test unit.</td>
</tr>
<tr>
<td>Tools</td>
<td>TIA Online &amp; Diagnostics (read SCPU IoT: F_Dest_Address / rotary-switch value)</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Baseline: read the current rotary-switch value (F_Dest_Add).</p>
<p># TIA Portal &gt; Online &amp; Diagnostics &gt; Identification &amp; Maintenance &gt; read</p>
<p># /devicestatus/rotary_switch (or via IoT-Core Visualizer, browser to</p>
<p># http://192.168.0.2/ &gt; 'devicestatus' menu). Photograph the seal state.</p>
<p># 2. While the device is running (Operate), attempt to non-destructively</p>
<p># remove the protective sleeve/cap and change the rotary switch. Check</p>
<p># whether the RUNNING F_Dest_Add changes (expected: no, only read at Init</p>
<p># - SRIO-8803/10812).</p>
<p># 3. Perform a cold start (disconnect the power-input cable, wait 5-10s,</p>
<p># reconnect; wait until RDY LED and P LED turn green).</p>
<p># 4. Read the rotary-switch value again; check whether the new value is now</p>
<p># applied.</p>
<p># 5. Assess whether the manipulation was possible without visible damage to</p>
<p># the seal (compare against the Step-1 photo).</p></td>
</tr>
<tr>
<td><p>Result</p>
<p>Evidence</p></td>
<td><p>Expected: the runtime change is ignored (confirms the temporal protection); after the cold start, the altered value takes effect, the stored value is physically corruptible; the only resistance is the passive seal, with no active tamper detection/response, confirms resistance-only physical protection (G-3).</p>
<p>Evidence: before/after photos, TIA screenshots.</p></td>
</tr>
</tbody>
</table>

**REQUIREMENT 3**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-003

- **MVO Requirement Text:** The system shall collect evidence of any legitimate or illegitimate intervention in hardware components relevant for connection or access to safety-critical software.

- **IEC 62443-4-2 CR Mapping : (**CR 2.8 not directly for phy.,) CR 2.9, CR 2.10, CR 2.11, (CR 2.12,) CR/EDR 2.13, CR 3.9, EDR 3.11, CR 6.1

- **Target Assets:** G (Physical F-address/OP-mode interface); I (Audit Data)

- **STRIDE:** Repudiation (, Tampering)

- **Security Function (Mitigation):**

  - Physical seals: Passive plastic/metal seals (SRIO-11000/11001).

  - Rotary Switch 192.168.0.91 read only at Init: Runtime change ignored (SRIO-10812).

  - I&M4 signature: F_iParCRC + F_Par_CRC fingerprint of the loaded configuration (SRIO-3011).

  - COM Error Log: ErrorEvents incl. SCPU-timeout (SRIO-10665/21357

- **Identified Gap:**

  - G-1: No tamper switch/sensor 🡪 EDR 3.11 detection limb unmet. An intervention avoiding visible seal damage is unrecorded and unattributable.

  - G-2: Even the events the device does log carry no absolute timestamp, only uptime that resets on cold start (SRIO-15218/15398). RQ-003 evidence is therefore not time-referenceable; a cold start both clears and de-times the record.

  - G-3: The store is non-safety (QM), circular, cleared on cold start (SRIO-10663/6521) 🡪 fails CR 2.9/3.9 and cannot be ‘retained for the mandated period.’

  - G-4: Fusing is a valid EDR 2.13 exclusion, but a physical re-probe still yields no log entry, so RQ-003’s ‘evidence of any intervention’ remains unmet at this interface.

**Step 2: Methodological Test Planning**

<table>
<colgroup>
<col style="width: 4%" />
<col style="width: 42%" />
<col style="width: 20%" />
<col style="width: 22%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td><p>Enumerate the evidence that exists: read COM Error Log (IoT-Core);</p>
<p>read I&amp;M4</p></td>
<td>Functional baseline of the partial controls (CR 6.1 met; CR 2.8 partial)</td>
<td><p>Requirements-based verification;</p>
<p>NIST SP 800-115 §3.2</p></td>
<td>SVV-1</td>
</tr>
<tr>
<td>2</td>
<td><p>Perform an authorized address/parameter change + reboot;</p>
<p>check for any retained, time-stamped evidence</p></td>
<td>Effectiveness (or not) of the evidence function under normal use</td>
<td>Threat-mitigation verification</td>
<td>SVV-2</td>
</tr>
<tr>
<td>3</td>
<td><p>Illegitimate intervention avoiding visible seal damage (careful sleeve removal, rotary change incl. 🡪999), reboot;</p>
<p>verify no tamper record + cold start clears log</p></td>
<td>Proves G-1 &amp; G-3</td>
<td><p>MITRE ATT&amp;CK for ICS T0872; OWASP ISTG-PHY;</p>
<p>EDR 3.11</p></td>
<td>SVV-4</td>
</tr>
<tr>
<td>4</td>
<td><p>Time-attribution analysis: capture two events across a cold start;</p>
<p>show uptime resets and no absolute time exists</p></td>
<td>Proves G-2 (CR 2.11 unmet)</td>
<td>NIST SP 800-115 §3.2</td>
<td>SVV-3</td>
</tr>
<tr>
<td>5</td>
<td><p>Attempt the production-gated FIT function (/fit/setfit, WO/P) on a production unit;</p>
<p>confirm rejection and that the exclusion produces no log entry</p></td>
<td>Validates EDR 2.13 exclusion; confirms G-4 (no evidence)</td>
<td><p>NIST SP 800-115 §4.2;</p>
<p>OWASP FSTM / ISTG-PHY</p></td>
<td>SVV-3</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ003-01 - Baseline: What Evidence the Device Actually Collects</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-003 🡪 CR 2.8 / CR 6.1 🡪 Asset I</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Establish which intervention-evidence mechanisms exist and are readable (audit/error log; the parameter-change counter; the configuration signature), confirming that audit accessibility is met while characterizing the content's limitations.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Read the audit log and the identity/configuration records at a known-good baseline.</p></li>
<li><p>Perform one authorized parameter change.</p></li>
<li><p>Re-read; confirm the change counter incremented and the configuration signature changed.</p></li>
<li><p>Inspect each record for the presence of actor identity and absolute timestamp.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if the log and records are readable and the change is reflected (accessibility + partial auditability confirmed).</p>
<p>Documented shortfall if no record carries an actor identity or an absolute timestamp.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ-003-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>IoT-Core read + I&amp;M read via TIA</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA Online &amp; Diagnose.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq003-01_errorlog.json</p>
<p># In TIA: read I&amp;M4 signature (before/after one param change).</p></td>
</tr>
<tr>
<td>Result</td>
<td><p><em>Expected: log + records readable (accessibility PASS);</em></p>
<p><em>I&amp;M4 signature changes.</em></p>
<p><em>Documented shortfall: no record carries actor identity or absolute timestamp. Evidence: cm_rq003-01_errorlog.json, TIA I&amp;M0/I&amp;M4 screenshots (before/after).</em></p></td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ003-02 - Authorized Intervention Evidence Under Normal Use</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-003 🡪 CR 2.8 / CR 2.11 🡪 Asset I, Asset G</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-2</td>
</tr>
<tr>
<td>Objective</td>
<td>Determine whether an authorized address/parameter change followed by a restart generates any retained, time-referenceable evidence of the intervention.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Baseline the evidence stores.</p></li>
<li><p>Perform an authorized address/parameter change and restart.</p></li>
<li><p>Re-read the evidence stores.</p></li>
<li><p>Assess retention and time-referenceability of any generated record.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if a retained, time-referenceable record of the intervention exists after restart.</p>
<p>Expected shortfall: evidence detail is not retained/time-referenceable across the restart (feeds the retention and timestamp gaps).</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ003-02</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p># 1. Baseline (Kali):</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist/getdata | tee cm_rq003-02_before.json</p>
<p># 2. Authorized change in TIA Portal</p>
<p># a) Open the TIA project &gt; Hardware/network view &gt; select AL400S</p>
<p># b) Properties &gt; Module parameters (e.g. Filter F-DI 1: 10 ms -&gt; 5 ms)</p>
<p># c) Recalculate the iParCRC via the ifm-CRC-Tool (right-click the</p>
<p># module &gt; 'Start device tool' &gt; select 'ifm-CRC-Tool' &gt; confirm</p>
<p># parameters are correct &gt; update F_iPar_CRC, SRIO-20292)</p>
<p># d) Compile and download to the PLC ('Online' &gt;</p>
<p># 'Download to device')</p>
<p># e) Power-cycle the SRIO (cold start)</p>
<p># 3. After the cold start (Kali):</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist/getdata | tee cm_rq003-02_after.json</p>
<p>diff cm_rq003-02_before.json cm_rq003-02_after.json</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Post-reboot detail cleared (cold start), no absolute timestamp;</p>
<p>only counter delta persists.</p>
<p>Evidence: before/after json + TIA I&amp;M.</p></td>
</tr>
</tbody>
</table>

**TC-RQ003-03 - Illegitimate Physical Intervention & Anti-Forensic Clearing**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-003 🡪 EDR 3.11 (detection) / CR 2.8 / CR 3.9 🡪 Asset G, Asset I</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td><p>Demonstrate that</p>
<p>(a) physical intervention avoiding visible seal damage produces no automatic tamper record and no attribution, and</p>
<p>(b) subsequent cold start clears any incidental log content, proving the device cannot collect retained, protected evidence of the intervention.</p></td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Capture the baseline log, records, and address.</p></li>
<li><p>Defeat the seal carefully; alter the interface (including entry into a special mode); note any live status change.</p></li>
<li><p>Cold-restart to apply the change.</p></li>
<li><p>Re-read the log; check for any tamper/intervention entry and whether the log survived the restart.</p></li>
<li><p>Assess attribution and timing of anything found.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Gap-characterization test.</p>
<p>Expected: no tamper-specific entry; incidental entries lost on cold start; no actor identity and no absolute timestamp 🡪 confirms the missing-detection and unprotected-evidence gaps 🡪 FAIL against RQ-003. A persistent, attributed, time-stamped tamper record would indicate an undocumented capability (investigate).</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ003-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Physical setup as TC-RQ002-05, plus Kali (curl, IoT-Core error log) and the TIA laptop</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA Online &amp; Diagnostics.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Baseline:</p>
<p>export SRIO=192.168.0.2</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq003-03_00_baseline.json</p>
<p># Note the rotary-switch value and photograph the seal state.</p>
<p># 2. Non-destructively open the seal, set the rotary switch to a special mode</p>
<p># (e.g. 999 = firmware update); observe the live status (expect no</p>
<p># immediate effect).</p>
<p># 3. Cold start (disconnect power cable, wait 5-10s, reconnect; wait for</p>
<p># RDY/P LED green).</p>
<p># 4. Re-read the error log:</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq003-03_01_after_coldstart.json</p>
<p>diff cm_rq003-03_00_baseline.json cm_rq003-03_01_after_coldstart.json</p>
<p># 5. Check for any entry referencing the physical intervention, and whether</p>
<p># the log content persisted across the cold start (compare with baseline).</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: no tamper-specific entry found; log cleared by the cold start / intervention not attributable - confirms G-1/G-3 in RQ-003.</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ003-04 - Time-Attribution Failure of Collected Evidence</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-003 🡪 CR 2.11 / CR 3.9 🡪 Asset I</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that even the evidence the device does record cannot be placed in absolute time: the device exposes only an uptime reference that resets on cold start, with no synchronized real-time clock, so interventions separated by a power cycle cannot be temporally ordered or dated.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Generate a loggable event; read the uptime reference and the log entry.</p></li>
<li><p>Cold-restart.</p></li>
<li><p>Generate a second event; read the uptime reference again.</p></li>
<li><p>Compare: show the time base reset and the absence of any absolute timestamp.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if entries carry a retained absolute timestamp enabling cross-restart ordering.</p>
<p>Expected FAIL: the time base resets and no absolute timestamp is attached 🡪 evidence is not time-referenceable (CR 2.11 unmet).</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ003-04</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Kali</td>
</tr>
<tr>
<td>Tools</td>
<td>curl</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 0: Baseline</p>
<p>curl -s http://$SRIO/systemtime/systick/getdata | tee cm_rq003-04_systick_00_baseline.txt</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq003-04_log_00_baseline.json</p>
<p># 1: Event 1</p>
<p># Short-circuit pin 1 and pin 3.</p>
<p># 2: Readout after Event 1</p>
<p>curl -s http://$SRIO/systemtime/systick/getdata | tee cm_rq003-04_systick_01_event1.txt</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq003-04_log_01_event1.json</p>
<p># 3: Cold-Restart</p>
<p># -&gt; Disconnect the power input cable from the SRIO</p>
<p># --&gt; Wait 5 -10 seconds</p>
<p># --&gt; Reconnect the power cable; wait until the RDY LED and P LED turn green</p>
<p># 4: Readout after Cold-Restart</p>
<p>curl -s http://$SRIO/systemtime/systick/getdata | tee cm_rq003-04_systick_02_after_coldstart.txt</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq003-04_log_02_after_coldstart.json</p>
<p># 5: Event 2</p>
<p># Short-circuit pin 1 and pin 3.</p>
<p># 6: Readout after Event 2</p>
<p>curl -s http://$SRIO/systemtime/systick/getdata | tee cm_rq003-04_systick_03_event2.txt</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq003-04_log_03_event2.json</p>
<p># 7: Evaluation</p>
<p>echo " Log-comparison Baseline vs Event 1 "</p>
<p>diff cm_rq003-04_log_00_baseline.json cm_rq003-04_log_01_event1.json</p>
<p>echo " Log-comparison after Coldstart vs Event 2 "</p>
<p>diff cm_rq003-04_log_02_after_coldstart.json cm_rq003-04_log_03_event2.json</p>
<p>echo " Systick-comparison "</p>
<p>echo "Baseline: $(cat cm_rq003-04_systick_00_baseline.txt)"</p>
<p>echo "After Event 1: $(cat cm_rq003-04_systick_01_event1.txt)"</p>
<p>echo "After Coldstart: $(cat cm_rq003-04_systick_02_after_coldstart.txt)"</p>
<p>echo "After Event 2: $(cat cm_rq003-04_systick_03_event2.txt)"</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Expected FAIL:</p>
<p>uptime (systick) resets to ~0 on cold start; no absolute timestamp on any entry 🡪 not time-referenceable (CR 2.11 unmet).</p></td>
</tr>
</tbody>
</table>

**TC-RQ003-05 - Excluded (Development-Only) Interface Produces No Evidence**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-003 🡪 EDR 2.13 🡪 Asset G, Asset I</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Validate the compensating exclusion of the development/diagnostic interface: confirm that the production-gated diagnostic function is rejected on a production unit, and that exercising the excluded interface generates no log entry, so an intervention at this interface leaves no evidence.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>On a production-configured unit, attempt to invoke the production-gated diagnostic/test function.</p></li>
<li><p>Confirm rejection.</p></li>
<li><p>Inspect the audit log for any entry corresponding to the attempt.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS (exclusion valid) if the function is rejected on the production unit.</p>
<p>Documented gap: the excluded interface produces no evidence, so RQ-003's "evidence of any intervention" is unmet at this interface.</p>
<p>Limitation: a true hardware-fuse claim is not verifiable without invasive physical analysis and is out of scope; only the functional gate is tested.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ003-05</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Production-configured unit</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>Attempt the production-gated FIT service on a production unit:</p>
<p>`curl -s -X POST http://192.168.0.2/fit/setfit -d '{"type":1}' -w "%{http_code}\n"</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Expected: FIT rejected on the production unit (exclusion valid);</p>
<p>the excluded interface produces no log entry (documented gap). Limitation: a true silicon fuse is not verifiable without invasive PA-4 analysis, only the functional gate is tested. Evidence: cm_rq003-05_fit.txt, error-log excerpt.</p></td>
</tr>
</tbody>
</table>

**REQUIREMENT 4**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-004

- **MVO Requirement Text:** The system shall identify the software and data that are critical for compliance with the essential health and safety requirements

- **IEC 62443-4-2 CR Mapping:** CR 7.8(, CR 4.1)

- **Target Assets:** B (Config), D (Safety Firmware)

- **STRIDE:** Tampering, Information Disclosure

- **Security Function (Mitigation):**

  - Version/identification API:

> /deviceinfo/hwversion, /hwrevision, /swrevision, /swinfo/scpuversion, /swinfo/cpubootloaderversion, /swinfo/scpubootloaderversion (SRIO-2946 ff.).

- I&M0 / I&M5: Identity (MANUFACTURER_ID, ORDER_ID, SERIAL, HW/SW revision) and host-fw annotation, PROFINET acyclic records (SRIO-3002/3023).

- I&M4 data fingerprint: F_iParCRC + F_Par_CRC uniquely characterise the loaded safety configuration (SRIO-3011). This is a partial DATA-identification control

<!-- -->

- **Identified Gap:**

  - G-1 (residual only): I&M4 identifies that a specific configuration is loaded but the device does not enumerate/classify which data elements are EHSR-critical. Report this as the residual limitation, not as ‘data is not addressed.’

  - G-2: CR 7.8 expects identification of the third-party software genuinely critical for EHSR compliance: µC/OS-II (SRIO-1260), the SIL3 PROFIsafe stack (SRIO-1929), the STM32F7 self-test library (SRIO-10766), the netX90 PROFINET stack (SRIO-1768). Only top-level version strings are exposed and there is no SBOM 🡪 these cannot be inventoried or CVE-correlated.

  - G-3: Identification is served over plaintext HTTP (SRIO-7903/7907). Keep as a defense-in-depth observation only; under EN 50742 Approach B this is not a safety-security conformance FAIL (FR4 = none).

**Step 2: Methodological Test Planning**

<table>
<colgroup>
<col style="width: 4%" />
<col style="width: 42%" />
<col style="width: 20%" />
<col style="width: 22%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td><p>Enumerate the identification surface (/deviceinfo/*, I&amp;M0, I&amp;M5, /firmware/version, /fieldbussetup/fieldbusfirmware, I&amp;M4 for data);</p>
<p>build the actual inventory and diff vs. expected EHSR-critical SW+data</p></td>
<td>Functional CR 7.8; confirms SW + data (I&amp;M4) identification; exposes G2</td>
<td>Requirements-based verification; OWASP FSTM Stage 1</td>
<td>SVV-1</td>
</tr>
<tr>
<td>2</td>
<td><p>SBOM-completeness / version 🡪 CVE analysis:</p>
<p>attempt to derive third-party components (µC/OS-II, PROFIsafe stack, STM STL, netX90);</p>
<p>show no SBOM 🡪 no CVE correlation</p></td>
<td>Proves G-2</td>
<td>BSI TR-03183-2; 62443-4-1 SM-9/SM-10</td>
<td>SVV-3</td>
</tr>
<tr>
<td>3</td>
<td>Passive plaintext capture of the identification traffic (defence-in-depth observation, not a FAIL under EN 50742 FR4=none)</td>
<td>Documents G-3 (DiD only)</td>
<td><p>NIST SP 800-115 §3.5;</p>
<p>OWASP ISTG-DES-INFO;</p>
<p>ifm CM-005</p></td>
<td>SVV-3</td>
</tr>
<tr>
<td>4</td>
<td><p>Data-identification fingerprint check:</p>
<p>read I&amp;M4 for config A;</p>
<p>load a different config B;</p>
<p>read I&amp;M4;</p>
<p>confirm the signature uniquely characterizes the loaded config</p></td>
<td>Confirms the partial DATA-identification control (corrects G-1)</td>
<td>Requirements-based verification</td>
<td>SVV-1</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ004-01 - Identification-Surface Inventory (SW + Data)</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-004 🡪 CR 7.8 🡪 Asset D (software) + Asset B (data via configuration signature)</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Information Disclosure</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td><p>Enumerate the complete identification set the device exposes;</p>
<p>confirm it identifies safety software (firmware/bootloader/stack versions) and safety data (the configuration signature);</p>
<p>diff against the expected EHSR-critical software + data set to reveal the completeness gap.</p></td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Retrieve all device software version fields via the identification interface.</p></li>
<li><p>Retrieve the identity and configuration-signature records via the fieldbus acyclic identity records.</p></li>
<li><p>Retrieve the firmware and communication-stack version fields.</p></li>
<li><p>Compile the inventory and compare against the expected set, including third-party components.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS (partial-conformance baseline) if the device returns top-level software identification and a data-identification signature.</p>
<p>Documented shortfall if no software bill of materials of third-party components is present and no explicit safety-critical-data classification is exposed.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ004-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>curl, TIA, OWASP FSTM Stage 1.</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA, OWASP FSTM Stage 1 checklist.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>for p in deviceinfo/hwversion deviceinfo/hwrevision deviceinfo/swrevision \</p>
<p>deviceinfo/swinfo/cpubootloaderversion deviceinfo/swinfo/scpuversion \</p>
<p>deviceinfo/swinfo/scpubootloaderversion firmware/version fieldbussetup/fieldbusfirmware; do</p>
<p>echo "== $p =="</p>
<p>curl -s http://$SRIO/$p/getdata</p>
<p>echo</p>
<p>done | tee cm_rq004-01_inventory.txt</p>
<p>TIA: I&amp;M0, I&amp;M5, I&amp;M4 for data</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Expected (partial-conformance baseline): top-level SW identification + I&amp;M4 data signature present;</p>
<p>Evidence: cm_rq004-01_inventory.txt, TIA I&amp;M screenshots, inventory diff table.</p></td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ004-02 - Software-Bill-of-Materials Completeness & Third-Party Vulnerability</span> Correlation**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-004 🡪 CR 7.8/ 62443-4-1 SM-9 -SM-10 🡪 Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Information Disclosure</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that the exposed inventory is top-level only and provides no bill of materials for the safety-critical third-party components (real-time OS, safety-protocol stack, processor self-test library, communication stack), so their versions cannot be enumerated or vulnerability-correlated, CR 7.8 met at product granularity but not at component granularity.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>From TC-RQ004-01, list all device-exposed version strings.</p></li>
<li><p>From documentation, list the known constituent third-party components.</p></li>
<li><p>Attempt to derive each component's version from any exposed interface.</p></li>
<li><p>For derivable versions, correlate against a vulnerability database; record the remainder as un-inventoried.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td>Expected FAIL: third-party components are not individually exposed and no bill of materials exists 🡪 confirms the completeness gap; documented as a CR 7.8 shortfall requiring a machine-readable SBOM.</td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ004-02</td>
</tr>
<tr>
<td>HW/Network</td>
<td>document review; optionally supplemented by a CVE cross-check via Kali/GVM (CM-008).</td>
</tr>
<tr>
<td>Tools</td>
<td>GVM/OpenVAS (CM-008, optional - the community feed may need to be imported offline, see test-environment note, section 2), otherwise manual version-to-CVE lookup (NVD).</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. From references [6]-[14] (209_SRIO_CompSpec_Module_Com), compile the</p>
<p># third-party component versions: µC/OS-II, PROFIsafe stack V2.6 MU1,</p>
<p># STM32F7 STL Rev.7, netX90 PROFINET stack.</p>
<p># 2. For each component/version, check for a public CVE reference (NVD /</p>
<p># vendor advisories).</p>
<p># 3. If GVM is available:</p>
<p>sudo gvm-start</p>
<p># Open https://127.0.0.1:9392, log in, create targets for SRIO (192.168.0.2)</p>
<p># and PLC (192.168.0.1), and start a scan (or via CLI, see ifm CM-008</p>
<p># framework: gvm-cli --gmp-username admin --gmp-password &lt;pw&gt; socket --xml \</p>
<p># "&lt;create_target&gt;&lt;name&gt;cm_rq004-02&lt;/name&gt;&lt;hosts&gt;192.168.0.2&lt;/hosts&gt;&lt;/create_target&gt;")</p>
<p># 4. Compare the GVM findings against the manually compiled list; document</p>
<p># gaps (no machine-readable SBOM, no automated CVE correlation possible).</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected FAIL / gap confirmation - no machine-readable SBOM exists, components only derivable from free-text documentation, no automated CVE correlation possible (confirms G-2 in RQ-004/RQ-006).</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ004-03 - Plaintext Exposure of Identification Data</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-004🡪 CR 4.1 (observation only) 🡪 Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Information Disclosure</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Confirm that identification data is served without transport encryption and can be observed passively on the segment.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Trigger a legitimate identification read.</p></li>
<li><p>Passively observe the exchange.</p></li>
<li><p>Confirm the identification content is recoverable in cleartext and that no encrypted transport option exists.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Observation only.</p>
<p>Expected: cleartext recoverable, no encrypted transport. Recorded as a defence-in-depth note; not scored as a safety-security FAIL.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ004-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1/ NV2</td>
</tr>
<tr>
<td>Tools</td>
<td>Wireshark/tshark, sslscan (CM-005).</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>sslscan --show-certificate $SRIO:80 &gt; cm_rq004-03_sslscan.txt 2&gt;&amp;1</p>
<p>sudo tcpdump -i eth1 host $SRIO and port 80 -w cm_rq004-03_http.pcap &amp;</p>
<p>curl -s http://$SRIO/deviceinfo/getdata</p>
<p>kill %1</p>
<p>wireshark cm_rq004-03_http.pcap</p>
<p># -&gt; right-click HTTP-Paket -&gt; Follow -&gt; HTTP Stream</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Expected: sslscan returns NO TLS handshake at all (immediate connection error, since port 80 only offers plaintext HTTP without TLS, SRIO-7903/7907 „no HTTPS“).</p>
<p>Additionally, a parallel capture shows the plaintext content in Wireshark („Follow &gt; HTTP Stream“). Confirms G-3 (plaintext, no transport encryption) - recorded as a defense-in-depth observation, not a safety-security FAIL per EN 50742 FR4.</p></td>
</tr>
</tbody>
</table>

**TC-RQ004-04 - Data-Identification Signature Uniqueness**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-004 🡪 CR 7.8 🡪 Asset B</td>
</tr>
<tr>
<td>Target Threat</td>
<td>N/A, functional identification</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Confirm that safety data is identified: the configuration signature uniquely characterizes the loaded safety configuration, so different configurations yield different signatures, establishing that data is identified, correcting the "data not addressed" premise.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Load configuration A; read the configuration signature.</p></li>
<li><p>Load a materially different configuration B; read the configuration signature.</p></li>
<li><p>Confirm the two signatures differ and each uniquely maps to its configuration.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if distinct configurations produce distinct signatures (data identified via fingerprint).</p>
<p>Documented limitation: the signature identifies that a specific configuration is loaded but does not enumerate/classify which data elements are EHSR-critical (residual gap).</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>RQ004-04</td>
</tr>
<tr>
<td>HW/Network</td>
<td>TIA laptop, PLC, SRIO</td>
</tr>
<tr>
<td>Tools</td>
<td>TIA (I&amp;M4 read), config A/B projects.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Load configuration A:</p>
<p># TIA Portal &gt; Hardware/network view &gt; SRIO module (AL400S) &gt; Properties &gt;</p>
<p># Module parameters &gt; e.g. set 'Filter F-DI 1' = 10 ms</p>
<p># Recalculate iParCRC: right-click module &gt; 'Start device tool' &gt;</p>
<p># 'ifm-CRC-Tool' &gt; confirm parameters correct &gt; copy F_iPar_CRC &gt;</p>
<p># paste into Properties &gt; PROFIsafe &gt; F-Parameters &gt; F_iPar_CRC</p>
<p># Project &gt; Compile (Ctrl+Shift+B) &gt; Online &gt; Download to device (Ctrl+D)</p>
<p># 2. Read I&amp;M4 in TIA:</p>
<p># TIA Portal &gt; Online &amp; Diagnostics &gt; Identification &amp; Maintenance &gt; I&amp;M4</p>
<p># (record the SIGNATURE value = F_iParCRC + F_Par_CRC as hex)</p>
<p># 3. Load configuration B (materially different, e.g. Filter F-DI 1 = 5 ms +</p>
<p># Symmetry changed from 1oo1 to 1oo2): repeat step 1's parameter change +</p>
<p># ifm-CRC-Tool recalculation + compile + download.</p>
<p># 4. Read I&amp;M4 again (as in step 2); compare the two signature values.</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Expected PASS: distinct configs 🡪 distinct I&amp;M4 signatures (data identified via fingerprint).</p>
<p>Documented limitation: signature identifies that a config is loaded, not which elements are EHSR-critical. Evidence: two TIA I&amp;M4 screenshots + config notes.</p></td>
</tr>
</tbody>
</table>

**REQUIREMENT 5**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-005

- **MVO Requirement Text:** The system shall protect identified safety-critical software and data against corruption, whether accidental or intentional.

- **IEC 62443-4-2 CR :** CR 3.3 CR 3.4, EDR 3.10, EDR 3.12, EDR 3.13, EDR 3.14

- **Target Assets:** B (Runtime integrity), D (image integrity), F (Domain separation)

- **STRIDE:** (Spoofing,) Tampering

- **Security Function (Mitigation):**

  - iParCRC (UINT32) + F_ParCRC (UINT16): Verified each parametrization --\> EC3 on mismatch.

  - Certified CRC-Tool (T2, TÜV Süd): iParCRC generation (SRIO-9023).

  - Dual SCPU cross-check + STL, 1oo2 diversity + STM32F7 self-test library + startup tests.

  - FW update behind firewall - Environmental (SRIO-1196): compensating, not a device function.

  - Update container = unsigned BLOB: Stated for completeness, this is the deficiency, not a control (SRIO-2953).

- **Identified Gap:**

  - G-1 (Part B): iParCRC/F_ParCRC are checksums, not MACs; public seed/layout, 16-bit F_ParCRC 🡪 recomputable 🡪 intentional parameter corruption undetected. Same class as RQ-002

  - G-2 (Part D): The update installs an unsigned BLOB with no signature verification (EDR 3.10) and no secure boot (EDR 3.14), because there is no on-device trust anchor (EDR 3.12/3.13). Intentional firmware corruption is not prevented by any device-level cryptographic mechanism; the only barriers are the environmental firewall and (as authorization, per RQ-011) the physical/mode gate. This is the decisive gap of the whole requirement set.

  - G-3. A deliberate, identical malicious modification applied to both channels (dual-SCPU cross-check and the STL) is a systematic, coherent change, the two channels still agree, the cross-comparison passes, and the STL sees a consistent (though malicious) image.

> Hence safety integrity mechanisms provide no SECURITY authenticity: they cannot distinguish a genuine image from a coherently, tampered one. That is precisely what a signed-image / secure-boot mechanism (EDR 3.14) would catch.

**Step 2: Methodological Test Planning**

<table style="width:100%;">
<colgroup>
<col style="width: 4%" />
<col style="width: 35%" />
<col style="width: 19%" />
<col style="width: 32%" />
<col style="width: 9%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>Verify iParCRC/F_ParCRC rejection of a mismatched configuration (references TC-RQ002-01)</td>
<td>Functional CR 3.4 in normal operation</td>
<td>Requirements-based verification</td>
<td>SVV-1</td>
</tr>
<tr>
<td>2</td>
<td><p>Recompute valid iParCRC/F_ParCRC over modified parameters;</p>
<p>inject 🡪 accepted</p></td>
<td>Proves G-1 (Part B)</td>
<td><p>MITRE ATT&amp;CK for ICS T0836;</p>
<p>NIST SP 800-115 §5.2</p></td>
<td>SVV-4</td>
</tr>
<tr>
<td>3</td>
<td><p>Upload a modified/unsigned firmware BLOB;</p>
<p>confirm no signature/integrity verification before install</p></td>
<td>Proves G-2 (Part D)</td>
<td><p>OWASP ISTG-FW[UPDT]-CRYPT-001/004;</p>
<p>OWASP FSTM Stage 7;</p>
<p>MITRE T1693.001</p></td>
<td>SVV-4</td>
</tr>
<tr>
<td>4</td>
<td>Obtain the update image/BLOB; static analysis for signature/header + binary-hardening review</td>
<td>Characterizes absence of signing / secure-boot artefacts</td>
<td><p>OWASP FSTM Stage 3 -5;</p>
<p>ifm CM-008</p></td>
<td>SVV-3</td>
</tr>
<tr>
<td>5</td>
<td>Analytical: argue why 1oo2 cross-check + STL cannot detect a coherent tamper; cross-reference Test 3</td>
<td>Substantiates G-3 (Self-test <span class="math inline">≠</span>authenticity)</td>
<td><p>Requirements/architecture analysis;</p>
<p>IEC 61508 vs. 62443 integrity distinction</p></td>
<td>SVV-1</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ005-01 - Parameter Integrity-Value Rejection ⇄ TC-RQ002-01</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-005 🡪 CR 3.4 🡪 Asset B</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Verify (by reference to TC-RQ002-01) that a configuration with a mismatched parameter integrity value is rejected, remaining in the safe state.</td>
</tr>
<tr>
<td>Steps</td>
<td>Execute per TC-RQ002-01; record the result against RQ-005 traceability.</td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>As TC-RQ002-01. </p>
<p>PASS on rejection of the mismatched configuration</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

| Field | Content |
|----|----|
| Ref. Test Case | TC-RQ005-01 |
| HW/Network | As TC-RQ002-01. |
| Tools | As TC-RQ002-01. |
| Procedure | Execute TC-RQ002-01 procedure; record under RQ-005 traceability. |
| Result | *As TC-RQ002-01, PASS on rejection of the mismatched configuration. Evidence: reuse cm_rq002-01\_\*.* |

**<span class="mark">TC-RQ005-02 - Valid-Integrity Forgery over Modified Parameters</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-005 🡪 CR 3.4 🡪 Asset B</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that because the parameter integrity values are non-secret checksums, an attacker who modifies the safety parameter set and recomputes matching integrity values produces a configuration the safety CPU accepts, protection against accidental but not intentional corruption.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Capture/derive a legitimate parameter record and its integrity block.</p></li>
<li><p>Modify a safety-relevant parameter.</p></li>
<li><p>Recompute the parameter integrity values.</p></li>
<li><p>Present the forged configuration; observe whether the device accepts it or raises a configuration error.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Gap-characterization test.</p>
<p>Expected: the forged configuration is accepted, confirming that the parameter integrity values are not authentication. A rejection would indicate an undocumented cryptographic control (investigate).</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ005-02</td>
</tr>
<tr>
<td>HW/Network</td>
<td>TIA laptop, PLC, SRIO; Kali for observation/logging.</td>
</tr>
<tr>
<td>Tools</td>
<td>TIA Portal, ifm-CRC-Tool; optionally Scapy (if the manipulation should be built from a recreated acyclic-write telegram instead of via TIA).</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Change a safety-relevant parameter (e.g. Filter F-DI or Symmetry</p>
<p># Discrepancy Time) in TIA Portal (as in TC-RQ004-04, step 1).</p>
<p># 2. Do NOT regenerate the iParCRC correctly via the ifm-CRC-Tool. Instead,</p>
<p># recreate the acyclic configuration telegram with Scapy and attach a</p>
<p># freshly recomputed CRC over the MODIFIED parameter set,</p>
<p># using the byte layout captured in TC-RQ001-03 and the CRC algorithm</p>
<p># from SRIO-2998:</p>
<p>cat &gt; cm_rq005-02_forge.py &lt;&lt; 'PYEOF'</p>
<p>from scapy.all import Ether, Raw, sendp</p>
<p>iface = "eth1"</p>
<p>target_mac = "AA:BB:CC:DD:EE:FF"</p>
<p>forged_config = bytes.fromhex("REPLACE_WITH_MODIFIED_PARAM_SET_PLUS_VALID_CRC")</p>
<p>sendp(Ether(dst=target_mac, type=0x8892)/Raw(load=forged_config),</p>
<p>iface=iface, count=3, inter=0.1)</p>
<p>PYEOF</p>
<p>sudo python3 cm_rq005-02_forge.py</p>
<p># 3. Observe the PROFIsafe connection-establishment behaviour in the TIA</p>
<p># watch table.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: the configuration with a correctly recomputed CRC over modified data is accepted - confirms G-1 in RQ-005 (iParCRC is error detection only, not an authenticity check).</td>
</tr>
</tbody>
</table>

**TC-RQ005-03 - Unsigned / Modified Firmware Installation**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-005 🡪 EDR 3.10 / EDR 3.14 (🡪 EDR 3.12/3.13) 🡪 Asset D, Asset F</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering + Spoofing</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that the firmware-update mechanism installs an update without cryptographic authenticity/integrity verification: a modified/unsigned firmware package is accepted for installation, proving the intentional-corruption protection for the safety firmware is absent (only environmental and mode-gate barriers remain).</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Place a spare unit into the update state (operational precondition; the mode gate's authorization is tested under RQ-011).</p></li>
<li><p>Take a legitimate update package and modify a byte, or strip/forge any signature/header.</p></li>
<li><p>Upload via the update service and invoke installation.</p></li>
<li><p>Observe whether the device verifies the package before installation (rejects) or proceeds.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS against the requirement if the modified/unsigned package is rejected by a signature/integrity check before installation.</p>
<p>Expected FAIL: the package is accepted for installation 🡪 EDR 3.10/3.14 unmet.</p>
<p>Safety: spare unit only; re-flash a validated image afterwards.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ005-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td>ideally with a second unit for risk-bearing firmware tests.</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, hex editor (bless/ghex, or xxd/dd) to modify a single byte in the SRIO update container (structure: update container header, netX90 FW, CPU3 FW, Safe Container with safe header + safe app FW).</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Set the rotary switch to 999, power cycle --&gt; device boots into State</p>
<p># Update</p>
<p># 2. Back up the current official SRIO update container. Modify one byte</p>
<p># OUTSIDE the Safe Container, do not recompute checksums:</p>
<p>cp srio_update_official.bin cm_rq005-03_modified.bin</p>
<p>xxd cm_rq005-03_modified.bin | head -20 # identify a padding byte offset</p>
<p># Flip 1 byte at the chosen offset, e.g. using a hex editor:</p>
<p>ghex cm_rq005-03_modified.bin</p>
<p># (or via dd, replacing &lt;OFFSET&gt; with the actual byte offset found above)</p>
<p>printf '\xFF' | dd of=cm_rq005-03_modified.bin bs=1 seek=&lt;OFFSET&gt; count=1 conv=notrunc</p>
<p># 3. Upload via IoT-Core:</p>
<p>export SRIO=192.168.0.2</p>
<p>CHUNK=2048</p>
<p>curl -s -X POST http://$SRIO/firmware/container/start_stream_set</p>
<p>split -b $CHUNK cm_rq005-03_modified.bin cm_rq005-03_chunk_</p>
<p>for f in cm_rq005-03_chunk_*; do</p>
<p>curl -s -X POST http://$SRIO/firmware/container/stream_set --data-binary @$f</p>
<p>done</p>
<p># 4. Trigger installation and observe the reaction:</p>
<p>curl -s -X POST http://$SRIO/firmware/install -w "%{http_code}\n" | tee cm_rq005-03_install.txt</p>
<p># 5. AFTER the test: re-upload the unmodified, official firmware (repeat</p>
<p># steps 1+3 with the original file) and repeat the functional check from</p>
<p># TC-RQ001-01 to confirm the device is back to its original state.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected FAIL (against the requirement): there is no cryptographic signature check (EDR 3.10/3.14). Whether this specific byte is caught depends on whether an existing consistency check covers it; both acceptance and rejection by a simple checksum confirm the core finding: no signature = no assured authenticity.</td>
</tr>
</tbody>
</table>

**TC-RQ005-04 - Update-Package Static Analysis for Signing / Boot-Chain Artefacts**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-005 🡪 EDR 3.12 / EDR 3.14 🡪 Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Characterize the absence of signing and secure-boot artefacts by static analysis of the update package (header structure, signature region, binary-hardening posture).</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Obtain the legitimate update package.</p></li>
<li><p>Statically inspect its structure for a signature/header and trust-anchor references.</p></li>
<li><p>Assess the binary-hardening posture of the contained image.</p></li>
<li><p>Record the presence/absence of each artefact.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td>Expected: no signature/trust-anchor artefacts present, consistent with an unsigned package 🡪 supports the firmware-authenticity gap.</td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ005-04</td>
</tr>
<tr>
<td>HW/Network</td>
<td>analytical file analysis of the update container</td>
</tr>
<tr>
<td>Tools</td>
<td>binwalk, file, xxd/hexdump, strings</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>file cm_update_container.bin</p>
<p>binwalk -A cm_update_container.bin</p>
<p>strings cm_update_container.bin | grep -i -E "sig|cert|rsa|ecdsa|sha256"</p>
<p>xxd cm_update_container.bin | less</p>
<p># Compare the identified header fields against the documented structure</p>
<p># check whether any header field goes beyond CRC/compatibility identifiers.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: no signature/certificate structure found, only CRC/compatibility fields - confirms the EDR 3.12/3.14 gap.</td>
</tr>
</tbody>
</table>

**TC-RQ005-05 - Analytical: Safety Self-Tests ≠ Authenticity**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-005 🡪 CR 3.3 🡪 Asset A, Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>N/A, architectural analysis</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Establish, analytically, why the dual-channel cross-check and the processor self-test library cannot detect a coherent malicious modification applied identically to both channels, a systematic change on which both channels still agree, and therefore provide no security authenticity. Cross-references the empirical proof in TC-RQ005-03.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Describe the fault model of the safety self-tests (random, independent hardware faults; channel divergence).</p></li>
<li><p>Describe the attack model (coherent, identical modification of both channels).</p></li>
<li><p>Argue that the two are disjoint; conclude that only a signed-image/secure-boot mechanism would detect the latter.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td>Analytical finding. Substantiates that integrity-of-execution (safety) does not provide authenticity (security); no lab exploit required beyond TC-RQ005-03.</td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ005-05</td>
</tr>
<tr>
<td>HW/Network</td>
<td>document review</td>
</tr>
<tr>
<td>Tools</td>
<td>None</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. List the fault model of the self-tests (STL, 1oo2 cross-check):</p>
<p># random, independent hardware faults.</p>
<p># 2. Contrast this with the attack model (identical, coordinated</p>
<p># manipulation of both channels, actually performed in TC-RQ005-03).</p>
<p># 3. Conclude that only a signed image / secure boot mechanism would be able</p>
<p># to detect a coherent manipulation of this kind.</p>
<p># 4. Document the conclusion, referencing the empirical result of TC-RQ005-03.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Analytical finding - confirms that safety self-tests provide no security authenticity (see the empirical evidence from TC-RQ005-03).</td>
</tr>
</tbody>
</table>

**REQUIREMENT 6**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-006

- **MVO Requirement Text:** The system shall identify the software installed on it that is necessary for safe operation.

- **IEC 62443-4-2 CR: Mapping** (CR 4.1,) CR 7.8

- **Target Assets:** D (host FW, SCPU FW, bootloaders)

- **STRIDE:** Tampering, Information Disclosure

- **Security Function (Mitigation):**

  - Software inventory (IoT-Core): /deviceinfo/swrevision, /swinfo/cpubootloaderversion, /swinfo/scpuversion, /swinfo/scpubootloaderversion.

  - I&M0 SOFTWARE_REVISION / I&M5 annotation: PROFINET acyclic (SRIO-3002/3023).

  - /firmware/version, /fieldbussetup/fieldbusfirmware: PROFIsafe stack version (SRIO-2953, SRIO-2948).

- **Identified Gap:**

  - G-1: Identical root cause to RQ-004 G-2: no SBOM of µC/OS-II, PROFIsafe stack, STM32F7 STL, netX90 🡪 CR 7.8 met at product granularity, not component granularity. Reuse TC-RQ004-02; do not re-derive.

  - G-2: Plaintext HTTP inventory read; defence-in-depth observation only (EN 50742 FR4 = none), not a conformance FAIL.

**Step 2: Methodological Test Planning**

<table>
<colgroup>
<col style="width: 3%" />
<col style="width: 35%" />
<col style="width: 32%" />
<col style="width: 18%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td><p>Enumerate the full installed-software surface (/deviceinfo/swinfo/*, I&amp;M0, I&amp;M5, /firmware/version, /fieldbussetup/fieldbusfirmware);</p>
<p>build the installed-software inventory</p></td>
<td>Functional CR 7.8; confirms host/SCPU/bootloader/stack identification</td>
<td>Requirements-based verification; OWASP FSTM Stage 1</td>
<td>SVV-1</td>
</tr>
<tr>
<td>2</td>
<td><p>SBOM completeness / version 🡪 CVE</p>
<p>REUSE TC-RQ004-02 by reference</p></td>
<td>Proves G-1 (requirement-specific)</td>
<td><p>OWASP FSTM ‘SBOM Generation’; BSI TR-03183-2;</p>
<p>ifm CM-008</p></td>
<td>SVV-3</td>
</tr>
<tr>
<td>3</td>
<td>Passive plaintext capture of the inventory read (DiD observation)</td>
<td>Documents G-2 (DiD only)</td>
<td>NIST SP 800-115 §3.5; OWASP ISTG-DES-INFO; ifm CM-005</td>
<td>SVV-3</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

<span class="mark">TC-RQ006-01 - Installed-Software Inventory Enumeration</span>

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-006 🡪 CR 7.8 🡪 Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Information Disclosure (requirement level); test itself functional</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td><p>Enumerate the complete set of installed-software identifiers and confirm coverage of the software necessary for safe operation (host firmware, both bootloaders, safety-CPU firmware, safety-protocol stack);</p>
<p>map each entry to the safety function it supports.</p></td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Read all software-version and bootloader-version fields via the identification interface.</p></li>
<li><p>Read the software-revision identity record and any annotation record.</p></li>
<li><p>Read the firmware and communication-stack version fields.</p></li>
<li><p>Assemble the inventory; map each entry to its supported safety function.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS (partial-conformance baseline) if host firmware, both bootloaders, safety-CPU firmware, and the safety-protocol stack version are all retrievable and mutually consistent.</p>
<p>Documented shortfall where any safety-relevant installed component is not individually identified.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ006-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>IoT-Core read + Engineering Laptop für I&amp;M-Auslesen via TIA</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA Online &amp; Diagnose</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>for p in deviceinfo/swinfo/cpubootloaderversion deviceinfo/swinfo/scpuversion \</p>
<p>deviceinfo/swinfo/scpubootloaderversion deviceinfo/swrevision firmware/version \</p>
<p>fieldbussetup/fieldbusfirmware; do</p>
<p>echo "== $p =="</p>
<p>curl -s http://$SRIO/$p/getdata</p>
<p>echo</p>
<p>done | tee cm_rq006-01_installed.txt</p>
<p>I&amp;M</p></td>
</tr>
<tr>
<td>Result</td>
<td><p>Host FW, both bootloaders, SCPU FW, stack version retrievable + consistent. Evidence: cm_rq006-01_installed.txt, TIA I&amp;M0/I&amp;M4 screenshots 🡪</p>
<p>reference RQ-004-01</p></td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ006-02 - SBOM Completeness & Vulnerability Correlation ⇄ TC-RQ004-02</span>**

**Level 1 - Abstract Test Scenario**

| Field | Content |
|----|----|
| Traceability | RQ-006 🡪 CR 7.8 / 62443-4-1 SM-9 -SM-10 🡪 Asset D |
| Target Threat | Information Disclosure |
| SVV Category | SVV-3 |
| Objective | By reference to TC-RQ004-02, demonstrate that no bill of materials of the third-party constituents exists, so their versions cannot be enumerated or vulnerability-correlated, CR 7.8 met at product but not component granularity. |
| Steps | Execute per TC-RQ004-01; record against RQ-006 traceability. Do not re-derive. |
| Pass/Fail | As TC-RQ004-02. Expected FAIL: no component-level SBOM. |

**Level 2 - Concrete Execution**

| Field | Content |
|----|----|
| Ref. Test Case | TC-RQ006-02 |
| HW/Network | reuse TC-RQ004-02. |
| Tools | As TC-RQ004-02. |
| Procedure | Execute per TC-RQ004-02; record under RQ-006. Do not re-derive. |
| Result | As TC-RQ004-02, no component-level SBOM (SDL/CRA shortfall). Evidence: reuse TC-RQ004-02 artefacts. \[PLACEHOLDER: Result\] |

**<span class="mark">TC-RQ006-03 - Plaintext Inventory Exposure (Defense-in-Depth Observation)</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-006 🡪 CR 4.1 (observation only) 🡪 Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Information Disclosure</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Confirm the inventory read is served without transport encryption. Recorded as a defense-in-depth observation (EN 50742 FR4 target = none), not a conformance FAIL.</td>
</tr>
<tr>
<td>Steps</td>
<td><p>Trigger an inventory read;</p>
<p>passively observe;</p>
<p>confirm cleartext and no encrypted transport option.</p></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td>Observation only. Documented as defense-in-depth; not scored.</td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ006-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1, Kali as its own client</td>
</tr>
<tr>
<td>Tools</td>
<td>tcpdump/Wireshark, curl, sslscan (CM-005).</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>sslscan --show-certificate $SRIO:80 | tee cm_rq006-03_sslscan.txt</p>
<p># In parallel:</p>
<p>sudo tcpdump -i eth1 host $SRIO and port 80 -w cm_rq006-03_http.pcap &amp;</p>
<p>curl -s http://$SRIO/deviceinfo/swrevision/getdata</p>
<p>kill %1</p>
<p># Open cm_rq006-03_http.pcap in Wireshark, right-click a packet &gt;</p>
<p># Follow &gt; HTTP Stream, to show the plaintext content.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: plaintext transmission confirmed (defense-in-depth observation, no safety-security FAIL per EN 50742 FR4).</td>
</tr>
</tbody>
</table>

**REQUIREMENT 7**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-007

- **MVO Requirement Text:** The system shall be able to provide the identification information of safety-relevant installed software at all times in an easily accessible form.

- **IEC 62443-4-2 CR: Mapping** CR 6.1, CR 7.1, CR 7.2, CR 7.7 (supporting), CR 7.8

- **Target Assets:** D (identification data - at all times); F (Domain separation-availability dependency); H (IoT-Core service Availability);

- **STRIDE:** Denial of Service, Information Disclosure

- **Security Function (Mitigation):**

  - Max 2 concurrent HTTP connections (SRIO-7909): intended as DoS protection.

  - Incoming-only, no outgoing/subscription: (SRIO-7908).

  - IoT-Core Visualizer (browser, by IP) (SRIO-7914): satisfies ‘easily accessible form’.

  - HTTP served by non-safety COM (QM) only: Stated as a structural limitation.

- **Identified Gap:**

  - G-1: Identification is not available at all times:

> \(a\) install reboot (/firmware/install 🡪 reboot, SRIO-2953);
>
> \(b\) Init at every power-on before IoT-Core is up (SRIO-1417);
>
> \(c\) SCPU-flash window 🡪 SCPU-sourced identifiers absent (SRIO-15759); (d) FatalError safe-state hold (SRIO-15757);
>
> \(e\) EMC disturbance: the manufacturer’s own Criterion A/B concedes IoT-Core is ‘Not supervised … After the tests: IoT-Core access possible’ (SRIO-11573/11572).

- G-2: Two held/idle connections exhaust the pool (SRIO-7909) and block all further legitimate identification reads; incoming-only, no documented idle timeout.

- G-3 (no redundancy): A COM fault or SysCom timeout removes identification availability entirely while the safety function persists 🡪 identification is structurally LESS available than the safety function it describes.

**Step 2: Methodological Test Planning**

<table>
<colgroup>
<col style="width: 4%" />
<col style="width: 42%" />
<col style="width: 20%" />
<col style="width: 22%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td><p>Retrieve identification via IoT-Core + Visualizer in OPERATE;</p>
<p>confirm human-readable, browser-accessible</p></td>
<td>Functional CR 7.8; confirms "easily accessible"</td>
<td>Requirements-based verification</td>
<td>SVV-1</td>
</tr>
<tr>
<td>2</td>
<td><p>Availability-across-states: continuously poll while driving Init (power-cycle), Update (999 + install reboot), FatalError;</p>
<p>log outage windows + SCPU-flash window</p></td>
<td>Proves G-1 (not available "at all times"; design, not attack)</td>
<td>NIST SP 800-115 §3.2</td>
<td>SVV-2</td>
</tr>
<tr>
<td>3</td>
<td><p>Connection-hold self-DoS: open and hold 2 HTTP connections;</p>
<p>attempt a 3rd legitimate identification read</p></td>
<td>Proves G-2 (the CR 7.1 mechanism is itself a CR 7.1 weakness)</td>
<td><p>MITRE ATT&amp;CK for ICS T0814;</p>
<p>NIST SP 800-115 §5.2;</p></td>
<td>SVV-4</td>
</tr>
<tr>
<td>4</td>
<td>Redundancy check: with a COM/SysCom interruption present, confirm identification is unavailable while the safety function persists</td>
<td>Proves G-3 (availability inversion)</td>
<td><p>NIST SP 800-115 §3.2;</p>
<p>OWASP ISTG-DES</p></td>
<td>SVV-3</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ007-01 - Identification Availability & Accessibility Baseline</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-007 🡪 CR 7.8 / CR 6.1 🡪 Asset H, Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>N/A, functional/accessibility verification</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Confirm that, in normal operating state, the safety-relevant installed-software identification is retrievable and presented in an easily accessible form (browser-based visualizer + human-readable version strings), establishing the availability baseline.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>In normal operating state, open the device's browser-based information interface.</p></li>
<li><p>Retrieve all safety-relevant software identifiers.</p></li>
<li><p>Confirm values are human-readable and the interface renders without special tooling.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if the interface loads and all safety-relevant identifiers are shown in human-readable form.</p>
<p>FAIL if any identifier is unreadable or the interface is inaccessible in normal operation.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ007-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Kali + device in OPERATE.</td>
</tr>
<tr>
<td>Tools</td>
<td>Browser (IoT-Core Visualizer), curl</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># Manual step on laptop (Port 4):</p>
<p># Open browser -&gt; navigate to http://192.168.0.2/</p>
<p># -&gt; IoT-Core Visualizer should load; navigate to the "deviceinfo" menu</p>
<p># -&gt; Take a screenshot as proof of it being "human-readable, easily accessible"</p>
<p># Kali command (supplementary proof via curl):</p>
<p>curl -s http://$SRIO/deviceinfo/swrevision/getdata | tee cm_rq007-01_swrev.txt</p></td>
</tr>
<tr>
<td>Result</td>
<td><em>Expected PASS: Visualizer loads without special tooling; all safety-relevant identifiers human-readable. Evidence: Visualizer screenshot, cm_rq007-01_swrev.txt.</em></td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ007-02 - Identification Availability Across Operating States</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-007 🡪 CR 7.8 / (availability, FR 7) 🡪 Asset H, Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>N/A, inherent unavailability (design/reliability)</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-2</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that identification data is not available "at all times" by continuously polling while the device transitions through initialization (power-cycle), update (including the install restart), and fatal-error safe-state, and by identifying the safety-CPU-flash window in which safety-sourced identifiers vanish.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Start a timestamped polling loop against one gateway-sourced and one safety-sourced identifier.</p></li>
<li><p>Power-cycle the device (initialization window).</p></li>
<li><p>Enter the update state and trigger the install restart.</p></li>
<li><p>Force the fatal-error safe-state.</p></li>
<li><p>Record every interval where the request fails or the safety-sourced value is absent.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Gap-characterization test.</p>
<p>Expected: measurable outage windows during initialization, install-restart, and fatal-error; and unavailability of safety-sourced identifiers during the flash window 🡪 confirms the "at all times" gap 🡪</p>
<p>FAIL against that clause. Continuous availability through all states would refute the gap (investigate).</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ007-02</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Kali polls continuously; TIA laptop</td>
</tr>
<tr>
<td>Tools</td>
<td>curl in a polling loop, TIA Online &amp; Diagnostics.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p># Start the polling loop in one terminal</p>
<p>while true; do</p>
<p>echo "$(date +%s) $(curl -s -o /dev/null -w '%{http_code}' --max-time 1 http://$SRIO/deviceinfo/swrevision/getdata)"</p>
<p>sleep 0.2</p>
<p>done | tee cm_rq007-02_poll.log</p>
<p># In a second terminal / on the TIA laptop, trigger state transitions</p>
<p># a) Init window: power-cycle the SRIO (disconnect/reconnect power cable)</p>
<p># b) Update window: rotary switch to 999 + power cycle</p>
<p># firmware only, see risk note in TC-RQ005-03), then exit update (power</p>
<p># cycle again)</p>
<p># c) FatalError: short-circuit an F-DI test pin briefly (as in TC-RQ003-04)</p>
<p># or another documented EC1-triggering condition</p>
<p># After the run, extract all failing/timed-out intervals</p>
<p>grep -v ' 200$' cm_rq007-02_poll.log</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: measurable outage windows during Init/update-restart/FatalError - confirms the “not available at all times” finding (G-1 in RQ-007).</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ007-03 - Connection-Hold Self-DoS on the Identification Interface</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-007 🡪 CR 7.1 / CR 7.2 🡪 Asset H</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Denial of Service (self-inflicted)</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that the concurrent-connection limit, intended as denial-of-service protection, is itself a denial-of-service vector: holding the maximum permitted connections exhausts the pool and blocks all further legitimate access to the identification interface, defeating "at all times" without any bandwidth-based flooding.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>In normal operating state, open and hold the maximum number of permitted connections (no completion / slow read).</p></li>
<li><p>From an additional client, attempt a legitimate identification read.</p></li>
<li><p>Measure whether the additional request is refused or times out.</p></li>
<li><p>Release one held connection; confirm access is restored.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS against the requirement if a legitimate additional read still succeeds while the maximum connections are held.</p>
<p>Expected FAIL: the additional request is blocked, and access returns only after release 🡪 confirms the self-inflicted availability failure.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ007-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Kali</td>
</tr>
<tr>
<td>Tools</td>
<td>curl</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>LOGDIR=~/rq007-03_evidence</p>
<p>mkdir -p $LOGDIR</p>
<p>cd $LOGDIR</p>
<p>echo " Baseline: Connection working normally" | tee cm_rq007-03_00_baseline.txt</p>
<p>( time curl -s --max-time 5 http://$SRIO/deviceinfo/swrevision/getdata ) &gt;&gt; cm_rq007-03_00_baseline.txt 2&gt;&amp;1</p>
<p>cat cm_rq007-03_00_baseline.txt</p>
<p>echo "Block both slots"</p>
<p>for i in 1 2; do</p>
<p>(exec 3&lt;&gt;/dev/tcp/$SRIO/80; printf 'GET /deviceinfo HTTP/1.1\r\nHost: x\r\n\r\n' &gt;&amp;3; sleep 600) &amp;</p>
<p>done</p>
<p>jobs | tee cm_rq007-03_01_jobs.txt</p>
<p>echo "3rd attempt while both slots are occupied (expected: timeout)" | tee cm_rq007-03_02_blocked.txt</p>
<p>( time curl -s --max-time 5 http://$SRIO/deviceinfo/swrevision/getdata ) &gt;&gt; cm_rq007-03_02_blocked.txt 2&gt;&amp;1</p>
<p>cat cm_rq007-03_02_blocked.txt</p>
<p>echo "Free up one slot"</p>
<p>kill %1</p>
<p>echo "Retry after freeing up slot (expected: successful again)" | tee cm_rq007-03_03_after_release.txt</p>
<p>( time curl -s --max-time 5 http://$SRIO/deviceinfo/swrevision/getdata ) &gt;&gt; cm_rq007-03_03_after_release.txt 2&gt;&amp;1</p>
<p>cat cm_rq007-03_03_after_release.txt</p>
<p>echo "Cleanup: releasing second slot as well"</p>
<p>kill %2</p>
<p>echo ""</p>
<p>echo "SUMMARY"</p>
<p>echo "- Baseline -"; cat cm_rq007-03_00_baseline.txt</p>
<p>echo "- While blocked -"; cat cm_rq007-03_02_blocked.txt</p>
<p>echo "- After release -"; cat cm_rq007-03_03_after_release.txt</p></td>
</tr>
<tr>
<td>Expected</td>
<td><p>Expected FAIL vs requirement: 3rd legitimate read blocked/timeout while 2 held; access restored only after release.</p>
<p>Evidence: cm_rq007-03_hold.log, curl timing before/after.</p></td>
</tr>
</tbody>
</table>

**TC-RQ007-04 - Availability Inversion under Gateway/Internal-Comms Interruption**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-007 🡪 CR 7.2 🡪 Asset H, Asset F</td>
</tr>
<tr>
<td>Target Threat</td>
<td>N/A , reliability/redundancy</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that a fault or internal-communication timeout in the non-safety gateway removes identification availability entirely while the safety function persists, so identification is structurally less available than the safety function it describes.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Establish normal operation with identification available.</p></li>
<li><p>Induce a gateway or internal-communication interruption.</p></li>
<li><p>Confirm the safety function persists (safe I/O behaviour unaffected).</p></li>
<li><p>Confirm identification becomes unavailable during the interruption.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Gap-characterization test.</p>
<p>Expected: identification unavailable while the safety function persists 🡪 confirms the no-redundancy gap (availability inversion).</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ007-04</td>
</tr>
<tr>
<td>HW/Network</td>
<td>partially Feasible: The entire fieldbus path is interrupted (switch port 2), yielding the same finding: IoT-Core AND safety communication depend on the same physical interface (no redundancy).</td>
</tr>
<tr>
<td>Tools</td>
<td>curl polling script, switch CLI/web UI, TIA Online &amp; Diagnostics.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p># 1. Establish normal operation (both safety function and IoT-Core reachable).</p>
<p># 2. Disable switch port 2 (complete communication outage):</p>
<p># switch web UI/CLI: administratively shut down port 2</p>
<p># 3. Observe:</p>
<p>curl -s -o /dev/null -w '%{http_code}\n' --max-time 2 http://$SRIO/deviceinfo/swrevision/getdata</p>
<p># (expected: curl times out / non-200)</p>
<p># In parallel, check the TIA watch table: qualifier bad, outputs de-energized</p>
<p># after F_WD_Time (as in TC-RQ001-05)</p>
<p># 4. Re-enable port 2; check re-integration/acknowledgement in TIA.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: IoT-Core and safety communication fail TOGETHER (no separate diagnostic access while safety operation is active) - confirms the lack of redundancy (G-3); this may differ from the originally assumed pure „availability inversion“ - instead a common failure cause; document accordingly.</td>
</tr>
</tbody>
</table>

**REQUIREMENT 8**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-008

- **MVO Requirement Text:** The system shall collect evidence of any legitimate or illegitimate intervention in the software installed on it.

- **IEC 62443-4-2 CR Mapping :** CR 2.8, CR 2.9, CR 2.10 CR 2.11, CR 2.12, EDR 2.13, CR 3.9, CR 6.1

- **Target Assets:** D (subject of intervention); G (software-invention trigger); I (evidence), F (Domain separation)

- **STRIDE:** (Tampering, ) Repudiation

- **Security Function (Mitigation):**

  - COM Error Log: FW-update actions, self-detected errors, SysCom timeout (SRIO-10665).

  - SysCom update command/response events: USER_SYS_RSP_UPDATE\_\* (SRIO-10785).

  - /firmware/version + I&M0 SOFTWARE_REVISION delta: Version change is observable.

  - Update-state LED sequence: US green / FS on fail (SRIO-11359 ff.).

  - Debug/test interface declared development

- **Identified Gap:**

  - G-1: Events recorded without actor identity; no user auth on the FW-update path (password removed, SRIO-8299) 🡪 CR 2.12 unmet. An illegitimate intervention avoiding the official path is unrecorded/unattributable.

  - G-2: RQ-008 demands evidence of BOTH legitimate AND illegitimate intervention. The evidence footprint of a genuine update and a modified/unsigned image is identical (‘update completed’ + version change). Cause = no signature verification, but that PROTECTION gap is RQ-005 (TC-RQ005-03); here the finding is that the evidence cannot CLASSIFY the two.

  - G-3: /firmware/install ‘initiates a reboot to install’ (SRIO-2953) and Exit-Update requires a power reset (SRIO-9916); a cold start clears the log (SRIO-6521) and resets uptime (SRIO-15398). The act of installing software destroys the log evidence of that installation. (The 5-year retention dimension 🡪 RQ-012.)

  - G-4: Production_fuse exclusion (EDR 2.13); a re-probe still generates no log entry.

**Step 2: Methodological Test Planning**

<table>
<colgroup>
<col style="width: 4%" />
<col style="width: 42%" />
<col style="width: 20%" />
<col style="width: 22%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>Enumerate the software-event evidence that exists: Error Log, /firmware/version, I&amp;M0 SOFTWARE_REVISION at baseline</td>
<td>Functional baseline (CR 6.1; CR 2.8 partial)</td>
<td><p>Requirements-based verification;</p>
<p>NIST SP 800-115 §3.2</p></td>
<td>SVV-1</td>
</tr>
<tr>
<td>2</td>
<td><p>Perform a legitimate authorized FW update;</p>
<p>capture whether a retained, time-stamped, attributed record survives the install reboot</p></td>
<td>Proves G-3 (self-erasing install) + G-1</td>
<td>NIST SP 800-115 §3.2 / §7</td>
<td>SVV-2</td>
</tr>
<tr>
<td>3</td>
<td><p>Compare evidence footprints of a legitimate update vs the modified/unsigned image installed in TC-RQ005-03;</p>
<p>check whether the log distinguishes them</p></td>
<td>Proves G-2 (evidence cannot classify)</td>
<td>MITRE ATT&amp;CK for ICS T0872; OWASP ISTG-FW[UPDT]</td>
<td>SVV-4</td>
</tr>
<tr>
<td>4</td>
<td>Time-attribution across the install cold start (reuse TC-RQ003-04 method): uptime resets, no absolute timestamp</td>
<td>Proves G-1/CR 2.11</td>
<td>NIST SP 800-115 §3.2</td>
<td>SVV-3</td>
</tr>
<tr>
<td>5</td>
<td>Attempt the production-gated FIT path (/fit/setfit, WO/P); confirm exclusion produces no log entry (reuse RQ-003 Scenario 5)</td>
<td><p>Validates EDR 2.13;</p>
<p>confirms G-4</p></td>
<td><p>NIST SP 800-115 §4.2;</p>
<p>OWASP FSTM / ISTG-PHY</p></td>
<td>SVV-3</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ008-01 - Software-Event Evidence Baseline</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-008 🡪 CR 2.8 / CR 6.1 🡪 Asset I, Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Establish which software-intervention evidence the device produces and whether it is readable (audit/error log; firmware version; software-revision identity record), and inspect each for actor identity and absolute timestamp.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Read the error log and firmware/software-revision records at a known-good baseline.</p></li>
<li><p>Trigger a benign self-detected software event.</p></li>
<li><p>Re-read; confirm an audit entry appears.</p></li>
<li><p>Inspect the entry for identity and absolute timestamp.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if the log and software records are readable and the induced event is captured.</p>
<p>Documented shortfall if no entry carries actor identity or absolute timestamp.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ008-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Kali (curl), TIA laptop.</td>
</tr>
<tr>
<td>Tools</td>
<td>curl.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq008-01_baseline.json</p>
<p>curl -s http://$SRIO/firmware/version/getdata</p>
<p>curl -s http://$SRIO/deviceinfo/swrevision/getdata</p>
<p># Trigger a benign, self-detected software event, e.g. a brief SysCom</p>
<p># interruption; short-circuit method from TC-RQ003-04.</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq008-01_after_event.json</p>
<p>diff cm_rq008-01_baseline.json cm_rq008-01_after_event.json</p>
<p>I&amp;M0</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: an entry is created, but without actor identity and without an absolute timestamp (only an uptime reference).</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ008-02 - Self-Erasing Firmware Install</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-008 🡪 CR 3.9 / CR 2.11 🡪 Asset I, Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation (+Tampering)</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-2</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that a legitimate firmware install destroys its own evidence: the install restart (and the mandatory update-exit power reset) triggers a cold start that clears the audit log and resets the uptime reference, so no retained, time-stamped record of the software intervention survives.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Baseline the audit log and uptime reference.</p></li>
<li><p>Perform an authorized firmware update (enter update state, upload, install).</p></li>
<li><p>After the install restart, re-read the audit log and uptime reference.</p></li>
<li><p>Determine whether any persistent, time-stamped record of the install remains.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Gap-characterization test.</p>
<p>Expected: post-install log cleared and uptime reset 🡪 the install has erased its own evidence 🡪</p>
<p>FAIL against RQ-008. A retained, time-stamped install record would refute the gap (investigate).</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ008-02</td>
</tr>
<tr>
<td>HW/Network</td>
<td>TIA laptop (rotary-switch/reboot control, triggering the update)</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq008-02_before.json</p>
<p>curl -s http://$SRIO/systemtime/systick/getdata | tee cm_rq008-02_systick_before.txt</p>
<p># Enter update state and re-upload/install the OFFICIAL current firmware:</p>
<p># 1. Rotary switch to 999 + power cycle</p>
<p># 2. Upload the official update container via IoT-Core Visualizer or curl</p>
<p># (see /firmware/container/start_stream_set + stream_set, as in</p>
<p># TC-RQ005-03 step 3, but with the UNMODIFIED official file)</p>
<p># 3. curl -s -X POST http://$SRIO/firmware/install</p>
<p># (device restarts automatically as part of the install)</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq008-02_after.json</p>
<p>curl -s http://$SRIO/systemtime/systick/getdata | tee cm_rq008-02_systick_after.txt</p>
<p>diff cm_rq008-02_before.json cm_rq008-02_after.json</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected FAIL (against the requirement) - the log is cleared by the install-triggered cold start and the systick resets to ~0; no persistent, timestamped record of the installation remains on the device itself.</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ008-03 - Legitimate vs Illegitimate: Evidence Cannot Classify</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-008 🡪 CR 2.8 (classification intent) 🡪 Asset D, Asset I, Asset F</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that the evidence record cannot distinguish a legitimate update from an illegitimate one: installing a modified/unsigned image (installation performed per TC-RQ005-03) produces the same audit/version footprint as a genuine update, so the "legitimate OR illegitimate" evidence obligation is unmet. The cause, no signature verification, is RQ-005's protection gap; RQ-008 tests only the evidence footprint.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Record the evidence delta of a legitimate update (from TC-RQ008-02).</p></li>
<li><p>On the spare DUT, install the modified/unsigned image per TC-RQ005-03.</p></li>
<li><p>Record its evidence delta (log entries, version change, any classification flag).</p></li>
<li><p>Compare: determine whether any evidence field marks the second install as illegitimate/unauthorized.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Gap-characterization test.</p>
<p>Expected: the illegitimate install produces an indistinguishable footprint (same completion semantics + version change, no authenticity flag) 🡪 confirms the classification gap 🡪</p>
<p>FAIL. Any field flagging the unsigned image as illegitimate would refute the gap (record as a positive finding).</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ008-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td>spare unit</td>
</tr>
<tr>
<td>Tools</td>
<td>curl</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Take the evidence delta of a legitimate installation from TC-RQ008-02</p>
<p># as the reference.</p>
<p># 2. Capture the evidence delta of the (in TC-RQ005-03 performed) manipulated</p>
<p># installation (log entries, firmware version string, any classification</p>
<p># flag):</p>
<p>export SRIO=192.168.0.2</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq008-03_after_manipulated.json</p>
<p>curl -s http://$SRIO/firmware/version/getdata | tee cm_rq008-03_version_after.txt</p>
<p># 3. Compare both deltas.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: both installation types produce an identical log/version footprint with no distinguishing feature (“legitimate” vs. “illegitimate”) - confirms G-2.</td>
</tr>
</tbody>
</table>

**TC-RQ008-04 - Time-Attribution across the Install Cold Start ⇄ TC-RQ003-04**

**Level 1 - Abstract Test Scenario**

| Field | Content |
|----|----|
| Traceability | RQ-008 🡪 CR 2.11 / CR 3.9 🡪 Asset I |
| Target Threat | Repudiation |
| SVV Category | SVV-3 |
| Objective | By reference to the TC-RQ003-04 method, demonstrate that the install cold start resets the uptime reference and that no absolute timestamp is attached to either the pre- or post-install state. |
| Steps | Execute the TC-RQ003-04 method around a firmware install; record against RQ-008 traceability. |
| Pass/Fail | Expected: uptime resets, no absolute timestamp on the install event 🡪 CR 2.11 unmet |

**Level 2 - Concrete Execution**

| Field | Content |
|----|----|
| Ref. Test Case | TC-RQ008-04 |
| HW/Network | Kali |
| Tools | curl, TIA. |
| Procedure | Execute the TC-RQ003-04 method around a firmware install; record under RQ-008. |
| Result | Expected: uptime resets, no absolute timestamp on the install event (CR 2.11 unmet). Evidence: systick before/after install. |

**TC-RQ008-05 - Excluded (Development-Only) Interface Produces No Evidence ⇄ TC-RQ003-05**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-008 🡪 EDR 2.13 🡪 Asset D, Asset I</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>By reference to TC-RQ003-05, confirm the production-gated diagnostic path is rejected on a production unit and that exercising the excluded interface produces no log entry.</td>
</tr>
<tr>
<td>Steps</td>
<td><p>Execute per TC-RQ003-05;</p>
<p>record against RQ-008</p></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>As TC-RQ003-05.</p>
<p>Documented gap: excluded interface produces no evidence</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ008-05</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Kali, directly against SRIO</td>
</tr>
<tr>
<td>Tools</td>
<td>curl</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>curl -s -X POST http://$SRIO/fit/setfit -d '{"type":1}' -w "%{http_code}\n" | tee cm_rq008-05_fit.txt</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq008-05_errorlog.json</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: rejection (HTTP error code / service not executable) and NO new log entry for this attempt.</td>
</tr>
</tbody>
</table>

**REQUIREMENT 9**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-009

- **MVO Requirement Text:** The system shall collect evidence of any modification of the installed software or its configuration.

- **IEC 62443-4-2 CR Mapping:** CR 2.8, CR 2.9, CR 2.10, CR 2.11, CR 2.12, (CR 3.4 Addition,) CR 3.9, CR 6.1

- **Target Assets:** B (Config); D (Firmware); F (Domain separation); I (Audit Data)

- **STRIDE:** (Tampering,) Repudiation

- **Security Function (Mitigation):**

  - iParCRC/F_ParCRC change + I&M4 signature: Modification is fingerprinted (SRIO-3011).

  - Acyclic config write blocked after param-end (SRIO-7749): temporal write gate.

  - FW/HW compatibility check + error-log entry; /firmware/version delta: Version modification observable.

- **Identified Gap:**

  - G-1: Configuration is authored in the engineering tool, stored on the (password-protected) PLC and pushed via fieldbus (SRIO-1983; System-Architecture §3.2). The actor is knowable, but only at the PL)/engineering-tool layer, not device-resident 🡪 device-level CR 2.12 is architecturally delegated for this QM slave.

  - G-2: No RTC; uptime resets on cold start 🡪 modifications not datable.

  - G-3 (asymmetric persistence): Error-Log detail is cleared on cold start (volatile).

**Step 2: Methodological Test Planning**

<table style="width:100%;">
<colgroup>
<col style="width: 4%" />
<col style="width: 39%" />
<col style="width: 19%" />
<col style="width: 28%" />
<col style="width: 9%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>Enumerate the config-modification evidence surface (iParCRC/I&amp;M4, Error Log) at baseline</td>
<td>Functional baseline (CR 6.1 met; CR 2.8 partial)</td>
<td><p>Requirements-based verification;</p>
<p>NIST SP 800-115 §3.2</p></td>
<td>SVV-1</td>
</tr>
<tr>
<td>2</td>
<td>Change one iPar; capture I&amp;M4 delta; cold-start and re-read; check for time/actor</td>
<td>Proves G-2 and settles G-3</td>
<td>NIST SP 800-115 §3.2 + §7</td>
<td>SVV-2</td>
</tr>
<tr>
<td>3</td>
<td><p>Actor-delegation analysis: authorized config change;</p>
<p>confirm the device holds no actor identity;</p>
<p>attribution exists only in the PLC/ engineering project</p></td>
<td>Proves G-1</td>
<td>NIST SP 800-115 §3.1/§3.2</td>
<td>SVV-3</td>
</tr>
<tr>
<td>4</td>
<td><p>Post-param-end write-gate: attempt an acyclic config write after param-end;</p>
<p>confirm rejection and absence of an evidence entry</p></td>
<td><p>Validates temporal write-gate;</p>
<p>no-evidence-on-block</p></td>
<td><p>OWASP ISTG-DES;</p>
<p>NIST SP 800-115 §5.2</p></td>
<td>SVV-3</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ009-01 - Config-Modification Evidence Surface Baseline</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-009 🡪 CR 2.8 / CR 3.4 / CR 6.1 🡪 Asset B, Asset I</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td><p>Establish which configuration-modification evidence mechanisms exist and are readable (the parameter-change counter, the configuration signature, and the audit log);</p>
<p>inspect each for actor identity and absolute timestamp. Firmware-modification evidence 🡪 RQ-008.</p></td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Read the audit log, the change counter, and the configuration signature at a known baseline.</p></li>
<li><p>Record which fields carry identity/timestamp.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS (partial baseline) if config-modification indicators are readable.</p>
<p>Documented shortfall where no field carries actor identity or absolute timestamp.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ009-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Kali (curl), TIA laptop (I&amp;M4/iParCRC display)</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq009-01_errorlog.json</p>
<p># In TIA: Online &amp; Diagnostics &gt; Identification &amp; Maintenance &gt; I&amp;M4</p>
<p># (record the signature value: F_iParCRC + F_Par_CRC as hex)</p>
<p># Check both sources for any actor-identity field or absolute timestamp.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: parameter-change indicators (iParCRC value) are readable, but without actor identity/timestamp.</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ009-02 - Config-Modification Evidence & Asymmetric</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-009 🡪 CR 2.8 / CR 2.11 / CR 3.9 🡪 Asset B, Asset I</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-2</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that a configuration/parameter-modification event produces an asymmetric evidence trail: the parameter-change fingerprint (I&amp;M4 signature / iParCRC-F_ParCRC), Error-Log entry describing WHEN and HOW the change was applied does not, leaving a permanent fingerprint without context, and a contextual log entry that is lost.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Read the I&amp;M4 signature and the Error Log at baseline.</p></li>
<li><p>Perform an authorized parameter change (via the engineering tool) and record the resulting I&amp;M4 signature and any generated log entry.</p></li>
<li><p>Cold-start the device.</p></li>
<li><p>Re-read the I&amp;M4 signature and the Error Log; compare persistence of both indicators across the reset.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td>Expected gap-characterization result: the I&amp;M4 signature, Error-Log entry documenting the change is cleared by the cold start, confirming an asymmetric, incomplete evidence trail for configuration modifications.</td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ009-02</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Kali (curl), TIA laptop</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p># 1. Baseline:</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq009-02_log_before.json</p>
<p># In TIA: read I&amp;M4 signature (Online &amp; Diagnostics &gt; Identification &amp;</p>
<p># Maintenance &gt; I&amp;M4), record F_iParCRC/F_Par_CRC.</p>
<p># 2. Authorized parameter change (as in TC-RQ004-04, step 1): change a</p>
<p># parameter, recompute iParCRC via ifm-CRC-Tool, compile + download.</p>
<p># Read I&amp;M4 signature again (new value); read the error log again:</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq009-02_log_after_change.json</p>
<p># 3. Cold start (disconnect/reconnect power cable).</p>
<p># 4. Re-read both indicators:</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq009-02_log_after_coldstart.json</p>
<p># In TIA: read I&amp;M4 signature again.</p>
<p>diff cm_rq009-02_log_after_change.json cm_rq009-02_log_after_coldstart.json</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: the I&amp;M4 signature and error-log entry does not confirms an asymmetric, incomplete evidence trail for configuration modifications.</td>
</tr>
</tbody>
</table>

<span class="mark">TC-RQ009-03 - Actor Attribution Is Delegated, Not Device-Resident</span>

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-009 🡪 CR 2.12 🡪 Asset B, Asset F</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that because configuration is authored at the engineering tool and pushed from the (access-controlled) controller over the fieldbus, the device holds no actor identity for a configuration modification, attribution, if it exists, resides in the controller/engineering project, not on the device. This bounds CR 2.12 as delegated, not implemented at component level.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Perform an authorized configuration change from a known engineering-tool user.</p></li>
<li><p>Inspect every device-side evidence field for any actor/identity attribute.</p></li>
<li><p>Inspect the controller/engineering side for where the actor identity resides.</p></li>
<li><p>Conclude where (if anywhere) non-repudiation is anchored.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Gap-characterization test.</p>
<p>Expected: no device-side field carries an actor identity 🡪 CR 2.12 not met at the device; attribution only at the controller/engineering layer 🡪 confirms attribution is delegated. Documented as: device-level non-repudiation for configuration modification is architecturally delegated for this QM component.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ009-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td>TIA laptop + Kali</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Perform an authorized parameter change via TIA as in TC-RQ004-04 step 1.</p>
<p># 2. Check all available evidence fields on the SRIO for an actor-identity</p>
<p># attribute:</p>
<p>export SRIO=192.168.0.2</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq009-03_errorlog.json</p>
<p># In TIA: check I&amp;M1-I&amp;M4 for any user-identity field.</p>
<p># 3. On the PLC/engineering side, check where the attribution actually</p>
<p># resides (TIA project history, Windows user account, TIA project version control if used).</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: no field on the SRIO itself contains an actor identity; attribution exists only at the PLC/engineering layer - confirms G-1 (attribution is delegated, not device-resident).</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ009-04 - Post-Configuration-Phase Write Gate</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-009 🡪 CR 3.4 🡪 Asset B</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Validate the temporal write-gate: an attempt to write configuration records after the configuration phase has ended is rejected, and confirm whether the blocked attempt itself generates any evidence entry.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Complete the configuration phase and reach operation.</p></li>
<li><p>Attempt an acyclic configuration write after the configuration phase end.</p></li>
<li><p>Observe rejection.</p></li>
<li><p>Inspect the audit log for any entry corresponding to the blocked attempt.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS (write-gate valid) if the post-phase write is rejected.</p>
<p>Documented observation: whether a blocked attempt produces an evidence entry (expected: none).</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ009-04</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1: Kali (port 3), SRIO in Operate</td>
</tr>
<tr>
<td>Tools</td>
<td>Scapy (recreating a PROFINET acyclic write), Wireshark</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Bring the SRIO into Operate (parametrization phase completed, param-end</p>
<p># already sent by the PLC).</p>
<p># 2. Send an acyclic-write telegram to the F-parameter index (0x200,</p>
<p># SRIO-2999) using Scapy:</p>
<p>cat &gt; cm_rq009-04_write.py &lt;&lt; 'PYEOF'</p>
<p>from scapy.all import Ether, Raw, sendp</p>
<p>iface = "eth1"</p>
<p>target_mac = "AA:BB:CC:DD:EE:FF"</p>
<p>acyclic_write_frame = bytes.fromhex("REPLACE_WITH_ACYCLIC_WRITE_RECORD_HEX")</p>
<p>sendp(Ether(dst=target_mac, type=0x8892)/Raw(load=acyclic_write_frame),</p>
<p>iface=iface, count=1)</p>
<p>PYEOF</p>
<p>sudo python3 cm_rq009-04_write.py</p>
<p># 3. Check the response/diagnostics; check the error log for a corresponding</p>
<p># entry:</p>
<p>export SRIO=192.168.0.2</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq009-04_errorlog.json</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected PASS: the write attempt is rejected; as expected, NO log entry is created for the rejected attempt (observation to document).</td>
</tr>
</tbody>
</table>

**REQUIREMENT 10**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-010

- MVO Requirement Text: The control system shall withstand reasonably foreseeable malicious attempts from third parties that could lead to a hazardous situation.

- **IEC 62443-4-2 CR Mapping :** CR 3.5, CR 3.6, CR 3.7, CR 7.1 (1), CR 7.2

- **Target Assets:** A (Trusted Safety Function, E Safety Monitoring), F (Domain Separation)), H (Network)

- **STRIDE:** Denial of Service (primary); Tampering, Spoofing, Elevation of Privilege

- **Security Function (Mitigation):**

  - External HW watchdog + F_WD_Time --\> passivation (CR 3.6).

  - Black-channel principle: COM = QM; safety on SCPU.

  - Dual SCPU cross-check + STL: Random-fault detection.

  - PROFINET Net Load Class III (SRIO-1916), CC-C (SRIO-1915), IRT non-disturbance, port deactivation: Conformant-load robustness.

  - 2-connection HTTP cap (SRIO-7909).

- **Identified Gap:**

  - G-1: Net Load Class III certifies robustness to high CONFORMANT load, but there is no documented protection against MALFORMED frames or application-layer floods on the IoT/DCP path 🡪 verify by fuzzing/flood.

  - G-2: Even if every attack resolves safely to passivation, continuous forced passivation = continuous unavailability of the safety function 🡪 the device satisfies the FAIL-SAFE interpretation but may fail the AVAILABILITY interpretation of ‘withstand’ (a permanently safe-stated machine can itself be an operational hazard).

  - G-3: Almost all foreseeable attacks resolve to the safe state (black channel + watchdog + CR 3.6) except the unsigned-firmware install (RQ-005 G-2 / TC-RQ005-03), which installs attacker-controlled safety firmware --\> can lead to a hazardous situation. RQ-010 is met for the communication/DoS/fuzzing classes but NOT for the firmware-integrity class.

**Step 2: Methodological Test Planning**

<table>
<colgroup>
<col style="width: 4%" />
<col style="width: 42%" />
<col style="width: 20%" />
<col style="width: 22%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>Baseline resilience: nominal PROFIsafe exchange under rated Net Load Class III conditions; confirm stable OPERATE</td>
<td>Functional baseline CR 7.1/7.2</td>
<td><p>Requirements-based;</p>
<p>PROFINET Net Load Class III</p></td>
<td>SVV-1</td>
</tr>
<tr>
<td>2</td>
<td><p>PROFINET/L2 flood (escalating rate); observe safe-comms vs safe-passivation vs undefined;</p>
<p>sustain to test repeated passivation</p></td>
<td>Proves G-1/G-2</td>
<td><p>MITRE T0814;</p>
<p>NIST SP 800-115 §5.2;</p>
<p>ifm CM-009</p></td>
<td>SVV-4</td>
</tr>
<tr>
<td>3</td>
<td><p>Protocol fuzzing :</p>
<p>malformed PROFINET/DCP + PROFIsafe + HTTP;</p>
<p>monitor crash/hang vs safe rejection</p></td>
<td>Proves CR 3.5/3.7; characterizes G-1</td>
<td><p>OWASP FSTM Stage 7;</p>
<p>ifm CM-010 (boofuzz);</p>
<p>MITRE T0836</p></td>
<td>SVV-4</td>
</tr>
<tr>
<td>4</td>
<td><p>IoT-Core application-layer flood request flood;</p>
<p>confirm COM-path attack does not reach the safety path (domain separation)</p></td>
<td>Confirms Asset F resilience</td>
<td><p>ifm CM-009;</p>
<p>NIST SP 800-115 §4.3;</p>
<p>MITRE T0814</p></td>
<td>SVV-3</td>
</tr>
<tr>
<td>5</td>
<td>Outcome-verification harness (aggregate): for Tests 2-4 + imported TC-RQ001-02 and TC-RQ005-03, confirm outputs = Low + qualifier bad (CR 3.6), else flag hazardous</td>
<td>The EHSR success criterion; surfaces G-3 exception</td>
<td>Requirements-based + threat-mitigation; PROFIsafe passivation theory</td>
<td>SVV-2</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ010-01 - Baseline Resilience under Rated Conformant Load</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-010 🡪 CR 7.1 / CR 7.2 🡪 Asset A, Asset H</td>
</tr>
<tr>
<td>Target Threat</td>
<td>N/A, functional baseline</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Confirm stable operation and safe communication under the device's rated conformant network-load conditions, establishing the resilience baseline.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Establish normal operating state.</p></li>
<li><p>Apply network load up to the rated conformant-load class.</p></li>
<li><p>Monitor safe communication, qualifier, and output state.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if safe communication and stable operation are maintained under rated conformant load.</p>
<p>FAIL if the device loses safe communication or destabilizes within rated load.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ010-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>PROFINET conformance-test tool, Kali, TIA laptop</td>
</tr>
<tr>
<td>Tools</td>
<td>hping3, nmap --min-rate, Siege (CM-009, HTTP path), TIA Online &amp; Diagnostics.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p># 1. Establish the baseline PROFIsafe connection as in TC-RQ001-01.</p>
<p># 2. Generate approximated load (run in parallel):</p>
<p>sudo hping3 --flood --rand-source -2 -p 34964 $SRIO &amp;</p>
<p>siege -c 50 -t 5M -v http://$SRIO/deviceinfo/getdata -l cm_rq010-01_siege.log</p>
<p># 3. While the load runs, observe the TIA watch table for connection</p>
<p># stability / qualifier.</p></td>
</tr>
<tr>
<td>Expected</td>
<td>Expected PASS - safety communication remains stable within the Kali-generated load limits (qualifier stays good, no passivation).</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ010-02 - Network/Layer-2 Flood Resilience</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-010 🡪 CR 7.1 (RE1) / CR 7.2 / CR 3.6 🡪 Asset H, Asset A, Asset E, Asset F</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Denial of Service</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td><p>Determine behavior under a high-rate network flood:</p>
<p>(a) maintain safe communication (conformant-load robustness),</p>
<p>(b) passivate to the defined safe state, or</p>
<p>(c) enter an undefined/hazardous state; and whether sustained flooding causes continuous forced passivation (availability impact).</p></td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Establish normal operating state.</p></li>
<li><p>Apply an escalating frame flood (unicast + broadcast).</p></li>
<li><p>Continuously monitor qualifier, output state, and device state.</p></li>
<li><p>Sustain the flood; measure recovery vs. continuous passivation.</p></li>
<li><p>Stop; confirm acknowledged re-integration.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if the device maintains safe communication up to its rated limits and, beyond them, passivates to the safe state (outputs de-energized, qualifier bad) with no undefined/unsafe output.</p>
<p>FAIL if any flood level produces an undefined or hazardous output state. Continuous forced passivation under sustained flood is recorded as an availability finding.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ010-02</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1</td>
</tr>
<tr>
<td>Tools</td>
<td>hping3, macof (dsniff package), Wireshark, TIA Online &amp; Diagnostics.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p># 1. Establish baseline.</p>
<p># 2. Escalating flood:</p>
<p>sudo hping3 --flood --rand-source $SRIO</p>
<p># then, in a separate run:</p>
<p>sudo macof -i eth1</p>
<p># 3. Continuously observe the TIA watch table + diagnostics buffer; measure</p>
<p># the time until passivation / restart.</p>
<p># 4. Stop the load (Ctrl+C); confirm restart requires acknowledgement.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected PASS - the SRIO passivates in a controlled manner (safe state) instead of entering an undefined state; after the load ends, restart occurs after acknowledgement.</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ010-03 - Protocol Fuzzing Robustness</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-010 🡪 CR 3.5 / CR 3.7 / CR 3.6 🡪 Asset H, Asset A, Asset E</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td>Determine whether malformed fieldbus-discovery, safety-protocol, and web-interface inputs are safely rejected (input validation, error handling) or cause a crash/hang/undefined state, verifying the device "withstands" unexpected input without a hazardous condition.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Establish normal operating state.</p></li>
<li><p>Fuzz each interface with malformed inputs (discovery messages, safety-frame fields, web requests).</p></li>
<li><p>Monitor for crash/hang/watchdog reset vs. safe rejection/passivation.</p></li>
<li><p>Log every input that changes device state; root-cause each.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if all malformed inputs are safely rejected or resolve to passivation, with no crash into an undefined/hazardous state.</p>
<p>FAIL if any malformed input causes a hang, an uncommanded output, or an unrecoverable state other than the defined safe state.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 15%" />
<col style="width: 2%" />
<col style="width: 82%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th colspan="2">Content</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2">Ref. Test Case</td>
<td>TC-RQ010-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td colspan="2">NV1</td>
</tr>
<tr>
<td>Tools</td>
<td colspan="2">boofuzz (CM-010), ZAP/zaproxy (CM-004), Scapy (DCP fuzzing).</td>
</tr>
<tr>
<td>Procedure</td>
<td colspan="2"><p>export SRIO=192.168.0.2</p>
<p># 1. IoT-Core/HTTP fuzzing (CM-004 pattern):</p>
<p>zaproxy -daemon -host 127.0.0.1 -port 8090 -config api.disablekey=true &amp;</p>
<p>curl "http://127.0.0.1:8090/JSON/spider/action/scan/?url=http://$SRIO/"</p>
<p>curl "http://127.0.0.1:8090/JSON/ascan/action/scan/?url=http://$SRIO/"</p>
<p>curl "http://127.0.0.1:8090/OTHER/core/other/htmlreport/" -o cm_rq010-03_zap_report.html</p>
<p># 2. PROFINET DCP fuzzing (custom Scapy script, no TCP transport):</p>
<p>cat &gt; cm_rq010-03_dcp_fuzz.py &lt;&lt; 'PYEOF'</p>
<p>import random</p>
<p>from scapy.all import Ether, Raw, sendp</p>
<p>iface = "eth1"</p>
<p>target_mac = "AA:BB:CC:DD:EE:FF"</p>
<p>for i in range(200):</p>
<p>length = random.randint(1, 300)</p>
<p>fuzz_payload = bytes([random.randint(0, 255) for _ in range(length)])</p>
<p>sendp(Ether(dst=target_mac, type=0x8892)/Raw(load=fuzz_payload),</p>
<p>iface=iface, verbose=False)</p>
<p>PYEOF</p>
<p>sudo python3 cm_rq010-03_dcp_fuzz.py</p>
<p># 3. PROFIsafe frame fuzzing (reuse the byte layout from TC-RQ001-03,</p>
<p># randomize individual fields):</p>
<p>cat &gt; cm_rq010-03_safety_fuzz.py &lt;&lt; 'PYEOF'</p>
<p>import random</p>
<p>from scapy.all import Ether, Raw, sendp</p>
<p>iface = "eth1"</p>
<p>target_mac = "AA:BB:CC:DD:EE:FF"</p>
<p>base = bytearray.fromhex("REPLACE_WITH_CAPTURED_PROFISAFE_PAYLOAD_HEX")</p>
<p>for i in range(200):</p>
<p>mutated = bytearray(base)</p>
<p>idx = random.randrange(len(mutated))</p>
<p>mutated[idx] = random.randint(0, 255)</p>
<p>sendp(Ether(dst=target_mac, type=0x8892)/Raw(load=bytes(mutated)),</p>
<p>iface=iface, verbose=False)</p>
<p>PYEOF</p>
<p>sudo python3 cm_rq010-03_safety_fuzz.py</p>
<p># 4. During all runs, continuously observe SRIO state (LEDs, TIA watch</p>
<p># table, diagnostics buffer); log every crash/hang.</p></td>
</tr>
<tr>
<td>Result</td>
<td colspan="2">Expected PASS - all malformed inputs are safely rejected or resolve to controlled passivation; no hang/crash into an undefined state.</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ010-04 - Application-Layer Flood & Domain-Separation Confirmation</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-010 🡪 CR 7.2 / CR 5.1 🡪 Asset F, Asset H</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Denial of Service</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Apply an application-layer request flood to the non-safety interface and confirm the attack does not propagate to the safety path (domain separation holds).</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Establish normal operating state.</p></li>
<li><p>Apply an application-layer request flood to the non-safety interface.</p></li>
<li><p>Monitor the safety path (qualifier, outputs, safe communication) throughout.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if the safety path is unaffected (no passivation caused by, and no propagation of, the non-safety-path flood).</p>
<p>FAIL if the non-safety-path flood degrades or disturbs the safety function.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ010-04</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1</td>
</tr>
<tr>
<td>Tools</td>
<td>Siege (CM-009), curl.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>siege -c 100 -t 10M -v http://$SRIO/deviceinfo/getdata -l cm_rq010-04_siege.log &amp;</p>
<p># In parallel, observe the PROFIsafe connection / safety function in TIA</p>
<p># (watch table: qualifier, outputs).</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected PASS - the safety path remains unaffected by the web-interface flood (confirms domain separation / black-channel architecture).</td>
</tr>
</tbody>
</table>

**TC-RQ010-05 - Outcome-Verification Aggregation Harness**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-010 🡪 CR 3.6 🡪 Asset A, Asset E</td>
</tr>
<tr>
<td>Target Threat</td>
<td>N/A, aggregate outcome check across all classes</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-2</td>
</tr>
<tr>
<td>Objective</td>
<td>For every attack, the RQ-010-owned flood (TC-RQ010-02) and fuzz (TC-RQ010-03), plus the connecting-device spoofing (TC-RQ001-03/04) and unsigned-firmware install (TC-RQ005-03), positively verify the EHSR outcome: no attempt produces an uncommanded/unsafe output; the device continues safely or enters the defined safe state. Surface the one class (firmware) that escapes the fail-safe design.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Provide independent readback of the safe outputs.</p></li>
<li><p>For each attack case (owned + cross-referenced), sample output state and qualifier.</p></li>
<li><p>Classify each outcome as {safe-continue, safe-passivate, hazardous}.</p></li>
<li><p>Consolidate into an outcome matrix; flag any hazardous result.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS (RQ-010 met for that class) if every outcome is safe-continue or safe-passivate.</p>
<p>FAIL if any yields uncommanded/unsafe actuation.</p>
<p>Expected: flood/fuzz/spoofing classes PASS (black channel + CR 3.6); the firmware-install class is the documented exception that can lead to hazard.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ010-05</td>
</tr>
<tr>
<td>HW/Network</td>
<td>evaluation/aggregation task</td>
</tr>
<tr>
<td>Tools</td>
<td>Spreadsheet/test-management tool for consolidation.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. For each referenced test case, take the outcome (qualifier, outputs)</p>
<p># from its respective test log.</p>
<p># 2. Classify each into an outcome matrix {safe-continue, safe-passivate,</p>
<p># hazardous}.</p>
<p># 3. Flag any hazardous result for follow-up.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected - flood/fuzzing/spoofing classes result in safe-continue/safe-passivate; the firmware-installation class (TC-RQ005-03) remains the documented exception.</td>
</tr>
</tbody>
</table>

**REQUIREMENT 11**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-011

- **MVO Requirement Text:** The system shall prevent modifications to safety-relevant settings or rules, including those generated during a learning phase, where such modifications could lead to a hazardous situation.

- **IEC 62443-4-2 CR Mapping:** CR 1.1, CR 1.2, CR 2.1 (2), CR 3.4, EDR 3.10

- **Target Assets:** B (Safety Config), G (Operating Mode), F (Domain Separation)

- **STRIDE:** Tampering (, Spoofing, Elevation of Privilege)

- **Security Function (Mitigation):**

  - IoT-Core read-only, incoming-only: No parameter writes over IoT (SRIO-7908, SRIO-8299).

  - Parameter writes only via fieldbus/PLC 192.168.0.1 (PORT 1) engineering tool (SRIO-1983).

  - F-address/update-mode change needs physical Switch 192.168.0.91 + power-cycle (SRIO-10812, SRIO-2013).

  - FW update accepted only in Update state (SRIO-11534) the mode gate (authorization limb of RQ-005).

  - Config write blocked after param-end (SRIO-7749).

- **Identified Gap:**

  - G-1: Password protection was deliberately removed (SRIO-8299), so authorization for safety-parameter writes over the fieldbus is fully delegated to the environment (locked cabinet SRIO-9402), a CCSC-2 compensating control that is documented but NOT device-enforced. CR 1.1/1.2/2.1 are met only at system level, not component level.

  - G-2: DCP ‘Reset to Factory’ (Mode 2 mandatory) resets communication parameters; SRIO-7772/3030 describe modes, not authentication, and SRIO-3029 states an IO-Controller/engineering system ‘can change IP parameters or the NameOfStation at any time.’ Impact is BOUNDED: DCP reset hits communication parameters (🡪 passivation), not silent safety-iPar modification. Confirmed by Test 2.

  - G-3: Whether the Switch can be moved without visible seal damage, the authorization barrier's silent-defeat question

**Step 2: Methodological Test Planning**

<table>
<colgroup>
<col style="width: 4%" />
<col style="width: 42%" />
<col style="width: 20%" />
<col style="width: 22%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>Confirm the IoT-Core write-path is blocked (attempt parameter writes via IoT-Core; expect read-only)</td>
<td><p>Positive verification;</p>
<p>CR 2.1 read-only design</p></td>
<td><p>Requirements-based;</p>
<p>OWASP ISTG-DES-AUTHZ</p></td>
<td>SVV-1</td>
</tr>
<tr>
<td>2</td>
<td>DCP factory-reset without authentication from a peer node (Mode 2, then 3/4 if present); observe unauthenticated reset of com-config</td>
<td>Proves/refutes G-2</td>
<td>MITRE T0836 Modify Parameter; OWASP ISTG-DES-AUTHZ-001; NIST SP 800-115 §5.2</td>
<td>SVV-4</td>
</tr>
<tr>
<td>3</td>
<td><p>Fieldbus parameter write without device authentication:</p>
<p>from not a legitimate PLC, attempt an acyclic write of safety iPars during the param phase;</p>
<p>observe whether any credential is demanded</p></td>
<td>Proves G-1</td>
<td>MITRE T0843/T0836; NIST SP 800-115 §5.2</td>
<td>SVV-4</td>
</tr>
<tr>
<td>4</td>
<td>Firmware-update access gate (from RQ-005): attempt update outside Update state; confirm rejection; then in Update state confirm acceptance</td>
<td>Validates the authorization gate (EDR 3.10), bounds G-1</td>
<td><p>OWASP ISTG-FW[UPDT]-AUTHZ-001;</p>
<p>NIST SP 800-115 §5.2</p></td>
<td>SVV-2</td>
</tr>
<tr>
<td>5</td>
<td><p>Physical-barrier silent defeat</p>
<p>REUSE TC-RQ003-03 / TC-RQ002-05 by reference</p></td>
<td>Proves G-3</td>
<td><p>OWASP ISTG-PHY;</p>
<p>EDR 3.11</p></td>
<td>SVV-4</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ011-01 - Read-Only Enforcement on the Non-Safety Interface</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-011 🡪 CR 2.1 🡪 Asset B</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Confirm the design intent that safety-relevant parameters cannot be written via the non-safety information interface (read-only), so that interface is not an authorization bypass. (Positive control verification.)</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Enumerate writable-looking endpoints on the information interface.</p></li>
<li><p>Attempt writes to safety-relevant nodes.</p></li>
<li><p>Confirm each is rejected / read-only.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if all safety-parameter write attempts via the information interface are refused.</p>
<p>FAIL if any safety parameter is writable via that interface.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ011-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1.</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, ZAP (CM-004, optional for automated endpoint enumeration).</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p># Attempt write access to all safety-relevant nodes listed in</p>
<p># 209_SRIO_CompSpec_Module_Com §5.3.1 (only /devicetag/applicationtag is</p>
<p># documented as writable; all others should be read-only):</p>
<p>curl -s -X POST http://$SRIO/safecom/f_address/setdata -d '{"value":123}' -w "%{http_code}\n"</p>
<p>curl -s -X POST http://$SRIO/io/do/port7/pin4/digital_output/setdata -d '{"value":true}' -w "%{http_code}\n"</p>
<p>curl -s -X POST http://$SRIO/devicetag/applicationtag/setdata -d '"factoryXYZ"' -w "%{http_code}\n"</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected PASS - all safety-relevant nodes return “read-only” / an error code; only non-critical fields (e.g. applicationtag) are writable.</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ011-02 - Unauthenticated Configuration-Protocol Factory Reset</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-011 🡪 CR 1.2 / CR 2.1 🡪 Asset G, Asset F, Asset B</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Spoofing + Elevation of Privilege</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td>Determine whether a peer node can issue a fieldbus device-configuration set/reset (including reset-to-factory of communication parameters) without any credential and without touching the physical barrier, demonstrating that a connection-relevant setting can be modified by an unauthorized third party.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Baseline the device's communication identity and operating state.</p></li>
<li><p>From a peer node, issue a configuration identify, then a set (change communication identity) and a reset-to-factory.</p></li>
<li><p>Observe whether the actions succeed without authentication.</p></li>
<li><p>Observe the safety impact (loss of the safety connection 🡪 passivation).</p></li>
<li><p>Attempt higher reset modes if supported.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS against the requirement if the set/reset requires authentication or is refused from an unauthorized node.</p>
<p>Expected FAIL: the reset succeeds unauthenticated.</p>
<p>Bound: the impact is on communication parameters (🡪 passivation), not silent safety-parameter modification.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ011-02</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1</td>
</tr>
<tr>
<td>Tools</td>
<td>Scapy or pnio_dcp (pip install pnio_dcp), Wireshark</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>pip install pnio_dcp</p>
<p># 1. Baseline: read the current device name/IP via DCP-Identify</p>
<p>python3 -c "import pnio_dcp; c = pnio_dcp.DCP('eth1'); print(c.identify_all())"</p>
<p># 2. DCP-Set (name change) WITHOUT any credentials:</p>
<p>python3 -c "import pnio_dcp; c = pnio_dcp.DCP('eth1'); c.set_name_of_station('AA:BB:CC:DD:EE:FF', 'test-hijack')"</p>
<p># 3. DCP-Reset-to-Factory (Mode 2, mandatory):</p>
<p>python3 -c "import pnio_dcp; c = pnio_dcp.DCP('eth1'); c.reset_to_factory('AA:BB:CC:DD:EE:FF')"</p>
<p># 4. Check the TIA watch table for connection loss / passivation.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected FAIL (against the requirement) - set/reset succeeds without credentials; the impact is limited to communication parameters --&gt; passivation (no silent safety-parameter modification).</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ011-03 - Fieldbus Parameter Write Without Device-Side Authorization</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-011 🡪 CR 1.1 / CR 1.2 / CR 2.1 🡪 Asset B, Asset F</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering + Spoofing + Elevation of Privilege</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that the device enforces no credential of its own on the fieldbus parameter-write path: an unauthorized node presenting a syntactically valid parameter record (correct destination address + valid parameter integrity values) during the configuration phase can write safety parameters, confirming authorization is entirely delegated to the environment, not device-enforced.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Observe the legitimate configuration sequence.</p></li>
<li><p>From an unauthorized node (impersonating the controller or injecting during the configuration phase), present a modified parameter record with recomputed integrity values.</p></li>
<li><p>Determine whether the device demands any authentication before accepting the write.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS against the requirement if the device requires authentication/authorization before accepting a parameter write.</p>
<p>Expected FAIL: the only checks are addressing + integrity values (no credential) 🡪 confirms authorization is delegated. The finding here is the absence of an authorization credential, distinct from the integrity-value forgeability of TC-RQ005-02.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ011-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1</td>
</tr>
<tr>
<td>Tools</td>
<td>Scapy</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Bring the SRIO into Parametrization (disconnect the real PLC / let the</p>
<p># device go through Init again).</p>
<p># 2. From Kali, send an acyclic write with the correct destination address</p>
<p># and a self-computed, valid iParCRC (no credential attached):</p>
<p>cat &gt; cm_rq011-03_write.py &lt;&lt; 'PYEOF'</p>
<p>from scapy.all import Ether, Raw, sendp</p>
<p>iface = "eth1"</p>
<p>target_mac = "AA:BB:CC:DD:EE:FF"</p>
<p>forged_param_write = bytes.fromhex("REPLACE_WITH_ACYCLIC_WRITE_PLUS_VALID_CRC_HEX")</p>
<p>sendp(Ether(dst=target_mac, type=0x8892)/Raw(load=forged_param_write),</p>
<p>iface=iface, count=1)</p>
<p>PYEOF</p>
<p>sudo python3 cm_rq011-03_write.py</p>
<p># 3. Observe the reaction (acceptance/rejection, error message) in the TIA</p>
<p># watch table / diagnostics buffer.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected FAIL (against the requirement) - the SRIO only checks addressing + CRC consistency, no sender authentication; a syntactically correct telegram is accepted regardless of the sender.</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ011-04 - Firmware-Update Mode Gate</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-011 🡪 EDR 3.10 / CR 2.1 🡪 Asset G, Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Elevation of Privilege</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-2</td>
</tr>
<tr>
<td>Objective</td>
<td>Validate the update authorization gate: an update attempt outside the update state is rejected, while an attempt in the update state is accepted, bounding the delegated-authorization gap by confirming the mode gate operates.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Attempt a firmware update while the device is not in the update state.</p></li>
<li><p>Confirm rejection.</p></li>
<li><p>Place the device in the update state and attempt again.</p></li>
<li><p>Confirm acceptance of the (validated) update.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS if the update is rejected outside the update state and accepted only in it.</p>
<p>FAIL if an update can be initiated outside the update state.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ011-04</td>
</tr>
<tr>
<td>HW/Network</td>
<td>TIA laptop, Kali (curl against /firmware/install)</td>
</tr>
<tr>
<td>Tools</td>
<td>curl.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p># 1. In Operate state (NOT Update):</p>
<p>curl -s -X POST http://$SRIO/firmware/install -w "%{http_code}\n" | tee cm_rq011-04_outside_update.txt</p>
<p># expected: rejected (SRIO-11534)</p>
<p># 2. Rotary switch to 999 + power cycle (Update state).</p>
<p># 3. Repeat the same call:</p>
<p>curl -s -X POST http://$SRIO/firmware/install -w "%{http_code}\n" | tee cm_rq011-04_inside_update.txt</p>
<p># without an actual container upload, a different (but equally meaningful)</p>
<p># error is expected (no container present, instead of ‘wrong state’);</p>
<p># to distinguish these clearly, optionally combine with a harmless/empty</p>
<p># container upload as in TC-RQ005-03 steps 2-3.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected PASS - the update request is rejected outside the update state and accepted only inside it (mode gate works).</td>
</tr>
</tbody>
</table>

**TC-RQ011-05 - Physical-Barrier Silent Defeat ⇄ TC-RQ003-03 / TC-RQ002-05**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-011 🡪 EDR 3.11 🡪 Asset G, Asset B</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td>By reference to TC-RQ003-03 / TC-RQ002-5, confirm that the physical address/mode interface can be altered without visible seal damage and that the change applies after restart, the authorization barrier's silent-defeat question.</td>
</tr>
<tr>
<td>Steps</td>
<td>Execute per TC-RQ003-3 / TC-RQ002-5; record against RQ-011 traceability</td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>As referenced.</p>
<p>Expected: the barrier can be silently defeated 🡪 confirms the physical-authorization gap.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

| Field | Content |
|----|----|
| Ref. Test Case | TC-RQ011-05 |
| HW/Network | identical to TC-RQ002-05/TC-RQ003-03 |
| Tools | See TC-RQ002-05. |
| Procedure | Execute per TC-RQ002-05 / TC-RQ003-03; record the result under RQ-011 traceability, do not re-derive. |
| Result | As TC-RQ002-05 - the seal provides only passive protection, manipulation is possible without visible damage, and the effect only applies after a cold start. |

**REQUIREMENT 12**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-012

- MVO Requirement Text: The system shall enable a tracing log of data generated in relation to an intervention for five years after the machinery or related product has been placed on the market or put into service.

- **IEC 62443-4-2 CR: Mapping:** CR 2.8, CR 2.9, CR 2.10, CR 3.9, CR 6.1

- **Target Assets:** I (tracing log), F (Domain Separation)

- **STRIDE:** (Tampering), Repudiation

- **Security Function (Mitigation):**

  - Error Log ≥100 entries (SRIO-10703).

  - Circular buffer: Oldest overwritten when full (SRIO-10663).

  - Cleared on cold start (SRIO-6521): stated as the deficiency.

- **Identified Gap:**

  - G-1: Cold start clears the log (SRIO-6521). Crucially, the device’s own MANDATORY ≤1-year reboot interval (SRIO-1812), required to test watchdog/safety functions untestable at runtime, forces an annual cold start, so the log is guaranteed to be wiped at least once per year by the device’s own safety-maintenance requirement. The 5-year window is therefore structurally impossible, independent of any attack. (The firmware-install reboot is an additional clearing event 🡪 RQ-008 G-3.)

  - G-2: A fixed ≥100-entry circular buffer (SRIO-10663) with no timestamp (no RTC; SRIO-15218/15398) means that over five years even a modest event rate overflows the buffer, and the surviving 100 entries cannot be bounded to a 5-year window because they are undatable.

  - G-3 (incomplete retained scope): Even ignoring deletion/capacity, the retained data is incomplete: software/error events only, no physical-intervention events (RQ-003), only partial config/software markers (RQ-008/009). Cross-reference; the collection-completeness limitation is owned by RQ-003/008/009.

**Step 2: Methodological Test Planning**

<table>
<colgroup>
<col style="width: 4%" />
<col style="width: 42%" />
<col style="width: 20%" />
<col style="width: 22%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td><p>Capacity/overflow: generate &gt;100 loggable events;</p>
<p>confirm oldest entries overwritten (fixed buffer)</p></td>
<td>Proves G-2</td>
<td>NIST SP 800-115 §3.2 (log review); OWASP ISTG-DES</td>
<td>SVV-2</td>
</tr>
<tr>
<td>2</td>
<td><p>Cold-start deletion:</p>
<p>populate the log, cold-start, confirm cleared;</p>
<p>optionally check EC3/EC4 recovery as exploratory</p></td>
<td>Proves G-1</td>
<td>NIST SP 800-115 §3.2 / §7</td>
<td>SVV-2</td>
</tr>
<tr>
<td>3</td>
<td>Mandated-reboot retention check: simulate the annual reboot interval (SRIO-1812) and confirm the log does not survive the device's own required maintenance reboot</td>
<td>Proves G-1 is structural</td>
<td>Requirements-based + documentation review (SRIO-1812)</td>
<td>SVV-1</td>
</tr>
<tr>
<td>4</td>
<td>Time-attribution: confirm no absolute timestamp on any retained entry, so a 5-year window cannot be bounded (reuse TC-RQ003-04)</td>
<td>Proves G-2 compound</td>
<td>NIST SP 800-115 §3.2</td>
<td>SVV-3</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ012-01 - Circular-Buffer Overflow / Capacity Conflict</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-012 🡪 CR 2.9 / CR 2.10 🡪 Asset I</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-2</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that the tracing log is a fixed-capacity circular buffer that overwrites oldest entries once full, so intervention data is not retained for any duration bounded by event volume, conflicting with the five-year mandate.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Read and record the current log.</p></li>
<li><p>Generate a controlled series exceeding the documented capacity, each event individually identifiable.</p></li>
<li><p>Read the log after each block.</p></li>
<li><p>Confirm the earliest events are overwritten and the buffer never exceeds its fixed size.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS against the requirement if the log retains all events for the retention window.</p>
<p>Expected FAIL: the buffer caps at its fixed size and overwrites oldest-first.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ012-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Kali (curl script), SRIO in operation</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, Bash script.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq012-01_00_baseline.json</p>
<p># Generate at least 105 distinguishable events, e.g. repeatedly and</p>
<p># distinctly disconnecting/reconnecting a DI channel (with a short pause</p>
<p># between events so they remain distinguishable):</p>
<p>for i in $(seq 1 105); do</p>
<p>echo "Event $i: short-circuit/disconnect DI channel now, then press enter"</p>
<p>read</p>
<p>done</p>
<p># After every 10th event, re-read and compare the log:</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq012-01_progress.json</p>
<p>diff cm_rq012-01_00_baseline.json cm_rq012-01_progress.json</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: once the documented capacity is reached (≥100 entries, SRIO-10703), the oldest entries are overwritten</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ012-02 - Cold-Start Deletion</span> ⇄ TC-RQ003-04**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-012 🡪 CR 3.9 / CR 2.9 🡪 Asset I</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation (+Tampering)</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-2</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that a cold start clears the tracing log (intervention data does not persist across a power cycle).</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Populate the log with identifiable entries.</p></li>
<li><p>Apply a cold start (power cycle); read the log.</p></li>
<li><p>Optionally exercise any documented non-cold recovery path and record whether entries survive (exploratory).</p></li>
<li><p>Compare pre/post states.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS against the requirement if entries persist across the reset.</p>
<p>Expected FAIL (cold start): the log is cleared after cold start. Any non-cold-recovery result is recorded factually.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

| Field | Content |
|----|----|
| Ref. Test Case | TC-RQ012-02 |
| HW/Network | See TC-RQ003-04. |
| Tools | See TC-RQ003-04. |
| Procedure | Take the result from TC-RQ003-04 (log is cleared by a cold start) and record it under RQ-012; optionally use the near-full circular buffer produced in TC-RQ012-01 as the starting point before the cold start, to show that even a full buffer is completely cleared. |
| Result | As TC-RQ003-04 - log completely cleared after a cold start (confirms G-1). |

**<span class="mark">TC-RQ012-03 - Mandated-Reboot Retention Impossibility</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-012 🡪 CR 2.9 🡪 Asset I</td>
</tr>
<tr>
<td>Target Threat</td>
<td>N/A, lifecycle/documentation analysis</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Establish that the device's own mandatory maximum reboot interval (required to test safety functions untestable at runtime) forces at least one cold start within the retention period, so the five-year on-device retention is structurally impossible, independent of any attack.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Identify the mandated maximum reboot interval from documentation.</p></li>
<li><p>Show that each mandated reboot is a cold start that clears the log (per TC-RQ012-02).</p></li>
<li><p>Conclude that the retention window cannot be sustained on-device.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>Structural finding.</p>
<p>Expected: the mandated reboot guarantees periodic log erasure within the retention period --&gt; five-year on-device retention structurally impossible.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ012-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td>analytical</td>
</tr>
<tr>
<td>Tools</td>
<td>None</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Reference SRIO-1812 (max. 1-year reboot interval, required to test</p>
<p># watchdog/safety functions that cannot be tested at runtime).</p>
<p># 2. Link this to the empirical finding from TC-RQ012-02 (cold start clears</p>
<p># the log).</p>
<p># 3. Draw the conclusion.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: structural impossibility of 5-year on-device retention, since a cold start is guaranteed to clear the log at least once per year due to the device's own mandated maintenance reboot.</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ012-04 - Time-Attribution of Retained Entries ⇄ TC-RQ003-04</span>**

**Level 1 - Abstract Test Scenario**

| Field | Content |
|----|----|
| Traceability | RQ-012 🡪 CR 2.11 🡪 Asset I |
| Target Threat | Repudiation |
| SVV Category | SVV-3 |
| Objective | By reference to TC-RQ003-04, confirm that no retained entry carries an absolute timestamp, so even surviving entries cannot be bounded to a five-year window. |
| Steps | Execute per TC-RQ003-04; record against RQ-012. |
| Pass/Fail | Expected: entries carry only a relative uptime reference, no absolute timestamp 🡪 retained fragment is undatable (compounds the capacity gap). |

**Level 2 - Concrete Execution**

| Field | Content |
|----|----|
| Ref. Test Case | TC-RQ012-04 |
| HW/Network | See TC-RQ003-04 |
| Tools | See TC-RQ003-04. |
| Procedure | Take the result from TC-RQ003-04 and record it under RQ-012 traceability. |
| Result | As TC-RQ003-04 - only a relative uptime reference, no absolute timestamp. |

**REQUIREMENT 13**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-013

- **MVO Requirement Text:** The system shall enable a tracing log of the versions of safety software uploaded after the machinery or related product has been placed on the market or put into service, for five years after each upload.

- **IEC 62443-4-2 CR: Mapping :** CR 2.8, CR 2.9, CR 2.10, CR 2.11, CR 3.9, CR 6.1

- **Target Assets:** I (Audit Data); D (Safety Sofware)

- **STRIDE:** (Tampering,) Repudiation

- **Security Function (Mitigation):**

  - /deviceinfo/swrevision, /firmware/version: Current version exposed.

  - I&M0 SOFTWARE_REVISION / I&M5 annotation (SRIO-3002/3023).

  - Release Notes per release (SRIO-16242): external, not per-serial.

  - SysCom UPDATE_COMPLETED event (SRIO-10785).

- **Identified Gap:**

  - G-1: The device stores only the CURRENT version; there is no append-only, per-device, per-upload version history. It witnesses every upload (UPDATE_COMPLETED) and can hold remanent state, so this is a design omission.

  - G-2: 5 years after each upload’ requires a per-upload absolute timestamp. With no RTC and uptime reset on cold start (the install forces a cold start), the device cannot timestamp an upload at all --\> even a hypothetical history would be undatable and the per-upload retention clock cannot be started. This is the finding no external record can cure for a specific physical unit.

  - G-3: Not device-resident, not per-serial, not tamper-evident, no guaranteed 5-year per-upload retention, no per-upload timestamp.

**Step 2: Methodological Test Planning**

<table>
<colgroup>
<col style="width: 4%" />
<col style="width: 42%" />
<col style="width: 20%" />
<col style="width: 22%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>Confirm only the current version is exposed (no historical/previous-version fields) via IoT-Core + I&amp;M</td>
<td>Proves G-1</td>
<td><p>Requirements-based verification;</p>
<p>NIST SP 800-115 §3.2</p></td>
<td>SVV-1</td>
</tr>
<tr>
<td>2</td>
<td>Sequential-upload history test: two successive firmware uploads (v_A 🡪 v_B); after each, query for any record of the previous version</td>
<td>Proves G-1</td>
<td><p>NIST SP 800-115 §3.2 / §7;</p>
<p>OWASP ISTG-FW[UPDT]</p></td>
<td>SVV-2</td>
</tr>
<tr>
<td>3</td>
<td>Per-upload timestamp test: after an upload, check whether any absolute date/time is attached to the version change (reuse TC-RQ003-04 method)</td>
<td>Proves G-2</td>
<td>NIST SP 800-115 §3.2</td>
<td>SVV-3</td>
</tr>
<tr>
<td>4</td>
<td>External-record verification: assess whether Release Notes provide per-serial, timestamped, tamper-evident, 5-year records for this unit</td>
<td>Proves G-3</td>
<td><p>NIST SP 800-115 §3.1;</p>
<p>OWASP FSTM Stage 1</p></td>
<td>SVV-1</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ013-01 - Current-Version-Only Confirmation</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-013 🡪 CR 2.9 🡪 Asset I, Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Confirm that only the current version is exposed and that no historical or previous-version fields exist via the identification interface and identity records.</td>
</tr>
<tr>
<td>Steps</td>
<td><p>Read all version fields via the identification interface.</p>
<p>Read the version-bearing identity records.</p>
<p>Search for any previous-version or upload-history field.</p></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS against the requirement if a query able per-upload history is exposed.</p>
<p>Expected FAIL: only the current version is reported; no history field exists.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ013-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>Kali (curl), TIA (I&amp;M).</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>curl -s http://$SRIO/deviceinfo/swrevision/getdata</p>
<p>curl -s http://$SRIO/firmware/version/getdata</p>
<p># In TIA: Online &amp; Diagnostics &gt; Identification &amp; Maintenance &gt; I&amp;M0, I&amp;M5</p>
<p># Explicitly search all responses for any ‘version history’ / ‘previous</p>
<p># version’ field (none documented).</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected FAIL (against the requirement) - only the current version is retrievable, no history field exists.</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ013-02 - Sequential-Upload Version-History Test</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-013 🡪 CR 2.8 / CR 2.9 / CR 3.9 🡪 Asset I, Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-2</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that the device retains no historical, per-upload record of previously uploaded safety-software versions: after uploading a new version over the current one, no device-resident field reports that the previous version was ever installed. Self-erasing install mechanics are cross-referenced to RQ-008; this test targets version-history existence</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Record the current version and all version fields.</p></li>
<li><p>Upload a new version; after install, read all version fields.</p></li>
<li><p>Search for any device-resident record of the previous version.</p></li>
<li><p>Upload a further version; repeat the search for both prior versions.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS against the requirement if the device retains a query able per-upload history including previous versions.</p>
<p>Expected FAIL: only the current version is reported; no record of prior uploads persists.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ013-02</td>
</tr>
<tr>
<td>HW/Network</td>
<td>TIA laptop, Kali (curl, version polling)</td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p># 1. Record the current version and all version fields:</p>
<p>curl -s http://$SRIO/deviceinfo/swrevision/getdata | tee cm_rq013-02_v1.json</p>
<p># 2. Official downgrade to an older version (Update state, rotary 999 +</p>
<p># power cycle, upload the OLDER official container as in TC-RQ005-03</p>
<p># steps 1+3):</p>
<p>curl -s http://$SRIO/deviceinfo/swrevision/getdata | tee cm_rq013-02_v2_after_downgrade.json</p>
<p># check for any 'previous version' field (none expected)</p>
<p># 3. Upgrade back to the current version (repeat step 2 with the current</p>
<p># container):</p>
<p>curl -s http://$SRIO/deviceinfo/swrevision/getdata | tee cm_rq013-02_v3_after_upgrade.json</p>
<p># check again for any historical version field</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected FAIL - at no point is the respective previous version additionally stored/displayed alongside the current one.</td>
</tr>
</tbody>
</table>

**TC-RQ013-03 - Per-Upload Timestamp Absence**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-013 🡪 CR 2.11 / CR 3.9 🡪 Asset I</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that a firmware upload carries no absolute per-upload timestamp: with no real-time clock and an install-forced cold start that resets the uptime reference, no date/time is attached to the version change, so the "five years after each upload" retention clock cannot be established on-device.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Read the uptime reference and current version before an upload.</p></li>
<li><p>Perform an upload (forces install restart).</p></li>
<li><p>After restart, read the uptime reference and version.</p></li>
<li><p>Confirm the time base reset and that no absolute date/time is associated with the upload event.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS against the requirement if a per-upload absolute timestamp is recorded and retained.</p>
<p>Expected FAIL: uptime resets, no real-time clock, no absolute time on the version change --&gt; per-upload retention clock cannot be started.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ013-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td><p>See TC-RQ003-04</p>
<p>Kali, plus TIA laptop for triggering the update</p></td>
</tr>
<tr>
<td>Tools</td>
<td>curl, TIA.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p># Reuse the TC-RQ003-04 procedure, replacing 'Event 1'/'Event 2' with an</p>
<p># official firmware upload/install (as in TC-RQ013-02):</p>
<p>curl -s http://$SRIO/systemtime/systick/getdata | tee cm_rq013-03_systick_00_baseline.txt</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq013-03_log_00_baseline.json</p>
<p># perform the official firmware upload/install (rotary 999, upload,</p>
<p># /firmware/install)</p>
<p>curl -s http://$SRIO/systemtime/systick/getdata | tee cm_rq013-03_systick_01_after_update.txt</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist | tee cm_rq013-03_log_01_after_update.json</p>
<p>diff cm_rq013-03_log_00_baseline.json cm_rq013-03_log_01_after_update.json</p></td>
</tr>
<tr>
<td>Result</td>
<td>As TC-RQ003-04/TC-RQ008-04 - systick resets, no absolute timestamp exists for the upload event.</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ013-04 - External-Record (Release-Notes) Verification</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-013 🡪 CR 2.9 (compensating) 🡪 Asset I, Asset D</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Repudiation</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-1</td>
</tr>
<tr>
<td>Objective</td>
<td>Assess whether the external release documentation provides per-unit (per-serial), timestamped, tamper-evident, five-year, per-upload records for the specific physical unit.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Review the external release documentation available for the unit.</p></li>
<li><p>Assess it against the criteria: device-resident? per-serial? tamper-evident? guaranteed five-year per-upload retention? per-upload timestamp?</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td>Expected: the external records are not device-resident, not per-serial, not tamper-evident, and provide no guaranteed per-upload timestamped five-year retention 🡪 the external record cannot cure the on-device gap for a specific unit.</td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ013-04</td>
</tr>
<tr>
<td>HW/Network</td>
<td>document review</td>
</tr>
<tr>
<td>Tools</td>
<td>Web browser.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p># 1. Open the release-notes page for AL400S/AL401S.</p>
<p># 2. Check: does it contain serial-number/per-unit information? A timestamp</p>
<p># per upload? Tamper protection (signature/hash of the notes)?</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: the release notes are product-wide (not per-unit), without cryptographic tamper protection, and without a guaranteed 5-year retention obligation per individual upload - cannot compensate for the on-device gap (confirms G-3).</td>
</tr>
</tbody>
</table>

**REQUIREMENT 14**

**Step 1: Critical Review & Theoretical Validation**

- **MVO-ID:** RQ-014

- MVO Requirement Text: The system shall restrict access to the tracing log data exclusively to demonstrating conformity further to a reasoned request from a competent national authority.

- **IEC 62443-4-2 CR Mapping :** CR 1.1, CR 1.2, CR 2.1, CR 3.9, CR 4.1, CR 6.1 (inversion)

- **Target Assets:** I (tracing log to be access-restricted); H (IoT Access Channel)

- **STRIDE:** (Tampering,) Information Disclosure (primary)

- **Security Function (Mitigation):**

  - Error log readable via IoT-Core: No auth gate (SRIO-10662), stated as the deficiency.

  - IoT-Core incoming HTTP, no HTTPS (SRIO-7903/7907).

  - 2 concurrent connections, incoming-only (SRIO-7909/7908).

  - No documented delete/erase command; Stated for completeness.

- **Identified Gap:**

  - G-1: There is no gate because the device has no user-identity model at all (password removed, SRIO-8299). RQ-014’s ‘restrict access exclusively to \[X\]’ is therefore architecturally impossible: you cannot restrict access to a party on a device that cannot identify any party. CR 2.1 fails because CR 1.1/1.2 are absent.

  - G-2: The log is readable by anyone with segment access, not ‘exclusively’ for a competent-authority request. The only barrier is the environmental SRIO-9402 assumption, not the fine-grained, purpose-limited control RQ-014 demands.

  - G-3: No documented erase command 🡪 no data-lifecycle control

**Step 2: Methodological Test Planning**

<table>
<colgroup>
<col style="width: 4%" />
<col style="width: 42%" />
<col style="width: 20%" />
<col style="width: 22%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr>
<th></th>
<th>Scenario</th>
<th>Proves</th>
<th>Justification</th>
<th>SVV</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>Unauthenticated read: from an arbitrary segment node, read the full error log via IoT-Core with no credentials</td>
<td>Proves G-1/G-2 (no auth, no purpose-limit)</td>
<td><p>NIST SP 800-115 §4.2;</p>
<p>OWASP ISTG-DES-AUTHZ-001</p></td>
<td>SVV-4</td>
</tr>
<tr>
<td>2</td>
<td>Cleartext capture: passively capture the log; confirm plaintext + no TLS</td>
<td>Documents the confidentiality-in-transit observation (DiD; MR-restriction is the primary finding)</td>
<td><p>NIST SP 800-115 §3.5;</p>
<p>ifm CM-005 (SSLscan, --show-certificate)</p></td>
<td>SVV-3</td>
</tr>
<tr>
<td>3</td>
<td>Access-control probe: enumerate the IoT-Core for any auth mechanism, role, or purpose-gate on the log endpoint</td>
<td>Proves G-1 (no gate by design)</td>
<td>OWASP ISTG-DES-AUTHZ-002; ifm CM-004 (ZAP)</td>
<td>SVV-3</td>
</tr>
<tr>
<td>4</td>
<td>Deletion-control probe: attempt any delete/erase of log data; confirm no controlled-deletion command exists (only cold-start wipe)</td>
<td>Proves G-3</td>
<td><p>NIST SP 800-115 §4.2;</p>
<p>OWASP ISTG-DES</p></td>
<td>SVV-3</td>
</tr>
</tbody>
</table>

**Step 3 - Two-Level Test Catalog**

**<span class="mark">TC-RQ014-01 - Unauthenticated Tracing-Log Read</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-014 🡪 CR 1.1/1.2 / CR 2.1 / CR 3.9 🡪 Asset I, Asset H</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Information Disclosure (missing authorization boundary)</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-4</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that the tracing log is fully readable by an arbitrary, unauthenticated node on the segment, with no identity, authentication, authorization, or purpose-limitation, directly violating the requirement that access be restricted exclusively to a competent-authority request.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>From a node with only network access (no credentials, no configuration privilege), request the tracing-log content.</p></li>
<li><p>Confirm the full log content is returned.</p></li>
<li><p>Confirm no authentication challenge, session, or authorization check is presented at any point.</p></li>
<li><p>Confirm no purpose/requestor context is required.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS against the requirement if the log read requires authentication and a purpose-limited authorization.</p>
<p>Expected FAIL: the log is returned to an unauthenticated arbitrary node with no gate 🡪 confirms the missing access-control gap.</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ014-01</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1</td>
</tr>
<tr>
<td>Tools</td>
<td>curl</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist</p>
<p># executed with NO credentials/headers whatsoever; check the response for</p>
<p># the full log content.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected FAIL (against the requirement) - the complete log content is returned without authentication.</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ014-02 - Cleartext Confidentiality of the Tracing Log</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-014 🡪 CR 4.1 / CR 4.3 (supporting observation) 🡪 Asset I, Asset H</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Information Disclosure</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that tracing-log content is transmitted without transport encryption and can be captured passively on the segment, and that no encrypted transport option exists. Supporting observation; the primary RQ-014 finding is the missing access control, not the absence of encryption.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Trigger a legitimate log read.</p></li>
<li><p>Passively capture the exchange.</p></li>
<li><p>Extract the cleartext log content.</p></li>
<li><p>Confirm no encrypted transport endpoint is available.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td><p>PASS against the requirement if log transport is encrypted.</p>
<p>Expected: cleartext recoverable and no encrypted transport 🡪 supporting confidentiality-in-transit observation. (Method aligned to the framework's TLS-analysis step, including certificate-chain capture, for consistency.)</p></td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ014-02</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1</td>
</tr>
<tr>
<td>Tools</td>
<td>tcpdump/Wireshark, sslscan (CM-005).</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>sslscan --show-certificate $SRIO:80 | tee cm_rq014-02_sslscan.txt</p>
<p>sudo tcpdump -i eth1 host $SRIO and port 80 -w cm_rq014-02_log.pcap &amp;</p>
<p>curl -s http://$SRIO/devicestatus/errorlog/loglist</p>
<p>kill %1</p>
<p># Open cm_rq014-02_log.pcap in Wireshark &gt; Follow &gt; HTTP Stream to show</p>
<p># the plaintext log content.</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: log content is readable in plaintext, no transport encryption (defense-in-depth observation).</td>
</tr>
</tbody>
</table>

**<span class="mark">TCm-RQ014-03 - Access-Control Mechanism Probe</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-014 🡪 CR 1.1 / CR 1.2 / CR 2.1 🡪 Asset I, Asset H</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Information Disclosure (missing authorization gate)</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Enumerate the information interface for any authentication mechanism, role model, or purpose-gate governing the tracing-log endpoint, establishing that no gate exists by design.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Enumerate the tracing-log endpoint and adjacent endpoints for any authentication or authorization control.</p></li>
<li><p>Attempt to identify any role/identity model.</p></li>
<li><p>Confirm whether any purpose-limitation mechanism is present.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td>Expected: no authentication mechanism, role model, or purpose-gate is present 🡪 confirms the requirement cannot be met because the device has no identity model to restrict access to any party.</td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ014-03</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1</td>
</tr>
<tr>
<td>Tools</td>
<td>ZAP (CM-004), Nikto (CM-007), curl.</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p>nikto -h http://$SRIO -output cm_rq014-03_nikto.html -Format html</p>
<p># Search the output for any login/auth endpoints.</p>
<p>zaproxy -daemon -host 127.0.0.1 -port 8090 -config api.disablekey=true &amp;</p>
<p>curl "http://127.0.0.1:8090/JSON/spider/action/scan/?url=http://$SRIO/"</p>
<p># check ZAP's discovered URLs / responses for any 401/403 status codes</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: no authentication/role mechanism found on any endpoint - confirms G-1 (no identity model exists).</td>
</tr>
</tbody>
</table>

**<span class="mark">TC-RQ014-04 - Deletion-Control Probe</span>**

**Level 1 - Abstract Test Scenario**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Traceability</td>
<td>RQ-014 🡪 CR 3.9 🡪 Asset I</td>
</tr>
<tr>
<td>Target Threat</td>
<td>Tampering</td>
</tr>
<tr>
<td>SVV Category</td>
<td>SVV-3</td>
</tr>
<tr>
<td>Objective</td>
<td>Demonstrate that there is no controlled-deletion mechanism for the tracing log (only the uncontrolled cold-start wipe), so no data-lifecycle control exists to govern who may erase the record and when.</td>
</tr>
<tr>
<td>Steps</td>
<td><ol type="1">
<li><p>Enumerate the interface for any delete/erase command applying to the tracing log.</p></li>
<li><p>Attempt any discoverable deletion operation.</p></li>
<li><p>Confirm whether controlled deletion is possible and, if so, whether it is access-controlled.</p></li>
</ol></td>
</tr>
<tr>
<td>Pass/Fail</td>
<td>Expected: no controlled-deletion command exists (only the cold-start wipe) 🡪 confirms the absence of data-lifecycle control.</td>
</tr>
</tbody>
</table>

**Level 2 - Concrete Execution**

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 83%" />
</colgroup>
<thead>
<tr>
<th>Field</th>
<th>Content</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ref. Test Case</td>
<td>TC-RQ014-04</td>
</tr>
<tr>
<td>HW/Network</td>
<td>NV1</td>
</tr>
<tr>
<td>Tools</td>
<td>curl</td>
</tr>
<tr>
<td>Procedure</td>
<td><p>export SRIO=192.168.0.2</p>
<p># List all endpoints documented as service ‘S’ in</p>
<p># 209_SRIO_CompSpec_Module_Com §5.3.1 (/devicecontrol/signal,</p>
<p># /firmware/install, /fit/setfit, ...) - none of these relate to errorlog.</p>
<p># Test explicitly for a delete/erase capability:</p>
<p>curl -s -X DELETE http://$SRIO/devicestatus/errorlog/loglist -w "%{http_code}\n"</p>
<p>curl -s -X POST http://$SRIO/devicestatus/errorlog/loglist -d '{}' -w "%{http_code}\n"</p></td>
</tr>
<tr>
<td>Result</td>
<td>Expected: no delete/erase service exists; the only way to clear the log remains the (uncontrolled) cold-start wipe (confirms G-3).</td>
</tr>
</tbody>
</table>

Possible additions:

RQ002

- Tampering:

> Signal injection at the physical layer (PHY)
>
> Transceiver/buffer overflow at the hardware level

RQ-003:

- Tampering:

> Physical tampering attempt on the log memory

RQ-004

- Tampering:

> Firmware version spoofing (version rollback / manipulation)
>
> Manipulation of I&M data (Identification & Maintenance)

- Separation of Concerns:

> Overlapping configuration injection (boundary test)

RQ-005

- Runtime Integrity

> NVRAM / Flash tampering of the safety configuration

- Domain Separation & Security Functionality Protection

> JTAG / Debug Port Lockdown

RQ-009:

- Log Flooding:

> Configuration Flapping / Audit Exhaustion

- Firmware Modification:

> Verification of the Combined FW/Config Logs

RQ-013:

- Firmware upload flooding / log exhaustion
