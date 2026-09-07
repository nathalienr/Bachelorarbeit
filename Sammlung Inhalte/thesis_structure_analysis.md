# Thesis Structure Analysis

**Working title:** *Functional Testing of Security in Industrial Gateways under the New Machinery Regulation*
**Date:** 2026-09-07 · **Revision 2** (corrected execution status)
**Purpose of this document:** Advisory analysis only. It reconstructs the actual research process, identifies inconsistencies, proposes a coherent chapter structure, and defines an evidence-status discipline. It does **not** write thesis prose and does **not** invent tests, results, or citations.

> **Non-negotiable rule used throughout:** In `WORKFLOW.md` every `Result` field that begins with *"Expected …"* is a **plan**, not an observation. A command, an expected output, or a proposed procedure is **not** proof of execution.

> ## Revision 2 banner — read first
>
> The author supplied corrected execution facts (see §§13–19, which **supersede** the affected parts of §§3, 5, 6, 8, 10, 11). Two findings dominate this revision:
>
> 1. **No evidence files exist in the repository.** A workspace scan found **zero** raw artifacts (no `.nmap/.xml/.json/.pcap/.png/.html/.log/.dat`), no `evidence/` folder, and no result data inside the `.tex` files. Every corrected "performed" status below is therefore **author-reported only** and must be re-backed by a stored, citable artifact before any result is written into the thesis.
> 2. **The strict `NV1` feasibility boundary still holds** (NV2 mirror and NV3 inline bridge were not implemented), but several **NV1** company tests (CM-001, CM-004 web scan, CM-007, CM-009, CM-010) and robustness tests (Siege, boofuzz) **were** run — which changes the earlier "fuzzing out of scope" framing and the earlier over-cautious CM classifications.
>
> Where Revision 1 text conflicts with §§13–19, **§§13–19 win.**

---

## 1. Current state of the thesis

| File | Role | State | One-line assessment |
|------|------|-------|---------------------|
| `Moodle Anmeldung.txt` | Registered topic | Authoritative | Defines scope: functional testing of security at the **physical IT/OT interface**, empirical evidence of mitigation effectiveness, a **validated testing methodology**. |
| `grundlagen.tex` | Fundamentals | Mature | Strong, well-cited. A few foundations used later are still ungrounded (verification vs. validation, SVV taxonomy, repeatability, black-channel, evidence concept). |
| `vorgehen.tex` | Methodology | Started, misaligned | DSRM + traceability chain + requirement derivation are excellent. Four sections do not match the real method in `WORKFLOW.md` and over-claim the testbed. |
| `umsetzung.tex` | Implementation/Results | Disorganized | Notes dump + outdated System-Analysis + brainstorming. Reusable: asset table, Test Object description. Body must be rebuilt. |
| `anhang.tex` | Appendix | Partly mature | Requirement-derivation matrices = backbone (keep). SDLC = supporting (keep short). AI register = **not touched**. |
| `Security_Testing_Framework_Kali_EN.md` | Company input | Source | CM-001…CM-010, one Kali tool per countermeasure. Input, **not** a validated scientific source. |
| `WORKFLOW.md` | Working method + catalog | Mixed | 3-step method + two-level catalog for RQ-001…RQ-014. Contains real work **and** preliminary/AI-suggested ideas. |
| `Notizen.md` | Lab notes | Source | The as-built topology (flat /24, ports 1–4), Defense-in-Depth, MITM idea. |

---

## 2. Reconstructed research logic (from evidence only)

1. **Problem.** Regulation (EU) 2023/1230 makes cybersecurity part of machinery conformity. Industrial gateways at the IT/OT interface were historically perimeter-protected, so functional validation never systematically verified security functions → a gap between regulatory expectation and the company's established functional testing.
2. **Objective.** Produce a traceable, standards-based method to verify security functions at physical IT/OT interfaces and give practically justified evidence of mitigation effectiveness.
3. **Requirements derivation.** 14 requirements (RQ-001…RQ-014) extracted from MVO Annex III §1.1.9/§1.2.1, mapped via **prEN 50742** to **IEC 62443-4-2** CR/RE/EDR (documented in `anhang.tex`).
4. **Asset model.** SUT decomposed into Assets A–I with protection objectives (`umsetzung.tex`, Table `tab:assets`).
5. **Threat model.** STRIDE per requirement/asset, with a **dual role**: which threat a control *mitigates* vs. which threat the control is itself *exposed to*.
6. **Method.** `WORKFLOW.md` 3-step process → **Step 1** critical review of mitigations + gaps against device docs; **Step 2** SVV test planning (scenario → proves → justification → SVV category); **Step 3** two-level test catalog.
7. **Environment.** Flat `192.168.0.0/24` on switch `.91`: PLC `.1`/port1, SRIO `.2`/port2, Kali `.80`/port3 (USB3-GbE dongle), laptop `.7`/port4. Network variants **NV1** (direct IP), **NV2** (mirror/SPAN), **NV3** (inline bridge/MITM).
8. **Execution reality.** Only **NV1** was realizable. **NV2** (mirror port unconfirmed) and **NV3** (inline bridge) were **not** performed. Therefore all capture/injection/MITM tests are theoretical.
9. **Evaluation.** Verdicts (PASS/PARTIAL/FAIL/N-A) + four KPIs (RCR, TMC, TER, ETS) — computable only over the **performed** subset.

