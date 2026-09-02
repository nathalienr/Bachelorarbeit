# Testumgebung und kategorisierter Testplan – Safe Remote I/O (SRIO, AL400S/AL401S)

Physical IT/OT Interface Testbed – Stand: aktuelle, finale Topologie (ohne Zusatz-Hardware)

---

## 1. Testumgebung – detaillierte Beschreibung

### 1.1 Geräteübersicht

| Gerät | Rolle | IP-Adresse | Subnetzmaske | Switch-Port |
|---|---|---|---|---|
| Managed Switch | Netzwerkverteiler | 192.168.0.91 (Management) | 255.255.255.0 | – |
| SPS (F-Host) | Safety-Master, PROFIsafe-Verbindung | 192.168.0.1 | 255.255.255.0 | Port 1 |
| SRIO (DUT) | Testobjekt | 192.168.0.2 | 255.255.255.0 | Port 2 |
| Kali-Linux-Rechner | Angriffs-/Analyse-Host | 192.168.0.80 | 255.255.255.0 | Port 3 |
| Firmenlaptop | Engineering (TIA Portal) | 192.168.0.7 | 255.255.255.0 | Port 4 |

Alle Geräte im selben Subnetz 192.168.0.0/24, feste IP-Adressen (kein DHCP). Alle vier Geräte hängen als eigenständige Access-Ports am selben Switch (klassische Stern-Topologie, kein Inline-Tap, keine dedizierte Mirror-Verkabelung im Grundzustand).

### 1.2 Topologie

```
                     ┌─────────────────────────┐
                     │   Managed Switch          │
                     │   192.168.0.91 (Mgmt)      │
                     │                            │
                     │  Port1  Port2  Port3  Port4│
                     └───┬──────┬──────┬──────┬───┘
                         │      │      │      │
                ┌────────┘      │      │      └────────┐
                │               │      │               │
          ┌─────┴─────┐   ┌─────┴────┐ │         ┌─────┴─────┐
          │    SPS     │   │  SRIO    │ │         │Firmenlaptop│
          │(F-Host)    │   │  (DUT)   │ │         │(TIA Portal)│
          │192.168.0.1 │   │192.168.0.2│ │         │192.168.0.7 │
          └────────────┘   │M12(D)↔RJ45│ │         └────────────┘
                            └──────────┘ │
                                   ┌──────┴──────┐
                                   │  Kali-Linux  │
                                   │192.168.0.80  │
                                   │(Wireshark u.a.)│
                                   └──────────────┘

SRIO zusätzlich (nicht über Switch):
  - Power In (M12, L-codiert) ← 24V-DC-Netzteil
  - DI-Port (M12, A-codiert)  ← Taster/Sensor
  - DO-Port (M12, A-codiert)  → Last (Lampe/Relais)
```

### 1.3 Switch – zwei Betriebsmodi

Der Switch wird **ohne Umverkabelung**, nur durch Aktivieren/Deaktivieren einer Softwarefunktion, in zwei Modi betrieben. Welcher Modus für welchen Testfall nötig ist, steht in Abschnitt 2 bzw. 3.

#### Modus 1 – „Standard" (Grundzustand, kein Mirroring)

| Port | Gerät | Modus |
|---|---|---|
| 1 | SPS | Access, Standard-VLAN |
| 2 | SRIO | Access, Standard-VLAN |
| 3 | Kali-Linux-Rechner | Access, Standard-VLAN |
| 4 | Firmenlaptop | Access, Standard-VLAN |

Alle Ports in derselben Broadcast-Domain. Der Kali-Rechner an Port 3 sieht in diesem Modus automatisch:
- jeden **Broadcast-/Multicast-Verkehr** (z. B. PROFINET-DCP)
- seinen **eigenen** Unicast-Verkehr (Anfragen, die er selbst an SRIO 192.168.0.2 schickt, inkl. der Antworten)

