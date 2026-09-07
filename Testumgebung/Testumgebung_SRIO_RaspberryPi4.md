# Testumgebung für Safe Remote I/O mit Raspberry Pi 4 Model B

## 1. Zweck und Abgrenzung

Diese Testumgebung dient zur Untersuchung eines Safe-Remote-I/O-Geräts vom Typ AL400S oder AL401S in einem isolierten PROFINET-/PROFIsafe-Labornetz.

---

## 2. Gesamtaufbau

Die Testumgebung besteht aus folgenden Hauptkomponenten:

1. Safe Remote I/O als Device Under Test
2. fehlersichere Siemens-SPS als PROFIsafe F-Host
3. Raspberry Pi 4 Model B als Test- und Netzwerkrechner
4. administrierbarer Ethernet-Switch mit Port-Mirroring
5. Engineering- und Aufzeichnungsrechner
6. 24-V-DC-Spannungsversorgung
7. sichere Ein- und Ausgangsbeschaltung
8. Ethernet-, Versorgungs- und I/O-Leitungen

### Logische Struktur

```text
Engineering-/Aufzeichnungsrechner
  - TIA Portal
  - Wireshark
           |
           | Spiegelport
           |
+---------------------------+
| Administrierbarer Switch  |
+---------------------------+
   |           |           |
   |           |           |
SPS/F-Host   SRIO/DUT   Raspberry Pi 4
192.168.0.1  192.168.0.2 192.168.0.100

Separate 24-V-DC-Versorgung:
  - SPS
  - SRIO US
  - SRIO UA
  - Sensoren und Lasten nach vorgesehener Beschaltung
```

Das Labornetz darf keine direkte Verbindung zum Unternehmensnetz oder zum Internet besitzen. Falls Dateien oder Softwarepakete übertragen werden müssen, erfolgt dies kontrolliert und getrennt vom laufenden Testnetz.

---

## 3. Komponenten

## 3.1 Safe Remote I/O

### Aufgabe

Das Safe Remote I/O ist das zu untersuchende Gerät und wird als Device Under Test, kurz DUT, bezeichnet. Es arbeitet als PROFINET IO Device und als PROFIsafe F-Device.

Es stellt zur Verfügung:

- sechs sichere Eingangsports mit jeweils zwei Eingangskanälen,
- zwei sichere Ausgangsports mit jeweils zwei Ausgangskanälen,
- zwei Ethernet-Feldbusanschlüsse,
- einen HTTP-basierten IoT-Core zur Anzeige von Geräteinformationen und Diagnosedaten,
- drei Drehschalter zur Einstellung der sicheren Adresse beziehungsweise des Update-Modus.

### Benötigt

- 24 V DC über eine PELV-Spannungsversorgung,
- getrennte Versorgungsdomänen US und UA,
- Ethernet-Verbindung zum PROFINET-Netz,
- eine konfigurierte sichere Adresse im Bereich 1 bis 899,
- eine zur Hardware passende GSDML-Datei im Engineering-Projekt,
- zugelassene M12-Leitungen und passende Stecker,
- eine definierte Ein- und Ausgangsbeschaltung.

### Versorgung

Das Gerät besitzt zwei galvanisch getrennte Versorgungsdomänen:

- **US:** Versorgung der internen Elektronik und der sicheren Eingänge beziehungsweise Sensorversorgung
- **UA:** Versorgung der sicheren Ausgänge beziehungsweise Aktoren

Die Nennspannung beträgt 24 V DC. Der spezifizierte Betriebsbereich liegt bei 19,2 V bis 30 V.

### Power-Anschluss

Der Power-Anschluss ist M12-L-codiert.

| Pin | Funktion |
|---:|---|
| 1 | L+ US |
| 2 | L- UA |
| 3 | L- US |
| 4 | L+ UA |
| 5 | Funktionserde FE |

Die Funktionserde wird entsprechend der Geräte- und Laborvorgaben angeschlossen. Die FE-Verbindung soll kurz ausgeführt werden.

