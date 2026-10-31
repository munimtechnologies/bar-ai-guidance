# Eight court texts, five ways to define a "safe" AI system: what each says about a self-hosted model

Written 31 October 2026. By MV2 of Munim, Inc. (mv2@munimtech.com); this note was made with AI agents working in his name. Text CC BY 4.0. It describes public documents. It is not legal advice, and it does not say whether any setup complies with any rule.

This is a descriptive comparison, not a pre-registered test: the texts were read first and compared afterwards. Every definition below is quoted from the issuer's own text, and the note says how each was read.

## Result in one paragraph

Courts that limit what confidential information may go into an AI tool define the safe kind of tool in at least five different ways: by **who controls the system** (California Rule of Court 10.430, Arkansas Administrative Order No. 25, the New York court system's interim policy), by **what the system does with what is entered** (Pennsylvania's interim policy), by **what the AI provider has promised in a contract** (a District of Colorado protective-order ruling), by **whether the code and model are public** (a District of Nevada standing order), and by **an approved list** (Delaware's interim policy, Utah's interim rules). Applied word for word to three common setups, the texts disagree. An openly published model running on the office's own server passes the three control tests. It fails the Nevada test, and under Pennsylvania's text it is secured only if the chat app keeps no history. The Colorado ruling does not say how a system with no outside provider qualifies. A free consumer chatbot fails every control, data-handling and contract test, yet the Nevada words do not reach it, because its code and model are not public, and Utah's approved list names ChatGPT, Claude.ai and Gemini. **No single fact, such as "it runs on our own machine", answers all eight texts.**

## The eight texts

| # | Text | Who it binds | How read |
|---|---|---|---|
| 1 | California Rules of Court, rule 10.430 (eff. 1 September 2025) | courts' policies for court staff and judicial officers | courts.ca.gov rules page, fetched 31 October 2026 |
| 2 | Arkansas Supreme Court, Administrative Order No. 25 as adopted (2025 Ark. 220, 11 December 2025), §1(b) | awareness for everyone in the court system; prohibition for court staff | copied in a browser from opinions.arcourts.gov, 30 October 2026 (the site refuses automated fetches) |
| 3 | New York State Unified Court System, Interim Policy on the Use of Artificial Intelligence (October 2025) | court system users | copied in a browser from nycourts.gov, 31 October 2026 |
| 4 | Supreme Court of Pennsylvania, Interim Policy on the Use of Generative AI by Judicial Officers and Court Personnel (order of 9 September 2025, eff. 8 December 2025; 55 Pa.B. 6696) | court personnel | policy PDF on pacourts.us and the Pennsylvania Bulletin, fetched 31 October 2026 |
| 5 | Supreme Court of Delaware, Interim Policy on the Use of GenAI by Judicial Officers and Court Personnel (order of 21 October 2024) | judicial officers and court personnel | order and policy PDF on courts.delaware.gov, fetched 31 October 2026 |
| 6 | Utah Judicial Council, Interim Rules on the Use of Generative AI (from 27 October 2025) | court-related work and court-owned devices | the Judiciary HR page and its approved-tools list, fetched 31 October 2026; the rules PDF itself is a Google Drive file that asks for sign-in, so its text was **not** read |
| 7 | D. Nev., First Amended Standing Order of Magistrate Judge Maximiliano D. Couvillier III (eff. 5 January 2026), §III(4) | counsel and parties | the court's PDF, fetched 31 October 2026 (see the [federal count](federal-ai-orders-inputs.md)) |
| 8 | D. Colo., *Morgan v. V2X, Inc.*, No. 25-cv-01991-SKC-MDB, Order of 30 March 2026 (Magistrate Judge Maritza Dominguez Braswell), ECF 65 | the parties and authorized recipients of CONFIDENTIAL information in that case | the order's PDF in the RECAP archive, copied in a browser, 31 October 2026 |

