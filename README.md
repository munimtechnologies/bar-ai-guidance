# bar-ai-guidance

A small, verified index of what US bars and courts have told lawyers about using generative AI, with a **primary-source link for every row**. One JSON file, one test, no dependencies.

Made by MV2 of Munim, Inc., with AI agents working in his name. It is information about public documents, not legal advice or an ethics opinion.

## Why

By October 2026 more than twenty US jurisdictions had issued opinions, guidance or rule changes on lawyers' use of generative AI, and the public hallucination-case database kept by Damien Charlotin listed over 2,000 decisions. Law firm trackers summarise the guidance behind HTML pages or paywalls. Nothing small and machine-readable pointed at the **issuing bar's or court's own page or PDF** for each document, with a record of when the link was last checked. That is what this is.

## What is in it

`data/guidance.json` holds one entry per document:

| field | meaning |
|---|---|
| `jurisdiction` | `US` for the ABA, otherwise the state code or `DC` |
| `issuer`, `title`, `number`, `date` | as the document itself states them (`YYYY-MM` when it gives no day, `YYYY` when only the year is known, with `notes` saying how) |
| `kind` | `formal_opinion`, `advisory_opinion`, `guidance`, `court_notice`, `court_policy` or `rule_amendment` |
| `binding` | `advisory`, or `court_rule` for an amendment a court adopted into its rules |
| `url` | the issuer's own page or PDF, never an aggregator |
| `url_verified`, `verification` | when MV2 last checked the link, and whether the page was `fetched` and its title matched, or only `cited` from the issuer's own site |
| `confidentiality_note` | a one-sentence paraphrase of the confidentiality point, in MV2's words |
| `in_house_tools_note` | what the document says about tools run inside the firm, if anything |

Version 0.4.0 (14 October 2026) has 34 entries from the ABA, 25 states and DC: AK, AL, AZ (Supreme Court committee best practices and State Bar guidance), CA, CO, DC, FL, GA, IL (Supreme Court policy and ARDC guide), KY, MI, MN, MO (two informal opinions), NC, NH, NJ, NM, NY (two City Bar opinions and the State Bar Task Force report), OH, OR (two formal opinions), PA, SC, TX, VA (bar guidance and LEO 1901 on fees), WA and WV. Where MV2's tool could not extract a PDF's text, the entry's `notes` say so and say where the date and paraphrase came from; where the text was read, the notes say that too.

What changed in 0.4.0:

- **California's 2026 revision.** The State Bar's Practical Guidance was revised on 14 May 2026, replaces the 2023 version, and now covers agentic AI: it says agents with access to firm email, document stores or client files need limited scope, monitoring and access controls. The entry now points at the 2026 PDF.
- **Colorado's rule change** (Rule Change 2026(02), 8 January 2026): the first entry of the new kind `rule_amendment`, adding AI to the Scope and the comments to Rule 1.1.
- **AI that listens or talks.** NYC Bar Formal Opinion 2025-6 (December 2025) says clients must be told, and must agree, when AI records their calls, and asks where recordings and transcripts are stored and for how long. Oregon Formal Opinion 2026-208 (February 2026) covers chatbots and AI agents used for client intake.
- **Two court documents and a bar article:** the Arizona Supreme Court committee's *Generative AI: Ethical Best Practices for Lawyers and Judges* (November 2024), South Carolina's interim AI policy order (March 2025), and the New Hampshire Bar Ethics Committee's Ethics Corner article (May 2024).
- **Alabama** Formal Opinion 2026-01: the text was read, and it confirms the document states no date or number on its face.

Known gaps, to be added as each primary link is verified:

- **MS** (Ethics Opinion 267, November 2024): the Mississippi Bar's site says formal opinions are available through its member research platform after logging in, so there is no public primary link to point at.
- **MD** (Maryland State Bar Association AI Task Force, *An Overview of Ethical Considerations for Attorney Use of Generative Artificial Intelligence Technologies*, April 2025, 7 pages): sold in the MSBA store at $29 for non-members, free to members; no public copy found.
- **RI**: the Supreme Court's Executive Order 2024-03 set up a Committee on Artificial Intelligence and the Courts with a report due by 30 June 2025; the order itself gives no guidance to lawyers, so it is not indexed.
- The ABA's January 2026 law-firm guidance (americanbar.org refuses automated fetches), and DE, MA, IN, IA, KS, NE, TN, UT and WI (trackers report no formal opinion as of mid-2026).

## Use

```bash
python -m unittest test_bar_ai_guidance   # schema, enums, dates, order, primary hosts
python -c "import json; d=json.load(open('data/guidance.json')); print(len(d['entries']))"
```

The test checks that every URL is HTTPS on a listed primary host, that dates and codes are well formed, that a year-only date always has a note, that rule amendments are marked as court rules, that entries are sorted by jurisdiction, and that notes are paraphrases rather than quotations.

## Corrections

If a link has moved, a date is wrong, or a jurisdiction is missing, open an issue with the issuer's URL. MV2 re-checks every link when he changes the file and records the date in `url_verified`.

## Licence

The index (this repository's data and text) is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); cite "bar-ai-guidance, MV2 of Munim, Inc.". The test code is MIT (see `LICENSE`). Each linked opinion or notice remains under its issuer's own terms; this index links to them and paraphrases, it does not copy them.

## Related

- A plain-English use of this data for small offices that run AI on their own machines: https://munimv2.github.io/law-office.html
- A browser tool that masks client names before text goes to a cloud AI: https://munimv2.github.io/paste-safe/
