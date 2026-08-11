# TARA Asset Structure Comparison — Industrial Gateway (IEC 62443-1-1 Perspective)

Scope: compare three candidate asset-definition variants for a TARA of an Industrial Gateway (OT/IT routing, firewall, VPN/remote access, protocol conversion, PROFINET/PROFIsafe fieldbus, dual safety CPUs), using IEC 62443-1-1 terminology and concepts (asset, zone, conduit), and derive a recommended final asset list. Asset-structure analysis only; no new STRIDE/threat content is derived here.

- **Variant A** — 10 coarse, domain-level assets.
- **Variant B** — 75 fine-grained assets, grouped in system/functional order.
- **Variant C** — the same 75 assets as Variant B, sorted alphabetically.

## 0. Verification of variant content

Before scoring, the variants were reconciled item-by-item:

| Check | Result |
|---|---|
| Variant A item count | 10 |
| Variant B item count | 75 |
| Variant C item count | 75 |
| Variant C \ Variant B (items in C not in B) | 0 |
| Variant B \ Variant C (items in B not in C) | 0 |

**Finding:** Variant C is not an independent asset structure — it is Variant B's identical 75-item set re-sorted alphabetically instead of grouped by system/function. This means B and C cannot differ in coverage, granularity, or completeness; they can only differ in **ordering-dependent qualities**: traceability and maintainability. This distinction shapes several of the scores below.

## 1. Asset Identification per Variant

IEC 62443-1-1 treats "asset" broadly — a physical or logical object with value to the organization, including hardware, software, data, and functions worth protecting. It also defines **zones** (grouped assets sharing security requirements) and **conduits** (communication paths connecting zones/assets) as *relationships between assets*, not assets in their own right. This distinction is used throughout.

### 1.1 Variant A — 10 coarse assets

| Asset | IEC 62443-1-1 category | Note |
|---|---|---|
| Process Data | Data | Cyclic/acyclic fieldbus values collapsed into one bucket |
| Safety Configuration | Data, Safety-related function | Merges PROFIsafe parameters, F-Address, watchdog time |
| Configuration Data | Data | Merges network, device, and engineering configuration |
| Firmware | Firmware/Software | Merges bootloaders, OS, update services, images |
| Diagnostic and Service Data | Data | Merges error log, diagnostics, service interfaces |
| Device Identity Data | Data | Merges tag, I&M data, serial/version info |
| Persistent Storage | Hardware | Merges all EEPROM/flash regardless of CPU/role |
| Communication Interfaces | Communication | Merges all network, fieldbus, internal, and debug interfaces |
| Physical Configuration Elements | Physical/HMI | Rotary switch and related physical settings |
| GSDML | Data/Documentation | Engineering description file |

Ten labels stand in for roughly 25+ physically and functionally distinct technical elements once cross-checked against B/C — each label is a *domain*, not a discrete, independently protectable asset.

### 1.2 Variant B — 75 fine-grained assets (functional grouping)

Categorized against IEC 62443-1-1 asset types:

