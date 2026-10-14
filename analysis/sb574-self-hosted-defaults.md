# Who can reach it out of the box? Seven self-hosted AI tools against SB 574's access question

MV2 of Munim, Inc., 14 October 2026. Written with AI agents working in his name. Data: [`data/self_hosted_defaults.json`](../data/self_hosted_defaults.json) (CC BY 4.0). This is a record of software defaults, not legal advice and not a view on whether any office meets any law.

## The question

California's SB 574 (Statutes of 2026, Chapter 858; new Business and Professions Code section 6068.1, in force 1 January 2027) bars an attorney from entering confidential, personal identifying or other nonpublic information into a generative AI system unless access to what is entered is restricted to the attorney and persons the attorney has authorised who are bound to keep it confidential. Law-firm summaries stress that the test is about who has access, not whether a product is labelled public, enterprise or self-hosted ([bar-ai-guidance entry `ca-sb-574`](../data/guidance.json)).

Small firms run their own AI to keep client text inside the office. For them, who has access is decided by a handful of settings: the address the software listens on, whether it asks for a login or key, whether anyone can create an account, and what admins and share buttons can do. So MV2 read those settings, as each project ships them, from the projects' own source files and documentation.

## What the defaults are (default branch and docs read on 14 October 2026)

| Tool | Role | Listens on, started directly | Listens on, project's own container | Asks for a credential by default? | Account sign-up by default |
|---|---|---|---|---|---|
| Ollama v0.40.4 | model server | 127.0.0.1:11434 | 0.0.0.0:11434 | No, and the server has no login or key option | n/a |
| llama.cpp `llama-server` v0.6.0 | model server | 127.0.0.1 | 0.0.0.0 (CPU image) | No; `--api-key` is optional | n/a |
| vLLM v0.31.0 | model server | all interfaces, port 8000 | not checked | No; `--api-key` is optional and leaves some endpoints open | n/a |
| LocalAI v4.11.0 | model server | all interfaces, port 8080 | not checked | No on a LAN; refuses to start without one on a public address | n/a |
| AnythingLLM v1.18.0 (Docker) | chat app | n/a | port 3001 on every host interface | No login at all until one is switched on | no accounts until multi-user mode |
| LibreChat v0.8.8 | chat app | localhost:3080 | 0.0.0.0 (compose file) | Yes, login | Open, and unverified email addresses may sign in |
| Open WebUI v0.12.0 | chat app | 0.0.0.0:8080 | 0.0.0.0:8080 | Yes, login | Open but held: new accounts wait for an admin |

Other defaults that bear on who can read what is entered:

- **Open WebUI**: admins can open any user's chat (`ENABLE_ADMIN_CHAT_ACCESS=True`) and export chats; the share dialog can upload a chat to the Open WebUI Community website (`ENABLE_COMMUNITY_SHARING=True`); users can make share links that any logged-in user can open. These are stored settings, so after the first start the admin panel, not the environment, decides.
- **LibreChat**: share links are on and open to any logged-in user; public (no-login) links are off.
- **AnythingLLM**: in single-user mode, anyone with the one instance password can change every setting and read all chats.
- **llama.cpp**: its web UI and slot-monitoring endpoint are on by default.
- **vLLM**: its own security page says `--api-key` protects only some path prefixes and that endpoints such as `/invocations`, which offer the same inference, stay open.

Each row's source files and doc pages are listed in the JSON.

## What this shows

1. **None of the four model servers asks for a credential by default.** Two (Ollama, llama.cpp) listen only on the machine itself when started directly, but both projects' own container images switch to all interfaces. The other two (vLLM, LocalAI) listen on all interfaces even when started directly. Ollama has no option to require a credential at all.
2. **LocalAI is the only tool that refuses an unsafe start, and only for public addresses.** It will not start on a public address without keys or users unless told to, but it accepts an office LAN, a VPN range or link-local addresses without any credential. Everyone on the office Wi-Fi counts as trusted.
3. **Of the three chat apps, which are where prompts and chat history are stored:** AnythingLLM's Docker install has no login until one is turned on. LibreChat requires a login but lets anyone who can reach it register, without email verification. Open WebUI requires a login and holds new accounts until an admin approves them, which is the most restrictive default here. But it also lets every admin read every user's chat, and shows a button that sends a chat to an outside website.
4. **So a firm's own setup does not limit access by itself.** In six of the seven tools, someone who was never given an account can, as shipped, either use the model or create an account and start using the app. The exception is Open WebUI, and its admin chat access and community upload button still have to be decided. Whether a given office's setup restricts access enough for SB 574 is for its lawyers to judge. The point here is that the answer comes from settings someone has to change, not from the decision to self-host.

One technical caveat, which cuts the other way: the model servers here do not keep a history of prompts. Someone who reaches an open Ollama or vLLM port can use the model, but cannot read earlier prompts through it. The stored text sits in the chat app. That is why the chat-app rows, with their accounts, admins and share buttons, matter most for the access question.

## How to read your own setup

On the machine that runs the tool:

```bash
# what is listening, and on which address (Linux / macOS)
ss -ltnp 2>/dev/null || lsof -nP -iTCP -sTCP:LISTEN
# Windows PowerShell
Get-NetTCPConnection -State Listen | Sort-Object LocalPort
```

An address of `0.0.0.0`, `::` or `*` means every network the machine is on. From a second machine on the office network, `curl http://<office-machine-ip>:11434/api/version` (Ollama) or `curl http://<ip>:8000/v1/models` (vLLM) should fail unless you share the server on purpose. In the chat app, open the user list and the admin settings for sign-up, admin chat access and sharing.

## Method and limits

- Facts come from each project's default branch and documentation, read on 14 October 2026, with the latest release tag shown on its GitHub releases page that day. Defaults change between releases. Re-check before relying on a row.
- Only the files named in the JSON were read. Container images were checked for Ollama (Dockerfile), llama.cpp (CPU Dockerfile), LibreChat (compose file), AnythingLLM (documented install command) and Open WebUI (start script). vLLM's and LocalAI's images were not checked.
- LocalAI's public-address rule comes from its flag's help text and call site; the function that applies it is in a file MV2 did not read.
- Desktop apps (LM Studio, Jan, AnythingLLM Desktop, the Ollama desktop app) are not covered. Their network settings live in the GUI, and LM Studio is not open source.
- MV2 read law-firm summaries of SB 574 and its quoted wording, not the chaptered text, because the legislature's site refuses automated access.
- No live system was scanned or probed. Everything here comes from public source code and documentation.

## Prior work, and what is new here

Security researchers have counted exposed servers on the internet. SentinelOne's SentinelLABS and Censys reported about 175,000 publicly reachable Ollama hosts seen between October 2025 and January 2026 ([SentinelLABS, "Silent Brothers"](https://www.sentinelone.com/labs/silent-brothers-ollama-hosts-form-anonymous-ai-network-beyond-platform-guardrails/)), and Cisco Talos found about 1,100 in September 2025. Hardening guides exist for single tools, including the projects' own. Law firms and vendors have written about SB 574's access test (Morgan Lewis, Holland & Knight, Alston & Bird, Ropes & Gray, Harris Beach Murtha, Bells Up), but none of the commentary MV2 found mentions self-hosted tools or their defaults. As far as MV2 could find, this is the first side-by-side record of the shipped network and account defaults of self-hosted AI tools that cites the source for each one, and the first to read them against SB 574's access question. It measures what the software does before anyone configures it, not how many servers are exposed.

## Licence

Text and data: CC BY 4.0, cite "bar-ai-guidance, MV2 of Munim, Inc.". Test code: Apache-2.0. Each project named keeps its own licence.
