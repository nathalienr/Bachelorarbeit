# SRIO TARA: Combined and Optimized Analysis


## Contents

- [README](#readme)
- [Dashboard](#dashboard)
- [SUC Assumptions](#suc-assumptions)
- [Assets](#assets)
- [Interfaces](#interfaces)
- [Risk Matrix](#risk-matrix)
- [TARA](#tara)
- [Requirements](#requirements)
- [Interface Asset Matrix](#interface-asset-matrix)

## README

| Topic | Description |
| --- | --- |
| Purpose | Threat Analysis and Risk Assessment for SRIO focused on interfaces, data flows, and affected assets. |
| Method |Interface -> Asset -> Threat Scenario -> Impact/Likelihood -> Risk Treatment -> Residual Risk. |
| Scoring | Likelihood and Impact are rated 1..5. Risk Score = Likelihood x Impact. |
| Risk levels | Low: 1-4; Medium: 5-9; High: 10-15; Critical: 16-25. |
| Scope boundary | Product-level TARA only. Plant architecture, controller hardening, and operator network governance remain system responsibilities unless explicitly stated as product controls. |
| How to use | Review orange TBD/Review fields, adapt likelihood/impact in the TARA sheet, assign owners and due dates, then confirm residual risks. |


## Dashboard

### Metrics

| Metric | Value |
| --- | --- |
| Total TARA scenarios| 24 |
| Critical (revised) | 0 |
| High (revised) | 8 |
| Medium (revised) | 12 |
| Low (revised) | 4 |
| Open issues | 8 |
| Open items | 24 |
| Review items | 0 |

### Top interfaces by scenario count

| Interface ID | Scenario count |
| --- | --- |
| IF-04 | 4 |
| IF-03 | 4 |
| IF-05 | 3 |
| IF-01 | 2 |
| IF-02 | 2 |
| IF-06 | 1 |
| IF-07 | 1 |
| IF-08 | 1 |
| IF-09 | 1 |
| IF-10 | 1 |
| IF-11 | 1 |
| IF-12 | 1 |
| IF-01/03 | 1 |
| IF-01/02 | 1 |

## SUC Assumptions

| Category | Statement | Responsibility | TARA relevance | Status |
| --- | --- | --- | --- | --- |
| System role | SRIO is a functional safety remote I/O gateway between sensors/actuators and an F-Host. | Product | Defines protected system and safety role. | Confirmed |
| Safety context | Product targets include SIL3 and PL e/Cat.4 depending on configuration. | Product + _Integrator_ |  High safety impact if safety assets are compromised. | Confirmed |
| Included product scope |  Product-level cybersecurity analysis for COM, SCPU, IPC, field interfaces and IoTCore interface. _COM, SCPU, SysCom, DI/DO, IPC, update path, local interfaces, IoTCore interface._| Product |  Defines analyzed modules and interfaces. | Confirmed |
| Excluded system scope |  Complete plant/network architecture risk treatment, third-party PLC hardening and customer-specific remote access are out of scope. | Operator/Integrator |  External dependencies must be documented separately. | Confirmed |
| Environment assumption | Operation is assumed in an IEC EN 62443-1-1 compliant environment with additional system-side measures.| Operator/Integrator |  Limits product-level treatment; environmental requirements required and must stay explicit in customer documentation.  | Confirmed |

| Exposure | Typical deployment is fieldbus level / machine network / cell level. Direct internet exposure is not intended. | Operator/Integrator | _Defines likelihood assumptions for network attacks; a scenario where this assumption does not hold is tracked separately_  ??| 

| Physical protection | Physical protection is part of operator responsibility based on risk analysis. | Operator/Integrator | Local manipulation risks (rotary switches, debug points, wiring, power, indicators) require external controls| 

| Trust assumption TB1 / | A compromised communication channel must not directly affect the Safety Domain. (external Ethernet / IoT / engineering access into the COM domain.) | Product | Confirmed as architectural intent 

| Trust assumption TB2 | The Safe CPU detects manipulated data from the COM module. _COM domain into SCPU over SysCom._ | Product | Drives internal data validation requirements.| 

| Trust assumption TB3 | The Safe CPU does not trust Shared Flash but verifies the firmware image itself. _COM-managed update-container handling into safe firmware installation via the shared update flash_ | Product | Drives secure update verification requirements | 

_| IoT access control assumption | Authenticated or role-based IoT service controls are present. | Product | Would reduce IF-03 likelihood. | Not evidenced (Open issue) |_

_| Update authenticity assumption | Cryptographic authenticity checks (signature policy) are present for update acceptance. | Product | Would reduce IF-03/IF-05 integrity risk. | Not evidenced (Open issue) |_

_| Debug lock assumption | Production lock/disable is implemented for debug paths. | Product | Would reduce IF-09 privilege risk. | Not evidenced (Open issue) |_

_| GSDML trust assumption | GSDML runtime exchange integrity is protected by local checks; toolchain trust is externally governed. | Shared | Affects IF-01 configuration threats. | Partial: runtime checks evidenced, supply-chain controls not evidenced |_


_| Trust boundary `TB-FIELD` (added in this revision) | Local field wiring access at the DI and DO ports is a distinct boundary from the COM/IoT and update boundaries. | Operator/Integrator | Drives IF-06/IF-07 rationale; kept separate from TB1-TB3 because the attack path, preconditions and controls differ materially. | Derived for this consolidation |_

_| Trust boundary `TB-LOCAL-SERVICE` (added in this revision) | Local physical access to rotary switches, debug points, power supply and visual indicators is a distinct boundary from the network-facing and field-wiring boundaries. | Operator/Integrator | Drives IF-08/IF-09/IF-10/IF-11 rationale. | Derived for this consolidation |_



| Topic | Product responsibility | System / operator / integrator responsibility |
| --- | --- | --- |
| PROFIsafe integrity and fallback | Yes. | No. |
| Configuration completeness, iParCRC, parameter dependency checks | Yes. | No. |
| Update mode gating by rotary-switch value and reboot | Yes. | Operator must control physical access to the switch and reboot event. |
| Firmware authenticity policy | TBD. Current documentation only proves compatibility and consistency checks. | Shared — deployment alone cannot compensate for missing product authenticity checks. |
| IoTCore reachability and firewall placement | Product only documents assumptions; it does not document compensating internal access control. | Yes, primarily system responsibility. |
| Controller / F-Host hardening | No. | Yes. |
| Physical protection of field wiring, debug access, and local service access | Partially, where the product can lock or document interfaces. | Yes, primarily. |
| DI/DO fault detection and safe-state behavior | Yes. | External actuator/sensor selection and wiring remain system responsibilities. |
| Power-quality protection | Product-side detection/protection is documented. | Installation quality and daisy-chain loading remain system responsibilities. |

## Assets

| Asset ID | Asset | Description | Primary objectives | Revised interpretation | Typical affected resources|
| --- | --- | --- | --- | --- | --- |
| A | Trusted Safety Function | SRIO correctly executes intended safety function. | Integrity, Availability | Do not classify as directly compromised when documented response is fail-safe stop/fallback only. | Safe CPU, SysCom, DI/DO, PROFIsafe channel | 

| B | Integrity of Safety Configuration | Safe behavior is determined by intended configuration. | Integrity, Authenticity | Covers correctness of F-Parameters, iParameters, and the device's own F_Dest address handling. | Safe CPU, SysCom, CPU3/COM, PROFINET parameterization|

| C | Integrity and Authenticity of Safety-Relevant Process Data | Input/output/PROFIsafe data represent true safety state. | Integrity, Authenticity, Availability | Directly impacted where safe communication or DI/DO truth is attacked. | Safe CPU, SysCom, CPU3/COM, PROFIsafe channel, DI/DO |
| D | Authenticity and Integrity of Safety Software | Bootloader/firmware remain authentic and unmodified. | Authenticity, Integrity | *High concern due to missing documented cryptographic authenticity policy.* | Safe CPU, COM CPU, Shared Flash, IoT interface, update workflow |
| E | Integrity of Safety Monitoring | Diagnostics, plausibility checks, self-tests,and fault responses remain trustworthy.  | Integrity, Availability | Directly impacted by diagnostics tampering, monitoring faults, and observability trust issues. | Safe CPU, SysCom, diagnostics, watchdog|
| F | Separation of Safety and Non-Safety Domain | COM compromise must not violate safety-domain integrity. | Integrity, Isolation, Availability |  Used only where the documented COM-to-SCPU split, black-channel assumptions, SysCom boundary, or update-handover boundary are directly challenged. Not used merely because two functions reside on neighboring blocks.| Safe CPU, SysCom, COM, IoT, Shared Flash |
| G | Integrity of Operating Mode | Test and update functions must not be activated or used without authorization. | Integrity, Authenticity, Availability | Direct for update/test mode abuse and local mode-switch manipulation. |  Rotary switches, IoT service functions, update mode, COM/SCPU control path |
| H | SRIO Functionality | Availability of SRIO functionality is maintained. | Availability, Fail-safe behavior | Primary direct impact in many detected-attack/fallback scenarios. | Power supply, COM, SCPU, network channels, field I/O |

## Interfaces

| Interface ID | Interface / Boundary | Type | Direction | Protocol / Medium | Relevant data flows | Trust boundary | Affected assets (revised tendency) | Open points |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IF-01 | Ethernet / PROFINET | External | Bidirectional | PROFINET over Ethernet M12 D-coded | | Cyclic/acyclic PROFINET communication, parameterization, network services | External -> COM | B, C, H (F/A mostly indirect) | COM CPU, NetX90, PROFINET channel 


| IF-02 | PROFIsafe over PROFINET | External logical safety channel | Bidirectional | PROFIsafe black channel over PROFINET | Safety process data, F-Host communication  | External -> COM -> SCPU | C, H (A mostly indirect via fail-safe behavior) |  PROFIsafe channel, COM, SCPU, SysCom |  | `TB-EXT-COM`; `TB-COM-SAFETY` | SCPU PROFIsafe stack, COM transport path | 


| IF-03 | IoTCore service interface | External | Bidirectional | HTTP/JSON service interface |  Diagnostics, monitoring, error log, firmware update handling, device information | External -> COM | D, G, H (E/F conditional) | | `TB-EXT-COM` | COM CPU3, IoTCore app, COM-side firmware/update services | IoT interface, COM CPU, Shared Flash | 



| IF-04 | SysCom | Internal | Bidirectional | SPI (COM/CPU3 <-> SCPU) | Config transfer, cyclic data, diagnostics, update trigger | COM -> Safety |A, B, C, D, E, F, G, H | None material. | Configuration data, process data, diagnostics, update trigger, firmware reference | `TB-COM-SAFETY` (primary COM-to-safety boundary) | COM CPU3, SCPU CPU1, SPI transport | SysCom, COM, SCPU |


| IF-05 | Shared Flash update path | Internal | Bidirectional | Shared non-volatile update storage | Safe container handover, version metadata Write/read firmware image, version information | COM <-> shared update path <-> SCPU | D, G, H (F conditional) |. || `TB-COM-FLASH-SAFETY` | Shared update flash, COM update container handling, SCPU update loader | Shared Flash, COM, SCPU | 



| IF-06 | Safety input terminals | External local field | Input to SRIO | 24V F-DI | Sensor states, DI diagnostics | Field boundary | C, E, H (A indirect) | | DI module, SCPU input processing  | DI, SCPU |


| IF-07 | Safety output terminals | External local field | Output from SRIO | 24V binary F-DO, associated supply  | Actuator commands, safe switch-off path | Field boundary | C, E, H (A indirect) | Actuator commands, safe switch-off, maintained OFF state | `TB-FIELD` | DO module, SCPU output control | DO, SCPU |


| IF-08 | Rotary switches | External local | Input to SRIO | Physical local switch  | F-address, update-mode selection | Local physical boundary | B, G, H || Addressing / update mode / function selection | `TB-LOCAL-SERVICE`; read only during init | SCPU rotary-switch readout and operating-state logic | Rotary switches, SCPU |


| IF-09 | JTAG / debug interfaces | Internal/service local | Local physical | Debug/service access | Debug, memory/firmware access | Physical/service boundary | D, H (others conditional) | CPU debug access, firmware/memory inspection or manipulation | `TB-LOCAL-SERVICE`; development-only intent | Debug/flash access for each controller, COM debug points | JTAG per CPU, SCPU, COM CPU |


| IF-10 | Power supply / daisy-chain | External physical | Supply input/output | US/UA supply | Device and I/O supply paths | Installation boundary | H (A/E mostly indirect) | Downstream daisy-chain current not measured by SRIO. | `TB-LOCAL-SERVICE` / installation boundary | PS, COM, SCPU, DI, DO |Power supply, field supply || 


| IF-11 | LED status indication | External local | Output from SRIO | Local indicators | Status visibility/observability | Local observation boundary | E/H indirect only | 
|| `TB-LOCAL-SERVICE`; local observation only | COM LEDs and SCPU LEDs | LEDs, diagnostics |


| IF-12 | IPC SCPU1 <-> SCPU2 | Internal | Bidirectional | Internal cross communication |1oo2 cross-communication and plausibility monitoring | Safety internal boundary | E, H (A/C indirect) | SCPU1, SCPU2, watchdog-related cross-checking || SCPU1, SCPU2, IPC, watchdog | No external access path is documented for this interface by itself. | 

## Risk Matrix

| Impact \\ Likelihood | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 | 2 | 3 | 4 | 5 |
| 2 | 2 | 4 | 6 | 8 | 10 |
| 3 | 3 | 6 | 9 | 12 | 15 |
| 4 | 4 | 8 | 12 | 16 | 20 |
| 5 | 5 | 10 | 15 | 20 | 25 |

### Risk-level formula

Low: 1-4; Medium: 5-9; High: 10-15; Critical: 16-25

### Risk acceptance guidance

Residual Critical/High: explicit acceptance or further treatment required.
Medium: review and tracked justification required.
Low: acceptable with rationale.

## TARA

| TARA ID | Interface ID | Threat scenario | Attacked interface/component | Access/preconditions | Immediate cybersecurity effect | Existing control response | Direct product impact | Machine-level consequence | Affected assets (Direct / Indirect) | L | I | Risk | Level | Treatment direction | Verification evidence target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TARA-001 | IF-01 | Parameterization tampering | PROFINET config path via COM -> SCPU | Network/engineering access | Manipulated F-Params/iParams | SCPU completeness/CRC/dependency/F_Dest checks | Rejected config, blocked startup | Startup delay or inability | B,H / A,C | 2 | 4 | 8 | Medium | Keep strict SCPU validation authority | Negative config + CRC mismatch evidence |
| TARA-001 | IF-01 | PROFINET parameterization | Tampering | Attacker with access to the machine network, engineering path, or F-Host/PLC configuration path manipulates PROFINET parameterization (F-Parameters/iParameters) before or during commissioning. | B, H | A, C | Safety behavior depends on the intended configuration (B); rejected/invalid configuration blocks normal operation (H). A/C are only relevant if manipulated data were somehow accepted, which the documented SCPU checks are designed to prevent. | Configuration rejection, blocked or delayed startup, or need for re-parameterization; machine startup prevented until valid configuration is restored. | SCPU verifies completeness, iParCRC, parameter dependencies and F_Dest address consistency before activation; invalid configuration is rejected in Parametrization and raises EC3. | 2 | 4 | 8 | Medium | Keep SCPU-side configuration completeness/CRC/dependency/F_Dest validation mandatory at every startup and reconnection; document who is authorized to change configuration. | No evidence found for authenticated origin protection of PROFINET configuration traffic beyond the described validation checks. | Safety/Security | Open | Configuration rejection, CRC-mismatch and F_Dest-mismatch evidence from startup/parametrization tests. | 



| TARA-002 | IF-01 | PROFINET DoS/overload | COM/NetX90 fieldbus handling | Network traffic flood/malformed traffic | Link/service degradation | Fallback behavior + diagnostics | Availability loss/reconnect loops | Safe stop, downtime | H / F,A | 3 | 3 | 9 | Medium | Preserve deterministic fallback and diagnostics | Timeout/fallback behavior evidence |

| TARA-002 | IF-01 | PROFINET network services | Denial of Service | Attacker with fieldbus network access sends malformed or excessive PROFINET traffic to overload COM or the communication stack. | H | F, A | COM supports fieldbus communication and must not compromise the safety domain; the documented design intends non-safety COM failures to fail safe rather than directly corrupt the safety domain. | Availability loss, repeated reconnection attempts; safe stop or machine downtime caused by communication loss. | Communication loss triggers fallback from Operate to Parametrization; safe channels/ports switch to fail-safe state during fallback; COM reports diagnosis information. | 3 | 3 | 9 | Medium | Preserve deterministic fallback, timeout handling, and PROFINET diagnostics; define explicit robustness expectations for malformed traffic in the COM specification. | No evidence found for parser hardening, rate limiting, or protocol fuzz-robustness claims. | Product Security | Open | Communication-loss fallback evidence and COM-side diagnostic evidence. | 

| TARA-003 | IF-02 | PROFIsafe spoof/tamper | SCPU PROFIsafe path | Fieldbus attacker access | Invalid safe frame attempts | PROFIsafe safety mechanisms and handling | Invalid data rejected | Safe stop/downtime | C / A,H | 2 | 4 | 8 | Medium | Preserve certified stack + checks | Invalid telegram handling evidence |


| TARA-003 | IF-02 | PROFIsafe telegrams | Spoofing/Tampering | Attacker with fieldbus network access tampers with or spoofs PROFIsafe telegrams to alter safe input/output process data. | C | A, H | The attacked content is the safe process-data path itself; A/H are indirect because the documented behavior is safe-communication validation and fallback, not direct unsafe execution. | Invalid communication should be detected and not accepted as valid safe process data; safe stop or loss of function possible if communication is rejected or times out. | SRIO acts as PROFIsafe F-Slave with a certified PROFIsafe stack, 4-byte CRC-related F-parameter handling, and watchdog-related timing constraints. | 2 | 4 | 8 | Medium | Preserve certified PROFIsafe implementation, F-parameter checks, watchdog timing, and error classification. | None beyond the documented PROFIsafe mechanisms. | Safety/Security | Open | PROFIsafe certification evidence and invalid-frame handling evidence. | 

| TARA-004 | IF-02 | PROFIsafe availability loss | SCPU safe comm path | Interruption/repeated invalid comms | Safe comm not maintained | Timeout -> fallback/safe behavior | Operate state exit | Safe stop/downtime | C,H / A | 3 | 4 | 12 | High | Preserve timeout + operator-visible diagnostics | Timeout + fallback diagnostics evidence |

| TARA-004 | IF-02 | PROFIsafe communication availability | Denial of Service | Attacker interrupts, delays, or repeatedly invalidates PROFIsafe communication so it cannot remain active. | C, H | A | Safe process-data availability is interrupted (C); SRIO functionality is unavailable (H); A is indirect because the documented response is fail-safe rather than silent corruption. | SRIO leaves normal operation and enters fallback behavior; machine safe stop and downtime. | Communication timeout triggers fallback to Parametrization; fail-safe values applied; PROFIsafe timeout behavior handled by the stack. | 3 | 4 | 12 | High | Keep explicit timeout, fallback, and operator-visible diagnostics in the product and manual. | None material. | Safety/Security | Open | Timeout/fallback evidence and diagnostic evidence for safe-communication loss. | 

| TARA-005 | IF-03 | Read-only service information disclosure | IoT diagnostics/status endpoints | IoT reachability | Device/service info exposure | Read-only model; no documented auth model | No direct behavior manipulation | Recon support for follow-on attacks | none direct / D,E,G,H | 2 | 2 | 4 | Low | Restrict exposure and clarify environment constraints | Endpoint exposure review |
| TARA-005 | IF-03 | IoT diagnostics / monitoring | Information Disclosure | Attacker with network reachability to IoTCore reads device status, versions, network details, error log, or other documented read-only data. | *(none directly supported by A-H)* | D, E, G, H | The current asset set has no confidentiality-specific asset. Disclosed data can support follow-on attacks against software, diagnostics, service mode, or availability, but a direct product-level impact on A-H is not evidenced. | No direct manipulation of SRIO behavior is documented for this read-only disclosure path; primarily improved attacker reconnaissance for follow-on attacks. | Read-only IoT access for diagnostics and device information is documented; authenticated user access is not documented. | 2 | 2 | 4 | Low | Restrict IoTCore exposure to the intended machine network and document service-exposure constraints explicitly. | No evidence found for IoTCore authentication, authorization, or confidentiality controls. | Product Security | Open | Endpoint inventory and confirmation that documented read-only items match intended exposure. | 

| TARA-006 | IF-03 | Unauthorized update workflow use | IoT update path into COM/SCPU flow | IoT reachability + update-mode preconditions | Malicious/unauthorized update attempt | Rotary 999 gating + compatibility/consistency checks | Risk of unintended but compatible firmware install | Outage/altered behavior | D,G,H / F,A | 2 | 5 | 10 | High | Add documented authenticity policy | Update acceptance/rejection trace evidence |

| TARA-006 | IF-03 | IoT firmware update handling | Elevation of Privilege/Tampering | Attacker with IoT reachability plus update-mode preconditions (rotary-switch value `999` + reboot) attempts to upload and install an unauthorized or manipulated update container. | D, G, H | F, A | Firmware integrity is directly targeted (D); update mode is the attacked operating mode (G); update misuse can take the device out of service (H); F/A are indirect because malicious firmware could later challenge separation or safety execution, which is not itself documented. | Installation of unintended but "compatible" firmware remains a concern, since only compatibility/consistency checks are documented, not cryptographic authenticity; device outage, changed behavior, or later safety impact depending on installed firmware. | Update request accepted only in update mode; COM and SCPU perform compatibility and consistency checks; update state keeps I/Os in safe state. | 2 | 5 | 10 | High | Add documented authenticity protection for update containers and safe firmware; define an explicit accepted/forbidden downgrade policy for security cases. | No evidence found for cryptographic signature verification or anti-rollback protection. | Product Security | Open | Evidence of update-mode gating, compatibility rejection, and any future authenticity-check evidence. | 


| TARA-007 | IF-03 | Service/test function misuse | IoT service/FIT control surface | IoT service reachability | Unauthorized service invocation | Mode gating partly documented; no auth model evidenced | Availability/mode disturbance | Maintenance disruption | G,H / E | 3 | 3 | 9 | Medium | Restrict or justify production service exposure | Production service inventory evidence |
| TARA-007 | IF-03 | IoT test/service functions | Elevation of Privilege | Attacker with IoTCore reachability to service endpoints triggers service or test-related functions without authorization. | G, H | E | Test/update-related service use concerns operating-mode integrity (G); service misuse can disrupt device functionality (H); E is indirect because FIT/service use can interfere with diagnostics or maintenance interpretation. | Service misuse can affect availability or mode integrity even without directly corrupting safe process data; maintenance disruption, nuisance downtime, or unintended test activity. | IoTCore remains read-only for normal parameterization; update mode requires rotary-switch gating; a FIT service is documented in COM. | 3 | 3 | 9 | Medium | Document and implement explicit access restrictions for the FIT and update-related services. | No evidence found for access control on the FIT service or IoT service endpoints. | Product Security | Open | Service inventory evidence and confirmation which services remain enabled in production. | 

| TARA-008 | IF-03 | Parser/service handler compromise attempt | COM IoT request handling | Malformed/abusive request input | COM crash/compromise attempt | Architectural separation intent documented; parser hardening not evidenced | COM function loss, separation challenge | Downtime via comm loss | F,H / D,E,G | 3 | 4 | 12 | High | Define hardening expectations and surface minimization | Robustness/hardening evidence |
| TARA-008 | IF-03 | IoT HTTP/JSON parser | Tampering/DoS | Attacker with IoTCore reachability sends malformed JSON or unexpected requests to exploit the COM parser or service handler. | F, H | D, E, G | This is a direct attempt to compromise the non-safety domain that interfaces with the safety domain (F); COM compromise can stop SRIO communication (H); D/E/G become relevant only if the compromise is leveraged into update, diagnostics, or mode functions. | Loss of COM functionality and a direct challenge to the separation assumption; machine stop or unavailability if COM-side failure causes communication loss. | Architectural separation between non-safety COM and safety SCPU is documented; fail-safe handling for communication loss is documented; parser hardening is not documented. | 3 | 4 | 12 | High | Define and verify hardening expectations for the IoTCore application and minimize exposed production services. | No evidence found for parser hardening, memory safety, process isolation, or authenticated IoT request handling. | Product Security | Open | COM robustness evidence, production-service inventory, and separation-claim evidence. | 

| TARA-009 | IF-04 | SysCom config tampering | COM->SCPU acyclic config messages | COM compromise/boundary abuse | Manipulated config at safety boundary | SCPU config validation checks | Reject config, reduced availability | Startup delay/block | B / F,H,A | 2 | 4 | 8 | Medium | Keep SCPU validation independent | End-to-end config validation evidence |
| TARA-009 | IF-04 | SysCom configuration transfer | Tampering | Compromised COM (or manipulation of the SysCom configuration-transfer path) sends manipulated F-Parameters/iParameters to SCPU. | B | F, H, A | Safety configuration is the directly attacked object (B); F is indirect because the scenario challenges COM-to-safety separation; H/A depend on whether the manipulation is detected or somehow accepted. | Rejected configuration and loss of availability if manipulation is detected; machine startup blocked or delayed. | Configuration is transferred in defined messages; SCPU checks completeness, dependencies, CRC, and F_Dest address constraints before activation. | 2 | 4 | 8 | Medium | Keep SCPU as the sole authority for configuration acceptance. | None beyond the documented checks. | Safety/Security | Open | Evidence that every configuration path still ends in SCPU-side validation. | 

| TARA-010 | IF-04 | SysCom cyclic data tampering/replay/delay | Cyclic COM<->SCPU path | COM compromise/boundary manipulation | Cyclic safe data corruption/interruption | Timeout handling + PROFIsafe checks | Fallback/safe stop | Downtime | C,F,H / A | 2 | 4 | 8 | Medium | Preserve timeout and validated safe data handling | Replay/delay fault behavior evidence |
| TARA-010 | IF-04 | SysCom process data transfer | Tampering | Process data passed via SysCom is modified, replayed, delayed or reordered (COM compromise or direct SysCom manipulation). | C, F, H | A | Safe cyclic data is directly attacked (C); the COM-to-safety boundary is directly challenged (F); H because the documented response to communication interruption is fallback; A is indirect because the intended response is fail-safe. | Communication interruption or rejected cyclic data leading to fallback or safe stop; potential machine stop. | SysCom exchanges the PROFIsafe frame; COM IO-Delegator implements SPI timeout handling; PROFIsafe provides safe-communication checks. | 2 | 4 | 8 | Medium | Preserve timeout handling and ensure SCPU relies on validated PROFIsafe content rather than COM trust. | No evidence found for additional SysCom integrity protection independent of PROFIsafe checks. | Safety/Security | Open | Evidence of timeout/fallback behavior when cyclic SysCom data is corrupted or interrupted. | 

| TARA-011 | IF-04 | Diagnostic transfer tampering | SysCom ErrorEvent/diagnostics path | COM compromise | Hidden/delayed/altered diagnostics | ErrorEvent structure and reporting path | Misleading maintenance observability | Slower recovery | E / H | 2 | 2 | 4 | Low | Clarify authoritative diag hierarchy | Diagnostic consistency evidence |
| TARA-011 | IF-04 | SysCom diagnostics transfer | Repudiation/Tampering | COM hides, alters or delays diagnostic information (ErrorEvent) transferred to or from SCPU. | E | H | Diagnostic integrity is the directly attacked subject (E); H is indirect because degraded diagnostics can prolong downtime. | Misleading operator/maintenance diagnostics; slower fault localization or delayed recovery rather than immediate unsafe control. | ErrorEvent structure is documented; COM logs received ErrorEvents and forwards diagnosis information; safety-related error information also exists inside PROFIsafe status handling. | 2 | 2 | 4 | Low | Make explicit in documentation which diagnosis originates from SCPU and which from COM. | None material. | Product Security | Open | Consistency review between ErrorEvent content, visible diagnosis, and safety-communication status. | 



| TARA-013 | IF-04 | Unauthorized update trigger via boundary | SysCom update command path | COM compromise + command abuse | Unauthorized update attempt | SCPU checks update-mode preconditions | Unintended update handling | Downtime/disruption | G,D,H / F | 2 | 4 | 8 | Medium | Preserve SCPU precondition authority | Negative command path evidence |
 TARA-013 | IF-04 | SysCom update trigger | Elevation of Privilege | COM triggers update mode or related commands without authorization or under unsafe conditions (documented update mode still requires rotary-switch value `999`). | G, D, H | F | Update mode integrity is targeted (G); update behavior targets software handling (D); update entry interrupts normal function (H); F is indirect because a compromised COM uses the boundary to influence the safety domain. | Unintended update handling or service interruption; downtime or maintenance disruption. | SCPU evaluates update only when update mode is active; COM sends start signal only after update-container placement; update state keeps I/Os safe. | 2 | 4 | 8 | Medium | Keep SCPU-side evaluation of update preconditions independent from a COM request alone. | None beyond the documented gating. | Product Security | Open | Evidence that update commands are ignored when rotary-switch preconditions are not met. | 

| TARA-014 | IF-05 | Shared update payload tampering | Shared flash safe-container handover | COM/local service compromise | Modified payload before install | Compatibility/consistency checks only | Potential acceptance of modified payload | Outage/unsafe software assurance gap | D,G,H / F,A | 2 | 5 | 10 | High | Add authenticity checks for container path | Container verification evidence |
| TARA-014 | IF-05 | Shared Flash write firmware image | Tampering | Attacker (via COM compromise or local service access) modifies the safe firmware image/container stored in Shared Flash before SCPU reads/installs it. | D, G, H | F, A | Safety firmware is directly targeted (D); update mode is involved (G); update failure or misuse can disable the device (H); F/A are indirect because malicious installed firmware could later cross domains or affect safe execution, which is not itself documented. | Acceptance of modified but still "compatibility-consistent" firmware remains an open security concern; device misuse, later malfunction, or loss of safety assurance after update. | SCPU verifies compatibility and consistency of data transferred to shared update flash; update state is dedicated with documented safe-state behavior. | 2 | 5 | 10 | High | Add documented authenticity verification of safe containers and their metadata. | No evidence found for cryptographic signature validation of the safe container. | Product Security | Open | Evidence of future authenticity checks, plus current compatibility/consistency rejection evidence. | 


| TARA-015 | IF-05 | Version metadata abuse/downgrade forcing | Shared flash version path | Same as TARA-014 | Downgrade or update-block attempt | Compatibility checks; downgrade allowed | Potential older firmware acceptance | Increased residual exposure/downtime | D,G,H / - | 2 | 4 | 8 | Medium | Define security-aware version policy | Version policy enforcement evidence |
| TARA-015 | IF-05 | Shared Flash version information | Tampering | Version/metadata is manipulated to force a downgrade or block an update. | D, G, H | – | Software-version control is the attacked object (D); update mode and version policy are affected (G); blocked or unsuitable update paths affect device operability (H). | Installation of an older but "compatible" firmware remains allowed by the documented requirements; reintroduction of a previously fixed weakness or a certification/maintenance mismatch. | Compatibility checks are documented; downgrade is explicitly allowed for safe application firmware. | 2 | 4 | 8 | Medium | Decide and document whether security-relevant downgrade should remain allowed, and under which constraints. | No evidence found for anti-rollback enforcement. | Product Security | Open | Version-policy review and evidence of operator documentation for downgrade responsibilities. |

| TARA-016 | IF-05 | Update storage corruption/exhaustion | Shared update storage | Repeated/aborted update attempts | Incomplete/invalid update state | Staged update and checks, safe-state behavior | Update failure / unavailability | Maintenance delay | D,H / G | 2 | 3 | 6 | Medium | Clarify recovery behavior | Failed-update recovery evidence |
| TARA-016 | IF-05 | Shared Flash exhaustion/corruption | Denial of Service | Repeated update attempts or flash corruption leave an invalid or incomplete update state. | D, H | G | Update payload/state is corrupted (D); failed update handling affects SRIO availability (H); G is indirect because the device remains in update-related handling. | Failed update and temporary or persistent device unavailability; maintenance delay and machine downtime. | Update flow is staged with documented compatibility/consistency checks; update state is dedicated and I/Os stay safe. | 2 | 3 | 6 | Medium | Clarify recovery behavior for incomplete update state and preserve safe-state handling during interruption. | No evidence found for atomic rollback or storage wear-handling details. | Product Security | Open | Evidence of failed-update detection and recovery guidance. | 


| TARA-017 | IF-06 | Field input spoof/short/tamper | DI terminals and SCPU DI processing | Local field wiring access | False DI state or channel faults | DI diagnostics/testpulse/qualifier/safe-state handling | Passivation/bad qualifier/input loss | Stop/inhibited restart | C,E,H / A | 3 | 4 | 12 | High | Preserve DI diagnostic and wiring guidance | DI fault simulation evidence | | TARA-017 | IF-06 | Safe digital inputs | Tampering/Spoofing | Attacker with physical access to field wiring, connected sensors, or DI port wiring causes false input states, shorts, cross-circuits, or wiring faults. | C, E, H | A | Safe input data is directly attacked (C); diagnostics and qualifier handling are directly involved (E); channel faults can make the function unavailable (H); A is indirect because the documented reaction is safe-state handling where faults are detected. | Passivation, bad qualifier, false inactive state, or loss of input availability; machine stop, inhibited restart, or (in a faulted case) an input not representing the actual field state. | DI module and SCPU document testpulse behavior, stuck-at-high testing, switchable sensor supply, supply-switch diagnosis, qualifier behavior, and safe-state reporting. | 3 | 4 | 12 | High | Preserve DI diagnostics, testpulse capability, and user documentation for valid sensor wiring and reactivation use. | None material. | Safety/Security | Open | Evidence of DI fault detection behavior, qualifier transition behavior, and documented use constraints. | 

| TARA-018 | IF-07 | Field output forcing/prevented switch-off | DO terminals and SCPU DO control | Local output wiring access | Forced/blocked actuation path | Watchdog + monitoring + safe-state behavior | Channel fault/unavailable actuation | Stop or actuation failure | C,E,H / A | 3 | 4 | 12 | High | Preserve output monitoring and safe deactivation | DO fault behavior evidence | | TARA-018 | IF-07 | Safe digital outputs | Tampering/Spoofing | Attacker with physical access to output wiring or the attached actuator path forces an output state, prevents switch-off, or manipulates the external actuation path. | C, E, H | A | Safe output command fidelity is directly affected (C); monitoring and qualifiers are involved (E); the port can become unavailable (H); A is indirect because the documented response is deactivation/safe-state behavior when faults are detected. | Channel fault, forced passivation, or inability to achieve intended actuation; machine stop or failure to actuate as intended (danger depends on the external actuator/machine design). | DO module and SCPU document watchdog support, switch-off capability, voltage/current monitoring, qualifier handling, logic tables, and documented safe state (outputs inactive/high impedance). | 3 | 4 | 12 | High | Preserve actual-vs-commanded evaluation, watchdog-based fail behavior, and external-wiring restrictions in the manual. | None material. | Safety/Security | Open | Evidence that detected DO faults force bad qualifier and inactive output state. | 


| TARA-019 | IF-08 | Rotary switch mode/address tampering | Local rotary-switch path | Physical access before cold start | Wrong F_Dest or forced update mode | Init-only read + validity handling | Wrong mode/address or blocked operation | Commissioning/operation disruption | B,G,H / - | 2 | 4 | 8 | Medium | Keep init-only semantics and physical controls | Cold-start/value-handling evidence |  TARA-019 | IF-08 | Rotary switches addressing/mode | Tampering | Local attacker changes the rotary switches (before the next cold start/update cycle) to alter F_Dest address, update mode, or function selection. | B, G, H | – | The device's own safe address is configuration-relevant (B); update mode is directly controlled here (G); wrong address or mode can prevent operation (H). | Startup in wrong mode, wrong-address acceptance attempt, or blocked operation; machine cannot communicate correctly with the intended F-Host or enters update handling unexpectedly. | Rotary value is only read during initialization; `1...899` is a valid F_Dest address, `999` requests update mode, other values cause documented configuration-error behavior. | 2 | 4 | 8 | Medium | Preserve init-only read behavior and document physical-protection expectations clearly. | No evidence found for tamper detection on the rotary-switch sleeves or caps. | Product + Operator | Open | Evidence that changed rotary values are only applied after cold start and that invalid values trigger the documented error path. | 


| TARA-020 | IF-09 | Debug path privilege escalation | JTAG/debug and flash interfaces | Physical service access | Firmware read/modify/reset abuse | Dev-only intent documented; production lock not evidenced | Software compromise/unavailability | Out-of-service/reprogramming risk | D,H / G,F,A,B,C,E | 2 | 5 | 10 | High | Add auditable production lock proof | Production lock evidence |  TARA-020 | IF-09 | JTAG/debug interfaces | Elevation of Privilege | Attacker with physical service access to debug contacts/connectors reads or modifies firmware/memory. | D, H | G, F, A, B, C, E | Firmware manipulation is explicitly possible through debug/flash paths (D); reset/flash actions interrupt service (H); the broader assets become conditional because arbitrary debug access could later influence them, but those follow-on behaviors are not documented in detail. | Firmware/software compromise or service unavailability; device taken out of service or reprogrammed. | Requirements state debug/test interfaces shall only be usable during development and shall be blocked after development, but the implemented production-lock mechanism itself is not documented. | 2 | 5 | 10 | High | Provide auditable evidence of production lock, disable, fuse, or equivalent debug restriction for all controllers. | No evidence found for a production-lock implementation for debug access. | Product Security | Open | Production configuration evidence showing debug/test lock-down. | 


| TARA-021 | IF-10 | Power manipulation DoS | Supply input/output path | Physical supply manipulation | Brownout/reset/overvoltage faults | Voltage/current protections and monitoring | Reset/shutdown/function loss | Safe stop/downtime | H / A,E | 2 | 4 | 8 | Medium | Preserve supply monitoring and install constraints | Brownout/overvoltage handling evidence |
 | TARA-021 | IF-10 | Power supply / daisy-chain | Denial of Service | Attacker with physical access to power input/output/supply conditions causes brownout, reset, reverse-polarity, overvoltage, or overcurrent. | H | A, E | Supply manipulation immediately affects SRIO availability (H); A/E are indirect because the documented design responds with shutdown, diagnosis, and safe-state behavior rather than silent unsafe behavior. | Device reset, shutdown, or local function loss; safe stop or machine downtime. | Voltage detection, overvoltage protection, reverse-polarity protection, hardware shutoff thresholds, overcurrent detection, and safe-state behavior are documented. | 2 | 4 | 8 | Medium | Preserve documented supply monitoring and keep installation constraints explicit in the user documentation. | None material. | Operator + Product | Open | Supply-fault detection evidence and documented installation constraints. | 

| TARA-022 | IF-11 | Misleading status indication | LED indications | Local observation | Misinterpreted status / limited disclosure | LEDs non-safety informational role | No direct control-path effect | Delayed diagnosis | none direct / E,H | 2 | 1 | 2 | Low | Keep LED non-authoritative rule explicit | Documentation consistency review |
| TARA-022 | IF-11 | LED status indication | Information Disclosure/Tampering | Local observer misinterprets status LEDs, or LEDs provide limited operational information to an unauthorized observer. | *(none directly supported by A-H)* | E, H | The current asset set has no confidentiality-specific asset; E/H are only indirect because LEDs influence interpretation, not the authoritative safety control path — the documentation explicitly treats LEDs as non-safety information. | No documented direct control-path effect on SRIO behavior; slower diagnosis or operator misunderstanding. | The manual states LED use is non-safety-related; several LED functions are informational only. | 2 | 1 | 2 | Low | Keep the manual warning that LEDs are not the safety-truth source. | No evidence found for software-driven falsification of LED behavior beyond their documented state mapping. | Product Security | Open | Documentation review and confirmation that safety decisions do not depend on LED state alone. | 

| TARA-023 | IF-12 | Internal cross-communication inconsistency | SCPU1<->SCPU2 IPC/watchdog coordination | Internal fault/indirect compromise route | Inconsistent safety coordination | 1oo2 cross-check + watchdog + fatal-error handling | Safe stop/availability loss | Maintenance intervention | E,H / A,C | 1 | 4 | 4 | Low | Preserve independent watchdog/cross-checking | IPC inconsistency handling evidence | | TARA-023 | IF-12 | IPC SCPU1-SCPU2 cross communication | Tampering/DoS | Internal cross-communication is corrupted, delayed or inconsistent between both safe CPUs (no direct external interface is documented for this path; practical exploitation would require compromise of internal safety logic or service-level access through another interface). | E, H | A, C | Monitoring and internal coordination are the attacked subject (E); detected inconsistency can stop operation (H); A/C are indirect because the intended response is safe fault handling instead of silent unsafe operation. | Fatal error or loss of availability if inconsistency is detected; safe stop or maintenance intervention. | The safety architecture uses two safety controllers, cross-checking logic, watchdog functionality, self-tests, and fatal-error handling. | 1 | 4 | 4 | Low | Maintain independent watchdog and cross-checking as documented. | No evidence found for an external direct access path to IF-12 itself. | Safety/Security | Open | Evidence that inconsistent SCPU coordination leads to documented fatal-error handling. | 


| TARA-024 | IF-01/03 | Untrusted network exposure condition | External reachability condition | Misdeployment/exposure | Increased attack surface likelihood | Environmental assumptions only | No direct state change alone | Follow-on attack probability increase | none direct / D,E,F,G,H | 3 | 2 | 6 | Medium | Treat as system responsibility, keep constraints explicit | Security manual/environment checklist | | TARA-024 | IF-01/03 | External network reachability | Spoofing/Elevation of Privilege | Product is deployed contrary to the intended restricted machine-network environment, or is reachable from a broader untrusted network (unsecured network connection / IoT interface reachable from an untrusted network). | *(none directly supported by A-H)* | D, E, F, G, H | This is a system-level exposure condition. It increases the likelihood of attacks against COM, update, diagnostics, and availability, but does not by itself directly corrupt an asset. | None until another exploit path is used; elevated probability of remote follow-on attacks. | Documentation states the use case is assumed behind a firewall, with restricted network access and update performed by a trustworthy person. | 3 | 2 | 6 | Medium | Treat this primarily as a system responsibility and keep the network-placement assumptions explicit in the manual. | No evidence found for product-side network hardening sufficient to replace the documented firewall/restricted-network assumption. | Operator + Product | Open | Manual review showing clear environmental constraints and update/operator assumptions. | 


| TARA-025 | IF-01/02 | Upstream controller/F-Host compromise | Trusted upstream dependency | PLC/F-Host/engineering compromise | Malicious but protocol-conform data/commands | Local parameter/protocol checks only | Wrong intent can still drive behavior | Unsafe system behavior or downtime | B,C / A,H | 2 | 5 | 10 | High | Preserve trust-boundary documentation + local checks | Commissioning/trust-assumption evidence | | TARA-025 | IF-01/02 | Controller/F-Host dependency | Spoofing/Tampering | Upstream PLC, F-Host, or engineering system that legitimately talks to SRIO is compromised and sends malicious but protocol-conformant configuration or process-data commands. | B, C | A, H | SRIO consumes safety configuration and safe process-data content from the upstream controller (B, C); A/H depend on whether the malicious input is rejected or accepted as protocol-valid but semantically wrong from a system perspective. | Incorrect upstream intent can still drive SRIO behavior within the permitted protocol model, or cause rejected configuration if inconsistent; unsafe machine behavior or downtime depending on what the compromised controller commands and what SRIO checks reject. | SCPU validates configuration structure, iParCRC, dependencies, and F_Dest addressing; PROFIsafe handles safe-communication integrity. Controller hardening itself is outside SRIO product scope. | 2 | 5 | 10 | High | Keep controller/F-Host trust assumptions explicit and preserve all SCPU-side validation of what can be validated locally. | No evidence found that SRIO can independently verify the semantic correctness of controller commands beyond documented parameter and protocol checks. | Operator + Product | Open | Documentation review of trust assumptions and SCPU validation coverage. |

## Requirements

| Req ID | Related TARA IDs | Requirement | Type | Target / owner | Status |
| --- | --- | --- | --- | --- | --- |
| SRIO-CS-001 | TARA-001,009,025 | SCPU shall remain the authority for safety-configuration acceptance and verify completeness, iParCRC, dependencies, and F_Dest consistency. | Product control | Safety/Security | Supported |
| SRIO-CS-002 | TARA-003,004,010 | PROFIsafe integrity/timeout failures shall lead to deterministic fallback, safe-state behavior, and diagnostics. | Product control | Safety/Security | Supported |
| SRIO-CS-003 | TARA-005,007,008,024 | IoTCore exposure model shall be explicit; if no authentication exists, restricted-network assumptions shall be mandatory external constraints. | Shared control | Product + Operator | Partial / Gap |
| SRIO-CS-004 | TARA-006,013,019 | Update mode entry shall remain constrained by documented local preconditions (including rotary-switch gating and reboot semantics). | Product control | Product Security | Supported |
| SRIO-CS-005 | TARA-006,014,015,016 | Firmware update acceptance shall include documented authenticity policy in addition to compatibility/consistency checks. | Product control | Product Security | Open issue |
| SRIO-CS-006 | TARA-008,009,010,011 | COM-to-SCPU boundary shall preserve fail-safe behavior so COM faults cannot silently override SCPU safety decisions. | Product architecture | Safety/Security | Supported intent; evidence gap |
| SRIO-CS-007 | TARA-017,018,021 | DI/DO/supply faults shall produce documented safe-state, qualifier, and diagnostics behavior. | Product control | Safety | Supported |
| SRIO-CS-008 | TARA-020 | Debug/test interfaces shall have verifiable production lock-down or explicit validated physical/service compensations. | Product + process | Product Security | Open issue |
| SRIO-CS-009 | TARA-019,024,025 | Documentation shall state system responsibilities for segmentation, restricted access, trusted controller context, and physical protection. | System/process | Operator/Integrator | Supported |
| SRIO-CS-010 | TARA-011,022 | Diagnostic truth hierarchy shall keep safety-path status authoritative over local indicators. | Product + documentation | Product Security | Supported |
| SRIO-CS-011 | TARA-007 | Production enablement of FIT service shall be justified, restricted, or removed. | Product/process | Product Security | Open issue |
| SRIO-CS-012 | TARA-001,025 | GSDML runtime configuration influence is in scope; toolchain trust controls (generation/distribution/integrity governance) shall be explicitly allocated to process/system responsibilities unless product controls are documented. | Shared scope control | Product + Operator/Process | Partial / Gap |

| Req ID | Related TARA IDs | Requirement | Rationale | Target / owner | Verification approach | Status | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SRIO-CS-001 | TARA-001, TARA-009, TARA-025 | SCPU shall remain the sole authority for safety-configuration acceptance and shall verify completeness, iParCRC, parameter dependencies, and F_Dest address consistency before activation. | Protects asset B and supports the `TB-COM-SAFETY` trust assumption. | Safety/Security | CRC/signature mismatch tests; commissioning validation. | Supported (already documented/implemented). | 
| SRIO-CS-002 | TARA-003, TARA-004, TARA-010 | SRIO shall continue to treat PROFIsafe integrity and timeout failures as safe-communication faults leading to documented fallback, safe-state, and diagnostics behavior. | Protects C, A and H. | Safety/Security | Invalid-telegram and timeout tests. | Supported (already documented/implemented). | 
| SRIO-CS-003 | TARA-005, TARA-007, TARA-008, TARA-024 | IoTCore service endpoints shall require appropriate authentication/authorization and robust input validation; until implemented, the restricted machine-network and trustworthy-operator assumptions shall be treated as mandatory external constraints and stated explicitly in customer documentation. | Protects G, E, F and H. | Product Security | Authorization tests; API fuzzing; negative tests; interim security-manual review. | Open – authentication/authorization not yet implemented; environmental compensating constraint documented. | 
| SRIO-CS-004 | TARA-006, TARA-013, TARA-019 | Update mode shall only be entered under the documented local preconditions, including rotary-switch value `999` and reboot into update state. | Protects D and G; implements `TB-COM-FLASH-SAFETY`. | Product Security | Mode-authorization tests; update-trigger negative tests. | Supported (already documented/implemented). | 
| SRIO-CS-005 | TARA-006, TARA-014, TARA-015, TARA-016 | Firmware update acceptance for COM and SCPU shall include a documented authenticity policy (cryptographic signature/anti-rollback) in addition to the already documented compatibility and consistency checks. | Protects D and G; closes the TB3/`TB-COM-FLASH-SAFETY` authenticity gap. | Product Security | Signature, corrupted-image and downgrade tests. | Open – cryptographic authenticity/anti-rollback not documented. |
| SRIO-CS-006 | TARA-002, TARA-008, TARA-009, TARA-010, TARA-011 | The COM-to-SCPU boundary shall continue to enforce a fail-safe model where COM-side faults or compromise cannot silently override SCPU safety decisions; harden the COM domain so a compromised external communication channel cannot directly affect safety-domain integrity. | Protects F and follows `TB-EXT-COM`/`TB-COM-SAFETY`. | Product Security | Architecture review; penetration/fuzz tests; SysCom fault-injection and replay/delay tests; separation evidence. | Supported in architecture intent; implementation-hardening evidence (parser hardening, fuzzing) incomplete. | 
| SRIO-CS-007 | TARA-017, TARA-018 | Field I/O diagnostics shall continue to detect relevant wiring and signal faults and transition to defined safe state where required. | Protects A, C, E and H. | Safety | Field-fault simulation and diagnostics evidence. | Supported (already documented/implemented). | 
| SRIO-CS-008 | TARA-019, TARA-020 | Local physical/service interfaces shall be protected against unauthorized production use (documented production lock-down for debug/test interfaces) or explicitly documented as operator responsibility (rotary-switch physical protection). | Protects B, D, F, G and H. | Product + Operator | Production debug-lock evidence; security manual. | Open – debug production lock-down not documented; rotary-switch tamper protection remains operator responsibility. | 
| SRIO-CS-009 | TARA-021, TARA-024, TARA-025 | Customer documentation shall state environmental security requirements: segmentation, access control, secure remote access, physical protection, trusted controller context, and system-level risk assessment. | Addresses out-of-scope and operator-level dependencies. | Operator/Integrator | Security manual review; external requirement list. | Supported, but needs to remain explicit in every release of the manual. | 
| SRIO-CS-010 | TARA-011, TARA-022 | Authoritative diagnostic truth shall remain on the documented safety/control path, while LEDs and COM-side user-facing diagnosis remain clearly identified as secondary/informational. | Protects E and supports operator interpretation. | Product Security | Diagnostic consistency tests. | Supported (already documented/implemented). | 
| SRIO-CS-011 | TARA-007 | Production enablement of the IoT FIT service shall be explicitly justified, restricted, or removed. | Protects G and H against unauthorized test/service use. | Product Security | Service inventory review; production configuration check. | Open – production access policy for the FIT service not documented. | 


## Interface Asset Matrix
Legend (refined from a plain "X" marker to a direct/indirect distinction, since this materially changes how strongly an interface should be weighted per asset):

- `D` = direct interface relevance, supported by the supplied SRIO documentation.
- `I` = indirect or conditional relevance only (documented fail-safe/fallback response means the asset is only reached if that response does not work as intended).
- blank = not supported by the supplied SRIO documentation.



| Interface ID | Interface | A | B | C | D | E | F | G | H | Comment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IF-01 | Ethernet / PROFINET |  | D | D |  |  | I |  | D | Configuration/process-data/availability path in COM; no evidenced authenticated origin control. |
| IF-02 | PROFIsafe over PROFINET | I |  | D |  |  | I |  | D | Direct on safe communication data and availability; A mostly indirect through fail-safe behavior. |
| IF-03 | IoTCore service interface |  |  |  | D | I | I | D | D | Direct on update/mode/service surface; disclosure-only impact often indirect with current asset model. |
| IF-04 | SysCom | I | D | D | D | D | D | D | D | Primary safety boundary between COM and SCPU. |
| IF-05 | Shared Flash update path |  |  |  | D |  | I | D | D | Direct on software/update integrity and availability. |
| IF-06 | Safety input terminals | I |  | D |  | D |  |  | D | Direct on DI truthfulness, diagnostics, and availability. |
| IF-07 | Safety output terminals | I |  | D |  | D |  |  | D | Direct on DO actuation integrity, diagnostics, and availability. |
| IF-08 | Rotary switches |  | D |  |  |  |  | D | D | Direct on mode/address behavior; tamper detection not evidenced. |
| IF-09 | JTAG / debug interfaces | I | I | I | D | I | I | D | D | Direct on firmware/software and availability; broader impacts conditional. |
| IF-10 | Power supply / daisy-chain | I |  |  |  | I |  |  | D | Primarily availability; safety impact mostly indirect via fail-safe transition. |
| IF-11 | LED status indication |  |  |  |  | I |  |  | I | Informational boundary; direct control-path compromise not evidenced. |
| IF-12 | IPC SCPU1 <-> SCPU2 | I |  | I |  | D |  |  | D | Internal safety coordination and monitoring continuity. |

## Product vs. System Responsibility

## System Under Consideration – Confirmed Technical Facts

| Topic | Confirmed technical conclusion |
| --- | --- |
| COM domain | COM contains CPU3 and NetX90, handles PROFINET and IoTCore, and is explicitly described as non-safety-related. |
| Safety domain | SCPU handles PROFIsafe, DI, DO, monitoring, and watchdog functions. |
| COM-to-SCPU boundary | SysCom is the SPI-based communication path between COM and SCPU, with acyclic configuration, cyclic PROFIsafe frame exchange, ErrorEvent, and IoT-related data exchange. |
| Update architecture | Firmware update enters a dedicated update state, uses IoTCore upload on COM, stores an SRIO update container in COM flash, moves a safe container into shared update flash, and then lets SCPU install safe firmware. |
| Update mode gating | Update is only allowed when the rotary-switch value is `999`, followed by reboot into update state. |
| Fail-safe behavior | Communication loss, EC1, EC3, EC4, update state, and fatal error state all have documented safe-state or fallback behavior. |

## Confirmed Facts, Assumptions and Open Issues
| Type | Item | Assessment |
| --- | --- | --- |
| Confirmed fact | IoTCore is intended for non-safety-related functionality such as diagnostics, status, and firmware update. | Confirmed. |
| Confirmed fact | IoTCore parameter write access was removed; current statement says read-only access for IoTCore and no password currently required, while firmware update is gated by rotary-switch setting plus reboot. | Confirmed. |
| Confirmed fact | PROFIsafe is handled in SCPU; COM tunnels the safe communication via the black-channel principle. | Confirmed. |
| Confirmed fact | SCPU validates configuration by CRC and parameter dependency checks and rejects bad configuration in Parametrization. | Confirmed. |
| Confirmed fact | Rotary switches are only read during initialization. | Confirmed. |
| Confirmed fact | Update compatibility and consistency checks are documented for COM and SCPU. | Confirmed. |
| Confirmed fact | Downgrade of safe application firmware is explicitly allowed and documented. | Confirmed. |
| Open issue | Cryptographic authenticity of update containers or safe firmware is not documented in the supplied SRIO sources. | Open. No supporting evidence found. |
| Open issue | Authenticated or role-based access control for IoTCore service use is not documented in the supplied SRIO sources. | Open. No supporting evidence found. |
| Open issue | A documented production lock or disable mechanism for debug access is not present in the supplied SRIO sources, although debug use is stated to be development-only. | Open. |
| Open issue | The source workbook numbering is inconsistent: dashboard says 25 scenarios, but the supplied TARA IDs run `TARA-001` to `TARA-025` with `TARA-012` missing. | Open. Numbering gap preserved rather than silently renumbered. |



## Open Issues

1. Update authenticity is not documented. The supplied SRIO sources document compatibility and consistency checks, but not cryptographic authenticity checks for update containers or safe firmware. → `SRIO-CS-005`.
2. Anti-rollback protection is not documented. The supplied SRIO sources explicitly allow downgrade. → `SRIO-CS-005`.
3. IoTCore authentication and role separation are not documented; the current documentation instead relies on environment restrictions and read-only design assumptions. → `SRIO-CS-003`.
4. The production lock-down mechanism for debug access is not documented in the supplied SRIO sources. → `SRIO-CS-008`.
5. The production access policy for the documented FIT service is not documented. → `SRIO-CS-011`.
6. The original source-workbook TARA numbering is inconsistent because `TARA-012` is missing while the dashboard states 25 scenarios. → Tracked in [Dashboard](#dashboard) and kept as an explicit gap row in the TARA table.
7. The current asset set does not contain a confidentiality-specific asset, so pure read-only information-disclosure scenarios (`TARA-005`, `TARA-022`, `TARA-024`) cannot always be mapped directly to assets A-H without overstatement. → See [Missing Coverage and GSDML Scope Clarification](#missing-coverage-and-gsdml-scope-clarification).
8. GSDML runtime influence is in scope via `IF-01` and existing TARA scenarios, but no explicit product-level controls are documented for GSDML supply-chain trust (generation/distribution/integrity assurance in the engineering workflow). → No requirement currently assigned; needs an owner decision.