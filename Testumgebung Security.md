# SRIO Security-Testumgebung (Zone B) – geprüfte Komplettbeschreibung

---

## Inhalt

1. [Was die Umgebung macht (in 3 Sätzen)](#1-was-die-umgebung-macht)
2. [Die 5 Komponenten und ihre Rolle](#2-die-5-komponenten-und-ihre-rolle)
3. [Topologie (Gesamtbild)](#3-topologie-gesamtbild)
4. [Die zwei getrennten Netze](#4-die-zwei-getrennten-netze)
5. [Verbindungen (Kabel für Kabel)](#5-verbindungen-kabel-für-kabel)
6. [IP-Adressplan](#6-ip-adressplan)
7. [Wie ein Test technisch abläuft](#7-wie-ein-test-technisch-abläuft)
8. [Wo läuft welches Werkzeug?](#8-wo-läuft-welches-werkzeug)
9. [Der Firmen-Laptop (organisatorisch wichtig)](#9-der-firmen-laptop)
10. [Side-Inject vs. In-Path](#10-side-inject-vs-in-path)


---

## 1. Was die Umgebung macht

> Die **SPS** und das **SRIO** tauschen über den **Switch** laufend PROFIsafe-Daten
> aus. Der **Raspberry Pi (Kali)** hängt am selben Switch und führt die Testskripte
> aus (Frames senden, scannen). Du **startest diese Skripte per Klick auf einer
> Website**, die auf dem Pi läuft und die du vom **Laptop-Browser** öffnest – während
> der Laptop parallel mit **Wireshark** passiv mitschneidet.

---

## 2. Die 5 Komponenten und ihre Rolle

| Komponente | Rolle | Was sie tut |
|---|---|---|
| **SPS** (S7-15xxF) | PROFIsafe-Master | erzeugt den zyklischen Safety-Verkehr zum SRIO |
| **SRIO** (AL400S/AL401S) | **Prüfling (DUT)** | das zu testende Gerät |
| **Managed Switch** | Verbindung + **Port-Mirroring** | verbindet alle OT-Geräte; kopiert Verkehr auf den Mirror-Port |
| **Raspberry Pi (Kali)** | **Testausführer** | führt Scapy/Nmap/tshark aus; hostet die Steuer-Website |
| **Laptop** | **Fernbedienung + Beobachter** | Browser (klickt Test-Buttons) + Wireshark (passiv) |

Zwei kleine, aber nötige Zusätze:
- Der **Pi braucht 2 Netzwerkports** → ein **USB-Ethernet-Adapter** (~10 €).
- Der **Laptop braucht 2 Anschlüsse** (Mirror + Browser) → ggf. auch ein USB-Adapter.

---

## 3. Topologie (Gesamtbild)

```
        ISOLIERTES TESTLABOR – KEINE VERBINDUNG ZUM FIRMENNETZ
 ┌──────────────────────────────────────────────────────────────────┐
 │                                                                    │
 │   ┌─────────┐          ┌──────────────────────────┐                │
 │   │  SPS    │          │      MANAGED SWITCH       │               │
 │   │ S7-15xxF├──[K1]────┤ Port1                     │               │
 │   └─────────┘          │ Port2 ├──[K2]── SRIO (Prüfling)           │
 │                        │ Port3 ├──[K3]── Raspberry Pi  eth0        │
 │                        │ Port4 (MIRROR)├──[K4]── Laptop NIC1       │
 │                        └──────────────────────────┘     (Wireshark)│
 │                                                                    │
 │      OT-SEGMENT (192.168.0.0/24) – hier läuft der Testverkehr      │
 │  ································································· │
 │      MANAGEMENT (192.168.50.0/24) – hier läuft nur die Steuerung   │
 │                                                                    │
 │   Raspberry Pi eth1 ──[K5, Direktkabel]── Laptop NIC2 (Browser)    │
 │                                                                    │
 └──────────────────────────────────────────────────────────────────┘

  Mirror-Quelle = Port2 (SRIO) + Port3 (Pi)  →  siehe Korrektur 1 (Abschnitt 12)
```

---

## 4. Die zwei getrennten Netze

Der Schlüssel zum Verständnis: es gibt **zwei Netze, die sich nie berühren**.

### Netz 1 – OT-Segment (der „Testverkehr")
- **Dran:** SPS, SRIO, Pi-`eth0`, Laptop-NIC1 (Mirror)
- **Hier passiert:** PROFIsafe SPS↔SRIO; der Pi injiziert Frames; Wireshark
  schneidet über den Mirror-Port passiv mit.
- **Adressbereich:** `192.168.0.0/24`

### Netz 2 – Management (die „Fernbedienung")
- **Dran:** Pi-`eth1`, Laptop-NIC2
- **Hier passiert:** Du öffnest im Browser die Website des Pi und klickst Buttons.
- **Adressbereich:** `192.168.50.0/24`
- **Warum getrennt:** damit deine Steuerbefehle **nie** im Testverkehr auftauchen.
  Saubere Rollentrennung „Steuerung ≠ Test" – das stärkt die Beweisführung.

> **Merksatz:** OT-Segment = *worüber getestet wird*. Management = *womit du den
> Test auslöst*.

---

## 5. Verbindungen (Kabel für Kabel)

| Kabel | Von | Nach | Netz | Zweck |
|---|---|---|---|---|
| **K1** | SPS | Switch Port 1 | OT | PROFIsafe-Master |
| **K2** | SRIO | Switch Port 2 | OT | Prüfling |
| **K3** | Pi `eth0` | Switch Port 3 | OT | Frame-Injection |
| **K4** | Switch **Mirror-Port** | Laptop NIC1 | OT | Wireshark (passiv) |
| **K5** | Pi `eth1` (USB-Eth) | Laptop NIC2 | Mgmt | Web-Steuerung (Browser) |

**K4 – Mirror:** Der Switch muss so konfiguriert werden, dass er den
Verkehr **des SRIO-Ports (Port2) UND des Pi-Ports (Port3)** auf den Mirror-Port
kopiert. Nur dann sieht Wireshark **sowohl** den normalen SPS↔SRIO-Verkehr **als
auch** deine injizierten Frames vom Pi. (Menü heißt je nach Switch „Port Mirroring",
„SPAN" oder „Monitor Port".)

**K5 – Direktkabel:** ein **direktes Kabel** Pi↔Laptop, **nicht** über den Switch.
So bleibt die Steuerung sauber vom Testnetz getrennt.

---

## 6. IP-Adressplan

| Gerät | Interface | IP-Adresse | Netz |
|---|---|---|---|
| SPS | – | 192.168.0.1 | OT |
| **SRIO (Prüfling)** | – | 192.168.0.2 | OT |
| Raspberry Pi | `eth0` | 192.168.0.100 | OT |
| Laptop | NIC1 (Mirror) | *keine IP* | OT (nur Empfang) |
| Raspberry Pi | `eth1` | 192.168.50.10 | Mgmt |
| Laptop | NIC2 (Browser) | 192.168.50.20 | Mgmt |

- Subnetzmaske überall: `255.255.255.0`; **kein Gateway, DNS, DHCP** – alles statisch.
- NIC1 (Mirror) braucht **keine IP** – sie hört nur zu.
- SRIO-IP wird per **DCP-Tool** gesetzt (Gerät hat ab Werk keine IP).

> **Wichtig zu verstehen ** Der **zyklische PROFIsafe-Verkehr läuft
> auf Layer 2** (Ethernet, EtherType 0x8892) und braucht **gar keine IP**. Die
> IP-Adressen oben werden **nur** für die IP-basierten Tests gebraucht: DCP,
> HTTP/IoT-Core, Nmap-Scan. Beide Welten laufen parallel über dieselben Kabel.

---

## 7. Wie ein Test technisch abläuft

```
  LAPTOP                                   RASPBERRY PI
  ┌──────────┐                             ┌────────────────────────┐
  │ Browser  │ ── Button-Klick (HTTP) ──►  │ Flask-Website           │
  │ 192.168. │      über K5 (Mgmt)         │ startet Testskript      │
  │ 50.10... │                             │        │                │
  │          │                             │        ▼                │
  │          │                             │ Skript sendet Frames    │
  │          │                             │ über eth0 → Switch → SRIO│
  │ Wireshark│ ◄── Mirror-Port (K4) ──     │                         │
  │ sieht    │   sieht SRIO- + Pi-Verkehr  │ Ergebnis + Log          │
  │ alles    │                             │ (~/evidence/)           │
  └──────────┘                             └────────────────────────┘
```

Schritt für Schritt:
1. **SPS in RUN** → zyklischer PROFIsafe-Verkehr läuft.
2. **Wireshark am Laptop** starten (NIC1/Mirror), Filter `pn_rt || pnio`.
3. **Browser am Laptop** → `http://192.168.50.10:5000` → Test-Button klicken.
4. Der **Pi führt das Skript aus** – die Injection läuft über `eth0` in den Switch
   zum SRIO. **Nicht** über den Laptop.
5. **Wirkung beobachten:** Passiviert das SRIO? Geht es in den sicheren Zustand?
   → im Wireshark-Mitschnitt + am SPS-/SRIO-Status ablesen.
6. **Evidence sichern:** PCAP (Laptop) + Log (Pi), gleicher Zeitstempel.

---

## 8. Wo läuft welches Werkzeug?

| Werkzeug | Läuft auf | Typ |
|---|---|---|
| **Scapy** (Injection) | 🍓 Raspberry Pi | aktiv |
| **Nmap** (Portscan) | 🍓 Raspberry Pi | aktiv |
| **boofuzz** (Fuzzing) | 🍓 Raspberry Pi | aktiv |
| **pnio_dcp** (IP setzen) | 🍓 Raspberry Pi | aktiv |
| **Flask-Website** | 🍓 Raspberry Pi | – |
| **Wireshark** (GUI) | 💻 Laptop | passiv |
| **Browser** (Steuerung) | 💻 Laptop | passiv |

> **Merkregel: Aktiv = Pi. Passiv = Laptop.**
> Auf dem Firmen-Laptop läuft **kein** aktives Test-Tool – nur Browser + Wireshark.

---

## 9. Der Firmen-Laptop

**Wichtigste Regel – keine Netzkopplung:** Der Firmen-Laptop darf **nie gleichzeitig**
am Firmennetz (WLAN) und am Testnetz (Kabel) hängen.

- 🔴 **WLAN + Mobilfunk AUS**, solange ein Testkabel steckt.
- 🔴 **Keine Angriffs-Tools** (Nmap/Scapy) auf dem Firmen-Laptop – nur auf dem Pi.
- 🔴 **Vorher schriftliche IT-Freigabe** einholen (Fehlalarm vermeiden).

Falls die IT **Wireshark auf dem Firmen-Laptop nicht erlaubt** (Npcap-Treiber
braucht Adminrechte, EDR kann ihn blockieren): dann **tshark auf dem Pi** laufen
lassen (Pi zusätzlich am Mirror), und der Laptop ist **nur noch Browser**.

---

## 10. Side-Inject vs. In-Path

### Side-Inject (Standard hier)
- Pi hängt als **normaler Switch-Port** (K3).
- **Kann:** Frames an das SRIO senden (Spoofing, CRC-Bitflip, DCP-Reset), scannen.
- **Kann NICHT:** den laufenden SPS↔SRIO-Zyklus unterbrechen.
- Deckt die **meisten** Testfälle ab. ✅

### In-Path (nur für den Watchdog-Test, F_WD_Time)
- Pi **zwischen** SPS und SRIO als **2-Port-Bridge** (braucht 3. Port am Pi):
  ```bash
  sudo ip link add br0 type bridge
  sudo ip link set eth0 master br0    # Richtung SPS
  sudo ip link set eth2 master br0    # Richtung SRIO
  sudo ip link set br0 up
  # Verkehr kurz unterbrechen (> F_WD_Time):
  sudo ip link set br0 down; sleep 1; sudo ip link set br0 up
  ```
- Für diesen einen Test **kurz umstecken**, danach zurück auf Side-Inject.

---
