Testumgebung: Standalone-PC vs. isoliertes VLAN





Das SRIO ist kein einfaches "Gerät mit einem Ethernet-Port" – es hat spezifische Anforderungen, die die Topologie-Entscheidung direkt beeinflussen:



Anforderung												Konsequenz für Topologie

Muss in den State "Operate" wechseln, um viele Tests (RQ-008, 009, 010) sinnvoll durchzuführen		Braucht einen PROFINET/PROFIsafe F-Host (echte SPS oder Simulator), sonst bleibt es in "Parametrization"
2 physische Fieldbus-Ports (M12, D-coded)								Ermöglicht/erfordert zwei unterschiedliche Netzsegmente gleichzeitig anzuschließen
RQ-001-Gap: Annahme "used in a safe zone behind a firewall" (SRIO-9402)					Dieser Gap ist nur mit zwei getrennten Zonen empirisch prüfbar – ein einzelner PC kann das nicht simulieren
RQ-011: DCP-Reset auf Layer 2, cross-segment-Frage							Braucht ebenfalls zwei Segmente ("Zone A → Zone B", exakt wie CM-002 in eurem eigenen Framework)
Debug/Prog-Interface (SRIO-8628), Rotary-/DIL-Switches							Physischer Zugriff, unabhängig von Netzwerktopologie
Passives Mitschneiden (Wireshark) parallel zu aktivem Testing (Scapy)					Idealerweise getrennte Rollen (nicht ein Interface für alles)



Kernerkenntnis: Ein reiner Single-PC-Ansatz kann die in deiner eigenen Tabelle geforderten Multi-Zonen-Tests (RQ-001, RQ-011) strukturell nicht abbilden – dafür brauchst du mindestens zwei logisch getrennte Netzsegmente gleichzeitig.



Option A: Standalone-Rechner ("Stand von '98")

&#x09;Ein einzelner, physisch isolierter Rechner, per Direktkabel mit dem SRIO verbunden, ohne Internet, ohne Switch, ohne VLAN 

&#x09;	– der klassische Air-Gap-Ansatz aus der Zeit, als "Netzwerksicherheit" noch gleichbedeutend mit "Kabel raus" war.

&#x09;Vorteile:

&#x09;	- Maximal einfache, unangreifbare Isolation – kein Restrisiko durch Fehlkonfiguration einer Netzwerkkomponente
		- Kein Switch/Router als zusätzliche, im Testbericht zu rechtfertigende Komponente in der Trusted Computing Base
		- Für die rein passiven/lesenden Tests (RQ-004, 006, 009-Web, 013, 014 – dein "Web/API-Block") völlig ausreichend
		- Historisch das, was NIST 800-115 als einfachstes "external test system" beschreibt (Laptop mit Toolkit) ???



&#x09;Grenzen:

&#x09;	- Kann RQ-001 und RQ-011 nicht abbilden – es gibt keine "zweite Zone", von der aus du den Cross-Segment-Zugriff testen könntest
		- Keine gleichzeitige F-Host-Simulation und Angreifer-Perspektive und passives Mitschneiden ohne mehrere NICs oder mehrere Rechner – dann bist du faktisch schon bei einer Mini-Topologie, nur unstrukturiert
		- Schlecht reproduzierbar/dokumentierbar für eine Bachelorarbeit (kein sauberes Netzwerkdiagramm, keine IP-/VLAN-Tabelle, die du im Methodik-Kapitel referenzieren kannst)
		- Wenn du später Reviewer/Prüfer überzeugen willst, dass die "safe zone behind a firewall"-Annahme (SRIO-9402) tatsächlich geprüft wurde, brauchst du einen nachvollziehbaren Beleg für zwei Zonen 

&#x09;		– "ein Kabel" reicht dafür nicht als Nachweis

Fazit: Als alleinige Umgebung nicht ausreichend, aber als eine Rolle innerhalb einer größeren Topologie weiterhin sinnvoll (z. B. als isolierte Angreifer-Maschine).



Option B: Isoliertes VLAN

&#x09;Ein Managed Switch, auf dem mehrere VLANs eingerichtet sind – aber der Switch selbst hat keinen Uplink zu irgendeinem anderen Netz (kein Trunk zur Firmen-IT, kein Internet-Gateway). 

&#x09;Das ist wichtig: Es handelt sich nicht um "ein Segment in einem großen Netz", sondern um eine komplett abgeschottete Netzinsel, die intern logisch segmentiert ist.

&#x09;Vorteile:

&#x09;	- Bildet exakt das ab, was ihr in eurem eigenen Kali-Framework unter CM-002 ("Zone A → Zone B") testet 

&#x09;		– du kannst RQ-001 und RQ-011 damit tatsächlich empirisch validieren, statt nur zu dokumentieren, dass die Annahme unbelegt ist

&#x09;	- Ermöglicht SPAN/Port-Mirroring für passives Wireshark-Sniffing, ohne den aktiven Pfad (Scapy, boofuzz) zu stören

&#x09;	- Mehrere Rollen gleichzeitig möglich: F-Host-Simulator (PLC oder Software-Stack), SRIO (DUT), Kali-Angreifer-VM, Monitoring-Host – jede Rolle bekommt ihre eigene VLAN-Zuordnung

&#x09;	- Sauber dokumentierbar: VLAN-ID-Tabelle, IP-Schema, Netzplan – genau das, was NIST 800-115 unter "Assessment Logistics" fordert ???
		- Reduziert Hardware-Bedarf durch Virtualisierung: die einzelnen Rollen können VMs auf einem einzigen physischen Host sein, der Host selbst bleibt komplett air-gapped vom Rest der Welt

&#x09;Zu beachten/Risiken:

&#x09;	- Der Switch selbst wird Teil der Testumgebung und muss im Bericht mitgedacht werden (Firmware-Stand, keine versehentliche Trunk-Konfiguration, die VLANs "durchlässig" macht)
		- Reine VLAN-Trennung auf einem einzigen physischen Switch ist eine logische, keine physische Isolation 

