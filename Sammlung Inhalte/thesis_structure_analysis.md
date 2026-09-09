# Thesis Structure Analysis

**Thesis:** *Functional Testing of Security in Industrial Gateways under the New Machinery Regulation*
**Date of analysis:** 2026-09-08
**Scope of this document:** structural/methodological review + evidence classification. No prose was rewritten; only LaTeX comment blocks were inserted into the chapter files.

---

## A. Executive assessment

The thesis is **conceptually strong and methodologically mature, but empirically partial**. The regulatory derivation chain (Regulation (EU) 2023/1230 → prEN 50742 → IEC 62443-4-2), the methodology (`vorgehen.tex`), and the results chapter (`umsetzung.tex`) are already written in coherent academic English and are internally consistent. `grundlagen.tex` is the most finished chapter.

The correct academic framing is a **Design Science Research artifact: a prototype security-testing methodology with partial practical validation**. This is already stated honestly in `vorgehen.tex` (`subsec:reliability_validity`) and `umsetzung.tex` (`sec:objective_validation`). The empirical work was executed **only under network position NV1 (direct IP access)**. All PROFIsafe/PROFINET injection and man-in-the-middle tests (NV2 passive tap, NV3 inline bridge) were **designed but not executed**, because the lab switch was not configured for port mirroring and no inline bridge was inserted.

Maturity by chapter: `grundlagen` ~90%, `vorgehen` ~80% (needs de-duplication of German scratch blocks), `umsetzung` ~70% (needs missing evidence + table bodies), `anhang` ~75% (one dangling reference, untranslated fragment), `zusammenfassung` ~10% (German scratchpad).

**There is no main `.tex` file, `.bib`, or `.cls` in this folder** — it is a content-collection directory. The thesis cannot be compiled from here (see §14).

---

## B. Current document map

| File | Purpose | Maturity | Major issues |
|---|---|---|---|
| `Moodle Anmeldung.txt` | Official topic/abstract | Fixed | Reference for goal alignment. |
| `grundlagen.tex` | Fundamentals | High (~90%) | Missing small foundations consumed later: V&V, SVV taxonomy, repeatability/reproducibility, evidence concept, testing-limits, PROFIsafe black-channel. Marked with inline `%TODO` + new note. |
| `vorgehen.tex` | Methodology (planned) | Medium-high (~80%) | Two German scratch blocks duplicating SVV taxonomy; trailing German outline (3.2/3.3); STRIDE-at-requirement-level `%TODO`. |
| `umsetzung.tex` | Implementation & results | Medium (~70%) | Several referenced tables have omitted bodies; missing Siege/boofuzz/ZAP evidence; legacy `\iffalse` planning block; SSLscan evidence points to a broken file. |
| `zusammenfassung.tex` | Summary & outlook | Low (~10%) | German notes only; no compiled prose. |
| `anhang.tex` | RQ matrices + SDLC | Medium-high (~75%) | Dangling `\ref{sec:security_requirements}`; untranslated German prEN 50742 fragment; open CR-mapping `%TODO`. AI register = do not touch. |
| `WORKFLOW.md` | Per-requirement test catalog (2-level) | Working doc | Source of truth for test-case design; NV2/NV3 tests are skeletons. |
| `Security_Testing_Framework_Kali_EN.md` | Company framework CM-001..CM-010 | Working doc | The `.docx` referenced in the task is present here as `.md`; treat as the same document. |
| `Notizen.md` | Execution notes | Working doc | Primary statement of what was actually run per CM. |
| `Test_Cases_Srio/` | Stored evidence artifacts | — | See §F/§G evidence map. |

**Capitalization note:** the task references `workflow.md`, `WORKFLOW.docx`, and `Security_Testing_Framework_Kali_EN.docx`. The workspace contains `WORKFLOW.md` and `Security_Testing_Framework_Kali_EN.md`. No `.docx` duplicates exist; these are the same documents in Markdown. No content conflict detected between them.

---

## C. Scientific argument (reconstructed chain)

