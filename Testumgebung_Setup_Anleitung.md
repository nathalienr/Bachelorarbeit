# Testumgebung – Setup-Anleitung

Physical IT/OT Interface Testbed für Safe Remote I/O (SRIO, AL400S/AL401S)

---

## 1. Komponentenübersicht

| # | Komponente | Spezifikation | Rolle |
|---|---|---|---|
| 1 | SRIO (DUT) | AL400S oder AL401S | Testobjekt |
| 2 | SPS (F-Host) | z. B. Siemens S7-1500F, CPU 1511F-1PN | Safety-Master, PROFIsafe-Verbindung |
| 3 | Engineering-Laptop | Windows 11, TIA Portal ≥ V17 | Projektierung/Parametrierung, I&M-Lesepfad |
| 4 | Managed Switch | 100BASE-TX, Port-Mirroring-fähig, Storm-Control-fähig | Netzwerkverteiler + Sniff-Port |
| 5 | Raspberry Pi 4 Model B | Kali Linux ARM64 | Angriffs-/Analyse-Host |
| 6 | USB3→Gigabit-Ethernet-Adapter | 2. NIC für Pi | **Erforderlich** für Inline-Bridge (TC-RQ001-04, siehe Abschnitt 11) |
| 7 | 2. SRIO-Gerät (Ersatzgerät) | baugleich | Für destruktive Tests (Siegel, Firmware) |
| 8 | 24V-DC-Netzteil | M12 L-codiert, männlich, ≥16A | Stromversorgung SRIO |
| 9 | 2× Patchkabel M12(D-codiert)↔RJ45 | Cat5e/6 | Feldbusanschluss SRIO↔Switch |
| 10 | Ethernet-Patchkabel RJ45↔RJ45 | Cat5e/6 | SPS↔Switch, Laptop↔Switch, Pi↔Switch |
| 11 | DI-Taster/Schalter + Kabel M12(A-codiert, 5-pol.) | ZVEI Typ A oder C | Stimulus für Sicherheits-Eingang |
| 12 | Last am DO (Lampe/Relais) + Kabel M12(A-codiert, 5-pol.) | – | Aktor am Sicherheitsausgang |
| 13 | USB-C-Netzteil | 5V/3A | Stromversorgung Pi |
| 14 | Micro-HDMI→HDMI-Kabel | 2× am Pi vorhanden | Standalone-Monitor |
| 15 | USB-Tastatur/-Maus | – | Standalone-Bedienung Pi |
| 16 | microSD-Karte | ≥ 32GB, Class 10 | Kali-Image für Pi |
| 17 | Multimeter | – | Physische Tests (Siegel/Kontinuität) |

---

## 2. Netzwerk-/IP-Adressplan

Alle Geräte im selben Subnetz, keine DHCP-Nutzung (feste IPs, damit Wireshark-Filter und Scapy-Skripte stabil bleiben).

| Gerät | IP-Adresse | Subnetzmaske | Anschluss am Switch |
|---|---|---|---|
| SPS (F-Host) | 172.18.87.1 | 255.255.192.0 | Port 1 |
| SRIO (DUT) | 172.18.87.2 | 255.255.192.0 | Port 2 |
| Engineering-Laptop | 172.18.87.10 | 255.255.192.0 | Port 3 |
| Kali-Pi (aktiv, Setup B) | 172.18.87.20 | 255.255.192.0 | Port 4 |
| Kali-Pi (passiv, Setup A) | ohne IP im Testnetz (nur Sniffing) | – | Mirror-Port (Port 5) |
| Kali-Pi Bridge `br0` (Setup B-Inline) | optional 172.18.87.21 nur zur Fernwartung | 255.255.192.0 | inline, siehe Abschnitt 11 |

**Hinweis zum Adressbereich:** Die Beispieladressen (172.18.87.x) sind direkt aus der ifm-IoT-Core-Dokumentation übernommen. 172.16.0.0/12 ist regulärer RFC1918-Bereich und kann mit dem Firmennetz kollidieren. Das Testnetz **muss physisch getrennt** vom Firmennetz betrieben werden (siehe Abschnitt 3). Falls unternehmensintern ein anderer Adressbereich vorgeschrieben ist, kann der Plan beliebig angepasst werden – wichtig ist nur die Konsistenz zwischen SPS-Projektierung (Abschnitt 5.2) und der hier verwendeten Adressierung.

