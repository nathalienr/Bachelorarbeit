# Asset-Definitionen

## Variante 1: Funktions- und Sicherheitssicht

1. Gateway-Missionsfunktion (OT/IT Interconnection, Filtering, Routing, Remote Access Mediation)
2. Safety-Enforcement-Funktion (Safe-State Behavior, Safety Integrity Logic)
3. Host-Compute-Plattform (CPU3 und Runtime Stack)
4. Safety-Compute-Plattform (SCPU1/SCPU2 und Safe Runtime/OS)
5. Fieldbus/Network Processing Engine (NetX90 und Protocol Core)
6. Secure Boot und Lifecycle Trust Chain
7. Firmware Images und Update-Artefakte
8. Firmware Update/Install Mechanismen
9. Persistenter Speicher fuer Code und Security-Daten
10. Device Identity und Trust-Daten
11. Security-Konfigurationsdaten
12. Safety-Konfigurationsdaten
13. Factory Reset und Reprovisioning-Faehigkeiten
14. OT-Conduit Interfaces
15. IT- und Remote-Management-Conduit Interfaces
16. Interne Inter-Processor-Conduits
17. Debug-, Programming- und Test-Access-Pfade
18. Physische I/O-Interfaces und Field Wiring Boundary
19. Power- und Electrical-Isolation-Domain-Assets
20. Availability- und Fault-Detection-Mechanismen
21. Operational Logging, Diagnostics und Timebase
22. Engineering-Integrationsartefakte und Channel
23. Security/Safety-Dokumentation mit Cyber-Relevanz
24. Physische Maintenance-/Konfigurationsaktoren

## Variante 2: Architektur- und Lifecycle-Sicht 

1. **Hardware:** CPU3, SCPU1, SCPU2, NetX90, Watchdog, Isolatoren, eFUSE, Flash, EEPROM, Ports, Power, FE, Rotary Switch, DI/DO, LEDs
2. **Firmware/Software/OS:** Bootloader CPU3, Bootloader SCPU1/SCPU2, Safe uCOS-II, aktive/gestagte Firmware-Images, Downgrade-Faehigkeit, FW\_UPDATE State
3. **Kommunikationsschnittstellen und Services:** Web HTTP, SysCom, IPC, Debug/Programming, eRPC, Shared Memory, DCP, FIT, Device Control, Firmware Transfer, Acyclic Writes, GSD Channel
4. **Daten- und Konfigurationsassets:** zyklische/azyklische Prozessdaten, Device/App Tags, Safe Address, iParameters, F-Parameters, GSD/GSDML, I\&M, Error Log, Uptime, Zeitbasis, iPar CRC, Diagnosereadouts
5. **Security-relevante Mechanismen/Zustaende:** Safe-State-Logik, Production-Fuse/Production-Mode, externes CRC-Tool
6. **Dokumentation/Supply Chain:** Release Notes, Safety Manual, User Manual

## Variante 3: Detaillierte Asset-Register-Sicht

1. Safe Input Process Data
2. Safe Output Process Data
3. Safety Application Parameters (iPar)
4. Safe Fieldbus Parameters (F-Parameters)
5. Own Safe Address (F\_Dest\_Address)
6. Network Configuration Data
7. Device Identity und I\&M Data
8. Installed Firmware and Bootloader Software
9. Firmware Update Container
10. Error Log and Diagnostic History
11. Device Status and Monitoring Data
12. Persistent Remanent Data
13. GSDML Device Description

## Variante 4: Kompakte Domaenen-Sicht

* Process Data: F-DI/F-DO Daten, Qualifier, zyklische PROFINET-Daten
* Safety Configuration: F-Address, PROFIsafe Parameter, Safety-Einstellungen
* Configuration Data: IP-Adresse, Hostname, Netzwerkparameter, Device Settings
* Firmware: COM, NetX90, Bootloader, Update-Container
* Diagnostic and Service Data: Error Log, Statusinformationen, Diagnose
* Device Identity Data: Seriennummer, I\&M-Daten, Produktinformationen
* Persistent Storage: EEPROM, remanente Daten
* Communication Interfaces: PROFINET/PROFIsafe, IoT-Core, SysCom
* Physical Configuration Elements
* GSDML