| Link | Status | Location |
|---|---|---|
| **Problem**: security functions of IT/OT gateways not systematically verified | Coherent | `Moodle Anmeldung.txt`, intro (referenced) |
| **Regulatory motivation**: (EU) 2023/1230 makes cybersecurity part of conformity | Coherent | `grundlagen` `subsec:eu_machinery_regulation` |
| **Research gap**: no systematic verification approach | Coherent | `vorgehen` `sec:research_design` |
| **Research question / objective**: validated testing methodology for security functions at the physical IT/OT interface | Coherent | `Moodle Anmeldung.txt`, `vorgehen` DSRM |
| **Requirements**: 14 RQ derived from Annex III 1.1.9/1.2.1 | Coherent | `anhang` `app:sec:mvo_requirements` |
| **Methodology**: SVV taxonomy + requirement-driven test cases + filtered company tools + NV1-3 variants | Coherent | `vorgehen` |
| **Practical investigation**: NV1 tests on SRIO | **Partial** | `umsetzung` `sec:executed_tests` |
| **Evidence**: stored artifacts in `Test_Cases_Srio/` | **Partial / gaps** | §F |
| **Validation**: against thesis objective | **Bounded to NV1** | `umsetzung` `sec:objective_validation` |
| **Conclusion / outlook** | **Weak (not written)** | `zusammenfassung` (scratchpad) |

**Weak/missing links:** (1) conclusion chapter not written; (2) several requirement verdicts remain "not yet assessed" for lack of stored evidence; (3) the intro chapter (`chap:introduction`) is referenced everywhere but is not in this folder — confirm it exists in the real main project.

---

## D. Foundations gap analysis (only genuinely needed)

| Missing foundation | Why needed later | Suggested home |
|---|---|---|
| Verification vs. Validation | `vorgehen`/`umsetzung` "verify against requirements" vs. "validate against goal" | `grundlagen` `sec:security_testing_approaches` |
| IEC 62443-4-1 SVV taxonomy (SVV-1..4) | Every test carries an SVV label; currently defined only in German scratch text | `grundlagen` (define once), referenced by `vorgehen` |
| Repeatability vs. reproducibility | Justifies two-level data sheet + TER/ETS metrics | `grundlagen` `subsec:testing_taxonomy` |
| Evidence / evidence-status & auditability | Entire results chapter rests on evidence-status classification | `grundlagen` (new short block) |
| Epistemic limit of testing (presence ≠ absence of flaws) | Justifies the "prototype/partial validation" framing | `grundlagen` `sec:security_testing_approaches` |
| PROFINET/PROFIsafe black-channel principle | Grounds RQ-001/RQ-002 and all NV2/NV3 rationale | `grundlagen` `subsec:architectural_role_gateways` |

All are already flagged with inline `%TODO` markers in `grundlagen.tex`; a consolidated note was added at the chapter top.

---

## E. Methodology analysis

**Implied methodology:** Design Science Research (Peffers DSRM), explicitly adopted in `vorgehen` `sec:research_design`. The artifact is a testing methodology; the SRIO is the single demonstration case.

**How it should be described academically:** *methodology development + single-case demonstration/proof-of-concept with partial empirical validation.* It is **not** a controlled experiment, **not** a full case study of an organization, and **not** a completed validation. The strongest empirical component (the intervention-log time-attribution / cold-start-deletion sequence) is a **controlled, repeatable observation** and is the closest the work comes to experimental evidence.

Recommended precise phrasing: *"a prototype, standards-based functional security-testing methodology, demonstrated and partially validated on one safety-related industrial gateway under the NV1 network position."*

---

## F. Test classification

`CM` = company framework instruction; `TC` = thesis test case (WORKFLOW.md). Evidence checked against `Test_Cases_Srio/`.

