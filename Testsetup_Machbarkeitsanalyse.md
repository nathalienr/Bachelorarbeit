# Machbarkeitsanalyse: Testumgebung vs. Testfallkatalog (WORKFLOW.docx)

**Bezug:**

* Physische Testumgebung: `Testumgebung\\\_Beschreibung.md` (Switch 192.168.0.91, SPS 192.168.0.1 @ Port1, SRIO/DUT 192.168.0.2 @ Port2, Kali-Linux 192.168.0.80 @ Port3, Firmenlaptop 192.168.0.7 @ Port4)
* Abstrakter/konkreter Testfallkatalog: `WORKFLOW.docx` (Test Cases TC‑RQ001‑01 … TC‑RQ014‑04, insgesamt 63 Testfälle zu 14 Requirements)

**Ziel dieses Dokuments:** Für jeden Testfall aus deinem Katalog klären, ob er mit dem aktuellen Aufbau (Switch, SPS, SRIO, Kali, Laptop – Sterntopologie, Ports 1–4) durchführbar ist, und wenn nicht, was konkret fehlt.

\---

## 1\. Kurzantwort

**Ja, dein Aufbau ist grundsätzlich korrekt und für die klare Mehrheit der Testfälle (ca. 45 von 63) direkt oder mit einer reinen Switch-Konfigurationsänderung nutzbar.** Es gibt aber **zwei strukturelle Lücken**, die einen relevanten Teil der Testfälle (insgesamt ca. 18) verhindern oder nur eingeschränkt erlauben:

|#|Lücke|Betrifft|
|-|-|-|
|1|**Kein Inline-/Bridge-Zugriff** (Kali sitzt an einem normalen Access-Port, nicht transparent zwischen SPS und SRIO)|Tests, die das *Unterdrücken des echten Producers* + *Ersetzen des Frames* voraussetzen (echtes MITM)|
|2|**Kein zweites/Ersatz-SRIO-Gerät**|Destruktive Tests (Firmware-Korruption, Siegel-Manipulation) und sicherheitshalber auch alle Firmware-Update-/Rotary-Switch-Grenztests|

Beide Lücken sind in deiner eigenen `Testumgebung\\\_Beschreibung.md` bereits als Einschränkung dokumentiert (Abschnitt 7.3 bzw. Abschnitt 8) – dieses Dokument übersetzt das jetzt konkret auf jeden einzelnen Testfall deines Kataloges.

\---

## 2\. Wichtiger Mechanismus: „Setup A“ / „Setup B“ sind KEINE unterschiedlichen Ports

Im Testfallkatalog (WORKFLOW.docx) wird zwischen mehreren „Setups“ unterschieden. Wichtig für dich: **Setup A und Setup B laufen auf demselben physischen Kali-Anschluss (Port 3)** – der Unterschied ist reine Switch-Konfiguration, kein Umstecken:

|Setup im Katalog|Bedeutung|Umsetzung in deiner Topologie|
|-|-|-|
|**Setup A (passiv)**|Kali sieht (fast) den kompletten Traffic zwischen SPS↔SRIO mit|Port-Mirroring aktivieren: Quelle Port1+Port2 → Ziel Port3 (Kali), siehe `Testumgebung\\\_Beschreibung.md` Abschnitt 3.3. Kali bekommt dabei zusätzlich weiterhin seinen eigenen Verkehr – Setup A und aktive Tests können parallel laufen.|
|**Setup B (aktiv)**|Kali agiert als normaler Netzteilnehmer, sendet gezielt Pakete an SRIO|Mirroring kann aktiv bleiben oder deaktiviert werden – für reine Portscans/HTTP-Requests irrelevant, Port3 bleibt gleich.|
|**Setup B‑Inline**|Kali sitzt *transparent zwischen* Switch-Port2 und SRIO (Bridge aus zwei NICs), kann Frames abfangen/unterdrücken/ersetzen|**In deinem Aufbau nicht vorhanden** – Kali hat nur eine physische Schnittstelle zum Switch. Siehe Abschnitt 3 unten.|
|**Setup C (Ersatzgerät)**|Ein zweites, nicht-primäres SRIO-Gerät für destruktive/irreversible Tests|**In deinem Aufbau nicht vorhanden** – du hast nur ein SRIO (192.168.0.2). Siehe Abschnitt 3 unten.|

