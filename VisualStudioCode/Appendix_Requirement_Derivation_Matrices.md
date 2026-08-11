# Detailed Requirement Derivation Matrices
{#app-requirement-derivation}

This appendix provides the complete, requirement-by-requirement documentation underlying the derivation methodology described in Section *Security Requirements*. It contains the 14 security requirements derived from Annex III, Sections 1.1.9 and 1.2.1 of **Regulation (EU) 2023/1230**, together with their detailed mapping to **prEN 50742** and subsequently to **IEC 62443-4-2** Component Requirements (CRs), Requirement Enhancements (REs), and component-specific requirements such as Embedded Device Requirements (EDRs).

The three tables correspond to the three derivation stages and share a common requirement identifier (`RQ-XXX`) to preserve traceability across all stages.

---

# Security Requirements Derived from Regulation (EU) 2023/1230
{#app-sec-mvo-requirements}

The following requirements were derived from Annex III, Sections 1.1.9 and 1.2.1 of Regulation (EU) 2023/1230.

## RQ-001

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.1.9 |
| Requirement | The system shall be designed so that the connection of another device, including any remote device that communicates with it, does not lead to a hazardous situation. |
| Security Objective | Integrity |
| Requirement Type | Secure Communication |
| Rationale | The regulatory text directly requires that any connection made by an external or remote device shall not compromise the safety of the machinery, which is a foundational requirement for secure interfacing. |

## RQ-002

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.1.9 |
| Requirement | The system shall protect hardware components transmitting signal or data relevant to connection or access to safety-critical software against corruption, whether accidental or intentional. |
| Security Objective | Integrity |
| Requirement Type | Data Integrity |
| Rationale | The regulation requires adequate protection of safety-relevant hardware transmission paths against corruption irrespective of whether the cause is accidental or deliberate. |

## RQ-003

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.1.9 |
| Requirement | The system shall collect evidence of any legitimate or illegitimate intervention in hardware components relevant for connection or access to safety-critical software. |
| Security Objective | Accountability |
| Requirement Type | Logging and Auditability |
| Rationale | The regulation mandates tamper evidence for safety-relevant hardware, which is a direct accountability and forensic traceability requirement. |

## RQ-004

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.1.9 |
| Requirement | The system shall identify the software and data that are critical for compliance with the essential health and safety requirements. |
| Security Objective | Integrity |
| Requirement Type | Configuration Protection |
| Rationale | The identification obligation is separated from the protection obligation because both represent independently verifiable engineering activities. |

## RQ-005

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.1.9 |
| Requirement | The system shall protect identified safety-critical software and data against corruption, whether accidental or intentional. |
| Security Objective | Integrity |
| Requirement Type | Data Integrity |
| Rationale | Protection against corruption of safety-critical software and data is a single verifiable integrity property covering both accidental and deliberate causes. |

## RQ-006

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.1.9 |
| Requirement | The system shall identify the software installed on it that is necessary for safe operation. |
| Security Objective | Integrity |
| Requirement Type | Configuration Protection |
| Rationale | This decomposes the identification obligation from the provisioning-of-information obligation, keeping one verifiable capability per requirement. |

## RQ-007

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.1.9 |
| Requirement | The system shall be able to provide the identification information of safety-relevant installed software at all times in an easily accessible form. |
| Security Objective | Availability |
| Requirement Type | Configuration Protection |
| Rationale | The requirement to make identification information accessible at all times is an independent, separately testable obligation. |

## RQ-008

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.1.9 |
| Requirement | The system shall collect evidence of any legitimate or illegitimate intervention in the software installed on it. |
| Security Objective | Accountability |
| Requirement Type | Logging and Auditability |
| Rationale | Intervention and modification are considered distinct event classes and therefore require separate evidence collection mechanisms. |

## RQ-009

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.1.9 |
| Requirement | The system shall collect evidence of any modification of the installed software or its configuration. |
| Security Objective | Accountability |
| Requirement Type | Logging and Auditability |
| Rationale | Modification of software or configuration is a distinct event class from intervention and requires independent traceability. |

## RQ-010

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.2.1 |
| Requirement | The control system shall withstand reasonably foreseeable malicious attempts from third parties that could lead to a hazardous situation. |
| Security Objective | Availability |
| Requirement Type | Availability / Resilience |
| Rationale | The regulation explicitly mentions malicious third-party attempts as a factor that control systems must withstand. |

## RQ-011

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.2.1 |
| Requirement | The system shall prevent modifications to safety-relevant settings or rules, including those generated during a learning phase, where such modifications could lead to a hazardous situation. |
| Security Objective | Integrity |
| Requirement Type | Configuration Protection |
| Rationale | This is a direct configuration integrity protection requirement. |

## RQ-012

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.2.1 |
| Requirement | The system shall enable a tracing log of data generated in relation to an intervention for five years after the machinery or related product has been placed on the market or put into service. |
| Security Objective | Accountability |
| Requirement Type | Logging and Auditability |
| Rationale | This requirement isolates the intervention-data logging obligation and retention period. |

## RQ-013

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.2.1 |
| Requirement | The system shall enable a tracing log of the versions of safety software uploaded after the machinery or related product has been placed on the market or put into service, for five years after each upload. |
| Security Objective | Accountability |
| Requirement Type | Logging and Auditability |
| Rationale | Software-version logging is treated separately because it concerns a distinct data object with a dedicated retention trigger. |

## RQ-014

| Field | Description |
|---------|---------|
| Source | Annex III, Section 1.2.1 |
| Requirement | The system shall restrict access to the tracing log data exclusively to demonstrating conformity further to a reasoned request from a competent national authority. |
| Security Objective | Confidentiality |
| Requirement Type | Access Control |
| Rationale | The regulation constrains the purpose for which logged data may be accessed, creating an independent access-control obligation. |

---

# Mapping to prEN 50742
{#app-sec-mapping-pren50742}

| MVO ID | prEN 50742 Clause | prEN 50742 Requirement / Topic | Mapping Type |
|----------|----------|----------|----------|
| RQ-001 | §4.2 | Design/construction shall not permit hazardous situations arising from connections | Direct |
| RQ-002 | §1; §7.1; §7.2.1 | Protection of hardware interfaces and accessible communication paths | Partial |
| RQ-003 | §3.4; §7.3.3 | Physical tamper evidence and traceability | Partial |
| RQ-004 | §3.12; §7.5; §7.4.1 | Identification of critical data and software | Partial |
| RQ-005 | §7.4.3.4.1 | SRSL integrity requirements, cryptographic verification | Direct |
| RQ-006 | §7.5 | Identification of software versions and configuration data | Partial |
| RQ-007 | §7.5 | Availability of identification data upon request | Partial |
| RQ-008 | §3.2; §7.3.1-7.3.3 | Intervention logging requirements | Direct |
| RQ-009 | §3.2; §3.3; §7.3.1; §7.3.2 | Modification logging and version identification | Direct |
| RQ-010 | §4.3 | Vulnerability elimination and mitigation process | Partial |
| RQ-011 | §7.4.3.3.1 | Authorization requirements for interventions | Partial |
| RQ-012 | §7.3.4 | Logging retention for five years | Direct |
| RQ-013 | §7.3.1 | Requirement explicitly not identified in prEN | Not identified |
| RQ-014 | §7.3.5; §7.3.3 | Protection of logs and evidence | Partial |

---

# Mapping to IEC 62443-4-2
{#app-sec-mapping-iec62443}

| MVO ID | FR | CR / RE / EDR | IEC 62443-4-2 Topic | Type |
|----------|----------|----------|----------|----------|
| RQ-001 | FR3 | CR 3.1 | Communication Integrity | Partial |
| RQ-002 | FR2, FR3 | CR 3.1, CR 2.13 | Communication Integrity / Interface Protection | Partial |
| RQ-003 | FR2, FR3 | CR 2.8, CR 2.12, CR 2.13, CR 3.11 | Auditable Events, Non-Repudiation, 