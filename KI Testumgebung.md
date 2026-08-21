Testumgebung: Standalone-PC vs. isoliertes VLAN

Ja, das ist der logische nächste Schritt – bevor du CM-001 bis CM-014 tatsächlich ausführst, muss die Testumgebung als Kapitel in deiner Methodik stehen (analog zu NIST SP 800-115, Abschnitt 6.4 "Assessment Logistics", und den Environment-Regeln aus eurem eigenen Kali-Framework:"Run all tests only in the approved test environment... never against production systems").

Lass mich zunächst analysieren, was das SRIO überhaupt von einer Testumgebung braucht, bevor ich die beiden Ansätze gegenüberstelle.

Was die Testumgebung leisten muss

Das SRIO ist kein einfaches "Gerät mit einem Ethernet-Port" – es hat spezifische Anforderungen, die die Topologie-Entscheidung direkt beeinflussen:

Anforderung	Konsequenz für TopologieMuss in den State "Operate" wechseln, um viele Tests (RQ-008, 009, 010) sinnvoll durchzuführen	Braucht einen PROFINET/PROFIsafe F-Host (echte SPS oder Simulator), sonst bleibt es in "Parametrization"
2 physische Fieldbus-Ports (M12, D-coded)	Ermöglicht/erfordert zwei unterschiedliche Netzsegmente gleichzeitig anzuschließen
RQ-001-Gap: Annahme "used in a safe zone behind a firewall" (SRIO-9402)	Dieser Gap ist nur mit zwei getrennten Zonen empirisch prüfbar – ein einzelner PC kann das nicht simulieren
RQ-011: DCP-Reset auf Layer 2, cross-segment-Frage	Braucht ebenfalls zwei Segmente ("Zone A → Zone B", exakt wie CM-002 in eurem eigenen Framework)
Debug/Prog-Interface (SRIO-8628), Rotary-/DIL-Switches	Physischer Zugriff, unabhängig von Netzwerktopologie
Passives Mitschneiden (Wireshark) parallel zu aktivem Testing (Scapy/boofuzz)	Idealerweise getrennte Rollen (nicht ein Interface für alles)

Kernerkenntnis: Ein reiner Single-PC-Ansatz kann die in deiner eigenen Tabelle geforderten Multi-Zonen-Tests (RQ-001, RQ-011) strukturell nicht abbilden – dafür brauchst du mindestens zwei logisch getrennte Netzsegmente gleichzeitig.

Option A: Standalone-Rechner ("Stand von '98")

Damit meinst du vermutlich: ein einzelner, physisch isolierter Rechner, per Direktkabel mit dem SRIO verbunden, ohne Internet, ohne Switch, ohne VLAN – der klassische Air-Gap-Ansatz aus der Zeit, als "Netzwerksicherheit" noch gleichbedeutend mit "Kabel raus" war.

Vorteile:

Maximal einfache, unangreifbare Isolation – kein Restrisiko durch Fehlkonfiguration einer Netzwerkkomponente
Kein Switch/Router als zusätzliche, im Testbericht zu rechtfertigende Komponente in der Trusted Computing Base
Für die rein passiven/lesenden Tests (RQ-004, 006, 009-Web, 013, 014 – dein "Web/API-Block") völlig ausreichend
Historisch das, was NIST 800-115 als einfachstes "external test system" beschreibt (Laptop mit Toolkit)

Grenzen (entscheidend für dein Vorhaben):

Kann RQ-001 und RQ-011 nicht abbilden – es gibt keine "zweite Zone", von der aus du den Cross-Segment-Zugriff testen könntest
Keine gleichzeitige F-Host-Simulation und Angreifer-Perspektive und passives Mitschneiden ohne mehrere NICs oder mehrere Rechner – dann bist du faktisch schon bei einer Mini-Topologie, nur unstrukturiert
Schlecht reproduzierbar/dokumentierbar für eine Bachelorarbeit (kein sauberes Netzwerkdiagramm, keine IP-/VLAN-Tabelle, die du im Methodik-Kapitel referenzieren kannst)
Wenn du später Reviewer/Prüfer überzeugen willst, dass die "safe zone behind a firewall"-Annahme (SRIO-9402) tatsächlich geprüft wurde, brauchst du einen nachvollziehbaren Beleg für zwei Zonen – "ein Kabel" reicht dafür nicht als Nachweis

