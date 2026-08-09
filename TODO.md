# Fahrplan Bachelorarbeit
* MO: Assets
* Mo: Dokumente Bastian
* MO: Verbinden Assets mit MVO-Requirements
* DI: Methoden aus Standards ableiten
* DO: Anfangen Testfälle schreiben
* FR: Vorgehen Text + Belegen


##  Die Kern
Du testest nicht einfach blind drauf los. Jeder Testfall in deiner Arbeit ist das Endprodukt einer lückenlosen Beweiskette (**Traceability**):
1. **Gesetz:** MVO Annex III (Was fordert der Staat?)
2. **Norm:** IEC 62443 (Was heißt das für Ingenieure?)
3. **Bedrohung:** STRIDE (Was macht der Hacker, wenn das fehlt?)
4. **Test-Domäne:** Z.B. Authentication (Was für eine Art Test brauchen wir?)
5. **Methode & Tool:** OWASP/NIST + Kali Linux (Wie testen wir es konkret?)
6. **Evidenz:** Log-File (Der Beweis für den TÜV).

---

## Phase 1: Vorbereitung & Test-Design 

**Schritt 1.1: Assets und Requirements verheiraten**
* Nimm deine MVO/IEC-Requirements und lege sie neben deine Asset-Liste (Web-API, PROFINET-Port, Rotary Switch etc.).
* Bilde Paare: *Welches Requirement muss an welchem Asset getestet werden?* (z. B. Authentifizierung am HTTP Web-Interface).

**Schritt 2.2: Methoden aus Standards ableiten**
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