Zusätzlich: Der Testfallkatalog verwendet in den „Concrete Execution“-Feldern **Platzhalter** (Gerätename „Pi“ statt „Kali-Rechner“, Beispiel-IP-Subnetz `172.18.87.x` statt deinem echten `192.168.0.x`, teils Port4 statt Port3). Das ist rein redaktionell aus einer generischen Vorlage übernommen – du musst beim Ausführen jeder Konkret-Ausführung die **IP‑Adressen und Interfacenamen an deine reale Umgebung anpassen** (z. B. `172.18.87.2` → `192.168.0.2`, `eth0` ggf. anpassen). Das ist keine strukturelle Einschränkung, nur eine Anpassung der Befehle.

\---

## 3\. Die zwei fehlenden Bausteine im Detail

### 3.1 Fehlender Inline-/Bridge-Zugriff (echtes MITM)

Deine `Testumgebung\\\_Beschreibung.md` beschreibt das bereits korrekt (Abschnitt 7.3): Kali hängt als **regulärer Access-Port** am Switch. Der zyklische PROFINET/PROFIsafe-Verkehr zwischen SPS und SRIO läuft direkt Port1↔Port2 über den Switch und wird **nicht** an Port3 (Kali) dupliziert – außer im Mirroring-Fall, und selbst dann kann Kali den Verkehr nur *mitlesen*, nicht *abfangen und ersetzen*. Außerdem ist PROFINET RT/PROFIsafe ein eigener EtherType (0x8892) ohne IP-Adressierung – ARP-Spoofing wirkt hier nicht.

**Betroffen sind alle Testfälle, die explizit voraussetzen, dass der legitime Producer unterdrückt und durch einen kontrollierten Angreifer-Frame ersetzt wird** (nicht nur zusätzlicher/paralleler Verkehr, sondern echte Substitution).

**Notwendige Änderung:** Ein zweiter Netzwerkadapter am Kali-Rechner (USB3-zu-Gigabit-Ethernet-Adapter reicht), der es erlaubt, Kali als **transparente Bridge** zwischen Switch-Port2 und SRIO einzusetzen (`brctl`/`bridge-utils` + `ebtables` + `NetfilterQueue`, wie in den Concrete-Execution-Feldern der betroffenen Testfälle beschrieben). Das bedeutet auch eine **Verkabelungsänderung**: SRIO wird nicht mehr direkt an Switch-Port2 angeschlossen, sondern an die zweite Kali-NIC; die erste Kali-NIC bleibt am Switch-Port2. Das ist in der aktuellen, finalen Topologie laut deiner eigenen Beschreibung bewusst **nicht vorgesehen** und müsste separat ergänzt werden.

### 3.2 Fehlendes Ersatz-/Zweitgerät (Setup C)

Deine `Testumgebung\\\_Beschreibung.md` weist in Abschnitt 8 („Sicherheitshinweise“) bereits selbst darauf hin: *„Destruktive Tests (Siegel entfernen, Firmware-Korruption) nur an einem separaten Ersatzgerät durchführen, nicht am primären DUT.“* Aktuell besitzt dein Aufbau nur **ein** SRIO (192.168.0.2) – kein Ersatzgerät.

**Notwendige Änderung:** Ein zweites AL400S/AL401S-Gerät beschaffen, das ausschließlich für folgende Testklassen verwendet wird:

* Aufbrechen/Wiederherstellen der Rotary-Switch-Plombe (physische Manipulation)
* Installation eines modifizierten/unsignierten Firmware-Containers
* Wiederholte Firmware-Up-/Downgrades zur Historien-/Timestamp-Analyse
* Tests, bei denen ein irreversibler oder schwer rückgängig zu machender Zustand riskiert wird (z. B. Rotary-Switch dauerhaft auf „999“, danach Firmware-Wiederherstellung nötig)

Ohne Ersatzgerät kannst du diese Tests **nicht risikofrei** an deinem produktiven Setup durchführen (Gefahr: dauerhafter Defekt/Bricking des einzigen DUT, das du für alle anderen Tests brauchst).

