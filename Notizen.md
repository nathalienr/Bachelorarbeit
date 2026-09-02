USB3-zu-Gigabit-Ethernet-Dongle von kali zu switch
switch 192.168.0.91, eine sps 192.168.0.1, das safe remote i/o 192.168.0.2, den kali linux rechner mit 192.168.0.80 und meinen firmenlaptop mit 192.168.0.7. sps ist mit port1 , safe remote i/o ist mit port2, kali-rechner mit port3 und laptop mit port4 vom switch verbunden


**Basis-Setup** (SPS + SRIO + Engineering-Laptop, kein Kali nötig)
Testfall									Warum kein Kali nötig
TC-RQ001-01									Reine Funktionsprüfung über TIA Portal (I/O togglen)
TC-RQ002-01, TC-RQ005-01							Falsche iParCRC wird direkt in TIA Portal erzeugt
TC-RQ003-02, TC-RQ003-04							Autorisierte Änderung + Log-Lesen (Browser/IoT-Core reicht)
TC-RQ004-01, TC-RQ004-04, TC-RQ006-01, TC-RQ009-01/02/03, TC-RQ013-01		I\&M-Daten nur über TIA Portal lesbar, Rest über Browser
TC-RQ007-01, TC-RQ008-01							Baseline-Lesezugriff, kein Angriff
TC-RQ012-02, TC-RQ012-04							Reiner Power-Cycle + Log-Lesen



**Setup A** – passiv (Mirror-Port / Bridge ohne Eingriff)
Testfall							Warum passiv reichen muss
TC-RQ004-03, TC-RQ006-03, TC-RQ014-02				Ziel ist explizit Nachweis von Klartext, jeder aktive Eingriff würde das Messergebnis verfälschen
TC-RQ001-05 (Timing-Nachweis), TC-RQ007-02 (Ausfallfenster)	Nur mitschneiden, nicht eingreifen, um echte Zeiten zu messen



**Setup B** – aktiv, aber regulärer Port reicht (kein Suppression nötig)
Grund: Der Switch liefert eine Unicast-Frame an SRIOs MAC-Adresse unabhängig davon, von welchem Port sie kommt – für reines "zusätzliches böses Frame senden, während das echte auch ankommt" brauchst du keine Inline-Position.

Testfall										Warum Setup B ausreicht
TC-RQ001-02 (Portscan), TC-RQ011-01 (Read-only-Check), TC-RQ011-04 (Update-Gate)	Reine Scans/HTTP-Requests
TC-RQ001-03, TC-RQ002-02								Ziel ist Rejection nachzuweisen (falsche Adresse/CRC) – das funktioniert auch parallel zum echten Traffic, du musst nichts unterdrücken
TC-RQ003-05, TC-RQ008-05								HTTP-Call auf /fit/setfit
TC-RQ005-03 (Netzwerkteil), TC-RQ013-02	Firmware-Upload per HTTP (kombiniert mit Setup C, siehe unten)
TC-RQ007-03										HTTP-Verbindungen offenhalten
TC-RQ009-04										Acyclic-Write-Versuch außerhalb Param-Phase
TC-RQ010-02/03/04									Flood/Fuzzing – hier willst du keine Inline-Bridge, weil die selbst zum Flaschenhals würde
TC-RQ011-02										DCP ist Broadcast-basiert, jeder Port im Segment sieht/sendet ihn
TC-RQ014-01/03/04									HTTP-Requests gegen IoT-Core



**Setup B-Inline** – echte Frame-Unterdrückung nötig
Testfall				Warum reguläres Senden NICHT reicht
TC-RQ001-04 (zwingend)			Kern des Tests ist explizit "suppress the legitimate producer" – ohne Inline-Position unmöglich
TC-RQ002-03, TC-RQ005-02		Laut deiner eigenen Gap-Analyse in RQ-001 kollidieren zwei parallel aktive Producer an der Consecutive-Number – ein gefälschtes Frame würde bei noch aktivem echtem Producer abgelehnt, nicht 						angenommen. Für das in der Testbeschreibung erwartete Ergebnis "wird akzeptiert" musst du den echten Producer unterdrücken
TC-RQ011-03 (unterstützend)		Erhöht Erfolgswahrscheinlichkeit, da kein Konflikt mit echtem Controller während der Param-Phase
TC-RQ001-05 (Alternative)		Für reproduzierbares, exaktes Timing der Unterbrechung – Alternative: Kabel manuell ziehen (auch ok, dann kein Kali nötig)



**Setup C** – physisch/destruktiv (Ersatzgerät)
Testfall					Warum zwingend Ersatzgerät
TC-RQ002-05, TC-RQ003-03, TC-RQ011-05		Siegel-Entfernung ist irreversibel/beschädigend
TC-RQ005-03, TC-RQ008-03			Firmware-Korruption kann fehlschlagen → Bricking-Risiko

**Rein analytisch** – kein Hardware-Setup nötig



TC-RQ002-04, TC-RQ004-02, TC-RQ005-04, TC-RQ005-05, TC-RQ006-02, TC-RQ009-05, TC-RQ012-03, TC-RQ013-04 (Dokumentenanalyse, Bit-Längen-Argumentation, Datenblatt-Review)



**Problematisch mit Standard-Setup**

TC-RQ007-04: verlangt eine interne COM/SysCom-Unterbrechung – von außen ohne Dev-Mode-Zugriff (der laut Doku im Serienzustand gesperrt ist) kaum sauber auslösbar. Solltest du in deiner Arbeit als Limitation vermerken.

TC-RQ010-01: "rated conformant load" nach Net Load Class III wird normalerweise mit zertifizierten PROFINET-Testgeräten erzeugt – Kali/Scapy kann das nur annähern, nicht vollständig ersetzen.
---
Ja, du kannst alle zehn Testfälle zumindest anstoßen und dokumentieren. Aber du darfst nicht bei allen behaupten, dass sie vollständig oder aussagekräftig durchgeführt wurden. Entscheidend ist die Unterscheidung zwischen PASS/FAIL, nicht anwendbar, nicht vollständig prüfbar und durch die Testumgebung blockiert.

Kurzfazit

Mit deiner aktuellen Testumgebung kannst du:

einige Tests vollständig und sinnvoll durchführen,
einige nur eingeschränkt durchführen,
einige zwar starten, aber kein belastbares PASS/FAIL-Ergebnis für das SRIO erhalten,
einzelne Tests fachlich als nicht anwendbar einstufen.

Die richtige Aussage wäre daher nicht:

„Ich habe alle Tests erfolgreich durchgeführt.“

Sondern:

„Alle vorgesehenen Testfälle wurden hinsichtlich ihrer Anwendbarkeit geprüft. Technisch anwendbare Tests wurden ausgeführt. Nicht anwendbare oder durch die Testumgebung beziehungsweise Geräteschnittstellen begrenzte Tests wurden mit Begründung dokumentiert.“