Er sieht **nicht**: den gezielten Unicast-Verkehr zwischen SPS (Port 1) und SRIO (Port 2) – der wird vom Switch ausschließlich an den jeweiligen Zielport ausgeliefert, nicht dupliziert.

→ Für alle Testfälle, bei denen Kali selbst der Kommunikationspartner ist (Portscans, HTTP-Requests, DCP-Frames, gezielte Unicast-Frames an die SRIO-MAC-Adresse), reicht **Modus 1**.

#### Modus 2 – „Mirroring aktiv"

Zusätzlich zu Modus 1 wird am Switch Port-Mirroring eingerichtet:
- Quell-Ports: Port 1 (SPS) und Port 2 (SRIO), Richtung *both/ingress+egress*
- Ziel-Port: Port 3 (Kali-Linux-Rechner)
- Verifikation: `tcpdump -i eth0` bzw. `tshark -i eth0` auf dem Kali-Rechner

**Einschränkung:** Solange Mirroring aktiv ist, empfängt Kali an Port 3 zusätzlich zum eigenen (aktiven) Verkehr auch den gespiegelten SPS↔SRIO-Verkehr. Das kann bei parallelen aktiven Tests (Nmap, Injection) zu größeren Mitschnitten führen – unkritisch, aber beim Auswerten der PCAPs berücksichtigen (nach Quell-/Ziel-IP filtern).

→ Für alle Testfälle, bei denen der **zyklische PROFINET/PROFIsafe-Verkehr zwischen SPS und SRIO** mitgeschnitten werden muss (z. B. um Qualifier-Zustände, Timing oder Reaktionen auf Injection zu verifizieren), ist **Modus 2** erforderlich.

#### Storm-Control

Vor Flood-Tests (TC-RQ010-01/02) bewusst festlegen und dokumentieren, ob Storm-Control (Broadcast-/Multicast-/Unicast-Sturmschutz) am Switch aktiv ist, da dies das Testergebnis beeinflusst. Das ist keine Testvoraussetzung im engeren Sinn, sondern eine Dokumentationspflicht für die spätere Ergebnisinterpretation.

### 1.4 SPS (F-Host) – Konfiguration

- IP: 192.168.0.1 / 255.255.255.0, kein Gateway nötig (lokales Testnetz)
- TIA Portal: SRIO aus Hardware-Katalog auf die PROFINET-Linie ziehen (GSD-Datei zuvor importieren), passendes DAP wählen (AL400S oder AL401S), CPU-IP auf 192.168.0.1 setzen
- PROFIsafe-Parameter: F_Dest_Add = Wert des Drehschalters an der SRIO (1–899), F_WD_Time (Default 150 ms, Minimum 50 ms), iParameter der DI-/DO-Ports konfigurieren, iPar-CRC über ifm-CRC-Tool erzeugen und in F_iPar_CRC eintragen
- Projekt übersetzen, auf CPU laden, CPU in RUN

### 1.5 SRIO (DUT) – Konfiguration

- IP: 192.168.0.2 / 255.255.255.0, wird beim ersten Verbindungsaufbau per DCP von TIA Portal zugewiesen
- Drehschalter (F-Adresse): 1–899 = F_Dest_Add (muss mit TIA-Portal-Wert übereinstimmen), 000 = Auslieferungszustand, 999 = Firmware-Update-Modus; wird nur beim Boot/Init gelesen
- Verkabelung: Power In (M12, L-codiert) ← 24V-DC-Netzteil; Fieldbus-Port 1 (M12, D-codiert) → Switch Port 2; DI-Port ← Taster/Sensor; DO-Port → Last/Lampe
- Erstinbetriebnahme: Netzteil einschalten, RDY-LED grün prüfen, Verbindungsaufbau über TIA Portal, nach erfolgreicher Parametrierung P-LED statisch grün = sichere Kommunikation aktiv

### 1.6 Firmenlaptop – Konfiguration

