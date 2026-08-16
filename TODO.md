# Fahrplan Bachelorarbeit
~~DI: Assets~~ 
* DI: Verbinden Assets mit MVO-Requirements
* MI: Methoden aus Standards ableiten
* MI: Till überarbeitung
* DO: Text an Lau
* FR: Anfangen Testfälle schreiben
* FR: Vorgehen Text + Belegen
* Testplan in Polarion für Security erstellen
* Raussuchen welches die IT/OT Schnittstellen sind
* GSD, MRP fehlt
---

## Phase 1: Vorbereitung & Test-Design 

**Schritt 1.1: Assets und Requirements verheiraten**
* Nimm deine MVO/IEC-Requirements und lege sie neben deine Asset-Liste (Web-API, PROFINET-Port, Rotary Switch etc.).
* Bilde Paare: *Welches Requirement muss an welchem Asset getestet werden?* (z. B. Authentifizierung am HTTP Web-Interface).

**Schritt 1.2: Methoden aus Standards ableiten**
* Erfinde keine eigenen Tests! Nutze etablierte Frameworks als "Bedienungsanleitung":
  * **OWASP Web Security Testing Guide (WSTG):** Für alles rund um das Asset `IoT-Core API` (Authentifizierung, Autorisierung, API-Missbrauch).
  * **NIST SP 800-115:** Für Netzwerk-Tests (Port-Scanning, offene Dienste) am Asset `PROFINET-Schnittstelle`.
  * **MITRE ATT&CK for ICS:** Für OT-spezifische Angriffe.

**Schritt 1.3: Testfälle schreiben (Datenblätter ausfüllen)**
* Schreibe für jedes Paar aus Schritt 1.1 ein Test-Datenblatt für Kapitel 4.2.
* **Aufbau pro Test:**
  * **ID & Ziel:** (z. B. TC-01, Schutz vor unbefugtem Firmware-Update).
  * **Referenz:** (z. B. RQ-011 / IEC 62443 CR 2.1).
  * **Vorbedingungen:** (z. B. Rotary Switch auf 0).
  * **Durchführung:** (z. B. OWASP ZAP starten, POST Request senden).
  * **Akzeptanzkriterium (PASS):** (z. B. Gateway liefert HTTP 403 Forbidden).

---

##  Phase 2: Das Testlabor aufbauen 

**Schritt 2.1: Physische und logische Isolation**
* "Ich darf beim Testen nichts kaputt machen $\rightarrow$ Ich brauche ein isoliertes Labornetzwerk."
* Verbinde das **SRIO Gateway** über einen physisch getrennten Switch mit deinem **Kali-Laptop** (Angreifer) und einer **SPS** (OT-Simulation).
* Keine Verbindung zum Firmennetzwerk!

**Schritt 2.2: Labor dokumentieren (Für Kapitel 4.1.2)**
* Erstelle ein Architektur-Diagramm (z. B. mit draw.io oder Visio), das diesen Aufbau zeigt. Das sieht in der Arbeit hochprofessionell aus.

---

## Phase 3: Testdurchführung
**Ansatz A**: Der Standalone / Air-Gap Rechner ("Stand von '98")
Das System (Kali-Rechner, Gateway, SPS) ist physisch komplett vom Firmennetzwerk getrennt (kein LAN-Kabel zur Wanddose).

Vorteile:

Maximales Schutzniveau (Zero Risk): Es ist physikalisch unmöglich, dass ein Amok laufendes Kali-Tool das Firmennetzwerk lahmlegt.

Keine IT-Freigabe nötig: Da ihr das Firmennetz nicht berührt, kann die strenge IT-Abteilung das Setup nicht blockieren. Man kann sofort loslegen.

Nachteile:

Sneakernet-Problem: Wie kommen Updates auf Kali? Wie kommen die Testergebnisse (Screenshots, Logs) auf deinen Office-Rechner, um die Bachelorarbeit zu schreiben? Meistens sind USB-Sticks durch die Firmen-IT ohnehin gesperrt (Device Control). Das macht das Arbeiten extrem zäh ("Stand '98").

Nicht zukunftsfähig: Wenn das Unternehmen in Zukunft automatisierte Security-Tests (CI/CD-Pipelines) machen will, funktioniert das mit einem isolierten Insel-PC nicht.

1. Physische Isolation (Standalone / Air-Gap)
Dieser Ansatz wird in der Literatur oft als "Testbed", "Staging Environment" oder "Air-Gapped Network" bezeichnet. Die Kernbegründung hierfür ist der Schutz der Produktionsverfügbarkeit (Safety & Availability).

NIST SP 800-82 Rev. 3 (Guide to Operational Technology Security):

Relevanz: Dies ist die Bibel der US-Regierung für OT-Security.

