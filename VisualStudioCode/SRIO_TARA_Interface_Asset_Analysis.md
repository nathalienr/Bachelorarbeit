# SRIO TARA: Interface-Based Asset Analysis

> Converted from `SRIO_TARA_Interface_Asset_Analysis 1.xlsx`. The workbook content is reproduced below in Markdown format.

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

|  |  |
| --- | --- |
| Topic | Description |
| Purpose | Threat Analysis and Risk Assessment for SRIO focusing on interfaces, data flows and affected assets. |
| Method | Interface -> Asset -> Threat Scenario -> Impact/Likelihood -> Risk Treatment -> Residual Risk. |
| Scoring | Likelihood and Impact are rated 1..5. Risk Score = Likelihood x Impact. Levels: Low <=4, Medium 5..9, High 10..15, Critical >=16. |
| Important assumption | The document states SRIO product-level TARA does not replace plant/system-level risk assessment or operator environmental measures. |
| Source | Cybersecurity_Process.html, provided by user. Plain source reference is included in the Source columns and comments. |
| How to use | Review orange TBD/Review fields, adapt likelihood/impact in the TARA sheet, assign owners and due dates, then confirm residual risks. |

## Dashboard

### Metrics

| Metric | Value |
| --- | --- |
| Total TARA scenarios | 25 |
| Initial Critical | 2 |
| Initial High | 21 |
| Residual Critical | 0 |
| Residual High | 0 |
| Open items | 25 |
| Review items | 0 |

### Top interfaces by scenario count

| Interface ID | Scenario count |
| --- | --- |
| IF-04 | 5 |
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

| Category | Statement | Responsibility | TARA relevance | Source |
| --- | --- | --- | --- | --- |
| System | SRIO is a functionally safe remote I/O module in a PROFINET/PROFIsafe network, acting as safe gateway between sensors/actuators and F-Host. | Product | Defines protected system and safety role. | Cybersecurity_Process.html |
| Safety context | Safety context includes IEC 61508 SIL3 and EN ISO 13849-1 PL e Cat.4. | Product | High safety impact if safety assets are compromised. | Cybersecurity_Process.html |
| Included scope | Product-level cybersecurity analysis for COM, SCPU, IPC, field interfaces and IoTCore interface. | Product | Defines analyzed modules and interfaces. | Cybersecurity_Process.html |
| Excluded scope | Complete plant/network architecture risk treatment, third-party PLC hardening and customer-specific remote access are out of scope. | Operator/Integrator | External dependencies must be documented separately. | Cybersecurity_Process.html |
| Environment | Operation is assumed in an IEC EN 62443-1-1 compliant environment with additional system-side measures. | Operator/Integrator | Limits product-level treatment; environmental requirements required. | Cybersecurity_Process.html |
| Exposure | Typical deployment is fieldbus level / machine network / cell level. Direct internet exposure is not intended. | Operator/Integrator | Defines likelihood assumptions for network attacks. | Cybersecurity_Process.html |
| Physical protection | Physical protection is part of operator responsibility based on risk analysis. | Operator/Integrator | Local manipulation risks require external controls. | Cybersecurity_Process.html |
| Trust assumption TB1 | A compromised communication channel must not directly affect the Safety Domain. | Product | Drives separation and verification requirements. | Cybersecurity_Process.html |
| Trust assumption TB2 | The Safe CPU detects manipulated data from COM module. | Product | Drives internal data validation requirements. | Cybersecurity_Process.html |
| Trust assumption TB3 | The Safe CPU does not trust Shared Flash but verifies the firmware image itself. | Product | Drives secure update verification requirements. | Cybersecurity_Process.html |

## Assets