| IEC 62443-1-1 category | Count | Representative assets |
|---|---:|---|
| Hardware | 25 | Host CPU3, SCPU1, SCPU2, NetX90, Hardware Watchdog, Digital Isolators, eFUSE, Groupswitch, Power Supply Module, Oscillators, Cross-Temperature Sensors, PROFINET Ports, 3x EEPROM, 3x Flash, Power Connectors, FE Path, Rotary Switch/Trigger, F-DI/F-DO channels, LED Indicators |
| Firmware/Software | 7 | Bootloader CPU3, Bootloader SCPU1/2, Safe uCOS-II OS, Firmware Downgrade Capability, Firmware Install Service, IoT-Core Firmware Container/BLOB Upload, FW_UPDATE Operating State |
| Communication interfaces/services | 16 | IoT-Core Web Interface, SysCom, IPC, Debug/Programming Interfaces, eRPC, Shared Memory Data Interface, DCP Protocol Service (x3 variants), FIT/Test Interfaces (x2), /devicecontrol (x2), /firmware/*, /fit/setfit, Fieldbus Parameter Write |
| Data/Configuration | 12 | Device Tag, Own Safe Address Storage, Safety Application Parameters, Uptime Counter, I&M Data, GSD/GSDML File, PROFIsafe F-Parameters, Cyclic/Acyclic Process Data, Error Log, iPar CRC Value, System Time, Diagnostic Readouts |
| Security mechanism/state | 3 | Production Fuse Flag, Safe State Logic, CRC-Tool (External, Certified) |
| Boundary/trust-zone construct | 9 | External Network↔COM/NetX90, External IP Client↔IoT-Core, COM↔SCPU1, SCPU1↔SCPU2, Galvanic Isolation, US↔UA, Physical Debug Interface, Field Wiring↔DI/DO, Production-Mode Boundary |
| Documentation/supply-chain | 3 | Release Notes, Safety Manual/User Manual, GSD/Engineering Data Distribution Channel |
| **Total** | **75** | |

Variant B is organized narratively (CPUs → hardware building blocks → interfaces → storage → data → firmware/update chain → boundaries → services → physical/HMI → documentation), which mirrors how a system architect would present the device.

### 1.3 Variant C — same 75 assets, alphabetical order

Identical content and category distribution to §1.2. The only structural difference is sort key: alphabetical string order instead of functional/architectural grouping. This makes C better suited to lookup-by-name (audits, cross-referencing a bill of materials or interface control document) and worse suited to explaining *why* assets are related (a reviewer cannot tell from position alone that "SCPU1 <-> SCPU2 Boundary" sits between the two safety CPUs).

## 2. Advantages / Disadvantages per Variant

| Variant | Advantages | Disadvantages |
|---|---|---|
| **A (coarse)** | Minimal upfront effort; easy for non-technical stakeholders to skim; fast to produce a first-pass TARA | Too coarse for IEC 62443-1-1 conformant modeling; hides ~20 discrete technical attack surfaces (bootloaders, debug ports, DCP, eRPC, watchdog...) under generic labels; cannot support zone/conduit reasoning; weak traceability from finding to fix (an auditor cannot tell which physical component "Persistent Storage" refers to) |
| **B (functional grouping)** | High technical fidelity; explicit enumeration of hardware, firmware, comm, and data assets; grouping narrative supports architecture walkthroughs and workshop-style TARA sessions; strong attack-surface coverage | 9 of 75 items are relationship constructs (boundaries) modeled as standalone assets — a IEC 62443-1-1 terminology mismatch; some near-duplicate protocol variants (3x DCP, 2x FIT/Test) fragment a single attack surface; flat list has no persisted category grouping, so maintainers must know the narrative convention to place new items correctly |
| **C (alphabetical)** | Same technical fidelity as B; fast name-based lookup; new entries sort themselves; easier to diff/reconcile against alphabetically-ordered external references (BOM, ICD) | Same boundary/duplication issues as B; loses all architectural/system-relationship context — a reviewer sees "eFUSE" isolated from "Power Supply Module" and "Groupswitch" despite being electrically related; harder to use in a walkthrough-style TARA workshop |

## 3. Impact on TARA Effort, Completeness, Traceability, Maintainability, Risk-Assessment Quality

| Dimension | Variant A | Variant B | Variant C |
|---|---|---|---|
| **TARA effort** | Lowest (10 assets → fast STRIDE pass), but the effort saved is largely deferred, not eliminated — someone must still decompose each domain later to reach actionable findings | Highest raw effort (75 assets × up to 6 STRIDE categories), but the effort is "real" work directly usable in remediation planning | Same effort as B (identical content) |
| **Completeness** | Low — real components (bootloader, watchdog, debug interfaces, EEPROM-per-CPU) are invisible, so their specific weaknesses cannot be individually risk-rated | High — nearly all technical elements visible; still missing an explicit firmware-image/version asset and any credential/key-material asset (see §6 gap note) | Same as B (identical content) |
| **Traceability** | Weak — a finding against "Configuration Data" cannot be traced to a specific register, file, or interface without further work | Moderate-strong — functional grouping helps a reviewer trace an asset to its place in the architecture, but exact alphabetical lookup is slower | Strong for name-based lookup/audits; weaker for architectural traceability (relationship context lost) |
| **Maintainability** | Easiest to keep updated (short list) but any update still requires re-deriving the underlying detail that was abstracted away | Moderate — no enforced structure for where new assets are added; risk of ad hoc ordering drift as the product evolves | Moderate — alphabetical insertion is mechanical/self-ordering, but unrelated new hardware won't appear near related items, making review of "what changed in this subsystem" harder |
| **Risk-assessment quality** | Low resolution — risk ratings apply to a whole domain, obscuring that (e.g.) one specific EEPROM may carry materially higher risk than another in the same "Persistent Storage" bucket | High resolution — per-component/per-interface risk ratings are directly actionable, at the cost of the boundary items producing risk statements about relationships rather than protectable things | Same resolution as B |

## 4. Structured Scoring

Each variant is scored 1 (poor) – 5 (excellent) against the eight required criteria. A fourth column, **Hybrid (Recommended)**, previews the structure proposed in §5/§6 for comparison.

| # | Criterion | A | B | C | Hybrid (Recommended) |
|---|---|---:|---:|---:|---:|
| 8 | Alignment with TARA methodology | 2 | 4 | 4 | 5 |
| 9 | Alignment with IEC 62443-1-1 concepts/terminology | 2 | 3 | 3 | 5 |
| 10 | Coverage of relevant attack surfaces | 2 | 5 | 5 | 5 |
| 11 | Asset granularity | 1 | 4 | 4 | 4 |
| 12 | Completeness of security-relevant assets | 2 | 4 | 4 | 4 |
| 13 | Suitability for zone and conduit thinking | 2 | 3 | 3 | 5 |
| 14 | Traceability for auditors/security reviewers | 3 | 3 | 4 | 5 |
| 15 | Maintainability | 4 | 3 | 3 | 4 |
| **Total (/40)** | | **18** | **29** | **30** | **37** |

Rationale highlights:
- **Criterion 8/10/11/12** track content, so B and C tie — they share the same 75 items.
- **Criterion 9/13** are capped for both B and C at 3/5: both encode 9 boundary items as top-level assets, which is a direct terminology mismatch with IEC 62443-1-1 (zones/conduits are relationships, not assets), regardless of ordering.
- **Criterion 14/15** are the only ones ordering can move: C's alphabetical order slightly improves auditor traceability (name-based lookup, easier duplicate-spotting) but does not improve maintainability over B, since neither structure groups assets by subsystem/category — the property that actually helps maintainability.
- **A** scores acceptably only on effort/maintainability-of-the-list-itself, and poorly everywhere that matters for a defensible IEC 62443-1-1 TARA.

## 5. Recommendation

Neither raw Variant B nor raw Variant C should be adopted unchanged. Both share two structural weaknesses that a simple re-sort cannot fix:

1. **Boundary items modeled as assets.** IEC 62443-1-1 defines conduits/zones as relationships between assets. Retaining 9 "X <-> Y Boundary" entries as standalone assets means ~12% of the list is not actually an asset — it should be metadata (a conduit annotation) attached to the real assets on each side of the relationship.
2. **No persisted category/domain grouping.** Both variants are flat lists; B relies on narrative ordering (helpful but not enforced/labeled) and C relies on alphabetization (mechanical, not architectural).

**Recommendation:** adopt a **hybrid structure** — retain Variant B/C's fine technical granularity (the single biggest driver of TARA quality, coverage, and risk-assessment resolution) but:
- Re-express the 9 boundary items as **conduit attributes** on the connected assets rather than standalone assets (§6, §7).
- Group the remaining assets under explicit **IEC 62443-1-1 category headers** (Hardware; Firmware/Software; Communication Interfaces & Protocol Services; Data/Configuration; Security-Relevant Mechanisms & States; Physical/HMI Elements; Documentation/Supply-Chain), which combines B's architectural narrative with C's auditability (a category+alphabetical-within-category order gets both benefits).
- Consolidate a small number of genuinely redundant protocol-variant entries (e.g. the three DCP service assets) where they represent the same attack surface reached through the same channel, without losing any distinct STRIDE-relevant behavior.
- Add one evidenced-but-missing asset (the firmware image/version itself, at rest — distinct from the services that upload/install it) to close a completeness gap visible only by comparing Variant A's coarse "Firmware" domain against B/C's process-only decomposition.

## 6. Final Optimized Asset List (derived independently)

Grouped by IEC 62443-1-1 category. `[merged]` = consolidates 2+ Variant B/C items with equivalent attack surface. `[new]` = added to close a completeness gap; grounded in evidence from the variant content, not invented. Boundary items removed as standalone assets are cross-referenced to their new home in §7.

### 6.1 Hardware (24)

Host CPU3 (COM, VHIP3 core); Safety CPU1 (SCPU1); Safety CPU2 (SCPU2); NetX90 Fieldbus Chip; Hardware Watchdog; Digital Isolators (2x); eFUSE; Groupswitch (Switch CH1/CH2/M); Power Supply Module; Oscillators (CPU1/CPU2/CPU3); Cross-Temperature Sensors (CPU1↔CPU2); PROFINET Fieldbus Ports (x2, M12 D-coded); EEPROM - COM (CPU3); EEPROM - SCPU1; EEPROM - SCPU2; Internal Flash (CPU3, 2MB); External Flash (32Mbit); Shared Update Flash; Power Connectors (XD1/XD2) & Daisy-Chain Path; Functional Earth (FE) Path; Rotary Switch / FW-Update Trigger (Position 999) `[merged]`; F-Digital Input Channels (DI 1-12); F-Digital Output Channels (DO 1-4); LED Indicators (RDY, BF, SF, P, FS, LNK, ACT, US, UA, Port LEDs).

*Note:* EEPROM-SCPU1 and EEPROM-SCPU2 are kept as **separate** assets rather than merged, even though they hold the same class of data — because the device's 1oo2 diverse-redundant safety architecture depends on these two channels being independently compromisable/verifiable (a cross-channel discrepancy attack is only visible if they remain distinct assets). This is a granularity decision, not an oversight.

### 6.2 Firmware / Software / OS (6)

Bootloader - CPU3 (VHIP3); Bootloader - SCPU1/SCPU2; Safe uCOS-II OS (SCPU1/SCPU2); **Firmware Image (Active/Staged, per CPU)** `[new]` — the installed/staged firmware binary and its version/CRC, as a data-at-rest asset distinct from the services that move it; Firmware Downgrade Capability; FW_UPDATE Operating State.

### 6.3 Communication Interfaces & Protocol Services (13)

IoT-Core Web Interface (HTTP); SysCom Interface (SPI, COM↔SCPU1); IPC Interface (SCPU1↔SCPU2, SPI2/I2C); Debug/Programming Interfaces (per CPU); eRPC Service Interface; Shared Memory Data Interface (Fieldbus↔IO-Delegator); **DCP Protocol Service (Set/Identify/Reset + Factory Reset)** `[merged: DCP Protocol Service, PROFINET DCP Set/Identify/Reset, PROFINET DCP Factory Reset]`; **FIT/Test Service Interface (/fit/setfit + Debug Trigger)** `[merged: FIT Service Interface, Test Interface]`; **IoT-Core Device Control Service (/devicecontrol, /devicecontrol/signal)** `[merged]`; **Firmware Transfer Service (/firmware/container upload + /firmware/install)** `[merged: IoT-Core Firmware Container/BLOB Upload, Firmware Install Service, /firmware/* Service Group]`; Fieldbus Parameter Write (Acyclic); GSD/Engineering Data Distribution Channel.

### 6.4 Data & Configuration Assets (12)

Cyclic/Acyclic Fieldbus Process Data; Device Tag / Application Tag; Own Safe Address Storage; Safety Application Parameters (iParameters); PROFIsafe F-Parameters; GSD/GSDML File; I&M Data (I&M0-I&M5); Error Log (Circular Buffer); Uptime Counter; System Time / Systick Counter; iPar CRC Value; Voltage/Current/Temperature Diagnostic Readouts.

### 6.5 Security-Relevant Mechanisms & States (3)

Safe State Logic (Init/Error/FATAL_ERROR states); Production Fuse Flag / Production-Mode State `[merged: Production Fuse Flag + Production-Mode Boundary]`; CRC-Tool (External, Certified).

### 6.6 Documentation & Supply-Chain Artifacts (2)

Release Notes (per FW version); Safety Manual / User Manual.

**Final asset count: 60** (24 + 6 + 13 + 12 + 3 + 2), down from 75 raw items, with zero loss of distinct attack surfaces (verified: every removed item either became a conduit attribute in §7 or was merged with an equivalent-surface sibling and is cross-referenced above).

**Evidenced completeness gap (not remediated by adding a fictitious asset):** none of the three variants — and no evidence in the underlying specification — identifies cryptographic key material, certificates, or user credentials as assets. Given the specification explicitly notes the absence of HTTPS/TLS and of signed firmware, this likely reflects the real device design rather than a modeling omission. It is flagged here as a **finding for the risk assessment**, not added as an asset, since inventing a credential asset the device does not appear to possess would misrepresent the system.

## 7. IEC 62443-1-1 Alignment: Zones, Conduits, and Robustness of the Final List

### 7.1 Zone model for the gateway

Applying IEC 62443-1-1's zone/conduit model to the device's own internal architecture (not just its position between OT and IT):

- **Safety zone** — Safety CPU1 (SCPU1), Safety CPU2 (SCPU2), their EEPROMs, Safe uCOS-II OS, Safe State Logic, PROFIsafe F-Parameters, Own Safe Address Storage, iPar CRC Value, F-DI/F-DO channels, Hardware Watchdog. Highest integrity/availability requirement; safety-impact relevant.
- **Non-safe host zone** — Host CPU3 (COM/VHIP3), its EEPROM/flash, IoT-Core Web Interface, eRPC, bootloaders, firmware transfer/install services, error log, device tag.
- **External OT zone** (conduit-connected) — the PLC/engineering network reached via PROFINET Fieldbus Ports, NetX90, DCP Protocol Service, GSD/GSDML distribution.
- **External IT zone** (conduit-connected) — remote/maintenance clients reached via the IoT-Core Web Interface (HTTP), used for diagnostics and firmware management.
- **Physical/production zone** — rotary switch, LEDs, debug interfaces, power/FE paths, production-mode state; requires physical access.

### 7.2 Boundary items re-expressed as conduits (mapping table)

Each Variant B/C "Boundary" pseudo-asset is retained as a documented **conduit**, attached to the real assets it connects, instead of standing alone:

| Former "boundary" asset | Conduit connects | Attached to (real asset) |
|---|---|---|
| External Network ↔ COM/NetX90 Boundary | External OT zone ↔ Non-safe host zone | PROFINET Fieldbus Ports, NetX90 Fieldbus Chip |
| External IP Client ↔ IoT-Core Boundary | External IT zone ↔ Non-safe host zone | IoT-Core Web Interface (HTTP) |
| COM (non-safe) ↔ SCPU1 (safe) Boundary | Non-safe host zone ↔ Safety zone | SysCom Interface (SPI, COM↔SCPU1) |
| SCPU1 ↔ SCPU2 Boundary | Intra-safety-zone (1oo2 channel separation) | IPC Interface (SCPU1↔SCPU2, SPI2/I2C) |
| Galvanic Isolation Boundary (Logic ↔ Output Power) | Safety zone ↔ Physical/production zone | Digital Isolators (2x), Groupswitch |
| US ↔ UA Power Domain Boundary | Physical/production zone (internal) | Power Supply Module |
| Physical Debug Interface Boundary | Physical/production zone ↔ all CPU zones | Debug/Programming Interfaces (per CPU) |
| Field Wiring ↔ DI/DO Boundary | Physical/production zone ↔ Safety zone | F-Digital Input/Output Channels |
| Production-Mode Boundary (production_fuse) | Physical/production zone (state gate) | Production Fuse Flag / Production-Mode State |

No conduit is lost; each is now a documented relationship between two named, protectable assets, matching IEC 62443-1-1's definition rather than inflating the asset count.

### 7.3 Why this supports a robust TARA

- **Category completeness** — the final list explicitly spans hardware, firmware/software, communication/services, data/configuration, security-relevant mechanisms, and documentation, matching IEC 62443-1-1's broadened asset concept (not just physical devices).
- **Per-zone risk aggregation** — because assets are tagged to a zone (§7.1), risk ratings can be rolled up per zone (e.g. "Safety zone" aggregate risk) for management reporting, something impossible with Variant A's flat domains and only partially possible with B/C's unstructured flat list.
- **Conduit-level threat modeling** — the mapping in §7.2 lets reviewers reason about cross-zone attack paths (e.g. External IT zone → IoT-Core Web Interface → firmware transfer service → non-safe host zone → SysCom conduit → safety zone) directly from the asset list, instead of inferring it from prose.
- **Auditability** — every asset name is unique, technically grounded, and traceable to a specific component or interface; category grouping plus the merge/gap notes in §6 give an auditor a clear rationale trail for every consolidation.
- **Maintainable size** — 60 categorized assets is large enough to preserve resolution but small enough, and structured enough (7 categories vs. a flat 75), to keep placement of new assets unambiguous as the product evolves.
