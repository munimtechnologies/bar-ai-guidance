---
name: court-ai-rules
description: Use when drafting, checking or filing a document for a US court with help from generative AI, when a user asks which bar opinions, court rules, court orders or statutes on AI apply to lawyers in a US state, or before client or case information goes into an AI tool for legal work. Looks the state up in an open index of primary-source documents from the ABA, US states and DC, says which ones are binding court rules or statutes, links the issuer's own text, and gives a pre-filing checklist. Information about public documents, not legal advice.
license: Apache-2.0
---

# Court and bar AI rules (United States)

Made with AI agents working in MV2's (Munim, Inc.) name. Skill and script: Apache-2.0. The index
it reads, `data/guidance.json` in https://github.com/munimtechnologies/bar-ai-guidance, is
CC BY 4.0; every linked document keeps its issuer's own terms.

The index holds one entry per document that a US bar, court or legislature issued on lawyers'
use of generative AI (62 entries from the ABA, 39 states and DC in version 0.16.2; the script
prints the current count). Each entry links the issuer's own page or PDF, says whether it is a
**court rule**, a **state statute** or **advisory guidance**, records when the link was last
checked, and carries a one-sentence paraphrase of its confidentiality point.

What it is not:

- **Not legal advice.** It says what public documents say and where to read them. Whether a
  filing or a practice complies is for the responsible lawyer, and in the end the court.
- **Not complete.** It lists only documents read from primary sources. It does **not** list
  federal judges' standing orders, federal or state local rules, or individual judges' orders.
  A state with no entry is not a state with no rules.
- **Paraphrases, not quotations.** The confidentiality and in-house-tools lines are MV2's
  words. Quote the linked document itself, never these lines, as if they were the rule.

## When to use

- You are drafting, editing or checking a brief, motion, pleading or other court filing with an
  AI tool, or reviewing one an AI tool helped write.
- The user asks what AI rules, ethics opinions or disclosure duties apply in a US state.
- The user is about to paste client, case or sealed information into an AI tool, or is setting
  one up for a law office.

## Step 1: look up the jurisdiction

Run the script from this skill folder. It needs Python 3.8+ (standard library only). Inside a
checkout of the repository it reads the local `data/guidance.json`; elsewhere it makes one
read-only HTTPS GET for the published file (or reads `--file PATH`).

```
python scripts/court_ai_rules.py --state CT
python scripts/court_ai_rules.py --state NY --no-national
python scripts/court_ai_rules.py --state FL,IN --binding court_rule
python scripts/court_ai_rules.py --state CA --json
python scripts/court_ai_rules.py --grep citation
python scripts/court_ai_rules.py --id ms-op-267 --notes
python scripts/court_ai_rules.py --summary
```

`--state` takes two-letter codes, `DC` or `US` (repeat it or separate with commas). National
entries (the ABA, code `US`) are added unless you pass `--no-national`. Other filters:
`--binding` (`court_rule`, `statute`, `advisory`), `--kind` (for example `rule_amendment`,
`formal_opinion`, `court_policy`), `--id` (exact) and `--grep` (any field, case-insensitive).
`--notes` adds each entry's notes, which say how the entry was read and what is uncertain.
`--json` prints the entries with a `binding_label` and a `link_label` added.

Exit code 0 means at least one entry matched (with `--state`, at least one entry of that state
itself, not only the ABA's); 1 means none; 2 means the index could not be read. When a state
has no entry the script says so in words: pass that message on, do not turn it into "there are
no rules".

## Step 2: tell the user

- Put binding instruments first: a **court rule** or **state statute** binds; **advisory
  guidance** (ethics opinions, bar guidance, court policies addressed to court staff) does not
  by itself, though it shows how a bar reads the rules it enforces.
- For each entry give the issuer, title, date and link, and say "MV2's paraphrase" for the
  confidentiality line. If the link label says `cited` (not retrieved) or `archived` (an Internet
  Archive copy of the issuer's own file), say that too.
- Give the date the index was updated. Rules here change monthly; say when something might be
  newer than the index, and check the issuer's own site when it matters.
- Never tell the user a filing complies, that a use is permitted, or what a court will do. Say
  what the document says and that the responsible lawyer decides.

## Step 3: before an AI-assisted filing

Work through this list with the user. It is a reading list, not a compliance certificate.

1. **State filing rules.** Look the court's state up (Step 1) and read every `court rule` and
   `statute` entry. Examples in the index: Florida's amended Rule 2.515
   (`fl-sc2026-0673-rule-2-515`) makes every signer represent that the cited authorities exist
   and are accurately cited, and administrative order AOSC26-12 (`fl-aosc26-12`) stops Florida's
   courts from adding their own AI disclosure or certification requirements. Indiana's amended
   Trial Rule 11 (`in-trial-rule-11-2026`) makes an attorney's signature certify that every cited
   authority is authentic. Connecticut's Practice Book Section 4-9 (`ct-practice-book-4-9-2026`)
   requires anyone who used generative AI to create or edit a filed document to verify each
   citation, authority or piece of evidence it produced. New York's Part 161 (`ny-ucs-part-161`)
   allows AI use in preparing court papers without mandatory disclosure but requires the
   attorney to review each paper for fabricated material. California's SB 574 (`ca-sb-574`)
   takes effect on 1 January 2027.
2. **Pending rules.** The repository README's "Known gaps" lists documents not yet indexed,
   such as Texas's preliminarily approved amendments to Civil Procedure Rule 13 and Appellate
   Rule 9.1 (Misc. Docket No. 26-9054), which had no final order as of 6 November 2026.
3. **The court and the judge.** Federal courts, and many state judges, set AI duties by local
   rule or standing order (certifications, disclosure of the tool used, or nothing beyond Rule
   11). Check the court's own website and the assigned judge's page for every filing. The
   repository's `data/federal_orders_inputs.json` is a coded research sample of 62 federal
   orders, not a lookup list.
4. **Disclosure.** Whether AI use must be disclosed depends on the court. Some state courts have
   said it need not be: Illinois's Supreme Court policy (`il-supreme-court-ai-policy`) says
   disclosure should not be required in a pleading, and New York's Part 161 imposes none, while
   individual judges elsewhere require it. Follow the specific order for the case.
5. **Every citation, in a primary source.** Check each case, statute, quotation and pin cite
   against an official or reliable source (the court's own site, an official reporter or a
   citator). An AI tool's own confirmation is not a check. Damien Charlotin's AI Hallucination
   Cases database listed 2,267 decisions about fabricated or false AI-generated material on
   6 November 2026; MV2's pre-registered count of what courts did in those decisions is at
   https://github.com/munimtechnologies/bar-ai-guidance/blob/main/analysis/hallucination-sanctions.md
6. **Confidentiality.** Before client or case information goes into an AI tool, read the
   state's confidentiality and in-house-tools lines and ABA Formal Opinion 512 (`us-aba-512`),
   then the documents themselves. Running a model on the office's own machine does not settle the
   question by itself: if the office does, the repository's `data/self_hosted_defaults.json`
   records who can reach fifteen self-hosted AI tools as shipped, with sources.

## Keep it current

The script reads the published index by default, so it is as current as the repository. If you
find a bar, court or legislative document on lawyers' AI use that the index lacks, or a link
that has moved, the user can open an issue at
https://github.com/munimtechnologies/bar-ai-guidance/issues with the issuer's own URL.

MV2, Munim, Inc., mv2@munimtech.com
