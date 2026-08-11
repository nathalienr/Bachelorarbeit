# SRIO Requirement-to-Asset Applicability Analysis

## Scope and System Boundary

- **Assumed role of SRIO**: The source documents describe SRIO as "a functionally safe remote I/O module in a PROFINET/PROFIsafe network, acting as [a] safe gateway between sensors/actuators and F-Host" (SUC Assumptions, "System" row), operating to IEC 61508 SIL3 / EN ISO 13849-1 PL e Cat.4. SRIO is therefore a **component** that is integrated by others into a larger control system and, ultimately, into a complete machine — it is not itself described as a complete machine.
- **Product category under Regulation (EU) 2023/1230**: The provided documents (`Appendix_Requirement_Derivation_Matrices.md`, `SRIO_TARA_Interface_Asset_Analysis.md`) contain **no explicit statement** of SRIO's legal classification (e.g., "machinery", "related product", "safety component", or "partly completed machinery" under Article 3 / Annex I of the Regulation). Given SRIO's function (a safety-related I/O gateway performing a safety function within a larger machine control chain) it *behaves like* a safety component in engineering terms, but this document does **not** assert a definitive legal classification — this is recorded below as an open issue.
- **Product/machine responsibility boundary**: Per the SUC Assumptions ("Included scope" / "Excluded scope" rows), SRIO's own cybersecurity analysis explicitly covers COM, SCPU, IPC, field interfaces and the IoTCore interface. It explicitly **excludes** "complete plant/network architecture risk treatment, third-party PLC hardening and customer-specific remote access", which are assigned to the "Operator/Integrator". The documents further state that "SRIO product-level TARA does not replace plant/system-level risk assessment or operator environmental measures" (README, "Important assumption"). This is treated as the authoritative boundary: SRIO product responsibility = its own hardware, firmware, configuration, logs and documented interfaces (IF-01…IF-12); machine/system responsibility = F-Host/PLC behavior, network architecture, physical installation environment, operator procedures, and the hazard/risk assessment of the complete machine.
- **Assumptions that could not be confirmed from the input documents** (open issues):
  1. SRIO's exact legal product classification under Regulation (EU) 2023/1230 is not stated in the source files.
  2. Whether the SRIO vendor also acts as, or supplies documentation directly to, the "machine manufacturer" role is not stated.
  3. No concrete target machine, application, or installation topology is described — hazard consequences of a connected/remote device (relevant to RQ-001, RQ-010, RQ-011) can therefore only be discussed generically, not verified against a specific machine.
  4. No log-retention or archival mechanism (e.g., external log server, capacity for multi-year storage) is described for the 5-year retention obligations (RQ-012, RQ-013); Shared Flash is described only as a firmware/version storage medium, not a log archive.
  5. No "learning phase" / adaptive or AI-based configuration mechanism is described anywhere in the SRIO source material (relevant to RQ-011).

## Applicability Summary

