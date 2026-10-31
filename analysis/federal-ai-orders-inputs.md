# Do federal judges' AI orders say anything about what lawyers put into AI? Result of a pre-registered count

Graded 31 October 2026 against the [pre-registration](federal-ai-orders-inputs-prereg.md) published on 30 October 2026, before the fetch job ran (it ran 31 October 2026, 01:11-01:22 UTC). By MV2 of Munim, Inc. (mv2@munimtech.com); this analysis was made with AI agents working in his name. Text CC BY 4.0. It describes public documents. It is not legal advice.

Coded data: [data/federal_orders_inputs.json](../data/federal_orders_inputs.json) (CC BY 4.0). Sample source: [legalrealist/AI-orders-explorer](https://github.com/legalrealist/AI-orders-explorer) (MIT), `data/processed/explorer_data.json` at commit `c70cdc1e43813849fa99d3cf6e3c3ac6aed602b4` (SHA-256 `b3db3509...995f3`, 929 entries).

## Result in one paragraph

Of 62 federal AI orders whose text could be read, 5 (8.1%) impose a duty about what may be put into an AI tool: three Court of International Trade judges' orders, the Western District of Oklahoma bankruptcy court's General Order 23-01, and Magistrate Judge Couvillier's standing order in the District of Nevada. About 87% impose an output duty (check what the tool produced). All 5 input-duty orders also require disclosure of AI use. P1, P2 and P3 held; **P4 failed**: one order, Judge Couvillier's, does draw a line between kinds of AI system, but on a different axis from the state courts' rules. It bans uploading sealed filings to an "open AI system", defined by whether the "source code, learning materials, and underlying models" are publicly accessible, not by who controls the data.

## Sample, and what the audit changed

| Step | Count |
|---|---|
| Explorer entries | 929 (754 judicial opinions, 108 standing orders, 35 administrative orders, 28 local rules, 4 practice directions) |
| Non-opinion entries classed federal by the job's fixed rule | 102 |
| Audit of the court list: state courts wrongly classed federal ("11th Jud. Cir.", "17th Jud. Cir." x2, "18th Jud. Cir.": Florida and Illinois circuit courts) | -4 (all four were readable) |
| No readable text (no PDF or federal link 14, HTTP 403/404 3, image-only PDF 4, 133 characters 1) | -22 |
| Same file listed twice (same SHA-256) | -9 |
| Fetched page is not the order (two judges' index pages and a court home page; one scheduling order whose AI pages are images) | -4 |
| Same order fetched from two copies with different hashes (Judge Hudson's Pretrial Schedule A in *Kelly v. Altria*, E.D. Va.) | -1 |
| **Unique federal orders with readable AI text** | **62** |

Deviations from the pre-registration, all found by reading and all reported here: the four state-court entries and the four non-order pages are left out of every share, and the two copies of the Hudson order count once. The pre-registration said every document with an input-term hit would be read in full. Many hits were in long chambers rules or local rules (up to 260,000 characters) and were about sealing motions or protective orders in general. In practice, every AI section was read in full, and so was every input-term hit within 1,500 characters of a mention of AI. The 22 documents with no readable text are listed in the data file's notes; the CIT, W.D. Okla. and D. Nev. orders all had text.

## P1: at most 10% impose an input duty. HELD (5 of 62, 8.1%)

| Explorer id | Court and judge | Date | Input duty (quoted) |
|---|---|---|---|
| 722 | Ct. Int'l Trade, Judge Stephen Alexander Vaden | 8 June 2023 | A filing drafted with generative AI must come with "A certification that the use of such program has not resulted in the disclosure of any confidential or business proprietary information to any unauthorized party". |
| 643 | Ct. Int'l Trade, Judge Claire R. Kelly | dated 24 July 2025 | Same certification as Judge Vaden's. |
| 644 | Ct. Int'l Trade, Judge Jane A. Restani | dated 24 July 2025 | Same certification as Judge Vaden's. |
| 710 | Bankr. W.D. Okla., General Order 23-01 (Chief Judge Sarah A. Hall) | effective 1 September 2023 | An attestation "certifying the use of such program has not resulted in the disclosure of any confidential information to any unauthorized party". |
| 265 | D. Nev., Magistrate Judge Maximiliano D. Couvillier III, First Amended Standing Order | effective 5 January 2026 | "Counsel and parties are prohibited from uploading onto any open AI system - where the source code, learning materials, and underling models maybe publicly accessible - any filed documents which: (a) have been filed under seal; or (b) contain personal-data identifiers listed in LR IC 6-1(a)(1)-(6). Violation may result in sanctions." (as printed) |

Coded **not** input duty, with the reason:

- **Pointer plus prompt records** (id 489, N.D. Cal., Magistrate Judge Peter H. Kang, 16 July 2025): counsel using AI "shall fully comply with any applicable protective order and all applicable ethical/legal obligations (including issues relating to privilege) in their use, disclosure to, submission to, or other interaction with any such AI tools", and must keep records "such as by keeping records of all prompts or inquiries submitted to any such third-party AI tools". The limit on what goes in is the existing protective order.
- **Caution** (id 579, M.D. Pa., Magistrate Judge Phillip Caraballo): "All parties and counsel are cautioned to verify any facts or legal citations prepared through generative AI, and to safeguard against the disclosure of confidential information."
- **Pointer** (id 458, N.D. Cal., Judge Trina L. Thompson): cites ABA Resolution 604 "including maintaining client confidentiality".
- **Prompt records only** (id 694, N.D. Cal., Judge Araceli Martínez-Olguín): counsel keeps "records of all prompts or inquiries submitted to any generative AI tools"; nothing on what may be entered.
- **Risk named, no duty** (id 508, M.D. Pa., Magistrate Judge Leo A. Latella): the preamble names the risk that a tool "may disclose confidential information in the public sphere"; the operative duties are disclosure and accuracy.
- **Prohibition** (id 688, N.D. Ohio, Judge Christopher A. Boyko, 19 December 2023): "no attorney for a party, or a pro se party, may use Artificial Intelligence ("AI") in the preparation of any filing", excluding Westlaw, LexisNexis, Google and Bing. Left out of the primary count, as pre-registered.
- **Research certification** (id 576, E.D. Va., Judge Robert E. Payne): filers certify that no AI was used for research apart from AI built into Westlaw, Lexis, FastCase and Bloomberg. It is a partial prohibition, not an input rule.

Sensitivity: counting the ban, 6 of 62 (9.7%), and P1 still holds. Counting the Kang and Caraballo orders as well, 8 of 62 (12.9%), and P1 would fail. **P1 held under the pre-registered coding, but only narrowly**: counting the two softer orders as input duties would put the share above 10%.

## P2: at least 70% impose an output duty. HELD (about 87%)

The fixed pattern codes 55 of 62 (88.7%) as having an output duty. The random audit (seed 20261030; 30 drawn, 25 left after removing 3 state entries, 1 non-order page and 1 duplicate) agreed on the output code in 24 of 25 documents. The one miss was N.D. Tex. Local Criminal Rule 47.2(e), which requires disclosure only, so the pattern over-counted. Correcting it gives 54 of 62 (87.1%).

The disclosure pattern was weaker: it agreed in 19 of 25. All 6 misses were over-counts: orders where the word "disclose" appears elsewhere in the document, a certificate that lets the filer attest "either" no AI use "or" human checking, or a page saying the judge no longer requires a certification. Treat the automatic disclosure count (46 of 62) as an upper bound. Based on the audit, roughly half of the orders require disclosure.

## P3: at least 75% of input-duty orders also require disclosure. HELD (5 of 5)

All three CIT orders and the W.D. Okla. order require a notice that names the program and the portions it drafted. The Nevada order requires every filing to certify that AI "was [used / not used]".

## P4: no order distinguishes public from privately hosted models. FAILED (1 of 62)

Judge Couvillier's order distinguishes "closed AI system v. open AI system". It encourages protective orders to set out which kind is permissible, and it bans uploading sealed filings or filings with personal-data identifiers to an "open AI system - where the source code, learning materials, and underling models maybe publicly accessible". No other order in the sample draws a line between kinds of system. Judge Kang's order describes "publicly available AI tools" run by third parties that "may have access to, ownership of, or otherwise retain information input", but its rule applies to every AI tool alike.

## The unexpected finding: the Nevada line runs on a different axis from the state courts' lines

The state court instruments that MV2's [bar-ai-guidance](https://github.com/munimtechnologies/bar-ai-guidance) index has read all decide which AI systems are safe for confidential court data by **who controls the data**:

- **California Rule of Court 10.430(a)(4)** (court staff and judicial officers): a "public" generative AI system is one "that allows anyone other than court staff or judicial officers to access the data" or "to use that data to train AI systems"; it "does not include any system that the court creates or manages".
- **Arkansas Administrative Order No. 25 §1(b)** (2025 Ark. 220): a public LLM "is accessible to anyone and usually hosted by a third party"; a private LLM "is deployed and controlled by an organization and operated on its own infrastructure or cloud account".
- **New York Unified Court System Interim Policy (October 2025)**: "A private model is a model that is under UCS control and does not share data with any public LLM."

The Nevada order instead asks whether the system's **source code, learning materials or models are publicly accessible**. Read literally, the two tests can give opposite answers:

- An open-weight model running on a firm's own server, with no data leaving it, is "private" under Arkansas's and New York's tests. But its "underlying models" are publicly accessible, so the Nevada text would seem to call it an "open AI system".
- A proprietary model offered as a hosted service is "public" under the Arkansas test (hosted by a third party and accessible to anyone). Under the Nevada text it is not "open", because its code and model are not public.

A stipulated protective order in the same district, as quoted by the eDiscovery LLC blog ([*RMME LLC v. Majestic Steel USA, Inc.*, D. Nev. 24 June 2026](https://www.ediscoveryllc.com/another-a-i-protective-order/); not read at the source for this note), adopts the same split. It defines a closed AI system as "any AI system that is not an open AI system" that also has safeguards and does not train on the material. On those words, a self-hosted open-weight deployment cannot be "closed".

No court is known to have applied either text to a self-hosted open-weight model. Judge Couvillier's order may well be read by its purpose (keeping sealed material away from systems that expose it) rather than by its wording. The point here is narrower: **the definitions differ, and an office that runs its own model and appears before that judge cannot rely on the state courts' "who controls the data" test to answer the Nevada question.** We found no commentary that notices this difference (searched 31 October 2026: the Ropes & Gray tracker, legalaigovernance.com, the eDiscovery LLC and Cimplifi posts on AI protective orders).

## Why this count is new

The public trackers (Ropes & Gray, RAILS, LegalRealist's explorer) code disclosure, certification, verification and prohibition. None codes input duties, and none compares the definitions of "public", "open" or "private" AI systems across federal and state instruments. Single orders such as Judge Vaden's and Judge Couvillier's are well known. What is new here is the count of input duties across a fixed federal sample, from primary text with quotations, and the side-by-side reading of the definitions.

## Limits

- The sample is what two trackers caught; the RAILS half stops in May 2025, and federal orders they missed are not counted.
- 22 of 98 federal entries had no readable text, and 4 more fetched pages were not the order. If any of those contain input duties, the 8.1% would rise.
- The explorer's dates for some entries differ from the dates printed on the orders (the Kelly and Restani orders are listed as March 2024 but are dated 24 July 2025), so the table uses dates as printed where the text shows one.
- One team of AI agents coded the documents. Every input-duty call is quoted, so anyone can check it.
- Orders that say nothing about input do not leave lawyers free: Rule 1.6, protective orders and the bar opinions still apply.
- This note describes what the documents say. Whether any particular tool or setup complies with any order is a question for the lawyer and the court.
