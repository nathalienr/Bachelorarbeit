### 1\. Die Asset-Mapping Tabelle



|MVO-ID|IEC 62443-4-2 CR|Target Asset|Threat (STRIDE)|Security Function (Mitigation)|Test Tool (Kali / Manuell)|
|-|-|-|-|-|-|
|**RQ-001**|CR 3.1 (Kommunikationsintegrität)|**F** (COM/IoT Interface), **H** (Network Channels)|Spoofing / Tampering|**\[K]** Protokoll-Validierung durch PROFINET/PROFIsafe-Stack.<br>**\[A]** Netzwerkisolation ist keine Komponentenfähigkeit, sondern dokumentierte Umgebungsannahme ("safe zone behind a firewall")|`Nmap` (Discovery), `Scapy` (Fuzzing) — Netzwerkisolation nur via Dokumenten-/Topologie-Audit prüfbar|
|**RQ-002**|CR 3.1, EDR 3.11 (Physikalische Manipulationssicherheit)|**C** (PROFINET Data), **G** (Rotary Switches)|Tampering|**\[K]** PROFIsafe Black-Channel-Prinzip + 4-Byte-CRC (F\_iParCRC, F\_ParCRC).<br>**\[K]** Physische Manipulationssicherheit der Rotary Switches durch Kunststoff-/Metallsiegel|`Scapy` (CRC-Verletzung provozieren), manueller Hardware-Trigger (Siegel-Manipulation)|
|**RQ-003**|CR 2.8 (Prüfbare Ereignisse), EDR 3.11|**G** (Rotary Switches)|Repudiation|**\[P] Lücke:** Nur visuelle Manipulationserkennung dokumentiert; kein automatisiertes Hardware-Event-Logging für Zugriffe auf die Rotary Switches belegt (EDR 3.11 RE(1) scheint nicht implementiert)|Manuelle Siegel-Manipulation + visuelle Inspektionsprüfung (Log-Analyse nicht anwendbar)|
|**RQ-004**|CR 7.8 (Verzeichnis der Komponenten)|**B** (Config), **D** (Safety Firmware)|Tampering / Info Disclosure|**\[K]** Version-Identification-API via IoT-Core (`/deviceinfo/hwversion`, `/deviceinfo/swrevision`, `/deviceinfo/swinfo/scpuversion`).<br>Caveat: Übertragung nur via HTTP (kein HTTPS)|`curl`, `OWASP ZAP`|
|**RQ-005**|CR 3.4 (Softwareintegrität), EDR 3.14|**B** (Config), **D** (Update Workflow)|Tampering|**\[K] Korrigiert:**  Belegt ist ein CRC-basierter Kompatibilitäts-/Konsistenzcheck der Update Container (Safe Container Verifikation durch SCPU)|`curl` (Upload manipulierter Firmware/CRC) — PASS-Kriterium: Ablehnung bei CRC-Mismatch|
|**RQ-006**|CR 7.8 (Verzeichnis der Komponenten)|**D** (Safety Firmware)|Tampering|**\[K]** Software Inventory Readout via `/deviceinfo/swinfo/cpubootloaderversion`, `/scpuversion`, `/scpubootloaderversion`|`curl`, `OWASP ZAP`|
|**RQ-007**|CR 7.8 (Verzeichnis der Komponenten)|**D** (IoT Interface / Firmware)|Denial of Service|**\[K]** API-Verfügbarkeit begrenzt durch dokumentiertes Verbindungslimit (max. 2 aktive HTTP-Connections)|`hping3` (Lasttest gezielt gegen das 2-Connection-Limit)|
|**RQ-008**|CR 2.8, CR 2.12 (Nichtabstreitbarkeit)|**B** (Config), **G** (Operating Mode)|Repudiation|**\[K]** Intervention Audit Logging via ErrorEvent-Struktur (Channel, ErrorClass, ErrorCode, Timestamp), Übertragung SCPU→COM via SysCom|`OWASP ZAP` (Event triggern) + Log-Analyse via `/devicestatus/errorlog/loglist`|
|**RQ-009**|CR 2.8, CR 3.4 (Informationsintegrität)|**B** (Config), **D** (Firmware)|Repudiation|**\[K]** Modification Audit Logging + I\&M1 "REVISION\_COUNTER" (inkrementiert bei jeder Parameteränderung)|`curl` (Update triggern) + Log-/Revision-Counter-Analyse|
|**RQ-010**|CR 7.1 (Schutz vor DoS-Ereignissen)|**A** (Trusted Safety Function), **E** (Safety Monitoring), **H** (Network)|**Denial of Service**|**\[K]** Externer Hardware-Watchdog (SCPU-seitig, unabhängig von den µCs) + HTTP-Verbindungslimit (COM/IoT-Core, max. 2)|`hping3`, `Slowloris` (insb. gegen Connection-Limit)|
|**RQ-011**|CR 2.1 (Durchsetzung der Autorisierung)|**B** (Safety Config), **G** (Mode)|**Elevation of Privilege**|**\[A] Kritisch korrigiert:** Kein Software-RBAC implementiert (Passwortschutz explizit gestrichen, IoT-Core read-only). Tatsächlicher Schutz ist rein physisch: Rotary-Switch-Stellung "999" + Power-Cycle für FW-Update-Modus|~~`Hydra` (nicht anwendbar — keine Login-Schnittstelle)~~ → manueller Schreibversuch ohne korrekte Rotary-Switch-Stellung, `OWASP ZAP` (Read-Only-Enforcement)|
|**RQ-012**|CR 2.8, CR 2.9 (Speicherkapazität)|**B**, **D**, **G** (Shared Flash Logs)|Tampering|**\[K]** Non-volatile Log Storage: Circular Buffer, mind. 100 ErrorEvents, EEPROM-/Flash-basiert|Log-Analyse (Prüfung von Zeitstempeln, Buffer-Wraparound)|
|**RQ-013**|CR 2.8, CR 2.9 (Speicherkapazität)|**D** (Update Workflow Logs)|Repudiation|**\[K]** Firmware Update Logging via I\&M1 Revision Counter + `swrevision`/`scpuversion`-Elemente|Log-Analyse (Versionshistorie, Revision-Counter)|
|**RQ-014**|CR 2.1, CR 4.1 (Vertraulichkeit von Informationen)|**F** (Shared Flash / IoT Interface)|**Information Disclosure**|**\[A] Kritisch korrigiert:** Kein komponentenseitiger Zugriffsschutz implementiert (IoT-Core ohne Authentifizierung, ohne HTTPS). Schutz basiert ausschließlich auf derselben Ausgleichsmaßnahme wie RQ-001|`curl`/`OWASP ZAP` (Unauth GET Request) — erwartetes Ergebnis: Zugriff erfolgreich (akzeptiertes Restrisiko, kein Testfehler)|



