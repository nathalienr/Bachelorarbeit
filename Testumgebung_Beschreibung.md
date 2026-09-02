# Testumgebung – Beschreibung (final)

Physical IT/OT Interface Testbed für Safe Remote I/O (SRIO, AL400S/AL401S)

---

## 1. Übersicht

| Gerät | Rolle | IP-Adresse | Subnetzmaske | Switch-Port |
|---|---|---|---|---|
| Managed Switch | Netzwerkverteiler | 192.168.0.91 (Management) | 255.255.255.0 | – |
| SPS (F-Host) | Safety-Master, PROFIsafe-Verbindung | 192.168.0.1 | 255.255.255.0 | Port 1 |
| SRIO (DUT) | Testobjekt | 192.168.0.2 | 255.255.255.0 | Port 2 |
| Kali-Linux-Rechner | Angriffs-/Analyse-Host | 192.168.0.80 | 255.255.255.0 | Port 3 |
| Firmenlaptop | Engineering (TIA Portal) | 192.168.0.7 | 255.255.255.0 | Port 4 |

Alle Geräte befinden sich im selben Subnetz `192.168.0.0/24`, feste IP-Adressen (kein DHCP).

---

## 2. Topologie

```
                         ┌─────────────────────────┐
                         │   Managed Switch          │
                         │   192.168.0.91 (Mgmt)      │
                         │                            │
                         │  Port1  Port2  Port3  Port4│
                         └───┬──────┬──────┬──────┬───┘
                             │      │      │      │
                    ┌────────┘      │      │      └────────┐
                    │               │      │               │
              ┌─────┴─────┐   ┌─────┴────┐ │         ┌─────┴─────┐
              │    SPS     │   │  SRIO    │ │         │Firmenlaptop│
              │(F-Host)    │   │  (DUT)   │ │         │(TIA Portal)│
              │192.168.0.1 │   │192.168.0.2│ │         │192.168.0.7 │
              └────────────┘   │M12(D)↔RJ45│ │         └────────────┘
                                └──────────┘ │
                                       ┌──────┴──────┐
                                       │  Kali-Linux  │
                                       │192.168.0.80  │
                                       │(Wireshark u.a.)│
                                       └──────────────┘

SRIO zusätzlich (nicht über Switch):
   - Power In (M12, L-codiert) ← 24V-DC-Netzteil
   - DI-Port (M12, A-codiert)  ← Taster/Sensor
   - DO-Port (M12, A-codiert)  → Last (Lampe/Relais)
```

Alle vier Geräte hängen als eigenständige Access-Ports am selben Switch (klassische Stern-Topologie, kein Inline-Tap, keine dedizierte Mirror-Verkabelung im Grundzustand).

---

## 3. Switch – Konfiguration

### 3.1 Management-Zugriff
- Web-UI/CLI über `192.168.0.91` erreichbar (z. B. via Browser vom Firmenlaptop, sofern gleiches Subnetz).
- Management-Zugriff ist nicht mit den Testfunktionen der einzelnen Ports zu verwechseln – die Portbelegung (Abschnitt 3.2) bestimmt, welches Gerät welchen Verkehr sieht.

### 3.2 Portbelegung

| Port | Gerät | Modus |
|---|---|---|
| 1 | SPS | Access, Standard-VLAN |
| 2 | SRIO | Access, Standard-VLAN |
| 3 | Kali-Linux-Rechner | Access, Standard-VLAN |
| 4 | Firmenlaptop | Access, Standard-VLAN |

Alle Ports befinden sich in derselben Broadcast-Domain. Damit sieht der Kali-Rechner an Port 3 automatisch jeden **Broadcast-/Multicast-Verkehr** (z. B. PROFINET-DCP), nicht aber gezielten Unicast-Verkehr zwischen SPS (Port 1) und SRIO (Port 2) – der wird vom Switch ausschließlich an den jeweiligen Zielport ausgeliefert, nicht dupliziert.

### 3.3 Optional: Port-Mirroring für passives Mitschneiden
Falls der zyklische PROFIsafe-Datenverkehr zwischen SPS und SRIO vollständig (nicht nur Broadcasts) am Kali-Rechner sichtbar sein soll:
1. Switch-Menü *Port Mirroring* öffnen.
2. Quell-Ports: Port 1 (SPS) und Port 2 (SRIO), Richtung *both/ingress+egress*.
3. Ziel-Port: Port 3 (Kali-Linux-Rechner).
4. Aktivieren, mit `tcpdump -i eth0` auf dem Kali-Rechner verifizieren.