&#x09;		– für eine Bachelorarbeit i. d. R. ausreichend zu rechtfertigen, sollte aber explizit benannt werden, damit niemand "physische Trennung" unterstellt, wo nur logische vorliegt


Empfehlung: Hybrid-Ansatz

&#x09;Eine physisch komplett abgeschottete, aber intern segmentierte Testinsel:

┌───────────────────────────────────────────────────────── ┐
│  ISOLIERTE TESTINSEL — kein Uplink zu Firma/Internet     │
│                                                          │
│   Managed Switch (VLAN-fähig, kein Trunk nach außen)     │
│                                                          │
│   VLAN 10 „Feldbus-Zone“         VLAN 20 „Angreifer-Zone“│
│   ┌──────────────┐                ┌──────────────┐       │
│   │ F-Host /     │◄──Port 1──┐    │ Kali-VM      │       │
│   │ PLC-Simulator│           │    │ (Scapy,      │       │
│   │ (PROFINET/   │           │    │ Nmap, ZAP,   │       │
│   │ PROFIsafe)   │           │    │ boofuzz)     │       │
│   └──────────────┘           │    └──────────────┘       │
│                              │                           │
│                        ┌─────▼─────┐                    │
│                        │  SRIO     │◄──Port 2──┐        │
│                        │  (DUT)    │            │        │
│                        └───────────┘            │        │
│                                                 ▼        │
│                      SPAN-Port ──► Monitoring-Host       │
│                                    (Wireshark, passiv)   │
│                                                          │
│   Physisch getrennt:  Debug-Bench (JTAG/UART, Rotary/DIL) │
└─────────────────────────────────────────────────────────┘



Warum das funktioniert:

&#x09;- Der äußere Rahmen (kein Uplink nach außen) gibt dir die Sicherheitsgarantie des Standalone-Ansatzes – "Stand von '98"-Prinzip, aber für die gesamte Insel statt für einen einzelnen PC
	- Die interne VLAN-Struktur gibt dir die Testfähigkeit für RQ-001/RQ-011, weil du echte Zonenübergänge produzieren kannst 

&#x09;	(Port 1 des SRIO in VLAN 10, Port 2 in VLAN 20 – oder beide Ports zunächst in derselben Zone, dann gezielt in getrennte, um den Unterschied zu zeigen)
	- SPAN-Port trennt sauber "passiv beobachten" von "aktiv angreifen" – wichtig, damit deine Wireshark-Captures nicht durch dieselbe Maschine laufen, die gerade Scapy-Frames einspeist (Nachvollziehbarkeit für die Thesis)
	- Debug-Bench (JTAG/UART, Rotary-/DIL-Switch-Zugriff) bleibt bewusst physisch getrennt von der Netzwerktopologie, weil das laut deiner Prioritätenliste ohnehin ein eigener Testblock ist

&#x09;- Praktisch reduzierbar auf wenig Hardware: F-Host-Simulator, Kali-Angreifer und Monitoring-Host können als VMs auf einem einzigen Host-PC laufen 

&#x09;	(der Host hat dann 2–3 virtuelle NICs, die an die jeweiligen VLAN-Ports des physischen Switches gebunden sind) 

&#x09;	– du brauchst also nicht zwingend vier Rechner, sondern einen leistungsfähigen Host + Switch + SRIO. Das entspricht dem, was NIST 800-115 unter "VM images... more versatile... favorable option for test teams" empfiehlt.



Für dein Methodik-Kapitel: was du dokumentieren solltest
	- Netzplan (wie oben) mit VLAN-IDs und IP-Schema
	- Begründung der Isolation (kein Uplink = kein Risiko für Produktivsysteme, referenziert auf NIST 800-115 6.4.2 "Location Selection")
	- Rollenverteilung (F-Host-Simulator, DUT, Angreifer, Monitor) und welche Tools auf welcher Rolle laufen
	- Begründung, warum VLAN statt reinem Air-Gap – nämlich weil RQ-001/RQ-011 sonst nicht testbar wären
	- Ein Verweis auf euer eigenes CM-002 als internes Präzedenzbeispiel für genau diese Testtopologie



\*\* Der hybride Testumgebungs-Ansatz – ausführliche Erläuterung \*\*



1. Das Grundprinzip: zwei Isolationsebenen, nicht eine

&#x09;- Äußere Isolation (der "Stand-von-98"-Gedanke): 

&#x09;	Die gesamte Testumgebung hat keinerlei physische Verbindung nach außen – kein Kabel zur Firmen-IT, kein WLAN, kein Internet-Gateway. 

&#x09;	Das ist die Garantie, dass egal was innerhalb der Umgebung passiert (Fuzzing-Crash, versehentlicher Broadcast-Sturm, kompromittierte VM), nichts nach außen dringen kann.
	- Innere Segmentierung (der VLAN-Gedanke): 

&#x09;	Innerhalb dieser abgeschotteten Insel schaffst du trotzdem mehrere logisch getrennte Zonen, weil du sonst die Zonenübergangs-Tests (RQ-001, RQ-011) gar nicht durchführen könntest 

&#x09;		– ein Air-Gap ohne interne Struktur ist ja nur "ein Kabel", das simuliert keine Netzwerktopologie.

&#x09;

&#x09;Der entscheidende Denkfehler, den man vermeiden muss: 

&#x09;	Diese beiden Ebenen dürfen nicht miteinander verwechselt werden. 

&#x09;	Die VLAN-Trennung schützt nicht vor der Außenwelt (das tut die physische Abschottung), und die physische Abschottung schützt nicht die Zonen voneinander (das tut die VLAN-Konfiguration). 

&#x09;	Beide haben unterschiedliche Aufgaben.



2. Die vier Rollen im Detail
Rolle A: F-Host-Simulator (PROFINET/PROFIsafe-Master)

&#x09;- Das SRIO ist als PROFIsafe F-Slave konzipiert und bleibt ohne einen ansprechenden F-Host im State "Parametrization" hängen 

