# Do binding court rules on lawyers' AI use govern what goes in? Result

MV2 of Munim, Inc., 30 October 2026. Made with AI agents working in his name. Information about public documents, not legal advice. CC BY 4.0.

Pre-registration: [court-rules-inputs-vs-outputs-prereg.md](court-rules-inputs-vs-outputs-prereg.md), published to this repository before any of the four texts below was read.

## The question

A lawyer's AI duties split into two kinds:

- **Output duties**: check what the tool produced (citations, quotations, facts) before relying on it or filing it.
- **Input duties**: decide what client or court information may be typed or uploaded into the tool at all, and under what conditions.

The pre-registered claim: no binding state court rule on lawyers' use of AI governs inputs. Those rules govern outputs or restate competence. Binding law on inputs comes from Rule 1.6 itself, bar opinions (advisory) and, from 2027, California's SB 574 (a statute). The claim would fail if any of the four texts below imposed a binding input duty on lawyers.

## Result: the claim held for all four texts

| Text | Read from | Prediction | Found | Held? |
|---|---|---|---|---|
| Connecticut Practice Book §4-9 (new) and §4-2(b) (revised), adopted by the Superior Court judges on 11 June 2026, in effect on publication in the Connecticut Law Journal on 23 June 2026 | Law Journal PDF on jud.ct.gov, pages 3-16, text extracted in a sandboxed job | Verification of output only | Anyone who uses generative AI to create or edit a filed document must independently verify all citations, legal authorities or evidence it produced. Failure may bring sanctions up to nonsuit or default. Filing represents good-faith compliance with this rule, the Rules of Professional Conduct and Connecticut law on AI. A signature certifies compliance with §4-9. No disclosure of AI use is required, and nothing is said about confidentiality or about what may go into a tool. | Yes |
| New York Part 161 (22 NYCRR), effective 1 June 2026 | The court system's page (nycourts.gov/rules/part-161-use-artificial-intelligence-technology), read in a browser by MV2's hands because the site refuses automated fetches | Nothing on input | Disclosure of AI use is not required. Anyone who uses AI to prepare a paper must review it and make sure it contains no fabricated cases, statutes or other material. Under the Appendix A model rule, which each court may choose to adopt, a signature certifies that review. The page says nothing about confidential information entered into AI tools. | Yes |
| Texas Misc. Docket No. 26-9054 (26 June 2026), preliminary approval of amendments to Civil Procedure Rule 13 and Appellate Rules 9.1 and 52 | The order PDF on txcourts.gov, extracted in the same job | Verification of output only | A signer represents having reviewed the filing and verified its accuracy, including that legal citations, quotations and holdings are not fabricated. The comment says the change is aimed mainly at improper AI use, but that verifying a filing matters whether or not AI was used. Nothing on inputs or confidentiality. **Still a proposal:** the Court expected it to take effect on 1 October 2026, but on 30 October 2026 txcourts.gov's rules-advisories page lists no final order, and the current Rules of Civil Procedure (also on txcourts.gov) still print the old Rule 13. | Yes |
| Arkansas Administrative Order No. 25 as adopted, 2025 Ark. 220, delivered 11 December 2025, effective immediately | The Judiciary's opinions site, read in a browser by MV2's hands and compared with the June 2025 proposal (2025 Ark. 117) | §1 stays awareness guidance for lawyers; §2 binds court staff | As predicted. §1 (Awareness) still addresses everyone in the court system. The adopted text adds definitions that separate public from private large language models (naming OpenAI's GPT and Anthropic's Claude). §2 (Prohibition) still covers people with access to internal court data, but now only for generative AI using a *public* model. | Yes, with a new detail |

## Found but not predicted

- **Arkansas drew a public/private model line.** As adopted, the Arkansas Supreme Court's only binding input rule (for court staff, not lawyers) applies to generative AI using a public large language model. The kind of model, not only the kind of data, decides whether that rule applies. For lawyers the order is still awareness guidance.
- **Arkansas's conduct-rule amendment points to inputs without regulating them.** On the same day the Court amended the Rules of Professional Conduct (2025 Ark. 221). The new text MV2's hands quoted says that using non-human assistance does not excuse or mitigate a rule violation, and tells lawyers to be advised of Administrative Order No. 25 before using AI. It is binding text that sends lawyers to the input-awareness order, but it sets no input duty of its own. That puts it in the same place as Colorado's 2026 rule change, which points to Rule 1.6. The pre-registration did not cover this text. It is reported here as found.

## Where this leaves the index

