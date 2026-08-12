# SRIO TARA: Interface-Based Asset Analysis (Revised)

## 1. Scope

- Risk rating formula used throughout: `Risk Score = Likelihood x Impact`.
- Risk level thresholds used throughout: `Low 1-4`, `Medium 5-9`, `High 10-15`, `Critical 16-25`.


## 3. System Under Consideration

| Topic | Confirmed technical conclusion | 
| --- | --- | 
| Safety role | SRIO is a functional safety gateway used for safe inputs and safe outputs in a machine context. | 
| Safety targets | Product targets include SIL 3 and PL e / Cat. 4 depending on configuration. | 
| _COM domain_ | _COM contains CPU3 and NetX90, handles PROFINET and IoTCore, and is explicitly described as non-safety-related._ | 
| _Safety domain_ | _SCPU handles PROFIsafe, DI, DO, monitoring, and watchdog functions._ | 
| _COM-to-SCPU boundary_ | _SysCom is the SPI-based communication path between COM and SCPU, with acyclic configuration, cyclic PROFIsafe frame exchange, ErrorEvent, and IoT-related data exchange_ | 
| _Update architecture_ | _Firmware update enters a dedicated update state, uses IoTCore upload on COM, stores an SRIO update container in COM flash, moves a safe container into shared update flash, and then lets SCPU install safe firmware._ | 
| _Update mode gating_ | _Update is only allowed when the rotary-switch value is `999`, followed by reboot into update state._ | 
| _Fail-safe behavior_ | _Communication loss, EC1, EC3, EC4, update state, and fatal error state all have documented safe-state or fallback behavior._ | 
| _Environment assumption_ | _Use is assumed inside a machine, typically behind a firewall and with restricted access to the machine or control cabinet._ | 

Trust-boundary interpretation used in this revision:

- _`TB-EXT-COM`: External Ethernet / IoT / engineering access into the COM domain._
- _`TB-COM-SAFETY`: COM domain into SCPU over SysCom._
- `TB-COM-FLASH-SAFETY`: COM-managed update container handling into safe firmware installation via shared update flash.
- _`TB-FIELD`: Local field wiring access at DI and DO ports._
- _`TB-LOCAL-SERVICE`: Local physical access to rotary switches, debug points, power, and visual indicators_.

## 4. Confirmed Facts, Assumptions and Open Issues

| Type | Item | Assessment |
| --- | --- | --- | 
| Confirmed fact | IoTCore is intended for non-safety-related functionality such as diagnostics, status, and firmware update. | Confirmed. |
| Confirmed fact | IoTCore parameter write access was removed; current statement says read-only access for IoTCore and no password currently required, while firmware update is gated by rotary-switch setting plus reboot. | Confirmed. | 
| Confirmed fact | PROFIsafe is handled in SCPU; COM tunnels the safe communication via black-channel principle. | Confirmed. | 
| Confirmed fact | SCPU validates configuration by CRC and parameter dependency checks and rejects bad configuration in Parametrization. | Confirmed. | 
| Confirmed fact | Rotary switches are only read during initialization. | Confirmed. |
| Confirmed fact | Update compatibility and consistency checks are documented for COM and SCPU. | Confirmed. | 
| Confirmed fact | Downgrade of safe application firmware is explicitly allowed and documented. | Confirmed. | 
| Open issue | Cryptographic authenticity of update containers or safe firmware is not documented in the supplied SRIO sources. | Open issue. No supporting evidence found in the supplied documentation. | 
| Open issue | Authenticated or role-based access control for IoTCore service use is not documented in the supplied SRIO sources. | Open issue. No supporting evidence found in the supplied documentation. | 
| Open issue | A documented production lock or disable mechanism for debug access is not present in the supplied SRIO sources, although debug use is stated to be development-only. | Open issue. |
| Open issue | The source workbook numbering is inconsistent: dashboard says 25 scenarios, but the supplied TARA IDs run `TARA-001` to `TARA-025` with `TARA-012` missing. | Open issue. Numbering gap preserved in this revision. | 

## 5. Assets A-H

The asset IDs and names remain unchanged. The descriptions below clarify how they were interpreted for this revision.

| Asset ID | Asset name | Revised assessment used for this review | 
| --- | --- | --- | 
| A | Trusted Safety Function | `A` is only treated as directly affected when the documentation supports loss of correct safety execution itself, not merely a safe-state transition, channel passivation, update mode, or machine downtime. In many scenarios the documented response is fail-safe fallback, so `A` becomes indirect rather than direct. | 
| B | Integrity of Safety Configuration | `B` covers the correctness of F-Parameters, iParameters, and the device's own F_Dest address handling. |
| C | Integrity and Authenticity of Safety-Relevant Process Data | `C` covers safe input data, safe output commands, qualifiers, and PROFIsafe frame content. Availability of this process data is considered where the documentation ties communication loss to safe fallback. | 
| D | Authenticity and Integrity of Safety Software | `D` covers safe application firmware, bootloader handling where documented, and update-container acceptance decisions. Because the supplied SRIO documentation documents compatibility and consistency checks but not cryptographic authenticity, `D` remains a major open concern. | 
| E | Integrity of Safety Monitoring | `E` covers diagnostics, voltage/current/temperature monitoring, watchdog-related state indication, ErrorEvent generation, qualifiers, and authoritative safety-related diagnosis. |
| F | Separation of Safety and Non-Safety Domain | `F` is used only where the documented COM-to-SCPU split, black-channel assumptions, SysCom boundary, or update handover boundary are directly challenged. It is not used merely because two functions reside on neighboring blocks. |
| G | Integrity of Operating Mode | `G` covers update mode, fit or test related mode entry, and other documented state transitions that should not be entered without the intended preconditions. | 
| H | SRIO Functionality | `H` covers availability and operational continuity of SRIO, including safe fallback, startup blocking, update availability, and local field availability. | 

## 6. Interfaces IF-01-IF-12

