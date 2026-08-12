# Requirement-to-Asset Mapping

## Summary
- Total requirements analyzed: 14 (RQ-001 to RQ-014 from Regulation (EU) 2023/1230 Annex III Sections 1.1.9 and 1.2.1)
- Total assets analyzed: 20 (8 SRIO assets A-H and 12 SRIO interfaces IF-01 to IF-12)
- Total mappings created: 44 requirement-to-asset mappings

## Requirement Mapping

### Requirement: RQ-001

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-001
- Regulation (EU) 2023/1230, Annex III, Section 1.1.9
- IEC 62443-4-2 anchor: FR3, CR 3.1

**Requirement Description**
- The system shall be designed so that connection of another device, including remote devices, does not lead to a hazardous situation.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| A - Trusted Safety Function | External and remote connections must not compromise intended safety behavior. | Connect external/remote devices via IF-01, IF-02 and IF-03 and verify no hazardous behavior is introduced. | Safety, Integrity |
| F - Separation of Safety and Non-Safety Domains | Connections terminate in COM; separation must prevent silent override of SCPU decisions. | Inject malformed traffic toward COM and verify safety decisions remain SCPU-authoritative. | Integrity, Safety |
| H - SRIO Functionality | Connection failures or abuse must result in deterministic fail-safe behavior. | Verify fallback, passivation or safe stop under connection disturbance scenarios. | Availability, Safety |

---

### Requirement: RQ-002

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-002
- Regulation (EU) 2023/1230, Annex III, Section 1.1.9
- IEC 62443-4-2 anchor: FR2/FR3, CR 3.1, CR 2.13

**Requirement Description**
- The system shall protect hardware components transmitting signal/data relevant to connection or access to safety-critical software against accidental and intentional corruption.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| C - Integrity and Authenticity of Safety-Relevant Process Data | Signal/data channels carry safety-relevant communication into safety logic. | Corrupt/alter communication on IF-02 and IF-04 and verify corruption is detected/rejected. | Integrity, Authenticity |
| D - Authenticity and Integrity of Safety Software | Hardware paths such as update and debug can affect firmware integrity. | Attempt payload corruption on IF-05 and unauthorized hardware influence on IF-09. | Integrity, Authenticity, Safety |
| F - Separation of Safety and Non-Safety Domains | Corruption attempts often traverse COM-to-safety boundaries. | Validate that corrupted COM-side transfers cannot silently alter safety behavior across IF-04. | Integrity, Isolation |

---

### Requirement: RQ-003

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-003
- Regulation (EU) 2023/1230, Annex III, Section 1.1.9
- IEC 62443-4-2 anchor: FR2/FR3, CR 2.8, CR 2.12, CR 2.13, CR 3.11

**Requirement Description**
- The system shall collect evidence of legitimate or illegitimate intervention in hardware components relevant for connection/access to safety-critical software.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| D - Authenticity and Integrity of Safety Software | Hardware intervention at debug or update paths can alter safety software. | Verify tamper evidence and event traces for interventions through IF-09 and IF-05. | Accountability, Integrity |
| G - Integrity of Operating Mode | Hardware interventions at rotary switch and mode controls change operational state. | Verify intervention evidence for physical mode manipulation at IF-08. | Accountability, Authorization |
| H - SRIO Functionality | Hardware interventions can degrade operation and must remain traceable for forensic review. | Verify evidence is retained and correlated for hardware-triggered service interruptions. | Accountability, Availability |

---

### Requirement: RQ-004

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-004
- Regulation (EU) 2023/1230, Annex III, Section 1.1.9
- IEC 62443-4-2 anchor: FR7, CR 7.8

**Requirement Description**
- The system shall identify software and data critical for compliance with essential health and safety requirements.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| B - Integrity of Safety Configuration | F-Parameters, iParameters and F_Dest are explicitly safety-critical data. | Verify safety-critical configuration items are explicitly identified and listable. | Integrity, Authenticity |
| D - Authenticity and Integrity of Safety Software | Firmware/bootloader are critical software for safety conformity. | Verify safety-relevant software identity/version set is clearly identified. | Integrity, Authenticity |
| E - Integrity of Safety Monitoring | Monitoring logic and watchdog-related data affect safety conformity and must be identified. | Verify safety-monitoring-related software/data are included in identified critical set. | Integrity, Safety |

