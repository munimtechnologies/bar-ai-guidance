# bar-ai-guidance

A small, verified index of what US bars, courts and legislatures have told lawyers about using generative AI, with a **primary-source link for every row**. One JSON file, one test, no dependencies.

Made by MV2 of Munim, Inc., with AI agents working in his name. It is information about public documents, not legal advice or an ethics opinion.

## Why

By October 2026 more than twenty-five US jurisdictions had issued opinions, guidance, rule changes or, in California's case, a statute on lawyers' use of generative AI, and the public hallucination-case database kept by Damien Charlotin listed over 2,000 decisions. Law firm trackers summarise the guidance behind HTML pages or paywalls. Nothing small and machine-readable pointed at the **issuing bar's, court's or legislature's own page or PDF** for each document, with a record of when the link was last checked. That is what this is.

## What is in it

`data/guidance.json` holds one entry per document:

| field | meaning |
|---|---|
| `jurisdiction` | `US` for the ABA, otherwise the state code or `DC` |
| `issuer`, `title`, `number`, `date` | as the document itself states them (`YYYY-MM` when it gives no day, `YYYY` when only the year is known, with `notes` saying how) |
| `kind` | `formal_opinion`, `advisory_opinion`, `guidance`, `court_notice`, `court_policy`, `rule_amendment` or `statute` |
| `binding` | `advisory`; `court_rule` for an amendment a court adopted into its rules; `statute` for an enacted law |
| `url` | the issuer's own page or PDF, never an aggregator |
| `url_verified`, `verification` | when MV2 last checked the link, and whether the page was `fetched` and its title matched, or only `cited` (the issuer's own address, not retrieved; `notes` then say why and where the details came from) |
| `confidentiality_note` | a one-sentence paraphrase of the confidentiality point, in MV2's words |
| `in_house_tools_note` | what the document says about tools run inside the firm, if anything |

Version 0.5.0 (14 October 2026) has 38 entries from the ABA, 26 states and DC: AK, AL, AZ (Supreme Court committee best practices and State Bar guidance), CA (State Bar guidance and SB 574), CO, DC, FL, GA, HI, IL (Supreme Court policy and ARDC guide), KY, MI, MN, MO (two informal opinions), NC, NH, NJ (Supreme Court guidelines and State Bar Association task force report), NM, NY (three City Bar opinions and the State Bar Task Force report), OH, OR (two formal opinions), PA, SC, TX, VA (bar guidance and LEO 1901 on fees), WA and WV. Where MV2's tool could not extract a PDF's text, the entry's `notes` say so and say where the date and paraphrase came from; where the text was read, the notes say that too.

What changed in 0.5.0:

- **California SB 574** (Statutes of 2026, Chapter 858, signed 30 September 2026, effective 1 January 2027): the first entry of the new kind `statute`. It adds Business and Professions Code section 6068.1: no delegating the practice of law to generative AI; no confidential, personal identifying or other nonpublic information into a generative AI system unless access is limited to the attorney and authorised persons bound to confidentiality; verify AI output and every citation; disclose generative AI use to the court. The legislature's site refused MV2's automated fetch, so this entry is `cited` and its notes name the law-firm summaries the paraphrase rests on.
- **NYC Bar Formal Opinion 2026-2** (5 August 2026): AI that records, transcribes and summarises calls with people who are not clients. Consent of every participant, know how the tool stores and shares what it captures, and by default do not record.
- **Hawaiʻi**: the Chief Justice's letter of 21 January 2025 to the Hawaii State Bar Association, giving initial guidance on AI, read from the Supreme Court committee's final report (December 2025).
- **New Jersey State Bar Association** task force report (May 2024), with a sample AI use policy and questions to ask AI vendors about data access, retention, deletion and subcontractors.
- The `binding` field now has a documented value list that the test checks, and every `cited` entry must carry notes.

Known gaps, to be added as each primary link is verified:

- **MS** (Ethics Opinion 267, November 2024): the Mississippi Bar's site says formal opinions are available through its member research platform after logging in, so there is no public primary link to point at.
- **MD** (Maryland State Bar Association AI Task Force, *An Overview of Ethical Considerations for Attorney Use of Generative Artificial Intelligence Technologies*, April 2025, 7 pages): sold in the MSBA store at $29 for non-members, free to members; no public copy found.
- **RI**: the Supreme Court's Executive Orders 2024-03 and 2025-06 set up and extended a Committee on Artificial Intelligence and the Courts (progress report due 27 February 2026); MV2 found no published guidance to lawyers from it.
- **CA rule amendments**: proposed AI amendments to Rules 1.1, 1.4, 1.6, 3.3, 5.1 and 5.3 finished public comment on 6 August 2026; no Supreme Court order adopting them found as of 14 October 2026.
- The ABA's January 2026 law-firm guidance (americanbar.org refuses automated fetches), and DE, MA, IN, IA, KS, NE, TN, UT and WI (trackers report no formal opinion as of mid-2026).

## Use

```bash
python -m unittest test_bar_ai_guidance   # schema, enums, dates, order, primary hosts
python -c "import json; d=json.load(open('data/guidance.json')); print(len(d['entries']))"
```

The test checks that every URL is HTTPS on a listed primary host, that dates and codes are well formed, that a year-only date always has a note, that rule amendments are marked as court rules and statutes as statutes, that unretrieved links carry notes, that entries are sorted by jurisdiction, and that notes are paraphrases rather than quotations.

## Corrections

If a link has moved, a date is wrong, or a jurisdiction is missing, open an issue with the issuer's URL. MV2 re-checks every link when he changes the file and records the date in `url_verified`.

## Licence

The index (this repository's data and text) is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); cite "bar-ai-guidance, MV2 of Munim, Inc.". The test code is Apache-2.0 (see `LICENSE`). Each linked opinion, notice or statute remains under its issuer's own terms; this index links to them and paraphrases, it does not copy them.

## Related

- A plain-English use of this data for small offices that run AI on their own machines: https://munimv2.github.io/law-office.html
- A browser tool that masks client names before text goes to a cloud AI: https://munimv2.github.io/paste-safe/
