# Testumgebung: Security-Funktionsprüfung Safe Remote I/O (SRIO)
### Überarbeitete Version 2.0 — korrigiert, ergänzt, mit Rollentrennung

> Ein einzelner Stand-Alone-Rechner reicht nicht aus, weil ein Teil der Sicherheitslücken (CRC-Manipulation, Parametrierungs-Bypass, Fuzzing) nur im laufenden PROFIsafe-Betrieb mit echter Safety-SPS beobachtbar ist. Deshalb werden zwei sich ergänzende Testumgebungen aufgebaut: ein isolierter Einzelplatzrechner für geräte-lokale Tests (HTTP/IoT-Core, physische Manipulation) und ein isoliertes VLAN mit echter F-CPU für die netzwerk-/protokollabhängigen Tests. Beide sind komplett vom Firmennetz getrennt und bilden damit kontrolliert genau die "Firewall-Annahme" (SRIO-9402) nach — statt sie unbelegt zu übernehmen.

**Wichtigste Änderungen gegenüber der Ursprungsversion:**

| # | Problem in v1.0 | Korrektur in v2.0 |
|---|---|---|
| 1 | Angreifer-PC hing am **Mirror/SPAN-Port** → kann keine Frames injizieren, nur mitlesen | Rollentrennung: **Access-Port-Angreifer** (aktiv, injiziert) getrennt vom **Sniffer** (passiv, am Mirror-Port) |
| 2 | Kein Hinweis, dass ein zweiter "Rogue-Master" i. d. R. keine parallele AR zum F-Host aufbauen kann | Eigener Abschnitt "Rogue-Master-Fähigkeit" mit Tooling-Machbarkeitsplan |
| 3 | Kein Hinweis auf Risiko der Geräte-Degradation durch physische/Debug-Tests | Zwei-DUT-Strategie (Referenz-SRIO / Verschleiß-SRIO) |
| 4 | Keine Aussage zu Lasten an den DO-Ports während Fuzzing/DoS | Dummy-Lasten-Vorgabe (keine realen Aktoren) |
| 5 | Umsteck-Optionen nicht bewertet | Klare Empfehlung: Hardware-A/B-Switch als Standard |
| 6 | Kein Hinweis auf F_Source_Add-Korrektur aus Gap-Review | In Testdesign RQ-001 eingearbeitet |
| 7 | Keine Testreihenfolge/Sequenzplanung als Artefakt | Eigener Abschnitt „Testsequenz & Abhängigkeiten" |

---

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
┌──────────────────────────────────────────────────────────────┐
│                    EBENE A — Air-Gapped Bench                │
│                                                                │
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
│                                                                │
│   Zusatz-Equipment:                                            │
│   • Siegel-Test-Kit (Nachbau-/Ablösewerkzeug)                 │
│   • Schaltbare Steckdosenleiste (ferngesteuert, für            │
│     kontrollierte, geplante Power-Cycles)                      │
│   • Logic Analyzer (für Debug-Interface-Tests)                 │
│   • Sekundäres "Verschleiß-DUT" (siehe Abschnitt 5)            │
│                                                                │
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

### 2.4 Relevante RQ-Zuordnung (aus MVO-Tabelle)

RQ-003, RQ-004, RQ-006, RQ-007, RQ-012, RQ-013, RQ-014 sowie die physischen Teile von RQ-002, RQ-008, RQ-011.

---

## 3. EBENE B: "Isoliertes VLAN-Testnetzwerk" (Segmented Testbed)

* Reales PROFINET-Netz
* Mit echter F-CPU
* PROFIsafe-Zyklus-abhängige Tests
* **Korrigiert:** getrennte Rollen Access-Port-Angreifer / passiver Sniffer

### 3.1 Zweck

Diese Ebene bildet die **reale Betriebssituation** ab: SRIO als PROFINET-I/O-Device im zyklischen Datenaustausch mit einer echten Safety-SPS (F-Host), eingebettet in ein Netzwerksegment, das komplett vom Firmennetz getrennt ist.

### 3.2 Warum die ursprüngliche Mirror-Port-Platzierung korrigiert werden musste

