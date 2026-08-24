# Testumgebung: Security-Funktionsprüfung Safe Remote I/O (SRIO)
### Überarbeitete Version 2.0 — korrigiert, ergänzt, mit Rollentrennung

> Ein einzelner Stand-Alone-Rechner reicht nicht aus, weil ein Teil der Sicherheitslücken (CRC-Manipulation, Parametrierungs-Bypass, Fuzzing) nur im laufenden PROFIsafe-Betrieb mit echter Safety-SPS beobachtbar ist. Deshalb werden zwei sich ergänzende Testumgebungen aufgebaut: ein isolierter Einzelplatzrechner für geräte-lokale Tests (HTTP/IoT-Core, physische Manipulation) und ein isoliertes VLAN mit echter F-CPU für die netzwerk-/protokollabhängigen Tests. Beide sind komplett vom Firmennetz getrennt und bilden damit kontrolliert genau die "Firewall-Annahme" (SRIO-9402) nach — statt sie unbelegt zu übernehmen.


## 1. Kategorien der Testinterfaces

* **Geräte-lokal** (HTTP/IoT-Core, Physical/Debug) — kein F-Host, kein Netzwerk-Segment nötig
* **Netzwerk-/Protokoll-abhängig** (PROFIsafe-Zyklus, F-Host-State, DCP, Fuzzing) — erfordert reale PROFINET-Topologie

---

## 2. EBENE A: "Isolierter Stand-Alone-Rechner" (Air-Gapped Bench Setup)

* Kein Netzwerk, 1:1-Verbindung
* Kein F-Host nötig
* HTTP / Physical / Debug-Tests

### 2.1 Zweck

* *"The usecase of this device is assumed to be located in a safe zone behind a firewall."* (SRIO-9402)
* *"From the point of view of Security the FW-Update shall be done behind a firewall (shopfloor) by a trustworthy person."* (SRIO-1196)

### 2.2 Visualisierung

