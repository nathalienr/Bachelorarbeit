# Step 3 — Two-Level Test Catalog
## Level 1: Abstract Test Scenarios (Product-Neutral)

**Scope of this iteration:** Level 1 only. Level 2 (concrete execution: hardware, IP plan, tools, commands, evidence artefacts) is deliberately omitted pending finalisation of the Hardware-in-the-Loop environment.

### Conventions
- **ID scheme:** `TC-<RQ number>-<letter>` (e.g., `TC-001-A`). Letters follow the Step-2 scenario order.
- **Product neutrality:** Scenarios reference *functions and protocol behaviours* (safe channel, watchdog, integrity-check value, audit log, identification interface, firmware update package), never specific IP addresses, tools, commands, or model identifiers.
- **Traceability:** `RQ → CR (→ supporting standard) → Asset`. CRs are IEC 62443-4-2 component requirements reached via DIN EN 50742 Approach B.
- **Target Threat:** STRIDE class under test. Functional/availability verifications carry `N/A — functional verification` because STRIDE is an adversarial taxonomy applied at requirement level.
- **SVV Category:** IEC 62443-4-1 — SVV-1 (requirements-based), SVV-2 (threat-mitigation), SVV-3 (vulnerability), SVV-4 (penetration).
- **Cross-references** (`⇄`) indicate a scenario that reuses, or imports the outcome of, another test case to avoid duplication.

---

## RQ-001 — Connection of a device must not create a hazard

### TC-001-A — Baseline Safety Exchange
- **Traceability:** RQ-001 → CR 3.1 / CR 3.6 → Asset A, Asset C
- **Target Threat:** N/A — functional verification (reference baseline)
- **SVV Category:** SVV-1
- **Objective:** Demonstrate that, under a correctly configured safety destination address and valid integrity-check value, the safe consumer exchanges cyclic safety data, sets the process-data qualifier to *good*, and drives outputs strictly per the received control data.
- **Abstract Steps:**
  1. Configure the safety controller with a destination address matching the device.
  2. Establish the safety connection and bring the system to normal operating state.
  3. Toggle a safe input and a safe output via the controller.
  4. Observe process data, qualifiers, and integrity-check behaviour over a sustained interval.
- **Pass/Fail:** **PASS** if the qualifier remains *good* throughout, outputs mirror the commanded control data, and no passivation occurs under nominal conditions. **FAIL** if the qualifier becomes *bad*, or any output/command mismatch is observed.

### TC-001-B — Attack-Surface Enumeration on the Non-Safety Path
- **Traceability:** RQ-001 → CR 3.1 → Asset F
- **Target Threat:** Spoofing / Tampering (surface evidence)
- **SVV Category:** SVV-3
- **Objective:** Enumerate the services a connecting device can reach on the non-safety communication path and compare them against the approved architecture/port matrix, providing attack-surface evidence for the environmental residual risk.
- **Abstract Steps:**
  1. From the position of a connecting device, perform a full service/port discovery against the device.
  2. Perform service and version identification on any responding port.
  3. Compile the reachable-service list.
  4. Compare the list against the approved design matrix.
- **Pass/Fail:** **PASS** if only design-approved services are reachable. **FAIL** if any service outside the approved matrix is reachable. *(Confidentiality of an exposed service is recorded as a defence-in-depth observation, not scored here — EN 50742 FR4 target = none.)*

### TC-001-C — Codename / Integrity-Value Mismatch Rejection
- **Traceability:** RQ-001 → CR 3.1 (+RE1) / CR 3.6 → Asset A, Asset C
- **Target Threat:** Spoofing + Tampering
- **SVV Category:** SVV-4
- **Objective:** Prove that a safety telegram whose consumer identity / integrity-check value does not match the legitimate parameters is rejected, resolving to the safe state rather than to an uncommanded output.
- **Abstract Steps:**
  1. With cyclic safety traffic running, inject crafted telegrams that violate the consumer identity or the integrity-check value (mis-addressed telegram; bit-flipped payload/integrity value).
  2. Observe the qualifier, output state, and diagnostics.
- **Pass/Fail:** **PASS** if the device rejects the crafted telegrams and either continues on legitimate traffic or passivates to the safe state (outputs de-energised, qualifier *bad*), with no uncommanded actuation. **FAIL** if any crafted telegram causes an uncommanded or hazardous output change.

### TC-001-D — In-Path Adversary-in-the-Middle Boundary
- **Traceability:** RQ-001 → CR 3.1 (+RE1) → Asset C, Asset F
- **Target Threat:** Spoofing + Tampering (Adversary-in-the-Middle)
- **SVV Category:** SVV-4
- **Objective:** Characterise the true residual boundary of the authenticity mitigation: because authenticity ultimately rests on the black-channel assumption, determine whether an in-path adversary that suppresses the legitimate producer and assumes control of the consecutive-number sequence can present a telegram the consumer cannot distinguish from a legitimate one.
- **Abstract Steps:**
  1. Insert a controlled in-path element between the legitimate producer and the safe consumer.
  2. Suppress the legitimate producer's telegrams.
  3. Continue the consecutive-number sequence and inject a fully valid-integrity telegram carrying modified process data.
  4. Observe whether the consumer accepts the substituted stream or detects the takeover.
- **Pass/Fail:** *Boundary-characterisation test (not scored as a device FAIL).* **Expected:** a full in-path takeover is accepted, demonstrating that authenticity depends on the black-channel/environmental assumption; this is documented as a residual risk covered by the network-segregation control. **A device FAIL is recorded only if** a *parallel* (non-in-path) injection — without producer suppression — is accepted, which would indicate a genuine consumer-side defect.

### TC-001-E — Channel-Disruption Watchdog Response
- **Traceability:** RQ-001 → CR 3.1 / CR 3.6 → Asset A, Asset C, Asset E
- **Target Threat:** Denial of Service
- **SVV Category:** SVV-2
- **Objective:** Verify that interruption of the safe channel beyond the watchdog time causes passivation to the defined safe state, and that re-integration requires explicit acknowledgement — i.e., a connection-induced disruption resolves to a safe, not hazardous, state.
- **Abstract Steps:**
  1. Reach normal operating state with a known watchdog time.
  2. Interrupt the safe-communication path for longer than the watchdog time.
  3. Measure the time to reach the safe state; confirm outputs de-energised and qualifier *bad*.
  4. Restore the link; confirm no automatic re-integration occurs without acknowledgement.
- **Pass/Fail:** **PASS** if passivation occurs within the specified device response time, outputs are de-energised, the qualifier is *bad*, and re-integration is gated by acknowledgement. **FAIL** if outputs remain energised beyond the watchdog time, or the device auto-re-integrates without acknowledgement.

---

## RQ-002 — Protect hardware transmitting connection/safety data from corruption

### TC-002-A — Parameter Integrity-Value Rejection
- **Traceability:** RQ-002 → CR 3.4 → Asset C (configuration at rest)
- **Target Threat:** Tampering
- **SVV Category:** SVV-1
- **Objective:** Demonstrate that the device validates the safety parameter set and rejects a configuration whose parameter integrity values do not match, remaining in the safe (parametrisation) state.
- **Abstract Steps:**
  1. Establish a valid baseline configuration.
  2. Present a configuration whose parameter integrity value is deliberately incorrect.
  3. Observe device state, diagnostics, and qualifiers.
- **Pass/Fail:** **PASS** if the mismatch triggers a configuration error, the device remains in the safe/parametrisation state, qualifiers remain *bad*, and no operating handshake completes. **FAIL** if a configuration with a mismatched integrity value is accepted.