---

### Requirement: RQ-005

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-005
- Regulation (EU) 2023/1230, Annex III, Section 1.1.9
- IEC 62443-4-2 anchor: FR3, CR 3.4, EDR 3.14

**Requirement Description**
- The system shall protect identified safety-critical software and data against accidental and intentional corruption.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| B - Integrity of Safety Configuration | Safety behavior depends on correct and untampered safety parameters. | Verify iParCRC/dependency/F_Dest validation rejects corrupted configuration. | Integrity, Authenticity, Safety |
| D - Authenticity and Integrity of Safety Software | Firmware and boot integrity must resist corruption and unauthorized change. | Verify boot/software integrity checks and update consistency/compatibility checks. | Integrity, Authenticity |
| C - Integrity and Authenticity of Safety-Relevant Process Data | Corrupted safety data can produce unsafe state transitions if not detected. | Verify invalid/replayed/manipulated safety frames are rejected. | Integrity, Authenticity, Safety |

---

### Requirement: RQ-006

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-006
- Regulation (EU) 2023/1230, Annex III, Section 1.1.9
- IEC 62443-4-2 anchor: FR7, CR 7.8

**Requirement Description**
- The system shall identify installed software necessary for safe operation.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| D - Authenticity and Integrity of Safety Software | Installed safety software identity is a direct requirement target. | Verify installed safety firmware/bootloader versions can be identified consistently. | Integrity |
| A - Trusted Safety Function | Safe operation depends on known, correct safety software baseline. | Verify identified software baseline is linked to safety-function enablement. | Safety, Integrity |

---

### Requirement: RQ-007

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-007
- Regulation (EU) 2023/1230, Annex III, Section 1.1.9
- IEC 62443-4-2 anchor: FR7, CR 7.8 (partial)

**Requirement Description**
- The system shall provide identification information of safety-relevant installed software at all times in easily accessible form.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| D - Authenticity and Integrity of Safety Software | Software identification information belongs to this asset. | Verify retrieval of installed safety software identity through documented access path. | Availability, Integrity |
| H - SRIO Functionality | Access to identification data must remain available during normal lifecycle use. | Verify software identification remains accessible during operation/maintenance states. | Availability |
| G - Integrity of Operating Mode | Identification accessibility must remain valid across mode changes, including update state. | Verify identification access before/during/after update mode transitions. | Availability, Accountability |

---

### Requirement: RQ-008

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-008
- Regulation (EU) 2023/1230, Annex III, Section 1.1.9
- IEC 62443-4-2 anchor: FR2/FR3, CR 2.8, CR 2.12, CR 3.4

**Requirement Description**
- The system shall collect evidence of legitimate or illegitimate intervention in installed software.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| D - Authenticity and Integrity of Safety Software | Firmware intervention events are software intervention events. | Verify intervention logs for upload, install attempt, rejection and success paths. | Accountability, Integrity |
| G - Integrity of Operating Mode | Software intervention is mode-gated (operate vs update) and must be traceable. | Verify mode-entry and software intervention event correlation in logs. | Accountability, Authorization |
| F - Separation of Safety and Non-Safety Domains | Interventions originate in COM-side paths and cross toward safety domain. | Verify evidence includes interventions traversing COM-to-SCPU boundary paths. | Accountability, Integrity |

---

### Requirement: RQ-009

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-009
- Regulation (EU) 2023/1230, Annex III, Section 1.1.9
- IEC 62443-4-2 anchor: FR2/FR3, CR 2.8, CR 2.12, CR 3.4

**Requirement Description**
- The system shall collect evidence of modifications of installed software or its configuration.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| D - Authenticity and Integrity of Safety Software | Software modifications require verifiable traceability. | Verify version/CRC-related modification evidence for software changes. | Accountability, Integrity |
| B - Integrity of Safety Configuration | Configuration modifications directly affect safety behavior. | Verify trace records for parameter/config changes and attempted invalid changes. | Accountability, Integrity, Safety |
| G - Integrity of Operating Mode | Many modifications occur only in specific modes and need mode-linked traceability. | Verify each logged modification is linked to valid operating mode context. | Accountability, Authorization |

