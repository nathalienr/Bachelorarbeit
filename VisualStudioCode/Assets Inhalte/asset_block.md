# System Asset Inventory

Assets extracted from `SystemBlockdiagramm_Security.drawio` (diagram "SRIO Security-Scope"). Naming follows the labels shown in the diagram; internal IDs use the prefix `AST-BD-` (Block Diagram) to avoid collision with the data-asset register (`AST-0xx`) used elsewhere in this workspace.

| Asset ID | Asset Name | Asset Type | Function |
|-----------|-------------|------------|------------|
| AST-BD-01 | NetX90 | Hardware – Communication Processor | Fieldbus/Ethernet communication processor; terminates the external network and forwards process/diagnostic data to the Host [CPU3]. |
| AST-BD-02 | Host [CPU3] | Hardware – Application/Host Processor | Main application processor; bridges the external network (via NetX90) and the safety subsystem (via SysCom to SCPU1); owns Flash and its local EEPROM. |
| AST-BD-03 | Flash | Hardware – Non-volatile Memory | Program/firmware storage for the Host [CPU3]. |
| AST-BD-04 | EEPROM (Host) | Hardware – Non-volatile Memory | Configuration/persistent data storage attached to the Host [CPU3]. |
| AST-BD-05 | Shared Update | Logical – Shared Memory Region | Shared memory/mailbox used to coordinate firmware update data between Host [CPU3] and SCPU1. |
| AST-BD-06 | SCPU1 [CPU1] | Hardware – Safety CPU (Channel 1) | Safety-related processor, channel 1 of the 1oo2 safety architecture; reads F-DI, drives F-DO, exchanges data with SCPU2 via IPC and with Host via SysCom. |
| AST-BD-07 | SCPU2 [CPU2] | Hardware – Safety CPU (Channel 2) | Safety-related processor, channel 2 of the 1oo2 safety architecture; reads F-DI, drives F-DO, exchanges data with SCPU1 via IPC only (no direct COM-zone link). |
| AST-BD-08 | EEPROM (SCPU1) | Hardware – Non-volatile Memory | Local safety configuration/parameter storage for SCPU1. |
| AST-BD-09 | EEPROM (SCPU2) | Hardware – Non-volatile Memory | Local safety configuration/parameter storage for SCPU2. |
| AST-BD-10 | Rotary Switches | Hardware – Physical HMI Element | Physical rotary encoder(s) used to set device/network address; feeds SCPU1. |
| AST-BD-11 | Watchdog | Hardware – Safety Monitoring Component | Independent monitoring element supervising SCPU1/SCPU2 life-signs and able to act on F-DI/F-DO paths; visually highlighted in the diagram (distinct fill/stroke color and bold conduit lines). |
| AST-BD-12 | F-DI (Safe Inputs) | Hardware – Safety I/O Terminal | Safety-rated digital input terminal block, read redundantly by SCPU1 and SCPU2. |
| AST-BD-13 | F-DO (Safe Outputs) | Hardware – Safety I/O Terminal | Safety-rated digital output terminal block, driven redundantly by SCPU1 and SCPU2. |
| AST-BD-14 | External Network / Ethernet Cloud | External – Network | External Ethernet/fieldbus network shown outside the "Device" trust boundary; connects to NetX90 across the "external network boundary". |
| AST-BD-15 | External PC / Engineering Workstation | External – Endpoint Device | External PC (network icon) shown outside the "Device" trust boundary; connects to NetX90 across the "external network boundary" for engineering/service access. |

---

# Interface Inventory