Ein SPAN-/Mirror-Port kopiert Traffic nur **einseitig** zum Analyse-Port; er ist kein normaler, bidirektional weiterleitender Switch-Port. Ein Angreifer-Rechner an diesem Port kann PROFINET-Traffic zwar **mitlesen**, aber **keine eigenen Frames** in die laufende Kommunikation zwischen F-Host und SRIO **injizieren** — der Switch leitet vom Mirror-Port gesendete Pakete nicht in die überwachte Konversation weiter. Alle Tests, die aktives Senden erfordern (CRC-Kollision, Parameter-Manipulation, DCP-Reset, Flood/Fuzzing), benötigen daher einen **regulären Access-Port** im selben VLAN mit eigener MAC/IP.

### 3.3 Visualisierung (korrigiert)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    EBENE B — Isoliertes VLAN-Testnetzwerk                 │
│                    (kein Routing nach außen, kein Firmennetz-Zugriff)     │
│                                                                           │
│                         ┌────────────────────────┐                        │
│                         │   Managed Switch        │                       │
│                         │   (z. B. SCALANCE)      │                       │
│                         │   Port-Mirroring (SPAN)  │                       │
│                         │   + Protected Ports      │                       │
│                         └──┬────────┬────────┬────┘                       │
│                            │        │        │                           │
│              ┌─────────────┘        │        └─────────────┐             │
│              │                      │                      │             │
│    ┌─────────▼──────────┐  ┌────────▼──────────┐  ┌────────▼──────────┐  │
│    │   F-Host / SPS      │  │      SRIO          │  │  Engineering-PC   │  │
│    │  ──────────────────  │  │   AL400S/AL401S   │  │  ────────────────  │  │
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
│                              │  • Nmap              │  │  ────────────  │    │
│                              │  • pnio_dcp/profi-dcp│  │  Wireshark    │    │
│                              │  • ggf. Community-   │  │  (PROFIsafe-  │    │
│                              │    Stack als          │  │   Dissector)  │    │
│                              │    Rogue-Master-Basis │  │  rein passiv, │    │
│                              │  (eigene MAC/IP, im   │  │  KEINE Frame- │    │
│                              │   selben VLAN, normal │  │  Injektion    │    │
│                              │   weitergeleitet)     │  └──────────────┘    │
│                              └─────────────────────┘                       │
│                                                                            │
│   Optional (Erweiterung):                                                  │
│   ┌────────────────────────┐                                               │
│   │  2. Feldgerät           │  → für Lateral-Movement- /                   │
│   │  (Daisy-Chain)          │    Shared-Segment-Tests                      │
│   └────────────────────────┘                                               │
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

### 3.5 Rogue-Master-Fähigkeit — eigener Machbarkeits-Baustein

Mehrere Tests (RQ-001, RQ-005, RQ-011) setzen voraus, dass der Angreifer-PC eine **vollständige oder teilweise PROFINET-Verbindung** aufbauen kann (DCP-Discovery, AR-Verbindungsaufbau, F-Parameter-Übergabe) — nicht nur einzelne Pakete senden. Das ist protokolltechnisch aufwändiger als ein einfaches Scapy-Skript und sollte als **eigener Arbeitspaket-Posten mit Zeitpuffer** eingeplant werden, nicht als Nebenprodukt der Testdurchführung.

| Baustein | Eignung | Aufwand |
|---|---|---|
| **Scapy + `scapy.contrib.pnio_dcp`** | Gut für DCP-Discovery/-Reset, einzelne RT-Frames, gezielte CRC-Kollisionstests an bereits etablierten Frametypen | Niedrig–Mittel |
| **ProFuzz** (Scapy-basiert, TH Augsburg, GPL-3.0) | Fuzzing von DCP-/Alarm-/zyklischen Frames; alt (2012) und rudimentär, aber als Ausgangsbasis nutzbar | Mittel (Anpassung nötig) |
| **PROFINET Community Stack** (PI, Open Source) | Enthält vollwertige Controller- **und** Device-Funktionalität inkl. Security-Class-1/2/3-Ansätzen; realistischste Basis für einen eigenen "Test-Master" mit vollständigem Verbindungsaufbau | Hoch (Einarbeitung), aber am belastbarsten |
| **p-net** (RT-Labs, reiner Device-Stack) | Keine Master-Rolle, daher nicht direkt nutzbar — aber als Referenz interessant: Fuzzing gegen p-net deckte 2025 zehn Schwachstellen auf, guter methodischer Beleg für Fuzzing-Wirksamkeit in der Thesis | — (nur Referenz) |
| **Kommerzielle Tools (z. B. Penzzer)** | Zeigen das Tooling-Niveau für belastbares PROFINET-Fuzzing (DCP, RT-Frames, Records, Alarme, stateful) | Lizenzabhängig |