---

## 3. Sicherheitsregeln (verbindlich)

Diese Regeln gelten für die gesamte Testkampagne, unabhängig vom aktiven Setup.

1. **Air-Gap:** Der Switch darf **keinen Uplink** zum Firmennetz haben. Vor Testbeginn physisch prüfen (Kabel am Switch zählen: nur die in Abschnitt 2 gelisteten Geräte dürfen angeschlossen sein).
2. **Kali-Pi Dual-Homing-Verbot:** Der Pi darf **nie gleichzeitig** mit Firmennetz und Testnetz verbunden sein. Vor dem Umstecken ins Testnetz Netzwerkkabel zum Firmennetz physisch trennen (siehe Abschnitt 10.2).
3. **Aktive/aggressive Tools** (bettercap, ettercap, hping3-Floods, boofuzz) ausschließlich im air-gapped Testnetz ausführen, nie mit aktiver zweiter Netzwerkverbindung.
4. **Destruktive Tests** (Siegel entfernen, Firmware-Korruption) ausschließlich am Ersatzgerät (Setup C), nie am primären Baseline-DUT.
5. **Firmware-Recovery-Image** (validierter Original-Container) vor jedem Firmware-Test lokal sichern (siehe Abschnitt 9.2).

---

## 4. Engineering-Laptop – Vorbereitung

### 4.1 Betriebssystem & Voraussetzungen
- Windows 11 (oder neuer)
- Administratorrechte für Installation erforderlich
- Netzwerkadapter mit freier Ethernet-Buchse (ggf. USB→Ethernet-Adapter)

### 4.2 TIA Portal installieren
1. TIA Portal Version 17 oder höher installieren.
2. Sicherstellen, dass die Software TCI (Tool Calling Interface) Version ≥ V1.1-MU1 unterstützt (Standard ab TIA Portal V17).
3. Firewall-Ausnahme für TIA Portal/PROFINET-Kommunikation (S7comm, DCP) aktivieren, falls Windows-Firewall aktiv ist.

### 4.3 GSD-Datei der SRIO importieren
1. GSD-Datei `GSDML-V2.yy-ifm-AL40xS-xxxxxxxx.xml` von ifm beziehen (liegt dem Gerät bei oder auf ifm-Website).
2. In TIA Portal: *Extras → Gerätebeschreibungsdateien (GSD) verwalten*.
3. Pfad zur GSD-Datei angeben → *Installieren*.
4. Nach Installation ist SRIO im Hardware-Katalog unter *Weitere Feldgeräte → PROFINET IO → I/O → ifm electronic* auffindbar.

### 4.4 ifm-CRC-Tool installieren
1. Installation erfordert Administratorrechte.
2. Das Tool läuft **nicht standalone**, sondern wird ausschließlich aus der PROFINET-Konfigurationssoftware heraus gestartet (Rechtsklick auf SRIO-Gerät in der Hardware-Konfiguration → *Device Tool starten*).
3. Nach Start erscheint Zertifikatsdialog → Zertifikat installieren, sonst lässt sich das Tool nicht öffnen.

### 4.5 Netzwerkkonfiguration Laptop
1. Netzwerkadapter → IPv4-Eigenschaften → feste IP `172.18.87.10 / 255.255.192.0` setzen (siehe Tabelle Abschnitt 2).
2. Kein Gateway, kein DNS nötig (isoliertes Testnetz).
3. Windows-Netzwerkprofil auf "Privat" setzen (nicht "Öffentlich"), sonst blockiert die Firewall ggf. DCP/S7comm.

---

## 5. SPS (F-Host) – Konfiguration

### 5.1 Hardware-Konfiguration in TIA Portal
1. Neues Projekt anlegen → CPU (z. B. CPU 1511F-1PN) einfügen, passende Firmware-Version wählen.
2. SRIO aus Hardware-Katalog (nach GSD-Import, siehe 4.3) per Drag & Drop auf die PROFINET-Linie der CPU ziehen.
3. Passendes DAP wählen (AL400S oder AL401S, siehe importierte GSD).

