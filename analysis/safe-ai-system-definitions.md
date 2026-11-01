# Eight court texts, five ways to define a "safe" AI system: what each says about a self-hosted model

Written 31 October 2026. By MV2 of Munim, Inc. (mv2@munimtech.com); this note was made with AI agents working in his name. Text CC BY 4.0. It describes public documents. It is not legal advice, and it does not say whether any setup complies with any rule.

This is a descriptive comparison, not a pre-registered test: the texts were read first and compared afterwards. Every definition below is quoted from the issuer's own text, and the note says how each was read.

## Result in one paragraph

Courts that limit what confidential information may go into an AI tool define the safe kind of tool in at least five different ways: by **who controls the system** (California Rule of Court 10.430, Arkansas Administrative Order No. 25, the New York court system's interim policy), by **what the system does with what is entered** (Pennsylvania's interim policy), by **what the AI provider has promised in a contract** (a District of Colorado protective-order ruling), by **whether the code and model are public** (a District of Nevada standing order), and by **an approved list** (Delaware's interim policy, Utah's interim rules). Applied word for word to three common setups, the texts disagree. An openly published model running on the office's own server passes the three control tests. It fails the Nevada test, and under Pennsylvania's text it is secured only if the chat app keeps no history. The Colorado ruling does not say how a system with no outside provider qualifies. A free consumer chatbot fails every control, data-handling and contract test, yet the Nevada words do not reach it, because its code and model are not public, and Utah's approved list names ChatGPT, Claude.ai and Gemini. **No single fact, such as "it runs on our own machine", answers all eight texts.** An addendum at the end adds three texts read later the same day (the DC Courts' internal policy, Iowa's Chapter 27 rules and a District of Nevada protective order); they add three more variations and do not change this.

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

## Two loose ends (as first published; both are settled in the addendum below)

- **Vermont.** Administrative Directive No. 38 as amended on 6 October 2025 contains the sentence "In addition, all court users must ensure that AI systems do not compromise sensitive or confidential information". If that sentence is in force, it is an input-side duty that reaches lawyers appearing in Vermont courts, with no definition of a safe system. The amendment marks new matter by underlining and deleted matter by striking through, and plain text extraction loses both. So MV2 is checking which kind of text this sentence is before relying on it. If it is in force, his [earlier result](court-rules-inputs-vs-outputs.md) needs a qualification: that check found no binding state court rule on what lawyers may put into an AI tool, but Vermont's directive was outside its fixed sample.
- **District of Columbia.** A search result describes a DC Courts internal AI policy that sorts tools into "sequestered" and "non-sequestered" systems. The court's PDF refused an automated fetch, so it is not counted here until it has been read.

## Addendum, 31 October 2026 (later the same day): three more texts, and Vermont settled

These three texts were read after the comparison above was published. They are added here with their own counts, so the eight-text counts above stay as first published. The setups and the meaning of "allowed" are the same as above.

**9. DC Courts AI Internal Use Policy (promulgated 16 May 2025): what the provider promises.** Read in the court's PDF on dccourts.gov, by a sandboxed job and in a browser by MV2's hands, 31 October 2026. It governs "all DC Courts' judicial officers, employees, contractors, and volunteers"; it does not name attorneys. A "Non-Sequestered System" covers "virtually all free AI tools and a number of paid AI tools, where the confidentiality of data and prompts entered by the user may not be private to the user". A sequestered tool "is one which the provider purports to protect the confidentiality of data and prompts entered by the user". "No court information, whether public or confidential, should be entered into a non-sequestered system. No confidential information should be shared with an AI tool." But "AI tools contracted for or developed for the DC Courts are exempt from this policy", and "No non-sequestered system may be locally installed on court-owned devices nor on personal devices used to access confidential court information."
A: **unclear**: the policy expects some tools to be installed locally, but it sorts them by what a provider promises, and an openly published model has no provider making a promise; a model the courts deploy themselves may count as "developed for the DC Courts" and so be exempt, but the policy does not say. B: allowed if contracted for the courts (exempt); otherwise no confidential information, and public court information only if the vendor promises confidentiality. C: not allowed.
Like Colorado, this turns on the provider's word, but a weaker one: Colorado needs a contractual bar on storing and training, DC only a provider that "purports" to protect confidentiality.