| Requirement | Applicability | Gateway responsibility | External responsibility | Mapped interfaces | Evidence status |
|-------------|---------------|------------------------|--------------------------|--------------------|------------------|
| RQ-001 | Partially applicable / shared responsibility | Domain separation (TB1) and safe-state reaction to anomalous external communication | Machine-level hazard analysis; F-Host/PLC behavior; network architecture (operator) | IF-01, IF-02, IF-03 | Partial |
| RQ-002 | Partially applicable / shared responsibility | Logical/electrical protection of SysCom and Shared Flash data paths (TB2/TB3) | Physical protection of JTAG/debug access is explicit operator responsibility | IF-04, IF-05, IF-09 | Partial |
| RQ-003 | Partially applicable / shared responsibility | Detection/logging of rotary-switch mismatch and debug-lock state | Physical tamper protection of local/physical interfaces is operator responsibility | IF-05, IF-08, IF-09 | Partial |
| RQ-004 | Partially applicable / shared responsibility | Identification of SRIO's own safety software/data (SRSL, firmware, config) | Determination of which software is "critical for compliance with EHSRs" is a machine-level risk-assessment outcome | IF-03, IF-04, IF-05 | Partial |
| RQ-005 | Directly applicable at gateway level | Firmware/data integrity verification, boot integrity, signature checks | None identified beyond standard supply-chain trust | IF-04, IF-05, IF-09 | Sufficient |
| RQ-006 | Directly applicable at gateway level | Identification/storage of installed firmware version and configuration data | None identified | IF-03, IF-05 | Sufficient |
| RQ-007 | Directly applicable at gateway level | On-demand (IoTCore) and local (LED) provisioning of identification data | None identified | IF-03, IF-11 | Sufficient |
| RQ-008 | Directly applicable at gateway level | Logging of update/service-function triggers and debug access | None identified | IF-03, IF-04, IF-05, IF-09 | Sufficient |
| RQ-009 | Directly applicable at gateway level | Logging of configuration/software modification events regardless of origin | Legitimacy of an externally-issued configuration command may need correlation with F-Host/engineering-tool records | IF-01, IF-03, IF-04, IF-05, IF-08 | Partial |
| RQ-010 | Partially applicable / shared responsibility | Local resilience: rate-limiting, parser hardening, watchdog, deterministic fail-safe reaction | Network segmentation, plant-level DoS protection, and whether an attack actually causes a "hazardous situation" are machine/operator-level | IF-01, IF-02, IF-03, IF-10 | Partial |
| RQ-011 | Partially applicable / shared responsibility | SCPU-side validation/rejection of unauthorized configuration changes | Whether a change "could lead to a hazardous situation" is a machine-level judgment; no learning-phase mechanism exists in SRIO to assess | IF-01, IF-04, IF-08 | Partial |
| RQ-012 | Partially applicable / shared responsibility | Generation and short/medium-term local exposure of intervention-related diagnostic data | Long-term (5-year) archival/retention infrastructure is not evidenced at gateway level; likely a manufacturer/operator record-keeping obligation | IF-03, IF-05 | Insufficient (retention) / Partial (origin) |
| RQ-013 | Partially applicable / shared responsibility | Generation and short/medium-term exposure of firmware version/upload records | Long-term (5-year) archival/retention is not evidenced at gateway level | IF-03, IF-05 | Insufficient (retention) / Partial (origin) |
| RQ-014 | Partially applicable / shared responsibility | Technical access control/authentication on SRIO's own diagnostic/log endpoints | The organizational policy that log access is granted "exclusively" for authority-conformity requests is a manufacturer/process-level control, not purely technical | IF-03 | Partial |

## Detailed Assessment

### RQ-001

**Requirement:**
The system shall be designed so that the connection of another device, including any remote device that communicates with it, does not lead to a hazardous situation.

**Applicability classification:**
Partially applicable / shared responsibility

**Applicability rationale:**
SRIO can only control its own reaction to an external/remote connection (e.g., rejecting invalid PROFINET/PROFIsafe/IoTCore traffic and entering a safe state); whether such a connection actually causes a "hazardous situation" is a property of the complete machine (actuators, physical process, environment) that SRIO is integrated into. This cannot be fully verified by testing SRIO alone — it requires machine-level hazard/risk assessment by the manufacturer/integrator, consistent with the documented exclusion of "complete plant/network architecture risk treatment" from the SRIO-level TARA.

**SRIO contribution:**
Trust boundary TB1 requires that a compromised communication channel must not directly affect the Safety Domain; SRIO is designed to reject invalid/anomalous PROFINET, PROFIsafe and IoTCore traffic and transition to a defined safe state (TARA-001 through TARA-008, TARA-024).

**External dependencies:**
Machine manufacturer/system integrator must perform the machine-level hazard analysis that determines whether a given connection scenario is hazardous; the F-Host/PLC and overall network architecture determine actual exposure; the operator is responsible for network segmentation per the documented "Excluded scope" (customer-specific remote access, plant/network architecture).

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-01 | Ethernet / PROFINET | Documented "External" connection point; TARA records tampering/DoS scenarios from network-connected devices | TARA-001, TARA-002 | High |
| IF-02 | PROFIsafe over PROFINET | Documented "External logical safety channel"; safety process data spoofing/DoS is directly relevant to hazardous outcomes | TARA-003, TARA-004 | High |
| IF-03 | IoTCore service interface | Documented "External" interface reachable from operator network; DoS/EoP scenarios recorded | TARA-005–008, TARA-024 | Medium |