### 5.2 IP-Adresse der SPS setzen
1. SRIO/PROFINET-Gerät anklicken → *Eigenschaften → Ethernet-Adressen*.
2. IP-Adresse der CPU auf `172.18.87.1 / 255.255.192.0` setzen (siehe Abschnitt 2).
3. PROFINET-Gerätename der SRIO vergeben (wird per DCP zugewiesen, z. B. `srio-dut-01`).

### 5.3 PROFIsafe-Parameter setzen
1. Im Modul-Eigenschaftsdialog der SRIO → Reiter *F-Parameter*.
2. `F_Dest_Add` auf denselben Wert setzen, der später am Drehschalter der SRIO physisch eingestellt wird (Bereich 1–899).
3. `F_WD_Time` (Watchdog-Zeit) setzen, Default 150 ms, Minimum 50 ms.
4. `F_Source_Add` kann auf einen beliebigen Wert im Bereich 1–65534 bleiben (wird bei Address Type 1 nicht geprüft).
5. iParameter der einzelnen DI-/DO-Ports (Testpulse, Filterzeiten, Symmetrie) je nach gewünschtem Testszenario konfigurieren.
6. iPar-CRC über ifm-CRC-Tool erzeugen (siehe 4.4) und in Feld `F_iPar_CRC` eintragen:
   - ifm-CRC-Tool aus TIA Portal öffnen.
   - Angezeigte Parameterliste mit der in TIA Portal eingestellten Konfiguration vergleichen.
   - Bei Übereinstimmung: Checkbox "Ich habe alle Geräteparameter überprüft" aktivieren.
   - CRC wird berechnet, per "Copy to clipboard" übernehmen.
   - Wert in `F_iPar_CRC`-Feld in TIA Portal einfügen.
7. Projekt übersetzen (*Compile*) – Fehler bei Adress-/Parameterkonflikten hier bereinigen.

### 5.4 Projekt auf CPU laden
1. SPS per Ethernet-Kabel direkt oder über Switch mit Laptop verbinden.
2. *Laden in Gerät* → Zielgerät auswählen → Laden bestätigen.
3. CPU in RUN versetzen.

---

## 6. I&M-Daten auslesen (Lesepfad-Klarstellung)

`I&M0` (REVISION_COUNTER), `I&M4` (iParCRC/F_ParCRC-Signatur) und `I&M5` (Firmware-Annotation) sind **nicht** über IoT-Core abrufbar. Diese Daten ausschließlich über TIA Portal lesen:

1. Online-Verbindung zur CPU herstellen (*Online → Online gehen*).
2. SRIO-Modul in der Gerätesicht anklicken → *Online & Diagnose*.
3. Reiter *Allgemein → Kennungsdaten (I&M)* → I&M0/I&M4/I&M5 werden angezeigt.

IoT-Core (per Kali/Browser, siehe Abschnitt 10) liefert nur Firmware-Versionsstrings (`/deviceinfo/swrevision`, `/deviceinfo/swinfo/*`, `/firmware/version`), keine I&M0/I&M4-Rohdaten.

---

## 7. Managed Switch – Konfiguration

### 7.1 Grundkonfiguration
1. Switch per Konsolenkabel oder Web-UI (Werks-IP laut Handbuch) initial konfigurieren.
2. Management-IP außerhalb des Testsubnetzes legen (z. B. separates Management-VLAN), damit sie nicht mit den Testadressen kollidiert.
3. Auto-Negotiation auf allen Ports aktiv lassen (SRIO/PROFINET nutzt 100BASE-TX Vollduplex).
4. **Kein Uplink-Port aktiv beschalten** (Air-Gap, siehe Abschnitt 3).

### 7.2 Portbelegung festlegen

