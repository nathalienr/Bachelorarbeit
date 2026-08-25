# Testumgebung: Security-Funktionsprüfung Safe Remote I/O (SRIO)

**Testobjekt (DUT):** ifm AL400S / AL401S — PROFINET/PROFIsafe F-Device, 6×2 F-DI + 2×2 F-DO
**Zweck:** Systematische, empirische Verifikation der Security-Funktionen am physischen IT/OT-Interface im Rahmen der Maschinenverordnung (EU) 2023/1230.

---

## 1. Grundprinzip

Ein **einziges physisches Testbed** mit **einem** dauerhaft verkabelten DUT, das über die **Switch-Konfiguration** in zwei logische Betriebsmodi versetzt wird:

- **VLAN A — Isoliert:** Nur der Angreifer-/Test-PC ist mit dem SRIO im Segment. Für geräte-lokale Tests (HTTP/IoT-Core, physischer Zugriff, Debug-Interface).
- **VLAN B — Voll:** F-Host, Engineering-PC, Angreifer-PC und Sniffer-PC teilen sich das Segment mit dem SRIO. Für netzwerk-/protokollabhängige Tests mit **aktivem PROFIsafe-Zyklus**.

**Drei feste Konstruktionsregeln, die durchgehend gelten:**

1. **Ein DUT, ein Kabel, durchgehende Stromversorgung.** Der Moduswechsel erfolgt ausschließlich per VLAN-Toggle am Switch — das SRIO wird nie umgesteckt und nie stromlos. Damit bleibt der **Cold-Start ein bewusst gesetzter, letzter Testschritt** und kein Nebeneffekt des Umbaus.
2. **Strikte Rollentrennung.** Angreifer ≠ Engineering ≠ Beobachter. Jede Rolle läuft auf eigener Hardware, damit jeder Nachweis eindeutig einer Quelle zugeordnet werden kann.
3. **Passiver, unabhängiger Beobachter.** Der Sniffer hängt ausschließlich am Mirror-Port/TAP und sendet nie — er liefert manipulationssicheres Beweismaterial (Drei-Quellen-Nachweis: Prozesszustand ↔ Netzwerk-Frame ↔ Geräte-Log).

Das gesamte Labor ist physisch vollständig vom Firmennetz und vom Internet getrennt (kein Routing, kein externes DHCP) und bildet damit die Herstellerannahme „safe zone behind a firewall" **kontrolliert nach**.

---

## 2. Architektur (Visualisierung)

```
                        ISOLIERTES TESTLABOR  (kein Routing, kein Firmennetz, kein Internet)
 ┌───────────────────────────────────────────────────────────────────────────────────────────  ┐
 │                                                                                             │
 │                           ┌──────────────────────────────────┐                              │
 │                           │        MANAGED SWITCH            │                              │
 │                           │  VLAN A / VLAN B   +  SPAN-Port  │                              │
 │                           │  Protected Ports  (+ opt. TAP)   │                              │
 │                           └───┬───────┬───────┬───────┬──────┘                              │
 │                               │       │       │       │                                     │
 │        ┌──────────────────────┘       │       │       └───────────────────────┐             │
 │        │                              │       │                               │             │
 │  ┌─────▼──────┐              ┌─────────▼──┐  ┌─▼──────────────┐        ┌────────▼────────┐  │
 │  │  F-HOST    │              │    SRIO    │  │ ENGINEERING-PC │        │  ANGREIFER-PC   │  │
 │  │  S7-15xxF  │◄──PROFIsafe──┤ AL400S/    │  │  (Windows)     │        │  (Kali,         │  │
 │  │  /S7-12xxF │   (VLAN B)   │ AL401S     │  │  TIA V18 +     │        │   bare-metal,   │  │
 │  │  TIA V18   │              │  = DUT     │  │  ifm-CRC-Tool  │        │   Intel-NIC)    │  │
 │  └────────────┘              └─────┬──────┘  │  reine Konfig  │        │                 │  │
 │                                    │         └────────────────┘        └───────┬─────────┘  │
 │            Rotary/DIL-Switch  &    │  (permanentes Kabel,                      │            │
 │            Debug-Interface frei ◄──┤   durchgehend Strom)                      │            │
 │            zugänglich              │                                           │            │
 │                                    │  ┌──────────────── SPAN / TAP ────────────┘            │
 │                                    │  │  (nur Kopie, keine Injektion)                       │
 │                              ┌─────▼──▼──────┐                                              │
 │                              │  SNIFFER-PC   │   rein passiv                                │
 │                              │  Wireshark +  │   (darf Raspberry Pi 4                       │
 │                              │  tshark       │    + tshark sein)                            │
 │                              └───────────────┘                                              │
 │                                                                                             │
 │  PHYSISCHES ZUSATZ-KIT (VLAN-unabhängig, direkt am DUT):                                    │
 │  • schaltbare Steckdosenleiste (gezielter Cold-Start)                                       │
 │  • JTAGulator + Logic Analyzer (sigrok/PulseView)  • Siegel-/Tamper-Werkzeug                │
 │                                                                                             │
 └───────────────────────────────────────────────────────────────────────────────────────────  ┘
                                         │
                                         ▼
                 ┌──────────────────────────────────────────────────  ┐
                 │   GEMEINSAME DOKUMENTATIONS- & AUSWERTUNGSSCHICHT  │
                 │  • PCAP-Archiv (VLAN A + B, zeitgestempelt)        │
                 │  • Geräte-Logs: Error Log, I&M0, REVISION_COUNTER  │
                 │  • Testprotokoll je RQ (Normalbetrieb vs. Testfall)│
                 │  • Foto-/Video-Doku physischer Tests               │
                 │  • FW-/HW-Revisionsstand (einmalig fixiert)        │
                 └──────────────────────────────────────────────────  ┘
```

