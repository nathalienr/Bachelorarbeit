Group 1 – Processing Hardware

Asset ID	Asset Name	Asset Description

A-001	CPU3 / VHIP3 Core (STM32F777NI)	Host Communication CPU. Runs the COM module firmware (non-safe, µCOS-II), manages IoT Core, fieldbus integration via NetX90 (QSPI/SPI3), SysCom link to SCPU (SPI1), and access to shared update Flash (SPI5). 2 MB onboard Flash, 768 kB RAM.

A-002	CPU1 / Safe CPU1 (STM32F777NI)	Safety Controller 1. Runs safe µCOS-II. Primary safe CPU responsible for DI/DO process data, parameter handling, and PROFIsafe communication. Connected to COM via SysCom (SPI1/IPC), to EEPROM via SPI4, and to CPU2 via IPC (SPI2) and I2C.

A-003	CPU2 / Safe CPU2 (STM32F777NI)	Safety Controller 2. Runs safe µCOS-II. Secondary safety CPU, redundant partner to CPU1 for diversity/redundancy. Reads DO LED and I/O signals (SPI5), communicates with CPU1 via IPC (SPI2) and I2C, connected to its own EEPROM (SPI4).

A-004	NetX90 Fieldbus Chip	Third-party Ethernet fieldbus controller implementing PROFINET 2.4MU3 and PROFIsafe on behalf of the device. Connected to CPU3 via QSPI/SPI3. Runs its own embedded PROFINET stack (fieldbus firmware). Manages the two Ethernet physical ports (XF1, XF2).

A-005	Watchdog Hardware (Matchdog)	Hardware watchdog controlled by both safe CPUs and monitored by COM. Independent hardware element that supervises CPU liveness. Prevents the safe system from remaining in an undefined state. Located in the SCPU subsystem boundary.

A-006	Oscillators (CPU1, CPU2, CPU3)	Independent clock sources for each of the three CPUs. Safe CPUs each have their own oscillator to support independent timing in redundant architecture.

A-007	Temperature Sensors (CPU1 / CPU2 area)	Hardware temperature monitoring for CPU1 and CPU2. Values are read via I2C and reported via IoT Core and potentially via fieldbus diagnostics. Used for functional safety condition monitoring.

A-008	Monitoring Circuit – DI Module	Hardware monitoring function on the DI module. Supervises sensor supply current, detects over-current conditions per port, and enables isolated diagnostics per port (SRIO-797).

A-009	Monitoring Circuit – DO Module	Hardware monitoring on the DO module. Supervises actuator current, enables overcurrent detection, short-circuit protection and switch-off capability testing (test pulses) for F-DO channels.

A-010	Digital Isolators – DI Side	Galvanic isolation components between SCPU logic and the DI field-side circuitry. Enforce electrical separation between the safety logic domain (3V3\_2S) and the sensor field domain (3V3\_2A). Trust boundary element.

A-011	Digital Isolators – DO Side	Galvanic isolation components between SCPU logic and DO field-side circuitry. Enforce electrical separation between the safety logic domain (3V3\_1S) and the actuator domain (3V3\_1A). Trust boundary element.

A-012	eFUSE – DO Module	Electronic fuse protecting the DO module from overcurrent. Part of the power integrity and safety architecture on the actuator supply (UA domain).

A-013	Groupswitch – DO Module	Group switch controlling power to multiple DO channels. Can cut power to the DO output group as part of the safe-state reaction.

A-014	Switch CH1, Switch CH2 (F-DO)	Individual high-side switching components for F-DO1 and F-DO2. PP-switching or PM-switching capable. Controlled by SCPU; subject to switch-off test pulses (testpulse) to verify switch-off capability.

A-015	Switch M – DO Module	Low-side switch for PM-switching mode of digital outputs. Controlled by SCPU alongside high-side switches CH1/CH2.

Group 2 – Physical I/O and Connectors

Asset ID	Asset Name	Asset Description

