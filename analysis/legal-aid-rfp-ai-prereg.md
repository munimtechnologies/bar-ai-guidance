# Pre-registration: how 2026 legal-aid RFPs treat a vendor's own use of AI

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name.
Text: CC BY 4.0. Code: Apache-2.0. Information about public procurement documents, not legal advice.

Written 4 November 2026, before any posting in the frame has been read for AI language. Its first
commit time on GitHub is the registration time. The only posting read so far is the one that prompted
the question (below); it is in the frame and is coded under the same rules as the rest.

## Why

Legal-aid organisations hire consultants and vendors for intake assessments, evaluations, software and
strategic plans. On 3 November 2026, Georgia Legal Services Program posted an intake-assessment RFP that
asks bidders to disclose any AI use and their safeguards, and requires human review of AI-assisted
deliverables before they are final. We found no count of how often legal-aid RFPs say anything about
a vendor's own use of AI (searches on 4 November 2026: web search for legal-aid RFP AI disclosure and
human-review clauses; LSNTAP; general procurement commentary, which covers federal and state
government, not legal aid). Vendors need to know what they will be asked to disclose, and programs may
want to see what other programs ask.

## Frame (fixed now)

- **Source:** the LSNTAP Jobs & RFPs board (https://www.lsntap.org/jobs-rfps), the main public board
  where US legal-aid programs post technology and consulting RFPs.
- **Postings:** every posting page at `https://www.lsntap.org/jobs-rfps/<slug>` found in (a) the live
  listing on the collection day, (b) the Wayback Machine CDX index for the URL prefix
  `lsntap.org/jobs-rfps/` (captures 1 Sep 2025 to 4 Nov 2026), or (c) any Wayback capture of the listing
  page from 1 Jan to 4 Nov 2026. Collected by `rfpai/collect_rfps.py` (job `rfp-ai-collect-v1`).
- **In the study:** postings that are a request for proposals, quotes, information or bids (listing type,
  or a title beginning "(RFP)", "(RFQ)", "(RFI)" or "Request for"), NOT job adverts, whose "Posted"
  date falls between 1 January and 4 November 2026.
- **Codable:** an in-study posting with at least 1,000 characters of text, counting the posting page and
  its attached PDF or DOCX files together. Image-only files are OCR'd and the use of OCR is recorded.
  Postings that are not codable are listed with the reason and left out of every percentage.

## Coding (each call backed by a verbatim quotation found in the collected text)

- **VENDOR_AI clause:** any sentence that asks about, requires, limits or forbids the bidder's or
  contractor's own use of AI (artificial intelligence, generative AI, large language models, ChatGPT and
  the like, or "AI tools") in preparing the proposal or doing the work. Sub-codes, more than one allowed:
  `disclose` (must say whether or how AI is used), `human_review` (AI output must be reviewed by a
  person), `data` (limits on putting the organisation's or clients' data into AI tools), `restrict`
  (some use needs permission or is limited), `ban` (any AI use forbidden).
- **AI_IN_SCOPE:** the work requested includes AI as something the organisation wants or may want
  (for example an AI intake tool, a chatbot, or "groundwork for future AI"). Coded separately from
  VENDOR_AI. A posting can have both, either or neither.
- **TECH posting:** the requested work is mainly software, a website, a case management, intake, phone
  or data system, or IT services. Others (strategic plans, evaluations, needs assessments, branding)
  are NON_TECH. Intake assessments that are mainly a review of processes are NON_TECH.
- Terms used only to locate passages (reading decides): "artificial intelligence", "AI", "A.I.",
  "generative", "GenAI", "LLM", "large language", "ChatGPT", "Copilot", "machine learning", "automated".
- A standard boilerplate clause about "automated" processing with no mention of AI does not count.
- Coding is done by reading, by AI agents working in MV2's name; there is no second coder. Every call
  and its quotation are published, so any reader can check them.

## Predictions

| | Prediction | Over |
|---|---|---|
| P1 | At most 30% of codable postings have a VENDOR_AI clause | all codable 2026 postings |
| P2 | The VENDOR_AI share among postings posted 1 Jul to 4 Nov 2026 is strictly higher than among those posted 1 Jan to 30 Jun 2026 | both halves need at least 5 codable postings, else P2 is "not testable" |
| P3 | No codable posting has a `ban` sub-code | all codable 2026 postings |
| P4 | At least 25% of codable TECH postings have AI_IN_SCOPE | codable TECH postings; at least 5 needed, else "not testable" |

Each prediction is graded held / failed / not testable and published whichever way it comes out,
together with the frame (every slug and why it is in or out), each posting's codes and quotations, and
the hashes of the collected files.

## Limits known in advance

- One board. Programs that post RFPs only on their own sites, or on state procurement portals, are
  missing, so this is a census of the board, not of legal aid.
- Postings removed from the board before any Wayback capture are missing.
- An RFP's text says what a program asks for, not how it scores answers.