| Test | Source | CM / security objective | Category (SVV) | Network pos. | Prerequisite | Expected evidence | **Actual evidence status** | Level | Recommended location |
|---|---|---|---|---|---|---|---|---|---|
| TC-RQ001-02 Attack-surface enum | WORKFLOW / Notizen | CM-001+CM-007 / domain separation | SVV-3 | NV1 | HTTP+IP reachable | nmap .nmap/.xml, Nikto html | **EXECUTED_WITH_EVIDENCE** (`RQ001_02_srio.*`, `RQ002_02_udp.*`, `RQ001_02_srio.html.htm`) | 1 | `umsetzung` results |
| TC-RQ003-01 Evidence baseline | WORKFLOW | CM-—/ accountability | SVV-1 | NV1 | IoT-Core read | errorlog json | **EXECUTED_WITH_EVIDENCE** (`RQ003_01_errorlog_srio.json`, `RQ003_02_...before...json`) | 1 | `umsetzung` results |
| TC-RQ003-04 / TC-RQ012-02 Time-attribution + cold-start deletion | WORKFLOW / Befehle Tests.txt | accountability/retention | SVV-3 | NV1 | IoT-Core read, physical cable/power | systick+log 00–03 | **EXECUTED_WITH_EVIDENCE** (8 files, clean sequence) | 1 | `umsetzung` (strongest result) |
| TC-RQ004-01 Identification inventory | WORKFLOW | integrity/identification | SVV-1 | NV1 | IoT-Core read | inventory dump | **EXECUTED_WITH_EVIDENCE** (`cm_rq004-01_inventory.txt`) | 1 | `umsetzung` |
| TC-RQ006-01 Installed-SW inventory | WORKFLOW | integrity | SVV-1 | NV1 | IoT-Core read | inventory dump | **EXECUTED_WITH_EVIDENCE** (`cm_rq006-01_installed.txt`) | 1 | `umsetzung` |
| TC-RQ006-03 / CM-005 TLS/cleartext | WORKFLOW / Notizen | CM-005 / confidentiality | SVV-4b | NV1 | port 80 | sslscan txt | **EXECUTED_WITH_EVIDENCE** (`cm_rq006-03_sslscan.txt` = valid; all TLS disabled) | 1 | `umsetzung` |
| CM-005/TC-RQ004-03 SSLscan (2nd run) | Befehle Tests.txt | confidentiality | SVV-4b | NV1 | port 80 | sslscan txt | **EXECUTED_BUT_EVIDENCE_INCOMPLETE** (`cm_rq004-03_sslscan.txt` = ERROR, `$SRIO` unset) | 1 | discard/annotate as void |
| TC-RQ007-01 Identification availability | WORKFLOW | availability | SVV-1 | NV1 | IoT-Core read | swrev 200 | **EXECUTED_WITH_EVIDENCE** (`cm_rq007-01_swrev.txt`) | 1 | `umsetzung` |
| TC-RQ007-03 Connection-hold self-DoS | Befehle Tests.txt | availability | SVV-2 | NV1 | HTTP slots | baseline/blocked/after logs | **PREPARED_NOT_EXECUTED** (script only; no output files; `umsetzung` TODO confirms) | 2 | `umsetzung` "not yet assessable" / future |
| CM-009 Siege load | Notizen | CM-009 / availability+logging | SVV-5a | NV1 | HTTP endpoint | siege log | **EXECUTED_BUT_EVIDENCE_INCOMPLETE** (Notizen says run at 50 & 3 conn; no log stored) | 1 | `umsetzung` (add evidence) |
| CM-010 / TC-RQ010-03 boofuzz | Notizen / `cm010_fuzz.py` | CM-010 / robustness | SVV-5b | NV1 | HTTP port | session log + crash | **EXECUTED_BUT_EVIDENCE_INCOMPLETE** (err 0x1000 reported in Notizen; no `boofuzz-results/` stored) | 1 | `umsetzung` (RQ-010 inconclusive) |
| CM-004 OWASP ZAP | Notizen | CM-004 / authorization | SVV-4a | NV1 | web app | ZAP html | **EXECUTED_BUT_EVIDENCE_INCOMPLETE** ("Report gespeichert"; not in folder) | 1 | `umsetzung` (locate report) |
| CM-002 Segmentation | Notizen | CM-002 | SVV-4b | NV1/2 | 2nd zone | nmap cross-zone | **NOT_APPLICABLE** (flat segment) | 1 | `umsetzung` applicability |
| CM-003 Hydra | Notizen | CM-003 / auth | SVV-4a | NV1 | login endpoint | hydra log | **NOT_APPLICABLE** (no auth endpoint) | 1 | `umsetzung` applicability |
| CM-006 Lynis | Notizen | CM-006 / hardening | SVV-4a | local | OS shell | lynis report | **NOT_APPLICABLE** (no OS shell) | 1 | `umsetzung` applicability |
| CM-008 OpenVAS/GVM | Notizen | CM-008 / CVEs | SVV-4a/b | NV1 | vuln feed | GVM report | **PREPARED_NOT_EXECUTED / blocked** (feed unavailable offline) | 1 | `umsetzung` blocked |
| TC-RQ001-01/05 Baseline safety exchange, watchdog | WORKFLOW | RQ-001 / integrity+availability | SVV-1/2 | NV1(TIA) | TIA + PLC | TIA watch/diagnostics | **THEORETICALLY_DESCRIBED** (Notizen: "mit TIA aber nur I&M auslesen"; no stored TIA export) | 2 | `umsetzung`/future |
| TC-RQ001-03/04, TC-RQ002-02/03 PROFIsafe inject/MITM | WORKFLOW | RQ-001/002 / tampering | SVV-4 | **NV2/NV3** | mirror port / inline bridge | pcap + TIA | **THEORETICALLY_DESCRIBED / PREPARED_NOT_EXECUTED** (skeleton scripts; positions never realized) | 2 | `vorgehen` design + future work |
| TC-RQ002-04 Parameter-CRC forgeability | WORKFLOW | RQ-002 | SVV-3 | doc review | GSD | analytical note | **THEORETICALLY_DESCRIBED** (analytical, no artifact) | 2 | `anhang`/future |
| TC-RQ002-05 Physical tamper | WORKFLOW | RQ-002 / EDR 3.11 | SVV-4 | physical | seal/rotary access | photos + TIA | **PREPARED_NOT_EXECUTED** (no photos stored) | 2 | future work |