**Modus-Umschaltung (Zoom):**

```
  VLAN A (Isoliert)                         VLAN B (Voll)
  ┌───────────────┐                         ┌─────────────────────────────────────┐
  │ SRIO ── Kali  │   ── Switch-Toggle ──►  │ SRIO ── F-Host ── Engineering        │
  │  (allein)     │   (Sekunden, kein       │   └── Angreifer ── Sniffer(passiv)   │
  └───────────────┘    Cold-Start)          └─────────────────────────────────────┘
```

---

## 3. Komponenten im Detail

### 3.1 Kern-Hardware (dauerhaft, VLAN-unabhängig)

| Komponente | Ausprägung | Zweck |
|---|---|---|
| **Managed Switch** | VLAN-fähig, Port-Mirroring (SPAN), Protected Ports (z. B. Industrie-Switch) | Logische Segmentierung (VLAN A/B) + passives Traffic-Mirroring ohne Eingriff in den Live-Datenpfad |
| **Passiver Netzwerk-TAP** *(optional, empfohlen)* | inline zwischen F-Host und SRIO | Jitterfreie Zeitmessung für Zykluszeit-/DoS-Tests (präziser als SPAN) |
| **SRIO (DUT)** | AL400S / AL401S | Testobjekt; permanent an einem Switch-Port, ein Kabel für die gesamte Kampagne |
| **Schaltbare Steckdosenleiste** | fernsteuerbar/manuell schaltbar | Gezielter, sauberer Cold-Start ohne andere Verbindungen zu berühren |

### 3.2 PCs / Rollen

| Rolle | Hardware/OS | Werkzeuge | Zweck |
|---|---|---|---|
| **Angreifer-PC** | **Kali, bare-metal, Intel-NIC (i210/i350)** | Scapy (`scapy.contrib.pnio_dcp`), boofuzz, Nmap, curl, OWASP ZAP, Nikto, pnio_dcp/profi-dcp | Einzige Angreifer-Instanz; aktiv in **beiden** VLAN-Modi. Bare-metal wegen timing-sensitiver L2-Frames (EtherType 0x8892, DCP, PROFIsafe-CRC/Watchdog) |
| **Sniffer-PC** | beliebiges OS (Laptop **oder Raspberry Pi 4**) | Wireshark (PROFIsafe-Dissector), tshark | Rein passiver, unabhängiger Beobachter am SPAN/TAP; erzeugt manipulationssicheres Beweismaterial |
| **Engineering-PC** | **Windows** | TIA Portal V18, ifm-CRC-Tool | Ausschließlich Konfigurationsrolle (F-Parameter, iParCRC). Keine Angreiferfunktion → saubere Rollentrennung |
| **F-Host / Safety-SPS** | S7-1500F (z. B. 1511F-1PN) oder S7-1200F, TIA V18 | — | PROFIsafe-Master; erzeugt realen zyklischen Verkehr für protokollabhängige Tests |