Was drinsteht: In den Kapiteln zur Netzwerkarchitektur und Systemwartung wird explizit gefordert, dass Security-Tests (insbesondere Penetration Tests und Vulnerability Scans) niemals in produktiven Netzwerken durchgeführt werden dürfen. Sie fordern strikt isolierte "Testbeds" oder Staging-Umgebungen, die physisch vom Rest getrennt sind.

BSI - ICS-Security-Kompendium (Bundesamt für Sicherheit in der Informationstechnik):

Relevanz: Der deutsche Goldstandard für industrielle IT-Sicherheit.

Was drinsteht: Das BSI betont die Gefahr von aktiven Scans (z. B. mit Nmap) auf alte oder sensible OT-Komponenten, da diese oft abstürzen (Denial of Service). Ein komplett entkoppeltes Test-Setup wird als Best Practice für Evaluierungen genannt.

**Ansatz B:** Das isolierte VLAN (Der moderne Netzwerk-Ansatz)
Das Testlabor hängt physisch am Firmennetzwerk, wird aber logisch durch Managed Switches und Firewalls in ein streng isoliertes Virtual Local Area Network (VLAN) gesperrt.

Vorteile:

Komfort und Effizienz: Du hast kontrollierten Internetzugriff (für Tool-Updates) und kannst Ergebnisse über bestimmte freigegebene Routen (z. B. auf einen File-Share) sicher in dein Office-Netzwerk übertragen.

Skalierbarkeit: Wenn die Methodik aus deiner Bachelorarbeit später in die reguläre Entwicklung übernommen wird, kann dieses VLAN bestehen bleiben und automatisiert bespielt werden.

Nachteile:

Hoher Abstimmungsaufwand: Die IT-Abteilung muss das VLAN einrichten, Firewall-Regeln (Access Control Lists) schreiben und Ports freischalten. Das dauert oft Wochen und sprengt den Zeitplan einer Bachelorarbeit.

Restrisiko: Ein Konfigurationsfehler in der Firewall könnte bedeuten, dass Netzwerk-Scans (Nmap) aus Versehen in das produktive Firmennetz überschwappen und dort Alarme im Security Operations Center (SOC) auslösen.

2. Logische Isolation (Isoliertes VLAN / Firewalls)
Hier argumentierst du mit dem Konzept der Netzwerksegmentierung. Die Fachbegriffe, die du hier brauchst, sind "Zones and Conduits" (Zonen und Übergänge).

IEC 62443-3-2 (Security risk assessment for system design):

Relevanz: Deine Hauptnorm.

Was drinsteht: Hier wird das "Zones and Conduits"-Modell definiert. Du kannst argumentieren, dass dein Testlabor (VLAN) als eigene "Untrusted Zone" (Zone mit niedrigem Vertrauensniveau) definiert wird, während das Firmennetz eine "Trusted Zone" ist. Der Übergang (Conduit) wird durch strenge Firewall-Regeln (Access Control Lists) im Managed Switch kontrolliert.

ISA-95 / Purdue Enterprise Reference Architecture (PERA):

Relevanz: Das absolute Standard-Architekturmodell für Industrieanlagen.

Was drinsteht: Das Purdue-Modell definiert verschiedene Level (Level 0 bis 5). Ein VLAN-Setup zur Isolation simuliert eine Demilitarized Zone (DMZ), die verhindert, dass Traffic aus der Testumgebung (Level 3/4) ungefiltert in die Office-IT durchdringt.


**Andere / Fortschrittliche Ansätze**
Wenn du in Kapitel 4.1.2 glänzen willst, nennst du nicht nur Air-Gap und VLAN, sondern erwähnst kurz ein bis zwei hochmoderne Ansätze (und verwirfst sie dann für deine Arbeit als zu aufwendig). Das bringt richtig Punkte für den methodischen Weitblick.

Hardware-in-the-Loop (HiL) / Cyber Ranges / Digital Twins:

Konzept: Anstatt echte Hardware anzugreifen, wird das Gateway virtuell nachgebaut (Digitaler Zwilling). Man testet in einer komplett virtuellen Umgebung (Cyber Range).

Quelle: ENISA (European Union Agency for Cybersecurity) - "Cybersecurity requirements for ICS" oder akademische Paper zu "ICS Cyber Ranges".

Bewertung für dich: Viel zu teuer und komplex für eine Bachelorarbeit, aber der absolute Trend in großen Konzernen.

Datendioden (Unidirektionale Gateways):

Konzept: Wenn du ein Air-Gap-Netzwerk hast, aber die Testergebnisse/Logs live auf deinen Office-Rechner bekommen musst, ohne dass Viren zurückfließen können. Eine Datendiode ist ein Stück Hardware (Glasfaser), das Daten physikalisch nur in eine Richtung senden kann.