| Interface ID | Interface / Boundary | Documented attacked component(s) | Trust boundary view for this revision |  Open points |
| --- | --- | --- | --- |  --- |
| IF-01 | Ethernet / PROFINET | COM, NetX90, fieldbus application | External access into the non-safety COM domain, with configuration forwarding into SCPU. |  No supporting evidence found in the supplied documentation for authenticated origin protection of engineering/configuration traffic beyond PROFIsafe/F-parameter mechanisms. |
| IF-02 | PROFIsafe over PROFINET | SCPU PROFIsafe stack, COM transport path | Logical safety channel using black-channel transport through COM. | None material; the interface is well documented. |
| IF-03 | IoTCore service interface | COM CPU3, IoTCore app, COM-side firmware/update services | External access into COM for read-only diagnostics plus update and FIT related services. | No supporting evidence found in the supplied documentation for authenticated user access or role separation. |
| IF-04 | SysCom | COM CPU3, SCPU CPU1, SPI transport | Primary COM-to-safety boundary. |  None material; boundary is explicit. |
| IF-05 | Shared Flash update path | Shared update flash, COM update container handling, SCPU update loader | COM-managed update handover into safe firmware installation. | No supporting evidence found in the supplied documentation for cryptographic signature or anti-rollback enforcement. |
| IF-06 | Safety input terminals | DI module, SCPU input processing | External local field-wiring boundary for safe input data. |  None material. |
| IF-07 | Safety output terminals | DO module, SCPU output control | External local field-wiring boundary for safe output actuation. |  None material. |
| IF-08 | Rotary switches | SCPU rotary-switch readout and operating-state logic | Local physical mode/address boundary, read only during init. |  The hardware sleeves/caps are documented, but no tamper-detection mechanism is documented. |
| IF-09 | JTAG / debug interfaces | Debug/flash access for each controller, COM debug points | Local service boundary with development-only intent. |  Production disable evidence is not documented in the supplied SRIO sources. |
| IF-10 | Power supply / daisy-chain | PS, COM, SCPU, DI, DO | External physical supply boundary affecting overall availability. |Downstream daisy-chain current is not measured by SRIO. |
| IF-11 | LED status indication | COM LEDs and SCPU LEDs | Local observation boundary only. | LEDs are explicitly non-safety information only. |
| IF-12 | IPC SCPU1 <-> SCPU2 | SCPU1, SCPU2, watchdog-related cross-checking | Internal safety-only coordination boundary. | No external access path is documented for this interface by itself. |

## 7. Revised Interface-to-Asset Matrix

Legend:

- `D` = direct interface relevance supported by the supplied SRIO documentation.
- `I` = indirect or conditional relevance only.
- blank = not supported by the supplied SRIO documentation.

| Interface ID | Interface | A | B | C | D | E | F | G | H | Comment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | 
| IF-01 | Ethernet / PROFINET |  | D | D |  |  | I |  | D | Direct relevance is configuration, process-data transport, and availability in COM. | 
| IF-02 | PROFIsafe over PROFINET | I |  | D |  |  | I |  | D | Safe communication directly affects safe process data and SRIO availability; trusted safety function impact is typically indirect because invalid communication should fail safe. | 
| IF-03 | IoTCore service interface |  |  |  | D | I | I | D | D | Documented direct relevance is diagnostics/service/update behavior in COM, not normal safety process control. |
| IF-04 | SysCom | I | D | D | D | D | D | D | D | SysCom is the documented COM-to-safety boundary for configuration, cyclic data, ErrorEvent, and IoT-related requests. |
| IF-05 | Shared Flash update path |  |  |  | D |  | I | D | D | Direct relevance is safe firmware handling and update availability; separation relevance is conditional. | 
| IF-06 | Safety input terminals | I |  | D |  | D |  |  | D | DI manipulation directly affects safe input data, diagnostics, and local SRIO function. | 
| IF-07 | Safety output terminals | I |  | D |  | D |  |  | D | DO manipulation directly affects actuation data, diagnostics, and local SRIO function. | 
| IF-08 | Rotary switches |  | D |  |  |  |  | D | D | Rotary-switch value directly controls F_Dest address validity and update-mode entry. | 
| IF-09 | JTAG / debug interfaces | I | I | I | D | I | I | D | D | Firmware/debug access directly affects software integrity and availability; wider asset reach is only conditional. |
| IF-10 | Power supply / daisy-chain | I |  |  |  | I |  |  | D | Power faults mainly affect availability; safety impact is primarily via fail-safe response. | 
| IF-11 | LED status indication |  |  |  |  | I |  |  | I | LEDs are informational only; diagnostic and availability relevance is indirect. | 
| IF-12 | IPC SCPU1 <-> SCPU2 | I |  | I |  | D |  |  | D | Internal cross-communication directly affects monitoring and continuity; trusted safety function impact is typically through safe fault handling. | 

## 8. Revised TARA

### TARA-001

- Attacked interface and component: `IF-01 Ethernet / PROFINET`; COM fieldbus path forwarding configuration to SCPU.
- Attacker access and preconditions: Access to the machine network, engineering path, or F-Host/PLC configuration path. 
- Immediate cybersecurity effect: Manipulated F-Parameters or iParameters are received by COM and forwarded toward SCPU.
- Existing control response: SCPU verifies completeness, CRC, parameter dependencies, and F_Dest address consistency; invalid configuration remains rejected in Parametrization and raises EC3. 
- Direct product-level impact: Configuration rejection, blocked startup, or re-parametrization need. The documented direct effect is configuration-integrity and availability impact, not automatic compromise of the trusted safety function.
- Possible machine-level consequence: Machine startup prevented or interrupted until valid configuration is restored.
- Affected assets: direct `B, H`; indirect or conditional `A, C`.
- Evidence for affected-asset mapping: `B` because F_Parameters, iParameters, and F_Dest address are explicitly validated; `H` because rejected configuration keeps the device out of normal operation; `A` and `C` only if invalid configuration were somehow accepted despite the documented checks. 
- Likelihood: `2`.
- Impact: `4`.
- Risk score and level: `8`, `Medium`.
- Rating rationale: Network access and configuration influence are required, and the documented response is rejection and availability loss rather than undetected unsafe execution.
- Suitable mitigation: Keep SCPU-side configuration completeness, CRC, dependency, and rotary-address validation mandatory for every startup and reconnection; add explicit documentation of who is allowed to change configuration.
- Suitable verification evidence: Configuration rejection evidence, CRC mismatch evidence, and F_Dest mismatch evidence from startup/parametrization behavior.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for authenticated origin protection of PROFINET configuration traffic.

### TARA-002

- Attacked interface and component: `IF-01 Ethernet / PROFINET`; COM / NetX90 / fieldbus communication path.
- Attacker access and preconditions: Access to the fieldbus network and ability to send malformed or excessive traffic. 
- Immediate cybersecurity effect: COM or the fieldbus path is overloaded, loses link, or cannot maintain normal communication.
- Existing control response: Communication loss leads to fallback from Operate to Parametrization; safe channels/ports are switched to failsafe state during fallback; COM also reports diagnosis information. 
- Direct product-level impact: Availability loss or repeated reconnection attempts.
- Possible machine-level consequence: Safe stop or machine downtime caused by communication loss.
- Affected assets: direct `H`; indirect or conditional `F, A`.
- Evidence for affected-asset mapping: `H` because communication loss directly prevents normal SRIO operation; `F` and `A` are indirect because the documented architecture intends a non-safety COM failure to fail safe rather than directly corrupt the safety domain. 
- Likelihood: `3`.
- Impact: `3`.
- Risk score and level: `9`, `Medium`.
- Rating rationale: Network access is plausible in the intended machine network, but documented consequences are mainly availability and fallback.
- Suitable mitigation: Preserve deterministic fallback, timeout handling, and PROFINET diagnostics; consider explicit robustness expectations for malformed traffic in the COM specification.
- Suitable verification evidence: Communication-loss fallback evidence and COM-side diagnostic evidence.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for parser hardening, rate limiting, or protocol fuzz robustness claims.