Fazit: Als alleinige Umgebung nicht ausreichend, aber als eine Rolle innerhalb einer größeren Topologie weiterhin sinnvoll (z. B. als isolierte Angreifer-Maschine).

Option B: Isoliertes VLAN

Ein Managed Switch, auf dem mehrere VLANs eingerichtet sind – aber der Switch selbst hat keinen Uplink zu irgendeinem anderen Netz (kein Trunk zur Firmen-IT, kein Internet-Gateway). Das ist wichtig: Es handelt sich nicht um "ein Segment in einem großen Netz", sondern um eine komplett abgeschottete Netzinsel, die intern logisch segmentiert ist.

Vorteile:

Bildet exakt das ab, was ihr in eurem eigenen Kali-Framework unter CM-002 ("Zone A → Zone B") testet – du kannst RQ-001 und RQ-011 damit tatsächlich empirisch validieren, statt nur zu dokumentieren, dass die Annahme unbelegt ist
Ermöglicht SPAN/Port-Mirroring für passives Wireshark-Sniffing, ohne den aktiven Pfad (Scapy, boofuzz) zu stören
Mehrere Rollen gleichzeitig möglich: F-Host-Simulator (PLC oder Software-Stack), SRIO (DUT), Kali-Angreifer-VM, Monitoring-Host – jede Rolle bekommt ihre eigene VLAN-Zuordnung
Sauber dokumentierbar: VLAN-ID-Tabelle, IP-Schema, Netzplan – genau das, was NIST 800-115 unter "Assessment Logistics" fordert
Reduziert Hardware-Bedarf durch Virtualisierung: die einzelnen Rollen können VMs auf einem einzigen physischen Host sein, der Host selbst bleibt komplett air-gapped vom Rest der Welt

Zu beachten/Risiken:

Der Switch selbst wird Teil der Testumgebung und muss im Bericht mitgedacht werden (Firmware-Stand, keine versehentliche Trunk-Konfiguration, die VLANs "durchlässig" macht)
Reine VLAN-Trennung auf einem einzigen physischen Switch ist eine logische, keine physische Isolation – für eine Bachelorarbeit i. d. R. ausreichend zu rechtfertigen, sollte aber explizit benannt werden, damit niemand "physische Trennung" unterstellt, wo nur logische vorliegt
Empfehlung: Hybrid-Ansatz

Nimm nicht "entweder/oder", sondern kombiniere beide Prinzipien zu einer physisch komplett abgeschotteten, aber intern segmentierten Testinsel:

┌─────────────────────────────────────────────────────────┐
│  ISOLIERTE TESTINSEL — kein Uplink zu Firma/Internet     │
│                                                            │
│   Managed Switch (VLAN-fähig, kein Trunk nach außen)     │
│                                                            │
│   VLAN 10 „Feldbus-Zone“         VLAN 20 „Angreifer-Zone“│
│   ┌──────────────┐                ┌──────────────┐       │
│   │ F-Host /     │◄──Port 1──┐    │ Kali-VM      │       │
│   │ PLC-Simulator│           │    │ (Scapy,      │       │
│   │ (PROFINET/   │           │    │ Nmap, ZAP,   │       │
│   │ PROFIsafe)   │           │    │ boofuzz)     │       │
│   └──────────────┘           │    └──────────────┘       │
│                                │                           │
│                          ┌─────▼─────┐                    │
│                          │  SRIO     │◄──Port 2──┐        │
│                          │  (DUT)    │            │        │
│                          └───────────┘            │        │
│                                                     ▼        │
│                          SPAN-Port ──► Monitoring-Host       │
│                                        (Wireshark, passiv)   │
│                                                            │
│   Physisch getrennt:  Debug-Bench (JTAG/UART, Rotary/DIL) │
└─────────────────────────────────────────────────────────┘