**Einschränkung:** Solange Mirroring aktiv ist, empfängt Kali an Port 3 zusätzlich zum eigenen (aktiven) Verkehr auch den gespiegelten SPS↔SRIO-Verkehr. Für reine Enumeration/aktive Angriffe (Nmap, HTTP-Requests gegen IoT-Core) ist Mirroring nicht nötig und kann deaktiviert bleiben.

### 3.4 Storm-Control
Vor Flood-/Fuzzing-Tests (z. B. hping3, boofuzz) bewusst festlegen und dokumentieren, ob Storm-Control (Broadcast-/Multicast-/Unicast-Sturmschutz) am Switch aktiv ist, da dies das Testergebnis beeinflusst.

---

## 4. SPS (F-Host) – Konfiguration

### 4.1 IP-Adresse
- `192.168.0.1 / 255.255.255.0`, kein Gateway nötig (lokales Testnetz).

### 4.2 Hardware-Konfiguration in TIA Portal
1. Projekt anlegen → passende CPU einfügen.
2. SRIO aus Hardware-Katalog auf die PROFINET-Linie ziehen (GSD-Datei zuvor importieren, siehe Abschnitt 5.2).
3. Passendes DAP wählen (AL400S oder AL401S).
4. IP-Adresse der CPU auf `192.168.0.1` setzen.

### 4.3 PROFIsafe-Parameter
1. Modul-Eigenschaftsdialog SRIO → Reiter *F-Parameter*.
2. `F_Dest_Add` auf denselben Wert setzen, der am Drehschalter der SRIO physisch eingestellt wird (1–899).
3. `F_WD_Time` setzen (Default 150 ms, Minimum 50 ms).
4. iParameter der DI-/DO-Ports konfigurieren.
5. iPar-CRC über ifm-CRC-Tool erzeugen (siehe Abschnitt 5.3) und in `F_iPar_CRC` eintragen.
6. Projekt übersetzen und auf CPU laden, CPU in RUN.

---

## 5. Firmenlaptop – Konfiguration

### 5.1 IP-Adresse
- `192.168.0.7 / 255.255.255.0`, kein Gateway nötig.
- Windows-Netzwerkprofil auf „Privat" setzen, sonst blockiert die Firewall ggf. DCP/S7comm.

### 5.2 TIA Portal
- TIA Portal vorhanden (Version ≥ V17 empfohlen, TCI ≥ V1.1-MU1).
- GSD-Datei der SRIO importieren: *Extras → Gerätebeschreibungsdateien (GSD) verwalten* → Pfad angeben → Installieren.

### 5.3 ifm-CRC-Tool
- Wird ausschließlich aus TIA Portal heraus gestartet (Rechtsklick auf SRIO-Modul → *Device Tool starten*).
- Bei erstem Start Zertifikatsdialog bestätigen/installieren.

### 5.4 I&M-Daten lesen
`I&M0` (REVISION_COUNTER), `I&M4` (iParCRC/F_ParCRC-Signatur), `I&M5` (Firmware-Annotation) sind **nur** über TIA Portal auslesbar, nicht über IoT-Core:
1. Online-Verbindung zur CPU herstellen.
2. SRIO-Modul → *Online & Diagnose → Kennungsdaten (I&M)*.

---

## 6. SRIO (DUT) – Konfiguration

### 6.1 IP-Adresse
- `192.168.0.2 / 255.255.255.0`, wird beim ersten Verbindungsaufbau per DCP von TIA Portal zugewiesen (unter *Erreichbare Teilnehmer* suchen).

### 6.2 Drehschalter (F-Adresse)
1. Gerät stromlos.
2. Drehschalter unter der Siegel-Hülse einstellen (1–899 = F_Dest_Add, muss mit TIA-Portal-Wert übereinstimmen; 000 = Auslieferungszustand; 999 = Firmware-Update-Modus).
3. Adresse wird nur beim Boot/Init gelesen.

### 6.3 Verkabelung
| Anschluss | Steckertyp | Verbindung |
|---|---|---|
| Power In | M12, L-codiert, männlich | 24V-DC-Netzteil (Pin1 L+US, Pin3 L−US, Pin4 L+UA, Pin2 L−UA, Pin5 FE) |
| Fieldbus-Port 1 | M12, D-codiert, weiblich | Patchkabel → Switch Port 2 |
| Fieldbus-Port 2 | M12, D-codiert, weiblich | unbenutzt |
| DI-Port | M12, A-codiert, 5-pol., weiblich | Taster/Sensor (Pin1 L+/TSOut1, Pin4 F-DI1, Pin2 F-DI2, Pin5 L+/TSOut2, Pin3 L−US) |
| DO-Port | M12, A-codiert, 5-pol., weiblich | Last/Lampe (Pin4 F-DO1, Pin2 F-DO2, Pin3 L−UA, Pin5 FE) |