| Port | Gerät | Modus |
|---|---|---|
| 1 | SPS | Access, normales VLAN |
| 2 | SRIO | Access, normales VLAN |
| 3 | Engineering-Laptop | Access, normales VLAN |
| 4 | Kali-Pi (Setup B, aktiv, IP-Ebene) | Access, normales VLAN |
| 5 | Kali-Pi (Setup A, passiv) | Mirror-Ziel (siehe 7.3) |

Für Setup B-Inline (Abschnitt 11) wird die direkte Verbindung Switch↔SRIO an Port 2 vorübergehend aufgetrennt und durch die Pi-Bridge ersetzt – siehe Abschnitt 11.2.

### 7.3 Port-Mirroring (SPAN) einrichten
1. Im Switch-Menü *Port Mirroring* (Bezeichnung je Hersteller z. B. "SPAN", "RSPAN", "Traffic Mirroring") aufrufen.
2. Quell-Ports: Port 1 (SPS) und Port 2 (SRIO), Richtung *both/ingress+egress*.
3. Ziel-Port: Port 5 (Kali-Pi, Setup A).
4. Speichern/aktivieren, Mirroring-Funktion testen (auf Kali: `tcpdump -i eth0` sollte PROFINET-Frames zeigen, sobald SPS/SRIO kommunizieren).

**Einschränkung bei Flood-Tests (TC-RQ010-02):** Der Mirror-Port spiegelt beide Richtungen zweier 100-Mbit/s-Ports auf einen einzigen 100-Mbit/s-Zielport. Bei hoher Paketrate kann der Zielport überlastet werden → Frame-Verlust im Mitschnitt (PCAP-Evidenz unvollständig). Für Flood-/Fuzzing-Tests mit Beweispflicht stattdessen über die Inline-Bridge (Abschnitt 11) mitschneiden, oder den möglichen Frame-Verlust im Testprotokoll vermerken.

### 7.4 Storm-Control
Vor jedem Flood-Test (TC-RQ010-02) bewusst festlegen, ob Storm-Control (Broadcast-/Multicast-/Unicast-Sturmschutz) am Switch aktiv oder deaktiviert ist, und den Zustand im Testprotokoll dokumentieren (beeinflusst die Realitätsnähe des Testergebnisses).

---

## 8. SRIO (DUT) – Vorbereitung

### 8.1 Drehschalter (F-Adresse) einstellen
1. Gerät ist stromlos.
2. Drei Drehschalter unter der Kunststoff-/Metallsiegel-Hülse freilegen (nur bei Bedarf, sonst Siegel intakt lassen).
3. Zahlenwert entsprechend gewünschter F_Dest_Add einstellen (Wertebereich 1–899, Ziffern 0–9 je Schalter, Multiplikator 100/10/1).
4. Wert 000 = Auslieferungszustand, Wert 999 = Firmware-Update-Modus (siehe Abschnitt 9 für Update-Vorgang).
5. Adresse wird nur beim Boot/Init gelesen – Änderung im laufenden Betrieb wird erst nach Neustart wirksam.

### 8.2 Verkabelung
1. **Power In (M12, L-codiert, männlich):** 24V-DC-Netzteil anschließen.
   - Pin 1: L+ (US), Pin 3: L− (US), Pin 4: L+ (UA), Pin 2: L− (UA), Pin 5: FE.
2. **Fieldbus-Port 1 (M12, D-codiert, weiblich):** Patchkabel zu Switch-Port 2.
3. **Fieldbus-Port 2:** unbenutzt lassen (Daisy-Chain-Option, für Grundsetup nicht nötig).
4. **DI-Port (M12, A-codiert, 5-pol., weiblich):** Taster/Sensor anschließen.
   - Pin 1: L+/TSOut1, Pin 4: F-DI1, Pin 2: F-DI2, Pin 5: L+/TSOut2, Pin 3: L− (US).
5. **DO-Port (M12, A-codiert, 5-pol., weiblich):** Last (Lampe/Relais) anschließen.
   - Pin 4: F-DO1, Pin 2: F-DO2, Pin 3: L− (UA), Pin 5: FE.
6. Optional: DO-Ausgang zusätzlich auf einen freien Digitaleingang der SPS zurückführen (unabhängiges Readback für Testauswertung).

