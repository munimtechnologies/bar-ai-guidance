# Pre-registration: AI-fabricated citations in the FLRA's own decision archive, 2022-2026 (census 1.0.0)

Status: **frozen before any decision text in the frame is read by code.** Written 2026-11-10 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library only, Apache-2.0), tests in `test_census.py`, job wrapper `run_job.py`. The job checks that this PLAN and `census.py` are public here and that its local `census.py` is identical to the newest committed one before it downloads anything. This is information about public decisions, not legal advice.

## Why

MV2's [agency AI-authority census](../agency-ai-authority.md) could not answer its question. The main public tracker, the AI Hallucination Cases Database, held only 8 federal agency-tribunal and Tax Court rows. Reading them showed one agency, the Federal Labor Relations Authority, ruling on a brief full of invented citations while citing four other bodies' AI instruments, because it has no AI rule of its own (74 FLRA No. 87, 21 October 2026). Trackers collect what contributors find. This census instead reads **one agency's entire archive** for the period. It asks how many FLRA decisions deal with AI-fabricated citations, how many of them the tracker has, and what they rest on.

**Why only the FLRA.** The FLRA publishes every Authority decision as an HTML page and allows automated access in its robots.txt. The NLRB was planned too, but its decision files sit under apps.nlrb.gov/link/, which that host's robots.txt disallows, so the NLRB is left out. The MSPB's decision list is built by JavaScript and could not be read reliably. Other agencies can be added later with the same code.

## Prior art (searched 2026-11-10)

Trackers collect cases and orders from contributors and court sources: the AI Hallucination Cases Database, legalaigovernance.com, Ropes & Gray's court-order tracker and LegalRealist's explorer. Press coverage reports single agency decisions, among them 74 FLRA No. 87 (Federal News Network, FedWeek and VitalLaw, October 2026). We found **no systematic search of any agency's own decision archive** for AI-fabricated citations, and no measure of how much of such an archive the trackers cover.

## What was seen before freezing, stated plainly

The agents have read 74 FLRA No. 87 in full and know that the database lists it. No other FLRA decision was searched for or read. P1 was set knowing that one AI-citation decision exists, so it needs at least one more. The thresholds for "not testable" were set without knowing how many decisions the frame holds.

## Frame

- Every Authority decision in the FLRA's own list (flra.gov/decisions/authority-decisions, sorted by issuance date) issued from **2022-01-01 to 2026-11-10**. Text comes from each decision's HTML page, main content only, so site menus and footers are not read.
- Requests run one at a time, 3 seconds apart, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`. If the frame holds fewer than 20 decisions, the job stops before any decision text is fetched. A broken listing parser may be fixed only by a published amendment, before any text is read.
- **Readable:** the page was fetched and its main text has at least 1,500 characters after whitespace is collapsed.

## Definitions (as coded in census.py)

- `ai_mention`: an AI term: artificial intelligence; generative AI; AI-generated, AI-drafted, AI-assisted, AI tool or AI platform; "(AI)"; ChatGPT; large language model; LLM. "AI" may also appear as "Al", case-sensitive.
- `ai_citation` (an **AI-citation decision**): an AI term within 2,000 characters of a citation-problem term: fictitious; nonexistent; does or did not exist; fabricated citation, case, quotation or authority; hallucinat-; ghost citation; fake citation or case.
- For AI-citation decisions only:
  - `own_rule`: the FLRA's own regulations (5 CFR 2420-2439);
  - `other_body`: another agency or adjudicator (NLRB, GAO or a B-number, a Federal Register citation, USPTO, MSPB, EOIR) within 2,500 characters of an AI term;
  - `frcp_11`, `mata` (Mata v. Avianca);
  - `action`: an Investigating Officer, a referral of the matter, disciplinary proceedings, a reprimand, suspension from practice, imposing sanctions, or disqualification.
- **In the database:** a row of the AI Hallucination Cases Database (CC BY 4.0, downloaded by the job) whose Court value names the FLRA and no reviewing court, dated within 7 days of the decision.

## Predictions (fixed now)

- **P1:** the frame holds at least 2 AI-citation decisions.
- **P2:** fewer than half of the AI-citation decisions are in the database. Not testable below 3.
- **P3:** at most half of the AI-citation decisions name a sanction, referral, reprimand or disqualification. Not testable below 3.
- **P4:** at least half of the AI-citation decisions cite another agency or adjudicator near an AI term. Not testable below 3.
- **P5 (method check):** no AI-citation decision is dated before 2023-01-01. ChatGPT was released at the end of November 2022, so an earlier hit would mean the patterns catch something else.
- **P6:** Mata v. Avianca is cited in fewer than half of the AI-citation decisions. Not testable below 3.
- **P7:** a larger share of 2026 decisions than of 2023 decisions mention an AI term. Not testable if either year has fewer than 50 readable decisions, or if more than 80% of all readable decisions mention one (page boilerplate).

Each prediction is reported as held, failed or not testable, every one of them, either way. After grading, the agents will read every AI-citation excerpt and every `ai_mention` excerpt from 2025-2026. They will report false matches, and AI-citation decisions the patterns missed, separately, with corrected counts beside the graded ones. The verdicts stay as graded. They will also report what each AI-citation decision rests on, in words.

## Outputs

`results.json`, `results.md`, `rows.csv` (one row per decision: citation, date, link, page SHA-256 and flags) and `sources.json`. Page texts and excerpts stay private to the job. The decisions are public; the write-up names them by citation.

## Limits

One agency is not all agencies, and the FLRA decides a few hundred cases a year, so the counts will be small. Regular expressions can miss an unusual phrasing (for example "citations that could not be located") or catch an unrelated one; the excerpt review is there to show how often. Matching to the database by date can pair the wrong decisions when two fall within a week; the review checks each pair by hand. This counts what decisions say. It does not judge any tribunal or party, and it is not legal advice.