### Sichere Adresse

Die drei Drehschalter werden wie folgt verwendet:

- `000`: Auslieferungszustand
- `001` bis `899`: sichere PROFIsafe-Adresse
- `900` bis `998`: reserviert
- `999`: Firmware-Update-Modus

Für den normalen Testbetrieb wird beispielsweise die Adresse `007` eingestellt. Dieselbe Adresse muss im SPS-Projekt als `F_Dest_Add` konfiguriert sein.

---

## 3.2 Fehlersichere Siemens-SPS

### Aufgabe

Die fehlersichere SPS ist der PROFINET IO Controller und der PROFIsafe F-Host. Sie:

- baut die PROFINET- und PROFIsafe-Verbindung zum DUT auf,
- überträgt die sichere Parametrierung,
- liest die sicheren Eingänge,
- steuert die sicheren Ausgänge,
- zeigt Diagnose-, Qualifier- und Passivierungszustände an,
- ermöglicht die Quittierung und Wiedereingliederung nach einer Passivierung.

### Geeignete Ausführung

Vorgesehen ist eine fehlersichere Siemens-SPS, beispielsweise eine S7-1500F. Für das Produkt ist insbesondere die Kommunikation mit einer CPU 1511F-1 PN vorgesehen.

### Benötigt

- eine F-fähige CPU,
- PROFINET-Schnittstelle,
- passendes 24-V-DC-Netzteil,
- TIA-Portal-Projekt mit Safety-Unterstützung,
- importierte GSDML-Datei des DUT,
- korrekt eingestellte Geräte-IP-Adresse,
- identische sichere Adresse in Projekt und DUT,
- freigegebenes Sicherheitsprogramm,
- Beobachtungs- oder Trace-Möglichkeit für Ein- und Ausgangszustände.

### Beispielkonfiguration

```text
SPS/F-Host
IP-Adresse: 192.168.0.1
Subnetzmaske: 255.255.255.0
Rolle: PROFINET IO Controller und PROFIsafe F-Host
```

---

## 3.3 Raspberry Pi 4 Model B

### Aufgabe

Der Raspberry Pi ist der kontrollierte Testrechner im Labornetz. Er kann abhängig vom Aufbau drei Rollen übernehmen:

1. **Teilnehmer am Testnetz** für Diagnose und Netzwerkbeobachtung
2. **Testquelle** für kontrollierte Netzwerkpakete oder Last
3. **In-Path-Gerät** zwischen SPS und DUT, wenn der Datenverkehr vollständig durch den Pi geführt werden muss

Der Raspberry Pi übernimmt keine Sicherheitsfunktion und darf nicht als Ersatz für SPS, Schutzgerät oder sichere Abschalteinrichtung verwendet werden.

### Hardware

Benötigt werden:

- Raspberry Pi 4 Model B,
- geeignetes USB-C-Netzteil,
- microSD-Karte mit ausreichender Kapazität,
- ein kurzes Ethernet-Patchkabel für den normalen Teilnehmerbetrieb,
- optional ein zweiter Ethernet-Adapter über USB 3.0 für In-Path-Aufbauten,
- optional eine Echtzeituhr oder externe Zeitquelle, wenn Zeitstempel unabhängig vom Netzwerk benötigt werden,
- ausreichend Kühlung für längere Last- oder Aufzeichnungsvorgänge.

### Netzwerkschnittstellen

Der Raspberry Pi 4 besitzt nur einen integrierten Ethernet-Port. Deshalb gilt:

- Für den normalen Anschluss an den Switch reicht `eth0`.
- Für eine transparente Position zwischen SPS und DUT wird ein zweiter USB-Ethernet-Adapter benötigt.
- Die zweite Schnittstelle erscheint typischerweise als `eth1` oder `enx...`. Die tatsächliche Bezeichnung muss vor dem Aufbau geprüft werden.

### Betriebssystem und Software