**Wichtige Randbedingung:** Solange der reale F-Host eine aktive Application Relationship (AR) mit dem SRIO hält, kann ein zweiter, unabhängiger Master i. d. R. **keine parallele Verbindung** aufbauen (PROFINET/PROFIsafe erlauben typischerweise nur eine aktive Steuerungsbeziehung). Für "Rogue-Master ohne physischen Schalterzugriff"-Tests (RQ-011) muss daher entweder:

1. der F-Host kurzzeitig vom Access-Port getrennt werden (der Angreifer übernimmt testweise die Master-Rolle), oder
2. echtes Inline-MITM über einen **bidirektionalen Netzwerk-TAP** (statt Mirror-Port) betrieben werden, um Frames innerhalb der bestehenden Session abzufangen und zu verändern.

Beide Varianten sind sauber dokumentierbar; Variante 1 ist deutlich einfacher umzusetzen und für die meisten MVO-Punkte ausreichend.

### 3.6 Relevante RQ-Zuordnung

RQ-001 (Netzwerk-/Sniff-Teil), RQ-005 (Netzwerk-Teil), RQ-008/RQ-009 (I&M0-Auslese), RQ-010 (Flood/Fuzzing), RQ-011 (Netzwerk- und DCP-Teil).

---

## 4. Gesamtarchitektur — Wie beide Ebenen zusammen ein Testlabor bilden