**Gateway-level verification potential:**
Fault-injection/fuzz testing of IF-01/IF-02/IF-03 to confirm SRIO rejects invalid/malicious input and reaches a defined, documented safe state; verification that COM-side anomalies do not alter SCPU state (TB1/TB2 separation tests).

**Machine/system-level verification need:**
Confirming that a connection-induced fault at SRIO does not translate into an actual hazardous situation requires machine-level FMEA, testing of the F-Host/PLC's reaction to SRIO's safe-state signaling, and physical/process hazard analysis — none of which can be performed by testing SRIO in isolation.

**Open assumptions or missing evidence:**
No specific target machine or hazard scenario is described in the source documents; the phrase "hazardous situation" cannot be evaluated without machine-specific context.

---

### RQ-002

**Requirement:**
The system shall protect hardware components transmitting signal or data relevant to connection or access to safety-critical software against corruption, whether accidental or intentional.

**Applicability classification:**
Partially applicable / shared responsibility

**Applicability rationale:**
SRIO implements logical/electrical protection for its own internal data paths that carry access to safety-critical software (SysCom, Shared Flash), which is directly testable at gateway level. However, the JTAG/debug interface — the clearest "hardware component" providing direct access to safety-critical software — is explicitly documented as relying on "encapsulation and operator physical protection" (TARA-020 mitigation), i.e., physical protection is a shared, partly external responsibility per the SUC Assumption "Physical protection is part of operator responsibility based on risk analysis."

**SRIO contribution:**
TB2 requires the Safe CPU to detect manipulated data from the COM module over SysCom; TB3 requires the Safe CPU to independently verify the firmware image rather than trust Shared Flash; production debug-lock of JTAG is a documented product-side mitigation (SRIO-CS-007).

**External dependencies:**
Physical tamper protection of JTAG/debug access and of the device enclosure is an operator responsibility based on the operator's own risk analysis (SUC Assumption "Physical protection"); this cannot be verified by testing the gateway's logic alone.

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-04 | SysCom | Internal SPI path explicitly protected against manipulation per TB2; fully within gateway control | TARA-009, TARA-010 | High |
| IF-05 | Shared Flash update path | Firmware image transfer path explicitly not trusted by SCPU per TB3; verification logic is gateway-internal | TARA-014, TARA-016 | High |
| IF-09 | JTAG / debug interfaces | Direct hardware access to safety-critical software; mitigation explicitly shared with operator physical protection | TARA-020 | Medium |

**Gateway-level verification potential:**
SCPU-side validation tests for manipulated SysCom data; signature/hash verification tests for Shared Flash firmware images; verification that production units have debug access locked/disabled.

**Machine/system-level verification need:**
Confirming that physical access to JTAG/debug ports is actually prevented in the field depends on the installation's physical security measures, which are outside SRIO's own testable scope.

**Open assumptions or missing evidence:**
No details are given on the specific physical protections (enclosure, sealing, tamper-evident labels) assumed to be in place at installation; cannot confirm a specific external control exists beyond the general SUC statement.

---

### RQ-003

**Requirement:**
The system shall collect evidence of any legitimate or illegitimate intervention in hardware components relevant for connection or access to safety-critical software.

**Applicability classification:**
Partially applicable / shared responsibility

**Applicability rationale:**
SRIO can technically detect and log some hardware-level interventions it has visibility into (rotary-switch state mismatch, debug-lock status), which is directly testable. However, "evidence collection" for a physical intervention (e.g., an opened enclosure or a used JTAG port in the field) fundamentally depends on physical tamper-evidence measures that are, per the SUC Assumptions, an operator responsibility informed by the operator's own risk analysis — SRIO cannot alone attest to physical events it has no sensor for.

