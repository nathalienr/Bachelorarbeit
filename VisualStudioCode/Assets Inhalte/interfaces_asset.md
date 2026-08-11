# Interface Asset Overview

**System:** SRIO – Safe Remote IO (AL400S / AL401S, PROFINET / PROFIsafe, 6x2 F-DI, 2x2 F-DO)

## Interface: Fieldbus
**Interface ID:** IF-01
**Aliases:** "NetX90 - PROFINET Fieldbus" , "PROFINET" , "BB Fieldbus", "Fieldbus [Ethernet]" 

### Description
External Ethernet-based fieldbus connection of SRIO to the F-Host/PLC. Implemented via the NetX90 SoC inside the COM module (CPU3), running the PROFINET stack. The safety protocol PROFIsafe is tunneled through PROFINET using the black-channel principle, keeping COM itself non-safety-related while SCPU handles the safety application. 

### Connected Components
- COM (CPU3, Host application)
- NetX90 (PROFINET stack / SoC)
- Two Fieldbus Connectors (M12, D-coded, female) – XF1 / XF2
- PLC / F-Host (upper controller)
- Downstream fieldbus devices (via internal NetX90 switch, daisy-chained PROFINET)

### Assets
| Asset | Description | 
|---|---|
| PROFINET communication (cyclic/acyclic) | Process data exchange and acyclic record access with the PLC | 
| Device configuration / DCP protocol | Device naming, IP assignment, factory reset (DCP Mode 1–9) 
| PROFINET diagnosis / process alarms | Channel/diagnosis alarms mapped to fieldbus diagnosis 
| Cyclic process data path (input/output data) | DI/DO mapping incl. qualifiers, PROFIsafe status/control byte | 
| Internal NetX90 switch / downstream devices | Deactivation could impact daisy-chained fieldbus devices | 
| PROFIsafe frame (black-channel) | Safety communication tunneled through PROFINET | 
| GSD file / Device Identity (Vendor ID, Device ID, F-Parameters) | GSDML file describing modules, submodules, F-Parameters | 
| I&M data (I&M0–I&M5) | Identification & Maintenance data (order ID, serial no., HW/SW revision, FW annotation) | 
| Fieldbus connector / pinout | M12, D-coded, female; TD+/RD+/TD-/RD- | 
| Network identification (MAC/IP/subnet/gateway/hostname, DHCP mode) | Exposed also via IoT-Core `/fieldbussetup/network` | 
| MediaRedundancyProtocol (MRP) / Port deactivation | Fieldbus resiliency and port management |

---

## Interface: IoT-Core
**Interface ID:** IF-02 
**Aliases:** "NetX90 - IoT API", "ifm IoT-Core" / "Webserver ifm IoT Core" , "IoTCore App" 

### Description
Read-mostly web interface for diagnostics, device information, and firmware update, reached via the fieldbus physical port in parallel to PROFINET traffic. Only incoming connections are supported; no outgoing/push connections. Firmware update and the write-capable parts of the tree are gated by the DIL/rotary-switch "Update Mode" (999) and device state. 

### Connected Components
- COM (CPU3) – IoTCore Application
- NetX90 (transport layer, shared with Fieldbus)
- SCPU (CPU1/CPU2) – data source for device status, transmitted cyclically via SysCom
- EEPROM (COM side) – storage for device info elements
- Visualizer (browser-based UI loaded from the device)