Das ist fachlich sogar besser, weil du damit nicht nur Checkboxen abarbeitest, sondern die Aussagekraft der Ergebnisse bewertest.

Bewertung der zehn Tests
CM-001: Network Exposure vs. Architecture

Status: vollständig durchführbar

Du kannst das SRIO unter 192.168.0.2 mit Nmap auf TCP- und UDP-Dienste untersuchen. Das Gerät besitzt eine Ethernet-Schnittstelle, PROFINET und einen über HTTP erreichbaren IoT-Core. Die Spezifikation sieht HTTP ausdrücklich vor, während HTTPS, WebSocket und MQTT nicht unterstützt werden sollen.

Wichtig ist, dass du für das Ergebnis eine erwartete Port- und Diensteliste brauchst. Ohne diese kannst du zwar einen Scan durchführen, aber nicht zuverlässig zwischen beabsichtigtem und unbeabsichtigtem Dienst unterscheiden. Das Security Framework setzt eine solche Architektur- oder Portmatrix ausdrücklich voraus.

Möglicher Ergebnisstatus:

PASS, wenn ausschließlich erwartete Dienste gefunden werden
FAIL, wenn unerwartete Dienste offen sind
INCONCLUSIVE, wenn keine freigegebene Portmatrix zum Vergleich vorliegt
CM-002: Network Segmentation

Status: in deiner aktuellen Topologie nicht sinnvoll prüfbar

Alle Geräte befinden sich im selben Subnetz 192.168.0.0/24 und in derselben Broadcast-Domain. Es gibt keine getrennte Zone A und Zone B und keinen dokumentierten Firewall-Conduit zwischen diesen Zonen.

Du kannst zwar den im Framework genannten Nmap-Befehl ausführen. Das Ergebnis wäre aber kein gültiger Nachweis einer Netzwerksegmentierung, weil es in deiner Testumgebung aktuell gar keine Segmentgrenze gibt. Der Test würde lediglich bestätigen, dass Geräte im selben Netz erreichbar sind.

Richtige Dokumentation:

NOT APPLICABLE / ENVIRONMENT LIMITATION
 Der Test wurde auf Anwendbarkeit geprüft. Die Testumgebung enthält nur ein gemeinsames Layer-2-Subnetz ohne separate Zonen oder Firewall-Conduits. Daher kann keine Cross-Segment-Exposure bewertet werden.

Falls du unbedingt eine Ausführung nachweisen möchtest, kannst du einen Baseline-Scan durchführen. Kennzeichne ihn aber nur als:

EXECUTED, BUT NOT VALID FOR SEGMENTATION VERIFICATION

CM-003: Default / Weak Credentials

Status: wahrscheinlich nicht anwendbar oder nur stark eingeschränkt

Das Framework setzt ein Login-Interface wie Web-Login, SSH, Telnet oder FTP voraus.

Beim SRIO ist der IoT-Core laut Systemarchitektur grundsätzlich nur für nicht sicherheitsrelevante Informationen gedacht. Die Architektur beschreibt den IoT-Zugriff als read-only und sagt ausdrücklich, dass aktuell kein Passwort implementiert werden muss. Der Firmware-Update-Zugang wird stattdessen durch Drehschalterstellung 999 und Neustart geschützt.

Hydra gegen eine nicht vorhandene Anmeldemaske auszuführen, prüft daher keine Kennwortsicherheit.

Sinnvolle Vorgehensweise:

Mit CM-001 prüfen, ob SSH, Telnet, FTP oder weitere Login-Dienste existieren.
Den Webzugang manuell auf Login- oder Authentifizierungsmechanismen prüfen.
Wenn kein Login vorhanden ist:

NOT APPLICABLE: No credential-based authentication interface exposed

Wenn unerwartet ein Login-Dienst gefunden wird, kann Hydra gezielt und nur im isolierten Labor eingesetzt werden.

Nicht machen: Hydra blind gegen den HTTP-Port laufen lassen und anschließend „PASS“ eintragen. Das wäre kein gültiger Nachweis.

CM-004: RBAC / Privilege Escalation

Status: für dieses Gerät wahrscheinlich nicht anwendbar

Der Test benötigt:

eine Rollen- und Berechtigungsmatrix,
mehrere Benutzerrollen,
mindestens ein Konto pro Rolle,
geschützte Endpunkte oder Objekte.

Das Framework weist selbst darauf hin, dass viele Embedded-Geräte beziehungsweise der IoT-Core nur einen administrativen Zugriff oder keine differenzierten Rollen besitzen.

Für das SRIO wird aktuell kein rollenbasierter Zugriff beschrieben. Die IoT-Core-Daten sind überwiegend lesbar, Firmware-Funktionen werden über den Gerätezustand beziehungsweise die Schalterstellung eingeschränkt.

Du kannst ZAP trotzdem als Proxy starten und die Weboberfläche erfassen. Das ist dann aber eher eine Web-Interface-Analyse, kein gültiger RBAC-Test.

Richtige Einstufung:

NOT APPLICABLE: The DUT does not implement multiple user roles or a role-based authorization model.

Optional kannst du ergänzen:

ZAP traffic capture was performed to verify whether undocumented role- or session-based endpoints are present. No RBAC test could be executed because no role matrix and no separate user roles exist.

CM-005: TLS Configuration

Status: Test ausführbar, Anforderung selbst nicht anwendbar

Laut Kommunikationsspezifikation soll das SRIO HTTP unterstützen und HTTPS ausdrücklich nicht unterstützen.

Du kannst sslscan gegen typische TLS-Ports ausführen. Wenn kein TLS-Endpunkt vorhanden ist, bedeutet das aber nicht automatisch PASS. Es bedeutet zunächst:

NOT APPLICABLE: The device has no TLS endpoint by design.

Es kann zusätzlich ein sicherheitsrelevanter Architekturhinweis entstehen:

Das Gerät stellt HTTP im Klartext bereit und muss deshalb gemäß vorgesehenem Einsatzfall in einem kontrollierten, geschützten Netzwerk betrieben werden.

Die SRIO-Anforderungen gehen ohnehin von einem Einsatz in einer sicheren Zone hinter einer Firewall aus.

Dokumentation:

SSLscan-Ausgabe speichern
Nmap-Ergebnis für 443 und andere TLS-Ports beilegen
mit der Spezifikation vergleichen
Ergebnis als N/A by design, nicht als PASS, kennzeichnen
CM-006: Hardening Validation mit Lynis

Status: auf dem SRIO nicht durchführbar

Lynis muss lokal auf dem zu prüfenden Linux-System laufen oder benötigt administrativen Shell-Zugang. Das Framework nennt Root- beziehungsweise Admin-Zugriff als Voraussetzung.