### 8.3 Erstinbetriebnahme
1. Netzteil einschalten.
2. LED-Zustand prüfen: RDY grün = Host-CPU läuft.
3. Bei erstem Verbindungsaufbau meldet sich SRIO per DCP im Netz – in TIA Portal über *Erreichbare Teilnehmer* suchen und Gerätename/IP zuweisen (siehe 5.2).
4. Nach erfolgreicher Parametrierung (Abschnitt 5.3) und Übertragung: P-LED wird statisch grün = sichere Kommunikation aktiv.

---

## 9. Firmware-Handling & Ersatzgerät (Setup C)

Betrifft TC-RQ005-03, TC-RQ005-04, TC-RQ008-03.

### 9.1 Legitimes Firmware-Image beschaffen
1. Aktuellen offiziellen SRIO Update Container (identisch zum Firmware-Stand des primären DUT) von ifm beziehen.
2. Datei-Hash (z. B. `sha256sum`) notieren, um später den validierten Ausgangszustand zweifelsfrei wiederherstellen zu können.

### 9.2 Recovery-Image sichern
Vor jedem Test mit modifizierter Firmware eine unveränderte Kopie des Update Containers an einem separaten Ort aufbewahren (nicht im gleichen Verzeichnis wie die zu modifizierende Kopie).

### 9.3 Modifiziertes Firmware-BLOB erzeugen
1. Kopie des Update Containers anlegen.
2. Mit Hex-Editor (z. B. `bless`, `ghex`, oder per Kommandozeile `xxd`/`dd`) ein einzelnes Byte im Anwendungsteil ändern.
3. Kein erneutes Signieren nötig – der Container ist laut Testkatalog (RQ-005, Gap G-2) unsigniert; eine Prüfung findet nicht statt.
4. Modifizierten Container über IoT-Core/Visualizer auf das Ersatzgerät hochladen (Update-Modus, Rotary = 999, siehe 8.1).

### 9.4 Recovery nach Test
1. Gerät verbleibt nach fehlgeschlagenem/absichtlich fehlerhaftem Update im Update-Zustand.
2. Validierten Original-Container (aus 9.2) erneut über IoT-Core/Visualizer hochladen.
3. Neustart (Power-Cycle) auslösen.
4. Hinweis: Bootloader von SCPU (µC1) und der Hardware-Bootloader von µC2 sind selbst nicht aktualisierbar und bleiben in jedem Fall erhalten – ein vollständiges Bricking des Ersatzgeräts ist bei diesem Ablauf nicht zu erwarten, ein erneuter Firmware-Upload bleibt möglich.

---

## 10. Raspberry Pi 4 + Kali Linux – Setup

### 10.1 Image erstellen
1. Aktuelles Kali-Linux-ARM64-Image für Raspberry Pi 4 herunterladen (offizielles Kali-ARM-Image).
2. Mit Raspberry Pi Imager oder `dd`/`balenaEtcher` auf microSD-Karte schreiben.
3. microSD in Pi einsetzen.

### 10.2 Erstkonfiguration
1. Pi per HDMI-Kabel, Tastatur, Maus und USB-C-Netzteil als Standalone-Rechner starten (siehe Abschnitt 1, Punkte 13–15).
2. Login mit Standard-Zugangsdaten, danach sofort Passwort ändern.
3. System aktualisieren, solange Pi noch am normalen Netz hängt (nicht im isolierten Testnetz):
   ```
   apt update && apt full-upgrade -y
   ```
4. Danach Netzwerkkabel zum normalen Netz **physisch abziehen**, bevor Pi ins isolierte Testnetz gehängt wird (Dual-Homing-Verbot, siehe Abschnitt 3).

### 10.3 Netzwerkkonfiguration (statische IP)
1. Netzwerk-Interface identifizieren (`ip a`, i. d. R. `eth0`).
2. Statische IP je nach Setup konfigurieren:
   - **Setup A (passiv, Mirror-Port):** keine IP nötig, Interface nur in *promiscuous mode* versetzen:
     ```
     ip link set eth0 promisc on
     ```
   - **Setup B (aktiv, regulärer Port, IP-Ebene):**
     ```
     ip addr add 172.18.87.20/18 dev eth0
     ip link set eth0 up
     ```
