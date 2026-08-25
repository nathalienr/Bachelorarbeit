# Testumgebung: Security-Funktionsprüfung Safe Remote I/O (SRIO)
> Ein einzelner Stand-Alone-Rechner reicht nicht aus, weil ein Teil der Sicherheitslücken (CRC-Manipulation, Parametrierungs-Bypass) nur im laufenden PROFIsafe-Betrieb mit echter Safety-SPS beobachtbar ist. Deshalb schlage ich zwei sich ergänzende Testumgebungen vor: einen isolierten Einzelplatzrechner für geräte-lokale Tests (HTTP/IoT-Core, physische Manipulation) und ein isoliertes VLAN mit echter F-CPU für die netzwerk-/protokollabhängigen Tests. Beide sind komplett vom Firmennetz getrennt und bilden damit kontrolliert genau die 'Firewall-Annahme' nach."

Kategorien der Testinterfaces:
* **Geräte-lokal** (HTTP/IoT-Core, Physical/Debug) 
* **Netzwerk-/Protokoll-abhängig** (PROFIsafe-Zyklus, F-Host-State) 


## **EBENE A**: "Isolierter Stand-Alone-Rechner" (Air-Gapped Bench Setup)   
* Kein Netzwerk, 1:1 Verbindung    
* Kein F-Host nötig
* HTTP / Physical / Debug-Tests 


### Zweck
* *"The usecase of this device is assumed to be located in a safe zone behind a firewall."* (SRIO-9402)
* *"From the point of view of Security the FW-Update shall be done behind a firewall (shopfloor) by a trustworthy person."* (SRIO-1196)