### Assets
| Asset | Description | 
|---|---|
| Diagnostic / service functions | Read access to error log, uptime, device status | 
| Configuration data (read) | `/devicetag`, `/fieldbussetup`, `/safecom` elements | 
| Firmware update package / SRIO Update Container | Container with Update Header, NetX90 FW, CPU3 FW, Safe Container (SCPU FW) | 
| Firmware update trigger (`/firmware/install`, `/firmware/container`) | Service to upload and install firmware, requires state "Update" | 
| Test-Interface (trigger SW-FITs) | Development-only interface to trigger Fault Injection Tests / receive error messages | 
| Production-flag / Test-Interface access lock | Access to Test-Interface blocked after development (fusing) |
| Device identification data (deviceinfo) | productcode, productname, vendor, devicefamily, serialnumber, production date, hw/sw revision, bootloader version |
| Device status / diagnosis information | operatingstate, temperature (SCPU1/2, DO1/2), voltage US/UA, current US, rotary switch value, error log | 
| Error Log | Circular buffer, min. 100 ErrorEvents, readable via IoT | 
| Device control (`/devicecontrol/signal`) | Trigger RDY-LED blinking (device identification) | 
| System time / Uptime (`/systemtime/systick`) | Uptime/systick counter, cleared on coldstart | 
| DI/DO process data readout | `/io/di/port[n]`, `/io/do/port[n]` incl. qualifiers and current measurement | 
| FIT trigger (`/fit/setfit`) | Fault Injection Test trigger, write-only, production-mode gated |
| Bootloader (COM) | Hardware-coupled, verifies FW integrity before installing; not itself an interface but an existing control for firmware update | 
| Firmware-Update-File integrity | Risk of forged CAC calculation; no Secure Boot; verified only via official website comparison | 
| HTTP support | Device shall support HTTP (plaintext) | PRS SRIO-7903 <cite>turn1search2</cite> |
| HTTPS/Websocket/MQTT (declared **not** supported) | PRS explicitly states HTTPS, Websocket and MQTT are **not** supported - see Notes/Discrepancies below | 
| Connection limits | Max. 2 simultaneous incoming HTTP connections; incoming-only (no outgoing/push) |
| IoT-Core API / Catalogue version | IoT-Core API V2.0, Catalogue V2.0 | 

---
## Interface: Rotary Switch
**Interface ID:** IF-03
**Aliases:** "Rotary Switch" , "DIL Switches" , "Rotary Switch Interface" 

### Description
Three rotary/DIL switches (each 0–9), physically read only during the Init state, used to set the device's own safe F-Address (1–899) or trigger Firmware Update mode (value 999). Physical, local-access-only interface. 

### Connected Components
- SCPU (CPU1) – reads switch state during Init
- COM (CPU3) – reads rotary switch state for IoT-Core exposure

### Assets
| Asset | Description | 
|---|---|
| Operating mode / function selection | Determines device behavior at boot (address vs. update mode) | 
| Own safe address / F_Dest_Address (1–899) | Safety-relevant own address, validated against PROFIsafe configuration | 
| Firmware Update trigger (value 999) | Boots device into Update state, enables IoT-Core firmware acceptance | 
| Reserved range (900–998) | Reserved for future functionality | 
| Delivery state (0) | Default/factory rotary switch position | 
| Rotary switch value (read via IoT-Core) | `/devicestatus/rotary_switch`, exposed for diagnostics | 
| Physical switch protection (sleeve/seal) | Plastic/metal seals for IP protection, mounted in sleeves | 

---


## Interface: Debug / Test Interface
**Interface ID:** IF-04
**Aliases:** "JTAG / interne Debug-Interfaces" , "Com Debug" / "VHIP3 core Debug", "Debug Interface", "Test interface" 

### Description
Physical debug/programming interfaces (JTAG/SWD/UART-class) for each controller (COM, SCPU1, SCPU2), plus a software-level Test Interface reachable via IoT-Core to trigger SW Fault-Injection-Tests (FITs). Intended for development use only; physically hardened via overmolding and access-locked via fusing after production. 

### Connected Components
- Debug connector / contact plane on PCB (COM)
- VHIP3 core ↔ BB-Fieldbus reset lines
- SCPU1 / SCPU2 debug/programming interfaces
- IoT-Core Test Interface (software trigger)