---

## G. Performed vs. unperformed work

- **Performed with evidence (7 activities):** attack-surface enumeration (nmap TCP+UDP+Nikto); identification inventory (RQ004-01); installed-software inventory (RQ006-01); software-revision availability (RQ007-01); TLS/cleartext (valid sslscan RQ006-03); intervention-log baseline (RQ003-01); intervention-log time-attribution + cold-start deletion sequence (RQ003-04/RQ012-02).
- **Partially performed (evidence incomplete, 4):** CM-009 Siege, CM-010 boofuzz, CM-004 ZAP, second SSLscan run (broken file).
- **Prepared, not executed (2):** TC-RQ007-03 connection-hold; CM-008 OpenVAS (blocked by missing feed).
- **Theoretically described only:** all NV2/NV3 PROFIsafe injection/MITM tests, TIA baseline safety-exchange tests, parameter-CRC forgeability, physical tamper.
- **Not applicable (device/topology):** CM-002, CM-003, CM-005-as-TLS-test, CM-006.
- **Unclear:** whether a stored ZAP report and Siege log exist outside `Test_Cases_Srio/`; whether the introduction chapter exists in the real main project.

---

## H. Proposed structure of `vorgehen.tex`

The current structure is sound; **keep it** and only consolidate the German duplicates. Target hierarchy:

1. `sec:research_design` — DSRM, initial situation, constraints, scope/delimitation. *Purpose: what and why, before building.*
2. `sec:traceability` — regulatory derivation + asset mapping + STRIDE + traceability chain. *Purpose: verifiable link from law to evidence.*
3. `sec:approach_selection` — evaluation of alternatives, company framework applicability, selected approach (fold the SVV taxonomy in here, once, in English). *Purpose: justify the chosen method.*
4. `sec:test_derivation` — two-level test-case format, categorisation, evidence/execution status. *Purpose: how a requirement becomes a repeatable test.*
5. `sec:test_environment` — generic requirements, reference zone design, NV1/NV2/NV3. *Purpose: define feasibility boundary.*
6. `sec:execution_governance` — tooling, reuse of functional/safety tests, RACI + lifecycle. *Purpose: process governance.*
7. `sec:evaluation_metrics` — verdicts + RCR/TMC/TER/ETS + reliability/validity. *Purpose: how results become requirement verdicts.*