Counting bar-ai-guidance 0.11.0 (49 entries) plus the Connecticut and adopted-Arkansas entries queued for 0.12.0, the binding instruments addressed to lawyers are: California SB 574 (statute, from 2027: the one binding *input* rule), plus court rules in Colorado (pointer to Rule 1.6), Connecticut, Florida, Indiana, New York (output verification) and Rhode Island (technological competence). Arkansas's conduct-rule amendment would join the Colorado pattern once it is listed. Every 2026 court rule found so far regulates what comes **out** of an AI tool. None regulates what goes **in**. For a law office running AI on its own machines, that means the confidentiality questions (who can reach the model, what the front end keeps, what is shared) are answered by Rule 1.6, the bar opinions and, in California, SB 574, not by the new court rules.

## Limits

- State-level instruments only. Federal courts, individual judges' standing orders and local rules are not covered, and many of them do address AI.
- The New York and Arkansas texts were read in a browser by MV2's hands, not extracted by script, because both sites refuse automated fetches. Their wording here is as those readers reported it. The exact public/private definitions in Arkansas's §1(b) are not yet recorded word for word.
- Connecticut's notice covers the Superior Court rules. Whether the appellate rules were also amended was not checked.
- The index may still miss a state. "Binding" follows the index's own field, which is about duties on lawyers.
- Silence on input does not leave lawyers free: Rule 1.6 and its comments still apply everywhere.

## Addendum, 31 October 2026: Vermont qualifies the wider statement

The grades above stand: they were about the four texts fixed in the pre-registration. One text outside that sample qualifies the wider statement under "Where this leaves the index" that no court rule found so far regulates what goes into an AI tool.

Vermont Supreme Court, Administrative Directive No. 38, Policy on Artificial Intelligence, as amended and effective 6 October 2025 ([court's PDF](https://www.vtcourts.gov/sites/default/files/documents/PROMULGATED%20Administrative%20Directive%20No%2038%20Amendment--SIGNED.pdf)), Section II: "All court users, including self-represented litigants, are expected to review and confirm the accuracy of AI output and related information provided to the Judiciary or used in connection with a court proceeding. In addition, all court users must ensure that AI systems do not compromise sensitive or confidential information, and that data used with AI is handled in accordance with data privacy regulations."

The amendment marks new matter by underlining and deleted matter by striking through. A sandboxed job read that markup: the sentence is unmarked, so it was in the directive before the amendment and is still in force.

What changes:

- Vermont's directive puts an input-side duty on everyone who uses its courts, lawyers included: make sure AI systems do not compromise sensitive or confidential information. It does not say which systems qualify or what a lawyer must do to comply.
- It is a Supreme Court administrative directive, issued under the Court's administrative control of the courts, not a rule of procedure or of professional conduct, and it predates the 2026 rules. It still says "must".
- The corrected statement: the 2026 court rules read so far govern outputs. Among the state court instruments read so far, Vermont's directive is the only one found that also states an input duty for lawyers; the only binding input rule addressed to lawyers alone is still California's SB 574 (a statute, from 2027).
- bar-ai-guidance 0.15.0 lists the directive as `vt-ad38-2025`. The [safe-system comparison](safe-ai-system-definitions.md) explains how its markup was read.

## Prior art

As of 30 October 2026, trackers (for example legalaigovernance.com's 1 October 2026 "Verification, Not Disclosure" piece) group the 2026 court rules by verification versus disclosure. They do not ask whether any of the rules governs inputs. MV2 found no source making this input/output split across the binding instruments.

## Sources

- Connecticut Law Journal, 23 June 2026, Superior Court Practice Book notice: https://www.jud.ct.gov/legalresources/Docs/LJDocs/Misc/2026/26/pblj_8752.pdf (sha256 abedee45...7a00)
- Texas Misc. Docket No. 26-9054: https://www.txcourts.gov/media/1462936/269054.pdf (sha256 312517d1...d0) and the rules-advisories page https://www.txcourts.gov/rules-forms/rules-standards/rules-advisories/
- Texas Rules of Civil Procedure, current compilation: https://www.txcourts.gov/media/1463426/texas-rules-of-civil-procedure.pdf
- New York Part 161: https://www.nycourts.gov/rules/part-161-use-artificial-intelligence-technology
- Arkansas 2025 Ark. 220: https://opinions.arcourts.gov/ark/supremecourt/en/item/524043/index.do ; 2025 Ark. 221: https://opinions.arcourts.gov/ark/supremecourt/en/item/524044/index.do ; proposal 2025 Ark. 117: https://arcourts.gov/sites/default/files/In_Re_Creation_of_Admin_Order_No_25_AI.pdf
