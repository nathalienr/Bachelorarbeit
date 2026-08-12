# MVO/IEC Requirement to Asset & Interface Test Pairing

## Contents
- [README](#readme)
- [Legend](#legend)
- [Requirement to Asset/Interface Pairing](#requirement-to-assetinterface-pairing)
- [Asset/Interface Index](#assetinterface-index)
- [Coverage Gaps](#coverage-gaps)

## README
| Topic | Description |
| --- | --- |
| Purpose | Pairs each of the 14 MVO-derived security requirements (RQ-001 ... RQ-014, [Appendix_Requirement_Derivation_Matrices.tex](Text/Appendix_Requirement_Derivation_Matrices.tex)) with the concrete SRIO assets and interfaces ([SRIO_TARA_Uebersicht.md](SRIO_TARA_Uebersicht.md)) that must be exercised to verify the requirement. |
| Method | For each requirement, its IEC 62443-4-2 CR/RE/EDR anchor (from the same appendix) is used to identify which asset(s) the CR technically protects, then which interface(s) provide physical/logical access to that asset. Existing TARA scenarios and product requirements (SRIO-CS-xxx) already covering the pair are cross-referenced; pairs without an existing TARA/requirement reference are flagged as gaps. |
| Source: Requirements | Table 1 of [Appendix_Requirement_Derivation_Matrices.tex](Text/Appendix_Requirement_Derivation_Matrices.tex) (RQ-001 ... RQ-014). |
| Source: Assets/Interfaces | [SRIO_TARA_Uebersicht.md](SRIO_TARA_Uebersicht.md), sections "Assets" (A-H) and "Interfaces" (IF-01 ... IF-12). |
| Scope note | Requirements mapped to "No direct mapping" or process-level CRs in the appendix (RQ-010, RQ-013) are still paired with assets/interfaces because they remain testable at the product/system level, even though no single component-level CR fully closes them. |

## Legend
| Symbol | Meaning |
| --- | --- |
| Covered | An existing TARA scenario or SRIO-CS requirement already tests this pair. |
| Partial | Related TARA scenarios exist but do not fully test the requirement as worded (e.g. availability vs. on-request access). |
| Gap | No existing TARA scenario or requirement currently tests this pair; a new test case is needed. |
| Conflict | The lower-tier standard (prEN 50742) explicitly contradicts the requirement; testable only against the documented deviation. |

## Requirement to Asset/Interface Pairing
| MVO ID | Requirement (short) | Security Objective | IEC 62443-4-2 Anchor | Target Asset(s) | Target Interface(s) | Test Focus | Related TARA / Req IDs | Coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RQ-001 | Connection of another/remote device shall not cause a hazardous situation. | Integrity | CR 3.1 | A, H | IF-01 (Ethernet/PROFINET), IF-02 (PROFIsafe), IF-03 (IoTCore) | Attach/spoof an external or remote device on each network interface and confirm no unsafe state results. | TARA-001, TARA-002, TARA-024, TARA-025 | Covered |
| RQ-002 | Protect hardware transmitting connection/access signals to safety-critical software against corruption. | Integrity | CR 3.1, CR 2.13 | D, F | IF-09 (JTAG/debug), IF-04 (SysCom), IF-05 (Shared Flash) | Verify physical/service interfaces cannot corrupt data transmitted toward safety-critical software. | TARA-009, TARA-010, TARA-020 | Covered |
| RQ-003 | Collect evidence of legitimate/illegitimate intervention in relevant hardware components. | Accountability | CR 2.8, CR 2.12, CR 2.13, CR 3.11 | D, G | IF-09 (JTAG/debug), IF-08 (Rotary switches) | Confirm physical tamper evidence (covers, seals) and event logging on debug/service and mode-selection hardware. | TARA-020 | Partial |
| RQ-004 | Identify software and data critical for EHSR compliance. | Integrity | CR 7.8 | D, B | IF-03 (IoTCore), IF-05 (Shared Flash) | Verify the product can enumerate/identify safety-critical software and configuration items. | TARA-005, TARA-015 | Covered |
| RQ-005 | Protect identified safety-critical software and data against corruption. | Integrity | CR 3.4, EDR 3.14 | D, B | IF-05 (Shared Flash update path), IF-04 (SysCom), IF-09 (JTAG) | Verify checksum/hash verification at boot and during operation, and iParCRC verification of configuration. | TARA-001, TARA-009, TARA-014, TARA-015 | Covered |
| RQ-006 | Identify installed software necessary for safe operation. | Integrity | CR 7.8 | D | IF-03 (IoTCore), IF-11 (LED, informational only) | Verify installed safety-software version can be identified via the service interface. | TARA-005 | Covered |
| RQ-007 | Provide identification info of safety-relevant software at all times, easily accessible. | Availability | CR 7.8 | D, H | IF-03 (IoTCore), IF-11 (LED) | Verify availability of version info without an active request; check whether "on request" (IoTCore) actually satisfies "at all times". | TARA-005 | Partial |
| RQ-008 | Collect evidence of intervention in installed software. | Accountability | CR 2.8, CR 2.12, CR 3.4 | D, G | IF-05 (Shared Flash update path), IF-03 (IoTCore upload), IF-08 (Rotary switches) | Verify audit events are generated for update-mode entry and firmware-upload interventions. | TARA-006, TARA-013, TARA-019 | Covered |
| RQ-009 | Collect evidence of modification of installed software or its configuration. | Accountability | CR 2.8, CR 2.12, CR 3.4 | B, D | IF-04 (SysCom config transfer), IF-05 (Shared Flash) | Verify version-number/CRC identification means and modification logging for configuration and firmware changes. | TARA-009, TARA-014, TARA-015 | Covered |
| RQ-010 | Withstand reasonably foreseeable malicious third-party attempts. | Availability | No direct CR (process-level) | H, F | IF-01 (Ethernet/PROFINET), IF-02 (PROFIsafe), IF-03 (IoTCore, HTTP/JSON), IF-10 (Power supply) | DoS/fuzzing/malformed-traffic and brownout testing on each externally reachable or physically accessible interface; confirm deterministic fallback. | TARA-002, TARA-004, TARA-008, TARA-021 | Covered |
| RQ-011 | Prevent unauthorized modification of safety-relevant settings/rules, incl. learning-phase data. | Integrity | CR 1.1, CR 2.1 | B, G | IF-03 (IoTCore, **HTTP/JSON web interface authentication**), IF-01 (PROFINET engineering access), IF-08 (Rotary switches, physical mode change) | Verify authentication is enforced before any configuration-changing request on the web interface, and that physical rotary-switch changes require local access authorization equivalents. | TARA-001, TARA-019, TARA-025 | Partial |
| RQ-012 | Enable a tracing log of intervention data, retained 5 years. | Accountability | CR 2.8, CR 2.9 | G, H | IF-04/IF-05 (event sources), IF-03 (log retrieval) | Verify the log retains at least the last intervention of each type and that storage capacity supports the 5-year retention period. | SRIO-CS-004, TARA-006, TARA-013, TARA-019 | Covered |
| RQ-013 | Enable a tracing log of safety-software versions uploaded, retained 5 years per upload. | Accountability | CR 2.8, CR 2.9 (conflict) | D | IF-05 (Shared Flash update path), IF-03 (IoTCore upload) | Verify actual logging behavior against the documented prEN 50742 exclusion of SRASW/SRESW binary versions from the log; document the deviation, do not assume compliance. | TARA-014, TARA-015, TARA-016 | Conflict |
| RQ-014 | Restrict tracing-log access exclusively to conformity demonstration for a competent authority. | Confidentiality | CR 3.9, CR 6.1 | G, H | IF-03 (IoTCore log/diagnostic access), IF-09 (JTAG, bypass risk) | Verify log retrieval requires authorization, deletion only via an authorized procedure, and that no unrestricted read path exists (incl. via debug interface). | - | Gap |

## Asset/Interface Index
Reverse view: for each asset/interface, which requirements must be tested against it.

| Asset/Interface | Description | Applicable MVO IDs |
| --- | --- | --- |
| A | Trusted Safety Function | RQ-001 |
| B | Integrity of Safety Configuration | RQ-004, RQ-005, RQ-009, RQ-011 |
| D | Authenticity and Integrity of Safety Software | RQ-002, RQ-003, RQ-004, RQ-005, RQ-006, RQ-007, RQ-008, RQ-009, RQ-013 |
| F | Separation of Safety and Non-Safety Domains | RQ-002, RQ-010 |
| G | Integrity of Operating Mode | RQ-003, RQ-008, RQ-011, RQ-012, RQ-014 |
| H | SRIO Functionality (Availability + Fail-Safe) | RQ-001, RQ-007, RQ-010, RQ-012, RQ-014 |
| IF-01 | Ethernet / PROFINET | RQ-001, RQ-010, RQ-011 |
| IF-02 | PROFIsafe over PROFINET | RQ-001, RQ-010 |
| IF-03 | IoTCore service interface (HTTP/JSON web API) | RQ-004, RQ-006, RQ-007, RQ-008, RQ-010, RQ-011, RQ-012, RQ-013, RQ-014 |
| IF-04 | SysCom | RQ-002, RQ-005, RQ-009, RQ-012 |
| IF-05 | Shared Flash update path | RQ-002, RQ-004, RQ-005, RQ-008, RQ-009, RQ-012, RQ-013 |
| IF-08 | Rotary switches | RQ-003, RQ-008, RQ-011 |
| IF-09 | JTAG / debug interfaces | RQ-002, RQ-003, RQ-005, RQ-014 |
| IF-10 | Power supply / daisy-chain | RQ-010 |
| IF-11 | LED status indication | RQ-006, RQ-007 |

## Coverage Gaps
| MVO ID | Gap | Recommended Action |
| --- | --- | --- |
| RQ-003 | Only physical tamper-evidence on service points is tested (TARA-020); no dedicated scenario for rotary-switch tamper evidence. | Add a TARA scenario for evidence collection on IF-08 mode-selection tampering. |
| RQ-007 | IoTCore provides identification data "on request", not continuously/"at all times" as required. | Confirm with product team whether this is an accepted deviation or requires a design change; document either outcome. |
| RQ-011 | No TARA scenario currently tests authentication/authorization on the IoTCore HTTP/JSON web interface itself; existing scenarios (TARA-001, TARA-019, TARA-025) cover configuration validation, not access authentication. | Add a dedicated TARA scenario and test case for web-interface authentication enforcement (the concrete "authentication on the HTTP web interface" pairing). |
| RQ-013 | prEN 50742 explicitly excludes SRASW/SRESW binary versions from the tracing log, conflicting with the MVO requirement. | Keep as a documented, flagged conflict; do not close via testing against prEN alone - verify against the MVO wording directly. |
| RQ-014 | No TARA scenario currently addresses purpose-restricted access to tracing-log data. | Add a new TARA scenario and SRIO-CS requirement for log-access authorization scoped to conformity demonstration. |
