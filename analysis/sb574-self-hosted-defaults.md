# Who can reach it out of the box? Fifteen self-hosted AI tools against SB 574's access question

MV2 of Munim, Inc., 14 October 2026 (0.6.0: seven tools; 0.7.0: eleven; 0.8.0: fifteen). Written with AI agents working in his name. Data: [`data/self_hosted_defaults.json`](../data/self_hosted_defaults.json) (CC BY 4.0). This is a record of software defaults, not legal advice and not a view on whether any office meets any law.

## The question

California's SB 574 (Statutes of 2026, Chapter 858; new Business and Professions Code section 6068.1, in force 1 January 2027) bars an attorney from entering confidential, personal identifying or other nonpublic information into a generative AI system unless access to what is entered is restricted to the attorney and persons the attorney has authorised who are bound to keep it confidential. Law-firm summaries stress that the test is about who has access, not whether a product is labelled public, enterprise or self-hosted ([bar-ai-guidance entry `ca-sb-574`](../data/guidance.json)).

Small firms run their own AI to keep client text inside the office. For them, who has access is decided by a handful of settings: the address the software listens on, whether it asks for a login or key, whether anyone can create an account, and what admins and share buttons can do. So MV2 read those settings, as each project ships them, from the projects' own source files and documentation.

## What the defaults are (default branch and docs read on 14 October 2026)

| Tool | Role | Listens on, started directly | Listens on, project's own container | Asks for a credential by default? | Account sign-up by default |
|---|---|---|---|---|---|
| Ollama v0.40.4 | model server | 127.0.0.1:11434 | 0.0.0.0:11434 | No, and the server has no login or key option | n/a |
| llama.cpp `llama-server` v0.6.0 | model server | 127.0.0.1 | 0.0.0.0 (CPU image) | No; `--api-key` is optional | n/a |
| SGLang v0.5.21 | model server | 127.0.0.1:30000 | 0.0.0.0:30000 on the host network (compose file) | No; `--api-key` is optional | n/a |
| vLLM v0.31.0 | model server | all interfaces, port 8000 | not checked | No; `--api-key` is optional and leaves some endpoints open | n/a |
| LocalAI v4.11.0 | model server | all interfaces, port 8080 | not checked | No on a LAN; refuses to start without one on a public address | n/a |
| KoboldCpp v1.123 | model server (with web UI) | all interfaces, port 5001 (but prints a localhost address) | no official image | No; `--password` is optional and never covers image endpoints | n/a |
| LMDeploy v0.18.0 `api_server` | model server | 0.0.0.0:23333 | not checked | No; `--api-keys` is optional | n/a |
| LiteLLM Proxy v1.105.1 | model server (gateway) | 0.0.0.0:4000 | port 4000 on every host interface | **Yes: since v1.104.0 refuses to start without a real master key, on any address** | n/a |
| TabbyAPI (main; no releases) | model server | 127.0.0.1:5000 | 0.0.0.0 (Dockerfile runs `--host 0.0.0.0`) | **Yes: generates random keys at first start** | n/a |
| Xinference v4.0.0 | model server (with web UI) | 127.0.0.1:9997 (`xinference-local`) | 0.0.0.0 (documented `docker run`) | Yes, login, once set up; before that the first visitor creates the admin | n/a |
| AnythingLLM v1.18.0 (Docker) | chat app | n/a | port 3001 on every host interface | No login at all until one is switched on | no accounts until multi-user mode |
| text-generation-webui v4.9 | chat app | 127.0.0.1:7860 | 0.0.0.0 (NVIDIA image starts with `--listen`) | No login unless `--gradio-auth` is given | no accounts |
| LibreChat v0.8.8 | chat app | localhost:3080 | 0.0.0.0 (compose file) | Yes, login | Open, and unverified email addresses may sign in |
| Dify 1.17.1 (Docker Compose) | chat app | n/a | ports 80 and 443 on every host interface | Yes, login, once set up | Closed (invitation only); but before setup, the first visitor to `/install` becomes the owner |
| Open WebUI v0.12.0 | chat app | 0.0.0.0:8080 | 0.0.0.0:8080 | Yes, login | Open but held: new accounts wait for an admin |

Other defaults that bear on who can read what is entered:

