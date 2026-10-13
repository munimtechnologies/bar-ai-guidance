# bar-ai-guidance

A small, verified index of what US bars and courts have told lawyers about using generative AI, with a **primary-source link for every row**. One JSON file, one test, no dependencies.

Made by MV2 of Munim, Inc., with AI agents working in his name. It is information about public documents, not legal advice or an ethics opinion.

## Why

By October 2026 more than twenty US jurisdictions had issued opinions or guidance on lawyers' use of generative AI, and the public hallucination-case database kept by Damien Charlotin listed over 2,000 decisions. Law firm trackers summarise the guidance behind HTML pages or paywalls. Nothing small and machine-readable pointed at the **issuing bar's own page or PDF** for each document, with a record of when the link was last checked. That is what this is.

## What is in it

`data/guidance.json` holds one entry per document:

| field | meaning |
|---|---|
| `jurisdiction` | `US` for the ABA, otherwise the state code or `DC` |
| `issuer`, `title`, `number`, `date` | as the document itself states them (`YYYY-MM` when it gives no day) |
| `kind` | `formal_opinion`, `advisory_opinion`, `guidance` or `court_notice` |
| `url` | the issuer's own page or PDF, never an aggregator |
| `url_verified`, `verification` | when MV2 last checked the link, and whether the page was `fetched` and its title matched, or only `cited` from the issuer's own site |
| `confidentiality_note` | a one-sentence paraphrase of the confidentiality point, in MV2's words |
| `in_house_tools_note` | what the document says about tools run inside the firm, if anything |

Version 0.1.0 (13 October 2026) covers the ABA and nine jurisdictions: CA, DC, FL, KY, NJ, NY (City Bar), NC, PA, TX. Known gaps, to be added as each primary link is verified: AK, AL, MO, MS, NM, OR, RI, VA, WA, WV, the NYSBA Task Force report, and the ABA's January 2026 law-firm guidance.

## Use

```bash
python -m unittest test_bar_ai_guidance   # schema, enums, dates, primary hosts
python -c "import json; d=json.load(open('data/guidance.json')); print(len(d['entries']))"
```

The test checks that every URL is HTTPS on a listed primary host, that dates and codes are well formed, and that notes are paraphrases rather than quotations.

## Corrections

If a link has moved, a date is wrong, or a jurisdiction is missing, open an issue with the issuer's URL. MV2 re-checks every link when he changes the file and records the date in `url_verified`.

## Licence

The index (this repository's data and text) is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); cite "bar-ai-guidance, MV2 of Munim, Inc.". The test code is MIT (see `LICENSE`). Each linked opinion or notice remains under its issuer's own terms; this index links to them and paraphrases, it does not copy them.

## Related

- A plain-English use of this data for small offices that run AI on their own machines: https://munimv2.github.io/law-office.html
- A browser tool that masks client names before text goes to a cloud AI: https://munimv2.github.io/paste-safe/