A-016	DI Module – Port Circuitry (X1–X6)	Functional circuitry for 6 safety digital input ports, each with 2 channels (F-DI1, F-DI2) and a switchable sensor supply (TSOut1, TSOut2). Supports ZVEI Type A and Type C sensor interfaces. Connected to SCPU via Digital Isolators.

A-017	DO Module – Port Circuitry (X7–X8)	Functional circuitry for 2 safety digital output ports, each with 2 channels (F-DO1, F-DO2), supported by eFUSE, Groupswitch, and switching components. Supports ZVEI Type C and Type D actuator interfaces.

A-018	Sensor Supply (TSOut1/TSOut2 per DI Port)	Switchable 24 V sensor supply (derived from US domain) per DI port channel. Used for test pulse generation in ZVEI Type C mode and passive sensor power. Externally accessible via DI port connector pins 1 and 5.

A-019	Power Input Connector (XD1)	M12, L-coded, male. External power input for both US (sensor) and UA (actuator) domains. PELV 24 V DC. Entry point for external supply; carries US+, US-, UA+, UA-, FE.

A-020	Power Output Connector (XD2)	M12, L-coded, female. Daisy-chain power output. Passes US and UA to the next device in the chain. Same signal set as XD1.

A-021	DI Port Connectors (X1–X6)	6× M12, A-coded, 5-pin, female. External input connectors for connecting safe sensors (ZVEI Type A/C). Each carries: TSOut1 (pin 1), F-DI2 (pin 2), GND-US (pin 3), F-DI1 (pin 4), TSOut2 (pin 5). Externally accessible.

A-022	DO Port Connectors (X7–X8)	2× M12, A-coded, 5-pin, female. External output connectors for safe actuators (ZVEI Type C/D). PP-switching: F-DO2 (pin 2), GND-UA (pin 3), F-DO1 (pin 4), FE (pin 5). PM-switching: F-DO1 (pin 4) only. Externally accessible.

A-023	Fieldbus Connectors (XF1, XF2)	Two Ethernet fieldbus ports (100BASE-TX, IEEE 802.3u). M-coded or Ethernet-standard connectors on the COM module. Externally accessible network entry points for PROFINET and PROFIsafe traffic. Media Redundancy Protocol (MRP client) supported.

A-024	Functional Earth Connection (FE)	Functional earth pin provided on power connectors (XD1/XD2) and DO port connectors. Used for EMC purposes (not PE/safety earth). Cable length restricted to ≤3 m (SRIO-20173).

A-025	Rotary Switches (3×)	Three physical 0–9 rotary switches. Set the device's own safe PROFIsafe address (1–899) or select special modes: 0 = delivery/factory state, 999 = FW\_UPDATE mode. Physically accessible upon housing access. Configuration-critical physical component.

A-026	LED Indicators	HMI status indicators: RDY (host CPU), BF (bus failure), SF (system failure), P (PROFIsafe state), FS (safe state/fail-safe), LNK (fieldbus link), ACT (speed), UA (actuator supply), US (sensor supply), Port-Channel LEDs. Non-safety-relevant for control; safety-relevant for diagnostics observability.

Group 3 – Firmware and Software

Asset ID	Asset Name	Asset Description

A-027	COM Module Firmware (VHIP3)	Firmware running on CPU3 (STM32F777NI). Implements: IoT Core application, SysCom IO-Delegator, Fieldbus-Delegator, Device-Delegator, NVMEM-Delegator, error handling, LED control, uptime tracking. Non-safe (QM). Updated via IoT Core firmware update mechanism.

A-028	SCPU Firmware (CPU1 + CPU2)	Functional safety firmware running on CPU1 and CPU2 (safe µCOS-II). Implements: PROFIsafe protocol, safety DI/DO logic, parameter validation, IPC communication, self-test routines, FATAL\_ERROR state management. Safety-critical (SIL 3 / PLe).

A-029	NetX90 Fieldbus Firmware	Embedded PROFINET stack and PROFIsafe firmware running inside the NetX90 chip. Manages PROFINET conformance class C, Net Load III, MRP, IRT support, DCP, and I\&M data exposure. Updated as part of the overall FW update.

