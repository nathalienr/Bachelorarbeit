USB3-zu-Gigabit-Ethernet-Dongle von kali zu switch
switch 192.168.0.91, eine sps 192.168.0.1, das safe remote i/o 192.168.0.2, den kali linux rechner mit 192.168.0.80 und meinen firmenlaptop mit 192.168.0.7. sps ist mit port1 , safe remote i/o ist mit port2, kali-rechner mit port3 und laptop mit port4 vom switch verbunden

- Defense-in-Depth Strategie
- Man-in-the-Middle

- **TC-RQ001-02** - Attack-Surface Enumeration on the Non-Safety Path 
- TC-RQ003-01 - Baseline: What Evidence the Device Actually Collects
- TC-RQ003-04 - Time-Attribution Failure of Collected Evidence/ TC-RQ012-02 -  Cold-Start Deletion ⇄ TC-RQ003-04
- **TC-RQ004-01** -  Identification-Surface Inventory (SW + Data)
- **TC-RQ006-01** -  Installed-Software Inventory Enumeration
- TC-RQ006-03 - Plaintext Inventory Exposure (Defense-in-Depth Observation)
- TC-RQ007-01 -  Identification Availability & Accessibility Baseline
- TC-RQ007-03 -  Connection-Hold Self-DoS on the Identification Interface
- TC-RQ008-01 - Software-Event Evidence Baseline
- TC-RQ009-01 - Config-Modification Evidence Surface Baseline
- **TC-RQ010-02** - Network/Layer-2 Flood Resilience
- **TC-RQ010-04** - Application-Layer Flood & Domain-Separation Confirmation
- TC-RQ011-01 - Read-Only Enforcement on the Non-Safety Interface
- TC-RQ011-02 - Unauthenticated Configuration-Protocol Factory Reset
- TC-RQ013-01 - Current-Version-Only Confirmation
- TC-RQ014-02 - Cleartext Confidentiality of the Tracing Log 
- TC-RQ014-03 - Access-Control Mechanism Probe


ich habe die Sicherheitstests nach dem Security Testing Framework (CM-001 bis CM-010) in durchgeführt
 
CM-001 - Network Exposure (Nmap): Vollständig durchgeführt (TCP Full-Scan + UDP Top-Ports) und logisches, auswertbares Ergebnis erhalten
 
CM-002 - Netzwerksegmentierung (Nmap): Ich ja kein Conduit-/Zonenmodell, gegen das ein Segmentierungs-Scan sinnvoll verglichen werden könnte....
 
CM-003 - Default/Weak Credentials (Hydra):  Der IoT-Core hat keinen Login (Read-Only-Zugriff ohne Passwortschutz), es gibt also keine Anmeldeoberfläche, gegen die Hydra Zugangsdaten testen könnte
 
CM-004 - RBAC/Privilege Escalation (OWASP ZAP): Technisch durchgeführt (Active Scan + manuelles Durchklicken über ZAP-Proxy), Report gespeichert. Vergleich zweier Rollen auf unzulässige Rechteausweitung ist  nicht anwendbar, da SRIO nur eine einzige, anonyme Read-Only-Rolle hat
 
CM-005 - TLS-Konfiguration (SSLscan):  SRIO kein HTTPS unterstützt --> Port 443 ist nicht offen, wodurch kein TLS-Endpunkt zum Testen existiert
 
CM-006 - Hardening Validation (Lynis): Nicht durchgeführt. Lynis kann ausschließlich Linux-Systeme überprüfen
 
CM-007 - Debug/Service Interface Exposure (Nikto): Durchgeführt gegen den IoT-Core-Webserver, Ergebnis gespeichert.
 
CM-008 - Patch Level/CVEs (OpenVAS/GVM): Hab ich nicht hinbekommen, brauche ich eventuell hilfe
 
CM-009 - Load Behavior & Logging (Siege): Mit 50 Verbindungen (Doku) und mit 3 Verbindungen durchgeführt (Anforderungen)
 
CM-010 - Fuzzing/Robustness (boofuzz): Durchgeführt gegen den HTTP-Port des SRIO. Dabei ist am Gerät ein Fehler mit Code 0x1000 aufgetreten


\begin{table}[htbp]
	\centering
	\renewcommand{\arraystretch}{1.3} % Etwas mehr Platz zwischen den Zeilen
	\small % Schriftgröße leicht reduziert für bessere Passform
	\begin{tabularx}{\textwidth}{@{} c >{\raggedright\arraybackslash}X >{\raggedright\arraybackslash}X >{\raggedright\arraybackslash}X >{\raggedright\arraybackslash}X l @{}}
		\toprule
		\textbf{ID} & \textbf{Asset} & \textbf{Description} & \textbf{Protection objectives} & \textbf{Typical affected resources} \\ 
		\midrule
		
		A & Trusted Safety Function & SRIO correctly executes its specified safety function. & Integrity, Availability & Safe CPU, SysCom, DI/DO, PROFIsafe channel & \\ 
		
		B & Integrity of Safety Configuration & Safe behavior is determined by the intended configuration. & Accountability, Authorization, Integrity, Authenticity & Safe CPU, SysCom, CPU3/COM, PROFINET parameterization & \\ 
		
		C & Integrity and Authenticity of Safety-Relevant Process Data & Input, output and PROFIsafe data correspond to the actual safety state. & Integrity, Authenticity, Availability & Safe CPU, SysCom, CPU3/COM, PROFIsafe channel, DI/DO & \\ 
		
		D & Authenticity and Integrity of Safety Software & Bootloader and firmware remain authentic and unmodified. & Accountability, Authenticity, Integrity & Safe CPU, COM CPU, Shared Flash, IoT interface, update workflow & \\ 
		
		E & Integrity of Safety Monitoring & Self-tests, plausibility checks, diagnostics and fault responses remain trustworthy. & Integrity, Availability & Safe CPU, SysCom, diagnostics, watchdog & \\ 
		
		F & Separation of Safety and Non-Safety Domain & A compromised COM system must not affect the integrity of the safety function. & Confidentiality, Integrity, Availability & Safe CPU, SysCom, COM, IoT, Shared Flash & \\ 
		
		G & Integrity of Operating Mode & Test and update functions must not be activated or used without authorization. & Accountability, Authorization, Integrity, Authenticity, Availability & Rotary switches, IoT service functions, update mode, COM/SCPU control path & \\ 
		
		H & SRIO Functionality & Availability of SRIO functionality shall be ensured. & Availability & Power supply, COM, SCPU, network channels, field I/O & \\ 
		
		I & Integrity, Availability and Confidentiality of Audit/Tracing Data & Evidence of interventions, configuration changes and installed software versions must be generated, retained for the mandated period and access-restricted. & Accountability, Availability, Confidentiality & COM Error Log (circular buffer), IoT-Core /devicestatus/errorlog, /firmware/version, /deviceinfo/*, I\&M data  \\
		\bottomrule
	\end{tabularx}
	\caption{Overview of Assets and Protection Objectives}
	\label{tab:assets}
\end{table}