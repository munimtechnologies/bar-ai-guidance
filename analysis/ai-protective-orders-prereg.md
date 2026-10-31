# Pre-registration: how do AI clauses in protective orders treat a self-hosted open-weight model?

Written 31 October 2026, before any post in the sample below was read. By MV2 of Munim, Inc. (mv2@munimtech.com); this note was made with AI agents working in his name. Text CC BY 4.0. It is about public court documents, not legal advice.

## Why

Since late 2025, US courts have entered a run of protective and confidentiality orders that limit how parties may use AI tools with material produced in discovery. Commentators sort them into a few drafting models (for example Kilpatrick Townsend's four approaches, 1 May 2026: blanket prohibition, data rights, contractual safeguards, notice and secure environment). No source found counts how often each test is used, or asks how the orders treat an office that runs an openly published model on its own server.

Two June 2026 orders already point in opposite directions. *RMME LLC v. Majestic Steel USA, Inc.* (D. Nev., ECF 20, 24 June 2026) calls a system "open" if its "source code, training data, or underlying models are publicly accessible", so a self-hosted open-weight model can never be its "closed" kind. *Velez v. OnePlus* (S.D.N.Y., No. 25-cv-2432, ECF 28, 16 June 2026), as quoted in a National Law Review article (Jack Pringle, 26 June 2026), lists "self-hosted language models" among the systems that may be used. This count asks which way most orders go.

## What was already known before this note

MV2 has read *RMME*'s definitions and *Morgan v. V2X* (D. Colo., 30 March 2026) at the source, and has seen secondary summaries of *Velez v. OnePlus*, *Jeffries v. Harcros Chemicals* (D. Kan., 25 March 2026) and the cases Kilpatrick Townsend names. He has seen the titles of the blog posts that the sample is drawn from, in the blog's own search results, but not their text. These cases are coded like all the others if they fall in the frame.

## Sample frame (fixed now)

- **Source:** Michael Berman's E-Discovery LLC blog, ediscoveryllc.com, which has reported AI protective orders since 2025. The source is fixed in advance because it is public and dated, and its author covers these orders as they appear. It is a convenience frame, not a census.
- **Posts:** every post the site's public WordPress REST API (`/wp-json/wp/v2/posts`) lists as published from 1 October 2025 to 31 October 2026, inclusive, read by a sandboxed job that starts only after this file is on GitHub.
- **Filter (mechanical, in `frame.py`):** the title contains "AI" or "A.I." as a word, or "artificial intelligence"; and the title or text contains "protective order", "confidentiality order", "protective/confidentiality order", "confidentiality agreement" or "disclosure materials".
- **Unit:** one court order per case. A case enters the sample if a post in the frame quotes or describes an order (protective, confidentiality or similar discovery order, stipulated or not) whose text limits the use of AI with material from the case. If a case has several such orders in the frame, the latest one is used. Orders that only refuse a proposed AI clause are counted separately as refusals.
- **Codable:** an order is codable if its AI text is quoted in the post, or can be read for free at the source (court site or the RECAP archive). Orders described but not quoted, and not readable at the source, are listed as "not codable" and left out of every denominator.

## Coding (fixed now)

For each codable order, every call is backed by a quotation in the published data file.

1. **Tests used** (more than one may apply):
   - **BAN:** no AI use with protected material at all, or only with the producing party's consent.
   - **PUBLIC:** the permitted or forbidden class depends on whether the tool is public, consumer, publicly available or third-party hosted.
   - **OPENNESS:** the class depends on whether source code, training data, weights or models are publicly accessible.
   - **DATA:** the class depends on what the tool does with inputs: training, retention, disclosure to third parties or deletion.
   - **CONTRACT:** the order requires contract terms with the AI provider.
   - **NOTICE:** the order requires notice, disclosure to the other side, an objection procedure or court approval before use.
   - **OTHER.**
2. **Self-hosting named:** does the AI text mention self-hosted, on-premises, locally run or locally installed tools, or a party's own infrastructure? (yes or no)
3. **Openness named:** does the AI text mention open-source software or publicly available models or weights? (yes or no)
4. **Setup A under the literal words.** Setup A is an openly published model (for example Llama or Qwen weights) running on a server the party controls, reachable only from its own network, with no outside provider, never trained on inputs, with chat history kept on that server. Codes: **permitted**; **conditional** (permitted only after notice, consent, approval, a contract, or a changed setting); **forbidden**; **unclear** (the words do not settle it, with the reason).

## Predictions

Over codable orders:

- **P1.** At most 20% name self-hosting (item 2).
- **P2.** At least 50% use the DATA test.
- **P3.** At most 25% use the OPENNESS test, and no order that uses it codes setup A as permitted.
- **P4.** Setup A is permitted by the literal words in at least 50%, and forbidden in at most 20%.

If fewer than 10 orders are codable, the result is reported as too small to grade, with the counts.

## What would count as failure

Each prediction holds or fails on its own numbers. All four are reported, whichever way they go, with the coded data (`data/ai_protective_orders.json`) and the frame (`frame.json`, post ids, dates, links and content hashes).

## Limits fixed in advance

- One blog is the frame, so the sample reflects which orders its author found and chose to write about.
- Many orders will be read as quoted in a post, not at the source; those calls say so. A sample of orders available in the RECAP archive will be checked against the source where a free copy exists.
- One team of AI agents codes the orders, without a second, independent coder. Every call carries its quotation so that anyone can recheck it.
- Literal readings only. Courts may read their own orders by purpose, and none is known to have applied an AI clause to a self-hosted open-weight model.
