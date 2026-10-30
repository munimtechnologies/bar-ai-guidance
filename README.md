# bar-ai-guidance

A small, verified index of what US bars, courts and legislatures have told lawyers about using generative AI, with a **primary-source link for every row**. Since 0.6.0 it also records **what self-hosted AI tools let people reach out of the box**, the software side of the same confidentiality question. JSON files and tests, no dependencies.

Made by MV2 of Munim, Inc., with AI agents working in his name. It is information about public documents and public source code, not legal advice or an ethics opinion.

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

The guidance index is at version 0.12.0 (30 October 2026), with 51 entries from the ABA, 34 states and DC: AK, AL, AR (Supreme Court's Administrative Order No. 25 on AI, as published for comment in June 2025 and as adopted in December 2025), AZ (Supreme Court committee best practices and State Bar guidance), CA (State Bar guidance and SB 574), CO, CT (Superior Court's 2026 Practice Book Section 4-9 on verifying generative AI output), DC, FL (Bar ethics opinion 24-1, the Supreme Court's 2026 amendment to Rule 2.515 on cited authorities and administrative order AOSC26-12 barring local AI disclosure orders), GA, HI, IL (Supreme Court policy and ARDC guide), IN (Supreme Court's 2026 amendment to Trial Rule 11 on authentic citations), KY, LA (Supreme Court letter to the bar), MA (Office of Bar Counsel article), MI, MN, MO (two informal opinions), NC, ND (court system public notice), NH, NJ (Supreme Court guidelines and State Bar Association task force report), NM, NY (three City Bar opinions, the State Bar Task Force report and the court system's Part 161 rule), OH, OR (two formal opinions), PA, RI (Supreme Court order amending Rule 1.1 and its interim guidelines for lawyers), SC, TX, VA (bar guidance and LEO 1901 on fees), WA, WI (State Bar ethics counsel column) and WV. Version 0.9.0 added eight documents, five of them court instruments from 2026; the Part 161 entry rests on the State Bar's posting of the court system's notice, because nycourts.gov refused MV2's automated fetch. Version 0.10.0 added Indiana's Trial Rule 11 amendment, read on the Supreme Court's official rules site. Version 0.11.0 added Florida's AOSC26-12 and Arkansas's Administrative Order No. 25 as published for comment in June 2025 (the adopted December 2025 text could not be read from a primary source), and the Indiana entry now also rests on the Court's own order. Version 0.12.0 added Connecticut's Practice Book Section 4-9 (read in the Connecticut Law Journal) and Arkansas's adopted Administrative Order No. 25 (read in a browser, because the Judiciary's opinions site refuses automated fetches), and the New York Part 161 entry now also records what the court system's own page says. Where MV2's tool could not extract a PDF's text, the entry's `notes` say so and say where the date and paraphrase came from; where the text was read, the notes say that too.

## Who can reach a self-hosted AI tool out of the box (0.8.0: fifteen tools)

California's **SB 574** (in force 1 January 2027) asks whether access to what an attorney enters into a generative AI system is restricted to the attorney and authorised persons. For a firm that runs its own AI, the answer depends on software settings. `data/self_hosted_defaults.json` records them as shipped for fifteen tools: ten model servers (Ollama, llama.cpp, SGLang, vLLM, LocalAI, KoboldCpp, LMDeploy, LiteLLM Proxy, TabbyAPI, Xinference) and five chat apps (AnythingLLM, text-generation-webui, LibreChat, Dify, Open WebUI). For each it gives the address the tool listens on when started directly and in the project's own container, whether it asks for a credential, whether anyone can sign up, and the admin and sharing defaults. Each fact links the source file or doc page it was read from, and each entry says what was not checked. 0.8.0 added KoboldCpp, LMDeploy, TabbyAPI and Xinference, and dates LiteLLM's master-key check to its first release.

What it shows ([full write-up](analysis/sb574-self-hosted-defaults.md)):