### TARA-003

- Attacked interface and component: `IF-02 PROFIsafe over PROFINET`; SCPU PROFIsafe stack and COM transport path.
- Attacker access and preconditions: Access to the fieldbus network and ability to tamper with or spoof PROFIsafe frames.
- Immediate cybersecurity effect: Manipulated safe communication frames are delivered or attempted.
- Existing control response: SRIO is required to act as PROFIsafe F-Slave, use a certified PROFIsafe stack, support 4-byte CRC-related F-parameter handling, and use watchdog-related timing constraints. 
- Direct product-level impact: Invalid communication should be detected and should not be accepted as valid safe process data.
- Possible machine-level consequence: Safe stop or loss of function if communication is rejected or times out.
- Affected assets: direct `C`; indirect or conditional `A, H`.
- Evidence for affected-asset mapping: `C` because the attacked content is the safe process data path itself; `A` and `H` are indirect because the documented behavior is safe communication validation and fallback, not direct unsafe execution.
- Likelihood: `2`.
- Impact: `4`.
- Risk score and level: `8`, `Medium`.
- Rating rationale: Safety protocol defenses are documented, reducing likelihood of accepted tampering; impact remains significant because communication loss can stop the machine.
- Suitable mitigation: Preserve certified PROFIsafe implementation, F-parameter checks, watchdog timing, and error classification.
- Suitable verification evidence: PROFIsafe certification evidence and invalid-frame handling evidence.
- Unsupported assumptions: None beyond the documented PROFIsafe mechanisms.

### TARA-004

- Attacked interface and component: `IF-02 PROFIsafe over PROFINET`; SCPU safe communication availability.
- Attacker access and preconditions: Ability to interrupt, delay, or repeatedly invalidate PROFIsafe communication.
- Immediate cybersecurity effect: Safe communication cannot remain active.
- Existing control response: Communication timeout triggers fallback to Parametrization; failsafe values are applied; PROFIsafe timeout behavior is handled by the stack. 
- Direct product-level impact: SRIO leaves normal operation and enters fallback behavior.
- Possible machine-level consequence: Machine safe stop and downtime.
- Affected assets: direct `C, H`; indirect or conditional `A`.
- Evidence for affected-asset mapping: `C` because safe process-data availability is interrupted; `H` because SRIO functionality is unavailable; `A` is indirect because the documented response is fail-safe rather than silent corruption of the safety function. 
- Likelihood: `3`.
- Impact: `4`.
- Risk score and level: `12`, `High`.
- Rating rationale: A communication-availability attack is plausible on the machine network and directly causes operational loss.
- Suitable mitigation: Keep explicit timeout, fallback, and operator-visible diagnostics in the product and manual.
- Suitable verification evidence: Timeout/fallback evidence and diagnostic evidence for safe communication loss.
- Unsupported assumptions: None material.

### TARA-005

- Attacked interface and component: `IF-03 IoTCore service interface`; COM IoTCore diagnostics and device-information endpoints.
- Attacker access and preconditions: Network reachability to IoTCore.
- Immediate cybersecurity effect: Read-out of device status, versions, network details, error log, or other documented read-only data.
- Existing control response: The supplied SRIO documentation documents read-only IoT access for diagnostics and device information, but does not document authenticated user access. 
- Direct product-level impact: No direct manipulation of SRIO behavior is documented for this read-only disclosure path.
- Possible machine-level consequence: Primarily improved attacker reconnaissance for follow-on attacks.
- Affected assets: direct `none supported by assets A-H`; indirect or conditional `D, E, G, H`.
- Evidence for affected-asset mapping: The current asset set contains no confidentiality-specific asset. The disclosed data can support follow-on attacks against software, diagnostics, service mode, or availability, but a direct product-level impact on `A` to `H` is not evidenced by the supplied documentation. 
- Likelihood: `2`.
- Impact: `2`.
- Risk score and level: `4`, `Low`.
- Rating rationale: The scenario is relevant as reconnaissance, but the current documentation does not show a direct product effect through read-only disclosure alone.
- Suitable mitigation: Restrict IoTCore exposure to the intended machine network and document service exposure constraints more explicitly.
- Suitable verification evidence: Endpoint inventory and confirmation that documented read-only items match intended exposure.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for IoTCore authentication, authorization, or confidentiality controls.

### TARA-006

- Attacked interface and component: `IF-03 IoTCore service interface`; COM update workflow and handover toward shared update flash.
- Attacker access and preconditions: IoT reachability plus update-mode preconditions; documented update acceptance requires rotary-switch value `999` and reboot into update mode. 
- Immediate cybersecurity effect: Unauthorized or malicious update container upload and attempted installation.
- Existing control response: Update request is accepted only in update mode; COM and SCPU perform compatibility and consistency checks; update state keeps I/Os in safe state.
- Direct product-level impact: Installation of unintended but compatible firmware remains a concern because documented controls show compatibility/consistency checks, but not cryptographic authenticity checks.
- Possible machine-level consequence: Device outage, changed behavior, or later safety impact depending on what the installed firmware does.
- Affected assets: direct `D, G, H`; indirect or conditional `F, A`.
- Evidence for affected-asset mapping: `D` because firmware integrity is directly targeted; `G` because update mode is the attacked operating mode; `H` because update misuse can take the device out of service; `F` and `A` are indirect because a malicious firmware image could later challenge separation or safety execution, but that behavior is not documented per se. 
- Likelihood: `2`.
- Impact: `5`.
- Risk score and level: `10`, `High`.
- Rating rationale: Physical/local preconditions reduce likelihood, but successful abuse can fundamentally alter firmware.
- Suitable mitigation: Add documented authenticity protection for update containers and safe firmware, and define accepted/forbidden downgrade policy explicitly for security cases.
- Suitable verification evidence: Evidence of update-mode gating, compatibility rejection, and any future authenticity-check evidence.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for cryptographic signature verification or anti-rollback protection.

### TARA-007