| Interface | Source Asset | Destination Asset | Purpose |
|------------|---------------|------------------|---------|
| IF-01 External Network Link | External Network / Ethernet Cloud (AST-BD-14) | NetX90 (AST-BD-01) | Field network / Ethernet connection carrying process, diagnostic, and configuration traffic into the device. |
| IF-02 Engineering/Service Link | External PC / Engineering Workstation (AST-BD-15) | NetX90 (AST-BD-01) | Engineering/maintenance access into the device via the network interface. |
| IF-03 NetX90–Host Bus | NetX90 (AST-BD-01) | Host [CPU3] (AST-BD-02) | Internal data path carrying fieldbus process/diagnostic data between the communication processor and the host application. |
| IF-04 Host–Flash Bus | Host [CPU3] (AST-BD-02) | Flash (AST-BD-03) | Firmware/code storage access. |
| IF-05 Host–EEPROM Bus | Host [CPU3] (AST-BD-02) | EEPROM (Host) (AST-BD-04) | Configuration/persistent data storage access. |
| IF-06 SysCom | Host [CPU3] (AST-BD-02) | SCPU1 [CPU1] (AST-BD-06) | Inter-domain system communication between Host and the safety subsystem, crossing the internal COM↔SCPU domain boundary. |
| IF-07 Shared Update (Host side) | Host [CPU3] (AST-BD-02) | Shared Update (AST-BD-05) | Host writes firmware-update coordination data. |
| IF-08 Shared Update (SCPU side) | SCPU1 [CPU1] (AST-BD-06) | Shared Update (AST-BD-05) | SCPU1 reads/writes firmware-update coordination data. |
| IF-09 IPC | SCPU1 [CPU1] (AST-BD-06) | SCPU2 [CPU2] (AST-BD-07) | Inter-processor communication between the two safety CPUs (cross-channel comparison / 1oo2 voting). |
| IF-10 SCPU1–EEPROM Bus | SCPU1 [CPU1] (AST-BD-06) | EEPROM (SCPU1) (AST-BD-08) | Safety configuration/parameter storage access. |
| IF-11 SCPU2–EEPROM Bus | SCPU2 [CPU2] (AST-BD-07) | EEPROM (SCPU2) (AST-BD-09) | Safety configuration/parameter storage access. |
| IF-12 Rotary Switch Input | Rotary Switches (AST-BD-10) | SCPU1 [CPU1] (AST-BD-06) | Physical address/configuration input. |
| IF-13 F-DI Channel 1 | F-DI (Safe Inputs) (AST-BD-12) | SCPU1 [CPU1] (AST-BD-06) | Safety input signal, channel 1. |
| IF-14 F-DI Channel 2 | F-DI (Safe Inputs) (AST-BD-12) | SCPU2 [CPU2] (AST-BD-07) | Safety input signal, channel 2. |
| IF-15 F-DO Channel 1 | SCPU1 [CPU1] (AST-BD-06) | F-DO (Safe Outputs) (AST-BD-13) | Safety output signal, channel 1. |
| IF-16 F-DO Channel 2 | SCPU2 [CPU2] (AST-BD-07) | F-DO (Safe Outputs) (AST-BD-13) | Safety output signal, channel 2. |
| IF-17 Watchdog Supervision 1 | SCPU1 [CPU1] (AST-BD-06) | Watchdog (AST-BD-11) | Life-sign/heartbeat monitoring, channel 1. |
| IF-18 Watchdog Supervision 2 | SCPU2 [CPU2] (AST-BD-07) | Watchdog (AST-BD-11) | Life-sign/heartbeat monitoring, channel 2. |
| IF-19 Watchdog–F-DI Enforcement | Watchdog (AST-BD-11) | F-DI (Safe Inputs) (AST-BD-12) | Safe-state enforcement/test path on the input channel. |
| IF-20 Watchdog–F-DO Enforcement | Watchdog (AST-BD-11) | F-DO (Safe Outputs) (AST-BD-13) | Safe-state enforcement (forces outputs off) on watchdog trip. |

---

# Asset-to-Asset Connectivity

External Network / Ethernet Cloud → IF-01 → NetX90
External PC / Engineering Workstation → IF-02 → NetX90
NetX90 → IF-03 → Host [CPU3]
Host [CPU3] → IF-04 → Flash
Host [CPU3] → IF-05 → EEPROM (Host)
Host [CPU3] → IF-06 (SysCom) → SCPU1 [CPU1]
Host [CPU3] → IF-07 (Shared Update) → Shared Update
SCPU1 [CPU1] → IF-08 (Shared Update) → Shared Update
SCPU1 [CPU1] → IF-09 (IPC) → SCPU2 [CPU2]
SCPU1 [CPU1] → IF-10 → EEPROM (SCPU1)
SCPU2 [CPU2] → IF-11 → EEPROM (SCPU2)
Rotary Switches → IF-12 → SCPU1 [CPU1]
F-DI (Safe Inputs) → IF-13 → SCPU1 [CPU1]
F-DI (Safe Inputs) → IF-14 → SCPU2 [CPU2]
SCPU1 [CPU1] → IF-15 → F-DO (Safe Outputs)
SCPU2 [CPU2] → IF-16 → F-DO (Safe Outputs)
SCPU1 [CPU1] → IF-17 (Watchdog Supervision) → Watchdog
SCPU2 [CPU2] → IF-18 (Watchdog Supervision) → Watchdog
Watchdog → IF-19 → F-DI (Safe Inputs)
Watchdog → IF-20 → F-DO (Safe Outputs)