Das SRIO ist kein allgemeines Linux-Zielsystem mit SSH-Shell, auf dem du Lynis installieren oder starten kannst. Die Architektur beschreibt Embedded-Controller, NetX90, µC/OS-II beziehungsweise interne Firmware-Komponenten, nicht ein zugängliches Linux-System.

Du könntest Lynis auf deinem Kali-Rechner ausführen, aber damit würdest du Kali und nicht das SRIO testen.

Richtige Einstufung:

NOT EXECUTABLE ON DUT: Lynis requires local or administrative OS access. The SRIO does not expose a supported operating-system shell.

Optional wäre eine alternative Hardening-Prüfung möglich, zum Beispiel:

Diensteminimierung über Nmap,
Prüfung von Debug-Schnittstellen,
Firmware-Konfiguration,
Produktions-Fuses,
SBOM- und Komponentenprüfung.

Aber diese alternative Prüfung darf nicht ohne Weiteres als „Lynis PASS“ eingetragen werden.

CM-007: Debug / Service Interface Exposure

Status: teilweise durchführbar

Der Web-Teil ist durchführbar:

Nmap auf offene Dienste,
Nikto gegen den HTTP-Endpunkt,
Prüfung auf versteckte Verwaltungs- und Debugpfade,
Prüfung auf Serverbanner und Defaultdateien.

Das Gerät soll allerdings interne Debug- und Testinterfaces besitzen, wobei deren Zugriff nach der Entwicklungsphase gesperrt werden soll.

Nikto kann keine physischen UART-, JTAG-, SWD- oder PCB-Kontaktflächen untersuchen. Deshalb besteht CM-007 aus zwei Teilen:

Netzwerk-/Webprüfung: in deiner Umgebung möglich
Physische Debugprüfung: nur mit Hardwarezugang, Schaltplan beziehungsweise PCB-Dokumentation und passender Messtechnik möglich

Möglicher Ergebnisstatus:

PARTIALLY EXECUTED
 Network and web exposure were tested using Nmap and Nikto. Physical debug interfaces were not tested because hardware access and interface equipment were outside the available test setup.

CM-008: Patch Level / Known CVEs

Status: technisch ausführbar, aber nur bedingt belastbar

Du kannst einen GVM/OpenVAS-Scan gegen 192.168.0.2 durchführen. Das Framework verlangt aber zusätzlich:

einen aktuellen GVM-Feed,
die aktuelle SBOM,
einen Vergleich gefundener Versionen und Komponenten mit der SBOM.

Bei Embedded-Geräten erkennt ein Netzwerkscanner häufig nur erreichbare Dienste. Nicht über das Netzwerk sichtbare Bibliotheken, Bootloader, PROFINET-Stacks und Firmwarekomponenten werden möglicherweise nicht erkannt.

Bewertung:

mit aktuellem Feed und SBOM: weitgehend sinnvoll
ohne SBOM: nur Netzwerk-Vulnerability-Scan
ohne aktuellen Feed: kein belastbares Ergebnis

Passende Einstufung ohne SBOM:

PARTIALLY EXECUTED / INCONCLUSIVE
 The network vulnerability scan was completed. A complete patch-level assessment was not possible because no validated SBOM was available for correlation.

CM-009: Load Behavior & Logging

Status: eingeschränkt durchführbar, mit Vorsicht

Der IoT-Core ist über HTTP erreichbar und die Spezifikation erlaubt maximal zwei aktive HTTP-Verbindungen.

Der Beispieltest aus dem Framework verwendet 50 parallele Benutzer. Das wäre für ein Gerät, dessen Spezifikation nur zwei aktive Verbindungen vorsieht, keine normale Lastprüfung, sondern eher ein absichtlicher Überlast- oder Robustheitstest. Das ist nicht automatisch falsch, muss aber so benannt werden.

Außerdem soll während des Tests geprüft werden:

ob PROFIsafe stabil bleibt,
ob das Gerät in einen sicheren Zustand wechselt,
ob Neustarts auftreten,
ob Fehler im Error Log oder in der SPS-Diagnose erscheinen.

Das SRIO verfügt über einen Error Log, der über den IoT-Core lesbar sein soll, und Fehler sollen zusätzlich als PROFINET-Diagnose an die SPS gesendet werden.

Empfehlung:

zuerst 1 bis 2 parallele Verbindungen als Sollbereich,
danach stufenweise Überlast,
SPS, P-LED, FS-LED, DI/DO-Signale und Error Log überwachen,
Switch-Storm-Control dokumentieren.

Status: FULLY EXECUTABLE, sofern Monitoring und Logging verfügbar sind. Ohne Zugriff auf die Logs nur PARTIALLY EXECUTED.

CM-010: Fuzzing / Robustness

Status: grundsätzlich möglich, aber nicht mit einem generischen Skript vollständig

Das Framework verlangt eine genaue Protokollspezifikation und ein an das Protokoll angepasstes boofuzz-Skript.

Für das SRIO sind mehrere unterschiedliche Angriffsflächen vorhanden:

HTTP / IoT-Core,
PROFINET DCP,
PROFINET RT,
PROFIsafe innerhalb von PROFINET,
gegebenenfalls Firmware-Upload im Update-Modus.

Ein einfaches TCP-boofuzz-Beispiel prüft nur einen TCP-Dienst. PROFINET RT und PROFIsafe laufen nicht einfach als gewöhnliche TCP-Verbindung. Deine Testumgebung weist bereits darauf hin, dass für PROFINET/DCP Scapy beziehungsweise entsprechende Protokollerweiterungen benötigt werden.

Hinzu kommt: Kali hängt an einem normalen Switch-Port. Es kann zusätzliche Frames an das SRIO senden, aber den legitimen zyklischen SPS-SRIO-Verkehr nicht unterdrücken oder ersetzen. Ein echtes Inline-MITM ist ohne zweite Netzwerkschnittstelle beziehungsweise transparente Bridge nicht möglich.

Daher:

HTTP-Fuzzing: möglich
DCP-/zusätzliche PROFINET-Frames: möglich
Mitschnitt mit Port-Mirroring: möglich
legitime PROFIsafe-Telegramme ersetzen oder unterdrücken: nicht möglich
Firmware-Fuzzing: nur im Update-Modus und mit Recovery-Plan
vollständige Protokollrobustheit: mit aktueller Topologie nicht nachweisbar

Richtiger Status:

PARTIALLY EXECUTED oder ENVIRONMENT LIMITATION

