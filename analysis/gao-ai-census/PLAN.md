# Pre-registration: a prospective census of GAO bid-protest decisions that discuss AI-fabricated authority (census 1.0.0)

Status: **frozen before the first census fetch.** Written 2026-11-08 by AI agents working in MV2's
name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` (standard library only, Apache-2.0),
tests in `test_census.py`, one-wave wrapper `run_job.py`. Each wave checks that this PLAN and
`census.py` are public in this repository, and that its own `census.py` matches the newest
committed one, before it contacts gao.gov. Information about public decisions only, not legal
advice and not advice on any protest.

## Why

MV2's graded study of the AI Hallucination Cases Database ([`../procurement-ai.md`](../procurement-ai.md))
found 24 GAO decisions from 2025 to October 2026 that discuss fabricated or garbled authority. Those
counts have no denominator: nobody knows what share of GAO's published protest decisions they are.
The database's coverage of new decisions is also unknown. This census counts GAO's own published
decisions as they appear, so both questions get an answer.

## Prior art

David P. J. Timm (Burr & Forman, 11 Sep 2026) counts these decisions by hand, without a
denominator. Washington Technology (Oct 2025) counted 9 GAO decisions. We found no published
share of all GAO decisions and no measure of how fast such decisions reach the database.

## How the data are collected (gao.gov robots.txt honoured)

GAO's robots.txt disallows `/search` and asks for `Crawl-delay: 420`. A wave makes one request to
the legal-decisions RSS feed (`/rss/reportslegal.xml`, about 25 items covering roughly 18 days).
It then fetches each new bid-protest decision page (`/products/b-...`), with at least 425 seconds
between requests and at most 40 pages per wave. It never requests `/search`. The User-Agent names
MV2 and his email. A wave runs about every 7-12 days, so consecutive feeds overlap. A wave whose
feed does not reach back to the previous wave's newest item records `gap_possible: true`, and every
such gap is reported.

- **Bid protest:** the feed link's first B-number is B-400000 or higher. Lower numbers (B-33xxxx) are
  appropriations-law decisions and are counted but not fetched.
- **Decision text:** from the "Matter of:" paragraph to the General Counsel's signature
  ("General Counsel</p>"). Site menus and footers are never classified, because every gao.gov page
  carries an "Artificial Intelligence (AI)-Related Reports" menu link. A page without a "Matter of:"
  paragraph is counted as unparsed.
- **Categories** (lower-cased decision text; each term must start at a word boundary):
  AI terms = artificial intelligence, large language model, large-language model, generative ai,
  genai, chatgpt, hallucinat*, ai-generated, ai program, ai tool. Citation terms = non-existent,
  nonexistent, does not exist, do not exist, fabricated, fictitious, no such decision, erroneous
  citation, inaccurate citation, could not locate, unable to locate.
  `ai_citation` = both kinds of term. `ai_only` = AI terms only (for example, protests about an
  agency's own AI tools). `cite_only` = citation terms only (a reading list, not a finding).
  `none` = neither.
- **Counsel:** in the header (before DIGEST), the first line naming "the protester". It is `lawyer`
  if that line contains "Esq.", otherwise `no_lawyer` (the company or person acting for itself),
  and `unknown` if there is no such line.
- **Sustained:** the decision text contains "protest is/are sustained" or "we sustain the protest".
- **Published rows** (`decisions.csv`): B-numbers, link, feed date, decision date, protester name
  only if it carries a company marker (LLC, Inc., Corp., Company, Ltd., LP, LLP, PLLC, P.C., JV,
  d/b/a; otherwise left blank), counsel class, category, matched terms, sustained flag, text length
  and SHA-256. Raw pages are never republished. Read them at gao.gov.

## Window

Every bid-protest decision seen in any wave from the first wave through the last wave run before
**2027-02-01**. The first wave's feed reaches back about 18 days, to around 2026-10-20. Grading is
done in February 2027 by a separate, later job that uses the frozen functions in `census.py`
(`db_match` for B3), plus this plan.

**Seen before freezing, stated plainly.** A design pilot on 2026-11-08 (three requests, 425 s apart)
fetched the feed and two decision pages, B-424064 (Bramstedt Surgical Inc., 28 Jan 2026, outside
the window, already in the database) and B-424672 (NDCHealth Corporation, 27 Oct 2026). Those
pages were used to design the parser. B-424672's text mentions no AI term, and its only
"Artificial Intelligence" is the site menu. No other decision in the window has been read.

## Predictions (fixed now)

- **B1 (share):** among parsed bid-protest decisions in the window, the `ai_citation` share is at
  least 1% and at most 10%. Not testable below 40 parsed decisions. (Basis: about 24 database rows
  in 22 months, against roughly 30 published protest decisions a month in the feed.)
- **B2 (who):** at least half of the `ai_citation` decisions have counsel `no_lawyer`. Not testable
  below 3 `ai_citation` decisions. (The database's 2026 GAO rows are about half lawyer, so this
  could go either way.)
- **B3 (database coverage):** at grading time, at least 75% of `ai_citation` decisions dated on or
  before 2027-01-15 match a GAO row in the AI Hallucination Cases Database under `db_match`. A row
  matches if it contains the decision's B-number core, or if the protester key and a date within 3
  days agree. Not testable below 3 such decisions.
- **B4 (outcome):** none of the `ai_citation` decisions is sustained. Not testable below 3.

Each prediction is reported as held, failed or not testable, every one of them, either way.

## Secondary (reported, not graded)

Before grading, an AI agent reads every `ai_citation` and `cite_only` decision at gao.gov and
records whether the decision itself discusses inaccurate citations attributed to AI. B1-B4 are
then also reported on that reading, beside the code-graded primary result. The reading is
labelled as an AI agent's reading, not a human review. We also report the counts of `ai_only`
decisions and of decisions per feed day.

## Limits

GAO does not publish every decision (some are closed, and dismissals often go unpublished), so the
denominator is published decisions only. Keyword rules miss decisions that describe the problem in
other words, which is why `cite_only` exists. A feed gap can drop decisions, and gaps are reported.
The protester line may name a company officer, not a lawyer, and that is what `no_lawyer` means.
This is not legal advice and not advice on any protest.