**SRIO contribution:**
Rotary-switch changes are detected and compared against expected configuration with mismatch diagnostics (TARA-019); production debug-lock state is a documented control point (SRIO-CS-007) that could, in principle, be logged/attested.

**External dependencies:**
Physical/tamper-evident protection of the enclosure and of local physical interfaces is an operator responsibility; no product-level physical tamper sensor (e.g., enclosure switch) is documented in the provided material.

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-08 | Rotary switches | Documented mismatch-diagnostics capability for local physical setting changes | TARA-019 | High |
| IF-09 | JTAG / debug interfaces | Documented debug-lock control point; evidence collection concept only partially described | TARA-020 | Medium |
| IF-05 | Shared Flash update path | Hardware write-path for firmware; intervention evidence tied to firmware verification failures | TARA-014 | Medium |

**Gateway-level verification potential:**
Verify that a rotary-switch change is detected, logged, and surfaced as a diagnostic event; verify debug-lock state can be queried/attested.

**Machine/system-level verification need:**
Verifying that a physical enclosure intrusion or an actual field use of JTAG is detected requires physical tamper-evidence mechanisms and procedures that are not described as part of SRIO's own design in the provided documents.

**Open assumptions or missing evidence:**
No documented tamper-evident hardware feature (e.g., enclosure switch, seal) exists in the source material; whether such a feature exists at all is unclear and flagged as an evidence gap.

---

### RQ-004

**Requirement:**
The system shall identify the software and data that are critical for compliance with the essential health and safety requirements.

**Applicability classification:**
Partially applicable / shared responsibility

**Applicability rationale:**
SRIO can identify its own safety-relevant software/data components (SRSL/firmware, safety configuration) via IoTCore device information and Shared Flash version metadata — this part is directly testable. However, the determination of *which* software/data across the complete machine is "critical for compliance with the essential health and safety requirements" is inherently a machine-level risk-assessment outcome performed by the machine manufacturer, since EHSRs under the Regulation apply to the complete machinery, not to a component in isolation.

**SRIO contribution:**
IoTCore exposes device/firmware identification information; Shared Flash stores firmware version metadata; SysCom carries configuration/version data internally to the SCPU for identification purposes.