Warum das funktioniert:

Der äußere Rahmen (kein Uplink nach außen) gibt dir die Sicherheitsgarantie des Standalone-Ansatzes – "Stand von '98"-Prinzip, aber für die gesamte Insel statt für einen einzelnen PC
Die interne VLAN-Struktur gibt dir die Testfähigkeit für RQ-001/RQ-011, weil du echte Zonenübergänge produzieren kannst (Port 1 des SRIO in VLAN 10, Port 2 in VLAN 20 – oder beide Ports zunächst in derselben Zone, dann gezielt in getrennte, um den Unterschied zu zeigen)
SPAN-Port trennt sauber "passiv beobachten" von "aktiv angreifen" – wichtig, damit deine Wireshark-Captures nicht durch dieselbe Maschine laufen, die gerade Scapy-Frames einspeist (Nachvollziehbarkeit für die Thesis)
Debug-Bench (JTAG/UART, Rotary-/DIL-Switch-Zugriff) bleibt bewusst physisch getrennt von der Netzwerktopologie, weil das laut deiner Prioritätenliste ohnehin ein eigener Testblock ist

Praktisch reduzierbar auf wenig Hardware: F-Host-Simulator, Kali-Angreifer und Monitoring-Host können als VMs auf einem einzigen Host-PC laufen (der Host hat dann 2–3 virtuelle NICs, die an die jeweiligen VLAN-Ports des physischen Switches gebunden sind) – du brauchst also nicht zwingend vier Rechner, sondern einen leistungsfähigen Host + Switch + SRIO. Das entspricht dem, was NIST 800-115 unter "VM images... more versatile... favorable option for test teams" empfiehlt.

Für dein Methodik-Kapitel: was du dokumentieren solltest
Netzplan (wie oben) mit VLAN-IDs und IP-Schema
Begründung der Isolation (kein Uplink = kein Risiko für Produktivsysteme, referenziert auf NIST 800-115 6.4.2 "Location Selection")
Rollenverteilung (F-Host-Simulator, DUT, Angreifer, Monitor) und welche Tools auf welcher Rolle laufen
Begründung, warum VLAN statt reinem Air-Gap – nämlich weil RQ-001/RQ-011 sonst nicht testbar wären
Ein Verweis auf euer eigenes CM-002 als internes Präzedenzbeispiel für genau diese Testtopologie

Soll ich dir das Diagramm oben als sauberes Grafik-Asset für deine Thesis erzeugen, oder brauchst du eher eine tabellarische VLAN-/IP-Zuordnungsvorlage zum direkten Einfügen?
------------------------------------------------------------
Der hybride Testumgebungs-Ansatz – ausführliche Erläuterung

Ich gehe das systematisch durch: zunächst das Grundprinzip, dann jede Komponente einzeln, dann die konkrete Nutzung für deine priorisierten Testfälle, und zum Schluss die Aspekte, die du für dein Methodik-Kapitel brauchst (Reversibilität, Dokumentierbarkeit, Restrisiken).

1. Das Grundprinzip: zwei Isolationsebenen, nicht eine

Der Kern der Idee ist, zwei unabhängige Sicherheitsmechanismen zu stapeln, statt dich auf einen zu verlassen:

Äußere Isolation (der "Stand-von-98"-Gedanke): Die gesamte Testumgebung hat keinerlei physische Verbindung nach außen – kein Kabel zur Firmen-IT, kein WLAN, kein Internet-Gateway. Das ist die Garantie, dass egal was innerhalb der Umgebung passiert (Fuzzing-Crash, versehentlicher Broadcast-Sturm, kompromittierte VM), nichts nach außen dringen kann.
Innere Segmentierung (der VLAN-Gedanke): Innerhalb dieser abgeschotteten Insel schaffst du trotzdem mehrere logisch getrennte Zonen, weil du sonst die Zonenübergangs-Tests (RQ-001, RQ-011) gar nicht durchführen könntest – ein Air-Gap ohne interne Struktur ist ja nur "ein Kabel", das simuliert keine Netzwerktopologie.

Der entscheidende Denkfehler, den man vermeiden muss: Diese beiden Ebenen dürfen nicht miteinander verwechselt werden. Die VLAN-Trennung schützt nicht vor der Außenwelt (das tut die physische Abschottung), und die physische Abschottung schützt nicht die Zonen voneinander (das tut die VLAN-Konfiguration). Beide haben unterschiedliche Aufgaben.

2. Die vier Rollen im Detail
Rolle A: F-Host-Simulator (PROFINET/PROFIsafe-Master)

Das SRIO ist als PROFIsafe F-Slave konzipiert und bleibt ohne einen ansprechenden F-Host im State "Parametrization" hängen – für alle Tests, die den State "Operate" voraussetzen (RQ-008, RQ-009, RQ-010, Teile von RQ-011), brauchst du zwingend einen Kommunikationspartner.

Zwei Realisierungsmöglichkeiten:

Echte SPS (z. B. Siemens S7-1500F mit PROFIsafe-fähiger CPU) – am nächsten an der Realität, aber teurer und weniger flexibel für gezielte Protokollverletzungen
Software-Simulator (z. B. ein PROFINET-Stack unter Linux mit p-net oder einer kommerziellen Konformitätstest-Suite) – flexibler, weil du auch bewusst fehlerhafte oder grenzwertige F-Host-Antworten erzeugen kannst, was für manche deiner Tests (z. B. Verhalten bei Watchdog-Timeout, RQ-010) sogar nötig ist

Für deine Zwecke würde ich die Software-Variante empfehlen, weil sie dir erlaubt, den F-Host selbst als Testwerkzeug einzusetzen (z. B. bewusstes Aussetzen von Frames, um F_WD_Time-Verhalten zu prüfen), ohne eine reale SPS zu manipulieren.

Rolle B: Device Under Test (SRIO, AL400S/AL401S)

Das physische Gerät selbst. Hier ist wichtig: Das SRIO hat zwei physische Fieldbus-Ports (M12, D-coded, weil Daisy-Chaining vorgesehen ist) plus einen Rotary-/DIL-Switch-Block und ein Debug-Interface (SRIO-2580, SRIO-8628). Diese physischen Anschlusspunkte bestimmen, wie viele Kabel du überhaupt zur Verfügung hast, um Zonen zu bilden.

Rolle C: Angreifer-Instanz (Kali-VM)

Das ist die Instanz, von der aus die aktiven Tests laufen (Scapy, Nmap, Hydra, ZAP, boofuzz – dein bereits definiertes Kali-Toolset). Sie sollte virtualisiert sein, aus einem einfachen Grund: Du willst nach jedem potenziell destruktiven Test (Fuzzing, CRC-Kollisionsversuch) einen sauberen, reproduzierbaren Ausgangszustand herstellen können – das geht mit einem VM-Snapshot in Sekunden, mit einer physischen Neuinstallation nicht.

Rolle D: Monitoring-Host (passiv)

Eine separate Instanz, die ausschließlich mitschneidet (Wireshark, tcpdump), aber selbst niemals aktiv Pakete sendet. Diese Trennung ist kein Luxus, sondern methodisch wichtig: Wenn dieselbe Maschine gleichzeitig angreift und mitschneidet, vermischt sich in deinen Captures der von dir erzeugte Traffic mit dem, was du eigentlich beobachten willst (z. B. das Verhalten des SRIO als Reaktion auf den Angriff). Für eine saubere, in der Thesis zitierfähige Beweisführung ("Wireshark zeigt X") solltest du diese Rollen sauber trennen können.