- Attacked interface and component: `IF-03 IoTCore service interface`; documented service functions including firmware control and FIT service.
- Attacker access and preconditions: IoTCore reachability to service endpoints.
- Immediate cybersecurity effect: Unauthorized triggering of service or test related functions.
- Existing control response: IoTCore remains read-only for normal parameterization; update mode requires rotary-switch gating; a FIT service is documented in COM. 
- Direct product-level impact: Service misuse can affect availability or mode integrity even without directly corrupting safe process data.
- Possible machine-level consequence: Maintenance disruption, nuisance downtime, or unintended test activity.
- Affected assets: direct `G, H`; indirect or conditional `E`.
- Evidence for affected-asset mapping: `G` because test or update related service use concerns operating-mode integrity; `H` because service misuse can disrupt device functionality; `E` is indirect because FIT or service use can interfere with diagnostics or maintenance interpretation. 
- Likelihood: `3`.
- Impact: `3`.
- Risk score and level: `9`, `Medium`.
- Rating rationale: The service surface is documented, but strong access control is not.
- Suitable mitigation: Document and implement explicit access restrictions for FIT and update related services.
- Suitable verification evidence: Service inventory evidence and confirmation which services remain enabled in production.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for access control on the FIT service or IoT service endpoints.

### TARA-008

- Attacked interface and component: `IF-03 IoTCore service interface`; COM parser / IoTCore application handling HTTP or JSON style requests.
- Attacker access and preconditions: IoTCore reachability and ability to send malformed service requests.
- Immediate cybersecurity effect: COM application failure or compromise attempt.
- Existing control response: The documentation supports architectural separation between non-safety COM and safety SCPU and documents fail-safe handling for communication loss, but does not document parser hardening. 
- Direct product-level impact: Loss of COM functionality and a direct challenge to the separation assumption.
- Possible machine-level consequence: Machine stop or unavailability if COM-side failure causes communication loss.
- Affected assets: direct `F, H`; indirect or conditional `D, E, G`.
- Evidence for affected-asset mapping: `F` because this is a direct attempt to compromise the non-safety domain that interfaces with the safety domain; `H` because COM compromise can stop SRIO communication; `D`, `E`, and `G` become relevant only if the compromise is leveraged into update, diagnostics, or mode functions.
- Likelihood: `3`.
- Impact: `4`.
- Risk score and level: `12`, `High`.
- Rating rationale: External service reachability is documented, while defensive parser controls are not.
- Suitable mitigation: Define and verify hardening expectations for the IoTCore application and minimize exposed production services.
- Suitable verification evidence: COM robustness evidence, production-service inventory, and separation-claim evidence.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for parser hardening, memory safety, process isolation, or authenticated IoT request handling.

### TARA-009

- Attacked interface and component: `IF-04 SysCom`; acyclic configuration data from COM to SCPU.
- Attacker access and preconditions: COM compromise or manipulation of the SysCom configuration-transfer path.
- Immediate cybersecurity effect: Manipulated F-Parameters or iParameters reach SCPU over SysCom.
- Existing control response: Configuration is transferred in defined messages; SCPU checks completeness, dependencies, CRC, and F_Dest address constraints before activation.
- Direct product-level impact: Rejected configuration and loss of availability if manipulation is detected.
- Possible machine-level consequence: Machine startup blocked or delayed.
- Affected assets: direct `B`; indirect or conditional `F, H, A`.
- Evidence for affected-asset mapping: `B` is direct because safety configuration is the attacked object; `F` is indirect because the scenario challenges COM-to-safety separation; `H` and `A` depend on whether the manipulation is detected or somehow accepted.
- Likelihood: `2`.
- Impact: `4`.
- Risk score and level: `8`, `Medium`.
- Rating rationale: COM compromise or boundary manipulation is needed, but documented SCPU checks reduce direct impact.
- Suitable mitigation: Keep SCPU as the sole authority for configuration acceptance.
- Suitable verification evidence: Evidence that every configuration path still ends in SCPU-side validation.
- Unsupported assumptions: None beyond the documented checks.

### TARA-010

- Attacked interface and component: `IF-04 SysCom`; cyclic PROFIsafe frame transfer and related cyclic data.
- Attacker access and preconditions: COM compromise or direct manipulation of SysCom cyclic traffic.
- Immediate cybersecurity effect: Modified, replayed, delayed, or lost cyclic safe communication between COM and SCPU.
- Existing control response: SysCom exchanges the PROFIsafe frame; COM IO-Delegator implements SPI timeout handling; PROFIsafe itself provides safe communication checks. 
- Direct product-level impact: Communication interruption or rejected cyclic data, leading to fallback or safe stop.
- Possible machine-level consequence: Machine stop or unavailability.
- Affected assets: direct `C, F, H`; indirect or conditional `A`.
- Evidence for affected-asset mapping: `C` because safe cyclic data is directly attacked; `F` because the COM-to-safety boundary is directly challenged; `H` because the documented response to communication interruption is fallback; `A` is indirect because the intended response is fail safe. 
- Likelihood: `2`.
- Impact: `4`.
- Risk score and level: `8`, `Medium`.
- Rating rationale: Boundary compromise is needed, and the documented design should convert many failures into availability loss instead of unsafe output.
- Suitable mitigation: Preserve timeout handling and ensure that SCPU relies on validated PROFIsafe content rather than COM trust.
- Suitable verification evidence: Evidence of timeout/fallback behavior when cyclic SysCom data is corrupted or interrupted.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for additional SysCom integrity protection independent of PROFIsafe checks.

### TARA-011

- Attacked interface and component: `IF-04 SysCom`; ErrorEvent and diagnosis-related exchanges between SCPU and COM.
- Attacker access and preconditions: COM compromise or boundary manipulation affecting diagnostic transfer.
- Immediate cybersecurity effect: Delayed, hidden, or altered diagnostic information at COM side.
- Existing control response: ErrorEvent structure is documented; COM logs received ErrorEvents and forwards diagnosis information, while safety-related error information also exists inside PROFIsafe status handling.
- Direct product-level impact: Misleading operator or maintenance diagnostics.
- Possible machine-level consequence: Slower fault localization or delayed recovery, rather than immediate unsafe control.
- Affected assets: direct `E`; indirect or conditional `H`.
- Evidence for affected-asset mapping: `E` is direct because diagnostic integrity is the attacked subject; `H` is indirect because degraded diagnostics can prolong downtime. 
- Likelihood: `2`.
- Impact: `2`.
- Risk score and level: `4`, `Low`.
- Rating rationale: The consequence is mainly maintenance and diagnosability degradation.
- Suitable mitigation: Make clear in documentation which diagnosis originates from SCPU and which from COM.
- Suitable verification evidence: Consistency review between ErrorEvent content, visible diagnosis, and safety communication status.
- Unsupported assumptions: None material.

### TARA-012

`TARA-012` was not present in the supplied source TARA. The numbering gap is preserved. See section 11 for the related open issue.

### TARA-013