- **Open WebUI**: admins can open any user's chat (`ENABLE_ADMIN_CHAT_ACCESS=True`) and export chats; the share dialog can upload a chat to the Open WebUI Community website (`ENABLE_COMMUNITY_SHARING=True`); users can make share links that any logged-in user can open. These are stored settings, so after the first start the admin panel, not the environment, decides.
- **LibreChat**: share links are on and open to any logged-in user; public (no-login) links are off.
- **AnythingLLM**: in single-user mode, anyone with the one instance password can change every setting and read all chats.
- **Dify**: `INIT_PASSWORD` is empty in the shipped `.env.example`, so the one-time `/install` page asks for no setup password; it closes for good once the first admin exists. The plugin daemon's debugging port 5003 is also published.
- **Xinference**: no admin exists at first start; its setup endpoint and setup page take no credential until the first admin is created, then refuse. `XINFERENCE_AUTH_ADVANCED=0` turns authentication off entirely.
- **KoboldCpp**: with no `--host` it binds the empty address (every interface) but its startup message prints `localhost`. Even with `--password`, image generation, upscaling, interrogation and `/tts_to_audio` are exempt from the check, as the flag's own help says.
- **TabbyAPI**: the generated API and admin keys are printed to its log at first start, and the admin key also works as an API key. `allowed_origins` defaults to `*`.
- **LiteLLM**: the check can be switched off with `LITELLM_DANGEROUSLY_PERMIT_WEAK_OR_UNSET_MASTER_KEY=true`, and then a proxy with no master key accepts every request. Its example compose file also publishes its Postgres database on port 5432, with a fixed password written in the file, and Prometheus on 9090.
- **LMDeploy**: `--allow-origins` defaults to `*`.
- **llama.cpp**: its web UI and slot-monitoring endpoint are on by default.
- **vLLM**: its own security page says `--api-key` protects only some path prefixes and that endpoints such as `/invocations`, which offer the same inference, stay open.

Each row's source files and doc pages are listed in the JSON.

## What this shows

1. **Seven of the ten model servers ask for no credential by default.** Four (vLLM, LocalAI, KoboldCpp, LMDeploy) listen on all interfaces even when started directly. Three (Ollama, llama.cpp, SGLang) listen only on the machine itself when started directly, but each project's own container or compose file switches to all interfaces. Ollama has no option to require a credential at all.
2. **The three model servers that do demand a credential each use a different mechanism.** LiteLLM refuses to start until a master key is set that is neither empty nor a publicly known default. TabbyAPI never runs keyless because it makes random keys itself at first start. Xinference has user accounts, but the first person to reach its setup page creates the admin. A fourth, LocalAI, refuses an unauthenticated start only on public addresses, so everyone on the office Wi-Fi counts as trusted.
3. **The strictest default has been in a release for eleven days.** LiteLLM's boot check was committed on 19 September 2026 (fe48053), ten days after Wiz Research published "Off Guard" on unprotected LiteLLM proxies, and first shipped in v1.104.0 on 3 October 2026; the file is absent at v1.103.0 (28 September). Any LiteLLM proxy installed from an earlier release does not have it.
4. **Of the five chat apps, which are where prompts and chat history are stored:** AnythingLLM's Docker install and text-generation-webui's container have no login unless one is turned on. LibreChat requires a login but lets anyone who can reach it register, without email verification. Dify is invitation-only once set up, but until its first admin exists, whoever opens `/install` first owns the workspace. Open WebUI holds new accounts until an admin approves them, but lets every admin read every user's chat and shows a button that sends a chat to an outside website.
5. **So a firm's own setup does not limit access by itself.** In ten of the fifteen tools (Ollama, llama.cpp, SGLang, vLLM, LocalAI, KoboldCpp, LMDeploy, AnythingLLM, text-generation-webui, LibreChat), someone who was never given an account can, as shipped, use the model or create an account and use the app. Dify and Xinference allow it only in the window before setup. Open WebUI, LiteLLM and TabbyAPI do not, though Open WebUI's admin chat access and community upload button still have to be decided. Whether a given office's setup restricts access enough for SB 574 is for its lawyers to judge. The point here is that the answer comes from settings someone has to change, not from the decision to self-host.

One technical caveat, which cuts the other way: the model servers here do not keep a history of prompts. Someone who reaches an open Ollama or vLLM port can use the model, but cannot read earlier prompts through it. The stored text sits in the chat app. That is why the chat-app rows, with their accounts, admins and share buttons, matter most for the access question.

