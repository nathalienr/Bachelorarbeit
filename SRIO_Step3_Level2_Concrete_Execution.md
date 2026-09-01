# Step 3 — Two-Level Test Catalog
## Level 2: Concrete Test Execution (Hardware-in-the-Loop)

**Environment:** Physical IT/OT testbed per `Testumgebung_Setup_Anleitung.md` (revised).
**Status:** Environment APPROVED (Condition B).

### Fixed reference values (from the setup document)
| Element | Value |
|---|---|
| PLC / F-Host | `172.18.87.1` — Switch Port 1 |
| SRIO DUT | `172.18.87.2` — Switch Port 2 |
| Engineering laptop (TIA Portal, I&M read path) | `172.18.87.10` — Switch Port 3 |
| Kali-Pi active (Setup B) | `172.18.87.20/18` — Switch Port 4 |
| Kali-Pi passive (Setup A) | no test-net IP, `promisc on` — Switch Port 5 (SPAN of Ports 1+2) |
| Kali-Pi inline bridge `br0` (Setup B-Inline) | optional `172.18.87.21/18` — inline between Port 2 and SRIO |
| Spare SRIO (Setup C) | destructive/firmware/physical tests only |
| PROFINET/PROFIsafe EtherType | `0x8892` (Wireshark display filter: `pn_io` / `pn_io.ps`) |
| IoT-Core (HTTP) | `http://172.18.87.2/` (plaintext, max 2 connections) |
| I&M0/I&M4/I&M5 | read **only** via TIA Portal → *Online & Diagnose → Kennungsdaten (I&M)* |

### Conventions
- **Setup A** = passive mirror capture; **Setup B** = active IP-layer; **Setup B-Inline** = transparent L2 bridge (§11); **Setup C** = spare, destructive.
- Evidence files use the framework naming `cm_<tcid>_<desc>.<ext>`; store unchanged in the project evidence folder and reference in the test log.
- Every aggressive test (flood/fuzz/firmware) runs the §12 health monitor with the ≥5 s-unreachable abort criterion.
- `[PLACEHOLDER: Result]` and `[PLACEHOLDER: Evidence file]` are filled at execution time.

---

# RQ-001 — Connection of a device must not create a hazard

## TC-RQ001-01 — Baseline Safety Exchange
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ001-01 (Level 1) |
| **HW/Network** | Setup A (passive). Pi on Port 5 (mirror of Ports 1+2), `promisc on`, no IP. PLC↔SRIO in normal OPERATE; DI button + DO lamp wired; DO looped back to a spare PLC F-DI for independent readback. |
| **Tools** | Wireshark/`tshark`, TIA Portal (PLC watch table), camera. |
| **Commands / Config** | `sudo ip link set eth0 promisc on`<br>`sudo tshark -i eth0 -f "ether proto 0x8892" -Y "pn_io.ps" -w cm_rq001-01_baseline.pcap`<br>In TIA *Online & Diagnose*: create a watch table monitoring the F-DI/F-DO channel value + PROFIsafe qualifier. Toggle the DI button; command the DO from the PLC. |
| **Expected Result & Evidence** | **Expected:** qualifier = *good* for the whole capture; DO follows the control byte; DO-readback F-DI mirrors the commanded state; no passivation. **Evidence:** `cm_rq001-01_baseline.pcap`; TIA watch-table screenshot; photo/video of DO lamp; test-log PASS. `[PLACEHOLDER: Result]` |

## TC-RQ001-02 — Attack-Surface Enumeration on the Non-Safety Path
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ001-02 |
| **HW/Network** | Setup B (active). Pi `172.18.87.20` on Port 4. |
| **Tools** | Nmap (ifm CM-001). |
| **Commands / Config** | `sudo nmap -sS -sV -p- -T3 -oA cm_rq001-02_tcp 172.18.87.2`<br>`sudo nmap -sU --top-ports 200 -oA cm_rq001-02_udp 172.18.87.2` |
| **Expected Result & Evidence** | **Expected:** only design-approved services reachable — TCP/80 (IoT-Core HTTP) and PROFINET/DCP infrastructure; **no** Telnet/FTP/SSH/HTTPS. Any port outside the matrix = FAIL. Plaintext HTTP recorded as defence-in-depth only (FR4 = none). **Evidence:** `cm_rq001-02_tcp.xml/.nmap`, `cm_rq001-02_udp.*`; port-matrix comparison table. `[PLACEHOLDER: Result]` |

## TC-RQ001-03 — Codename / Integrity-Value Mismatch Rejection
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ001-03 |
| **HW/Network** | Setup B (active, parallel injection) with simultaneous Setup A capture on the mirror. PLC↔SRIO in OPERATE. |
| **Tools** | Scapy (`pnio`, `pnio_rtc` contrib), Wireshark, DO-readback via PLC. |
| **Commands / Config** | Capture one legitimate cyclic frame to obtain frame-ID / structure:<br>`sudo tshark -i eth0 -Y "pn_io.ps" -c 5 -w cm_rq001-03_ref.pcap`<br>Craft & send parallel frames from the Pi (Scapy skeleton):<br>`from scapy.all import *`<br>`load_contrib('pnio'); load_contrib('pnio_rtc')`<br>`# (a) mis-addressed: alter PROFIsafe F-address/consumer-ID; (b) bit-flip PD + leave CRC stale`<br>`sendp(frame_bad, iface="eth0", loop=1, inter=0.002)` |
| **Expected Result & Evidence** | **Expected:** parallel injection does **not** hijack the consumer — the consecutive-number collision with the live producer drives passivation, or the frames are ignored; DO de-energised (qualifier *bad*) or unchanged; **no uncommanded actuation** = PASS. **Evidence:** `cm_rq001-03_inject.pcap`, PLC diagnostic-buffer export, DO-lamp video. `[PLACEHOLDER: Result]` |

## TC-RQ001-04 — In-Path Adversary-in-the-Middle Boundary
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ001-04 |
| **HW/Network** | **Setup B-Inline** (§11). Pi bridges `eth0`↔Switch Port 2 and `eth1`(USB3-GbE)↔SRIO Port 1; `br0` transparent. |
| **Tools** | `bridge-utils`, `ebtables`, Python + `NetfilterQueue` + Scapy, Wireshark on `br0`. |
| **Commands / Config** | Build bridge (§11.3): `brctl addbr br0; brctl addif br0 eth0; brctl addif br0 eth1; ip link set br0 up`<br>Verify transparency: `sudo tcpdump -i br0 ether proto 0x8892`<br>Divert for takeover: `sudo ebtables -A FORWARD -i eth0 --nfqueue-num 0`<br>Python NFQUEUE script: suppress the genuine producer's cyclic frame, continue the consecutive-number sequence, inject a valid-CRC frame with modified PD toward the consumer. |
| **Expected Result & Evidence** | **Boundary characterisation — NOT scored as a device FAIL.** Expected: an in-path takeover that suppresses the producer and continues the sequence is accepted → confirms authenticity rests on the black-channel assumption (documented residual risk). A **device FAIL** is recorded only if a *parallel* injection (TC-RQ001-03, no suppression) had succeeded. **Evidence:** `cm_rq001-04_mitm.pcap` (br0), NFQUEUE script + log, DO-readback trace. Restore cabling per §11.5 afterwards. `[PLACEHOLDER: Result]` |