### Assets
| Asset | Description | 
|---|---|
| Firmware / memory contents / keys-secrets | Readable/writable via physical debug access | 
| Debug interface connector on PCB | Physical connector or contact plane, mandatory presence | 
| Com Debug Reset independence | Debugger can reset BB-Fieldbus without influencing VHIP core (and vice-versa) | 
| Debug Interface (per controller) | Each controller (Host + both Safety Controllers) has its own debug/flash interface, development-phase only | 
| Test Interface (SW-FIT trigger) | Development-only interface for triggering SW Fault Injection Tests / receiving error messages | 
| Access Test Interface lock | Access blocked after development (fusing of required elements) | 
| Overmolding / physical barrier | Device is overmolded, strongly hindering physical debug access | 

---

## Interface: Digital Input
**Interface ID:** IF-05 
**Aliases:** "F-Digital Inputs", "Module DIGITAL INPUT [DI]", "DI" 

### Description
Six safe digital input ports (2 channels each), each supporting ZVEI Interface-Type A (passive sensor, SRIO generates test pulse) or Type C (sensor provides own test pulse, filtered by SRIO). Signal processing (symmetry, filtering, diagnosis) is performed jointly by the DI hardware module and SCPU. 

### Connected Components
- DI Module (HW)
- SCPU (CPU1/CPU2) – signal processing, diagnosis
- M12, A-coded, 5-pin, female connector (per port)
- Connected external sensors (ZVEI Type A/C)

### Assets
| Asset | Description | 
|---|---|
| F-DI1 / F-DI2 safety digital input signal | Safety-relevant input state per channel |
| Sensor supply (TSOut1/TSOut2, US-based) | Switchable test-pulse/supply per channel, used for crosscircuit detection and Sensor Reactivation | 
| Input parameters (iPar): Symmetry, Discrepancy Time, Resolve Symmetry Violation, Filter F-DI1/2, Testpulse Supply 1/2 | Safety application parameters (part of iParCRC-protected set) | 
| Input Connector / pinout | M12, A-coded, 5 pins, female (L+/F-DI2/L-/F-DI1/L+) | |
| DI diagnostic data | Stuck-at-High detection, supply-switch diagnosis, over-current detection, port-isolated error handling | 
| DI process data / qualifier | `/io/di/port[n]/pin{2,4}/digital_input` + qualifier, exposed via PROFINET and IoT-Core | 
| ZVEI Interface-Type A / Type C electrical parameters | Input current/voltage/capacity (Type A); test-pulse timing, input resistance/capacity/inductance (Type C) | 
| Achievable SIL/PL per configuration | 1oo1/1oo2, pulsed/unpulsed combinations mapped to SIL/PL/Category | |
| Cable installation constraints | Indoor use only, ≤30 m, capacitive load 30 m + 20 nF | 

---

## Interface: Digital Output
**Interface ID:** IF-06
**Aliases:** "F-Digital Outputs", "Module DIGITAL OUTPUT [DO]", "DO" 

### Description
Two safe digital output ports (2 channels each), supporting ZVEI Interface-Type C (PP-switching) or Type D (PM-switching), with switch-off test-pulse, watchdog and overcurrent protection (eFUSE, Groupswitch, Digital Isolators). 

### Connected Components
- DO Module (HW): eFUSE, Groupswitch, P/M-Channel switches, Digital Isolator
- SCPU (CPU1/CPU2) – switching control, diagnosis, watchdog
- M12, A-coded, 5-pin, female connector (per port)
- Connected external actuators (ZVEI Type C/D)

### Assets
| Asset | Description | 
|---|---|
| F-DO1 / F-DO2 safety digital output signal | Safety-relevant output state per channel (P/PP/PM switching) | 
| Output parameters (iPar): Symmetry (1oo1 P / 1oo2 PP / 1oo2 PM), Testpulse, Testpulse Duration, Switch-off Delay 1/2 | Safety application parameters (part of iParCRC-protected set) | 
| Output Connector / pinout (PP- and PM-Switching variants) | M12, A-coded, 5 pins, female; incl. FE pin | 
| Overload/short-circuit protection & switching components | eFUSE, Groupswitch, P/M-Switch, watchdog-triggered switch-off | 
| DO diagnostic data | Voltage/current monitoring, single-output failure detection, restart-interlock (acknowledge required) |
| DO process data / qualifier | `/io/do/port[n]/pin{2,4}/digital_output` + qualifier + current measurement | 
| ZVEI Interface-Type C / Type D electrical parameters | Test-pulse timing, rated/leakage current, capacitive/inductive load limits | 
| Achievable SIL/PL per configuration | Unpulsed/pulsed 1-/2-channel combinations mapped to SIL/PL/Category |
| Discharge circuit (external capacitive loads) | Non-safety-related discharge function; faults must not disrupt safety function | 