---

# Communication Matrix

| Source | Destination | Interface |
|----------|-------------|-----------|
| External Network / Ethernet Cloud | NetX90 | IF-01 External Network Link |
| External PC / Engineering Workstation | NetX90 | IF-02 Engineering/Service Link |
| NetX90 | Host [CPU3] | IF-03 NetX90–Host Bus |
| Host [CPU3] | Flash | IF-04 Host–Flash Bus |
| Host [CPU3] | EEPROM (Host) | IF-05 Host–EEPROM Bus |
| Host [CPU3] | SCPU1 [CPU1] | IF-06 SysCom |
| Host [CPU3] | Shared Update | IF-07 Shared Update (Host side) |
| SCPU1 [CPU1] | Shared Update | IF-08 Shared Update (SCPU side) |
| SCPU1 [CPU1] | SCPU2 [CPU2] | IF-09 IPC |
| SCPU1 [CPU1] | EEPROM (SCPU1) | IF-10 SCPU1–EEPROM Bus |
| SCPU2 [CPU2] | EEPROM (SCPU2) | IF-11 SCPU2–EEPROM Bus |
| Rotary Switches | SCPU1 [CPU1] | IF-12 Rotary Switch Input |
| F-DI (Safe Inputs) | SCPU1 [CPU1] | IF-13 F-DI Channel 1 |
| F-DI (Safe Inputs) | SCPU2 [CPU2] | IF-14 F-DI Channel 2 |
| SCPU1 [CPU1] | F-DO (Safe Outputs) | IF-15 F-DO Channel 1 |
| SCPU2 [CPU2] | F-DO (Safe Outputs) | IF-16 F-DO Channel 2 |
| SCPU1 [CPU1] | Watchdog | IF-17 Watchdog Supervision 1 |
| SCPU2 [CPU2] | Watchdog | IF-18 Watchdog Supervision 2 |
| Watchdog | F-DI (Safe Inputs) | IF-19 Watchdog–F-DI Enforcement |
| Watchdog | F-DO (Safe Outputs) | IF-20 Watchdog–F-DO Enforcement |

---

# Power Distribution

The diagram does not depict any power rails, voltage domains, or a power-supply tree — it is a logical/security block diagram focused on data conduits and trust boundaries. No power-domain vertices (e.g. `3V3`, `5V`, PSU blocks) are present in the source file.

Best-effort grouping inferred purely from the visible **trust-zone** structure (marked *Assumed* — rationale: embedded safety devices typically isolate power domains along the same boundaries as data/trust domains, but this is not shown explicitly):

## Assumed COM Domain Supply
Connected Assets (Assumed):
- NetX90
- Host [CPU3]
- Flash
- EEPROM (Host)
- Shared Update

## Assumed SCPU Domain Supply (dual/redundant)
Connected Assets (Assumed):
- SCPU1 [CPU1]
- SCPU2 [CPU2]
- EEPROM (SCPU1)
- EEPROM (SCPU2)
- Rotary Switches
- Watchdog
- F-DI (Safe Inputs)
- F-DO (Safe Outputs)

No further detail (voltage levels, isolation components, supply source) can be derived from this diagram; a dedicated power/electrical schematic would be required for a complete Power Distribution section.

---

# Safety-Relevant Assets