Geeignet ist ein aktuelles 64-Bit-Linux-System, beispielsweise Raspberry Pi OS oder eine ARM64-kompatible Kali-Linux-Installation.

Benötigte Softwaregruppen:

- Netzwerkverwaltung: `iproute2`
- Paketaufzeichnung: `tcpdump`
- Protokollanalyse: `tshark` oder Wireshark ohne grafische Oberfläche
- Netzwerkerkennung: `nmap`
- Paketverarbeitung: Python 3 und Scapy
- HTTP-Zugriff: `curl`
- optional Bridge-Verwaltung für In-Path-Betrieb
- SSH nur für die lokale Administration, sofern im isolierten Netz erforderlich

### Beispielkonfiguration im Teilnehmerbetrieb

```text
Raspberry Pi 4
Schnittstelle: eth0
IP-Adresse: 192.168.0.100
Subnetzmaske: 255.255.255.0
Standardgateway: nicht gesetzt
DNS-Server: nicht gesetzt
WLAN: deaktiviert
Bluetooth: deaktiviert, falls nicht benötigt
```

Das Fehlen von Standardgateway und DNS verhindert, dass der Pi versehentlich Daten aus dem isolierten Testnetz nach außen überträgt.

### In-Path-Betrieb

Für den In-Path-Betrieb benötigt der Pi zwei Ethernet-Schnittstellen:

```text
SPS  <---->  eth0 | Raspberry Pi | eth1  <---->  DUT
```

Die beiden Schnittstellen werden zu einer transparenten Layer-2-Bridge zusammengefasst. Die Bridge transportiert Ethernet-Frames zwischen SPS und DUT. Für die reine Weiterleitung ist auf den beiden physischen Ports keine IP-Adresse erforderlich.

Eine Management-IP darf nur dann auf der Bridge oder einer zusätzlichen separaten Schnittstelle liegen, wenn dadurch keine unbeabsichtigte Verbindung zwischen Testnetz und einem anderen Netz entsteht.

---

## 3.4 Administrierbarer Ethernet-Switch

### Aufgabe

Der Switch verbindet SPS, DUT und Raspberry Pi im gemeinsamen Ethernet-Segment. Zusätzlich stellt er einen Spiegelport für die passive Aufzeichnung bereit.

### Benötigte Funktionen

- mindestens vier 100-Mbit/s- oder Gigabit-Ethernet-Ports,
- Port-Mirroring beziehungsweise SPAN,
- Deaktivierung nicht benötigter Dienste,
- keine automatische Verbindung zu einem übergeordneten Netzwerk,
- optional VLAN-Unterstützung zur sauberen Trennung von Test- und Managementverkehr.

### Portbelegung

| Switch-Port | Angeschlossene Komponente | Funktion |
|---:|---|---|
| 1 | SPS | PROFINET/PROFIsafe F-Host |
| 2 | DUT | PROFINET/PROFIsafe F-Device |
| 3 | Raspberry Pi | Test- und Diagnoseknoten |
| 4 | Aufzeichnungsrechner | Spiegelport für Wireshark |

### Port-Mirroring

Beim Port-Mirroring kopiert der Switch den Datenverkehr der überwachten Ports auf den Spiegelport. Der Aufzeichnungsrechner kann den Verkehr dadurch passiv mitschneiden, ohne selbst aktiv an der Kommunikation teilzunehmen.

Für eine vollständige Beobachtung werden mindestens die Ports von SPS und DUT in beide Richtungen auf den Spiegelport gespiegelt. Der Spiegelport selbst darf nicht als normaler Kommunikationsport verwendet werden.

---

## 3.5 Engineering- und Aufzeichnungsrechner

### Aufgabe

Der Rechner übernimmt zwei Funktionen:

1. Engineering der SPS und des DUT
2. passive Aufzeichnung und Auswertung des Netzwerkverkehrs

Beide Funktionen können auf einem Rechner ausgeführt werden. Für eine klarere Trennung kann ein separater Aufzeichnungsrechner verwendet werden.