## TC-RQ001-05 — Channel-Disruption Watchdog Response
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ001-05 |
| **HW/Network** | Setup A capture + physical link interruption of SRIO fieldbus (or drop-all on the §11 bridge). Known `F_WD_Time` (default 150 ms). |
| **Tools** | Wireshark (frame timestamps), stopwatch/DO-readback, TIA diagnostics. |
| **Commands / Config** | Start capture: `sudo tshark -i eth0 -Y "pn_io.ps" -w cm_rq001-05_wd.pcap -t a`<br>Interrupt: unplug SRIO Port-1 patch cable **or** on bridge `sudo ebtables -A FORWARD -i eth1 -j DROP`. Hold > `F_WD_Time`. Measure Δt from last valid frame to DO de-energise. Restore link; confirm re-integration requires PLC acknowledgement. |
| **Expected Result & Evidence** | **Expected:** passivation within the specified device response time; DO de-energised, qualifier *bad*; **no auto re-integration** without acknowledgement = PASS. **Evidence:** `cm_rq001-05_wd.pcap` (timestamp delta), DO-lamp video, PLC diagnostic showing passivation + acknowledged reintegration. `[PLACEHOLDER: Result]` |

---

# RQ-002 — Protect hardware transmitting connection/safety data from corruption

## TC-RQ002-01 — Parameter-CRC Rejection (iParCRC / F_ParCRC)
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ002-01 |
| **HW/Network** | Setup A capture + Engineering laptop (TIA). Baseline valid configuration downloaded. |
| **Tools** | TIA Portal, Wireshark. |
| **Commands / Config** | In TIA, set a valid config and note the correct `F_iPar_CRC`. Then manually enter a **wrong** `F_iPar_CRC` (or alter one iParameter without regenerating the CRC), compile, download. Capture the connection establishment: `sudo tshark -i eth0 -Y "pn_io" -w cm_rq002-01_crc.pcap`. |
| **Expected Result & Evidence** | **Expected:** device raises a configuration/F-parameter error (EC3-class), stays in Parametrization, qualifier *bad*, no OPERATE handshake = PASS. **Evidence:** TIA diagnostic-buffer screenshot (F-parameter/iPar-CRC error), `cm_rq002-01_crc.pcap`. `[PLACEHOLDER: Result]` |

## TC-RQ002-02 — Stale Integrity-Value Fault Detection
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ002-02 |
| **HW/Network** | Setup B (active) parallel injection + Setup A capture. OPERATE. |
| **Tools** | Scapy (`pnio_rtc`), Wireshark, DO-readback. |
| **Commands / Config** | Capture a cyclic frame; modify one process-data byte **leaving the PROFIsafe CRC unchanged**; replay:<br>`sendp(frame_stale_crc, iface="eth0", loop=1, inter=0.002)` |
| **Expected Result & Evidence** | **Expected:** CRC mismatch detected → device passivates or ignores the corrupted frame; DO not driven by the tampered data = PASS. **Evidence:** `cm_rq002-02_stale.pcap`, PLC diagnostic, DO video. `[PLACEHOLDER: Result]` |

## TC-RQ002-03 — Valid-Integrity-Value Injection over Modified Data
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ002-03 |
| **HW/Network** | **Setup B-Inline** (single-stream substitution needed for a clean result) + Setup A capture. |
| **Tools** | Scapy + PROFIsafe CRC routine (CRC-Seed24/32 from GSD), NetfilterQueue, Wireshark. |
| **Commands / Config** | Implement the PROFIsafe F-CRC over the modified PD using the public seed; on the bridge, suppress the genuine frame and forward the re-CRC'd frame. |
| **Expected Result & Evidence** | **Gap-characterisation.** Expected: recomputed-CRC telegram is accepted (checksum ≠ authenticity) — residual risk documented. A rejection would indicate an undocumented crypto control (investigate). **Evidence:** `cm_rq002-03_recrc.pcap`, CRC-routine source, DO-readback. `[PLACEHOLDER: Result]` |

## TC-RQ002-04 — Parameter-Integrity Forgeability Assessment
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ002-04 (analytical; **not** an authentication test — demonstrates *absence of forgery resistance*) |
| **HW/Network** | No live DUT interaction required (desk analysis on Engineering laptop / Pi). |
| **Tools** | Documentation (GSD, SRIO-2998), a short script to enumerate the 16-bit space. |
| **Commands / Config** | Record bit-length/algorithm of each value (F_ParCRC = 16-bit; iParCRC = 32-bit, CRC over public layout). Demonstrate the 16-bit space is exhaustively enumerable (`2^16 = 65 536`) and the 32-bit value is deterministically recomputable via the certified CRC-tool algorithm — neither depends on a secret. |
| **Expected Result & Evidence** | **Analytical finding:** both values are forgeable → error-detection, not authentication. **Evidence:** written keyspace argument + enumeration snippet output. `[PLACEHOLDER: Result]` |

## TC-RQ002-05 — Physical Tamper-Resistance of the Address/Mode Interface
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ002-05 |
| **HW/Network** | **Setup C** (spare SRIO). Basis for the "runtime read only at Init" claim: setup doc §8.1 ("Adresse wird nur beim Boot/Init gelesen") + SRIO-8803/10812. |
| **Tools** | Multimeter, camera, TIA (to read back the effective F_Dest_Add). |
| **Commands / Config** | (1) Record baseline rotary value + seal state (photo). (2) In OPERATE, defeat the seal sleeve, change the rotary switch; confirm the **running** address is unchanged (PLC still in safe comms). (3) Cold power-cycle; confirm the **new** address now takes effect (safe connection drops / F-address mismatch). (4) Inspect whether alteration was possible without visible seal damage. |
| **Expected Result & Evidence** | **Gap-characterisation.** Expected: runtime change ignored (temporal protection = partial mitigation); post-restart the altered value applies (stored value corruptible); only passive seal resists, no active detection. **Evidence:** before/after photos, TIA screenshot of changed F-address behaviour, test-log. `[PLACEHOLDER: Result]` |

---

# RQ-003 — Collect evidence of intervention in hardware components

## TC-RQ003-01 — Baseline: What Evidence the Device Actually Collects
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ003-01 |
| **HW/Network** | Setup B (IoT-Core read) + Engineering laptop (I&M read via TIA, §6). |
| **Tools** | `curl`, TIA *Online & Diagnose*. |
| **Commands / Config** | Error log via IoT-Core: `curl -s http://172.18.87.2/devicestatus/errorlog/loglist | tee cm_rq003-01_errorlog.json`<br>Read I&M0 (REVISION_COUNTER) and I&M4 (signature) in TIA. Perform one authorised iParameter change in TIA + download; re-read all three. |
| **Expected Result & Evidence** | **Expected:** log + records readable (accessibility PASS); REVISION_COUNTER increments; I&M4 signature changes. **Documented shortfall:** no record carries actor identity or absolute timestamp. **Evidence:** `cm_rq003-01_errorlog.json`, TIA I&M0/I&M4 screenshots (before/after). `[PLACEHOLDER: Result]` |

## TC-RQ003-02 — Authorised Intervention Evidence Under Normal Use
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ003-02 |
| **HW/Network** | Setup B + TIA. |
| **Tools** | `curl`, TIA. |
| **Commands / Config** | Baseline error log + I&M0. Perform an authorised rotary/F-address or iPar change (§8.1) and reboot. Re-read error log + I&M0/I&M4. Assess whether any retained, time-referenceable record of the intervention exists. |
| **Expected Result & Evidence** | **Expected shortfall:** post-reboot the error-log detail is cleared (cold start) and no absolute timestamp exists; only the counter delta persists (verify empirically — cf. RQ-009). **Evidence:** before/after `cm_rq003-02_errorlog_*.json`, TIA I&M screenshots. `[PLACEHOLDER: Result]` |