**Intended vs. proposed vs. implemented vs. evaluated**

- *Intended:* a validated functional-security testing methodology for the IT/OT interface.
- *Proposed (documents):* a complete 14-requirement, ~60-test-case catalog with NV1/NV2/NV3.
- *Implemented:* the NV1-reachable subset (IoT-Core HTTP enumeration/behavior + TIA-based functional baselines) — extent must be confirmed by the author against saved evidence.
- *Evaluated:* only what was implemented; the catalog as a whole is **not** empirically validated.

---

## 3. Main inconsistencies and contradictions (need author decisions)

1. **"Green marking" vs. feasibility — the central contradiction.**
   The brief says *"I only performed the tests marked green,"* but in `WORKFLOW.md` almost every test-case title is highlighted (`class="mark"`), **including** NV2/NV3 tests such as `TC-RQ001-03` (mirror capture), `TC-RQ001-04` (inline MITM), and `TC-RQ002-02/03` (injection). These are **impossible** with the built topology. → The highlighting cannot mean "performed." **Decision needed:** treat highlighting as *headings/navigation*, and classify execution strictly by (a) NV1 feasibility and (b) presence of saved evidence, **not** by color.
2. **Fuzzing scope.** `vorgehen.tex` (research design) declares fuzzing **out of scope**, yet `TC-RQ010-03` and company `CM-010` (boofuzz) are fuzzing. → Either admit robustness/fuzzing as in-scope SVV-3/SVV-5, or mark those cases *Proposed*.
3. **Testbed description vs. reality.** `vorgehen.tex` describes a 5-zone, VLAN-segmented, air-gapped, port-mirrored testbed; `Notizen.md` shows a single flat `/24`, no VLANs, no confirmed mirror. → Reframe as *target design* (method) vs. *as-built* (implementation).
4. **Test Specification vs. actual method.** `vorgehen.tex` data-sheet fields ≠ the real 3-step + two-level schema in `WORKFLOW.md` (missing SVV field, STRIDE dual role, NV precondition, Level-1/Level-2 split).
5. **Segmentation tests (CM-002).** Require ≥2 zones; the flat `/24` has none. → Document as *N/A — environment* rather than *FAIL*.
6. **TLS/hardening CMs.** CM-005 (SSLscan) is N/A because the SUT is HTTP-only; CM-006 (Lynis) needs host/root access unavailable on a closed device. → Mark *N/A* with justification.
7. **Dangling cross-references (compile-clean but wrong):**
   - `sec:security_requirements` (in `anhang.tex`) — no label. Likely target: `subsec:derivation_mapping`.
   - `subsec:methodological_scope` (in `vorgehen.tex`) — **fixed**: label added to the scope paragraph.
   - `subsec:attack_surface_asset_identification` (in `umsetzung.tex`) — no label. Likely target: `subsec:assets_attack_surfaces`.
8. **Duplicate content.** SVV taxonomy and STRIDE→FR mapping appear as free text/commented drafts in `umsetzung.tex` and again in `vorgehen.tex`. Consolidate once.
9. **Untranslated German TODO fragment** inside the prEN 50742 mapping table in `anhang.tex`.

---

## 4. Proposed chapter structure

### 4.1 Fundamentals (`grundlagen.tex`) — keep, add targeted foundations
Add only what later chapters consume (each with a "used in Chapter X" pointer):
- **Verification vs. Validation** (IEC 62443-4-1) — *Purpose:* ground the two words the whole thesis uses. *Source:* existing 4-1 citation. *Missing:* explicit definition.
- **IEC 62443-4-1 SVV test-type taxonomy (SVV-1…SVV-4)** — *Purpose:* every test is SVV-labeled. *Source:* WORKFLOW.md/company doc. *Must not:* present SVV-5 unless a source defines it.
- **Repeatability & reproducibility** — *Purpose:* justify the standardized data sheet and TER/ETS.
- **Evidence & evidence status / auditability** — *Purpose:* introduce the classification used in results.
- **PROFINET/PROFIsafe black-channel, consecutive number, F_WD_Time, CRC/F_Dest_Add** — *Purpose:* RQ-001/RQ-002 rationale. *Source:* WORKFLOW.md + PROFIsafe refs. *Must not:* invent numeric parameters beyond cited docs.
- **Limitations of security testing** (presence not absence; black-box boundary) — *Purpose:* supports the "prototype/partially validated" framing.

### 4.2 Methodology (`vorgehen.tex`) — realign to the real method
Recommended section flow:
1. **Research design & scope (DSRM)** — keep; add a *scope-limitation* label (done).
2. **Initial situation, environment, constraints** — *new:* isolated OT, black-box product, no source access, single-switch topology, safety-first (no production testing).
3. **Requirements analysis → requirements definition** — reuse the derivation chain; state the 14 RQ as the requirements baseline.
4. **Regulatory derivation & asset mapping** — keep; reference `app:requirement_derivation`.
5. **Traceability model** — keep (strong).
6. **Derivation and evaluation of alternative testing approaches** — *new/relocated:* distill the rejected options currently commented in `umsetzung.tex` (pure functional black-box; abstract 62443 verification; unstructured pentest; fuzzing; OWASP IoT; risk-based) into a short structured comparison, then justify the chosen **SVV-structured functional verification + company CM tool bindings**.
7. **Test specification schema** — *rewrite:* the 3-step method + two-level catalog (Level 1 abstract / Level 2 concrete), STRIDE dual role, SVV field, NV precondition; define the **evidence-status classification** here.
8. **Test environment (generic requirements + NV1/NV2/NV3)** — *reframe:* generic safe-testbed principles; move the as-built topology to Implementation.
9. **Execution framework & governance (RACI, lifecycle)** — keep; reconcile tool set with CM-001…CM-010.
10. **Evaluation metrics** — keep verdicts + KPIs; state they apply to the **performed subset** only.
11. **Reliability, accuracy, limitations** — *new:* repeatability of black-box tests, tester dependence, non-performability of NV2/NV3.