**Deletions:** the two German scratch blocks and the trailing "3.2/3.3" outline (flagged in-file).

---

## I. Proposed structure of `umsetzung.tex`

The current structure is already close to the target; **keep the spine**, fill evidence, complete table bodies:

1. `sec:practical_scope` — realized scope, NV1-only, goal vs. validation-coverage distinction.
2. `sec:testbed_setup` — Test Object (REUSE) + `tab:assets` (REUSE) + realized environment + `tab:testbed_components`. *Add the topology figure (TODO present).*
3. `sec:instantiation` — applicability assessment (`tab:cm_applicability`) + CM↔TC↔RQ map (`tab:cm_tc_map`).
4. `sec:executed_tests` — one subsection per executed activity (attack-surface, identification, cleartext, intervention evidence, availability, robustness, access control, N/A+blocked). *Report only stored-evidence outcomes.*
5. `sec:requirement_verification` — `tab:status_matrix` + `tab:req_verification`.
6. `sec:objective_validation` — DSRM evaluation, `tab:goal_validation`, NV1 boundary.
7. `sec:discussion` — interpretation.
8. `sec:reliability_validity` — threats to validity.

**Remove/relocate:** the `\iffalse` legacy SVV/STRIDE block → methodology or delete; the commented System Analysis block is superseded by `subsec:test_object`.

---

## J. Content relocation plan

| Content | Source | Destination | Proposed section | Reason | Action |
|---|---|---|---|---|---|
| SVV-1..4 taxonomy (German) | `vorgehen` scratch block; `umsetzung` `\iffalse` | `grundlagen` | `sec:security_testing_approaches` | Established knowledge, referenced everywhere, currently duplicated | Rewrite in English once, delete both German copies |
| "Warum/Was/Wie" 3-layer model (MVO/62443-4-2/62443-4-1) | `vorgehen` + `umsetzung` German | `vorgehen` | `subsec:selected_approach` | Belongs to method justification; duplicated | Shorten to one English paragraph, delete duplicate |
| Condensed 14-RQ + CR-mapping summary | `anhang` matrices | `vorgehen` | `sec:traceability` | Main text needs the outcome; detail stays in appendix | Copy condensed, keep full matrices in appendix |
| Full CM-001..010 ↔ TC ↔ RQ mapping detail | `Notizen`/`WORKFLOW` | `anhang` | new appendix table | Too long for results body | Move detail, reference from `umsetzung` |
| Legacy asset-decomposition prose (commented) | `umsetzung` top comment | `umsetzung` | `subsec:test_object` (already covers it) or drop | Already superseded | Delete or fold selectively |
| STRIDE-at-requirement-level rule | `vorgehen` `%TODO` | `grundlagen`/`vorgehen` | `subsec:stride` / `subsec:derivation_mapping` | Recurs across tests | Write once |

---

## K. Requirement traceability assessment

Full RQ list is in `anhang` `tab:mvo-requirements`. Verification status is bounded by NV1 and stored evidence.