**K**omponentenfähigkeit, eine **A**usgleichsmaßnahme (Ausschluss von der Komponententestbarkeit) oder eine **P**rozess-/Dokumentationsmaßnahme ist



REQ-04: Deshalb bleibt „Version Identification API" die korrekte Bezeichnung der Mitigation, aber dein Testfall mit curl/OWASP ZAP sollte gezielt prüfen, ob die Daten unauthentifiziert abrufbar sind – das ist dann der eigentliche Prüfpunkt für den Information-Disclosure-Teil.



\---

### 2\. Test Case Data Sheets

Hier sind zwei detaillierte Testfälle (Datenblätter), die genau deiner Methodik aus Kapitel 3.2.3 entsprechen. Du kannst diese Struktur direkt in dein LaTeX-Dokument für Kapitel 4.2 übernehmen.

#### Test Case 1: Schutz gegen unautorisierte Konfigurationsänderung (RBAC)

Dieser Test prüft, ob jemand ohne Admin-Rechte die Sicherheitskonfiguration (Asset B) über das IoT/COM-Interface (Asset F) ändern kann.

* **Test ID:** TC-01-ConfigTampering
* **Test Objective:** Verify that unauthorized users cannot modify safety-relevant settings (Asset B) via the network interface.
* **Normative Reference:** RQ-011 / IEC 62443-4-2 CR 2.1 (Authorization Enforcement)
* **Target Asset:** Asset B (Integrity of Safety Configuration) \& Asset F (IoT Interface)
* **Threat Modeled:** Elevation of Privilege / Tampering (STRIDE)
* **Preconditions:**
* SUT (Gateway) is powered on and connected to the isolated test switch.
* Attacker machine (Kali) has network access to the SUT's IoT/Web interface.
* No valid administrator session is active.



* **Execution Procedure:**
1. Start Interception Proxy (`OWASP ZAP`) on the attacker machine.
2. Capture a legitimate HTTP POST request that modifies a safety parameter (e.g., changing a sensor threshold).
3. Drop the valid session token (Cookie/Bearer Token) from the request header.
4. Replay the modified, unauthenticated POST request to the SUT API endpoint.
5. Attempt a secondary attack using `Hydra` to brute-force the default admin credentials on the login endpoint.



* **Acceptance Criterion (PASS):**
* The SUT strictly rejects the unauthenticated POST request with an `HTTP 401 Unauthorized` or `HTTP 403 Forbidden` error.
* The safety configuration (Asset B) remains unmodified.
* The brute-force attempt is mitigated (e.g., via account lockout or rate limiting).



\---

#### Test Case 2: Resilienz gegen Netzwerk-Überlastung (DoS)

Dieser Test prüft, ob das Gateway (Asset H) bei einem massiven Angriff aus dem IT-Netz abstürzt oder ob die sicherheitskritische M2M-Kommunikation weiterläuft.

* **Test ID:** TC-02-NetworkResilience
* **Test Objective:** Verify that the gateway maintains core safety functionality and does not enter a hazardous state during a network flood attack.
* **Normative Reference:** RQ-010 / IEC 62443-4-2 CR 7.1 (Protection against DoS)
* **Target Asset:** Asset H (SRIO Functionality / Network Channels)
* **Threat Modeled:** Denial of Service (STRIDE)
* **Preconditions:**
* SUT is operating normally, routing process data between the simulated PLC and field I/O.
* A continuous network baseline is established (e.g., stable `ping` or Modbus TCP polling from the PLC simulator).