## TC-RQ003-03 — Illegitimate Physical Intervention & Anti-Forensic Clearing
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ003-03 |
| **HW/Network** | **Setup C** (spare). |
| **Tools** | Multimeter, camera, `curl`, TIA. |
| **Commands / Config** | Capture baseline log/records/address. Carefully remove the seal sleeve, change the rotary (incl. →999 update mode); note any live status change. Cold-restart. Re-read error log (`curl … /devicestatus/errorlog/loglist`) and check for any tamper/intervention entry and whether the log survived. Assess attribution/timing. |
| **Expected Result & Evidence** | **Gap-characterisation → FAIL vs RQ-003.** Expected: no tamper-specific entry; incidental entries lost on cold start; no actor identity, no absolute timestamp. **Evidence:** photos, `cm_rq003-03_errorlog_before/after.json`, test-log. `[PLACEHOLDER: Result]` |

## TC-RQ003-04 — Time-Attribution Failure of Collected Evidence
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ003-04 (reused by TC-008-04, TC-012-04, TC-013-03) |
| **HW/Network** | Setup B + TIA. |
| **Tools** | `curl`, TIA. |
| **Commands / Config** | Generate a loggable event; read uptime `curl -s http://172.18.87.2/systemtime/systick` and the log entry. Cold-restart. Generate a second event; read uptime again. Compare. |
| **Expected Result & Evidence** | **Expected FAIL:** uptime (systick) resets to ~0 on cold start; no absolute timestamp on any entry → not time-referenceable (CR 2.11 unmet). **Evidence:** two `cm_rq003-04_systick_*.txt`, two log excerpts. `[PLACEHOLDER: Result]` |

## TC-RQ003-05 — Excluded (Development-Only) Interface Produces No Evidence
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ003-05 (reused by TC-008-05). Basis: SRIO-2580/1526 (development-only) + `production_fuse` gating, `/fit/setfit` = WO(P) (SRIO-17130). |
| **HW/Network** | Setup B against a production-configured unit. |
| **Tools** | `curl`, TIA. |
| **Commands / Config** | Attempt the production-gated FIT service on a production unit:<br>`curl -s -X POST http://172.18.87.2/fit/setfit -d '{"type":1}' -w "%{http_code}\n" | tee cm_rq003-05_fit.txt`<br>Then read the error log and check for any entry for the attempt. |
| **Expected Result & Evidence** | **Expected:** FIT rejected on the production unit (exclusion valid); the excluded interface produces **no** log entry (documented gap). **Limitation:** a true silicon fuse is not verifiable without invasive PA-4 analysis — only the functional gate is tested. **Evidence:** `cm_rq003-05_fit.txt`, error-log excerpt. `[PLACEHOLDER: Result]` |

---

# RQ-004 — Identify software AND data critical for EHSR compliance

## TC-RQ004-01 — Identification-Surface Inventory (SW + Data)
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ004-01 |
| **HW/Network** | Setup B (IoT-Core) + TIA (I&M, §6). |
| **Tools** | `curl`, TIA, OWASP FSTM Stage 1 checklist. |
| **Commands / Config** | `for p in deviceinfo/hwversion deviceinfo/hwrevision deviceinfo/swrevision deviceinfo/swinfo/cpubootloaderversion deviceinfo/swinfo/scpuversion deviceinfo/swinfo/scpubootloaderversion firmware/version fieldbussetup/fieldbusfirmware; do echo "== $p =="; curl -s http://172.18.87.2/$p; echo; done | tee cm_rq004-01_inventory.txt`<br>Read I&M0/I&M4/I&M5 in TIA. Compile inventory; diff vs expected EHSR-critical SW+data set. |
| **Expected Result & Evidence** | **Expected (partial-conformance baseline):** top-level SW identification + I&M4 data signature present; **shortfall:** no third-party SBOM and no explicit safety-critical-data classification. **Evidence:** `cm_rq004-01_inventory.txt`, TIA I&M screenshots, inventory diff table. `[PLACEHOLDER: Result]` |

## TC-RQ004-02 — SBOM Completeness & Third-Party Vulnerability Correlation
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ004-02. **Traceability corrected:** RQ-004 → **IEC 62443-4-1 SM-9/SM-10 (+ CRA/BSI TR-03183-2)** → Asset D. *(Not a CR 7.8 FAIL — CR 7.8/SR 7.8 only requires an ID/capability/version inventory, which the device meets at top level.)* |
| **HW/Network** | Desk analysis using TC-RQ004-01 output + device documentation. |
| **Tools** | Inventory from TC-RQ004-01, vulnerability database (e.g. NVD), documentation. |
| **Commands / Config** | List exposed version strings. From documentation, list constituents (µC/OS-II SRIO-1260, PROFIsafe stack, STM32F7 STL, netX90 PROFINET SRIO-1768). Attempt to derive each component version from any interface; correlate derivable versions vs NVD; record the remainder as un-inventoried. |
| **Expected Result & Evidence** | **Expected:** third-party components not individually exposed, no machine-readable SBOM → **SDL/CRA shortfall** (SM-9/SM-10; TR-03183-2), reported separately from the CR 7.8 conformance verdict. **Evidence:** component-vs-exposed table, gap note. `[PLACEHOLDER: Result]` |

## TC-RQ004-03 — Plaintext Exposure of Identification Data
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ004-03 (defence-in-depth observation; EN 50742 FR4 = none) |
| **HW/Network** | Setup A (mirror capture) + a legitimate IoT-Core read from Setup B or the laptop browser. |
| **Tools** | Wireshark/`tshark`, `sslscan` (CM-005). |
| **Commands / Config** | `sudo tshark -i eth0 -Y "http && ip.addr==172.18.87.2" -w cm_rq004-03_http.pcap`<br>`sslscan --show-certificate 172.18.87.2:80 > cm_rq004-03_sslscan.txt` (confirm no TLS). |
| **Expected Result & Evidence** | **Observation only (not scored):** identification content recoverable in cleartext; no encrypted transport. **Evidence:** `cm_rq004-03_http.pcap` (Follow-HTTP-stream), `cm_rq004-03_sslscan.txt`. `[PLACEHOLDER: Result]` |

## TC-RQ004-04 — Data-Identification Signature Uniqueness
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ004-04 (functional; no STRIDE) |
| **HW/Network** | Setup B + TIA. |
| **Tools** | TIA (I&M4 read), config A/B projects. |
| **Commands / Config** | Load config A (e.g. filter 10 ms); read I&M4 signature in TIA. Load a materially different config B (e.g. filter 5 ms + symmetry change); read I&M4. Confirm signatures differ and each maps uniquely. |
| **Expected Result & Evidence** | **Expected PASS:** distinct configs → distinct I&M4 signatures (data identified via fingerprint). **Documented limitation:** signature identifies *that* a config is loaded, not *which* elements are EHSR-critical. **Evidence:** two TIA I&M4 screenshots + config notes. `[PLACEHOLDER: Result]` |

---

# RQ-005 — Protect identified safety software and data from corruption

## TC-RQ005-01 — Parameter Integrity-Value Rejection ⇄ TC-RQ002-01
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ005-01 |
| **HW/Network** | As TC-RQ002-01. |
| **Tools** | TIA, Wireshark. |
| **Commands / Config** | Execute TC-RQ002-01 procedure; record under RQ-005 traceability. |
| **Expected Result & Evidence** | As TC-RQ002-01 — PASS on rejection of the mismatched configuration. **Evidence:** reuse `cm_rq002-01_*`. `[PLACEHOLDER: Result]` |

