
Wo Scapy berechtigt ist (nur mit dokumentierter Begründung nach SM‑5):

CM‑002 Segmentierungs‑Bypass: gecraftete/fragmentierte/gespoofte Pakete zum Testen von Firewall‑/Conduit‑Regeln – NIST 800‑115 nennt hier ausdrücklich „tools with packet‑builder ability" für internes Testing mit „highly customized packets".
OT‑/ICS‑Protokolle (Modbus, proprietäre Feldbusse), die nmap nicht nativ erzeugt.
CM‑010 als Ergänzung/Vorstufe zu boofuzz (Protokoll‑Fuzzing).

Rq-002: nmap/standard scanners N/A — cannot craft or recompute PROFIsafe CRC (documented deviation from nmap default per 4-1 SM-5).
---
I ll first look at your uploaded image, then give you a thorough analysis.Ich habe alle fünf Anhänge vollständig durchgearbeitet: die drei SRIO‑Spezifikationen (Product Requirements, Component Spec COM, System‑Architektur), das Manual und deine Testumgebungs‑Beschreibung. Deine MVO‑Anforderungstabelle und die Gap-/Tool‑Matrix habe ich dagegen gehalten. Die Tools lasse ich bewusst noch außen vor – hier zuerst die gründliche Analyse.

Ein Hinweis vorab: Die Datei mit dem Namen*„Market_Access_and_Compliance…"* hat beim Öffnen inhaltlich die System‑Architektur (201_SRIO) geliefert, nicht das Market‑Access‑Paper. Falls du das Paper wirklich mitanalysiert haben willst, lade es bitte nochmal hoch – aktuell habe ich es nicht im Zugriff.

1. Das Gerät als Prüfobjekt – das Sicherheitsprofil in einem Bild

Bevor man über Gaps und Tools redet, muss die zentrale Architekturentscheidung sitzen, weil fast alle deiner 14 Gaps daraus folgen:

Das SRIO (AL400S/AL401S) ist ein PROFINET/PROFIsafe‑Gateway, SIL 3 / PL e Cat. 4, mit drei STM32F777: COM/CPU3 (Host, Fieldbus, IoT‑Core) und SCPU1/SCPU2 (die sichere Doppelrechner‑Instanz).
Der COM‑Teil ist ausdrücklich nicht funktional sicher ("Not functional safety related"). Die Sicherheit wird über das Black‑Channel‑Prinzip hergestellt: PROFIsafe wird durch PROFINET getunnelt, die SCPU prüft F‑Adresse, CRC und Watchdog end‑to‑end.
Konsequenz: Angriffe auf COM/PROFINET/IoT degradieren im besten Fall zur Verfügbarkeit – bei Kommunikationsverlust fällt das Gerät über F_WD_Time‑Watchdog und Transition 9 in den definierten Fail‑Safe‑Zustand.

Das ist der wissenschaftliche Dreh‑ und Angelpunkt deiner Arbeit, und ich würde ihn im Text ganz nach vorne stellen:

Der Hersteller argumentiert „Security‑Fehler führen zu Safety (sicherer Zustand), nicht zu Gefahr". Die MVO 2023/1230 (Anh. III, 1.1.9 / 1.2.1) verlangt aber Security‑Eigenschaften als Selbstzweck – Integrität, Nachweisbarkeit, Vertraulichkeit, Verfügbarkeit – unabhängig davon, ob am Ende ein sicherer Zustand erreicht wird. Deine Methodik prüft also empirisch die Lücke zwischen**„fällt sicher aus"** und**„ist sicher"**.

Genau diese Trennung macht fast jede deiner Gap‑Begründungen präzise – und deckt zugleich auf, wo deine Tabelle noch unscharf ist (siehe §3).

2. Die sicherheitsrelevanten „Ground‑Truth"-Fakten aus den Dokumenten

Ich habe die Belege gebündelt, weil du sie in der Arbeit sauber referenzieren musst (und weil ein paar davon deine Tabelle korrigieren):

Fieldbus / PROFIsafe
Fakt	Beleg	RelevanzNur Address Type 1 – es wird nur F_Dest_Add geprüft, F_Source_Add NICHT	SRIO‑7830, SRIO‑7794, SRIO‑10806	Korrigiert deine RQ‑001‑Zeile (siehe §3, A)
F_Dest_Add per Rotary‑Switch [1..899], nur im Init gelesen	SRIO‑10812, SRIO‑8803	RQ‑011 physische Barriere
4‑Byte‑CRC, F_CRC_Seed24/32, F_SIL3 – rein prüfsummenbasiert, keine Krypto‑Authentisierung	SRIO‑2998, 6552	RQ‑002/005 Kern-Gap
iParCRC (UINT32) + F_ParCRC (UINT16), extern per TÜV‑Süd‑zertifiziertem T2‑CRC‑Tool erzeugt	SRIO‑9023, 8.6.4.3	RQ‑005
F_WD_Time 50…10000 ms, Default 150 ms; externer HW‑Watchdog	SRIO‑1857, 12868	RQ‑010
DCP Factory‑Reset Mode 2 (mandatory), IP/NameOfStation jederzeit änderbar	SRIO‑7772, 3030, 3029	RQ‑011 zweiter Pfad
IoT‑Core (COM)
Fakt	BelegNur HTTP; HTTPS, Websocket, MQTT explizit NICHT unterstützt	SRIO‑7903/7907/7906/7905
IoT‑Core ist Read‑Only – Passwortschutz wurde bewusst gestrichen, Parameter werden nicht mehr über IoT geschrieben	8.1.3 Password Handling
Max. 2 gleichzeitige HTTP‑Verbindungen	SRIO‑7909
IoT‑Core während SCPU‑Update deaktiviert	SRIO‑11289
Error‑Log über IoT lesbar (/devicestatus/errorlog), ohne dokumentiertes Auth/Delete	SRIO‑10662, 11532
Logging / Audit
Fakt	BelegError‑Log = Circular Buffer, ≥100 Einträge, wird bei Coldstart gelöscht	SRIO‑10703, 10663, 6521
Uptime ebenfalls bei Coldstart zurückgesetzt	SRIO‑15398
REVISION_COUNTER (I&M0) inkrementiert bei jeder Parameteränderung – ohne Zeitstempel, ohne Akteur	SRIO‑3002
Physik / Debug
Fakt	BelegDebug‑ und Test‑Interface nur in Entwicklung, danach per Fusing gesperrt	SRIO‑2580, 1526, 8331
Rotary/DIL‑Switches durch Plastik‑/Metall‑Siegel geschützt	SRIO‑2102, 11001
Die Sicherheits‑Grundannahme
Fakt	Beleg„Usecase assumed to be located in a safe zone behind a firewall"	SRIO‑9402
FW‑Update hinter Firewall durch vertrauenswürdige Person	SRIO‑1196
Security‑Risk‑Assessment gefordert	SRIO‑16243

Diese Firewall‑Annahme ist der normative Angelpunkt: Sie verschiebt die Verantwortung nach außen und ist per Funktionstest am Gerät allein nicht verifizierbar – genau das machst du in der Arbeit sichtbar.

3. Faktencheck deiner RQ→Gap→Tool‑Tabelle

Insgesamt: sehr solide und gut belegt. Die Gaps für RQ‑005, RQ‑007, RQ‑008/009, RQ‑011, RQ‑012, RQ‑013, RQ‑014 decken sich präzise mit den Dokumenten. Es gibt aber einen Faktenfehler und einige konzeptionelle Unschärfen, die du vor der Toolphase glattziehen solltest:

A) 🔴 RQ‑001 – Faktenfehler „Address Type 2"

Deine „Security Function"-Spalte nennt*„F_Dest_Add/F_Source_Add address verification (Address Type 2)"*. Das Gerät unterstützt aber nur Address Type 1, bei dem F_Source_Add gerade NICHT geprüft wird. Das ist doppelt wichtig:

Die Mitigation ist schwächer als in deiner Tabelle behauptet.
Es verstärkt deinen Gap: Ein Spoofing über eine falsche Quelladresse wird gar nicht erkannt – der Nachweis wird dadurch sogar leichter führbar. In deiner Gap‑Spalte deutest du das über SRIO‑7830 schon an, aber die Security‑Function‑Spalte widerspricht dem. Bitte konsistent auf Address Type 1 umstellen.
B) 🟠 STRIDE vs. MVO‑Eigenschaft – eine wiederkehrende Verwechslung

Bei RQ‑004 und RQ‑006 verlangt die MVO eine Identifikations‑Fähigkeit (Integrität/Verfügbarkeit der Identifikationsdaten), du testest aber die Vertraulichkeit (Klartext‑HTTP). Beides ist legitim, aber es sind zwei verschiedene Prüfziele:

Konformitätstest: „Existiert die Identifikationsfunktion und liefert sie korrekt?" (das verlangt der Regulierungstext)
Security‑Weakness‑Test: „Wird die Information unverschlüsselt/ungeschützt preisgegeben?" (dein Zusatzbefund)

Ich würde diese zwei Ebenen in der Methodik explizit benennen, sonst wirkt es, als würdest du am Wortlaut der Anforderung vorbeiprüfen.

C) 🟡 RQ‑011 – deine eigene wissenschaftliche Vorsicht ist goldrichtig