&#x09;		– für alle Tests, die den State "Operate" voraussetzen (RQ-008, RQ-009, RQ-010, Teile von RQ-011), brauchst du zwingend einen Kommunikationspartner.

&#x09;Zwei Realisierungsmöglichkeiten:

&#x09;	- Echte SPS (z. B. Siemens S7-1500F mit PROFIsafe-fähiger CPU) – am nächsten an der Realität, aber teurer und weniger flexibel für gezielte Protokollverletzungen
		- Software-Simulator (z. B. ein PROFINET-Stack unter Linux mit p-net oder einer kommerziellen Konformitätstest-Suite) 

&#x09;		– flexibler, weil du auch bewusst fehlerhafte oder grenzwertige F-Host-Antworten erzeugen kannst, was für manche deiner Tests (z. B. Verhalten bei Watchdog-Timeout, RQ-010) sogar nötig ist

&#x09;Für deine Zwecke würde ich die Software-Variante empfehlen, weil sie dir erlaubt, den F-Host selbst als Testwerkzeug einzusetzen 

&#x09;	(z. B. bewusstes Aussetzen von Frames, um F\_WD\_Time-Verhalten zu prüfen), ohne eine reale SPS zu manipulieren.



&#x20;   Rolle B: Device Under Test (SRIO, AL400S/AL401S)

&#x09;	Das physische Gerät selbst. 

&#x09;	Hier ist wichtig: 

&#x09;		- Das SRIO hat zwei physische Fieldbus-Ports (M12, D-coded, weil Daisy-Chaining vorgesehen ist) plus einen Rotary-/DIL-Switch-Block und ein Debug-Interface (SRIO-2580, SRIO-8628). 

&#x09;			Diese physischen Anschlusspunkte bestimmen, wie viele Kabel du überhaupt zur Verfügung hast, um Zonen zu bilden.



&#x20;  Rolle C: Angreifer-Instanz (Kali-VM)

&#x09;	Das ist die Instanz, von der aus die aktiven Tests laufen (Scapy, Nmap, Hydra, ZAP, boofuzz – dein bereits definiertes Kali-Toolset). 

&#x09;	Sie sollte virtualisiert sein, aus einem einfachen Grund: 

&#x09;		- Du willst nach jedem potenziell destruktiven Test (Fuzzing, CRC-Kollisionsversuch) einen sauberen, reproduzierbaren Ausgangszustand herstellen können 

&#x09;			– das geht mit einem VM-Snapshot in Sekunden, mit einer physischen Neuinstallation nicht.



&#x20;  Rolle D: Monitoring-Host (passiv)

&#x09;Eine separate Instanz, die ausschließlich mitschneidet (Wireshark, tcpdump), aber selbst niemals aktiv Pakete sendet. 

&#x09;Diese Trennung ist kein Luxus, sondern methodisch wichtig: 

&#x09;	Wenn dieselbe Maschine gleichzeitig angreift und mitschneidet, vermischt sich in deinen Captures der von dir erzeugte Traffic mit dem, was du eigentlich beobachten willst 

&#x09;	(z. B. das Verhalten des SRIO als Reaktion auf den Angriff). 

&#x09;Für eine saubere, in der Thesis zitierfähige Beweisführung ("Wireshark zeigt X") solltest du diese Rollen sauber trennen können.



3. Physisch vs. virtuell – was wird wie realisiert

&#x09;

&#x09;Rolle			Realisierung					Warum

&#x09;F-Host-Simulator	VM auf Host-PC					Muss reproduzierbar konfigurierbar sein
	Kali-Angreifer		VM auf Host-PC					Snapshot-Fähigkeit essenziell
	Monitoring-Host		VM auf Host-PC oder separates Mini-Gerät	Wenn VM: eigene virtuelle NIC am SPAN-Port
	SRIO (DUT)		Physisch, keine Alternative			Ist das reale Testobjekt
	Managed Switch		Physisch, keine Alternative			VLAN-Trennung ist Hardware-/Firmware-Funktion
	Debug-Bench		Physisch, separat				JTAG/UART/Rotary-Zugriff geht nicht virtuell



Ein einziger, ausreichend leistungsfähiger Host-PC mit einem Hypervisor (z. B. VirtualBox, VMware Workstation oder – sauberer für Netzwerktests – Proxmox/ESXi) und mehreren physischen Netzwerkkarten (oder einer Karte mit mehreren Ports) genügt für die drei virtuellen Rollen. Jede VM bekommt eine eigene virtuelle NIC, die 1:1 an einen physischen Port des Host-PCs gebunden ist (kein virtueller Switch innerhalb des Hypervisors dazwischen, sonst untergräbst du die spätere VLAN-Kontrolle des physischen Switches).



4. Das VLAN-Design im Detail

&#x09;Konkreter Vorschlag für dein Setup:

&#x09;VLAN-ID	Name			Enthält						Zweck

&#x09;10	Feldbus-Zone		F-Host-Simulator, SRIO-Port 1			Simuliert die "vertrauenswürdige" Automatisierungszelle
	20	Angreifer-Zone		Kali-VM						Simuliert einen potenziellen Angreifer, der sich Netzwerkzugriff verschafft hat (z. B. über einen kompromittierten Laptop im selben Segment)
	30	Management/Monitoring	Monitoring-Host					Getrennt, damit der SPAN-Traffic nicht mit Testtraffic kollidiert
	99	Physisch nicht belegt	(leer, ggf. für ungenutzte Switch-Ports)	Best Practice, um versehentliche Auto-Negotiation in ein aktives VLAN zu verhindern



&#x09;Der SRIO-Port 2 wird je nach Testfall unterschiedlich verkabelt – das ist der eigentliche Clou dieser Topologie:

&#x09;- Für Tests, die den Normalzustand abbilden (Baseline für RQ-004, 006, 007, 009, 013, 014): 