Quelle: BSI TR-02106 (Technische Richtlinie für Unidirektionale Gateways).

Bewertung für dich: Zeigt, dass du das "Sneakernet"-Problem (USB-Sticks hin und her tragen) bei Air-Gaps kennst, sprengt aber das Budget.

**Die pragmatische Lösung** 
Für eine Bachelorarbeit hast du meistens keine Zeit, 3 Wochen auf eine VLAN-Freigabe der IT zu warten. Du musst pragmatisch sein.

Dein Vorschlag für die Essener / deinen Vorgesetzten (Der Hybrid-Ansatz):
Du baust einen physischen Air-Gap (Ansatz A) auf dem Schreibtisch auf: Ein kleiner, dummer 5-Port-Switch verbindet nur deinen Kali-Laptop und das Gateway. ABER: Für den Datenaustausch nutzt du nicht das Firmen-LAN. Stattdessen verbindest du den Kali-Laptop über sein WLAN-Modul mit dem Gäste-WLAN der Firma (oder dem Hotspot deines Handys).

Warum das genial ist: Das Gäste-WLAN ist von der Firmen-IT sowieso schon vom produktiven Netz isoliert. Du hast Internet für Updates, du kannst dir die Logfiles per E-Mail an dich selbst schicken, aber die IT-Abteilung bekommt keine Panik, weil du keine Kabel in ihre sensiblen Netzwerkdosen steckst.


**Schritt 3.1: Werkzeugkoffer Kali Linux nutzen**
Führe deine geschriebenen Testfälle am echten Gerät durch. Nutze dafür die Kali-Tools:
* **Nmap:** Port-Scanning (Welche Türen sind offen?)
* **Hydra:** Brute-Force (Halten Passwörter/Logins stand?)
* **OWASP ZAP / Burp Suite:** API-Manipulation (Kann ich das Update ohne Rotary-Switch triggern?)
* **Siege / Slowloris:** DoS / Last-Tests (Bricht die SPS-Verbindung ab, wenn die API geflutet wird?)
* **SSLscan / Nikto:** Web-Vulnerability-Checks (Gibt es unverschlüsselte Daten oder Debug-Schnittstellen?)

**Schritt 3.2: Evidenzen sammeln (Extrem wichtig!)**
* Mache von jedem abgelehnten Angriff oder jedem Fehler einen Screenshot.
* Speichere die Konsolen-Outputs (Logs) ab. 
* Diese Evidenzen kommen später in den Anhang deiner Arbeit. Sie sind der "TÜV-Beweis".

---

##  Phase 4: Auswertung & Fazit

**Schritt 4.1: Ergebnisse bewerten**
* Gib jedem Testfall ein hartes Urteil:
  * **PASS:** Angriff abgewehrt, MVO-Forderung erfüllt.
  * **FAIL:** Angriff erfolgreich, Sicherheitslücke gefunden.
  * **PARTIAL:** Schutz teilweise vorhanden, aber nicht vollständig greifend.

**Schritt 4.2: MVO Compliance Verification (Der Kreis schließt sich)**
* Beantworte in Kapitel 4.3.3 die Frage: *Habe ich für jedes MVO-Requirement aus meiner Tabelle in Kapitel 3 mindestens einen PASS-Testfall geliefert?*
* Wenn ja: Die Methodik funktioniert und beweist die rechtliche Konformität des Gateways!

**Schritt 4.3: Zusammenfassung & Ausblick (Kapitel 5)**
* Reflektiere: Was lief gut, was war schwer? (Limitationen).
* Ausblick: Wie könnte man das in Zukunft automatisieren (z. B. in einer CI/CD-Pipeline in der Entwicklung)?

---

##Wichtige Begrifflichkeiten & Argumentationen

**Warum dieser Ansatz?**
* *Problem:* Funktionale Tests prüfen nur das "Soll" (Passwortfeld ist da). Penetration Tests sind unstrukturiert.
* *Lösung:* Ein **hybrider, anforderungsbasierter Ansatz**. Wir nutzen Angreifer-Werkzeuge, arbeiten aber eine juristische Checkliste ab.

**Die 3 Ebenen der Umsetzung:**
1. **Methode:** *Was tue ich?* (z. B. Port-Scanning, abgeleitet aus NIST SP 800-115).
2. **Tool:** *Womit tue ich es?* (z. B. Nmap).
3. **Plattform:** *Worauf läuft das?* (z. B. Kali Linux).

**Warum Kali Linux? (Wissenschaftliche Begründung für Kap 4.1.3)**
* **Vollständigkeit:** Alle von NIST und OWASP empfohlenen Tools sind out-of-the-box installiert.
* **Reproduzierbarkeit:** Open-Source-Tools erlauben es Dritten (oder Prüfern), die Tests exakt nachzustellen (Gegensatz zu teuren Blackbox-Lösungen).
* **Effizienz:** Minimiert den Setup-Aufwand im Labor und ist etablierter Industrie-Standard für Security-Assessments.