Deine Anmerkung, dass der unauthentifizierte DCP‑Factory‑Reset eine allgemeine PROFINET‑Eigenschaft ist und in den SRIO‑Dokumenten nicht explizit als „ungeschützt" belegt wird (SRIO‑7772/3030 beschreiben nur die Modi), ist methodisch vorbildlich. Genau so kennzeichnen – „auf Protokollwissen basierend, im Test zu verifizieren", nicht als gesicherte Tatsache. Das ist übrigens ein Muster, das du auch bei anderen Zeilen anwenden solltest (z. B. Flooding‑Resilienz RQ‑010).

D) 🟡 RQ‑003 „N.I." und RQ‑014 „N.I."

Bei beiden steht als Security Function „N.I." (nicht implementiert). Das ist korrekt, aber prüfe die Formulierung: Bei RQ‑003 existiert doch eine Teil‑Maßnahme (Siegel + Sichtprüfung), nur eben kein automatisches Tamper‑Logging. Sauberer: „nur physische Siegel, kein Audit‑Trail" statt „N.I.".

4. Was deine Testumgebung kann – und was systematisch NICHT

Das ist der wichtigste Realitäts‑Check vor der Toolauswahl. Deine Zone‑B‑Umgebung (SPS + SRIO + Managed Switch + Raspberry Pi/Kali + Laptop, mit Port‑Mirroring und getrenntem Management‑Netz) ist ein reiner Netzwerk‑/Fieldbus‑Prüfstand.

Deckt ab ✅	Deckt strukturell NICHT ab ❌PROFINET/PROFIsafe Frame‑Injection, Spoofing, CRC‑Manipulation (RQ‑001, 002‑Netz, 005‑Netz, 011‑Netz)	Physische Siegel-/Tamper‑Prüfung (RQ‑002 physisch, RQ‑003)
DCP‑Scan/Reset (RQ‑011)	JTAG/Debug‑Hardware‑Zugriff (RQ‑003, RQ‑008 physischer Teil)
HTTP/IoT‑Core Abfragen, Cleartext‑Nachweis (RQ‑004, 006, 007, 013, 014)	Chip‑/Bus‑Level‑Analyse (Logic‑Analyzer)
Flooding/Fuzzing Fieldbus (RQ‑010)	
Cold‑Start‑Persistenz (RQ‑012) – Strom ziehen geht am Bench	

Folge für deine Tabelle: Ein spürbarer Teil deiner „Concrete Tools" (JTAGulator, Logic‑Analyzer/sigrok, manuelle Siegelprüfung) liegt außerhalb des beschriebenen Aufbaus. Du hast damit faktisch zwei Prüf‑Domänen:

Netzwerk/Fieldbus‑Bench (deine Zone B – der Großteil)
Physical/Hardware‑Bench (Siegel, Debug‑Ports – separater Aufbau nötig oder als „nicht Teil dieser Arbeit" abgrenzen)

Das solltest du früh im Methodikteil als Scoping‑Entscheidung deklarieren, sonst greift ein Gutachter genau hier an.

5. Drei Testkategorien – dein methodisches Rückgrat

Du hast intuitiv schon drei Testtypen vermischt. Ich würde sie explizit als Klassifikation einführen, weil sie sich sauber auf die IEC 62443‑4‑1 „Security Verification & Validation Testing" (SVV) abbilden lassen:

Aktiver Security‑Test – ein Verhalten/Exploit wird provoziert und beobachtet (z. B. RQ‑001 Spoofing‑Frame → nimmt SCPU ihn an?; RQ‑010 Flood → bleibt PROFINET stabil?).
Bestätigender Einzeltest – eine einzelne, gezielte Anfrage beweist An-/Abwesenheit einer Eigenschaft binär (z. B. RQ‑014 ein GET auf /devicestatus/errorlog ohne Auth; RQ‑012 ein Cold‑Start).
Struktureller Nachweis / Design‑Review – ein Feature fehlt konstruktiv, kein aktives Tool nötig (z. B. RQ‑006/013 fehlende geräteseitige Historie; RQ‑005 D fehlendes Secure Boot).

Diese Dreiteilung ist dein Gegenargument gegen den naheliegenden Einwand „warum kein vollautomatischer Scanner überall?": Weil Kategorie 2 und 3 gar keinen Scanner brauchen – ein Nikto/ZAP bringt bei einem bekannten Einzelendpunkt keinen Erkenntnisgewinn. Genau diese Begründung hast du bei RQ‑004/014 schon richtig formuliert; ich würde sie zum generellen Prinzip erheben.

6. Normative Verankerung – der rote Faden, den du für die Tools suchst

Du hast gesagt, du willst dich „möglichst an Normen orientieren". Die gute Nachricht: Dein 62443‑Anker steht schon und ist überwiegend korrekt gesetzt. Er ist der Hebel, um von „Bauchgefühl‑Tools" zu „normativ begründeter Testauswahl" zu kommen. Die Kette, die ich dir für den Methodikteil vorschlagen würde:

Regulierung → Sicherheitsziel → Norm‑Anforderung → Testtyp → Werkzeug

MVO 2023/1230, Anh. III 1.1.9/1.2.1 = die Warum-Ebene (deine 14 RQ).
IEC 62443‑4‑2 (Component / EDR Requirements) = die Was genau-Ebene. Deine CR/EDR‑Zuordnungen (CR 3.1 Kommunikationsintegrität, CR 3.4 SW‑/Info‑Integrität, CR 2.8/2.9/2.12 Audit & Non‑Repudiation, CR 7.1 DoS‑Schutz, CR 7.8 Komponenten‑Inventar, EDR 3.11 Tamper, EDR 3.14 Boot‑Integrität) sind größtenteils stimmig – das ist genau die Norm‑Brücke, die du wolltest.
IEC 62443‑4‑1, Practice SVV = die Wie prüfe ich-Ebene (deine drei Testkategorien oben).
Pentest‑Methodik‑Standards für die eigentliche Durchführung: NIST SP 800‑115, PTES, OSSTMM – die geben dir den Prozessrahmen (Scoping, Evidence, Reporting), den ein Funktionstest im Qualitätsmanagement braucht.
PROFINET Security Guideline (PI) und prEN 50742 (die du schon zitierst) für die fieldbus‑spezifische Ebene.

Damit wird die Toolauswahl ableitbar statt gegriffen: Jedes Tool muss sich künftig rechtfertigen als „demonstriert Konformität/Non‑Konformität zu CR x.y über Testtyp 1/2/3".

7. Offene Punkte, die ich vor der Toolphase klären würde
RQ‑001 Address‑Type‑Korrektur – einbauen (§3 A).
Scoping physisch vs. Netzwerk – gehören Siegel-/JTAG‑Tests in die Arbeit, oder grenzt du sie explizit aus? (§4)
Konformitäts‑ vs. Weakness‑Test – willst du beide Ebenen prüfen oder nur die Security‑Weaknesses? Das entscheidet, ob RQ‑004/006 überhaupt „aktiv" getestet werden. (§3 B)
Gehört das Market‑Access‑Paper in die Analyse? Falls ja, bitte neu hochladen – ich hatte nur die System‑Architektur im Zugriff.
Das mitgeschickte Bild (image.png) kam bei mir nicht als Datei an – ist das die Topologie‑Grafik zur Testumgebung? Falls du willst, dass ich es einbeziehe, lade es bitte erneut hoch.

Wenn du einverstanden bist, würde ich als nächsten Schritt vorschlagen, dass wir Punkt für Punkt die normativ begründete Tool‑Zuordnung aufbauen – also je RQ: 62443‑CR → Testkategorie → minimal nötiges, normkonformes Werkzeug, konsequent gegen deinen Zone‑B‑Bench geprüft. Sag mir vorher nur kurz, wie du Punkt 2 und 3 entscheiden willst (Physik rein/raus, Konformität rein/raus) – davon hängt ab, wie breit die Tool‑Matrix am Ende wird.

Soll ich außerdem die korrigierte RQ‑001‑Zeile direkt als sauberen LaTeX/Text‑Baustein für deinen Anhang formulieren?
---

Let's work through RQ‑006, column by column, with drop‑in text ("→ Put in cell:"). This row has the same conceptual tension as RQ‑004: the regulation asks the device to identify installed software necessary for safe operation (an inventory/integrity obligation, CR 7.8), but your row tests confidentiality (cleartext HTTP). I'll apply the same primary/secondary split so it's consistent with how we fixed RQ‑004.

⚠️ Also — one distinction to keep clean between RQ‑004 and RQ‑006 so they don't look like duplicates:

RQ‑004 = "identify the software and data critical for the EHSRs" → the finding is data/config (B) is not identified.
RQ‑006 = "identify the installed software necessary for safe operation" → this is purely the software inventory (asset D), no data‑completeness angle. So RQ‑006's primary test is: is the software inventory complete and correct? The cleartext issue is secondary (and largely a cross‑reference to RQ‑004/RQ‑014).
RQ‑006 — "Identify the software installed on it that is necessary for safe operation"


Step 2 — Test cases

TC‑006‑A — Software inventory enumeration & completeness (curl · primary)

Objective: Enumerate all installed safety-relevant software components the device identifies, and assess completeness against the actual build (CR 7.8).
Setup: SRIO on OT segment (192.168.0.2), IoT‑Core reachable; device in Operate.
Steps:
curl http://192.168.0.2/deviceinfo/swrevision
curl http://192.168.0.2/deviceinfo/swinfo/cpubootloaderversion
curl http://192.168.0.2/deviceinfo/swinfo/scpuversion
curl http://192.168.0.2/deviceinfo/swinfo/scpubootloaderversion
Cross-check the returned set against the documented installed components (host FW, both SCPU FWs, bootloaders) to identify any component not exposed in the inventory.
Expected: All four endpoints return valid versions; cross-check reveals whether the exposed inventory is complete or whether safety-relevant components are missing from the identifiable set.
Pass/Fail: PASS if the enumerated inventory is complete/correct; gap-confirmation if components are unidentifiable or no consolidated inventory exists.
Evidence: curl outputs rq006a_*.txt + a component-vs-inventory comparison table.

TC‑006‑B — Cleartext transmission of inventory data (Wireshark · secondary)

Objective: Confirm the software-inventory data is transmitted without TLS/access control (confidentiality weakness).
Setup: Laptop NIC1 on mirror port; filter http || tcp.port==80; trigger the TC‑006‑A GETs from the Pi.
Steps: Start capture → issue the /deviceinfo/swinfo/* requests → inspect for TLS handshake vs. cleartext.
Expected: No TLS; firmware/bootloader versions visible in cleartext; no auth challenge.
Pass/Fail: Gap-confirmation (secondary finding to RQ‑006).
Evidence: rq006b.pcap.

(Optional) TC‑006‑C — Cross-verification via PROFINET I&M0/I&M5

Objective: Confirm the software identification is consistent across interfaces (IoT‑Core vs. PROFINET I&M) and complete.
Setup: Wireshark on mirror port; read I&M0 (0xAFF0, SOFTWARE_REVISION) and I&M5 (annotation "host_fw_x.x.x.x").
Steps: Trigger/capture acyclic I&M0/I&M5 reads; compare software revision against the IoT‑Core values from TC‑006‑A.
Expected: Consistent version data across both channels.
Pass/Fail: PASS if consistent; note any discrepancy as an inventory-integrity finding.
Evidence: rq006c.pcap + comparison table.

That's RQ‑006 fully worked, kept clearly distinct from RQ‑004 (pure software inventory vs. software‑and‑data), with the primary/secondary split consistent. Ready for RQ‑007?

---

Let's work through RQ‑007, column by column, with drop‑in text ("→ Put in cell:"). This is your first Availability requirement, and the row is largely correct — the main work is tightening the CR mapping, translating, and separating the two distinct gaps (the "at all times" conflict vs. the 2‑connection‑limit‑as‑DoS‑vector) so each has its own test.

RQ‑007 — "Provide identification information of safety‑relevant installed software at all times in an easily accessible form"

Step 2 — Test cases

TC‑007‑A — Connection-limit exhaustion (curl/netcat · Gap 2)

Objective: Verify whether holding the 2 permitted HTTP connections open blocks all further legitimate access to the identification API → the connection limit acts as a DoS vector.
Setup: Pi on OT/management path; SRIO IoT‑Core at 192.168.0.2:80; device in Operate.
Steps:
Open connection 1 and hold it: curl --no-keepalive http://192.168.0.2/deviceinfo/swrevision & (or a raw nc 192.168.0.2 80 session kept open).
Open connection 2 the same way and hold it.
From a third client/session, attempt curl http://192.168.0.2/deviceinfo/hwversion.
Record whether the 3rd request is refused/times out; then close one held connection and retry.
Expected (confirms Gap 2): 3rd request is blocked/timed out while 2 connections are held; succeeds again once one is released → identification data not reliably accessible.
Pass/Fail: Gap‑confirmation; record refusal behaviour and recovery.
Evidence: terminal logs of all three sessions with timestamps.

TC‑007‑B — Identification API downtime during FW update (curl polling · Gap 1)

Objective: Measure the actual downtime of the identification API while an SCPU firmware update is in progress → violates "at all times".
Setup: Test unit only, controlled test window; polling from the Pi; FW‑update triggered via IoT‑Core /firmware/install (company rule: no production rollout).
Steps:
Start a polling loop: while true; do curl -s -o /dev/null -w "%{http_code} %{time_total}\n" http://192.168.0.2/deviceinfo/swrevision; sleep 1; done | ts (timestamped).
Trigger the SCPU firmware update.
Record the interval during which the identification endpoint is unreachable (device in Update state).
Continue polling until the API recovers post‑update.
Expected (confirms Gap 1): A measurable downtime window where identification data is unavailable → "at all times" not met.
Pass/Fail: Gap‑confirmation; report the downtime duration.
Evidence: timestamped polling log showing the unreachable window.

(Optional) TC‑007‑C — Behaviour under concurrent load (Siege · supplementary)

Objective: Observe how the IoT‑Core service behaves under a higher concurrent‑request profile (graceful rejection vs. instability) — supplementary, not required to prove the gap.
Setup: Zone B; controlled window; monitoring/watchdog on target (company safety rule).
Steps: siege -c 10 -t 2M -v http://192.168.0.2/deviceinfo/swrevision -l rq007c.log (keep concurrency modest given the 2‑connection design).
Expected: Excess connections are cleanly rejected; no crash/instability; device stays in Operate.
Pass/Fail: PASS if stable with clean rejection; FAIL on crash/instability.
Evidence: rq007c.log + device state log.

That's RQ‑007 fully worked, with the two availability gaps separated, the CR mapping corrected to CR 7.1/7.2‑primary, and the Siege‑vs‑curl instrument choice justified. Ready for RQ‑008?

---
Let's work through RQ‑008, column by column, with drop‑in text ("→ Put in cell:").

⚠️ First, the key distinction to keep RQ‑008 separate from RQ‑003 and RQ‑009, because all three are Repudiation/audit rows and a reviewer will check they aren't duplicates:

RQ‑003 = evidence of intervention in hardware components (physical switches/debug) → physical tamper logging.
RQ‑008 = evidence of intervention in the installed software → software‑level intervention logging.
RQ‑009 = evidence of modification of software or its configuration → change logging.

So RQ‑008's center of gravity is**"was a software intervention recorded?"** The REVISION_COUNTER (which tracks parameter changes) is actually a weak/partial fit here — it's really more relevant to RQ‑009 (config modification). I'll flag that so your three rows stay distinct and defensible.

RQ‑008 — "Collect evidence of any legitimate or illegitimate intervention in the software installed on it"


Step 2 — Test cases

TC‑008‑A — Software-intervention logging completeness (curl + Wireshark · Zone B, primary)

Objective: Verify whether a software intervention (FW‑update action) is recorded as an auditable event with sufficient non‑repudiation detail (actor, timestamp).
Setup: Test unit on OT segment (192.168.0.2); IoT‑Core reachable; Wireshark on mirror port (pn_rt || pnio); I&M0 readable via 0xAFF0; controlled window.
Steps:
Read baseline: curl http://192.168.0.2/devicestatus/errorlog and capture I&M0/REVISION_COUNTER.
Trigger a FW‑update/software intervention normally (via IoT‑Core /firmware/install).
Re‑read the error log and I&M0/REVISION_COUNTER.
Inspect whether the intervention produced a log entry, and whether it contains actor and timestamp fields.
Expected (confirms gap): The event is recorded (or REVISION_COUNTER increments) but without actor and without a reliable timestamp → limited non‑repudiation value.
Pass/Fail: Gap‑confirmation; document exactly which fields are present/absent.
Evidence: baseline + post curl outputs, rq008a.pcap, event field analysis.

TC‑008‑B — Debug-port non-logging (JTAGulator / logic-analyzer · separate bench, optional)

Objective: Show that access via the fused debug/test interface (if any residual access exists) produces no software‑intervention log entry.
Setup: Separate physical bench; JTAGulator + logic‑analyzer on the debug/test contacts.
Steps:
Probe the debug/test interface for residual accessibility after fusing.
If any interaction is possible, perform a software‑relevant action via that path.
Read the error log (via Zone B) afterward to check for any entry.
Expected: Either fully fused (no access — design exclusion, not logging) or access produces no log entry → both support the gap.
Pass/Fail: Gap‑confirmation; document which outcome occurred.
Evidence: logic‑analyzer capture, photos, post‑action curl output.

That's RQ‑008 fully worked, kept distinct from RQ‑003 (hardware) and RQ‑009 (config modification), with the REVISION_COUNTER honestly repositioned as a weak marker and the primary software‑event logging path (error log) brought to the front. Ready for RQ‑009?

---
Let's work through RQ‑009, column by column, with drop‑in text ("→ Put in cell:"). This row is already in good shape — the columns are mostly correct and the test logic is strong. Main work: tighten the CR mapping, translate the remaining German, and make sure RQ‑009 stays clearly distinct from RQ‑008.

⚠️ Distinction reminder (so RQ‑008 vs RQ‑009 don't look duplicated): RQ‑008 = evidence of intervention in installed software; RQ‑009 = evidence of modification of software or its configuration. So RQ‑009 is exactly where the REVISION_COUNTER belongs as the primary mechanism (it tracks config/parameter changes) — which is why I repositioned it as only a weak marker in RQ‑008. This is now consistent.

RQ‑009 — "Collect evidence of any modification of the installed software or its configuration"
Step 1 — Column-by-column review

MVO‑ID / Source — RQ‑009, Annex III 1.1.9 → ✅ correct, no change.

IEC 62443 CR — Current: CR 2.8, CR 2.12, CR 3.4

⚠️ Refine. CR 2.8 (auditable events) + CR 2.12 (non‑repudiation) are the right evidence anchors. CR 3.4 (software/info integrity) is about preventing modification, not recording it — that overlaps RQ‑005/RQ‑011. Since RQ‑009 is a logging requirement, I'd make CR 2.8/2.12 primary and add CR 2.11 (timestamps) (the core gap is the missing timestamp), keeping CR 3.4 only as a secondary cross‑reference.
→ Put in cell: CR 2.8 (auditable events); CR 2.12 (non-repudiation); CR 2.11 (timestamps — supports the missing-timestamp gap); CR 3.4 (secondary — integrity cross-reference)

Target Asset — Current: B (Config); D (Firmware); I (Audit Data)

✅ Correct — modification can target config (B) or firmware (D), evidenced in audit data (I). No change; optionally clarify roles.
→ Put in cell: B (Configuration/Parameter — modification target); D (Firmware/Software — modification target); I (Audit Data — evidence)

Threat (STRIDE) — Current: Repudiation → ✅ correct, no change.

Security Function — Current is accurate. Tighten wording and add that error‑log entries also cover FW changes.

→ Put in cell: Configuration change: REVISION_COUNTER (I&M0) increments and iParCRC/F_ParCRC change on parameter modification. Firmware change: FW/HW compatibility check per component + error-log entry; manufacturer-hosted Release Notes document version history per release.

Gap — Current is correct and well‑stated. Add the coldstart‑persistence angle so it links to RQ‑012, and keep the actor/timestamp point.

→ Put in cell: REVISION_COUNTER records THAT a change occurred, but not WHO performed it or WHEN — no actor or timestamp field is documented, limiting genuine non-repudiation. Error-log entries evidencing modification reside in a circular buffer cleared on coldstart, so the evidence is not durably retained. Release Notes are an external artifact, not a device-resident, per-device modification record.

Target Interface Type — Current: Web/API (IoT-Core HTTP, firmware version only); Network (PROFINET acyclic/I&M0 records, for REVISION_COUNTER)

✅ Correct and precise. Optionally add the error‑log path (config/FW modification events land there too).
→ Put in cell: Web/API — IoT-Core HTTP (firmware version + /devicestatus/errorlog); Network — PROFINET acyclic I&M0 (0xAFF0, REVISION_COUNTER) + iParCRC comparison

Tool Category — Current: Log/Audit Review (Protocoll-Layer); Web Application Analysis → ✅ correct; translate slightly.

→ Put in cell: Log/Audit Review (protocol layer + API); Web Application Analysis

Concrete Tool — Current: Wireshark (I&M0/iParCRC) + curl (FW version)

✅ Correct tools; translate and add error‑log read.
→ Put in cell: Wireshark PROFINET dissector (I&M0/REVISION_COUNTER + iParCRC comparison via acyclic 0xAFF0) + curl (firmware version + /devicestatus/errorlog via IoT-Core). nmap/scanners N/A — known endpoints, structural finding.

Concrete Tool (Reason) — Current is already in English and good. Keep, minor polish.

→ Put in cell: Perform two different configuration changes one after the other (e.g., two different parameter changes, simulated as if on two different days or by two different "people"). Read the REVISION_COUNTER (and iParCRC) afterward. Result: although the counter has incremented (the change is visible), it is impossible to distinguish which of the two changes occurred, when, or by whom — only that "a change took place." curl additionally confirms only the current FW version is exposed, not a modification history.

Prioritisation — Current: Web-Teil: Web/API-Block; Netzwerk-Teil: I&MO auslesen

⚠️ Translate.
→ Put in cell: Web/API part: Web/API block (no dependencies). Network part: read I&M0 (I&M0 block)

Environment feasibility check: Fully runs in Zone B — parameter changes via the PLC/engineering tool or acyclic write, REVISION_COUNTER/iParCRC read via Wireshark on the mirror port, FW version + error log via curl. No physical bench. ✅

Company‑doc mapping: CM‑009 (logging completeness) is the natural home; norm anchor CR 2.8/2.11/2.12. This is a pure audit/logging review — a good place to note it's a structural finding (no active exploit needed), so no Scapy/Nikto required.

Step 2 — Test cases

TC‑009‑A — Non-attributability of configuration modifications (Wireshark + curl · primary)

Objective: Demonstrate that two distinct configuration changes are recorded only as an incremented counter, with no way to attribute which change, when, or by whom → non‑repudiation gap.
Setup: SRIO on OT segment (192.168.0.2); PLC/engineering tool able to write parameters; Wireshark on mirror port (pn_rt || pnio); I&M0 readable via 0xAFF0.
Steps:
Read baseline REVISION_COUNTER + iParCRC (Wireshark) and error log (curl http://192.168.0.2/devicestatus/errorlog).
Apply configuration change #1 (e.g., modify a safe‑input filter/symmetry parameter). Record your own timestamp/identity externally.
Read REVISION_COUNTER + iParCRC again.
Apply a different configuration change #2 (e.g., a different parameter). Record externally.
Read REVISION_COUNTER + iParCRC again, and re‑read the error log.
Attempt, using only device‑resident data, to reconstruct which change was #1 vs #2, when each occurred, and who made them.
Expected (confirms gap): Counter increments each time and iParCRC changes, but device‑resident data cannot distinguish the two changes, their times, or actors → "a change took place" is all that's provable.
Pass/Fail: Gap‑confirmation; document the absence of timestamp/actor fields.
Evidence: rq009a.pcap (three I&M0 reads), curl error‑log outputs, your external change journal for contrast.

TC‑009‑B — Firmware-modification evidence completeness (curl · secondary)

Objective: Verify whether a firmware modification is evidenced device‑side as a durable, per‑device record, or only as the current version + external Release Notes.
Setup: Test unit, controlled window; IoT‑Core reachable.
Steps:
Read current FW version (curl http://192.168.0.2/deviceinfo/swrevision) and error log.
Perform a firmware change (update) via /firmware/install.
Re‑read FW version + error log.
Check whether a device‑resident record of the previous version / modification history exists (vs. only the new current version).
Expected (confirms gap): Only the current FW version is exposed; no device‑resident modification history → evidence relies on external Release Notes.
Pass/Fail: Gap‑confirmation.
Evidence: before/after curl outputs, error‑log excerpts.

That's RQ‑009 fully worked, kept distinct from RQ‑008, with REVISION_COUNTER now correctly positioned as the primary mechanism here and the CR mapping tightened toward the logging CRs. Ready for RQ‑010?
---

Let's work through RQ‑010, column by column, with drop‑in text ("→ Put in cell:"). This is your control‑system resilience/DoS requirement, and it's one of the more genuinely offensive tests in your set — so the environment and safety caveats matter a lot here.

⚠️ One methodological caution up front: RQ‑010's gap ("no rate‑limiting/flood‑protection on the fieldbus") is — like the RQ‑011 DCP point you already flagged — partly based on general PROFINET/stack knowledge, not on an explicit SRIO document statement. So the gap should be phrased as**"to be verified by test,"** not as an established fact. I've written the cell that way.

RQ‑010 — "The control system shall withstand reasonably foreseeable malicious attempts from third parties that could lead to a hazardous situation"
Step 1 — Column-by-column review

MVO‑ID / Source — RQ‑010, Annex III 1.2.1 → ✅ correct, no change.

IEC 62443 CR — Current: CR 7.1 (1)

⚠️ Refine. CR 7.1 (DoS protection) is right, and RE(1) is the specific rate‑limiting enhancement your gap targets — but write it in the standard's notation and add CR 3.5 (Input validation) because you're also fuzzing malformed PROFINET frames (robustness, not just volume).
→ Put in cell: CR 7.1 + RE(1) (DoS protection / rate limiting); CR 3.5 (input validation — malformed-frame robustness)

Target Asset — Current: A (Trusted Safety Function), B (PROFINET), H (Network), (E Safety Monitoring)

⚠️ Small precision. The asset under attack is the PROFINET/COM stack (B/H); what must be preserved is the trusted safety function (A) via safety monitoring/watchdog (E). Label roles rather than listing flat.
→ Put in cell: B/H (PROFINET stack / network — attack surface); A (Trusted Safety Function — must be preserved); E (Safety Monitoring/watchdog — mitigation)

Threat (STRIDE) — Current: Denial of Service

⚠️ DoS is a category, not a STRIDE letter; in STRIDE terms this is Denial of Service (the D in STRIDE) — so it's actually fine. Optionally note Tampering for the malformed‑frame fuzzing angle.
→ Put in cell: Denial of Service (primary); Tampering (malformed-frame fuzzing)

Security Function — Current is accurate. Tighten and correct "state transition 9" wording to match the passivation concept.

→ Put in cell: External hardware watchdog + PROFIsafe F_WD_Time device-acknowledgment watchdog trigger a controlled passivation to the defined fail-safe state on communication loss/staleness (fail-safe transition). Max. 2 concurrent HTTP connections limit COM/IoT-side resource exhaustion.

Gap — Current is correct but should be marked "to verify." Add the "safe‑fail ≠ available" nuance (a successful flood that forces constant passivation is itself a hazard‑adjacent availability loss).

→ Put in cell: Mitigations address loss/staleness of communication, not a deliberate flooding/DoS or malformed-frame attack on the PROFINET stack itself. No rate-limiting or flood-protection (cf. CR 7.1 RE(1)) is documented for the fieldbus interface — based on general PROFINET/stack knowledge, to be verified by test. Note: even if flooding only forces repeated passivation, continuous unavailability of the safety function is itself an availability impact under RQ-010.

Target Interface Type — Current: Network (PROFINET/PROFIsafe); Physical (Power supply)

⚠️ The power‑supply line is odd for a DoS‑by‑flood requirement — power interruption is a different threat. Either drop it or reframe it as an optional resilience check. Keep the network as primary.
→ Put in cell: Network — PROFINET/PROFIsafe (L2, EtherType 0x8892) — primary. Optional: power-supply interruption resilience (separate resilience check, not flooding)

Tool Category — Current: Network DoS/ Flood Testing; Fuzzing Framework (Fieldbus) → ✅ correct.

→ Put in cell: Network DoS / Flood Testing; Protocol Fuzzing (fieldbus)

Concrete Tool — Current: Scapy (PROFINET-Flood) + boofuzz (Protokoll-Fuzzing)

✅ Correct choices — and this is a legitimate place where nmap is NOT sufficient (it can't flood/fuzz fieldbus frames), so document the deviation. Add the in‑path requirement note for boofuzz targeting the cyclic exchange.
→ Put in cell: Scapy (PROFINET/PROFIsafe flood generation) + boofuzz (protocol fuzzing of the fieldbus interface). nmap/generic web-DoS tools N/A — cannot generate/fuzz fieldbus frames (documented deviation per 4-1 SM-5). Active tools only with target monitoring/watchdog (company safety rule).

Concrete Tool (Reason) — Current is good English. Keep, expand slightly.

→ Put in cell: Explicitly tests for the absence of rate limiting on the fieldbus (CR 7.1 RE(1)), which generic web-DoS tools do not cover. Scapy generates high-rate/oversized PROFINET traffic to test flood resilience; boofuzz sends malformed frames to test stack robustness (CR 3.5). Observe whether the device stays in Operate, passivates cleanly, or becomes unstable.

Prioritisation — Current: Flood/Fuzzing-Test

⚠️ Translate; note this needs its own controlled window (disruptive).
→ Put in cell: Flood / fuzzing test (dedicated controlled window; disruptive)

Environment feasibility check: This is the most disruptive test in your set. Flooding/fuzzing can be done side‑inject (Pi injects onto the OT segment), but if you want to disrupt the specific PLC↔SRIO cyclic stream you may need in‑path bridge mode — the same mode reserved for the watchdog test in your environment doc. Mandatory: PLC + SCPU state monitoring and a hardware watchdog on the target during the run (company safety rule). Run only on a test unit in an isolated Zone B, never touching production.

Company‑doc mapping: CM‑010 (Fuzzing/Robustness, boofuzz) is the direct home for the fuzzing part; the flood part conceptually touches CM‑009 (load) but Siege is web‑only, so Scapy is the correct fieldbus instrument — flag this to the TM as a fieldbus gap in the CM baseline. Norm anchor: CR 7.1 RE(1) + CR 3.5; also IEC 62443‑4‑1 SVV‑3 (fuzz/DoS testing is part of vulnerability testing).

Step 2 — Test cases

TC‑010‑A — PROFINET flood resilience / rate-limiting absence (Scapy · active)

Objective: Determine whether high‑rate PROFINET traffic degrades or disrupts the safety communication, and whether any rate‑limiting is present (CR 7.1 RE(1)).
Setup: Pi on OT segment (side‑inject; in‑path bridge if targeting the cyclic stream); PLC in RUN; SCPU/PLC state + F‑DO outputs monitored; hardware watchdog active; dedicated controlled window.
Steps:
Baseline the cyclic PROFIsafe exchange (Wireshark, mirror port) — cycle time, jitter.
Generate escalating PROFINET traffic with Scapy (increasing packet rate / oversized frames toward the SRIO).
Observe: does the SRIO stay in Operate, passivate to fail‑safe, or become unstable? Does the PLC log connection interrupts?
Record the traffic rate at which behaviour changes.
Expected: If no rate‑limiting exists, sufficient flood forces passivation or connection loss → confirms the gap (and quantifies the threshold). If the device stays stable, document the resilience.
Pass/Fail: Gap‑confirmation with the observed threshold; note whether passivation is controlled (safe) or uncontrolled (unsafe).
Evidence: baseline + attack .pcap, Scapy script, PLC/SCPU state log, rate‑vs‑behaviour table.

TC‑010‑B — Fieldbus protocol fuzzing / stack robustness (boofuzz · active)

Objective: Verify the PROFINET/PROFIsafe stack does not crash or behave undefined on malformed/unexpected input (CR 3.5, SVV‑3).
Setup: Pi with boofuzz targeting the fieldbus interface; PLC in RUN; crash monitoring/watchdog on target; boofuzz web UI (127.0.0.1:26000) for crash logging; controlled window.
Steps:
Define a boofuzz session modeling the target PROFINET frame structure (fields to fuzz: header, length, F‑fields).
Run the fuzzing campaign; monitor SRIO state, outputs, and PLC diagnosis continuously.
Log every crash/hang with payload, timestamp, and device state; begin root‑cause on any finding.
Expected: No crash/undefined behaviour → PASS; any crash/hang/uncontrolled state → FAIL (robustness gap).
Pass/Fail: PASS if no crash and every fault leads to a controlled safe state; FAIL on crash/instability.
Evidence: boofuzz session DB (boofuzz-results/), crash logs, correlated device‑state log.

(Optional) TC‑010‑C — Power-supply interruption resilience (separate resilience check)

Objective: Confirm the device reaches/holds a defined safe state on power interruption (distinct from network flooding).
Setup: Controlled power switching on a test unit; outputs + PLC monitored.
Steps: Interrupt US/UA supply briefly and on longer scales; observe safe‑state behaviour and recovery (non‑persistent safe state per spec).
Expected: Outputs go to safe state on loss; controlled recovery on restore.
Pass/Fail: PASS if defined safe state maintained; FAIL otherwise.
Evidence: power‑event log + output/PLC state capture.

That's RQ‑010 fully worked — with the gap correctly flagged as "verify by test," the CR notation fixed, the power‑supply interface reframed, and the disruptive‑test safety caveats made explicit. Ready for RQ‑011?
---

Let's work through RQ‑011, column by column, with drop‑in text ("→ Put in cell:"). This is the densest and most important row in your whole table — it's your "major finding" (device‑side authorization was deliberately dropped). Because it bundles four independent attack paths, my main structural recommendation is to keep them clearly labelled as sub‑paths (a)–(d) in every column, so a reviewer can follow each one. I'll also carry forward your own excellent caveat about the DCP reset being "to verify, not established fact."

⚠️ Structural note: This row currently packs so much that it risks becoming unreadable. Two options: (1) keep it as one RQ‑011 row with explicit sub‑paths (a)–(d) as I've done below, or (2) split into RQ‑011a (fieldbus param write), RQ‑011b (DCP reset), RQ‑011c (IoT‑Core write — negative), RQ‑011d (physical bypass). I recommend option 1 for the appendix table + option 2's granularity in the test cases. Flag this choice to your Technical Manager.

RQ‑011 — "Prevent modifications to safety‑relevant settings or rules… where such modifications could lead to a hazardous situation"
Step 1 — Column-by-column review

MVO‑ID / Source — RQ‑011, Annex III 1.2.1 → ✅ correct, no change.

IEC 62443 CR — Current: CR 1.1, CR 1.2, CR 2.1 (2), CR 3.4

✅ Strong mapping. CR 1.1 (Human user ID&auth), CR 1.2 (Software/device ID&auth), CR 2.1 + RE(2) (Authorization enforcement), CR 3.4 (info integrity). Write RE in standard notation and add the DCP hook.
→ Put in cell: CR 1.1 (user ID&auth); CR 1.2 (device/software ID&auth); CR 2.1 + RE(2) (authorization enforcement); CR 3.4 (config integrity); CR 1.1/1.2 also anchor the unauthenticated DCP-reset sub-path

Target Asset — Current: B (Safety Config), G (Operating Mode)

✅ Correct. Optionally add "communication config" since DCP reset also wipes NameOfStation/IP.
→ Put in cell: B (Safety Config/parameters); G (Operating mode / F-address via switches); communication config (NameOfStation/IP — affected by DCP reset)

Threat (STRIDE) — Current: Tampering, Spoofing, Elevation of Privilege → ✅ correct — this is genuinely a multi‑class row. No change.

Security Function — Current is accurate. Add the IoT‑Core read‑only fact explicitly (it's the counterpart to the dropped password).

→ Put in cell: F-address change and FW-update mode entry require physical access to the rotary/DIL switches plus a power-cycle — a physical-presence barrier for these two specific actions. IoT-Core is designed read-only (no parameter writes via IoT). Parameter writes occur only via the fieldbus/PLC engineering tool.

Gap — Current is excellent but mixes German + your caveat. Restructure into the four sub‑paths, English, with the DCP "to verify" flag preserved.

→ Put in cell: Major finding: device-side password protection for safety-parameter writes was explicitly dropped; IoT-Core was made read-only instead. (a) Parameter writes via fieldbus: authorization is fully delegated to an external, unverified assumption (locked cabinet, restricted network); CR 1.1/1.2/2.1 are not enforced on the device itself. No mechanism exists for learning-phase settings. (b) DCP "Reset to Factory" operates at Layer 2 and is, per general PROFINET knowledge, unauthenticated — a node in the same segment could reset safety-relevant/communication config (Mode 2, optionally 3/4) without touching the physical switch barrier. NOTE: SRIO-7772/3030 describe only the reset modes, not their authentication → this is based on general protocol knowledge and MUST be verified by test, not treated as established fact. (c) IoT-Core write path: expected to be correctly blocked (read-only) — tested for confirmation, not to prove the gap. (d) Physical barrier robustness: whether the switch position can be changed without visible tampering.

Target Interface Type — Current: Network (PROFINET/PROFIsafe records); Physical (Rotary/DIL switch)

⚠️ Add DCP (L2) and IoT‑Core HTTP explicitly.
→ Put in cell: Network — PROFINET acyclic parameter records (param-begin/write/param-end); Network — DCP (Layer 2, factory reset); Web/API — IoT-Core HTTP (write attempt, negative); Physical — rotary/DIL switch (separate bench)

Tool Category — Current: Authentication & Authorization Testing; Physical Access Testing → ✅ correct.

→ Put in cell: Authentication & Authorization Testing; Physical Access Testing

Concrete Tool — Current lists everything (good) but in German and unstructured. Restructure per sub‑path, translate.

→ Put in cell: (a) Scapy (custom PROFINET param-begin/write/param-end sequence per SRIO-7749, sent WITHOUT prior physical switch access). (b) pnio_dcp / profi-dcp (Python) or Scapy (scapy.contrib.pnio_dcp) for the factory-reset request + Wireshark ("Set OK" response verification). (c) curl / OWASP ZAP (unauthenticated PUT/POST against IoT-Core parametrization endpoints — expected: blocked). (d) manual physical bypass test (change switch without visible tampering) + FW-update-mode-entry replay (Wireshark reference capture of the legitimate trigger + Scapy replay without the physical switch). nmap N/A — this is auth/authz, not port discovery.

Concrete Tool (Reason) — Current is a full English/German paragraph; keep the English substance, restructure per sub‑path.

→ Put in cell: (a) Scapy directly proves the core gap: since authorization is fully delegated to the physical switch (asset G) and CR 1.1/1.2/2.1 are not device-enforced, test whether a pure network attacker — without switch access — can send a valid param-begin/write/param-end sequence that the SCPU accepts. A positive finding (frame processed) confirms the physical barrier is the only effective control and is bypassable by protocol knowledge alone. (b) pnio_dcp offers a high-level factory-reset request (DCPControlBlock) without manual frame building; Wireshark confirms via the "Set OK" response whether the reset executed — same normative gap over the network path. (c) curl/ZAP confirm the IoT-Core HTTP path has no write/auth gate; since IoT-Core is documented read-only, a negative result (no write possible) is expected — this validates that path is secured, not the gap itself. (d) The physical bypass test independently checks whether the switch position can be changed without visible damage, ruling out that the assumed physical barrier is trivially circumvented.

Prioritisation — Current: Physischer F-Adress-/Mode-Test + Power-Cycle Prüfen: löscht dieser Cycle bereits das Log?…

⚠️ Translate; and note the important sequencing dependency you spotted (power‑cycle may clear the log — order matters vs RQ‑012).
→ Put in cell: Network auth/authz tests (fieldbus + DCP) — primary. Physical F-address/mode test + power-cycle — separate bench. SEQUENCING: a power-cycle may already clear the error log (RQ-012) — run any log-dependent step BEFORE the power-cycle.

Environment feasibility check: Sub‑paths (a), (b), (c) all run in Zone B side‑inject (Pi active on OT segment; curl/ZAP over HTTP; DCP is L2 on the same segment). Sub‑path (d) physical is a separate bench. All active writes/resets on a test unit in a controlled window with monitoring (company safety rule). Critical sequencing: the DCP reset and any power‑cycle are destructive to device state/log — schedule them last and after RQ‑012's log tests.

Company‑doc mapping: (a)/(b) → no clean CM covers fieldbus/DCP authorization → flag to TM as a baseline gap. (c) → CM‑004 (RBAC/PrivEsc, ZAP) — but note Striegel's comment that only Bernatzky/Rosenheim uses roles; here IoT‑Core is admin‑only/read‑only, so CM‑004 mainly confirms the write path is blocked. (d) → CM‑007 hardware extension. Norm anchors: CR 1.1/1.2/2.1 RE(2).

Step 2 — Test cases

TC‑011‑A — Unauthorized fieldbus parameter write (Scapy · active) — the core gap test

Objective: Prove a network attacker without physical switch access can send a valid param‑begin/write/param‑end sequence that the SCPU accepts → device‑side authorization (CR 1.1/1.2/2.1) not enforced.
Setup: Pi side‑inject on OT segment; target in a state that accepts parametrization; SCPU/PLC state monitored; watchdog; controlled window.
Steps:
Capture a legitimate parametrization sequence (Wireshark, mirror) as reference (per SRIO‑7749 acyclic write between param‑begin/param‑end).
In Scapy, craft the param‑begin → write (safety‑relevant parameter) → param‑end sequence without any physical switch interaction.
Send to the SRIO; observe whether the SCPU validates and applies the parameter (enters Operate with the injected config).
Expected (confirms gap): Sequence accepted → physical barrier is the only control; bypassable by protocol knowledge alone.
Pass/Fail: Gap‑confirmation; record whether the parameter took effect.
Evidence: reference + attack .pcap, Scapy script, SCPU/PLC state log.

TC‑011‑B — Unauthenticated DCP factory reset (pnio_dcp/Scapy · active) — second path, VERIFY

Objective: Test whether an unauthenticated DCP "Reset to Factory" (Mode 2, optionally 3/4) executes from a same‑segment node, resetting communication/safety‑relevant config without touching the switch barrier. Framed as verification of a protocol‑knowledge assumption, not a given.
Setup: Pi on OT segment; Wireshark on mirror; run LAST (destructive — wipes NameOfStation/IP); controlled window.
Steps:
Baseline device identity (NameOfStation, IP) via DCP Identify.
Send a DCP Set → Reset‑to‑Factory request (pnio_dcp DCPControlBlock, or scapy.contrib.pnio_dcp).
Verify via Wireshark whether a "Set OK" response is returned and the device identity is actually reset.
Expected: If "Set OK" + identity reset → unauthenticated reset confirmed (gap over network path). If rejected → SRIO implements additional protection (documents a positive security property).
Pass/Fail: Gap‑confirmation OR positive security finding — either outcome is a documented result.
Evidence: before/after DCP identity, rq011b.pcap with the Set/Set‑OK exchange.

TC‑011‑C — IoT-Core write attempt (curl/ZAP · negative confirmation)

Objective: Confirm the IoT‑Core HTTP path correctly rejects parameter writes (read‑only design) — validates a secured path, not the gap.
Setup: Pi over HTTP to IoT‑Core; device in Operate.
Steps: Attempt unauthenticated PUT/POST against parametrization‑relevant IoT‑Core endpoints (e.g., a write to a safe‑parameter node); optionally an active ZAP scan of the tree.
Expected: All write attempts rejected (read‑only) → path correctly secured.
Pass/Fail: PASS if writes are blocked; FAIL (unexpected) if any write succeeds.
Evidence: curl responses / ZAP report rq011c_report.html.

TC‑011‑D — Physical barrier robustness + FW-update-mode replay (manual + Scapy · separate bench)

Objective: (i) Check whether the switch position can be changed without visible tampering; (ii) test whether the FW‑update‑mode entry trigger can be replayed without the physical switch.
Setup: Separate physical bench for (i); Zone B for (ii) replay; controlled window.
Steps:
(i) Attempt to change the rotary/DIL switch (F‑address / mode 999) without visibly damaging the seal.
(ii) Capture the legitimate FW‑update‑mode entry signaling (Wireshark), then Scapy‑replay it without operating the physical switch; observe whether the device enters update mode.
Expected: (i) any change leaves visible evidence; (ii) if replay triggers update mode without the switch → confirms the barrier is bypassable over the network.
Pass/Fail: Gap‑confirmation depending on outcomes; document each.
Evidence: photos (i), reference + replay .pcap (ii), device state log.

That's RQ‑011 fully worked, with the four attack paths cleanly separated, your DCP "verify‑don't‑assume" caveat preserved, the IoT‑Core path correctly framed as a negative confirmation, and the critical power‑cycle/log sequencing dependency flagged. Ready for RQ‑012?
---

Let's work through RQ‑012, column by column, with drop‑in text ("→ Put in cell:"). This is one of your cleanest, most defensible rows — a confirmed non‑conformity backed directly by the spec (log cleared on coldstart; ≥100 entries fixed). The work here is mostly tightening, translating, and adding the two capacity/retention angles so the "5‑year" gap is fully argued.

RQ‑012 — "Enable a tracing log of data generated in relation to an intervention for five years after placing on the market / putting into service"
Step 1 — Column-by-column review

MVO‑ID / Source — RQ‑012, Annex III 1.2.1 → ✅ correct, no change.

IEC 62443 CR — Current: CR 2.8, CR 2.9

✅ Correct and well‑chosen. CR 2.8 (Auditable events) + CR 2.9 (Audit storage capacity) — CR 2.9 is exactly the right anchor for a retention/capacity requirement. Optionally add CR 2.10 (Response to audit processing failures) since overwrite‑on‑full is a related behavior.
→ Put in cell: CR 2.8 (auditable events); CR 2.9 (audit storage capacity — primary for retention); CR 2.10 (response to audit-storage overflow — circular-buffer overwrite)

Target Asset — Current: I (Audit Data) → ✅ correct, no change.

→ Put in cell: I (Audit Data — the tracing log)

Threat (STRIDE) — Current: Repudiation → ✅ correct, no change.

Security Function — Current: accurate. Make the two limiting properties explicit and add the "non‑cold‑start survival" nuance.

→ Put in cell: Non-volatile circular-buffer error log (≥100 entries), readable via IoT-Core. Survives non-cold-start resets but is cleared on coldstart; when full, oldest entries are overwritten (circular buffer).

Gap — Current is strong. Tighten and separate the two independent conflicts with the 5‑year mandate (deletion + capacity).

→ Put in cell: Confirmed non-conformity — two independent conflicts with the 5-year retention mandate: (1) Deletion: the log is explicitly cleared on every coldstart (SRIO-6521), so intervention data does not persist across a coldstart. (2) Capacity: the log is a fixed ≥100-entry circular buffer (SRIO-10703/10663), so once full, older intervention data is overwritten regardless of the 5-year window. Neither mechanism provides the durable per-intervention retention RQ-012 requires.

Target Interface Type — Current: Physical (power cycle); Web/API (IoT-Core, /devicestatus/errorlog) → ✅ correct.

→ Put in cell: Web/API — IoT-Core HTTP (/devicestatus/errorlog, read); Physical — power cycle (coldstart trigger)

Tool Category — Current: Data Persistence/ Retention Testing; Physical Interface Testing (Power Cycle) → ✅ correct.

→ Put in cell: Data Persistence / Retention Testing; Physical Interface Testing (Power Cycle)

Concrete Tool — Current: curl/Burp + physical power cycle

⚠️ Small refine. Burp adds nothing here (single known endpoint, plain read) — curl is sufficient, consistent with your RQ‑004/014 rationale. Keep Burp only as optional. Add that the capacity test needs log‑filling (many events).
→ Put in cell: curl (read /devicestatus/errorlog before/after coldstart; and to fill/observe the circular buffer) + physical power-cycle. Burp/scanners N/A — single known endpoint, structural finding; curl is sufficient.

Concrete Tool (Reason) — Current is good English. Keep; add the capacity‑overflow test rationale.

→ Put in cell: curl reads the log before and after the coldstart, enabling direct comparison of entry count and content. The physical power-cycle reliably triggers the documented coldstart-deletion mechanism. A single run is sufficient as structural evidence — one deletion already contradicts the 5-year mandate; a real 5-year test is neither practical nor necessary since the mechanism is documented as consistent/reproducible. Separately, generating >100 events demonstrates the circular-buffer overwrite (capacity conflict), without any power-cycle.

Prioritisation — Current: Erzwungener Cold-Start (ZULETZT – zerstört Log-Zustand für dieses Gerät)

⚠️ Translate; keep the critical sequencing warning (this links to RQ‑003/008/011 which also read the log).
→ Put in cell: Forced coldstart — run LAST (destroys the log state for this unit). SEQUENCING: perform all log-dependent tests (RQ-003/008/009/011) BEFORE this coldstart.

Environment feasibility check: Fully runs in Zone B — curl over the IoT‑Core HTTP path; power‑cycle physically at the bench. The coldstart test is destructive to the log state, so per your own note it must be the last log‑touching action on that unit — this is the same sequencing dependency flagged in RQ‑011. ✅

Company‑doc mapping: Closest is CM‑009 (logging) for the audit angle, but this is really a data‑retention/persistence test with no direct CM equivalent → flag to TM. Norm anchor: CR 2.8/2.9/2.10. This is a pure structural/persistence finding — no offensive tool, no Scapy.

Step 2 — Test cases

TC‑012‑A — Coldstart log deletion (curl + power-cycle · primary, run LAST)

Objective: Demonstrate that intervention data in the error log does not survive a coldstart → violates 5‑year retention (deletion conflict).
Setup: Test unit on OT segment (192.168.0.2), IoT‑Core reachable; all other log‑dependent tests already completed; controlled window.
Steps:
Ensure the log contains known entries (from prior tests, or generate a few events).
Read and save the log: curl http://192.168.0.2/devicestatus/errorlog > rq012a_before.txt.
Perform a physical coldstart (full power‑cycle of US/UA).
After reboot, read again: curl http://192.168.0.2/devicestatus/errorlog > rq012a_after.txt.
Compare entry count/content before vs after.
Expected (confirms gap): Log is empty/cleared after coldstart → intervention data not retained.
Pass/Fail: Gap‑confirmation (confirmed non‑conformity); one run suffices as structural evidence.
Evidence: rq012a_before.txt, rq012a_after.txt, power‑event timestamp.

TC‑012‑B — Circular-buffer capacity overflow (curl · capacity conflict, non-destructive)

Objective: Demonstrate that once the log exceeds its fixed ≥100‑entry capacity, older intervention data is overwritten → violates 5‑year retention (capacity conflict), independent of coldstart.
Setup: Test unit; a repeatable way to generate loggable events (e.g., repeated diagnosable faults / parameter events); IoT‑Core reachable. No power‑cycle needed — can run before TC‑012‑A.
Steps:
Read baseline log and note the oldest entry.
Generate >100 new loggable events (repeat a diagnosable action).
Re‑read the log; check whether the original oldest entry has been overwritten and total entries are capped.
Expected (confirms gap): Oldest entries overwritten; entry count capped at the fixed buffer size → no durable retention.
Pass/Fail: Gap‑confirmation (capacity conflict).
Evidence: baseline + post‑fill curl outputs showing overwrite and the fixed cap.

That's RQ‑012 fully worked — with the retention gap now argued on both axes (deletion and capacity), Burp downgraded to optional, and the "run LAST" sequencing tied back to RQ‑003/008/009/011. Ready for RQ‑013?
---


Let's work through RQ‑013, column by column, with drop‑in text ("→ Put in cell:"). This is another clean, structural non‑conformity row — well argued already. The work is mostly tightening, translating one cell, and making sure it stays clearly distinct from RQ‑012.

⚠️ Distinction reminder (RQ‑012 vs RQ‑013): RQ‑012 = tracing log of intervention data (5‑year retention); RQ‑013 = tracing log of safety‑software versions uploaded (5‑year per upload). Same 5‑year mandate, different data object. Your row already states this — I'll keep it sharp so they don't read as duplicates.

RQ‑013 — "Enable a tracing log of the versions of safety software uploaded… for five years after each upload"
Step 1 — Column-by-column review

MVO‑ID / Source — RQ‑013, Annex III 1.2.1 → ✅ correct, no change.

IEC 62443 CR — Current: CR 2.8, CR 2.9

✅ Correct — same audit/retention anchors as RQ‑012 (CR 2.8 auditable events, CR 2.9 storage capacity), fitting because it's a retention‑of‑version‑records requirement. Optionally add CR 7.8 (component/software inventory) since the data object is software versions — it ties the version‑tracking to the inventory family.
→ Put in cell: CR 2.8 (auditable events); CR 2.9 (audit storage capacity — retention); CR 7.8 (secondary — software-version inventory context)

Target Asset — Current: I (Audit Data); D

⚠️ Clarify the "D". Here D = the safety software whose version must be logged; I = the version tracing log itself.
→ Put in cell: I (Audit Data — version tracing log); D (Safety Software — the versioned object whose uploads must be logged)

Threat (STRIDE) — Current: Repudiation → ✅ correct, no change.

Security Function — Current is accurate. Tighten wording.

→ Put in cell: Current firmware version readable via IoT-Core (/deviceinfo/swrevision, /firmware/version) and PROFINET I&M0/I&M5; manufacturer-hosted Release Notes document version history per release (SRIO-16242).

Gap — Current is strong. Keep, but structure the failure against the literal requirement (device‑resident + tamper‑evident + per‑upload + timestamp + 5‑year) so each missing property is visible.

→ Put in cell: The device exposes only the CURRENT firmware version, not a historical, per-device, per-upload log. Release Notes are a manufacturer/website artifact — not device-resident, not per-device/serial, not tamper-evident, with no guaranteed 5-year retention per upload and no timestamp per upload — so they do not satisfy the literal requirement. prEN 50742 §7.3.1 explicitly excludes SW-version storage from the tracing log, reinforcing the gap. Missing properties vs. requirement: device-residence, tamper-evidence, per-upload record, per-upload timestamp, 5-year retention.

Target Interface Type — Current: Web/API (IoT-Core, firmware version)

⚠️ Add the documentation artifact (Release Notes) since the actual proof comes from reviewing it, plus optional I&M5.
→ Put in cell: Web/API — IoT-Core HTTP (/deviceinfo/swrevision, /firmware/version); Network — PROFINET I&M0/I&M5 (software revision/annotation); Documentation — manufacturer Release Notes (review artifact)

Tool Category — Current: Information Disclosure/ Documentation Review; Web Application Analysis

⚠️ Slightly reframe — this isn't really Information Disclosure; it's version read-out + documentation review (a structural/negative proof).
→ Put in cell: Version Read-out (device); Documentation Review (structural / negative proof)

Concrete Tool — Current: curl + manual document review

✅ Correct and appropriately minimal. Add the nmap/scanner‑N/A note for consistency.
→ Put in cell: curl (query the firmware-version endpoints — confirms only current version exposed) + manual document review (Release Notes vs. the literal RQ-013 properties). Optional: Wireshark for I&M5 cross-check. No active pentest tool required — structural (missing-feature) finding; nmap/Nikto N/A.

Concrete Tool (Reason) — Current is good English. Keep, minor polish + tie to SVV‑1 negative-proof style (as you referenced in RQ‑005).

→ Put in cell: curl confirms the IoT-Core API returns only the currently installed firmware version, not a historical sequence of previous uploads — supporting evidence that no device-resident version-tracking mechanism exists. The actual proof is the documentation review: Release Notes are external, not tied to device/serial, with no guaranteed 5-year per-upload retention and no tamper protection, so they do not meet the tamper-evident, device-resident tracing-log requirement. This is a structural (missing-feature) finding verifiable without active testing — analogous to the SVV-1 negative confirmation used at RQ-005.

Prioritisation — Current: Dokumentenprüfung

⚠️ Translate.
→ Put in cell: Documentation review (structural finding; no active test)

Environment feasibility check: The curl read runs in Zone B; the core evidence is a documentation review (no bench needed). This is the least environment‑dependent row — a good one to present as a "structural finding confirmed without active testing." ✅

Company‑doc mapping: No offensive CM applies — closest is CM‑008 (SBOM/version context) and the 4‑1 SVV‑1 design/documentation review approach; reuse the SM‑5 "structural, not active‑testable" justification you established earlier. Norm anchor: CR 2.8/2.9 + prEN 50742 §7.3.1.

Step 2 — Test cases

TC‑013‑A — Current-version-only exposure (curl · supporting evidence)

Objective: Confirm the device exposes only the current firmware version, with no device‑resident history of previous uploads.
Setup: SRIO on OT segment (192.168.0.2); IoT‑Core reachable.
Steps:
curl http://192.168.0.2/deviceinfo/swrevision
curl http://192.168.0.2/firmware/version
Search the IoT‑Core tree for any endpoint exposing a history of uploaded versions (expected: none).
Expected: Only the current version is returned; no historical/per‑upload version list exists on the device.
Pass/Fail: Gap‑confirmation (no device‑resident version history).
Evidence: curl outputs rq013a_*.txt.

TC‑013‑B — Release Notes vs. requirement (documentation review · the actual proof)

Objective: Establish, as a negative proof, that the manufacturer Release Notes do not satisfy the literal RQ‑013 properties (device‑resident, tamper‑evident, per‑upload, per‑upload timestamp, 5‑year retention).
Setup: Manufacturer Release Notes (SRIO‑16242) + RQ‑013 requirement text.
Steps:
List the five literal properties RQ‑013 requires.
Assess the Release Notes against each property (device/serial binding? tamper‑evidence? per‑upload record? per‑upload timestamp? guaranteed 5‑year retention?).
Cross‑reference prEN 50742 §7.3.1 (SW‑version storage excluded from tracing log).
Expected: Release Notes fail on device‑residence, tamper‑evidence, per‑device binding, and guaranteed retention → requirement not met.
Pass/Fail: Gap‑confirmation via structural/documentation review; no active test needed.
Evidence: a property‑by‑property comparison table (requirement vs. Release Notes) + prEN 50742 reference.

(Optional) TC‑013‑C — I&M5 cross-check (Wireshark · supplementary)

Objective: Confirm the PROFINET I&M5 annotation also reflects only the current firmware version, not a history.
Setup: Wireshark on mirror port; read I&M5 (annotation string, e.g., "host_fw_1.0.3.215").
Steps: Trigger/capture the I&M5 read; verify it carries only the current version.
Expected: Only current version present; consistent with TC‑013‑A.
Pass/Fail: Supplementary confirmation.
Evidence: rq013c.pcap.

That's RQ‑013 fully worked — kept distinct from RQ‑012 (version records vs. intervention data), with the negative‑proof documentation review as the primary evidence and the missing‑properties list made explicit. Ready for the final one, RQ‑014?
---
Let's work through RQ‑014, the final requirement, column by column with drop‑in text ("→ Put in cell:"). This is a clean confirmed non‑conformity and your row is already strong. The work: refine the CR mapping (it's a bit over‑stuffed), fix the STRIDE nuance, and translate the two German cells.

RQ‑014 — "Restrict access to the tracing log data exclusively to demonstrating conformity further to a reasoned request from a competent national authority"



Step 2 — Test cases

TC‑014‑A — Unauthenticated log access (curl · primary, the gap test)

Objective: Confirm the tracing/error log is readable without any authentication, authorization, or purpose limitation → violates the "exclusively for competent-authority request" restriction.
Setup: SRIO on OT segment (192.168.0.2); IoT‑Core reachable; no credentials supplied.
Steps:
Issue an unauthenticated GET: curl -i http://192.168.0.2/devicestatus/errorlog.
Observe whether the log content is returned and whether any authentication challenge (401/403) or purpose-limitation control is enforced.
Retry from a second, unrelated client to confirm it is not session/context restricted.
Expected (confirms gap): Full log returned with HTTP 200, no auth challenge, no purpose limitation → unrestricted access confirmed.
Pass/Fail: Gap‑confirmation (confirmed non‑conformity).
Evidence: rq014a.txt (curl response incl. headers + body).

TC‑014‑B — Absence of delete/erase & purpose control (curl · supplementary)

Objective: Confirm there is no documented/available command to delete, erase, or purpose-restrict the log, and no authorization on any log-affecting operation.
Setup: IoT‑Core reachable; device in Operate.
Steps:
Enumerate log-related endpoints/services under /devicestatus/errorlog (e.g., loglist service).
Attempt any delete/clear operation (if exposed) unauthenticated; observe behaviour.
Document that no purpose-limitation or authority-request gate exists on read or on any operation.
Expected: No access-restriction/purpose control present; no controlled delete path → reinforces the gap (and links to RQ-012's uncontrolled coldstart-clear as the only deletion mechanism).
Pass/Fail: Gap‑confirmation.
Evidence: curl outputs of enumeration + any operation attempt.

(Optional) TC‑014‑C — Cleartext exposure of log in transit (Wireshark · secondary)

Objective: Confirm the log data is transmitted in cleartext (confidentiality, CR 4.1), compounding the unrestricted-access finding.
Setup: Laptop NIC1 on mirror port; filter http || tcp.port==80; trigger TC‑014‑A from the Pi.
Steps: Capture the response; confirm no TLS and that log content is visible in cleartext.
Expected: Log content visible in cleartext; no TLS handshake.
Pass/Fail: Gap-confirmation (secondary/confidentiality).
Evidence: rq014c.pcap.

That completes RQ‑014 — and with it, all 14 requirements are now fully worked (column‑by‑column corrections + English test cases), consistent across the whole table.

Wrap-up: cross-cutting items to carry into your thesis

A few threads recurred across all 14 rows — worth stating once in your methodology so the appendix stays consistent:

Address Type 1 correction (RQ‑001) — propagate anywhere source-address checking is implied.
Primary vs. secondary objective split (identification/inventory vs. cleartext confidentiality) — RQ‑004, RQ‑006.
Two-bench scoping — Zone B network bench vs. a separate physical/hardware bench (RQ‑002 seal, RQ‑003, RQ‑008 debug, RQ‑011d). Declare this explicitly.
"Verify, don't assume" flags — RQ‑010 (fieldbus rate-limiting) and RQ‑011b (DCP reset auth) rest on general protocol knowledge → test-to-confirm, not established fact.
Sequencing dependency — the forced coldstart (RQ‑012) and power-cycle/DCP reset (RQ‑011) destroy log state; run all log-dependent tests (RQ‑003/008/009/011) first.
nmap-first / Scapy-with-justification — consistent with your manager's guidance and documented as SM-5 deviations where fieldbus framing requires Scapy/boofuzz.
CM baseline gaps to flag to the Technical Manager — the 10 CMs are Web/IT-centric; PROFIsafe/DCP framing (RQ-001/002/005/010/011) has no clean CM home, and CM-007 needs the JTAG/UART extension (RQ-003/008).

Would you like me to now consolidate all 14 reworked rows into a single clean English table (Word or Excel) — plus a companion test-case catalogue document — so you have both deliverables ready to hand over? If so, tell me which format (docx/xlsx) and whether you want the "→ Put in cell" corrections merged in as the final cell text.