&#x09;	Port 2 bleibt frei oder wird ebenfalls an VLAN 10 gehängt (Daisy-Chain-Simulation).
	- Für RQ-001 (Prüfung der Firewall-Annahme "safe zone behind a firewall"): 

&#x09;	Du verkabelst Port 2 testweise so, dass er in VLAN 20 hängt, und prüfst, ob von der Angreifer-Zone aus tatsächlich unerwartete Dienste/Ports auf dem SRIO erreichbar sind, 

&#x09;	obwohl die Dokumentation eine Firewall zwischen den Zonen voraussetzt.
	- Für RQ-011 (DCP-Reset über Cross-Segment): 

&#x09;	Du platzierst die Kali-VM bewusst in VLAN 20, richtest auf dem Switch eine (eigentlich nicht vorgesehene) Layer-2-Verbindung zu VLAN 10 ein oder prüfst, ob DCP-Broadcast-Frames trotz VLAN-Trennung durchkommen 

&#x09;		– das bildet exakt euer eigenes CM-002-Szenario ab ("Zone A → Zone B, Cross-Segment-Exposure").

&#x09;Wichtig für die Sauberkeit deiner Ergebnisse: 

&#x09;Diese Zonenverschiebung machst du nicht permanent, sondern gezielt pro Testlauf, mit dokumentiertem Vorher-/Nachher-Zustand der Switch-Konfiguration (Screenshot der VLAN-Zuordnung vor und nach jedem Testschritt) 

&#x09;– das macht deine Ergebnisse nachvollziehbar und reproduzierbar.



5. SPAN/Port-Mirroring im Detail

&#x09;Der Monitoring-Host hängt an einem SPAN-Port (auch "Mirror Port" genannt) des Switches. 

&#x09;Das bedeutet: Der Switch kopiert den gesamten Traffic von VLAN 10 (und optional VLAN 20) auf diesen einen zusätzlichen Port, ohne dass der Monitoring-Host selbst am eigentlichen Datenaustausch teilnimmt.

&#x09;Das ist deshalb wichtig, weil einige deiner Tests (z. B. RQ-001, "Wireshark verifiziert F\_Dest\_Add/F\_Source\_Add und CRC im normalen Betrieb") einen kontinuierlichen, unverfälschten Blick auf den PROFIsafe-Verkehr brauchen, 

&#x09;während gleichzeitig von der Kali-VM aus aktiv Frames eingespeist werden (RQ-002, Scapy-CRC-Kollision). Ohne SPAN-Port müsstest du entweder den aktiven und passiven Part nacheinander auf derselben Maschine laufen lassen 	(verliert Gleichzeitigkeit) oder einen klassischen Hub statt Switch verwenden (unrealistisch, da moderne Netzwerktechnik nicht mehr so funktioniert und PROFINET ohnehin Switches voraussetzt).



6. Die Debug-Bench als bewusst getrennte physische Einheit

&#x09;JTAG-, UART- und Rotary-/DIL-Switch-Zugriffe (deine Tests für RQ-002/003/008/011, JTAGulator, Logic-Analyzer) haben nichts mit der Netzwerktopologie zu tun – das ist eine rein physische Interaktion mit dem Gehäuse und den 	Kontakten des Geräts. 

&#x09;Deshalb sollte diese Testbank bewusst als eigener, von der Netzwerktopologie unabhängiger Arbeitsplatz behandelt werden:

&#x09;	- Eigener Tisch/Bereich, unabhängig davon, ob das SRIO gerade netzwerkseitig in VLAN 10 oder 20 hängt
	Wichtig für deine Priorisierungslogik: Wenn du die physische Testkampagne durchführst (Siegel öffnen, Schalter manipulieren), sollte das SRIO idealerweise weiterhin an der Netzwerktopologie hängen, damit du – wie in deiner 	Tabelle korrekt vorgesehen – sofort danach Log-Auslese (I\&M0, Error-Log) über das Netzwerk durchführen kannst, ohne das Gerät neu zu verkabeln.


7\. Reversibilität und Rollback-Strategie

&#x09;Das ist der Punkt, an dem der hybride Ansatz seinen praktischen Wert für deine Priorisierungslogik aus dem letzten Schritt zeigt:

&#x09;	- VMs (F-Host-Simulator, Kali, Monitoring): 

&#x09;		Vor jeder Testkampagne einen Snapshot ziehen. 

&#x09;		Nach einem destruktiven Test (z. B. boofuzz-Crash der Kali-Seite selbst, falls ein Response-Handler abstürzt) einfach zurückrollen – kostet Sekunden, kein Neuaufsetzen.
		- Switch-Konfiguration: 

&#x09;		VLAN-Zuordnungen als Config-Backup vor jeder Testkampagne sichern (bei den meisten Managed Switches per CLI-Export oder Web-GUI-Backup möglich), 

&#x09;		damit du nach einem Test mit absichtlich fehlkonfigurierten VLANs (RQ-011) zuverlässig in den Ausgangszustand zurückkommst.
		- SRIO selbst: Hier hast du laut deiner eigenen Analyse zwei Zustände, die nicht reversibel sind 

&#x09;		– das physische Siegel (einmal geöffnet, bleibt es sichtbar geöffnet) und der Error-Log nach Cold-Start (wird laut Dokumentation bei jedem Cold-Start gelöscht). 

&#x09;		
8. Sicherheitsgarantien und verbleibende Restrisiken

&#x09;Für dein Methodik-Kapitel solltest du explizit benennen, was diese Umgebung tatsächlich garantiert und was nicht:

&#x09;Garantiert:

&#x09;	- Kein Zugriff von der Testumgebung auf Produktivsysteme oder das Internet (physische Abschottung)
		- Kein unautorisierter Zugriff auf die Testumgebung von außen (gleicher Grund)
		- Reproduzierbare, dokumentierte Zonenübergänge für RQ-001/RQ-011

&#x09;Nicht garantiert / zu benennen als Limitation:

&#x09;	- Die VLAN-Trennung ist logisch, nicht physisch – ein Switch-Firmware-Bug oder eine Fehlkonfiguration könnte theoretisch VLANs "durchlässig" machen. 

&#x09;		Das ist für eine akademische Arbeit als bewusste, begründete Einschränkung zu dokumentieren (ähnlich wie ihr es selbst schon in eurem Kali-Framework bei den Kommentaren zu CM-002 diskutiert habt).

&#x09;	- Die Software-F-Host-Simulation bildet nicht zu 100 % das reale Verhalten einer zertifizierten SPS ab – falls das für deine Bewertung von RQ-010/RQ-011 relevant wird, solltest du das als methodische Einschränkung im 			Diskussionsteil der Thesis erwähnen.




\*\* Brauchst du wirklich Kali Linux? \*\*



Nein, du brauchst Kali nicht zwingend – und für den Kernteil deiner Tests (die PROFINET/PROFIsafe-spezifischen Sachen) bringt es dir sogar fast nichts. Aber es gibt einen guten pragmatischen Grund, es trotzdem zu verwenden. 



Was Kali eigentlich ist – und was nicht

&#x09;Kali ist keine eigene Technologie, sondern ein Debian-Derivat mit ca. 600 vorinstallierten Sicherheitswerkzeugen. 

&#x09;Es gibt keinen einzigen Test in deiner Tabelle, der nur unter Kali funktioniert – jedes Tool (Nmap, Wireshark, Hydra, ZAP, Scapy, boofuzz, sslscan, Nikto, Lynis, OpenVAS) lässt sich genauso auf einem normalen Debian/Ubuntu 	installieren. 

&#x09;\*\* Kali spart dir im Wesentlichen nur den apt install-Schritt für jedes einzelne Tool.\*\*



Wenn ich deine 14 Zeilen durchgehe, zeigt sich ein aufschlussreiches Muster:



Tool-Kategorie				Beispiele aus deiner Tabelle								Kali-exklusiv?

Generische Netzwerk-/Web-Tools		Nmap, Hydra, ZAP, Nikto, sslscan, Lynis, siege						Nein – auf jedem Linux per apt/pip installierbar

PROFINET/PROFIsafe-spezifisch		Scapy (scapy.contrib.pnio\_dcp), Wireshark mit PROFIsafe-Dissector, pnio\_dcp/profi-dcp	Nein – reine Python-Pakete/Wireshark-Plugins, die es in Kali gar nicht vorinstalliert gibt; du installierst 																sie so oder so selbst nach

Hardware-Recon				JTAGulator, Logic-Analyzer (sigrok/PulseView)						Nein – laufen über serielle Schnittstelle bzw. eigene Software, betriebssystemunabhängig

Firmware-Analyse			binwalk, checksec									Teilweise in Kali vorinstalliert, aber auch trivial nachinstallierbar

Fuzzing					boofuzz											Nein – reines pip install boofuzz, läuft überall



Ergebnis: Gerade der Teil, der deine Arbeit inhaltlich interessant und eigenständig macht – die PROFINET/PROFIsafe-spezifischen Tests – hat mit Kali überhaupt nichts zu tun. Das sind Python-Skripte und Wireshark-Erweiterungen, die du auf jedem Linux gleichermaßen selbst nachinstallieren musst. Kalis Vorteil ("alles ist schon drauf") greift also genau bei den Tests am wenigsten, die für deine Thesis den größten wissenschaftlichen Mehrwert haben.



Argumente FÜR Kali

&#x09;- Konsistenz mit eurem bereits bestehenden internen Framework: Euer eigenes Dokument (CM-001 bis CM-010) ist explizit als "Kali Linux Toolset" betitelt und listet für jede Countermeasure den passenden Kali-Befehl . Wenn deine 		Methodik später produktiv im Unternehmen eingesetzt werden soll (dein erklärtes Ziel: "systematically verify security in future product releases"), ist es praktisch sinnvoll, auf demselben Fundament aufzubauen wie das 		bereits akzeptierte Framework – andere Ingenieure kennen die Umgebung schon.

&#x09;- Anerkannter Standard: Für eine Bachelorarbeit ist Kali als "die" Pentest-Distribution breit bekannt und akzeptiert – das erspart dir Rechtfertigungsaufwand im Methodik-Kapitel, warum du gerade dieses Setup gewählt hast.

&#x09;- Zeitersparnis: Kein Debugging von Abhängigkeiten bei den generischen Tools (Nmap, Hydra, ZAP etc.) – die sind vorinstalliert und aufeinander abgestimmt getestet.



Argumente GEGEN Kali (bzw. für ein schlankes Setup)

&#x09;- Reproduzierbarkeit ist ein wissenschaftliches Kernkriterium – und Kali ist eine Rolling-Release-Distribution. 

&#x09;	Tool-Versionen ändern sich laufend. Wenn du in deiner Methodik Wert auf nachvollziehbare, wiederholbare Ergebnisse legst (was für eine "validated testing methodology" zentral ist), ist eine versionsfixierte, minimale 		Debian/Ubuntu-LTS-Installation mit exakt dokumentierten Tool-Versionen methodisch sauberer und leichter zu rechtfertigen.

&#x09;- Unnötig große Angriffsfläche/Werkzeugmenge für ein schmales Testszenario: 

&#x09;	Du brauchst realistisch ca. 8–10 Tools, Kali liefert \~600. Für eine saubere, vollständig auditierbare Testumgebung (die du im Anhang exakt auflisten willst) ist ein minimales, kuratiertes Setup einfacher vollständig zu 		dokumentieren – niemand muss sich fragen, was von den 600 vorinstallierten Tools tatsächlich benutzt wurde und was nicht.

&#x09;- Ein gewisser methodischer Widerspruch: Deine gesamte Arbeit dreht sich um das Prinzip "nur die minimal notwendige Funktionalität sollte vorhanden sein" (das ist ja der Kerngedanke hinter CR 7.8/Asset-Inventar und den 			Identifikationspflichten der Verordnung). Es wäre argumentativ etwas inkonsistent, deine Testumgebung selbst als maximalistische "Alles-drauf"-Distribution aufzusetzen, während du beim SRIO genau das Gegenteil forderst.



