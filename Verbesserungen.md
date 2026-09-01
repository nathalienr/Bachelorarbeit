
Part 1 — Review & Refinement
1.1 Direct answers to your inline comments

① TC‑RQ002‑04 —"Überprüfen, ob das Sinn macht (wie kommt man auf: Authentication nachweisen)" Your instinct is correct — the wording was slightly misleading. This test does not "prove authentication." It demonstrates the absence of forgery resistance, i.e. that the parameter checksums are an error-detection mechanism, not a cryptographic authenticity mechanism. Re-word the objective to:

"Establish by keyspace/analytical argument that the parameter integrity values provide no forgery resistance, and therefore cannot serve as an authenticity control (they are error-detection only)." Keep it SVV‑3 / analytical. The logical chain is: 16‑bit F_ParCRC → 2¹⁶ = 65 536 candidates (brute-forceable in milliseconds); 32‑bit iParCRC → deterministically recomputable from the public GSD layout + certified CRC-tool algorithm → neither depends on a secret → by definition not authentication. You never "test for authentication"; you show its structural impossibility.

② TC‑RQ002‑05 —"Gibt es einen Beleg für 'runtime change'?" Yes, and it is well-supported — including by your own setup document, which states:"Adresse wird nur beim Boot/Init gelesen – Änderung im laufenden Betrieb wird erst nach Neustart wirksam." Device sources: the rotary switch / F‑address is read only at initialisation (SRIO‑8803, SRIO‑10812), and the value range 1–899 / 999 = update-mode is defined in SRIO‑2013. Cite these three together; the "runtime change ignored" claim is documentary, not inferred.

③ TC‑RQ003‑05 —"Gibt es einen Beleg dafür?" (development-only / production_fuse) Yes. The interface is declared development-only — SRIO‑2580 (debug/flash interface "only usable during the development phase") and SRIO‑1526 (test/FIT interface, same wording). The production gating is the production_fuse flag in the Com‑Spec §5.3.1 legend —"(P) Only in production mode (production_fuse not set)" — and the FIT service /fit/setfit is WO (P) (SRIO‑17130/17129). Keep the explicit limitation you already added: a silicon fuse is not verifiable without invasive PA‑4 analysis; only the functional gate is tested.

④ TC‑RQ004‑02 —"Ist das notwendig? (IEC 62443‑3‑3 SR 7.8 …)" — important standards correction Excellent catch, and it changes the framing. You are right: CR 7.8 / SR 7.8 is modest — it asks for a component inventory that may include component ID, capability and version, kept consistent with the system under a configuration-management process. It does not mandate a third-party SBOM with CVE correlation. Therefore:

Correction: The SBOM/CVE-completeness finding must not be scored as a CR 7.8 FAIL. CR 7.8 is met at product/top-level granularity (the device does expose ID + version).
The deeper SBOM + CVE expectation derives from IEC 62443‑4‑1 SM‑9/SM‑10 (secure development / third-party component management) and the CRA / BSI TR‑03183‑2, not from CR 7.8.
Re-map TC‑RQ004‑02 and TC‑RQ006‑02 traceability from CR 7.8 to 62443‑4‑1 SM‑9/SM‑10 (+ CRA/TR‑03183‑2), and re-label the verdict as an SDL/CRA shortfall, not a CR 7.8 conformance failure. This makes the test defensible and answers "ist das notwendig?": it is necessary for the 4‑1/CRA dimension, but it is not a CR 7.8 requirement.

⑤ TC‑RQ007‑04 —"Wie kommt man darauf? Quelle?" (availability inversion) Sources: IoT‑Core / HTTP is served exclusively by the non-safety COM (CPU3, QM); the safety function runs independently on the SCPU via the black channel. A COM fault or SysCom timeout (SRIO‑21357, diagnostic on loss of SCPU↔COM link; SRIO‑10250) removes the IoT identification path while the SCPU safety loop persists. This is independently corroborated by the manufacturer's EMC Criterion A/B, which explicitly lists IoT‑Core as*"Not supervised … After the tests: IoT‑Core access possible"* (SRIO‑11573/11572) while the safety I/O must remain controlled. Hence identification is structurally less available than the safety function it describes. Cite SRIO‑21357 + SRIO‑11573/11572.

⑥ RQ‑009 G‑3 — your note:"it is currently being deleted just like the error log" Applied, and it has a knock-on correction. If REVISION_COUNTER (I&M0) is cleared on cold start like the error log, then:

RQ‑009 G‑3 is re-written as a NOTE, not an asymmetry:"In the current implementation the parameter-change counter is volatile — cleared on cold start like the error log — so there is no durable audit asymmetry; both the counter and the log detail are lost. TC‑RQ009‑02 confirms this empirically."
RQ‑013 mitigation must be corrected: the bullet*"Remanent audit state exists (REVISION_COUNTER)"* is now false and must be replaced. The valid example that the device can hold remanent state is I&M1/I&M2/I&M3, which are documented as stored*"powercycle proof"* (SRIO‑7767 / SRIO‑7764 / SRIO‑7761). So the "version history is a design omission, not a capability limit" argument still holds — just anchored on I&M1/2/3, not on the counter.
TC‑RQ009‑02 expected result flips: expect the counter to be cleared on cold start (not retained). The test stays valid (it "verifies, not pre-asserts"), only the expected outcome changes.

⑦ TC‑RQ013‑03 —"Referenz zu TC‑RQ003‑04 möglich?" Yes. The time-attribution method (no RTC; uptime = 4‑byte second count SRIO‑15218, cleared on cold start SRIO‑15398; /systemtime/systick returns uptime in ms SRIO‑19921) is identical. Set TC‑RQ013‑03 Steps to*"Execute per the TC‑RQ003‑04 method around a firmware upload; record against RQ‑013,"* and add the ⇄ TC‑RQ003‑04 marker as you did for TC‑008‑04 and TC‑012‑04.

⑧ RQ‑014 Step 2 —"Was für mirror?" The port mirror (SPAN) on your managed switch — Setup A. Per your setup doc, switch Port 5 is the mirror destination, with Port 1 (PLC) and Port 2 (SRIO) mirrored both directions, and the passive Kali‑Pi (no test-net IP, promisc on) attached there for capture only. Re-word the Step‑2 justification to*"passively capture the log read on the switch SPAN/mirror port (Setup A)"* so the term is unambiguous.

1.2 Two corrections you should apply that you did not flag (MITRE IDs)

Your revised text still carries invalid ATT&CK‑for‑ICS identifiers — these will not survive examiner scrutiny:

Location	In your draft	Correct ICS techniqueRQ‑001 Test 3	T0842/1692.002	T0856 (Spoof Reporting Message) + T0836 (Modify Parameter). T0842 = Network Sniffing — that is passive, not injection.
RQ‑005 Test 3	T1693.001	T0857 (System Firmware) + T0843 (Program Download); optionally T0873 (Project File Infection). T1693.001 is not a valid ICS ID.

The IDs you used elsewhere (T0814 DoS, T0830 AiTM, T0836 Modify Parameter, T0872 Indicator Removal, T0843 Program Download) are valid — please just verify each against the current ATT&CK for ICS matrix before submission.

Everything else in your Step‑1/Step‑2 revisions is sound and internally consistent. The three-bucket structure, the demotion of confidentiality findings (except RQ‑014), and the cross-reference reuse are all correctly carried through.
---