\---

## 4\. Testfall-für-Testfall-Bewertung

Legende: ✅ direkt durchführbar (ggf. Switch-Mirroring an/aus) · ⚠️ eingeschränkt durchführbar / Ersatzgerät empfohlen · ❌ ohne Zusatz-Hardware nicht (sauber) durchführbar

### RQ‑001 – Verbindung Dritter darf nicht zu Gefährdung führen

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ001‑01|Baseline PROFIsafe-Austausch, Qualifier=good|✅|Mirroring Port1+2→Port3 aktivieren, TIA-Watchtable am Laptop|
|TC‑RQ001‑02|Nmap-Enumeration Non-Safety-Pfad|✅|Reines Setup B, Kali direkt gegen 192.168.0.2|
|TC‑RQ001‑03|Mis-addressed/CRC-Mismatch-Injection (parallel, kein Producer-Ausfall)|✅|Paralleles Senden per Scapy von Port3 aus, Mirroring parallel aktiv lassen zur Beobachtung|
|TC‑RQ001‑04|**Echtes** In-Path-MITM (Producer unterdrücken + Sequenznummer übernehmen)|❌|Braucht Inline-Bridge (siehe 3.1)|
|TC‑RQ001‑05|Kanalunterbrechung > F\_WD\_Time, Watchdog-Reaktion|✅|Patchkabel an Port1 oder Port2 manuell ziehen, Mirroring an Port3 zur Beobachtung|

### RQ‑002 – Schutz von HW-Komponenten vor Korruption

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ002‑01|iParCRC/F\_ParCRC-Mismatch wird abgelehnt|✅|TIA + Mirroring|
|TC‑RQ002‑02|Stale-CRC-Payload-Injection (parallel)|✅|Wie 001‑03|
|TC‑RQ002‑03|Recompute-CRC über modifizierte Nutzdaten, **saubere** Einzel-Frame-Substitution|❌|Katalog fordert explizit Inline für „ein sauberes Ergebnis“ – ohne Bridge nur mit Einschränkungen (Kollision mit echtem Producer) durchführbar|
|TC‑RQ002‑04|Analytisch: Forgeability von F\_ParCRC/iParCRC (Bit-Länge)|✅|Reine Schreibtischanalyse, keine Hardware nötig|
|TC‑RQ002‑05|Physische Manipulation Rotary-Switch/Siegel + Neustart|⚠️/❌|Nur mit Ersatzgerät sicher durchführbar (siehe 3.2)|

### RQ‑003 – Nachweisbarkeit von Eingriffen (Hardware)

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ003‑01|Baseline: Welche Evidenz existiert (ErrorLog, I\&M0, I\&M4)|✅|IoT-Core (curl) + TIA|
|TC‑RQ003‑02|Autorisierter Parameter-/Adresswechsel + Reboot, Evidenzverlust prüfen|✅|TIA + IoT-Core|
|TC‑RQ003‑03|Physische Manipulation ohne sichtbare Siegel-Beschädigung|⚠️/❌|Ersatzgerät empfohlen/nötig (Siegel-Manipulation ist irreversibel)|
|TC‑RQ003‑04|Zeitbezug: Uptime resettet, keine RTC|✅|IoT-Core (`/systemtime/systick`)|
|TC‑RQ003‑05|FIT-Interface auf Produktionsgerät ablehnen|✅|Dein DUT ist ein Produktionsgerät – Ablehnung erwartbar|

### RQ‑004 – Identifikation sicherheitsrelevanter Software/Daten

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ004‑01|Vollständigkeit der Identifikationsdaten (SW+Daten)|✅|IoT-Core + TIA (I\&M)|
|TC‑RQ004‑02|SBOM-Vollständigkeit Drittkomponenten|✅|Schreibtischanalyse (Dokumentation + NVD)|
|TC‑RQ004‑03|Klartext-Übertragung der Identifikationsdaten (HTTP)|✅|Mirroring + sslscan|
|TC‑RQ004‑04|Eindeutigkeit der Config-Signatur (I\&M4) bei zwei Configs|✅|TIA, zwei Konfigurationen laden|

