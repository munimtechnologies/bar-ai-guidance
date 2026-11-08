#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# ai_protective_orders.py 0.1.0: look up how US federal protective and confidentiality orders
# word their AI clauses, in MV2's coded dataset (data/ai_protective_orders.json, CC BY 4.0,
# in https://github.com/munimtechnologies/bar-ai-guidance).
# Made with AI agents working in MV2's (Munim, Inc.) name. Standard library only, read-only.
# It reports what public court orders say and where the coding came from. It is not legal advice.
"""Look up coded AI clauses in US protective orders by court, outcome, clause test, id or text.

Data source, in this order: --file PATH; the repository's own data/ai_protective_orders.json
when the script runs inside a checkout of munimtechnologies/bar-ai-guidance; otherwise one
HTTPS GET of --url (default: the file on the repository's main branch).

Exit codes: 0 = at least one case matched; 1 = no match; 2 = the dataset could not be read or
an argument was not valid.
"""
import argparse
import json
import os
import re
import sys
import urllib.request

__version__ = "0.1.0"

DEFAULT_URL = ("https://raw.githubusercontent.com/munimtechnologies/bar-ai-guidance/"
               "main/data/ai_protective_orders.json")
REPO_URL = "https://github.com/munimtechnologies/bar-ai-guidance"
WRITEUP_URL = REPO_URL + "/blob/main/analysis/ai-protective-orders.md"

# Setup A, as the dataset defines it: an openly published model (for example Llama or Qwen
# weights) running on a server the party controls, reachable only from the party's own network,
# with no outside provider, never trained on inputs.
SETUP_LABELS = {
    "permitted": "the order's words allow it",
    "conditional": "only with consent, notice, the parties' agreement or a court order",
    "unclear": "the order's words do not settle it",
    "forbidden": "the order's words rule it out",
}
STATUS_LABELS = {
    "codable": "coded",
    "refusal": "a court refused a proposed AI clause (not coded for setup A)",
    "not_codable": "not coded (the order's own words could not be read; see reason)",
}
# MV2's short glosses of the clause-test codes used in the dataset's "tests" field.
TEST_LABELS = {
    "BAN": "bars putting the material into any AI platform",
    "CONTRACT": "asks for a contract or commitment from the AI provider or platform",
    "DATA": "how the tool treats inputs (no training, retention or disclosure; deletion)",
    "NOTICE": "asks for notice to, disclosure to or permission from the other side",
    "OPENNESS": "turns on whether the system or model is open",
    "OTHER": "other conditions (security practices, server location, enterprise licence)",
    "PUBLIC": "bars public, consumer or publicly available AI tools",
}
SETUP_A = ("setup A = an openly published model run on a server the party controls, with no "
           "outside provider and no training on inputs")
FOOTER = ("Information about public court orders, not legal advice. 'Permitted' means the "
          "order's literal words allow setup A, not that any court has ruled so. The order in "
          "your own case governs: read it, and ask the responsible lawyer or the court.")
COURT_RE = re.compile(r"[^a-z0-9]")


