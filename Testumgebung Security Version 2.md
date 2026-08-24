# Architektur-Übersicht

```
┌──────────────────────────────────────────────────────────────────────────────┐
│           SINGLE-SWITCH-MULTI-VLAN-ARCHITEKTUR                               │
│           Ein Switch · Ein SRIO · Kein Umstecken · Kein zweites DUT          │
│           Switch NIEMALS mit Firmennetz verbunden                            │
│                                                                              │
│                        ┌─────────────────────────────┐                       │
│                        │   Managed Switch              │                     │
│                        │   (dediziert, nur für Labor)   │                    │
│                        │   • kein Inter-VLAN-Routing    │                    │
│                        │   • keine SVI konfiguriert     │                    │
│                        │   • DTP deaktiviert            │                    │
│                        │   • Native VLAN ≠ VLAN 1       │                    │
│                        │   • alle Ports = Access-Mode   │                    │
│                        └───┬──────┬──────┬──────┬──────┘                     │
│                            │      │      │      │                            │
│         SRIO-Port          │      │      │      │                            │
│         (FEST, wird NIE    │      │      │      │                            │
│          umgesteckt) ──────┘      │      │      │                            │
│              │                    │      │      │                            │
│    ┌─────────▼─────────┐          │      │      │                            │
│    │   SRIO (DUT)       │         │      │      │                            │
│    │   AL400S/AL401S    │         │      │      │                            │
│    │   Rotary/DIL frei  │         │      │      │                            │ 
│    │   zugänglich        │        │      │      │                            │
│    └─────────────────────┘        │      │      │                            │
│                                   │      │      │                            │
│         VLAN 10 "Isolation"       │      │      │                            │
│         (nur SRIO-Port + Test-PC  │      │      │                            │
│          Mitglied dieser VLAN)    │      │      │                            │
│                                   │      │      │                            │
│    ┌────────────────────┐         │      │      │                            │
│    │   Test-PC            │◄──────┘      │      │                            │
│    │   Kali, Wireshark,   │  VLAN 10       │      │                          │
│    │   Scapy, curl, JTAG  │                │      │                          │
│    └────────────────────┘                  │      │                          │
│                                            │      │                          │
│         VLAN 20 "Field-Zone"               │      │                          │
│         (F-Host, Engineering-PC,           │      │                          │
│          Access-Port-Angreifer,            │      │                          │
│          SRIO-Port bei Bedarf              │      │                          │
│          zugewiesen)                       │      │                          │
│                                            │      │                          │
│    ┌────────────────┐  ┌────────────────┐  │      │                          │
│    │  F-Host / SPS   │  │ Engineering-PC │◄─┘      │                         │
│    │  S7-1500F/1200F │  │ TIA Portal V18 │  VLAN 20│                         │
│    └────────────────┘  └────────────────┘          │                         │
│                                                    │                         │
│    ┌────────────────────┐                          │                         │
│    │ Access-Port-        │◄────────────────────────┘                         │
│    │ Angreifer-PC        │  VLAN 20                                          │
│    │ Scapy, boofuzz,     │  (normaler Access-Port,                           │
│    │ pnio_dcp, Community-│   NICHT Mirror — aktive                           │
│    │ Stack als Rogue-    │   Injektion möglich)                              │
│    │ Master-Basis         │                                                  │
│    └────────────────────┘                                                    │
│                                                                              │
│         Mirror-Port (SPAN, VLAN 20)                                          │
│    ┌────────────────────┐                                                    │
│    │  Sniffer-PC          │◄── nur Kopie des VLAN-20-Traffics,               │
│    │  Wireshark, passiv   │    keine Injektion möglich                       │
│    └────────────────────┘                                                    │
│                                                                              │
│         VLAN 30 "Attack-Only" (optional, für RQ-011)                         │
│         (SRIO-Port + Angreifer-PC, OHNE F-Host —                             │
│          simuliert Netzwerkangreifer ohne physischen                         │
│          Schalterzugriff und ohne konkurrierende AR)                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```
### Ablauf eines Ebenenwechsels (statt Umstecken)

| Schritt | Aktion | Dauer | Auswirkung auf SRIO |
|---|---|---|---|
| 1 | Administrator/Skript weist SRIO-Switchport per CLI/Web-GUI/SNMP eine neue VLAN-ID zu (z. B. `switchport access vlan 20`) | wenige Sekunden | Kein Kabelkontakt, keine Stromunterbrechung |
| 2 | Physischer Ethernet-Link bleibt bestehen (reine Control-Plane-Änderung, keine PHY-Neuverhandlung) — **am konkreten Switch-Modell einmalig verifizieren und dokumentieren** | — | LNK-LED am SRIO bleibt durchgehend an |
| 3 | Eine ggf. aktive PROFINET/PROFIsafe-Verbindung zum bisherigen VLAN bricht ab (andere Broadcast-Domäne) | sofort | SRIO fällt in State **Parametrization** zurück (EC3-Fallback, dokumentiertes Standardverhalten), **kein Cold-Start** |
| 4 | Bei Rückkehr in ein VLAN mit F-Host: SRIO baut PROFINET-Verbindung automatisch neu auf, PROFIsafe integriert sich nach Bestätigung neu | Sekunden bis wenige Zehnersekunden | Error-Log bleibt erhalten (nur Coldstart löscht ihn) |


### 9.5 Switch-Härtungs-Checkliste (Pflicht vor Testbeginn)

| Maßnahme | Befehl/Einstellung (Beispiel Cisco-ähnliche CLI) | Zweck |
|---|---|---|
| DTP deaktivieren auf allen Ports | `switchport nonegotiate` | Verhindert Switch-Spoofing-Trunk-Aufbau durch Angreifer-PC |
| Alle Ports explizit als Access-Port | `switchport mode access` | Kein Port kann sich selbst zum Trunk verhandeln |
| Kein Gerät auf VLAN 1 | eigene VLAN-IDs (z. B. 10/20/30) für alle Access-Ports | Reduziert Angriffsfläche für Default-VLAN-Annahmen |
| Native VLAN auf trunk-freien Switches irrelevant, bei Stack-Trunks: Native VLAN ändern | `switchport trunk native vlan 999` (nur falls Trunks existieren) | Verhindert Double-Tagging-Angriffe |
| Kein Inter-VLAN-Routing / keine SVI konfigurieren | keine `interface vlan X` mit IP-Adresse anlegen | Erzwingt echte L2-Trennung ohne Router dazwischen |
| Switch ausschließlich für das Labor, nie ans Firmennetz | physische Trennung des Uplinks | Begrenzt Blast-Radius eines Restfehlers auf das Labor |
| Isolation aktiv verifizieren | Portscan/Ping aus VLAN 20 gegen SRIO-IP in VLAN 10, muss fehlschlagen | Belegt die Trennung empirisch statt sie nur zu behaupten (Nachweis für Dokumentationsschicht) |

