# Review of vorgehen.tex (Methodology Chapter)

I read all three files in full (grundlagen.tex 438 lines, vorgehen.tex 330 lines, anhang.tex 528 lines — note the files are considerably longer than a naive line-count tool reports; see caveat at the end) and cross-checked every terminology item, requirement ID, FR/CR mapping, and cross-reference between them.

## A. Executive Summary

vorgehen.tex is methodologically solid and, in most places, unusually well cross-referenced against grundlagen.tex: the DSRM framing, the traceability chain, the requirement-derivation criteria, and — most impressively — nearly all numeric claims (5 Direct / 7 Partial / 2 No-mapping IEC 62443-4-2 outcomes, the FR sets per test domain) check out exactly against the detailed tables in anhang.tex. This is genuinely careful engineering of a requirement-derivation pipeline.

The main weaknesses are not gross contradictions but **quiet gaps between what the main text asserts and what the foundations chapter actually defines**, plus a few **orphaned or under-justified elements**: a security-objective category ("Accountability") that is used as if it were introduced in grundlagen.tex, the silent blending of prEN 50742 "Approach A" (SRSL) content into an "Approach B" (IEC 62443)-based derivation chain without ever explaining the relationship in the main text, one small FR omission that is repeated in two tables, and a fully worked-out appendix figure/chapter that is never referenced from the methodology chapter that it was clearly created for.

## B. Major Issues

**1. "Accountability" is used as a Security Objective without ever being defined as a security goal.**
vorgehen.tex states requirements were "classified by the security objective it primarily expresses, corresponding to the security goals ... introduced in Section [subsec:security_goals]". But grundlagen.tex formally introduces only Confidentiality, Integrity, Availability, plus the extensions Authenticity and Utility. "Accountability" is never defined there (the closest related idea, "Non-repudiation," appears only inside a table cell, grundlagen.tex and grundlagen.tex, not as a defined goal). Yet the Appendix — which vorgehen.tex explicitly cites as backing this claim — assigns "Accountability" as the Security Objective for 5 of 14 requirements (RQ-003, 008, 009, 012, 013; see e.g. anhang.tex). Over a third of the requirement catalogue is classified under a term the reader was never given a definition for.

**2. Mixing of prEN 50742 "Approach A" and "Approach B" content is never explained in the main text.**
grundlagen.tex frames Approach A (SRSL-based) and Approach B (IEC 62443-based) as **alternative, mutually exclusive conformity paths** a manufacturer chooses between. Yet the derivation in vorgehen.tex pulls SRSL-graded clauses (an Approach A instrument, e.g. RQ-005 → §7.4.3.4.1 SRSL1–SRSL3, RQ-011 → §7.4.3.3.1 SRSL-graded authorization) and maps them directly onto IEC 62443-4-2 CRs (the Approach B instrument). The only explanation for why this is legitimate is a caption footnote buried in anhang.tex ("Sections 4, 5, 7 ... are the only parts of the source text providing clause-level content"). A reader relying on vorgehen.tex's main narrative alone cannot tell whether the thesis assumes Approach A or B for the case-study gateway, or why content from both is merged into one requirement chain. This is a reproducibility/rigor gap that belongs in the methodology chapter itself, not only in an appendix caption.

**3. Target SL-C level is never stated, even though it is required to select CRs/REs.**
grundlagen.tex explicitly states CR/RE selection under IEC 62443-4-2 depends on the targeted Component Security Level Capability ("typically SL-C 1 or SL-C 2"). vorgehen.tex's requirement-derivation section never states which SL-C the gateway targets, yet the appendix tables select specific CRs and REs (e.g., anhang.tex "EDR 3.14" vs. the base CR) that are level-dependent. Without a stated target level, the reproducibility of the CR/RE selection cannot be assessed by a reader.

