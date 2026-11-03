# How AI clauses in US court protective orders treat a self-hosted open-weight model: graded results

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name.
Text and data: CC BY 4.0. Code: Apache-2.0. Court documents are public record.
**Information about public court documents, not legal advice.** Whether any order allows any particular
setup in a given case is a question for the lawyers in that case and for the court.

Pre-registration: [`ai-protective-orders-prereg.md`](ai-protective-orders-prereg.md) (P1-P4) and
[`ai-protective-orders-prereg-addendum.md`](ai-protective-orders-prereg-addendum.md) (grader, P5-P6).
Data: [`../data/ai_protective_orders.json`](../data/ai_protective_orders.json) (version 1.0.0; every call is
backed by a quotation that the grader found word for word in the court's own text).
Full grader output: [`aipo/results-1.0.0.json`](aipo/results-1.0.0.json); build check:
[`aipo/check-1.0.0.json`](aipo/check-1.0.0.json); frame: [`aipo/frame.json`](aipo/frame.json);
every coding version: [`aipo/draft/`](aipo/draft/).

## The question

Since late 2025, US courts have entered protective orders that limit how parties may put discovery
material into AI tools. Setup A, fixed in the pre-registration, is an openly published model (for
example Llama or Qwen weights) running on a server the party controls, reachable only from the party's
own network, with no outside provider, never trained on inputs, and keeping chat history on that server.
For each order we asked, under its literal words: is setup A permitted, permitted on a condition
(consent, notice, agreement or a court order), forbidden, or left unclear?

## Frame and coding

- **Frame:** the 29 posts on Michael Berman's E-Discovery LLC blog (1 Oct 2025 to 31 Oct 2026) that the
  pre-registered filter selects. A convenience frame, not a census.
- **Cases:** 51. **Codable: 44.** Refusals of a proposed AI clause: 3 (tallied apart). Not codable: 4
  (no free copy of the order's words: Campbell v. TidalHealth, Elgin v. Wells Fargo, Dunn v.
  LexisNexis; and US v. Davis, whose quoted text cannot be separated from another order's).
- 14 orders that the posts describe without quoting in full were checked at the source: 13 free PDFs
  in the RECAP archive, each pinned by sha256 (4 image-only, read by OCR; Dunn's free PDF only
  describes the clause, so Dunn stays not codable), and the Velez order, whose five provisos were
  copied from the PDF's text layer.
- "Criminal" below means the 19 codable orders in criminal cases (every "United States v." case except
  the civil United States v. The New York and Presbyterian Hospital).
- Rules R2-R13 were written while coding. Each rule that decides a call has a pre-declared opposite
  reading, and every prediction is reported under each one (sensitivity table below).

## Results

| | Prediction | Result | Count (of 44 codable) | Outcome |
|---|---|---|---|---|
| P1 | No more than 20% name self-hosting | 3 orders (Velez, ZL Technologies v. KLDiscovery, Sarris) | 6.8% | **held** |
| P2 | At least 50% use a DATA test (how the tool handles inputs) | 43 | 97.7% | **held** |
| P3 | No more than 25% use an OPENNESS test, and none of those permits setup A | 3 (RMME: unclear; Rapacon: forbidden; Hoffman: conditional) | 6.8% | **held** |
| P4 | Setup A permitted in at least 50% and forbidden in no more than 20% | permitted 18, forbidden 2 (conditional 10, unclear 14) | 40.9% / 4.5% | **failed** (permitted below 50%) |
| P5 | At least one pair of orders from different courts shares a verbatim run of 25+ words | 28 cross-court pairs; longest 45 words | | **held** |
| P6 | No more than a third of orders share a 25-word run with another order | 24 orders | 54.5% | **failed** |

Tests used (an order can use several): DATA 43, PUBLIC 29, OTHER 17, CONTRACT 15, NOTICE 9, OPENNESS 3,
BAN 2.

### Sensitivity: each contested reading reversed

| Reading | Orders changed | Permitted | Forbidden | Outcomes that change |
|---|---|---|---|---|
| Main coding | | 18 (40.9%) | 2 (4.5%) | |
| R5 provider_contract coded forbidden | 10 | 18 | 12 (27.3%) | none (P4 also fails its second half) |
| R6 public_model coded permitted | 2 | 20 (45.5%) | 2 | none |
| R8 open_use_conditions coded permitted (RMME) | 1 | 19 (43.2%) | 2 | **P3 fails** (an OPENNESS order would then permit setup A) |
| R9 provisos_not_copied coded permitted | 0 | 18 | 2 | none |
| R13 self_hosted_contract_proviso coded permitted (Velez) | 1 | 19 (43.2%) | 2 | none |
| Conditional coded forbidden | 10 | 18 | 12 (27.3%) | none |
| R4 "whether cloud-based or otherwise" counted as naming self-hosting | 17 | 18 | 2 | **P1 fails** (20 of 44, 45.5%) |
| All reading rules reversed at once | 14 | 22 (50.0%) | 12 (27.3%) | **P3 fails**; P4 still fails (forbidden above 20%) |

P2, P5 and P6 come out the same under every reading. P4 fails under every reading.

## What the numbers say

1. **Almost every order tests what happens to the data, not where the model runs.** 43 of 44 use a
   DATA test (no training on inputs, no retention, no disclosure, deletion at the end); only 3 name
   self-hosting and only 3 make openness of code or weights the test.
2. **Setup A is not clearly allowed in most orders.** Its literal words permit it in 18 of 44 (40.9%).
   It is rarely forbidden outright (2 of 44), but 14 orders leave it unclear. In 10 of those 14 the only
   route to use is a contract or representation from an outside AI provider (rule R5), and a
   self-hosted model has no provider to sign one.
3. **Criminal and civil orders differ sharply** (exploratory, not pre-registered; counted from the
   per-case coding in `results-1.0.0.json`). In the 19 codable orders from criminal cases, setup A is
   permitted in 14 (all S.D.N.Y.), conditional in 4 and unclear in 1 (Stamp). In the 25 civil orders it
   is permitted in only 4 (Stansfield v. IBM, In re ByHeart, STT WebOS v. ByteDance, James v. Cerebras),
   conditional in 6, forbidden in 2 and unclear in 13, nine of them because of a provider-contract
   test.
4. **Copying is common, not rare (P6 failed).** 24 of 44 orders share a run of 25 or more words with
   another order. Most of that is the S.D.N.Y. criminal template ("Restrictions on Use of Artificial
   Intelligence Tools to Process Disclosure Materials"), but it also crosses courts (P5 held): the
   template's "AI tool" definition and its claw-back sentence appear in US v. Hoskins (N.D. Ill.) and
   US v. Peplow (E.D. Cal.), and Peplow also carries 43 words of the civil Pujas v. BDO (S.D.N.Y.)
   clause ("enterprise-grade platform ... binding written agreement"). Two civil pairs share long
   runs within one court: Rudasill v. Swiss Re and Orechovesky v. BNY (S.D.N.Y., 191 words) and ANR
   Pipeline Co. v. B&B Metal Processing Co. and Zask v. Kohl's Corp. (E.D. Wis., 139 words). Shared wording does not show who
   copied whom.

## Reading at the source changed the coding

Posts often say an order is "the same" as another. Read at the source, several are not:
Robinson (S.D.N.Y.) lacks the duties on the government that Lockhart has; Stamp's certification rests on
what the AI provider represents, which moves setup A from permitted (as in Mora and Dygdon, which it
otherwise follows) to unclear; Sarris leaves "software that operates entirely on systems controlled by
the defense" out of its AI-tool definition, so setup A falls outside the clause (rule R12); Velez lists
"self-hosted language models" among permitted systems but its fourth proviso asks for a good-faith
belief that "the platform contractually prohibits use of the information for generalized model
training", which has no one to give it for a self-hosted model (rule R13); Fischman v. Epic (N.D. Tex.)
makes a provider contract the test (paras. 26-31).

## What is new here, and prior art

Commentators track these orders one by one (the E-Discovery LLC and EDRM series), firms publish
drafting guidance, and a September 2026 article on the AAA site ("AI Is Not a Special Case") traces
by hand how form paragraphs, including the criminal template's claw-back sentence, spread between
districts and says it is not an exhaustive catalogue. We found no prior count that codes each order's
test from a quotation of its own words, grades pre-registered predictions, or asks how the orders treat
a self-hosted open-weight model. This study adds that, plus a word-for-word measure of reuse.

## Limits, stated plainly

- **One blog's frame.** 29 posts from one commentator; orders he did not write about are missing. The
  S.D.N.Y. criminal template makes up 17 of the 44 codable orders, so pooled percentages lean towards it.
- **One coding team.** Coded by AI agents working in MV2's name, with no independent second coder.
  Every call has a quotation, so any reader can check it.
- **Literal readings only.** No court is known to have applied one of these clauses to a self-hosted
  open-weight model; "permitted" means the words allow it, not that a court has said so.
- **Text sources.** 4 orders were read by OCR (tesseract 5.5.0), and the Velez provisos were copied from
  the PDF's text layer by hand and then found once, word for word, in pypdf's extraction of the same
  PDF. Orders quoted only in posts may be partial, so P5/P6 counts are a lower bound.
- **Timing of the last coding change.** Every coding version up to 0.9.2 was on GitHub before grading.
  The final patch 1.0.0 (Fischman coded, Dunn not codable, Velez recoded under R13) was written and
  handed to the grading job before any count was computed, but its commit failed to land, so it is
  first published here with the results. It touches three cases. With Fischman and Velez both coded
  permitted and Dunn codable and permitted too, setup A would be permitted in 21 of 45 (46.7%), so P4
  fails whatever those three are coded; P1, P2, P5 and P6 do not depend on them either, and none of
  their texts contains an OPENNESS test, so P3 holds as well.

## Reproduce

`aipo/build_aipo.py` (Apache-2.0; offline tests in `aipo/test_build_aipo.py`) downloads the frozen 0.9.0
coding and the published patches, applies `aipo/patch-1.0.0.json`, re-downloads each cited RECAP PDF and
checks its pinned sha256, rebuilds each cited text (pypdf, or tesseract OCR) and checks its pinned hash,
re-reads the 29 frame posts against their content hashes, runs the grader's tests and its check of every
quotation, and only then grades with `--grade`. It refuses to grade if any check fails. The published
run (2 Nov 2026, python 3.12, pypdf 5.1.0) reported 0 problems and 0 integrity failures:

```
python -I -B -m unittest discover -v
python -I -B build_aipo.py --patches patch-1.0.0.json --manifest build_manifest.json \
    --extra-src srcextra --out out --grade
```