### Benötigt

- Ethernet-Schnittstelle für das Engineering-Netz,
- optional zweite Ethernet-Schnittstelle ausschließlich für den Spiegelport,
- TIA Portal mit Safety-Unterstützung,
- GSDML-Datei des DUT,
- Wireshark,
- ausreichend Speicherplatz für PCAPNG-Dateien,
- Möglichkeit zur Erstellung von Screenshots und zum Export der SPS-Diagnose.

### Mirror-Schnittstelle

Die Netzwerkkarte am Spiegelport erhält normalerweise:

- keine IP-Adresse,
- kein Standardgateway,
- keinen DNS-Server.

Sie dient ausschließlich zur passiven Aufzeichnung. Eine zweite Netzwerkkarte kann für das reguläre Engineering verwendet werden.

---

## 3.6 24-V-DC-Spannungsversorgung

### Aufgabe

Die Spannungsversorgung speist SPS, DUT und gegebenenfalls angeschlossene Sensoren oder Lasten.

### Benötigt

- 24-V-DC-PELV-Netzteil,
- ausreichende Stromreserve für SPS, DUT und I/O-Beschaltung,
- getrennte Absicherung der Versorgungszweige,
- klar beschriftete Leitungen für US und UA,
- sichere Abschaltmöglichkeit,
- geeignete Reihenklemmen oder Laborverteiler.

US und UA werden entsprechend der DUT-Belegung separat zum Gerät geführt. Auch wenn beide Domänen im Labor aus demselben Netzteil gespeist werden, müssen Verdrahtung, Absicherung und Rückleiter eindeutig getrennt bleiben.

---

## 3.7 Eingangs- und Ausgangsbeschaltung

### Sichere Eingänge

Die Eingangsports des DUT verwenden M12-A-codierte, fünfpolige Buchsen.

| Pin | Funktion |
|---:|---|
| 1 | L+ US beziehungsweise Testsignalversorgung 1 |
| 2 | F-DI2 |
| 3 | L- US |
| 4 | F-DI1 |
| 5 | L+ US beziehungsweise Testsignalversorgung 2 |

Für einen einfachen Laboraufbau werden geeignete sichere Sensoren oder definierte Schaltelemente verwendet. Die Beschaltung muss zur gewählten Eingangsparametrierung passen, insbesondere zu 1oo1, 1oo2, äquivalent, antivalent und zur Testpulsversorgung.

Externe Spannungen dürfen nicht direkt auf die DI-Pins eingespeist werden, wenn dies nicht ausdrücklich durch die vorgesehene Beschaltung erlaubt ist. Die Sensorversorgung erfolgt über die vorgesehenen DUT-Anschlüsse.

### Sichere Ausgänge

Die Ausgangsports verwenden ebenfalls M12-A-codierte, fünfpolige Buchsen.

Für PP-Schaltung:

| Pin | Funktion |
|---:|---|
| 1 | nicht belegt |
| 2 | F-DO2 |
| 3 | L- UA |
| 4 | F-DO1 |
| 5 | FE |

Für PM-Schaltung wird die Verdrahtung entsprechend der Geräteparametrierung und der Gerätedokumentation angepasst.

Als Lasten werden geeignete ohmsche Testlasten oder freigegebene Aktoren verwendet. Für die Zustandsrückmeldung kann ein Ausgang auf einen dafür vorgesehenen SPS-Eingang geführt werden. Dabei müssen Spannungsbereich, gemeinsame Bezugspotentiale und Eingangseigenschaften geprüft werden.

---

## 3.8 Ethernet- und Anschlussleitungen

Benötigt werden:

- geschirmte Ethernet-Leitungen für PROFINET,
- passende M12-Ethernet-Adapter oder Geräteanschlussleitungen,
- M12-L-codierte Versorgungsleitung für das DUT,
- M12-A-codierte Leitungen für sichere Ein- und Ausgänge,
- Standard-RJ45-Patchleitungen für Switch, Raspberry Pi und Rechner,
- optional USB-3.0-Ethernet-Adapter für den Raspberry Pi.

