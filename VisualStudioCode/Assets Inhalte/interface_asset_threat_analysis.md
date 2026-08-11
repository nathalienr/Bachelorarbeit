# Interface- und Asset-Übersicht Threat Analysis

## Interface-Tabelle

| Interface ID | Interface | Type / Protocol | External access | Assets via this interface | In scope | Threat Scenario | Impact S / F / O / P | Existing Controls | Gap |
|---|---|---|---|---|---|---|---|---|---|
| IF-01 | NetX90 — PROFINET Fieldbus | PROFINET, inkl. DCP | Direct, network | Kommunikationsverfügbarkeit, Gerätekonfig, Diagnose, Prozessdatenpfad; interner NetX90-Switch, Downstream-Geräte | Yes | Unautorisierter Teilnehmer, Telegramm-Manipulation, DoS/Flooding, DCP-Missbrauch, Device-Rename, Reset, Deaktivierung interner Switch → Ausfall aller Downstream-Geräte | H / M / H / L | Externe Netzgrenze; SysCom-Isolation schützt Safe Core | AuthN/AuthZ, Segmentierung, DCP-Filter, Service-Härtung noch zu definieren |
| IF-02 | NetX90 — IoT API | HTTP, Klartext | Direct, network | Diagnose-/Servicefunktionen, Konfigdaten, Firmware-Update-Trigger, Test-Interface | Yes | Klartext-MITM, Credential-Diebstahl, Command Injection, Session Hijacking, unautorisiertes Firmware-Update-Anstoßen | M / M / H / M | Nicht ersichtlich | Kritisch: keine Vertraulichkeit/Integrität; kein AuthN/AuthZ sichtbar. Abklären, ob HTTP überhaupt erlaubt bleibt |
| IF-03 | NetX90 — IoT API | HTTPS / TLS | Direct, network | Wie IF-02 plus Zertifikate/Schlüssel; Firmware-Update-File-Integrität; Test-Interface, Production-Flag gesichert | Yes | Schwache TLS-Konfig, Zertifikatsmissbrauch, API-Missbrauch, manipuliertes Firmware-Update-File, CAC-Wissen ausnutzen, DoS | M / M / H / M | TLS vorhanden; Test-Interface durch Production-Flag gesichert; Bootloader prüft Firmware-Integrität und verhindert Installation korrupter Images | Kein Secure Boot; Firmware-File-Integrität extern nur über Website-Vergleich prüfbar; mTLS/Cert-Pinning, RBAC, Rate-Limiting noch offen |
| IF-04 | Rotary Switch | Physischer Eingang, GPIO | Physical direct | Betriebsmodus, Funktionswahl | Yes | Unautorisierte lokale Umschaltung | M / L / M / L | Physischer Zugriff erforderlich; Zugangskontrolle = Kundenverantwortung | Technisch kaum weiter absicherbar → Kundenverantwortung in Dokumentation explizit festhalten |
| IF-05 | JTAG / interne Debug-Interfaces | JTAG / SWD / UART | Physical direct, intern | Firmware, Speicherinhalte, Keys/Secrets, Laufzeitkontrolle | Yes | Auslesen/Ändern von Firmware und Secrets, Bypass Bootloader/Integrity-Check | H / H / H / H | Gerät ist umspritzt, Overmolding → physischer Zugriff stark erschwert | Debug-Lock / Production-Fusing Status unklar; Overmolding als primäre physische Barriere dokumentieren |
| IF-06 | Digital IOs, F-DI / F-DO | Elektrische digitale Ein-/Ausgänge | Physical / field side | Safety-Zustände, Aktorsteuerung, Prozesssicherheit | Yes | Signal-Spoofing, erzwungene Ausgänge, Leitungsmissbrauch | H / L / H / L | Safety-Architektur, SCPU1/SCPU2, Watchdog; PROFINET SafetyStack durch SysCom-Isolation von IT-Seite abgekapselt | Leitungsdiagnose, Plausibilisierung, Fail-safe-Default konkretisieren |
| IF-07 | SysCom — Host [CPU3] ↔ SCPU1 | Interne Kommunikation, Protokoll TBD | Intern, indirekt über COM-Domain | Safe-Core-Isolation, Rückwirkungsfreiheit COM→SCPU, TÜV-Nachweis, Safety-Kommandos/Status | Yes | Kompromittierter/malicious Host sendet ungültige Kommandos an Safe Core; IT-seitige Störung mit Rückwirkung auf Safety-Funktion | H / M / M / L | Domain-Grenze COM/SCPU im Diagramm; SCPU schiebt Daten zyklisch unidirektional Richtung Host; Kommandoset auf definierte Befehle reduziert | Protokollspezifikation, erlaubte Kommandos, formal dokumentieren; Rückwirkungsfreiheitsnachweis für TÜV noch ausstehend |

## Assets außerhalb Interface-Tabelle, Notizen

| Asset | Begründung | Entscheidung |
|---|---|---|
| Bootloader | Hardware-gekoppelt, nicht updatebar → prüft Firmware-Integrität, verhindert korrupte Installation | Control für IF-03, kein eigenes Interface → als Existing Control dokumentieren |
| Firmware-Update-File | Könnte mit bekannter CAC-Berechnung gefälscht werden; kein Secure Boot | Risk: in IF-03 erfasst; Maßnahme: Integritätsprüfung über offizielle Website; langfristig: Secure Boot |
| EEPROM, Safe Side | Durch SysCom-Isolation abgekapselt; nur definierte Bereiche beschreibbar, Rest read-only | De-priorisiert; kurzer Vermerk in IF-07 ausreichend |
| Power Supply / Daisy Chain | Availability-Relevanz vorhanden; physischer Schutz kaum möglich | Out of scope — Verweis auf Installationsvorschrift / Kundenverantwortung |
| NetX90, Hardware | Interner Switch kann Downstream-Geräte betreffen | In IF-01 mit erfasst |

## Offene Punkte / Follow-ups

- Klären, ob HTTP für IF-02 weiterhin zulässig ist oder vollständig deaktiviert werden muss.
- AuthN/AuthZ-Konzept für Netzwerk- und API-Zugriffe definieren.
- Segmentierung und DCP-Filterung für PROFINET konkretisieren.
- TLS-Härtung, mTLS oder Cert-Pinning sowie RBAC und Rate-Limiting bewerten.
- Status von Debug-Lock und Production-Fusing verifizieren.
- Protokollspezifikation für SysCom dokumentieren, inklusive erlaubter Kommandos.
- Rückwirkungsfreiheitsnachweis für TÜV vorbereiten.
- Kundenverantwortung für physische Zugriffskontrolle, Power Supply und Daisy Chain explizit in der Dokumentation festhalten.