```
┌────────────────────────────────────────────────────────────── ┐
│                    EBENE A — Air-Gapped Bench                 │
│                                                               │
│   ┌───────────────────────────┐                               │
│   │   Test-PC (isoliert)      │                               │
│   │  ─────────────────────    │                               │
│   │  • Kein Internet          │                               │
│   │  • Keine Domäne           │        1 Ethernet-Kabel       │
│   │  • Fixierter OS-Stand     │◄───────(Punkt-zu-Punkt,──────►│  ┌───────────┐
│   │    (Snapshot/Image)       │         kein Switch,          │  │   SRIO    │
│   │                           │         kein DHCP)            │  │ AL400S /  │
│   │  Werkzeuge:               │                               │  │ AL401S    │
│   │  - Kali Linux (VM/Dual)   │                               │  │ (DUT-A)   │
│   │  - Wireshark + PROFIsafe- │                               │  └─────┬─────┘
│   │    Dissector              │                               │        │
│   │  - Scapy                  │                               │   Rotary/DIL-
│   │  - curl / Burp            │                               │   Switches frei
│   │  - JTAGulator-Treiber     │                               │   zugänglich
│   │  - sigrok / PulseView     │                               │
│   └───────────────────────────┘                               │
│                                                               │
│   Zusatz-Equipment:                                           │
│   • Siegel-Test-Kit (Nachbau-/Ablösewerkzeug)                 │
│   • Schaltbare Steckdosenleiste (ferngesteuert, für           │
│     kontrollierte, geplante Power-Cycles)                     │
│   • Logic Analyzer (für Debug-Interface-Tests)                │
│   • Sekundäres "Verschleiß-DUT" (siehe Abschnitt 5)           │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 Komponenten im Detail

| Komponente | Ausprägung | Zweck |
|---|---|---|
| Rechner | Physisch getrennter Laptop/PC, kein Internet, keine Domänenanbindung, fixiertes OS-Image | Reproduziert "hinter Firewall"-Isolation kontrolliert und reproduzierbar |
| Netzwerk | 1 Ethernet-Kabel direkt zum SRIO, kein Switch, kein DHCP-Server | "Ein Gerät, ein Zugang" — keine Störfaktoren, keine Fremdgeräte im Segment |
| Software | Kali Linux, Wireshark (PROFIsafe-Dissector), Scapy, curl/Burp, JTAGulator, sigrok/PulseView | Deckt Netzwerk-Sniffing, HTTP-Tests, Debug-Zugriff ab |
| Physischer Aufbau | SRIO auf Laborhalterung, Schalter frei zugänglich | Für Siegel-/Tamper- und Schalterstellungstests |
| Zusatz | Ferngesteuerte Steckdosenleiste, Siegel-Testkit | Für RQ-003 (Tamper), RQ-012 (Cold-Start) — Power-Cycle *kontrolliert und protokolliert*, nicht durch physisches Kabelziehen |


---

## 3. EBENE B: "Isoliertes VLAN-Testnetzwerk" (Segmented Testbed)

* Reales PROFINET-Netz
* Mit echter F-CPU
* PROFIsafe-Zyklus-abhängige Tests
* getrennte Rollen Access-Port-Angreifer / passiver Sniffer

### 3.1 Zweck

Diese Ebene bildet die **reale Betriebssituation** ab: SRIO als PROFINET-I/O-Device im zyklischen Datenaustausch mit einer echten Safety-SPS (F-Host), eingebettet in ein Netzwerksegment, das komplett vom Firmennetz getrennt ist.


### 3.2 Visualisierung 

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    EBENE B — Isoliertes VLAN-Testnetzwerk                 │
│                    (kein Routing nach außen, kein Firmennetz-Zugriff)     │
│                                                                           │
│                         ┌────────────────────────┐                        │
│                         │   Managed Switch        │                       │
│                         │   (z. B. SCALANCE)      │                       │
│                         │   Port-Mirroring (SPAN)  │                      │
│                         │   + Protected Ports      │                      │
│                         └──┬────────┬────────┬────┘                       │
│                            │        │        │                            │
│              ┌─────────────┘        │        └─────────────┐              │
│              │                      │                      │              │
│    ┌─────────▼────────── ┐  ┌────────▼──────────┐  ┌────────▼──────────┐  │
│    │   F-Host / SPS      │  │      SRIO          │  │  Engineering-PC   │ │
│    │  ────────────────── │  │   AL400S/AL401S    │  │  ────────────────  │  │
│    │  Siemens S7-1500F   │  │   (DUT-B)          │  │  TIA Portal V18    │  │
│    │  oder S7-1200F      │  │                    │  │  (Konfiguration,   │  │
│    │  (TIA Portal V18)   │  │  PROFINET/         │  │   NICHT Angreifer- │  │
│    │                     │◄─┤  PROFIsafe         │  │   Rolle!)          │  │
│    │  zyklische          │  │  aktiv             │  │                    │  │
│    │  Kommunikation      │  │                    │  │                    │  │
│    └─────────────────────┘  └─────────┬──────────┘  └────────────────────┘  │
│                                        │                                   │
│                              ┌─────────┴──────────┐    Mirror-Port         │
│                              │  ACCESS-PORT        │◄──(nur Kopie,         │
│                              │  Angreifer-PC        │    keine Injektion)  │
│                              │  ────────────────    │                      │
│                              │  Kali Linux          │        │             │
│                              │  • Scapy             │        │             │
│                              │    (scapy.contrib.   │        ▼             │
│                              │     pnio_dcp)        │  ┌──────────────┐    │
│                              │  • boofuzz/ProFuzz   │  │  Sniffer-PC   │    │
│                              │  • Nmap              │  │  ──────────── │    │
│                              │  • pnio_dcp/profi-dcp│  │  Wireshark    │    │
│                              │  • ggf. Community-   │  │  (PROFIsafe-  │    │
│                              │    Stack als         │  │   Dissector)  │    │
│                              │    Rogue-Master-Basis│  │  rein passiv, │    │
│                              │  (eigene MAC/IP, im  │  │  KEINE Frame- │    │
│                              │   selben VLAN, normal│  │  Injektion    │    │
│                              │   weitergeleitet)    │  └──────────────┘    │
│                              └─────────────────────┘                       │
│                                                                            │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 Komponenten im Detail

| Komponente | Ausprägung | Begründung / Quelle |
|---|---|---|
| **F-Host** | Siemens S7-1500F (z. B. 1511F-1PN) oder S7-1200F, TIA Portal V18, **Safety Advanced Engineering-Option + F-Runtime-Lizenz vorab beschaffen** | Offiziell als primäre Testplattform des Herstellers vorgesehen (SRIO-6599) |
| **Managed Switch** | Mit Port-Mirroring/SPAN **und** Protected-Port/Private-VLAN-Funktion | Ermöglicht Traffic-Capture ohne Beeinflussung der Echtzeitkommunikation; Protected Ports verhindern unkontrolliertes "Übersprechen" zwischen Test-Segmenten |
| **VLAN-Segmentierung** | Physisch/logisch komplett vom Firmennetz getrennt, kein Routing, **Isolation selbst durch Portscan verifizieren** (nicht nur unterstellen) | Reproduziert "Shopfloor hinter Firewall" *kontrolliert*, statt sie zu unterstellen |
| **Access-Port-Angreifer-PC** | Kali Linux, eigene MAC/IP, **normaler Switch-Port** (kein Mirror) | Für aktive Injektion: CRC-Manipulation, DCP-Reset, Fuzzing, Rogue-Master-Sequenzen |
| **Sniffer-PC** (kann zweite NIC am selben Rechner sein) | Am Mirror-Port, rein passiv | Für Verifikation des Normalbetriebs (RQ-001: "läuft F_Dest_Add/CRC im normalen Betrieb wie dokumentiert?") ohne Beeinflussung der Live-Kommunikation |
| **Engineering-PC** | TIA Portal, physisch getrennt vom Angreifer-PC | Klare Rollentrennung Konfigurator ≠ Angreifer → saubere Nachweisführung |
| **DUT-B** | SRIO AL400S/AL401S (Referenzgerät, siehe Abschnitt 5) | Testobjekt |
| **Optional** | Zweites Feldgerät in Daisy-Chain | Für realistischere "Shared-Segment"-Angriffsszenarien |


---

## 4. Gesamtarchitektur — Wie beide Ebenen zusammen ein Testlabor bilden

```
   ┌─────────────────────────────────┐         ┌───────────────────────────────────┐
   │                                 │         │                                   │
   │        ZONE 1                   │         │            ZONE 2                  │
   │   EBENE A — Air-Gapped          │         │    EBENE B — Isoliertes VLAN       │
   │       Bench Setup               │         │      Segmented Testbed             │
   │                                 │  DUT    │                                    │
   │  ┌────────────────────────┐     │ wandert │  ┌──────────────┐ ┌──────────────┐ │
   │  │   Test-PC (isoliert)   │     │  NICHT  │  │  F-Host (SPS)│ │Engineering-  │ │
   │  │  Kali, Wireshark,      │     │ zwischen│  │  S7-1500F /  │ │PC (TIA)      │ │
   │  │  Scapy, curl, JTAG     │     │  Zonen  │  │  S7-1200F    │ │              │ │
   │  └──────────┬──────────────┘    │ (siehe  │  └──────┬───────┘ └──────┬───────┘ │
   │             │ 1:1 Kabel         │ Abschn. │         │                │         │
   │  ┌──────────▼──────────────┐    │ 5: zwei │  ┌──────▼────────────────▼──────┐  │
   │  │   SRIO (DUT-A)          │    │ separate│  │      Managed Switch          │  │
   │  │   Rotary/DIL-Switch     │    │  DUTs)  │  │  (Port-Mirroring/SPAN,       │  │
   │  │   frei zugänglich       │    │         │  │   Protected Ports)           │  │
   │  └─────────────────────────┘    │         │  └───┬───────────────────┬─────┘   │
   │                                 │         │      │                   │        │
   │  Zusatzequipment:               │         │  ┌───▼──────┐    ┌───────▼──────┐ │
   │  • Siegel-Testkit               │         │  │ SRIO     │    │ Access-Port  │ │
   │  • ferngest. Steckdosenleiste   │         │  │ (DUT-B)  │    │ Angreifer-PC │ │
   │  • Logic Analyzer               │         │  └──────────┘    │ Scapy,       │ │
   │                                 │         │      ▲            │ boofuzz,    │ │
   │                                 │         │      │ Mirror     │ Community-  │ │
   │                                 │         │  ┌───┴──────┐    │ Stack        │ │
   │                                 │         │  │ Sniffer  │    └──────────────┘ │
   │                                 │         │  │ -PC      │                     │
   │                                 │         │  │ (passiv) │                     │
   │                                 │         │  └──────────┘                     │
   └─────────────────────────────────┘         └───────────────────────────────────┘
                  │                                              │
                  └──────────────────┬───────────────────────────┘
                                     │
                                     ▼
                  ┌────────────────────────────────────────────┐
                  │      GEMEINSAME DOKUMENTATIONS- &            │
                  │           AUSWERTUNGSSCHICHT                 │
                  │  ─────────────────────────────────────────   │
                  │  • PCAP-Mitschnitte (Ebene A + B)            │
                  │  • Testprotokolle je RQ (Vorlage)            │
                  │  • Foto-/Videodokumentation physischer Tests │
                  │  • Firmware-/Hardware-Revisionsstand-Log     │
                  │    (fixiert für gesamte Testkampagne)        │
                  │  • Testsequenz-/Abhängigkeitsplan            │
                  │  • Gap-Nachweis-Ablage (pro RQ ein Ordner)   │
                  └────────────────────────────────────────────┘