* **Execution Procedure:**
1. Launch `Wireshark` to monitor and record the baseline M2M traffic (PCAP evidence).
2. Execute `hping3` from the Kali machine to initiate a TCP SYN flood against the SUT's open ports (e.g., `sudo hping3 -S -p 443 --flood <SUT-IP>`).
3. Maintain the flood for 60 seconds.
4. Observe the M2M traffic (PLC to Field I/O) and the SUT's diagnostic LEDs (Asset E).



* **Acceptance Criterion (PASS):**
* The SUT does not crash or reboot during the attack.
* The physical safety function (Asset A) and process data routing (Asset C) remain available and deterministic.
* The SUT successfully drops the malicious packets (e.g., via rate limiting) without entering a hazardous state.



\---



1. **Nimm die Excel-Tabelle:** Kopiere sie dir als Arbeitsgrundlage. Das ist dein Kompass für die nächsten zwei Wochen. Wenn du jeden dieser 14 Tests einmal durchgespielt hast, hast du deine MVO-Compliance bewiesen.
2. **Schreibe die Datenblätter:** Kopiere die Struktur von TC-01 und TC-02 für 1-2 weitere Tests (z.B. für RQ-001 Nmap Port-Scanning oder RQ-005 Firmware-Signatur). Dann hast du dein Kapitel 4.2 fast fertig geschrieben, *bevor* du überhaupt ein Kabel angesteckt hast. Das ist reinstes wissenschaftliches Arbeiten (Design Science Research)!
3. **Ab 13:00 Uhr:** Geh ans Gerät, steck den Switch an und lass `Nmap` und `Wireshark` laufen.





IEC 62443-4-2 (Das "WAS"):

Rolle: Liefert dir das Ziel.

Warum nutzen: Sie sagt dir, dass du rollenbasierte Zugriffskontrolle (CR 2.1) oder Schutz vor DoS (CR 7.1) brauchst.

Grenze: Die Norm ist abstrakt. Sie sagt dir nicht, wie du das praktisch testen sollst (keine Tools, keine Kommandozeilen). Dafür brauchst du die anderen beiden.

NIST SP 800-115 (Das "WIE" für das Netzwerk):

Rolle: Liefert die Methodik für Netzwerk- und Infrastrukturtests.

Warum nutzen: Hier holst du dir die konkreten Testschritte für das Asset "Netzwerkschnittstellen/Profinet". Die NIST beschreibt genau die Phasen Discovery (Port-Scans mit Nmap) und Attack (z. B. Passwort-Cracking mit Hydra).

OWASP Web Security Testing Guide - WSTG (Das "WIE" für Web \& APIs):

Rolle: Der Goldstandard für das Testen von Applikationen.

Warum nutzen: Moderne Gateways (IoT-Interfaces) werden meist über Web-APIs oder Weboberflächen konfiguriert. Wenn du in deinem Testfall TC-01 prüfst, ob jemand ohne Login Parameter ändern kann, referenzierst du direkt auf OWASP-Kategorien (z. B. WSTG-ATHN-02: Testing for Default Credentials oder WSTG-ATHZ-02: Testing for Bypassing Authorization).

2. Welche anderen Quellen du unbedingt ergänzen solltest
Da du ein Industrie-Gateway (OT) und keinen normalen Büro-Router testest, solltest du akademisch zeigen, dass du die Besonderheiten von industriellen Anlagen verstehst. Ergänze diese beiden Quellen, um deine Methodik unantastbar zu machen:

MITRE ATT\&CK for ICS (Industrial Control Systems):

Was es ist: Eine weltweit anerkannte Wissensdatenbank für reale Angriffsvektoren auf Industrieanlagen.

Wie du es nutzt: Wenn du in deinem Datenblatt den "Threat" beschreibst, nimmst du nicht nur STRIDE, sondern nennst eine MITRE ICS-Technik. Zum Beispiel: Wenn du testest, ob jemand die Sicherheitskonfiguration ändert, ist das die MITRE-Technik T836 (Modify Parameter). Das wirkt extrem professionell.

BSI ICS-Security-Kompendium \& NIST SP 800-82 Rev. 3:

Was es ist: Die Standardwerke für OT-Security vom deutschen BSI und der US-Regierung.

Wie du es nutzt: Du ziehst dir daraus die Verhaltensregeln für das Testen. Dort steht zum Beispiel explizit, dass man SPSen und Gateways nicht blindlings mit wilden Fuzzing-Attacken bewerfen darf, weil sie sonst unwiderruflich abstürzen (Stichwort: "Fragility of OT devices"). Daraus leitest du deine Regel ab, dass du erst eine Baseline (Normalzustand) aufzeichnest, bevor du angreifst.

Wie das im Test Case Data Sheet aussieht