**4. A dedicated appendix artifact is never referenced.**
anhang.tex contains a whole appendix chapter ("Secure Development Lifecycle") with a custom figure (`Secure System Development Lifecycle-Main Overview.drawio`), evidently created for the exact SSDLC/DevSecOps discussion in vorgehen.tex. That subsection instead only cites generic, non-thesis-specific web sources (`ibm_ssdlc_2025`, `geeksforgeeks_ssdlc_2026`, `cloudaware_devsecops_lifecycle_2026`) and never points the reader to the appendix figure. This is a concept/artifact introduced elsewhere that is never used where it clearly belongs. (Note in passing: the figure's `\caption{}` in anhang.tex is also empty — a defect in the chapter you were confident about.)

**5. FR omission repeated in two tables.**
Per anhang.tex, RQ-002 maps to **FR2 and FR3** (CR 3.1 for communication integrity, CR 2.13 for physical diagnostic/test interfaces). But both vorgehen.tex and vorgehen.tex list "Data and Software Integrity" as **FR3 only**, silently dropping FR2. Because the same omission is duplicated in two tables, a reader cross-checking one against the other will not catch the discrepancy — only the appendix reveals it.

**6. Unexplained shift of RACI "Accountable" role across lifecycle phases.**
The vorgehen.tex makes Security Engineering accountable for Design and Execution, but Test Engineering accountable (`A/R`) for Preparation, and QA/Compliance accountable for Evidence/Evaluation. The prose (vorgehen.tex) states "Security Engineering ... holds technical accountability for test scope and execution integrity" as if this were a fixed role, but the table quietly reassigns Accountability phase-by-phase without ever explaining the rationale for the handoff. This undermines the RACI section's own stated purpose of making accountability assignment "explicit."

## C. Minor Issues

- **Terminology drift**: Appendix "Requirement Type" field uses "Data Integrity" for RQ-002/RQ-005 (anhang.tex, anhang.tex), while vorgehen.tex's category of the same name is "Data **and Software** Integrity" (vorgehen.tex). Harmless once cross-referenced, but avoidable friction for a careful reader.
- **Unused mapping category**: vorgehen.tex defines four prEN 50742 mapping types — Direct, Partial, Indirect, Not identified (vorgehen.tex) — but the Appendix table never actually uses "Indirect" for any of the 14 requirements. Either drop the category or note why it exists as a theoretical placeholder.
- **RQ-014's stated Security Objective ("Confidentiality", anhang.tex) sits awkwardly next to its actual FR mapping (FR3/FR6 — System Integrity / Timely Response, anhang.tex)**, rather than FR4 (Data Confidentiality) or FR2 (Use Control), which would more naturally match "restrict access". Worth one clarifying sentence.
- **Unjustified decomposition criteria**: the four requirement-derivation criteria (Traceability, Atomicity, Verifiability, Product relevance, vorgehen.tex) appear to be author-defined with no citation and no discussion of validation (e.g., inter-rater check, alternative decompositions considered). Not wrong, but weak on academic rigor as currently presented.
- Minor style: "I\textbf{EC 62443-4-1}" typo in grundlagen.tex (stray "I" before the bold) — flagged only because it sits next to content vorgehen.tex heavily depends on.

## D. Detailed Chapter Review of vorgehen.tex

- **§ Derivation of Security Requirements** (vorgehen.tex): Strongest section. The three-stage chain (MVO → prEN 50742 → IEC 62443-4-2) is logically presented, the "none of the three sources is independently sufficient" argument is well justified, and the numeric summary (5/7/2 split) is verified correct against the appendix. Weakness: Approach A/B blending (Major #2) and missing SL-C target (Major #3) are not addressed here, even though this is exactly where they belong.
- **§ Functional Security Testing Framework Architecture / Scope and Boundaries** (vorgehen.tex): Correctly and accurately back-references `sec:security_testing_approaches` and `subsec:vulnerabilities_fuzzing_pentesting`, both of which do exist in grundlagen.tex (I initially suspected these were dangling forward references — confirmed on a fuller re-read that they are not; this part of the chapter is sound).
- **§ Traceability Model** (vorgehen.tex): Clear, well-structured seven-node chain; correctly ties back to TARA (`subsec:tara`) and forward to Chapter 4. No issues.
- **§ Functional Security Test Classification** (vorgehen.tex): The justification for rejecting a pure FR-partitioned taxonomy is a genuine highlight — it explicitly reasons from Table req_categories's own data. The FR2 omission (Major #5) is the only defect.
- **§ Verification Lifecycle and Governance** (vorgehen.tex): Good linkage to IEC 62443-4-1 Practice 5 / SVV-1. RACI accountability shift (Major #6) and the orphaned appendix figure (Major #4) are the issues here.
- **§ Evaluation Metrics and Assessment Scheme** (vorgehen.tex): Rigorously defined ratio metrics ($C_{map}$, $C_{exec}$, $C_{fulfil}$, $T_{fwd}$, $T_{bwd}$, $EC$, $TDEC$, $R$, $MVC$), each with a clear denominator convention and honest scope caveats (e.g., repeatability explicitly limited to "same laboratory, same tester"). This is the most academically rigorous part of the chapter.

## E. Specific Passages to Revise

1. vorgehen.tex — *"Each requirement was classified by the security objective it primarily expresses, corresponding to the security goals ... introduced in Sections~\ref{subsec:security_goals}..."* → Either add "Accountability" as a formally defined extension of the CIA triad in `grundlagen.tex §Security Goals` (alongside Authenticity/Utility), or rephrase to "...corresponding to the security goals introduced in Section~\ref{subsec:security_goals} and the accountability-related property of Non-repudiation."

2. Derivation-chain intro, vorgehen.tex — add one or two sentences: "The derivation draws on prEN 50742 content irrespective of whether it originates from an Approach A– or Approach B–specific clause; Sections 4, 5, and 7 of the standard apply regardless of the chosen conformity path, while Section 6/8 content is Approach B–specific (Appendix~\ref{app:sec:mapping_pren50742})." This moves the currently appendix-only clarification into the main text where the reader needs it.

3. vorgehen.tex (just before Table req_categories) — state the assumed SL-C target, e.g. "The derivation assumes a target Component Security Level Capability of SL-C 1/2, consistent with prEN 50742's typical range for machinery components (Section~\ref{subsec:pren_50742})."

4. vorgehen.tex and vorgehen.tex — change "FR3" to "FR2, FR3" for the "Data and Software Integrity" row in both tables.

5. vorgehen.tex — add one sentence explaining why Accountability shifts across phases in Table raci_matrix_verification, e.g. "Accountability shifts from Security Engineering in the Design and Execution phases to Test Engineering during Preparation, reflecting that test-bed configuration is an operational task delegated to the executing team, and to Quality/Compliance Management during Evidence/Evaluation, reflecting its ownership of release-readiness sign-off."

6. vorgehen.tex — insert a reference to `\ref{fig:secure-system-development-lifecycle-main-overview}` / `\ref{app:SecureDevelopmentLifecycle}` where SSDLC/DevSecOps models are discussed.

## F. Ratings

| Dimension | Rating (1–10) | Justification |
|---|---|---|
| Internal consistency | 7 | Numeric derivations (5/7/2 split, FR unions per category) verify correctly against the appendix in almost every case; the FR2 omission and Accountability/FR mismatch are the exceptions. |
| Alignment with other chapters | 6 | Terminology and asset/threat concepts align well overall (STRIDE, TARA, FRs, asset classes), but "Accountability" is used without foundation, and the Approach A/B relationship is never reconciled in the main text. |
| Methodological clarity | 7 | Traceability chain, test taxonomy rationale, and evaluation metrics are unusually well designed and clearly written; gaps are the unexplained SL-C target and Approach A/B blending. |
| Academic quality | 6.5 | Strong quantitative rigor in the evaluation-metrics section; weaker on justifying the requirement-decomposition criteria and on making the RACI/appendix-figure connections explicit. |

**Caveat on tooling**: a naive `Get-Content | Measure-Object -Line` under-reported the true line counts of these three files (e.g., 308 vs. actual 438 for grundlagen.tex), which initially made me suspect the chapter was truncated. Re-reading with `-Raw` and splitting on `` `n `` gave correct counts, and all files turned out complete — worth knowing if you script anything against these files' line counts.




------------------------------------------------