Meine konkrete Empfehlung: rollenbasiert entscheiden, nicht pauschal



Erinnere dich an die vier Rollen aus der hybriden Testumgebung – die Antwort auf "Kali ja/nein" ist für jede Rolle unterschiedlich:



Rolle							Kali sinnvoll?		Begründung

Angreifer-VM (Nmap, Hydra, ZAP, Scapy, boofuzz)		Ja, sinnvoll		Genau der Einsatzzweck, für den Kali gebaut ist; passt zu eurem bestehenden CM-Framework

F-Host-Simulator					Nein, unnötig		Braucht nur einen PROFINET-Stack, keine offensiven Tools – ein Kali-Unterbau wäre hier unbegründeter Ballast

Monitoring-Host (nur Wireshark/tcpdump, rein passiv)	Nein, unnötig		Ein minimaler Debian-Server mit genau einem Tool ist sauberer und reduziert die Angriffsfläche der eigenen Testinfrastruktur

Debug-Bench (JTAGulator, Logic-Analyzer)		Irrelevant		Läuft ohnehin über eigene Software/serielle Schnittstelle, betriebssystemunabhängig



Ja, für drei deiner vier Rollen ist ein schlankes, selbst zusammengestelltes Debian sinnvoller – nur für die eine Rolle, die tatsächlich aktiv angreift, lohnt sich Kali, hauptsächlich aus Konsistenzgründen mit eurem bestehenden Framework, nicht aus technischer Notwendigkeit.



Praktischer Kompromiss für deine Thesis



Falls dir das zu viel Abstimmungsaufwand ist: Nimm für die Angreifer-VM Kali (spart Zeit, passt zum bestehenden Framework), aber dokumentiere im Methodik-Kapitel explizit nur die tatsächlich verwendeten Pakete und deren exakte Versionen (z. B. per dpkg -l oder pip freeze als Anhang-Snapshot) – dann hast du den Bequemlichkeitsvorteil von Kali, ohne die Reproduzierbarkeits-Schwäche in Kauf zu nehmen, weil jeder Prüfer/Nachnutzer genau sieht, welche Teilmenge tatsächlich relevant war.





\*\* Testumgebung komplett ohne Kali Linux \*\*



Wenn du Kali auch für die Angreifer-Rolle weglässt, wird deine gesamte Umgebung homogen: Alle vier virtuellen/physischen Rollen laufen auf derselben schlanken Basis (z. B. Debian 12 "Bookworm" minimal, ohne grafische Oberfläche), und jede Rolle bekommt nur die Pakete, die sie tatsächlich braucht. Das ist – wie in der letzten Antwort angedeutet – für eine wissenschaftliche Arbeit sogar die methodisch sauberere Variante, weil du dann ein einziges, konsistentes Basis-Image hast, das du für jede Rolle nur unterschiedlich bestückst. Ich gehe das systematisch durch.



1\. Grundprinzip: ein Basis-Image, vier Rollenprofile



Statt "Kali für Angriff, Debian für den Rest" hast du jetzt ein goldenes Basis-Image (minimal Debian, gehärtet, aktualisiert, ohne unnötige Dienste), das du klonst und pro Rolle mit genau den benötigten Paketen bestückst. Das erleichtert dir die Dokumentation enorm, weil du im Anhang nur eine Basis-Spezifikation brauchst plus vier kurze Diff-Listen ("zusätzlich installiert: …").



┌─────────────────────────────────────────────────────────	┐

│  ISOLIERTE TESTINSEL — kein Uplink nach außen            						│

│  Alle VMs: Debian 12 minimal (gleiches Basis-Image)      						│

│                                                            					│

│   VLAN 10 „Feldbus-Zone"          VLAN 20 „Angreifer-Zone"					│

│   ┌──────────────────	┐             ┌──────────────────	┐  	│

│   │ F-Host-Simulator  		│             │ Test-VM          			│  	│

│   │ + p-net-Stack     		│             │ + Nmap/Hydra/ZAP 			│  │

│   │                    		│             │ + Scapy/boofuzz  			│  │

│   └────────┬──────────┘             └──────────────────	┘  	│

│            	 │                                              │

│      ┌─────▼─────┐                                        │

│      │  SRIO     │                                        │

│      │  (DUT)    │                                        │

│      └───────────┘                                        │

│            │ SPAN                                         │

│   ┌────────▼──────────┐                                   │

│   │ Monitoring-Host    │                                  │

│   │ + tshark/tcpdump   │                                  │

│   └────────────────────┘                                  │

└─────────────────────────────────────────────────────────┘





Die Topologie (VLANs, SPAN-Port, physische SRIO-Anbindung, Debug-Bench) bleibt komplett unverändert – es ändert sich ausschließlich, woher die Software auf den drei virtuellen Rollen kommt.



2\. Wahl der Basis-Distribution



&#x09;Empfehlung: Debian 12 (Bookworm), minimal/netinst, ohne Desktop-Umgebung, aus zwei Gründen:



&#x09;Debian ist die Basis, auf der Kali selbst aufbaut – du verlierst also keine Paket-Kompatibilität, sondern näherst dich nur "einen Schritt näher an die Wurzel"

&#x09;Debian hat sehr lange Support-Zyklen und stabile, version-gepinnte Repositories – wichtig für die Reproduzierbarkeit, die dir bei Kalis Rolling-Release-Modell fehlt



&#x09;Alternative wäre Ubuntu Server LTS – funktional nahezu austauschbar, ich bleibe bei Debian als Referenz.



3\. Rolle für Rolle: welche Pakete woher kommen

&#x09;F-Host-Simulator (VLAN 10)

&#x09;Bestandteil					Quelle					Bemerkung