### 4.3 Implementation & Results (`umsetzung.tex`) — rebuild body, keep facts
1. **Test Object & attack surface** — keep Test Object + Table `tab:assets`; salvage facts from the commented System-Analysis.
2. **Realized test environment** — flat `/24`, NV1 realized; NV2/NV3 not built (state why).
3. **Instantiation of the methodology on the SUT** — RQ→CR→Asset→TC map; which company CMs were adopted/adapted/omitted; evidence-status legend.
4. **Executed tests & observed results** — *only performed TCs*, grouped by SVV. Real Nmap-style output (e.g., the `TC-RQ001-02` port findings) may be reported **once confirmed** as saved evidence.
5. **Non-executed / theoretically specified tests** — NV2/NV3, injection, MITM, fuzzing — presented as design + rationale, explicitly **not executed**.
6. **Requirement verification** — verdicts + KPIs over the performed subset.
7. **Discussion** — validation against the thesis goal, reliability, repeatability/reproducibility, limitations, threats to validity, residual validation gap.

### 4.4 Appendix (`anhang.tex`)
- **Requirement Derivation Matrices** — keep (backbone); lift a condensed summary into Methodology; fix the dangling `sec:security_requirements` ref; resolve the German TODO fragment.
- **Secure Development Lifecycle** — keep short/supporting; verify figure path and single reference from Governance.
- **AI usage register** — unchanged.

---

## 5. Recommended test categorization (manageable for a Bachelor's thesis)

Use **one primary scientific axis** plus **two orthogonal secondary axes**. Do **not** adopt all the candidate dimensions.

**Primary axis — IEC 62443-4-1 SVV test type** (already used, standards-anchored, gives traceability from requirement to test purpose):
- SVV-1 Requirements-based (functional baseline in normal operation)
- SVV-2 Threat-mitigation (effectiveness under fault/attack)
- SVV-3 Vulnerability (attack-surface/known-weakness discovery)
- SVV-4 Penetration (active protocol manipulation/exploitation)

**Secondary axis 1 — Network position / prerequisite (feasibility):** NV1 (direct IP) / NV2 (mirror/SPAN) / NV3 (inline bridge/MITM). This axis directly encodes what was *possible* on the built topology.

**Secondary axis 2 — Execution status (evidence discipline):** see §6.

**Recommendation on Level 1 / Level 2:** keep them as a **documentation schema** (abstract spec vs. concrete execution), **not** as a scientific category. They answer *"what/how is specified"* and *"how is it run here,"* which is a presentation format, not a taxonomy. The scientific categorization is SVV × NV × execution status. This is the combination that best supports end-to-end traceability while staying scope-appropriate.

**Company CM-001…CM-010 — corrected execution status (see §13 for the full matrix).** Statuses are author-reported; no artifact is yet in the repo.

| CM | Tool | Corrected execution status | Applicability |
|----|------|----------------------------|---------------|
| CM-001 Network exposure | Nmap | **Performed** (TCP full + UDP top-ports) — reported | Fully applicable (NV1) |
| CM-002 Segmentation | Nmap | **Not applicable in setup** (no zone/conduit model) | N/A to topology — *methodology finding, not product fault* |
| CM-003 Default/weak creds | Hydra | **Not applicable** (no authentication endpoint) | N/A to device — anonymous read-only is a *separate* observation |
| CM-004 RBAC/priv-esc | OWASP ZAP | **Web scan performed** (report); **multi-role RBAC N/A** (single anonymous role) | Split: scan applicable / RBAC comparison N/A |
| CM-005 TLS config | SSLscan | **Not applicable** (no TLS endpoint, 443 closed) | N/A to device — HTTP-only is a *separate* observation |
| CM-006 Hardening | Lynis | **Not executed** (tool-to-target mismatch; no OS shell) | N/A to device (embedded) |
| CM-007 Debug/iface exposure | Nikto | **Performed** against IoT-Core (report) — reported | Applicable with caveats (generic signatures, false positives) |
| CM-008 Known CVEs | OpenVAS/GVM | **Not executed** (offline-environment/tool constraints) | Blocked by environment |
| CM-009 Load/logging | Siege | **Performed** at 50 conns (framework) **and** 3 conns (SRIO req) | Applicable (NV1) — availability claim needs evidence |
| CM-010 Fuzzing | boofuzz | **Performed** against HTTP; **error `0x1000` observed** | Applicable (NV1) — causation/impact **unresolved** |

