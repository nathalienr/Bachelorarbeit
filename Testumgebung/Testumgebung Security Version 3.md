# SRIO Security-Testumgebung (Zone B) – Komplettanleitung

Diese Anleitung beschreibt den kompletten Aufbau der vereinfachten Testumgebung,
so wie sie mit dem Betreuer besprochen wurde: **nur Zone B**, mit einer Safety-SPS,
dem SRIO (Prüfling), einem Managed Switch, einem Raspberry Pi (Kali Linux) als
Testausführer und einem Laptop für Wireshark + Web-Steuerung.

Der Fokus liegt auf: **Wie sehen die Verbindungen aus? Wie setze ich das um? Und
worauf muss ich achten, wenn ich meinen Firmen-Laptop benutze?**

---

## Inhalt

1. [Idee in einem Satz](#1-idee-in-einem-satz)
2. [Komponentenliste](#2-komponentenliste)
3. [Das Wichtigste zuerst: der Firmen-Laptop](#3-das-wichtigste-zuerst-der-firmen-laptop)
4. [Topologie (Gesamtbild)](#4-topologie-gesamtbild)
5. [Die zwei getrennten Netze](#5-die-zwei-getrennten-netze)
6. [Verbindungen im Detail (Kabel für Kabel)](#6-verbindungen-im-detail-kabel-für-kabel)
7. [IP-Adressplan](#7-ip-adressplan)
8. [Schritt-für-Schritt-Aufbau](#8-schritt-für-schritt-aufbau)
9. [Die Web-Steuerung einrichten](#9-die-web-steuerung-einrichten)
10. [Ablauf eines Tests](#10-ablauf-eines-tests)
11. [Side-Inject vs. In-Path (wichtig!)](#11-side-inject-vs-in-path-wichtig)


---

## 1. Idee in einem Satz

> Der **Raspberry Pi** führt die Testskripte aus (Frames senden, scannen). Du
> startest sie **per Klick über eine Weboberfläche** vom Laptop aus. Der **Laptop**
> schneidet parallel mit **Wireshark** passiv mit. Alles läuft in einem **isolierten
> Netz ohne Verbindung zum Firmennetz**.

---

## 2. Komponentenliste

| # | Komponente | Rolle | Anmerkung |
|---|---|---|---|
| 1 | **Safety-SPS** (z. B. S7-1500F) | erzeugt zyklischen PROFIsafe-Verkehr | „Gegenstelle" des SRIO |
| 2 | **SRIO** (AL400S/AL401S) | **Prüfling (DUT)** | das zu testende Gerät |
| 3 | **Managed Switch** | verbindet alles + **Port-Mirroring** | muss SPAN/Mirror können! |
| 4 | **Raspberry Pi 4** | **Testausführer** (Kali Linux) | braucht **2 Netzwerkports** |
| 5 | **USB-Ethernet-Adapter** | 2. Netzwerkport für den Pi | ~10 €, wichtig! |
| 6 | **Laptop** | **Wireshark** + Browser für Steuerung | siehe Kapitel 3 zum Firmen-Laptop |
| 7 | Ethernet-Kabel | Verbindungen | 5–6 Stück |

---

## 3. Das Wichtigste zuerst: der Firmen-Laptop

**Die größte Gefahr ist nicht technisch, sondern organisatorisch.** Wenn dein
Firmen-Laptop **gleichzeitig** am Firmennetz (WLAN) und am Testnetz (Kabel) hängt,
koppelst du beide Netze ungewollt zusammen. Dann kann:

- dein Test-Traffic (Scapy, Nmap) Richtung Firmennetz „auslaufen", und
- die IT-Überwachung deine Test-Tools als **echten Angriff** werten
  (Nmap/Scapy sehen für ein Firmen-EDR/SIEM exakt wie ein Angriff aus).

Deshalb drei feste Regeln:

> ### 🔴 Regel 1 – Niemals gleichzeitig zwei Netze
> Solange das Testkabel im Laptop steckt: **WLAN und Mobilfunk AUS.**
>
> ### 🔴 Regel 2 – Keine Angriffs-Tools auf dem Firmen-Laptop
> Nmap, Scapy, boofuzz laufen **nur auf dem Raspberry Pi**, nie auf dem Firmen-Laptop.
> Der Laptop macht nur zwei harmlose Dinge: **Wireshark (passiv)** und **Browser**.
>
> ### 🔴 Regel 3 – Vorher schriftliche IT-Freigabe
> Damit du keinen Fehlalarm auslöst. Nutze dafür den separaten Freigabeantrag.

### Drei Varianten – welche passt zu dir?

| Variante | Firmen-Laptop-Nutzung | Wireshark läuft auf | IT-Aufwand |
|---|---|---|---|
| **A (am saubersten)** | **gar nicht** | dediziertem Lab-Rechner / 2. Pi | gering |
| **B (Kompromiss)** | nur als **Browser** | dem **Raspberry Pi** (tshark) | mittel |
| **C (nur mit Freigabe)** | Browser **+ Wireshark** | dem **Firmen-Laptop** | hoch (Npcap-Treiber, Adminrechte, EDR-Freigabe) |

**Empfehlung:** Wenn irgend möglich **Variante A oder B.** Bei Variante C brauchst
du fast sicher Adminrechte + IT-Genehmigung für den Wireshark-Treiber (Npcap),
und ein EDR kann den Sniffer-Treiber blockieren.

Die folgende Anleitung beschreibt **Variante B** (Firmen-Laptop nur als Browser,
Wireshark wahlweise am Laptop **falls erlaubt** oder am Pi). So bist du auf der
sicheren Seite.

---

## 4. Topologie (Gesamtbild)

```
        ISOLIERTES TESTLABOR – KEINE VERBINDUNG ZUM FIRMENNETZ
 ┌──────────────────────────────────────────────────────────────────┐
 │                                                                    │
 │   ┌─────────┐          ┌──────────────────────┐                    │
 │   │  SPS    │          │    MANAGED SWITCH     │                    │
 │   │ S7-15xxF├──[K1]────┤ Port1                 │                    │
 │   └─────────┘          │ Port2 ├──[K2]── SRIO (Prüfling)           │
 │                        │ Port3 ├──[K3]── Raspberry Pi  eth0        │
 │                        │ Port4 (MIRROR) ├──[K4]── Laptop  NIC1     │
 │                        └──────────────────────┘        (Wireshark) │
 │                                                                    │
 │        OT-SEGMENT  (192.168.0.0/24)  – hier läuft der Testverkehr  │
 │  ················································································ │
 │        MANAGEMENT  (192.168.50.0/24) – hier läuft nur die Steuerung │
 │                                                                    │
 │   Raspberry Pi  eth1 ──[K5, Direktkabel]── Laptop  NIC2 (Browser)  │
 │                                                                    │
 └──────────────────────────────────────────────────────────────────┘
```

- **[K1]–[K4]** hängen am Switch = OT-Segment (der eigentliche Testverkehr).
- **[K5]** ist ein **direktes Kabel** Pi ↔ Laptop = Management (nur Steuerung).
- Der Laptop hat **zwei Anschlüsse**: NIC1 (Mirror, Wireshark) und NIC2 (Browser).
  Falls dein Laptop nur einen Ethernet-Port hat → USB-Ethernet-Adapter für den zweiten.

---

## 5. Die zwei getrennten Netze

Das ist der Schlüssel zum Verständnis. Es gibt **zwei komplett getrennte Netze**,
die sich nie vermischen:

### Netz 1: OT-Segment (der „Testverkehr")
- **Wer hängt dran:** SPS, SRIO, Pi-`eth0`, Laptop-NIC1 (Mirror)
- **Was passiert hier:** PROFIsafe zwischen SPS und SRIO; der Pi injiziert Frames;
  der Laptop schneidet über den Mirror-Port passiv mit.
- **Adressbereich:** `192.168.0.0/24`

### Netz 2: Management (die „Fernbedienung")
- **Wer hängt dran:** Pi-`eth1`, Laptop-NIC2
- **Was passiert hier:** Du öffnest im Browser die Weboberfläche des Pi und klickst
  Test-Buttons. Sonst nichts.
- **Adressbereich:** `192.168.50.0/24`
- **Warum getrennt:** Damit deine Steuerbefehle nie im Testverkehr auftauchen –
  saubere Trennung „Steuerung ≠ Test". Das stärkt deine Beweisführung.



---

## 6. Verbindungen im Detail (Kabel für Kabel)

| Kabel | Von | Nach | Netz | Zweck |
|---|---|---|---|---|
| **K1** | SPS | Switch Port 1 | OT | PROFIsafe-Master |
| **K2** | SRIO | Switch Port 2 | OT | Prüfling |
| **K3** | Raspberry Pi `eth0` | Switch Port 3 | OT | Frame-Injection |
| **K4** | Switch **Mirror-Port** | Laptop NIC1 | OT | Wireshark (passiv, nur lesend) |
| **K5** | Raspberry Pi `eth1` (USB-Eth) | Laptop NIC2 | Mgmt | Web-Steuerung (Browser) |

**Wichtig zu K4 (Mirror-Port):** Der Switch muss so konfiguriert werden, dass er
den Verkehr **zwischen SPS-Port und SRIO-Port** auf den Mirror-Port kopiert. Nur
dann sieht Wireshark den PROFIsafe-Austausch. (Menüpunkt heißt je nach Switch
„Port Mirroring", „SPAN" oder „Monitor Port".)

**Wichtig zu K5 (Direktkabel):** Das ist ein **direktes Kabel** zwischen Pi und
Laptop, **nicht** über den Switch. So bleibt die Steuerung sauber vom Testnetz
getrennt.

---

## 7. IP-Adressplan

| Gerät | Interface | IP-Adresse | Netz |
|---|---|---|---|
| SPS | – | 192.168.0.1 | OT |
| **SRIO (Prüfling)** | – | 192.168.0.2 | OT |
| Raspberry Pi | `eth0` | 192.168.0.100 | OT |
| Laptop | NIC1 (Mirror) | *keine IP nötig* | OT (nur Empfang) |
| Raspberry Pi | `eth1` | 192.168.50.10 | Mgmt |
| Laptop | NIC2 (Browser) | 192.168.50.20 | Mgmt |

- **Subnetzmaske überall:** `255.255.255.0`
- **Kein Gateway, kein DNS, kein DHCP** – alles statisch, alles isoliert.
- Die NIC1 des Laptops (Mirror) braucht **keine IP** – sie hört nur zu.
- Die IP des SRIO wird meist per **DCP-Tool** gesetzt (das Gerät hat ab Werk keine).

---

## 8. Schritt-für-Schritt-Aufbau

### Schritt 1 – Hardware verkabeln
1. SPS → Switch Port 1 (K1)
2. SRIO → Switch Port 2 (K2)
3. Raspberry Pi `eth0` → Switch Port 3 (K3)
4. Switch Mirror-Port → Laptop NIC1 (K4)
5. Raspberry Pi `eth1` (USB-Adapter) → Laptop NIC2 (K5, Direktkabel)

### Schritt 2 – Switch konfigurieren
- Port-Mirroring einrichten: Quelle = Port1 + Port2, Ziel = Mirror-Port.
- (Optional) Alle Ports ins selbe VLAN, unbenutzte Ports deaktivieren.

### Schritt 3 – Raspberry Pi vorbereiten
```bash
sudo apt update
sudo apt install -y python3-flask python3-scapy nmap tshark
```
IPs setzen (Beispiel über /etc/network/interfaces):
```
auto eth0
iface eth0 inet static
    address 192.168.0.100
    netmask 255.255.255.0

auto eth1
iface eth1 inet static
    address 192.168.50.10
    netmask 255.255.255.0
```
Neu einlesen / Pi neu starten, dann prüfen:
```bash
ip a                    # eth0 = .0.100, eth1 = .50.10 ?
```

### Schritt 4 – SRIO-IP setzen
Mit einem DCP-Tool (z. B. `pnio_dcp` auf dem Pi) dem SRIO die 192.168.0.2 geben,
dann testen:
```bash
ping 192.168.0.2
```

### Schritt 5 – Laptop konfigurieren
- **NIC1 (Mirror):** keine IP, nur Wireshark drauf lauschen lassen.
- **NIC2 (Browser):** statische IP 192.168.50.20 / 255.255.255.0.
- **WLAN + Mobilfunk ausschalten**, solange das Testkabel steckt (Regel 1!).

---

## 9. Die Web-Steuerung einrichten

Die kleine Steuer-App (Flask) liegt im separaten Ordner `srio_testctl/`
(app.py + tests/ + README). Kurzfassung:

```bash
# App-Dateien auf den Pi kopieren (per USB-Stick oder scp)
cd ~/srio_testctl
sudo python3 app.py      # Scapy/Nmap brauchen root
```

Am **Laptop** im Browser öffnen:
```
http://192.168.50.10:5000
```

Du siehst pro Testfall einen **Button**. Ein Klick startet das zugehörige Skript
auf dem Pi, zeigt die Ausgabe im Browser und speichert sie als Evidence-Log
(`~/evidence/TC-…_Zeitstempel.log`).

**Sicherheit der App:** Es werden nur vordefinierte Skripte aus einer Whitelist
ausgeführt – keine frei eingegebenen Befehle. Damit kann über die Weboberfläche
kein beliebiger Befehl eingeschleust werden.

---

## 10. Ablauf eines Tests

1. **SPS in RUN** → zyklischer PROFIsafe-Verkehr läuft.
2. **Wireshark am Laptop starten** (NIC1/Mirror), Filter z. B. `pn_rt || pn_io`.
3. **Browser am Laptop** → `http://192.168.50.10:5000` → Testfall-Button klicken.
4. Der **Pi führt das Skript aus** (z. B. Frame-Injection über eth0).
5. **Wirkung beobachten:** Passiviert das SRIO? Fällt es in den sicheren Zustand?
   → im Wireshark-Mitschnitt + am SPS-/SRIO-Status ablesen.
6. **Evidence sichern:** PCAP (Laptop) + Log (Pi) mit gleichem Zeitstempel ablegen.

---

## 11. Side-Inject vs. In-Path (wichtig!)

Es gibt zwei Arten, wie der Pi am Netz hängt – das entscheidet, welche Tests gehen:

### Side-Inject (Standard in dieser Anleitung)
- Pi hängt als **normaler Port am Switch** (K3).
- **Kann:** Frames an das SRIO senden (Spoofing, CRC-Bitflip, DCP-Reset), scannen.
- **Kann NICHT:** den laufenden SPS↔SRIO-Zyklus unterbrechen.
- Deckt die **meisten** Testfälle ab. ✅

### In-Path (nur für den Watchdog-Test)
- Für Tests, bei denen du den Verkehr **anhalten** musst (F_WD_Time-Watchdog),
  muss der Pi **zwischen** SPS und SRIO hängen – als **2-Port-Bridge**.
- Dafür brauchst du am Pi einen **zweiten OT-Port** (weiterer USB-Eth-Adapter) und
  baust eine Bridge:
  ```bash
  sudo ip link add br0 type bridge
  sudo ip link set eth0 master br0    # Richtung SPS
  sudo ip link set eth2 master br0    # Richtung SRIO
  sudo ip link set br0 up
  # Verkehr kurz unterbrechen (> F_WD_Time):
  sudo ip link set br0 down; sleep 1; sudo ip link set br0 up
  ```
- Für diesen einen Test **steckst du kurz um**. Danach zurück auf Side-Inject.