## SCPU1 [CPU1] / SCPU2 [CPU2]
- **Function:** Redundant (1oo2) safety-related processors executing the safety logic; each independently reads F-DI and drives F-DO.
- **Connected interfaces:** IF-09 (IPC, cross-channel), IF-06 (SysCom, SCPU1 only), IF-10/IF-11 (local EEPROM), IF-12 (Rotary Switches, SCPU1 only), IF-13/IF-14 (F-DI), IF-15/IF-16 (F-DO), IF-17/IF-18 (Watchdog).
- **Safety role:** Implements the diverse/redundant safety function (1oo2 voting via IPC); each channel independently drives the safety outputs.
- **Potential impact of failure:** Loss or corruption of one channel could go undetected without correct IPC cross-checking, potentially leading to loss of the safety function or an undetected dangerous failure; a common-cause failure affecting both channels could defeat the redundancy entirely.

## Watchdog
- **Function:** Independent supervisory element monitoring life-signs of SCPU1 and SCPU2 and capable of acting directly on F-DI/F-DO.
- **Connected interfaces:** IF-17, IF-18 (supervision inputs from both SCPUs), IF-19, IF-20 (enforcement outputs to F-DI/F-DO).
- **Safety role:** Independent safe-state enforcement mechanism; forces I/O to a defined safe state if either SCPU fails to service the watchdog in time.
- **Potential impact of failure:** A failed or bypassed Watchdog removes the last line of defense against a hung/faulty SCPU, potentially allowing an unsafe output state to persist.

## F-DI (Safe Inputs)
- **Function:** Safety-rated digital input terminal, read redundantly by both SCPUs.
- **Connected interfaces:** IF-13, IF-14 (to SCPU1/SCPU2), IF-19 (from Watchdog).
- **Safety role:** Physical/electrical entry point for safety process data (e.g. PROFIsafe F-DI values per project data-asset register).
- **Potential impact of failure:** Corrupted or manipulated input data can cause unsafe control decisions or false safe-state trips.

## F-DO (Safe Outputs)
- **Function:** Safety-rated digital output terminal, driven redundantly by both SCPUs.
- **Connected interfaces:** IF-15, IF-16 (from SCPU1/SCPU2), IF-20 (from Watchdog).
- **Safety role:** Physical/electrical actuation point for the safety function; must reach a defined safe state on failure.
- **Potential impact of failure:** Manipulated or "stuck" output data can cause unintended actuation or block a required safety action.

## EEPROM (SCPU1) / EEPROM (SCPU2)
- **Function:** Local non-volatile storage of safety configuration/parameters per channel.
- **Connected interfaces:** IF-10, IF-11.
- **Safety role:** Persists safety parameters (e.g. F-Parameters/iPar equivalents) required for correct safety-function configuration.
- **Potential impact of failure:** Corruption of stored parameters could cause the safety function to start with an incorrect or inconsistent configuration.

## Rotary Switches
- **Function:** Physical local input for device/network address configuration, feeding SCPU1.
- **Connected interfaces:** IF-12.
- **Safety role:** Establishes the device's safety address (relevant to safe addressing, cf. `F_Dest_Address` in the project's data-asset register); SCPU2 is assumed to obtain this value via IPC (not directly wired).
- **Potential impact of failure:** Incorrect or tampered address setting can cause misbinding of safety communication (talking to/being controlled by the wrong safety partner).

---

# External Interfaces

| Interface | Type | Direction | Connected Asset |
|------------|------|------------|----------------|
| IF-01 External Network Link | Ethernet / Fieldbus Network | Bidirectional | NetX90 |
| IF-02 Engineering/Service Link | Network (Engineering/Service Access) | Bidirectional | NetX90 |

Both external interfaces terminate at NetX90 and cross the diagram's dashed-red **"external network boundary"**, which itself lies outside the outer **"Device"** trust boundary. No other externally facing interfaces (e.g. USB, serial/debug, wireless) are shown in this diagram.

---

# Data Flow Analysis

**Fieldbus / Network process data (inbound)**
External Network / Ethernet Cloud
→ NetX90 (IF-01)
→ Host [CPU3] (IF-03)
→ SysCom (IF-06)
→ SCPU1
→ IPC (IF-09)
→ SCPU2
→ F-DO Safe Outputs (IF-15/IF-16)