**External dependencies:**
The machine manufacturer must determine, at machine level, which software (including SRIO's software as one contributing element) is "critical for compliance with the essential health and safety requirements" of the complete machine.

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-03 | IoTCore service interface | Documented source of "device information" used for identification | TARA-005, TARA-006 | Medium |
| IF-05 | Shared Flash update path | Documented store of firmware "version information" | TARA-015 | High |
| IF-04 | SysCom | Internal transfer path for configuration/version data to SCPU | — | Low |

**Gateway-level verification potential:**
Verify that SRIO's own safety software/data components can be uniquely and correctly identified via IoTCore/Shared Flash.

**Machine/system-level verification need:**
Confirming that the *complete set* of software/data critical for machine-level EHSR compliance has been correctly identified (including software outside SRIO, e.g., in the F-Host/PLC) cannot be demonstrated by testing SRIO alone.

**Open assumptions or missing evidence:**
No machine-level risk assessment or EHSR compliance documentation is provided; it is unclear whether SRIO's safety software is currently formally designated as "critical for compliance" at the machine level.

---

### RQ-005

**Requirement:**
The system shall protect identified safety-critical software and data against corruption, whether accidental or intentional.

**Applicability classification:**
Directly applicable at gateway level

**Applicability rationale:**
Once SRIO's own safety-critical software/data is identified (RQ-004), its protection against corruption is a property that SRIO implements and that can be fully verified by testing SRIO alone: boot/firmware integrity verification (TB3), SCPU-side validation of configuration and process data (TB2), and internal transmission-path integrity checks. No external component is required to exercise or verify this protection mechanism.

**SRIO contribution:**
Cryptographic signature/hash verification of firmware images before use; SCPU-side integrity/consistency validation of configuration and process data received over SysCom; rejection of corrupted/invalid data with a safe-state fallback.

**External dependencies:**
None identified for the core protection mechanism; supply-chain trust in the initial (un-corrupted) firmware/key provisioning is an implicit assumption but not attributed to a specific external party in the source documents.

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-04 | SysCom | SCPU independently validates configuration/process data integrity per TB2 | TARA-009, TARA-010 | High |
| IF-05 | Shared Flash update path | SCPU verifies firmware image integrity independent of Shared Flash trust per TB3 | TARA-014 | High |
| IF-09 | JTAG / debug interfaces | Potential firmware/memory modification vector requiring integrity protection | TARA-020 | Medium |

**Gateway-level verification potential:**
Signature/hash mismatch tests, corrupted-firmware-image rejection tests, SysCom fault-injection tests, and confirmation of safe-state fallback on any detected corruption — all executable directly against SRIO.

**Machine/system-level verification need:**
None specific to this requirement beyond confirming that the identification step (RQ-004) correctly scoped what must be protected.

**Open assumptions or missing evidence:**
None beyond the general open issue of initial key/firmware provisioning trust, which is not detailed in the source documents.

---

### RQ-006

**Requirement:**
The system shall identify the software installed on it that is necessary for safe operation.

**Applicability classification:**
Directly applicable at gateway level

**Applicability rationale:**
This requirement concerns SRIO's own installed software, which SRIO stores and exposes identification information for via IoTCore and Shared Flash. This is fully testable by examining SRIO alone.

**SRIO contribution:**
IoTCore firmware update handling and device information; Shared Flash version metadata storage for the installed firmware.

**External dependencies:**
None identified — the requirement is scoped to "the software installed on it" (i.e., on SRIO itself).

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-03 | IoTCore service interface | Documented firmware update handling and device information exposure | TARA-006 | High |
| IF-05 | Shared Flash update path | Documented storage of firmware version information | TARA-015 | High |

**Gateway-level verification potential:**
Verify that installed firmware version/identity can be retrieved and matches the actually running software.

**Machine/system-level verification need:**
None — this requirement is scoped to SRIO's own installed software.

**Open assumptions or missing evidence:**
None identified.

---

### RQ-007

**Requirement:**
The system shall be able to provide the identification information of safety-relevant installed software at all times in an easily accessible form.

**Applicability classification:**
Directly applicable at gateway level

**Applicability rationale:**
"At all times in an easily accessible form" maps directly to SRIO's own documented output channels (networked IoTCore query, local LED indication), both of which can be verified by testing SRIO alone.

**SRIO contribution:**
IoTCore provides on-demand diagnostics/device information; LED status indication provides always-available local observability.

**External dependencies:**
None identified for the technical provisioning mechanism; however, whether "at all times" is interpreted to include periods of power loss/network outage is not addressed in the source documents.

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-03 | IoTCore service interface | Documented diagnostics/device information retrieval point | TARA-005 | High |
| IF-11 | LED status indication | Only always-on, local observation interface documented | TARA-022 | Medium |

**Gateway-level verification potential:**
Verify identification data availability/retrieval via IoTCore under normal operation; verify LED status behavior is consistent with authoritative diagnostic state.

**Machine/system-level verification need:**
None specific — accessibility is a gateway-local property.

**Open assumptions or missing evidence:**
No definition of "at all times" edge cases (e.g., during boot, power loss) is provided.

---

### RQ-008

**Requirement:**
The system shall collect evidence of any legitimate or illegitimate intervention in the software installed on it.

**Applicability classification:**
Directly applicable at gateway level

**Applicability rationale:**
All documented mechanisms by which SRIO's installed software can be accessed, triggered for update, or physically manipulated (IoTCore, SysCom update trigger, Shared Flash, JTAG) are internal to SRIO, making evidence collection for these events fully verifiable by testing SRIO alone.

**SRIO contribution:**
Logging/diagnostics for firmware update triggers, service-function use, SysCom update-trigger events, and (where implemented) debug-lock status.

**External dependencies:**
None identified — the intervention paths themselves are all gateway-internal or gateway-facing.

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-03 | IoTCore service interface | Firmware update/service-function trigger point | TARA-006, TARA-007 | High |
| IF-04 | SysCom | Internal update-trigger data flow | TARA-013 | High |
| IF-05 | Shared Flash update path | Firmware write path subject to intervention | — | Medium |
| IF-09 | JTAG / debug interfaces | Physical debug/manipulation path | TARA-020 | Medium |

**Gateway-level verification potential:**
Verify that update triggers, service-function invocations, and (if implemented) debug access attempts are logged with sufficient detail to distinguish legitimate from illegitimate use.

**Machine/system-level verification need:**
None specific — evidence collection is a gateway-local logging property.

**Open assumptions or missing evidence:**
The provided TARA/Requirements sections describe mitigations (authorization, signature checks) more thoroughly than the logging/evidence mechanism itself; exact log content/format is not specified.

---

### RQ-009

**Requirement:**
The system shall collect evidence of any modification of the installed software or its configuration.

**Applicability classification:**
Directly applicable at gateway level

**Applicability rationale:**
SRIO is the entity that ultimately applies and must log any configuration/software modification, regardless of whether the modification command originated internally or from an external source (F-Host/PLC/engineering tool via IF-01). The logging obligation itself is therefore testable at gateway level, even though the legitimacy/origin of an externally-issued command may require correlation with external records.

**SRIO contribution:**
SCPU-side configuration validation and logging (TARA-001, TARA-009); firmware update logging (TARA-006); Shared Flash version-change logging (TARA-014, TARA-015); rotary-switch change detection (TARA-019).

**External dependencies:**
Establishing whether an externally-issued configuration change (via IF-01/PROFINET) was itself authorized may require correlating SRIO's log with F-Host/PLC/engineering-tool records, which are outside SRIO's own evidence.

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-01 | Ethernet / PROFINET | Source of external parameterization changes that SRIO must log | TARA-001 | Medium |
| IF-03 | IoTCore service interface | Firmware update workflow modification path | TARA-006 | High |
| IF-04 | SysCom | Internal configuration transfer/modification path | TARA-009 | High |
| IF-05 | Shared Flash update path | Firmware write path for modifications | TARA-014, TARA-015 | High |
| IF-08 | Rotary switches | Local physical configuration modification path | TARA-019 | High |

**Gateway-level verification potential:**
Verify that each listed modification path produces a corresponding, attributable log entry at SRIO.

**Machine/system-level verification need:**
Confirming the *authorization chain* for an externally-issued modification (e.g., that the F-Host/engineering tool itself was used by an authorized person) is outside SRIO's testable scope.

**Open assumptions or missing evidence:**
No detail is given on whether SRIO's logs include sufficient context (e.g., source address/identity) to support external correlation.

---

### RQ-010

**Requirement:**
The control system shall withstand reasonably foreseeable malicious attempts from third parties that could lead to a hazardous situation.

**Applicability classification:**
Partially applicable / shared responsibility

**Applicability rationale:**
SRIO implements local resilience measures (rate-limiting, parser hardening, watchdog, deterministic fail-safe behavior) that are directly testable. However, the requirement addresses the "control system" withstanding attacks that "could lead to a hazardous situation" — full resilience depends on network-level protections (segmentation, firewalls) that the source documents explicitly assign to the operator/integrator ("Excluded scope"), and whether a successful attack actually produces a hazardous situation is a machine-level consequence, not a gateway-level property.

**SRIO contribution:**
Documented DoS mitigations for PROFINET (TARA-002), PROFIsafe timeout/safe-state handling (TARA-004), IoTCore parser hardening (TARA-008, rated Critical initial risk), and power-supply brownout/safe-state behavior (TARA-021).

**External dependencies:**
Network segmentation, firewalling, and secure remote-access architecture are explicitly operator/integrator responsibilities (TARA-024 treatment: "Transfer/Mitigate"; SUC "Excluded scope"); whether an attack leads to a hazardous situation depends on the complete machine/process.

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-01 | Ethernet / PROFINET | Documented DoS/flooding scenario | TARA-002 | High |
| IF-02 | PROFIsafe over PROFINET | Documented communication-loss/DoS scenario | TARA-004 | High |
| IF-03 | IoTCore service interface | Documented Critical-rated parser DoS scenario | TARA-008, TARA-024 | High |
| IF-10 | Power supply / daisy-chain | Documented power-manipulation DoS scenario (explicitly "Transfer/Mitigate" — shared) | TARA-021 | Medium |

**Gateway-level verification potential:**
Robustness/fuzz testing, network-overload testing, and watchdog/fail-safe behavior verification at each listed interface.

**Machine/system-level verification need:**
Verifying that the operator's network segmentation is actually in place, and that a successful attack does not translate into a hazardous situation for the specific machine, requires system/plant-level assessment outside SRIO's test scope.

**Open assumptions or missing evidence:**
No specific third-party attack scenario tied to an actual machine/hazard is described; "reasonably foreseeable" is not further specified for a concrete deployment.

---

### RQ-011

**Requirement:**
The system shall prevent modifications to safety-relevant settings or rules, including those generated during a learning phase, where such modifications could lead to a hazardous situation.

**Applicability classification:**
Partially applicable / shared responsibility

**Applicability rationale:**
SRIO directly implements and can be tested for prevention of unauthorized static configuration changes (SCPU-side validation/rejection). However, no "learning phase" or adaptive/AI-based configuration-generation mechanism is described anywhere in the SRIO source material, so that part of the requirement has no corresponding gateway function to verify. In addition, whether a prevented/allowed modification "could lead to a hazardous situation" is, as with RQ-001, a machine-level judgment.

**SRIO contribution:**
SCPU independently validates configuration integrity, sequence, source context and activation conditions before applying safety-relevant settings (TARA-001, TARA-009); rotary-switch changes are detected and compared against expected configuration (TARA-019).

**External dependencies:**
Machine-level judgment of hazard consequence from a configuration change; no learning-phase mechanism exists in SRIO, so any machine-level learning/adaptive safety-rule generation (if present elsewhere in the system) is entirely outside SRIO's scope.

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-01 | Ethernet / PROFINET | Source of external parameterization changes to safety-relevant settings | TARA-001 | Medium |
| IF-04 | SysCom | SCPU validates configuration changes transferred from COM | TARA-009 | High |
| IF-08 | Rotary switches | Local physical modification of addressing/mode settings | TARA-019 | Medium |

**Gateway-level verification potential:**
Negative tests for unauthorized/invalid configuration changes on IF-01/IF-04/IF-08, confirming rejection and safe-state fallback.

**Machine/system-level verification need:**
Confirming that a rejected/accepted configuration change genuinely avoids a hazardous situation requires machine-level context; any learning-phase mechanism, if it exists at machine level (e.g., in the F-Host/PLC), is entirely untestable via SRIO.

**Open assumptions or missing evidence:**
No learning-phase/adaptive mechanism is documented for SRIO or the wider system in the provided files — this sub-clause is flagged as **not applicable to SRIO based on current evidence**, pending confirmation of whether such a mechanism exists elsewhere in the machine.

---

### RQ-012

**Requirement:**
The system shall enable a tracing log of data generated in relation to an intervention for five years after the machinery or related product has been placed on the market or put into service.

**Applicability classification:**
Partially applicable / shared responsibility

**Applicability rationale:**
SRIO can generate and expose intervention-related diagnostic/log data (via IoTCore) and this origin function is testable at gateway level. However, no five-year (or any long-term) retention/archival mechanism is described in the source documents; Shared Flash is documented only as firmware/version storage, not as a log archive, so the retention obligation itself cannot currently be verified against gateway-level evidence and likely depends on an external logging/archival system managed by the manufacturer or operator.

**SRIO contribution:**
Generation of diagnostic/error-log data accessible via IoTCore (TARA-005).

**External dependencies:**
Long-term (five-year) log retention infrastructure (e.g., external log server, SIEM, or manufacturer record-keeping system) is not described as part of SRIO and is assumed to be a system/manufacturer-level responsibility.

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-03 | IoTCore service interface | Documented "error log" and diagnostics retrieval point (data origin) | TARA-005 | Medium |
| IF-05 | Shared Flash update path | Only persistent non-volatile storage medium described, though not documented as a log archive | — | Low |

**Gateway-level verification potential:**
Verify that intervention-related data is generated and retrievable via IoTCore in the short/medium term.

**Machine/system-level verification need:**
Verifying five-year retention requires an external archival system and record-keeping process that cannot be demonstrated by testing SRIO alone.

**Open assumptions or missing evidence:**
No retention/archival mechanism, storage capacity analysis, or data-export process is documented; it is unclear whether "the system" in this requirement refers to SRIO or to the complete machine's data-retention infrastructure.

---

### RQ-013

**Requirement:**
The system shall enable a tracing log of the versions of safety software uploaded after the machinery or related product has been placed on the market or put into service, for five years after each upload.

**Applicability classification:**
Partially applicable / shared responsibility

**Applicability rationale:**
Analogous to RQ-012: SRIO documents a firmware update workflow (IoTCore) and version-information storage (Shared Flash), which can serve as the origin of upload/version records, but no five-year retention mechanism is evidenced, and long-term retention likely depends on an external system.

**SRIO contribution:**
Firmware update handling via IoTCore (TARA-006); version information storage in Shared Flash (TARA-015).

**External dependencies:**
Long-term retention/archival of upload records beyond the gateway's own operational lifetime/storage capacity.

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-03 | IoTCore service interface | Firmware update workflow (upload event origin) | TARA-006 | Medium |
| IF-05 | Shared Flash update path | Version information storage | TARA-015 | Medium |

**Gateway-level verification potential:**
Verify that each firmware upload event and its version are recorded at the time of upload.

**Machine/system-level verification need:**
Five-year, per-upload retention cannot be demonstrated by testing SRIO alone; requires an external record-keeping system.

**Open assumptions or missing evidence:**
No information on log/version-record storage capacity or lifecycle (e.g., overwrite behavior) is provided in the source documents.

---

### RQ-014

**Requirement:**
The system shall restrict access to the tracing log data exclusively to demonstrating conformity further to a reasoned request from a competent national authority.

**Applicability classification:**
Partially applicable / shared responsibility

**Applicability rationale:**
SRIO can implement technical access control/authentication on its own diagnostic/log-exposing interface (IoTCore), which is testable at gateway level. However, the specific organizational constraint that access be granted *exclusively* "further to a reasoned request from a competent national authority" is a process/legal control over *who* is granted access and *why* — this is a manufacturer-level compliance/process obligation that cannot be verified purely by testing the gateway's technical access-control mechanism.

**SRIO contribution:**
IoTCore endpoint authentication/authorization mechanism restricting who can query diagnostics/log data (TARA-005, TARA-007).

**External dependencies:**
The manufacturer's process for handling and validating "reasoned requests from a competent national authority" and granting access accordingly is an organizational/legal process outside SRIO's technical scope.

**Mapped SRIO interfaces/assets:**

| Interface ID | Interface name | Mapping rationale | Related TARA IDs | Mapping confidence |
|--------------|----------------|--------------------|-------------------|---------------------|
| IF-03 | IoTCore service interface | Only documented interface exposing diagnostic/log data and gating service-function access | TARA-005, TARA-007 | Medium |

**Gateway-level verification potential:**
Verify that IoTCore enforces authentication/authorization before exposing log/diagnostic data, and that no anonymous/unauthenticated access path exists.

**Machine/system-level verification need:**
Verifying that access is granted *only* in response to an authority's reasoned request is an organizational/process control that must be assessed at the manufacturer's compliance-process level, not through gateway testing.

**Open assumptions or missing evidence:**
No process documentation for handling authority requests is provided; it is unclear whether any such organizational process currently exists.