- Attacked interface and component: `IF-04 SysCom`; update-start and related commands between COM and SCPU.
- Attacker access and preconditions: COM compromise or manipulation of update-related SysCom commands; documented update mode still requires rotary-switch value `999`.
- Immediate cybersecurity effect: Unauthorized attempt to drive SCPU into update handling.
- Existing control response: SCPU evaluates update only when update mode is active; COM sends start signal only after update container placement; update state keeps I/Os safe. 
- Direct product-level impact: Unintended update handling or service interruption.
- Possible machine-level consequence: Downtime or maintenance disruption.
- Affected assets: direct `G, D, H`; indirect or conditional `F`.
- Evidence for affected-asset mapping: `G` because the scenario targets update mode integrity; `D` because update behavior targets software handling; `H` because update entry interrupts normal function; `F` is indirect because a compromised COM uses the boundary to influence the safety domain. 
- Likelihood: `2`.
- Impact: `4`.
- Risk score and level: `8`, `Medium`.
- Rating rationale: Documented mode gating reduces likelihood, but mode abuse still affects operation.
- Suitable mitigation: Keep SCPU-side evaluation of update preconditions independent from COM request alone.
- Suitable verification evidence: Evidence that update commands are ignored when rotary-switch preconditions are not met.
- Unsupported assumptions: None beyond the documented gating.

### TARA-014

- Attacked interface and component: `IF-05 Shared Flash update path`; shared update flash and safe container handover to SCPU.
- Attacker access and preconditions: COM compromise, local service access, or manipulated update path able to alter the shared safe container.
- Immediate cybersecurity effect: Modified safe update payload is stored before SCPU installs it.
- Existing control response: SCPU verifies compatibility and consistency of data transferred to shared update flash; update state is dedicated and safe-state behavior is documented. 
- Direct product-level impact: Acceptance of modified but still compatibility-consistent firmware remains an open security concern.
- Possible machine-level consequence: Device misuse, later malfunction, or loss of safety assurance after update.
- Affected assets: direct `D, G, H`; indirect or conditional `F, A`.
- Evidence for affected-asset mapping: `D` because safety firmware is directly targeted; `G` because update mode is involved; `H` because update failure or misuse can disable the device; `F` and `A` are indirect because malicious installed firmware could later cross domains or affect safe execution.
- Likelihood: `2`.
- Impact: `5`.
- Risk score and level: `10`, `High`.
- Rating rationale: Update-path access is narrower than normal network exposure, but successful abuse can fundamentally change device software.
- Suitable mitigation: Add documented authenticity verification of safe containers and their metadata.
- Suitable verification evidence: Evidence of future authenticity checks, plus current compatibility/consistency rejection evidence.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for cryptographic signature validation of the safe container.

### TARA-015

- Attacked interface and component: `IF-05 Shared Flash update path`; update metadata and version handling.
- Attacker access and preconditions: Same as `TARA-014`, but targeting version or metadata semantics.
- Immediate cybersecurity effect: Downgrade or update-blocking attempt through manipulated version-related information.
- Existing control response: Compatibility checks are documented; downgrade is explicitly allowed for safe application firmware.
- Direct product-level impact: Installation of an older but compatible firmware remains allowed by the documented requirements.
- Possible machine-level consequence: Reintroduction of a previously fixed weakness or a maintenance mismatch between machine certification and installed software.
- Affected assets: direct `D, G, H`.
- Evidence for affected-asset mapping: `D` because software-version control is the attacked object; `G` because update mode and version policy are affected; `H` because blocked or unsuitable update paths affect device operability. 
- Likelihood: `2`.
- Impact: `4`.
- Risk score and level: `8`, `Medium`.
- Rating rationale: The downgrade path is documented, which lowers uncertainty but leaves a security-management gap.
- Suitable mitigation: Decide and document whether security-relevant downgrade should remain allowed, and under which constraints.
- Suitable verification evidence: Version-policy review and evidence of operator documentation for downgrade responsibilities.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for anti-rollback enforcement.

### TARA-016

- Attacked interface and component: `IF-05 Shared Flash update path`; update storage handling.
- Attacker access and preconditions: Repeated or interrupted update attempts, or corruption of the shared update path.
- Immediate cybersecurity effect: Invalid or incomplete update state in shared flash.
- Existing control response: Update flow is staged and compatibility/consistency checks are documented; update state is dedicated and I/Os stay safe. Evidence: `201_SRIO_System_Spec_Architecture`, sections 5.4 and 9.1.
- Direct product-level impact: Failed update and temporary or persistent device unavailability.
- Possible machine-level consequence: Maintenance delay and machine downtime.
- Affected assets: direct `D, H`; indirect or conditional `G`.
- Evidence for affected-asset mapping: `D` because the update payload/state is corrupted; `H` because failed update handling affects SRIO availability; `G` is indirect because the device remains in update-related handling. 
- Likelihood: `2`.
- Impact: `3`.
- Risk score and level: `6`, `Medium`.
- Rating rationale: Update corruption is plausible under fault or malicious interruption, but the primary effect is availability.
- Suitable mitigation: Clarify recovery behavior for incomplete update state and preserve safe-state handling during interruption.
- Suitable verification evidence: Evidence of failed-update detection and recovery guidance.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for atomic rollback or storage wear-handling details.

### TARA-017

- Attacked interface and component: `IF-06 Safety input terminals`; DI hardware and SCPU input processing.
- Attacker access and preconditions: Physical access to field wiring, connected sensors, or DI port wiring.
- Immediate cybersecurity effect: False input states, shorts, cross-circuits, or wiring faults at the DI interface.
- Existing control response: DI module and SCPU document testpulse behavior, stuck-at-high testing, switchable sensor supply, supply-switch diagnosis, qualifier behavior, and safe-state reporting. 
- Direct product-level impact: Passivation, bad qualifier, false inactive state, or loss of input availability.
- Possible machine-level consequence: Machine stop, inhibited restart, or in a faulted case an input not representing actual field state.
- Affected assets: direct `C, E, H`; indirect or conditional `A`.
- Evidence for affected-asset mapping: `C` because safe input data is directly attacked; `E` because diagnostics and qualifier handling are directly involved; `H` because channel faults can make the function unavailable; `A` is indirect because the documented reaction is safe-state handling where faults are detected. 
- Likelihood: `3`.
- Impact: `4`.
- Risk score and level: `12`, `High`.
- Rating rationale: Physical field access is plausible in machine environments, and the direct result is on safe input truthfulness and availability.
- Suitable mitigation: Preserve DI diagnostics, testpulse capability, and user documentation for valid sensor wiring and reactivation use.
- Suitable verification evidence: Evidence of DI fault detection behavior, qualifier transition behavior, and documented use constraints.
- Unsupported assumptions: None material.

### TARA-018