### Visualisierung
```
┌──────────────────────────────────────────────────────────────┐
│                    EBENE A — Air-Gapped Bench                │
│                                                              │
│   ┌─────────────────────────  ┐                              │
│   │   Test-PC (isoliert)      │                              │
│   │  ─────────────────────    │                              │
│   │  • Kein Internet          │                              │
│   │  • Keine Domäne           │        1 Ethernet-Kabel      │
│   │  • Alter/minimaler OS-    │◄───────(Punkt-zu-Punkt,─────►│  ┌───────────┐
│   │    Stand (optional)       │         kein Switch,         │  │   SRIO    │
│   │                           │         kein DHCP)           │  │ AL400S /  │
│   │  Werkzeuge:               │                              │  │ AL401S    │
│   │  - Kali Linux (VM/Dual)   │                              │  │ (DUT)     │
│   │  - Wireshark + PROFIsafe- │                              │  └─────┬─────┘
│   │    Dissector              │                              │        │
│   │  - Scapy                  │                              │   Rotary/DIL-
│   │  - curl                   │                              │   Switches frei
│   │  - JTAGulator-Treiber     │                              │   zugänglich
│   │  - sigrok / PulseView     │                              │
│   └─────────────────────────  ┘                              │
│                                                              │
│   Zusatz-Equipment:                                          │
│   • Siegel-Test-Kit (Nachbau-/Ablösewerkzeug)                │
│   • Power-Cycle-Schalter / Steckdosenleiste mit Schalter     │
│   • Logic Analyzer (für Debug-Interface-Tests)               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Komponenten im Detail

| Komponente | Ausprägung | Zweck |
|---|---|---|
| Rechner | Physisch getrennter Laptop/PC, kein Internet, keine Domänenanbindung | Reproduziert "hinter Firewall"-Isolation kontrolliert |
| Netzwerk | 1 Ethernet-Kabel direkt zum SRIO, kein Switch, kein DHCP-Server | "Ein Gerät, ein Zugang" — keine Störfaktoren |
| Software | Kali Linux, Wireshark (PROFIsafe-Dissector), Scapy, curl, JTAGulator, sigrok/PulseView | Deckt Netzwerk-Sniffing, HTTP-Tests, Debug-Zugriff ab |
| Physischer Aufbau | SRIO auf Laborhalterung, Schalter frei zugänglich | Für Siegel-/Tamper- und Schalterstellungstests |
| Zusatz | Power-Cycle-Schalter, Siegel-Testkit | Für RQ-003 (Tamper), RQ-012 (Cold-Start) |


## **EBENE B**: "Isoliertes VLAN"  abhängige Tests (Segmented Testbed)     
* Reales PROFINET-Netz     
* Mit echter F-CPU 
* PROFIsafe-Zyklus- abhängige Tests 


### Zweck
Diese Ebene bildet die **reale Betriebssituation** ab: SRIO als PROFINET-I/O-Device im zyklischen Datenaustausch mit einer echten Safety-SPS (F-Host), eingebettet in ein Netzwerksegment.

### Visualisierung

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

### Komponenten im Detail

| Komponente | Ausprägung | Begründung / Quelle |
|---|---|---|
| **F-Host** | Siemens S7-1500F (z. B. 1511F-1PN) oder S7-1200F, TIA Portal V18 | Offiziell als primäre Testplattform des Herstellers vorgesehen  |
| **Managed Switch** | Mit Port-Mirroring/SPAN-Funktion | Ermöglicht Traffic-Capture ohne Beeinflussung der Echtzeitkommunikation |
| **VLAN-Segmentierung** | Physisch/logisch komplett vom Firmennetz getrennt, kein Routing | Reproduziert "Shopfloor hinter Firewall" *kontrolliert*, statt sie zu unterstellen |
| **Angreifer-PC** | Kali Linux; Scapy, boofuzz, Wireshark, Nmap, pnio_dcp/profi-dcp | Deckt Netzwerk-Scan, DCP-Reset, CRC-Manipulation, Fuzzing ab |
| **Engineering-PC** | TIA Portal, physisch getrennt vom Angreifer-PC | Klare Rollentrennung Konfigurator ≠ Angreifer → saubere Nachweisführung |
| **DUT** | SRIO AL400S/AL401S | Testobjekt |
| **Optional** | Zweites Feldgerät in Daisy-Chain | Für realistischere "shared segment"-Angriffsszenarien |

## 4. Gesamtarchitektur — Wie beide Ebenen zusammen ein Testlabor bilden
```



   ┌────────────────────────────    ┐         ┌──────────────────────────────────┐
   │                                │         │                                  │
   │        ZONE 1                  │         │            ZONE 2                │
   │   EBENE A — Air-Gapped         │         │    EBENE B — Isoliertes VLAN     │
   │       Bench Setup              │         │      Segmented Testbed           │
   │                                │  DUT    │                                  │
   │  ┌──────────────────────  ┐    │ wandert │  ┌──────────────┐ ┌─────────────┐│
   │  │   Test-PC (isoliert)   │    │ zwischen│  │  F-Host (SPS)│ │Engineering- ││
   │  │  Kali, Wireshark,      │    │  Zonen  │  │  S7-1500F /  │ │PC (TIA)     ││
   │  │  Scapy, curl, JTAG     │    │ ──────► │  │  S7-1200F    │ │             ││
   │  └──────────┬─────────────┘    │         │  └──────┬───────┘ └──────┬──────┘│
   │             │ 1:1 Kabel        │         │         │                │       │
   │             │                  │         │         │                │         │
   │  ┌──────────▼──────────────┐    │        │  ┌──────▼────────────────▼──────┐  │
   │  │   SRIO (DUT-A)          │    │        │  │      Managed Switch          │  │
   │  │   Rotary/DIL-Switch     │    │        │  │  (Port-Mirroring/SPAN,       │  │
   │  │   frei zugänglich       │    │        │  │   Protected Ports)           │  │
   │  └─────────────────────────┘    │        │  └───┬───────────────────┬─────┘   │
   │                                 │        │      │                   │        │
   │  Zusatzequipment:               │        │  ┌───▼──────┐    ┌───────▼──────┐ │
   │  • Siegel-Testkit               │        │  │ SRIO     │    │ Access-Port  │ │
   │  • ferngest. Steckdosenleiste   │        │  │ (DUT-B)  │    │ Angreifer-PC │ │
   │  • Logic Analyzer               │        │  └──────────┘    │ Scapy,       │ │
   │                                 │        │      ▲            │ boofuzz,    │ │
   │                                 │        │      │ Mirror     │ Community-  │ │
   │                                 │        │  ┌───┴──────┐    │ Stack        │ │
   │                                 │        │  │ Sniffer  │    └──────────────┘ │
   │                                 │        │  │ -PC      │                     │
   │                                 │        │  │ (passiv) │                     │
   │                                 │        │  └──────────┘                     │
   └─────────────────────────────────┘        └───────────────────────────────────┘
                  │                                              │
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