A-030	ifm IoT Core Application	Embedded web application (IoT Core Visualizer) accessible via HTTP at device IP. Exposes the IoT Core tree: device info, device status, DI/DO states, fieldbus setup, error log, and firmware update endpoint. No HTTPS/WebSocket/MQTT.

A-031	µCOS-II RTOS (COM, non-safe)	Non-safety real-time operating system for CPU3. Provides task scheduling, IPC, and OS services for the COM module software. Freedom-of-interference mechanisms prevent non-safe partitions from interfering with safe data.

A-032	Safe µCOS-II RTOS	Safety-certified real-time operating system (from Micrium) used on CPU1 and CPU2. Provides safe partitioning of safe and non-safe code regions with MPU-based isolation.

A-033	CPU Bootloader (COM/CPU3)	Boot loader for the VHIP3/CPU3. Manages initial hardware startup, firmware validity check, and transition into FW\_UPDATE state.

A-034	SCPU Bootloader (CPU1 / CPU2)	Safety CPU bootloaders. Support firmware update reception and integrity validation before handing control to SCPU firmware. Version exposed via IoT Core (/deviceinfo/swinfo/scpubootloaderversion).

A-035	GSD File (GSDML)	PROFINET General Station Description (XML). Defines device identity (VendorID 0x0136, DeviceID 0xAC25), modules/submodules, F-parameters, I\&M capabilities, and process data layout. Distributed to PROFINET engineering tools (e.g., TIA Portal). Integrity protected by F\_ParDescCRC.

Group 4 – Internal Communication Interfaces

Asset ID	Asset Name	Asset Description

A-036	SysCom Interface (SPI1)	Internal synchronous SPI-based communication channel between CPU3 (COM) and CPU1 (SCPU). Carries cyclic process data (IO-Delegator, 2 ms cycle), error events, commands (COMCommand), and remanent data. Timeout detection implemented; loss triggers diagnostic event.

A-037	IPC Interface (SPI2)	Inter-Processor Communication between CPU1 and CPU2 (safe CPUs). Used for synchronization, safety state exchange, and diagnostic data sharing between the two redundant safety controllers.

A-038	QSPI Interface (CPU3 ↔ NetX90)	Quad-SPI interface between VHIP3 core (CPU3) and the NetX90 fieldbus chip. Carries fieldbus process data, configuration commands, and boot control signals (boot-select, DIRQ, SIRQ interrupt lines).

A-039	SPI4 – COM-side EEPROM	SPI interface between CPU1 and the EEPROM connected to the COM/SCPU subsystem. Used by the NVMEM-Delegator to store and restore persistent device configuration data.

A-040	SPI4 – SCPU-side EEPROM	SPI interface between CPU2 and the EEPROM on the SCPU module. Stores safety-relevant persistent data for the secondary safe CPU.

A-041	SPI5 – Shared Update Flash	SPI interface between CPU3 and the external 32 Mbit Flash chip. Used for firmware image storage and the firmware update process. Also accessible by CPU2 for LED/IO data (SPI5 shown in block diagram).

A-042	SPI6 – LED Control	SPI interface for LED control signals originating from CPU1, driving the status and diagnostic LEDs (P, FS, UA, US, Port-Channel LEDs).

A-043	I2C – Temperature Monitoring	I2C bus connecting CPU1 and CPU2 for cross-monitoring of CPU temperature values. Temperature readings are reported via IoT Core and used in derating/diagnostic functions.

Group 5 – External Communication / Fieldbus Interfaces

Asset ID	Asset Name	Asset Description

A-044	PROFINET Interface	Industrial Ethernet fieldbus protocol (PROFINET IO Device, v2.4MU3+). Conformance Class C, Net Load Class III. Externally accessible over XF1/XF2. Carries cyclic process data (DI/DO states, qualifiers), acyclic records (parameters, I\&M), and diagnosis alarms to PROFINET IO-Controller (PLC).

A-045	PROFIsafe Protocol	Safety communication protocol running over PROFINET (black-channel). Implements F-Parameters (F\_Dest\_Add, F\_Source\_Add, F\_WD\_Time, F\_iPar\_CRC, F\_Par\_CRC, CRC-32). Watchdog time 50–10,000 ms. Carries safe process data between F-Host (PLC) and F-Device (SRIO). SIL3-certified channel.