### TC-002-B — Stale Integrity-Value Fault Detection
- **Traceability:** RQ-002 → CR 3.1 → Asset C
- **Target Threat:** Tampering (fault condition)
- **SVV Category:** SVV-2
- **Objective:** Verify the effectiveness of the transmission integrity-check countermeasure by modifying payload while leaving the integrity value stale, producing a detectable mismatch that resolves to passivation.
- **Abstract Steps:**
  1. Establish cyclic safety traffic.
  2. Modify a payload field while leaving the integrity value unchanged.
  3. Observe detection and the resulting device state.
- **Pass/Fail:** **PASS** if the mismatch is detected and the device passivates (outputs de-energised, qualifier *bad*) or continues on legitimate traffic without acting on the corrupted data. **FAIL** if the modified payload is acted upon.

### TC-002-C — Valid-Integrity-Value Injection over Modified Data
- **Traceability:** RQ-002 → CR 3.1 (+RE1) → Asset C
- **Target Threat:** Tampering
- **SVV Category:** SVV-4
- **Objective:** Demonstrate the central residual risk: because the transmission integrity value is a non-secret checksum (not a cryptographic MAC), an attacker who modifies the process data and recomputes a matching integrity value produces a telegram the consumer cannot distinguish from a legitimate one — protection against accidental but not intentional corruption.
- **Abstract Steps:**
  1. Capture a legitimate telegram and extract the parameters needed to reproduce the integrity value.
  2. Modify the process data.
  3. Recompute a valid integrity value over the modified data.
  4. Inject and observe the qualifier and outputs.
- **Pass/Fail:** *Gap-characterisation test.* **Expected:** the recomputed-integrity telegram is accepted, confirming that authenticity depends on the black channel (residual risk documented). A **positive finding** (rejection) would indicate an undocumented cryptographic authenticity control and must be investigated.

### TC-002-D — Parameter-Integrity Forgeability Assessment
- **Traceability:** RQ-002 → CR 3.4 → Asset C
- **Target Threat:** Tampering (analytical)
- **SVV Category:** SVV-3
- **Objective:** Establish, by keyspace/analytical argument, that the parameter integrity values provide no forgery resistance: the shorter parameter integrity value occupies a trivially searchable space, and the longer one is deterministically recomputable from the public parameter layout.
- **Abstract Steps:**
  1. Determine the bit-length and algorithm class of each parameter integrity value from documentation.
  2. Argue the computational feasibility of forging each (search space vs. deterministic recomputation).
  3. Conclude on cryptographic forgery resistance.
- **Pass/Fail:** *Analytical finding.* **Expected:** both parameter integrity values are forgeable (no cryptographic resistance), confirming they are error-detection, not authentication, mechanisms. *(This is a keyspace analysis, not a network-fuzzing exercise.)*

### TC-002-E — Physical Tamper-Resistance of the Address/Mode Interface
- **Traceability:** RQ-002 → EDR 3.11 (resistance limb) → Asset G
- **Target Threat:** Tampering
- **SVV Category:** SVV-4
- **Objective:** Assess the protection against physical corruption of the safety address/mode interface: (a) confirm the temporal protection (a runtime change is ignored until restart, so the running safety address cannot be corrupted live), and (b) determine whether the stored/next-restart value can be corrupted by physically altering the interface, with the seal as the only resisting barrier. *Whether the intervention is recorded is assessed separately under RQ-003.*
- **Abstract Steps:**
  1. Record the baseline address and seal state.
  2. In normal operating state, defeat the physical seal and alter the interface; verify the running address is unchanged.
  3. Perform a cold restart; confirm whether the altered value now takes effect.
  4. Assess whether the alteration required visible seal damage.
- **Pass/Fail:** *Gap-characterisation test.* **Expected:** (i) runtime change ignored (temporal protection = a genuine partial mitigation to credit); (ii) after restart the altered value applies → the stored value is physically corruptible; (iii) the only resistance is the passive seal, with no active tamper-detection/response → confirms resistance-only physical protection (partial EDR 3.11 result).

---

## RQ-003 — Collect evidence of intervention in hardware components

### TC-003-A — Baseline: Evidence Actually Collected
- **Traceability:** RQ-003 → CR 2.8 / CR 6.1 → Asset I
- **Target Threat:** Repudiation
- **SVV Category:** SVV-1
- **Objective:** Establish which intervention-evidence mechanisms exist and are readable (audit/error log; the parameter-change counter; the configuration signature), confirming that audit accessibility is met while characterising the content's limitations.
- **Abstract Steps:**
  1. Read the audit log and the identity/configuration records at a known-good baseline.
  2. Perform one authorised parameter change.
  3. Re-read; confirm the change counter incremented and the configuration signature changed.
  4. Inspect each record for the presence of actor identity and absolute timestamp.
- **Pass/Fail:** **PASS** if the log and records are readable and the change is reflected (accessibility + partial auditability confirmed). **Documented shortfall** if no record carries an actor identity or an absolute timestamp.

### TC-003-B — Authorised Intervention Evidence Under Normal Use
- **Traceability:** RQ-003 → CR 2.8 / CR 2.11 → Asset I, Asset G
- **Target Threat:** Repudiation
- **SVV Category:** SVV-2
- **Objective:** Determine whether an authorised address/parameter change followed by a restart generates any retained, time-referenceable evidence of the intervention.
- **Abstract Steps:**
  1. Baseline the evidence stores.
  2. Perform an authorised address/parameter change and restart.
  3. Re-read the evidence stores.
  4. Assess retention and time-referenceability of any generated record.
- **Pass/Fail:** **PASS** if a retained, time-referenceable record of the intervention exists after restart. **Expected shortfall:** evidence detail is not retained/time-referenceable across the restart (feeds the retention and timestamp gaps).

### TC-003-C — Illegitimate Physical Intervention & Anti-Forensic Clearing
- **Traceability:** RQ-003 → EDR 3.11 (detection) / CR 2.8 / CR 3.9 → Asset G, Asset I
- **Target Threat:** Repudiation
- **SVV Category:** SVV-4
- **Objective:** Demonstrate that (a) a physical intervention avoiding visible seal damage produces no automatic tamper record and no attribution, and (b) a subsequent cold start clears any incidental log content — proving the device cannot collect retained, protected evidence of the intervention.
- **Abstract Steps:**
  1. Capture the baseline log, records, and address.
  2. Defeat the seal carefully; alter the interface (including entry into a special mode); note any live status change.
  3. Cold-restart to apply the change.
  4. Re-read the log; check for any tamper/intervention entry and whether the log survived the restart.
  5. Assess attribution and timing of anything found.
- **Pass/Fail:** *Gap-characterisation test.* **Expected:** no tamper-specific entry; incidental entries lost on cold start; no actor identity and no absolute timestamp → confirms the missing-detection and unprotected-evidence gaps → **FAIL against RQ-003**. A persistent, attributed, time-stamped tamper record would indicate an undocumented capability (investigate).

### TC-003-D — Time-Attribution Failure of Collected Evidence
- **Traceability:** RQ-003 → CR 2.11 / CR 3.9 → Asset I
- **Target Threat:** Repudiation
- **SVV Category:** SVV-3
- **Objective:** Demonstrate that even the evidence the device does record cannot be placed in absolute time: the device exposes only an uptime reference that resets on cold start, with no synchronised real-time clock, so interventions separated by a power cycle cannot be temporally ordered or dated.
- **Abstract Steps:**
  1. Generate a loggable event; read the uptime reference and the log entry.
  2. Cold-restart.
  3. Generate a second event; read the uptime reference again.
  4. Compare: show the time base reset and the absence of any absolute timestamp.
- **Pass/Fail:** **PASS** if entries carry a retained absolute timestamp enabling cross-restart ordering. **Expected FAIL:** the time base resets and no absolute timestamp is attached → evidence is not time-referenceable (CR 2.11 unmet).