| RQ | Wording (short) | Acceptance criterion | Planned verification | Available evidence | Status | Gap |
|---|---|---|---|---|---|---|
| RQ-001 | Connection of a device must not cause hazard | Only design-approved services reachable; disruption → safe state | Attack-surface enum (NV1) + PROFIsafe injection (NV2/3) | nmap/Nikto (NV1) | **Partial** | Safe-state & injection need NV2/NV3 |
| RQ-002 | Protect HW transmitting safety-relevant data from corruption | CRC/param mismatch rejected; forged-CRC characterized | CRC injection (NV2/3), analytical forgeability | none stored | **Not assessed** | Needs NV2/NV3 + analysis artifact |
| RQ-003 | Collect evidence of interventions | Records readable, time-referenced, actor-attributed | Log read + event sequence (NV1) | `cm_rq003-04_*`, `RQ003_01/02` | **Supported (deviation)** | Only relative systick, no timestamp/actor |
| RQ-004 | Identify safety-critical SW/data | Identifiers retrievable | Identification inventory (NV1) | `cm_rq004-01_inventory` | **Partial** | Product granularity, no SBOM |
| RQ-005 | Protect safety-critical SW/data integrity | Integrity verified | (not covered) | none | **Not assessed** | No integrity test executed |
| RQ-006 | Identify installed SW | Inventory retrievable | Installed-SW inventory (NV1) | `cm_rq006-01_installed` | **Partial** | No component-level SBOM |
| RQ-007 | Provide SW identification at all times | Available on demand | swrev read + connection-hold | `cm_rq007-01_swrev` (avail. on request) | **Partial** | "at all times" not shown; RQ007-03 not executed |
| RQ-008 | Evidence of SW-installed events | Install event recorded | SW-change evidence | none (only conn/SCPU errors) | **Not assessed** | No install-event evidence |
| RQ-009 | Evidence of config modification | Config change recorded before/after | Config-change evidence | none | **Not assessed** | No config-change artifact |
| RQ-010 | Withstand malicious attempts | Stays available / robust | Siege + boofuzz + flood | boofuzz err 0x1000 (no log), Siege (no log) | **Inconclusive** | Missing stored outputs; cause of 0x1000 unknown |
| RQ-011 | Prevent unauthorized changes to safety settings | Writes rejected | Read-only enforcement, factory-reset | none (only anonymous read observed) | **Not assessed** | No write attempts recorded |
| RQ-012 | Tracing log retained 5 years | Records persist | Cold-start persistence (NV1) | `cm_rq003-04_log_02_after_coldstart` (empty) | **Supported (deviation)** | Log cleared on cold start |
| RQ-013 | Log versions of uploaded safety SW | Current-version-only confirmed | Inventory + downgrade | inventory (current only) | **Partial** | Downgrade not tested |
| RQ-014 | Restrict access to tracing-log data | Access controlled; not cleartext | Cleartext + access-control probe | valid sslscan (no TLS) | **Partial** | Third-party observation needs NV2 |

---

## L. Evidence and validation gaps (claims currently unsupported)

1. **RQ-010 robustness** — "boofuzz surfaced error 0x1000" has **no stored session log**; cause, reproducibility, and safety impact unknown.
2. **Availability (CM-009 Siege, TC-RQ007-03)** — no Siege summary or connection-hold outputs stored; cannot claim availability under load.
3. **Access control (RQ-011, RQ-014-03)** — no recorded **write/factory-reset attempts**; anonymous read ≠ proof of missing write protection.
4. **Config/SW-install evidence (RQ-008, RQ-009)** — no before/after config-change artifacts.
5. **CM-004 ZAP report** — referenced but not present in `Test_Cases_Srio/`.
6. **SSLscan** — the cited artifact must be `cm_rq006-03_sslscan.txt` (valid), not `cm_rq004-03_sslscan.txt` (failed run). Corrected via in-file note.
7. **All NV2/NV3 conclusions** — no traffic capture exists; do **not** claim visibility of cyclic PROFINET/PROFIsafe traffic or successful/failed MITM.
8. **Nikto Spring Boot Actuator finding** — unvalidated scanner output; verify directly before reporting.

---

## M. Quantitative evaluation opportunities (proposed — not measured values)