A-046	IoT Core HTTP Interface	Unencrypted HTTP-based management interface accessible via device IP address. Supports up to 2 concurrent incoming connections. Exposes the full IoT Core tree (read/write/service operations). Used for device monitoring, firmware update, and configuration. No HTTPS/WebSocket/MQTT/outgoing connections.

A-047	DCP (Discovery and Configuration Protocol)	PROFINET DCP for IP address and NameOfStation assignment. Allows any PROFINET controller or engineering system to set network parameters at any time. Factory reset (Mode 2/8) resets IP to 0.0.0.0 and NameOfStation to "".

A-048	eRPC Service Interface (Internal)	Embedded Remote Procedure Call framework used internally within the COM module for asynchronous service operations between SW components (Delegators, IoT Core). Not externally accessible; internal software communication boundary.

Group 6 – Persistent Data Storage

Asset ID	Asset Name	Asset Description

A-049	External Flash (32 Mbit)	SPI Flash chip connected to CPU3. Primary storage for firmware images (current and update candidate). Accessed during FW\_UPDATE state to install new firmware.

A-050	EEPROM – COM side (128 Kbit)	Non-volatile EEPROM connected to CPU1 via SPI4. Stores: I\&M1–I\&M3 data (device tag, installation date, descriptor), remanent device parameters, NVMEM state data. Read at startup by NVMEM-Delegator and Device-Delegator. Power-cycle safe.

A-051	EEPROM – SCPU side	Non-volatile EEPROM connected to CPU2 via SPI4. Stores safety-relevant persistent data per the VHPP/BuildingBlocks Device Information layout. Holds device information and state for the secondary safe CPU.

A-052	I\&M Data Records (I\&M0–I\&M5)	PROFINET Identification \& Maintenance records stored in EEPROM. I\&M0: read-only device identity (serial number, HW/SW revision, order ID). I\&M1–3: writable (tag function, location, installation date, descriptor). I\&M4: runtime CRC signature (F\_iParCRC, F\_Par\_CRC). I\&M5: firmware annotation. Factory-reset-sensitive.

A-053	Safety Application Parameters (iPars)	Safety-relevant per-port DI/DO configuration parameters stored in EEPROM and transmitted by the F-Host via PROFIsafe. Includes: F-DI/F-DO enable, testpulse enable/duration, symmetry mode (1oo1/1oo2), discrepancy time, filter time, switch-off delay. Protected by iPar CRC.

A-054	F-Parameters (PROFIsafe)	PROFIsafe safety fieldbus parameters set by the engineering tool (TIA Portal/GSD): F\_Dest\_Add (own safe address via rotary switch), F\_Source\_Add (F-Host address), F\_WD\_Time (watchdog), F\_SIL (SIL3), F\_CRC\_Length, F\_Par\_CRC, F\_iPar\_CRC. Integrity checked end-to-end.

A-055	Network Configuration Parameters	PROFINET network parameters: IP address, subnet mask, default gateway, NameOfStation, DHCP mode, MAC address. Set via DCP or engineering tool. Stored remanently in EEPROM. Exposed read-only via IoT Core (/fieldbussetup/network).

A-056	Device Tag (applicationtag)	User-writable identification string (max 31 characters) stored in EEPROM. Accessible via IoT Core (R/W). Used for plant-level device identification.

A-057	Error Log (Circular Buffer)	RAM-resident circular buffer storing ≥100 error events with uptime timestamp. Contains error events from COM self-detection and SCPU. Cleared on cold start. Accessible via IoT Core service call. Also forwarded to PROFINET diagnosis.

A-058	Uptime Counter	4-byte counter (seconds) tracking device uptime since last cold start. Not persistent across power cycles. Used as timestamp reference in error log entries. Accessible via IoT Core (/systemtime/systick).

Group 7 – Firmware Update Mechanism

Asset ID	Asset Name	Asset Description