Die Ethernet-Schirmung wird entsprechend den Labor- und Geräteanforderungen an beiden Enden aufgelegt. Nicht benötigte Geräteports werden verschlossen oder unbeschaltet gelassen.

---

## 4. Netzwerkadressierung

Für den Grundaufbau wird ein isoliertes IPv4-Netz verwendet.

| Komponente | Beispieladresse | Funktion |
|---|---|---|
| SPS/F-Host | `192.168.0.1/24` | PROFINET IO Controller und PROFIsafe F-Host |
| SRIO/DUT | `192.168.0.2/24` | PROFINET IO Device und IoT-Core |
| Raspberry Pi | `192.168.0.100/24` | Test- und Diagnoseknoten |
| Engineering-Rechner | `192.168.0.10/24` | TIA Portal und Gerätezugriff |
| Mirror-NIC | keine IP-Adresse | passive Aufzeichnung |

Es wird kein Standardgateway eingetragen. Die tatsächlichen Adressen dürfen angepasst werden, müssen aber eindeutig sein und im selben Subnetz liegen.

PROFINET verwendet neben IPv4 auch Layer-2-Kommunikation. Daher müssen alle beteiligten Geräte im gleichen Ethernet-Broadcast-Domain liegen. Router zwischen SPS und DUT sind für den Grundaufbau nicht vorgesehen.

---

## 5. Aufbau der Testumgebung

## 5.1 Mechanischer Aufbau

1. DUT auf einer ebenen, festen Fläche montieren.
2. SPS, Spannungsversorgung, Switch und Klemmen berührungssicher anordnen.
3. Raspberry Pi und Engineering-Rechner außerhalb der 24-V-Verdrahtungszone platzieren.
4. Leitungen nach Funktion trennen und beschriften:
   - Ethernet
   - US
   - UA
   - sichere Eingänge
   - sichere Ausgänge
   - Funktionserde
5. Eine gut erreichbare Abschaltmöglichkeit für die 24-V-Versorgung vorsehen.

## 5.2 Elektrischer Aufbau

1. Spannungsversorgung ausgeschaltet lassen.
2. US, UA und FE nach Pinbelegung mit dem DUT verbinden.
3. SPS mit ihrer vorgesehenen Versorgung verbinden.
4. Eingangssensoren oder Schaltelemente anschließen.
5. Ausgangslasten anschließen.
6. Falls eine Ausgangsrücklesung verwendet wird, Verbindung zum vorgesehenen SPS-Eingang herstellen.
7. Verdrahtung, Polarität, Absicherung und Kurzschlussfreiheit prüfen.
8. Erst danach die 24-V-Versorgung einschalten.

## 5.3 Netzwerkaufbau im Normalbetrieb

1. SPS an Switch-Port 1 anschließen.
2. DUT an Switch-Port 2 anschließen.
3. Raspberry Pi über `eth0` an Switch-Port 3 anschließen.
4. Aufzeichnungsrechner an Switch-Port 4 anschließen.
5. Auf dem Switch Port 1 und Port 2 auf Port 4 spiegeln.
6. Dem Mirror-Interface keine IP-Konfiguration zuweisen.
7. Statische IP-Adressen für SPS, DUT, Pi und Engineering-Rechner konfigurieren.
8. WLAN und weitere externe Netzverbindungen am Raspberry Pi während des Tests deaktivieren.

## 5.4 SPS- und DUT-Konfiguration

1. GSDML-Datei des DUT in TIA Portal importieren.
2. DUT in die PROFINET-Konfiguration aufnehmen.
3. PROFINET-Gerätename und IP-Adresse zuweisen.
4. Sichere Adresse am DUT über die Drehschalter einstellen.
5. Dieselbe Adresse als `F_Dest_Add` im Projekt eintragen.
6. F-Watchdog-Zeit und I/O-Parametrierung festlegen.
7. Sicherheitsprogramm erzeugen, prüfen und laden.
8. SPS in RUN setzen.
9. Prüfen, ob PROFINET und PROFIsafe verbunden sind.
10. Qualifier, Eingänge, Ausgänge und Geräte-LEDs kontrollieren.