- IP: 192.168.0.7 / 255.255.255.0, Windows-Netzwerkprofil auf „Privat" (sonst blockiert die Firewall ggf. DCP/S7comm)
- TIA Portal ≥ V17, TCI ≥ V1.1-MU1; GSD-Datei der SRIO importiert
- ifm-CRC-Tool wird ausschließlich aus TIA Portal heraus gestartet (Rechtsklick auf SRIO-Modul → Device Tool starten)
- I&M-Daten (I&M0, I&M4, I&M5) sind **nur** über TIA Portal auslesbar, nicht über IoT-Core: Online-Verbindung zur CPU → SRIO-Modul → Online & Diagnose → Kennungsdaten (I&M)

### 1.7 Kali-Linux-Rechner – Konfiguration

- IP: 192.168.0.80/24 (statisch, `ip addr add 192.168.0.80/24 dev eth0; ip link set eth0 up`)
- Vorhandene/benötigte Tools: Wireshark (vorhanden), zusätzlich `apt install -y nmap tshark scapy hping3 ettercap-text-only bettercap zaproxy`
- PROFINET/DCP-fähige Scapy-Erweiterung: `python3 -c "from scapy.all import load_contrib; load_contrib('pnio'); load_contrib('pnio_rtc')"`, `pip install pnio-dcp`
- Vor Testbeginn jedes Tool einzeln auf Funktion prüfen

### 1.8 Sicherheitshinweise

- Switch darf keinen Uplink zum Firmennetz haben, sofern aktive/aggressive Tools (bettercap, ettercap, hping3, boofuzz) zum Einsatz kommen
- Vor Firmware-relevanten Tests (auch nur lesenden) einen validierten Original-Firmware-Container sichern (Recovery-Möglichkeit)
- Diese Testumgebung enthält **kein Ersatz-SRIO-Gerät** und **keine transparente Inline-Bridge** am Kali-Rechner. Testfälle, die diese Zusatz-Hardware voraussetzen (z. B. echtes MITM, destruktive Firmware-/Siegel-Tests), sind **bewusst nicht** Teil der folgenden Listen und werden aktuell zurückgestellt.

### 1.9 Checkliste vor Testbeginn

- [ ] Alle Geräte mit korrekter IP erreichbar (ping 192.168.0.1/.2/.7/.80/.91)
- [ ] GSD-Datei in TIA Portal importiert, SRIO-Drehschalter-Adresse = F_Dest_Add in TIA Portal identisch
- [ ] Projekt auf SPS geladen, CPU in RUN, P-LED an SRIO statisch grün
- [ ] Kali-Tools installiert und einzeln getestet
- [ ] Firmware-Backup + Hash des SRIO gesichert
- [ ] Für Abschnitt 3 (Mirroring-Tests): Switch-Mirroring-Konfiguration einmal testweise eingerichtet und mit `tcpdump`/`tshark` verifiziert
- [ ] Storm-Control-Einstellung am Switch dokumentiert (vor TC-RQ010-01/02)

---

## 2. Kategorie A – Direkt durchführbar (Switch im Standard-Modus, kein Mirroring nötig)

**33 Testfälle.** Kali kommuniziert dabei direkt mit der SRIO (Unicast) oder wertet Broadcast-Verkehr aus; kein Mitschnitt des SPS↔SRIO-Verkehrs nötig. Einige Testfälle sind reine Desk-/Dokumentenanalysen ohne Netzwerkinteraktion.