| Asset ID | Asset | Description | Primary protection objectives | Typical affected resources | Source |
| --- | --- | --- | --- | --- | --- |
| A | Trusted Safety Function | SRIO correctly executes its specified safety function. | Integrity, Availability | Safe CPU, SysCom, DI/DO, PROFIsafe channel | Cybersecurity_Process.html |
| B | Integrity of Safety Configuration | Safe behavior is determined by the intended configuration. | Integrity, Authenticity | Safe CPU, SysCom, CPU3/COM, PROFINET parameterization | Cybersecurity_Process.html |
| C | Integrity and Authenticity of Safety-Relevant Process Data | Input, output and PROFIsafe data correspond to the actual safety state. | Integrity, Authenticity, Availability | Safe CPU, SysCom, CPU3/COM, PROFIsafe channel, DI/DO | Cybersecurity_Process.html |
| D | Authenticity and Integrity of Safety Software | Bootloader and firmware remain authentic and unmodified. | Authenticity, Integrity | Safe CPU, COM CPU, Shared Flash, IoT interface, update workflow | Cybersecurity_Process.html |
| E | Integrity of Safety Monitoring | Self-tests, plausibility checks, diagnostics and fault responses remain trustworthy. | Integrity, Availability | Safe CPU, SysCom, diagnostics, watchdog | Cybersecurity_Process.html |
| F | Separation of Safety and Non-Safety Domain | A compromised COM system must not affect the integrity of the safety function. | Integrity, Isolation, Availability | Safe CPU, SysCom, COM, IoT, Shared Flash | Cybersecurity_Process.html |
| G | Integrity of Operating Mode | Test and update functions must not be activated or used without authorization. | Integrity, Authenticity, Availability | Rotary switches, IoT service functions, update mode, COM/SCPU control path | Cybersecurity_Process.html |
| H | SRIO Functionality | Availability of SRIO functionality shall be ensured. | Availability, Fail-safe behavior | Power supply, COM, SCPU, network channels, field I/O | Cybersecurity_Process.html |

## Interfaces

| Interface ID | Interface / Boundary | Type | Direction | Protocol / Medium | Relevant data flows | Trust boundary | Affected assets | Main resources | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IF-01 | Ethernet / PROFINET | External | Bidirectional | PROFINET over Ethernet M12 D-coded | Cyclic/acyclic PROFINET communication, parameterization, network services | TB1 External World -> COM | B, C, F, H | COM CPU, NetX90, PROFINET channel | Cybersecurity_Process.html |
| IF-02 | PROFIsafe over PROFINET | External logical safety channel | Bidirectional | PROFIsafe black-channel over PROFINET | Safety process data, F-Host communication | TB1 External World -> COM; TB2 COM -> Safety | A, C, F, H | PROFIsafe channel, COM, SCPU, SysCom | Cybersecurity_Process.html |
| IF-03 | IoTCore service interface | External | Bidirectional | HTTP/JSON | Diagnostics, monitoring, error log, firmware update handling, device information | TB1 External World -> COM | D, E, G, F, H | IoT interface, COM CPU, Shared Flash | Cybersecurity_Process.html |
| IF-04 | SysCom | Internal | Bidirectional | SPI between COM/CPU3 and SCPU | Configuration data, process data, diagnostics, heartbeat, update trigger, firmware reference | TB2 COM Domain -> Safety Domain | A, B, C, D, E, F, G, H | SysCom, COM, SCPU | Cybersecurity_Process.html |
| IF-05 | Shared Flash update path | Internal | Bidirectional | Non-volatile shared update flash | Write/read firmware image, version information | TB3 COM Domain <-> Shared Flash | D, F, G, H | Shared Flash, COM, SCPU | Cybersecurity_Process.html |
| IF-06 | Safety input terminals | External field local | Input to SRIO | 24V binary F-DI, associated supply | Sensor states, input diagnostics | Field device boundary | A, C, E, H | DI, SCPU | Cybersecurity_Process.html |
| IF-07 | Safety output terminals | External field local | Output from SRIO | 24V binary F-DO, associated supply | Actuator commands, safe switch-off, maintained OFF state | Field device boundary | A, C, E, H | DO, SCPU | Cybersecurity_Process.html |
| IF-08 | Rotary switches | External local | Input to SRIO | Physical local switch | Addressing / update mode / function selection | Local physical boundary | B, G, F, H | Rotary switches, SCPU | Cybersecurity_Process.html |
| IF-09 | JTAG / debug interfaces | Internal/service | Local physical | Debug/service access | CPU debug access, firmware/memory inspection or manipulation | Physical/service boundary | D, F, G, H | JTAG per CPU, SCPU, COM CPU | Cybersecurity_Process.html |
| IF-10 | Power supply / daisy-chain | External physical | Supply input/output | Device supply US/UA | Device supply, field I/O supply paths | Installation boundary | H, A | Power supply, field supply | Cybersecurity_Process.html |
| IF-11 | LED status indication | External local | Output from SRIO | Local indicator | Status indication and diagnostic observability | Local observation boundary | E, H | LEDs, diagnostics | Cybersecurity_Process.html |
| IF-12 | IPC SCPU1 <-> SCPU2 | Internal | Bidirectional | Internal cross communication | 1oo2 cross-communication and plausibility monitoring | Safety internal boundary | A, C, E, F, H | SCPU1, SCPU2, IPC, watchdog | Cybersecurity_Process.html |