### TC-003-E — Excluded (Development-Only) Interface Produces No Evidence
- **Traceability:** RQ-003 → EDR 2.13 → Asset G, Asset I
- **Target Threat:** Repudiation
- **SVV Category:** SVV-3
- **Objective:** Validate the compensating exclusion of the development/diagnostic interface: confirm that the production-gated diagnostic function is rejected on a production unit, and that exercising the excluded interface generates no log entry — so an intervention at this interface leaves no evidence.
- **Abstract Steps:**
  1. On a production-configured unit, attempt to invoke the production-gated diagnostic/test function.
  2. Confirm rejection.
  3. Inspect the audit log for any entry corresponding to the attempt.
- **Pass/Fail:** **PASS (exclusion valid)** if the function is rejected on the production unit. **Documented gap:** the excluded interface produces no evidence, so RQ-003's "evidence of any intervention" is unmet at this interface. *Limitation: a true hardware-fuse claim is not verifiable without invasive physical analysis and is out of scope; only the functional gate is tested.*

---

## RQ-004 — Identify software AND data critical for EHSR compliance

### TC-004-A — Identification-Surface Inventory (Software + Data)
- **Traceability:** RQ-004 → CR 7.8 → Asset D (software) + Asset B (data via configuration signature)
- **Target Threat:** Information Disclosure
- **SVV Category:** SVV-1
- **Objective:** Enumerate the complete identification set the device exposes; confirm it identifies safety software (firmware/bootloader/stack versions) and safety data (the configuration signature); diff against the expected EHSR-critical software+data set to reveal the completeness gap.
- **Abstract Steps:**
  1. Retrieve all device software version fields via the identification interface.
  2. Retrieve the identity and configuration-signature records via the fieldbus acyclic identity records.
  3. Retrieve the firmware and communication-stack version fields.
  4. Compile the inventory and compare against the expected set, including third-party components.
- **Pass/Fail:** **PASS (partial-conformance baseline)** if the device returns top-level software identification and a data-identification signature. **Documented shortfall** if no software bill of materials of third-party components is present and no explicit safety-critical-data classification is exposed.

### TC-004-B — Software-Bill-of-Materials Completeness & Third-Party Vulnerability Correlation
- **Traceability:** RQ-004 → CR 7.8 (SBOM limb) / 62443-4-1 SM-9–SM-10 → Asset D
- **Target Threat:** Information Disclosure
- **SVV Category:** SVV-3
- **Objective:** Demonstrate that the exposed inventory is top-level only and provides no bill of materials for the safety-critical third-party components (real-time OS, safety-protocol stack, processor self-test library, communication stack), so their versions cannot be enumerated or vulnerability-correlated — CR 7.8 met at product granularity but not at component granularity.
- **Abstract Steps:**
  1. From TC-004-A, list all device-exposed version strings.
  2. From documentation, list the known constituent third-party components.
  3. Attempt to derive each component's version from any exposed interface.
  4. For derivable versions, correlate against a vulnerability database; record the remainder as un-inventoried.
- **Pass/Fail:** **Expected FAIL:** third-party components are not individually exposed and no bill of materials exists → confirms the completeness gap; documented as a CR 7.8 shortfall requiring a machine-readable SBOM.

### TC-004-C — Plaintext Exposure of Identification Data (Defence-in-Depth Observation)
- **Traceability:** RQ-004 → CR 4.1 (observation only) → Asset D
- **Target Threat:** Information Disclosure
- **SVV Category:** SVV-3
- **Objective:** Confirm that identification data is served without transport encryption and can be observed passively on the segment. *Under EN 50742 Approach B (FR4 target = none) this is recorded as a defence-in-depth observation, not a conformance FAIL.*
- **Abstract Steps:**
  1. Trigger a legitimate identification read.
  2. Passively observe the exchange.
  3. Confirm the identification content is recoverable in cleartext and that no encrypted transport option exists.
- **Pass/Fail:** *Observation only.* **Expected:** cleartext recoverable, no encrypted transport. Recorded as a defence-in-depth note; not scored as a safety-security FAIL.

### TC-004-D — Data-Identification Signature Uniqueness
- **Traceability:** RQ-004 → CR 7.8 (data limb) → Asset B
- **Target Threat:** N/A — functional identification
- **SVV Category:** SVV-1
- **Objective:** Confirm that safety data is identified: the configuration signature uniquely characterises the loaded safety configuration, so different configurations yield different signatures — establishing that data is identified (as a fingerprint), correcting the "data not addressed" premise.
- **Abstract Steps:**
  1. Load configuration A; read the configuration signature.
  2. Load a materially different configuration B; read the configuration signature.
  3. Confirm the two signatures differ and each uniquely maps to its configuration.
- **Pass/Fail:** **PASS** if distinct configurations produce distinct signatures (data identified via fingerprint). **Documented limitation:** the signature identifies *that* a specific configuration is loaded but does not enumerate/classify *which* data elements are EHSR-critical (residual gap).

---

## RQ-005 — Protect identified safety software and data from corruption

### TC-005-A — Parameter Integrity-Value Rejection ⇄ TC-002-A
- **Traceability:** RQ-005 → CR 3.4 → Asset B
- **Target Threat:** Tampering
- **SVV Category:** SVV-1
- **Objective:** Verify (by reference to TC-002-A) that a configuration with a mismatched parameter integrity value is rejected, remaining in the safe state.
- **Abstract Steps:** Execute per TC-002-A; record the result against RQ-005 traceability.
- **Pass/Fail:** As TC-002-A. **PASS** on rejection of the mismatched configuration.

### TC-005-B — Valid-Integrity Forgery over Modified Parameters
- **Traceability:** RQ-005 → CR 3.4 → Asset B
- **Target Threat:** Tampering
- **SVV Category:** SVV-4
- **Objective:** Demonstrate that because the parameter integrity values are non-secret checksums, an attacker who modifies the safety parameter set and recomputes matching integrity values produces a configuration the safety CPU accepts — protection against accidental but not intentional corruption.
- **Abstract Steps:**
  1. Capture/derive a legitimate parameter record and its integrity block.
  2. Modify a safety-relevant parameter.
  3. Recompute the parameter integrity values.
  4. Present the forged configuration; observe whether the device accepts it or raises a configuration error.
- **Pass/Fail:** *Gap-characterisation test.* **Expected:** the forged configuration is accepted, confirming that the parameter integrity values are not authentication. A rejection would indicate an undocumented cryptographic control (investigate).