### RQ‑005 – Schutz identifizierter SW/Daten vor Korruption

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ005‑01|= TC‑RQ002‑01|✅|s. o.|
|TC‑RQ005‑02|Valide CRC über modifizierte Parameter (Forgery)|⚠️|Alternative „TIA-seitig geforgte Parameter“ ohne Inline möglich, für „saubere“ Variante Ersatzgerät/Inline empfohlen|
|TC‑RQ005‑03|Installation unsignierter/modifizierter Firmware|❌|**Nur am Ersatzgerät**, da destruktiv (Bricking-Risiko)|
|TC‑RQ005‑04|Statische Analyse Update-Container (Signatur/Header)|✅|Offline, kein DUT nötig|
|TC‑RQ005‑05|Analytisch: Self-Test ≠ Authentizität|✅|Reine Argumentation, keine Hardware|

### RQ‑006 – Identifikation sicherheitsrelevanter Software

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ006‑01|Vollständige SW-Inventarisierung|✅|IoT-Core + TIA|
|TC‑RQ006‑02|= TC‑RQ004‑02 (SBOM)|✅|Schreibtischanalyse|
|TC‑RQ006‑03|Klartext-Inventar (DiD-Beobachtung)|✅|Mirroring + sslscan|

### RQ‑007 – Verfügbarkeit der Identifikationsinformationen

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ007‑01|Baseline Visualizer/Browser-Zugriff|✅|Laptop-Browser|
|TC‑RQ007‑02|Verfügbarkeit über Init/Update/FatalError-Zustände|⚠️|Init/FatalError-Teil ✅ direkt; SCPU-Flash-Fenster erfordert Firmware-Update – auf Primärgerät möglich, aber Backup/Recovery vorher sichern (Abschnitt 8 deiner Umgebungsbeschreibung)|
|TC‑RQ007‑03|Connection-Hold Self-DoS (2 HTTP-Verbindungen)|✅|Reines Setup B|
|TC‑RQ007‑04|Verfügbarkeitsinversion bei COM/SysCom-Störung|⚠️|Wie genau eine „induzierte COM/SysCom-Unterbrechung“ ohne FIT-Zugriff auf Produktionsgerät erzeugt werden soll, ist im Katalog nicht eindeutig spezifiziert – ggf. nur eingeschränkt reproduzierbar|

### RQ‑008 – Nachweisbarkeit von Eingriffen (Software)

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ008‑01|Baseline Software-Evidenz|✅|IoT-Core + TIA|
|TC‑RQ008‑02|Selbstlöschendes Firmware-Update (Log wird bei Neustart gelöscht)|⚠️|Nicht destruktiv, aber Katalog sieht Ersatzgerät vor – kann bei Bedarf auch am Primärgerät mit vorherigem Firmware-Backup erfolgen|
|TC‑RQ008‑03|Legitimes vs. illegitimes Update – Evidenz nicht unterscheidbar|❌|Erfordert Installation eines manipulierten Images → **nur Ersatzgerät**|
|TC‑RQ008‑04|Zeitbezug über Update-Kaltstart|⚠️|Wie 008‑02|
|TC‑RQ008‑05|= TC‑RQ003‑05 (FIT auf Produktionsgerät)|✅|s. o.|

### RQ‑009 – Nachweisbarkeit von Konfigurationsänderungen

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ009‑01|Baseline Config-Evidenz (REVISION\_COUNTER, I\&M4)|✅|TIA + IoT-Core|
|TC‑RQ009‑02|Persistenz von Zähler vs. Log über Kaltstart|✅|TIA + IoT-Core|
|TC‑RQ009‑03|Akteurs-Zuordnung liegt nur bei TIA/PLC, nicht am Gerät|✅|TIA-Projekt einsehen|
|TC‑RQ009‑04|Schreibzugriff nach Param-End wird blockiert|✅|Scapy PROFINET-acyclic-write während OPERATE, Mirroring optional|
|TC‑RQ009‑05|Analytisch: Zähler-Wrap-Around über Missionszeit|✅|Schreibtischanalyse|