---

### Requirement: RQ-010

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-010
- Regulation (EU) 2023/1230, Annex III, Section 1.2.1
- IEC 62443-4-2 mapping note: no direct single CR; treated as resilience objective

**Requirement Description**
- The control system shall withstand reasonably foreseeable malicious third-party attempts that could lead to a hazardous situation.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| A - Trusted Safety Function | Resilience objective ultimately protects safe execution of safety functions. | Perform malicious-attempt scenarios and verify safe behavior is preserved or safely degraded. | Safety, Availability |
| F - Separation of Safety and Non-Safety Domains | Separation is key to containing third-party attacks in non-safety paths. | Verify COM compromise or malformed COM traffic cannot silently alter safety decisions. | Integrity, Isolation, Safety |
| H - SRIO Functionality | Withstanding attack includes deterministic fail-safe availability behavior. | Verify deterministic fallback and recovery under DoS, malformed traffic and disturbance. | Availability, Safety |
| E - Integrity of Safety Monitoring | Detection and monitoring mechanisms are needed to withstand malicious attempts. | Verify watchdog/self-test/plausibility mechanisms detect and trigger documented responses. | Integrity, Availability |

---

### Requirement: RQ-011

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-011
- Regulation (EU) 2023/1230, Annex III, Section 1.2.1
- IEC 62443-4-2 anchor: FR1/FR2, CR 1.1, CR 2.1

**Requirement Description**
- The system shall prevent modifications to safety-relevant settings or rules where those modifications could lead to a hazardous situation.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| B - Integrity of Safety Configuration | Safety-relevant settings are represented by safety parameters and addressing. | Verify unauthorized parameter/rule modification attempts are blocked and logged. | Authorization, Integrity, Safety |
| G - Integrity of Operating Mode | Mode logic controls when safety-relevant modifications are even possible. | Verify update/test mode gating prevents modification outside defined state model. | Authorization, Integrity |
| D - Authenticity and Integrity of Safety Software | Safety-relevant rules include installed safety software behavior definitions. | Verify unauthorized software/rule changes are prevented by compatibility/integrity controls. | Authorization, Authenticity, Integrity |
| F - Separation of Safety and Non-Safety Domains | Authorization boundaries must hold across COM-originating requests. | Verify COM-side requests cannot bypass SCPU-side authorization/validation authority. | Authorization, Integrity |

---

### Requirement: RQ-012

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-012
- Regulation (EU) 2023/1230, Annex III, Section 1.2.1
- IEC 62443-4-2 anchor: FR2, CR 2.8, CR 2.9

**Requirement Description**
- The system shall enable a tracing log of intervention data for five years after placing on the market or putting into service.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| G - Integrity of Operating Mode | Mode-related interventions are key intervention event classes. | Verify intervention events across operate/update/test are logged and retained. | Accountability |
| D - Authenticity and Integrity of Safety Software | Software interventions are central intervention types in source requirements. | Verify software intervention events are recorded with type/correlation information. | Accountability, Integrity |
| B - Integrity of Safety Configuration | Configuration interventions are explicitly safety-relevant interventions. | Verify configuration intervention logging and retention behavior. | Accountability, Integrity |
| H - SRIO Functionality | Five-year traceability must remain operationally maintainable across lifecycle. | Verify log retention policy, storage handling and retrieval over long retention horizon. | Accountability, Availability |

---

### Requirement: RQ-013

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-013
- Regulation (EU) 2023/1230, Annex III, Section 1.2.1
- prEN mapping note: not identified/explicit conflict in lower-tier mapping

**Requirement Description**
- The system shall enable a tracing log of uploaded safety software versions for five years after each upload.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| D - Authenticity and Integrity of Safety Software | Uploaded safety software versions are direct objects of this requirement. | Verify every safety software upload creates version-identifiable log evidence and retention start point. | Accountability, Integrity |
| G - Integrity of Operating Mode | Upload is mode-dependent and the mode context must be traceable with version logging. | Verify upload-version log entries are correlated with update-state entry events. | Accountability |
| H - SRIO Functionality | Retention and retrievability over time are operational obligations tied to product lifecycle. | Verify per-upload retention behavior and practical retrieval for historical version evidence. | Accountability, Availability |