## Risk Matrix

| Impact \\ Likelihood | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 | 2 | 3 | 4 | 5 |
| 2 | 2 | 4 | 6 | 8 | 10 |
| 3 | 3 | 6 | 9 | 12 | 15 |
| 4 | 4 | 8 | 12 | 16 | 20 |
| 5 | 5 | 10 | 15 | 20 | 25 |

### Risk-level formula

Low <=4; Medium 5..9; High 10..15; Critical >=16

### Risk acceptance

Residual Critical/High must be explicitly accepted or further treated. Medium requires review. Low may be accepted if justified.

## TARA

| TARA ID | Interface ID | Interface / Data Flow | Threat Category | Threat scenario | Affected Asset IDs | Affected asset rationale | Damage / impact description | Existing controls or assumptions from source | Likelihood (1-5) | Impact (1-5) | Initial Risk | Initial Level | Treatment decision | Recommended security requirement / mitigation | Residual Likelihood | Residual Impact | Residual Risk | Residual Level | Owner | Status | Verification / evidence | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TARA-001 | IF-01 | PROFINET parameterization | Tampering | Attacker manipulates PROFINET parameterization before or during commissioning. | B, A, H | Safety behavior depends on intended configuration. | Incorrect device behavior, loss of intended safety configuration, possible unavailable safe function. | Primary functional configuration by PLC/F-Host; Safe CPU is expected to validate manipulated data via TB2. | 3 | 5 | 15 | High | Mitigate | Validate safety-relevant configuration on SCPU with CRC/signature/consistency checks before activation. Reject invalid configuration and enter defined safe state. | 1 | 5 | 5 | Medium | Product Security | Open | Configuration negative tests; CRC mismatch tests; safe-state evidence | Cybersecurity_Process.html |
| TARA-002 | IF-01 | PROFINET network services | Denial of Service | Malformed or excessive PROFINET traffic overloads COM or communication stack. | H, F, A | COM supports fieldbus communication but must not compromise safety domain. | Loss of availability, delayed communication, potential fail-safe reaction. | Direct internet exposure not intended; deployment in fieldbus/cell network. | 3 | 4 | 12 | High | Mitigate | Rate-limit, robust input parsing, watchdog monitoring, and deterministic fail-safe behavior on communication loss. | 2 | 3 | 6 | Medium | Product Security | Open | Robustness/fuzz tests; network overload tests; watchdog behavior | Cybersecurity_Process.html |
| TARA-003 | IF-02 | PROFIsafe telegrams | Spoofing/Tampering | Spoofed or manipulated PROFIsafe telegrams attempt to alter safe input/output process data. | C, A, H | Process data must correspond to actual safety state. | Incorrect actuator command or reported sensor state. Potential safety function impact if not detected. | PROFIsafe used as black-channel protocol over PROFINET. | 2 | 5 | 10 | High | Mitigate | Rely on PROFIsafe safety mechanisms and verify integration assumptions; monitor communication errors and enter safe state on invalid telegrams. | 1 | 5 | 5 | Medium | Safety/Security | Open | PROFIsafe conformance evidence; invalid telegram tests | Cybersecurity_Process.html |
| TARA-004 | IF-02 | PROFIsafe communication availability | Denial of Service | Communication interruption or repeated invalid safety telegrams suppress normal safety communication. | H, A, C | SRIO functionality and safety data availability are affected. | SRIO enters fail-safe or unavailable state causing machine downtime. | Availability and deterministic fail-safe are protection objectives. | 3 | 4 | 12 | High | Mitigate | Define timeouts, safe-state behavior, diagnostic event logging and operator guidance for network outages. | 2 | 3 | 6 | Medium | Product Security | Open | Timeout validation; diagnostic event evidence | Cybersecurity_Process.html |
| TARA-005 | IF-03 | IoT diagnostics / monitoring | Information Disclosure | Unauthorized IoTCore access reads diagnostics, device information, error log or service data. | E, G, H | Diagnostics may expose system status and service capabilities. | Information gathering supports follow-on attacks or hides operational issues if combined with tampering. | IoTCore uses HTTP/JSON for service functions and can be reachable from operator network. | 4 | 3 | 12 | High | Mitigate | Authenticate service access, restrict endpoints by role, minimize sensitive data exposure, document required network segmentation. | 2 | 2 | 4 | Low | Product Security | Open | Access-control tests; endpoint review | Cybersecurity_Process.html |
| TARA-006 | IF-03 | IoT firmware update handling | Elevation of Privilege/Tampering | Unauthorized user triggers firmware update workflow or injects manipulated update container via IoT path. | D, G, F, H | Safety software and operating mode must remain authentic and authorized. | Execution of unauthorized software or unintended update mode, possible device outage. | Firmware update manipulation is listed as foreseeable misuse; TB3 assumes Safe CPU verifies firmware image. | 3 | 5 | 15 | High | Mitigate | Require authenticated/authorized update trigger; cryptographic signature and version checks; fail-safe rollback or rejection for invalid image. | 1 | 5 | 5 | Medium | Product Security | Open | Secure update tests; signature/downgrade tests | Cybersecurity_Process.html |
| TARA-007 | IF-03 | IoT test/service functions | Elevation of Privilege | Unauthorized use of service/test functions changes operating mode or influences safety behavior indirectly. | G, F, A, H | Test/update functions must not be activated without authorization. | Unauthorized operating mode change, degraded function availability or inhibited safety function. | IoTCore supports diagnostics, monitoring, update workflow and service functions. | 3 | 5 | 15 | High | Mitigate | Implement role-based access control, mode gating, local confirmation where needed, and audit logging. | 1 | 4 | 4 | Low | Product Security | Open | Authorization tests; mode transition tests | Cybersecurity_Process.html |
| TARA-008 | IF-03 | IoT HTTP/JSON parser | Tampering/DoS | Malformed JSON or unexpected requests exploit COM parser or service handler. | F, H, E | Compromised COM must not affect safety function; diagnostics integrity must remain intact. | COM compromise, service outage, potential attempt to cross into safety domain. | Compromised communication channel must not directly affect Safety Domain. | 4 | 4 | 16 | Critical | Mitigate | Harden parser, validate schema, apply memory-safe handling, fuzz test IoTCore endpoints, isolate process privileges. | 2 | 3 | 6 | Medium | Product Security | Open | Fuzzing report; static analysis; negative API tests | Cybersecurity_Process.html |
| TARA-009 | IF-04 | SysCom configuration transfer | Tampering | Compromised COM sends manipulated configuration data to SCPU over SysCom. | B, F, A | SysCom is the internal path from COM to safety domain. | Activation of incorrect safety configuration if SCPU does not detect manipulation. | TB2: Safe CPU detects manipulated data from COM module. | 3 | 5 | 15 | High | Mitigate | SCPU independently validates complete configuration integrity, sequence, source context and activation conditions. | 1 | 5 | 5 | Medium | Safety/Security | Open | SCPU validation tests; SysCom fault injection | Cybersecurity_Process.html |
| TARA-010 | IF-04 | SysCom process data transfer | Tampering | Process data passed via SysCom is modified, replayed, delayed or reordered. | C, A, F, H | Process data must correspond to actual safety state; safety/non-safety separation is critical. | Incorrect process image or fail-safe reaction; potential machine stop. | SysCom carries PROFIsafe process data and heartbeat information. | 3 | 5 | 15 | High | Mitigate | Use sequence counters, CRC/MAC where applicable, timeout monitoring, plausibility checks and safe-state fallback. | 1 | 5 | 5 | Medium | Safety/Security | Open | Replay/delay tests; sequence counter tests | Cybersecurity_Process.html |
| TARA-011 | IF-04 | SysCom diagnostics transfer | Repudiation/Tampering | COM hides, alters or delays diagnostic information transferred to or from SCPU. | E, H, F | Safety monitoring relies on diagnostics and fault responses. | Faults may be hidden from operator or incorrect status displayed. | Diagnostic information is a TB2 data flow and affects Safety Monitoring. | 3 | 4 | 12 | High | Mitigate | SCPU retains authoritative diagnostic state; signed/integrity-protected diagnostic records; consistency checks between local and network view. | 1 | 3 | 3 | Low | Product Security | Open | Diagnostic manipulation tests; event log consistency | Cybersecurity_Process.html |
| TARA-013 | IF-04 | SysCom update trigger | Elevation of Privilege | COM triggers update mode without authorization or under unsafe conditions. | G, D, F, H | Operating mode and safety software integrity are affected. | Device enters update mode unexpectedly or executes update workflow at wrong lifecycle state. | Update trigger is identified as TB2 flow. | 3 | 5 | 15 | High | Mitigate | SCPU authorizes update mode only under defined local/secure conditions; require authenticated trigger and safe operational state. | 1 | 4 | 4 | Low | Product Security | Open | Mode authorization tests; update trigger negative tests | Cybersecurity_Process.html |
| TARA-014 | IF-05 | Shared Flash write firmware image | Tampering | Attacker modifies firmware image stored in Shared Flash before SCPU reads it. | D, F, H | Shared Flash provides safe FW container; SCPU must not trust it. | Unauthorized or corrupted firmware could be installed if verification fails. | TB3: Safe CPU does not trust Shared Flash but verifies firmware image itself. | 3 | 5 | 15 | High | Mitigate | Cryptographic signature verification, hash validation, secure version policy and rejection of corrupted/update images. | 1 | 5 | 5 | Medium | Product Security | Open | Signature validation; corrupted image tests | Cybersecurity_Process.html |
| TARA-015 | IF-05 | Shared Flash version information | Tampering | Version metadata is manipulated to force downgrade or block update. | D, G, H | Version information is related to safety software authenticity and operating mode. | Downgrade to vulnerable firmware or update denial. | Downgrade attacks listed as TB3 risk. | 3 | 4 | 12 | High | Mitigate | Anti-rollback counters or signed version metadata; clear update failure diagnostics. | 1 | 3 | 3 | Low | Product Security | Open | Downgrade tests; version metadata tests | Cybersecurity_Process.html |
| TARA-016 | IF-05 | Shared Flash exhaustion/corruption | Denial of Service | Repeated update attempts or flash corruption exhaust storage or leaves invalid update state. | H, D, G | Update storage affects firmware workflow and device availability. | Device cannot update or may remain in service/update error condition. | Shared Flash is critical non-volatile update resource. | 3 | 3 | 9 | Medium | Mitigate | Atomic update workflow, integrity checks, storage wear/error handling and recovery procedure. | 1 | 2 | 2 | Low | Product Security | Open | Power-loss/update interruption tests | Cybersecurity_Process.html |
| TARA-017 | IF-06 | Safe digital inputs | Tampering/Spoofing | Field input signals are spoofed, shorted or manipulated at terminal level. | A, C, E, H | Input states and diagnostics must correspond to actual safety state. | Incorrect input state reported or diagnostic fault leading to safe shutdown. | Field side DI/DO and associated supply paths are in intended port use. | 3 | 5 | 15 | High | Mitigate | Input diagnostics, plausibility checks, safe state on detected fault, customer documentation for wiring/physical protection. | 2 | 4 | 8 | Medium | Safety/Security | Open | Input fault simulation; wiring fault tests | Cybersecurity_Process.html |
| TARA-018 | IF-07 | Safe digital outputs | Tampering/Spoofing | Output signal path is manipulated, externally forced or prevented from safe switch-off. | A, C, E, H | Safe output path requires forced switch-off and maintained OFF state for dangerous internal failures. | Actuator may not reach intended safe state or machine availability is lost. | Covered safety behavior includes safe output path and maintained OFF state. | 2 | 5 | 10 | High | Mitigate | Output diagnostics, read-back/plausibility checks, defined safe state, field wiring requirements in documentation. | 1 | 5 | 5 | Medium | Safety/Security | Open | Output fault simulation; safe switch-off evidence | Cybersecurity_Process.html |
| TARA-019 | IF-08 | Rotary switches addressing/mode | Tampering | Local attacker changes rotary switches to alter F-address, update mode or function selection. | B, G, H, F | Local selection affects device functions and operating mode. | Incorrect parameterization/addressing, unintended update mode or unavailable function. | Rotary switch manipulation is listed as foreseeable misuse. | 3 | 4 | 12 | High | Mitigate | Detect change, require reset/commissioning validation, compare with expected configuration, document tamper protection responsibilities. | 2 | 3 | 6 | Medium | Product + Operator | Open | Switch change tests; mismatch diagnostics | Cybersecurity_Process.html |
| TARA-020 | IF-09 | JTAG/debug interfaces | Elevation of Privilege | Physical attacker uses debug interface to read or modify firmware/memory. | D, F, G, H | Debug interfaces expose CPU internals and safety/non-safety separation. | Firmware extraction/modification, bypass of update controls, service mode abuse. | JTAG interfaces per CPU are listed for completeness and physically protected by encapsulated design. | 2 | 5 | 10 | High | Mitigate | Disable or lock debug access in production; protect debug credentials; rely on encapsulation and operator physical protection. | 1 | 4 | 4 | Low | Product Security | Open | Production debug lock evidence; penetration test | Cybersecurity_Process.html |
| TARA-021 | IF-10 | Power supply / daisy-chain | Denial of Service | Power manipulation causes brownout, resets or field supply disruption. | H, A, E | Power supply is relevant for availability and safe behavior. | Device outage or safe-state transition; possible diagnostic events. | Power supply is treated as installation/environment responsibility for availability. | 3 | 4 | 12 | High | Transfer/Mitigate | Document supply requirements, brownout behavior and safe-state transitions; product validates power diagnostics where applicable. | 2 | 3 | 6 | Medium | Operator + Product | Open | Brownout tests; installation manual requirement | Cybersecurity_Process.html |
| TARA-022 | IF-11 | LED status indication | Information Disclosure/Tampering | Status indication is misleading or provides operational information to unauthorized observer. | E, H | Local status indication supports diagnostics and monitoring. | Operator may misinterpret device status or attacker gains limited process insight. | LEDs are local status indication interface. | 2 | 2 | 4 | Low | Accept/Mitigate | Ensure LED status cannot be source of safety truth alone; document diagnostic hierarchy and prevent software manipulation of safety-critical status. | 1 | 2 | 2 | Low | Product Security | Open | Status indication consistency tests | Cybersecurity_Process.html |
| TARA-023 | IF-12 | IPC SCPU1-SCPU2 cross communication | Tampering/DoS | Internal cross-communication is corrupted, delayed or inconsistent between both safe CPUs. | A, C, E, F, H | 1oo2 safety architecture depends on cross-communication and monitoring. | Safety monitoring detects fault and transitions safe; availability impact if persistent. | SCPU contains both channels, IPC and watchdog in 1oo2 architecture. | 2 | 5 | 10 | High | Mitigate | Cross-monitoring with CRC/counters/timeouts; independent watchdog and safe-state on inconsistency. | 1 | 4 | 4 | Low | Safety/Security | Open | IPC fault injection; 1oo2 diagnostic coverage evidence | Cybersecurity_Process.html |
| TARA-024 | IF-01/03 | External network reachability | Spoofing/Elevation of Privilege | Device is connected to unsecured network or IoT interface from untrusted network. | F, G, H, D, E | Foreseeable misuse increases external reachability of COM and service functions. | Remote compromise of COM/service function and attempts to influence update or diagnostics. | Connection to unsecured networks and IoT from untrusted networks are foreseeable misuse scenarios. | 4 | 4 | 16 | Critical | Transfer/Mitigate | Customer documentation for network segmentation, firewalls, access control and secure remote access; product hardening for exposed services. | 2 | 3 | 6 | Medium | Operator + Product | Open | Security manual; network hardening checklist | Cybersecurity_Process.html |
| TARA-025 | IF-01/02 | Controller/F-Host dependency | Spoofing/Tampering | Third-party PLC/F-Host or controller-side parameterization is compromised. | B, C, A, H | SRIO relies on intended configuration and safety communication from controller side. | Incorrect configuration or commands from compromised upstream system. | Third-party controller hardening is out of scope and handled by controller vendor/operator. | 3 | 5 | 15 | High | Transfer/Mitigate | Document system-level requirement for trusted F-Host, controller hardening and secure commissioning; product validates received safety parameters. | 2 | 4 | 8 | Medium | Operator + Product | Open | Customer documentation; commissioning validation tests | Cybersecurity_Process.html |