A-059	IoT Core Firmware Update (Blob Upload)	Firmware update mechanism via HTTP POST to IoT Core endpoint (/firmware/container). Chunked upload (2048-byte chunks, max \~4 MB). Device must be in FW\_UPDATE state. Initiated by /firmware/install service call. No authentication enforced at protocol level (HTTP only). Behind-firewall assumption per security requirement SRIO-1196.

A-060	FW\_UPDATE Operating State	Special device operating state triggered when rotary switches are set to 999. In this state the device accepts firmware uploads via IoT Core and boots into update mode. All safe I/O functions are suspended during this state.

A-061	Firmware Version Container	Version information exposed via IoT Core (/firmware/version, /deviceinfo/swinfo). Contains: COM FW version, SCPU FW version, COM bootloader version, SCPU bootloader version, fieldbus firmware version. Used for update validation and downgrade decisions.

Group 8 – Trust Boundaries

Asset ID	Asset Name	Asset Description

A-062	Shopfloor Firewall (Assumed)	External network-level security boundary assumed to surround the device (SRIO-9402). The device has no internal authentication or encryption on any external interface. All security relies on this perimeter. Not implemented within the device itself.

A-063	PROFIsafe Safety Protocol Boundary	The PROFIsafe black-channel protocol provides an independent safety communication trust boundary over the untrusted PROFINET network. Integrity protected by CRC-32, sequence numbers, watchdog time, and address checking (F\_Dest\_Add).

A-064	Galvanic Separation (US / UA Domains)	Reinforced/double isolation between the sensor supply domain (US) and actuator supply domain (UA). Fault-excluded per EN ISO 13849-1:2023. Electrical trust boundary preventing faults in one power domain from propagating to the other.

A-065	Digital Isolator Boundary (SCPU ↔ DI/DO)	Galvanic isolation between the SCPU logic domain (3V3\_2S / 3V3\_1S) and the field-side DI/DO circuitry (3V3\_2A / 3V3\_1A). Prevents field-side disturbances or attacks from directly reaching the safety CPUs.

A-066	Debug / Programming Interface (Restricted)	PCB-level debug interface (JTAG/SWD-equivalent). Requirement states it shall be usable only during development phase (SRIO-2580). Represents a critical trust boundary: if accessible in the field, it provides full CPU access. No field protection mechanism documented.

A-067	FIT / Test Interface (Restricted)	Fault Injection Test interface used to trigger software FITs and receive error messages (SRIO-1526). Intended for development/production phase only. If accessible, it can trigger deliberate faults in the safety system.

Group 9 – Supporting / Regulatory Assets

Asset ID	Asset Name	Asset Description

A-068	TÜV Safety Approval (SIL3 / PLe Cat.4)	Third-party certification confirming the device meets IEC 61508:2010 SIL3 and EN ISO 13849-1:2023 Category 4 / PLe. Required approval for use in safety applications. Loss or revocation makes the device legally unusable in safety functions.

A-069	PROFINET Certification (CC-C / Net Load III)	PROFINET conformance certification from the PROFIBUS \& PROFINET International organisation. Required for interoperability with PROFINET controllers. Depends on GSD file integrity.

A-070	PROFIsafe Certification	F-Device certification for PROFIsafe compliance per PROFIBUS \& PROFINET International. Required for acceptance by PROFIsafe masters (F-PLCs).

A-071	iPar CRC Tool (T2 Off-line Support Tool)	Externally certified tool (TÜV Süd accredited) used to calculate the iPar CRC that protects safety application parameters. Classified as T2 offline support tool. If the tool is compromised, incorrect CRC values could allow acceptance of corrupted safety parameters.

A-072	Safety Manual	Published safety manual containing: SIL/PL declarations, parameter tables, wiring instructions, proof test intervals, response time formulas, downgrade procedures, and PROFIsafe operational requirements. Loss of integrity undermines safe commissioning by end users.

A-073	CE / UKCA Declaration of Conformity	Mandatory regulatory declaration covering Machinery Directive (2006/42/EC), LVD (2014/35/EU), EMC (2014/30/EU), RoHS (2011/65/EU). Required per market regulations