*Because no artifact is stored, each "Performed" is author-reported and needs a citable file (command, params, tool version, timestamp, output) before any result enters the thesis. Do not call an N/A test "failed"; do not call a blocked test "passed."*

---

## 6. Evidence-status model (four independent dimensions — do NOT collapse to pass/fail)

A single pass/fail field is insufficient. Classify every test on **all four** axes. A test can be *successfully executed but inconclusive*, *not applicable without being failed*, or *technically completed while the requirement stays unverified*.

**(a) Execution status:** Performed · Partially performed · Not performed · Not applicable · Blocked by environment/tool · Planned & still feasible (NV1) · Status unclear.

**(b) Evidence quality:** Raw evidence available · Report available · Only narrative notes · Evidence incomplete · **No evidence available** *(← current state for every test: nothing is stored in the repo)*.

**(c) Applicability:** Fully applicable · Applicable with adaptation · Partially applicable · Not applicable to the device · Not applicable to the topology · Applicability cannot be assessed.

**(d) Assessment outcome:** Requirement supported by evidence · Requirement partially supported · Requirement not supported · Potential deviation observed · Inconclusive · Not assessed.

**Gate rule:** With evidence quality = *No evidence available*, the assessment outcome can be at most *Inconclusive / Not assessed*, regardless of a confident execution report. Author-reported execution raises **(a)** but not **(d)** until an artifact is stored.

---

## 7. Traceability model (target, end-to-end)

```
Regulatory source (MVO Annex III §1.1.9 / §1.2.1)
  → Requirement (RQ-0xx)
    → Standard control (prEN 50742 clause → IEC 62443-4-2 CR/RE/EDR)
      → Asset / interface (A–I; IoT-Core HTTP, PROFINET/PROFIsafe, physical switch/rotary)
        → Threat (STRIDE, dual role: mitigated vs. exposed)
          → Security function (mitigation) / identified gap
            → Test objective
              → Test technique (SVV-1..4)
                → Prerequisite (NV1 / NV2 / NV3)
                  → Execution status (evidence-status class)
                    → Evidence (PCAP / XML / JSON / screenshot / log)
                      → Result (verdict; observed, not expected)
                        → Assessment criterion (PASS/PARTIAL/FAIL/N-A)
                          → Compliance conclusion (partial, no legal/cert claim)
```

Suggested master table columns for the thesis (one row per TC): `RQ | CR/EDR | Asset | STRIDE(mit/exp) | Security function/Gap | Objective | SVV | NV | Status | Evidence | Result | Verdict`.

---

## 8. Evidence availability — corrected finding

**Repository scan result: NO evidence artifacts are present.** Zero `.nmap/.xml/.json/.pcap(ng)/.png/.jpg/.html/.log/.dat/.csv` files; no `evidence/`, `results/`, `scans/`, or `reports/` folder; the `.tex` files contain no result data. The only real-looking data anywhere is the inline `TC-RQ001-02` fragment in `WORKFLOW.md` (ports 80/tcp, 161/udp, 49152/udp) — that is a note in a planning document, **not** a stored scan file.

**Consequence:** every corrected "Performed" (CM-001, CM-004 scan, CM-007, CM-009, CM-010, and the NV1 TC-RQ tests) is currently **author-reported without a citable artifact**. This is the single largest evidence gap and the top priority (see §19).

**To be collected/stored per performed test (P0):** the exact command + parameters, tool + version, timestamp, target IP/interface, raw output file, and a short observation. Store under a versioned `evidence/` tree named by test ID (e.g. `evidence/cm001/…`, `evidence/tc-rq001-02/…`).

**Genuinely not obtainable with the current topology (future work):** PROFIsafe capture (needs NV2), frame injection/CRC-recompute/MITM (needs NV3), cross-zone segmentation (no 2nd zone), TLS results (no TLS endpoint), OS-level hardening (no shell), machine-readable SBOM (RQ-004/RQ-006 completeness).

---

## 9. Risks to the scientific argument & threats to validity

- **Over-claiming execution** (biggest risk): presenting "Expected" outputs as measured. Mitigate with the §6 discipline.
- **Construct validity:** does an NV1 HTTP verdict actually evidence the *safety* control, or only the diagnostic path? State the boundary explicitly.
- **Internal validity / reproducibility:** black-box, single device, single run; tester-dependent steps. Report N runs and fix parameters.
- **External validity:** one SUT, one vendor, one fieldbus — do not generalize to "industrial gateways" broadly.
- **Regulatory validity:** the derivation is the author's, not a certified assessment; avoid legal/certification conclusions.
- **Validation gap:** the methodology is exercised only on the NV1 subset; the full framework is not empirically validated.

---

## 10. Answers to the mandatory questions

1. **Realistic scientific contribution:** a **traceable, standards-anchored functional-security test methodology** (MVO → prEN 50742 → IEC 62443-4-2 → STRIDE → SVV → test case) **plus a partial empirical demonstration** on one SUT via the NV1-reachable interface. The contribution is the *method + traceability + partial evidence*, not a fully validated framework.
2. **Nature of the output:** a **prototype / partially validated methodology** (a validated *concept* with a *partial* empirical demonstration). Not a fully validated final framework.
3. **Research question (suggested):** *"How can the cybersecurity obligations of Regulation (EU) 2023/1230 for industrial gateways at the physical IT/OT interface be translated into a traceable, standards-based functional security testing methodology, and to what extent can its mitigation-effectiveness claims be empirically demonstrated on a representative safety-related I/O device?"*
   Sub-questions: (a) How are MVO obligations derived into testable component requirements? (b) Which security testing approaches fit functional verification at the IT/OT interface? (c) How should tests be categorized for traceability? (d) Which requirements can be empirically verified on the SUT, and which remain theoretical due to environmental constraints?