Zusammenfassung
Test	BewertungCM-001 Network Exposure	vollständig durchführbar
CM-002 Segmentation	nicht sinnvoll prüfbar, keine Zonen vorhanden
CM-003 Credentials	wahrscheinlich nicht anwendbar
CM-004 RBAC	nicht anwendbar, keine Rollen
CM-005 TLS	scanbar, aber TLS ist laut Design nicht vorhanden
CM-006 Lynis	nicht auf dem SRIO ausführbar
CM-007 Debug Interfaces	Netzwerk ja, physische Interfaces separat
CM-008 CVEs	eingeschränkt, SBOM und aktueller Feed erforderlich
CM-009 Load & Logging	durchführbar, aber Lastprofil anpassen und überwachen
CM-010 Fuzzing	teilweise durchführbar, kein Inline-MITM
Empfohlenes Ergebnisschema

Nutze nicht nur PASS und FAIL, sondern mindestens:

PASS: vollständig ausgeführt, Akzeptanzkriterium erfüllt
FAIL: vollständig ausgeführt, Akzeptanzkriterium verletzt
N/A: Test fachlich nicht auf das Gerät anwendbar
BLOCKED: Test wäre anwendbar, kann mit der aktuellen Umgebung aber nicht ausgeführt werden
PARTIAL: nur ein Teil des Testumfangs wurde geprüft
INCONCLUSIVE: ausgeführt, aber erforderliche Referenzdaten fehlen
NOT EXECUTED: nicht durchgeführt
Gute Formulierung für dein Testprotokoll

Der Testfall wurde hinsichtlich seiner Anwendbarkeit auf das SRIO und der Durchführbarkeit in der vorhandenen Testumgebung bewertet. Die technisch möglichen Testschritte wurden ausgeführt und die Rohdaten als Evidence gespeichert. Aufgrund der fehlenden beziehungsweise nicht implementierten Geräteeigenschaft konnte kein vollständiges PASS/FAIL-Ergebnis ermittelt werden. Der Test wird daher als N/A, PARTIAL, BLOCKED oder INCONCLUSIVE dokumentiert.

Damit kannst du ehrlich sagen, dass du alle Testfälle bearbeitet und bewertet hast, ohne vorzugeben, dass jeder Test auf deinem Gerät vollständig möglich war.
---
Ja, dein Befehl für CM-002 ist syntaktisch grundsätzlich richtig, sofern Kali tatsächlich über eth1 mit dem Testnetz verbunden ist. Wichtig: Da Kali und SRIO im gleichen Subnetz liegen, prüft dieser Scan nur die Erreichbarkeit, nicht die Segmentierung zwischen zwei Zonen.

Die folgenden Befehle sind ausschließlich für dein isoliertes und freigegebenes SRIO-Testnetz mit dem Ziel 192.168.0.2 gedacht. Besonders CM-003, CM-009 und CM-010 können das Gerät belasten.

0. Vorbereitung
Arbeitsverzeichnis anlegen
mkdir -p ~/srio_security_tests
cd ~/srio_security_tests

Netzwerkschnittstelle feststellen
ip -br addr
ip route get 192.168.0.2


In der Ausgabe von ip route get steht hinter dev die verwendete Schnittstelle, beispielsweise eth1.

Optional automatisch speichern:

IFACE=$(ip route get 192.168.0.2 | awk '/dev/ {for(i=1;i<=NF;i++) if($i=="dev") print $(i+1); exit}')
echo "$IFACE"

Erreichbarkeit prüfen
ping -c 4 192.168.0.2


Wenn Ping nicht beantwortet wird, bedeutet das nicht zwingend, dass das Gerät nicht erreichbar ist. Deshalb wird bei Nmap teilweise -Pn verwendet.

Tool-Versionen protokollieren
{
    date -Is
    uname -a
    ip -br addr
    nmap --version
    hydra -h 2>&1 | head -n 3
    sslscan --version 2>&1
    nikto -Version 2>&1
    siege --version 2>&1
    python3 --version
} | tee test_environment.txt

CM-001: Network Exposure vs. Architecture

Hier solltest du sowohl TCP als auch UDP prüfen. Nmap kann mit -sS einen SYN-Scan, mit -sV eine Diensterkennung und mit -sU einen UDP-Scan durchführen.

Vollständiger TCP-Scan
sudo nmap -sS -sV -Pn -p- -T3 --reason \
  -oA cm001_srio_tcp \
  192.168.0.2

UDP Top 200
sudo nmap -sU -sV -Pn --top-ports 200 -T3 --reason \
  -oA cm001_srio_udp \
  192.168.0.2


Das kann deutlich länger dauern.

Ergebnisse anzeigen
cat cm001_srio_tcp.nmap
cat cm001_srio_udp.nmap

Erwartung dokumentieren

Das SRIO soll HTTP unterstützen. HTTPS, MQTT und WebSocket sollen laut Kommunikationsspezifikation dagegen nicht unterstützt werden.

grep -E "^[0-9]+/(tcp|udp).*open" cm001_srio_*.nmap | tee cm001_open_ports.txt


Bewertung:

Nur erwartete Dienste: PASS
Unerwarteter Dienst: FAIL
Keine freigegebene Portmatrix: INCONCLUSIVE
CM-002: Network Segmentation

Dein Befehl ist verwendbar:

sudo nmap -sS -Pn -p 1-65535 -e eth1 \
  -oA cm002_kali_to_srio \
  192.168.0.2


Ich würde ihn leicht erweitern:

sudo nmap -sS -sV -Pn -p- -T3 --reason \
  -e "$IFACE" \
  -oA cm002_kali_to_srio \
  192.168.0.2

Prüfen, ob eth1 wirklich korrekt ist
ip link show eth1
ip addr show eth1
ip route get 192.168.0.2


Falls ip route get zum Beispiel dev eth0 meldet, musst du eth0 statt eth1 verwenden.

Dokumentationsdatei anlegen
cat > cm002_assessment.txt <<'EOF'
Result: ENVIRONMENT LIMITATION

The scan from the Kali system to the SRIO was executed.
However, Kali and SRIO are located in the same IP subnet and the same
Layer-2 broadcast domain. No firewall, VLAN boundary, or zone conduit
exists between the systems. Therefore, this execution demonstrates
reachability but does not verify cross-segment isolation.
EOF


Deine Testumgebung enthält aktuell nur ein gemeinsames Subnetz und keine getrennten Sicherheitszonen. Daher ist der Scan kein vollständiger Segmentierungsnachweis.

CM-003: Default / Weak Credentials

Beim SRIO ist zunächst zu prüfen, ob überhaupt ein Login-Dienst vorhanden ist. Die Architektur beschreibt den IoT-Core aktuell ohne Passwortschutz, da der Zugriff im Wesentlichen lesend ist und Firmware-Updates durch die Drehschalterstellung 999 geschützt werden.

Schritt 1: Login-Dienste suchen
sudo nmap -sS -sV -Pn \
  -p 21,22,23,80,443,8080,8443 \
  --script http-title,http-auth-finder \
  -oA cm003_login_interfaces \
  192.168.0.2