3. Physisch vs. virtuell – was wird wie realisiert

Hier die praktische Reduktion, damit du nicht vier Rechner kaufen musst:

Rolle	Realisierung	WarumF-Host-Simulator	VM auf Host-PC	Muss reproduzierbar konfigurierbar sein
Kali-Angreifer	VM auf Host-PC	Snapshot-Fähigkeit essenziell
Monitoring-Host	VM auf Host-PC oder separates Mini-Gerät	Wenn VM: eigene virtuelle NIC am SPAN-Port
SRIO (DUT)	Physisch, keine Alternative	Ist das reale Testobjekt
Managed Switch	Physisch, keine Alternative	VLAN-Trennung ist Hardware-/Firmware-Funktion
Debug-Bench	Physisch, separat	JTAG/UART/Rotary-Zugriff geht nicht virtuell

Ein einziger, ausreichend leistungsfähiger Host-PC mit einem Hypervisor (z. B. VirtualBox, VMware Workstation oder – sauberer für Netzwerktests – Proxmox/ESXi) und mehreren physischen Netzwerkkarten (oder einer Karte mit mehreren Ports) genügt für die drei virtuellen Rollen. Jede VM bekommt eine eigene virtuelle NIC, die 1:1 an einen physischen Port des Host-PCs gebunden ist (kein virtueller Switch innerhalb des Hypervisors dazwischen, sonst untergräbst du die spätere VLAN-Kontrolle des physischen Switches).

4. Das VLAN-Design im Detail

Konkreter Vorschlag für dein Setup:

VLAN-ID	Name	Enthält	Zweck10	Feldbus-Zone	F-Host-Simulator, SRIO-Port 1	Simuliert die "vertrauenswürdige" Automatisierungszelle
20	Angreifer-Zone	Kali-VM	Simuliert einen potenziellen Angreifer, der sich Netzwerkzugriff verschafft hat (z. B. über einen kompromittierten Laptop im selben Segment)
30	Management/Monitoring	Monitoring-Host	Getrennt, damit der SPAN-Traffic nicht mit Testtraffic kollidiert
99	Physisch nicht belegt / totes VLAN	(leer, ggf. für ungenutzte Switch-Ports)	Best Practice, um versehentliche Auto-Negotiation in ein aktives VLAN zu verhindern

Der SRIO-Port 2 wird je nach Testfall unterschiedlich verkabelt – das ist der eigentliche Clou dieser Topologie:

Für Tests, die den Normalzustand abbilden (Baseline für RQ-004, 006, 007, 009, 013, 014): Port 2 bleibt frei oder wird ebenfalls an VLAN 10 gehängt (Daisy-Chain-Simulation).
Für RQ-001 (Prüfung der Firewall-Annahme "safe zone behind a firewall"): Du verkabelst Port 2 testweise so, dass er in VLAN 20 hängt, und prüfst, ob von der Angreifer-Zone aus tatsächlich unerwartete Dienste/Ports auf dem SRIO erreichbar sind, obwohl die Dokumentation eine Firewall zwischen den Zonen voraussetzt.
Für RQ-011 (DCP-Reset über Cross-Segment): Du platzierst die Kali-VM bewusst in VLAN 20, richtest auf dem Switch eine (eigentlich nicht vorgesehene) Layer-2-Verbindung zu VLAN 10 ein oder prüfst, ob DCP-Broadcast-Frames trotz VLAN-Trennung durchkommen – das bildet exakt euer eigenes CM-002-Szenario ab ("Zone A → Zone B, Cross-Segment-Exposure").

Wichtig für die Sauberkeit deiner Ergebnisse: Diese Zonenverschiebung machst du nicht permanent, sondern gezielt pro Testlauf, mit dokumentiertem Vorher-/Nachher-Zustand der Switch-Konfiguration (Screenshot der VLAN-Zuordnung vor und nach jedem Testschritt) – das macht deine Ergebnisse nachvollziehbar und reproduzierbar.