Computable from **stored** evidence:
- Open TCP ports: **1** (port 80). Open UDP ports: **2** (161 snmp, 49152 open|filtered). *(from nmap)*
- Anonymously exposed firmware/version identifiers: **8**. *(from `cm_rq004-01_inventory`)*
- Intervention-log entries lost on cold start: **2 → 0**; systick reset **44979 → 27509**. *(from `cm_rq003-04_*`)*
- Company instructions applicable vs. total: **applicable/blocked/N-A split over CM-001..010** (e.g. N-A: CM-002/003/006; blocked: CM-008).
- Test-case execution distribution: **executed-with-evidence / incomplete / prepared / theoretical / N-A** counts (see §G).
- nmap TCP scan duration: **808 s**; UDP scan: **28.8 s** *(timestamps in `.nmap` files)*.

**Must NOT be claimed without more evidence:** RCR/TMC/TER/ETS percentages, availability %, error rates under load, MITM success rate, any NV2/NV3 metric. Label all KPIs as *proposed* until Siege/boofuzz/ZAP/write-test evidence is stored.

---

## N. Prioritized next steps

**Essential for scientific coherence**
1. Consolidate the SVV taxonomy into `grundlagen` (English, cited) and delete both German duplicates in `vorgehen`/`umsetzung`.
2. Fix the dangling `\ref{sec:security_requirements}` in `anhang.tex` → point to `subsec:derivation_mapping`.
3. Confirm the `chap:introduction` and main document exist in the real project (this folder has neither a main file nor the intro).

**Essential for defensible results**
4. Store the missing artifacts: Siege log, boofuzz session/`boofuzz-results/`, ZAP report, and any write/factory-reset attempt logs; or explicitly mark those requirements "not assessed".
5. Re-point the SSLscan citation to `cm_rq006-03_sslscan.txt`; annotate `cm_rq004-03_sslscan.txt` as a void run.
6. Fill the omitted table bodies (`tab:assets`, `tab:testbed_components`, `tab:cm_applicability`, `tab:cm_tc_map`, `tab:status_matrix`, `tab:req_verification`, `tab:goal_validation`).

**Recommended improvement**
7. Add the topology figure and the IoT-Core screenshot (TODOs already present).
8. Add the small missing foundation blocks in `grundlagen` (V&V, evidence, black-channel, testing limits).

**Optional / future work**
9. Realize NV2 (mirror port) and NV3 (inline bridge) campaigns for the PROFIsafe tests; frame clearly as future validation.

---

## Consistency checks (§14)

- **Topic vs. structure:** `Moodle Anmeldung.txt` goal (validated testing methodology, empirical evidence at physical IT/OT interface) matches the chapter chain; the "validated" claim is appropriately softened to "partially validated (NV1)".
- **Traceability:** RQ → CR → asset → test → evidence chain is defined (`vorgehen` `subsec:traceability_model`) and mostly holds; gaps are in §K.
- **Labels/refs:** one confirmed dangling reference (`sec:security_requirements`). `chap:introduction` referenced but not in this folder (external). Alias label `chap:implementation_results_evaluation` correctly added.
- **Duplicated structures:** German SVV block duplicated across `vorgehen` and `umsetzung`; trailing outline in `vorgehen` duplicates finished sections.
- **`WORKFLOW.md` vs. `.docx`:** no `.docx` present; `.md` is authoritative; no conflict with `Security_Testing_Framework_Kali_EN.md`.
- **Level 1/2 usage:** consistent in `Notizen.md` and `WORKFLOW.md` (NV1 = Level 1 executed; NV2/NV3 = Level 2 designed). Verified before relying on it.
- **Executed vs. unexecuted:** clearly separable (§F/§G); the chapter comments now enforce the boundary.
- **University structure:** proposed hierarchies (§H/§I) follow Grundlagen/Vorgehen/Umsetzung/Zusammenfassung requirements.
- **"Validated" realism:** the network setup (single switch, no mirror/inline) does **not** support NV2/NV3 claims; "validated methodology" must remain "prototype with partial NV1 validation".
- **Compilation:** **Not performed — not possible here.** This folder has no main `.tex`, no `\documentclass`, no `.bib`, and no `.cls`. Only comment blocks were inserted (no new environments, no changes inside tables/captions/labels), so the additions are compile-safe when the files are included in the real main document. Compile from the actual thesis root to verify.