- Attacked interface and component: `IF-07 Safety output terminals`; DO hardware and SCPU output control.
- Attacker access and preconditions: Physical access to output wiring or attached actuator path.
- Immediate cybersecurity effect: Forced output state, prevented switch-off, or manipulated external actuation path.
- Existing control response: DO module and SCPU document watchdog support, switch-off capability, voltage/current monitoring, qualifier handling, logic tables, and safe state with outputs inactive/high impedance as documented. 
- Direct product-level impact: Channel fault, forced passivation, or inability to achieve intended actuation.
- Possible machine-level consequence: Machine stop or failure to actuate as intended; danger depends on the external actuator and machine design.
- Affected assets: direct `C, E, H`; indirect or conditional `A`.
- Evidence for affected-asset mapping: `C` because safe output command fidelity is directly affected; `E` because monitoring and qualifiers are involved; `H` because the port can become unavailable; `A` is indirect because the documented response is deactivation or safe-state behavior when faults are detected. 
- Likelihood: `3`.
- Impact: `4`.
- Risk score and level: `12`, `High`.
- Rating rationale: Physical access is needed, but actuator-side manipulation remains severe for local function and machine availability.
- Suitable mitigation: Preserve actual-versus-commanded evaluation, watchdog-based fail behavior, and external-wiring restrictions in the manual.
- Suitable verification evidence: Evidence that detected DO faults force bad qualifier and inactive output state.
- Unsupported assumptions: None material.

### TARA-019

- Attacked interface and component: `IF-08 Rotary switches`; SCPU rotary-switch interpretation.
- Attacker access and preconditions: Local physical access to the switch sleeves/caps before the next cold start or update cycle.
- Immediate cybersecurity effect: Wrong F_Dest address or forced update mode selection.
- Existing control response: Rotary value is only read during initialization; `1...899` is valid F_Dest address, `999` requests update mode, and other values outside the valid range cause configuration error behavior. 
- Direct product-level impact: Startup in wrong mode, wrong address acceptance attempt, or blocked operation.
- Possible machine-level consequence: Machine cannot communicate correctly with the intended F-Host or enters update handling unexpectedly.
- Affected assets: direct `B, G, H`.
- Evidence for affected-asset mapping: `B` because the device's own safe address is configuration-relevant; `G` because update mode is directly controlled here; `H` because wrong address or mode can prevent operation. 
- Likelihood: `2`.
- Impact: `4`.
- Risk score and level: `8`, `Medium`.
- Rating rationale: Local physical access is required and changes only take effect at initialization, but they materially alter mode or configuration validity.
- Suitable mitigation: Preserve init-only read behavior and document physical protection expectations clearly.
- Suitable verification evidence: Evidence that changed rotary values are only applied after cold start and that invalid values trigger the documented error path.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for tamper detection on the rotary-switch sleeves or caps.

### TARA-020

- Attacked interface and component: `IF-09 JTAG / debug interfaces`; debug and firmware-flash paths for controllers.
- Attacker access and preconditions: Physical service access to debug contacts or connectors.
- Immediate cybersecurity effect: Firmware readout, firmware modification, debug control, or low-level reset/flash actions.
- Existing control response: The requirement set says debug and test interfaces shall only be usable during development, and test-interface access shall be blocked after development, but the supplied SRIO documentation does not document the implemented production lock mechanism. 
- Direct product-level impact: Firmware/software compromise or service unavailability.
- Possible machine-level consequence: Device taken out of service or reprogrammed.
- Affected assets: direct `D, H`; indirect or conditional `G, F, A, B, C, E`.
- Evidence for affected-asset mapping: `D` is direct because firmware manipulation is explicitly possible through debug/flash paths; `H` is direct because reset/flash actions interrupt service; the broader assets become conditional because arbitrary debug access could later influence them, but those follow-on behaviors are not documented in detail. 
- Likelihood: `2`.
- Impact: `5`.
- Risk score and level: `10`, `High`.
- Rating rationale: Physical access narrows likelihood, but successful debug abuse can fundamentally alter the product.
- Suitable mitigation: Provide auditable evidence of production lock, disable, fuse, or equivalent debug restriction for all controllers.
- Suitable verification evidence: Production configuration evidence showing debug/test lock-down.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for a production lock implementation for debug access.

### TARA-021

- Attacked interface and component: `IF-10 Power supply / daisy-chain`; PS and dependent modules.
- Attacker access and preconditions: Physical access to power input, power out, or supply conditions.
- Immediate cybersecurity effect: Brownout, reset, reverse-polarity condition, overvoltage, or overcurrent condition.
- Existing control response: Voltage detection, overvoltage protection, reverse-polarity protection, hardware shutoff thresholds, overcurrent detection, and safe-state behavior are documented. 
- Direct product-level impact: Device reset, shutdown, or local function loss.
- Possible machine-level consequence: Safe stop or machine downtime.
- Affected assets: direct `H`; indirect or conditional `A, E`.
- Evidence for affected-asset mapping: `H` is direct because supply manipulation immediately affects SRIO availability; `A` and `E` are indirect because the documented design responds by shutdown, diagnosis, and safe-state behavior rather than silent unsafe behavior. 
- Likelihood: `2`.
- Impact: `4`.
- Risk score and level: `8`, `Medium`.
- Rating rationale: Physical supply manipulation is required; documented protections convert many cases into availability loss.
- Suitable mitigation: Preserve documented supply monitoring and keep installation constraints explicit in the user documentation.
- Suitable verification evidence: Supply-fault detection evidence and documented installation constraints.
- Unsupported assumptions: None material.

### TARA-022

- Attacked interface and component: `IF-11 LED status indication`; COM and SCPU LED indications.
- Attacker access and preconditions: Local observation or misleading interpretation of LEDs.
- Immediate cybersecurity effect: Misinterpretation of device state or limited operational information leakage.
- Existing control response: The manual shall state that LED use is non-safety-related; several LED functions are informational only. 
- Direct product-level impact: No documented direct control-path effect on SRIO behavior.
- Possible machine-level consequence: Slower diagnosis or operator misunderstanding.
- Affected assets: direct `none supported by assets A-H`; indirect or conditional `E, H`.
- Evidence for affected-asset mapping: `E` and `H` are only indirect because LEDs influence interpretation, not the authoritative safety control path; the documentation explicitly treats LEDs as non-safety information. 
- Likelihood: `2`.
- Impact: `1`.
- Risk score and level: `2`, `Low`.
- Rating rationale: The scenario has little direct technical effect on the device itself.
- Suitable mitigation: Keep the manual warning that LEDs are not the safety truth source.
- Suitable verification evidence: Documentation review and confirmation that safety decisions do not depend on LED state alone.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for software-driven falsification of LED behavior beyond their documented state mapping.

### TARA-023

