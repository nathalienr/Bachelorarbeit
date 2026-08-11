# Optimized Asset Block v2


---

## 3. Optimized Asset Inventory

| Asset ID | Asset Name | Diagram Element | Original Asset Reference | Category | Asset Type | Protection Goal | TARA Rationale | Granularity | Template Alignment | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| AST-V2-01 | NetX90 | Cell 2192 | AST-BD-01 | Physical Assets | Physical (Hardware Component – Communication Processor) | Integrity; Availability | Primary network-facing entry point (fieldbus + engineering access); compromise enables pivoting into COM/SCPU zones | One asset per physical processor | Partial Match | Template's "Hardware Components" row matches the chip itself; the PROFINET/Ethernet protocol stack it runs is a logical sub-asset not separately drawn (see Section 8). |
| AST-V2-02 | Host [CPU3] | Cell 2187 | AST-BD-02 | Physical Assets | Physical (Hardware Component – Application/Host Processor) | Integrity; Availability; Confidentiality | Bridges the untrusted network path (via NetX90) to the safety zone (via SysCom); central attack pivot | One asset per physical processor | Direct Match | Firmware/OS/Application software executed on the Host is not separately modeled in the diagram (Section 8). |
| AST-V2-03 | Flash (Host) | Cell 2376 | AST-BD-03 | Physical Assets | Physical/Logical (Internal Storage) | Integrity | Stores Host firmware/code; compromise enables persistence of malicious code | One asset per physical storage device | Direct Match | Template row "Internal Storage (Flash, EEPROM, eMMC, SD)"; renamed "Flash (Host)" to disambiguate from SCPU-side storage. |
| AST-V2-04 | EEPROM (Host) | Cell 2189 | AST-BD-04 | Physical Assets | Physical/Logical (Internal Storage) | Integrity; Confidentiality | Persists Host configuration/identity data | One asset per physical storage device, kept separate from SCPU EEPROMs (different trust zone) | Direct Match | — |
| AST-V2-05 | Shared Update (Host↔SCPU1 Firmware-Update Buffer) | Cell 2184 ("shared Update") | AST-BD-05 | Firmware and Software Assets | Logical/Security (Update Mechanism / shared memory) | Integrity; Availability | Sole conduit carrying firmware-update coordination data across the COM↔SCPU trust boundary; prime target to inject unauthorized code into the safety zone | One asset (single shared region); do not merge into Host or SCPU1 | Partial Match | Closest template rows: "Update Configuration", "Update Packages", "Update Mechanism" (M-13). Boundary-crossing — see Section 5. |
| AST-V2-06 | SCPU1 [CPU1] | Cell 2155 | AST-BD-06 | Physical Assets | Physical (Hardware Component – Safety CPU, Channel 1) | Integrity; Availability | Executes safety logic, channel 1 of the 1oo2 architecture; only safety CPU with a direct COM-zone link | One asset per redundant channel (not merged with SCPU2) | Direct Match | Safety-relevant — see Section 4. |
| AST-V2-07 | SCPU2 [CPU2] | Cell 2156 | AST-BD-07 | Physical Assets | Physical (Hardware Component – Safety CPU, Channel 2) | Integrity; Availability | Executes safety logic, channel 2 of the 1oo2 architecture; reachable only via IPC from SCPU1 | One asset per redundant channel | Direct Match | Safety-relevant — see Section 4. |
| AST-V2-08 | EEPROM (SCPU1) | Cell 2181 | AST-BD-08 | Physical Assets | Physical/Logical (Internal Storage – safety config) | Integrity | Stores safety configuration/parameters for channel 1; corruption can misconfigure the safety function | One asset per channel (redundant, not merged with SCPU2's EEPROM) | Direct Match | Safety-relevant — see Section 4. |
| AST-V2-09 | EEPROM (SCPU2) | Cell 2176 | AST-BD-09 | Physical Assets | Physical/Logical (Internal Storage – safety config) | Integrity | Stores safety configuration/parameters for channel 2 | One asset per channel | Direct Match | Safety-relevant — see Section 4. |
| AST-V2-10 | Rotary Switches | Cell 2386 | AST-BD-10 | Physical Assets / Configuration Assets | Physical/Interface (HMI input element) | Integrity | Sets the device/safety address (own safe address); tampering enables address-spoofing or misbinding of safety communication | One asset (physical HMI element) | Partial Match | No exact template row for a physical rotary switch; closest match is "Device Parameters" (the data it sets) combined with generic "Hardware Components". Only wired to SCPU1 in the diagram (see Section 11, Assumption carried over from `asset_block.md`). |
| AST-V2-11 | Watchdog | Cell 2503 | AST-BD-11 | Physical Assets | Physical (Hardware Component – Safety Monitoring/Enforcement) | Availability; Integrity | Independent last line of defense forcing a safe state on SCPU failure | One asset | Diagram-Specific Asset | No generic template equivalent (industrial-safety-specific component); safety-relevant — see Section 4. |
| AST-V2-12 | F-DI (Safe Inputs) | Cell 2501 | AST-BD-12 | Physical Assets | Physical/Interface (Safety Digital Input Terminal) | Integrity; Availability | Physical/electrical entry point for safety input signals, read redundantly by both SCPUs | One asset (terminal block covering both channels; channel detail kept at interface level, see IF-13/IF-14) | Partial Match | Closest generic template row is "Service Interfaces"; template has no safety-I/O-specific category. Safety-relevant and boundary-crossing — see Sections 4 and 5. |
| AST-V2-13 | F-DO (Safe Outputs) | Cell 2502 | AST-BD-13 | Physical Assets | Physical/Interface (Safety Digital Output Terminal) | Integrity; Availability | Physical/electrical actuation point for the safety function, driven redundantly by both SCPUs | One asset (terminal block covering both channels; channel detail kept at interface level, see IF-15/IF-16) | Partial Match | Same as above. Safety-relevant and boundary-crossing — see Sections 4 and 5. |

**Reclassified (removed from the core device-asset table — see Section 9, Decision 1):**

| Original ID | Original Name | Reclassification |
|---|---|---|
| AST-BD-14 | External Network / Ethernet Cloud | Non-asset external entity (network infrastructure/threat source) — see Sections 5 and 6 |
| AST-BD-15 | External PC / Engineering Workstation | Non-asset external entity (external actor/threat source) — see Sections 5 and 6 |

---

## 4. Safety-Relevant Assets

| Asset | Diagram Evidence | Safety Relevance | Protection Goal | Notes |
|---|---|---|---|---|
| SCPU1 [CPU1] (AST-V2-06) | Cell 2155; edges to IPC (2157), SysCom (2195), EEPROM (2182), Rotary Switches (2388), F-DI (2505), F-DO (2520), Watchdog (2508) | Channel 1 of the redundant (1oo2) safety logic; sole bridge to the COM zone | Integrity; Availability | Loss of independence/diversity between SCPU1 and SCPU2 due to shared design defects is a common-cause-failure concern. |
| SCPU2 [CPU2] (AST-V2-07) | Cell 2156; edges to IPC (2157), EEPROM (2500), F-DI (2515), F-DO (2510), Watchdog (2512) | Channel 2 of the redundant (1oo2) safety logic | Integrity; Availability | No direct COM-zone interface — reduced (not eliminated) direct exposure vs. SCPU1. |
| EEPROM (SCPU1) (AST-V2-08) | Cell 2181; edge 2182 | Stores channel-1 safety configuration/parameters | Integrity | Kept separate from EEPROM (SCPU2) to preserve redundant-channel traceability. |
| EEPROM (SCPU2) (AST-V2-09) | Cell 2176; edge 2500 | Stores channel-2 safety configuration/parameters | Integrity | Kept separate from EEPROM (SCPU1). |
| Watchdog (AST-V2-11) | Cell 2503 (visually highlighted, distinct fill/stroke); edges 2508, 2512, 2518, 2519 | Independent safety-enforcement mechanism; forces F-DI/F-DO to a safe state if either SCPU fails to service it | Availability; Integrity | Disabling/bypassing removes the last safety backstop. |
| F-DI (Safe Inputs) (AST-V2-12) | Cell 2501; edges 2505, 2515, 2518 | Redundant (dual-channel) safety input field terminal | Integrity; Availability | Field-wiring boundary; also listed under Section 5 as boundary-crossing. |
| F-DO (Safe Outputs) (AST-V2-13) | Cell 2502; edges 2510, 2520, 2519 | Redundant (dual-channel) safety output field terminal | Integrity; Availability | Field-wiring boundary; also listed under Section 5. |
| Rotary Switches (AST-V2-10) | Cell 2386; edge 2388 | Establishes the device's safety address (own safe address), foundational to correct safety-partner binding | Integrity | Physical/local-access-only attack surface. |

---

## 5. External and Boundary-Crossing Assets

| Asset | Zone / Boundary | Interface Exposure | Risk Relevance | Notes |
|---|---|---|---|---|
| NetX90 (AST-V2-01) | COM Zone, terminates the "external network boundary" | External Network Link (IF-01), Engineering/Service Link (IF-02) | High — the only component directly reachable from the untrusted external network | Primary attack surface of the whole device. |
| Host [CPU3] (AST-V2-02) | COM Zone | Reachable indirectly via NetX90 (IF-03) | High | Central logic behind the network-facing processor; also the sole originator of the SysCom conduit into the SCPU zone. |
| Shared Update (AST-V2-05) | Physically located in COM Zone but written by both Host (COM) and SCPU1 (SCPU) | IF-07 (Host side), IF-08 (SCPU1 side) | Medium-High | Crosses the internal COM↔SCPU trust boundary; key link in the firmware-update attack path. |
| SCPU1 [CPU1] (AST-V2-06) | SCPU Zone, terminates the internal "SCPU ↔ COM" domain boundary (SysCom) | IF-06 (SysCom), IF-12 (Rotary Switches) | High | Only safety CPU with a direct interface into/from the COM zone — primary ingress point into the SCPU zone. |
| F-DI (Safe Inputs) (AST-V2-12) | SCPU Zone / field-wiring boundary (edge of the modeled "Device" trust boundary) | IF-13, IF-14 (from field wiring), IF-19 (from Watchdog) | High | Physical entry point for externally wired process signals. |
| F-DO (Safe Outputs) (AST-V2-13) | SCPU Zone / field-wiring boundary | IF-15, IF-16 (to field wiring), IF-20 (from Watchdog) | High | Physical actuation point; direct safety impact if manipulated. |
| Rotary Switches (AST-V2-10) | SCPU Zone, physical/local access boundary (outside any network path) | IF-12 | Medium | Requires physical presence at the enclosure; not remotely reachable. |
| *External Network / Ethernet Cloud* (reclassified, was AST-BD-14) | Outside the "Device" trust boundary | IF-01 → NetX90 | High (as a threat source, not a protectable asset) | Retained here only for boundary traceability; see Section 9, Decision 1. |
| *External PC / Engineering Workstation* (reclassified, was AST-BD-15) | Outside the "Device" trust boundary | IF-02 → NetX90 | High (as a threat source, not a protectable asset) | Retained here only for boundary traceability; see Section 9, Decision 1. |

---

## 6. Interfaces and Conduits (Not Assets)

| Interface | Connected Components | Diagram Reference | Reason Excluded From Asset Inventory |
|---|---|---|---|
| IF-01 External Network Link | External Network / Ethernet Cloud ↔ NetX90 | Edge 2544, label 2217 "[Ethernet]", label 2548 "external network boundary" | Represents a conduit/data path, not a protectable component. |
| IF-02 Engineering/Service Link | External PC / Engineering Workstation ↔ NetX90 | Edge 2547, cell 2546 (PC icon), label 2548 | Conduit, not a component. |
| IF-03 NetX90–Host Bus | NetX90 ↔ Host [CPU3] | Edge 2193 | Internal data conduit between two assets. |
| IF-04 Host–Flash Bus | Host [CPU3] ↔ Flash (Host) | Edge 2190 | Local storage bus, not an asset itself. |
| IF-05 Host–EEPROM Bus | Host [CPU3] ↔ EEPROM (Host) | Edge 2377 | Local storage bus. |
| IF-06 SysCom | Host [CPU3] ↔ SCPU1 | Edge 2195, label 2198 "SysCom" | Named inter-domain conduit crossing the COM↔SCPU boundary; explicitly labeled as an interface in the diagram. |
| IF-07 Shared Update (Host side) | Host [CPU3] → Shared Update | Edge 2186 | Write path into the Shared Update asset, not a separate component. |
| IF-08 Shared Update (SCPU side) | SCPU1 ↔ Shared Update | Edge 2183 | Read/write path into the Shared Update asset. |
| IF-09 IPC | SCPU1 ↔ SCPU2 | Edge 2157, label 2199 "IPC" | Named inter-processor conduit, explicitly labeled as an interface in the diagram. |
| IF-10 SCPU1–EEPROM Bus | SCPU1 ↔ EEPROM (SCPU1) | Edge 2182 | Local storage bus. |
| IF-11 SCPU2–EEPROM Bus | SCPU2 ↔ EEPROM (SCPU2) | Edge 2500 | Local storage bus. |
| IF-12 Rotary Switch Input | Rotary Switches → SCPU1 | Edge 2388 | Physical signal path, not a component. |
| IF-13 / IF-14 F-DI Channels 1/2 | F-DI → SCPU1 / SCPU2 | Edges 2505, 2515 | Signal paths of the F-DI asset, not separate components. |
| IF-15 / IF-16 F-DO Channels 1/2 | SCPU1 / SCPU2 → F-DO | Edges 2520, 2510 | Signal paths of the F-DO asset. |
| IF-17 / IF-18 Watchdog Supervision 1/2 | SCPU1 / SCPU2 → Watchdog | Edges 2508, 2512 | Monitoring signal paths. |
| IF-19 / IF-20 Watchdog Enforcement | Watchdog → F-DI / F-DO | Edges 2518, 2519 | Enforcement signal paths. |

---