&#x09;PROFINET-Stack (p-net oder vergleichbar)	GitHub-Quellcode, selbst kompiliert	Kein Debian-Paket verfügbar, muss so oder so manuell gebaut werden – unabhängig von Kali

&#x09;Python 3 + pip					Debian-Repo				Für Steuerskripte des Simulators



Hier ändert sich durch den Kali-Verzicht nichts, da dieser Stack ohnehin nie aus Kali kam.



Test-VM / "Angreifer"-Rolle (VLAN 20) – hier passiert die eigentliche Umstellung

Tool				Ohne Kali: Bezugsquelle										Aufwand

Nmap				apt install nmap										Debian-Repo, identisch zu Kali

Hydra (thc-hydra)		apt install hydra										In Debian-Repos vorhanden, keine Änderung

sslscan				apt install sslscan										Debian-Repo

Lynis				apt install lynis										Debian-Repo

Nikto				apt install nikto										Debian-Repo

Scapy				apt install python3-scapy oder pip install scapy						Debian-Repo, reines Python-Paket

boofuzz				pip install boofuzz										War nie ein Kali-Paket, immer via pip

pnio\_dcp / profi-dcp		pip install pnio\_dcp (PyPI)									Ebenfalls unabhängig von Kali

OWASP ZAP			Manueller Download von zaproxy.org (.tar.gz) oder Snap-Paket					Etwas mehr Aufwand als apt, aber gut dokumentiert

OpenVAS / Greenbone (GVM)	Debian-Community-Repository der Greenbone-Community-Edition, manuelle Einrichtung (gvm-setup)	Deutlich aufwendiger ohne Kali – das ist der einzige Punkt, an dem der Verzicht auf Kali spürbar mehr 																		Einrichtungszeit kostet

Siege				apt install siege										Debian-Repo





Monitoring-Host (SPAN-Port, rein passiv)

Tool				Quelle

tshark / Wireshark (CLI)	apt install tshark

tcpdump				apt install tcpdump

PROFINET/PROFIsafe-Dissector	In aktuellen Wireshark-Versionen bereits als eingebauter Dissector enthalten (kein Kali-Spezifikum)



Debug-Bench (JTAGulator, Logic-Analyzer)

Tool				Quelle

JTAGulator-Steuersoftware	Eigenständiges Tool, seriell angebunden, betriebssystemunabhängig

sigrok / PulseView		apt install sigrok pulseview – Debian-Repo





4\. Was konkret aufwendiger wird

Um ehrlich zu bleiben, nenne ich die zwei Stellen, an denen der komplette Kali-Verzicht tatsächlich spürbaren Mehraufwand bedeutet:

&#x09;- OpenVAS/Greenbone (für RQ-008, CVE-Scanning): In Kali ist der komplette Feed samt Datenbank vorkonfiguriert startbereit. 

&#x09;	Auf reinem Debian musst du das Greenbone-Community-Repository selbst einbinden, den Feed-Sync manuell anstoßen (kann je nach Internetanbindung mehrere Stunden dauern) und die PostgreSQL-Datenbank selbst initialisieren. 	- Für deine isolierte, offline Testumgebung bedeutet das zusätzlich: Feed-Synchronisation muss vor der Abschottung erfolgen, da sie Internetzugriff braucht 

&#x09;	– ein Punkt, den du in der Ablaufplanung einbauen musst (Feed aktualisieren, dann Netzwerkkabel für die Isolation kappen).

&#x09;- OWASP ZAP: Kein Debian-Repo-Paket, du lädst das offizielle Release-Archiv herunter oder nutzt die Snap-Distribution. Minimal aufwendiger, aber unkompliziert.



5\. Dokumentationsvorteil dieser Variante



Für dein Methodik-Kapitel wird die Beschreibung jetzt einheitlicher und kürzer, weil du nur noch eine Basis-Spezifikation brauchst:



Basis-Image: Debian 12.x (Bookworm), minimal, Kernel-Version X.X

Gehärtet nach: \[z. B. CIS Debian Benchmark, sofern relevant]



Rolle „Test-VM" – zusätzlich installierte Pakete:

&#x20; nmap 7.9x (Debian-Paket, Version Y)

&#x20; hydra 9.x (Debian-Paket)

&#x20; scapy x.x (pip, Version Z)

&#x20; boofuzz x.x (pip, Version Z)

&#x20; pnio\_dcp x.x (pip)

&#x20; zaproxy x.x (manuell, Quelle: zaproxy.org, SHA256: ...)

&#x20; openvas/gvm x.x (Greenbone Community Repo, Feed-Stand: DATUM)



Rolle „F-Host-Simulator" – zusätzlich installiert:

&#x20; p-net (Commit-Hash: ...)



Rolle „Monitoring-Host" – zusätzlich installiert:

&#x20; tshark x.x (Debian-Paket)





Das ist prüfbarer und eindeutiger als eine Kali-Beschreibung, bei der ein Prüfer nie ganz sicher sein kann, ob ein bestimmtes Verhalten von einem der \~600 mitgelieferten Pakete beeinflusst wurde, die du nie explizit erwähnst.



6\. Kurzes Fazit dieser Variante gegenüber der vorherigen (Kali für Angreifer-Rolle)

Aspekt						Mit Kali (Angreifer-Rolle)					Ganz ohne Kali

Einrichtungsaufwand				Geringer (vorinstalliert)					Etwas höher, v. a. wegen GVM

Reproduzierbarkeit				Schwächer (Rolling Release)					Stärker (versionsfixiertes Debian)

Konsistenz mit eurem bestehenden CM-Framework	Direkt passend							Muss im Bericht explizit als "äquivalent, aber Kali-unabhängig" begründet werden

Dokumentationsaufwand im Anhang			Höher (Kali-Gesamtpaketliste vs. genutzte Teilmenge klären)	Geringer (jedes Paket ist explizit und bewusst installiert)

Wissenschaftliche Sauberkeit			Gut								Etwas besser