| Test-ID | Requirement | Ziel (kurz) | Tools / Vorgehen |
|---|---|---|---|
| TC-RQ001-02 | RQ-001 | Enumeration erreichbarer Dienste/Ports auf SRIO, Abgleich mit Architektur | Nmap (`-sS -sV -p-` + `-sU --top-ports 200`) gegen 192.168.0.2 |
| TC-RQ002-04 | RQ-002 | Analytisch: Forgeability von F_ParCRC (16-Bit)/iParCRC (32-Bit) | Schreibtischanalyse, kein DUT-Zugriff |
| TC-RQ003-01 | RQ-003 | Baseline: welche Interventions-Evidenz existiert (ErrorLog, I&M0, I&M4) | curl (IoT-Core Errorlog) + TIA (I&M) |
| TC-RQ003-02 | RQ-003 | Autorisierter Parameter-/Adresswechsel + Reboot, Evidenz danach prüfen | curl + TIA |
| TC-RQ003-04 | RQ-003 | Zeitbezug: Uptime (systick) resettet bei Kaltstart, kein absoluter Zeitstempel | curl `/systemtime/systick` |
| TC-RQ003-05 | RQ-003 | FIT-Interface (`/fit/setfit`) wird auf Produktionsgerät abgelehnt | curl POST gegen `/fit/setfit` |
| TC-RQ004-01 | RQ-004 | Vollständigkeit der Identifikationsdaten (SW-Versionen + I&M) | curl gegen mehrere `/deviceinfo/*`-Endpunkte + TIA |
| TC-RQ004-02 | RQ-004 | SBOM-Lücke: Drittkomponenten (µC/OS-II, PROFIsafe-Stack etc.) nicht einzeln versioniert | Desk-Analyse auf Basis TC-RQ004-01 + Doku |
| TC-RQ004-04 | RQ-004 | Eindeutigkeit der Konfigurationssignatur I&M4 bei zwei unterschiedlichen Configs | TIA, zwei Konfigurationen laden und I&M4 vergleichen |
| TC-RQ005-04 | RQ-005 | Statische Analyse des Firmware-Update-Containers auf Signatur-/Boot-Chain-Artefakte | `binwalk`, `strings`, Entropie-Analyse – offline, kein DUT nötig |
| TC-RQ005-05 | RQ-005 | Analytisch: Safety-Selbsttests (1oo2/STL) ≠ Security-Authentizität | Reine Argumentation, keine Hardware |
| TC-RQ006-01 | RQ-006 | Vollständige Inventarisierung installierter Software (Host-FW, Bootloader, SCPU-FW, Stack) | curl gegen `/deviceinfo/swinfo/*`, `/firmware/version` + TIA |
| TC-RQ006-02 | RQ-006 | = TC-RQ004-02 (SBOM-Lücke), unter RQ-006 referenziert | Desk-Analyse |
| TC-RQ007-01 | RQ-007 | Baseline: Identifikationsdaten im Normalbetrieb browserbasiert abrufbar | Laptop-Browser (IoT-Core Visualizer) + curl |
| TC-RQ007-03 | RQ-007 | Connection-Hold Self-DoS: 2 gehaltene HTTP-Verbindungen blockieren weitere Reads | `nc`/Python Slow-Read-Holder + curl von Kali |
| TC-RQ008-01 | RQ-008 | Baseline: welche Software-Interventions-Evidenz existiert | curl (Errorlog) + TIA |
| TC-RQ008-05 | RQ-008 | = TC-RQ003-05 (FIT-Interface auf Produktionsgerät), unter RQ-008 referenziert | curl POST `/fit/setfit` |
| TC-RQ009-01 | RQ-009 | Baseline: Config-Änderungs-Evidenz (REVISION_COUNTER, I&M4, ErrorLog) | TIA + curl |
| TC-RQ009-02 | RQ-009 | Persistenz REVISION_COUNTER vs. Log-Löschung über Kaltstart hinweg | TIA + curl, Config ändern, Kaltstart, erneut lesen |
| TC-RQ009-03 | RQ-009 | Akteurs-Zuordnung liegt nur bei TIA/PLC, nicht am Gerät selbst | TIA-Projekt-Nutzer einsehen + Gerätefelder prüfen |
| TC-RQ009-05 | RQ-009 | Analytisch: 16-Bit-Zähler-Wrap-Around über 20 Jahre Missionszeit | Schreibtischanalyse (SRIO-706) |
| TC-RQ010-03 | RQ-010 | Protokoll-Fuzzing HTTP/IoT-Core (+ DCP-Fuzzing als Broadcast) | boofuzz gegen 192.168.0.2:80, Scapy pnio-dcp |
| TC-RQ010-04 | RQ-010 | Applikationsebenen-Flood gegen IoT-Core, Domänentrennung zur Safety-Seite prüfen | Siege/`ab` gegen `/deviceinfo`, parallel DO-Readback via TIA |
| TC-RQ011-01 | RQ-011 | Read-Only-Durchsetzung: Schreibversuche über IoT-Core müssen scheitern | curl POST/PUT gegen `/devicecontrol/...`, `/fieldbussetup/...` |
| TC-RQ012-01 | RQ-012 | Ringpuffer-Überlauf: >100 Log-Einträge erzwingen, älteste werden überschrieben | curl, wiederholte Events erzeugen (z. B. Passivierungen) |
| TC-RQ012-02 | RQ-012 | Log-Löschung bei Kaltstart nachweisen | curl vor/nach Power-Cycle |
| TC-RQ012-03 | RQ-012 | Analytisch: Pflicht-Reboot ≤1 Jahr macht 5-Jahres-Retention strukturell unmöglich | Desk-Analyse (SRIO-1812 + TC-RQ012-02-Ergebnis) |
| TC-RQ012-04 | RQ-012 | = TC-RQ003-04 (Zeitbezug), unter RQ-012 referenziert | curl `/systemtime/systick` |
| TC-RQ013-01 | RQ-013 | Nur aktuelle Firmware-Version wird angezeigt, keine Historie | curl `/firmware/version`, `/deviceinfo/swrevision` + TIA I&M |
| TC-RQ013-04 | RQ-013 | Externe Release Notes als Ersatznachweis prüfen (Kriterien: geräteresident? pro Seriennummer? fälschungssicher?) | Desk-Analyse der ifm-Release-Notes |
| TC-RQ014-01 | RQ-014 | Unauthentisiertes Auslesen des ErrorLogs von beliebigem Netzknoten | curl `/devicestatus/errorlog/loglist` ohne Credentials |
| TC-RQ014-03 | RQ-014 | Kein Auth-/Rollenmodell am Log-Endpunkt auffindbar | OWASP ZAP-Enumeration + curl |
| TC-RQ014-04 | RQ-014 | Keine kontrollierte Löschfunktion für das Log auffindbar | curl `DELETE` gegen Errorlog-Pfad, Response-Code prüfen |