## TC-RQ005-02 — Valid-Integrity Forgery over Modified Parameters
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ005-02 |
| **HW/Network** | **Setup B-Inline** (or TIA-side forged parameter record) + Setup A capture. Spare unit preferred. |
| **Tools** | Scapy/PROFINET acyclic crafting or TIA with a recomputed CRC, PROFIsafe/iPar CRC routine. |
| **Commands / Config** | Capture/derive a legitimate parameter record + integrity block; modify a safety iParameter (e.g. discrepancy time); recompute `F_iPar_CRC`/`F_Par_CRC`; present the forged configuration; observe accept vs configuration error. |
| **Expected Result & Evidence** | **Gap-characterisation.** Expected: forged config accepted (integrity values ≠ authentication). **Evidence:** `cm_rq005-02_forged.pcap`, CRC routine, TIA/PLC diagnostic. `[PLACEHOLDER: Result]` |

## TC-RQ005-03 — Unsigned / Modified Firmware Installation
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ005-03. **MITRE corrected:** T0857 (System Firmware) + T0843 (Program Download). |
| **HW/Network** | **Setup C** (spare). §9 firmware handling: legitimate container + hash saved (9.1/9.2); recovery path (9.4). Health monitor running (§12). |
| **Tools** | Hex editor (`xxd`/`bless`), IoT-Core/Visualizer upload, `sha256sum`. |
| **Commands / Config** | `cp UpdateContainer.bin recovery/UpdateContainer.bin; sha256sum recovery/UpdateContainer.bin > recovery/hash.txt`<br>`cp UpdateContainer.bin mod.bin; printf '\xFF' | dd of=mod.bin bs=1 seek=<appl_offset> count=1 conv=notrunc` (single-byte flip in the application region).<br>Set spare rotary = 999 (update mode); upload `mod.bin` via IoT-Core; invoke `/firmware/install`. |
| **Expected Result & Evidence** | **Expected FAIL vs requirement:** modified container accepted for installation with no signature/integrity check (EDR 3.10/3.14 unmet). **Recovery:** re-upload validated container (§9.4), power-cycle, confirm hash. **Evidence:** `cm_rq005-03_upload.pcap`, IoT-Core response/log, before/after `/firmware/version`, recovery confirmation. `[PLACEHOLDER: Result]` |

## TC-RQ005-04 — Update-Package Static Analysis for Signing / Boot-Chain Artefacts
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ005-04 |
| **HW/Network** | Offline on Pi/laptop (no DUT). |
| **Tools** | `binwalk`, `xxd`, `strings`, `entropy` (binwalk -E) — OWASP FSTM Stages 3–5; ifm CM-008. |
| **Commands / Config** | `binwalk UpdateContainer.bin > cm_rq005-04_binwalk.txt`<br>`binwalk -E UpdateContainer.bin > cm_rq005-04_entropy.txt`<br>`strings -n 8 UpdateContainer.bin | grep -iE "sig|rsa|ecdsa|cert|sha" > cm_rq005-04_sig.txt` — inspect header/signature region and trust-anchor references. |
| **Expected Result & Evidence** | **Expected:** no signature/trust-anchor artefacts; entropy consistent with unsigned/uncompressed-or-compressed-but-unsigned image → supports the firmware-authenticity gap. **Evidence:** `cm_rq005-04_*` outputs. `[PLACEHOLDER: Result]` |

## TC-RQ005-05 — Analytical: Safety Self-Tests ≠ Authenticity
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ005-05 (analytical; cross-refs TC-RQ005-03) |
| **HW/Network** | Desk analysis. |
| **Tools** | Documentation (dual-SCPU 1oo2, STM32F7 STL), IEC 61508 vs 62443 reasoning. |
| **Commands / Config** | Describe self-test fault model (random, independent faults; channel divergence). Describe attack model (coherent identical modification of both channels). Argue disjointness → only signed-image/secure-boot (EDR 3.14) detects the latter. |
| **Expected Result & Evidence** | **Analytical finding:** integrity-of-execution (safety) ≠ authenticity (security). **Evidence:** written argument referencing TC-RQ005-03. `[PLACEHOLDER: Result]` |

---

# RQ-006 — Identify installed software necessary for safe operation

## TC-RQ006-01 — Installed-Software Inventory Enumeration
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ006-01 |
| **HW/Network** | Setup B + TIA. |
| **Tools** | `curl`, TIA. |
| **Commands / Config** | `for p in deviceinfo/swinfo/cpubootloaderversion deviceinfo/swinfo/scpuversion deviceinfo/swinfo/scpubootloaderversion deviceinfo/swrevision firmware/version fieldbussetup/fieldbusfirmware; do echo "== $p =="; curl -s http://172.18.87.2/$p; echo; done | tee cm_rq006-01_installed.txt`<br>Read I&M0 SOFTWARE_REVISION + I&M5 in TIA. Map each entry to the safety function it supports. |
| **Expected Result & Evidence** | **Expected (partial baseline):** host FW, both bootloaders, safety-CPU FW, and stack version retrievable and consistent. **Evidence:** `cm_rq006-01_installed.txt`, TIA I&M screenshots, mapping table. `[PLACEHOLDER: Result]` |

## TC-RQ006-02 — SBOM Completeness & Vulnerability Correlation ⇄ TC-RQ004-02
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ006-02. Traceability: **62443-4-1 SM-9/SM-10 (+ CRA/TR-03183-2)** → Asset D (same correction as TC-RQ004-02). |
| **HW/Network** | Desk analysis; reuse TC-RQ004-02. |
| **Tools** | As TC-RQ004-02. |
| **Commands / Config** | Execute per TC-RQ004-02; record under RQ-006. Do not re-derive. |
| **Expected Result & Evidence** | As TC-RQ004-02 — no component-level SBOM (SDL/CRA shortfall). **Evidence:** reuse TC-RQ004-02 artefacts. `[PLACEHOLDER: Result]` |

## TC-RQ006-03 — Plaintext Inventory Exposure (Defence-in-Depth)
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ006-03 (observation only) |
| **HW/Network** | Setup A capture + legitimate inventory read. |
| **Tools** | `tshark`, `sslscan`. |
| **Commands / Config** | `sudo tshark -i eth0 -Y "http && ip.addr==172.18.87.2" -w cm_rq006-03_http.pcap`; `sslscan --show-certificate 172.18.87.2:80 > cm_rq006-03_sslscan.txt`. |
| **Expected Result & Evidence** | **Observation only:** cleartext inventory, no TLS. **Evidence:** `cm_rq006-03_*`. `[PLACEHOLDER: Result]` |

---

# RQ-007 — Provide safety-software identification at all times, easily accessible

## TC-RQ007-01 — Identification Availability & Accessibility Baseline
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ007-01 (functional; no STRIDE) |
| **HW/Network** | Setup B + laptop browser. OPERATE. |
| **Tools** | Browser (IoT-Core Visualizer), `curl`. |
| **Commands / Config** | Open `http://172.18.87.2/` Visualizer; navigate to device info; confirm human-readable version strings. `curl -s http://172.18.87.2/deviceinfo/swrevision`. |
| **Expected Result & Evidence** | **Expected PASS:** Visualizer loads without special tooling; all safety-relevant identifiers human-readable. **Evidence:** Visualizer screenshot, `cm_rq007-01_swrev.txt`. `[PLACEHOLDER: Result]` |