Schritt 2: HTTP-Seite speichern
curl --max-time 10 -v \
  http://192.168.0.2/ \
  -o cm003_http_root.html \
  2> cm003_http_headers.txt

Schritt 3: Nach typischen Login-Begriffen suchen
grep -Eio \
  'login|username|password|signin|authentication|authorization' \
  cm003_http_root.html \
  | sort -u \
  | tee cm003_login_terms.txt

Falls kein Login vorhanden ist
cat > cm003_assessment.txt <<'EOF'
Result: NOT APPLICABLE

The DUT was checked for reachable credential-based interfaces.
No SSH, Telnet, FTP, or authenticated web login interface was identified.
Hydra testing was therefore not applicable to this DUT.
EOF

Nur falls tatsächlich SSH gefunden wurde

Erstelle eine sehr kleine, projektspezifisch freigegebene Testliste. Nutze keine große öffentliche Passwortliste:

printf '%s\n' admin root user > cm003_users.txt
printf '%s\n' admin password root > cm003_passwords.txt


Dann nur innerhalb des genehmigten Testfensters:

hydra -L cm003_users.txt -P cm003_passwords.txt \
  -t 1 -W 3 -f \
  -o cm003_hydra_ssh.txt \
  ssh://192.168.0.2


Falls eine Sperrung oder Verzögerung auftritt, Test abbrechen:

pkill -INT hydra


Wichtig: Ohne existierende Anmeldeschnittstelle ist das Ergebnis N/A, nicht PASS.

CM-004: RBAC / Privilege Escalation

Der Test ist nur vollständig sinnvoll, wenn verschiedene Rollen oder Benutzerkonten existieren. Beim SRIO ist kein Mehrrollenmodell dokumentiert.

Du kannst trotzdem ZAP starten und die Weboberfläche erfassen.

ZAP als lokalen Proxy starten
zaproxy -daemon \
  -host 127.0.0.1 \
  -port 8090 \
  -config api.disablekey=true \
  > cm004_zap_daemon.log 2>&1 &


Kurz warten:

sleep 10

Prüfen, ob ZAP läuft
curl -s \
  "http://127.0.0.1:8090/JSON/core/view/version/" \
  | tee cm004_zap_version.json

SRIO über den ZAP-Proxy abrufen
curl -x http://127.0.0.1:8090 \
  --max-time 15 \
  http://192.168.0.2/ \
  -o cm004_srio_via_zap.html

Passive Ergebnisse abrufen
curl -s \
  "http://127.0.0.1:8090/JSON/core/view/alerts/?baseurl=http%3A%2F%2F192.168.0.2" \
  -o cm004_zap_alerts.json

HTML-Bericht exportieren
curl -s \
  "http://127.0.0.1:8090/OTHER/core/other/htmlreport/" \
  -o cm004_zap_report.html

ZAP beenden
curl -s \
  "http://127.0.0.1:8090/JSON/core/action/shutdown/"

Ergebnis dokumentieren
cat > cm004_assessment.txt <<'EOF'
Result: NOT APPLICABLE

The web interface was captured through OWASP ZAP.
No multiple user roles, separate role accounts, or RBAC permission matrix
were available for the DUT. Therefore, horizontal and vertical privilege
escalation could not be evaluated as an RBAC test.
EOF


Ich würde hier zunächst keinen aktiven ZAP-Scan ausführen. Das manuelle Aufzeichnen reicht für den Nachweis, dass die Anwendbarkeit geprüft wurde.

CM-005: TLS Configuration

Das Gerät soll HTTP, aber kein HTTPS unterstützen. Ein TLS-Scan dient daher in erster Linie dazu, unerwartete TLS-Endpunkte auszuschließen.

Typische TLS-Ports prüfen
sudo nmap -sS -sV -Pn \
  -p 443,8443,9443 \
  --script ssl-enum-ciphers,ssl-cert \
  -oA cm005_tls_ports \
  192.168.0.2

SSLscan auf Port 443
sslscan --show-certificate \
  192.168.0.2:443 \
  2>&1 | tee cm005_sslscan_443.txt

Optional Port 8443
sslscan --show-certificate \
  192.168.0.2:8443 \
  2>&1 | tee cm005_sslscan_8443.txt

HTTP-Klartextzugriff dokumentieren
curl --max-time 10 -v \
  http://192.168.0.2/ \
  -o /dev/null \
  2> cm005_http_cleartext.txt

Ergebnisdatei
cat > cm005_assessment.txt <<'EOF'
Result: NOT APPLICABLE BY DESIGN

No TLS endpoint was detected. The DUT supports HTTP but does not support
HTTPS according to its design specification. Therefore, TLS cipher and
certificate configuration cannot be assessed. Cleartext HTTP exposure
must be considered in the intended protected-network deployment.
EOF

CM-006: Hardening Validation mit Lynis

Lynis muss auf dem geprüften Betriebssystem selbst laufen. Es kann nicht von Kali aus über das Netzwerk gegen das SRIO ausgeführt werden. Das Framework verlangt lokalen oder administrativen Betriebssystemzugriff.

Prüfen, ob administrativer Shell-Zugang vorhanden ist
sudo nmap -sS -sV -Pn \
  -p 22,23 \
  -oA cm006_admin_access \
  192.168.0.2

Nur Kali selbst prüfen, deutlich als Kontrolltest markieren
sudo lynis audit system \
  --no-colors \
  --logfile cm006_kali_only.log \
  --report-file cm006_kali_only_report.dat


Dieser Befehl prüft ausschließlich deinen Kali-Rechner, nicht das SRIO.

Bewertung dokumentieren
cat > cm006_assessment.txt <<'EOF'
Result: BLOCKED / NOT EXECUTABLE ON DUT

Lynis requires local execution or administrative operating-system access.
The SRIO does not expose a supported shell for running Lynis.
A Lynis audit of the Kali test host, if performed, is not a hardening
assessment of the DUT.
EOF

CM-007: Debug / Service Interface Exposure
Nikto gegen HTTP starten
nikto \
  -h http://192.168.0.2 \
  -output cm007_nikto.html \
  -Format html

Gleichzeitig Dienstescan durchführen
sudo nmap -sS -sV -Pn -p- -T3 \
  --script banner,http-title,http-headers,http-methods \
  -oA cm007_service_exposure \
  192.168.0.2

Typische Debug- und Administrationspfade vorsichtig prüfen
for path in \
  debug diagnostics diag admin console status test swagger api-docs \
  .git/config config backup
do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time 5 \
    "http://192.168.0.2/$path")
  printf "%-20s %s\n" "/$path" "$code"
done | tee cm007_path_check.txt

HTTP-Methoden separat prüfen
curl -i -X OPTIONS \
  --max-time 10 \
  http://192.168.0.2/ \
  | tee cm007_http_options.txt