---

## 3. Kategorie B – Durchführbar, aber Switch-Mirroring muss aktiviert werden

**12 Testfälle.** Für diese Fälle muss der Switch von Modus 1 in **Modus 2 (Mirroring aktiv, Abschnitt 1.3)** umgeschaltet werden, weil der zyklische SPS↔SRIO-Verkehr (Port 1 ↔ Port 2) mitgeschnitten werden muss, den Kali im Standardmodus nicht sieht.

| Test-ID | Requirement | Ziel (kurz) | Tools / Vorgehen |
|---|---|---|---|
| TC-RQ001-01 | RQ-001 | Baseline PROFIsafe-Austausch: Qualifier bleibt „good", Output folgt Steuerbyte | tshark-Mitschnitt (`ether proto 0x8892`) + TIA-Watchtable, DI/DO manuell togglen |
| TC-RQ001-03 | RQ-001 | Mis-addressed/CRC-Mismatch-Frame parallel einspielen, Ablehnung nachweisen | Scapy (pnio/pnio_rtc) von Kali senden, parallel Mitschnitt zur Auswertung |
| TC-RQ001-05 | RQ-001 | Kanalunterbrechung > F_WD_Time: Passivierung + Zeitmessung bis Safe State | tshark-Mitschnitt mit Zeitstempeln, Patchkabel Port 1 oder Port 2 manuell ziehen |
| TC-RQ002-01 | RQ-002 | Konfiguration mit falschem iParCRC/F_ParCRC wird abgelehnt (bleibt in Parametrierung) | TIA (falschen CRC eintragen) + tshark-Mitschnitt des Verbindungsaufbaus |
| TC-RQ004-03 | RQ-004 | Klartext-Übertragung der Identifikationsdaten (kein TLS) nachweisen | tshark HTTP-Mitschnitt + `sslscan` gegen Port 80 |
| TC-RQ005-01 | RQ-005 | = TC-RQ002-01 (Parameter-Integritäts-Ablehnung), unter RQ-005 referenziert | wie TC-RQ002-01 |
| TC-RQ006-03 | RQ-006 | Klartext-Übertragung des Software-Inventars (Defense-in-Depth-Beobachtung) | tshark HTTP-Mitschnitt + `sslscan` |
| TC-RQ009-04 | RQ-009 | Schreibzugriff nach Param-End wird blockiert, keine Log-Spur beim Blockieren | Scapy PROFINET-acyclic-write während OPERATE + Mitschnitt zur Verifikation |
| TC-RQ010-01 | RQ-010 | Baseline-Stabilität unter Nennlast (PROFINET Net Load Class III) | Traffic-Generator (hping3, konformitätskonforme Rate) + Mitschnitt, Storm-Control vorher dokumentieren |
| TC-RQ010-02 | RQ-010 | Netzwerk-/L2-Flood: Verhalten bis Passivierung, ggf. Mitschnittverluste bei hoher Rate vermerken | hping3-Flood + Scapy-Broadcast-Storm, Mitschnitt (kann bei Flood unvollständig sein – als bekannte Einschränkung dokumentieren) |
| TC-RQ011-02 | RQ-011 | Unauthentisierter DCP-Reset (Mode 2) von einem Peer-Knoten aus | `pnio-dcp`-Skript von Kali + Mitschnitt zur Bestätigung |
| TC-RQ014-02 | RQ-014 | Klartext-Übertragung des Tracing-Logs (kein TLS) nachweisen | tshark HTTP-Mitschnitt + `sslscan` |