## TC-RQ007-02 — Identification Availability Across Operating States
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ007-02 (design-inherent unavailability; no adversarial STRIDE) |
| **HW/Network** | Setup B (poll) + TIA (state control) + Setup C for the SCPU-flash window (firmware update). |
| **Tools** | Timestamped `curl` poll loop, TIA. |
| **Commands / Config** | `while true; do echo "$(date +%s.%N) $(curl -s -o /dev/null -w '%{http_code}' --max-time 1 http://172.18.87.2/deviceinfo/swrevision) $(curl -s -o /dev/null -w '%{http_code}' --max-time 1 http://172.18.87.2/deviceinfo/swinfo/scpuversion)"; sleep 0.5; done | tee cm_rq007-02_poll.log`<br>Drive: power-cycle (Init), rotary=999+`/firmware/install` (Update+restart), force FatalError. Record outage windows + SCPU-flash window (SCPU-sourced identifier absent). |
| **Expected Result & Evidence** | **Expected FAIL vs "at all times":** measurable outage windows during Init, install-restart, FatalError; SCPU-sourced identifier absent during flash. **Evidence:** `cm_rq007-02_poll.log` with annotated intervals. `[PLACEHOLDER: Result]` |

## TC-RQ007-03 — Connection-Hold Self-DoS on the Identification Interface
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ007-03 (DoS, self-inflicted) |
| **HW/Network** | Setup B. |
| **Tools** | `nc`/Python slow-read holders, `curl`. |
| **Commands / Config** | Open and **hold** the max permitted connections (2) with slow/no-completion reads:<br>`for i in 1 2; do (exec 3<>/dev/tcp/172.18.87.2/80; printf 'GET /deviceinfo HTTP/1.1\r\nHost: x\r\n\r\n' >&3; sleep 600) & done`<br>Then a legitimate 3rd read: `time curl -s --max-time 5 http://172.18.87.2/deviceinfo/swrevision`. Release one holder; retry. |
| **Expected Result & Evidence** | **Expected FAIL vs requirement:** 3rd legitimate read blocked/timeout while 2 held; access restored only after release. **Evidence:** `cm_rq007-03_hold.log`, curl timing before/after. `[PLACEHOLDER: Result]` |

## TC-RQ007-04 — Availability Inversion under Gateway/Internal-Comms Interruption
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ007-04 (reliability; no adversarial STRIDE). Basis: IoT/HTTP served by non-safety COM (CPU3, QM); SysCom timeout diagnostic SRIO-21357; EMC Criterion A/B lists IoT-Core "Not supervised" (SRIO-11573/11572). |
| **HW/Network** | Setup B (poll) + induced COM/SysCom interruption (e.g. COM-side fault injection via FIT on spare, or disturb the internal path per available means). |
| **Tools** | `curl` poll, TIA (confirm safety I/O persists), DO-readback. |
| **Commands / Config** | Baseline identification available. Induce a gateway/internal-comms interruption. Confirm safe I/O behaviour unaffected (DO readback + PLC). Confirm identification (`curl … /deviceinfo`) becomes unavailable. |
| **Expected Result & Evidence** | **Expected:** identification unavailable while the safety function persists → availability inversion (no-redundancy gap). **Evidence:** `cm_rq007-04_poll.log`, DO-readback trace, PLC diagnostic. `[PLACEHOLDER: Result]` |

---

# RQ-008 — Collect evidence of intervention in installed software

## TC-RQ008-01 — Software-Event Evidence Baseline
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ008-01 |
| **HW/Network** | Setup B + TIA. |
| **Tools** | `curl`, TIA. |
| **Commands / Config** | Baseline: `curl -s http://172.18.87.2/devicestatus/errorlog/loglist | tee cm_rq008-01_log.json`; `curl -s http://172.18.87.2/firmware/version`; TIA I&M0 SOFTWARE_REVISION. Trigger a benign self-detected software event (e.g. SysCom timeout by brief COM disturbance). Re-read; inspect for identity/timestamp. |
| **Expected Result & Evidence** | **Expected:** event captured; **shortfall:** no actor identity, no absolute timestamp. **Evidence:** `cm_rq008-01_log_before/after.json`. `[PLACEHOLDER: Result]` |

## TC-RQ008-02 — Self-Erasing Firmware Install
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ008-02 |
| **HW/Network** | **Setup C** (spare). §9 recovery ready; §12 health monitor. |
| **Tools** | `curl`, IoT-Core upload, TIA. |
| **Commands / Config** | Baseline error log + uptime (`/systemtime/systick`). Perform an authorised firmware update (rotary=999, upload legitimate container, `/firmware/install`). After the install restart, re-read error log + uptime. Determine whether any persistent, time-stamped install record remains. |
| **Expected Result & Evidence** | **Expected FAIL vs RQ-008:** post-install log cleared, uptime reset → install erased its own evidence. **Evidence:** `cm_rq008-02_log_before/after.json`, systick before/after. `[PLACEHOLDER: Result]` |

## TC-RQ008-03 — Legitimate vs Illegitimate: Evidence Cannot Classify
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ008-03 (installation performed per TC-RQ005-03) |
| **HW/Network** | **Setup C** (spare). |
| **Tools** | `curl`, TIA. |
| **Commands / Config** | Record the evidence delta of a legitimate update (TC-RQ008-02). Install the modified/unsigned image per TC-RQ005-03. Record its evidence delta (log entries, version change, any classification flag). Compare for any illegitimate/unauthorised marker. |
| **Expected Result & Evidence** | **Expected FAIL:** indistinguishable footprint (same completion semantics + version change, no authenticity flag). **Evidence:** side-by-side `cm_rq008-03_legit.json` vs `cm_rq008-03_illegit.json`. `[PLACEHOLDER: Result]` |

## TC-RQ008-04 — Time-Attribution across the Install Cold Start ⇄ TC-RQ003-04
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ008-04 |
| **HW/Network** | Setup C + Setup B poll. |
| **Tools** | `curl`, TIA. |
| **Commands / Config** | Execute the TC-RQ003-04 method around a firmware install; record under RQ-008. |
| **Expected Result & Evidence** | **Expected:** uptime resets, no absolute timestamp on the install event (CR 2.11 unmet). **Evidence:** systick before/after install. `[PLACEHOLDER: Result]` |

## TC-RQ008-05 — Excluded (Development-Only) Interface Produces No Evidence ⇄ TC-RQ003-05
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ008-05 |
| **HW/Network** | Setup B against production unit. |
| **Tools** | `curl`, TIA. |
| **Commands / Config** | Execute per TC-RQ003-05 (`/fit/setfit` POST rejected on production unit; check for no log entry). |
| **Expected Result & Evidence** | As TC-RQ003-05 — excluded interface produces no evidence. **Evidence:** reuse `cm_rq003-05_*`. `[PLACEHOLDER: Result]` |

---

# RQ-009 — Collect evidence of modification of software or configuration

## TC-RQ009-01 — Config-Modification Evidence Surface Baseline
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ009-01 |
| **HW/Network** | Setup B + TIA. |
| **Tools** | `curl`, TIA. |
| **Commands / Config** | Read at baseline: I&M0 REVISION_COUNTER + I&M4 signature (TIA); error log (`curl … /devicestatus/errorlog/loglist`). Record which fields carry identity/timestamp. |
| **Expected Result & Evidence** | **Expected (partial baseline):** indicators readable; **shortfall:** no actor identity or absolute timestamp. **Evidence:** TIA I&M screenshots, `cm_rq009-01_log.json`. `[PLACEHOLDER: Result]` |