### 3.3 Physisches Zusatz-Kit (direkt am DUT)

| Komponente | Ausprägung | Zweck |
|---|---|---|
| **Debug-Ausrüstung** | JTAGulator + Logic Analyzer (sigrok/PulseView) | Untersuchung des (nach Produktion gefusten) Debug-/Testinterfaces |
| **Siegel-/Tamper-Kit** | Nachbau-/Ablöse-/Bohrwerkzeug, Wärmequelle | Physische Manipulationstests an Gehäuse und Schaltersiegel |
| **Zugriff Rotary/DIL-Switch** | frei zugänglich montiert | F-Adress-/Mode-Änderung, physischer Bypass-Test |

---

## 4. Betriebsmodi

### VLAN A — Isoliert (geräte-lokale Tests)

- Im Segment sichtbar: **nur SRIO + Angreifer-PC**.
- IP-Vergabe an das SRIO per DCP (`pnio_dcp`/`profi-dcp`), da ohne DCP-Tool keine IP gesetzt ist.
- Abgedeckte Interfaces: **HTTP/IoT-Core** (Web/API), **Physical/Debug** (Schalter, Gehäuse, gefustes Interface).

### VLAN B — Voll (netzwerk-/protokollabhängige Tests)

- Im Segment sichtbar: **SRIO + F-Host + Engineering-PC + Angreifer-PC + Sniffer-PC**.
- F-Host hält den **zyklischen PROFIsafe-Verkehr** aktiv (Voraussetzung für CRC-, Watchdog- und Reparametrierungstests).
- Angreifer-PC mit **eigener MAC/IP** im selben VLAN; Sniffer-PC ausschließlich am Mirror-Port/TAP.

**Umschaltung:** Config-Toggle am Switch (Sekunden). Kabel und Stromversorgung des SRIO bleiben unberührt → **kein Cold-Start**. Jede Switch-Konfiguration wird als **Config-Snapshot** gesichert, um jeden Testlauf eindeutig einem Modus zuzuordnen.

---

## 5. Test-Interface-Kategorien

| Kategorie | Betriebsmodus | Beispiele |
|---|---|---|
| **Geräte-lokal — Web/API** | VLAN A | IoT-Core-Endpunkte (`/deviceinfo/*`, `/devicestatus/errorlog`), Klartext-HTTP, Verbindungslimit |
| **Geräte-lokal — Physical/Debug** | VLAN A | Rotary/DIL-Switch, Gehäuse-/Siegelprüfung, gefustes Debug-Interface |
| **Netzwerk-/Protokoll-abhängig** | VLAN B | PROFIsafe-CRC/iParCRC, F_WD_Time-Watchdog, DCP-Reset, Reparametrierung, Flood/Fuzzing |

---

## 6. Testreihenfolge (verbindlich)

Die Reihenfolge ist festgelegt, weil einzelne Tests den Gerätezustand dauerhaft verändern:

1. **VLAN A zuerst** — alle geräte-lokalen, nicht-invasiven Tests (HTTP/IoT-Core auslesen, Siegelprüfung, Debug-Interface-Untersuchung).
2. **VLAN B danach** — Moduswechsel per Switch-Toggle; alle netzwerk-/protokollabhängigen Tests mit aktivem PROFIsafe-Zyklus.
3. **Cold-Start-/Power-Cycle-Test als letzter Schritt** — löscht das Error-Log unwiderruflich; darf erst ausgeführt werden, **nachdem alle vorherigen Logs gesichert sind**.

---

## 7. Dokumentations- & Auswertungsschicht

Gilt modusunabhängig und wird für jeden Testlauf identisch befüllt:

| Ablage | Inhalt |
|---|---|
| **PCAP-Archiv** | Mitschnitte aus VLAN A + B, zeitgestempelt (`tshark`-Export) |
| **Geräte-Logs** | Error Log (`/devicestatus/errorlog`), I&M0-Records, `REVISION_COUNTER`, `F_iParCRC`/`F_ParCRC` |
| **Testprotokoll je RQ** | Gegenüberstellung Normalbetrieb vs. Testfall (Antwortzeiten, Zykluszeit, beobachtetes Verhalten, Pass/Fail-Oracle) |
| **Foto-/Video-Doku** | Physische Tests (Siegel, Schalter, Debug-Zugriff) |
| **FW-/HW-Revisions-Log** | Firmware- und Hardwarestand, für die gesamte Kampagne einmalig fixiert und dokumentiert |
| **Gap-Nachweis-Ablage** | Pro RQ ein Ordner mit allen zugehörigen Belegen |

---

## 8. RQ → Betriebsmodus → Werkzeug (Zuordnung)

| RQ | Betriebsmodus | Primär-Werkzeug(e) | Beobachter/Beleg |
|---|---|---|---|
| RQ-001 (Trusted Safety / Domain Separation) | A + B | Nmap, Wireshark, Scapy | Sniffer: F_Dest/F_Source/CRC im Normalbetrieb |
| RQ-002 (Tampering Prozessdaten, CRC) | B | Scapy (PROFIsafe-Frame), Siegelprüfung | Sniffer + SCPU-Reaktion |
| RQ-003 (Tamper-Evidence physisch) | A | JTAGulator/Logic Analyzer, curl, Wireshark | Error-Log-Negativnachweis |
| RQ-004 (Info Disclosure Version) | A | curl (+ Wireshark Klartext-Beleg) | PCAP: kein TLS-Handshake |
| RQ-005 (Config/Firmware Integrity) | B (+ A für Doku) | Scapy (iPar/F-Param), binwalk + Doku-Review | Sniffer + Header-Analyse |
| RQ-006 (SW-Inventory Disclosure) | A | curl | PCAP |
| RQ-007 (DoS Verbindungslimit) | A | curl (2 offene Sessions + 3. Versuch) | Monitoring-Skript |
| RQ-008 (Repudiation FW/Mode) | A + B | Wireshark (I&M0/Record 0xAFF0), Debug-Prüfung | Sniffer |
| RQ-009 (Repudiation Config-Change) | B (+ A) | Wireshark (I&M0/iParCRC), curl | Sniffer |
| RQ-010 (DoS PROFINET-Stack) | B | Scapy (Flood), boofuzz | TAP: Zykluszeit-Messung |
| RQ-011 (Auth/Autorisierung Parametrierung) | B | Scapy (Param-Begin/Write/End), pnio_dcp, physischer Bypass | Sniffer + Response-Verifikation |
| RQ-012 (Log-Retention, Cold-Start) | A (**zuletzt**) | curl (vor/nach), schaltbare Steckdose | PCAP + Log-Vergleich |
| RQ-013 (Version-Tracing) | A | curl + Doku-Review | — |
| RQ-014 (Log-Zugriffsbeschränkung) | A | curl (unauth. GET) | PCAP |

---

## 9. Kurzübersicht aller Bestandteile

- **1× Managed Switch** (VLAN, SPAN, Protected Ports) — optional zusätzlich **1× passiver TAP**
- **1× SRIO (AL400S/AL401S)** als DUT, dauerhaft verkabelt
- **1× schaltbare Steckdosenleiste** für kontrollierte Cold-Starts
- **1× Angreifer-PC** — Kali bare-metal, Intel-NIC (Scapy, boofuzz, Nmap, curl, ZAP, Nikto, pnio_dcp)
- **1× Sniffer-PC** — passiv am SPAN/TAP (Wireshark + tshark); Raspberry Pi 4 genügt
- **1× Engineering-PC** — Windows, TIA V18 + ifm-CRC-Tool (reine Konfig-Rolle)
- **1× F-Host** — S7-1500F/1200F, TIA V18
- **1× Debug-Ausrüstung** (JTAGulator, Logic Analyzer)
- **1× Siegel-/Tamper-Testkit**
- **1× Dokumentationsablage** (PCAP, Geräte-Logs, Testprotokolle, Revisionsstände)