3. Für dauerhafte Konfiguration in `/etc/network/interfaces` oder NetworkManager-Profil eintragen.

### 10.4 Tools installieren/prüfen
Vorinstalliert bei Kali, sonst nachinstallieren:
```
apt install -y nmap wireshark tshark scapy hping3 ettercap-text-only bettercap zaproxy bridge-utils ebtables
```
PROFINET/DCP-fähige Erweiterung (für TC-RQ001-03, TC-RQ011-02, TC-RQ010-02/03):
```
python3 -c "from scapy.all import load_contrib; load_contrib('pnio'); load_contrib('pnio_rtc')"
pip install pnio-dcp
```
Verfügbarkeit vor Testbeginn prüfen (Import ohne Fehler, `pip show pnio-dcp`) – je nach Scapy-/Kali-Version kann der Funktionsumfang der Contrib-Module variieren.

Optional für Fuzzing:
```
pip install boofuzz
```
Vor Testbeginn Funktionsfähigkeit jedes Tools einmal isoliert prüfen (z. B. `nmap -V`, `scapy` interaktiv starten).

### 10.5 Standalone-Zubehör (laut Anweisung Vorgesetzter)
1. Micro-HDMI-Kabel in einen der beiden Micro-HDMI-Ports des Pi stecken, anderes Ende an Monitor.
2. USB-Tastatur/-Maus an USB-Ports.
3. USB-C-Netzteil (5V/3A) anschließen.
4. Zweck: Bedienung des Pi ohne Netzwerkzugriff von außen, damit das Test-Ethernet-Interface ausschließlich für Capture-/Angriffsverkehr reserviert bleibt und eine SSH-Sitzung nicht durch eigene Flood-/Fuzzing-Tests unterbrochen wird.

### 10.6 Reichweite von ARP-Spoofing (Klarstellung)
ARP-Spoofing (arpspoof/bettercap/ettercap) wirkt **ausschließlich auf IP-basierten Verkehr** (z. B. IoT-Core-HTTP-Sitzungen). PROFINET RT und die darin getunnelten PROFIsafe-Frames werden als eigener EtherType (0x8892) ohne IP-Adressierung übertragen und sind über ARP-Spoofing **nicht** umlenkbar. Für Tests, die eine echte Manipulation des zyklischen PROFINET/PROFIsafe-Datenstroms erfordern (insbesondere TC-RQ001-04, unterstützend auch TC-RQ011-03), ist zwingend die Inline-Bridge aus Abschnitt 11 nötig.

---

## 11. Transparente Inline-Bridge (Layer-2-MITM, für TC-RQ001-04)

Erforderlich für: TC-RQ001-04 (zwingend). Empfohlen für: TC-RQ011-03 (erhöht Erfolgswahrscheinlichkeit der Impersonation, da Suppression des legitimen Frames möglich).

### 11.1 Voraussetzung
- USB3→Gigabit-Ethernet-Adapter am Pi angeschlossen (2. Interface, i. d. R. `eth1`).
- Pakete `bridge-utils` und `ebtables` installiert (siehe 10.4).

### 11.2 Physischer Einbau
1. Patchkabel zwischen Switch-Port 2 und SRIO-Fieldbus-Port 1 abziehen.
2. Switch-Port 2 → Pi-Interface `eth0`.
3. Pi-Interface `eth1` (USB-Adapter) → SRIO-Fieldbus-Port 1.
4. Damit läuft der gesamte Verkehr zwischen Switch (und damit SPS) und SRIO physisch durch den Pi.

### 11.3 Bridge einrichten
```
ip link set eth0 down
ip link set eth1 down
brctl addbr br0
brctl addif br0 eth0
brctl addif br0 eth1
ip link set eth0 up
ip link set eth1 up
ip link set br0 up
```
Optional, nur zur Fernwartung des Pi über die Bridge (nicht für den Testverkehr nötig):
```
ip addr add 172.18.87.21/18 dev br0
```
Transparenter Betrieb (reines Durchreichen aller Frames, inkl. EtherType 0x8892) mit `tcpdump -i br0` verifizieren, bevor mit dem eigentlichen Test begonnen wird.