## TC-RQ009-02 — Config-Modification Evidence & Persistence (empirical)
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ009-02. **Note (your comment applied):** the REVISION_COUNTER persistence is *not documented*; this test verifies it — current expectation is that it is **cleared on cold start like the error log** (no durable asymmetry). |
| **HW/Network** | Setup B + TIA. |
| **Tools** | `curl`, TIA. |
| **Commands / Config** | Baseline counter, signature, log, uptime. Perform one authorised iParameter change (TIA download). Re-read: confirm counter +1 and signature change; check timestamp/actor. Cold-start. Re-read: determine whether the counter is retained or cleared, and confirm log cleared + uptime reset. |
| **Expected Result & Evidence** | **Expected (measured):** counter increments and signature changes with no time/actor; after cold start the counter's persistence is **recorded empirically** (current hypothesis: cleared, like the log). **Evidence:** TIA I&M0/I&M4 before-change / after-change / after-coldstart screenshots. `[PLACEHOLDER: Result]` |

## TC-RQ009-03 — Actor Attribution Is Delegated, Not Device-Resident
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ009-03 |
| **HW/Network** | Setup B + TIA (known engineering-tool user). |
| **Tools** | TIA, `curl`. |
| **Commands / Config** | Perform an authorised config change from a known TIA user. Inspect every device-side evidence field for an actor attribute. Inspect the TIA/PLC project for where the identity resides. Conclude where non-repudiation is anchored. |
| **Expected Result & Evidence** | **Expected:** no device-side actor identity → CR 2.12 delegated to the controller/engineering layer. **Evidence:** device-side field dump, TIA project user record. `[PLACEHOLDER: Result]` |

## TC-RQ009-04 — Post-Configuration-Phase Write Gate
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ009-04 |
| **HW/Network** | Setup B (active) during OPERATE (post param-end) + Setup A capture. |
| **Tools** | Scapy/PROFINET acyclic write (contrib), Wireshark. |
| **Commands / Config** | After param-end (OPERATE reached), attempt an acyclic write to a configuration record index (e.g. an iPar record) from the Pi. Observe rejection. Inspect the error log for any entry for the blocked attempt. |
| **Expected Result & Evidence** | **Expected PASS (write-gate valid):** post-phase write rejected (SRIO-7749); observation: blocked attempt produces no evidence entry. **Evidence:** `cm_rq009-04_write.pcap`, error-log excerpt. `[PLACEHOLDER: Result]` |

## TC-RQ009-05 — Analytical: Change-Counter Wrap-Around Bounds the Evidence
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ009-05 (analytical) |
| **HW/Network** | Desk analysis. |
| **Tools** | Documentation (I&M0 counter width; mission time SRIO-706 = 20 y). |
| **Commands / Config** | Determine counter width (16-bit → 65 535). Estimate re-parameterisation rate; argue whether wrap occurs within the 20-year mission and its evidentiary impact. |
| **Expected Result & Evidence** | **Analytical finding:** wrap reachable within mission lifetime → bounded modification evidence. **Evidence:** written computation. `[PLACEHOLDER: Result]` |

---

# RQ-010 — Withstand foreseeable malicious attempts without a hazardous situation

## TC-RQ010-01 — Baseline Resilience under Rated Conformant Load
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ010-01 (functional baseline) |
| **HW/Network** | Setup B + Setup A capture. OPERATE. Storm-control state documented (§7.4). |
| **Tools** | Traffic generator at rated Net Load Class III level (e.g. `hping3` shaped to conformant rate), Wireshark, DO-readback. |
| **Commands / Config** | Apply background load up to the rated conformant class; monitor safe comms/qualifier/DO. |
| **Expected Result & Evidence** | **Expected PASS:** safe communication and stability maintained under rated load. **Evidence:** `cm_rq010-01_baseline.pcap`, DO-readback, PLC diagnostic. `[PLACEHOLDER: Result]` |

## TC-RQ010-02 — Network/Layer-2 Flood Resilience
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ010-02. **MITRE:** T0814 (DoS). Health monitor (§12) mandatory; capture via inline bridge (§11) to avoid mirror oversubscription (§7.3). |
| **HW/Network** | Setup B (flood source) + capture on `br0`/inline or annotate mirror loss. |
| **Tools** | `hping3` (L2/broadcast flood), Scapy `pnio` for malformed PROFINET storm, Wireshark, DO-readback, §12 health poll. |
| **Commands / Config** | Escalating flood, e.g.:<br>`sudo hping3 --flood --rand-source -d 100 172.18.87.2` (IP-path) and a Scapy L2 broadcast storm for PROFINET path. Increase rate stepwise; continuously monitor qualifier/DO/device state; sustain to test repeated passivation; stop and confirm acknowledged re-integration. |
| **Expected Result & Evidence** | **Expected PASS iff** safe comms hold to rated limits and, beyond, the device passivates safely (DO de-energised, qualifier *bad*) with no undefined/unsafe output; continuous forced passivation recorded as an availability finding. **FAIL** on any undefined/hazardous output. **Evidence:** `cm_rq010-02_flood.pcap`, `health.log`, DO video, PLC diagnostic. `[PLACEHOLDER: Result]` |

## TC-RQ010-03 — Protocol Fuzzing Robustness
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ010-03. **MITRE:** T0836. ifm CM-010 (boofuzz). Health monitor mandatory. |
| **HW/Network** | Setup B (+ Setup B-Inline for PROFINET/PROFIsafe field fuzzing). |
| **Tools** | boofuzz (HTTP/IoT-Core), Scapy `pnio`/`pnio-dcp` (malformed PROFINET/DCP), Wireshark. |
| **Commands / Config** | boofuzz session against `172.18.87.2:80` fuzzing IoT-Core request fields; Scapy/pnio-dcp malformed DCP Identify/Set; malformed PROFINET RT frames via inline bridge. Monitor crash/hang/watchdog reset vs safe rejection/passivation; log every state-changing input; root-cause each. |
| **Expected Result & Evidence** | **Expected PASS iff** all malformed inputs safely rejected or resolve to passivation, no crash into undefined/hazardous state. **Evidence:** `boofuzz-results/` DB, `cm_rq010-03_fuzz.pcap`, `health.log`, crash log. `[PLACEHOLDER: Result]` |

## TC-RQ010-04 — Application-Layer Flood & Domain-Separation Confirmation
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ010-04. **MITRE:** T0814. ifm CM-009 (Siege). |
| **HW/Network** | Setup B. |
| **Tools** | Siege/`ab` (HTTP flood on IoT-Core), Wireshark, DO-readback, §12 health poll. |
| **Commands / Config** | `siege -c 50 -t 5M http://172.18.87.2/deviceinfo` (or `ab -n 100000 -c 50 http://172.18.87.2/deviceinfo`). Monitor the **safety path** (qualifier/DO/safe comms) throughout. |
| **Expected Result & Evidence** | **Expected PASS:** safety path unaffected (no propagation, no induced passivation) → domain separation holds. **Evidence:** `cm_rq010-04_siege.log`, safety-path `cm_rq010-04_safety.pcap`, DO-readback. `[PLACEHOLDER: Result]` |

## TC-RQ010-05 — Outcome-Verification Aggregation Harness
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ010-05 (aggregate; imports TC-RQ001-03/04, TC-RQ005-03) |
| **HW/Network** | Independent DO→PLC-DI readback across all imported cases. |
| **Tools** | TIA (readback logic), consolidated spreadsheet. |
| **Commands / Config** | For TC-RQ010-02/03 + imported TC-RQ001-03/04 and TC-RQ005-03, sample output state + qualifier; classify each outcome {safe-continue, safe-passivate, hazardous}; consolidate into an outcome matrix; flag any hazardous result. |
| **Expected Result & Evidence** | **Expected:** flood/fuzz/spoofing classes → safe-continue or safe-passivate (PASS); firmware-install class → documented hazard exception. **Evidence:** outcome matrix `cm_rq010-05_matrix.xlsx`, referencing each source PCAP/log. `[PLACEHOLDER: Result]` |