Texts 1 to 6 govern courts and their staff, not lawyers (Arkansas's awareness section also speaks to everyone in the court system, as guidance). They are here because they are the most detailed definitions courts have written. Texts 7 and 8 govern lawyers and parties.

## What each text says (quoted) and how it sorts three setups

The three setups, described the same way for every text:

- **A. Self-hosted open-weight model.** An openly published model (for example Llama or Qwen weights) runs on a server the organisation owns and is reachable only from its own network. The chat app keeps conversation history on that server.
- **B. Business cloud service.** A proprietary model is used through a vendor's business plan. The contract bars training on inputs, and the vendor keeps inputs for a limited time for abuse monitoring.
- **C. Consumer chatbot.** A free consumer account whose terms allow inputs to be used to improve the vendor's models.

"Allowed" below means only that the text's own definition does not put the setup in the forbidden class for confidential or non-public information. Each text is applied as if the organisation in the setup were the one the text addresses.

**1. California, rule 10.430(a)(4) and (d)(1): who can reach or train on the data.** A "public generative AI system" is one "that allows anyone other than court staff or judicial officers to access the data that courts input or upload to the system or to use that data to train AI systems", and it "does not include any system that the court creates or manages". Court policies must prohibit entering "confidential, personal identifying, or other nonpublic information into a public generative AI system".
A: allowed (managed by the court; nobody outside reaches the data). B: **unclear**: there is no training, but vendor staff reviewing inputs for abuse may be "anyone other than court staff" with access to the data. C: not allowed.

**2. Arkansas, AO 25 §1(b): who deploys and controls it.** "A public LLM is accessible to anyone and usually hosted by a third party (like OpenAI's GPT or Anthropic's Claude). A private LLM is deployed and controlled by an organization and operated on its own infrastructure or cloud account."
A: private. B: **unclear**: a vendor-hosted service is "usually hosted by a third party", but a model "operated on its own ... cloud account" is private. C: public.

**3. New York UCS interim policy: under the court system's control.** "A private model is a model that is under UCS control and does not share data with any public LLM." Public models "can be accessed by anyone and may store data for use in future training." "No user may input into any generative AI program that does not operate on a private model ... any information that is confidential, private, or privileged ..."
A: private. B: not allowed: the vendor's model is not "under UCS control", and the policy has no contract exception. C: not allowed.

**4. Pennsylvania interim policy: what the system does with entered data.** A "Secured AI System" protects "the confidentiality and privilege of all data and documents entered"; such systems "do not retain any such data or documents entered into the system, do not transfer or sell such data or documents to third parties, and do not expose such data or documents to the public domain". A "Non-Secured AI System" "includes a system that retains user documents or data". "Personnel shall not share any non-public information with non-secured AI systems."
A: **depends on a setting**: read literally, a chat app that keeps conversation history "retains user documents or data", so the same self-hosted model is secured only with history off. B: depends on the contract: secured under zero-retention terms, non-secured while the vendor keeps inputs for abuse monitoring. C: not allowed.

**5. Delaware interim policy: administrative approval.** "Approved GenAI" means tools "approved by the Administrative Office"; "Authorized Users may not input any Non-Public Information into Non-Approved GenAI."
A, B, C: whichever the Administrative Office approves. Nothing in the definition turns on hosting, retention or training.

**6. Utah interim rules: an approved list.** The HR page says "Any AI Tools not expressly permitted in the attached interim rules is prohibited" and lists Adobe FireFly, ChatGPT, Claude.ai (Beta), Gemini Pro, Microsoft Copilot, NotebookLM (Google), Webex Cisco AI Assistant and Westlaw.
A: not on the list. B: depends on whether the vendor's product is one of those listed. C: ChatGPT, Claude.ai and Gemini are listed. Whatever the rules say about confidential inputs into listed tools could not be read.

**7. D. Nev., Judge Couvillier: whether code and model are public.** "Counsel and parties are prohibited from uploading onto any open AI system - where the source code, learning materials, and underling models maybe publicly accessible - any filed documents which: (a) have been filed under seal; or (b) contain personal-data identifiers ..." (as printed).
A: **not allowed**: the underlying model is publicly accessible. B: allowed (not "open"). C: **allowed by the literal words**: the code, training material and model are not public, even though inputs may be used for training.

**8. D. Colo., *Morgan v. V2X*: what the provider has promised in writing.** "No party or authorized recipient may input, upload, or submit CONFIDENTIAL Information into any modern artificial intelligence platform ... unless the AI provider is contractually prohibited from: (1) storing or using inputs to train or improve its model; and (2) disclosing inputs to any third party except where such disclosure is essential to facilitating delivery of the service." "A party intending to use AI that it contends meets these requirements must retain written documentation of these contractual protections." The court did not adopt the plaintiff's proposal that tools "operate within a secure, closed-circuit environment".
A: **unclear**: there is no outside provider, the model's licence makes no such promises, and the order does not say how a platform a party runs itself qualifies. B: depends on the contract: allowed only if it also bars *storing* inputs, so abuse-monitoring retention fails the literal words. C: not allowed.

## Side by side

| Text | Axis | A. self-hosted open-weight | B. business cloud | C. consumer chatbot |
|---|---|---|---|---|
| CA rule 10.430 | who can reach or train on data | allowed | unclear | not allowed |
| AR AO 25 | who deploys and controls | allowed | unclear | not allowed |
| NY UCS policy | under the court's control | allowed | not allowed | not allowed |
| PA interim policy | retention, transfer, exposure | only with history off | only with zero retention | not allowed |
| DE interim policy | approval | if approved | if approved | if approved |
| UT interim rules | approved list | not listed | if listed | listed |
| D. Nev. Couvillier | public code or model | **not allowed** | allowed | **allowed** |
| D. Colo. *Morgan* | provider's contract | unclear | only if storing is barred | not allowed |

Counted across the eight texts, setup A is allowed outright by 3, refused by 2 (Nevada, and Utah's list as it stands), allowed by 1 only with a setting changed (Pennsylvania), and left to an approval by 1 and unclear under 1. Setup C is refused by 5, left to an approval by 1, and allowed by the literal words of 2 (Nevada's text and Utah's list).

## What this means in practice

The texts ask for different facts. Between them, an office or court would need to know:

1. who operates the system (the organisation, a cloud account it controls, or a vendor);
2. who else can reach what is entered (vendor staff, sharing or community features, other users of the same server);
3. whether inputs are used to train or improve any model;
4. whether inputs and chat history are kept, and for how long;
5. whether the model's weights or code are publicly available;
6. what the provider's contract says, in writing;
7. whether the tool is on the court's approved list.

Facts 2 and 4 are often software settings on a self-hosted machine: whether the model server answers other machines, whether sharing is switched on, whether chat history is kept. MV2's [bar-ai-guidance](https://github.com/munimtechnologies/bar-ai-guidance) records what fifteen self-hosted tools do out of the box (`data/self_hosted_defaults.json`). Which of these facts matters, and whether a given setup meets a given text, is for the lawyer and the court.

## Two loose ends being checked

- **Vermont.** Administrative Directive No. 38 as amended on 6 October 2025 contains the sentence "In addition, all court users must ensure that AI systems do not compromise sensitive or confidential information". If that sentence is in force, it is an input-side duty that reaches lawyers appearing in Vermont courts, with no definition of a safe system. The amendment marks new matter by underlining and deleted matter by striking through, and plain text extraction loses both. So MV2 is checking which kind of text this sentence is before relying on it. If it is in force, his [earlier result](court-rules-inputs-vs-outputs.md) needs a qualification: that check found no binding state court rule on what lawyers may put into an AI tool, but Vermont's directive was outside its fixed sample.
- **District of Columbia.** A search result describes a DC Courts internal AI policy that sorts tools into "sequestered" and "non-sequestered" systems. The court's PDF refused an automated fetch, so it is not counted here until it has been read.

## Why this is new

Trackers and commentary describe these policies one at a time. LLRX's October 2025 survey describes Pennsylvania's secured/non-secured split and no other definition. The eDiscovery LLC and Cimplifi posts discuss single protective orders. MV2's own [federal count](federal-ai-orders-inputs.md) set the Nevada text beside three control tests. No source found (searched 31 October 2026) puts the control, data-handling, contract, openness and approval definitions side by side, or applies them word for word to the same concrete setups.

## Limits

- This is eight texts chosen because their definitions were readable at the source, not a census. Other courts' policies, and protective orders in individual cases, may define things differently.
- Literal readings. Courts may read their own texts by purpose. Judge Couvillier's order is most likely aimed at systems that expose sealed material, and Pennsylvania's "retain" is most likely aimed at vendors. No court is known to have applied any of these texts to a self-hosted open-weight model.
- Texts 1 to 6 govern courts, not law firms. Applying them to an office's own setup only shows how their definitions sort it.
- Utah's rules text was not readable, so only its approved list is used. The Arkansas, New York and Colorado wording was copied in a browser by MV2's hands rather than fetched by a script.
- One team of AI agents read and compared the texts. Every call above rests on a quotation, so anyone can check it.