4. **Chapter allocation:** foundations → Fundamentals; derivation/method/alternatives/metrics → Methodology; SUT, real environment, executed tests, results, verification, discussion → Implementation & Results; full matrices + SDLC → Appendix; validity/limitations → Discussion within Implementation & Results.
5. **CM categorization:** see §5 table (Adopted/Adapted/Omitted-N-A/Conditional/Decide).
6. **Actually performed:** NV1 HTTP enumeration/behavior tests and TIA functional baselines — *subset to be confirmed against saved evidence*.
7. **Only theoretical:** all NV2/NV3 tests (capture, injection, MITM), fuzzing, segmentation, TLS, host-hardening.
8. **Impossible with the topology:** anything needing port mirroring (NV2) or an inline bridge/MITM (NV3), and cross-segment segmentation.
9. **Evidence needed for "verified":** saved raw artifact per test (PCAP/XML/JSON/screenshot/log) tied to a PASS criterion, with repeatability across ≥1 documented re-run.
10. **Discussing Level 2 without implying execution:** present them in a dedicated *"Theoretically specified / not executed"* section, use conditional/future tense, and label each with the §6 status. Never place them in the *Observed Results* section.
11. **Compliance without unsupported claims:** speak of *"support for demonstrating conformity"* and *"evidence toward specific IEC 62443-4-2 CRs,"* never *"the device is compliant/certified."* Keep prEN 50742 as *draft*.
12. **Reliability/repeatability/reproducibility/validity:** dedicate a Discussion subsection; report fixed parameters, tool versions, number of runs, tester steps, and the §9 threats.
13. **`umsetzung.tex` to retain:** Test Object description; Table `tab:assets`; salvageable facts from the commented System-Analysis; the real topology. Discard commented brainstorming and expected-result narratives.
14. **`vorgehen.tex` to align with `WORKFLOW.md`:** Test Specification (3-step + two-level schema, STRIDE dual role, SVV field, NV precondition, evidence-status), Test Environment (generic + NV1/NV2/NV3), and reconcile the fuzzing-scope contradiction.
15. **Smallest realistic remaining task set for a defensible thesis:**
    1. Fix scope/environment contradictions and the three dangling refs.
    2. Rewrite Test Specification to the real method; define evidence-status.
    3. Consolidate the SUT/environment facts into Implementation.
    4. Report **only** confirmed NV1 results with saved evidence.
    5. Add the "not executed" section + a limitations/threats-to-validity discussion, and frame the output as a prototype/partially validated methodology.

---

## 11. Prioritized action list

> **Revision 2 override:** the single highest priority is now **P0 — collect and store the raw evidence** for the tests the author reports as performed (CM-001, CM-004 web scan, CM-007, CM-009 ×2 load levels, CM-010, and the NV1 TC-RQ tests). Without stored artifacts, none of these can be written up as results. See §19 for the consolidated priority list; the table below remains valid for the structural work.

| # | Priority | Action | Files |
|---|----------|--------|-------|
| 1 | **P0** | Resolve the "green = performed" contradiction; adopt the §6 evidence-status discipline and tag every TC. | WORKFLOW.md, umsetzung.tex |
| 2 | **P0** | Separate *target design* from *as-built* testbed; state NV2/NV3 not performed. | vorgehen.tex, umsetzung.tex |
| 3 | **P0** | Rewrite Test Specification to the 3-step + two-level schema; define evidence-status + STRIDE dual role. | vorgehen.tex |
| 4 | **P1** | Confirm which NV1 tests have saved evidence; report only those as results. | umsetzung.tex |
| 5 | **P1** | Fix dangling refs (`sec:security_requirements`, `subsec:attack_surface_asset_identification`); `subsec:methodological_scope` already fixed. | anhang.tex, umsetzung.tex |
| 6 | **P1** | Reconcile fuzzing scope; finalize CM adoption table with N/A justifications. | vorgehen.tex, umsetzung.tex |
| 7 | **P2** | Add missing foundations (verification/validation, SVV taxonomy, repeatability, black-channel, testing limits). | grundlagen.tex |
| 8 | **P2** | Consolidate duplicated SVV/STRIDE drafts into one location. | vorgehen.tex, umsetzung.tex |
| 9 | **P2** | Lift a condensed derivation summary into Methodology; resolve German TODO in mapping table. | vorgehen.tex, anhang.tex |
| 10 | **P3** | Add Discussion: reliability, reproducibility, threats to validity, residual validation gap; frame output as prototype/partially validated. | umsetzung.tex |

---

## 12. Confidential / anonymization flags

Review before publication: internal `SRIO-xxxx` document IDs, IoT-Core endpoint paths, the `ifm-CRC-Tool`, device order/serial identifiers, and internal IP plan. Confirm these may appear in an externally submitted thesis or replace with anonymized placeholders.

---

## 13. Corrected CM execution matrix (author-reported; no stored artifact yet)