- Attacked interface and component: `IF-12 IPC SCPU1 <-> SCPU2`; internal cross-checking and watchdog-related safety coordination.
- Attacker access and preconditions: There is no direct external interface documented for this path; practical exploitation would require compromise of internal safety logic or service-level access through another interface.
- Immediate cybersecurity effect: Corrupted or inconsistent safety-side coordination.
- Existing control response: The safety architecture uses two safety controllers, cross-checking logic, watchdog functionality, self-tests, and fatal-error handling. 
- Direct product-level impact: Fatal error or loss of availability if inconsistency is detected.
- Possible machine-level consequence: Safe stop or maintenance intervention.
- Affected assets: direct `E, H`; indirect or conditional `A, C`.
- Evidence for affected-asset mapping: `E` is direct because monitoring and internal coordination are the attacked subject; `H` is direct because detected inconsistency can stop operation; `A` and `C` are indirect because the intended response is safe fault handling instead of silent unsafe operation. 
- Likelihood: `1`.
- Impact: `4`.
- Risk score and level: `4`, `Low`.
- Rating rationale: High impact if the path is compromised, but direct attacker access is not documented.
- Suitable mitigation: Maintain independent watchdog and cross-checking as documented.
- Suitable verification evidence: Evidence that inconsistent SCPU coordination leads to documented fatal-error handling.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for an external direct access path to IF-12 itself.

### TARA-024

- Attacked interface and component: `IF-01/03`; deployment reachability of fieldbus and IoTCore interfaces.
- Attacker access and preconditions: Product is deployed contrary to the intended restricted machine-network environment or reachable from a broader untrusted network.
- Immediate cybersecurity effect: Increased attack surface exposure, not yet a completed exploit by itself.
- Existing control response: The documentation states the use case is assumed behind a firewall, with restricted network access and update by a trustworthy person. 
- Direct product-level impact: None until another exploit path is used.
- Possible machine-level consequence: Elevated probability of remote follow-on attacks.
- Affected assets: direct `none supported by assets A-H`; indirect or conditional `D, E, F, G, H`.
- Evidence for affected-asset mapping: The scenario is a system-level exposure condition. It increases likelihood of attacks against COM, update, diagnostics, and availability, but does not directly corrupt an asset by itself. 
- Likelihood: `3`.
- Impact: `2`.
- Risk score and level: `6`, `Medium`.
- Rating rationale: Misdeployment is plausible and materially changes attack preconditions, but does not itself alter device state.
- Suitable mitigation: Treat this primarily as a system responsibility and keep the network-placement assumptions explicit in the manual.
- Suitable verification evidence: Manual review showing clear environmental constraints and update/operator assumptions.
- Unsupported assumptions: No supporting evidence found in the supplied documentation for product-side network hardening sufficient to replace the documented firewall/restricted-network assumption.

### TARA-025

- Attacked interface and component: `IF-01/02`; trusted controller / F-Host dependency.
- Attacker access and preconditions: Compromise of the upstream PLC, F-Host, or engineering system that legitimately talks to SRIO.
- Immediate cybersecurity effect: Malicious but protocol-conform configuration or process-data commands are delivered to SRIO.
- Existing control response: SCPU validates configuration structure, iParCRC, dependencies, and F_Dest addressing; PROFIsafe handles safe communication integrity. However, controller hardening is outside SRIO product scope. 
- Direct product-level impact: Incorrect upstream intent can still drive SRIO behavior within the permitted protocol model, or cause rejected configuration if inconsistent.
- Possible machine-level consequence: Unsafe machine behavior or downtime, depending on what the compromised controller commands and what SRIO checks reject.
- Affected assets: direct `B, C`; indirect or conditional `A, H`.
- Evidence for affected-asset mapping: `B` and `C` are direct because SRIO consumes safety configuration and safe process-data content from the upstream controller; `A` and `H` depend on whether the malicious input is rejected or accepted as protocol-valid but semantically wrong from a system perspective.
- Likelihood: `2`.
- Impact: `5`.
- Risk score and level: `10`, `High`.
- Rating rationale: Upstream compromise is outside SRIO product control but can have severe consequences because SRIO relies on a trusted controller context.
- Suitable mitigation: Keep controller/F-Host trust assumptions explicit and preserve all SCPU-side validation of what can be validated locally.
- Suitable verification evidence: Documentation review of trust assumptions and SCPU validation coverage.
- Unsupported assumptions: No supporting evidence found in the supplied documentation that SRIO can independently verify the semantic correctness of controller commands beyond documented parameter and protocol checks.

## 9. Revised SRIO-CS Requirements

| Req ID | Related TARA IDs | Revised SRIO-CS requirement | Status from supplied documentation | 
| --- | --- | --- | --- | 
| SRIO-CS-001 | TARA-001, TARA-009, TARA-025 | SCPU shall remain the authority for safety-configuration acceptance and shall verify completeness, iParCRC, parameter dependencies, and F_Dest address consistency before activation. | Supported. | 
| SRIO-CS-002 | TARA-003, TARA-004, TARA-010 | SRIO shall continue to treat PROFIsafe integrity and timeout failures as safe-communication faults that lead to documented fallback, safe-state, and diagnostics behavior. | Supported. | 
| SRIO-CS-003 | TARA-005, TARA-007, TARA-008, TARA-024 | The IoTCore production exposure model shall be explicitly defined. If no authentication is implemented, the restricted machine-network and trustworthy-operator assumptions shall be treated as mandatory external constraints. | Partially supported; gap remains. | 
| SRIO-CS-004 | TARA-006, TARA-013, TARA-019 | Update mode shall only be entered under the documented local preconditions, including rotary-switch value `999` and reboot into update state. | Supported. | 
| SRIO-CS-005 | TARA-006, TARA-014, TARA-015, TARA-016 | Firmware update acceptance for COM and SCPU shall include a documented authenticity policy in addition to the already documented compatibility and consistency checks. | Open issue. | 
| SRIO-CS-006 | TARA-008, TARA-009, TARA-010, TARA-011 | The COM-to-SCPU boundary shall continue to enforce a fail-safe model where COM-side faults cannot silently override SCPU safety decisions. | Supported in architecture intent, but implementation-hardening evidence is incomplete. | 
| SRIO-CS-007 | TARA-017, TARA-018, TARA-021 | DI, DO, and supply-related faults shall continue to produce documented safe-state, qualifier, and diagnostic behavior rather than silent unsafe operation. | Supported. | 
| SRIO-CS-008 | TARA-020 | Debug and test interfaces shall have documented production lock-down or documented physical/service controls that are verifiable at release. | Open issue. | 
| SRIO-CS-009 | TARA-019, TARA-024, TARA-025 | Product documentation shall continue to state system responsibilities for firewalling, restricted access, trusted controller context, and local physical protection. | Supported, but needs to remain explicit. | 
| SRIO-CS-010 | TARA-011, TARA-022 | Authoritative diagnostic truth shall remain on the documented safety/control path, while LEDs and COM-side user-facing diagnosis remain clearly identified as secondary or informational. | Supported. | 
| SRIO-CS-011 | TARA-007 | Production enablement of the IoT FIT service shall be explicitly justified, restricted, or removed. | Open issue. | 