## Requirements

| Req ID | Related TARA IDs | Requirement | Rationale | Target / owner | Verification approach | Status | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SRIO-CS-001 | TARA-001,009 | SCPU shall validate safety-relevant configuration before activation using integrity and consistency checks. | Protects asset B and supports TB2 trust assumption. | Safety/Security | CRC/signature mismatch tests; commissioning validation | Open | Cybersecurity_Process.html |
| SRIO-CS-002 | TARA-003,004 | SRIO shall handle invalid or missing PROFIsafe communication with deterministic safe-state behavior and diagnostics. | Protects C, A and H. | Safety/Security | Invalid telegram and timeout tests | Open | Cybersecurity_Process.html |
| SRIO-CS-003 | TARA-005,007,008 | IoTCore service endpoints shall require appropriate authentication/authorization and robust input validation. | Protects G, E, F and H. | Product Security | Authorization tests; API fuzzing; negative tests | Open | Cybersecurity_Process.html |
| SRIO-CS-004 | TARA-006,014,015,016 | Firmware update workflow shall verify authenticity, integrity and anti-rollback properties before installation. | Protects D and G; implements TB3. | Product Security | Signature, corrupted-image and downgrade tests | Open | Cybersecurity_Process.html |
| SRIO-CS-005 | TARA-010,011,013 | SysCom communication shall be validated by SCPU for integrity, sequence, timing and allowed mode transitions. | Protects B, C, D, E, F, G. | Safety/Security | SysCom fault injection and replay/delay tests | Open | Cybersecurity_Process.html |
| SRIO-CS-006 | TARA-017,018 | Field I/O diagnostics shall detect relevant wiring and signal faults and transition to defined safe state where required. | Protects A, C, E and H. | Safety | Field fault simulation and diagnostics evidence | Open | Cybersecurity_Process.html |
| SRIO-CS-007 | TARA-019,020 | Local physical/service interfaces shall be protected against unauthorized production use or documented as operator responsibility. | Protects B, D, F, G and H. | Product + Operator | Production debug lock evidence; security manual | Open | Cybersecurity_Process.html |
| SRIO-CS-008 | TARA-021,024,025 | Customer documentation shall state environmental security requirements: segmentation, access control, secure remote access, physical protection and system-level risk assessment. | Addresses out-of-scope and operator-level dependencies. | Operator/Integrator | Security manual review; external requirement list | Open | Cybersecurity_Process.html |
| SRIO-CS-009 | TARA-002,008,024 | COM domain shall be hardened so that compromised external communication cannot directly affect safety domain integrity. | Protects F and follows TB1. | Product Security | Architecture review; penetration/fuzz tests; separation evidence | Open | Cybersecurity_Process.html |
| SRIO-CS-010 | TARA-011,022 | Diagnostics and local status indication shall be consistent with authoritative SCPU diagnostic state. | Protects E and supports operator interpretation. | Product Security | Diagnostic consistency tests | Open | Cybersecurity_Process.html |