5. SPAN/Port-Mirroring im Detail

Der Monitoring-Host hängt an einem SPAN-Port (auch "Mirror Port" genannt) des Switches. Das bedeutet: Der Switch kopiert den gesamten Traffic von VLAN 10 (und optional VLAN 20) auf diesen einen zusätzlichen Port, ohne dass der Monitoring-Host selbst am eigentlichen Datenaustausch teilnimmt.

Das ist deshalb wichtig, weil einige deiner Tests (z. B. RQ-001, "Wireshark verifiziert F_Dest_Add/F_Source_Add und CRC im normalen Betrieb") einen kontinuierlichen, unverfälschten Blick auf den PROFIsafe-Verkehr brauchen, während gleichzeitig von der Kali-VM aus aktiv Frames eingespeist werden (RQ-002, Scapy-CRC-Kollision). Ohne SPAN-Port müsstest du entweder den aktiven und passiven Part nacheinander auf derselben Maschine laufen lassen (verliert Gleichzeitigkeit) oder einen klassischen Hub statt Switch verwenden (unrealistisch, da moderne Netzwerktechnik nicht mehr so funktioniert und PROFINET ohnehin Switches voraussetzt).

6. Die Debug-Bench als bewusst getrennte physische Einheit

JTAG-, UART- und Rotary-/DIL-Switch-Zugriffe (deine Tests für RQ-002/003/008/011, JTAGulator, Logic-Analyzer) haben nichts mit der Netzwerktopologie zu tun – das ist eine rein physische Interaktion mit dem Gehäuse und den Kontakten des Geräts. Deshalb sollte diese Testbank bewusst als eigener, von der Netzwerktopologie unabhängiger Arbeitsplatz behandelt werden:

Eigener Tisch/Bereich, unabhängig davon, ob das SRIO gerade netzwerkseitig in VLAN 10 oder 20 hängt
Wichtig für deine Priorisierungslogik: Wenn du die physische Testkampagne durchführst (Siegel öffnen, Schalter manipulieren), sollte das SRIO idealerweise weiterhin an der Netzwerktopologie hängen, damit du – wie in deiner Tabelle korrekt vorgesehen – sofort danach Log-Auslese (I&M0, Error-Log) über das Netzwerk durchführen kannst, ohne das Gerät neu zu verkabeln.
7. Reversibilität und Rollback-Strategie

Das ist der Punkt, an dem der hybride Ansatz seinen praktischen Wert für deine Priorisierungslogik aus dem letzten Schritt zeigt:

VMs (F-Host-Simulator, Kali, Monitoring): Vor jeder Testkampagne einen Snapshot ziehen. Nach einem destruktiven Test (z. B. boofuzz-Crash der Kali-Seite selbst, falls ein Response-Handler abstürzt) einfach zurückrollen – kostet Sekunden, kein Neuaufsetzen.
Switch-Konfiguration: VLAN-Zuordnungen als Config-Backup vor jeder Testkampagne sichern (bei den meisten Managed Switches per CLI-Export oder Web-GUI-Backup möglich), damit du nach einem Test mit absichtlich fehlkonfigurierten VLANs (RQ-011) zuverlässig in den Ausgangszustand zurückkommst.
SRIO selbst: Hier hast du laut deiner eigenen Analyse zwei Zustände, die nicht reversibel sind – das physische Siegel (einmal geöffnet, bleibt es sichtbar geöffnet) und der Error-Log nach Cold-Start (wird laut Dokumentation bei jedem Cold-Start gelöscht). Das bestätigt nochmal, warum deine Reihenfolge aus dem letzten Schritt (Siegel-Test spät, Cold-Start ganz zuletzt) sich exakt mit dieser Umgebung verträgt: Die Netzwerktopologie kannst du beliebig oft zurücksetzen, das physische Gerät nicht.
8. Sicherheitsgarantien und verbleibende Restrisiken