# Beispiel 1: Authorization Bypass (Firmware Update ohne physischen Schalter)

Hier testen wir, ob ein Angreifer über das Netzwerk ein Update pushen kann, obwohl der physische Wahlschalter am Gerät auf "Normalbetrieb" (0) steht.

Der methodische Faden (Traceability):

Gesetz/Norm: RQ-011 (Schutz vor unbefugter Modifikation) $\rightarrow$ IEC 62443 CR 2.1 (Authorization enforcement)

Asset: IF-02 (IoT-Core, API-Endpunkt /firmware/install) und IF-03 (Rotary Switch)Bedrohung (STRIDE): Elevation of Privilege (Rechteausweitung ohne physische Autorisierung)

Kali-Tool: OWASP ZAP (oder simples curl im Terminal)

Das Test-Datenblatt für Kapitel 4:
Feld: Inhalt für diesen Testfall
Test-ID         TC-01
Testdomäne      Authorization / Privilege Escalation
Referenz        MVO RQ-011 / IEC 62443 CR 2.1
Ziel            Verifikation, dass schreibende API-Zugriffe (Firmware-Update, FIT-Trigger) ohne physische Autorisierung (Rotary Switch = 999) serverseitig blockiert werden.

Vorbedingungen  1. SRIO ist hochgefahren und via Ethernet mit dem Kali-Rechner verbunden.
                2. Rotary Switch am Gerät steht auf 0 (Normalbetrieb).
                
Durchführung    1. Starten von OWASP ZAP (oder Terminal) auf dem Kali-Host.
                2. Senden eines HTTP POST Requests an die API des SRIO: http://<IP-SRIO>/firmware/install3. 
                Optional: Senden eines POST Requests an /fit/setfit.Akzeptanzkriterium (PASS)
                Das Gateway lehnt die Anfrage sofort ab (z. B. HTTP 403 Forbidden oder HTTP 400 Bad Request mit Fehlermeldung). Der Gerätestatus verändert sich nicht.FAIL-KriteriumDas Gateway akzeptiert den Befehl (HTTP 200 OK) und leitet den Update- oder FIT-Prozess ein.EvidenzScreenshot des abgelehnten HTTP-Responses aus OWASP ZAP (wird im Anhang gespeichert).

%such as a corporate guest WLAN. 
%
%The guest WLAN provides the necessary internet access but is already logically segregated from the internal corporate IT by default. It acts as a trusted boundary control. This architecture ensures that the critical OT components remain isolated from internet-borne threats, while the attacker machine can safely interact with external resources. Consequently, the hybrid approach successfully satisfies the strict isolation mandates of industrial cybersecurity standards while ensuring practical feasibility within the given research constraints.
%%

\subsection{Evidence Collection and Documentation}
\label{subsec:evidence_collection}
%TODO Quelle
Executing a test is insufficient if the outcome cannot be formally proven. Article 10(2) and Annex IV Part A of Regulation (EU) 2023/1230 explicitly mandate comprehensive technical documentation to demonstrate conformity \cite{EU2023_1230}. Therefore, meticulous evidence collection is a mandatory methodological step.

For every executed test case, digital artifacts must be recorded. This includes raw console outputs (logs), network traffic captures (PCAP files), and screenshots showing blocked access attempts or error codes (e.g., HTTP 403 Forbidden). These artifacts serve as the indisputable empirical proof that a security mechanism successfully mitigated an attack. 
[ Test-Runner / Orchestrierung (Python / Robot Framework) ]
   ├── Port & Service Scan:    Nmap + NSE Scripts
   ├── TLS & Cipher Validierung: testssl.sh / SSLyze
   ├── Protokoll & Robustheit:   Scapy / Boofuzz (Modbus, OPC UA)
   └── Monitoring / Nachweis:   Wireshark / TShark (Packet Capturing)

Similarly, white box testing is also known as Static Analysis Security Testing (SAST) since it has access to internal
code and it helps developers write secure source code. The SAST
tool scans static code and reduces the number of vulnerabilities.
Both DAST and SAST tools can fit in the development process.
An important part of web application security testing tools is that
they are known to be error-prone and report false positives. The
problem of false positives and false negatives are common for the
automated web application security testing tools. If a vulnerability
is reported by a web application security tool but in reality it is not
existing, it is called as false positive. If an existing vulnerability is
missed by a web application security testing tool, this behavior is
called as false negative. Therefore, web application security testing
tools should have low value for false positives and the false
negatives \cite[p. 6777]{aydos_security_2022}