**Mirroring-Konfiguration für diese 12 Testfälle** (einmalig einrichten, danach für alle Tests dieser Kategorie aktiv lassen):
```
Switch-Menü → Port Mirroring
Quell-Ports: Port 1 (SPS) + Port 2 (SRIO), Richtung: both / ingress+egress
Ziel-Port:   Port 3 (Kali-Linux-Rechner)
Verifikation: sudo tcpdump -i eth0   (bzw. tshark -i eth0)
```

---

## 4. Zusammenfassung

| Kategorie | Anzahl | Switch-Konfiguration |
|---|---|---|
| A – direkt durchführbar | 33 | Modus 1 (Standard, kein Mirroring) |
| B – durchführbar mit Konfigänderung | 12 | Modus 2 (Mirroring Port1+2 → Port3) |
| **Summe aktuell geplant** | **45** | – |
| Zurückgestellt (Zusatz-Hardware nötig) | 18 | siehe vorheriges Analyse-Dokument |

Die Zuordnung basiert auf den in WORKFLOW.docx angegebenen „HW/Network"-Feldern der Concrete-Execution-Ebene jedes Testfalls: Wird dort „Setup A" bzw. „mirror" explizit genannt, ist Mitschnitt des SPS↔SRIO-Verkehrs erforderlich → Kategorie B. Andernfalls kommuniziert Kali direkt mit der SRIO oder es handelt sich um eine reine Dokumenten-/Desk-Analyse → Kategorie A.

**Hinweis zu IP-Adressen:** In den Concrete-Execution-Feldern von WORKFLOW.docx sind teils Platzhalter-IPs aus einer generischen Vorlage enthalten (`172.18.87.2` statt `192.168.0.2`, Interface `eth0` ggf. abweichend). Vor Ausführung jedes Befehls die IP-Adresse auf `192.168.0.2` (SRIO) bzw. das tatsächliche Kali-Interface anpassen.