### 6.4 Erstinbetriebnahme
1. Netzteil einschalten, RDY-LED grün prüfen.
2. Verbindungsaufbau über TIA Portal (siehe 6.1).
3. Nach erfolgreicher Parametrierung: P-LED statisch grün = sichere Kommunikation aktiv.

---

## 7. Kali-Linux-Rechner – Konfiguration

### 7.1 IP-Adresse
```
ip addr add 192.168.0.80/24 dev eth0
ip link set eth0 up
```
Für dauerhafte Konfiguration in `/etc/network/interfaces` oder NetworkManager-Profil eintragen.

### 7.2 Vorhandene/benötigte Tools
Wireshark ist vorhanden. Ergänzend für die Testfälle:
```
apt install -y nmap tshark scapy hping3 ettercap-text-only bettercap zaproxy
```
PROFINET/DCP-fähige Erweiterung (für Frame-Crafting-Tests, z. B. TC-RQ001-03, TC-RQ011-02, TC-RQ010-02/03):
```
python3 -c "from scapy.all import load_contrib; load_contrib('pnio'); load_contrib('pnio_rtc')"
pip install pnio-dcp
```
Vor Testbeginn jedes Tool einzeln auf Funktion prüfen.

### 7.3 Reichweite in dieser Topologie
Kali sitzt an einem regulären Access-Port (Port 3), nicht inline zwischen SPS und SRIO. Damit gilt:
- **Möglich:** Portscans/HTTP-Requests gegen SRIO (`192.168.0.2`), Senden gezielter Unicast-Frames an SRIOs MAC-Adresse (zusätzlich zum echten Verkehr, nicht anstelle davon), Empfang von Broadcast-/Multicast-Verkehr (z. B. DCP), Mitschneiden bei aktiviertem Port-Mirroring (Abschnitt 3.3).
- **Nicht möglich ohne zusätzliche Hardware:** Unterdrücken oder Ersetzen des echten zyklischen PROFINET/PROFIsafe-Frames zwischen SPS und SRIO (echtes Inline-MITM). ARP-Spoofing wirkt nur auf IP-Verkehr; PROFINET RT/PROFIsafe wird als eigener EtherType (0x8892) ohne IP-Adressierung übertragen und ist darüber nicht umlenkbar.
- Betroffen: Testfälle, die explizit die Unterdrückung des legitimen Producers voraussetzen (z. B. TC-RQ001-04), sind mit dieser Topologie **nicht ohne Weiteres durchführbar**. Für diesen Einzelfall wäre ein zusätzlicher zweiter Netzwerkadapter am Kali-Rechner nötig, um ihn physisch zwischen Switch-Port 2 und SRIO als transparente Bridge einzusetzen – das ist in der aktuellen, finalen Topologie nicht vorgesehen und müsste separat ergänzt werden, falls dieser Testfall durchgeführt werden soll.

---

## 8. Sicherheitshinweise

1. Switch darf keinen Uplink zum Firmennetz haben, sofern aktive/aggressive Tools (bettercap, ettercap, hping3, boofuzz) zum Einsatz kommen.
2. Destruktive Tests (Siegel entfernen, Firmware-Korruption) nur an einem separaten Ersatzgerät durchführen, nicht am primären DUT (`192.168.0.2`).
3. Vor Firmware-Tests validierten Original-Firmware-Container sichern (Recovery-Möglichkeit).

---

## 9. Checkliste

- [ ] Alle Geräte mit korrekter IP erreichbar (`ping 192.168.0.1/.2/.7/.80/.91`)
- [ ] GSD-Datei in TIA Portal importiert
- [ ] SRIO-Drehschalter-Adresse = F_Dest_Add in TIA Portal identisch
- [ ] Projekt auf SPS geladen, CPU in RUN
- [ ] P-LED an SRIO statisch grün
- [ ] I&M-Lesepfad bekannt (nur TIA Portal, nicht IoT-Core)
- [ ] Kali-Tools installiert und einzeln getestet
- [ ] Port-Mirroring-Bedarf je Testfall geprüft (Abschnitt 3.3)
- [ ] Storm-Control-Einstellung für Flood-Tests dokumentiert
- [ ] Grenzen der Topologie bekannt (kein Inline-MITM ohne zusätzliche Hardware, siehe Abschnitt 7.3)