### 11.4 Selektives Unterdrücken/Ersetzen einzelner Frames
Für TC-RQ001-04 (Unterdrücken des legitimen Producers, Übernahme der Consecutive-Number) reicht die reine Bridge nicht aus – sie leitet standardmäßig alles transparent weiter. Für gezieltes Abfangen einzelner Frames vor der Weiterleitung:
```
ebtables -A FORWARD -i eth0 --nfqueue-num 0
```
und ein Python-Skript mit `NetfilterQueue`, das je Frame entscheidet: weiterleiten, verwerfen, oder durch ein präpariertes Scapy-Frame ersetzen. Die konkrete Filter-/Ersetzungslogik ist Teil des Testskripts für TC-RQ001-04 und wird dort dokumentiert, nicht in dieser Umgebungsbeschreibung.

### 11.5 Rückbau
Nach Abschluss der Inline-Tests Bridge auflösen und Original-Verkabelung (Switch-Port 2 direkt an SRIO) wiederherstellen, bevor mit Setup A/B weitergetestet wird:
```
ip link set br0 down
brctl delif br0 eth0
brctl delif br0 eth1
brctl delbr br0
```

---

## 12. Automatisiertes Health-Monitoring (für Flood-/Fuzzing-Tests)

Betrifft TC-RQ010-02, TC-RQ010-03 und andere aggressive Tests (boofuzz, hping3-Floods).

### 12.1 Zweck
Die DO→SPS-Rückführung (Abschnitt 8.2, Punkt 6) deckt nur den I/O-Zustand ab. Ein Absturz/Hänger von COM/IoT-Core wird davon nicht erfasst. Zusätzlich ein einfaches Poll-Skript mitlaufen lassen.

### 12.2 Poll-Skript (Beispiel)
Auf Kali oder einem dritten Host im Testnetz:
```bash
while true; do
  ts=$(date +%s)
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://172.18.87.2/deviceinfo)
  if [ "$code" != "200" ]; then
    echo "$ts UNREACHABLE (code=$code)" >> health.log
  fi
  sleep 1
done
```

### 12.3 Abbruchkriterium
Bei ≥ 5 aufeinanderfolgenden Fehlschlägen (≥ 5 Sekunden Nichterreichbarkeit): Test sofort stoppen, DUT stromlos schalten, 10 Sekunden warten, neu starten, anschließend SPS-Diagnosepuffer (*Online & Diagnose*) auf zusätzliche Fehlermeldungen prüfen.

---

## 13. Physischer Verkabelungsplan – Übersicht

```
                    ┌─────────────────────┐
                    │   Managed Switch     │
                    │  Port1 Port2 Port3   │
                    │  Port4 Port5(Mirror) │
                    └──┬────┬────┬────┬────┘
                       │    │    │    │
        ┌──────────────┘    │    │    └───────────────┐
        │                   │    │                    │
   ┌────┴────┐        ┌─────┴───┐│              ┌─────┴─────┐
   │   SPS    │        │  SRIO   ││              │Engineering│
   │ (F-Host) │RJ45    │ (DUT)   ││RJ45          │  Laptop   │
   └──────────┘        │M12(D)   ││              └───────────┘
                        └─────────┘│
                                   │RJ45 (Port4, Setup B)
                              ┌────┴─────┐
                              │ Kali-Pi  │
                              │(aktiv)   │
                              └──────────┘

   Port5 (Mirror) → separates Kabel zu 2. Netzwerk-Interface
   oder Umstecken des Kali-Pi-Kabels zwischen Port4/Port5
   je nach Testphase (Setup A = passiv / Setup B = aktiv)

   SRIO zusätzlich:
   - Power In (M12,L) ← 24V-DC-Netzteil
   - DI-Port (M12,A)  ← Taster/Sensor
   - DO-Port (M12,A)  → Last (Lampe/Relais) [+ optional Rückführung zu freiem SPS-DI]
```