---



## Interface: SysCom
**Interface ID:** IF-07
**Aliases:** "SysCom - Host [CPU3] ↔ SCPU1" , "System Communication [SysCom]", 

### Description
Internal SPI-based communication link between the non-safety COM module (Host/CPU3) and the Safe CPUs (SCPU1/CPU2). Provides freedom of interference between the IT-side (COM) and the Safe Core, transporting cyclic process data, acyclic configuration data, error events and IoT-Core data via dedicated channels. 

### Connected Components
- CPU3 (COM / Host)
- CPU1 / CPU2 (SCPU, Safe Core, cross-checked pair)
- IO-Delegator, Fieldbus-Delegator, Device-Delegator, NVMEM-Delegator (COM-side software components)
- Watchdog (external HW watchdog)

### Assets
| Asset | Description | 
|---|---|
| Safe-Core isolation / freedom of interference (Rückwirkungsfreiheit) | Domain boundary COM/SCPU; SCPU pushes data unidirectionally/cyclically to Host; reduced command set | 
| Cyclic Data channel | PROFIsafe frame exchange (PD for DI/DO, Qualifiers, Status/Control Byte, CRC), Sensor Reactivation data | 
| Acyclic Data channel | Configuration data (F-Parameter, iPar), Commands between SCPU and Host | 
| ErrorEvent channel | Structured error event (ErrorHeader, ErrorClass, ErrorCode, Channel, Last Value) | 
| IoTCore channel | Transport of IoT data points from SCPU to COM buffer |
| SysCom Commands | e.g. USER_SYS_CMD_UPDATE_START_SAFE, USER_SYS_CMD_READY_FOR_SYNC_COM, USER_SYS_CMD_FB_ABORT_COM | 
| SPI transport / timeout detection | IO-Delegator timeout mechanism; COM triggers error event on SCPU communication loss | 
| System parameters (CPU temperature, current consumption) | Cyclically received/stored values used by IoTCore | 
| EEPROM, Safe Side | Only defined areas writable, remainder read-only; abstracted by NVMEM-Delegator |
| Configuration data transmission structure | F-Parameter + iPar transmitted in 9 messages across Ports 1–8 | 
| TÜV Rückwirkungsfreiheitsnachweis (proof of non-retroaction) | Open item; required certification evidence for the SysCom boundary | 

---


## Interface: Power Supply
**Interface ID:** IF-08 
**Aliases:** "Power Supply Interface" , "Module POWER SUPPLY [PS]" , "Powersupply" / "PowerIn" / "PowerOut" 

### Description
Dual-domain 24 V DC power supply (US for sensors/internals, UA for actuators), galvanically separated, PELV-compliant, with daisy-chain capability via M12 L-coded input/output connectors and internal monitoring/isolation 

### Connected Components
- Powersupply module (HW)
- SCPU (CPU1/CPU2) – voltage/current/temperature monitoring
- Digital Isolators (galvanic separation)
- eFUSE (overcurrent protection, shared with DO)
- Power In / Power Out connectors (M12, L-coded)