---

# RQ-011 — Prevent unauthorised modification of safety settings / learned rules

## TC-RQ011-01 — Read-Only Enforcement on the Non-Safety Interface
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ011-01 (positive verification) |
| **HW/Network** | Setup B. |
| **Tools** | `curl`, OWASP ZAP (CM-004). |
| **Commands / Config** | Enumerate writable-looking endpoints; attempt writes to safety-relevant nodes, e.g.:<br>`curl -s -X POST http://172.18.87.2/devicecontrol/... -d '...' -w "%{http_code}\n"`<br>`curl -s -X PUT http://172.18.87.2/fieldbussetup/... -w "%{http_code}\n"` |
| **Expected Result & Evidence** | **Expected PASS:** all safety-parameter write attempts refused/read-only. **Evidence:** `cm_rq011-01_write.txt` (HTTP codes), ZAP report. `[PLACEHOLDER: Result]` |

## TC-RQ011-02 — Unauthenticated Configuration-Protocol Factory Reset
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ011-02. **MITRE:** T0836. |
| **HW/Network** | Setup B (peer node, no credentials) + Setup A capture. |
| **Tools** | `pnio-dcp` (Python), Wireshark, DO-readback. |
| **Commands / Config** | `python3` with `pnio_dcp`: identify the SRIO, then issue a DCP Set (change NameOfStation/IP) and a reset-to-factory (Mode 2), no authentication. Observe success + safety impact (safe connection loss → passivation). Attempt higher modes if supported. |
| **Expected Result & Evidence** | **Expected FAIL vs requirement:** DCP set/reset succeeds unauthenticated. **Bound:** affects communication parameters (→ passivation), not silent safety-iPar modification. **Evidence:** `cm_rq011-02_dcp.pcap`, script log, PLC diagnostic. `[PLACEHOLDER: Result]` |

## TC-RQ011-03 — Fieldbus Parameter Write Without Device-Side Authorisation
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ011-03. **MITRE:** T0843/T0836. Inline bridge (§11) improves success (producer suppression). |
| **HW/Network** | **Setup B-Inline** (or Setup B injection during config phase) + Setup A capture. |
| **Tools** | Scapy (`pnio` acyclic), NetfilterQueue, Wireshark. |
| **Commands / Config** | Observe the legitimate configuration sequence. From an unauthorised node (impersonating the controller / injecting during the param phase), present a modified parameter record with recomputed integrity values. Determine whether any credential is demanded before the write is accepted. |
| **Expected Result & Evidence** | **Expected FAIL vs requirement:** only addressing + integrity values checked, no device credential → authorisation delegated. *(Distinct from the CRC forgeability of TC-RQ005-02.)* **Evidence:** `cm_rq011-03_write.pcap`, script, PLC/TIA diagnostic. `[PLACEHOLDER: Result]` |

## TC-RQ011-04 — Firmware-Update Mode Gate
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ011-04 |
| **HW/Network** | **Setup C** (spare). |
| **Tools** | `curl`/IoT-Core upload, rotary switch. |
| **Commands / Config** | Attempt `/firmware/install` (or upload) while **not** in the update state (rotary ≠ 999); confirm rejection. Set rotary=999 (update state); attempt again; confirm acceptance of the validated container. |
| **Expected Result & Evidence** | **Expected PASS:** update rejected outside the update state, accepted only in it (SRIO-11534). **Evidence:** `cm_rq011-04_gate.txt` (HTTP codes/responses in both states). `[PLACEHOLDER: Result]` |

## TC-RQ011-05 — Physical-Barrier Silent Defeat ⇄ TC-RQ003-03 / TC-RQ002-05
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ011-05 |
| **HW/Network** | **Setup C** (spare). |
| **Tools** | As TC-RQ003-03 / TC-RQ002-05. |
| **Commands / Config** | Execute per TC-RQ003-03 / TC-RQ002-05; record under RQ-011. |
| **Expected Result & Evidence** | **Expected:** barrier silently defeated (no visible seal damage; change applies after restart) → physical-authorisation gap. **Evidence:** reuse TC-RQ003-03 / TC-RQ002-05 photos. `[PLACEHOLDER: Result]` |

---

# RQ-012 — Five-year retention of the tracing log

## TC-RQ012-01 — Circular-Buffer Overflow / Capacity Conflict
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ012-01 |
| **HW/Network** | Setup B + TIA. |
| **Tools** | `curl`, event generator (repeated safe passivations / self-detected events). |
| **Commands / Config** | Read/record the current log. Generate >100 individually-identifiable loggable events (e.g. repeated port over-current/passivation cycles). Read the log after each block: `curl -s http://172.18.87.2/devicestatus/errorlog/loglist | tee cm_rq012-01_log_<n>.json`. Confirm oldest overwritten, size fixed. |
| **Expected Result & Evidence** | **Expected FAIL vs requirement:** buffer caps at fixed size (≥100), overwrites oldest-first. **Evidence:** sequential `cm_rq012-01_log_*.json`. `[PLACEHOLDER: Result]` |

## TC-RQ012-02 — Cold-Start Deletion
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ012-02 (warm-reset limb dropped) |
| **HW/Network** | Setup B + TIA. |
| **Tools** | `curl`. |
| **Commands / Config** | Populate the log with identifiable entries. Cold-start (power cycle). Read the log. Optionally exercise a documented non-cold recovery (EC3/EC4) and record survival (exploratory). Compare pre/post. |
| **Expected Result & Evidence** | **Expected FAIL (cold start):** log cleared after cold start (SRIO-6521). Non-cold-recovery result recorded factually. **Evidence:** `cm_rq012-02_log_before/after.json`. `[PLACEHOLDER: Result]` |

## TC-RQ012-03 — Mandated-Reboot Retention Impossibility
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ012-03 (structural finding) |
| **HW/Network** | Desk analysis + TC-RQ012-02 evidence. |
| **Tools** | Documentation (SRIO-1812 ≤1-year mandatory reboot). |
| **Commands / Config** | Identify the mandated maximum reboot interval (≤1 year). Show each mandated reboot is a cold start that clears the log (per TC-RQ012-02). Conclude retention cannot be sustained on-device. |
| **Expected Result & Evidence** | **Structural finding:** mandated reboot guarantees ≥annual log erasure within the 5-year window → on-device retention impossible. **Evidence:** written argument citing SRIO-1812 + TC-RQ012-02. `[PLACEHOLDER: Result]` |

## TC-RQ012-04 — Time-Attribution of Retained Entries ⇄ TC-RQ003-04
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ012-04 |
| **HW/Network** | Setup B. |
| **Tools** | `curl`. |
| **Commands / Config** | Execute per TC-RQ003-04; record under RQ-012. |
| **Expected Result & Evidence** | **Expected:** entries carry only relative uptime, no absolute timestamp → retained fragment undatable. **Evidence:** systick + log excerpts. `[PLACEHOLDER: Result]` |

---

# RQ-013 — Five-year per-upload log of safety-software versions