## Drei Wege, das Umstecken zu vermeiden

#### Option 1 — "Immer volle Topologie" (einfachste Lösung)

Das SRIO bleibt **dauerhaft** wie in Ebene B verkabelt: permanent an Switch, F-Host, Engineering-PC und Angreifer-PC angeschlossen, permanent mit Strom versorgt. Für alle "Ebene-A-artigen" Tests wird einfach der Test-/Angreifer-Rechner im selben Netz verwendet — unabhängig davon, ob der F-Host gerade aktiv zykliert oder nicht.

- ✅ Kein Umstecken, kein Kabel bewegen, keine Stromunterbrechung → **kein Cold-Start**
- ✅ Realistischeres Abbild des späteren Produktivbetriebs (SRIO ist in der Praxis fast immer an einer SPS angeschlossen)
- ✅ Geringster Aufwand
- ⚠️ Für RQ-001 (Firewall-Abschottung) allein nicht ausreichend — dafür braucht es Option 2 oder 3

#### Option 2 — VLAN-Portumschaltung am Switch (Software-Toggle)

Ein einzelner Managed Switch mit mehreren VLANs. Das SRIO bleibt fix am Switch verkabelt; über die Switch-Konfiguration (Web-Interface/CLI) wird der SRIO-Port einer VLAN "isoliert" (nur Test-Client erreichbar) oder VLAN "voll" (F-Host, Engineering-PC, Angreifer-PC erreichbar) zugewiesen.

- ✅ Kein Kabel wird am SRIO bewegt, keine Stromunterbrechung → **kein Cold-Start**
- ✅ Wechsel dauert Sekunden, reproduzierbar, per Config-Snapshot dokumentierbar
- ⚠️ Physisch bleibt es dieselbe Switch-Hardware — für strikt-physische Trennung ggf. als "logische Trennung" kennzeichnen (für die Nachweisführung i. d. R. ausreichend, da weiterhin komplett vom Firmennetz getrennt)

#### Option 3 — Hardware-Ethernet-A/B-Switch (physische Wegumschaltung ohne DUT-Eingriff)

Eine kostengünstige, handelsübliche "Ethernet A/B Switch Box" (mit manuellem Kippschalter oder relaisbasiert/fernsteuerbar) wird zwischen dem SRIO-Fieldbus-Port (ein einziges, dauerhaft angeschlossenes Kabel) und den beiden Zielumgebungen geschaltet: Pfad A → isolierter Test-PC, Pfad B → Zone-B-Switch mit F-Host.

- ✅ Echte galvanische/physische Pfadtrennung (kein gemeinsames Switch-Silicon, keine VLAN-Fehlkonfigurationsgefahr)
- ✅ SRIO-Stromversorgung bleibt während des *gesamten* Wechsels durchgehend angeschlossen → **kein Cold-Start**, allenfalls kurzer Link-Down (→ EC3/Fallback auf Parametrization — Standardverhalten, erholt sich automatisch)
- ⚠️ Zusatzkosten für die Switchbox (aber gering, off-the-shelf erhältlich)

####  Option 4 - **2 Geräte verwenden**