```
   ┌─────────────────────────────────┐         ┌────────────────────────────────────┐
   │                                 │         │                                    │
   │        ZONE 1                  │         │            ZONE 2                  │
   │   EBENE A — Air-Gapped         │         │    EBENE B — Isoliertes VLAN       │
   │       Bench Setup              │         │      Segmented Testbed             │
   │                                 │  DUT    │                                    │
   │  ┌────────────────────────┐    │ wandert │  ┌──────────────┐ ┌──────────────┐ │
   │  │   Test-PC (isoliert)   │    │  NICHT  │  │  F-Host (SPS)│ │Engineering-  │ │
   │  │  Kali, Wireshark,      │    │ zwischen│  │  S7-1500F /  │ │PC (TIA)      │ │
   │  │  Scapy, curl, JTAG     │    │  Zonen  │  │  S7-1200F    │ │              │ │
   │  └──────────┬──────────────┘    │ (siehe  │  └──────┬───────┘ └──────┬───────┘ │
   │             │ 1:1 Kabel        │ Abschn. │         │                │         │
   │  ┌──────────▼──────────────┐   │ 5: zwei │  ┌──────▼────────────────▼──────┐  │
   │  │   SRIO (DUT-A)          │   │ separate│  │      Managed Switch          │  │
   │  │   Rotary/DIL-Switch     │   │  DUTs)  │  │  (Port-Mirroring/SPAN,       │  │
   │  │   frei zugänglich       │   │         │  │   Protected Ports)           │  │
   │  └─────────────────────────┘   │         │  └───┬───────────────────┬─────┘  │
   │                                 │         │      │                   │        │
   │  Zusatzequipment:               │         │  ┌───▼──────┐    ┌───────▼──────┐ │
   │  • Siegel-Testkit               │         │  │ SRIO     │    │ Access-Port  │ │
   │  • ferngest. Steckdosenleiste  │         │  │ (DUT-B)  │    │ Angreifer-PC │ │
   │  • Logic Analyzer               │         │  └──────────┘    │ Scapy,       │ │
   │                                 │         │      ▲            │ boofuzz,     │ │
   │                                 │         │      │ Mirror     │ Community-   │ │
   │                                 │         │  ┌───┴──────┐    │ Stack        │ │
   │                                 │         │  │ Sniffer  │    └──────────────┘ │
   │                                 │         │  │ -PC      │                     │
   │                                 │         │  │ (passiv) │                     │
   │                                 │         │  └──────────┘                     │
   └─────────────────────────────────┘         └────────────────────────────────────┘
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

**Wichtige Änderung gegenüber v1.0:** Das DUT wandert **nicht mehr** zwischen den Zonen. Ebene A und Ebene B verwenden **zwei getrennte, physisch unterschiedliche SRIO-Geräte** (DUT-A / DUT-B). Begründung siehe Abschnitt 5.

---

## 5. Zwei-DUT-Strategie (neu)

Ein einzelnes SRIO-Gerät für *alle* Tests zu verwenden birgt zwei Risiken:

1. **Physische Degradation**: Siegel-Manipulationstests (RQ-003), JTAG/Debug-Zugriffsversuche und wiederholte Schalterbetätigung können das Gerät sichtbar beschädigen oder in einen nicht mehr repräsentativen Zustand versetzen — bevor die netzwerkbasierten PROFIsafe-Tests (Ebene B) überhaupt durchgeführt wurden.
2. **Zustandsverschmutzung**: Cold-Starts (RQ-012), Error-Log-Einträge und Firmware-Downgrades (RQ-005/RQ-013) aus Ebene-A-Tests würden den Beweiswert der Ebene-B-Tests verwässern (z. B. wäre nicht mehr eindeutig nachweisbar, ob ein Log-Eintrag aus einem echten PROFIsafe-Betriebsfehler oder einem vorherigen manuellen Eingriff stammt).

**Empfehlung**: Zwei separate SRIO-Einheiten gleicher Firmware-/Hardware-Revision beschaffen:

| Gerät | Rolle | Verwendung |
|---|---|---|
| **DUT-A ("Verschleiß-Gerät")** | Fest in Ebene A verbaut | Physische/Debug-Tests, Siegel, Cold-Start-Reihen, HTTP/IoT-Core |
| **DUT-B ("Referenz-Gerät")** | Fest in Ebene B verbaut | Ausschließlich PROFINET/PROFIsafe-Zyklus-Tests mit F-Host, möglichst wenig physisch angefasst |

Dies erhöht zwar die Beschaffungskosten leicht, vermeidet aber Verzerrungen der Testergebnisse und stellt sicher, dass jedes RQ auf einem für seine Testkategorie "sauberen" Gerätezustand basiert.

---

## 6. Sicherheitsvorkehrungen während aktiver Tests (neu)

| Vorkehrung | Begründung |
|---|---|
| **Nur Dummy-Lasten an DO-Ports** (LEDs, kleine Testrelais) während Fuzzing/DoS-Tests (RQ-010) — **keine realen Aktoren oder Maschinenteile** | SRIO ist ein Safety-Bauteil; unvorhersehbares Ausgangsverhalten während Fuzzing darf in der Laborumgebung keine reale Gefährdung erzeugen |
| **Ferngesteuerte, protokollierte Power-Cycles** statt manuellem Kabelziehen | Reproduzierbarkeit und exakte Zeitstempel für RQ-003/RQ-012 |
| **Switch-Backplane-Kapazität vorab prüfen** | Bei Flood-Tests (RQ-010) muss sichergestellt sein, dass nicht der Switch selbst zum Flaschenhals wird — sonst Fehlattribution des beobachteten DoS-Effekts |
| **Fixierte Firmware-/Hardware-Baseline** für die gesamte Testkampagne, keine Auto-Updates | Ergebnisse (bes. RQ-004/006/013) sind versionsgebunden; Vergleichbarkeit über die gesamte Kampagne nur bei fixiertem Stand gegeben |

---

## 7. Testsequenz & Abhängigkeiten (neu, als eigenes Artefakt zu pflegen)

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

## 8. Drei Wege, das Umstecken zu vermeiden — bewertet

### Option 1 — "Immer volle Topologie"

Das SRIO bleibt dauerhaft wie in Ebene B verkabelt: permanent an Switch, F-Host, Engineering-PC angeschlossen. Für alle "Ebene-A-artigen" Tests wird der Test-Rechner im selben Netz verwendet.

- ✅ Kein Umstecken, kein Cold-Start
- ✅ Realistischstes Abbild des Produktivbetriebs
- ✅ Geringster Aufwand — **empfohlen für alle reinen HTTP/IoT-Core-Tests** (RQ-004, 006, 007, 014), bei denen die Isolationsfrage keine Rolle spielt
- ⚠️ Für RQ-001 (Firewall-Abschottung) allein **nicht ausreichend**, da keine echte isolierte Vergleichsbedingung mehr existiert

### Option 2 — VLAN-Portumschaltung am Switch (Software-Toggle)

- ✅ Kein Kabel wird am SRIO bewegt, kein Cold-Start
- ✅ Wechsel dauert Sekunden, per Config-Snapshot dokumentierbar
- ⚠️ Physisch bleibt es dieselbe Switch-Hardware — die Isolationswirkung muss **aktiv verifiziert** werden (z. B. Portscan aus dem "vollen" VLAN gegen das isolierte VLAN, um Übersprechen auszuschließen), sonst ist die Trennung nur behauptet
- **Nur als Fallback**, falls Budget/Platz für Option 3 fehlt — dann mit explizitem Isolationsnachweis als Anhang dokumentieren

### Option 3 — Hardware-Ethernet-A/B-Switch (physische Wegumschaltung) ✅ **empfohlen als Standard**

Eine handelsübliche "Ethernet A/B Switch Box" (manueller Kippschalter oder fernsteuerbar) wird zwischen dem SRIO-Fieldbus-Port und den beiden Zielumgebungen geschaltet.

- ✅ Echte galvanische/physische Pfadtrennung (kein gemeinsames Switch-Silicon)
- ✅ SRIO-Stromversorgung bleibt während des *gesamten* Wechsels durchgehend angeschlossen → **kein Cold-Start**, allenfalls kurzer Link-Down (→ EC3/Fallback auf Parametrization, Standardverhalten, erholt sich automatisch)
- ✅ Geringe Zusatzkosten (fertige Boxen bereits ab ca. 15–40 €, auch mit robustem Metallgehäuse und Rotary-Wahlschalter erhältlich)
- ✅ Methodisch am saubersten für die Argumentation "kontrolliert nachgebildete Isolationsbedingung" in der Thesis
- ⚠️ Beim Wechsel muss auf F-Host-Seite ggf. die PROFIsafe-Verbindung neu quittiert/integriert werden — kleiner Zusatzaufwand, aber Standardverhalten, kein Show-Stopper

**Hinweis:** Da nun ohnehin zwei getrennte DUTs (Abschnitt 5) empfohlen werden, reduziert sich der praktische Bedarf für Option 3 auf Szenarien, in denen *dasselbe* Gerät testweise kurzzeitig zwischen einem isolierten und einem vernetzten Pfad wechseln soll (z. B. Vergleichsmessungen). Für den Regelbetrieb der beiden Ebenen mit getrennten DUTs ist eine Umschaltbox nicht zwingend erforderlich, aber als Option für spezielle Vergleichstests sinnvoll vorzuhalten.

---

## 9. Zusammenfassung der Kernänderungen

1. **Rollentrennung in Ebene B**: Access-Port-Angreifer (aktiv, injiziert) getrennt vom Sniffer-PC (passiv, Mirror-Port) — behebt den zentralen technischen Fehler der Ursprungsversion.
2. **Rogue-Master-Fähigkeit** als eigener, realistisch bewerteter Machbarkeits-Baustein mit konkreten Tooling-Optionen (Scapy/pnio_dcp, ProFuzz, PROFINET Community Stack) statt impliziter Annahme, dass "Scapy einfach eine Verbindung aufbaut".
3. **Zwei-DUT-Strategie**: verhindert Zustandsverschmutzung und physische Degradation zwischen Testebenen.
4. **Sicherheitsvorkehrungen**: Dummy-Lasten, ferngesteuerte Power-Cycles, Switch-Backplane-Prüfung, fixierte Firmware-Baseline.
5. **Testsequenzplan** als eigenes, verbindliches Dokumentationsartefakt.
6. **Klare Empfehlung** zu den Umsteck-Optionen: Option 1 für HTTP/IoT-Core, Option 3 (Hardware-A/B-Switch) als methodisch sauberster Standard für Vergleichstests, Option 2 nur als dokumentierter Fallback.
