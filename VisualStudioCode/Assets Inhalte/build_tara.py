# -*- coding: utf-8 -*-
"""
Builds TARA_SRIO_Optimized.md and TARA_Improvement_Report.xlsx from a single
curated dataset that reconciles TARA_srio.md (project TARA, 158 threats /
10 data-centric assets) with TARA_Generated.md (spec-derived TARA, 245
threats / 75 component-centric assets).
"""
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

# ---------------------------------------------------------------------------
# 1. Master asset taxonomy (component-centric, consolidated from 75 -> 55)
# ---------------------------------------------------------------------------
ASSETS = {
"A01": ("Host CPU3 (COM, VHIP3 core)", "STM32F777NI Cortex-M7 non-safe communication controller running Communication Module Software, IoT-Core, Fieldbus-Delegator."),
"A02": ("Safety CPU1 (SCPU1)", "STM32F777 safety controller executing safe DI/DO logic, PROFIsafe stack, safety parameter validation."),
"A03": ("Safety CPU2 (SCPU2)", "Second diverse-redundant safety controller (1oo2 with SCPU1); cross-monitors CPU1."),
"A04": ("NetX90 Fieldbus Chip", "Hardware building block implementing the PROFINET/Ethernet physical and protocol layer."),
"A05": ("Hardware Watchdog (SPI6, CPU1<->CPU2)", "Independent watchdog logic bridging SCPU1/SCPU2, enforcing safe-state on CPU hang/failure."),
"A06": ("Digital Isolators (Logic<->Output Domain, 2x)", "Galvanic isolation components separating the SysCom/logic domain from the output driver domain."),
"A07": ("eFUSE (Actuator Overcurrent Protection)", "Electronic fuse protecting the actuator supply/output switching path against overcurrent."),
"A08": ("Groupswitch (Output Switching Stage CH1/CH2/M)", "Output switching stage driving F-DO1/F-DO2/GND_UA; safety-relevant actuator control element."),
"A09": ("Cross-Temperature Sensors (CPU1<->CPU2)", "Mutual temperature monitoring inputs used for diagnostic cross-checking between the two safety CPUs."),
"A10": ("Oscillators (CPU1/CPU2/CPU3)", "Independent clock sources per controller; failure affects timing and diagnostics integrity."),
"A11": ("Power Supply Module (US/UA Domains incl. Isolation Boundary)", "Converts US/UA 24V domains, generates internal 3V3 supplies with reinforced/double-insulated isolation between sensor and actuator supply; includes monitoring block."),
"A12": ("SysCom Interface (SPI, COM<->SCPU1)", "Internal transport between Host CPU3 and Safety CPU1 carrying cyclic process data and acyclic error events; crosses the non-safe/safe boundary."),
"A13": ("IPC Interface (SCPU1<->SCPU2, SPI2/I2C)", "Inter-processor link between the two safety controllers used for cross-comparison and watchdog signaling."),
"A14": ("Debug/Programming Interfaces (JTAG/SWD, per CPU)", "JTAG/SWD debug and flashing connectors for CPU1, CPU2 and CPU3; intended for development phase only, forming a physical boundary to firmware/memory."),
"A15": ("eRPC Service Interface", "Asynchronous RPC-based service channel (erpcgen) used for non-real-time configuration/diagnostics."),
"A16": ("Shared Memory Data Interface (Fieldbus<->IO-Delegator)", "Low-latency shared-memory channel carrying process data between the fieldbus stack and IO handling."),
"A17": ("PROFINET Fieldbus Ports (x2, M12 D-coded)", "External Ethernet interface, 100BASE-TX, supporting IRT, MRP and DCP; connects the device to the PLC network."),
"A18": ("IoT-Core Web Interface (HTTP)", "Non-safety HTTP web interface (max. 2 connections, SRIO-7909) providing device info, diagnostics, /devicecontrol (signal/reset) and firmware-update trigger services."),
"A19": ("DCP Protocol Service (Set/Identify/Reset, Factory Reset Modes 1-9)", "PROFINET Discovery and Configuration Protocol; allows IP/NameOfStation change, LED identify, and factory reset of application, communication (incl. DHCP/SNMP OIDs) and engineering data (SRIO-7772)."),
"A20": ("Cyclic/Acyclic Fieldbus Process Data (incl. Parameter Write)", "PROFINET cyclic (17B in / 15B out) and acyclic process/parameter data exchange, including engineering-tool parameter writes during the parameterization phase."),
"A21": ("EEPROM - COM (CPU3)", "128Kbit EEPROM storing non-safe device configuration and device info."),
"A22": ("EEPROM - SCPU1", "Persistent storage of safety parameters/state for Safety CPU1 (SRIO-1258)."),
"A23": ("EEPROM - SCPU2", "Persistent storage of safety parameters/state for Safety CPU2; must stay consistent with SCPU1 for 1oo2 comparison."),
"A24": ("Internal Flash (CPU3, 2MB)", "Stores the Host CPU firmware image and instructions."),
"A25": ("External Flash (32Mbit)", "Staging/update storage for firmware images (VHIP3 core)."),
"A26": ("Shared Update Flash", "Flash region shared across CPU1/CPU2/CPU3, used during firmware update distribution."),
"A27": ("Error Log (Circular Buffer)", "Persistent circular buffer, >=100 entries, readable via IoT-Core; contains ErrorEvents from COM and SCPU; fully cleared on every coldstart (SRIO-10663/SRIO-6521)."),
"A28": ("Device Tag / Application Tag", "User-writable persistent identifier string (max. 31 chars) stored via the IoT-Core tree."),
"A29": ("Rotary Switch Physical Input (Safe Address 0-899 / FW-Update 999)", "Physically settable value selecting the own PROFIsafe address or forcing the device into FW_UPDATE boot mode (SRIO-2013)."),
"A30": ("Safety Application Parameters (iParameters + iPar CRC)", "Persistent safety-relevant parameters (filter time, symmetry, discrepancy time) protected by an iPar CRC generated with an externally certified tool (SRIO-9023)."),
"A31": ("PROFIsafe F-Parameters", "Safety fieldbus parameters: F_Source_Add, F_Dest_Add, F_Passivation, watchdog time (F_WD_TIME)."),
"A32": ("I&M Data (I&M0-I&M5)", "Identification & Maintenance records exposed via PROFINET, resettable via DCP."),
"A33": ("GSD/GSDML File & Distribution Channel", "Device description file (VendorID/DeviceID, identity, module/F-parameter definitions, SRIO-3019/3020/3021) used by engineering tools, including the process by which it reaches customers."),
"A34": ("Fieldbus Network Configuration Data", "IP address, subnet mask, default gateway, hostname, DHCP mode and SNMP writeable OIDs exposed under /fieldbussetup/network (SRIO-2948)."),
"A35": ("Uptime Counter", "4-byte persistent-until-coldstart uptime value."),
"A36": ("IoT-Core Firmware Upload (BLOB Container)", "/firmware/container service accepting a chunked (2048 byte) firmware BLOB upload up to 4,128,768 byte over HTTP (SRIO-2953)."),
"A37": ("Firmware Install & Downgrade Service", "/firmware/install service triggering a reboot to apply an uploaded image; the documented mechanism also permits installing older firmware versions (rollback)."),
"A38": ("FW_UPDATE Operating State", "Dedicated system state (SRIO-2022) handling the firmware update process across COM and SCPU subsystems."),
"A39": ("Bootloader - Host CPU3 (COM/VHIP3)", "Host controller bootloader responsible for loading and validating firmware images."),
"A40": ("Bootloader - Safety CPU1/CPU2", "Safety controller bootloaders (versioned)."),
"A41": ("F-Digital Input Channels (DI 1-12)", "Safety input channels (up to SIL3/PLe) reading sensor states, incl. test-pulse sensor supply."),
"A42": ("F-Digital Output Channels (DO 1-4)", "Safety output channels (up to SIL3/PLe) switching actuators, PP/PM switching modes."),
"A43": ("Field Wiring <-> DI/DO Boundary", "Boundary between external sensors/actuators and internal I/O circuitry."),
"A44": ("Power Connectors (XD1 In / XD2 Out) & Daisy-Chain Path", "Physical power path enabling daisy-chained devices; current-limiting and FE routing relevant."),
"A45": ("Functional Earth (FE) Path", "Common FE routing from Power-In to Power-Out; EMC/safety relevant."),
"A46": ("Safe uCOS-II OS (SCPU1/SCPU2)", "Certified safe operating system providing freedom-from-interference between safe/non-safe partitions."),
"A47": ("Safe State Logic (Init/Error/FATAL_ERROR states)", "State machine ensuring outputs revert to a defined safe state on error, power-cycle or fatal failure."),
"A48": ("Production Fuse Flag (Production-Mode Boundary)", "Internal flag distinguishing production vs. development mode, gating hidden/test tree elements and disabling JTAG/SWD (SRIO-2580)."),
"A49": ("CRC-Tool (External, Certified T2)", "Externally developed, TUeV Sued-certified offline tool used to generate the iPar CRC; supply-chain asset (SRIO-9023)."),
"A50": ("Release Notes (per FW version)", "Documentation of user-relevant changes; supports secure update decision-making."),
"A51": ("Safety Manual / User Manual", "Documentation covering wiring, parameterization, SIL/PL claims and security assumptions."),
"A52": ("Voltage/Current/Temperature Diagnostic Readouts", "Non-safety telemetry exposed via IoT-Core for maintenance."),
"A53": ("LED Indicators (RDY, BF, SF, P, FS, LNK, ACT, US, UA, Port LEDs)", "Non-safety status indicators; misleading operators if compromised."),
"A54": ("System Time / Systick Counter", "/systemtime/systick value used for diagnostics/timestamps, not persistent."),
"A55": ("FIT Service Interface (/fit/setfit + physical Test Interface)", "Fault Injection Test trigger reachable via IoT-Core (production-fuse gated, SRIO-17129/17130) and via the physical/dev test interface."),
}

rows = []      # master TARA rows
findings = []  # improvement report rows
_counter = {}

def T(asset, stride, desc, goal, attacker, rationale, test_obj, method, source, action):
    n = _counter.get(asset, 0) + 1
    _counter[asset] = n
    tid = f"TH-{asset}-{n}"
    name, adesc = ASSETS[asset]
    rows.append({
        "id": tid, "asset": name, "desc": adesc, "stride": stride,
        "threat_no": n, "threat_desc": desc, "goal": goal, "attacker": attacker,
        "rationale": rationale, "test_obj": test_obj, "method": method,
        "source": source, "action": action,
    })
    return tid

def F(finding_id, asset, threat, issue_type, old, new, reason, action):
    findings.append({
        "id": finding_id, "asset": asset, "threat": threat, "issue_type": issue_type,
        "old": old, "new": new, "reason": reason, "action": action,
    })