Insgesamt: Technisch ist der Verzicht auf Kali für praktisch alle Tools problemlos machbar, mit OpenVAS/GVM als einzigem nennenswerten Mehraufwand. Für deine Bachelorarbeit würde ich diesen vollständig Kali-freien Ansatz empfehlen, wenn du Wert auf maximale Nachvollziehbarkeit legst – solltest du dagegen zeitlich unter Druck stehen oder möchtest die Ergebnisse möglichst direkt an euer bestehendes Kali-Framework anschließen, ist die hybride Variante (Kali nur für die Angreifer-Rolle) der pragmatischere Mittelweg.



\--------------



\*\*Quellen\*\*

1\. Allgemeine ICS/OT-Testumgebungen (Grundlagenliteratur)

ICS testbed / industrial control system testbed

cyber-physical testbed / cyber-physical system (CPS) testbed

SCADA testbed security

OT security testbed design

ICS testbed maturity model (führt z. B. direkt zu Bhattacharya et al., "ICS-CTM2", einem Paper, das genau eine Bewertungssystematik für Testbeds liefert)

hardware-in-the-loop industrial control system testbed

testbed fidelity industrial control systems (Begriff "Fidelity" ist in der Literatur zentral für die Frage "wie realitätsnah muss meine Umgebung sein")



2\. Netzwerksegmentierung / Isolation (dein Kernthema VLAN vs. Air-Gap)

network segmentation industrial control systems

Purdue model network segmentation (Standardreferenz-Architektur für IT/OT-Zonierung, wird in fast jedem Testbed-Paper zitiert)

air-gapped network security limitations

logical vs physical network isolation OT (genau die Debatte, die wir besprochen haben – ein Fachartikel bringt das Argument "Logical Segmentation Is Not an Air Gap" explizit auf den Punkt)

VLAN segmentation security testing

zone and conduit model IEC 62443 (das ist der offizielle Fachbegriff für dein Zonen-Konzept aus IEC 62443-3-2/3-3)



3\. Speziell PROFINET/PROFIsafe (dein Protokoll)

PROFINET security testbed

PROFINET man-in-the-middle (führt z. B. zu einem sehr aktuellen, direkt einschlägigen Paper: Martín-Fraile et al. 2026, "A Hybrid Digital-Twin-Based Testbed for Real-Time Manipulation of PROFINET I/O")

PROFIsafe error management vulnerabilities (führt zu einer sehr passenden aktuellen Masterarbeit/Executive Summary: Alfonsi, Politecnico di Milano, über Angriffe auf PROFIbus/PROFIsafe via Error-Management-Schwachstellen)

black channel safety protocol security

fieldbus protocol fuzzing

digital twin PLC security testing (relevant, weil manche Papers PLC-Simulatoren statt echter Hardware für den F-Host nutzen – genau dein Diskussionspunkt)



4\. Methodik / Validierung von Testumgebungen selbst

testbed reproducibility cybersecurity research

resilience evaluation methodology industrial control systems (führt zu METRICS, einem methodisch sehr sauberen Paper zu genau diesem Thema – systematische, vergleichbare Testkampagnen)

virtual vs physical testbed comparison ICS

network emulation vs simulation industrial control systems

minimum viable testbed OT security / low-cost ICS testbed



5\. Regulatorischer/normativer Kontext (Anschluss an dein Hauptthema)

IEC 62443-4-1 secure development lifecycle testing

conformity assessment cybersecurity machinery

functional safety cybersecurity convergence testing

EU Machinery Regulation cybersecurity compliance (für die regulatorische Seite, ergänzend zu deinem bereits vorhandenen Kapitel)



6\. Praktisch-methodische Ergänzung (Rollen/Tools)

Kali Linux penetration testing methodology reproducibility (falls du die Kali-Diskussion wissenschaftlich untermauern willst)

virtual machine snapshot rollback security testing

SPAN port mirroring network forensics methodology





Konkrete Fundstellen, die schon direkt passen (zum sofortigen Nachschlagen)

Quelle																				Warum relevant

Martín-Fraile et al. 2026,"A Hybrid Digital-Twin-Based Testbed for Real-Time Manipulation of PROFINET I/O", MDPI Applied Sciences				Fast 1:1 dein Szenario: PROFINET-Testbed mit digitalem Zwilling + realer SPS

Alfonsi (Politecnico di Milano),"Novel attack strategies targeting PROFIbus and PROFIsafe Exploiting Error Management vulnerabilities"				Aktuelle Abschlussarbeit, direkt zu PROFIsafe-Angriffsvektoren

~~Bader et al. (Fraunhofer FKIE/RWTH Aachen),"METRICS: A Methodology for Evaluating and Testing the Resilience of Industrial Control Systems to Cyberattacks"~~	Saubere Methodik-Vorlage für systematische Testkampagnen

Pospisil et al. 2021,"Application Perspective on Cybersecurity Testbed for Industrial Control Systems", Sensors/MDPI						Guter Überblick "best practices for assembling 																									physical/simulated/virtual/hybrid testbeds" 

&#x09;																				– nützlich als methodische Referenz für dein Kapitel

Bhattacharya et al.,"ICS-CTM2: Industrial Control System Cybersecurity Testbed Maturity Model"									Bewertungsraster, falls du deine eigene Testumgebung gegen ein 																							Reifegradmodell rechtfertigen willst

Lancaster ICS Testbed / "ICS Testbed Tetris"															Sehr konkrete Bausteine (Management-Layer, VLAN-Empfehlung, Mirror-Feeds) – 																				praktisch direkt übertragbar auf dein Setup





Tipp für die Google-Scholar-Suche selbst



Kombiniere die Begriffe mit Anführungszeichen für Phrasen und nutze den Zeitfilter (z. B. "seit 2020"), da sich das Feld schnell entwickelt:



"ICS testbed" AND "network segmentation"

"PROFINET" AND "penetration testing"

"IEC 62443" AND "testbed" AND "methodology"

"air-gapped" AND "OT" AND "limitations"