def local_data_path():
    """data/ai_protective_orders.json of the checkout this script sits in, if any.

    In the repository the script is skills/ai-protective-orders/scripts/ai_protective_orders.py,
    so the repository root is three folders above the script's own folder.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    path = os.path.join(root, "data", "ai_protective_orders.json")
    return path if os.path.isfile(path) else None


def load_dataset(file_path=None, url=None, timeout=30):
    """Return (data, source). Raises ValueError or OSError when the dataset cannot be read."""
    if file_path:
        with open(file_path, encoding="utf-8") as fh:
            data = json.load(fh)
        source = file_path
    elif url is None and local_data_path():
        path = local_data_path()
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        source = path
    else:
        url = url or DEFAULT_URL
        if not url.startswith("https://"):
            raise ValueError("only https:// URLs are read")
        req = urllib.request.Request(url, headers={
            "User-Agent": "ai-protective-orders/" + __version__})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        source = url
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise ValueError("not an ai_protective_orders dataset (no 'cases' list)")
    return data, source


def court_key(text):
    """'S.D.N.Y.' and 'sdny' both become 'sdny'; 'N.D. Cal.' becomes 'ndcal'."""
    return COURT_RE.sub("", str(text or "").lower())


def case_text(case):
    parts = []
    for value in case.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, dict):
            parts.extend(str(v) for v in value.values() if isinstance(v, str))
    return " ".join(parts).lower()


def select(cases, courts=None, setup=None, status=None, test=None, ids=None,
           self_hosting=False, grep=None):
    keys = [court_key(c) for c in (courts or [])]
    out = []
    for case in cases:
        if keys and court_key(case.get("court")) not in keys:
            continue
        if setup and case.get("setup_a") != setup:
            continue
        if status and case.get("status") != status:
            continue
        if test and test not in (case.get("tests") or {}):
            continue
        if ids and case.get("case_id") not in ids:
            continue
        if self_hosting and case.get("self_hosting_named") is not True:
            continue
        if grep and grep.lower() not in case_text(case):
            continue
        out.append(case)
    return out


def labelled(case):
    item = dict(case)
    item["status_label"] = STATUS_LABELS.get(case.get("status"), str(case.get("status")))
    if case.get("setup_a"):
        item["setup_a_label"] = SETUP_LABELS.get(case["setup_a"], str(case["setup_a"]))
    item["test_labels"] = dict((k, TEST_LABELS.get(k, k)) for k in (case.get("tests") or {}))
    return item


def format_case(case, show_quotes=False, show_notes=False):
    status = case.get("status")
    head = case.get("setup_a") if status == "codable" else status
    lines = [
        "[%s] %s | %s | %s" % (case.get("case_id"), case.get("court"), head,
                               case.get("case_no")),
        "  %s" % case.get("caption"),
        "  Order: %s" % case.get("order"),
    ]
    if status == "codable":
        lines.append("  Setup A: %s (%s)" % (case.get("setup_a"),
                                             SETUP_LABELS.get(case.get("setup_a"), "?")))
        if case.get("setup_a_quote"):
            lines.append("    order's words: \"%s\"" % case["setup_a_quote"])
        if case.get("setup_a_reason"):
            lines.append("    why: %s" % case["setup_a_reason"])
        if case.get("reading_rule"):
            lines.append("    reading rule: %s (the write-up also reports the opposite reading)"
                         % case["reading_rule"])
        tests = case.get("tests") or {}
        lines.append("  Clause tests: %s" % (", ".join(sorted(tests)) or "none"))
        if show_quotes:
            for code in sorted(tests):
                lines.append("    %s (%s): \"%s\"" % (code, TEST_LABELS.get(code, code),
                                                      tests[code]))
        if case.get("self_hosting_named"):
            lines.append("  Names self-hosting: \"%s\"" % case.get("self_hosting_quote", ""))
        if case.get("openness_named"):
            lines.append("  Names openness: \"%s\"" % case.get("openness_quote", ""))
    else:
        lines.append("  Status: %s" % STATUS_LABELS.get(status, status))
        if case.get("reason"):
            lines.append("  Reason: %s" % case["reason"])
    if show_notes and case.get("note"):
        lines.append("  Note: %s" % case["note"])
    return "\n".join(lines)


def count(items):
    out = {}
    for item in items:
        out[item] = out.get(item, 0) + 1
    return out


def summary_lines(data):
    cases = data["cases"]
    coded = [c for c in cases if c.get("status") == "codable"]
    lines = ["%d cases, %d coded, version %s" % (len(cases), len(coded), data.get("version", "?"))]
    by_status = count(c.get("status") for c in cases)
    lines.append("by status: " + ", ".join("%s %d" % (k, by_status[k]) for k in sorted(by_status)))
    by_setup = count(c.get("setup_a") for c in coded)
    lines.append("setup A (coded cases): " + ", ".join(
        "%s %d" % (k, by_setup.get(k, 0)) for k in ("permitted", "conditional", "unclear",
                                                     "forbidden")))
    tests = count(k for c in coded for k in (c.get("tests") or {}))
    lines.append("clause tests: " + ", ".join(
        "%s %d" % (k, tests[k]) for k in sorted(tests, key=lambda k: (-tests[k], k))))
    courts = count(c.get("court") for c in cases)
    lines.append("courts (%d): " % len(courts) + ", ".join(
        "%s %d" % (k, courts[k]) for k in sorted(courts, key=lambda k: (-courts[k], k))))
    lines.append("self-hosting named in %d coded cases"
                 % sum(1 for c in coded if c.get("self_hosting_named") is True))
    return lines


def build_parser():
    p = argparse.ArgumentParser(
        prog="ai_protective_orders.py",
        description="Look up how US federal protective orders word their AI clauses "
                    "(MV2's coded dataset). Not legal advice.")
    p.add_argument("--court", action="append", metavar="COURT",
                   help="court as written or without dots, e.g. S.D.N.Y. or sdny; repeatable")
    p.add_argument("--setup", choices=sorted(SETUP_LABELS),
                   help="literal-reading outcome for setup A (coded cases only)")
    p.add_argument("--status", choices=sorted(STATUS_LABELS), help="coding status")
    p.add_argument("--test", type=str.upper, choices=sorted(TEST_LABELS), metavar="CODE",
                   help="clause test: " + ", ".join(sorted(TEST_LABELS)))
    p.add_argument("--id", action="append", dest="ids", metavar="ID", help="exact case id")
    p.add_argument("--self-hosting", action="store_true",
                   help="only orders whose words name self-hosting or the party's own systems")
    p.add_argument("--grep", metavar="TEXT", help="case-insensitive text in any field")
    p.add_argument("--quotes", action="store_true", help="print each clause test's quotation")
    p.add_argument("--notes", action="store_true", help="also print each case's coding note")
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    p.add_argument("--summary", action="store_true", help="print counts and stop")
    p.add_argument("--file", metavar="PATH", help="read this ai_protective_orders.json instead")
    p.add_argument("--url", metavar="URL", help="read the dataset from this https URL")
    p.add_argument("--version", action="version", version="%(prog)s " + __version__)
    return p


def main(argv=None):
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    try:
        data, source = load_dataset(args.file, args.url)
    except (OSError, ValueError) as exc:
        print("ai_protective_orders: could not read the dataset: %s" % exc, file=sys.stderr)
        return 2

    if args.summary:
        print("\n".join(summary_lines(data)))
        print("source: %s" % source)
        print("write-up: %s" % WRITEUP_URL)
        return 0

    cases = data["cases"]
    found = select(cases, courts=args.court, setup=args.setup, status=args.status,
                   test=args.test, ids=args.ids, self_hosting=args.self_hosting, grep=args.grep)

    if args.json:
        print(json.dumps({
            "version": data.get("version"),
            "source": source,
            "license": data.get("license"),
            "setup_a": SETUP_A,
            "matched": len(found),
            "cases": [labelled(c) for c in found],
            "write_up": WRITEUP_URL,
            "not_legal_advice": FOOTER,
        }, indent=2, ensure_ascii=False))
        return 0 if found else 1

    print("ai_protective_orders %s: %d of %d cases matched; source %s"
          % (data.get("version", "?"), len(found), len(cases), source))
    print("(%s)" % SETUP_A)
    if not found:
        print("")
        print("No case matched. The dataset is a research sample of orders reported on one "
              "e-discovery blog from October 2025 to October 2026, not a list of every order; "
              "no match does not mean no court has such an order. Write-up: %s" % WRITEUP_URL)
    for case in found:
        print("")
        print(format_case(case, show_quotes=args.quotes, show_notes=args.notes))
    print("")
    print(FOOTER)
    return 0 if found else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(errors="replace")
        except (ValueError, OSError):
            pass
    sys.exit(main())
