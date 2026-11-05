# Amendment 1 to the pre-registration "How 2026 legal-aid RFPs treat a vendor's own use of AI"

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name.
Text: CC BY 4.0. Code: Apache-2.0. Information about public procurement documents, not legal advice.

Written 5 November 2026. The original pre-registration (`analysis/legal-aid-rfp-ai-prereg.md`, commit 17f6f85,
4 Nov 2026 14:18 UTC) is unchanged. This amendment widens how the frame is collected. It changes no coding rule
and no prediction. When it was written, no collected posting text had been read for AI language. The one
exception is the Georgia Legal Services Program RFP, which the original pre-registration already named as
the posting that prompted the study.

## Why

The first collection (job `rfp-ai-collect-v1`, 4 Nov 2026 14:23 UTC) found 34 posting slugs. Only 5 pages
were still live; 14 came from Wayback captures; 15 had no fetchable page at all (9 had no capture, and for 6
Wayback refused the connection). LSNTAP removes a posting page once the posting closes. Every file linked from
the 14 archived pages was nevertheless still live on lsntap.org. Web searches on 5 November 2026 then turned up at least
six 2026 postings that v1 missed entirely, among them Legal Aid Chicago's RFI on AI architecture (posted 8/17/26),
a North Mississippi Rural Legal Services intake RFP (July 2026) and a Community Legal Services (Arizona)
strategic-plan RFP (July 2026). Their attached files are still live on lsntap.org even though the
posting pages are gone. A frame that misses them would not be the census of the board that the
pre-registration describes.

## Changes to the frame (collector v2, job `rfp-ai-collect-v2`)

1. **Listing teasers.** For every captured listing page, the text shown next to each posting (title,
   Posted, Closing, short description) is kept. A posting whose own page is gone takes its Posted date
   from the teaser.
2. **2026 files.** The Wayback CDX index for `lsntap.org/sites/default/files/2026-` (PDF and DOCX) is
   added. A file that no collected posting page links to becomes an "orphan file" record. Each file is
   fetched live from lsntap.org, or from Wayback if it is gone.
3. **Search seeds.** Slugs and file URLs returned by web searches on 5 November 2026 are added and marked
   `web_search_seed` (`analysis/rfpai/seeds.json`). The search results are leads only. Every text is read
   from the fetched source.
4. **Retries.** Wayback requests get longer back-off (Wayback rate-limits). PDFs with almost no text layer
   are OCR'd with tesseract, and each use of OCR is recorded.

## Rules fixed now for the new kinds of record

- **Posted date** for a posting without its own page: the listing teaser's "Posted" date. If there is
  none, the issue or release date printed in the document. If there is none of those either, the upload
  folder month (`2026-MM`), which counts as in the study only if it is 2026-01 to 2026-11. The source of
  each date is recorded.
- **One posting, one record.** Orphan files are matched to postings by reading: same organisation and
  same solicitation. An addendum or Q&A file joins its posting's text. Two LSNTAP postings whose RFP files
  are byte-identical (same SHA-256) and come from the same organisation count once, under the earlier
  Posted date. This already applies to the two Navajo Nation Judicial Branch postings (Sep 2026).
- **Codable** is unchanged: at least 1,000 characters of text across the page, the teaser and the
  attached files together.
- The listing type rule is unchanged. A file is in the study only if the document is itself a request for
  proposals, quotes, information or bids.

## Disclosure and sensitivity checks

The search results showed the titles of some seeded postings, and several titles name AI ("AI
Architecture", "Copilot Agents"). That knowledge could only push P4 (AI_IN_SCOPE among technology
postings) toward holding, and could affect P1. So P1 to P4 will each be reported twice. The primary
result covers the full amended frame. A sensitivity result covers only records found by sources (a) to
(c) of the original pre-registration plus source 2 above, leaving out records found only by
`web_search_seed`. If the two results differ on any prediction, the write-up says so in its first
paragraph.

## Unchanged

The coding rules (VENDOR_AI and its sub-codes, AI_IN_SCOPE, TECH/NON_TECH), the locator terms, the four
predictions and their thresholds, and the duty to publish every call with a verbatim quotation, whichever
way the predictions come out.
