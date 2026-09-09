
Testumgebung wie ich sie im Labor aufgenaut habe
USB3-zu-Gigabit-Ethernet-Dongle von kali zu switch
switch 192.168.0.91, eine sps 192.168.0.1, das safe remote i/o 192.168.0.2, den kali linux rechner mit 192.168.0.80 und meinen firmenlaptop mit 192.168.0.7. sps ist mit port1 , safe remote i/o ist mit port2, kali-rechner mit port3 und laptop mit port4 vom switch verbunden

Grundlagen?
- Defense-in-Depth Strategie
- Man-in-the-Middle

NV2
switch kann kein port mirroring --> andere switch für die zukunft notwendig
NV3
keine Zeit für umbau von testaufbau

Aus dem Wokrflow.md durchgeführte Tests, bzw. Tests die durchgeführt werden (sind hauptsächlich NV1)
- TC-RQ001-02 - Attack-Surface Enumeration on the Non-Safety Path
%- TC-RQ003-01 - Baseline: What Evidence the Device Actually Collects
%- TC-RQ003-04 - Time-Attribution Failure of Collected Evidence/ TC-RQ012-02 
- TC-RQ004-01 -  Identification-Surface Inventory (SW + Data)
- TC-RQ006-01 -  Installed-Software Inventory Enumeration
%- TC-RQ006-03 - Plaintext Inventory Exposure (Defense-in-Depth Observation)
%- TC-RQ007-01 -  Identification Availability & Accessibility Baseline
%- TC-RQ007-03 -  Connection-Hold Self-DoS on the Identification Interface
%- TC-RQ008-01 - Software-Event Evidence Baseline
%- TC-RQ009-01 - Config-Modification Evidence Surface Baseline
- TC-RQ010-02 - Network/Layer-2 Flood Resilience
- TC-RQ010-04 - Application-Layer Flood & Domain-Separation Confirmation
%- TC-RQ011-01 - Read-Only Enforcement on the Non-Safety Interface 
%- TC-RQ013-01 - Current-Version-Only Confirmation

 
ich habe die Sicherheitstests nach dem ifm Security Testing Framework (CM-001 bis CM-010) in durchgeführt
 
CM-001 - Network Exposure (Nmap): Vollständig durchgeführt (TCP Full-Scan + UDP Top-Ports) und logisches, auswertbares Ergebnis erhalten
 
CM-002 - Netzwerksegmentierung (Nmap): Ich ja kein Conduit-/Zonenmodell, gegen das ein Segmentierungs-Scan sinnvoll verglichen werden könnte....
 
CM-003 - Default/Weak Credentials (Hydra):  Der IoT-Core hat keinen Login (Read-Only-Zugriff ohne Passwortschutz), es gibt also keine Anmeldeoberfläche, gegen die Hydra Zugangsdaten testen könnte
 
CM-004 - RBAC/Privilege Escalation (OWASP ZAP): Technisch durchgeführt (Active Scan + manuelles Durchklicken über ZAP-Proxy), Report gespeichert. Vergleich zweier Rollen auf unzulässige Rechteausweitung ist  nicht anwendbar, da SRIO nur eine einzige, anonyme Read-Only-Rolle hat
 
CM-005 - TLS-Konfiguration (SSLscan):  SRIO kein HTTPS unterstützt --> Port 443 ist nicht offen, wodurch kein TLS-Endpunkt zum Testen existiert
 
CM-006 - Hardening Validation (Lynis): Nicht durchgeführt. Lynis kann ausschließlich Linux-Systeme überprüfen
 
CM-007 - Debug/Service Interface Exposure (Nikto): Durchgeführt gegen den IoT-Core-Webserver, Ergebnis gespeichert.
 
CM-008 - Patch Level/CVEs (OpenVAS/GVM): Hab ich nicht hinbekommen, brauche ich eventuell hilfe
 
CM-009 - Load Behavior & Logging (Siege): Mit 50 Verbindungen (Doku) und mit 3 Verbindungen durchgeführt (Anforderungen)
 
CM-010 - Fuzzing/Robustness (boofuzz): Durchgeführt gegen den HTTP-Port des SRIO. Dabei ist am Gerät ein Fehler mit Code 0x1000 aufgetreten --> schwachstelle von Gerät erkannt, Test fail --> Entwicklung muss das überprüfen