**Safety input reporting (outbound)**
F-DI Safe Inputs
→ SCPU1 / SCPU2 (IF-13/IF-14)
→ IPC cross-check (IF-09)
→ SysCom (IF-06)
→ Host [CPU3]
→ NetX90 (IF-03)
→ External Network / Ethernet Cloud (IF-01)

**Firmware update flow**
External PC / Engineering Workstation
→ NetX90 (IF-02)
→ Host [CPU3]
→ Flash / EEPROM (Host) (IF-04/IF-05)
→ Shared Update (IF-07)
→ SCPU1 (IF-08)
→ EEPROM (SCPU1) (IF-10)

**Safety monitoring / enforcement flow**
SCPU1 & SCPU2
→ Watchdog (IF-17/IF-18)
→ F-DI / F-DO (IF-19/IF-20, safe-state enforcement on trip)

**Device addressing flow**
Rotary Switches
→ SCPU1 (IF-12)
→ IPC (IF-09, assumed propagation to SCPU2)

---

# IEC 62443 Asset Inventory

| Asset | Zone | Interfaces | Criticality | Security Notes |
|---------|---------|---------|---------|---------|
| NetX90 | COM Zone | IF-01, IF-02, IF-03 | High | Primary network-facing entry point (fieldbus + engineering access); protocol parsing surface directly exposed to the external network boundary. |
| Host [CPU3] | COM Zone | IF-03, IF-04, IF-05, IF-06, IF-07 | High | Bridges untrusted network path to the safety zone via SysCom; compromise here threatens the SCPU zone. |
| Flash | COM Zone | IF-04 | Medium | Firmware/code integrity storage; target for persistence of malicious code if writable from Host. |
| EEPROM (Host) | COM Zone | IF-05 | Medium | Configuration data storage; disclosure/tamper risk for device identity/config. |
| Shared Update | COM Zone / SCPU Zone (conduit) | IF-07, IF-08 | Medium-High | Crosses the COM↔SCPU boundary; a key conduit for the firmware-update attack path into the safety zone. |
| SCPU1 [CPU1] | SCPU Zone | IF-06, IF-08, IF-09, IF-10, IF-12, IF-13, IF-15, IF-17 | High | Only safety CPU with a direct link to the COM zone (SysCom, Rotary Switches, Shared Update) — primary ingress point into the SCPU Zone. |
| SCPU2 [CPU2] | SCPU Zone | IF-09, IF-11, IF-14, IF-16, IF-18 | High | No direct COM-zone interface; reachable only via IPC from SCPU1, reducing (but not eliminating) direct exposure. |
| EEPROM (SCPU1) | SCPU Zone | IF-10 | High | Stores safety configuration/parameters for channel 1. |
| EEPROM (SCPU2) | SCPU Zone | IF-11 | High | Stores safety configuration/parameters for channel 2. |
| Rotary Switches | SCPU Zone | IF-12 | Medium | Physical-access-only attack surface (requires local/physical presence at the enclosure). |
| Watchdog | SCPU Zone | IF-17, IF-18, IF-19, IF-20 | High | Independent safety-enforcement path; disabling/bypassing it removes the last safety backstop. |
| F-DI (Safe Inputs) | SCPU Zone (I/O boundary) | IF-13, IF-14, IF-19 | High | Field-wiring boundary; entry point for manipulated process signals. |
| F-DO (Safe Outputs) | SCPU Zone (I/O boundary) | IF-15, IF-16, IF-20 | High | Field-wiring boundary; actuation point, direct safety impact if manipulated. |
| External Network / Ethernet Cloud | External / Untrusted Zone | IF-01 | N/A (external) | Untrusted network; principal attack origin. |
| External PC / Engineering Workstation | External / Untrusted Zone | IF-02 | N/A (external) | Untrusted engineering/service endpoint; principal attack origin for update/config attacks. |

---

# Security Zones and Conduits

**Security Zones** (as drawn by the three nested dashed rectangles in the diagram):
- **External / Untrusted Zone** — everything outside the outer "Device" boundary: External Network / Ethernet Cloud, External PC / Engineering Workstation.
- **Device Zone** (outer red dashed boundary, labeled "Thrusted boundary: Device" [sic] in the source) — encloses the entire device, i.e. the COM Zone and the SCPU Zone.
- **COM Zone** (orange dashed boundary, labeled "Thrusted boundary: COM") — contains NetX90, Host [CPU3], Flash, EEPROM (Host), Shared Update.
- **SCPU Zone** (orange dashed boundary, labeled "Thrusted boundary: SCPU") — contains SCPU1, SCPU2, EEPROM (SCPU1), EEPROM (SCPU2), Rotary Switches, Watchdog, F-DI, F-DO.