### RQ‑010 – Widerstandsfähigkeit gegen böswillige Angriffe

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ010‑01|Baseline unter Nennlast (Net Load Class III)|✅|Setup B + Mirroring; **vorher Storm-Control-Status am Switch dokumentieren** (Abschnitt 3.4 deiner Umgebungsbeschreibung)|
|TC‑RQ010‑02|Netzwerk-/L2-Flood, Passivierungsverhalten|✅|Ohne Inline möglich; bei hoher Flood-Rate kann die Mirror-Aufzeichnung Frames verlieren – als bekannte Einschränkung dokumentieren, kein Blocker|
|TC‑RQ010‑03|Protokoll-Fuzzing (HTTP/IoT-Core + PROFINET/DCP + PROFIsafe)|✅/⚠️|HTTP-Fuzzing (boofuzz) und DCP-Fuzzing (broadcast) direkt möglich; die im Katalog zusätzlich erwähnte Inline-Variante für PROFINET/PROFIsafe-Feld-Fuzzing ist optional – additive/parallele Frame-Injection (wie bei 001‑03) reicht für die meisten Fälle|
|TC‑RQ010‑04|Applikationsebene-Flood + Domänentrennung|✅|Setup B (Siege/ab)|
|TC‑RQ010‑05|Aggregation der Ergebnisse aus 010‑02/03 + 001‑03/04 + 005‑03|⚠️|Ergebnis hängt von TC‑RQ001‑04 und TC‑RQ005‑03 ab, die selbst eingeschränkt/nicht möglich sind – Matrix bleibt unvollständig ohne die fehlende Hardware|

### RQ‑011 – Schutz sicherheitsrelevanter Einstellungen vor Änderung

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ011‑01|Read-Only-Durchsetzung IoT-Core|✅|Setup B (curl/ZAP)|
|TC‑RQ011‑02|Unauthentisierter DCP-Factory-Reset|✅|pnio-dcp von Port3|
|TC‑RQ011‑03|Parameter-Schreibzugriff ohne Geräte-Auth, **sauber substituiert**|⚠️|Katalog erlaubt Alternative „Injection während Param-Phase“ ohne Inline – damit eingeschränkt durchführbar|
|TC‑RQ011‑04|Firmware-Update-Modusgatter (Rotary=999)|⚠️|Nicht zwingend destruktiv, Katalog sieht dennoch Ersatzgerät vor – am Primärgerät nur mit Backup/Recovery-Vorbereitung|
|TC‑RQ011‑05|= TC‑RQ003‑03/TC‑RQ002‑05 (physische Barriere)|⚠️/❌|Ersatzgerät empfohlen/nötig|

### RQ‑012 – Tracing-Log für 5 Jahre

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ012‑01|Ringpuffer-Überlauf (>100 Einträge)|✅|IoT-Core, wiederholte Events erzeugen|
|TC‑RQ012‑02|Log-Löschung bei Kaltstart|✅|IoT-Core + Power-Cycle|
|TC‑RQ012‑03|Analytisch: Pflicht-Reboot (≤1 Jahr) macht 5-Jahres-Retention unmöglich|✅|Schreibtischanalyse|
|TC‑RQ012‑04|= TC‑RQ003‑04 (Zeitbezug)|✅|s. o.|

### RQ‑013 – Tracing-Log der SW-Versionen (5 Jahre je Upload)

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ013‑01|Nur aktuelle Version wird angezeigt (keine Historie)|✅|IoT-Core + TIA|
|TC‑RQ013‑02|Zwei Uploads nacheinander – keine Vorversion nachweisbar|⚠️|Nicht destruktiv, aber sinnvollerweise am Ersatzgerät, um Verfügbarkeit des Primärgeräts nicht zu riskieren|
|TC‑RQ013‑03|Kein absoluter Zeitstempel je Upload|⚠️|Wie 013‑02|
|TC‑RQ013‑04|Externe Release Notes als Ersatznachweis prüfen|✅|Schreibtischanalyse (Dokumentenprüfung)|

### RQ‑014 – Zugriffsbeschränkung auf Tracing-Log