Für dein Methodik-Kapitel solltest du explizit benennen, was diese Umgebung tatsächlich garantiert und was nicht:

Garantiert:

Kein Zugriff von der Testumgebung auf Produktivsysteme oder das Internet (physische Abschottung)
Kein unautorisierter Zugriff auf die Testumgebung von außen (gleicher Grund)
Reproduzierbare, dokumentierte Zonenübergänge für RQ-001/RQ-011

Nicht garantiert / zu benennen als Limitation:

Die VLAN-Trennung ist logisch, nicht physisch – ein Switch-Firmware-Bug oder eine Fehlkonfiguration könnte theoretisch VLANs "durchlässig" machen. Das ist für eine akademische Arbeit als bewusste, begründete Einschränkung zu dokumentieren (ähnlich wie ihr es selbst schon in eurem Kali-Framework bei den Kommentaren zu CM-002 diskutiert habt).
Die Software-F-Host-Simulation bildet nicht zu 100 % das reale Verhalten einer zertifizierten SPS ab – falls das für deine Bewertung von RQ-010/RQ-011 relevant wird, solltest du das als methodische Einschränkung im Diskussionsteil der Thesis erwähnen.
9. Konkretes Ablaufbeispiel: RQ-011 durch diese Umgebung

Damit das nicht zu abstrakt bleibt, einmal durchgespielt, wie deine Tabellenzeile RQ-011 konkret in dieser Umgebung abläuft:

Ausgangszustand herstellen: SRIO-Port 1 → VLAN 10 (mit F-Host-Simulator), Port 2 unbelegt. Switch-Config-Backup ziehen. VM-Snapshots von F-Host-Simulator und Kali ziehen.
Baseline aufnehmen: Monitoring-Host über SPAN-Port starten, normale Parametrierung durch F-Host-Simulator beobachten (Wireshark bestätigt korrekten Param-Begin/Write/Param-End-Ablauf).
Angreifer-Zugriff simulieren: Kali-VM in VLAN 10 verschieben (simuliert: Angreifer hat bereits Netzwerkzugriff auf die Feldbus-Zone erlangt – realistisches Szenario, falls z. B. ein Laptop im selben Segment kompromittiert wurde). Von dort aus den in deiner Tabelle beschriebenen Scapy-Test (Param-Write ohne physischen Rotary-/DIL-Switch-Zugriff) durchführen.
Beobachtung protokollieren: Monitoring-Host zeichnet auf, ob die SCPU das Frame akzeptiert oder ablehnt.
Physischen Bypass ergänzend testen: Auf der Debug-Bench (unabhängig von der Netzwerktopologie) prüfen, ob die Schalterstellung ohne sichtbare Beschädigung veränderbar ist.
DCP-Reset-Cross-Segment-Test: Kali-VM zurück nach VLAN 20, dann gezielt einen DCP-Reset-Request Richtung VLAN 10 senden, um zu prüfen, ob die Zonentrennung diesen Layer-2-Broadcast tatsächlich blockiert.
Rückbau: Switch-Config aus Backup wiederherstellen, VM-Snapshots zurückrollen, SRIO-Verkabelung auf Ausgangszustand (Port 2 unbelegt) zurücksetzen.

Damit hast du für eine einzige Tabellenzeile eine vollständig reproduzierbare, dokumentierbare Testsequenz, die sowohl den Netzwerk- als auch den physischen Aspekt von RQ-011 abdeckt, ohne dass ein Schritt den nächsten verfälscht.

Soll ich dir aus diesem Ablaufbeispiel eine generische Vorlage/Checkliste machen, die du für jede der 14 RQ-Zeilen wiederverwenden kannst (Ausgangszustand → Aktion → Beobachtung → Rückbau), damit dein Testplan-Kapitel für alle 14 Fälle einheitlich strukturiert ist?