## 5.5 Raspberry-Pi-Grundkonfiguration

1. 64-Bit-Betriebssystem auf die microSD-Karte installieren.
2. Eindeutigen Hostnamen vergeben, zum Beispiel `srio-test-pi`.
3. Für `eth0` die statische Adresse `192.168.0.100/24` setzen.
4. Kein Gateway und keinen DNS-Server konfigurieren.
5. WLAN und Bluetooth deaktivieren, sofern sie nicht benötigt werden.
6. Systemzeit vor Beginn der Aufzeichnung einstellen.
7. Benötigte Test- und Aufzeichnungsprogramme installieren.
8. Schreibrechte und Speicherort für Ergebnisdateien festlegen.
9. Den Pi über `eth0` mit dem Test-Switch verbinden.
10. Erreichbarkeit von SPS und DUT prüfen, ohne die laufende sichere Kommunikation zu verändern.

## 5.6 Umbau auf In-Path-Betrieb

Der In-Path-Aufbau wird nur verwendet, wenn der gesamte Datenverkehr zwischen SPS und DUT über den Raspberry Pi laufen muss.

1. Test stoppen und Anlage in einen sicheren, spannungsfreien beziehungsweise passivierten Zustand bringen.
2. Zweiten USB-Ethernet-Adapter am Raspberry Pi anschließen.
3. SPS direkt mit der ersten Pi-Schnittstelle verbinden.
4. DUT direkt mit der zweiten Pi-Schnittstelle verbinden.
5. Beide Pi-Schnittstellen zu einer transparenten Bridge zusammenfassen.
6. IP-Adressen von den physischen Bridge-Ports entfernen.
7. Prüfen, ob normale PROFINET-/PROFIsafe-Kommunikation durch die Bridge möglich ist.
8. Aufzeichnung weiterhin über den gespiegelten Switchpfad oder direkt auf dem Pi durchführen.

Der In-Path-Aufbau muss nach jeder Änderung zunächst im unveränderten Weiterleitungsbetrieb geprüft werden. Erst wenn SPS und DUT stabil kommunizieren, darf dieser Aufbau für weitere Untersuchungen verwendet werden.

---

## 6. Funktion der Kommunikationswege

## 6.1 PROFINET

PROFINET übernimmt die industrielle Kommunikation zwischen SPS und DUT. Die SPS ist Controller, das DUT ist Device. Über PROFINET werden Konfiguration, Diagnose, azyklische Daten und zyklische Prozessdaten transportiert.

## 6.2 PROFIsafe

PROFIsafe überträgt die sicherheitsbezogenen Prozessdaten innerhalb der PROFINET-Kommunikation. Die SPS ist F-Host, das DUT ist F-Device. Die sichere Kommunikation verwendet unter anderem:

- sichere Zieladresse,
- fortlaufende Sequenzinformation,
- Watchdog-Zeit,
- vier Byte lange CRC,
- Qualifier für die Gültigkeit der Prozessdaten.

Bei ungültiger oder ausbleibender sicherer Kommunikation geht das DUT in den vorgesehenen sicheren Zustand. Die sicheren Ausgänge werden dabei Low geschaltet.

## 6.3 IoT-Core

Der IoT-Core ist die HTTP-basierte Informations- und Serviceschnittstelle des DUT. Er stellt unter anderem bereit:

- Geräteinformationen,
- Software- und Bootloader-Versionen,
- Betriebszustand,
- Netzwerkparameter,
- Ein- und Ausgangszustände,
- Qualifier,
- Fehlerprotokoll,
- System-Uptime,
- Firmware-Update-Funktionen im Update-Zustand.