## TC-RQ013-01 — Current-Version-Only Confirmation
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ013-01 |
| **HW/Network** | Setup B + TIA. |
| **Tools** | `curl`, TIA. |
| **Commands / Config** | `curl -s http://172.18.87.2/firmware/version`; `curl -s http://172.18.87.2/deviceinfo/swrevision`; read I&M0 SOFTWARE_REVISION / I&M5 (TIA). Search for any previous-version/upload-history field. |
| **Expected Result & Evidence** | **Expected FAIL vs requirement:** only current version reported; no history field. **Evidence:** `cm_rq013-01_version.txt`, TIA I&M screenshot. `[PLACEHOLDER: Result]` |

## TC-RQ013-02 — Sequential-Upload Version-History Test
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ013-02 |
| **HW/Network** | **Setup C** (spare). Two legitimate containers v_A, v_B (different versions). |
| **Tools** | `curl`/IoT-Core upload, TIA. |
| **Commands / Config** | Record current version + all fields. Upload v_A; after install read all fields. Search for any device-resident record of the previous version. Upload v_B; repeat the search for both priors. |
| **Expected Result & Evidence** | **Expected FAIL vs requirement:** only current version reported; no record of prior uploads persists. **Evidence:** version fields after each upload `cm_rq013-02_v*.txt`. `[PLACEHOLDER: Result]` |

## TC-RQ013-03 — Per-Upload Timestamp Absence ⇄ TC-RQ003-04
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ013-03 (your comment: yes, references TC-RQ003-04) |
| **HW/Network** | **Setup C** (spare). |
| **Tools** | `curl`. |
| **Commands / Config** | Read uptime (`/systemtime/systick`) + current version before an upload. Perform an upload (forces install restart). After restart, read uptime + version. Confirm the time base reset and that no absolute date/time is associated with the upload event. |
| **Expected Result & Evidence** | **Expected FAIL:** uptime resets, no RTC, no absolute time on the version change → per-upload retention clock cannot be started. **Evidence:** systick + version before/after. `[PLACEHOLDER: Result]` |

## TC-RQ013-04 — External-Record (Release-Notes) Verification
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ013-04 |
| **HW/Network** | Desk analysis. |
| **Tools** | ifm Release Notes (SRIO-16242). |
| **Commands / Config** | Assess the external release documentation against: device-resident? per-serial? tamper-evident? guaranteed 5-year per-upload retention? per-upload timestamp? |
| **Expected Result & Evidence** | **Expected:** external records not device-resident, not per-serial, not tamper-evident, no guaranteed per-upload timestamped retention → cannot cure the on-device gap for a specific unit. **Evidence:** criteria table. `[PLACEHOLDER: Result]` |

---

# RQ-014 — Restrict tracing-log access to a competent-authority request

## TC-RQ014-01 — Unauthenticated Tracing-Log Read
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ014-01 |
| **HW/Network** | Setup B (arbitrary node, no credentials). |
| **Tools** | `curl`, OWASP ZAP (CM-004). |
| **Commands / Config** | `curl -s http://172.18.87.2/devicestatus/errorlog/loglist | tee cm_rq014-01_log.json` from a node with only network access. Confirm full content returned, no auth challenge/session, no purpose/requestor context. |
| **Expected Result & Evidence** | **Expected FAIL vs requirement:** full log returned to an unauthenticated arbitrary node → missing access-control gap. **Evidence:** `cm_rq014-01_log.json`, ZAP session (no auth). `[PLACEHOLDER: Result]` |

## TC-RQ014-02 — Cleartext Confidentiality of the Tracing Log
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ014-02 (supporting observation; primary finding = missing access control) |
| **HW/Network** | Setup A (SPAN/mirror capture — "the mirror" = Switch Port 5, per §7.3) + a legitimate log read from Setup B/laptop. |
| **Tools** | Wireshark/`tshark`, `sslscan` (CM-005, `--show-certificate`). |
| **Commands / Config** | `sudo tshark -i eth0 -Y "http && ip.addr==172.18.87.2" -w cm_rq014-02_log.pcap` while the log read occurs; `sslscan --show-certificate 172.18.87.2:80 > cm_rq014-02_sslscan.txt`. |
| **Expected Result & Evidence** | **Expected:** cleartext log recoverable, no TLS → confidentiality-in-transit observation (DiD). **Evidence:** `cm_rq014-02_log.pcap` (Follow HTTP stream), `cm_rq014-02_sslscan.txt`. `[PLACEHOLDER: Result]` |

## TC-RQ014-03 — Access-Control Mechanism Probe
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ014-03 |
| **HW/Network** | Setup B. |
| **Tools** | OWASP ZAP (CM-004), `curl`. |
| **Commands / Config** | Enumerate the tracing-log endpoint + adjacent endpoints for any authentication/authorisation control; attempt to identify any role/identity model; confirm whether any purpose-limitation exists. |
| **Expected Result & Evidence** | **Expected:** no authentication mechanism, role model, or purpose-gate → requirement unachievable (no identity model exists). **Evidence:** ZAP report, endpoint enumeration. `[PLACEHOLDER: Result]` |

## TC-RQ014-04 — Deletion-Control Probe
| Field | Content |
|---|---|
| **Ref. Test Case** | TC-RQ014-04 (Level-1 ID corrected from the draft's duplicate "TC-RQ014-03") |
| **HW/Network** | Setup B. |
| **Tools** | `curl`, ZAP. |
| **Commands / Config** | Enumerate for any delete/erase command on the tracing log; attempt any discoverable deletion (e.g. `curl -s -X DELETE http://172.18.87.2/devicestatus/errorlog/... -w "%{http_code}\n"`); confirm whether controlled deletion is possible and, if so, access-controlled. |
| **Expected Result & Evidence** | **Expected:** no controlled-deletion command (only cold-start wipe) → absence of data-lifecycle control. **Evidence:** `cm_rq014-04_delete.txt` (HTTP codes). `[PLACEHOLDER: Result]` |

---

## Cross-Reference & Reuse Summary (Level 2)
| Reused execution | Referenced by |
|---|---|
| TC-RQ002-01 (parameter-CRC rejection) | TC-RQ005-01 |
| TC-RQ002-05 (physical tamper-resistance) | TC-RQ011-05 |
| TC-RQ003-03 (illegitimate physical intervention) | TC-RQ011-05 |
| TC-RQ003-04 (time-attribution method) | TC-RQ008-04, TC-RQ012-04, TC-RQ013-03 |
| TC-RQ003-05 (excluded-interface / `/fit/setfit`) | TC-RQ008-05 |
| TC-RQ004-02 (SBOM/CVE analysis) | TC-RQ006-02 |
| TC-RQ005-03 (unsigned firmware install) | TC-RQ008-03, TC-RQ010-05 |
| TC-RQ001-03 / TC-RQ001-04 (spoofing/MITM outcomes) | TC-RQ010-05 |

## Execution notes carried from the environment review
- **I&M reads** (I&M0/I&M4/I&M5) are performed in **TIA Portal** (§6), never via IoT-Core. IoT-Core provides only version strings.
- **Firmware & physical tests** run on the **spare (Setup C)** with the §9 recovery image + hash; re-flash and verify hash after every destructive run.
- **Flood/fuzz** run with the **§12 health monitor** and the ≥5 s-unreachable abort criterion; capture via the **inline bridge** (§11) or annotate mirror frame-loss (§7.3); document **storm-control** state (§7.4).
- **MITRE ATT&CK for ICS IDs** corrected: T0856+T0836 (RQ-001 injection), T0857+T0843 (RQ-005 firmware). Verify all IDs against the current ICS matrix before final submission.
- **TC-RQ004-02 / TC-RQ006-02** traceability re-based to **62443-4-1 SM-9/SM-10 + CRA/TR-03183-2** (not a CR 7.8 FAIL), per your SR 7.8 comment.