---

### Requirement: RQ-014

**Source**
- Appendix_Requirement_Derivation_Matrices.md, RQ-014
- Regulation (EU) 2023/1230, Annex III, Section 1.2.1
- IEC 62443-4-2 anchor: FR3/FR6, CR 3.9, CR 6.1 (partial)

**Requirement Description**
- The system shall restrict access to tracing log data exclusively for conformity demonstration upon reasoned request from a competent national authority.

**Mapped Assets**
| Asset | Reason for Mapping | Test Focus | Security Property |
|---------|---------|---------|---------|
| G - Integrity of Operating Mode | Log access procedures and deletion authorization are operational governance controls. | Verify only authorized procedures allow log access/deletion and actions are auditable. | Confidentiality, Authorization, Accountability |
| F - Separation of Safety and Non-Safety Domains | Log data is typically exposed through COM-side service paths that must be controlled. | Verify no bypass path from non-safety interfaces can read/modify protected log data. | Confidentiality, Integrity, Authorization |
| H - SRIO Functionality | Conformity-request-driven access must be supportable in real operation without violating purpose limits. | Verify documented process and technical controls enforce purpose-limited access scope. | Confidentiality, Availability, Accountability |

---

## Unmapped Requirements

None.

All 14 analyzed requirements were mapped to one or more SRIO assets using evidence from the provided sources.

## Assets Without Assigned Requirements

### Asset: IF-06 - Safety input terminals
Reason why no matching requirement was found: The 14 analyzed MVO-derived requirements focus on connection safety, software/configuration integrity, intervention logging and tracing-log access; they do not directly specify DI terminal behavior.

### Asset: IF-07 - Safety output terminals
Reason why no matching requirement was found: The analyzed requirement set does not directly state output-channel-specific protection requirements; these are covered in TARA/product controls but not explicitly in RQ-001 to RQ-014 wording.

### Asset: IF-11 - LED status indication
Reason why no matching requirement was found: The requirement set does not include direct obligations for local indicator behavior, only indirect relevance via traceability and safety status interpretation.

### Asset: IF-12 - IPC SCPU1 to SCPU2
Reason why no matching requirement was found: The requirement set does not explicitly call out internal redundant safety-CPU cross-communication, even though it is relevant in TARA.

## Coverage Overview

| Asset | Number of Assigned Requirements |
|---------|---------|
| A - Trusted Safety Function | 3 |
| B - Integrity of Safety Configuration | 5 |
| C - Integrity and Authenticity of Safety-Relevant Process Data | 4 |
| D - Authenticity and Integrity of Safety Software | 11 |
| E - Integrity of Safety Monitoring | 2 |
| F - Separation of Safety and Non-Safety Domains | 6 |
| G - Integrity of Operating Mode | 8 |
| H - SRIO Functionality | 7 |

## Traceability Notes

- Primary asset model and asset semantics were taken from SRIO_TARA_Uebersicht.md (Assets A-H, Interfaces IF-01 to IF-12, SUC assumptions, and confirmed technical facts).
- Requirement wording and requirement IDs were taken from Appendix_Requirement_Derivation_Matrices.md (RQ-001 to RQ-014).
- IEC 62443 anchors used in each requirement section follow the mapping rationale available in the derivation matrices (including partial mappings and no-direct-mapping notes).
- For RQ-013, a known lower-tier conflict exists: the prEN 50742 mapping notes that software version logging is not identified there, while the MVO-derived requirement explicitly requires it. The mapping therefore remains valid at MVO level and should be treated as a compliance gap candidate.
- Mapping is asset-centric (A-H). Interfaces and components are used as justification and test focus paths, and interface-level items without direct requirement wording are listed explicitly in Assets Without Assigned Requirements.
- No requirement or asset was invented; all entities are traceable to the provided source set.