Axes: (a) execution · (b) evidence quality · (c) applicability · (d) assessment outcome (see §6).

| CM | Tool | (a) Execution | (b) Evidence | (c) Applicability | (d) Assessment | Note |
|----|------|---------------|--------------|-------------------|----------------|------|
| CM-001 | Nmap | Performed (TCP full + UDP top-ports) | None stored | Fully applicable (NV1) | Inconclusive until artifact | Store `.nmap/.xml`; compare to a port matrix. |
| CM-002 | Nmap | Not applicable | — | N/A to topology | Not assessed | No zone/conduit model → *methodology/organizational* finding, not product fault. |
| CM-003 | Hydra | Not applicable | — | N/A to device (no auth endpoint) | Not assessed (credential) | Anonymous read-only access = *separate* observation, assess vs. RQ-011/RQ-014. |
| CM-004 | OWASP ZAP | Web scan performed; RBAC comparison N/A | Report (reported) | Split: scan applicable / RBAC N/A (1 role) | Inconclusive; RBAC not verifiable | Do not claim comprehensive RBAC. |
| CM-005 | SSLscan | Not applicable | — | N/A to device (no TLS/443) | Not assessed (TLS) | HTTP-only = *separate* confidentiality observation (link to TC-RQ014-02). |
| CM-006 | Lynis | Not executed | — | N/A to device (no OS shell) | Not assessed | Tool-to-target mismatch; propose embedded hardening review at method level only. |
| CM-007 | Nikto | Performed | Report (reported) | Applicable w/ caveats | Inconclusive until validated | Generic signatures → manually validate findings; no auto-vuln claims. |
| CM-008 | OpenVAS/GVM | Not executed (blocked) | — | Blocked by offline environment | Not assessed | Absence of results ≠ absence of CVEs. Offline/manual CVE correlation = future work. |
| CM-009 | Siege | Performed ×2 (50 conns framework; 3 conns SRIO req) | None stored | Applicable (NV1) | Inconclusive re availability/resilience | Safety/cyclic channel **not** monitored → no domain-separation claim. |
| CM-010 | boofuzz | Performed (HTTP); **error `0x1000` observed** | None stored | Applicable (NV1) | Inconclusive; causation unresolved | See §17. Cautious wording only. |

## 14. Corrected TC-RQ status matrix (18 listed tests; author-reported, no stored artifact)

| TC-RQ | Title (short) | NV | (a) Execution | (c) Applicability | (d) Assessment | Note |
|-------|---------------|----|---------------|-------------------|----------------|------|
| 001-02 | Attack-surface enumeration | NV1 | Performed (≡ CM-001+CM-007) | Fully | Partially supported | Store Nmap/Nikto artifacts. |
| 003-01 | Evidence baseline | NV1 + TIA I&M read | Performed | Applicable | Partially supported | curl error-log + I&M read. |
| 003-04 | Time-attribution failure (systick) | NV1 | Reported/feasible — **verify** | Applicable | Inconclusive | Needs pin-short + cold-start artifacts. |
| 012-02 | Cold-start deletion (⇄ 003-04) | NV1 | Reported/feasible — **verify** | Applicable | Inconclusive | Shares prereq with 003-04 (see §9). |
| 004-01 | Identification inventory (SW+data) | NV1 + TIA I&M | Performed | Applicable | Partially supported | curl `/deviceinfo/*` + I&M0/4/5. |
| 006-01 | Installed-software inventory | NV1 | Performed | Applicable | Partially supported | Top-level versions only (no SBOM). |
| 006-03 | Plaintext inventory exposure (DiD) | NV1 (self-response) | Partially performed | Partially (3rd-party exposure needs NV2) | Inconclusive for exposure | Only own-response cleartext is provable under NV1. |
| 007-01 | Identification availability baseline | NV1 | Performed | Applicable | Partially supported | |
| 007-03 | Connection-hold self-DoS | NV1 | Performed — cautious | Applicable | Inconclusive | See §9; report #conns/duration/recovery; no "DoS vuln" claim. |
| 008-01 | Software-event evidence baseline | NV1 | Performed | Applicable | Partially supported | curl error-log. |
| 009-01 | Config-mod evidence surface baseline | NV1 + TIA | Performed | Applicable | Partially supported | |
| 010-02 | Network/L2 flood resilience | NV1 flood | Partially performed | Partially (cyclic impact needs NV2) | Inconclusive re safety | Only HTTP-iface availability observable under NV1. |
| 010-04 | App-layer flood + domain separation | NV1 flood | Split: flood performed / domain-sep incomplete | Partially | Inconclusive re domain sep | Domain-separation needs safety-channel monitoring. |
| 011-01 | Read-only enforcement | NV1 | Performed | Applicable | Partially supported | Attempted writes over HTTP. |
| 011-02 | Unauthenticated factory reset | NV1 | **Verify** — was command sent/accepted/state changed? | Applicable | Inconclusive | Do not infer success from protocol discovery (see §9). |
| 013-01 | Current-version-only confirmation | NV1 | Performed | Applicable | Partially supported | |
| 014-02 | Cleartext confidentiality of tracing log | NV1 (self-response) | Partially performed | Partially (unauth-observer needs NV2) | Inconclusive for exposure | Distinguish cleartext-transport vs. confidential-content vs. third-party exposure. |
| 014-03 | Access-control mechanism probe | NV1 | Performed | Applicable | Partially supported | Do not generalize absence of auth on read-only iface to *all* access control. |