- Seven of the ten model servers ask for no credential by default. vLLM, LocalAI, KoboldCpp and LMDeploy listen on all interfaces even when started directly (KoboldCpp while printing a localhost address). Ollama, llama.cpp and SGLang stay on the machine when started directly, but their own container or compose setups listen on all interfaces.
- The three that demand a credential do it three different ways: LiteLLM's proxy refuses to start without a real master key; TabbyAPI generates random keys at first start; Xinference requires a login, but whoever reaches its setup page first creates the admin. LocalAI refuses an unauthenticated start only on public addresses.
- LiteLLM's check is new: committed 19 September 2026 and first released in v1.104.0 on 3 October 2026, so proxies installed from earlier releases do not have it.
- AnythingLLM's Docker install and text-generation-webui's container have no login until one is turned on. LibreChat lets anyone who reaches it register. Dify is invitation-only once set up, but until the first admin exists whoever opens `/install` first owns it. Open WebUI holds new sign-ups for admin approval, but lets every admin read every user's chat and shows a button that uploads a chat to an outside site.
- In ten of the fifteen, someone never given an account can, as shipped, either use the model or create an account and use the app; Dify and Xinference allow it only before setup. Self-hosting does not restrict access by itself; changed settings do.

This is a record of defaults on 14 October 2026, not a view on whether any office meets SB 574.

## Known gaps in the guidance index

- **MS** (Ethics Opinion 267, November 2024): the Mississippi Bar's site says formal opinions are available through its member research platform after logging in, so there is no public primary link to point at.
- **MD** (Maryland State Bar Association AI Task Force, *An Overview of Ethical Considerations for Attorney Use of Generative Artificial Intelligence Technologies*, April 2025, 7 pages): sold in the MSBA store at $29 for non-members, free to members; no public copy found.
- **AR**: the AI-related amendments to the Rules of Professional Conduct (2025 Ark. 221, 11 December 2025). MV2's hands read them in a browser, but their exact title and placement in the Rules are not yet recorded, so they are not listed yet.
- **CA rule amendments**: proposed AI amendments to Rules 1.1, 1.4, 1.6, 3.3, 5.1 and 5.3 finished public comment on 6 August 2026; no Supreme Court order adopting them found as of 14 October 2026.
- **TX**: Misc. Docket No. 26-9054 (26 June 2026) preliminarily approved amendments to Civil Procedure Rule 13 and Appellate Rule 9.1 under which a signer represents having verified the filing's accuracy, including that citations, quotations and holdings are not fabricated. The Court expected them to take effect on 1 October 2026, but on 30 October 2026 txcourts.gov's rules advisories list no final order and the current Rules of Civil Procedure still print the old Rule 13, so this stays a gap until a final order appears.
- The ABA's January 2026 law-firm guidance (americanbar.org refuses automated fetches), and DE, IA, KS, NE, TN and UT (trackers report no formal opinion as of mid-2026; trackers say the same of IN, MA and WI, whose Supreme Court rule amendment, Office of Bar Counsel article and State Bar guidance are now listed above).

## Use

```bash
python -m unittest test_bar_ai_guidance test_self_hosted_defaults
python -c "import json; d=json.load(open('data/guidance.json')); print(len(d['entries']))"
```

`test_bar_ai_guidance` checks that every URL is HTTPS on a listed primary host, that dates and codes are well formed, that a year-only date always has a note, that rule amendments are marked as court rules and statutes as statutes, that unretrieved links carry notes, that entries are sorted by jurisdiction, and that notes are paraphrases rather than quotations. `test_self_hosted_defaults` checks the defaults file's fields and enums, that every source is the project's own repository or documentation, that a tool marked as requiring a key says how it avoids a keyless start (refusing to start, or generating a key), that a project recorded without a release says it has none, and that the file draws no legal conclusions.

## Corrections

If a link has moved, a date is wrong, a default has changed or a jurisdiction is missing, open an issue with the issuer's or project's URL. MV2 re-checks every link when he changes the file and records the date in `url_verified` or `checked`.

## Licence

The index and the defaults record (this repository's data and text) are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); cite "bar-ai-guidance, MV2 of Munim, Inc.". The test code is Apache-2.0 (see `LICENSE`). Each linked opinion, notice or statute remains under its issuer's own terms, and each software project under its own licence; this repository links to them and paraphrases, it does not copy them.

## Related

- A plain-English use of this data for small offices that run AI on their own machines: https://munimv2.github.io/law-office.html
- A browser tool that masks client names before text goes to a cloud AI: https://munimv2.github.io/paste-safe/
- Do the binding court rules govern what goes into an AI tool, or only what comes out? A pre-registered check and its result: [pre-registration](analysis/court-rules-inputs-vs-outputs-prereg.md), [result](analysis/court-rules-inputs-vs-outputs.md).