### Assets
| Asset | Description | 
|---|---|
| Power Supply US / UA (24 V DC, nominal −15%/+20%) | Two separated power domains for sensors/internals (US) and actuators (UA) |
| Power connector / pinout (Power In / Power Out) | M12, L-coded, male (in) / female (out); FE pin |
| Daisy-chain current distribution | IUS_DaisyChain_Max (11.5 A), IUA_DaisyChain_Max (12 A), 16 A max per pin | 
| Galvanic separation US/UA | Reinforced/double insulation up to 60 V, fault-exclusion per EN ISO 13849-1 | 
| Voltage monitoring US/UA | Over-/Under-voltage detection, HW shut-off | 
| Temperature monitoring (SCPU/DO) | Two-level over-temperature reaction (power reduction, then EC1) | 
| Functional Earth (FE) connection | Common FE from Power In to Power Out; not intended to carry current | 
| Reverse polarity / over-voltage protection | Protection circuits for US/UA inputs | 
| Power-based current limitation (100 W, single-fault) | Fire-prevention limitation per electrical circuit | 
| Power Supply / Daisy Chain (availability) | Availability-relevant; physical protection largely out of scope, customer responsibility | 
| PELV / Protection Class III compliance | External power supply requirement | 

---


## Interface: HMI / LEDs
**Interface ID:** IF-09 
**Aliases:** "HMI" , individual LED requirements 

### Description
Set of status LEDs (RDY, BF, SF, P, FS, US, UA, LNK, ACT, per-channel LEDs) providing visual, none-safety-related status information on host health, bus/system failure, safe communication state, power domains and per-channel I/O state. 

### Connected Components
- COM (CPU3) – RDY, BF, SF, LNK, ACT LEDs
- SCPU (CPU1) – P, FS, US, UA, per-channel I/O LEDs

### Assets
| Asset | Description | 
|---|---|
| LED status information (RDY/BF/SF) | Host CPU health, bus failure, system failure states | 
| LED status information (P/FS) | Safe communication state, device safe/error state | 
| LED status information (US/UA) | Sensor/actuator supply voltage state incl. over/under-voltage | 
| LED status information (LNK/ACT) | Fieldbus link and communication speed | 
| Per-channel I/O LED state | Yellow (signal high) / Red (error) per port channel | |
| LED informational restriction | Explicit note: LEDs are none-safety-related | 
| Device-signal trigger (via IoT-Core) | `/devicecontrol/signal` blinks RDY LED for device identification | 

---



### Cross-Interface Assets (appear under more than one interface)
| Asset | Interfaces | Note |
|---|---|---|
| Network identification (MAC/IP/subnet/gateway/hostname) | IF-01, IF-02/03 | Configured/used by PROFINET, read via IoT-Core `/fieldbussetup/network` |
| Rotary switch value | IF-04, IF-02/03 | Physically read by SCPU; exposed read-only via IoT-Core |
| Error Log | IF-01 (diagnosis), IF-02/03, IF-07 | Populated via SysCom ErrorEvent channel, read via IoT-Core, mapped to PROFINET diagnosis |
| Bootloader / Firmware-Update-File integrity | IF-02/03 | Governs installation of firmware transported via IoT-Core and internally via SysCom/shared update flash |
| EEPROM, Safe Side | IF-07 | Isolated from COM-side EEPROM; only defined areas writable |


## Assets außerhalb Interface-Tabelle, Notizen

| Asset | Begründung | Entscheidung |
|---|---|---|
| Bootloader | Hardware-gekoppelt, nicht updatebar → prüft Firmware-Integrität, verhindert korrupte Installation | Control für IF-03, kein eigenes Interface → als Existing Control dokumentieren |
| Firmware-Update-File | Könnte mit bekannter CAC-Berechnung gefälscht werden; kein Secure Boot | Risk: in IF-03 erfasst; Maßnahme: Integritätsprüfung über offizielle Website; langfristig: Secure Boot |
| EEPROM, Safe Side | Durch SysCom-Isolation abgekapselt; nur definierte Bereiche beschreibbar, Rest read-only | De-priorisiert; kurzer Vermerk in IF-07 ausreichend |
| Power Supply / Daisy Chain | Availability-Relevanz vorhanden; physischer Schutz kaum möglich | Out of scope — Verweis auf Installationsvorschrift / Kundenverantwortung |
| NetX90, Hardware | Interner Switch kann Downstream-Geräte betreffen | In IF-01 mit erfasst |