*Evidence quality (b) = **No evidence available** for every row until artifacts are stored. "Verify" = execution not proven by the prompt; confirm before writing a result.*

## 15. CM-to-TC mapping (relationship types)

| CM | CM objective | Requirement | Related TC-RQ | Relationship | Execution status |
|----|--------------|-------------|---------------|--------------|------------------|
| CM-001 Nmap | Network exposure | RQ-001 (domain sep.) | TC-RQ001-02 | Direct implementation | Performed |
| CM-007 Nikto | Debug/iface exposure | RQ-001 | TC-RQ001-02 | Supporting test | Performed |
| CM-003 Hydra | Weak credentials | RQ-011/RQ-014 | TC-RQ011-01, 014-03 | No direct mapping (no auth endpoint) | N/A |
| CM-004 ZAP | RBAC/priv-esc | RQ-011 | TC-RQ011-01 | Partial implementation (scan yes / RBAC N/A) | Partial |
| CM-005 SSLscan | TLS config | RQ-014 (confid.) | TC-RQ014-02 | No direct mapping (no TLS) — informs cleartext observation | N/A |
| CM-008 OpenVAS | Known CVEs | RQ-004/RQ-006 | TC-RQ006-02 | Adapted implementation | Blocked |
| CM-009 Siege | Load/logging | RQ-007/RQ-010 | TC-RQ007-03, 010-02, 010-04 | Direct/partial implementation | Performed ×2 |
| CM-010 boofuzz | Fuzzing/robustness | RQ-010 | TC-RQ010-03 | Direct implementation | Performed (0x1000) |
| CM-002 Nmap | Segmentation | RQ-010 (domain sep.) | TC-RQ010-04 (concept) | No direct mapping | N/A |
| CM-006 Lynis | Hardening | — | — | No direct mapping (tool mismatch) | Not executed |

*Rule: CM IDs and TC-RQ IDs are **not** the same tests. Where one practical activity supports both systems (e.g. the Nmap run underlies CM-001 and TC-RQ001-02), describe the execution **once** and cross-reference via this table — do not double-count.*

## 16. Existing functional/safety-test overlap matrix (initial proposal)

| Security requirement | Existing functional/safety test | What it verifies | Adversarial perspective? | Security gap | Reuse decision |
|----------------------|----------------------------------|------------------|--------------------------|--------------|----------------|
| RQ-001 (connection → no hazard) | PROFIsafe watchdog/passivation & re-integration (safety validation) | Fail-safe on random channel loss; ack-gated re-integration | No (random fault, not attacker) | Deliberate disruption/replay boundary | Reusable **with** security-specific acceptance criteria |
| RQ-002 (transmission integrity) | iParCRC/F_ParCRC rejection (safety functional test) | Rejects mismatched parameter CRC | No | Intentional valid-CRC forgery (needs NV3) | Reusable with security acceptance criteria; forgery = dedicated future test |
| RQ-003/RQ-009 (intervention/mod evidence) | Diagnostic/error-log functionality | Records selected events | No (no attribution/time model) | Actor identity, absolute time, tamper-proof retention | Dedicated security test required |
| RQ-010 (withstand malicious attempts) | Safety watchdog / fail-safe reaction | Safe state on disturbance | No | Flooding/DoS resilience, domain separation under attack | Dedicated security test required |

*Rule: an existing functional or safety test does **not** automatically prove cybersecurity compliance. Treat TIA Portal as a supporting engineering tool, not a security testing tool.*

## 17. The boofuzz `0x1000` observation — how to handle it

**What is known (from the prompt):** boofuzz was run against the SUT's HTTP port and error code `0x1000` was displayed/produced during the test.

**What is NOT known (must be established from evidence before any claim):** the meaning of `0x1000`; where it was observed (web UI, IoT-Core JSON, LED/diagnostics); reproducibility; whether HTTP communication was interrupted; whether the web interface stayed accessible; whether the device recovered or needed a restart; and whether the **safety function** was affected (it was **not** independently monitored, so no safety claim is possible).

**Permitted wording:** “An error with code `0x1000` was observed during the boofuzz test on the HTTP interface.”
**Forbidden wording (unless evidence proves it):** “The fuzzing attack caused a security vulnerability / crash / safety failure.”

**Classification:** Execution = *Performed*; Evidence = *No artifact stored*; Assessment = *Inconclusive — causation, reproducibility, and impact unresolved*. Treat as a **finding requiring follow-up**, not a confirmed defect.

## 18. Revised, multi-dimensional test categorization

Keep it manageable: classify each test on four small axes (this replaces the earlier single-axis view).

- **Test purpose:** attack-surface/exposure · authentication & access control · confidentiality/protected communication · software/version/vulnerability identification · event evidence/logging/traceability · robustness & availability · segmentation/domain separation · secure configuration/hardening.
- **Required environment:** NV1 direct · NV2 passive visibility · NV3 active inline · TIA/engineering-tool support · existing functional-test evidence.
- **Test character:** observation/inventory · active functional verification · load/robustness · negative test · vulnerability scan · protocol manipulation · document/evidence review.
- **Execution status:** the §6 four-dimension model.

