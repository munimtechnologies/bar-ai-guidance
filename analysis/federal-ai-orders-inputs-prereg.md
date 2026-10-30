# Do federal judges' AI orders say anything about what lawyers put into AI? A pre-registered count

Pre-registered 30 October 2026, before any order text in the sample was read (the job that fetches the texts was written together with this file). By MV2 of Munim, Inc. (mv2@munimtech.com); this analysis was made with AI agents working in his name. Text CC BY 4.0. It describes public documents. It is not legal advice.

## Why

MV2's earlier check ([pre-registration](court-rules-inputs-vs-outputs-prereg.md), [result](court-rules-inputs-vs-outputs.md)) found that every binding state court rule on AI adopted in 2026 governs what comes out of an AI tool (verification of citations and authorities), and none governs what a lawyer may put into it. Its Limits section said the federal standing orders were not covered and that some of them address confidentiality. This check counts them.

The two sides are the same as before:

- **Output**: checking what the tool produces before it is filed.
- **Input**: what client or case information may be typed or uploaded into the tool at all (confidential, proprietary, sealed, privileged or personal information).

## Prior art (searched 30 October 2026)

- The public trackers sort AI court orders by disclosure, certification, verification and prohibition: Ropes & Gray's AI Court Order Tracker, Duke's RAILS AI in Courts Tracker (current through May 2025) and LegalRealist's AI-orders-explorer, which merges the two (643 entries; requirement keys such as `disclose`, `certify_all`, `verify`, `prohibited`). None of them has a field for input or confidentiality duties.
- Bloomberg Law's paywalled comparison table of federal standing orders (to 30 January 2024) labels a few orders "Confidentiality"; the best-known examples are Judge Stephen Vaden's order at the Court of International Trade (certify that AI use did not disclose confidential or business proprietary information) and the Western District of Oklahoma bankruptcy judges' order that adopts it.
- No public count found of how many federal AI orders impose an input duty, nor of whether any distinguishes public AI services from privately hosted or self-hosted models (as Arkansas's adopted Administrative Order No. 25 now does for court staff).

## Sample (fixed before reading)

- Source: `data/processed/explorer_data.json` of [legalrealist/AI-orders-explorer](https://github.com/legalrealist/AI-orders-explorer) (MIT), at the commit current when the fetch job runs; the commit and the file's SHA-256 are recorded.
- Included: every entry whose `type` is not `Judicial Opinion` (standing orders, local and general rules, guidelines; case decisions are left out) and whose `court` names a federal court, by a fixed rule in the job's code (district, bankruptcy, circuit, Court of International Trade, Court of Federal Claims). The full list of court strings and how each was classed is published for audit.
- Text: the entry's self-hosted PDF where there is one, otherwise its `link` if that is a PDF or a uscourts.gov or govinfo.gov page. An entry with no readable text is reported and left out of the shares.
- Unit: one unique document (by SHA-256 of the fetched file); a document listed twice counts once.

## Coding

- **Input duty**: the order itself imposes a duty or a prohibition about what information may be entered into or disclosed to an AI tool, or requires a certification about it (for example that AI use did not disclose confidential information). A sentence saying only that existing confidentiality rules still apply is coded **pointer**, not input duty. An order that bans AI use altogether is coded **prohibition**; it is left out of the input-duty count (primary) and reported as included too (sensitivity).
- How: every document is screened by a fixed list of terms (confidential, proprietary, sealed, protective order, privileged, personal or personally identifying, trade secret, non-public, client information, upload, input, retain, train); every document with a hit is read in full and coded with a quotation. Documents with no hit are coded "no input duty".
- **Output duty** (verify, check accuracy, no fabricated or fictitious authority, or certify that a person checked) and **disclosure** of AI use: coded by fixed patterns in the job's code, then a random audit of 30 documents (seed 20261030) is read in full; the agreement is reported.
- **Model line**: whether the order treats public or third-party AI services differently from privately hosted, enterprise, closed or self-hosted models; screened by fixed terms, every hit read.

## Predictions

1. **P1**: at most 10% of the readable documents impose an input duty.
2. **P2**: at least 70% impose an output duty.
3. **P3**: at least 75% of the documents with an input duty also require disclosure of AI use (the Vaden pattern: disclose, then certify nothing confidential went out).
4. **P4**: no document draws a line between public AI services and privately hosted or self-hosted models.

Each prediction will be graded as held or failed, with counts, and anything unexpected reported as found.

## Limits

- The sample is what two trackers caught; orders they missed are not counted, and the RAILS half stops in May 2025.
- Federal courts only. State and local judges' orders are a separate question.
- The coder is one team of AI agents working from the text, with quotations for every input-duty call so anyone can check them.
- An order that says nothing about input does not leave lawyers free: Rule 1.6, protective orders and the bar opinions still apply.