Die Schnittstelle verwendet HTTP und kein HTTPS. Der Zugriff erfolgt deshalb nur innerhalb des isolierten Labornetzes.

## 6.4 Port-Mirroring

Port-Mirroring erzeugt eine Kopie des relevanten Switch-Verkehrs. Dadurch kann der Aufzeichnungsrechner die Kommunikation passiv erfassen. Er beeinflusst die ursprünglichen Ethernet-Frames nicht und benötigt am Mirror-Interface keine IP-Adresse.

## 6.5 Raspberry-Pi-Bridge

Die Bridge verbindet zwei Ethernet-Schnittstellen auf Layer 2. Frames von der SPS werden an das DUT weitergeleitet und umgekehrt. Der Pi befindet sich dadurch physisch im Kommunikationspfad. Ohne zusätzliche Verarbeitung verhält sich die Bridge wie ein transparenter Zwe-port-Switch.

---

## 7. Erforderliche Grundzustände

Vor der Nutzung der Testumgebung müssen folgende Zustände erreicht sein:

- DUT ist korrekt mit US, UA und FE versorgt.
- SPS befindet sich in RUN.
- PROFINET-Verbindung ist aufgebaut.
- PROFIsafe-Verbindung ist aufgebaut.
- Sichere Adresse am DUT stimmt mit der Projektierung überein.
- Sichere Ein- und Ausgänge sind korrekt parametriert.
- Qualifier der verwendeten Kanäle sind im Normalbetrieb gültig.
- Ausgangslasten befinden sich in einem definierten Zustand.
- Raspberry Pi ist nur mit dem isolierten Testnetz verbunden.
- Port-Mirroring liefert Daten an den Aufzeichnungsrechner.
- Alle Geräte verwenden eine nachvollziehbare Zeitbasis für Aufzeichnungen.

---

## 8. Benötigte Unterlagen und Dateien

Für den Aufbau werden benötigt:

- Gerätehandbuch und Safety Manual des AL400S oder AL401S,
- aktuelle, zum DUT passende GSDML-Datei,
- TIA-Portal-Projekt mit Safety-Konfiguration,
- Dokumentation der SPS-Hardware,
- Pinbelegungen für Power, F-DI und F-DO,
- Freigabe beziehungsweise Laborvorgaben für Sensoren und Ausgangslasten,
- Netzplan mit IP-Adressen und Switch-Ports,
- dokumentierte Version des Raspberry-Pi-Betriebssystems und der installierten Werkzeuge.

---

## 9. Kompakte Materialliste

### Pflichtkomponenten

- 1 × Safe Remote I/O AL400S oder AL401S
- 1 × Siemens F-CPU, bevorzugt S7-1500F beziehungsweise CPU 1511F-1 PN
- 1 × Raspberry Pi 4 Model B
- 1 × microSD-Karte
- 1 × USB-C-Netzteil für den Raspberry Pi
- 1 × administrierbarer Ethernet-Switch mit Port-Mirroring
- 1 × Engineering-/Aufzeichnungsrechner
- 1 × 24-V-DC-PELV-Spannungsversorgung
- M12-L-codierte Power-Leitung
- M12-A-codierte I/O-Leitungen
- geeignete PROFINET-/Ethernet-Leitungen
- geeignete Sensoren, Schaltelemente und Ausgangslasten
- Absicherung, Klemmen, FE-Verbindung und Beschriftungsmaterial

### Zusätzlich für In-Path-Betrieb

- 1 × USB-3.0-Ethernet-Adapter für den Raspberry Pi
- 2 × zusätzliche Ethernet-Patchleitungen

### Empfohlene Zusatzausstattung

- separate Netzwerkkarte für den Mirror-Port
- schaltbare 24-V-Versorgung oder Labor-Hauptschalter
- ausreichend Speicher für PCAPNG- und Logdateien
- serieller Konsolenzugriff auf den Raspberry Pi
- Kühlkörper oder Lüfter für den Raspberry Pi