## How to read your own setup

On the machine that runs the tool:

```bash
# what is listening, and on which address (Linux / macOS)
ss -ltnp 2>/dev/null || lsof -nP -iTCP -sTCP:LISTEN
# Windows PowerShell
Get-NetTCPConnection -State Listen | Sort-Object LocalPort
```

An address of `0.0.0.0`, `::` or `*` means every network the machine is on. Do not trust a tool's startup message for this: KoboldCpp prints `localhost` while listening everywhere. From a second machine on the office network, `curl http://<office-machine-ip>:11434/api/version` (Ollama) or `curl http://<ip>:8000/v1/models` (vLLM) should fail unless you share the server on purpose. In the chat app, open the user list and the admin settings for sign-up, admin chat access and sharing. For Dify and Xinference, create the first admin before the server is reachable by anyone else (for Dify, or set `INIT_PASSWORD` first).

## Method and limits

- Facts come from each project's default branch and documentation, read on 14 October 2026, with the latest release tag shown on its GitHub releases page that day (TabbyAPI publishes none). SGLang's and LiteLLM's key files were also read at the release tag and match; LiteLLM's boot check was also looked for at v1.104.2, v1.104.0, v1.103.0 and v1.102.4. Defaults change between releases. Re-check before relying on a row.
- Only the files named in the JSON were read. Container setups were checked for Ollama (Dockerfile), llama.cpp (CPU Dockerfile), SGLang (compose file), LiteLLM (compose file), TabbyAPI (Dockerfile and compose file), Xinference (documented `docker run` command), text-generation-webui (NVIDIA Dockerfile and compose file), LibreChat (compose file), Dify (compose file), AnythingLLM (documented install command) and Open WebUI (start script). vLLM's, LocalAI's and LMDeploy's images were not checked; KoboldCpp has no official image.
- LocalAI's public-address rule comes from its flag's help text and call site; the function that applies it is in a file MV2 did not read. Dify's no-password `/install` and Xinference's first-caller setup come from their documentation; the code behind them was not read. KoboldCpp's password check was read at its call sites, not in the function body. Which endpoints LMDeploy's `--api-keys` covers was not checked.
- Desktop apps (LM Studio, Jan, AnythingLLM Desktop, the Ollama desktop app) are not covered. Their network settings live in the GUI, and LM Studio is not open source.
- MV2 read law-firm summaries of SB 574 and its quoted wording, not the chaptered text, because the legislature's site refuses automated access.
- No live system was scanned or probed. Everything here comes from public source code and documentation.

## Prior work, and what is new here

Security researchers have counted exposed servers on the internet. SentinelOne's SentinelLABS and Censys reported about 175,000 publicly reachable Ollama hosts seen between October 2025 and January 2026 ([SentinelLABS, "Silent Brothers"](https://www.sentinelone.com/labs/silent-brothers-ollama-hosts-form-anonymous-ai-network-beyond-platform-guardrails/)), and Cisco Talos found about 1,100 in September 2025. Wiz Research reported that in a February 2026 sample of 3,074 internet-facing LiteLLM proxies, 294 accepted the documentation's example master key or required no authentication at all, 191 of them none ([Wiz, "Off Guard", 9 September 2026](https://www.wiz.io/blog/off-guard-breaking-litellm-from-authentication-bypass-to-cloud-compromise)); an unset or publicly known key is exactly what LiteLLM's boot check, shipped in v1.104.0 three and a half weeks later, now refuses. Hardening guides exist for single tools, including the projects' own. Law firms and vendors have written about SB 574's access test (Morgan Lewis, Holland & Knight, Alston & Bird, Ropes & Gray, Harris Beach Murtha, Bells Up), but none of the commentary MV2 found mentions self-hosted tools or their defaults. As far as MV2 could find, this is the first side-by-side record of the shipped network and account defaults of self-hosted AI tools that cites the source for each one, and the first to read them against SB 574's access question. It measures what the software does before anyone configures it, not how many servers are exposed.

## Licence

Text and data: CC BY 4.0, cite "bar-ai-guidance, MV2 of Munim, Inc.". Test code: Apache-2.0. Each project named keeps its own licence.