### TC-005-C — Unsigned / Modified Firmware Installation
- **Traceability:** RQ-005 → EDR 3.10 / EDR 3.14 (→ EDR 3.12/3.13) → Asset D, Asset F
- **Target Threat:** Tampering + Spoofing
- **SVV Category:** SVV-4
- **Objective:** Demonstrate that the firmware-update mechanism installs an update without cryptographic authenticity/integrity verification: a modified/unsigned firmware package is accepted for installation — proving the intentional-corruption protection for the safety firmware is absent (only environmental and mode-gate barriers remain). *This is the decisive gap of the requirement set.*
- **Abstract Steps:**
  1. Place a spare unit into the update state (operational precondition; the mode gate's authorisation is tested under RQ-011).
  2. Take a legitimate update package and modify a byte, or strip/forge any signature/header.
  3. Upload via the update service and invoke installation.
  4. Observe whether the device verifies the package before installation (rejects) or proceeds.
- **Pass/Fail:** **PASS against the requirement iff** the modified/unsigned package is rejected by a signature/integrity check before installation. **Expected FAIL:** the package is accepted for installation → EDR 3.10/3.14 unmet. *Safety: spare unit only; re-flash a validated image afterwards.*

### TC-005-D — Update-Package Static Analysis for Signing / Boot-Chain Artefacts
- **Traceability:** RQ-005 → EDR 3.12 / EDR 3.14 → Asset D
- **Target Threat:** Tampering (analysis)
- **SVV Category:** SVV-3
- **Objective:** Characterise the absence of signing and secure-boot artefacts by static analysis of the update package (header structure, signature region, binary-hardening posture).
- **Abstract Steps:**
  1. Obtain the legitimate update package.
  2. Statically inspect its structure for a signature/header and trust-anchor references.
  3. Assess the binary-hardening posture of the contained image.
  4. Record the presence/absence of each artefact.
- **Pass/Fail:** **Expected:** no signature/trust-anchor artefacts present, consistent with an unsigned package → supports the firmware-authenticity gap.

### TC-005-E — Analytical: Safety Self-Tests ≠ Authenticity
- **Traceability:** RQ-005 → CR 3.3 → Asset A, Asset D
- **Target Threat:** N/A — architectural analysis
- **SVV Category:** SVV-1
- **Objective:** Establish, analytically, why the dual-channel cross-check and the processor self-test library cannot detect a coherent malicious modification applied identically to both channels — a systematic change on which both channels still agree — and therefore provide no security authenticity. Cross-references the empirical proof in TC-005-C.
- **Abstract Steps:**
  1. Describe the fault model of the safety self-tests (random, independent hardware faults; channel divergence).
  2. Describe the attack model (coherent, identical modification of both channels).
  3. Argue that the two are disjoint; conclude that only a signed-image/secure-boot mechanism would detect the latter.
- **Pass/Fail:** *Analytical finding.* Substantiates that integrity-of-execution (safety) does not provide authenticity (security); no lab exploit required beyond TC-005-C.

---

## RQ-006 — Identify installed software necessary for safe operation

### TC-006-A — Installed-Software Inventory Enumeration
- **Traceability:** RQ-006 → CR 7.8 → Asset D
- **Target Threat:** Information Disclosure (requirement level); test itself functional
- **SVV Category:** SVV-1
- **Objective:** Enumerate the complete set of installed-software identifiers and confirm coverage of the software necessary for safe operation (host firmware, both bootloaders, safety-CPU firmware, safety-protocol stack); map each entry to the safety function it supports.
- **Abstract Steps:**
  1. Read all software-version and bootloader-version fields via the identification interface.
  2. Read the software-revision identity record and any annotation record.
  3. Read the firmware and communication-stack version fields.
  4. Assemble the inventory; map each entry to its supported safety function.
- **Pass/Fail:** **PASS (partial-conformance baseline) iff** host firmware, both bootloaders, safety-CPU firmware, and the safety-protocol stack version are all retrievable and mutually consistent. **Documented shortfall** where any safety-relevant installed component is not individually identified.

### TC-006-B — SBOM Completeness & Vulnerability Correlation ⇄ TC-004-B
- **Traceability:** RQ-006 → CR 7.8 (SBOM limb) / 62443-4-1 SM-9–SM-10 → Asset D
- **Target Threat:** Information Disclosure
- **SVV Category:** SVV-3
- **Objective:** By reference to TC-004-B, demonstrate that no bill of materials of the third-party constituents exists, so their versions cannot be enumerated or vulnerability-correlated — CR 7.8 met at product but not component granularity.
- **Abstract Steps:** Execute per TC-004-B; record against RQ-006 traceability. Do not re-derive.
- **Pass/Fail:** As TC-004-B. **Expected FAIL:** no component-level SBOM.

### TC-006-C — Plaintext Inventory Exposure (Defence-in-Depth Observation)
- **Traceability:** RQ-006 → CR 4.1 (observation only) → Asset D
- **Target Threat:** Information Disclosure
- **SVV Category:** SVV-3
- **Objective:** Confirm the inventory read is served without transport encryption. *Recorded as a defence-in-depth observation (EN 50742 FR4 target = none), not a conformance FAIL.*
- **Abstract Steps:** Trigger an inventory read; passively observe; confirm cleartext and no encrypted transport option.
- **Pass/Fail:** *Observation only.* Documented as defence-in-depth; not scored.

---

## RQ-007 — Provide safety-software identification at all times, easily accessible

### TC-007-A — Identification Availability & Accessibility Baseline
- **Traceability:** RQ-007 → CR 7.8 / CR 6.1 → Asset H, Asset D
- **Target Threat:** N/A — functional/accessibility verification
- **SVV Category:** SVV-1
- **Objective:** Confirm that, in normal operating state, the safety-relevant installed-software identification is retrievable and presented in an easily accessible form (browser-based visualiser + human-readable version strings), establishing the availability baseline.
- **Abstract Steps:**
  1. In normal operating state, open the device's browser-based information interface.
  2. Retrieve all safety-relevant software identifiers.
  3. Confirm values are human-readable and the interface renders without special tooling.
- **Pass/Fail:** **PASS** if the interface loads and all safety-relevant identifiers are shown in human-readable form. **FAIL** if any identifier is unreadable or the interface is inaccessible in normal operation.

### TC-007-B — Identification Availability Across Operating States
- **Traceability:** RQ-007 → CR 7.8 / FR 7 (availability) → Asset H, Asset D
- **Target Threat:** N/A — inherent unavailability (design/reliability)
- **SVV Category:** SVV-2
- **Objective:** Demonstrate that identification data is not available "at all times" by continuously polling while the device transitions through initialisation (power-cycle), update (including the install restart), and fatal-error safe-state, and by identifying the safety-CPU-flash window in which safety-sourced identifiers vanish.
- **Abstract Steps:**
  1. Start a timestamped polling loop against one gateway-sourced and one safety-sourced identifier.
  2. Power-cycle the device (initialisation window).
  3. Enter the update state and trigger the install restart.
  4. Force the fatal-error safe-state.
  5. Record every interval where the request fails or the safety-sourced value is absent.
- **Pass/Fail:** *Gap-characterisation test.* **Expected:** measurable outage windows during initialisation, install-restart, and fatal-error; and unavailability of safety-sourced identifiers during the flash window → confirms the "at all times" gap → **FAIL** against that clause. Continuous availability through all states would refute the gap (investigate).

### TC-007-C — Connection-Hold Self-Denial-of-Service on the Identification Interface
- **Traceability:** RQ-007 → CR 7.1 / CR 7.2 → Asset H
- **Target Threat:** Denial of Service (self-inflicted)
- **SVV Category:** SVV-4
- **Objective:** Demonstrate that the concurrent-connection limit, intended as denial-of-service protection, is itself a denial-of-service vector: holding the maximum permitted connections exhausts the pool and blocks all further legitimate access to the identification interface, defeating "at all times" without any bandwidth-based flooding.
- **Abstract Steps:**
  1. In normal operating state, open and hold the maximum number of permitted connections (no completion / slow read).
  2. From an additional client, attempt a legitimate identification read.
  3. Measure whether the additional request is refused or times out.
  4. Release one held connection; confirm access is restored.
- **Pass/Fail:** **PASS against the requirement iff** a legitimate additional read still succeeds while the maximum connections are held. **Expected FAIL:** the additional request is blocked, and access returns only after release → confirms the self-inflicted availability failure.

### TC-007-D — Availability Inversion under Gateway/Internal-Comms Interruption
- **Traceability:** RQ-007 → CR 7.2 → Asset H, Asset F
- **Target Threat:** N/A — reliability/redundancy
- **SVV Category:** SVV-3
- **Objective:** Demonstrate that a fault or internal-communication timeout in the non-safety gateway removes identification availability entirely while the safety function persists, so identification is structurally less available than the safety function it describes.
- **Abstract Steps:**
  1. Establish normal operation with identification available.
  2. Induce a gateway or internal-communication interruption.
  3. Confirm the safety function persists (safe I/O behaviour unaffected).
  4. Confirm identification becomes unavailable during the interruption.
- **Pass/Fail:** *Gap-characterisation test.* **Expected:** identification unavailable while the safety function persists → confirms the no-redundancy gap (availability inversion).

---

## RQ-008 — Collect evidence of intervention in installed software

### TC-008-A — Software-Event Evidence Baseline
- **Traceability:** RQ-008 → CR 2.8 / CR 6.1 → Asset I, Asset D
- **Target Threat:** Repudiation
- **SVV Category:** SVV-1
- **Objective:** Establish which software-intervention evidence the device produces and whether it is readable (audit/error log; firmware version; software-revision identity record), and inspect each for actor identity and absolute timestamp. *Configuration markers are out of scope → RQ-009.*
- **Abstract Steps:**
  1. Read the error log and firmware/software-revision records at a known-good baseline.
  2. Trigger a benign self-detected software event.
  3. Re-read; confirm an audit entry appears.
  4. Inspect the entry for identity and absolute timestamp.
- **Pass/Fail:** **PASS** if the log and software records are readable and the induced event is captured. **Documented shortfall** if no entry carries actor identity or absolute timestamp.

### TC-008-B — Self-Erasing Firmware Install
- **Traceability:** RQ-008 → CR 3.9 / CR 2.11 → Asset I, Asset D
- **Target Threat:** Repudiation (+ Tampering)
- **SVV Category:** SVV-2
- **Objective:** Demonstrate that a legitimate firmware install destroys its own evidence: the install restart (and the mandatory update-exit power reset) triggers a cold start that clears the audit log and resets the uptime reference, so no retained, time-stamped record of the software intervention survives.
- **Abstract Steps:**
  1. Baseline the audit log and uptime reference.
  2. Perform an authorised firmware update (enter update state, upload, install).
  3. After the install restart, re-read the audit log and uptime reference.
  4. Determine whether any persistent, time-stamped record of the install remains.
- **Pass/Fail:** *Gap-characterisation test.* **Expected:** post-install log cleared and uptime reset → the install has erased its own evidence → **FAIL** against RQ-008. A retained, time-stamped install record would refute the gap (investigate).

### TC-008-C — Legitimate vs Illegitimate: Evidence Cannot Classify
- **Traceability:** RQ-008 → CR 2.8 (classification intent) → Asset D, Asset I, Asset F
- **Target Threat:** Repudiation
- **SVV Category:** SVV-4
- **Objective:** Demonstrate that the evidence record cannot distinguish a legitimate update from an illegitimate one: installing a modified/unsigned image (installation performed per TC-005-C) produces the same audit/version footprint as a genuine update, so the "legitimate OR illegitimate" evidence obligation is unmet. *The cause — no signature verification — is RQ-005's protection gap; RQ-008 tests only the evidence footprint.*
- **Abstract Steps:**
  1. Record the evidence delta of a legitimate update (from TC-008-B).
  2. On a spare unit, install the modified/unsigned image per TC-005-C.
  3. Record its evidence delta (log entries, version change, any classification flag).
  4. Compare: determine whether any evidence field marks the second install as illegitimate/unauthorised.
- **Pass/Fail:** *Gap-characterisation test.* **Expected:** the illegitimate install produces an indistinguishable footprint (same completion semantics + version change, no authenticity flag) → confirms the classification gap → **FAIL**. Any field flagging the unsigned image as illegitimate would refute the gap (record as a positive finding).

### TC-008-D — Time-Attribution across the Install Cold Start ⇄ TC-003-D
- **Traceability:** RQ-008 → CR 2.11 / CR 3.9 → Asset I
- **Target Threat:** Repudiation
- **SVV Category:** SVV-3
- **Objective:** By reference to the TC-003-D method, demonstrate that the install cold start resets the uptime reference and that no absolute timestamp is attached to either the pre- or post-install state.
- **Abstract Steps:** Execute the TC-003-D method around a firmware install; record against RQ-008 traceability.
- **Pass/Fail:** **Expected:** uptime resets, no absolute timestamp on the install event → CR 2.11 unmet.

### TC-008-E — Excluded (Development-Only) Interface Produces No Evidence ⇄ TC-003-E
- **Traceability:** RQ-008 → EDR 2.13 → Asset D, Asset I
- **Target Threat:** Repudiation
- **SVV Category:** SVV-3
- **Objective:** By reference to TC-003-E, confirm the production-gated diagnostic path is rejected on a production unit and that exercising the excluded interface produces no log entry.
- **Abstract Steps:** Execute per TC-003-E; record against RQ-008.
- **Pass/Fail:** As TC-003-E. **Documented gap:** excluded interface produces no evidence. *Silicon-fuse verification remains out of scope.*

---

## RQ-009 — Collect evidence of modification of software or configuration

### TC-009-A — Config-Modification Evidence Surface Baseline
- **Traceability:** RQ-009 → CR 2.8 / CR 3.4 / CR 6.1 → Asset B, Asset I
- **Target Threat:** Repudiation
- **SVV Category:** SVV-1
- **Objective:** Establish which configuration-modification evidence mechanisms exist and are readable (the parameter-change counter, the configuration signature, and the audit log); inspect each for actor identity and absolute timestamp. *Firmware-modification evidence → RQ-008.*
- **Abstract Steps:**
  1. Read the audit log, the change counter, and the configuration signature at a known baseline.
  2. Record which fields carry identity/timestamp.
- **Pass/Fail:** **PASS (partial baseline) iff** config-modification indicators are readable. **Documented shortfall** where no field carries actor identity or absolute timestamp.

### TC-009-B — Config-Modification Evidence & Persistence Asymmetry
- **Traceability:** RQ-009 → CR 2.8 / CR 2.11 / CR 3.9 → Asset B, Asset I
- **Target Threat:** Repudiation
- **SVV Category:** SVV-2
- **Objective:** Demonstrate that a configuration modification (a) increments the change counter and changes the configuration signature, but (b) carries no timestamp and no device-side actor, and (c) empirically establish whether, after a cold start, the change counter persists (durable count) while the audit-log detail is cleared (volatile detail). *The counter-persistence property is verified here, not pre-asserted.*
- **Abstract Steps:**
  1. Baseline the change counter, configuration signature, audit log, and uptime.
  2. Perform an authorised parameter change.
  3. Re-read: confirm the counter incremented and the signature changed; check for any timestamp/actor.
  4. Cold-start.
  5. Re-read: determine whether the counter is retained while the audit log is cleared and uptime reset.
- **Pass/Fail:** *Gap-characterisation test.* **Expected:** counter increments and signature changes, no time/actor present; after cold start the counter's persistence is recorded empirically and the log detail is lost → confirms the who/when limitations (CR 2.11/3.9). The durable/volatile asymmetry is reported as measured, not assumed.

### TC-009-C — Actor Attribution Is Delegated, Not Device-Resident
- **Traceability:** RQ-009 → CR 2.12 → Asset B, Asset F
- **Target Threat:** Repudiation
- **SVV Category:** SVV-3
- **Objective:** Demonstrate that because configuration is authored at the engineering tool and pushed from the (access-controlled) controller over the fieldbus, the device holds no actor identity for a configuration modification — attribution, if it exists, resides in the controller/engineering project, not on the device. This bounds CR 2.12 as delegated, not implemented at component level.
- **Abstract Steps:**
  1. Perform an authorised configuration change from a known engineering-tool user.
  2. Inspect every device-side evidence field for any actor/identity attribute.
  3. Inspect the controller/engineering side for where the actor identity resides.
  4. Conclude where (if anywhere) non-repudiation is anchored.
- **Pass/Fail:** *Gap-characterisation test.* **Expected:** no device-side field carries an actor identity → CR 2.12 not met at the device; attribution only at the controller/engineering layer → confirms attribution is delegated. Documented as: device-level non-repudiation for configuration modification is architecturally delegated for this QM component.

### TC-009-D — Post-Configuration-Phase Write Gate
- **Traceability:** RQ-009 → CR 3.4 → Asset B
- **Target Threat:** Tampering
- **SVV Category:** SVV-3
- **Objective:** Validate the temporal write-gate: an attempt to write configuration records after the configuration phase has ended is rejected, and confirm whether the blocked attempt itself generates any evidence entry.
- **Abstract Steps:**
  1. Complete the configuration phase and reach operation.
  2. Attempt an acyclic configuration write after the configuration phase end.
  3. Observe rejection.
  4. Inspect the audit log for any entry corresponding to the blocked attempt.
- **Pass/Fail:** **PASS (write-gate valid)** if the post-phase write is rejected. **Documented observation:** whether a blocked attempt produces an evidence entry (expected: none).

### TC-009-E — Analytical: Change-Counter Wrap-Around Bounds the Evidence
- **Traceability:** RQ-009 → CR 2.9 → Asset I
- **Target Threat:** N/A — lifecycle analysis
- **SVV Category:** SVV-1
- **Objective:** Establish, analytically, that the fixed-width change counter wraps over the device's stated mission lifetime under frequent re-parameterisation, bounding the evidence it can represent. *Not lab-testable in reasonable time; handled as an analytical finding with a scoping rationale.*
- **Abstract Steps:**
  1. Determine the counter width and the stated mission lifetime.
  2. Estimate a plausible re-parameterisation rate.
  3. Argue whether wrap-around occurs within the lifetime and its evidentiary impact.
- **Pass/Fail:** *Analytical finding.* **Expected:** wrap-around is reachable within the mission lifetime → the counter provides bounded, not unbounded, modification evidence.

---

## RQ-010 — Withstand foreseeable malicious attempts without a hazardous situation

### TC-010-A — Baseline Resilience under Rated Conformant Load
- **Traceability:** RQ-010 → CR 7.1 / CR 7.2 → Asset A, Asset H
- **Target Threat:** N/A — functional baseline
- **SVV Category:** SVV-1
- **Objective:** Confirm stable operation and safe communication under the device's rated conformant network-load conditions, establishing the resilience baseline.
- **Abstract Steps:**
  1. Establish normal operating state.
  2. Apply network load up to the rated conformant-load class.
  3. Monitor safe communication, qualifier, and output state.
- **Pass/Fail:** **PASS** if safe communication and stable operation are maintained under rated conformant load. **FAIL** if the device loses safe communication or destabilises within rated load.

### TC-010-B — Network/Layer-2 Flood Resilience
- **Traceability:** RQ-010 → CR 7.1 (RE1) / CR 7.2 / CR 3.6 → Asset H, Asset A, Asset E, Asset F
- **Target Threat:** Denial of Service
- **SVV Category:** SVV-4
- **Objective:** Determine behaviour under a high-rate network flood: (a) maintain safe communication (conformant-load robustness), (b) passivate to the defined safe state, or (c) enter an undefined/hazardous state; and whether sustained flooding causes continuous forced passivation (availability impact).
- **Abstract Steps:**
  1. Establish normal operating state.
  2. Apply an escalating frame flood (unicast + broadcast).
  3. Continuously monitor qualifier, output state, and device state.
  4. Sustain the flood; measure recovery vs. continuous passivation.
  5. Stop; confirm acknowledged re-integration.
- **Pass/Fail:** **PASS** if the device maintains safe communication up to its rated limits and, beyond them, passivates to the safe state (outputs de-energised, qualifier *bad*) with no undefined/unsafe output. **FAIL** if any flood level produces an undefined or hazardous output state. *Continuous forced passivation under sustained flood is recorded as an availability finding.*

### TC-010-C — Protocol Fuzzing Robustness
- **Traceability:** RQ-010 → CR 3.5 / CR 3.7 / CR 3.6 → Asset H, Asset A, Asset E
- **Target Threat:** Tampering
- **SVV Category:** SVV-4
- **Objective:** Determine whether malformed fieldbus-discovery, safety-protocol, and web-interface inputs are safely rejected (input validation, error handling) or cause a crash/hang/undefined state — verifying the device "withstands" unexpected input without a hazardous condition.
- **Abstract Steps:**
  1. Establish normal operating state.
  2. Fuzz each interface with malformed inputs (discovery messages, safety-frame fields, web requests).
  3. Monitor for crash/hang/watchdog reset vs. safe rejection/passivation.
  4. Log every input that changes device state; root-cause each.
- **Pass/Fail:** **PASS** if all malformed inputs are safely rejected or resolve to passivation, with no crash into an undefined/hazardous state. **FAIL** if any malformed input causes a hang, an uncommanded output, or an unrecoverable state other than the defined safe state.

### TC-010-D — Application-Layer Flood & Domain-Separation Confirmation
- **Traceability:** RQ-010 → CR 7.2 / CR 5.1 → Asset F, Asset H
- **Target Threat:** Denial of Service
- **SVV Category:** SVV-3
- **Objective:** Apply an application-layer request flood to the non-safety interface and confirm the attack does not propagate to the safety path (domain separation holds).
- **Abstract Steps:**
  1. Establish normal operating state.
  2. Apply an application-layer request flood to the non-safety interface.
  3. Monitor the safety path (qualifier, outputs, safe communication) throughout.
- **Pass/Fail:** **PASS** if the safety path is unaffected (no passivation caused by, and no propagation of, the non-safety-path flood). **FAIL** if the non-safety-path flood degrades or disturbs the safety function.

### TC-010-E — Outcome-Verification Aggregation Harness
- **Traceability:** RQ-010 → CR 3.6 → Asset A, Asset E
- **Target Threat:** N/A — aggregate outcome check across all classes
- **SVV Category:** SVV-2
- **Objective:** For every attack — the RQ-010-owned flood (TC-010-B) and fuzz (TC-010-C), plus the cross-referenced connecting-device spoofing (TC-001-C/D) and unsigned-firmware install (TC-005-C) — positively verify the EHSR outcome: no attempt produces an uncommanded/unsafe output; the device continues safely or enters the defined safe state. Surface the one class (firmware) that escapes the fail-safe design.
- **Abstract Steps:**
  1. Provide independent readback of the safe outputs.
  2. For each attack case (owned + cross-referenced), sample output state and qualifier.
  3. Classify each outcome as {safe-continue, safe-passivate, hazardous}.
  4. Consolidate into an outcome matrix; flag any hazardous result.
- **Pass/Fail:** **PASS (RQ-010 met for that class) iff** every outcome is safe-continue or safe-passivate. **FAIL iff** any yields uncommanded/unsafe actuation. **Expected:** flood/fuzz/spoofing classes PASS (black channel + CR 3.6); the firmware-install class is the documented exception that can lead to hazard.

---

## RQ-011 — Prevent unauthorised modification of safety settings / learned rules

### TC-011-A — Read-Only Enforcement on the Non-Safety Interface
- **Traceability:** RQ-011 → CR 2.1 → Asset B
- **Target Threat:** Tampering
- **SVV Category:** SVV-1
- **Objective:** Confirm the design intent that safety-relevant parameters cannot be written via the non-safety information interface (read-only), so that interface is not an authorisation bypass. *(Positive control verification.)*
- **Abstract Steps:**
  1. Enumerate writable-looking endpoints on the information interface.
  2. Attempt writes to safety-relevant nodes.
  3. Confirm each is rejected / read-only.
- **Pass/Fail:** **PASS** if all safety-parameter write attempts via the information interface are refused. **FAIL** if any safety parameter is writable via that interface.

### TC-011-B — Unauthenticated Configuration-Protocol Factory Reset
- **Traceability:** RQ-011 → CR 1.2 / CR 2.1 → Asset G, Asset F, Asset B
- **Target Threat:** Spoofing + Elevation of Privilege
- **SVV Category:** SVV-4
- **Objective:** Determine whether a peer node can issue a fieldbus device-configuration set/reset (including reset-to-factory of communication parameters) without any credential and without touching the physical barrier, demonstrating that a connection-relevant setting can be modified by an unauthorised third party.
- **Abstract Steps:**
  1. Baseline the device's communication identity and operating state.
  2. From a peer node, issue a configuration identify, then a set (change communication identity) and a reset-to-factory.
  3. Observe whether the actions succeed without authentication.
  4. Observe the safety impact (loss of the safety connection → passivation).
  5. Attempt higher reset modes if supported.
- **Pass/Fail:** **PASS against the requirement iff** the set/reset requires authentication or is refused from an unauthorised node. **Expected FAIL:** the reset succeeds unauthenticated. **Bound:** the impact is on communication parameters (→ passivation), not silent safety-parameter modification.

### TC-011-C — Fieldbus Parameter Write Without Device-Side Authorisation
- **Traceability:** RQ-011 → CR 1.1 / CR 1.2 / CR 2.1 → Asset B, Asset F
- **Target Threat:** Tampering + Spoofing + Elevation of Privilege
- **SVV Category:** SVV-4
- **Objective:** Demonstrate that the device enforces no credential of its own on the fieldbus parameter-write path: an unauthorised node presenting a syntactically valid parameter record (correct destination address + valid parameter integrity values) during the configuration phase can write safety parameters — confirming authorisation is entirely delegated to the environment, not device-enforced.
- **Abstract Steps:**
  1. Observe the legitimate configuration sequence.
  2. From an unauthorised node (impersonating the controller or injecting during the configuration phase), present a modified parameter record with recomputed integrity values.
  3. Determine whether the device demands any authentication before accepting the write.
- **Pass/Fail:** **PASS against the requirement iff** the device requires authentication/authorisation before accepting a parameter write. **Expected FAIL:** the only checks are addressing + integrity values (no credential) → confirms authorisation is delegated. *The finding here is the absence of an authorisation credential, distinct from the integrity-value forgeability of TC-005-B.*

### TC-011-D — Firmware-Update Mode Gate
- **Traceability:** RQ-011 → EDR 3.10 / CR 2.1 → Asset G, Asset D
- **Target Threat:** Elevation of Privilege
- **SVV Category:** SVV-2
- **Objective:** Validate the update authorisation gate: an update attempt outside the update state is rejected, while an attempt in the update state is accepted — bounding the delegated-authorisation gap by confirming the mode gate operates.
- **Abstract Steps:**
  1. Attempt a firmware update while the device is not in the update state.
  2. Confirm rejection.
  3. Place the device in the update state and attempt again.
  4. Confirm acceptance of the (validated) update.
- **Pass/Fail:** **PASS** if the update is rejected outside the update state and accepted only in it. **FAIL** if an update can be initiated outside the update state.

### TC-011-E — Physical-Barrier Silent Defeat ⇄ TC-003-C / TC-002-E
- **Traceability:** RQ-011 → EDR 3.11 → Asset G, Asset B
- **Target Threat:** Tampering
- **SVV Category:** SVV-4
- **Objective:** By reference to TC-003-C / TC-002-E, confirm that the physical address/mode interface can be altered without visible seal damage and that the change applies after restart — the authorisation barrier's silent-defeat question.
- **Abstract Steps:** Execute per TC-003-C / TC-002-E; record against RQ-011 traceability.
- **Pass/Fail:** As referenced. **Expected:** the barrier can be silently defeated → confirms the physical-authorisation gap.

---

## RQ-012 — Five-year retention of the tracing log

### TC-012-A — Circular-Buffer Overflow / Capacity Conflict
- **Traceability:** RQ-012 → CR 2.9 / CR 2.10 → Asset I
- **Target Threat:** Repudiation
- **SVV Category:** SVV-2
- **Objective:** Demonstrate that the tracing log is a fixed-capacity circular buffer that overwrites oldest entries once full, so intervention data is not retained for any duration bounded by event volume — conflicting with the five-year mandate.
- **Abstract Steps:**
  1. Read and record the current log.
  2. Generate a controlled series exceeding the documented capacity, each event individually identifiable.
  3. Read the log after each block.
  4. Confirm the earliest events are overwritten and the buffer never exceeds its fixed size.
- **Pass/Fail:** **PASS against the requirement** if the log retains all events for the retention window. **Expected FAIL:** the buffer caps at its fixed size and overwrites oldest-first.

### TC-012-B — Cold-Start Deletion
- **Traceability:** RQ-012 → CR 3.9 / CR 2.9 → Asset I
- **Target Threat:** Repudiation (+ Tampering)
- **SVV Category:** SVV-2
- **Objective:** Demonstrate that a cold start clears the tracing log (intervention data does not persist across a power cycle). *The speculative warm-reset limb is dropped for lack of a documented log-preserving reset; any non-cold recovery is treated as exploratory.*
- **Abstract Steps:**
  1. Populate the log with identifiable entries.
  2. Apply a cold start (power cycle); read the log.
  3. Optionally exercise any documented non-cold recovery path and record whether entries survive (exploratory).
  4. Compare pre/post states.
- **Pass/Fail:** **PASS against the requirement** if entries persist across the reset. **Expected FAIL (cold start):** the log is cleared after cold start. Any non-cold-recovery result is recorded factually.

### TC-012-C — Mandated-Reboot Retention Impossibility
- **Traceability:** RQ-012 → CR 2.9 → Asset I
- **Target Threat:** N/A — lifecycle/documentation analysis
- **SVV Category:** SVV-1
- **Objective:** Establish that the device's own mandatory maximum reboot interval (required to test safety functions untestable at runtime) forces at least one cold start within the retention period, so the five-year on-device retention is structurally impossible, independent of any attack.
- **Abstract Steps:**
  1. Identify the mandated maximum reboot interval from documentation.
  2. Show that each mandated reboot is a cold start that clears the log (per TC-012-B).
  3. Conclude that the retention window cannot be sustained on-device.
- **Pass/Fail:** *Structural finding.* **Expected:** the mandated reboot guarantees periodic log erasure within the retention period → five-year on-device retention structurally impossible.

### TC-012-D — Time-Attribution of Retained Entries ⇄ TC-003-D
- **Traceability:** RQ-012 → CR 2.11 → Asset I
- **Target Threat:** Repudiation
- **SVV Category:** SVV-3
- **Objective:** By reference to TC-003-D, confirm that no retained entry carries an absolute timestamp, so even surviving entries cannot be bounded to a five-year window.
- **Abstract Steps:** Execute per TC-003-D; record against RQ-012.
- **Pass/Fail:** **Expected:** entries carry only a relative uptime reference, no absolute timestamp → retained fragment is undatable (compounds the capacity gap).

---

## RQ-013 — Five-year per-upload log of safety-software versions

### TC-013-A — Current-Version-Only Confirmation
- **Traceability:** RQ-013 → CR 2.9 → Asset I, Asset D
- **Target Threat:** Repudiation
- **SVV Category:** SVV-1
- **Objective:** Confirm that only the current version is exposed and that no historical or previous-version fields exist via the identification interface and identity records.
- **Abstract Steps:**
  1. Read all version fields via the identification interface.
  2. Read the version-bearing identity records.
  3. Search for any previous-version or upload-history field.
- **Pass/Fail:** **PASS against the requirement** if a queryable per-upload history is exposed. **Expected FAIL:** only the current version is reported; no history field exists.

### TC-013-B — Sequential-Upload Version-History Test
- **Traceability:** RQ-013 → CR 2.8 / CR 2.9 / CR 3.9 → Asset I, Asset D
- **Target Threat:** Repudiation
- **SVV Category:** SVV-2
- **Objective:** Demonstrate that the device retains no historical, per-upload record of previously uploaded safety-software versions: after uploading a new version over the current one, no device-resident field reports that the previous version was ever installed. *Self-erasing install mechanics are cross-referenced to RQ-008; this test targets version-history existence.*
- **Abstract Steps:**
  1. Record the current version and all version fields.
  2. Upload a new version; after install, read all version fields.
  3. Search for any device-resident record of the previous version.
  4. Upload a further version; repeat the search for both prior versions.
- **Pass/Fail:** **PASS against the requirement** if the device retains a queryable per-upload history including previous versions. **Expected FAIL:** only the current version is reported; no record of prior uploads persists.

### TC-013-C — Per-Upload Timestamp Absence ⇄ TC-003-D
- **Traceability:** RQ-013 → CR 2.11 / CR 3.9 → Asset I
- **Target Threat:** Repudiation
- **SVV Category:** SVV-3
- **Objective:** Demonstrate that a firmware upload carries no absolute per-upload timestamp: with no real-time clock and an install-forced cold start that resets the uptime reference, no date/time is attached to the version change, so the "five years after each upload" retention clock cannot be established on-device.
- **Abstract Steps:**
  1. Read the uptime reference and current version before an upload.
  2. Perform an upload (forces install restart).
  3. After restart, read the uptime reference and version.
  4. Confirm the time base reset and that no absolute date/time is associated with the upload event.
- **Pass/Fail:** **PASS against the requirement** if a per-upload absolute timestamp is recorded and retained. **Expected FAIL:** uptime resets, no real-time clock, no absolute time on the version change → per-upload retention clock cannot be started.

### TC-013-D — External-Record (Release-Notes) Verification
- **Traceability:** RQ-013 → CR 2.9 (compensating) → Asset I, Asset D
- **Target Threat:** Repudiation
- **SVV Category:** SVV-1
- **Objective:** Assess whether the external release documentation provides per-unit (per-serial), timestamped, tamper-evident, five-year, per-upload records for the specific physical unit.
- **Abstract Steps:**
  1. Review the external release documentation available for the unit.
  2. Assess it against the criteria: device-resident? per-serial? tamper-evident? guaranteed five-year per-upload retention? per-upload timestamp?
- **Pass/Fail:** **Expected:** the external records are not device-resident, not per-serial, not tamper-evident, and provide no guaranteed per-upload timestamped five-year retention → the external record cannot cure the on-device gap for a specific unit.

---

## RQ-014 — Restrict tracing-log access to a competent-authority request

### TC-014-A — Unauthenticated Tracing-Log Read
- **Traceability:** RQ-014 → CR 1.1 / CR 1.2 / CR 2.1 / CR 3.9 → Asset I, Asset H
- **Target Threat:** Information Disclosure (missing access-control boundary)
- **SVV Category:** SVV-4
- **Objective:** Demonstrate that the tracing log is fully readable by an arbitrary, unauthenticated node on the segment, with no identity, authentication, authorisation, or purpose-limitation — directly violating the requirement that access be restricted exclusively to a competent-authority request.
- **Abstract Steps:**
  1. From a node with only network access (no credentials, no configuration privilege), request the tracing-log content.
  2. Confirm the full log content is returned.
  3. Confirm no authentication challenge, session, or authorisation check is presented at any point.
  4. Confirm no purpose/requestor context is required.
- **Pass/Fail:** **PASS against the requirement iff** the log read requires authentication and a purpose-limited authorisation. **Expected FAIL:** the log is returned to an unauthenticated arbitrary node with no gate → confirms the missing access-control gap.

### TC-014-B — Cleartext Confidentiality of the Tracing Log (Defence-in-Depth)
- **Traceability:** RQ-014 → CR 4.1 / CR 4.3 (supporting observation) → Asset I, Asset H
- **Target Threat:** Information Disclosure
- **SVV Category:** SVV-3
- **Objective:** Demonstrate that tracing-log content is transmitted without transport encryption and can be captured passively on the segment, and that no encrypted transport option exists. *Supporting observation; the primary RQ-014 finding is the missing access control, not the absence of encryption.*
- **Abstract Steps:**
  1. Trigger a legitimate log read.
  2. Passively capture the exchange.
  3. Extract the cleartext log content.
  4. Confirm no encrypted transport endpoint is available.
- **Pass/Fail:** **PASS against the requirement** if log transport is encrypted. **Expected:** cleartext recoverable and no encrypted transport → supporting confidentiality-in-transit observation. *(Method aligned to the framework's TLS-analysis step, including certificate-chain capture, for consistency.)*

### TC-014-C — Access-Control Mechanism Probe
- **Traceability:** RQ-014 → CR 1.1 / CR 1.2 / CR 2.1 → Asset I, Asset H
- **Target Threat:** Information Disclosure (missing authorisation gate)
- **SVV Category:** SVV-3
- **Objective:** Enumerate the information interface for any authentication mechanism, role model, or purpose-gate governing the tracing-log endpoint, establishing that no gate exists by design.
- **Abstract Steps:**
  1. Enumerate the tracing-log endpoint and adjacent endpoints for any authentication or authorisation control.
  2. Attempt to identify any role/identity model.
  3. Confirm whether any purpose-limitation mechanism is present.
- **Pass/Fail:** **Expected:** no authentication mechanism, role model, or purpose-gate is present → confirms the requirement cannot be met because the device has no identity model to restrict access to any party.

### TC-014-D — Deletion-Control Probe
- **Traceability:** RQ-014 → CR 3.9 → Asset I
- **Target Threat:** Tampering
- **SVV Category:** SVV-3
- **Objective:** Demonstrate that there is no controlled-deletion mechanism for the tracing log (only the uncontrolled cold-start wipe), so no data-lifecycle control exists to govern who may erase the record and when.
- **Abstract Steps:**
  1. Enumerate the interface for any delete/erase command applying to the tracing log.
  2. Attempt any discoverable deletion operation.
  3. Confirm whether controlled deletion is possible and, if so, whether it is access-controlled.
- **Pass/Fail:** **Expected:** no controlled-deletion command exists (only the cold-start wipe) → confirms the absence of data-lifecycle control.

---

## Cross-Reference & Reuse Summary
| Reused method | Referenced by |
|---|---|
| **TC-002-A** (parameter integrity-value rejection) | TC-005-A |
| **TC-002-E** (physical tamper-resistance) | TC-011-E |
| **TC-003-C** (illegitimate physical intervention) | TC-011-E |
| **TC-003-D** (time-attribution failure) | TC-008-D, TC-012-D, TC-013-C |
| **TC-003-E** (excluded-interface, no evidence) | TC-008-E |
| **TC-004-B** (SBOM completeness / vulnerability correlation) | TC-006-B |
| **TC-005-C** (unsigned/modified firmware install) | TC-008-C, TC-010-E |
| **TC-001-C / TC-001-D** (spoofing/MITM outcomes) | TC-010-E |

## Notes carried forward to Level 2
- **Verify before execution:** exact MITRE ATT&CK for ICS technique identifiers for the firmware-integrity and parameter-modification cases; empirical persistence of the change counter across cold start (RQ-009); and the precise ATT&CK technique for the in-path takeover (RQ-001-D).
- **Safety constraints to encode in Level 2:** spare-unit-only for all firmware and physical-tamper cases with a re-flash-to-validated-image step; managed test switch with rate limits and a defined abort criterion for all flood cases; isolated test zone and written test window per the framework's safety rules.
- **Scoring discipline:** confidentiality-only findings (TC-004-C, TC-006-C, TC-014-B) are defence-in-depth observations, not conformance failures, except where access restriction is a direct Machinery-Regulation duty (RQ-014).