**10. Iowa Court Rules, Chapter 27, Judicial Use of Artificial Intelligence Tools (adopted 21 July 2026, effective 1 January 2027): approval, in-house tools included.** Read in the rules PDF on iowacourts.gov by a sandboxed job, 31 October 2026. It governs judges and their adjudicative assistants, not lawyers appearing in court. Rule 27.106(1): "A judicial officer or adjudicative assistant must not use an artificial intelligence tool for the performance of a judicial officer's adjudicative duties with any judicial case information unless the tool is currently approved by the committee to meet the confidentiality, security, and reliability requirements for that use." An artificial intelligence tool is covered "whether developed by the judicial branch or provided by an outside vendor". Approval of a tool the branch does not provide "may be conditioned on the judicial officer's or adjudicative assistant's compliance with specific requirements for the configuration of the tool", and the approved list must be posted publicly (Rule 27.107).
A, B, C: if approved. Unlike California's rule and the DC policy, a system the court builds or runs gets no exemption, and the rule names configuration as something an approval may depend on.

**11. D. Nev., *RMME LLC v. Majestic Steel USA, Inc.*, stipulated protective order, ECF 20, filed 24 June 2026: openness, with "or".** The definitions were copied word for word in a browser by MV2's hands from the order's PDF on CourtListener, 31 October 2026. "For purposes of this section, an 'open AI system' means an AI system for which the source code, training data, or underlying models are publicly accessible." A "closed AI system" "means any AI system that is not an open AI system and that is subject to contractual, technical, or administrative safeguards reasonably designed to prevent unauthorized access, disclosure, or use of submitted materials, and that does not use Protected Material to train, improve, or refine its models or algorithms or otherwise incorporate Protected Material into outputs generated for other users or matters." Open AI systems "may be used only if such use does not result in the disclosure of Protected Material in violation of this Order and does not violate Section III(4) of Judge Couvillier's Standing Order".
A: **open, and it can never be closed**: its model is publicly accessible, so no safeguard makes it a closed system; it may be used only on the order's conditions for open systems. B: closed, if the contract and safeguards are as described. C: **neither**: its code and model are not public, so it is not open, and it trains on inputs, so it is not closed. Only part of the order's use rules was copied, so what it says about a system in neither class is not recorded here.
This is the parties' agreement entered as an order in one case, not a rule. It carries Judge Couvillier's openness test into a protective order, with "or" where the standing order has "and".

| Text | Axis | A. self-hosted open-weight | B. business cloud | C. consumer chatbot |
|---|---|---|---|---|
| DC Courts policy | provider's promise; contracted or developed tools exempt | unclear | allowed if contracted for the courts | not allowed |
| IA Chapter 27 | committee approval, in-house tools included | if approved | if approved | if approved |
| D. Nev. *RMME* order | public code, training data or model | open (never closed) | closed | neither class |

Across all eleven texts, setup A is allowed outright by 3, refused or restricted by 3 (Judge Couvillier's order, Utah's list and the *RMME* order), allowed by 1 only with a setting changed, left to approval by 2 and unclear under 2. Setup C is refused by 6, left to approval by 2, allowed by the literal words of 2 and in neither class under 1. Still no single fact answers all the texts.

**Vermont: the sentence is in force.** A sandboxed job read the underline and strike-through markup in Vermont's Administrative Directive No. 38 as amended on 6 October 2025 (the court's PDF on vtcourts.gov, sha256 41fd0716...fc161), and the extracted markup was checked by eye. The sentence "In addition, all court users must ensure that AI systems do not compromise sensitive or confidential information, and that data used with AI is handled in accordance with data privacy regulations" is unmarked: the amendment neither added nor deleted it, so it stands. The same section says "All court users, including self-represented litigants" are expected to check AI output. So Vermont puts an input-side duty on everyone who uses its courts, lawyers included, without defining a safe system. The [court-rules result](court-rules-inputs-vs-outputs.md) now carries an addendum saying so, and bar-ai-guidance 0.15.0 lists the directive, Iowa's rules and the DC policy.

## Why this is new

Trackers and commentary describe these policies one at a time. LLRX's October 2025 survey describes Pennsylvania's secured/non-secured split and no other definition. The eDiscovery LLC and Cimplifi posts discuss single protective orders. MV2's own [federal count](federal-ai-orders-inputs.md) set the Nevada text beside three control tests. No source found (searched 31 October 2026) puts the control, data-handling, contract, openness and approval definitions side by side, or applies them word for word to the same concrete setups.

## Limits

- This is eight texts chosen because their definitions were readable at the source, not a census. Other courts' policies, and protective orders in individual cases, may define things differently.
- Literal readings. Courts may read their own texts by purpose. Judge Couvillier's order is most likely aimed at systems that expose sealed material, and Pennsylvania's "retain" is most likely aimed at vendors. No court is known to have applied any of these texts to a self-hosted open-weight model.
- Texts 1 to 6 govern courts, not law firms. Applying them to an office's own setup only shows how their definitions sort it.
- Utah's rules text was not readable, so only its approved list is used. The Arkansas, New York and Colorado wording was copied in a browser by MV2's hands rather than fetched by a script.
- One team of AI agents read and compared the texts. Every call above rests on a quotation, so anyone can check it.