Das Gerät besitzt laut Anforderungen Debug- und Testinterfaces für die Entwicklungsphase. Diese sollen nach der Entwicklung nicht mehr zugänglich sein. Eine Netzprüfung kann jedoch keine physischen PCB-, UART-, SWD- oder JTAG-Kontakte bewerten.

Bewertung
cat > cm007_assessment.txt <<'EOF'
Result: PARTIALLY EXECUTED

Network services and web-accessible debug paths were tested with Nmap,
Nikto, curl, and HTTP method enumeration. Physical debug interfaces such
as PCB contact planes, UART, SWD, or JTAG were outside the available
network test setup and were not evaluated.
EOF

CM-008: Patch Level / Known CVEs mit GVM
GVM-Installation prüfen
command -v gvm-start
command -v gvm-check-setup


Falls nicht installiert:

sudo apt update
sudo apt install -y gvm gvm-tools

Einmalige Einrichtung
sudo gvm-setup


Das kann längere Zeit dauern.

Setup prüfen
sudo gvm-check-setup | tee cm008_gvm_setup_check.txt

Feeds aktualisieren

Je nach Kali-Version:

sudo greenbone-feed-sync


Anschließend:

sudo gvm-start

Weboberfläche öffnen
xdg-open https://127.0.0.1:9392


In der GVM-Weboberfläche:

Configuration → Targets
Neues Target anlegen
Name: CM008-SRIO
Hosts: 192.168.0.2
Alive Test möglichst auf Consider Alive oder geeignete lokale Erkennung setzen
Scans → Tasks
Task mit dem SRIO-Target erstellen
Zunächst einen normalen, nicht destruktiven Scan wählen
Scan starten
Bericht als PDF und XML exportieren
Dienste zusätzlich für SBOM-Abgleich speichern
sudo nmap -sS -sV -Pn -p- \
  -oA cm008_service_versions \
  192.168.0.2

Ergebnisbewertung
cat > cm008_assessment.txt <<'EOF'
Result: PARTIAL PENDING SBOM CORRELATION

A network vulnerability scan of the SRIO was performed using GVM.
The result covers network-visible services only. A complete patch-level
assessment additionally requires correlation with the validated device
SBOM, firmware version, bootloader version, fieldbus stack, and embedded
software components.
EOF


Das Framework verlangt für eine vollständige Bewertung sowohl einen aktuellen GVM-Feed als auch einen Vergleich mit der aktuellen SBOM.

CM-009: Load Behavior & Logging

Das SRIO soll maximal zwei aktive HTTP-Verbindungen unterstützen. Daher solltest du nicht unmittelbar mit -c 50 beginnen.

Baseline vor dem Test
{
    date -Is
    ping -c 10 192.168.0.2
    curl -sS --max-time 10 -D - http://192.168.0.2/ -o /dev/null
} | tee cm009_before.txt

Schonender Sollbereich: eine Verbindung, eine Minute
siege -c 1 -t 1M -v \
  http://192.168.0.2/ \
  2>&1 | tee cm009_c1_1m.log

Vorgesehene maximale Verbindungsanzahl: zwei Verbindungen
siege -c 2 -t 5M -v \
  http://192.168.0.2/ \
  2>&1 | tee cm009_c2_5m.log

Nur falls ausdrücklich als Überlasttest freigegeben
siege -c 5 -t 1M -v \
  http://192.168.0.2/ \
  2>&1 | tee cm009_overload_c5_1m.log


Ich würde nicht direkt auf 50 gleichzeitige Verbindungen gehen.

Parallel Mitschnitt starten

Vor dem Siege-Test in einem zweiten Terminal:

sudo tcpdump -i "$IFACE" \
  -nn host 192.168.0.2 \
  -w cm009_traffic.pcap


Beenden mit Ctrl+C.

Erreichbarkeit nach dem Test
{
    date -Is
    ping -c 10 192.168.0.2
    curl -sS --max-time 10 -D - http://192.168.0.2/ -o /dev/null
} | tee cm009_after.txt


Während des Tests solltest du zusätzlich beobachten:

SPS bleibt in RUN
sichere Kommunikation bleibt vorhanden oder erholt sich definiert
P-LED und FS-LED
DI/DO-Verhalten
PROFINET-Diagnose
Error Log des SRIO

Das SRIO soll Fehler im internen Error Log speichern und über IoT-Core beziehungsweise PROFINET-Diagnose zugänglich machen.

CM-010: Fuzzing / Robustness

Hier solltest du nicht direkt PROFIsafe oder Firmware-Upload fuzzing betreiben. Beginne mit dem nicht sicherheitsbezogenen HTTP-Endpunkt. Für PROFINET RT und PROFIsafe reicht ein gewöhnliches TCP-boofuzz-Skript nicht aus; deine Topologie erlaubt außerdem kein Ersetzen oder Unterdrücken des legitimen zyklischen Verkehrs.

Boofuzz installieren
python3 -m venv cm010_venv
source cm010_venv/bin/activate
pip install boofuzz

Endlichen, vergleichsweise kleinen HTTP-Test erstellen
cat > cm010_http_fuzz.py <<'PY'
from boofuzz import (
    Session,
    Target,
    TCPSocketConnection,
    s_initialize,
    s_get,
    s_group,
    s_static,
)

TARGET = "192.168.0.2"
PORT = 80

session = Session(
    target=Target(
        connection=TCPSocketConnection(TARGET, PORT)
    ),
    sleep_time=0.25,
    web_port=26000,
)

s_initialize("http_request")
s_group("method", values=["GET", "HEAD", "OPTIONS"])
s_static(" ")
s_group("path", values=["/", "/deviceinfo", "/devicestatus", "/invalid"])
s_static(" HTTP/1.1\r\n")
s_static("Host: 192.168.0.2\r\n")
s_static("Connection: close\r\n")
s_static("\r\n")

session.connect(s_get("http_request"))
session.fuzz(max_depth=1)
PY

Syntax prüfen
python3 -m py_compile cm010_http_fuzz.py

Vorher Erreichbarkeit dokumentieren
ping -c 4 192.168.0.2 | tee cm010_before_ping.txt
curl -sS --max-time 10 -D cm010_before_headers.txt \
  http://192.168.0.2/ \
  -o cm010_before.html

Mitschnitt in separatem Terminal
sudo tcpdump -i "$IFACE" \
  -nn host 192.168.0.2 \
  -w cm010_http_fuzz.pcap

Test starten
source cm010_venv/bin/activate
python3 cm010_http_fuzz.py \
  2>&1 | tee cm010_http_fuzz.log


Boofuzz-Oberfläche:

xdg-open http://127.0.0.1:26000

Nachher prüfen
ping -c 10 192.168.0.2 | tee cm010_after_ping.txt