**Conduits** (connections that cross a zone boundary):
- IF-01 / IF-02 — cross the External↔Device boundary (labeled "external network boundary" in the diagram) into NetX90.
- IF-06 (SysCom) — crosses the COM↔SCPU boundary (labeled "internal domain boundary (SCPU <-> COM)"), connecting Host [CPU3] to SCPU1.
- IF-07 / IF-08 (Shared Update) — effectively crosses the COM↔SCPU boundary, since the Shared Update block (COM zone) is written by both Host [CPU3] (COM zone) and SCPU1 (SCPU zone).
- IF-12 (Rotary Switches → SCPU1) — a purely physical, local conduit within the SCPU zone (no zone crossing).
- IF-09 (IPC) — intra-zone conduit within the SCPU Zone (SCPU1 ↔ SCPU2).

**Trust Boundaries:**
- External network boundary (External Zone / Device Zone) — dashed red lines terminating at NetX90.
- Device boundary (outer red dashed rectangle).
- COM/SCPU internal domain boundary (orange dashed rectangles + the explicitly labeled SysCom edge).

**Critical Assets:** SCPU1, SCPU2, Watchdog, F-DI, F-DO, EEPROM (SCPU1), EEPROM (SCPU2), Host [CPU3], NetX90.

**Entry Points:** External Network Link (IF-01) into NetX90; Engineering/Service Link (IF-02) into NetX90; Rotary Switches (local physical access); Shared Update path (firmware-update conduit into the SCPU zone).

**Attack Surfaces:**
- NetX90 fieldbus/Ethernet protocol stack (remote, network-reachable).
- External PC / engineering-service path into NetX90 (remote or on-site network access).
- Firmware update path: External PC → NetX90 → Host → Shared Update → SCPU1 (potential path to inject unauthorized firmware/config into the safety zone).
- SysCom channel Host ↔ SCPU1 (only bridge from COM to SCPU zone).
- Physical access to Rotary Switches, EEPROMs, and Flash (local/physical tampering, extraction, or reprogramming).

---

# Assumptions

- **SCPU2 rotary/address value:** Not directly wired in the diagram; only SCPU1 connects to Rotary Switches (IF-12). *Assumed* that SCPU2 receives the equivalent address/configuration value from SCPU1 via IPC (IF-09), since a 1oo2 safety architecture requires both channels to agree on the safety address. Rationale: no other path to SCPU2 exists in the diagram.
- **Bidirectionality of local storage/bus interfaces:** IF-04 (Host–Flash), IF-05 (Host–EEPROM), IF-10 (SCPU1–EEPROM), IF-11 (SCPU2–EEPROM), IF-03 (NetX90–Host) are drawn with mixed/partial arrowheads in the source XML. *Assumed* bidirectional (read/write) behavior, consistent with typical local memory/communication bus usage, since the exact directionality cannot be unambiguously derived from the raw diagram data.
- **Bus/protocol type of local interfaces:** The diagram does not label the physical bus technology for EEPROM, Flash, or Host↔NetX90 links (e.g. SPI/I²C/parallel). *Assumed* generic "local bus" interfaces; exact protocol is out of scope of this diagram.
- **Power domains:** No power/voltage information is present in the diagram. The grouping in the Power Distribution section is *Assumed*, based only on the visible trust-zone (COM/SCPU) partitioning, and should be verified against an electrical schematic.
- **External PC connection medium:** The external PC icon is connected with the same "external network boundary" style as the Ethernet cloud, so it is *Assumed* to reach NetX90 over the same network path (e.g. Ethernet-based engineering access) rather than a separate physical port (e.g. USB), which is not shown.
- **Diagram label typo:** The source diagram's trust-boundary labels read "Thrusted boundary" — retained here for traceability but understood to mean "Trusted boundary".