```

---

## 5. Zwei-DUT-Strategie

Ein einzelnes SRIO-Gerät für *alle* Tests zu verwenden birgt zwei Risiken:

1. **Physische Degradation**: Siegel-Manipulationstests, JTAG/Debug-Zugriffsversuche und wiederholte Schalterbetätigung können das Gerät sichtbar beschädigen oder in einen nicht mehr repräsentativen Zustand versetzen — bevor die netzwerkbasierten PROFIsafe-Tests (Ebene B) überhaupt durchgeführt wurden.
2. **Zustandsverschmutzung**: Cold-Starts, Error-Log-Einträge und Firmware-Downgrades aus Ebene-A-Tests würden den Beweiswert der Ebene-B-Tests verwässern (z. B. wäre nicht mehr eindeutig nachweisbar, ob ein Log-Eintrag aus einem echten PROFIsafe-Betriebsfehler oder einem vorherigen manuellen Eingriff stammt).

**Empfehlung**: Zwei separate SRIO-Einheiten gleicher Firmware-/Hardware-Revision beschaffen:

| Gerät | Rolle | Verwendung |
|---|---|---|
| **DUT-A ("Verschleiß-Gerät")** | Fest in Ebene A verbaut | Physische/Debug-Tests, Siegel, Cold-Start-Reihen, HTTP/IoT-Core |
| **DUT-B ("Referenz-Gerät")** | Fest in Ebene B verbaut | Ausschließlich PROFINET/PROFIsafe-Zyklus-Tests mit F-Host, möglichst wenig physisch angefasst |

Dies erhöht zwar die Beschaffungskosten leicht, vermeidet aber Verzerrungen der Testergebnisse und stellt sicher, dass jedes RQ auf einem für seine Testkategorie "sauberen" Gerätezustand basiert.

---




## 6. Testsequenz & Abhängigkeiten 

Manche Tests sind **irreversibel** oder beeinflussen nachfolgende Tests (Beispiel aus der ursprünglichen Tabelle: Cold-Start löscht den Error-Log). Eine dokumentierte Reihenfolge ist daher Pflichtbestandteil der Methodik, nicht optional:

1. **Web/API-Block** zuerst (keine Abhängigkeiten, non-destruktiv): RQ-004, RQ-006, RQ-007, RQ-014
2. **Netzwerk-Scan/Sniffing** (non-destruktiv, liefert Referenz-PCAPs für spätere Vergleiche): RQ-001
3. **I&M0-Auslese / Log-Reviews** (non-destruktiv, vor jeder Zustandsänderung als Baseline sichern): RQ-008, RQ-009
4. **CRC-Kollisionstests** (gebündelt, verändert Konfigurationszustand): RQ-002, RQ-005
5. **Flood/Fuzzing-Test** (kann Fehlerzustände erzeugen, danach ggf. Reset nötig): RQ-010
6. **Physischer F-Adress-/Mode-Test + Power-Cycle** (verändert Adressierung, ggf. Log-Einfluss prüfen): RQ-011
7. **Siegel-/Tamper-Test** (potenziell sichtbare/irreversible physische Veränderung): RQ-003
8. **Erzwungener Cold-Start** (**zuletzt** — zerstört den Log-Zustand des Geräts vollständig): RQ-012
9. **Dokumentenprüfung** (jederzeit parallel möglich, keine Geräteinteraktion): RQ-013

Diese Sequenz ist geräte- und ebenenspezifisch zu führen (getrennt für DUT-A und DUT-B) und als Prüfplan mit Ausführungsdatum/-uhrzeit in der Dokumentationsschicht abzulegen.

---