curl -sS --max-time 10 \
  -D cm010_after_headers.txt \
  http://192.168.0.2/ \
  -o cm010_after.html

Test bei Problemen sofort abbrechen
pkill -INT -f cm010_http_fuzz.py

Bewertung dokumentieren
cat > cm010_assessment.txt <<'EOF'
Result: PARTIALLY EXECUTED

A limited robustness test of the HTTP interface was performed.
The test did not replace or suppress legitimate PROFINET or PROFIsafe
traffic. Full PROFINET/PROFIsafe robustness and inline manipulation were
not covered by the available single-interface switched topology.
EOF

Evidence am Ende zusammenpacken
cd ~/srio_security_tests

find . -maxdepth 1 -type f \
  -printf '%f\n' \
  | sort \
  | tee evidence_file_list.txt

sha256sum ./* 2>/dev/null \
  | tee evidence_sha256.txt


Archiv erzeugen:

tar -czf srio_security_test_evidence.tar.gz \
  --exclude=srio_security_test_evidence.tar.gz \
  .

Empfohlene Ergebniszuordnung

Nach diesen Ausführungen würde ich die CMs voraussichtlich so eintragen:

CM-001: PASS, FAIL oder INCONCLUSIVE
CM-002: ENVIRONMENT LIMITATION
CM-003: N/A, sofern kein Login vorhanden
CM-004: N/A, sofern keine Rollen vorhanden
CM-005: N/A BY DESIGN
CM-006: BLOCKED / NOT EXECUTABLE ON DUT
CM-007: PARTIAL
CM-008: PARTIAL, bis ein SBOM-Abgleich erfolgt ist
CM-009: PASS oder FAIL, sofern Monitoring und Logs verfügbar sind
CM-010: PARTIAL wegen Beschränkung auf HTTP und fehlendem Inline-Zugriff
---
Ja, du kannst die Befehle aus der Zeile**„Commands“ grundsätzlich stumpf ausführen**, nachdem du Ziel-IP, Interface, Port, URL und Dateinamen ersetzt hast. Aber das bedeutet nur: Der Befehl wurde gestartet. Es bedeutet nicht automatisch, dass der jeweilige CM vollständig geprüft wurde oder dass das Ergebnis PASS/FAIL-fähig ist.

Praktisch für deine Dokumentation

Du kannst bei jedem CM festhalten:

Original command from the Security Testing Framework was executed with parameters adapted to the SRIO test environment. Applicability and result validity were evaluated separately.

Damit trennst du sauber:

Execution: Befehl ausgeführt
Applicability: Passt der Test überhaupt zum SRIO?
Result: PASS, FAIL, N/A, BLOCKED oder INCONCLUSIVE
Befehle direkt aus deinem Framework
CM-001: Network Exposure

Das kannst du praktisch direkt übernehmen:

sudo nmap -sS -sV -p- -T3 \
  -oA cm001_srio \
  192.168.0.2


Zusätzlich der UDP-Scan:

sudo nmap -sU --top-ports 200 \
  -oA cm001_srio_udp \
  192.168.0.2


Ja, sinnvoll und direkt verwendbar.

Ergebnis: PASS oder FAIL nur durch Vergleich mit der freigegebenen Portmatrix. Ohne Portmatrix ist der Scan ausgeführt, aber die Bewertung INCONCLUSIVE. Das Framework fordert diesen Vergleich ausdrücklich.

CM-002: Network Segmentation

Dein Befehl:

sudo nmap -sS -Pn -p 1-65535 \
  -e eth1 \
  -oA cm002_kali_to_srio \
  192.168.0.2


Ja, kannst du genau so ausführen.

Prüfe nur vorher:

ip route get 192.168.0.2


Wenn dort dev eth1 steht, passt es. Steht dort dev eth0, musst du eth0 verwenden.

Aber: Da Kali und SRIO im selben Subnetz und derselben Broadcast-Domain liegen, ist das kein echter Cross-Segment-Test.

Dokumentation:

Command executed successfully. Result classified as ENVIRONMENT LIMITATION because no separate network zones or firewall conduit exist in the test setup.

CM-003: Default / Weak Credentials

Hier kannst du den Framework-Befehl nicht ohne weitere Anpassung verwenden:

hydra -L users.txt -P passwords.txt \
  192.168.0.2 \
  http-post-form \
  "/login:username=^USER^&password=^PASS^:Login failed"


Der Befehl funktioniert nur, wenn das SRIO wirklich:

eine Seite /login besitzt,
Parameter namens username und password erwartet,
bei einem falschen Login den Text Login failed zurückgibt.

Diese Werte im Framework sind lediglich ein Beispiel. Das SRIO hat nach der vorliegenden Architektur kein dokumentiertes passwortbasiertes Web-Login.

Du kannst den Befehl technisch trotzdem eingeben, aber Hydra würde dann wahrscheinlich nur Fehler oder bedeutungslose Ergebnisse erzeugen.

Fazit: Erst Anmeldeschnittstelle ermitteln. Wenn keine existiert:

Command not applicable because the DUT does not provide a credential-based login interface.

CM-004: RBAC / Privilege Escalation

Den ersten Befehl kannst du direkt verwenden:

zaproxy -daemon \
  -host 127.0.0.1 \
  -port 8090 \
  -config api.disablekey=true


Der Scan-Befehl lässt sich ebenfalls anpassen:

curl "http://127.0.0.1:8090/JSON/ascan/action/scan/?url=http://192.168.0.2"


Bericht:

curl \
  "http://127.0.0.1:8090/OTHER/core/other/htmlreport/" \
  -o cm004_srio_report.html


Die Befehle kannst du ausführen. Der eigentliche RBAC-Test funktioniert aber nur mit unterschiedlichen Rollen und Konten. Der ZAP-Scan allein beweist nicht, dass es keine horizontale oder vertikale Rechteausweitung gibt. Genau deshalb bezeichnet das Framework den manuellen Rollentest als Kern des CM-004.

Wenn das SRIO keine Rollen hat:

ZAP command executed. RBAC test classified as NOT APPLICABLE because the DUT implements no multiple user roles.

CM-005: TLS Configuration

Framework-Befehl angepasst:

sslscan 192.168.0.2:443 \
  --show-certificate \
  > cm005_srio.txt


Ja, kannst du stumpf ausführen.

Wahrscheinlich meldet SSLscan, dass keine TLS-Verbindung hergestellt werden konnte, weil das SRIO laut Spezifikation HTTP unterstützt, HTTPS aber nicht.

Das ist dann kein Toolfehler. Dokumentiere:

Command executed. No TLS endpoint was available. CM-005 is NOT APPLICABLE BY DESIGN.

CM-006: Hardening Validation

Framework-Befehl:

sudo lynis audit system \
  --no-colors \
  --logfile cm006_srio.log \
  --report-file cm006_srio_report.dat


Diesen Befehl solltest du nicht einfach auf Kali ausführen und als SRIO-Test verbuchen.

Lynis prüft immer das Betriebssystem, auf dem der Befehl läuft. Wenn du ihn im Kali-Terminal startest, testest du Kali, nicht 192.168.0.2. Im Framework steht deshalb keine Ziel-IP im Lynis-Befehl. Als Voraussetzung wird lokaler oder administrativer Zugriff auf das Zielsystem genannt.

Wenn du ihn trotzdem zum Nachweis ausführst:

sudo lynis audit system \
  --no-colors \
  --logfile cm006_kali_not_srio.log \
  --report-file cm006_kali_not_srio_report.dat


Dokumentation:

Lynis was executed on the Kali test host for tool verification only. The command could not be executed on the SRIO because no supported shell or administrative operating-system access is available. Result: BLOCKED ON DUT.

Das ist der wichtigste CM, bei dem „stumpf ausführen“ sonst zu einer falschen Aussage führen würde.

CM-007: Debug / Service Interface Exposure

Framework-Befehl angepasst:

nikto -h http://192.168.0.2 \
  -output cm007_srio.html \
  -Format html


Ja, direkt verwendbar.

Der Befehl prüft jedoch nur das Webinterface. Physische Debug-Schnittstellen wie UART, JTAG, SWD oder Kontaktflächen prüft Nikto nicht. Das Framework weist ausdrücklich darauf hin, dass dafür eine zusätzliche Hardwareprüfung nötig ist.

Dokumentation:

Nikto web-interface test executed. Physical debug interfaces were outside the test scope. Result: PARTIAL.

CM-008: Known CVEs

Die Befehle aus dem Framework kannst du grundsätzlich verwenden:

sudo gvm-start


Dann die Weboberfläche öffnen:

xdg-open https://127.0.0.1:9392


In GVM legst du das Ziel 192.168.0.2 an und startest den Scan.

Der gezeigte gvm-cli-Befehl im Framework erstellt allerdings nur ein Target:

gvm-cli \
  --gmp-username admin \
  --gmp-password 'DEIN_PASSWORT' \
  socket \
  --xml "<create_target><name>cm008_srio</name><hosts>192.168.0.2</hosts></create_target>"


Das allein startet noch keinen vollständigen Scan. Dafür müssen zusätzlich eine Task, eine Scan-Konfiguration und ein Scanner zugeordnet werden. Deshalb ist für dich die Weboberfläche wahrscheinlich einfacher.

Ja, Framework-Anweisungen verwenden, aber ohne aktuelle Feeds und SBOM-Abgleich ist das Ergebnis nur teilweise belastbar. Das Framework verlangt beide Voraussetzungen.

CM-009: Load Behavior & Logging

Framework-Befehl angepasst:

siege -c 50 -t 10M -v \
  http://192.168.0.2/ \
  -l cm009_srio.log


Technisch kannst du ihn genau so eingeben.

Aber 50 bedeutet 50 simulierte gleichzeitige Benutzer beziehungsweise Verbindungen für zehn Minuten. Das SRIO soll laut Spezifikation nur zwei aktive HTTP-Verbindungen unterstützen.

Damit wäre dein Test kein normaler Lasttest im vorgesehenen Bereich, sondern ein deutlicher Überlasttest. Wenn genau das beabsichtigt und freigegeben ist, kannst du ihn ausführen. Wenn du erst einmal sicher anfangen möchtest:

siege -c 2 -t 10M -v \
  http://192.168.0.2/ \
  -l cm009_srio.log


Wenn du den Originalbefehl mit -c 50 nutzt, dokumentiere:

The framework example load of 50 concurrent users was executed as an overload test. The specified DUT limit is two active HTTP connections.

Währenddessen müssen SPS, PROFIsafe, LEDs, Ein-/Ausgänge und Logs überwacht werden. Sonst kannst du nur die HTTP-Antworten bewerten, nicht das vollständige CM-Akzeptanzkriterium.

CM-010: Fuzzing

Das Beispiel aus dem Framework:

from boofuzz import *

session = Session(
    target=Target(
        connection=TCPSocketConnection("192.168.0.2", 80)
    )
)

s_initialize("request")
s_string("USER")
s_delim(" ")
s_string("value")

session.connect(s_get("request"))
session.fuzz()


Ausführen:

python3 cm010_fuzz.py


Du kannst es ausführen, aber es ist nur ein Gerüst. Der Inhalt USER value ist kein gültiger HTTP-Request und wahrscheinlich auch kein gültiger Request für irgendeine andere SRIO-Schnittstelle.

Das Framework sagt ausdrücklich, dass das Skript an das konkret geprüfte Protokoll angepasst werden muss.

Wenn du das unveränderte Beispiel ausführst, kannst du nur sagen:

The boofuzz example skeleton was executed against TCP port 80.

Du kannst nicht sagen:

The SRIO HTTP, PROFINET, or PROFIsafe interface was comprehensively fuzz-tested.

PROFINET RT und PROFIsafe sind außerdem keine gewöhnlichen TCP-Dienste und können mit diesem Beispiel nicht geprüft werden. Die aktuelle Topologie erlaubt auch kein Unterdrücken oder Ersetzen des legitimen zyklischen Datenverkehrs.

Klare Antwort
Diese Befehle kannst du praktisch direkt übernehmen
CM-001: ja
CM-002: ja, aber nur Erreichbarkeit, keine echte Segmentierung
CM-004: ja, aber kein vollständiger RBAC-Nachweis
CM-005: ja, wahrscheinlich Ergebnis „kein TLS“
CM-007: ja, aber nur Webteil
CM-008: ja, vorzugsweise über die GVM-Weboberfläche
CM-009: ja, aber Lastwert bewusst wählen
Diese Befehle sind nur Vorlagen oder würden das falsche System prüfen
CM-003: Hydra-Befehl benötigt den echten Loginpfad und die echten Formularparameter
CM-006: Lynis im Kali-Terminal prüft Kali, nicht das SRIO
CM-010: Das boofuzz-Skript muss an das konkrete Protokoll angepasst werden
Mein pragmatischer Rat

Wenn dein Ziel zunächst lautet, jeden CM einmal bearbeitet beziehungsweise angestoßen zu haben, kannst du die Framework-Befehle mit deinen Parametern ausführen. Schreibe anschließend aber nicht überall PASS, sondern:

EXECUTED
N/A
PARTIAL
BLOCKED
INCONCLUSIVE
PASS
FAIL

So kannst du korrekt sagen:

„Ich habe alle CMs bearbeitet und die vorgesehenen Commands soweit technisch möglich ausgeführt. Einschränkungen durch das Gerät und die Testumgebung wurden je CM dokumentiert.“