The SVV-1..SVV-4 axis from Revision 1 remains the normative anchor; the four axes above are the practical filing system that makes the NV1-only reality and the applicability findings explicit.

## 19. Consolidated priorities (Revision 2)

**Essential for a defensible thesis**
1. **Collect & store raw evidence** for every author-reported performed test (CM-001, CM-004 scan, CM-007, CM-009 ×2, CM-010, NV1 TC-RQ tests): command, params, tool+version, timestamp, target, output file, observation.
2. Write the **applicability findings** (CM-002/003/005/006 N/A or blocked) as a *first-class methodology result* — tool-to-target and topology mismatches, not product failures.
3. Establish the `0x1000` facts (§17) or explicitly mark them unresolved.
4. Reframe scope: robustness/availability (Siege, boofuzz) **was** exercised → reconcile the “fuzzing out of scope” statement in `vorgehen.tex`.
5. Fix the three dangling refs; align Test Specification with the real 3-step + two-level method; separate target-design vs. as-built testbed.

**Valuable if time permits**
6. Manually validate Nikto findings; store a port-matrix comparison for CM-001.
7. Build the CM-to-TC and functional-overlap tables (§§15–16) with real entries.
8. Add the offline/manual CVE-correlation concept (RQ-004/006) as a scoped proposal.

**Future work (out of current topology)**
9. NV2 (mirror/SPAN) passive PROFIsafe capture; NV3 (inline bridge) MITM/injection.
10. Segmentation testing with a real zone/conduit model; embedded hardening assessment; safety-channel monitoring to substantiate domain-separation claims.

## 20. Answers to the new mandatory questions (§17 of the update)

1. **Fully executed CM:** CM-001 (Nmap), CM-007 (Nikto), CM-009 (Siege ×2), CM-010 (boofuzz); CM-004 web scan (RBAC part N/A) — **all author-reported, none with a stored artifact yet.**
2. **Only partially applicable:** CM-004 (scan yes / multi-role RBAC N/A).
3. **Not applicable to the device:** CM-003 (no auth endpoint), CM-005 (no TLS), CM-006 (no OS shell).
4. **Blocked by environment/tool:** CM-008 (OpenVAS offline), plus CM-002 (no zone model — topology applicability).
5. **Evidence per executed CM:** none in the repository → must be created/stored (see §8, §19).
6. **TC-RQ proven performed:** none is *proven* (no artifacts); strongest author-reported: 001-02, 003-01, 004-01, 006-01, 007-01, 008-01, 009-01, 011-01, 013-01, 014-03.
7. **Feasible under NV1:** all 18 listed (fully for HTTP/curl/scan tests; partially for 006-03, 010-02, 010-04, 014-02).
8. **Require NV2/NV3:** passive-capture/exposure sub-claims (006-03, 010-02, 010-04 domain-sep, 014-02) need NV2; injection/MITM (001-03/04, 002-02/03) need NV2/NV3.
9. **Need TIA/functional evidence:** 001-01, 001-05, 002-01, 003-01/009-01 (I&M reads), 004-01 (I&M), and any domain-separation claim.
10. **Overlap CM↔TC:** Nmap (CM-001≡TC-RQ001-02), Nikto (CM-007→TC-RQ001-02), Siege (CM-009→TC-RQ007-03/010-02/010-04), boofuzz (CM-010→TC-RQ010-03), ZAP (CM-004→TC-RQ011-01).
11. **Support requirement verification:** exposure/identification/logging-surface baselines (001-02, 004-01, 006-01, 007-01, 008-01, 013-01) — *partial* support once artifacts exist.
12. **Remain inconclusive:** 003-04, 012-02, 010-02, 010-04 (domain sep.), 011-02, 014-02, and the boofuzz impact.
13. **`0x1000` claim:** only “observed during the boofuzz HTTP test”; cause/reproducibility/impact unresolved (§17).
14. **Cannot conclude (no cyclic/safety monitoring):** no claim that the safety function was unaffected, no domain-separation confirmation, no passive-capture-based confidentiality proof.
15. **Represent N/A tests:** as *Not applicable* with a documented technical justification (missing interface/function/zone) — never as *FAIL*; separate setup limitation from product deficiency.
16. **Tool-to-target mismatch handling:** make *applicability assessment* an explicit methodology step; record why a tool assumes a function the embedded device lacks; propose a fitting alternative at method level only.
17. **Realistic contribution:** a **prototype security testing methodology with partial practical validation under NV1 constraints** — traceable derivation (MVO→prEN 50742→IEC 62443-4-2→STRIDE→SVV→TC) + a demonstrated, tool-to-target-aware application on one SUT.
18. **Minimum remaining work:** §19 “Essential” block (evidence consolidation, applicability findings, `0x1000`, scope reconciliation, structural fixes).
19. **Chapter split:** derivation/method/tool-applicability/NV-model/evidence-model/alternatives → `vorgehen.tex`; environment/executed tests/results/verification/limitations → `umsetzung.tex`.
20. **Functional-vs-security framing:** state that safety validation covers *random-fault* behavior; security requires an *adversarial* perspective and security-specific acceptance criteria (§16). Reuse functional evidence only where the adversarial objective is genuinely covered; otherwise mark *dedicated security test required*.