## 10. Product vs. System Responsibility

| Topic | Product responsibility | System / operator / integrator responsibility |
| --- | --- | --- | 
| PROFIsafe integrity and fallback | Yes. | No. | 
| Configuration completeness, iParCRC, parameter dependency checks | Yes. | No. | 
| Update mode gating by rotary-switch value and reboot | Yes. | Operator must control physical access to the switch and reboot event. | 
| Firmware authenticity policy | TBD. Current documentation only proves compatibility and consistency checks. | Shared, because deployment alone cannot compensate for missing product authenticity checks. | 
| IoTCore reachability and firewall placement | Product only documents assumptions; it does not document compensating internal access control. | Yes, primarily system responsibility. |
| Controller / F-Host hardening | No. | Yes. | 
| Physical protection of field wiring, debug access, and local service access | Partially, where product can lock or document interfaces. | Yes, primarily. | 
| DI/DO fault detection and safe-state behavior | Yes. | External actuator/sensor selection and wiring remain system responsibilities. |
| Power-quality protection | Product-side detection/protection is documented. | Installation quality and daisy-chain loading remain system responsibilities. | 

## 10.1 Missing Coverage and GSDML Scope Clarification

- Asset coverage status: Core asset model `A` to `H` is covered for integrity, authenticity, separation, mode integrity, monitoring, and availability concerns.
- Missing asset type: A confidentiality-focused asset is not present in the `A` to `H` set. This is why pure read-only information disclosure scenarios do not always have a direct `A` to `H` mapping.
- Scenarios without direct `A` to `H` mapping: `TARA-005`, `TARA-022`, and `TARA-024`.

- GSDML scope status: GSDML is not out of scope for this TARA where it affects runtime safety configuration exchange (`IF-01`, `TARA-001`, `TARA-025`) because the engineering configuration path directly influences F-Parameters / iParameters.
- GSDML boundary for this revision: Tool-chain lifecycle controls for GSDML generation, signing, packaging, distribution, and operator tool trust are treated as system/process scope unless explicitly specified in the supplied SRIO product documentation.

## 11. Open Issues

1. Update authenticity is not documented. The supplied SRIO sources document compatibility and consistency checks, but not cryptographic authenticity checks for update containers or safe firmware.
2. Anti-rollback protection is not documented. The supplied SRIO sources explicitly allow downgrade.
3. IoTCore authentication and role separation are not documented. The current documentation instead relies on environment restrictions and read-only design assumptions.
4. The production lock-down mechanism for debug access is not documented in the supplied SRIO sources.
5. The production access policy for the documented FIT service is not documented.
6. The original source TARA numbering is inconsistent because `TARA-012` is missing while the dashboard states 25 scenarios.
7. The current asset set does not contain a confidentiality-specific asset, so pure read-only information disclosure scenarios cannot always be mapped directly to assets `A` to `H` without overstatement.
8. GSDML runtime influence is in scope via `IF-01` and existing TARA scenarios, but no explicit product-level controls are documented for GSDML supply-chain trust (generation/distribution/integrity assurance in engineering workflow).

## 12. Detailed Revision Log

### 12.1 Global changes

| Area | Material change from source analysis | 
| --- | --- | 
| Evidence method | Replaced source-independent security assumptions with device-document evidence only. | 
| Safety impact method | Reclassified many scenarios so that fail-safe fallback or safe-state handling maps first to `H` and only conditionally to `A`. | 
| IoT assumptions | Removed unsupported assumptions about authenticated/role-based IoT access and treated IoTCore exposure as an open issue or system precondition. | 
| Update assumptions | Removed unsupported assumptions about cryptographic signature checks and anti-rollback, while keeping documented compatibility/consistency checks and documented downgrade allowance. | 
| Debug assumptions | Replaced implicit production debug lock assumption with an explicit open issue. | `
| Matrix method | Rebuilt the interface-to-asset matrix with direct/indirect distinction. | 

### 12.2 TARA-specific changes

| TARA ID | Material change from source analysis | 
| --- | --- | 
| TARA-001 | Narrowed direct impact from assumed safety compromise to direct `B, H` and indirect `A, C` because configuration rejection is documented. | 
| TARA-002 | Recast as COM availability/fallback issue, not direct safety-function corruption. | 
| TARA-003 | Kept as safe-process-data concern, but shifted `A` to indirect because PROFIsafe validation is documented. |
| TARA-004 | Raised emphasis on documented fallback and safe stop rather than generic high safety compromise. | 
| TARA-005 | Removed unsupported direct mapping into the existing asset set; treated as reconnaissance with no directly evidenced `A-H` asset compromise. | 
| TARA-006 | Removed unsupported claims of signature-based update verification and kept only documented update-mode gating and compatibility/consistency checks. | 
| TARA-007 | Refocused on documented update/FIT service exposure rather than generic role-based service abuse. |
| TARA-008 | Kept COM-compromise boundary concern but marked parser-hardening assumptions unsupported. | 
| TARA-009 | Reduced direct asset set to configuration integrity first. | 
| TARA-010 | Grounded the scenario in documented SysCom cyclic frame exchange and timeout handling instead of assumed extra integrity layers. | 
| TARA-011 | Reduced direct effect to diagnostic integrity because COM-side diagnosis is informational and secondary. | 
| TARA-013 | Kept update-trigger scenario but grounded it in the documented update command path and rotary-gated update mode. | 
| TARA-014 | Removed unsupported cryptographic-integrity claims and treated safe-container authenticity as an open issue. | 
| TARA-015 | Replaced original anti-rollback mitigation assumption with the documented fact that downgrade is allowed. | 
| TARA-016 | Kept as update availability concern; removed unsupported atomic-update and recovery assumptions. |
| TARA-017 | Kept field-input manipulation, but shifted `A` to indirect because diagnostic and safe-state behavior is documented. | 
| TARA-018 | Kept field-output manipulation, but shifted `A` to indirect because deactivation and qualifier logic are documented. |
| TARA-019 | Grounded the scenario strictly in init-only switch reading and documented valid/invalid number ranges. | 
| TARA-020 | Reduced direct assets to `D, H` and turned production lock into an explicit open issue instead of an assumed control. | 
| TARA-021 | Kept power manipulation mainly as availability concern with fail-safe side effects rather than direct safety corruption. | 
| TARA-022 | Reduced the scenario to operator-information impact and removed unsupported direct safety-asset compromise. | 
| TARA-023 | Reduced direct assets to `E, H` because the documented design should detect internal inconsistency and fail safe. | 
| TARA-024 | Reframed as a system-level exposure condition, not a direct exploit result. | 
| TARA-025 | Kept upstream-controller dependency, but grounded direct effects in `B, C` and left `A, H` conditional. | 