## Interface Asset Matrix

| Interface ID | Interface | A | B | C | D | E | F | G | H | Comment | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IF-01 | Ethernet / PROFINET |  | X | X |  |  | X |  | X | Derived from interface descriptions, trust boundaries and asset/resource mapping. | Cybersecurity_Process.html |
| IF-02 | PROFIsafe over PROFINET | X |  | X |  |  | X |  | X | Derived from interface descriptions, trust boundaries and asset/resource mapping. | Cybersecurity_Process.html |
| IF-03 | IoTCore service interface |  |  |  | X | X | X | X | X | Derived from interface descriptions, trust boundaries and asset/resource mapping. | Cybersecurity_Process.html |
| IF-04 | SysCom | X | X | X | X | X | X | X | X | Derived from interface descriptions, trust boundaries and asset/resource mapping. | Cybersecurity_Process.html |
| IF-05 | Shared Flash update path |  |  |  | X |  | X | X | X | Derived from interface descriptions, trust boundaries and asset/resource mapping. | Cybersecurity_Process.html |
| IF-06 | Safety input terminals | X |  | X |  | X |  |  | X | Derived from interface descriptions, trust boundaries and asset/resource mapping. | Cybersecurity_Process.html |
| IF-07 | Safety output terminals | X |  | X |  | X |  |  | X | Derived from interface descriptions, trust boundaries and asset/resource mapping. | Cybersecurity_Process.html |
| IF-08 | Rotary switches |  | X |  |  |  | X | X | X | Derived from interface descriptions, trust boundaries and asset/resource mapping. | Cybersecurity_Process.html |
| IF-09 | JTAG / debug interfaces |  |  |  | X |  | X | X | X | Derived from interface descriptions, trust boundaries and asset/resource mapping. | Cybersecurity_Process.html |
| IF-10 | Power supply / daisy-chain | X |  |  |  |  |  |  | X | Derived from interface descriptions, trust boundaries and asset/resource mapping. | Cybersecurity_Process.html |
| IF-11 | LED status indication |  |  |  |  | X |  |  | X | Derived from interface descriptions, trust boundaries and asset/resource mapping. | Cybersecurity_Process.html |
| IF-12 | IPC SCPU1 <-> SCPU2 | X |  | X |  | X | X |  | X | Derived from interface descriptions, trust boundaries and asset/resource mapping. | Cybersecurity_Process.html |