**Abweichende Verkabelung für Setup B-Inline (TC-RQ001-04):**
```
   ┌─────────────┐        ┌──────────┐  eth1(USB)   ┌─────────┐
   │Switch Port2 │──eth0──│  Kali-Pi │──────────────│  SRIO   │
   └─────────────┘        │  (br0)   │RJ45→M12(D)   │M12(D)   │
                           └──────────┘              └─────────┘
   SPS-Verkabelung an Switch Port1 bleibt unverändert.
```

---

## 14. Umschaltung zwischen Setups

| Setup | Zweck | Kali-Pi-Anschluss | Aktion |
|---|---|---|---|
| A – Passiv | Baseline-Mitschnitt, Enumeration ohne Beeinflussung | Port 5 (Mirror) | Kali-Kabel an Mirror-Port, `promisc on`, kein IP-Traffic senden |
| B – Aktiv, IP-Ebene | HTTP/IoT-Core-Angriffe, DCP-Broadcasts (kein MITM nötig, da im gleichen Broadcast-Domain sichtbar) | Port 4 (regulär) | Kali-Kabel an Port 4, statische IP setzen, ARP-Spoofing/Tools starten – Wirkung nur auf IP-Verkehr (siehe 10.6) |
| B-Inline – Aktiv, L2-MITM | Manipulation des zyklischen PROFINET/PROFIsafe-Datenstroms (TC-RQ001-04, unterstützend TC-RQ011-03) | inline zwischen Switch Port 2 und SRIO | Bridge gemäß Abschnitt 11 aufbauen, nach Test zurückbauen |
| C – Physisch/Destruktiv | Siegel-Manipulation, Firmware-Korruption | – | **2. SRIO-Gerät** verwenden, nicht das Baseline-DUT (siehe Abschnitt 9) |

Wechsel zwischen A und B: nur Netzwerkkabel des Pi umstecken (Port 4 ↔ Port 5) und Netzwerkkonfiguration gemäß 10.3 anpassen.
Wechsel zu B-Inline: Setup A/B beenden, Kabel gemäß 11.2 umstecken, Bridge aufbauen, nach Test gemäß 11.5 zurückbauen.

---

## 15. Inbetriebnahme-Checkliste

- [ ] Air-Gap bestätigt: Switch hat keinen Uplink ins Firmennetz
- [ ] Alle IP-Adressen gemäß Abschnitt 2 vergeben und mit `ping` gegenseitig erreichbar
- [ ] GSD-Datei in TIA Portal importiert
- [ ] ifm-CRC-Tool installiert und einmal testweise gestartet
- [ ] SRIO-Drehschalter-Adresse = F_Dest_Add in TIA Portal identisch
- [ ] Projekt übersetzt und fehlerfrei auf SPS geladen, CPU in RUN
- [ ] P-LED an SRIO statisch grün (sichere Kommunikation aktiv)
- [ ] I&M-Lesepfad bekannt: I&M0/I&M4/I&M5 nur über TIA Portal, nicht über IoT-Core
- [ ] Port-Mirroring am Switch aktiv und mit `tcpdump` verifiziert
- [ ] Storm-Control-Einstellung für Flood-Tests festgelegt und dokumentiert
- [ ] Kali-Pi Tools installiert und einzeln getestet (inkl. PROFINET/DCP-Contrib-Module)
- [ ] Kali-Pi Dual-Homing-Regel eingehalten (physisch nur ein Netz gleichzeitig angeschlossen)
- [ ] Standalone-Zubehör am Pi funktionsfähig (Monitor, Tastatur, Maus)
- [ ] Inline-Bridge (br0) für TC-RQ001-04 aufgebaut und beidseitig mit `tcpdump`/Ping verifiziert
- [ ] 2. SRIO-Gerät (Ersatzgerät) bereitgestellt und eindeutig gekennzeichnet
- [ ] Validierter Original-Firmware-Container für Ersatzgerät gesichert (Recovery-Image, Hash notiert)
- [ ] Health-Monitoring-Skript vorbereitet, Abbruchkriterium festgelegt (vor Flood-/Fuzzing-Tests zu starten)