|Test-ID|Kurzziel|Status|Bemerkung|
|-|-|-|-|
|TC‑RQ014‑01|Unauthentisiertes Auslesen des ErrorLogs|✅|curl von Port3|
|TC‑RQ014‑02|Klartext-Übertragung des Logs|✅|Mirroring + tshark/sslscan|
|TC‑RQ014‑03|Kein Auth-/Rollenmodell auffindbar|✅|ZAP-Enumeration|
|TC‑RQ014‑04|Keine kontrollierte Löschfunktion auffindbar|✅|curl DELETE-Versuch|

\---

## 5\. Statistik

|Status|Anzahl Testfälle|
|-|-|
|✅ direkt/ mit reiner Switch-Konfiguration durchführbar|45|
|⚠️ eingeschränkt durchführbar / Ersatzgerät empfohlen|12|
|❌ ohne Zusatz-Hardware nicht sauber durchführbar|6|

*(TC‑RQ001‑04, TC‑RQ002‑03, TC‑RQ002‑05, TC‑RQ005‑03, TC‑RQ008‑03, TC‑RQ011‑05 sind die sechs Testfälle, die ohne die in Abschnitt 3 beschriebenen Ergänzungen nicht durchführbar sind.)*

\---

## 6\. Empfohlene Änderungen an der Testumgebung (priorisiert)

1. **Zweiter Netzwerkadapter für Kali** (z. B. USB3-zu-Gigabit-Ethernet-Dongle), um Kali bei Bedarf als transparente Layer-2-Bridge zwischen Switch-Port2 und SRIO einzusetzen. Löst: TC‑RQ001‑04, TC‑RQ002‑03 vollständig; verbessert TC‑RQ005‑02, TC‑RQ011‑03, TC‑RQ010‑03.
2. **Ein zweites SRIO-Gerät (AL400S/AL401S) als Ersatzgerät** ausschließlich für destruktive/irreversible Tests. Löst: TC‑RQ002‑05, TC‑RQ003‑03, TC‑RQ005‑03, TC‑RQ008‑03, TC‑RQ011‑05 vollständig; erhöht die Sicherheit bei TC‑RQ007‑02, TC‑RQ008‑02/04, TC‑RQ011‑04, TC‑RQ013‑02/03.
3. **Vor Testbeginn:** Firmware-Container + Hash des Primärgeräts sichern (Recovery-Pfad, wie bereits in `Testumgebung\\\_Beschreibung.md` Abschnitt 8 gefordert) – auch wenn du (noch) kein Ersatzgerät hast, minimiert das die Auswirkung eines Fehlschlags bei den ⚠️-Tests, die du am Primärgerät durchführst.
4. **Vor Flood-/Fuzzing-Tests (TC‑RQ010‑01/02):** Storm-Control-Einstellung am Switch dokumentieren (wie in Abschnitt 3.4 deiner Umgebungsbeschreibung vorgesehen) – beeinflusst die Interpretierbarkeit der Ergebnisse.
5. **Bei jeder „Concrete Execution“ aus WORKFLOW.docx:** IP-Adressen (`172.18.87.x` → `192.168.0.x`) und Gerätenamen (`Pi` → Kali-Rechner) anpassen, bevor du die Befehle 1:1 übernimmst.

\---

## 7\. Kurz-Checkliste

* \[ ] Port-Mirroring-Konfiguration (Quelle Port1+2 → Ziel Port3) einmalig eingerichtet und getestet (`tcpdump`/`tshark` am Kali-Rechner)
* \[ ] Storm-Control-Status vor Flood-Tests dokumentiert
* \[ ] Firmware-Backup + Hash des Primär-SRIO gesichert, bevor irgendein Update-/Rotary-Switch-Test (auch die ⚠️-Fälle) am Primärgerät läuft
* \[ ] Entscheidung getroffen: zweiter NIC-Adapter beschafft? (ja/nein → betrifft 2 Testfälle direkt, 4 weitere in „sauberer“ Form)
* \[ ] Entscheidung getroffen: Ersatz-SRIO beschafft? (ja/nein → betrifft 5 Testfälle direkt, 6 weitere sicherheitshalber)
* \[ ] IP-Adressen/Gerätenamen in allen übernommenen Befehlen aus WORKFLOW.docx auf deine reale Umgebung angepasst

